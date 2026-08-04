"""Modal synthesis — resonator banks for physical modeling.

Sum of damped sinusoids. Each mode = frequency + decay + amplitude.
Inspired by reFX Rippler modal synthesis engine.

Usage:
    bank = ResonatorBank(sample_rate=44100)
    bank.add_mode(freq=440.0, amplitude=1.0, decay=5.0)
    bank.add_mode(freq=880.0, amplitude=0.5, decay=8.0)
    audio = bank.excite_impulse()
    
    # Or use presets
    bank = ResonatorBank.preset('marimba', sample_rate=44100)
    audio = bank.excite_noise(duration=0.1)
"""

import numpy as np
from typing import List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class ResonatorMode:
    """Single resonant mode (damped sinusoid)."""
    frequency: float      # Hz
    amplitude: float      # 0-1
    decay_rate: float     # Higher = faster decay
    phase: float = 0.0    # Initial phase (radians)


class Resonator:
    """Single damped sinusoid resonator.
    
    y(t) = A * exp(-decay * t) * sin(2π * freq * t + phase)
    """
    
    def __init__(self, mode: ResonatorMode, sample_rate: int = 44100):
        self.mode = mode
        self.sample_rate = sample_rate
    
    def render(self, duration: float) -> np.ndarray:
        """Render resonator output for given duration."""
        n_samples = int(duration * self.sample_rate)
        t = np.arange(n_samples) / self.sample_rate
        
        # Damped sinusoid
        envelope = np.exp(-self.mode.decay_rate * t)
        oscillation = np.sin(2 * np.pi * self.mode.frequency * t + self.mode.phase)
        
        return self.mode.amplitude * envelope * oscillation


class ResonatorBank:
    """
    Bank of coupled resonators for modal synthesis.
    
    Each resonator = damped sinusoid at specific frequency/decay/amplitude.
    Coupling matrix allows energy transfer between modes (optional).
    
    Parameters:
        modes: List of ResonatorMode objects
        coupling: NxN matrix of energy transfer coefficients (0-1)
        sample_rate: Audio sample rate
    """
    
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        self.modes: List[ResonatorMode] = []
        self.coupling: Optional[np.ndarray] = None
    
    def add_mode(self, freq: float, amplitude: float = 1.0, 
                 decay: float = 5.0, phase: float = 0.0):
        """Add a resonant mode to the bank."""
        self.modes.append(ResonatorMode(freq, amplitude, decay, phase))
    
    def set_coupling(self, matrix: np.ndarray):
        """
        Set inter-mode coupling matrix.
        
        Args:
            matrix: NxN array where matrix[i,j] = energy transfer from mode i to mode j
                   Diagonal should be 0 (no self-coupling)
        """
        n = len(self.modes)
        if matrix.shape != (n, n):
            raise ValueError(f"Coupling matrix must be {n}x{n}, got {matrix.shape}")
        self.coupling = matrix
    
    def excite_impulse(self, duration: float = 1.0) -> np.ndarray:
        """
        Excite all modes with impulse (delta function).
        
        Args:
            duration: Output duration in seconds
            
        Returns:
            Mixed audio from all modes
        """
        if not self.modes:
            return np.zeros(int(duration * self.sample_rate), dtype=np.float32)
        
        output = np.zeros(int(duration * self.sample_rate), dtype=np.float64)
        
        for mode in self.modes:
            resonator = Resonator(mode, self.sample_rate)
            output += resonator.render(duration)
        
        # Apply coupling if set
        if self.coupling is not None:
            output = self._apply_coupling(output, duration)
        
        # Normalize
        peak = np.max(np.abs(output))
        if peak > 0:
            output = output / peak * 0.9
        
        return output.astype(np.float32)
    
    def excite_noise(self, duration: float = 0.1) -> np.ndarray:
        """
        Excite modes with white noise burst.
        
        Args:
            duration: Noise burst duration (modes continue to ring)
            
        Returns:
            Audio output
        """
        if not self.modes:
            return np.zeros(int(duration * self.sample_rate), dtype=np.float32)
        
        # Generate noise burst
        noise_len = int(duration * self.sample_rate)
        noise = np.random.uniform(-1, 1, noise_len)
        
        # Render each mode convolved with noise
        total_duration = duration + 2.0  # Allow 2s ring time
        output = np.zeros(int(total_duration * self.sample_rate), dtype=np.float64)
        
        for mode in self.modes:
            resonator = Resonator(mode, self.sample_rate)
            mode_signal = resonator.render(total_duration)
            
            # Convolve noise with mode (noise excites mode)
            excited = np.convolve(noise, mode_signal, mode='full')[:len(mode_signal)]
            output += excited
        
        # Apply coupling
        if self.coupling is not None:
            output = self._apply_coupling(output, total_duration)
        
        # Normalize
        peak = np.max(np.abs(output))
        if peak > 0:
            output = output / peak * 0.9
        
        return output.astype(np.float32)
    
    def excite_custom(self, excitation: np.ndarray, ring_duration: float = 2.0) -> np.ndarray:
        """
        Excite modes with custom excitation signal.
        
        Args:
            excitation: Input signal (e.g., sampled strike, bowed signal)
            ring_duration: How long modes ring after excitation ends
            
        Returns:
            Audio output
        """
        if not self.modes:
            return np.zeros(len(excitation), dtype=np.float32)
        
        total_duration = len(excitation) / self.sample_rate + ring_duration
        output = np.zeros(int(total_duration * self.sample_rate), dtype=np.float64)
        
        for mode in self.modes:
            resonator = Resonator(mode, self.sample_rate)
            mode_signal = resonator.render(total_duration)
            
            # Convolve excitation with mode
            excited = np.convolve(excitation, mode_signal, mode='full')[:len(mode_signal)]
            output += excited
        
        if self.coupling is not None:
            output = self._apply_coupling(output, total_duration)
        
        peak = np.max(np.abs(output))
        if peak > 0:
            output = output / peak * 0.9
        
        return output.astype(np.float32)
    
    def _apply_coupling(self, audio: np.ndarray, duration: float) -> np.ndarray:
        """Apply inter-mode energy transfer (simplified)."""
        # Simplified: just mix modes with coupling coefficients
        # Full implementation would track per-mode energy and transfer
        if self.coupling is None:
            return audio
        
        # For now, just return audio (coupling is complex to implement properly)
        # TODO: Implement proper modal coupling with energy tracking
        return audio
    
    @classmethod
    def preset(cls, name: str, sample_rate: int = 44100) -> 'ResonatorBank':
        """
        Create resonator bank from preset.
        
        Presets: 'marimba', 'bell', 'drum', 'string', 'plate', 'tube'
        """
        bank = cls(sample_rate)
        
        if name == 'marimba':
            # Marimba: strong fundamental, odd harmonics, fast decay
            bank.add_mode(440.0, 1.0, 8.0)      # Fundamental
            bank.add_mode(880.0, 0.3, 12.0)     # 2nd (octave)
            bank.add_mode(1320.0, 0.15, 15.0)   # 3rd (octave + 5th)
            bank.add_mode(1760.0, 0.08, 18.0)   # 4th (2nd octave)
            bank.add_mode(2200.0, 0.05, 20.0)   # 5th
            
        elif name == 'bell':
            # Bell: inharmonic partials, slow decay
            bank.add_mode(440.0, 1.0, 3.0)
            bank.add_mode(660.0, 0.6, 4.0)      # Minor 3rd above
            bank.add_mode(880.0, 0.4, 5.0)      # Octave
            bank.add_mode(1100.0, 0.3, 6.0)     # Major 3rd above octave
            bank.add_mode(1320.0, 0.25, 7.0)    # 5th above octave
            bank.add_mode(1760.0, 0.2, 8.0)     # 2nd octave
            bank.add_mode(2200.0, 0.15, 9.0)
            
        elif name == 'drum':
            # Drum: low fundamental, inharmonic, fast decay
            bank.add_mode(100.0, 1.0, 15.0)
            bank.add_mode(180.0, 0.5, 20.0)
            bank.add_mode(260.0, 0.3, 25.0)
            bank.add_mode(340.0, 0.2, 30.0)
            bank.add_mode(420.0, 0.1, 35.0)
            
        elif name == 'string':
            # String: harmonic series, moderate decay
            bank.add_mode(440.0, 1.0, 4.0)
            bank.add_mode(880.0, 0.7, 5.0)
            bank.add_mode(1320.0, 0.5, 6.0)
            bank.add_mode(1760.0, 0.35, 7.0)
            bank.add_mode(2200.0, 0.25, 8.0)
            bank.add_mode(2640.0, 0.18, 9.0)
            bank.add_mode(3080.0, 0.12, 10.0)
            bank.add_mode(3520.0, 0.08, 11.0)
            
        elif name == 'plate':
            # Metal plate: inharmonic, slow decay
            bank.add_mode(300.0, 1.0, 2.0)
            bank.add_mode(520.0, 0.6, 3.0)
            bank.add_mode(780.0, 0.4, 4.0)
            bank.add_mode(1100.0, 0.3, 5.0)
            bank.add_mode(1450.0, 0.2, 6.0)
            bank.add_mode(1850.0, 0.15, 7.0)
            
        elif name == 'tube':
            # Hollow tube: odd harmonics only
            bank.add_mode(220.0, 1.0, 5.0)
            bank.add_mode(660.0, 0.5, 6.0)      # 3rd
            bank.add_mode(1100.0, 0.3, 7.0)     # 5th
            bank.add_mode(1540.0, 0.2, 8.0)     # 7th
            bank.add_mode(1980.0, 0.15, 9.0)    # 9th
            
        else:
            raise ValueError(f"Unknown preset: {name}. Use: marimba, bell, drum, string, plate, tube")
        
        return bank


class ModalSynth:
    """
    High-level modal synthesis interface.
    
    Combines resonator bank with excitation methods and presets.
    """
    
    PRESETS = ['marimba', 'bell', 'drum', 'string', 'plate', 'tube']
    
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
    
    def render_preset(self, preset: str, duration: float = 1.0,
                      excitation: str = 'impulse') -> np.ndarray:
        """
        Render a preset instrument.
        
        Args:
            preset: Instrument name
            duration: Output duration
            excitation: 'impulse', 'noise', or 'custom'
            
        Returns:
            Audio buffer
        """
        bank = ResonatorBank.preset(preset, self.sample_rate)
        
        if excitation == 'impulse':
            return bank.excite_impulse(duration)
        elif excitation == 'noise':
            return bank.excite_noise(duration * 0.1)
        else:
            raise ValueError(f"Unknown excitation: {excitation}")
    
    def render_custom(self, modes: List[Tuple[float, float, float]],
                      duration: float = 1.0,
                      excitation: str = 'impulse') -> np.ndarray:
        """
        Render custom modal configuration.
        
        Args:
            modes: List of (freq, amplitude, decay) tuples
            duration: Output duration
            excitation: 'impulse' or 'noise'
            
        Returns:
            Audio buffer
        """
        bank = ResonatorBank(self.sample_rate)
        for freq, amp, decay in modes:
            bank.add_mode(freq, amp, decay)
        
        if excitation == 'impulse':
            return bank.excite_impulse(duration)
        elif excitation == 'noise':
            return bank.excite_noise(duration * 0.1)
        else:
            raise ValueError(f"Unknown excitation: {excitation}")


if __name__ == "__main__":
    # Smoke test
    sr = 44100
    
    # Test preset
    bank = ResonatorBank.preset('marimba', sr)
    audio = bank.excite_impulse(1.0)
    print(f"Marimba: {audio.shape}, peak: {np.max(np.abs(audio)):.3f}")
    
    # Test custom
    bank2 = ResonatorBank(sr)
    bank2.add_mode(440.0, 1.0, 5.0)
    bank2.add_mode(880.0, 0.5, 8.0)
    audio2 = bank2.excite_impulse(0.5)
    print(f"Custom: {audio2.shape}, peak: {np.max(np.abs(audio2)):.3f}")
    
    # Test noise excitation
    audio3 = bank.excite_noise(0.05)
    print(f"Noise excite: {audio3.shape}, peak: {np.max(np.abs(audio3)):.3f}")
    
    print("✓ Modal synthesis smoke test passed")
