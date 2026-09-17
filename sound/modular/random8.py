"""Eight-channel controllable random-voltage generator — Mylar Melodies / Befaco
"RANDOM8" style.

Replicable logic from the Sound On Sound review "Mylar Melodies RANDOM8"
(September 2026 issue, reviewed by David Glasper) — Alex Theakston's debut module,
made with Befaco: eight channels of highly controllable random voltage in 8HP.

Published per-channel controls, all modelled here:
  * **Trigs / Dividr** — a channel outputs a new voltage on each trigger, but
    ``Dividr`` makes it "wait for up to eight trigs before generating a new
    voltage"; trig inputs cascade down the module so one input triggers every
    channel below it until another input is patched.
  * **Attenuation knob per channel** — scales the output to a usable range, and
    doubles as the editor for the menu parameters.
  * **Prob** — probability that the channel produces a *new* voltage.
  * **Style** — a menu of *kinds* of random (each useful for a different job):
    uniform, triangle-weighted, bell/centre-weighted, stepped walk, drift
    (random walk), and a burst style.
  * **Offset** — raises the *minimum* voltage, narrowing the range.
  * **Scale** — 15 scales plus unquantised; "the quantisation happens **after**
    attenuation", so you always get stepped voltages unless Slide is dialled in.
  * **Slide** — adds slewing (portamento) between voltages for LFO-like movement.
  * **Steps** — the loop length, up to 32 steps.
  * **Looping per channel** — press once to loop, again to "allow it to evolve",
    twice to return to fully random.  Modelled as three modes:
    ``random`` → ``evolve`` → ``loop``.

What is replicated here:
- ``Random8`` with the eight channels and their full parameter set, the cascading
  trigger bus, the quantise-after-attenuation order, slew/slide, and per-channel
  loop length up to 32.
- ``SCALES_15``: fifteen scales spanning Western, maqam, melakarta and pentatonic
  families plus unquantised — matching the module's documented organisation (the
  RANDOM8 manual organises these into groups; the reviewer notes the module ships
  15 scales plus unquantised).
- ``STYLES``: six random distributions with distinct statistics.

Not replicated: the physical panel, 8HP hardware, the coloured-LED scale
indication (the review's one complaint), and the >10,000-word hardware manual.

Usage:
    from sound.modular.random8 import Random8, STYLES, SCALES_15

    r8 = Random8(seed=42)
    r8.channel(0).scale = "minor_pentatonic"     # quantised after attenuation
    r8.channel(1).style = "drift"
    vals = r8.process(n_trigs=16)                # -> 8 x n_trigs matrix
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

__all__ = [
    "STYLES",
    "SCALES_15",
    "RandomChannel",
    "Random8",
    "quantize_cv",
]

MAX_STEPS = 32
NUM_CHANNELS = 8
LOOP_MODES = ("random", "evolve", "loop")

# Random-voltage styles: name -> (distribution kind, description).
STYLES: Dict[str, str] = {
    "uniform":  "flat over the full range",
    "triangle": "triangular (mid-favouring)",
    "bell":     "bell/centre-weighted (musical, stays near the middle)",
    "steps":    "quantised stepped walk (small integer jumps)",
    "drift":    "random walk with slow slew (very LFO-like)",
    "burst":    "occasional extreme excursions",
}

# Fifteen scales, organised as the module documents them (Western diatonic,
# Arabic maqam, Indian melakarta, Japanese pentatonic, plus the quarter/semi/
# whole-tone 'Full' category).  Values are semitone degrees from the root;
# quarter-tone scales use half-semitone units (24-TET).
SCALES_15: Dict[str, Tuple[float, ...]] = {
    # Western diatonic
    "major":            (0, 2, 4, 5, 7, 9, 11),
    "natural_minor":    (0, 2, 3, 5, 7, 8, 10),
    "dorian":           (0, 2, 3, 5, 7, 9, 10),
    "mixolydian":       (0, 2, 4, 5, 7, 9, 10),
    # Arabic maqam
    "maqam_rast":       (0, 2, 3.5, 5, 7, 9, 10.5),
    "maqam_bayati":     (0, 1.5, 3, 5, 7, 8, 10),
    "maqam_hijaz":      (0, 1, 4, 5, 7, 8, 10),
    # Indian melakarta
    "mayamalavagowla":  (0, 1, 4, 5, 7, 8, 11),
    "mecakalyani":      (0, 2, 4, 6, 7, 9, 11),
    "hanumatodi":       (0, 1, 3, 5, 7, 8, 10),
    # Japanese pentatonics
    "hirajoshi":        (0, 2, 3, 7, 8),
    "in_sen":           (0, 1, 5, 7, 10),
    "yo":               (0, 2, 5, 7, 9),
    # 'Full' category
    "whole_tone":       (0, 2, 4, 6, 8, 10),
    "quarter_tone":     (0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 5.5,
                         6, 6.5, 7, 7.5, 8, 8.5, 9, 9.5, 10, 10.5, 11, 11.5),
}


def quantize_cv(value: float, scale: Optional[str], root: float = 0.0,
                span: float = 12.0) -> float:
    """Snap a 0..1 CV value to the nearest member of a scale.

    The RANDOM8 quantises *after* attenuation, so this takes the already-scaled
    value and reports it in the same 0..1 space.  ``span`` is how many semitones
    the full 0..1 range covers (12 = one octave).  ``None`` = unquantised.
    """
    if scale is None:
        return float(value)
    if scale not in SCALES_15:
        raise ValueError(f"unknown scale {scale!r}; use one of {sorted(SCALES_15)}")
    degrees = SCALES_15[scale]
    v = float(value) * span + root                     # in semitones
    # build a pool over +/- 2 octaves and pick the nearest degree
    pool = []
    for octave in range(-3, 4):
        for d in degrees:
            pool.append(d + 12.0 * octave)
    best = min(pool, key=lambda d: abs(d - v))
    return (best - root) / span


@dataclass
class RandomChannel:
    """One of the eight RANDOM8 channels."""

    index: int = 0
    attenuate: float = 1.0          # output scaling 0..1 (the panel knob)
    dividr: int = 1                 # wait for 1..8 trigs before a new voltage
    probability: float = 1.0        # chance a new voltage is generated
    style: str = "uniform"
    offset: float = 0.0             # raises the minimum voltage (0..1)
    scale: Optional[str] = None     # None = unquantised
    slide: float = 0.0              # 0..1 slew amount
    steps: int = 32                 # loop length, up to 32
    loop_mode: str = "random"       # random | evolve | loop
    seed: int = 0

    def __post_init__(self):
        if self.style not in STYLES:
            raise ValueError(f"style must be one of {sorted(STYLES)}")
        if not 1 <= int(self.steps) <= MAX_STEPS:
            raise ValueError(f"steps must be 1..{MAX_STEPS}")
        if not 1 <= int(self.dividr) <= 8:
            raise ValueError("dividr must be 1..8")
        if self.loop_mode not in LOOP_MODES:
            raise ValueError(f"loop_mode must be one of {LOOP_MODES}")
        if self.scale is not None and self.scale not in SCALES_15:
            raise ValueError(f"unknown scale {self.scale!r}")
        self._state = 0.5
        self._buffer: List[float] = []
        self._cursor = 0

    # ------------------------------------------------------------------ modes
    def cycle_loop_mode(self) -> str:
        """Advance random -> evolve -> loop -> random (the button's behaviour)."""
        i = LOOP_MODES.index(self.loop_mode)
        self.loop_mode = LOOP_MODES[(i + 1) % len(LOOP_MODES)]
        if self.loop_mode == "loop" and self._buffer:
            self._cursor = 0
        return self.loop_mode

    def enable_looping(self, mode: str) -> None:
        """Set the loop mode explicitly."""
        if mode not in LOOP_MODES:
            raise ValueError(f"loop_mode must be one of {LOOP_MODES}")
        self.loop_mode = mode

    # ------------------------------------------------------------------ draw
    def _draw_style(self, rng: np.random.Generator) -> float:
        """One raw 0..1 draw from the selected style distribution."""
        s = self.style
        if s == "uniform":
            return float(rng.uniform(0.0, 1.0))
        if s == "triangle":
            return float(np.mean(rng.uniform(0.0, 1.0, 2)))
        if s == "bell":
            return float(np.clip(0.5 + rng.normal(0.0, 0.16), 0.0, 1.0))
        if s == "steps":
            step = rng.integers(-2, 3)                  # +/- 2 quantisation levels
            return float(np.clip(round(self._state * 8) / 8 + step / 8.0, 0.0, 1.0))
        if s == "drift":
            return float(np.clip(self._state + rng.normal(0.0, 0.12), 0.0, 1.0))
        if s == "burst":
            if rng.random() < 0.15:
                return float(rng.choice([0.0, 1.0]))
            return float(np.clip(0.5 + rng.normal(0.0, 0.05), 0.0, 1.0))
        raise ValueError(s)

    def next_value(self, rng: np.random.Generator, trig: bool = True) -> float:
        """Produce the channel's output for one trigger.

        Order of operations (as documented): draw -> offset -> attenuate ->
        quantise.  Looping replays a fixed buffer; "evolve" replays it but keeps
        drawing (so it changes over time).
        """
        if not trig:
            return self._last_output()

        if self.loop_mode == "loop" and self._buffer:
            raw = self._buffer[self._cursor % len(self._buffer)]
            self._cursor += 1
        else:
            if rng.random() <= self.probability:
                raw = self._draw_style(rng)
                self._state = raw
            else:
                raw = self._state
            if self.loop_mode == "evolve":
                self._buffer.append(raw)
                self._buffer = self._buffer[-self.steps:]
        self._raw = float(raw)
        return self._last_output()

    def _last_output(self) -> float:
        raw = float(getattr(self, "_raw", 0.5))
        # Offset raises the minimum; attenuate scales the resulting range.
        shifted = self.offset + raw * (1.0 - self.offset)
        scaled = shifted * self.attenuate
        # Quantisation happens AFTER attenuation (documented behaviour).
        return quantize_cv(min(1.0, max(0.0, scaled)), self.scale)

    def apply_slide(self, values: np.ndarray, sr: int,
                    max_time: float = 0.5) -> np.ndarray:
        """Slew a value sequence (Slide control) — returns an interpolated curve."""
        if self.slide <= 0.0 or values.size < 2:
            return values
        tau = max(1e-3, self.slide * max_time)
        a = 1.0 - np.exp(-1.0 / (tau * sr))
        out = np.empty_like(values)
        y = values[0]
        for i, v in enumerate(values):
            y += a * (v - y)
            out[i] = y
        return out


class Random8:
    """Eight-channel random-voltage generator with cascading triggers.

    Args:
        seed: RNG seed.
        styles / scales: per-channel overrides applied after construction.
    """

    def __init__(self, seed: int = 0, n_channels: int = NUM_CHANNELS):
        self.seed = int(seed)
        self.rng = np.random.default_rng(self.seed)
        self.channels: List[RandomChannel] = [
            RandomChannel(index=i, seed=self.seed + i) for i in range(n_channels)]
        self._trig_count = 0

    # ------------------------------------------------------------- accessors
    def channel(self, index: int) -> RandomChannel:
        """Fetch a channel by index (0..7)."""
        return self.channels[int(index)]

    def set_preset(self, index: int, **kwargs) -> RandomChannel:
        """Configure one channel in bulk (e.g. ``scale="hirajoshi", style="drift"``)."""
        ch = self.channels[int(index)]
        for k, v in kwargs.items():
            if not hasattr(ch, k):
                raise AttributeError(k)
            setattr(ch, k, v)
        ch.__post_init__()
        return ch

    def snapshot(self) -> Dict[str, object]:
        """Current parameter state (for saving a preset)."""
        return {f"ch{c.index}": {
            "attenuate": c.attenuate, "dividr": c.dividr,
            "probability": c.probability, "style": c.style,
            "offset": c.offset, "scale": c.scale, "slide": c.slide,
            "steps": c.steps, "loop_mode": c.loop_mode,
        } for c in self.channels}

    # ------------------------------------------------------------------- run
    def process(self, n_trigs: int = 16,
                trigs: Optional[Dict[int, Sequence[int]]] = None,
                cascading: bool = True) -> np.ndarray:
        """Generate values for ``n_trigs`` trigger events.

        Args:
            n_trigs: number of trigger events.
            trigs: optional ``{channel_index: [bool per event]}`` map.  Without it,
                every channel receives every trigger.
            cascading: when True and a channel has no explicit trig map, it is
                triggered by the nearest *lower* patched channel (the module's
                cascading trigger inputs).

        Returns:
            ``(n_channels, n_trigs)`` array of output voltages in 0..1.
        """
        out = np.zeros((len(self.channels), int(n_trigs)))
        for ci, ch in enumerate(self.channels):
            pending = 0
            # Resolve this channel's trigger source once: its own patch, else the
            # nearest patched channel *below* it (the module's cascading inputs),
            # else every trigger.
            if trigs is None:
                src = None
            elif ci in trigs:
                src = ci
            else:
                below = [k for k in trigs if k < ci]
                src = max(below) if (cascading and below) else None
            pattern = None if src is None else list(trigs[src])
            for t in range(int(n_trigs)):
                trig = True if pattern is None else (
                    bool(pattern[t]) if t < len(pattern) else True)
                pending += 1 if trig else 0
                new = pending >= ch.dividr
                if new:
                    pending = 0
                out[ci, t] = ch.next_value(self.rng, trig=new)
        self._trig_count += int(n_trigs)
        return out

    def cv_stream(self, n_trigs: int = 16, samples_per_trig: int = 256,
                  sr: int = 44100) -> np.ndarray:
        """Full-rate CV streams with per-channel Slide applied."""
        values = self.process(n_trigs)
        out = np.empty((len(self.channels), n_trigs * samples_per_trig))
        for ci, ch in enumerate(self.channels):
            up = np.repeat(values[ci], samples_per_trig)
            out[ci] = ch.apply_slide(up, sr, max_time=1.0)
        return out


def demo() -> str:
    """Prove styles differ, the attenuate/offset/quantise order, slide and loops."""
    print(f"channels: {NUM_CHANNELS}  scales: {len(SCALES_15)} (+ unquantised)  "
          f"styles: {len(STYLES)}  max loop steps: {MAX_STEPS}")
    print("scales:", ", ".join(sorted(SCALES_15)))
    assert len(SCALES_15) == 15 and len(STYLES) == 6

    # --- each style has distinct statistics: spread, jumpiness, tail behaviour
    stats = {}
    for style in STYLES:
        r8 = Random8(seed=3)
        r8.set_preset(0, style=style)
        vals = r8.process(400)[0]
        jumps = np.abs(np.diff(vals))
        extreme = float(np.mean((vals > 0.95) | (vals < 0.05)))
        stats[style] = {"sd": float(vals.std()),
                        "jump": float(jumps.mean()),
                        "extreme": extreme}
        print(f"  style {style:9s}: sd={stats[style]['sd']:.3f} "
              f"mean|jump|={stats[style]['jump']:.3f} "
              f"extremes={stats[style]['extreme']:.3f}  ({STYLES[style]})")

    # flat distribution is wider than a centre-weighted one
    assert stats["uniform"]["sd"] > stats["bell"]["sd"]
    # the drift walk moves slowly between triggers (that is what makes it LFO-like)
    assert stats["drift"]["jump"] < stats["uniform"]["jump"]
    # burst spends time pinned at the extremes
    assert stats["burst"]["extreme"] > stats["bell"]["extreme"]
    assert stats["burst"]["extreme"] >= stats["uniform"]["extreme"] / 2.0

    # --- quantise happens AFTER attenuation: at 0.5 attenuation a quantised
    #     channel produces fewer distinct values than an unquantised one
    r8 = Random8(seed=11)
    r8.set_preset(0, attenuate=0.35, scale="hirajoshi")
    r8.set_preset(1, attenuate=0.35, scale=None)
    out = r8.process(64)
    n_q = len(np.unique(np.round(out[0], 6)))
    n_u = len(np.unique(np.round(out[1], 6)))
    print(f"quantise after attenuation: hirajoshi -> {n_q} distinct values, "
          f"unquantised -> {n_u}")
    assert n_q < n_u
    # every quantised value must already sit exactly on a scale degree, i.e. the
    # quantiser is idempotent on its own output
    again = np.array([quantize_cv(v, "hirajoshi") for v in out[0]])
    ok = bool(np.allclose(out[0], again, atol=1e-12))
    print(f"  all {n_q} quantised values are fixed points of the hirajoshi "
          f"quantiser: {ok}")
    assert ok
    # and they must be a subset of the full degree grid in CV space
    grid = {round(quantize_cv(v, "hirajoshi"), 12) for v in np.linspace(0.0, 1.0, 2000)}
    print(f"  distinct degrees reachable in 0..1: {len(grid)} "
          f"(hirajoshi has {len(SCALES_15['hirajoshi'])} per octave, "
          f"span=12 semitones = 1 octave)")
    assert {round(v, 12) for v in out[0]} <= grid

    # --- Offset raises the minimum
    r8 = Random8(seed=5)
    r8.set_preset(0, offset=0.0, attenuate=1.0)
    r8.set_preset(1, offset=0.6, attenuate=1.0)
    o = r8.process(200)
    print(f"offset: ch0 min={o[0].min():.3f}  ch1 min={o[1].min():.3f} "
          f"(offset 0.6 lifts the floor)")
    assert o[1].min() > o[0].min()
    assert o[1].max() <= 1.0

    # --- Attenuation scales
    r8 = Random8(seed=5)
    r8.set_preset(0, attenuate=1.0)
    r8.set_preset(1, attenuate=0.25)
    a = r8.process(200)
    print(f"attenuation: full range max={a[0].max():.3f}, 0.25 -> "
          f"{a[1].max():.3f}")
    assert a[1].max() < a[0].max()

    # --- Dividr: wait for N trigs before a new voltage
    for div in (1, 4, 8):
        r8 = Random8(seed=7)
        r8.set_preset(0, dividr=div, scale=None, style="uniform")
        vals = r8.process(16)[0]
        changes = int(np.sum(np.diff(vals) != 0))
        print(f"  dividr {div}: {changes} value changes over 16 trigs "
              f"(~{16 // div} expected)")
        assert changes <= 16 // div

    # --- Probability
    r8 = Random8(seed=8)
    r8.set_preset(0, probability=0.25, scale=None, style="uniform")
    vals = r8.process(80)[0]
    print(f"probability 0.25 -> {int(np.sum(np.diff(vals) != 0))} new voltages "
          f"over 80 trigs")
    assert int(np.sum(np.diff(vals) != 0)) < 40

    # --- cascading triggers: patching channel 3 also fires 4..7
    trig_map = {0: [1] * 8, 3: [1, 0, 1, 0, 1, 0, 1, 0]}
    r8 = Random8(seed=9)
    for c in r8.channels:
        c.scale = None
        c.style = "uniform"
    out = r8.process(8, trigs=trig_map, cascading=True)
    ch4_changes = int(np.sum(np.diff(out[4]) != 0))
    print(f"cascading trigs: channel 4 fires on channel 3's pattern -> "
          f"{ch4_changes} changes over 8 events")
    assert ch4_changes > 0

    # --- looping modes
    r8 = Random8(seed=13)
    ch = r8.channel(0)
    ch.style, ch.scale = "uniform", None
    print(f"loop mode cycle: {ch.loop_mode} -> ", end="")
    modes = [ch.cycle_loop_mode()]
    modes.append(ch.cycle_loop_mode())
    modes.append(ch.cycle_loop_mode())
    print(" -> ".join(modes))
    assert modes == ["evolve", "loop", "random"]

    ch.loop_mode = "loop"
    ch.steps = 8
    ch._buffer = list(np.linspace(0.0, 1.0, 8))
    ch._cursor = 0
    looped = r8.process(16)[0]
    print(f"looped channel repeats its 8-step buffer: "
          f"{np.allclose(looped[:8], looped[8:16])}")
    assert np.allclose(looped[:8], looped[8:16])

    ch.loop_mode = "random"
    ch._buffer, ch._cursor = [], 0
    free = r8.process(16)[0]
    print(f"free-running differs from looped: {not np.allclose(free, looped)}")
    assert not np.allclose(free, looped)
    ch.steps = 32

    # --- slide slew
    r8 = Random8(seed=17)
    c = r8.channel(0)
    c.style, c.scale = "uniform", None
    vals = r8.process(8)[0]
    c.slide = 1.0                       # Slide fully up
    stream = c.apply_slide(np.repeat(vals, 64), 44100, max_time=0.05)
    steps = np.abs(np.diff(stream))
    hard = np.abs(np.diff(np.repeat(vals, 64)))
    print(f"slide: max jump with slide up = {steps.max():.5f}, "
          f"stepwise = {hard.max():.5f} (each 64-sample block moves gradually)")
    assert steps.max() < hard.max() / 10.0

    c.slide = 0.0
    noslide = c.apply_slide(np.repeat(vals, 64), 44100, max_time=0.05)
    print(f"slide off = raw steps unchanged: {np.allclose(noslide, np.repeat(vals, 64))}")
    assert np.allclose(noslide, np.repeat(vals, 64))

    full = r8.cv_stream(n_trigs=4, samples_per_trig=64)
    print(f"cv_stream: shape={full.shape} range="
          f"{full.min():.3f}..{full.max():.3f}")
    assert full.shape == (8, 256)
    print("  random8 demo OK")
    return "ok"


if __name__ == "__main__":
    demo()
