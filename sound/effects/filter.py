"""Digital filters — state-variable filter (SVF) + subtractive synthesis chain.

Classic subtractive synthesis: oscillator → filter → VCA.
SVF provides simultaneous LP/HP/BP/notch outputs.

Usage:
    # Standalone filter
    filt = StateVariableFilter(sample_rate=44100)
    filtered = filt.process(audio, cutoff=1000.0, resonance=0.7, mode='lp')
    
    # Subtractive synth voice
    voice = SubtractiveVoice(sample_rate=44100)
    audio = voice.render_note(freq=440.0, duration=1.0, waveform='saw',
                               cutoff=2000.0, resonance=0.5)
"""

import numpy as np
from typing import Optional
from ..utils.envelope import ADSREnvelope


class StateVariableFilter:
    """
    Chamberlin state-variable filter.
    
    Provides simultaneous lowpass, highpass, bandpass, and notch outputs.
    Stable at audio rates with proper damping.
    
    Parameters:
        cutoff: Cutoff frequency in Hz (20-20000)
        resonance: Resonance 0.0-1.0 (1.0 = self-oscillation)
        mode: 'lp', 'hp', 'bp', 'notch'
    """
    
    MODES = ['lp', 'hp', 'bp', 'notch']
    
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        self.cutoff = 1000.0
        self.resonance = 0.5
        self.mode = 'lp'
        
        # State variables
        self._lp = 0.0
        self._bp = 0.0
    
    def _calc_coefficients(self, cutoff: float) -> tuple:
        """Calculate filter coefficients from cutoff frequency."""
        # Chamberlin SVF coefficients
        f = 2.0 * np.sin(np.pi * min(cutoff, self.sample_rate * 0.49) / self.sample_rate)
        q = 1.0 - self.resonance  # Damping (1-res = more feedback at high resonance)
        return f, q
    
    def process(self, audio: np.ndarray, 
                cutoff: Optional[float] = None,
                resonance: Optional[float] = None,
                mode: Optional[str] = None) -> np.ndarray:
        """
        Filter audio buffer.
        
        Args:
            audio: Input audio (float32/64)
            cutoff: Override cutoff frequency (Hz)
            resonance: Override resonance (0-1)
            mode: Override filter mode
            
        Returns:
            Filtered audio (same shape as input)
        """
        if cutoff is not None:
            self.cutoff = cutoff
        if resonance is not None:
            self.resonance = resonance
        if mode is not None:
            if mode not in self.MODES:
                raise ValueError(f"Unknown mode: {mode}. Use: {self.MODES}")
            self.mode = mode
        
        f, q = self._calc_coefficients(self.cutoff)

        # Stereo support: process each channel independently.
        is_stereo = len(audio.shape) > 1 and audio.shape[1] == 2
        if is_stereo:
            left = self.process(audio[:, 0], cutoff=cutoff, resonance=resonance, mode=mode)
            right = self.process(audio[:, 1], cutoff=cutoff, resonance=resonance, mode=mode)
            return np.column_stack([left, right])

        n = len(audio)
        output = np.zeros(n, dtype=np.float64)
        
        lp = self._lp
        bp = self._bp
        
        for i in range(n):
            inp = audio[i]
            
            # SVF difference equations
            hp = inp - lp - q * bp
            bp += f * hp
            lp += f * bp
            
            # Select output mode
            if self.mode == 'lp':
                output[i] = lp
            elif self.mode == 'hp':
                output[i] = hp
            elif self.mode == 'bp':
                output[i] = bp
            elif self.mode == 'notch':
                output[i] = hp + lp  # Notch = HP + LP
        
        # Save state for next buffer
        self._lp = lp
        self._bp = bp
        
        return output.astype(audio.dtype)
    
    def reset(self):
        """Clear filter state."""
        self._lp = 0.0
        self._bp = 0.0


class BiquadFilter:
    """
    Generic biquad (2-pole) filter.
    
    Supports: lowpass, highpass, bandpass, notch, allpass, peaking, lowshelf, highshelf.
    Uses Robert Bristow-Johnson's Audio EQ Cookbook formulas.
    """
    
    TYPES = ['lowpass', 'highpass', 'bandpass', 'notch', 'allpass', 
             'peaking', 'lowshelf', 'highshelf']
    
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        self.b = np.array([1.0, 0.0, 0.0])
        self.a = np.array([1.0, 0.0, 0.0])
        
        # State (Direct Form II Transposed)
        self._z1 = 0.0
        self._z2 = 0.0
    
    def set_coefficients(self, b: np.ndarray, a: np.ndarray):
        """Set filter coefficients directly."""
        self.b = np.array(b, dtype=np.float64)
        self.a = np.array(a, dtype=np.float64)
    
    def design(self, filter_type: str, freq: float, Q: float = 0.707, 
               gain_db: float = 0.0):
        """
        Design filter using RBJ cookbook formulas.
        
        Args:
            filter_type: One of TYPES
            freq: Cutoff/center frequency (Hz)
            Q: Quality factor (0.1-10.0)
            gain_db: Gain for peaking/shelving filters
        """
        w0 = 2 * np.pi * freq / self.sample_rate
        cos_w0 = np.cos(w0)
        sin_w0 = np.sin(w0)
        alpha = sin_w0 / (2 * Q)
        
        A = 10 ** (gain_db / 40.0)  # For peaking/shelving
        
        if filter_type == 'lowpass':
            b0 = (1 - cos_w0) / 2
            b1 = 1 - cos_w0
            b2 = (1 - cos_w0) / 2
            a0 = 1 + alpha
            a1 = -2 * cos_w0
            a2 = 1 - alpha
        elif filter_type == 'highpass':
            b0 = (1 + cos_w0) / 2
            b1 = -(1 + cos_w0)
            b2 = (1 + cos_w0) / 2
            a0 = 1 + alpha
            a1 = -2 * cos_w0
            a2 = 1 - alpha
        elif filter_type == 'bandpass':
            b0 = alpha
            b1 = 0
            b2 = -alpha
            a0 = 1 + alpha
            a1 = -2 * cos_w0
            a2 = 1 - alpha
        elif filter_type == 'notch':
            b0 = 1
            b1 = -2 * cos_w0
            b2 = 1
            a0 = 1 + alpha
            a1 = -2 * cos_w0
            a2 = 1 - alpha
        elif filter_type == 'allpass':
            b0 = 1 - alpha
            b1 = -2 * cos_w0
            b2 = 1 + alpha
            a0 = 1 + alpha
            a1 = -2 * cos_w0
            a2 = 1 - alpha
        elif filter_type == 'peaking':
            b0 = 1 + alpha * A
            b1 = -2 * cos_w0
            b2 = 1 - alpha * A
            a0 = 1 + alpha / A
            a1 = -2 * cos_w0
            a2 = 1 - alpha / A
        elif filter_type == 'lowshelf':
            b0 = A * ((A + 1) - (A - 1) * cos_w0 + 2 * np.sqrt(A) * alpha)
            b1 = 2 * A * ((A - 1) - (A + 1) * cos_w0)
            b2 = A * ((A + 1) - (A - 1) * cos_w0 - 2 * np.sqrt(A) * alpha)
            a0 = (A + 1) + (A - 1) * cos_w0 + 2 * np.sqrt(A) * alpha
            a1 = -2 * ((A - 1) + (A + 1) * cos_w0)
            a2 = (A + 1) + (A - 1) * cos_w0 - 2 * np.sqrt(A) * alpha
        elif filter_type == 'highshelf':
            b0 = A * ((A + 1) + (A - 1) * cos_w0 + 2 * np.sqrt(A) * alpha)
            b1 = -2 * A * ((A - 1) + (A + 1) * cos_w0)
            b2 = A * ((A + 1) + (A - 1) * cos_w0 - 2 * np.sqrt(A) * alpha)
            a0 = (A + 1) - (A - 1) * cos_w0 + 2 * np.sqrt(A) * alpha
            a1 = 2 * ((A - 1) - (A + 1) * cos_w0)
            a2 = (A + 1) - (A - 1) * cos_w0 - 2 * np.sqrt(A) * alpha
        else:
            raise ValueError(f"Unknown filter type: {filter_type}")
        
        # Normalize
        self.b = np.array([b0 / a0, b1 / a0, b2 / a0])
        self.a = np.array([1.0, a1 / a0, a2 / a0])
    
    def process(self, audio: np.ndarray) -> np.ndarray:
        """
        Apply biquad filter to audio.

        Args:
            audio: Input audio buffer (mono 1D or stereo [n, 2])

        Returns:
            Filtered audio (same shape as input)
        """
        # Stereo support: process each channel independently.
        is_stereo = len(audio.shape) > 1 and audio.shape[1] == 2
        if is_stereo:
            return np.column_stack([
                self.process(audio[:, 0]),
                self.process(audio[:, 1]),
            ])

        n = len(audio)
        output = np.zeros(n, dtype=np.float64)
        
        z1 = self._z1
        z2 = self._z2
        
        for i in range(n):
            inp = audio[i]
            out = self.b[0] * inp + z1
            z1 = self.b[1] * inp - self.a[1] * out + z2
            z2 = self.b[2] * inp - self.a[2] * out
            output[i] = out
        
        self._z1 = z1
        self._z2 = z2
        
        return output.astype(audio.dtype)
    
    def reset(self):
        """Clear filter state."""
        self._z1 = 0.0
        self._z2 = 0.0


class SubtractiveVoice:
    """
    Subtractive synthesis voice: oscillator → filter → VCA.
    
    Classic analog-style synthesis.
    
    Parameters:
        waveform: 'sine', 'saw', 'square', 'triangle'
        cutoff: Filter cutoff frequency (Hz)
        resonance: Filter resonance (0-1)
        filter_mode: 'lp', 'hp', 'bp', 'notch'
        filter_env: Filter envelope amount (Hz)
        amp_env: Amplitude envelope (ADSR)
    """
    
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        self.filter = StateVariableFilter(sample_rate)
    
    def _oscillator(self, freq: float, duration: float, 
                    waveform: str = 'saw') -> np.ndarray:
        """Generate oscillator waveform."""
        n_samples = int(duration * self.sample_rate)
        t = np.linspace(0, duration, n_samples, endpoint=False)
        phase = 2 * np.pi * freq * t
        
        if waveform == 'sine':
            return np.sin(phase)
        elif waveform == 'saw':
            return 2.0 * (freq * t % 1.0) - 1.0
        elif waveform == 'square':
            return np.sign(np.sin(phase))
        elif waveform == 'triangle':
            return 2.0 * np.abs(2.0 * (freq * t % 1.0) - 1.0) - 1.0
        else:
            raise ValueError(f"Unknown waveform: {waveform}")
    
    def render_note(self,
                    freq: float,
                    duration: float,
                    waveform: str = 'saw',
                    cutoff: float = 2000.0,
                    resonance: float = 0.5,
                    filter_mode: str = 'lp',
                    filter_env: float = 0.0,
                    attack: float = 0.01,
                    decay: float = 0.1,
                    sustain_level: float = 0.7,
                    release: float = 0.2,
                    filter_attack: float = 0.05,
                    filter_decay: float = 0.2,
                    filter_sustain: float = 0.5,
                    filter_release: float = 0.3,
                    volume: float = 0.8) -> np.ndarray:
        """
        Render a single note.
        
        Args:
            freq: Frequency (Hz)
            duration: Duration (seconds)
            waveform: Oscillator waveform
            cutoff: Base filter cutoff (Hz)
            resonance: Filter resonance (0-1)
            filter_mode: 'lp', 'hp', 'bp', 'notch'
            filter_env: Filter envelope depth (Hz, added to cutoff)
            attack/decay/sustain_level/release: Amp ADSR
            filter_attack/decay/sustain/release: Filter ADSR
            volume: Peak amplitude (0-1)
            
        Returns:
            Audio buffer (float32)
        """
        # Oscillator
        osc = self._oscillator(freq, duration, waveform)
        
        # Filter envelope
        if filter_env > 0:
            filt_env = ADSREnvelope(filter_attack, filter_decay, 
                                    filter_sustain, filter_release, 
                                    self.sample_rate)
            env_curve = filt_env.generate(duration)
            
            # Modulate cutoff
            cutoff_mod = cutoff + env_curve * filter_env
            cutoff_mod = np.clip(cutoff_mod, 20, self.sample_rate * 0.49)
            
            # Apply filter sample-by-sample with modulating cutoff
            self.filter.reset()
            n = len(osc)
            output = np.zeros(n, dtype=np.float64)
            
            for i in range(n):
                self.filter.cutoff = cutoff_mod[i]
                self.filter.resonance = resonance
                self.filter.mode = filter_mode
                output[i] = self.filter.process(np.array([osc[i]]))[0]
        else:
            # Static filter
            output = self.filter.process(osc, cutoff=cutoff, 
                                         resonance=resonance, mode=filter_mode)
        
        # Amp envelope
        amp_env = ADSREnvelope(attack, decay, sustain_level, release, 
                               self.sample_rate)
        envelope = amp_env.generate(duration)
        
        output *= envelope * volume
        
        return output.astype(np.float32)
    
    def render_melody(self,
                      notes: list,
                      **voice_kwargs) -> np.ndarray:
        """
        Render a sequence of notes.
        
        Args:
            notes: List of (freq_hz, start_time_sec, duration_sec)
            **voice_kwargs: Passed to render_note()
            
        Returns:
            Mixed audio buffer
        """
        if not notes:
            return np.zeros(0, dtype=np.float32)
        
        max_end = max(start + dur for _, start, dur in notes)
        total_samples = int(max_end * self.sample_rate)
        output = np.zeros(total_samples, dtype=np.float32)
        
        for freq, start, dur in notes:
            self.filter.reset()
            note_audio = self.render_note(freq, dur, **voice_kwargs)
            start_sample = int(start * self.sample_rate)
            end_sample = min(start_sample + len(note_audio), total_samples)
            output[start_sample:end_sample] += note_audio[:end_sample - start_sample]
        
        # Normalize
        peak = np.max(np.abs(output))
        if peak > 0:
            output = output / peak * 0.9
        
        return output


def apply_filter(audio: np.ndarray, 
                 filter_type: str = 'lowpass',
                 cutoff: float = 1000.0,
                 Q: float = 0.707,
                 sample_rate: int = 44100) -> np.ndarray:
    """
    Convenience function: apply biquad filter to audio.
    
    Args:
        audio: Input audio
        filter_type: 'lowpass', 'highpass', 'bandpass', 'notch', etc.
        cutoff: Cutoff frequency (Hz)
        Q: Quality factor
        sample_rate: Sample rate
        
    Returns:
        Filtered audio
    """
    filt = BiquadFilter(sample_rate)
    filt.design(filter_type, cutoff, Q)
    return filt.process(audio)


if __name__ == "__main__":
    # Smoke test
    sr = 44100
    duration = 0.5
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    
    # Create test signal: sawtooth
    saw = 2.0 * (440.0 * t % 1.0) - 1.0
    
    # Apply lowpass filter
    filt = StateVariableFilter(sr)
    filtered = filt.process(saw, cutoff=500.0, resonance=0.3, mode='lp')
    
    print(f"Input: {saw.shape}, Output: {filtered.shape}")
    print(f"Peak input: {np.max(np.abs(saw)):.3f}")
    print(f"Peak output: {np.max(np.abs(filtered)):.3f}")
    
    # Test biquad
    bq = BiquadFilter(sr)
    bq.design('lowpass', 1000.0, Q=1.0)
    bq_out = bq.process(saw)
    print(f"Biquad output peak: {np.max(np.abs(bq_out)):.3f}")
    
    # Test subtractive voice
    voice = SubtractiveVoice(sr)
    note = voice.render_note(440.0, 0.5, waveform='saw', cutoff=1500.0, 
                              resonance=0.4, filter_env=2000.0)
    print(f"Subtractive note: {note.shape}, peak: {np.max(np.abs(note)):.3f}")
    
    print("✓ Filter smoke test passed")
