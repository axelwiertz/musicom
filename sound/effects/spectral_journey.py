# -*- coding: utf-8 -*-
"""Spectral "Journey" engine — Blinksonic Holodrift-style granular×spectral morph.

Source: MusicTech "The best new music plugins this week" (2026-10-22):
Blinksonic Holodrift = 8 granular slots, a "Journey" control that morphs between
the slots, then a spectral engine that "breaks the sound into partials, alters
them with 15 different effects, and rebuilds it".

What is replicated here (real DSP, no ML):

- **8 slots** (``set_slot``) each holding an arbitrary buffer; slot 0..7.
- **Journey morph**: a continuous position ``p`` in 0..7 linearly interpolates
  the *complex STFT* of the two neighbouring slots, so partials cross-fade
  coherently instead of two audio streams being gain-blended (no beating /
  phase cancellation at the seam).
- **Grain size ↔ time-frequency uncertainty**: ``grain_ms`` sets the STFT
  window length. Short windows (5–20 ms) smear frequency and read as broadband
  noise-like; long windows (60–200 ms) resolve stable pitch. This is the
  literal time-frequency trade-off the hardware/plugin exposes.
- **15 spectral partial effects** (see ``SPECTRAL_EFFECTS``): ``shift``,
  ``stretch``, ``compress``, ``freeze``, ``blur_freq``, ``blur_time``,
  ``prune``, ``inharmonic``, ``comb``, ``tilt``, ``formant``, ``phase_rand``,
  ``gate``, ``mirror``, ``ring``.

Not replicated: Blinksonic's proprietary effect voicings/UI, its sample
library, and the tabletop macro layout.

Usage:
    from sound.effects.spectral_journey import SpectralJourney
    sj = SpectralJourney(sample_rate=44100)
    for i, buf in enumerate(buffers[:8]):
        sj.set_slot(i, buf)
    out = sj.render(position=3.4, effects=[("blur_freq", {"bins": 3}),
                                          ("prune", {"keep": 12})],
                    grain_ms=40.0)
"""

from __future__ import annotations

from typing import Dict, List, Sequence, Tuple

import numpy as np

__all__ = ["SpectralJourney", "SPECTRAL_EFFECTS", "stft", "istft"]

SPECTRAL_EFFECTS: Tuple[str, ...] = (
    "shift", "stretch", "compress", "freeze", "blur_freq", "blur_time",
    "prune", "inharmonic", "comb", "tilt", "formant", "phase_rand",
    "gate", "mirror", "ring",
)


def stft(x: np.ndarray, n_fft: int, hop: int) -> np.ndarray:
    """Hann-windowed STFT -> complex matrix (frames, bins)."""
    win = np.hanning(n_fft + 1)[:-1]
    if len(x) < n_fft:
        x = np.pad(x, (0, n_fft - len(x)))
    n_frames = 1 + (len(x) - n_fft) // hop
    idx = np.arange(n_fft)[None, :] + hop * np.arange(n_frames)[:, None]
    return np.fft.rfft(x[idx] * win, axis=1)


def istft(spec: np.ndarray, n_fft: int, hop: int, length: int) -> np.ndarray:
    """Overlap-add inverse STFT with Hann analysis window normalisation."""
    win = np.hanning(n_fft + 1)[:-1]
    frames = np.fft.irfft(spec, n=n_fft, axis=1) * win
    out = np.zeros(hop * (len(frames) - 1) + n_fft)
    norm = np.zeros_like(out)
    for i, fr in enumerate(frames):
        out[i * hop:i * hop + n_fft] += fr
        norm[i * hop:i * hop + n_fft] += win ** 2
    out /= np.maximum(norm, 1e-9)
    if length <= len(out):
        return out[:length]
    return np.pad(out, (0, length - len(out)))


def _bin_freqs(n_fft: int, sr: int) -> np.ndarray:
    return np.fft.rfftfreq(n_fft, 1.0 / sr)


def _resample_bins(mag: np.ndarray, mapping: np.ndarray) -> np.ndarray:
    """Sample a magnitude spectrum at fractional bin positions."""
    src = np.arange(mag.shape[-1], dtype=np.float64)
    flat = mag.reshape(-1, mag.shape[-1])
    out = np.empty_like(flat)
    for i in range(flat.shape[0]):
        out[i] = np.interp(mapping, src, flat[i], left=0.0, right=0.0)
    return out.reshape(mag.shape)


class SpectralJourney:
    """8-slot granular/spectral morph engine (Holodrift-style)."""

    def __init__(self, sample_rate: int = 44100, n_slots: int = 8,
                 seed: int = 0):
        self.sr = int(sample_rate)
        self.n_slots = int(n_slots)
        self.slots: List[np.ndarray] = [np.zeros(0)] * self.n_slots
        self.rng = np.random.default_rng(seed)

    # -- slots -------------------------------------------------------------
    def set_slot(self, index: int, audio: np.ndarray) -> None:
        if not 0 <= index < self.n_slots:
            raise IndexError(f"slot {index} out of range 0..{self.n_slots - 1}")
        a = np.asarray(audio, dtype=np.float64)
        if a.ndim > 1:
            a = a.mean(axis=1)
        self.slots[index] = a

    def load_slots(self, buffers: Sequence[np.ndarray]) -> None:
        for i, b in enumerate(buffers[: self.n_slots]):
            self.set_slot(i, b)

    def _slot_or_pad(self, i: int, n: int) -> np.ndarray:
        a = self.slots[i % self.n_slots]
        if len(a) == 0:
            a = np.zeros(n)
        if len(a) < n:
            a = np.pad(a, (0, n - len(a)))
        return a[:n]

    def journey_weights(self, position: float) -> List[Tuple[int, float]]:
        """Linear morph weights: [(slot_lo, w_lo), (slot_hi, w_hi)]."""
        p = float(np.clip(position, 0, self.n_slots - 1))
        lo = int(np.floor(p))
        hi = min(lo + 1, self.n_slots - 1)
        frac = p - lo
        return [(lo, 1.0 - frac), (hi, frac)]

    # -- spectral effects --------------------------------------------------
    def _apply_effect(self, spec: np.ndarray, name: str, params: Dict,
                      n_fft: int, hop: int) -> np.ndarray:
        mag = np.abs(spec)
        ph = np.angle(spec)
        freqs = _bin_freqs(n_fft, self.sr)
        bins = np.arange(mag.shape[-1], dtype=np.float64)

        if name == "shift":
            hz = float(params.get("hz", 220.0))
            mag = _resample_bins(mag, bins - hz / (self.sr / n_fft))
        elif name == "stretch":
            r = float(params.get("ratio", 1.5))
            if abs(r - 1.0) > 1e-9:
                mag = _resample_bins(mag, bins / r)
        elif name == "compress":
            thr = float(params.get("threshold", 0.35))
            amt = float(params.get("amount", 0.7))
            m = mag / max(mag.max(), 1e-12)
            mag = np.where(m > thr, (thr + (m - thr) * (1 - amt)) * mag.max(),
                           mag)
        elif name == "freeze":
            hold = mag[0:1, :]
            mag = np.repeat(hold, mag.shape[0], axis=0) * np.ones_like(mag)
        elif name == "blur_freq":
            k = max(1, int(params.get("bins", 3)))
            kern = np.ones(k) / k
            mag = np.apply_along_axis(lambda v: np.convolve(v, kern, "same"),
                                      1, mag)
        elif name == "blur_time":
            k = max(1, int(params.get("frames", 5)))
            kern = np.ones(k) / k
            mag = np.apply_along_axis(lambda v: np.convolve(v, kern, "same"),
                                      0, mag)
        elif name == "prune":
            keep = max(1, int(params.get("keep", 16)))
            out = np.zeros_like(mag)
            for f in range(mag.shape[0]):
                top = np.argpartition(mag[f], -keep)[-keep:]
                out[f, top] = mag[f, top]
            mag = out
        elif name == "inharmonic":
            k = float(params.get("amount", 0.4))
            warp = bins * (1.0 + k * bins / max(1.0, bins[-1]))
            mag = _resample_bins(mag, warp)
        elif name == "comb":
            period_hz = float(params.get("period_hz", 180.0))
            depth = float(params.get("depth", 0.8))
            mag = mag * (1.0 - depth * 0.5 * (1 - np.cos(
                2 * np.pi * freqs / max(period_hz, 1.0))))
        elif name == "tilt":
            db_oct = float(params.get("db_per_oct", -6.0))
            f = np.maximum(freqs, 20.0)
            mag = mag * 10 ** (db_oct * np.log2(f / 1000.0) / 20.0)
        elif name == "formant":
            semis = float(params.get("semitones", 7.0))
            env = np.apply_along_axis(
                lambda v: np.convolve(v, np.ones(17) / 17, "same"), 1, mag)
            env_s = _resample_bins(env, bins / (2 ** (semis / 12.0)))
            mag = mag * (env_s / np.maximum(env, 1e-9))
        elif name == "phase_rand":
            amt = float(params.get("amount", 1.0))
            ph = ph + amt * self.rng.uniform(-np.pi, np.pi, ph.shape)
        elif name == "gate":
            thr = float(params.get("threshold", 0.2))
            rel = None
            if params.get("relative", True):
                rel = np.max(mag, axis=1, keepdims=True)
            else:
                rel = np.max(mag)
            mag = np.where(mag > thr * rel, mag, 0.0)
        elif name == "mirror":
            mag = mag[:, ::-1]
        elif name == "ring":
            hz = float(params.get("hz", 40.0))
            depth = float(params.get("depth", 0.7))
            t = np.arange(mag.shape[0]) * hop / self.sr
            mod = 1.0 - depth * 0.5 * (1 + np.sin(2 * np.pi * hz * t))
            mag = mag * mod[:, None]
        else:
            raise ValueError(f"unknown spectral effect {name!r}; "
                             f"choose from {SPECTRAL_EFFECTS}")
        mag = np.maximum(mag, 0.0)
        return mag * np.exp(1j * ph)

    # -- grain layer (time-frequency uncertainty) --------------------------
    def _grain_source(self, position: float, n: int) -> np.ndarray:
        mix = np.zeros(n)
        for slot, w in self.journey_weights(position):
            if w > 0:
                mix += w * self._slot_or_pad(slot, n)
        return mix

    def render_granular(self, position: float = 0.0, grain_ms: float = 40.0,
                        grain_rate: float = 30.0, jitter: float = 0.6,
                        scramble=None, duration=None,
                        normalize: bool = True) -> np.ndarray:
        """Granular re-synthesis: short grains -> broadband, long -> pitched.

        Each grain is read from a jittered source position and its phase is
        scrambled by ``scramble`` (default derived from grain length: grains
        shorter than 40 ms are progressively decorrelated). Phase scrambling
        is what turns 5 ms grains into noise-like hits and 200 ms grains into
        stable tones — the time-frequency trade-off, done in real DSP.
        """
        n = int(self.sr * duration) if duration else max(
            (len(s) for s in self.slots if len(s)), default=self.sr)
        src = self._grain_source(position, n + int(grain_ms * self.sr / 1000))
        gn = max(16, int(grain_ms * self.sr / 1000))
        hop = max(1, int(self.sr / max(1.0, grain_rate)))
        win = np.hanning(gn)
        sc = (max(0.0, 1.0 - grain_ms / 40.0) if scramble is None
              else float(scramble))
        out = np.zeros(len(src) + gn)
        norm = np.zeros_like(out)
        jit = int(jitter * gn / 2)
        for start in range(0, max(1, len(src) - gn), hop):
            pos = int(np.clip(start + self.rng.integers(-jit, jit + 1),
                              0, len(src) - gn))
            g = src[pos:pos + gn] * win
            if sc > 0:
                spec = np.fft.rfft(g)
                ph = np.angle(spec) + sc * self.rng.uniform(-np.pi, np.pi,
                                                            spec.shape)
                g = np.fft.irfft(np.abs(spec) * np.exp(1j * ph), n=gn)
            out[start:start + gn] += g * win
            norm[start:start + gn] += win ** 2
        out /= np.maximum(norm, 1e-6)
        out = out[:n]
        if normalize:
            peak = np.max(np.abs(out))
            if peak > 1e-9:
                out = out / peak * 0.9
        return out.astype(np.float32)

    # -- render ------------------------------------------------------------
    def render(self, position: float = 0.0,
               effects: Sequence = (),
               grain_ms: float = 40.0,
               duration: float = None,
               normalize: bool = True) -> np.ndarray:
        """Render the morph at ``position`` with an ordered effect chain."""
        n_fft = int(2 ** max(6, round(np.log2(max(64.0,
                                                grain_ms * self.sr / 1000.0)))))
        hop = max(1, n_fft // 4)
        n = int(self.sr * duration) if duration else max(
            (len(s) for s in self.slots if len(s)), default=self.sr)
        mix = np.zeros((0, n_fft // 2 + 1), dtype=complex)
        for slot, w in self.journey_weights(position):
            if w <= 0:
                continue
            spec = stft(self._slot_or_pad(slot, n), n_fft, hop)
            if mix.shape[0] == 0:
                mix = np.zeros_like(spec)
            m = min(mix.shape[0], spec.shape[0])
            mix[:m] += w * spec[:m]
        for eff in effects:
            name, params = (eff, {}) if isinstance(eff, str) else eff
            mix = self._apply_effect(mix, name, params or {}, n_fft, hop)
        out = istft(mix, n_fft, hop, n)
        if normalize:
            peak = np.max(np.abs(out))
            if peak > 1e-9:
                out = out / peak * 0.9
        return out.astype(np.float32)


def _tone(f0: float, sr: int, dur: float, partials: int = 8,
          rolloff: float = 0.7) -> np.ndarray:
    t = np.arange(int(sr * dur)) / sr
    out = np.zeros_like(t)
    for k in range(1, partials + 1):
        out += (rolloff ** (k - 1)) * np.sin(2 * np.pi * f0 * k * t)
    return out / max(1e-9, np.max(np.abs(out)))


def _centroid(x: np.ndarray, sr: int) -> float:
    s = np.abs(np.fft.rfft(x * np.hanning(len(x))))
    f = np.fft.rfftfreq(len(x), 1.0 / sr)
    return float((s * f).sum() / max(s.sum(), 1e-12))


def _flatness(x: np.ndarray, n: int = 512) -> float:
    """Mean short-time spectral flatness — rises with partial smearing."""
    win = np.hanning(n)
    frames = [x[i:i + n] * win for i in range(0, max(1, len(x) - n), n // 2)]
    vals = []
    for fr in frames:
        s = np.abs(np.fft.rfft(fr)) + 1e-12
        vals.append(np.exp(np.mean(np.log(s))) / np.mean(s))
    return float(np.mean(vals))


def demo() -> str:
    """Morph a harmonic stack -> saw -> noise band and apply partial effects."""
    sr = 22050
    sj = SpectralJourney(sample_rate=sr)
    noise = np.random.default_rng(7).uniform(-1, 1, sr)
    # crude band-limit: one-pole lowpass applied twice
    for _ in range(2):
        noise = np.convolve(noise, np.ones(8) / 8, "same")
    sj.load_slots([_tone(220, sr, 1.0, 8, 0.72),
                   _tone(110, sr, 1.0, 16, 0.93),
                   0.5 * noise / max(1e-9, np.max(np.abs(noise)))])
    rows = []
    for pos in (0.0, 1.0, 1.5, 2.0):
        out = sj.render(position=pos, grain_ms=64.0)
        rows.append(f"p={pos:.1f} centroid={_centroid(out, sr):7.1f}Hz "
                    f"rms={np.sqrt(np.mean(out ** 2)):.3f}")
    eff_rows = []
    for eff in ("prune", "blur_freq", "inharmonic", "phase_rand", "mirror"):
        out = sj.render(position=0.0, grain_ms=64.0,
                        effects=[(eff, {"keep": 6, "bins": 5,
                                        "amount": 0.6})])
        eff_rows.append(f"{eff:11s} centroid={_centroid(out, sr):7.1f}Hz")
    short = sj.render_granular(position=0.0, grain_ms=8.0)
    long_ = sj.render_granular(position=0.0, grain_ms=180.0, jitter=0.05)
    assert np.all(np.isfinite(short)) and np.all(np.isfinite(long_))
    f_short, f_long = _flatness(short), _flatness(long_)
    assert f_short > f_long, "short grains must smear partials (high flatness)"
    return ("slots=3 grain-morph OK\n  " + "\n  ".join(rows) +
            "\n  -- effects --\n  " + "\n  ".join(eff_rows) +
            f"\n  granular 8ms flatness={f_short:.4f} vs "
            f"180ms={f_long:.4f} (short grains decorrelate -> broadband, "
            f"long grains stay pitched; {len(short)} samples)")


if __name__ == "__main__":
    print(demo())
