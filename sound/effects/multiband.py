"""Multiband synth chain — UVI Rumble style.

Linkwitz-Riley crossovers split a signal into bands; a multiband
compressor dynamics-processes each band independently; a multiband
synth mixes per-band oscillators.

Usage:
    low, high = LinkwitzRiley.crossover(signal, sr, cutoff=100)
    mbc = MultibandCompressor(sr)
    out = mbc.process(signal)
"""

import numpy as np
from typing import List, Tuple, Optional
from dataclasses import dataclass

__all__ = ["LinkwitzRiley", "MultibandCompressor", "MultibandSynth"]


class LinkwitzRiley:
    """4th-order Linkwitz-Riley crossover (two cascaded 2nd-order Butterworth)."""

    @staticmethod
    def _butter_lowpass(signal: np.ndarray, sr: int, cutoff: float,
                        order: int = 2) -> np.ndarray:
        from scipy.signal import butter, lfilter
        nyq = sr / 2.0
        fc = min(max(cutoff, 10.0), nyq * 0.99)
        b, a = butter(order, fc / nyq, btype="low")
        out = lfilter(b, a, signal)
        return np.asarray(out, dtype=np.float64)

    @staticmethod
    def _butter_highpass(signal: np.ndarray, sr: int, cutoff: float,
                         order: int = 2) -> np.ndarray:
        from scipy.signal import butter, lfilter
        nyq = sr / 2.0
        fc = min(max(cutoff, 10.0), nyq * 0.99)
        b, a = butter(order, fc / nyq, btype="high")
        out = lfilter(b, a, signal)
        return np.asarray(out, dtype=np.float64)

    @classmethod
    def crossover(cls, signal: np.ndarray, sample_rate: int, cutoff: float,
                  order: int = 2) -> Tuple[np.ndarray, np.ndarray]:
        """Split signal into (low, high) at cutoff."""
        # Cascade two 2nd-order Butterworth = 4th-order LR
        low = cls._butter_lowpass(signal, sample_rate, cutoff, order)
        low = cls._butter_lowpass(low, sample_rate, cutoff, order)
        high = cls._butter_highpass(signal, sample_rate, cutoff, order)
        high = cls._butter_highpass(high, sample_rate, cutoff, order)
        return low, high


@dataclass
class _Band:
    """Compressor band config."""
    lo: float
    hi: float
    threshold_db: float = -12.0
    ratio: float = 2.0
    attack_ms: float = 10.0
    release_ms: float = 100.0


class MultibandCompressor:
    """Per-band dynamics processing (UVI Rumble multiband compression)."""

    def __init__(self, sample_rate: int = 44100,
                 bands: Optional[List[Tuple[float, float]]] = None):
        self.sample_rate = sample_rate
        if bands is None:
            bands = [(0, 100), (100, 400), (400, 4000), (4000, sample_rate / 2)]
        self.bands: List[_Band] = [_Band(lo, hi) for lo, hi in bands]

    def add_band(self, index: int, threshold_db: float = -12.0,
                 ratio: float = 2.0, attack_ms: float = 10.0,
                 release_ms: float = 100.0):
        """Configure an existing band."""
        band = self.bands[index]
        band.threshold_db = threshold_db
        band.ratio = ratio
        band.attack_ms = attack_ms
        band.release_ms = release_ms

    def _compress(self, signal: np.ndarray, band: _Band) -> np.ndarray:
        env = np.abs(signal)
        atk = int(band.attack_ms * 0.001 * self.sample_rate)
        rel = int(band.release_ms * 0.001 * self.sample_rate)
        atk = max(1, atk)
        rel = max(1, rel)
        a_coeff = np.exp(-1.0 / atk)
        r_coeff = np.exp(-1.0 / rel)
        n = len(env)
        smooth = np.zeros(n)
        prev = env[0]
        for i in range(n):
            coeff = a_coeff if env[i] > prev else r_coeff
            prev = prev * coeff + env[i] * (1 - coeff)
            smooth[i] = prev

        threshold = 10 ** (band.threshold_db / 20.0)
        gain = np.ones(n)
        mask = smooth > threshold
        over_db = 20 * np.log10(np.maximum(smooth[mask], 1e-12) / threshold)
        reduced_db = over_db / band.ratio
        gain[mask] = (10 ** (reduced_db / 20.0)) * threshold / np.maximum(smooth[mask], 1e-12)
        return signal * gain

    def process(self, audio: np.ndarray) -> np.ndarray:
        """Split, compress each band, sum back."""
        is_stereo = audio.ndim > 1 and audio.shape[1] >= 2
        if is_stereo:
            left = self.process(audio[:, 0])
            right = self.process(audio[:, 1])
            return np.column_stack([left, right])

        out = np.zeros(len(audio), dtype=np.float64)
        for band in self.bands:
            if band.lo <= 0 and band.hi >= self.sample_rate / 2:
                seg = audio.astype(np.float64)
            else:
                low, high = LinkwitzRiley.crossover(audio, self.sample_rate,
                                                    band.hi)
                if band.lo <= 0:
                    seg = low
                else:
                    low2, high2 = LinkwitzRiley.crossover(high, self.sample_rate,
                                                          band.lo)
                    seg = np.asarray(high2, dtype=np.float64)
            out += self._compress(seg, band)
        return out.astype(audio.dtype)


class MultibandSynth:
    """Synth with per-band oscillators (Rumble Body/Mid/Air concept)."""

    def __init__(self, sample_rate: int = 44100):
        from sound.synthesis.polysynth import Oscillator
        self.sample_rate = sample_rate
        self._Oscillator = Oscillator
        self.oscillators: List[dict] = []  # {band, waveform, freq, detune, level}

    def add_oscillator(self, band_index: int, waveform: str = "saw",
                       freq: float = 440.0, detune_cents: float = 0.0,
                       level: float = 1.0):
        """Register an oscillator in a band."""
        self.oscillators.append({
            "band": band_index,
            "waveform": waveform,
            "freq": freq,
            "detune_cents": detune_cents,
            "level": level,
        })

    def render(self, duration: float,
               compressor: Optional[MultibandCompressor] = None) -> np.ndarray:
        """Render mixed oscillators (optionally multiband-compressed)."""
        n_samples = int(duration * self.sample_rate)
        mix = np.zeros(n_samples, dtype=np.float64)
        for spec in self.oscillators:
            osc = self._Oscillator(self.sample_rate)
            osc.waveform = spec["waveform"]
            osc.detune_cents = spec["detune_cents"]
            osc.level = spec["level"]
            signal = osc.generate(spec["freq"], n_samples)
            mix += signal
        peak = np.max(np.abs(mix)) if n_samples else 1.0
        if peak > 1e-12:
            mix = mix / peak * 0.9

        if compressor is not None:
            mix = compressor.process(mix)
        return mix.astype(np.float32)
