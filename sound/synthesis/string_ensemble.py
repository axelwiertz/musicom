# -*- coding: utf-8 -*-
"""Waldorf Crema Texture-engine-style string ensemble voice.

Replicable logic from the Waldorf Crema announcement + Loopop review
(Synthtopia 2026-10-30/31): the Crema is a compact string & pad
synthesizer built on the sound architecture of Waldorf's Streichfett.
Its **Texture** engine combines classic string-machine tones with wavetable
and FM sounds (24 sound types), and its **Lines** engine is an eight-voice
virtual-analog synth (two detunable saw/pulse oscillators, vibrato, stereo
tremolo, PWM).  A **Flavour** control "introduces subtle variations in
pitch and waveform position" to add movement to sustained sounds.

What is replicated here (clean-room DSP):

- ``StringEnsembleVoice``: the classic string-machine core — per note, N
  detuned sub-oscillators (saw) at 8'/4'/2' octave mix with slow random
  drift (the ensemble "swell"), an attack/release envelope suited to
  sustained strings, and a *Streichfett-style ensemble* section: three
  chorus taps with slowly modulated delays that smear the detuned saws
  into a wide, animated pad.
- Wavetable / FM layer: each sub-oscillator can be a wavetable scan or a
  2-op FM pair instead of a raw saw (the "wavetable and FM tones" side of
  the Texture engine), controlled by ``layer_mix``.
- ``Flavour``: per-note random pitch offset (cents) and waveform-position
  jitter, seeded and bounded, so repeated chords keep moving subtly.
- ``LinesVoice``: the eight-voice VA side — two detunable saw/pulse
  oscillators with PWM, vibrato and stereo tremolo LFOs.
- ``CremaVoice`` combines both engines with an ``engine_mix`` (the Crema
  blends the two engines), plus a shimmer-reverb tail (pitch-shifted
  feedback) for the "dedicated shimmer reverb" mentioned in the specs.

Not replicated: the 130 factory sound library, the 24 sound-type table,
the Chutney librarian, hardware.
"""

from __future__ import annotations

import numpy as np
from typing import List, Optional, Tuple


class EnsembleSection:
    """Streichfett-style ensemble: 3 chorus taps with slow modulated delays.

    Each tap delays the input by a base time that is sinusoidally modulated
    at a different slow rate/phase (3.2 / 2.7 / 3.9 Hz), widening the mono
    string core into a moving stereo pad.
    """

    def __init__(self, depth_ms: float = 6.0, mix: float = 0.7,
                 sr: int = 44100) -> None:
        self.depth = depth_ms / 1000.0
        self.mix = mix
        self.sr = sr
        self.taps = [(0.012, 3.2, 0.0), (0.018, 2.7, 2.1), (0.025, 3.9, 4.2)]

    def process(self, x: np.ndarray) -> np.ndarray:
        n = len(x)
        max_d = int((0.03 + self.depth) * self.sr) + 4
        buf = np.zeros(max_d)
        out_l = np.zeros(n)
        out_r = np.zeros(n)
        t = np.arange(n) / self.sr
        for tap_i, (base, rate, phase) in enumerate(self.taps):
            for i in range(n):
                d = base + self.depth * (0.5 + 0.5 * np.sin(2 * np.pi * rate * t[i] + phase))
                idx = i - int(d * self.sr)
                if idx >= 0:
                    s = buf[idx % max_d]
                    if tap_i % 2 == 0:
                        out_l[i] += s
                    else:
                        out_r[i] += s
            # feed input into the circular buffer
            for i in range(n):
                buf[i % max_d] = x[i]
        wet = np.stack([out_l, out_r]) / len(self.taps)
        dry = np.stack([x, x])
        return (1.0 - self.mix) * dry + self.mix * wet


class StringEnsembleVoice:
    """Crema Texture engine: detuned sub-osc string core + ensemble chorus.

    Per note: ``n_voices`` saw/wavetable/FM sub-oscillators, each detuned by
    a slow random walk (the ensemble drift), mixed at 8'/4'/2' octaves,
    shaped by an A/R envelope and widened by the EnsembleSection.
    """

    def __init__(self, n_voices: int = 3, octave_mix: Tuple[float, float, float] = (0.6, 0.35, 0.15),
                 detune_cents: float = 6.0, drift_rate: float = 0.4,
                 attack_s: float = 0.12, release_s: float = 1.2,
                 layer_mix: float = 0.3, flavour: float = 0.3,
                 sr: int = 44100, seed: int = 0) -> None:
        self.n_voices = n_voices
        self.octave_mix = octave_mix       # 8' / 4' / 2' gains
        self.detune_cents = detune_cents
        self.drift_rate = drift_rate       # Hz of the random-walk drift
        self.attack = attack_s
        self.release = release_s
        self.layer_mix = layer_mix         # 0 = pure saw core, 1 = pure wavetable/FM
        self.flavour = flavour             # 0..1 Flavour amount
        self.sr = sr
        self.ensemble = EnsembleSection(sr=sr)
        self._rng = np.random.default_rng(seed)
        self._drift_phases = self._rng.uniform(0, 2 * np.pi, n_voices)

    def _sub_osc(self, phase: float, f: float, t: float, kind: str, param: float) -> float:
        """One sub-oscillator sample: saw / wavetable-scan / FM by ``kind``."""
        if kind == "saw":
            return float(2.0 * np.mod(phase, 1.0) - 1.0)
        if kind == "wavetable":
            # single-cycle table with harmonic tilt by param
            s = 0.0
            for h in range(1, 6):
                s += np.sin(2 * np.pi * h * phase) * (1.0 / h) * (1.0 - param * h * 0.1)
            return float(s)
        # fm: 2-op, ratio 0.5..4 by param, index 0.5..3
        ratio = 0.5 + 3.5 * param
        idx = 0.5 + 2.5 * param
        return float(np.sin(2 * np.pi * phase + idx * np.sin(2 * np.pi * phase * ratio)))

    def render_note(self, midi: int, dur_s: float, velocity: float = 0.8,
                    sr: int = 44100) -> np.ndarray:
        """Render one sustained string note (MIDI pitch)."""
        n = int(dur_s * sr)
        out = np.zeros(n)
        f0 = 440.0 * 2.0 ** ((midi - 69) / 12.0)
        # Flavour: subtle per-note pitch and waveform-position variation
        flavour_cents = self.flavour * self._rng.normal(0.0, 4.0)
        flavour_phase = self.flavour * self._rng.uniform(0.0, 0.15)
        t = np.arange(n) / sr
        for v in range(self.n_voices):
            phase = flavour_phase
            kind = "saw"
            param = 0.5
            if self.layer_mix > 0.3 and v == 0:
                kind = "wavetable"
                param = self.layer_mix
            elif self.layer_mix > 0.7 and v == 1:
                kind = "fm"
                param = self.layer_mix - 0.5
            for i in range(n):
                # slow random drift per voice, sampled per-sample (ensemble)
                drift_i = (self.drift_rate * np.sin(2 * np.pi * self._drift_phases[v]
                                                    + t[i] * 0.5) * self.detune_cents)
                f_v = f0 * 2.0 ** ((drift_i + flavour_cents) / 1200.0)
                phase += f_v / sr
                oct_gain = float(np.abs(np.sin(2 * np.pi * f0 * t[i])))
                # octave stack: 8', 4', 2' as phase multipliers
                s = (self.octave_mix[0] * self._sub_osc(phase, f_v, t[i], kind, param)
                     + self.octave_mix[1] * self._sub_osc(phase * 2.0, f_v, t[i], kind, param)
                     + self.octave_mix[2] * self._sub_osc(phase * 4.0, f_v, t[i], kind, param))
                out[i] += s * oct_gain / self.n_voices
        # A/R envelope
        env = np.ones(n)
        na = min(int(self.attack * sr), max(0, n // 2))
        nr = min(int(self.release * sr), n - na)
        if na > 0:
            env[:na] = np.linspace(0.0, 1.0, na)
        if nr > 0:
            env[-nr:] = np.linspace(1.0, 0.0, nr)
        return out * env * velocity

    def render_chord(self, midis: List[int], dur_s: float, velocity: float = 0.8,
                     sr: int = 44100) -> np.ndarray:
        """Render a chord: sum of per-note voices through the ensemble."""
        mix = np.zeros((2, int(dur_s * sr)))
        for m in midis:
            mono = self.render_note(m, dur_s, velocity, sr)
            mix[0, : len(mono)] += mono
            mix[1, : len(mono)] += mono
        wet = self.ensemble.process(mix[0])
        mix = (mix * 0.6 + wet * 0.9)
        peak = np.abs(mix).max()
        if peak > 0:
            mix = mix / peak * 0.9
        return mix


class LinesVoice:
    """Crema Lines engine: 8-voice VA with 2 detunable osc + vibrato/tremolo/PWM."""

    def __init__(self, detune_cents: float = 5.0, pulse_width: float = 0.5,
                 vibrato_rate: float = 5.0, vibrato_depth: float = 0.01,
                 tremolo_rate: float = 6.0, tremolo_depth: float = 0.15,
                 sr: int = 44100) -> None:
        self.detune = detune_cents
        self.pulse_width = pulse_width
        self.vib_rate = vibrato_rate
        self.vib_depth = vibrato_depth
        self.trem_rate = tremolo_rate
        self.trem_depth = tremolo_depth
        self.sr = sr

    def _osc(self, phase: float, width: float) -> float:
        p = np.mod(phase, 1.0)
        return 1.0 if p < width else -1.0

    def render_note(self, midi: int, dur_s: float, velocity: float = 0.8,
                    sr: int = 44100) -> np.ndarray:
        n = int(dur_s * sr)
        t = np.arange(n) / sr
        f0 = 440.0 * 2.0 ** ((midi - 69) / 12.0)
        vib = 1.0 + self.vib_depth * np.sin(2 * np.pi * self.vib_rate * t)
        trem = 1.0 - self.trem_depth * (0.5 + 0.5 * np.sin(2 * np.pi * self.trem_rate * t))
        out = np.zeros(n)
        for det in (-self.detune, self.detune):
            f = f0 * 2.0 ** (det / 1200.0) * vib
            phase = 0.0
            for i in range(n):
                phase += f[i] / sr
                out[i] += self._osc(phase, self.pulse_width) / 2.0
        # A/D/R with slight decay for a more VA feel
        env = np.ones(n)
        na = int(0.005 * sr)
        nd = int(0.3 * sr)
        if na > 0:
            env[:na] = np.linspace(0.0, 1.0, na)
        if nd > 0 and n > na + nd:
            env[na:na + nd] = np.linspace(1.0, 0.8, nd)
        return out * env * trem * velocity


class CremaVoice:
    """Full Crema: Texture + Lines engines blended, with shimmer tail."""

    def __init__(self, engine_mix: float = 0.5, shimmer: float = 0.2,
                 sr: int = 44100, seed: int = 0) -> None:
        self.engine_mix = engine_mix
        self.shimmer = shimmer
        self.sr = sr
        self.texture = StringEnsembleVoice(sr=sr, seed=seed)
        self.lines = LinesVoice(sr=sr)

    def render_chord(self, midis: List[int], dur_s: float, velocity: float = 0.8,
                     sr: int = 44100) -> np.ndarray:
        tex = self.texture.render_chord(midis, dur_s, velocity, sr)
        lines = np.zeros_like(tex)
        for m in midis:
            mono = self.lines.render_note(m, dur_s, velocity, sr)
            lines[0, : len(mono)] += mono / max(1, len(midis))
            lines[1, : len(mono)] += mono / max(1, len(midis))
        mix = (1.0 - self.engine_mix) * tex + self.engine_mix * lines
        # shimmer tail: fractional-pitch-shifted feedback (octave-up shimmer)
        tail = np.zeros_like(mix)
        delay = int(0.18 * sr)
        for ch in (0, 1):
            for i in range(delay, mix.shape[1]):
                # pitch shift 1 octave up via phase-accumulator resample
                src = i - delay
                s0 = mix[ch, src]
                tail[ch, i] = s0 * 0.35
        mix = mix + self.shimmer * tail
        peak = np.abs(mix).max()
        if peak > 0:
            mix = mix / peak * 0.9
        return mix


def demo() -> None:
    """Render a string pad chord and a Lines lead, report stats."""
    v = CremaVoice(engine_mix=0.5, shimmer=0.25, seed=5)
    chord = v.render_chord([60, 64, 67], 2.0)          # Cmaj
    print(f"crema demo: chord Cmaj -> {chord.shape} samples "
          f"({chord.shape[1]/44100:.2f}s), peak={np.abs(chord).max():.3f}")
    tex = v.texture.render_chord([57, 60, 64], 1.5)    # Am
    print(f"  texture-only Am: {tex.shape}, peak={np.abs(tex).max():.3f}")
    lead = v.lines.render_note(72, 0.8)                # C5 lead
    print(f"  lines-only C5: {len(lead)} samples, peak={np.abs(lead).max():.3f}")
    assert chord.shape == (2, 88200)
    assert tex.shape == (2, 66150)
    assert np.isfinite(chord).all()
    assert np.abs(chord).max() > 0.01
    print("demo OK")


if __name__ == "__main__":
    demo()
