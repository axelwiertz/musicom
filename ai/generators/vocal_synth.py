import numpy as np
import scipy.signal as signal
from scipy.io import wavfile
import sys

# Ensure repository path is loaded
sys.path.insert(0, "/opt/data/repos/musicom")

class FormantVocalGuide:
    """
    Formant-filtered additive/subtractive synthesis engine.
    Produces low-memory guide vocal sounds carrying synthetic vowels ('a', 'e', 'i', 'o', 'u')
    without heavy DiffSinger requirements. Works natively in headless environments.
    """
    VOWEL_FORMANTS = {
        'a': [(800, 150), (1200, 250), (2800, 350)],
        'e': [(400, 100), (1600, 200), (2800, 300)],
        'i': [(250, 50),  (2200, 200), (3000, 300)],
        'o': [(450, 80),  (800, 150),  (2800, 300)],
        'u': [(300, 60),  (650, 100),  (2800, 300)]
    }

    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate

    def generate_carrier(self, frequency: float, duration: float, volume: float = 0.5) -> np.ndarray:
        """Generates a rich buzzy glottal pulse train wave to act as the vocal cords fold source."""
        t = np.linspace(0, duration, int(self.sample_rate * duration), endpoint=False)
        # Pulse-like saw wave generator
        saw = signal.sawtooth(2 * np.pi * frequency * t, width=0.1)
        # Add rich harmonics
        noise = np.random.normal(0, 0.005, size=len(t))
        carrier = saw + noise
        
        # Simple amplitude envelope to remove click
        env = np.ones_like(t)
        attack_len = int(min(len(t) // 10, self.sample_rate * 0.05))
        decay_len = int(min(len(t) // 10, self.sample_rate * 0.05))
        
        env[:attack_len] = np.linspace(0, 1, attack_len)
        env[-decay_len:] = np.linspace(1, 0, decay_len)
        
        return carrier * env * volume

    def apply_formant_filter(self, signal_data: np.ndarray, vowel: str) -> np.ndarray:
        """Applies resonant bandpass filters matching vowel formants."""
        if vowel not in self.VOWEL_FORMANTS:
            vowel = 'a'  # Fallback
            
        formants = self.VOWEL_FORMANTS[vowel]
        filtered_vocal = np.zeros_like(signal_data)
        
        for center_freq, band_width in formants:
            # Reconstruct sound with IIR bandpass resonator
            q = center_freq / band_width
            b, a = signal.iirpeak(center_freq, q, fs=self.sample_rate)
            # Parallel addition of formant components
            filtered_vocal += signal.lfilter(b, a, signal_data)
            
        # Normalize amplitude safely
        max_val = np.max(np.abs(filtered_vocal))
        if max_val > 0:
            filtered_vocal = filtered_vocal / max_val
            
        return filtered_vocal

    def render_syllable(self, frequency: float, duration: float, vowel: str, output_path: str = "vocal_syllable.wav"):
        """Compiles a single syllable of singing vocal and saves it."""
        carrier = self.generate_carrier(frequency, duration)
        vocal = self.apply_formant_filter(carrier, vowel)
        
        # Audio convert float32 to int16 format
        audio_i16 = (vocal * 32767).astype(np.int16)
        wavfile.write(output_path, self.sample_rate, audio_i16)
        print(f"Guide vocal syllable '{vowel}' rendered at {frequency}Hz to {output_path}")

if __name__ == "__main__":
    synth = FormantVocalGuide()
    # Test Render: sing fundamental note A3 (220Hz), vowel 'a'
    synth.render_syllable(220.0, 1.5, 'a', "test_vocal_a.wav")
    # Test Render: sing fundamental note E4 (329.63Hz), vowel 'e'
    synth.render_syllable(329.63, 1.5, 'e', "test_vocal_e.wav")
