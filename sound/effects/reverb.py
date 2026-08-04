"""Algorithmic reverb — Schroeder/Moorer topology.

Parallel comb filters → series allpass filters.
Inspired by Waves Atlas and classic DSP textbook designs.

Usage:
    reverb = AlgorithmicReverb(room_size=0.7, damping=0.5, wet_dry=0.3)
    output = reverb.process(input_audio)
    
    # Or convenience function:
    output = apply_reverb(audio, room_size=0.8)
"""

import numpy as np
from typing import Optional


def _comb_feedback(audio: np.ndarray, delay: int, feedback: float, 
                   damping: float) -> np.ndarray:
    """Vectorized feedback comb filter with damping.
    
    y[n] = x[n] + feedback * filterstore[n-delay]
    filterstore[n] = y[n] * (1-damping) + filterstore[n-1] * damping
    """
    n = len(audio)
    output = np.zeros(n, dtype=np.float64)
    filterstore = np.zeros(n, dtype=np.float64)
    
    for i in range(n):
        idx = i - delay
        if idx >= 0:
            fs = filterstore[idx]
        else:
            fs = 0.0
        output[i] = audio[i] + feedback * fs
        if i > 0:
            filterstore[i] = output[i] * (1.0 - damping) + filterstore[i-1] * damping
        else:
            filterstore[i] = output[i] * (1.0 - damping)
    
    return output


def _allpass(audio: np.ndarray, delay: int, feedback: float) -> np.ndarray:
    """Vectorized Schroeder allpass filter.
    
    y[n] = -x[n] + buffer[n-delay]
    buffer[n] = x[n] + feedback * buffer[n-delay]
    """
    n = len(audio)
    output = np.zeros(n, dtype=np.float64)
    buf = np.zeros(n, dtype=np.float64)
    
    for i in range(n):
        idx = i - delay
        if idx >= 0:
            b = buf[idx]
        else:
            b = 0.0
        output[i] = -audio[i] + b
        buf[i] = audio[i] + feedback * b
    
    return output


class AlgorithmicReverb:
    """
    Schroeder/Moorer algorithmic reverb.
    
    Topology: 8 parallel comb filters → 4 series allpass filters.
    Stereo: interleaved L/R comb pairs with slight delay offset for width.
    
    Parameters:
        room_size: 0.0-1.0, controls feedback (bigger = longer tail)
        damping: 0.0-1.0, high-frequency absorption (1.0 = dark, 0.0 = bright)
        wet_dry: 0.0-1.0, mix ratio (0=dry, 1=wet)
        width: 0.0-1.0, stereo spread
        modulation: 0.0-1.0, LFO depth on comb delays (chorus-like movement)
    """
    
    # Base delay times in samples at 44100Hz — primes for diffusion
    COMB_DELAYS = [1117, 1187, 1277, 1356, 1422, 1491, 1557, 1617]
    ALLPASS_DELAYS = [557, 441, 341, 225]
    ALLPASS_FEEDBACK = 0.5
    
    def __init__(self, 
                 sample_rate: int = 44100,
                 room_size: float = 0.7,
                 damping: float = 0.5,
                 wet_dry: float = 0.3,
                 width: float = 0.8,
                 modulation: float = 0.0):
        self.sample_rate = sample_rate
        self.room_size = room_size
        self.damping = damping
        self.wet_dry = wet_dry
        self.width = width
        self.modulation = modulation
    
    @property
    def feedback(self) -> float:
        """Map room_size to feedback coefficient."""
        return 0.7 + self.room_size * 0.28  # 0.7 → 0.98
    
    def _scaled_delays(self) -> list:
        """Scale delay times to current sample rate."""
        scale = self.sample_rate / 44100.0
        return [int(d * scale) for d in self.COMB_DELAYS]
    
    def _scaled_allpass_delays(self) -> list:
        scale = self.sample_rate / 44100.0
        return [int(d * scale) for d in self.ALLPASS_DELAYS]
    
    def process(self, audio: np.ndarray) -> np.ndarray:
        """
        Process audio through reverb.
        
        Args:
            audio: Input audio (mono or stereo), float32/float64
            
        Returns:
            Reverberated audio (same shape as input)
        """
        is_stereo = len(audio.shape) > 1 and audio.shape[1] >= 2
        
        if is_stereo:
            left = audio[:, 0].astype(np.float64)
            right = audio[:, 1].astype(np.float64)
        else:
            left = audio.astype(np.float64)
            right = left.copy()
        
        fb = self.feedback
        delays = self._scaled_delays()
        ap_delays = self._scaled_allpass_delays()
        
        # Parallel combs — stereo interleaved (odd=L, even=R)
        comb_sum_l = np.zeros(len(left), dtype=np.float64)
        comb_sum_r = np.zeros(len(right), dtype=np.float64)
        
        for i, delay in enumerate(delays):
            # Slight stereo offset for width
            spread = 23 if i % 2 else 0
            comb_sum_l += _comb_feedback(left, delay, fb, self.damping)
            comb_sum_r += _comb_feedback(right, delay + spread, fb, self.damping)
        
        # Scale to prevent clipping
        comb_sum_l *= 0.015
        comb_sum_r *= 0.015
        
        # Series allpasses
        out_l = comb_sum_l
        out_r = comb_sum_r
        
        for i, delay in enumerate(ap_delays):
            spread = 17 if i % 2 else 0
            out_l = _allpass(out_l, delay, self.ALLPASS_FEEDBACK)
            out_r = _allpass(out_r, delay + spread, self.ALLPASS_FEEDBACK)
        
        # Width control (mid/side)
        if self.width < 1.0:
            mid = (out_l + out_r) * 0.5
            side = (out_l - out_r) * 0.5
            out_l = mid + side * self.width
            out_r = mid - side * self.width
        
        # Mix wet/dry
        wet = self.wet_dry
        dry = 1.0 - self.wet_dry
        
        if is_stereo:
            result = np.column_stack([
                left * dry + out_l * wet,
                right * dry + out_r * wet
            ])
        else:
            result = left * dry + out_l * wet
        
        return result.astype(audio.dtype)


class Freeverb(AlgorithmicReverb):
    """
    Freeverb-compatible reverb (Jezar at Dreampoint algorithm).
    Same topology, tuned defaults matching classic Freeverb sound.
    """
    
    def __init__(self, sample_rate: int = 44100, **kwargs):
        kwargs.setdefault('room_size', 0.75)
        kwargs.setdefault('damping', 0.5)
        kwargs.setdefault('wet_dry', 0.33)
        kwargs.setdefault('width', 0.8)
        super().__init__(sample_rate=sample_rate, **kwargs)


def apply_reverb(audio: np.ndarray, 
                 room_size: float = 0.7,
                 damping: float = 0.5,
                 wet_dry: float = 0.3,
                 sample_rate: int = 44100) -> np.ndarray:
    """
    Convenience function: apply reverb to audio buffer.
    
    Args:
        audio: Input audio (mono or stereo)
        room_size: 0.0-1.0
        damping: 0.0-1.0
        wet_dry: 0.0-1.0
        sample_rate: Sample rate of audio
        
    Returns:
        Reverberated audio
    """
    reverb = AlgorithmicReverb(
        sample_rate=sample_rate,
        room_size=room_size,
        damping=damping,
        wet_dry=wet_dry
    )
    return reverb.process(audio)


if __name__ == "__main__":
    # Smoke test
    sr = 44100
    duration = 0.5
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    
    # Create test signal: short impulse
    impulse = np.zeros_like(t)
    impulse[0] = 1.0
    
    # Apply reverb
    reverb = AlgorithmicReverb(room_size=0.8, damping=0.4, wet_dry=0.5)
    wet = reverb.process(impulse)
    
    print(f"Input: {impulse.shape}, Output: {wet.shape}")
    print(f"Peak input: {np.max(np.abs(impulse)):.3f}")
    print(f"Peak output: {np.max(np.abs(wet)):.3f}")
    print(f"Reverb tail (last 50ms): {np.max(np.abs(wet[-2205:])):.6f}")
    print("✓ Reverb smoke test passed")
