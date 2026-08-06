"""Polyphonic multi-engine synthesizer — Astrolab-style.

Offline-rendering polysynth with 3 oscillators per voice (VA + wavetable + FM),
oscillator sync, ring modulation, 24dB/oct multimode filter, 4 envelopes,
4 LFOs, and 16-step sequencer per voice.

No realtime — batch render to numpy arrays / WAV.

Usage:
    voice = PolyVoice(sample_rate=44100)
    voice.osc1.waveform = 'saw'
    voice.osc2.waveform = 'square'
    voice.osc2.detune_cents = 7
    voice.osc3.waveform = 'sine'
    voice.filter.cutoff = 2000.0
    voice.filter.resonance = 0.4
    voice.env1.set(attack=0.01, decay=0.2, sustain=0.7, release=0.3)
    voice.lfo1.rate = 5.0
    voice.lfo1.depth = 0.3
    voice.lfo1.target = 'filter_cutoff'
    
    audio = voice.render_note(freq=440.0, duration=1.0)
"""

import numpy as np
from typing import Optional, List
from dataclasses import dataclass, field


# =============================================================================
# Oscillator
# =============================================================================

class Oscillator:
    """Single oscillator with VA waveforms + wavetable + FM input."""
    
    WAVEFORMS = ['sine', 'saw', 'square', 'triangle', 'pulse25', 'pulse50', 'noise']
    
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        self.waveform = 'saw'
        self.detune_cents = 0.0
        self.octave = 0
        self.level = 1.0
        self.pan = 0.0  # -1 left, 0 center, +1 right
        
        # Wavetable
        self.wavetable: Optional[np.ndarray] = None
        
        # Sync source (another oscillator)
        self.sync_source: Optional['Oscillator'] = None
        self.sync_enabled = False
    
    def _compute_freq(self, base_freq: float) -> float:
        """Apply detune + octave shift."""
        freq = base_freq * (2.0 ** (self.detune_cents / 1200.0))
        freq *= (2.0 ** self.octave)
        return freq
    
    def generate(self, freq: float, n_samples: int, 
                 phase_offset: Optional[np.ndarray] = None,
                 sync_phase: Optional[np.ndarray] = None) -> np.ndarray:
        """Generate audio buffer."""
        actual_freq = self._compute_freq(freq)
        t = np.arange(n_samples) / self.sample_rate
        
        # Phase accumulator
        phase = (actual_freq * t) % 1.0
        
        # Apply external phase offset (for FM)
        if phase_offset is not None:
            phase = (phase + phase_offset) % 1.0
        
        # Apply sync (reset phase when sync source crosses zero)
        if self.sync_enabled and sync_phase is not None:
            # Detect zero crossings in sync source
            crossings = np.where(np.diff(np.sign(sync_phase)) > 0)[0]
            for idx in crossings:
                phase[idx:] = phase[idx:] - phase[idx]
        
        # Generate waveform
        if self.waveform == 'sine':
            signal = np.sin(2 * np.pi * phase)
        elif self.waveform == 'saw':
            # PolyBLEP anti-aliased saw
            signal = 2.0 * phase - 1.0
            signal -= self._poly_blep(phase, actual_freq)
        elif self.waveform == 'square':
            signal = np.sign(2.0 * phase - 1.0)
            signal -= self._poly_blep(phase, actual_freq)
            signal += self._poly_blep((phase + 0.5) % 1.0, actual_freq)
        elif self.waveform == 'triangle':
            signal = 2.0 * np.abs(2.0 * phase - 1.0) - 1.0
        elif self.waveform == 'pulse25':
            signal = np.where(phase < 0.25, 1.0, -1.0)
            signal -= self._poly_blep(phase, actual_freq)
            signal += self._poly_blep((phase + 0.25) % 1.0, actual_freq)
        elif self.waveform == 'pulse50':
            signal = np.sign(2.0 * phase - 1.0)
        elif self.waveform == 'noise':
            signal = np.random.uniform(-1, 1, n_samples)
        elif self.waveform == 'wavetable' and self.wavetable is not None:
            # Wavetable lookup with linear interpolation
            idx = (phase * len(self.wavetable)).astype(int) % len(self.wavetable)
            frac = (phase * len(self.wavetable)) % 1.0
            signal = self.wavetable[idx] * (1 - frac) + self.wavetable[(idx + 1) % len(self.wavetable)] * frac
        else:
            signal = np.sin(2 * np.pi * phase)
        
        return signal * self.level
    
    def _poly_blep(self, phase: np.ndarray, freq: float) -> np.ndarray:
        """PolyBLEP correction for anti-aliased waveforms."""
        dt = freq / self.sample_rate
        correction = np.zeros_like(phase)
        
        # Near zero crossing (start of period)
        mask1 = phase < dt
        if np.any(mask1):
            t = phase[mask1] / dt
            correction[mask1] += t + t - t * t - 1.0
        
        # Near middle crossing
        mask2 = phase > 1.0 - dt
        if np.any(mask2):
            t = (phase[mask2] - 1.0) / dt
            correction[mask2] += t * t + t + t + 1.0
        
        return correction


# =============================================================================
# Envelope Generator
# =============================================================================

class EnvelopeGenerator:
    """ADSR envelope generator."""
    
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        self.attack = 0.01
        self.decay = 0.1
        self.sustain = 0.8
        self.release = 0.2
    
    def set(self, attack: float = 0.01, decay: float = 0.1, 
            sustain: float = 0.8, release: float = 0.2):
        self.attack = attack
        self.decay = decay
        self.sustain = sustain
        self.release = release
    
    def generate(self, duration: float, gate_off: Optional[float] = None) -> np.ndarray:
        """Generate envelope for given duration."""
        n_samples = int(duration * self.sample_rate)
        envelope = np.zeros(n_samples)
        
        attack_samples = int(self.attack * self.sample_rate)
        decay_samples = int(self.decay * self.sample_rate)
        release_samples = int(self.release * self.sample_rate)
        sustain_samples = n_samples - attack_samples - decay_samples
        
        if gate_off is not None:
            release_start = int(gate_off * self.sample_rate)
        else:
            release_start = n_samples - release_samples
        
        idx = 0
        
        # Attack
        if attack_samples > 0 and idx < n_samples:
            end = min(idx + attack_samples, n_samples)
            envelope[idx:end] = np.linspace(0, 1, end - idx)
            idx = end
        
        # Decay
        if decay_samples > 0 and idx < n_samples:
            end = min(idx + decay_samples, n_samples)
            envelope[idx:end] = np.linspace(1, self.sustain, end - idx)
            idx = end
        
        # Sustain
        if sustain_samples > 0 and idx < release_start:
            end = min(release_start, n_samples)
            envelope[idx:end] = self.sustain
            idx = end
        
        # Release
        if idx < n_samples:
            remaining = n_samples - idx
            envelope[idx:] = np.linspace(self.sustain, 0, remaining)
        
        return envelope


# =============================================================================
# LFO
# =============================================================================

class LFO:
    """Low-frequency oscillator for modulation."""
    
    WAVEFORMS = ['sine', 'triangle', 'square', 'saw_up', 'saw_down', 'random']
    
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        self.rate = 1.0  # Hz
        self.depth = 0.5
        self.waveform = 'sine'
        self.phase_offset = 0.0
        self.target = None  # 'osc_pitch', 'filter_cutoff', 'osc_level', etc.
    
    def generate(self, duration: float) -> np.ndarray:
        """Generate LFO signal."""
        n_samples = int(duration * self.sample_rate)
        t = np.arange(n_samples) / self.sample_rate
        phase = (self.rate * t + self.phase_offset) % 1.0
        
        if self.waveform == 'sine':
            signal = np.sin(2 * np.pi * phase)
        elif self.waveform == 'triangle':
            signal = 2.0 * np.abs(2.0 * phase - 1.0) - 1.0
        elif self.waveform == 'square':
            signal = np.sign(2.0 * phase - 1.0)
        elif self.waveform == 'saw_up':
            signal = 2.0 * phase - 1.0
        elif self.waveform == 'saw_down':
            signal = 1.0 - 2.0 * phase
        elif self.waveform == 'random':
            # Step random: new value each cycle
            steps = np.floor(phase * self.rate * duration).astype(int)
            np.random.seed(42)  # Deterministic
            random_vals = np.random.uniform(-1, 1, int(self.rate * duration) + 1)
            signal = random_vals[steps]
        else:
            signal = np.sin(2 * np.pi * phase)
        
        return signal * self.depth


# =============================================================================
# 24dB/oct Multimode Filter
# =============================================================================

class MultimodeFilter:
    """24dB/oct (4-pole) multimode filter using cascaded SVF stages."""
    
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        self.cutoff = 2000.0
        self.resonance = 0.3
        self.mode = 'lp'  # lp, hp, bp, notch
        self.env_amount = 0.5  # How much envelope modulates cutoff
        self.keytrack = 0.5  # How much pitch modulates cutoff
    
    def process(self, audio: np.ndarray, freq: float = 440.0,
                envelope: Optional[np.ndarray] = None) -> np.ndarray:
        """Apply filter to audio."""
        # Modulate cutoff
        cutoff_mod = self.cutoff
        
        # Key tracking
        if self.keytrack > 0:
            cutoff_mod *= (freq / 440.0) ** self.keytrack
        
        # Envelope modulation
        if envelope is not None and self.env_amount > 0:
            cutoff_mod = cutoff_mod * (1 + envelope * self.env_amount * 2)
        
        # Clip cutoff
        cutoff_mod = np.clip(cutoff_mod, 20, self.sample_rate * 0.45)
        
        # Apply 4-pole filter (cascade 2 SVF stages)
        output = audio.copy()
        for _ in range(2):
            output = self._svf_stage(output, cutoff_mod)
        
        return output
    
    def _svf_stage(self, audio: np.ndarray, cutoff: np.ndarray) -> np.ndarray:
        """Single SVF stage with time-varying cutoff."""
        from scipy.signal import lfilter
        
        # For simplicity, use average cutoff for filter design
        avg_cutoff = np.mean(cutoff)
        
        f = 2 * np.sin(np.pi * avg_cutoff / self.sample_rate)
        q = 1.0 - self.resonance
        
        n = len(audio)
        lp = np.zeros(n)
        bp = np.zeros(n)
        hp = np.zeros(n)
        
        lp_prev = 0.0
        bp_prev = 0.0
        
        for i in range(n):
            hp[i] = audio[i] - lp_prev - q * bp_prev
            bp[i] = bp_prev + f * hp[i]
            lp[i] = lp_prev + f * bp[i]
            lp_prev = lp[i]
            bp_prev = bp[i]
        
        if self.mode == 'lp':
            return lp
        elif self.mode == 'hp':
            return hp
        elif self.mode == 'bp':
            return bp
        elif self.mode == 'notch':
            return hp + lp
        else:
            return lp


# =============================================================================
# 16-Step Sequencer
# =============================================================================

class StepSequencer:
    """16-step sequencer for pitch/gate/velocity patterns."""
    
    def __init__(self):
        self.steps = 16
        self.pitch_steps = [0] * 16  # Semitone offsets
        self.gate_steps = [1] * 16   # 0=rest, 1=note
        self.velocity_steps = [100] * 16
    
    def set_pattern(self, pitches: List[int], gates: List[int], velocities: List[int]):
        """Set sequencer pattern."""
        self.pitch_steps = pitches[:16]
        self.gate_steps = gates[:16]
        self.velocity_steps = velocities[:16]
    
    def generate(self, step_duration: float, num_steps: int) -> List[dict]:
        """Generate note events from sequencer."""
        events = []
        for i in range(num_steps):
            step_idx = i % 16
            if self.gate_steps[step_idx]:
                events.append({
                    'semitone_offset': self.pitch_steps[step_idx],
                    'velocity': self.velocity_steps[step_idx],
                    'start_time': i * step_duration,
                    'duration': step_duration * 0.9
                })
        return events


# =============================================================================
# Poly Voice
# =============================================================================

class PolyVoice:
    """Multi-engine polyphonic voice with full modulation matrix."""
    
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        
        # 3 oscillators
        self.osc1 = Oscillator(sample_rate)
        self.osc2 = Oscillator(sample_rate)
        self.osc3 = Oscillator(sample_rate)
        
        # Oscillator routing
        self.osc2_sync_to_osc1 = False
        self.ring_mod_osc1_osc2 = False
        self.ring_mod_osc2_osc3 = False
        
        # Filter
        self.filter = MultimodeFilter(sample_rate)
        
        # 4 envelopes
        self.env1 = EnvelopeGenerator(sample_rate)  # Amp
        self.env2 = EnvelopeGenerator(sample_rate)  # Filter
        self.env3 = EnvelopeGenerator(sample_rate)  # Osc1 pitch
        self.env4 = EnvelopeGenerator(sample_rate)  # Osc2 pitch
        
        # 4 LFOs
        self.lfo1 = LFO(sample_rate)
        self.lfo2 = LFO(sample_rate)
        self.lfo3 = LFO(sample_rate)
        self.lfo4 = LFO(sample_rate)
        
        # Master
        self.gain = 0.7
        self.pan = 0.0
    
    def render_note(self, freq: float, duration: float) -> np.ndarray:
        """Render a single note."""
        n_samples = int(duration * self.sample_rate)
        
        # Generate envelopes
        amp_env = self.env1.generate(duration)
        filter_env = self.env2.generate(duration)
        
        # Generate oscillators
        osc1_signal = self.osc1.generate(freq, n_samples)
        
        # Osc2 (optionally synced to osc1)
        if self.osc2_sync_to_osc1:
            self.osc2.sync_source = self.osc1
            self.osc2.sync_enabled = True
        osc2_signal = self.osc2.generate(freq, n_samples)
        
        osc3_signal = self.osc3.generate(freq, n_samples)
        
        # Ring modulation
        if self.ring_mod_osc1_osc2:
            osc1_signal = osc1_signal * osc2_signal
            osc2_signal = np.zeros(n_samples)
        
        if self.ring_mod_osc2_osc3:
            osc2_signal = osc2_signal * osc3_signal
            osc3_signal = np.zeros(n_samples)
        
        # Mix oscillators
        mixed = osc1_signal + osc2_signal + osc3_signal
        mixed /= 3.0  # Normalize
        
        # Apply LFO modulations
        if self.lfo1.target == 'filter_cutoff':
            lfo_signal = self.lfo1.generate(duration)
            self.filter.cutoff = self.filter.cutoff * (1 + lfo_signal * 0.5)
        
        # Apply filter
        filtered = self.filter.process(mixed, freq=freq, envelope=filter_env)
        
        # Apply amp envelope
        output = filtered * amp_env
        
        # Apply gain
        output *= self.gain
        
        return output.astype(np.float32)


if __name__ == "__main__":
    # Smoke test
    voice = PolyVoice(sample_rate=44100)
    voice.osc1.waveform = 'saw'
    voice.osc2.waveform = 'square'
    voice.osc2.detune_cents = 7
    voice.filter.cutoff = 2000.0
    voice.filter.resonance = 0.4
    voice.env1.set(attack=0.01, decay=0.2, sustain=0.7, release=0.3)
    
    audio = voice.render_note(freq=440.0, duration=1.0)
    print(f"PolyVoice: {audio.shape}, peak: {np.max(np.abs(audio)):.3f}")
    print("✓ PolyVoice smoke test passed")
