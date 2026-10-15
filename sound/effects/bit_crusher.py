"""Bit crusher / fidelity reducer (Modbap Fidelity Theory-style).

Single macro control that simultaneously adjusts sample rate and bit depth
across a range from 48kHz/6-bit to 6kHz/16-bit.

Two converter voicings:
- Iron: presence boost at ~4kHz + gentle drive
- Worn: low-mid emphasis, softened highs, asymmetric saturation + grain

Ring mode creates inharmonic metallic texture via aliasing foldover.
"""

import numpy as np
from dataclasses import dataclass
from typing import Optional


# ---------------------------------------------------------------------------
# Bit crusher core
# ---------------------------------------------------------------------------

@dataclass
class FidelityConfig:
    """Fidelity coordinate: sample_rate_hz and bit_depth are linked."""
    sample_rate_hz: float = 44100.0   # 6000..48000
    bit_depth: int = 16               # 6..16
    mode: str = 'iron'                # 'iron' | 'worn'
    ring: float = 0.0                 # 0..1 foldover/aliasing emphasis
    mix: float = 1.0                  # dry/wet


class BitCrusher:
    """Sample-rate reducer + bit-depth reducer with character voicing.

    The sample_rate and bit_depth are intentionally linked — decreasing
    the sample rate also reduces bandwidth, while decreasing bit depth
    adds quantization noise/distortion.  The combined effect is the
    "fidelity coordinate".
    """

    def __init__(self, sample_rate: int = 44100):
        self.host_sr = sample_rate
        self.config = FidelityConfig()
        self._phase: float = 0.0
        self._held_sample: float = 0.0
        self._worn_z1: float = 0.0   # one-pole for Worn LPF
        self._worn_z2: float = 0.0

    @property
    def fidelity(self) -> float:
        """Get fidelity coordinate as 0..1 where 0=lo-fi, 1=hi-fi."""
        sr_norm = (self.config.sample_rate_hz - 6000.0) / (48000.0 - 6000.0)
        bd_norm = (self.config.bit_depth - 6) / (16 - 6)
        return 0.5 * sr_norm + 0.5 * bd_norm

    @fidelity.setter
    def fidelity(self, v: float):
        """Set both sample rate and bit depth from a single 0..1 value.

        0.0 → 6kHz/6-bit (lo-fi)
        0.5 → 27kHz/11-bit
        1.0 → 48kHz/16-bit (hi-fi)
        """
        v = np.clip(v, 0.0, 1.0)
        sr = 6000.0 + v * (48000.0 - 6000.0)
        bd = 6 + int(v * (16 - 6))
        self.config.sample_rate_hz = float(round(sr / 100.0) * 100)  # round to 100
        self.config.bit_depth = max(6, min(16, bd))

    def _quantize(self, x: float) -> float:
        """Reduce bit depth."""
        levels = 2 ** self.config.bit_depth
        return np.round(x * (levels - 1)) / (levels - 1)

    def _iron_voice(self, x: np.ndarray) -> np.ndarray:
        """Iron mode: presence boost at ~4kHz + gentle drive."""
        # Simple one-pole peaking boost around 4kHz
        # Using a crude FIR: difference of smoothed versions
        alpha = min(1.0, 4000.0 / self.config.sample_rate_hz)
        out = np.empty_like(x)
        z = 0.0
        for i in range(len(x)):
            lp = alpha * x[i] + (1.0 - alpha) * z
            z = lp
            # presence = original + (original - lowpass) * boost
            presence = x[i] + 0.5 * (x[i] - lp)
            # gentle drive (soft clip)
            drive = np.tanh(presence * 1.5) / np.tanh(1.5)
            out[i] = drive
        return out

    def _worn_voice(self, x: np.ndarray) -> np.ndarray:
        """Worn mode: low-mid emphasis + softened highs + asymmetric sat."""
        # Low-mid emphasis: 2-pole LP at ~800Hz
        # Asymmetric saturation
        out = np.empty_like(x)
        for i in range(len(x)):
            # 2-pole LP around 800Hz
            wc = 2.0 * np.pi * 800.0 / self.host_sr
            a1 = np.exp(-wc)
            b0 = 1.0 - a1
            lp1 = b0 * x[i] + a1 * self._worn_z1
            self._worn_z1 = lp1
            lp2 = b0 * lp1 + a1 * self._worn_z2
            self._worn_z2 = lp2

            # Low-mid blend: emphasize the LP region
            emphasised = x[i] + 0.4 * lp2

            # Asymmetric saturation: different softness for positive/negative
            if emphasised > 0:
                asym = np.tanh(emphasised * 1.2) / np.tanh(1.2)
            else:
                asym = np.tanh(emphasised * 0.8) / np.tanh(0.8)
            out[i] = asym
        return out

    def process(self, x: np.ndarray) -> np.ndarray:
        """Process audio through the bit crusher.

        Parameters
        ----------
        x : np.ndarray (mono or stereo as 2D)

        Returns
        -------
        np.ndarray same shape as input
        """
        is_stereo = x.ndim == 2
        if is_stereo:
            left = self._process_mono(x[:, 0])
            right = self._process_mono(x[:, 1])
            return np.column_stack([left, right])
        return self._process_mono(x)

    def _process_mono(self, x: np.ndarray) -> np.ndarray:
        """Internal mono processing."""
        # Step 1: sample rate reduction (sample-and-hold)
        sr_ratio = self.config.sample_rate_hz / self.host_sr
        phase_inc = sr_ratio
        out = np.empty_like(x)

        for i in range(len(x)):
            self._phase += phase_inc
            if self._phase >= 1.0:
                self._phase -= 1.0
                self._held_sample = x[i]

            # Sample-rate reduced signal
            reduced = self._held_sample

            # Bit depth reduction
            quantized = self._quantize(reduced)

            # Character voicing
            if self.config.mode == 'iron':
                processed = self._iron_voice(np.array([quantized]))[0]
            else:
                processed = self._worn_voice(np.array([quantized]))[0]

            # Ring (aliasing foldover emphasis)
            if self.config.ring > 0.0:
                # Emphasise aliasing by folding high frequencies
                folded = np.abs(processed) * 2.0 - 1.0
                processed = (1.0 - self.config.ring) * processed + self.config.ring * folded

            # Dry/wet mix
            out[i] = (1.0 - self.config.mix) * x[i] + self.config.mix * processed

        return out


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def demo():
    """Generate demo audio: clean tone → progressive bit-crushing sweep."""
    import soundfile as sf
    sr = 44100
    dur = 4.0
    t = np.linspace(0, dur, int(sr * dur), endpoint=False)

    # Rich input: 440 Hz + harmonics
    tone = (np.sin(2 * np.pi * 440 * t) +
            0.5 * np.sin(2 * np.pi * 880 * t) +
            0.25 * np.sin(2 * np.pi * 1320 * t)) * 0.3

    crusher = BitCrusher(sample_rate=sr)

    # Sweep fidelity from clean to crushed over 4 seconds
    output = np.empty_like(tone)
    for i, fi in enumerate(np.linspace(1.0, 0.0, len(tone))):
        crusher.fidelity = fi
        crusher.config.mode = 'worn' if i < len(tone) // 2 else 'iron'
        crusher.config.ring = 0.0 if i < len(tone) // 4 else 0.3
        output[i] = crusher._process_mono(np.array([tone[i]]))[0]

    sf.write('/tmp/bitcrush_demo.wav', output, sr)
    print(f"Wrote /tmp/bitcrush_demo.wav  ({len(output)} samples, {sr} Hz)")
    print("  Sweep: 48kHz/16bit clean → 6kHz/6bit crushed, Worn→Iron mid-way")


if __name__ == '__main__':
    demo()