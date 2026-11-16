"""Arp 2.0-style probability / iteration / fill arpeggiator — Synthstrom Deluge
community firmware 1.3 "Derbyshire" style.

Replicable logic from Synthtopia 2026-11-15 ("Deluge 1.3 'Derbyshire' Firmware
Hands-On Demo"). The 1.3 firmware reworked the arpeggiator into "Arp 2.0" and,
crucially, made three step modifiers **independent or combinable**:

  * **probability** — each step triggers with a per-step chance (Bernoulli per
    pass, not a global "randomise" switch).
  * **iteration** — a step repeats its note N times inside the same step
    window (a ratchet, but on the arp step rather than the drum grid).
  * **fill** — a step only sounds on every Nth pass of the pattern, at an
    adjustable phase (the classic "fill every 4th bar" condition).
  * plus a **randomizer menu** with velocity spread and probability options.

Each dimension is applied in a fixed order that makes combination musically
sensible: fill gates whole passes (pattern-level), probability gates the step
within a pass, iteration subdivides the surviving step. Velocity spread is
sampled per emitted note, so a ratcheted step gets a little internal life
instead of a machine-gun repeat.

Timing is absolute ticks (480 PPQ), matching the engine's `MusicEvent`
convention: `Arp2.pattern_to_events()` returns plain dicts with
`pitch/start/end/velocity` ready to become MusicEvents.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
import numpy as np

ORDERS = ("up", "down", "updown", "downup", "played", "random",
          "converge", "diverge")


@dataclass
class ArpStep:
    """One arp step. `degree` indexes the expanded note pool."""
    degree: int = 0
    octave: int = 0
    probability: float = 1.0
    iteration: int = 1
    fill: int = 0            # 0 = always; N = only on every Nth pass
    fill_offset: int = 0
    velocity: float = 0.8
    gate: float = 0.85
    transpose: int = 0       # semitones

    def copy(self) -> "ArpStep":
        return replace(self)


@dataclass
class ArpNote:
    pitch: int
    start: int
    end: int
    velocity: int

    def as_dict(self) -> dict:
        return {"pitch": self.pitch, "start": self.start, "end": self.end,
                "velocity": self.velocity}


def build_pool(notes: list[int], octaves: int = 1) -> list[int]:
    """Expand a held chord over `octaves`, ordered ascending."""
    out: list[int] = []
    for o in range(max(1, octaves)):
        out.extend(n + 12 * o for n in sorted(notes))
    return out


def order_indices(mode: str, n: int) -> list[int]:
    """Index order over the pool for the arp direction modes."""
    if n <= 0:
        return []
    if mode == "up":
        idx = list(range(n))
    elif mode == "down":
        idx = list(range(n - 1, -1, -1))
    elif mode == "updown":
        idx = list(range(n)) + list(range(n - 2, 0, -1))
    elif mode == "downup":
        idx = list(range(n - 1, -1, -1)) + list(range(1, n - 1))
    elif mode == "converge":
        idx = []
        lo, hi = 0, n - 1
        while lo <= hi:
            idx.append(lo)
            if hi != lo:
                idx.append(hi)
            lo, hi = lo + 1, hi - 1
    elif mode == "diverge":
        idx = order_indices("converge", n)[::-1]
    else:  # "played" / "random" handled by caller (pool order / RNG)
        idx = list(range(n))
    return idx


class Arp2:
    """Probability + iteration + fill arpeggiator over a held chord."""

    def __init__(self, notes: list[int], steps: list[ArpStep] | None = None,
                 order: str = "up", octaves: int = 1, step_ticks: int = 480,
                 seed: int = 0):
        self.notes = sorted(notes)
        self.pool = build_pool(self.notes, octaves)
        self.order = order if order in ORDERS else "up"
        self.step_ticks = int(step_ticks)
        self.rng = np.random.default_rng(seed)
        self.steps = steps or [ArpStep(degree=d) for d in
                               order_indices(self.order, len(self.pool))]

    # ------------------------------------------------------------------ helpers
    def _pitch(self, step: ArpStep) -> int:
        if self.order in ("random", "played"):
            if self.order == "random":
                idx = int(self.rng.integers(0, len(self.pool)))
            else:
                idx = 0
        else:
            seq = order_indices(self.order, len(self.pool))
            idx = seq[step.degree % len(seq)]
        return int(self.pool[idx % len(self.pool)]) + 12 * step.octave + step.transpose

    def _velocity(self, step: ArpStep, spread: float) -> int:
        if spread <= 0.0:
            v = step.velocity
        else:
            # triangular spread around the programmed velocity
            jitter = (self.rng.random() + self.rng.random() - 1.0) * spread
            v = step.velocity + jitter
        return int(np.clip(round(v * 127), 1, 127))

    # -------------------------------------------------------------- generation
    def render(self, cycles: int = 1, velocity_spread: float = 0.0,
               start_tick: int = 0) -> list[ArpNote]:
        """Render `cycles` passes of the pattern into absolute-tick notes.

        Order of gating (independent, combinable):
          1. fill   — pattern-level: does this pass run this step at all?
          2. probability — step-level Bernoulli draw
          3. iteration   — surviving step subdivided into N equal notes
        """
        out: list[ArpNote] = []
        n_steps = max(1, len(self.steps))
        for c in range(max(0, cycles)):
            for si, step in enumerate(self.steps):
                if step.fill > 0:
                    if (c - step.fill_offset) % step.fill != 0:
                        continue
                if step.probability < 1.0 and self.rng.random() >= step.probability:
                    continue
                k = max(1, int(step.iteration))
                sub = self.step_ticks / k
                base = start_tick + (c * n_steps + si) * self.step_ticks
                pitch = self._pitch(step)
                for it in range(k):
                    s = int(round(base + it * sub))
                    e = int(round(base + (it + 1) * sub * step.gate))
                    if e <= s:
                        e = s + 1
                    out.append(ArpNote(pitch, s, e, self._velocity(step, velocity_spread)))
        return out

    def pattern_to_events(self, cycles: int = 2, velocity_spread: float = 0.0,
                          start_tick: int = 0) -> list[dict]:
        return [e.as_dict() for e in self.render(cycles, velocity_spread, start_tick)]

    # ------------------------------------------------------------- randomiser
    def randomize(self, probability_range: tuple[float, float] = (0.5, 1.0),
                  velocity_range: tuple[float, float] = (0.5, 1.0),
                  fill_range: tuple[int, int] = (0, 4),
                  iteration_range: tuple[int, int] = (1, 3),
                  keep_degrees: bool = True) -> list[ArpStep]:
        """Mutate per-step probability / velocity / fill / iteration in place.

        Mirrors the firmware's randomizer menu: velocity spread and
        probability are the headline options, fill and iteration are the
        pattern-shape options.
        """
        new: list[ArpStep] = []
        for s in self.steps:
            n = s.copy()
            n.probability = float(self.rng.uniform(*probability_range))
            n.velocity = float(self.rng.uniform(*velocity_range))
            n.fill = int(self.rng.integers(fill_range[0], fill_range[1] + 1))
            n.fill_offset = int(self.rng.integers(0, max(1, n.fill))) if n.fill else 0
            n.iteration = int(self.rng.integers(iteration_range[0], iteration_range[1] + 1))
            if not keep_degrees:
                n.degree = int(self.rng.integers(0, len(self.pool)))
            new.append(n)
        self.steps = new
        return new


def demo() -> None:
    chord = [60, 64, 67, 71]  # Cmaj7
    step = 480

    # ---- 1. direction modes are the expected permutations of an 8-note pool
    pool = build_pool(chord, 2)
    up = order_indices("up", len(pool))
    dn = order_indices("down", len(pool))
    ud = order_indices("updown", len(pool))
    print(f"pool={len(pool)} up={up[:4]} down={dn[:4]} updown_len={len(ud)}")
    assert dn == up[::-1] and len(ud) == 2 * len(pool) - 2

    # ---- 2. iteration subdivides one step into N equally spaced notes
    a = Arp2(chord, steps=[ArpStep(degree=0, iteration=4, gate=1.0)])
    ev = a.render(cycles=1)
    starts = [e.start for e in ev]
    print(f"iteration=4 -> {len(ev)} notes, starts={starts}")
    assert len(ev) == 4 and starts == [0, 120, 240, 360]
    assert {e.pitch for e in ev} == {60}

    # ---- 3. fill: step only sounds every 2nd pass
    b = Arp2(chord, steps=[ArpStep(degree=0, fill=2)], seed=1)
    ev_fill = b.render(cycles=4)
    passes = [sum(1 for e in ev_fill if e.start // step == c) for c in range(4)]
    print(f"fill=2 per-pass notes over 4 passes: {passes}")
    assert passes == [1, 0, 1, 0]

    # ---- 4. probability ~= p over many passes (seeded)
    p = 0.3
    c = Arp2(chord, steps=[ArpStep(degree=0, probability=p)], seed=42)
    hits = len(c.render(cycles=400))
    rate = hits / 400
    print(f"probability={p:.1f} -> measured rate {rate:.3f} over 400 passes")
    assert 0.22 < rate < 0.38

    # ---- 5. independent combination: probability 1 + iteration 2 + fill 2
    d = Arp2(chord, steps=[ArpStep(degree=0, probability=1.0, iteration=2, fill=2)])
    ev_d = d.render(cycles=4)
    counts = [sum(1 for e in ev_d if e.start // step == i) for i in range(4)]
    print(f"p=1 iter=2 fill=2 -> notes per pass {counts}")
    assert counts == [2, 0, 2, 0]

    # ---- 6. velocity spread stays inside the programmed window and varies
    e = Arp2(chord, steps=[ArpStep(degree=0, iteration=8, velocity=0.75)], seed=7)
    vels = [n.velocity for n in e.render(cycles=1, velocity_spread=0.3)]
    print(f"velocity spread 0.3: n={len(vels)} min={min(vels)} max={max(vels)} "
          f"distinct={len(set(vels))}")
    assert 40 <= min(vels) < max(vels) <= 127 and len(set(vels)) > 2

    # ---- 7. randomizer produces a playable, non-empty pattern
    f = Arp2(chord, seed=11)
    f.randomize()
    ev2 = f.render(cycles=4)
    print(f"randomized: steps={len(f.steps)} notes over 4 passes={len(ev2)}, "
          f"pitches={sorted({n.pitch for n in ev2})}")
    assert len(ev2) > 0
    assert all(n.pitch % 12 in {n % 12 for n in chord} for n in ev2)
    assert all(n.end > n.start for n in ev2)
    print("demo OK")


if __name__ == "__main__":
    demo()
