"""Phase modulation synthesis — FDS-style wavetable phase modulation.

Carrier wavetable phase-modulated by modulator waveform.
Based on Nintendo FDS sound chip architecture + general PM synthesis.

Usage:
    synth = PhaseModSynth(sample_rate=44100)
    audio = synth.render_note(freq=440.0, duration=1.0, carrier_shape='sine',
                               mod_freq_ratio=1.0, mod_depth=2.0)
"""

import numpy as np
from typing import Optional, List, Tuple
from ..utils.envelope import ADSREnvelope


# Wavetable shapes
WAVETABLE_SIZE = 256


def _build_wavetable(shape: str, size: int = WAVETABLE_SIZE) -> np.ndarray:
    """Build a single-cycle wavetable."""
    t = np.linspace(0, 2 * np.pi, size, endpoint=False)
    
    if shape == 'sine':
        return np.sin(t)
    elif shape == 'saw':
        return 2.0 * (t / (2 * np.pi)) - 1.0
    elif shape == 'square':
        return np.sign(np.sin(t))
    elif shape == 'triangle':
        return 2.0 * np.abs(2.0 * (t / (2 * np.pi)) - 1.0) - 1.0
    elif shape == 'pulse25':
        pulse = np.zeros(size)
        pulse[:size // 4] = 1.0
        pulse[size // 4:] = -1.0
        return pulse
    elif shape == 'pulse50':
        return np.sign(np.sin(t))  # Same as square
    elif shape == 'halfsine':
        wt = np.sin(t[:size // 2])
        return np.concatenate([wt, np.zeros(size - len(wt))])
    elif shape == 'noise':
        return np.random.uniform(-1, 1, size)
    else:
        raise ValueError(f"Unknown wavetable shape: {shape}")
    
    return np.sin(t)


def _build_harmonic_wavetable(harmonics: List[Tuple[int, float]], 
                               size: int = WAVETABLE_SIZE) -> np.ndarray:
    """Build wavetable from additive harmonic specification.
    
    Args:
        harmonics: List of (harmonic_number, amplitude) pairs
        size: Wavetable size
    
    Returns:
        Normalized wavetable
    """
    t = np.linspace(0, 2 * np.pi, size, endpoint=False)
    wt = np.zeros(size)
    
    for harmonic_num, amplitude in harmonics:
        wt += amplitude * np.sin(harmonic_num * t)
    
    # Normalize
    peak = np.max(np.abs(wt))
    if peak > 0:
        wt /= peak
    
    return wt


class PhaseModSynth:
    """
    Phase modulation synthesizer.
    
    Architecture:
        modulator → phase offset → carrier wavetable lookup → output
        
    The modulator waveform offsets the read pointer of the carrier wavetable,
    creating rich harmonic content from simple waveforms.
    
    Parameters:
        carrier_shape: Wavetable shape for carrier ('sine', 'saw', 'square', etc.)
        mod_shape: Wavetable shape for modulator
        mod_freq_ratio: Modulator frequency as ratio of carrier freq
        mod_depth: Phase modulation depth (in wavetable indices)
        harmonics: Alternative to carrier_shape — list of (harmonic, amplitude)
    """
    
    SHAPES = ['sine', 'saw', 'square', 'triangle', 'pulse25', 'pulse50', 
              'halfsine', 'noise']
    
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        
        # Pre-build wavetables
        self.wavetables = {}
        for shape in self.SHAPES:
            self.wavetables[shape] = _build_wavetable(shape)
    
    def _lookup(self, wavetable: np.ndarray, phase: float) -> float:
        """Lookup value from wavetable at fractional phase [0, 1)."""
        idx = phase * len(wavetable)
        i0 = int(idx) % len(wavetable)
        i1 = (i0 + 1) % len(wavetable)
        frac = idx - int(idx)
        # Linear interpolation
        return wavetable[i0] * (1 - frac) + wavetable[i1] * frac
    
    def _lookup_vectorized(self, wavetable: np.ndarray, 
                            phases: np.ndarray) -> np.ndarray:
        """Vectorized wavetable lookup with linear interpolation."""
        size = len(wavetable)
        idx = (phases % 1.0) * size
        i0 = idx.astype(np.int32) % size
        i1 = (i0 + 1) % size
        frac = idx - idx.astype(np.int32)
        return wavetable[i0] * (1 - frac) + wavetable[i1] * frac
    
    def render_note(self, 
                    freq: float,
                    duration: float,
                    carrier_shape: str = 'sine',
                    mod_shape: str = 'sine',
                    mod_freq_ratio: float = 1.0,
                    mod_depth: float = 2.0,
                    volume: float = 0.8,
                    attack: float = 0.01,
                    decay: float = 0.1,
                    sustain_level: float = 0.7,
                    release: float = 0.2,
                    harmonics: Optional[List[Tuple[int, float]]] = None,
                    mod_env: Optional[str] = None
                    ) -> np.ndarray:
        """
        Render a single note.
        
        Args:
            freq: Frequency in Hz
            duration: Duration in seconds
            carrier_shape: Carrier wavetable shape
            mod_shape: Modulator wavetable shape
            mod_freq_ratio: Mod freq = freq * ratio
            mod_depth: PM depth (wavetable index offset, 0-10 typical)
            volume: Peak amplitude (0-1)
            attack/decay/sustain_level/release: ADSR envelope
            harmonics: Override carrier_shape with additive harmonics
            mod_env: If 'adsr', apply envelope to mod_depth too
            
        Returns:
            Audio buffer (float32, normalized)
        """
        n_samples = int(duration * self.sample_rate)
        t = np.arange(n_samples) / self.sample_rate
        
        # Get carrier wavetable
        if harmonics:
            carrier_wt = _build_harmonic_wavetable(harmonics)
        else:
            if carrier_shape not in self.wavetables:
                raise ValueError(f"Unknown shape: {carrier_shape}. Use: {self.SHAPES}")
            carrier_wt = self.wavetables[carrier_shape]
        
        mod_wt = self.wavetables.get(mod_shape, self.wavetables['sine'])
        
        # Phase accumulators
        carrier_phase = np.cumsum(np.full(n_samples, freq / self.sample_rate)) % 1.0
        mod_freq = freq * mod_freq_ratio
        mod_phase = np.cumsum(np.full(n_samples, mod_freq / self.sample_rate)) % 1.0
        
        # Modulator output
        mod_signal = self._lookup_vectorized(mod_wt, mod_phase)
        
        # Apply mod depth — mod_depth is in radians of phase modulation
        # Typical values: 0.1-10.0 radians
        phase_offset = mod_signal * mod_depth / (2 * np.pi)
        
        # Phase-modulated carrier lookup
        modulated_phase = (carrier_phase + phase_offset) % 1.0
        output = self._lookup_vectorized(carrier_wt, modulated_phase)
        
        # ADSR envelope
        env = ADSREnvelope(attack, decay, sustain_level, release, self.sample_rate)
        envelope = env.generate(duration)
        
        # Apply mod envelope if requested
        if mod_env == 'adsr':
            # Re-modulate with envelope-scaled depth
            scaled_offset = mod_signal * mod_depth * envelope / len(carrier_wt)
            modulated_phase = (carrier_phase + scaled_offset) % 1.0
            output = self._lookup_vectorized(carrier_wt, modulated_phase)
        
        output *= envelope * volume
        
        return output.astype(np.float32)
    
    def render_melody(self, 
                      notes: List[Tuple[float, float, float]],
                      **synth_kwargs) -> np.ndarray:
        """
        Render a sequence of notes.
        
        Args:
            notes: List of (freq_hz, start_time_sec, duration_sec) tuples
            **synth_kwargs: Passed to render_note()
            
        Returns:
            Mixed audio buffer
        """
        if not notes:
            return np.zeros(0, dtype=np.float32)
        
        # Calculate total duration
        max_end = max(start + dur for _, start, dur in notes)
        total_samples = int(max_end * self.sample_rate)
        output = np.zeros(total_samples, dtype=np.float32)
        
        for freq, start, dur in notes:
            note_audio = self.render_note(freq, dur, **synth_kwargs)
            start_sample = int(start * self.sample_rate)
            end_sample = min(start_sample + len(note_audio), total_samples)
            output[start_sample:end_sample] += note_audio[:end_sample - start_sample]
        
        # Normalize
        peak = np.max(np.abs(output))
        if peak > 0:
            output = output / peak * 0.9
        
        return output


class FDSSynth(PhaseModSynth):
    """
    Nintendo FDS-style phase modulation synth.
    
    64-sample carrier wavetable, 32-step modulator sequence.
    Simplified to use our wavetable system with FDS-appropriate defaults.
    """
    
    def __init__(self, sample_rate: int = 44100):
        super().__init__(sample_rate)
        # FDS uses a custom modulator table — approximate with sine
        # Real FDS mod table: [0,0,0,0,1,1,1,1,2,2,2,2,1,1,1,1,0,0,0,0,-1,-1,-1,-1,-2,-2,-2,-2,-1,-1,-1,-1]
    
    def render_note(self, freq, duration, **kwargs):
        kwargs.setdefault('carrier_shape', 'sine')
        kwargs.setdefault('mod_shape', 'sine')
        kwargs.setdefault('mod_freq_ratio', 1.0)
        kwargs.setdefault('mod_depth', 3.0)
        kwargs.setdefault('attack', 0.005)
        kwargs.setdefault('release', 0.1)
        return super().render_note(freq, duration, **kwargs)


if __name__ == "__main__":
    synth = PhaseModSynth()
    
    # Render test note
    note = synth.render_note(440.0, 0.5, carrier_shape='sine', 
                              mod_shape='sine', mod_depth=3.0)
    print(f"Note: {note.shape}, peak: {np.max(np.abs(note)):.3f}")
    
    # Render melody
    melody = [
        (440.0, 0.0, 0.3),   # A4
        (523.25, 0.3, 0.3),  # C5
        (659.25, 0.6, 0.3),  # E5
        (880.0, 0.9, 0.5),   # A5
    ]
    result = synth.render_melody(melody, carrier_shape='sine', mod_depth=2.0)
    print(f"Melody: {result.shape}, peak: {np.max(np.abs(result)):.3f}")
    print("✓ Phase modulation synth smoke test passed")
