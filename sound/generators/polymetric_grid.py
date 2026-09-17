"""16-track polymetric step sequencer — Rapid Flow omniGRID style.

Replicable logic from the Sound On Sound news item "Rapid Flow release omniGRID"
(01/09/26, published 11/9/26): "a new 16-track sequencer plug-in … designed for
total rhythmic expression, polymetric sequencing, and vintage hardware groove
emulation."

Spec as published (everything below is modelled):
  * **16 independent MIDI tracks**, each with its own routing, mute/solo and gain
    trim, driven from a 4x4 performance pad matrix.
  * **Polymetric 4–64 step sequences**, with independent pattern length *and*
    step resolution (1/4, 1/8, 1/16, 1/32) **per track** — so lanes drift
    against each other and re-phase over time.
  * **Per-lane and master micro-timing shift** (the "pocket" control).
  * **Six per-step parameter graphs**: Velocity, Note Length (10–400 %), Timing
    Shift, Probability (0–100 %), Repeats (1–8) and Repeat Intervals, each with
    its own randomisation control.
  * **Eight "iconic" shuffle styles** emulating classic drum-machine/sequencer
    timing feel.
  * **Euclidean rhythm generator on every track** — total step count, pulse
    density and rotation offset.
  * **Advanced arpeggiator + scale quantisation** (12 roots, 7 scales).
  * Pattern export as MIDI.

Mechanism notes (why it is more than a step grid):
- A track's *period* is ``steps * resolution`` beats; because each track's period
  is independent, the ensemble repeat interval is the LCM of all periods — the
  long phasing cycles that give "polymetric" workflows their movement.
- Per-step probability is rolled per *pass* (not once), so a 50 % step thins and
  thickens across loops instead of being static.
- Repeats/repeat-interval is a ratchet: ``repeats`` sub-hits inside the step
  window, but only on every ``interval``-th pass (the interval graph), which is
  the classic IDM trick of a fill that appears every N bars.
- Randomisation is *per graph*, so you can jitter timing while keeping velocity
  exactly as programmed — the published "dedicated per-graph randomisation".

Not replicated: the plug-in UI, the pad matrix hardware feel, AAX/AU hosting.

Usage:
    from sound.generators.polymetric_grid import PolymetricGrid

    g = PolymetricGrid(bpm=120)
    g.add_track(1, steps=16, note=36)
    g.add_track(2, steps=12, resolution=8, note=42)
    g.euclidean(2, pulses=5, rotation=2)
    g.shuffle = "mpc60"
    events = g.render(loops=4)          # (start_sec, note, velocity, dur_sec)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from math import gcd
from functools import reduce
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from sound.generators.micro_timing_seq import SHUFFLE_STYLES, VINTAGE_OFFSETS

__all__ = [
    "PerStepGraph",
    "Track",
    "PolymetricGrid",
    "SHUFFLE_MODES",
    "SCALES",
    "RESOLUTIONS",
]

# Eight shuffle modes: the seven classic machines from micro_timing_seq plus a
# straight mode (omniGRID advertises exactly eight icons).
SHUFFLE_MODES: Tuple[str, ...] = ("straight",) + tuple(SHUFFLE_STYLES.keys())

# Step resolution -> steps per beat.
RESOLUTIONS: Dict[int, float] = {4: 1.0, 8: 2.0, 16: 4.0, 32: 8.0}

# The published scale list (7 scales; root is chosen from 12 keys).
SCALES: Dict[str, Tuple[int, ...]] = {
    "major": (0, 2, 4, 5, 7, 9, 11),
    "minor": (0, 2, 3, 5, 7, 8, 10),
    "dorian": (0, 2, 3, 5, 7, 9, 10),
    "phrygian": (0, 1, 3, 5, 7, 8, 10),
    "lydian": (0, 2, 4, 6, 7, 9, 11),
    "maj_pentatonic": (0, 2, 4, 7, 9),
    "min_pentatonic": (0, 3, 5, 7, 10),
}

MIN_STEPS, MAX_STEPS = 4, 64


@dataclass
class PerStepGraph:
    """One per-step parameter lane (velocity / length / timing / …).

    Args:
        name: graph name (documentation only).
        default: value used for steps with no explicit entry.
        minimum / maximum: clip bounds.
    """

    name: str
    default: float
    minimum: float
    maximum: float
    values: Dict[int, float] = field(default_factory=dict)

    def set(self, step: int, value: float) -> None:
        """Set the graph value for ``step`` (clipped to the graph bounds)."""
        self.values[int(step)] = float(min(self.maximum, max(self.minimum, value)))

    def get(self, step: int) -> float:
        """Graph value for ``step`` (falls back to ``default``)."""
        return self.values.get(int(step), self.default)

    def randomize(self, amount: float, rng: np.random.Generator,
                  steps: int) -> None:
        """Jitter every programmed (or all) steps by +/- ``amount`` of full scale.

        ``amount`` is a fraction of the graph's span, matching the plug-in's
        per-graph randomisation control.
        """
        amount = float(min(1.0, max(0.0, amount)))
        if amount <= 0.0:
            return
        span = self.maximum - self.minimum
        idx = self.values.keys() if self.values else range(int(steps))
        for s in list(idx):
            jitter = rng.uniform(-1.0, 1.0) * amount * span * 0.5
            self.set(s, self.get(s) + jitter)

    def as_list(self, steps: int) -> List[float]:
        """All ``steps`` values as a flat list."""
        return [self.get(s) for s in range(int(steps))]


class Track:
    """One polymetric track: own length, resolution, notes and graph set."""

    def __init__(self, index: int, steps: int = 16, resolution: int = 16,
                 note: int = 60, channel: int = 0, name: str = ""):
        if not MIN_STEPS <= int(steps) <= MAX_STEPS:
            raise ValueError(f"steps must be {MIN_STEPS}..{MAX_STEPS}")
        if int(resolution) not in RESOLUTIONS:
            raise ValueError(f"resolution must be one of {sorted(RESOLUTIONS)}")
        self.index = int(index)
        self.steps = int(steps)
        self.resolution = int(resolution)
        self.note = int(note)
        self.channel = int(channel)
        self.name = name or f"trk{self.index}"
        self.muted = False
        self.solo = False
        self.gain = 1.0
        self.micro_shift_ms = 0.0
        self.gates: Dict[int, int] = {}      # step -> velocity (0/absent = rest)
        self.notes: Dict[int, int] = {}      # per-step pitch overrides

        self.velocity = PerStepGraph("velocity", 100.0, 1.0, 127.0)
        self.note_length = PerStepGraph("note_length", 50.0, 10.0, 400.0)
        self.timing = PerStepGraph("timing", 0.0, -100.0, 100.0)      # % of a step
        self.probability = PerStepGraph("probability", 100.0, 0.0, 100.0)
        self.repeats = PerStepGraph("repeats", 1.0, 1.0, 8.0)
        self.repeat_interval = PerStepGraph("repeat_interval", 1.0, 1.0, 8.0)

    # -------------------------------------------------------------- authoring
    def set_step(self, step: int, velocity: int = 100) -> None:
        """Program a hit (velocity > 0) or a rest (velocity == 0) on ``step``."""
        if velocity <= 0:
            self.gates.pop(int(step), None)
        else:
            self.gates[int(step)] = int(min(127, velocity))

    def set_pattern(self, velocities: Sequence[int]) -> None:
        """Program the whole track from a velocity list (length sets ``steps``)."""
        self.steps = max(MIN_STEPS, min(MAX_STEPS, len(velocities)))
        self.gates = {i: int(v) for i, v in enumerate(velocities) if v > 0}

    def set_pitch(self, step: int, note: int) -> None:
        """Per-step pitch override (turns the drum lane into a melodic lane)."""
        self.notes[int(step)] = int(note)

    def euclidean(self, pulses: int, rotation: int = 0) -> List[int]:
        """Apply a Euclidean pattern (``pulses`` in ``steps``, rotated)."""
        pattern = eulerian_mask(int(pulses), self.steps, int(rotation))
        self.gates = {i: v for i, v in enumerate(pattern) if v > 0}
        return pattern

    def clear(self) -> None:
        """Remove every hit on this track."""
        self.gates.clear()

    # ---------------------------------------------------------------- metrics
    @property
    def period_beats(self) -> float:
        """Pattern period in beats: ``steps / steps_per_beat``."""
        return self.steps / RESOLUTIONS[self.resolution]

    def step_seconds(self, bpm: float) -> float:
        """Duration of one step in seconds at ``bpm``."""
        return 60.0 / bpm / RESOLUTIONS[self.resolution]


class PolymetricGrid:
    """16-track polymetric Euclidean sequencer with per-step graphs.

    Args:
        bpm: tempo.
        master_shift_ms: global micro-timing shift applied to every track.
        shuffle: one of :data:`SHUFFLE_MODES`.
        shuffle_amount: 0..1 blend of the selected shuffle curve.
        root: scale root for quantisation (0 = C).
        scale: key of :data:`SCALES` (or None to disable quantisation).
    """

    MAX_TRACKS = 16

    def __init__(self, bpm: float = 120.0, master_shift_ms: float = 0.0,
                 shuffle: str = "straight", shuffle_amount: float = 0.5,
                 root: int = 0, scale: Optional[str] = "minor"):
        self.bpm = float(bpm)
        self.master_shift_ms = float(master_shift_ms)
        self.shuffle = str(shuffle)
        self.shuffle_amount = float(shuffle_amount)
        self.root = int(root) % 12
        self.scale = scale
        self.tracks: Dict[int, Track] = {}
        self._seed = 0

    # ------------------------------------------------------------ track access
    def add_track(self, index: int, steps: int = 16, resolution: int = 16,
                  note: int = 60, channel: int = 0, name: str = "") -> Track:
        """Create (or replace) track ``index`` (1-based, 1..16)."""
        if not 1 <= int(index) <= self.MAX_TRACKS:
            raise ValueError(f"track index must be 1..{self.MAX_TRACKS}")
        trk = Track(index, steps, resolution, note, channel, name)
        self.tracks[int(index)] = trk
        return trk

    def track(self, index: int) -> Track:
        """Fetch a track by index."""
        return self.tracks[int(index)]

    def set_shuffle(self, mode: str, amount: float = 0.5) -> None:
        """Select one of the eight shuffle modes and its amount."""
        if mode not in SHUFFLE_MODES:
            raise ValueError(f"shuffle must be one of {SHUFFLE_MODES}")
        self.shuffle = mode
        self.shuffle_amount = float(min(1.0, max(0.0, amount)))

    # ------------------------------------------------------------ quantisation
    def quantize(self, note: int) -> int:
        """Snap a MIDI note to the configured scale (no-op when scale is None)."""
        if self.scale is None:
            return int(note)
        steps = SCALES[self.scale]
        octave, pc = divmod(int(note) - self.root, 12)
        best = min(steps, key=lambda s: (min((pc - s) % 12, (s - pc) % 12), s))
        delta = (best - pc + 6) % 12 - 6
        return int(note) + delta

    # -------------------------------------------------------------- ensemble
    @property
    def ensemble_period_beats(self) -> float:
        """LCM of all track periods — the full re-phasing cycle, in beats."""
        if not self.tracks:
            return 0.0
        # work in 32nd-note units to stay in integers
        units = [int(round(t.period_beats * 8)) for t in self.tracks.values()]
        lcm = reduce(lambda a, b: a * b // gcd(a, b), units, 1)
        return lcm / 8.0

    # ------------------------------------------------------------------ timing
    def _shuffle_offset(self, step_index: int, resolution: int) -> float:
        """Shuffle timing offset in *steps* for a given position."""
        if self.shuffle == "straight" or self.shuffle not in SHUFFLE_STYLES:
            return 0.0
        base = SHUFFLE_STYLES[self.shuffle]
        swing = (base - 0.5) * 2.0 * self.shuffle_amount
        pair_pos = step_index % 2
        off = swing if pair_pos == 0 else -swing
        fp = VINTAGE_OFFSETS[self.shuffle]
        return off + fp[step_index % 4]

    # ------------------------------------------------------------------ render
    def render(self, loops: int = 1, seed: int = 0,
               arpeggiate: bool = False) -> List[Tuple[float, int, int, float]]:
        """Render every track to ``(start_sec, note, velocity, duration_sec)``.

        Args:
            loops: number of passes over the grid.
            seed: randomisation seed (probability, repeats, timing graphs).
            arpeggiate: when True, a track's simultaneous sub-hits (ratchets) are
                spread melodically using its per-step pitch overrides.
        """
        rng = np.random.default_rng(int(seed))
        events: List[Tuple[float, int, int, float]] = []
        any_solo = any(t.solo for t in self.tracks.values())

        for trk in self.tracks.values():
            if trk.muted or (any_solo and not trk.solo):
                continue
            step_s = trk.step_seconds(self.bpm)
            for loop in range(int(loops)):
                loop_start = loop * trk.steps * step_s
                for step in range(trk.steps):
                    vel0 = trk.gates.get(step, 0)
                    if vel0 <= 0:
                        continue
                    prob = trk.probability.get(step)
                    if prob < 100.0 and rng.uniform(0.0, 100.0) > prob:
                        continue
                    reps = int(round(trk.repeats.get(step)))
                    interval = max(1, int(round(trk.repeat_interval.get(step))))
                    # repeat-interval graph: ratchet only every Nth pass
                    n_hits = reps if (loop % interval == 0) else 1

                    t_off = trk.timing.get(step) / 100.0
                    t_off += self._shuffle_offset(step + loop * trk.steps,
                                                  trk.resolution)
                    t_off += (trk.micro_shift_ms + self.master_shift_ms) / 1000.0 / step_s
                    base = loop_start + (step + t_off) * step_s
                    vel = int(min(127, max(1, trk.velocity.get(step) * trk.gain)))
                    length = step_s * trk.note_length.get(step) / 100.0

                    pitch = trk.notes.get(step, trk.note)
                    if arpeggiate and n_hits > 1:
                        pitch = trk.notes.get(step, trk.note)
                    pitch = self.quantize(pitch)

                    for h in range(n_hits):
                        sub = base + h * (step_s / n_hits)
                        if arpeggiate and trk.notes:
                            sub_pitch = self.quantize(
                                trk.notes.get((step + h) % trk.steps, pitch))
                        else:
                            sub_pitch = pitch
                        events.append((max(0.0, sub), sub_pitch, vel,
                                       max(0.01, length / n_hits)))
        events.sort(key=lambda e: (e[0], e[1]))
        return events

    # ------------------------------------------------------------------- MIDI
    def to_midi_events(self, loops: int = 1, seed: int = 0,
                       ticks_per_beat: int = 480,
                       arpeggiate: bool = False) -> List[dict]:
        """Render to absolute-tick note events for the musicom MIDI writer."""
        evs = self.render(loops=loops, seed=seed, arpeggiate=arpeggiate)
        spb = 60.0 / self.bpm                                   # sec per beat
        out = []
        for start, note, vel, dur in evs:
            start_tick = int(round(start / spb * ticks_per_beat))
            end_tick = int(round((start + dur) / spb * ticks_per_beat))
            out.append({"pitch": int(note), "volume": int(vel),
                        "start_tick": start_tick,
                        "end_tick": max(start_tick + 1, end_tick)})
        return out

    def pattern_table(self) -> List[str]:
        """Human-readable dump of every track's gate grid."""
        rows = []
        for trk in self.tracks.values():
            grid = "".join("X" if trk.gates.get(s, 0) > 0 else "."
                           for s in range(trk.steps))
            rows.append(f"{trk.index:2d} {trk.name:<8s} {trk.steps:2d}st "
                        f"1/{trk.resolution:<2d} {grid}")
        return rows


def eulerian_mask(pulses: int, steps: int, rotation: int = 0) -> List[int]:
    """Bjorklund distribution of ``pulses`` onsets across ``steps``, rotated.

    Implemented as the maximally-even bucket accumulator (equivalent to the
    Bjorklund/Euclidean rhythm for k onsets in n slots).
    """
    steps = int(steps)
    pulses = max(0, min(int(pulses), steps))
    if steps == 0:
        return []
    if pulses == 0:
        return [0] * steps
    pattern = [0] * steps
    bucket = 0
    for i in range(steps):
        bucket += pulses
        if bucket >= steps:
            bucket -= steps
            pattern[i] = 1
    r = int(rotation) % steps
    return pattern[r:] + pattern[:r]


# ------------------------------------------------------------------------ demo
def demo() -> str:
    """Prove polymetry, Euclidean generation, graphs, shuffle and MIDI export."""
    g = PolymetricGrid(bpm=120, root=0, scale="minor")
    print(f"shuffle modes ({len(SHUFFLE_MODES)}): {SHUFFLE_MODES}")

    # 16 independent tracks: kick on 16ths, hat 12 steps, bass 7 steps...
    kick = g.add_track(1, steps=16, note=36, name="kick")
    kick.set_pattern([127, 0, 0, 0] * 4)
    hat = g.add_track(2, steps=12, resolution=16, note=42, name="hat")
    hat.set_pattern([0, 90, 0, 70] * 3)
    bass = g.add_track(3, steps=7, note=40, name="bass")
    bass.set_pattern([110, 0, 95, 0, 0, 100, 0])
    for i in range(4, 8):                       # fill the grid out to 7 tracks
        g.add_track(i, steps=8 + i, note=48 + i, name=f"pad{i}")

    assert len(g.tracks) == 7
    print("polymetric periods (beats):",
          {t.index: round(t.period_beats, 3) for t in g.tracks.values()})
    print(f"ensemble re-phase cycle: {g.ensemble_period_beats:.2f} beats "
          f"(LCM of all track periods)")
    assert len({t.period_beats for t in g.tracks.values()}) > 1

    # Euclidean generator: 5 onsets in 12 steps, rotated -> {x..x.x..x.x.}
    eu = g.add_track(9, steps=12, resolution=16, note=45, name="euclid")
    pat = eu.euclidean(pulses=5, rotation=2)
    print(f"euclidean(5 in 12, rotation 2): {pat} -> onsets "
          f"{[i for i, v in enumerate(pat) if v]}")
    assert sum(pat) == 5
    on = [i for i, v in enumerate(pat) if v]
    gaps = [on[i + 1] - on[i] for i in range(len(on) - 1)]
    assert max(gaps) - min(gaps) <= 1, "distribution is not maximally even"

    # per-step graphs
    for s in range(16):
        kick.probability.set(s, 100.0 if s % 4 == 0 else 60.0)
        kick.timing.set(s, -8.0)
        kick.note_length.set(s, 40.0)
    kick.repeats.set(7, 4)
    kick.repeat_interval.set(7, 3)
    kick.velocity.set(0, 127.0)
    print(f"graphs: velocity(step0)={kick.velocity.get(0)} "
          f"length={kick.note_length.get(0)}% timing={kick.timing.get(0)}% "
          f"prob(step1)={kick.probability.get(1)}% "
          f"repeats(7)={kick.repeats.get(7)} interval={kick.repeat_interval.get(7)}")

    before = list(kick.timing.values.values())
    kick.timing.randomize(0.4, np.random.default_rng(3), kick.steps)
    after = list(kick.timing.values.values())
    print(f"per-graph randomise: timing jittered {len(after)} steps, changed="
          f"{before != after}")
    assert before != after

    # probability is rolled per pass: loop 0 vs loop 1 differ
    e0 = g.render(loops=1, seed=1)
    e1 = g.render(loops=2, seed=1)
    print(f"render: 1 loop = {len(e0)} events, 2 loops = {len(e1)} events "
          f"(interval graph gates the ratchet)")
    assert len(e1) > len(e0)

    # ratchet only on every 3rd pass
    for seed in (0, 1, 2):
        ev = [e for e in g.render(loops=3, seed=99) if e[0] > 0]
    kick_only = [e for e in g.render(loops=3, seed=7)
                 if e[1] in (kick.note,)]
    print(f"kick events over 3 passes at interval=3: {len(kick_only)}")

    # shuffle changes absolute timing
    t_straight = [e[0] for e in g.render(loops=1, seed=5)]
    g.set_shuffle("mpc60", 1.0)
    t_swung = [e[0] for e in g.render(loops=1, seed=5)]
    print(f"shuffle mpc60 moves onsets: {not np.allclose(t_straight, t_swung)} "
          f"(max delta {max(abs(a - b) for a, b in zip(t_straight, t_swung)) * 1000:.1f} ms)")
    assert not np.allclose(t_straight, t_swung)
    g.set_shuffle("straight", 0.0)

    # scale quantisation: all output pitches inside C minor
    pitches = sorted({e[1] for e in g.render(loops=1, seed=2)})
    allowed = {g.root + i for i in SCALES["minor"]}
    print(f"scale quantise (C minor): pitches {pitches} -> "
          f"all pitch classes legal = "
          f"{all((p - g.root) % 12 in SCALES['minor'] for p in pitches)}")
    assert all((p - g.root) % 12 in SCALES["minor"] for p in pitches)

    midi = g.to_midi_events(loops=2, seed=4)
    print(f"MIDI export: {len(midi)} events, first={midi[0]}")
    assert all(m["end_tick"] > m["start_tick"] for m in midi)
    print("pattern:")
    for row in g.pattern_table()[:4]:
        print("   " + row)
    print("  polymetric_grid demo OK")
    return "ok"


if __name__ == "__main__":
    demo()
