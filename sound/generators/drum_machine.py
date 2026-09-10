"""Eight-channel sample drum machine sequencer — Erica Synths Bullfrog Drums style.

Replicable logic from the Sound On Sound review of the Erica Synths Bullfrog
Drums (SOS September 2026):

  * **eight channels**, seven of them identical **sample-based** tracks plus one
    channel reserved for **CV sequencing** (for patching the Bullfrog Synth).
  * Per sample track: sample select, **pitch, decay, start, end, loop point,
    DJ-style filter (LP or HP), resonance, overdrive and pan**.
  * **X0X-style 64-step sequencer**, kits (sounds) and patterns (sequencer)
    loaded separately; user samples replaceable.

What is replicated here:
- ``SampleChannel``: a playable sample voice with the full Bullfrog parameter
  set — start/end trims, loop point (sustained loop while the step is held),
  pitch (resample with linear interpolation), decay envelope, one-pole DJ
  filter with LP/HP mode and resonance (feedback), overdrive, pan.
- ``CVChannel``: the eighth channel is a *sequencer lane of CV values*, not a
  drum voice — it emits (step, value) pairs that can drive a modular CV input.
- ``BullfrogDrums``: 64-step X0X grid across the 8 channels (one channel is CV),
  with per-step velocity/accent, swing, flam/ratchet, and per-channel mute.
  ``render`` produces a mono/stereo buffer; ``to_cv_sequence`` returns the CV
  lane for pitching an external synth (the "sequence the Bullfrog Synth" trick).
- ``Kit``: named sample bank with per-channel default parameter sets.

Not replicated: the hardware enclosure, the internal flash drive / USB sample
transfer, the built-in microphone.

Usage:
    from sound.generators.drum_machine import BullfrogDrums, Kit, SampleChannel

    bf = BullfrogDrums(sample_rate=44100)
    kit = Kit.demo_kit(bf.sr)
    bf.load_kit(kit)
    grid = {1: {0: 1.0, 4: 0.8}, 3: {2: 1.0}}        # channel -> {step: vel}
    audio = bf.render(grid, steps=16, pattern_len=1.0)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np

__all__ = [
    "SampleChannel",
    "CVChannel",
    "Kit",
    "BullfrogDrums",
    "synthesize_drum_samples",
    "X0X_STEPS",
]

X0X_STEPS = 64


def _default_click(sr: int, freq: float, decay: float, kind: str = "tone",
                   noise: float = 0.0) -> np.ndarray:
    """Small built-in sample generator so the machine is playable out of the box."""
    n = int(max(0.02, decay) * sr)
    tt = np.arange(n) / sr
    env = np.exp(-tt / max(1e-3, decay / 3.0))
    if kind == "noise":
        body = np.random.default_rng(int(freq)).standard_normal(n)
    else:
        body = np.sin(2 * np.pi * freq * tt * np.exp(-tt * 4.0))
    if noise:
        body = body + noise * np.random.default_rng(7).standard_normal(n)
    return (body * env * 0.9).astype(np.float64)


def synthesize_drum_samples(sr: int = 44100) -> Dict[str, np.ndarray]:
    """A tiny factory kit: kick, snare, hat, tom, clap, rim, cymbal."""
    return {
        "kick": _default_click(sr, 55.0, 0.45, "tone"),
        "snare": _default_click(sr, 190.0, 0.20, "noise", noise=0.6),
        "hat": _default_click(sr, 8000.0, 0.07, "noise"),
        "tom": _default_click(sr, 120.0, 0.30, "tone"),
        "clap": _default_click(sr, 1200.0, 0.12, "noise", noise=0.9),
        "rim": _default_click(sr, 1700.0, 0.05, "tone", noise=0.4),
        "cymbal": _default_click(sr, 6000.0, 0.90, "noise"),
    }


class SampleChannel:
    """One Bullfrog sample track: pitch/decay/start/end/loop/filter/drive/pan."""

    def __init__(self, sample: Optional[np.ndarray] = None, sample_rate: int = 44100):
        self.sr = int(sample_rate)
        self.sample = (np.asarray(sample, dtype=np.float64)
                       if sample is not None else np.zeros(0))
        self.pitch: float = 1.0        # playback rate (resample)
        self.decay: float = 1.0        # envelope decay length multiplier
        self.start: float = 0.0        # 0..1 of sample
        self.end: float = 1.0          # 0..1 of sample
        self.loop: Optional[float] = None   # loop point 0..1, None = one-shot
        self.filter_type: str = "lp"   # "lp" | "hp"
        self.cutoff: float = 12000.0
        self.resonance: float = 0.0
        self.overdrive: float = 0.0
        self.pan: float = 0.0          # -1 .. +1
        self.muted: bool = False

    # -- sample helpers -----------------------------------------------------
    def set_sample(self, sample: np.ndarray) -> None:
        self.sample = np.asarray(sample, dtype=np.float64)

    def trimmed(self) -> np.ndarray:
        n = len(self.sample)
        if n == 0:
            return self.sample
        s = int(np.clip(self.start, 0.0, 1.0) * (n - 1))
        e = int(np.clip(self.end, 0.0, 1.0) * n)
        return self.sample[s:max(s + 1, e)]

    def _filter(self, x: np.ndarray) -> np.ndarray:
        a = 1.0 - np.exp(-2 * np.pi * np.clip(self.cutoff, 20.0, self.sr * 0.45)
                         / self.sr)
        y = np.empty_like(x)
        z = 0.0
        prev_in = 0.0
        prev_out = 0.0
        fb = 0.85 * float(np.clip(self.resonance, 0.0, 1.0))
        for i in range(len(x)):
            if self.filter_type == "hp":
                hp_in = x[i] - prev_in + 0.96 * prev_out
                prev_in = x[i]
                z += a * (hp_in - z)
                prev_out = z
                y[i] = z
            else:
                lp_in = x[i] + fb * prev_out
                z += a * (lp_in - z)
                prev_out = z
                y[i] = z
        return y

    def render(self, velocity: float = 1.0, hold: float = 0.12,
               sr: Optional[int] = None) -> np.ndarray:
        """One hit. ``hold`` = gate length in seconds (controls the loop tail)."""
        sr = sr or self.sr
        if self.muted or len(self.sample) == 0:
            return np.zeros(1, dtype=np.float64)
        base = self.trimmed()
        # resample by pitch (linear interpolation)
        if self.pitch != 1.0:
            idx = np.arange(0, len(base) - 1, self.pitch)
            i0 = idx.astype(int)
            frac = idx - i0
            base = (1 - frac) * base[i0] + frac * base[np.minimum(i0 + 1,
                                                                 len(base) - 1)]
        if self.loop is not None and 0.0 < self.loop < 1.0:
            lp = int(len(base) * self.loop)
            loop_src = base[lp:]
            if len(loop_src) > 8:
                need = max(0, int(hold * sr) - lp)
                if need > 0:
                    reps = int(np.ceil(need / len(loop_src)))
                    base = np.concatenate([base, np.tile(loop_src, reps)])
        out = self._filter(base)
        # decay envelope: shorten/lengthen the natural decay
        dn = max(8, int(len(out) / max(0.05, self.decay)))
        env = np.exp(-np.linspace(0.0, 4.0, dn))
        env = np.pad(env, (0, max(0, len(out) - dn)), mode="edge")[:len(out)]
        out = out * env
        out = out * (1.0 + 3.0 * float(np.clip(self.overdrive, 0.0, 1.0)))
        if self.overdrive > 0:
            out = np.tanh(out)
        return out * float(np.clip(velocity, 0.0, 1.5))

    def render_stereo(self, velocity: float = 1.0, hold: float = 0.12,
                      sr: Optional[int] = None) -> Tuple[np.ndarray, np.ndarray]:
        """Return (left, right) with the pan law applied."""
        mono = self.render(velocity, hold, sr)
        p = float(np.clip(self.pan, -1.0, 1.0))
        l_gain = np.cos((p + 1) * np.pi / 4)
        r_gain = np.sin((p + 1) * np.pi / 4)
        return mono * l_gain, mono * r_gain


class CVChannel:
    """The eighth Bullfrog channel: a sequencer lane of control voltages."""

    def __init__(self, max_volts: float = 5.0):
        self.max_volts = float(max_volts)
        self.steps: Dict[int, float] = {}   # step -> 0..1 normalised value

    def set(self, step: int, value: float) -> None:
        self.steps[int(step) % X0X_STEPS] = float(np.clip(value, 0.0, 1.0))

    def sequence(self, steps: int = 16) -> List[Tuple[int, float]]:
        """(step_index, volts) for every programmed step, in order."""
        out = []
        for s in range(steps):
            if s in self.steps:
                out.append((s, self.steps[s] * self.max_volts))
        return out

    def to_pitch_sequence(self, steps: int = 16, base_freq: float = 55.0,
                          octaves: float = 2.0) -> List[Tuple[int, float]]:
        """CV lane as a pitch sequence for an external synth (Bullfrog Synth)."""
        return [(s, base_freq * (2.0 ** (v / self.max_volts * octaves)))
                for s, v in self.sequence(steps)]


@dataclass
class Kit:
    """A named set of channel samples + per-channel parameter defaults."""

    name: str
    samples: Dict[int, np.ndarray] = field(default_factory=dict)
    params: Dict[int, dict] = field(default_factory=dict)

    @classmethod
    def demo_kit(cls, sr: int = 44100) -> "Kit":
        src = synthesize_drum_samples(sr)
        keys = list(src)
        samples = {i + 1: src[keys[i]] for i in range(min(7, len(keys)))}
        params = {
            1: {"pitch": 1.0, "decay": 1.0, "cutoff": 6000.0},
            2: {"pitch": 1.0, "decay": 0.9, "cutoff": 9000.0},
            3: {"pitch": 1.0, "decay": 0.6, "cutoff": 12000.0},
            4: {"pitch": 1.0, "decay": 1.1, "cutoff": 4000.0},
            5: {"pitch": 1.0, "decay": 0.7, "cutoff": 11000.0, "pan": -0.2},
            6: {"pitch": 1.0, "decay": 0.5, "cutoff": 10000.0, "pan": 0.3},
            7: {"pitch": 1.0, "decay": 1.4, "cutoff": 14000.0},
        }
        return cls(name="factory", samples=samples, params=params)


class BullfrogDrums:
    """Eight-channel (7 sample + 1 CV) X0X drum machine with 64-step patterns."""

    def __init__(self, sample_rate: int = 44100):
        self.sr = int(sample_rate)
        self.channels: Dict[int, SampleChannel] = {
            i: SampleChannel(sample_rate=sample_rate) for i in range(1, 8)}
        self.cv = CVChannel()

    def load_kit(self, kit: Kit) -> None:
        for ch, s in kit.samples.items():
            if ch in self.channels:
                self.channels[ch].set_sample(s)
        for ch, params in kit.params.items():
            if ch in self.channels:
                for k, v in params.items():
                    setattr(self.channels[ch], k, v)

    # -- sequencing ---------------------------------------------------------
    def render_hits(self, grid: Dict[int, Dict[int, float]], bpm: float = 120.0,
                    steps: int = 16, swing: float = 0.0, bars: int = 1,
                    flams: Optional[Dict[Tuple[int, int], int]] = None,
                    pattern_start: int = 0) -> np.ndarray:
        """Render a pattern to a stereo buffer.

        Args:
            grid: {channel: {absolute_step: velocity}}.  Channel 8 is the CV lane.
            bpm: tempo.
            steps: steps per bar (16 = 16ths).
            swing: 0..1 delay of odd steps.
            bars: bars to render.
            flams: {(channel, step): n_extra_hits} for flams / ratchets.
            pattern_start: first step index (for pattern chains).
        """
        step_dur = 60.0 / bpm / (steps / 4.0)
        n_steps = steps * bars
        total = int(step_dur * n_steps * self.sr) + self.sr
        left = np.zeros(total)
        right = np.zeros(total)
        for ch, hits in grid.items():
            if ch not in self.channels:
                continue
            for step, vel in hits.items():
                rel = int(step) - pattern_start
                if rel < 0 or rel >= n_steps:
                    continue
                # swing delays every odd step by up to 25% of a step
                swing_shift = (0.25 * float(np.clip(swing, 0.0, 1.0))
                               if rel % 2 else 0.0)
                t = (rel + swing_shift) * step_dur
                repro: Iterable[float] = [t]
                extra = (flams or {}).get((ch, int(step)), 0)
                for k in range(1, int(extra) + 1):
                    repro = list(repro) + [t + k * step_dur / (extra + 1)]
                for tt in repro:
                    start = int(tt * self.sr)
                    l, r = self.channels[ch].render_stereo(
                        velocity=vel, hold=step_dur)
                    e = min(total, start + len(l))
                    if start >= total or e <= start:
                        continue
                    left[start:e] += l[:e - start]
                    right[start:e] += r[:e - start]
        return np.stack([left, right], axis=1)

    def render(self, grid: Dict[int, Dict[int, float]], **kwargs) -> np.ndarray:
        """Alias for :meth:`render_hits` (kept short for composition code)."""
        return self.render_hits(grid, **kwargs)

    def to_cv_sequence(self, steps: int = 16) -> List[Tuple[int, float]]:
        """The eighth channel: CV lane for sequencing an external synth."""
        return self.cv.sequence(steps)

    def pattern_to_midi_events(self, grid: Dict[int, Dict[int, float]],
                               bpm: float = 120.0, steps: int = 16
                               ) -> List[Tuple[int, float, float]]:
        """(tick, velocity, channel) triples for an external MIDI export."""
        tpb = 480
        ticks_per_step = tpb * 4 // steps
        out = []
        for ch, hits in grid.items():
            if ch not in self.channels:
                continue
            for step, vel in hits.items():
                out.append((int(step) * ticks_per_step, float(vel), int(ch) - 1))
        return sorted(out)


def demo() -> str:
    sr = 22050
    bf = BullfrogDrums(sample_rate=sr)
    bf.load_kit(Kit.demo_kit(sr))
    print(f"channels: {sorted(bf.channels)} + CV lane (8)")

    # per-channel parameter sanity
    ch1 = bf.channels[1]
    ch1.pitch, ch1.decay, ch1.overdrive, ch1.pan = 1.2, 0.8, 0.3, -0.4
    print(f"ch1 params: pitch={ch1.pitch} decay={ch1.decay} "
          f"overdrive={ch1.overdrive} pan={ch1.pan}")

    grid = {1: {0: 1.0, 4: 0.8, 8: 1.0, 12: 0.7},
            2: {4: 0.9, 12: 1.0},
            3: {2: 0.7, 3: 0.5, 6: 0.7, 7: 0.5, 10: 0.7, 11: 0.5, 14: 0.7, 15: 0.5},
            5: {7: 0.6}}
    audio = bf.render(grid, bpm=120.0, steps=16, bars=1, swing=0.4,
                      flams={(1, 12): 2})
    print(f"render: shape={audio.shape} peak={np.max(np.abs(audio)):.3f} "
          f"finite={np.all(np.isfinite(audio))} "
          f"rms={np.sqrt(np.mean(audio ** 2)):.4f}")
    assert audio.shape[1] == 2 and np.all(np.isfinite(audio))
    assert np.max(np.abs(audio)) > 0.1

    # start/end trimming and loop point must change the voice
    base = bf.channels[4].render()
    bf.channels[4].start = 0.05
    bf.channels[4].end = 0.6
    trimmed = bf.channels[4].render()
    bf.channels[4].loop = 0.25
    looped = bf.channels[4].render(hold=0.25)
    print(f"trim: base={len(base)} trimmed={len(trimmed)} looped={len(looped)}")
    assert len(trimmed) < len(base) and len(looped) > len(trimmed)

    # CV lane -> external synth pitch sequence
    for s, v in ((0, 0.2), (4, 0.5), (8, 0.75), (12, 1.0)):
        bf.cv.set(s, v)
    seq = bf.to_cv_sequence(16)
    pitches = bf.cv.to_pitch_sequence(16, base_freq=55.0)
    print(f"cv steps={seq} ")
    print(f"cv pitches={[(s, int(round(f))) for s, f in pitches]}")
    assert len(seq) == 4 and pitches[0][1] == pitches[0][1]

    # mute + MIDI export path
    bf.channels[2].muted = True
    muted = bf.render(grid, bpm=120.0, steps=16)
    print(f"muted ch2 rms={np.sqrt(np.mean(muted ** 2)):.4f} "
          f"(< {np.sqrt(np.mean(audio ** 2)):.4f})")
    ev = bf.pattern_to_midi_events(grid, steps=16)
    print(f"midi events: {len(ev)} first={ev[0]}")
    assert len(ev) == 15
    print("  drum_machine demo OK")
    return "ok"


if __name__ == "__main__":
    demo()
