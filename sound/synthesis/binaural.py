"""Binaural / dual-layer synthesis — UDO DMNO style.

Haas (precedence) stereo decorrelation, dual-layer synth with
cross-modulation, and play modes (layer split, stack, unison, cross,
swap, binaural).

Usage:
    haas = HaasDelay(sample_rate=44100)
    stereo = haas.process(mono)

    bs = BinauralSynth(sample_rate=44100)
    stereo = bs.render_note(440.0, 1.0, mode="binaural")
"""

import numpy as np
from typing import Optional, List

__all__ = ["HaasDelay", "BinauralSynth"]


class HaasDelay:
    """Precedence-effect stereo decorrelation (delay one channel)."""

    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate

    def process(self, audio: np.ndarray, delay_ms: float = 12.0,
                feedback: float = 0.0) -> np.ndarray:
        """Return stereo [n, 2] with the right channel delayed.

        Args:
            audio: Mono or stereo input.
            delay_ms: Inter-channel delay (Haas 5-30ms typical).
            feedback: Optional feedback on the delayed channel.
        """
        sr = self.sample_rate
        if audio.ndim > 1:
            left = audio[:, 0].astype(np.float64)
            right = audio[:, 1].astype(np.float64)
        else:
            left = audio.astype(np.float64)
            right = left.copy()

        d = int(delay_ms * 0.001 * sr)
        n = len(left)
        out_right = np.zeros(n, dtype=np.float64)
        if d > 0:
            out_right[d:] = right[:-d]
        else:
            out_right = right.copy()

        if feedback > 0:
            for i in range(d, n):
                out_right[i] += feedback * out_right[i - d]

        return np.column_stack([left, out_right]).astype(audio.dtype)


class BinauralSynth:
    """Dual-layer synth with cross-modulation and play modes."""

    PLAY_MODES = ["layer_split", "stack", "unison", "cross", "swap", "binaural"]

    def __init__(self, sample_rate: int = 44100):
        from sound.effects.filter import SubtractiveVoice
        self.sample_rate = sample_rate
        self.layer1 = SubtractiveVoice(sample_rate)
        self.layer2 = SubtractiveVoice(sample_rate)
        # Cross-modulation: layer2 pitch ratio
        self.interval_ratio = 1.5  # e.g. perfect fifth above
        self.layer1_waveform = "saw"
        self.layer2_waveform = "square"

    def render_note(self, freq: float, duration: float, mode: str = "layer_split",
                    layer1_kwargs: Optional[dict] = None,
                    layer2_kwargs: Optional[dict] = None) -> np.ndarray:
        """Render a stereo note in the given play mode.

        Returns:
            Stereo [n, 2] buffer.
        """
        if mode not in self.PLAY_MODES:
            raise ValueError(f"Unknown play mode: {mode}. Use: {self.PLAY_MODES}")

        kw1 = dict(layer1_kwargs or {})
        kw2 = dict(layer2_kwargs or {})
        kw1.setdefault("waveform", self.layer1_waveform)
        kw2.setdefault("waveform", self.layer2_waveform)

        n_samples = int(duration * self.sample_rate)
        mono1 = self.layer1.render_note(freq, duration, **kw1)
        freq2 = freq * self.interval_ratio

        if mode == "layer_split":
            # Layer 1 full-left, layer 2 full-right
            mono2 = self.layer2.render_note(freq2, duration, **kw2)
            left = mono1 + 0.3 * mono2
            right = 0.3 * mono1 + mono2
        elif mode == "stack":
            # Both layers summed, same both channels
            mono2 = self.layer2.render_note(freq2, duration, **kw2)
            both = mono1 + mono2
            left = both.copy()
            right = both.copy()
        elif mode == "unison":
            # Slight detune between channels (chorus effect)
            mono2 = self.layer2.render_note(freq * 1.004, duration, **kw2)
            left = mono1.copy()
            right = mono2.copy()
        elif mode == "cross":
            # Cross-modulation: layer2 freq follows layer1 envelope
            mono2 = self.layer2.render_note(freq * self.interval_ratio, duration, **kw2)
            left = mono1 + 0.5 * mono2
            right = mono2 + 0.5 * mono1
        elif mode == "swap":
            # Swap after half duration
            mono2 = self.layer2.render_note(freq2, duration, **kw2)
            half = n_samples // 2
            left = np.concatenate([mono1[:half], mono2[half:]])
            right = np.concatenate([mono2[:half], mono1[half:]])
        else:  # binaural
            # Haas-delayed stereo image
            mono2 = self.layer2.render_note(freq2, duration, **kw2)
            both = mono1 + mono2
            haas = HaasDelay(self.sample_rate)
            stereo = haas.process(both, delay_ms=15.0)
            return stereo

        peak = np.max(np.abs(np.concatenate([left, right])))
        if peak > 1.0:
            left = left / peak
            right = right / peak
        return np.column_stack([left, right]).astype(np.float32)
