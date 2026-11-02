# -*- coding: utf-8 -*-
"""Expressive E Noisy-style "noise through resonance" synthesis voice.

Replicable logic from the Expressive E Noisy 2.6 review (Sound On Sound,
November 2026 issue): Noisy is a 'noise through resonance' synthesizer —
the heart of the sound engine is a noise source (26 types, from white noise
to near-naturalistic 'frying' and 'rainforest') that excites up to three
resonators (now: three analogue synth oscillators, two FM oscillators, a
complex harmonic source, a wavetable-like 'wave map', plus four acoustic
models lending themselves to percussion and metallic/bell timbres).  The
resonators have pitch offsets and separate glide amounts, output to a
stereo mixer, then a multi-mode filter (five 12/24 dB modes), then a soft
clipper.  Two identical layers sum through multi-effect blocks.

What is replicated here (clean-room DSP, no proprietary models):

- ``NoiseSource``: 8 noise families (white, pink, brown, blue, metallic
  band-filtered, 'frying' = AM-burst noise, 'rainforest' = filtered noise +
  random resonant blips, grain) — a stand-in for the 26 hardware types.
- ``Resonator``: five resonator modes — VA osc (saw/square/triangle with
  detune), FM osc (2-op, ratio + index), harmonic (N partials with rolloff),
  wavemap (single-cycle table scan) and acoustic (modal struck resonator /
  comb, good for percussion + bells).  Each resonator has a pitch offset
  (in semitones) and its own glide time.
- ``NoiseResonatorVoice``: noise exciter -> up to 3 parallel resonators ->
  multimode filter (LP/BP/HP, 12 or 24 dB/oct via cascaded biquads) ->
  soft clipper.  Two layers (A/B) with independent settings are summed,
  mirroring Noisy's dual-layer architecture.
- ``render_note`` / ``render_melody`` produce audio for note sequences.

Not replicated: the MPE 'expression' bus (pressure/aftertouch/velocity
summed into one stream — we accept a per-note expression value instead),
the 26-noise-type library, the full effect blocks, the GUI.
"""

from __future__ import annotations

import numpy as np
from typing import List, Optional, Tuple


class NoiseSource:
    """Noise generator families standing in for Noisy's 26 noise types."""

    def __init__(self, kind: str = "white", color: float = 0.0,
                 seed: int = 0) -> None:
        assert kind in ("white", "pink", "brown", "blue", "metallic",
                        "frying", "rainforest", "grain")
        self.kind = kind
        self.color = color          # 0..1 blend toward white for colored kinds
        self.seed = seed
        self._rng = np.random.default_rng(seed)
        self._lp = 0.0
        self._brown = 0.0

    def render(self, n: int, sr: int = 44100) -> np.ndarray:
        rng = self._rng
        if self.kind == "white":
            return rng.uniform(-1.0, 1.0, n)
        if self.kind == "pink":
            # Voss-ish: average of successive random walks (band-limited 1/f)
            out = np.zeros(n)
            for _ in range(8):
                walk = np.zeros(n)
                acc = 0.0
                for i in range(n):
                    acc += rng.uniform(-1.0, 1.0)
                    walk[i] = acc
                out += walk / (np.sqrt(n) if n else 1.0)
            return out / 8.0 * 3.0
        if self.kind == "brown":
            out = np.zeros(n)
            for i in range(n):
                self._brown = 0.98 * self._brown + 0.02 * rng.uniform(-1, 1)
                out[i] = self._brown
            return out / np.abs(out).max()
        if self.kind == "blue":
            w = rng.uniform(-1.0, 1.0, n)
            return np.diff(np.concatenate([[0.0], w])) * 2.0
        if self.kind == "metallic":
            # bandpassed noise around a metallic resonance (3 kHz)
            w = rng.uniform(-1.0, 1.0, n)
            b, a = _biquad_bandpass(3000.0, 0.01, sr)
            return _lfilter(b, a, w)
        if self.kind == "frying":
            # AM-burst noise: noise gated by a fast pseudo-random pulse train
            w = rng.uniform(-1.0, 1.0, n)
            rate = int(sr / 220.0)          # ~220 Hz chop
            gate = np.repeat(rng.integers(0, 2, (n + rate - 1) // rate),
                             rate)[:n].astype(float)
            return w * (0.3 + 0.7 * gate)
        if self.kind == "rainforest":
            # filtered noise bed + random resonant blips (frog-ish)
            w = rng.uniform(-1.0, 1.0, n)
            b, a = _biquad_lowpass(1200.0, 0.7, sr)
            bed = _lfilter(b, a, w) * 0.4
            blips = np.zeros(n)
            pos = rng.integers(0, n, int(n / (sr * 0.7)) + 1)
            for p in pos:
                if p + 2048 < n:
                    f = rng.uniform(400, 1800)
                    tt = np.arange(2048) / sr
                    blips[p:p + 2048] += np.sin(2 * np.pi * f * tt) * \
                        np.exp(-40 * tt) * rng.uniform(0.2, 0.8)
            return bed + blips
        # grain: sparse bursts of bandpassed noise
        w = rng.uniform(-1.0, 1.0, n)
        b, a = _biquad_bandpass(2000.0, 0.02, sr)
        out = _lfilter(b, a, w)
        size = int(sr * 0.02)
        starts = rng.integers(0, max(1, n - size), int(n / (sr * 0.3)) + 1)
        mask = np.zeros(n)
        for s in starts:
            mask[s:s + size] = 1.0
        return out * mask


def _biquad_bandpass(f0: float, q: float, sr: float) -> Tuple[np.ndarray, np.ndarray]:
    w0 = 2.0 * np.pi * f0 / sr
    alpha = np.sin(w0) / (2.0 * q)
    b = np.array([alpha, 0.0, -alpha])
    a = np.array([1.0 + alpha, -2.0 * np.cos(w0), 1.0 - alpha])
    return b, a


def _biquad_lowpass(f0: float, q: float, sr: float) -> Tuple[np.ndarray, np.ndarray]:
    w0 = 2.0 * np.pi * f0 / sr
    alpha = np.sin(w0) / (2.0 * q)
    b = np.array([(1.0 - np.cos(w0)) / 2.0, 1.0 - np.cos(w0),
                  (1.0 - np.cos(w0)) / 2.0])
    a = np.array([1.0 + alpha, -2.0 * np.cos(w0), 1.0 - alpha])
    return b, a


def _lfilter(b: np.ndarray, a: np.ndarray, x: np.ndarray) -> np.ndarray:
    y = np.zeros_like(x)
    for i in range(len(x)):
        acc = b[0] * x[i]
        if i >= 1:
            acc += b[1] * x[i - 1] - a[1] * y[i - 1]
        if i >= 2:
            acc += b[2] * x[i - 2] - a[2] * y[i - 2]
        y[i] = acc / a[0]
    return y


class Resonator:
    """One Noisy-style resonator: a pitch-tracked filter/exciter structure."""

    MODES = ("va", "fm", "harmonic", "wavemap", "acoustic")

    def __init__(self, mode: str = "va", pitch_offset_semi: float = 0.0,
                 glide_s: float = 0.0, param: float = 0.5, seed: int = 0) -> None:
        assert mode in self.MODES
        self.mode = mode
        self.pitch_offset = pitch_offset_semi
        self.glide_s = glide_s
        self.param = param              # mode-specific (FM index, rolloff, ...)
        self.seed = seed
        self._phase = 0.0
        self._current_f = 440.0
        self._target_f = 440.0
        self._table = None

    def _freq(self, note_hz: float) -> float:
        return note_hz * (2.0 ** (self.pitch_offset / 12.0))

    def _set_table(self, kind: str = "saw") -> None:
        x = np.linspace(0.0, 1.0, 512, endpoint=False)
        if kind == "saw":
            self._table = 2.0 * x - 1.0
        elif kind == "square":
            self._table = np.where(x < 0.5, 1.0, -1.0)
        else:
            self._table = np.sin(2 * np.pi * x)

    def render(self, exciter: np.ndarray, note_hz: float, sr: int = 44100,
               glide: float = 0.0) -> np.ndarray:
        """Resonate ``exciter`` at ``note_hz``; returns output array."""
        f = self._freq(note_hz)
        glide = glide if glide > 0 else self.glide_s
        n = len(exciter)
        out = np.zeros(n)
        if self.mode == "va":
            # analogue osc: saw/square/triangle by param, slight detune pair
            det = 1.0 + 0.002 * self.param
            for sign in (1.0, -1.0):
                phase = 0.0
                for i in range(n):
                    f_i = f * (det if sign > 0 else 2.0 - det)
                    phase += 2 * np.pi * f_i / sr
                    p = np.mod(phase / (2 * np.pi), 1.0)
                    if self.param < 0.5:
                        w = 2.0 * p - 1.0
                    else:
                        w = np.where(p < 0.5, 1.0, -1.0)
                    out[i] += 0.5 * w * abs(exciter[i])
            return out
        if self.mode == "fm":
            # 2-op FM: carrier at note_hz, modulator at ratio*f, index=param
            ratio = 0.25 + 2.0 * self.param
            idx = 0.5 + 2.0 * self.param
            ph_c = 0.0
            ph_m = 0.0
            for i in range(n):
                ph_m += 2 * np.pi * f * ratio / sr
                mod = idx * np.sin(ph_m)
                ph_c += 2 * np.pi * f / sr + mod
                out[i] = np.sin(ph_c) * abs(exciter[i])
            return out
        if self.mode == "harmonic":
            # N partials (param -> 2..16) with 1/n rolloff
            n_part = max(2, int(1 + self.param * 15))
            roll = 0.6 + 0.4 * self.param
            ph = np.zeros(n_part)
            for i in range(n):
                ph += 2 * np.pi * f * np.arange(1, n_part + 1) / sr
                s = np.sum(np.sin(ph) * (1.0 / np.arange(1, n_part + 1) ** roll))
                out[i] = s / n_part * abs(exciter[i])
            return out
        if self.mode == "wavemap":
            # single-cycle table scan at note_hz; param selects table shape
            table = self._table
            if table is None:
                kinds = ("saw", "square", "sine")
                self._set_table(kinds[int(self.param * 2.999) % 3])
                table = self._table
            phase = 0.0
            for i in range(n):
                phase += f / sr
                p = np.mod(phase, 1.0) * (len(table) - 1)
                i0 = int(np.floor(p))
                i1 = min(i0 + 1, len(table) - 1)
                w = table[i0] + (p - i0) * (table[i1] - table[i0])
                out[i] = w * abs(exciter[i])
            return out
        # acoustic: modal struck resonator (inharmonic partials -> bells) or
        # comb (percussive body).  param < 0.5 -> modal, else comb.
        if self.param < 0.5:
            ratios = np.array([1.0, 2.76, 5.4, 8.93]) * (0.5 + self.param)
            amps = np.array([1.0, 0.5, 0.25, 0.12])
            decay = np.exp(-3.0 * np.arange(n) / sr)
            ph = np.zeros(4)
            for i in range(n):
                ph += 2 * np.pi * f * ratios / sr
                out[i] = np.sum(amps * np.sin(ph)) * decay[i] * abs(exciter[i])
            return out
        # comb: feed exciter into a delay line of length sr/f (one period)
        d = max(2, int(round(sr / f)))
        buf = np.zeros(d)
        for i in range(n):
            s = buf[i % d]
            buf[i % d] = exciter[i] + 0.9 * s
            out[i] = s
        return out


class NoiseResonatorVoice:
    """Noisy-style voice: noise exciter -> 3 resonators -> filter -> clipper."""

    def __init__(self, noise_kind: str = "white", n_resonators: int = 3,
                 filter_mode: str = "lp", filter_slope: int = 12,
                 cutoff: float = 6000.0, q: float = 0.8,
                 drive: float = 0.5, seed: int = 0) -> None:
        self.noise = NoiseSource(kind=noise_kind, seed=seed)
        self.resonators: List[Resonator] = []
        for i in range(n_resonators):
            self.resonators.append(Resonator(mode="va", seed=seed + i + 1))
        self.filter_mode = filter_mode   # lp | bp | hp
        self.filter_slope = filter_slope  # 12 or 24 dB/oct
        self.cutoff = cutoff
        self.q = q
        self.drive = drive               # 0..1 soft-clip drive
        self.layer_gain = 0.6

    def render_note(self, note_hz: float, dur_s: float, expression: float = 1.0,
                    sr: int = 44100) -> np.ndarray:
        """Render one note: exciter gain follows ``expression`` (0..1)."""
        n = int(dur_s * sr)
        exc = self.noise.render(n, sr) * (0.3 + 0.7 * expression)
        mix = np.zeros(n)
        for res in self.resonators:
            mix += res.render(exc, note_hz, sr) / max(1, len(self.resonators))
        mix = self._filter(mix, sr)
        # soft clipper with drive
        g = 1.0 + 3.0 * self.drive
        return np.tanh(mix * g) * self.layer_gain

    def _filter(self, x: np.ndarray, sr: int) -> np.ndarray:
        stages = self.filter_slope // 12
        y = x
        for _ in range(stages):
            if self.filter_mode == "lp":
                b, a = _biquad_lowpass(self.cutoff, self.q, sr)
            elif self.filter_mode == "hp":
                w0 = 2 * np.pi * self.cutoff / sr
                alpha = np.sin(w0) / (2 * self.q)
                b = np.array([(1 + np.cos(w0)) / 2, -(1 + np.cos(w0)),
                              (1 + np.cos(w0)) / 2])
                a = np.array([1 + alpha, -2 * np.cos(w0), 1 - alpha])
            else:
                b, a = _biquad_bandpass(self.cutoff, self.q, sr)
            y = _lfilter(b, a, y)
        return y

    def render_melody(self, notes: List[Tuple[float, float, float]],
                      sr: int = 44100, gap_s: float = 0.02) -> np.ndarray:
        """Render a note list ``(freq_hz, dur_s, expression)`` to audio."""
        total = sum(d for _, d, _ in notes) + gap_s * len(notes) + 0.2
        out = np.zeros(int(total * sr))
        t = 0.0
        for f, d, e in notes:
            seg = self.render_note(f, d, e, sr)
            i0 = int(t * sr)
            i1 = min(i0 + len(seg), len(out))
            out[i0:i1] += seg[: i1 - i0]
            t += d + gap_s
        return out


def demo() -> None:
    """Render a short pluck-ish melody and report output stats."""
    v = NoiseResonatorVoice(noise_kind="metallic", n_resonators=2,
                            filter_mode="bp", filter_slope=12,
                            cutoff=3000.0, q=1.2, drive=0.4, seed=3)
    v.resonators[0] = Resonator(mode="acoustic", param=0.3,
                                pitch_offset_semi=0.0)   # bell
    v.resonators[1] = Resonator(mode="va", param=0.8,
                                pitch_offset_semi=7.0)   # +fifth
    notes = [(261.63, 0.4, 1.0), (329.63, 0.4, 0.8), (392.0, 0.4, 1.0),
             (523.25, 0.6, 1.0)]
    audio = v.render_melody(notes)
    print(f"noise_resonator demo: {len(notes)} notes -> {len(audio)} samples "
          f"({len(audio)/44100:.2f}s), peak={np.abs(audio).max():.3f}")
    # single white-noise through 3 VA resonators, check finite + nonzero
    v2 = NoiseResonatorVoice(noise_kind="white", n_resonators=3)
    seg = v2.render_note(110.0, 0.5)
    print(f"  white->3xVA @110Hz: {len(seg)} samples, rms={np.sqrt((seg**2).mean()):.4f}")
    assert len(audio) > 44100 * 1.5
    assert np.isfinite(audio).all()
    assert np.abs(audio).max() > 0.01
    print("demo OK")


if __name__ == "__main__":
    demo()
