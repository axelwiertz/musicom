"""Tilt EQ — Triton Audio Tilt EQ-style.

A tilt EQ rotates the tonal balance around a pivot frequency: turning the
tilt control up boosts highs and cuts lows (bright), turning it down boosts
lows and cuts highs (dark). The pivot frequency is the crossover point
where no change occurs.

Replicated from: Triton Audio Tilt EQ (SoundOnSound 2026-08).

Usage:
    from sound.effects.tilt_eq import TiltEQ

    eq = TiltEQ(sample_rate=44100, pivot_freq=1000.0)
    bright = eq.process(audio, tilt=0.5)   # boost highs, cut lows
    dark = eq.process(audio, tilt=-0.5)    # boost lows, cut highs
    flat = eq.process(audio, tilt=0.0)     # no change
"""

import numpy as np
from typing import Optional

__all__ = ["TiltEQ"]


class TiltEQ:
    """Tilt equalizer: rotate tonal balance around a pivot frequency.

    The tilt parameter controls the slope: positive = brighter (boost highs,
    cut lows), negative = darker (boost lows, cut highs). The pivot frequency
    is the crossover point where gain = 0dB.
    """

    def __init__(self, sample_rate: int = 44100, pivot_freq: float = 1000.0,
                 max_tilt_db: float = 12.0):
        """Initialize.

        Args:
            sample_rate: Sample rate in Hz.
            pivot_freq: Pivot/crossover frequency in Hz.
            max_tilt_db: Maximum tilt amount in dB (at tilt=±1).
        """
        self.sample_rate = sample_rate
        self.pivot_freq = pivot_freq
        self.max_tilt_db = max_tilt_db

    def process(self, audio: np.ndarray, tilt: float = 0.0) -> np.ndarray:
        """Apply tilt EQ to audio.

        Args:
            audio: Input audio array.
            tilt: Tilt amount in [-1, 1]. 0 = flat, +1 = max bright, -1 = max dark.

        Returns:
            Tilted audio, same length as input.
        """
        audio = np.asarray(audio, dtype=np.float64)
        tilt = max(-1.0, min(1.0, tilt))
        if abs(tilt) < 1e-6:
            return audio.copy()

        n = len(audio)
        # FFT-based tilt
        X = np.fft.rfft(audio)
        freqs = np.fft.rfftfreq(n, 1.0 / self.sample_rate)
        freqs[0] = 1.0  # avoid log(0)

        # Calculate gain curve: linear slope in log-frequency domain
        # centered on pivot_freq
        log_freqs = np.log10(freqs)
        log_pivot = np.log10(self.pivot_freq)
        # Normalized distance from pivot in log domain
        slope = tilt * self.max_tilt_db  # dB per octave
        # Gain in dB: slope * (log_freq - log_pivot) / log10(2)
        # This gives ±max_tilt_db at one octave above/below pivot
        gain_db = slope * (log_freqs - log_pivot) / np.log10(2)
        # Convert to linear gain
        gain_linear = 10.0 ** (gain_db / 20.0)

        # Apply
        X *= gain_linear
        output = np.fft.irfft(X, n)
        return output

    def process_stereo(self, left: np.ndarray, right: np.ndarray,
                       tilt: float = 0.0) -> tuple:
        """Apply tilt EQ to stereo audio."""
        return self.process(left, tilt), self.process(right, tilt)


def demo() -> str:
    """Generate demo and return summary."""
    sr = 44100
    dur = 1.0
    t = np.linspace(0, dur, int(sr * dur), endpoint=False)
    # Test signal: mix of low and high frequencies
    signal = 0.5 * np.sin(2 * np.pi * 100 * t) + 0.5 * np.sin(2 * np.pi * 5000 * t)

    eq = TiltEQ(sample_rate=sr, pivot_freq=1000.0)
    bright = eq.process(signal, tilt=0.5)
    dark = eq.process(signal, tilt=-0.5)
    flat = eq.process(signal, tilt=0.0)

    # Measure energy in low vs high bands
    def band_energy(audio, low, high):
        X = np.fft.rfft(audio)
        freqs = np.fft.rfftfreq(len(audio), 1.0 / sr)
        mask = (freqs >= low) & (freqs <= high)
        return np.sum(np.abs(X[mask]) ** 2)

    low_flat = band_energy(flat, 20, 500)
    high_flat = band_energy(flat, 5000, 10000)
    low_bright = band_energy(bright, 20, 500)
    high_bright = band_energy(bright, 5000, 10000)
    low_dark = band_energy(dark, 20, 500)
    high_dark = band_energy(dark, 5000, 10000)

    lines = [
        f"TiltEQ demo (pivot=1kHz, max_tilt=12dB):",
        f"  flat:   low_energy={low_flat:.1f}, high_energy={high_flat:.1f}",
        f"  bright: low_energy={low_bright:.1f}, high_energy={high_bright:.1f}",
        f"  dark:   low_energy={low_dark:.1f}, high_energy={high_dark:.1f}",
        f"  bright/high ratio: {high_bright/max(low_bright,1):.2f}",
        f"  dark/low ratio: {low_dark/max(high_dark,1):.2f}",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    print(demo())
