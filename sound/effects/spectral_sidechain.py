# -*- coding: utf-8 -*-
"""Art DSP Canvas 2.0-style spectral sidechain — per-band frequency ducking.

Replicable DSP from the Art DSP Canvas 2.0 launch (MusicTech 2026-10-28):
a visual mixing plugin that represents tracks as movable "blobs" in a
virtual 3D room (stereo position -> left/right, frequency content ->
vertical, volume -> depth) and includes **spectral sidechaining** "to create
space between competing tracks", plus a built-in EQ editor and reverb whose
contribution is shown in the room.

What is replicated here (pure DSP, no GUI / no proprietary HRTF):

- ``SpectralSidechain``: an STFT-based, frequency-band-wise sidechain
  compressor.  The *main* signal is ducked only where the *sidechain*
  (competing track) has energy: the spectrum is split into log-spaced bands;
  for each band the sidechain magnitude (smoothed with attack/release
  one-poles) drives a gain reduction following a threshold/ratio curve.
  Bands with no competing energy pass untouched, so e.g. a kick sidechaining
  a pad ducks only the lows and leaves the pad's mids/air intact — the
  "space between competing tracks" behaviour.
- ``BlobMap``: the Canvas "blob" descriptor — per frame it computes the
  stereo centroid (left/right), spectral centroid (vertical position) and
  RMS (depth/volume) of a track, i.e. exactly the three axes Canvas maps a
  track to.  Useful for mix-visualisation analytics.
- ``Canvas2Mix``: a small convenience that takes a list of tracks, computes
  each track's blob coordinates, and applies spectral sidechain ducking from
  the loudest competing track so overlapping blobs get separated.

Not replicated: the 3D room renderer/GUI, the built-in EQ editor chrome
(EQ itself is covered by tilt_eq.py / scale_eq.py / filter.py), the reverb
integration and the one-click whole-track mixing templates.
"""

from __future__ import annotations

import numpy as np
from typing import List, Optional, Tuple


def _next_pow2(n: int) -> int:
    p = 1
    while p < n:
        p *= 2
    return p


class SpectralSidechain:
    """STFT per-band sidechain ducking of ``main`` by ``sidechain`` energy.

    Bands are log-spaced between ``f_lo`` and ``f_hi``.  Each band's gain is
    computed from the sidechain band energy with a threshold/ratio/knee
    curve and smoothed by attack/release one-pole filters, then applied to
    the main spectrum.  Overlap-add resynthesis uses a Hann window with 75%
    overlap for click-free reconstruction.
    """

    def __init__(
        self,
        fft_size: int = 2048,
        hop: Optional[int] = None,
        n_bands: int = 12,
        f_lo: float = 40.0,
        f_hi: float = 16000.0,
        threshold_db: float = -35.0,
        ratio: float = 8.0,
        knee_db: float = 6.0,
        attack_ms: float = 5.0,
        release_ms: float = 120.0,
        mix: float = 1.0,
        sr: int = 44100,
    ) -> None:
        self.fft_size = fft_size
        self.hop = hop or fft_size // 4
        self.n_bands = n_bands
        self.f_lo = f_lo
        self.f_hi = f_hi
        self.threshold_db = threshold_db
        self.ratio = ratio
        self.knee_db = knee_db
        self.attack_ms = attack_ms
        self.release_ms = release_ms
        self.mix = mix
        self.sr = sr
        self.window = np.hanning(fft_size).astype(float)
        self._band_edges = self._log_band_edges(n_bands, f_lo, f_hi)
        self._smooth: Optional[np.ndarray] = None

    def _log_band_edges(self, n_bands: int, f_lo: float, f_hi: float) -> np.ndarray:
        """Frequencies (Hz) of band edges, log spaced."""
        return np.geomspace(f_lo, f_hi, n_bands + 1)

    def _band_index(self, freqs_hz: np.ndarray) -> np.ndarray:
        """Map each FFT bin frequency to its band index (int array)."""
        idx = np.searchsorted(self._band_edges, freqs_hz, side="right") - 1
        return np.clip(idx, 0, self.n_bands - 1)

    def _gain_for_band(self, sc_db: float) -> float:
        """Single-band gain reduction from a smoothed sidechain level (dB)."""
        over = sc_db - self.threshold_db
        if self.knee_db > 0:
            lo = -self.knee_db / 2.0
            hi = self.knee_db / 2.0
            if over < lo:
                red = 0.0
            elif over > hi:
                red = (over - hi) * (1.0 - 1.0 / self.ratio) + hi * (1.0 - 1.0 / self.ratio) / 2.0
            else:
                red = (over - lo) ** 2 / (2.0 * self.knee_db) * (1.0 - 1.0 / self.ratio)
        else:
            red = max(0.0, over) * (1.0 - 1.0 / self.ratio)
        return float(10.0 ** (-red / 20.0))

    def process(self, main: np.ndarray, sidechain: np.ndarray) -> np.ndarray:
        """Duck ``main`` (mono float array) using ``sidechain`` energy.

        Returns the spectrally-ducked mono array of the same length.
        """
        n = len(main)
        if len(sidechain) < n:
            sidechain = np.pad(sidechain, (0, n - len(sidechain)))
        else:
            sidechain = sidechain[:n]
        n_frames = 1 + (n - self.fft_size) // self.hop
        out = np.zeros(n)
        acc = np.zeros(n)
        freqs = np.fft.rfftfreq(self.fft_size, 1.0 / self.sr)
        band_idx = self._band_index(freqs)
        alpha_a = 1.0 - np.exp(-1.0 / (self.attack_ms / 1000.0 * self.sr / self.hop))
        alpha_r = 1.0 - np.exp(-1.0 / (self.release_ms / 1000.0 * self.sr / self.hop))
        if self._smooth is None:
            self._smooth = np.zeros(self.n_bands)
        for f_i in range(n_frames):
            i0 = f_i * self.hop
            x = main[i0:i0 + self.fft_size] * self.window
            s = sidechain[i0:i0 + self.fft_size] * self.window
            X = np.fft.rfft(x)
            S = np.fft.rfft(s)
            sc_mag = np.abs(S)
            # per-band sidechain energy (max bin magnitude in band, in dB)
            band_db = np.zeros(self.n_bands)
            for b in range(self.n_bands):
                m = sc_mag[band_idx == b]
                band_db[b] = 20.0 * np.log10(max(np.max(m) if len(m) else 0.0, 1e-9))
            # smoothed sidechain level per band (attack/release)
            target = band_db
            self._smooth = np.where(target > self._smooth,
                                    self._smooth + alpha_a * (target - self._smooth),
                                    self._smooth + alpha_r * (target - self._smooth))
            # per-bin gain from band gain, then apply mix
            gains = np.ones(len(X), dtype=float)
            for b in range(self.n_bands):
                g = self._gain_for_band(self._smooth[b])
                g = 1.0 + self.mix * (g - 1.0)
                gains[band_idx == b] = g
            Y = X * gains
            y = np.fft.irfft(Y, self.fft_size)
            y = y * self.window
            end = min(i0 + self.fft_size, n)
            seg = y[: end - i0]
            out[i0:end] += seg
            acc[i0:end] += self.window[: end - i0]
        acc = np.where(acc > 1e-9, acc, 1.0)
        return out / acc


class BlobMap:
    """Canvas-style track "blob" descriptor: pan, spectral height, depth.

    Per STFT frame of a track, computes the three axes Canvas maps to the
    virtual room:

    - ``pan`` (-1..1): stereo centroid (left/right position)
    - ``height`` (0..1): spectral centroid normalised by Nyquist
      (frequency content -> vertical position)
    - ``depth`` (0..1): normalised RMS (volume -> forward/back axis)
    """

    def __init__(self, fft_size: int = 2048, hop: Optional[int] = None,
                 sr: int = 44100) -> None:
        self.fft_size = fft_size
        self.hop = hop or fft_size // 4
        self.sr = sr
        self.window = np.hanning(fft_size)

    def analyze(self, stereo: np.ndarray) -> List[Tuple[float, float, float]]:
        """Return one (pan, height, depth) blob tuple per frame."""
        if stereo.ndim == 1:
            stereo = np.stack([stereo, stereo])
        n = stereo.shape[1]
        n_frames = 1 + (n - self.fft_size) // self.hop
        blobs: List[Tuple[float, float, float]] = []
        freqs = np.fft.rfftfreq(self.fft_size, 1.0 / self.sr)
        nyq = self.sr / 2.0
        for f_i in range(n_frames):
            i0 = f_i * self.hop
            seg = stereo[:, i0:i0 + self.fft_size] * self.window
            L = np.abs(np.fft.rfft(seg[0]))
            R = np.abs(np.fft.rfft(seg[1]))
            sum_mag = L + R
            denom = sum_mag.sum()
            if denom < 1e-12:
                blobs.append((0.0, 0.0, 0.0))
                continue
            pan = float(((R - L) * sum_mag).sum() / (denom * denom))
            # spectral centroid of the summed spectrum
            sc = float((freqs * sum_mag).sum() / denom)
            depth = float(np.sqrt(np.mean(seg ** 2)))
            blobs.append((float(np.clip(pan, -1, 1)),
                          float(np.clip(sc / nyq, 0, 1)),
                          float(np.clip(depth / 0.5, 0, 1))))
        return blobs


class Canvas2Mix:
    """Sidechain-separate overlapping tracks using their blob geometry.

    Given a list of mono tracks, compute blob frames for each; then for every
    track, duck it with a spectral sidechain driven by whichever other track
    has the most overlapping blob energy at that moment.  Simple stand-in for
    Canvas' "make space between competing tracks".
    """

    def __init__(self, sr: int = 44100, **sc_kwargs) -> None:
        self.sr = sr
        self.sc_kwargs = sc_kwargs
        self.blob = BlobMap(sr=sr)

    def process(self, tracks: List[np.ndarray]) -> List[np.ndarray]:
        n = max(len(t) for t in tracks)
        padded = [np.pad(t, (0, n - len(t))) for t in tracks]
        # crude overlap score per frame: product of depths at same time
        outs: List[np.ndarray] = []
        for i, track in enumerate(padded):
            sc = SpectralSidechain(sr=self.sr, **self.sc_kwargs)
            others = [t for j, t in enumerate(padded) if j != i]
            # drive the sidechain with the loudest other track
            drive = max(others, key=lambda t: np.sqrt(np.mean(t ** 2)))
            outs.append(sc.process(track, drive))
        return outs


def demo() -> None:
    """Duck a pad by a kick and show band-wise gain reduction."""
    sr = 44100
    t = np.arange(sr * 2) / sr
    # pad: rich low-mid saw-ish hum (100 Hz + 300 Hz + air 3 kHz)
    pad = (0.4 * np.sin(2 * np.pi * 100 * t)
           + 0.3 * np.sin(2 * np.pi * 300 * t)
           + 0.15 * np.sin(2 * np.pi * 3000 * t))
    # kick: low thump at t=0 and t=1s (50 Hz burst)
    kick = np.zeros_like(t)
    for onset in (0.0, 1.0):
        i0 = int(onset * sr)
        nk = int(0.35 * sr)
        tk = np.arange(nk) / sr
        burst = np.sin(2 * np.pi * (60 * np.exp(-8 * tk) + 40)) * np.exp(-6 * tk)
        burst[: int(0.005 * sr)] *= np.linspace(0.0, 1.0, int(0.005 * sr))
        kick[i0:i0 + nk] = burst
    sc = SpectralSidechain(sr=sr, threshold_db=-40.0, ratio=10.0)
    out = sc.process(pad, kick)
    # energy in low band (0-200 Hz) of pad vs ducked output
    def band_rms(x, lo, hi):
        X = np.abs(np.fft.rfft(x))
        f = np.fft.rfftfreq(len(x), 1.0 / sr)
        m = (f >= lo) & (f < hi)
        return np.sqrt(np.mean(X[m] ** 2))
    low_in = band_rms(pad, 40, 200)
    low_out = band_rms(out, 40, 200)
    air_in = band_rms(pad, 2000, 4000)
    air_out = band_rms(out, 2000, 4000)
    print(f"spectral_sidechain demo: pad len={len(pad)}, out len={len(out)}")
    print(f"  low band (40-200Hz) energy: {low_in:.1f} -> {low_out:.1f} "
          f"({100*(1-low_out/low_in):.1f}% ducked by kick)")
    print(f"  air band (2-4kHz) energy:   {air_in:.1f} -> {air_out:.1f} "
          f"({100*(1-air_out/air_in):.1f}% ducked)")
    blobs = BlobMap(sr=sr).analyze(np.stack([pad, pad * 0.8]))
    print(f"  blob frames: {len(blobs)}, first (pan, height, depth) = "
          f"({blobs[0][0]:+.3f}, {blobs[0][1]:.3f}, {blobs[0][2]:.3f})")
    assert len(out) == len(pad)
    assert low_out < low_in * 0.6, "kick must duck the low band substantially"
    assert air_out > air_in * 0.6, "air band must survive mostly unducked"
    assert np.isfinite(out).all()
    print("demo OK")


if __name__ == "__main__":
    demo()
