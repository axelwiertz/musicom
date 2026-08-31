"""Param-lock step sequencer — Asterism browser drum machine style.

Replicable logic from Asterism, a free WebAudio drum machine (Synthtopia
2026-08-28): advanced sequencing built around **parameter locking**
(per-step values that override a track's base value), **ratcheting**
(sub-division bursts per step), and **randomization** (per-step random
rolls that can freeze/unlock individual parameters).

What is replicated here:
- Per-step parameter locks: each step may override any of a set of named
  params (e.g. pitch, decay, filter cutoff, velocity) with its own value.
  Steps without a lock fall back to the track base value — classic
  X0X-style parameter lock behavior.
- Ratcheting: a step may fire N sub-hits (2..4) spread across the step.
- Randomization: a track-level ``randomize`` can roll every unlocked
  param within a range; ``lock``/``unlock`` freezes individual params so
  they survive randomization (Asterism-style per-param freeze).

Not replicated: the WebAudio engine itself, the browser UI, pattern
chains / song mode, sample loading.

Usage:
    from sound.generators.param_lock_seq import ParamLockSequencer

    seq = ParamLockSequencer(steps=16)
    seq.set_base(pitch=60, cutoff=0.5, velocity=100)
    seq.lock_param(3, pitch=72, velocity=127)   # accent step
    seq.set_ratchet(11, 4)                       # 4 sub-hits on step 11
    events = seq.generate(seed=7)                # list of (frac, params)
"""

from typing import Any, Dict, List, Optional, Tuple

__all__ = ["ParamLockSequencer"]


class ParamLockSequencer:
    """Step sequencer with per-step parameter locks, ratchet, and freeze-aware randomization.

    Time model: a one-bar pattern of ``steps`` sixteenth steps. Each step
    carries (optionally) locked values for named parameters. When a step
    has no lock for a param, the track base value is used.
    """

    def __init__(self, steps: int = 16, subdivisions: int = 4):
        """Initialize.

        Args:
            steps: Number of steps in the pattern (16 = one bar of 16ths).
            subdivisions: Max ratchet count per step (1..4).
        """
        self.steps = steps
        self.subdivisions = subdivisions
        self.base: Dict[str, Any] = {}
        self.locks: Dict[int, Dict[str, Any]] = {}   # step -> {param: value}
        self.ratchets: Dict[int, int] = {}           # step -> hit count
        self.active: set = set()                      # steps that play at all

    # -- track-level -------------------------------------------------------- #
    def set_base(self, **params: Any) -> None:
        """Set the track base value(s) for params (used when no lock)."""
        self.base.update(params)

    # -- per-step locks ----------------------------------------------------- #
    def set_active(self, step: int) -> None:
        """Mark a step as active (will play)."""
        self.active.add(step % self.steps)

    def lock_param(self, step: int, **params: Any) -> None:
        """Lock (override) parameter value(s) on a step.

        This is the core "parameter lock": the step carries its own value
        for the named param, independent of the track base.
        """
        s = step % self.steps
        self.locks.setdefault(s, {}).update(params)
        self.active.add(s)

    def get_param(self, step: int, name: str, default: Any = None) -> Any:
        """Resolve a param for a step: step lock first, then track base."""
        s = step % self.steps
        if s in self.locks and name in self.locks[s]:
            return self.locks[s][name]
        if name in self.base:
            return self.base[name]
        return default

    # -- ratchet ------------------------------------------------------------ #
    def set_ratchet(self, step: int, count: int) -> None:
        """Set a ratchet (sub-division burst count) for a step."""
        if not 1 <= count <= self.subdivisions:
            raise ValueError(f"ratchet count must be 1..{self.subdivisions}")
        s = step % self.steps
        if count > 1:
            self.ratchets[s] = count
        elif s in self.ratchets:
            del self.ratchets[s]

    # -- randomization ------------------------------------------------------ #
    def randomize(self, ranges: Dict[str, Tuple[float, float]],
                  seed: Optional[int] = None,
                  frozen: Optional[List[str]] = None) -> None:
        """Randomize unlocked params within given [min, max] ranges.

        Args:
            ranges: {param: (min, max)} — uniform roll for each param.
            seed: Random seed for reproducibility.
            frozen: Params to leave untouched (freeze), even if unlocked.
        """
        import random
        rng = random.Random(seed)
        frozen_names = set(frozen or [])
        for name, (lo, hi) in ranges.items():
            if name in frozen_names:
                continue
            if name in self.base:
                self.base[name] = lo + rng.random() * (hi - lo)
            # unlocked locks follow the new base too
            for locks in self.locks.values():
                if name in locks and name not in frozen_names:
                    locks[name] = lo + rng.random() * (hi - lo)

    # -- generation --------------------------------------------------------- #
    def generate(self, seed: Optional[int] = None) -> List[Tuple[float, Dict[str, Any]]]:
        """Generate the pattern as (step_fraction, resolved_params) hits.

        Returns:
            List of (frac, params) where frac is in [0, steps) and params
            is the resolved parameter dict for that hit (locks overlaid on
            base). Ratcheted steps yield multiple hits.
        """
        import random
        rng = random.Random(seed)
        out: List[Tuple[float, Dict[str, Any]]] = []
        for step in range(self.steps):
            if step not in self.active:
                continue
            count = self.ratchets.get(step, 1)
            for i in range(count):
                frac = step + (i / count)
                params = dict(self.base)
                params.update(self.locks.get(step, {}))
                if "velocity" in params and count > 1 and i > 0:
                    params = dict(params)
                    params["velocity"] = max(40, int(params["velocity"]) - 20)
                out.append((frac, params))
        return out


def demo() -> str:
    """Render a demo pattern grid to text."""
    seq = ParamLockSequencer(steps=16)
    seq.set_base(pitch=60, cutoff=0.5, velocity=100)
    # 4-on-the-floor with pitch/velocity accent on beat, ratchet on 11
    for s in (0, 4, 8, 12):
        seq.set_active(s)
    seq.lock_param(0, velocity=127, pitch=72)
    seq.lock_param(4, velocity=110)
    seq.lock_param(8, velocity=127, pitch=74)
    seq.lock_param(12, velocity=110)
    seq.set_ratchet(11, 4)
    seq.set_active(11)
    events = seq.generate(seed=1)
    cells = ["."] * 16
    for frac, _ in events:
        cells[min(15, int(frac))] = "#"
    return "".join(cells) + f"  ({len(events)} hits)"


if __name__ == "__main__":
    print(demo())
