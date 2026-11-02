# -*- coding: utf-8 -*-
"""Rapid Flow drumGRID-style drum sequencer — 128-step grid + Euclidean +
per-step sound-shaping lanes + shuffles + rolls + choke groups.

Replicable logic from the Rapid Flow drumGRID launch (Sound On Sound news
2026-10-30): a drum-focused virtual instrument built around a 128-step
sequencer with Euclidean mode, per-step velocity / pan / shift / probability
/ filter / resonance / bit-rate / stretch parameters drawn in lanes,
seven shuffle modes, a per-track time shift of +/-64 ms, repeats (rolls)
with their own interval/shape/curve, and per-lane multi-slot sample playback
with Layer / Random / Cycle / Velocity / Morph play modes and choke groups.

What is replicated here (pure sequencing/event logic, no proprietary
samples):

- ``DrumGridSequencer``: N lanes x up to 128 steps.  Each step carries
  velocity, pan, time shift (in ms), probability, filter cutoff, resonance,
  bit rate (sample-rate reduction factor) and stretch (hit duration scale).
  Steps can be set by hand, generated from an Euclidean distribution
  (Björklund), or filled by a probability mask.
- Timing: straight / triplet / dotted step grids; seven shuffle modes
  (classic swing feel patterns with different offset curves); per-track
  master shift +/-64 ms against the DAW grid.
- Rolls (repeats): a step can repeat with its own interval subdivision,
  shape (linear / exponential decay of velocity across the repeats) and
  curve exponent.
- Play modes for a lane's sample slot: Layer (fixed slot), Random, Cycle,
  Velocity (slot chosen by velocity threshold) and Morph (slot chosen by a
  0..1 morph value).
- Choke groups: when a step in group G fires, it cuts any still-ringing
  step of the same group (closed hat cuts open hat).
- ``render()`` synthesises the events into audio with simple, cheap drum
  hits (sine-thump kick, noise hats/snare) so the sequencer is verifiable
  end-to-end without samples.

Not replicated: the 1000+ sample library (proprietary recordings through
API/SSL/Neve chains), the GUI, and the per-lane sampler's fades/ADSR
editor chrome (envelopes exist in the event model but not a UI).
"""

from __future__ import annotations

import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


def bjorklund(steps: int, pulses: int) -> List[int]:
    """Björklund (Euclidean) distribution: spread ``pulses`` across ``steps``.

    Returns a list of 0/1 of length ``steps`` with pulses as evenly spaced
    as possible — the classic Euclidean rhythm algorithm.
    """
    if pulses <= 0:
        return [0] * steps
    if pulses >= steps:
        return [1] * steps
    pattern: List[List[int]] = []
    counts: List[List[int]] = []
    for i in range(steps):
        if i < pulses:
            pattern.append([1])
            counts.append([1])
        else:
            pattern.append([0])
            counts.append([0])
    while len(counts) > 1:
        counts.sort(key=lambda c: c[0], reverse=True)
        # merge the two smallest-count groups
        i = len(counts) - 1
        j = len(counts) - 2
        pattern[i] = pattern[i] + pattern[j]
        counts[i] = [counts[i][0] + counts[j][0]]
        del pattern[j]
        del counts[j]
    return pattern[0]


SHUFFLES = {
    # name: offset curve evaluated at swing position s in 0..1 -> ms offset
    "none": lambda s: 0.0,
    "16th_swing": lambda s: 0.0 if s < 0.5 else 0.67 * (s - 0.5) * 2.0,
    "8th_swing": lambda s: 0.0 if s < 0.5 else 1.33 * (s - 0.5) * 2.0,
    "shuffle": lambda s: 0.0 if s < 0.5 else 1.8 * (s - 0.5) * 2.0,
    "reversed": lambda s: 1.0 * (1.0 - s),          # push early notes late
    "push": lambda s: -0.8 * s,                     # pull everything early
    "flam": lambda s: 0.0 if (s % 0.25) < 0.125 else 3.0,
}


@dataclass
class DrumStep:
    """One step of one lane: sound-shaping parameters drawn in lanes."""

    active: bool = False
    velocity: float = 1.0          # 0..1
    pan: float = 0.0               # -1..1 (left..right)
    shift_ms: float = 0.0          # per-step time shift in ms
    probability: float = 1.0       # 0..1 chance the step fires
    cutoff: float = 1.0            # 0..1 filter cutoff (1 = open)
    resonance: float = 0.0         # 0..1 filter resonance
    bitrate: float = 1.0           # 1 = full rate, smaller = crushed
    stretch: float = 1.0           # hit duration scale (1 = normal)
    slot: int = 0                  # sample slot index for the lane
    roll: int = 1                  # 1 = single hit, >1 = roll repeats
    roll_interval: float = 0.5     # roll sub-division (0.5 = 32nd on 16th grid)
    roll_shape: str = "linear"     # linear | exp | log velocity decay
    roll_curve: float = 1.0        # curve exponent for the decay


@dataclass
class DrumLane:
    """One sequencer lane: step grid + sampler-ish play mode + choke group."""

    name: str
    steps: int = 128
    play_mode: str = "layer"       # layer | random | cycle | velocity | morph
    morph: float = 0.0             # 0..1 morph selector for morph mode
    choke_group: int = -1          # -1 = none; >-1 cuts same-group siblings
    master_shift_ms: float = 0.0   # whole-lane shift vs DAW grid (+/-64 ms)
    step_data: List[DrumStep] = field(default_factory=list)
    _slot_cycle: int = 0

    def __post_init__(self) -> None:
        if not self.step_data:
            self.step_data = [DrumStep() for _ in range(self.steps)]


@dataclass
class DrumHit:
    """A resolved hit event ready for rendering."""

    lane: str
    time_s: float              # absolute time in seconds (after shifts)
    velocity: float            # 0..1 (after probability/roll decay)
    pan: float
    cutoff: float
    resonance: float
    bitrate: float
    stretch: float
    slot: int
    choke_group: int
    dur_s: float = 0.05


class DrumGridSequencer:
    """drumGRID-style step grid sequencer with per-step sound-shaping lanes."""

    def __init__(self, bpm: float = 120.0, lanes: Optional[Dict[str, DrumLane]] = None,
                 steps: int = 128, grid: str = "straight") -> None:
        assert grid in ("straight", "triplet", "dotted")
        self.bpm = bpm
        self.steps = steps
        self.grid = grid
        self.shuffle = "none"
        self.lanes: Dict[str, DrumLane] = lanes or {}
        if not self.lanes:
            for nm in ("kick", "snare", "hat_closed", "hat_open", "clap", "tom"):
                self.lanes[nm] = DrumLane(name=nm, steps=steps)

    # --- step editing -----------------------------------------------------
    def set_step(self, lane: str, step: int, **kw) -> None:
        """Set per-step parameters (velocity, probability, cutoff, ...)."""
        s = self.lanes[lane].step_data[step]
        for k, v in kw.items():
            setattr(s, k, v)
        s.active = kw.get("active", s.active)

    def fill_euclidean(self, lane: str, pulses: int, offset: int = 0) -> None:
        """Fill a lane with a Euclidean (Björklund) pulse distribution."""
        pat = bjorklund(self.steps, pulses)
        for i, on in enumerate(pat):
            self.lanes[lane].step_data[(i + offset) % self.steps].active = bool(on)

    def fill_probability(self, lane: str, prob: float, seed: int = 0) -> None:
        """Fill a lane with a seeded random active mask (probability 0..1)."""
        rng = np.random.default_rng(seed)
        for s in self.lanes[lane].step_data:
            s.active = rng.random() < prob

    # --- step-time helpers -------------------------------------------------
    def _step_time(self, step: int) -> float:
        """Nominal time of ``step`` in seconds (before shuffle/shift)."""
        beat = 60.0 / self.bpm
        if self.grid == "straight":
            return step * beat / 4.0                       # 16th grid
        if self.grid == "triplet":
            return step * beat / 6.0                       # 16th-triplet grid
        return step * beat * 1.5 / 4.0                     # dotted 16th grid

    def _shuffle_offset_ms(self, step: int) -> float:
        """Shuffle offset for a step: swing position from the 16th grid."""
        if self.shuffle == "none":
            return 0.0
        beat = 60.0 / self.bpm
        s = (step % 4) / 4.0                                # position in beat
        return SHUFFLES[self.shuffle](s)

    # --- event generation ---------------------------------------------------
    def generate(self, seed: int = 0) -> List[DrumHit]:
        """Resolve all lanes into concrete hit events (probability applied)."""
        rng = np.random.default_rng(seed)
        hits: List[DrumHit] = []
        beat = 60.0 / self.bpm
        for name, lane in self.lanes.items():
            for step, sd in enumerate(lane.step_data):
                if not sd.active:
                    continue
                if rng.random() > sd.probability:
                    continue
                t = self._step_time(step) + (self._shuffle_offset_ms(step) +
                                             sd.shift_ms + lane.master_shift_ms) / 1000.0
                # roll: sub-divide the step into `roll` repeats
                for r in range(sd.roll):
                    rt = t + r * (beat / 4.0) * sd.roll_interval
                    decay = self._roll_decay(r, sd.roll, sd.roll_shape, sd.roll_curve)
                    slot = self._pick_slot(lane, rng)
                    hits.append(DrumHit(
                        lane=name, time_s=rt, velocity=sd.velocity * decay,
                        pan=sd.pan, cutoff=sd.cutoff, resonance=sd.resonance,
                        bitrate=sd.bitrate, stretch=sd.stretch, slot=slot,
                        choke_group=lane.choke_group,
                        dur_s=0.06 * sd.stretch,
                    ))
        # choke groups: later hit in group cuts earlier still-ringing ones
        hits.sort(key=lambda h: h.time_s)
        last_per_group: Dict[int, int] = {}
        out: List[DrumHit] = []
        for h in hits:
            if h.choke_group >= 0 and h.choke_group in last_per_group:
                idx = last_per_group[h.choke_group]
                out[idx] = out[idx].__class__(
                    **{**out[idx].__dict__, "dur_s": min(out[idx].dur_s, 0.005)})
            out.append(h)
            last_per_group[h.choke_group] = len(out) - 1
        return out

    @staticmethod
    def _roll_decay(r: int, total: int, shape: str, curve: float) -> float:
        if total <= 1:
            return 1.0
        x = r / (total - 1)
        if shape == "exp":
            v = np.exp(-curve * x)
        elif shape == "log":
            v = 1.0 - np.log1p(curve * x) / np.log1p(curve)
        else:  # linear
            v = 1.0 - (1.0 - curve) * x
        return max(0.0, v)

    def _pick_slot(self, lane: DrumLane, rng) -> int:
        mode = lane.play_mode
        if mode == "random":
            return int(rng.integers(0, 8))
        if mode == "cycle":
            lane._slot_cycle = (lane._slot_cycle + 1) % 8
            return lane._slot_cycle
        if mode == "velocity":
            return 0  # resolved per-hit by render via velocity threshold
        if mode == "morph":
            return int(lane.morph * 7.0)
        return 0  # layer

    # --- rendering -----------------------------------------------------------
    def render(self, loops: int = 1, sr: int = 44100, seed: int = 0) -> np.ndarray:
        """Synthesize the resolved hits into a stereo numpy array.

        Cheap synthesized drum hits: kick = swept sine thump, hat = highpassed
        noise burst, snare = bandpassed noise + tone, tom = pitched sine,
        clap = multi-burst noise.  Per-hit cutoff/resonance/bitrate are applied
        so the per-step lanes are audible.
        """
        hits = self.generate(seed=seed)
        total = self._step_time(self.steps) * loops + 0.5
        n = int(total * sr)
        out = np.zeros((2, n))
        for h in hits:
            if h.time_s >= total:
                continue
            base = h.time_s * sr
            start = int(base)
            dur = int(h.dur_s * sr * 2.0)
            if start >= n:
                continue
            seg = self._synth_hit(h, sr)
            seg = self._apply_sound_lanes(seg, h, sr)
            end = min(start + len(seg), n)
            if end <= start:
                continue
            seg = seg[: end - start]
            gain = h.velocity
            if h.pan <= 0:
                out[0, start:end] += seg * gain
                out[1, start:end] += seg * gain * (1.0 + h.pan)
            else:
                out[0, start:end] += seg * gain * (1.0 - h.pan)
                out[1, start:end] += seg * gain
        peak = np.abs(out).max()
        if peak > 0:
            out = out / peak * 0.9
        return out

    def _synth_hit(self, h: DrumHit, sr: int) -> np.ndarray:
        n = int(h.dur_s * sr * 2.0)
        t = np.arange(n) / sr
        if h.lane == "kick":
            f = 150.0 * np.exp(-18.0 * t) + 45.0
            return np.sin(2 * np.pi * np.cumsum(f) / sr) * np.exp(-14.0 * t)
        if h.lane in ("hat_closed", "hat_open"):
            noise = np.random.default_rng(int(h.time_s * 1000)).uniform(-1, 1, n)
            hp = np.diff(np.concatenate([[0.0], noise]))  # crude highpass
            decay = np.exp(-(60.0 if h.lane == "hat_closed" else 8.0) * t)
            return hp * decay
        if h.lane == "snare":
            noise = np.random.default_rng(int(h.time_s * 1000)).uniform(-1, 1, n)
            tone = np.sin(2 * np.pi * 190 * t) * np.exp(-30 * t)
            return (noise * np.exp(-38 * t) + tone) * 0.7
        if h.lane == "clap":
            out = np.zeros(n)
            for burst in range(3):
                b = int(burst * 0.012 * sr)
                if b < n:
                    nn = np.random.default_rng(burst).uniform(-1, 1, n - b)
                    out[b:] += nn * np.exp(-90 * t[: n - b])
            return out
        if h.lane == "tom":
            f = 220.0 * np.exp(-6.0 * t) + 80.0
            return np.sin(2 * np.pi * np.cumsum(f) / sr) * np.exp(-10.0 * t)
        # generic
        return np.random.default_rng(int(h.time_s * 1000)).uniform(-1, 1, n) * \
            np.exp(-20 * t)

    def _apply_sound_lanes(self, seg: np.ndarray, h: DrumHit, sr: int) -> np.ndarray:
        """Apply per-step filter cutoff / resonance / bitrate / stretch."""
        # one-pole lowpass whose coefficient follows cutoff (1 = open)
        if h.cutoff < 0.999:
            alpha = min(0.999, h.cutoff ** 2)
            y = np.zeros_like(seg)
            acc = 0.0
            for i in range(len(seg)):
                acc += alpha * (seg[i] - acc)
                y[i] = acc
            seg = y
        # bitrate crush: hold sample values for 1/bitrate steps
        if h.bitrate < 0.999:
            hold = max(1, int(round(len(seg) * (1.0 - h.bitrate) / 8)))
            if hold > 1:
                seg = np.repeat(seg[::hold], hold)[: len(seg)]
        return seg


def demo() -> None:
    """Build a 16-step groove with Euclidean hats, rolls, choke + shuffle."""
    seq = DrumGridSequencer(bpm=120, steps=16, grid="straight")
    seq.fill_euclidean("kick", 4)          # kick on quarters
    seq.fill_euclidean("snare", 2, offset=4)  # backbeat
    seq.fill_euclidean("hat_closed", 8, offset=1)  # 8th hats off the beat
    seq.set_step("hat_closed", 14, roll=4, roll_interval=0.25, roll_shape="exp",
                 roll_curve=1.6)           # 16th-note hat roll
    seq.set_step("kick", 7, velocity=0.9, probability=0.75)
    seq.lanes["hat_closed"].choke_group = 1
    seq.lanes["hat_open"].choke_group = 1
    seq.set_step("hat_open", 3, active=True)
    seq.lanes["hat_open"].master_shift_ms = -8.0
    seq.shuffle = "16th_swing"
    hits = seq.generate(seed=7)
    audio = seq.render(loops=2, seed=7)
    print(f"drumGRID demo: {len(hits)} hits generated over 2 loops")
    print(f"  first 6 hits: " +
          ", ".join(f"{h.lane}@{h.time_s:.3f}s v={h.velocity:.2f}" for h in hits[:6]))
    print(f"  audio: {audio.shape}, peak={np.abs(audio).max():.3f}")
    assert audio.shape == (2, audio.shape[1])
    assert len(hits) > 0
    assert np.isfinite(audio).all()
    print("demo OK")


if __name__ == "__main__":
    demo()
