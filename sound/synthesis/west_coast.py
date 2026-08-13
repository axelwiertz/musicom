"""West Coast synthesis — Vannes Obsidian style.

Complex oscillator (sine + wavefolder + waveshaper) -> lowpass gate
(vactrol-style) -> dynamics.

Usage:
    wf = Wavefolder(amount=1.5)
    folded = wf.process(signal)

    lpg = LowpassGate(sample_rate=44100)
    gated = lpg.process(signal, cutoff=2000.0, decay=0.5)

    vc = WestCoastVoice(sample_rate=44100)
    audio = vc.render_note(440.0, 1.0)
"""

import numpy as np
from typing import Optional

__all__ = ["Wavefolder", "LowpassGate", "WestCoastVoice"]


class Wavefolder:
    """Piecewise wave folding (Serge-style).

    fold(x) = 1 - 2*|1 - 2*|x/2 - round(x/2)||  folded at integer boundaries.
    """

    def __init__(self, amount: float = 1.0):
        self.amount = amount

    def process(self, audio: np.ndarray, amount: Optional[float] = None) -> np.ndarray:
        """Fold the signal; higher amount = deeper fold.

        Classic Serge-style fold: y = 4*|x/2 - round(x/2)| - 1, which maps
        any input to [-1, 1] (folding at odd multiples of the unit).
        """
        amt = self.amount if amount is None else amount
        x = np.asarray(audio, dtype=np.float64) * (1.0 + amt)
        folded = 4.0 * np.abs(x / 2.0 - np.round(x / 2.0)) - 1.0
        return folded.astype(audio.dtype)


class LowpassGate:
    """Vactrol-style lowpass gate: cutoff decays exponentially (pluck-like)."""

    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate

    def process(self, audio: np.ndarray, cutoff: float = 2000.0,
                decay: float = 0.5) -> np.ndarray:
        """Filter with an exponentially decaying cutoff.

        Args:
            audio: Input signal.
            cutoff: Initial cutoff (Hz).
            decay: Decay rate (0-1); higher = faster decay to low cutoff.
        """
        sr = self.sample_rate
        n = len(audio)
        # Exponential cutoff sweep: start at cutoff, decay toward ~200 Hz
        end_cutoff = max(50.0, cutoff * (1.0 - decay))
        t = np.arange(n) / sr
        cutoff_curve = end_cutoff + (cutoff - end_cutoff) * np.exp(-decay * 8.0 * t)

        # One-pole lowpass with per-sample coefficient
        alpha = 1.0 - np.exp(-2.0 * np.pi * cutoff_curve / sr)
        out = np.zeros(n, dtype=np.float64)
        state = 0.0
        for i in range(n):
            state = state + alpha[i] * (audio[i] - state)
            out[i] = state
        return out.astype(audio.dtype)


class WestCoastVoice:
    """Complex osc -> wavefolder -> lowpass gate."""

    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        self.wavefolder = Wavefolder(amount=1.0)
        self.lpg = LowpassGate(sample_rate)

    def render_note(self, freq: float, duration: float,
                    wavefolder_amount: float = 1.0,
                    cutoff: float = 2000.0, decay: float = 0.5,
                    waveform: str = "sine", volume: float = 0.8) -> np.ndarray:
        """Render a West Coast style note.

        Returns:
            Mono float32 buffer.
        """
        n_samples = int(duration * self.sample_rate)
        t = np.arange(n_samples) / self.sample_rate
        phase = 2.0 * np.pi * freq * t

        if waveform == "sine":
            osc = np.sin(phase)
        elif waveform == "saw":
            osc = 2.0 * (freq * t % 1.0) - 1.0
        elif waveform == "square":
            osc = np.sign(np.sin(phase))
        else:
            osc = np.sin(phase)

        folded = self.wavefolder.process(osc, amount=wavefolder_amount)
        gated = self.lpg.process(folded, cutoff=cutoff, decay=decay)
        out = gated * volume

        peak = np.max(np.abs(out))
        if peak > 1.0:
            out = out / peak
        return out.astype(np.float32)
