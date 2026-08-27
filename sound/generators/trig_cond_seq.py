"""Trig-condition step sequencer — Korg Volca Drum alt-firmware style.

Replicable logic from the "hj Firmware" unofficial Volca Drum firmware
(Synthtopia 2026-08-23): it adds Elektron-style trigger conditions
(A-B, first bar, FILL), extended negative swing, negative accent values
for ghost notes, and extended SLICE for sub-step patterns.

What is replicated here:
- Trigger conditions per step: first / last / every-N pass, FILL-only,
  never, discrete Elektron probabilities (50/62/75/87%), and A-B
  (fire on passes in a set, e.g. 1st & 3rd).
- Ghost notes: velocity accent may be negative -> rendered as a very
  quiet (<=16) hit, the classic "ghost note" trick.
- Negative swing: swing amount may be negative (delays even steps
  backwards in time).
- SLICE sub-steps: a step may be sliced into N sub-hits, each with its
  own probability/velocity (the alt firmware's extended sub-step mode).

Not replicated: the actual ARM firmware image, FUNC+knob parameter
editing, TOUCH FX pads (hardware UI concerns).

Usage:
    from sound.generators.trig_cond_seq import TrigConditionSequencer

    seq = TrigConditionSequencer(steps=16)
    seq.set_active(0)                      # step 0 on, fires every pass
    seq.set_condition(3, "every", n=2)     # fire every 2nd pass
    seq.set_condition(7, "fill")           # only when fill is active
    seq.set_condition(11, "a_b", passes=[1, 3])
    seq.set_accent(3, -40)                 # negative accent -> ghost note
    seq.set_slice(5, sub_steps=3)          # 3 sub-hits inside step 5
    events = seq.generate(passes=4, fill=False, seed=7)
"""

from typing import Dict, List, Optional, Tuple

import numpy as np

__all__ = ["TrigConditionSequencer", "GHOST_VELOCITY_MAX"]

# Elektron-style discrete probabilities (percent).
ELEKTRON_PROBS = (50, 62, 75, 87)
GHOST_VELOCITY_MAX = 16  # velocities <= this count as ghost notes


class TrigConditionSequencer:
    """Step sequencer with Elektron-style trig conditions + ghost notes.

    Time model: a pattern runs for ``passes`` repeats. Each step may carry
    a condition that decides, per pass, whether it fires. Accents may be
    negative (ghost note). Steps may be sliced into sub-hits.
    """

    def __init__(self, steps: int = 16, subdivisions: int = 4):
        """Initialize.

        Args:
            steps: Number of steps in the pattern.
            subdivisions: Max sub-hits per step (SLICE depth, 1..4).
        """
        self.steps = int(steps)
        self.subdivisions = int(subdivisions)
        self._active: set = set()          # steps that are turned on
        self._conditions: Dict[int, Tuple[str, Optional[int], Optional[float],
                                         Optional[List[int]]]] = {}
        self._accents: Dict[int, int] = {}
        self._slices: Dict[int, int] = {}
        self.swing: float = 0.0  # negative swing delays even steps backwards

    # -- configuration -------------------------------------------------- #
    def set_active(self, step: int, active: bool = True) -> None:
        """Turn a step on (or off). Only active steps can fire."""
        step = step % self.steps
        if active:
            self._active.add(step)
        else:
            self._active.discard(step)

    def set_condition(self, step: int, kind: str, n: Optional[int] = None,
                      prob: Optional[float] = None,
                      passes: Optional[List[int]] = None) -> None:
        """Set the trigger condition for ``step``.

        Args:
            step: Step index (mod steps).
            kind: One of:
                "always"  — fire on every pass.
                "never"   — never fire.
                "first"   — fire only on pass 1.
                "last"    — fire only on the final pass.
                "every"   — fire every ``n`` passes (n >= 1).
                "fill"    — fire only when fill mode is active.
                "prob"    — fire with probability ``prob`` (0..1), rounded
                            to the nearest Elektron value {50,62,75,87}%.
                "a_b"     — fire when the 1-based pass number is in
                            ``passes`` (e.g. [1, 3]).
        """
        kind = kind.lower()
        if kind not in {"always", "never", "first", "last", "every", "fill",
                        "prob", "a_b"}:
            raise ValueError(f"unknown condition kind {kind!r}")
        if kind == "every" and (n is None or n < 1):
            raise ValueError("'every' needs n >= 1")
        if kind == "prob":
            if prob is None or not 0.0 <= prob <= 1.0:
                raise ValueError("'prob' needs 0 <= prob <= 1")
            prob = _snap_prob(prob)
        if kind == "a_b" and not passes:
            raise ValueError("'a_b' needs a non-empty pass list")
        step = step % self.steps
        self._conditions[step] = (kind, n, prob,
                                  list(passes) if passes else None)
        # configuring a condition implies the step is on
        self._active.add(step)

    def set_accent(self, step: int, accent: int) -> None:
        """Set accent for a step; negative values mean ghost note."""
        step = step % self.steps
        self._accents[step] = int(max(-127, min(127, accent)))
        self._active.add(step)

    def set_slice(self, step: int, sub_steps: int) -> None:
        """Slice a step into ``sub_steps`` sub-hits (SLICE / sub-step mode)."""
        if not 1 <= sub_steps <= self.subdivisions:
            raise ValueError(f"sub_steps must be 1..{self.subdivisions}")
        step = step % self.steps
        self._slices[step] = int(sub_steps)
        self._active.add(step)

    # -- generation ----------------------------------------------------- #
    def generate(self, passes: int = 1, fill: bool = False,
                 seed: Optional[int] = None
                 ) -> List[Tuple[float, int, bool]]:
        """Generate events across ``passes`` pattern repeats.

        Returns:
            List of (step_frac, velocity, is_ghost) where step_frac is in
            [0, steps) plus fractional sub-step offset, velocity is 0..127,
            and is_ghost marks ghost notes (negative accent).
        """
        rng = np.random.default_rng(seed)
        events: List[Tuple[float, int, bool]] = []
        for pass_no in range(1, passes + 1):
            for step in range(self.steps):
                if not self._fires(step, pass_no, passes, fill, rng):
                    continue
                accent = self._accents.get(step, 100)
                is_ghost = accent < 0
                vel = max(0, min(127, abs(accent)))
                if is_ghost:
                    vel = min(vel, GHOST_VELOCITY_MAX)
                n_sub = self._slices.get(step, 1)
                base = float(step)
                if self.swing and step % 2 == 1:
                    # negative swing pulls odd steps earlier
                    base += self.swing * 0.5
                for k in range(n_sub):
                    frac = base + k / float(n_sub)
                    # each sub-hit gets its own probability roll
                    if n_sub > 1 and rng.random() > 0.9:
                        continue
                    events.append((frac, vel, is_ghost))
        events.sort(key=lambda e: e[0])
        return events

    # -- internals ------------------------------------------------------ #
    def _fires(self, step: int, pass_no: int, total_passes: int,
               fill: bool, rng) -> bool:
        if step not in self._active:
            return False
        kind, n, prob, passes = self._conditions.get(step, ("always", None,
                                                            None, None))
        if kind == "always":
            return True
        if kind == "never":
            return False
        if kind == "first":
            return pass_no == 1
        if kind == "last":
            return pass_no == total_passes
        if kind == "every":
            return pass_no % n == 0
        if kind == "fill":
            return fill
        if kind == "prob":
            return rng.random() < prob
        if kind == "a_b":
            return pass_no in passes
        return True


def _snap_prob(p: float) -> float:
    """Snap a probability to the nearest Elektron discrete value."""
    return min(ELEKTRON_PROBS, key=lambda v: abs(v / 100.0 - p)) / 100.0


def demo() -> None:
    """Run a short demo of the trig-condition sequencer."""
    seq = TrigConditionSequencer(steps=16)
    seq.set_active(0)
    seq.set_condition(3, "every", n=2)
    seq.set_condition(7, "fill")
    seq.set_condition(11, "a_b", passes=[1, 3])
    seq.set_condition(13, "prob", prob=0.7)
    seq.set_accent(3, -40)          # ghost note on step 3
    seq.set_accent(7, 120)          # loud fill hit
    seq.set_slice(5, 3)             # triple sub-hit inside step 5
    seq.swing = -0.25               # negative swing
    ev = seq.generate(passes=4, fill=False, seed=42)
    ghosts = sum(1 for _, _, g in ev if g)
    print(f"generated {len(ev)} events over 4 passes "
          f"({ghosts} ghost notes)")
    for frac, vel, ghost in ev[:10]:
        tag = "GHOST" if ghost else "     "
        print(f"  step {frac:5.2f}  vel {vel:3d}  {tag}")


if __name__ == "__main__":
    demo()
