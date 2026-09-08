"""
Digital Waveguide Synthesis - Physical Modeling Demo
SP-033: Digital Waveguide Synthesis (1D/2D Wave Equation)

Technical core: Solves the 1D wave equation using bidirectional delay lines
and scattering junctions. Perfect for strings, acoustic tubes, membranes.
"""

import numpy as np
from structures import MusicUnit, MusicEvent, UnitMatrix, MidiInstrument
from workflows.unitmatrix_composer import UnitMatrixComposer, create_note_unit


class DigitalWaveguideString:
    """1D Digital Waveguide for ideal string (Karplus-Strong++).
    
    The wave equation: d2y/dt2 = c2 d2y/dx2
    Discretized as two delay lines (left/right traveling waves).
    
    Parameters:
        freq: fundamental frequency (Hz)
        fs: sample rate
        decay: exponential decay factor (0-1)
        brightness: bow/pluck position (0-1, lower = brighter)
    """
    
    def __init__(self, freq=440.0, fs=44100, decay=0.995, brightness=0.5):
        self.fs = fs
        self.freq = freq
        self.decay = decay
        
        # Delay length in samples (N = fs / f0)
        self.N = int(fs / freq)
        if self.N < 2:
            self.N = 2
        
        # Two delay lines: left-going and right-going waves
        self.delay_L = np.zeros(self.N + 1)
        self.delay_R = np.zeros(self.N + 1)
        self.ptr = 0
        
        # Loss filter (frequency-dependent damping)
        self.loss = 0.995 + 0.004 * (1.0 - brightness)
        
        # Bow/pluck position index
        self.bow_pos = int(brightness * self.N)
        if self.bow_pos < 1:
            self.bow_pos = 1
        if self.bow_pos >= self.N:
            self.bow_pos = self.N - 1
    
    def excite_pluck(self, amplitude=1.0):
        """Initialize with triangular pluck shape."""
        for i in range(self.N):
            if i <= self.bow_pos:
                val = amplitude * i / self.bow_pos
            else:
                val = amplitude * (self.N - i) / (self.N - self.bow_pos)
            self.delay_L[i] = val * 0.5
            self.delay_R[i] = val * 0.5
    
    def process_sample(self):
        """Process one sample: scattering junction."""
        L_out = self.delay_L[self.ptr]
        R_out = self.delay_R[self.ptr]
        
        bridge_loss = self.loss
        next_ptr = (self.ptr + 1) % self.N
        
        L_in = -R_out * bridge_loss
        R_in = -L_out * bridge_loss
        
        self.delay_L[self.ptr] = L_in
        self.delay_R[self.ptr] = R_in
        
        output = L_out + R_out
        self.ptr = next_ptr
        return output
    
    def render(self, num_samples):
        """Render audio samples."""
        out = np.zeros(num_samples)
        for i in range(num_samples):
            out[i] = self.process_sample()
        return out


def demo():
    """Run waveguide synthesis demos."""
    fs = 44100
    duration = 2.0
    num_samples = int(fs * duration)
    
    print("SP-033: Digital Waveguide Synthesis Demo")
    print("=" * 50)
    
    print("\n1. Plucked A4 string (440 Hz)...")
    string = DigitalWaveguideString(freq=440.0, fs=fs, decay=0.997, brightness=0.3)
    string.excite_pluck(amplitude=1.0)
    plucked = string.render(num_samples)
    print(f"   Rendered {len(plucked)} samples")
    print(f"   Peak: {np.max(np.abs(plucked)):.4f}")
    
    import wave
    data_norm = np.clip(plucked, -1, 1)
    data_16 = (data_norm * 32767).astype(np.int16)
    with wave.open("/opt/data/projects/Research/outputs/digital_waveguide_demo/plucked_string.wav", 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(fs)
        wf.writeframes(data_16.tobytes())
    print("   Saved: plucked_string.wav")
    
    print("\nDone.")


if __name__ == "__main__":
    demo()
