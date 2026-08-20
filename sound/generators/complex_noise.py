"""Complex noise generator — Synthesizers.com Q210-style.

Multiple noise types (white, pink, metallic/chaos), grainy processing,
and random gate generation. Inspired by the Q210 Complex Noise module.

Replicated from: Synthesizers.com Q210 (synthtopia 2026-08-18).

Usage:
    from sound.generators.complex_noise import ComplexNoise

    gen = ComplexNoise(sample_rate=44100)
    white = gen.white(duration=1.0)
    pink = gen.pink(duration=1.0)
    metallic = gen.metallic(duration=1.0, chaos=0.7)
    grainy = gen.grainy(source=white, grain_size=0.01, density=0.5)
    gates = gen.random_gate(duration=2.0, density=0.3, bpm=120)
"""

import numpy as np
from typing import Optional

__all__ = ["ComplexNoise"]


class ComplexNoise:
    """Multi-type noise generator with grainy processing and random gates."""

    def __init__(self, sample_rate: int = 44100, seed: Optional[int] = None):
        self.sample_rate = sample_rate
        self.rng = np.random.RandomState(seed)

    def white(self, duration: float, amplitude: float = 0.8) -> np.ndarray:
        """Generate white noise."""
        n = int(duration * self.sample_rate)
        return self.rng.uniform(-amplitude, amplitude, n)

    def pink(self, duration: float, amplitude: float = 0.8) -> np.ndarray:
        """Generate pink noise using Voss-McCartney algorithm."""
        n = int(duration * self.sample_rate)
        # Generate via spectral shaping: 1/f filter
        white = self.rng.randn(n)
        # Apply 1/f shaping in frequency domain
        X = np.fft.rfft(white)
        freqs = np.fft.rfftfreq(n, 1.0 / self.sample_rate)
        freqs[0] = 1.0  # avoid div by zero
        # 1/f magnitude response
        shaping = 1.0 / np.sqrt(freqs)
        shaping[0] = 0.0  # remove DC
        X *= shaping
        pink = np.fft.irfft(X, n)
        # Normalize
        peak = np.max(np.abs(pink))
        if peak > 0:
            pink = pink / peak * amplitude
        return pink

    def metallic(self, duration: float, chaos: float = 0.5,
                 amplitude: float = 0.8) -> np.ndarray:
        """Generate metallic/chaos noise.

        Uses iterated nonlinear maps to create metallic, bell-like noise.
        chaos parameter controls the nonlinearity (0=smooth, 1=fully chaotic).
        """
        n = int(duration * self.sample_rate)
        # Source: white noise
        source = self.rng.randn(n)
        # Resonant bandpass bank at metallic partial frequencies
        output = np.zeros(n, dtype=np.float64)
        resonances = [
            (800, 20), (1200, 15), (2400, 30),
            (3600, 25), (5100, 40), (7200, 35),
        ]
        try:
            from scipy.signal import iirpeak, lfilter
            for freq, bw in resonances:
                w0 = freq / (0.5 * self.sample_rate)
                # Clamp Q to <= 12 for numeric stability (narrower = NaN risk)
                q = min(freq / bw, 12.0)
                b, a = iirpeak(w0, q)
                y = lfilter(b, a, source)
                output += y
        except ImportError:
            # Fallback: simple two-pole resonator (direct form II)
            for freq, bw in resonances:
                q = min(freq / bw, 12.0)
                w0 = 2 * np.pi * freq / self.sample_rate
                alpha = np.sin(w0) / (2 * q)
                a0 = 1 + alpha
                a1 = -2 * np.cos(w0)
                a2 = 1 - alpha
                b0 = alpha
                b2 = -alpha
                y = np.zeros(n, dtype=np.float64)
                x1 = x2 = y1 = y2 = 0.0
                for i in range(n):
                    x = source[i]
                    y[i] = (b0 * x - b2 * x2 - a1 * y1 - a2 * y2) / a0
                    x2, x1 = x1, x
                    y2, y1 = y1, y[i]
                output += y

        # Chaos: modulate with iterated logistic map
        if chaos > 0:
            x = 0.5
            r = 3.5 + 0.5 * chaos  # 3.5..4.0
            mod = np.empty(n)
            for i in range(n):
                x = r * x * (1 - x)
                mod[i] = x
            # Modulate amplitude and slight pitch shimmer
            output *= (0.4 + 0.6 * mod)

        peak = np.max(np.abs(output))
        if peak > 0:
            output = output / peak * amplitude
        return output

    def grainy(self, source: np.ndarray, grain_size: float = 0.01,
               density: float = 0.5, pitch_shift: float = 0.0) -> np.ndarray:
        """Apply grainy processing to a source signal.

        Args:
            source: Input audio.
            grain_size: Grain size in seconds.
            density: Grain density (0..1, higher = more overlap).
            pitch_shift: Pitch shift in semitones (0 = no shift).

        Returns:
            Grainy processed audio, same length as source.
        """
        n = len(source)
        grain_samples = int(grain_size * self.sample_rate)
        if grain_samples < 2:
            grain_samples = 2
        output = np.zeros(n, dtype=np.float64)
        # Number of grains
        hop = max(1, int(grain_samples * (1 - density)))
        pos = 0
        while pos < n:
            end = min(pos + grain_samples, n)
            grain = source[pos:end].copy()
            # Apply pitch shift via resampling
            if abs(pitch_shift) > 0.01:
                ratio = 2.0 ** (pitch_shift / 12.0)
                new_len = max(1, int(len(grain) / ratio))
                indices = np.linspace(0, len(grain) - 1, new_len)
                grain = np.interp(indices, np.arange(len(grain)), grain)
            # Hann window
            win = np.hanning(len(grain))
            grain *= win
            # Place in output
            out_end = min(pos + len(grain), n)
            output[pos:out_end] += grain[:out_end - pos]
            pos += hop
        # Normalize
        peak = np.max(np.abs(output))
        if peak > 0:
            output = output / peak
        return output

    def random_gate(self, duration: float, density: float = 0.3,
                    bpm: float = 120.0, min_length: int = 1,
                    max_length: int = 4) -> np.ndarray:
        """Generate a random gate signal.

        Args:
            duration: Duration in seconds.
            density: Probability of gate being open per step (0..1).
            bpm: Tempo in BPM.
            min_length: Minimum gate-on length in steps.
            max_length: Maximum gate-on length in steps.

        Returns:
            Binary gate signal (0.0 or 1.0).
        """
        n = int(duration * self.sample_rate)
        step_samples = int(60.0 / bpm / 4 * self.sample_rate)  # 16th notes
        n_steps = (n + step_samples - 1) // step_samples
        gate_steps = np.zeros(n_steps)
        i = 0
        while i < n_steps:
            if self.rng.random() < density:
                length = self.rng.randint(min_length, max_length + 1)
                for j in range(length):
                    if i + j < n_steps:
                        gate_steps[i + j] = 1.0
                i += length
            else:
                i += 1
        # Convert to sample-level
        gate = np.zeros(n)
        for i in range(n_steps):
            start = i * step_samples
            end = min(start + step_samples, n)
            gate[start:end] = gate_steps[i]
        return gate


def demo() -> str:
    """Generate demo noise types and return summary."""
    gen = ComplexNoise(sample_rate=44100, seed=42)
    dur = 1.0

    w = gen.white(dur)
    p = gen.pink(dur)
    m = gen.metallic(dur, chaos=0.6)
    g = gen.grainy(w, grain_size=0.02, density=0.7, pitch_shift=3.0)
    gate = gen.random_gate(2.0, density=0.4, bpm=120)

    lines = [
        f"white: {len(w)} samples, peak={np.max(np.abs(w)):.3f}",
        f"pink: {len(p)} samples, peak={np.max(np.abs(p)):.3f}",
        f"metallic (chaos=0.6): {len(m)} samples, peak={np.max(np.abs(m)):.3f}",
        f"grainy (size=20ms, density=0.7): {len(g)} samples, peak={np.max(np.abs(g)):.3f}",
        f"random_gate (density=0.4): {len(gate)} samples, {int(np.sum(gate > 0))} on-samples",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    print(demo())
