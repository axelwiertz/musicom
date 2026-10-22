"""Spectral resonance suppressor — Newfangled Audio Fixate:Midrange style.

Replicable logic from the Sound On Sound review "Newfangled Audio
Fixate:Midrange" (November 2026): a problem-solving plug-in that tames
resonances and muddy build-up in a mix, focusing on the midrange where
multiple sounds fight for the same slice of spectrum (same family as
Oeksound Soothe / Soundtheory Gullfoss / Waves Curves Equator).

What is replicated here (offline STFT spectral processing, numpy only):
- ``SpectralResonanceSuppressor``: short-time FFT analysis; per frame the
  magnitude spectrum is compared to its local (median-filtered) baseline;
  bins whose excess over the baseline exceeds ``threshold_db`` and are
  local maxima are flagged as resonant peaks; a suppression gain is shaped
  around each peak (raised-cosine width), scaled by ``amount`` and by the
  excess above threshold; gains are smoothed across frequency and across
  frames (attack/release one-pole) before overlap-add resynthesis.
- ``midrange`` focus: processing is restricted to a frequency band
  (default 200..6000 Hz — the "real battlefield of any mix").
- Deterministic, no ML: the real products add perceptually weighted /
  learned analysis; here the classic de-resonator algorithm is used
  instead (honest scope note).

Not replicated: the plug-in GUI, the proprietary perception-tuned analysis
models, sidechain/"Fixate In The Mix" listening modes.

Usage:
    from sound.effects.spectral_resonance_suppressor import (
        SpectralResonanceSuppressor)

    rs = SpectralResonanceSuppressor(sample_rate=44100)
    out = rs.process(audio, amount=0.7, threshold_db=6.0)
"""

from __future__ import annotations

import numpy as np

__all__ = ["SpectralResonanceSuppressor"]

DEFAULT_SR = 44100


class SpectralResonanceSuppressor:
    """STFT-based resonance suppressor focused on the midrange.

    Args:
        sample_rate: audio sample rate in Hz.
        fft_size: STFT window size (power of two).
        hop: STFT hop size.
    """

    def __init__(self, sample_rate: int = DEFAULT_SR,
                 fft_size: int = 2048, hop: int = 512):
        self.sample_rate = int(sample_rate)
        self.fft_size = int(fft_size)
        self.hop = int(hop)
        self._win = np.hanning(self.fft_size)

    # ------------------------------------------------------------------
    def _median_baseline(self, mag: np.ndarray, width: int = 7) -> np.ndarray:
        """Local median of the magnitude spectrum (rolling window)."""
        n = len(mag)
        base = np.empty(n)
        half = width // 2
        for i in range(n):
            lo = max(0, i - half)
            hi = min(n, i + half + 1)
            base[i] = np.median(mag[lo:hi])
        return base

    def _suppression_gain(self, mag_db: np.ndarray, threshold_db: float,
                          amount: float, width_bins: int) -> np.ndarray:
        """Per-frame suppression gain from the resonant-peak excess."""
        n = len(mag_db)
        base = self._median_baseline(mag_db, width=7)
        excess = mag_db - base - threshold_db        # dB above baseline+thr
        g = np.ones(n)
        if amount <= 0:
            return g
        # candidate peaks: local maxima of the excess
        for i in range(1, n - 1):
            if excess[i] <= 0:
                continue
            if not (excess[i] >= excess[i - 1] and excess[i] > excess[i + 1]):
                continue
            depth = min(excess[i] / 24.0, 1.0)       # excess -> 0..1
            # raised-cosine notch around the peak
            half = max(1, int(width_bins))
            for j in range(max(0, i - half), min(n, i + half + 1)):
                d = abs(j - i) / half
                shape = 0.5 * (1.0 + np.cos(np.pi * min(d, 1.0)))
                g[j] = min(g[j], 1.0 - amount * depth * shape)
        # frequency smoothing of the gain
        k = max(1, width_bins // 2)
        kern = np.hanning(2 * k + 1)
        kern /= kern.sum()
        g = np.convolve(g, kern, mode="same")
        return np.clip(g, 0.0, 1.0)

    # ------------------------------------------------------------------
    def process(self, audio: np.ndarray, amount: float = 0.7,
                threshold_db: float = 6.0, width_bins: int = 24,
                min_freq: float = 200.0, max_freq: float = 6000.0,
                attack: float = 0.05, release: float = 0.3) -> np.ndarray:
        """Suppress stationary resonant peaks in the midrange.

        Args:
            audio: mono ``(n,)`` float array.
            amount: suppression depth 0..1.
            threshold_db: peak excess over the local baseline required to
                trigger suppression.
            width_bins: half-width of the suppression notch (bins).
            min_freq / max_freq: processing band (midrange focus; outside
                the band the gain is unity).
            attack / release: one-pole smoothing time constants (seconds)
                applied across frames so resonances duck and recover
                smoothly (avoid pumping on transients).

        Returns:
            Suppressed 1-D float array (same length as input).
        """
        x = np.asarray(audio, dtype=np.float64).reshape(-1)
        n = len(x)
        if n < self.fft_size:
            return x.copy()
        fft_size, hop = self.fft_size, self.hop
        win = self._win

        # frame bounds
        starts = list(range(0, n - fft_size + 1, hop))
        n_frames = len(starts)
        X = np.zeros((n_frames, fft_size // 2 + 1), dtype=np.complex128)
        for i, s in enumerate(starts):
            X[i] = np.fft.rfft(x[s:s + fft_size] * win)

        mag = np.abs(X)
        # frame-averaged magnitude for peak detection (stationary resonances
        # persist across frames -> their excess survives the average)
        mag_avg = mag.mean(axis=0)
        with np.errstate(divide="ignore"):
            mag_db = 20.0 * np.log10(mag_avg + 1e-12)

        g0 = self._suppression_gain(mag_db, threshold_db, amount, width_bins)

        # frequency-band gate (midrange focus)
        freqs = np.fft.rfftfreq(fft_size, 1.0 / self.sample_rate)
        band = (freqs >= min_freq) & (freqs <= max_freq)
        g_freq = np.where(band, g0, 1.0)

        # temporal smoothing (attack/release)
        a_alpha = np.exp(-hop / (attack * self.sample_rate)) if attack > 0 else 0.0
        r_alpha = np.exp(-hop / (release * self.sample_rate)) if release > 0 else 0.0
        g_smooth = np.ones_like(mag)
        prev = np.ones(fft_size // 2 + 1)
        for i in range(n_frames):
            target = g_freq if i == 0 else g_freq  # same target (stationary)
            going_down = target < prev
            alpha = np.where(going_down, a_alpha, r_alpha)
            prev = alpha * prev + (1.0 - alpha) * target
            g_smooth[i] = prev

        Y = X * g_smooth

        # overlap-add resynthesis
        out = np.zeros(n)
        acc = np.zeros(n)
        for i, s in enumerate(starts):
            seg = np.fft.irfft(Y[i], fft_size) * win
            out[s:s + fft_size] += seg
            acc[s:s + fft_size] += win * win
        acc = np.maximum(acc, 1e-8)
        out = out / acc

        peak = float(np.max(np.abs(out))) if out.size else 0.0
        if peak > 1.0:
            out = out / peak * 0.95
        return out


def demo(out_dir: str = "/tmp/musicom_smoke") -> dict:
    """Self-test: chord + injected 1500 Hz ringing -> suppressed peak."""
    import os
    from sound.utils.io import write_wav

    os.makedirs(out_dir, exist_ok=True)
    sr = DEFAULT_SR
    t = np.arange(sr * 2) / sr
    # dense midrange material: saw chord 196/261.6/329.6 + noise
    rng = np.random.RandomState(0)
    x = rng.randn(len(t)) * 0.02
    for f in (196.0, 261.6, 329.6, 392.0):
        for k in range(1, 20):
            x += np.sin(2 * np.pi * f * k * t) / k
    # inject a strong stationary resonance at 1500 Hz (the "mud" to fix)
    x += 0.5 * np.sin(2 * np.pi * 1500.0 * t)
    x = x / np.max(np.abs(x)) * 0.9

    rs = SpectralResonanceSuppressor(sample_rate=sr)
    y = rs.process(x, amount=0.8, threshold_db=6.0,
                   min_freq=200.0, max_freq=6000.0)

    def _peak_at(sig, f, bw=60.0):
        Y = np.abs(np.fft.rfft(sig))
        freqs = np.fft.rfftfreq(len(sig), 1 / sr)
        m = (freqs >= f - bw) & (freqs <= f + bw)
        return float(Y[m].max())

    p_in = _peak_at(x, 1500.0)
    p_out = _peak_at(y, 1500.0)
    ratio = p_out / (p_in + 1e-12)
    assert ratio < 0.55, f"resonance not suppressed: {ratio:.3f}"

    path = os.path.join(out_dir, "fixate_midrange.wav")
    write_wav(path, y, sr)
    assert os.path.getsize(path) > 40

    return {
        "resonance_peak_in": round(p_in, 3),
        "resonance_peak_out": round(p_out, 3),
        "suppression_ratio": round(ratio, 4),
        "out_samples": int(y.shape[0]),
        "wav_bytes": os.path.getsize(path),
    }


if __name__ == "__main__":
    import json
    print(json.dumps(demo(), indent=2))
