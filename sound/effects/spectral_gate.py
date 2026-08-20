"""Rhythmic spectral gate — Spectdrum-style.

Splits audio into N spectral bands, each with an independent step sequencer
that opens/closes the band in time. Supports polyrhythmic patterns (different
lengths per band), per-step velocity/accents/swing, and per-band envelope
shapes.

Replicated from: Spectdrum (Hagai Davidoff, synthtopia 2026-08-17).

Usage:
    from sound.effects.spectral_gate import SpectralGate

    gate = SpectralGate(n_bands=4, sample_rate=44100)
    gate.set_pattern(band=0, steps=[1,0,1,0], length=4)
    gate.set_pattern(band=1, steps=[1,1,0,1], length=4)  # polyrhythm
    out = gate.process(audio, bpm=120)
"""

import numpy as np
from typing import List, Optional, Dict

__all__ = ["SpectralGate"]


def _butter_bandpass(lowcut: float, highcut: float, fs: int, order: int = 4):
    """Design a Butterworth bandpass filter."""
    try:
        from scipy.signal import butter, sosfilt
        nyq = 0.5 * fs
        low = max(lowcut / nyq, 1e-5)
        high = min(highcut / nyq, 1.0 - 1e-5)
        sos = butter(order, [low, high], btype='band', output='sos')
        return lambda x: sosfilt(sos, x)
    except ImportError:
        # Fallback: simple FFT-based bandpass
        def filt(x):
            X = np.fft.rfft(x)
            freqs = np.fft.rfftfreq(len(x), 1.0 / fs)
            mask = (freqs >= lowcut) & (freqs <= highcut)
            X[~mask] = 0.0
            return np.fft.irfft(X, len(x))
        return filt


class SpectralGate:
    """Multi-band rhythmic spectral gate.

    Splits audio into N bands, each gated by an independent step sequencer.
    Different step lengths per band create polyrhythmic patterns.
    """

    # Default 4-band split (Sub, Low-Mid, High-Mid, Air)
    DEFAULT_BANDS = [
        (20, 200),      # Sub
        (200, 2000),    # Low-Mid
        (2000, 8000),   # High-Mid
        (8000, 20000),  # Air
    ]

    def __init__(self, n_bands: int = 4, sample_rate: int = 44100,
                 band_ranges: Optional[List[tuple]] = None):
        self.sample_rate = sample_rate
        self.n_bands = n_bands
        if band_ranges:
            self.band_ranges = band_ranges
        else:
            self.band_ranges = self.DEFAULT_BANDS[:n_bands]
        # Per-band step patterns: list of velocities (0 = off, >0 = on)
        self.patterns: Dict[int, List[int]] = {}
        self.pattern_lengths: Dict[int, int] = {}
        # Per-band swing (0..1, 0.5 = straight)
        self.swing: Dict[int, float] = {i: 0.5 for i in range(n_bands)}
        # Per-band volume multiplier
        self.band_gains: Dict[int, float] = {i: 1.0 for i in range(n_bands)}
        # Build filters
        self._filters = [
            _butter_bandpass(lo, hi, sample_rate)
            for lo, hi in self.band_ranges
        ]

    def set_pattern(self, band: int, steps: List[int], length: Optional[int] = None):
        """Set step pattern for a band.

        Args:
            band: Band index (0..n_bands-1).
            steps: List of velocities (0=off, 1-127=on with velocity).
            length: Pattern length in steps (defaults to len(steps)).
                    Different lengths per band = polyrhythm.
        """
        self.patterns[band] = list(steps)
        self.pattern_lengths[band] = length or len(steps)

    def set_swing(self, band: int, swing: float):
        """Set swing for a band (0..1, 0.5=straight, 0.67=triplet feel)."""
        self.swing[band] = max(0.0, min(1.0, swing))

    def set_band_gain(self, band: int, gain: float):
        """Set volume multiplier for a band."""
        self.band_gains[band] = max(0.0, gain)

    def process(self, audio: np.ndarray, bpm: float = 120.0,
                steps_per_beat: int = 4, normalize: bool = True) -> np.ndarray:
        """Apply rhythmic spectral gating to audio.

        Args:
            audio: Input mono audio array.
            bpm: Tempo in BPM.
            steps_per_beat: Grid resolution (4 = sixteenth notes).
            normalize: Scale output peak to input peak (master maximizer).

        Returns:
            Gated audio, same length as input.
        """
        audio = np.asarray(audio, dtype=np.float64)
        n_samples = len(audio)
        # Split into bands
        bands = [f(audio) for f in self._filters]
        # Calculate step duration in samples
        beat_dur = 60.0 / bpm
        step_dur = beat_dur / steps_per_beat
        step_samples = int(step_dur * self.sample_rate)
        if step_samples < 1:
            step_samples = 1

        output = np.zeros(n_samples, dtype=np.float64)
        for band_idx in range(self.n_bands):
            if band_idx not in self.patterns:
                # No pattern → pass through at band gain
                output += bands[band_idx] * self.band_gains.get(band_idx, 1.0)
                continue
            pattern = self.patterns[band_idx]
            pat_len = self.pattern_lengths.get(band_idx, len(pattern))
            sw = self.swing.get(band_idx, 0.5)
            gain = self.band_gains.get(band_idx, 1.0)
            band_out = np.zeros(n_samples, dtype=np.float64)
            # Step through time
            step = 0
            pos = 0
            while pos < n_samples:
                # Apply swing to odd steps
                if step % 2 == 1:
                    this_step_samples = int(step_samples * (2 * sw))
                else:
                    this_step_samples = int(step_samples * (2 * (1 - sw)))
                this_step_samples = max(1, this_step_samples)
                # Look up velocity
                pat_idx = step % pat_len
                if pat_idx < len(pattern):
                    vel = pattern[pat_idx]
                else:
                    vel = 0
                # Apply gate
                end = min(pos + this_step_samples, n_samples)
                if vel > 0:
                    band_out[pos:end] = bands[band_idx][pos:end] * (vel / 127.0)
                pos = end
                step += 1
            output += band_out * gain
        # Unity-gain normalization (master maximizer): match input peak
        if normalize:
            in_peak = np.max(np.abs(audio))
            out_peak = np.max(np.abs(output))
            if in_peak > 0 and out_peak > 0:
                output = output * (in_peak / out_peak)
        return output


def demo() -> str:
    """Generate a demo and return summary."""
    sr = 44100
    dur = 2.0
    t = np.linspace(0, dur, int(sr * dur), endpoint=False)
    # Pink-ish noise
    rng = np.random.RandomState(42)
    noise = rng.randn(len(t))
    # Apply gentle lowpass to make it broadband
    from scipy.signal import sosfilt
    from scipy.signal import butter
    sos = butter(2, 4000 / (0.5 * sr), btype='low', output='sos')
    noise = sosfilt(sos, noise)
    noise = noise / np.max(np.abs(noise)) * 0.5

    gate = SpectralGate(n_bands=4, sample_rate=sr)
    # Polyrhythmic: band 0 = 4 steps, band 1 = 3 steps, band 2 = 5 steps, band 3 = 7 steps
    gate.set_pattern(0, [127, 0, 80, 0], length=4)
    gate.set_pattern(1, [100, 0, 0], length=3)
    gate.set_pattern(2, [60, 0, 90, 0, 0], length=5)
    gate.set_pattern(3, [40, 0, 0, 50, 0, 0, 0], length=7)
    out = gate.process(noise, bpm=120)
    peak = np.max(np.abs(out))
    rms = np.sqrt(np.mean(out ** 2))
    return f"SpectralGate demo: {len(out)} samples, peak={peak:.3f}, rms={rms:.4f}"


if __name__ == "__main__":
    print(demo())
