"""Envelope and windowing utilities - DSP primitives.

Consolidates envelope generation from across the codebase.
"""

import numpy as np
from typing import Tuple, Optional


class ADSREnvelope:
    """ADSR (Attack-Decay-Sustain-Release) envelope generator.
    
    Generates smooth amplitude envelopes for audio synthesis.
    """
    
    def __init__(self, 
                 attack_time: float = 0.05,
                 decay_time: float = 0.1,
                 sustain_level: float = 0.7,
                 release_time: float = 0.2,
                 sample_rate: int = 44100):
        """
        Args:
            attack_time: Attack time in seconds
            decay_time: Decay time in seconds
            sustain_level: Sustain level (0-1)
            release_time: Release time in seconds
            sample_rate: Sample rate in Hz
        """
        self.attack_time = attack_time
        self.decay_time = decay_time
        self.sustain_level = sustain_level
        self.release_time = release_time
        self.sample_rate = sample_rate
    
    def generate(self, duration: float) -> np.ndarray:
        """Generate ADSR envelope for given duration.
        
        Args:
            duration: Total duration in seconds
            
        Returns:
            Envelope array (float32, 0-1)
        """
        total_samples = int(duration * self.sample_rate)
        
        # Calculate segment lengths
        attack_samples = int(self.attack_time * self.sample_rate)
        decay_samples = int(self.decay_time * self.sample_rate)
        release_samples = int(self.release_time * self.sample_rate)
        sustain_samples = total_samples - attack_samples - decay_samples - release_samples
        
        if sustain_samples < 0:
            # Duration too short for full ADSR, compress
            sustain_samples = 0
            # Proportionally scale segments
            scale = total_samples / (attack_samples + decay_samples + release_samples)
            attack_samples = int(attack_samples * scale)
            decay_samples = int(decay_samples * scale)
            release_samples = total_samples - attack_samples - decay_samples
        
        # Build envelope segments
        envelope = np.zeros(total_samples, dtype=np.float32)
        idx = 0
        
        # Attack
        if attack_samples > 0:
            envelope[idx:idx + attack_samples] = np.linspace(0, 1, attack_samples)
            idx += attack_samples
        
        # Decay
        if decay_samples > 0:
            envelope[idx:idx + decay_samples] = np.linspace(1, self.sustain_level, decay_samples)
            idx += decay_samples
        
        # Sustain
        if sustain_samples > 0:
            envelope[idx:idx + sustain_samples] = self.sustain_level
            idx += sustain_samples
        
        # Release
        if release_samples > 0:
            envelope[idx:idx + release_samples] = np.linspace(self.sustain_level, 0, release_samples)
        
        return envelope


def hanning_window(size: int) -> np.ndarray:
    """Generate Hanning (raised cosine) window.
    
    Args:
        size: Window size in samples
        
    Returns:
        Hanning window array (float32, 0-1)
    """
    return np.hanning(size).astype(np.float32)


def exponential_decay(duration: float, decay_rate: float = 5.0, 
                     sample_rate: int = 44100) -> np.ndarray:
    """Generate exponential decay envelope.
    
    Args:
        duration: Duration in seconds
        decay_rate: Decay rate (higher = faster decay)
        sample_rate: Sample rate in Hz
        
    Returns:
        Decay envelope array (float32, 0-1)
    """
    t = np.linspace(0, duration, int(duration * sample_rate), dtype=np.float32)
    envelope = np.exp(-decay_rate * t / duration)
    return envelope


__all__ = [
    "ADSREnvelope",
    "hanning_window",
    "exponential_decay",
]
