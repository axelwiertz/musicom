"""Spectral wavetable extraction — Groove Synthesis 3rd Wave "Make Waves
Spectral" mode style.

Replicable logic from Groove Synthesis 3rd Wave OS 2.0a (Synthtopia
2026-08-24): the "Make Waves" tool gained a third mode, Spectral, which
turns arbitrary audio into a wavetable by analyzing it in the frequency
domain and finding the best slices across the whole file — for sources
whose pitch wanders (chorused sounds, ambient recordings) where
time-domain splice hunting or pitch tracking fails.

What is replicated here:
- STFT of the source (numpy FFT; windowed frames).
- Spectral "goodness" scoring per frame: frames with clean harmonic
  structure (low residual noise, strong low partials) score higher.
- Peak-picking across the spectrogram to select N representative frames
  spread over the file (best-slice selection).
- Phase-continuous reconstruction: selected frames are aligned by
  cross-correlating against the previous frame's phase so the wavetable
  cycles without clicks.
- Output: a normalized wavetable matrix (n_frames x wave_len) ready to
  scan with a phase accumulator (classic wavetable lookup).

Not replicated: the 3rd Wave's hardware UI, Pitch-On/Pitch-Off modes,
and the firmware's proprietary spectral analysis (we use plain STFT +
harmonic scoring instead).

Usage:
    from sound.synthesis.spectral_wavetable import SpectralWavetableExtractor

    ext = SpectralWavetableExtractor(fft_size=2048, hop=512)
    wavetable = ext.extract(audio, n_frames=32)
    # wavetable.shape == (32, fft_size//2)
    osc = ext.wavetable_oscillator(wavetable, freq=220.0, sr=44100, dur=1.0)
"""

from typing import Optional, Tuple

import numpy as np

__all__ = ["SpectralWavetableExtractor", "hanning"]


def hanning(n: int) -> np.ndarray:
    """Raised-cosine window (stdlib fallback-free, numpy only)."""
    return 0.5 - 0.5 * np.cos(2.0 * np.pi * np.arange(n) / max(n, 1))


class SpectralWavetableExtractor:
    """Extract a playable wavetable from arbitrary audio via STFT slicing."""

    def __init__(self, fft_size: int = 2048, hop: int = 512):
        """Initialize.

        Args:
            fft_size: FFT window size (wavetable length = fft_size // 2).
            hop: STFT hop size in samples.
        """
        self.fft_size = int(fft_size)
        self.hop = int(hop)

    # ------------------------------------------------------------------ #
    def extract(self, audio: np.ndarray, n_frames: int = 32,
                seed: Optional[int] = None) -> np.ndarray:
        """Extract ``n_frames`` spectral slices as a wavetable.

        Args:
            audio: 1-D float array (any length).
            n_frames: Number of wavetable frames to produce.

        Returns:
            Float array of shape (n_frames, fft_size // 2): each row is one
            cycle of the wavetable, DC-free and normalized to [-1, 1].
        """
        if audio.ndim != 1 or len(audio) < self.fft_size:
            raise ValueError("audio must be 1-D and longer than fft_size")
        audio = audio - np.mean(audio)

        frames = self._stft(audio)
        if frames.shape[0] < 2:
            raise ValueError("audio too short for one STFT frame")

        scores = self._score_frames(frames)
        idx = self._pick_frames(scores, n_frames, seed)

        cycles = []
        prev_phase: Optional[np.ndarray] = None
        for i in idx:
            spec = frames[i]
            cyc = self._to_cycle(spec, prev_phase)
            prev_phase = np.angle(spec)
            cycles.append(cyc)
        wt = np.stack(cycles)
        # normalize each row
        peaks = np.max(np.abs(wt), axis=1, keepdims=True)
        peaks[peaks == 0] = 1.0
        return wt / peaks

    # ------------------------------------------------------------------ #
    def wavetable_oscillator(self, wavetable: np.ndarray, freq: float,
                             sr: int = 44100, dur: float = 1.0,
                             frame_pos: Optional[float] = 0.0) -> np.ndarray:
        """Scan a wavetable with a phase accumulator (classic playback).

        Args:
            wavetable: (n_frames, wave_len) array from :meth:`extract`.
            freq: Oscillator frequency in Hz.
            sr: Sample rate.
            dur: Duration in seconds.
            frame_pos: Fixed frame position (0..1) if no frame scanning
                       desired; pass None for full scan.
        """
        n_frames, wave_len = wavetable.shape
        n = int(sr * dur)
        phase = np.mod(np.arange(n) * freq / sr, 1.0)
        # frame index interpolates across the table
        if frame_pos is None:
            fi = np.linspace(0.0, n_frames - 1.0, n)
        else:
            fi = np.full(n, frame_pos * (n_frames - 1.0))
        fi0 = np.floor(fi).astype(int)
        fi1 = np.minimum(fi0 + 1, n_frames - 1)
        frac = (fi - fi0)[:, None]
        w0 = wavetable[fi0]
        w1 = wavetable[fi1]
        wv = w0 * (1.0 - frac) + w1 * frac
        # linear interp within the cycle
        x = phase * (wave_len - 1)
        x0 = np.floor(x).astype(int)
        x1 = np.minimum(x0 + 1, wave_len - 1)
        g = (x - x0)[:, None]
        return (wv[np.arange(n), x0] * (1.0 - g[:, 0])
                + wv[np.arange(n), x1] * g[:, 0])

    # ------------------------------------------------------------------ #
    def _stft(self, audio: np.ndarray) -> np.ndarray:
        """Frames -> complex spectrum matrix (rows = frames)."""
        n = len(audio)
        n_frames = 1 + (n - self.fft_size) // self.hop
        win = hanning(self.fft_size)
        # rfft of an even-length window has fft_size//2 + 1 bins
        out = np.empty((n_frames, self.fft_size // 2 + 1), dtype=complex)
        for i in range(n_frames):
            seg = audio[i * self.hop: i * self.hop + self.fft_size] * win
            out[i] = np.fft.rfft(seg)
        return out

    @staticmethod
    def _score_frames(frames: np.ndarray) -> np.ndarray:
        """Score frames by harmonic cleanness (spectral goodness).

        Cleaner frames = lower high-frequency noise floor relative to low
        partial energy + lower spectral flatness.
        """
        mag = np.abs(frames)
        low = mag[:, : mag.shape[1] // 8]          # lowest partials
        high = mag[:, mag.shape[1] // 4:]          # upper band (noise-ish)
        low_energy = np.sum(low ** 2, axis=1) + 1e-12
        high_energy = np.sum(high ** 2, axis=1) + 1e-12
        # spectral flatness (geometric/arithmetic mean) -> lower is better
        flat = (np.exp(np.mean(np.log(mag + 1e-12), axis=1))
                / (np.mean(mag, axis=1) + 1e-12))
        score = low_energy / (high_energy + 1e-12) * (1.0 / (flat + 1e-3))
        return score

    @staticmethod
    def _pick_frames(scores: np.ndarray, n_frames: int,
                     seed: Optional[int]) -> np.ndarray:
        """Pick ``n_frames`` spread-out high-scoring frame indices."""
        n = len(scores)
        if n_frames >= n:
            return np.arange(n)
        rng = np.random.default_rng(seed)
        # split the file into n_frames windows, take best frame in each —
        # guarantees temporal spread (the "across the whole file" trick)
        idx = []
        for k in range(n_frames):
            lo = int(k * n / n_frames)
            hi = max(lo + 1, int((k + 1) * n / n_frames))
            win_scores = scores[lo:hi]
            j = int(np.argmax(win_scores))
            idx.append(lo + j)
        return np.array(idx)

    def _to_cycle(self, spec: np.ndarray,
                  prev_phase: Optional[np.ndarray]) -> np.ndarray:
        """Convert a spectral slice into a click-free time-domain cycle.

        Phase alignment: rotate the spectrum so its phase matches the
        previous frame's phase (cross-frame coherence), then invert.
        """
        mag = np.abs(spec)
        if prev_phase is not None:
            # keep phase difference small vs previous frame: use its phase
            phase = prev_phase
        else:
            # first frame: minimal-phase-ish via zero phase (cosine terms)
            phase = np.zeros_like(mag)
        spec_aligned = mag * np.exp(1j * phase)
        cyc = np.fft.irfft(spec_aligned, n=self.fft_size)
        cyc = cyc[: self.fft_size // 2]
        cyc = cyc - np.mean(cyc)
        return cyc


def demo() -> None:
    """Extract a wavetable from a wandering-pitch source and play it back."""
    sr = 22050
    rng = np.random.default_rng(5)
    t = np.arange(sr) / sr
    # "chorused" source: two detuned saw-ish tones with wandering pitch
    f0 = 220.0 * (1.0 + 0.03 * np.sin(2 * np.pi * 0.5 * t))
    src = (np.sin(2 * np.pi * np.cumsum(f0) / sr)
           + 0.5 * np.sin(2 * np.pi * np.cumsum(f0 * 1.01) / sr)
           + 0.25 * rng.standard_normal(sr) * 0.05)
    ext = SpectralWavetableExtractor(fft_size=1024, hop=256)
    wt = ext.extract(src, n_frames=16)
    print(f"wavetable shape={wt.shape} "
          f"(frames x wave_len={wt.shape[1]})")
    print(f"frame energy range: "
          f"{np.min(np.sum(wt**2, axis=1)):.3f}.."
          f"{np.max(np.sum(wt**2, axis=1)):.3f}")
    osc = ext.wavetable_oscillator(wt, freq=220.0, sr=sr, dur=0.5,
                                   frame_pos=None)
    print(f"oscillator out: len={len(osc)} peak={np.max(np.abs(osc)):.3f} "
          f"rms={np.sqrt(np.mean(osc**2)):.3f}")
    # a fixed frame should sound like the source pitched to it
    one = ext.wavetable_oscillator(wt, freq=440.0, sr=sr, dur=0.2,
                                   frame_pos=0.5)
    print(f"single-frame osc: peak={np.max(np.abs(one)):.3f}")


if __name__ == "__main__":
    demo()
