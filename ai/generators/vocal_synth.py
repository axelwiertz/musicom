"""Low-memory formant vocal guide synthesizer (Missing-Link Area 1).

Formant-filtered subtractive synthesis. Produces guide vocals carrying synthetic
vowels without heavy DiffSinger RAM. Headless-safe; falls back to a plain sine
carrier if scipy signal filtering is unavailable.
"""
import numpy as np

try:
    import scipy.signal as signal
    from scipy.io import wavfile
    _SCIPY = True
except ImportError:          # pragma: no cover - fallback path
    _SCIPY = False


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
        """Generates a glottal-pulse-like source (saw+noise); sine fallback if no scipy."""
        t = np.linspace(0, duration, int(self.sample_rate * duration), endpoint=False)
        if _SCIPY:
            saw = signal.sawtooth(2 * np.pi * frequency * t, width=0.1)
            noise = np.random.normal(0, 0.005, size=len(t))
            carrier = saw + noise
        else:
            # Fallback: sine + a couple of harmonics to keep it buzzy-ish.
            carrier = (np.sin(2 * np.pi * frequency * t)
                       + 0.3 * np.sin(2 * np.pi * 2 * frequency * t)
                       + 0.15 * np.sin(2 * np.pi * 3 * frequency * t))

        env = np.ones_like(t)
        attack_len = int(min(len(t) // 10, self.sample_rate * 0.05))
        decay_len = int(min(len(t) // 10, self.sample_rate * 0.05))
        if attack_len > 0:
            env[:attack_len] = np.linspace(0, 1, attack_len)
        if decay_len > 0:
            env[-decay_len:] = np.linspace(1, 0, decay_len)

        return carrier * env * volume

    def apply_formant_filter(self, signal_data: np.ndarray, vowel: str) -> np.ndarray:
        """Applies resonant bandpass filters matching vowel formants (no-op without scipy)."""
        if not _SCIPY:
            # Fallback: return the carrier as-is (no formant shaping available).
            max_val = np.max(np.abs(signal_data))
            return signal_data / max_val if max_val > 0 else signal_data
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

    def _write_wav(self, path: str, audio_float: np.ndarray):
        """Write float [-1,1] audio to 16-bit PCM WAV (scipy or stdlib wave)."""
        audio_i16 = np.clip(audio_float, -1.0, 1.0)
        audio_i16 = (audio_i16 * 32767).astype(np.int16)
        if _SCIPY:
            wavfile.write(path, self.sample_rate, audio_i16)
        else:  # pragma: no cover - fallback path
            import wave
            with wave.open(path, "wb") as w:
                w.setnchannels(1)
                w.setsampwidth(2)
                w.setframerate(self.sample_rate)
                w.writeframes(audio_i16.tobytes())

    def render_syllable(self, frequency: float, duration: float, vowel: str,
                        output_path: str = "vocal_syllable.wav") -> str:
        """Compiles a single syllable of singing vocal and saves it."""
        carrier = self.generate_carrier(frequency, duration)
        vocal = self.apply_formant_filter(carrier, vowel)
        self._write_wav(output_path, vocal)
        print(f"Guide vocal syllable '{vowel}' rendered at {frequency}Hz to {output_path}")
        return output_path

    @staticmethod
    def midi_to_freq(midi_pitch: int) -> float:
        """MIDI note number -> frequency in Hz (A4=69=440Hz)."""
        return 440.0 * (2.0 ** ((midi_pitch - 69) / 12.0))

    def render_melody(self, unit, output_path: str,
                      vowels=None, ticks_per_beat: int = 480, bpm: int = 120) -> str:
        """Render a MusicUnit melody as a monophonic guide vocal WAV.

        Args:
            unit: MusicUnit with a melody (uses each event's pitch + tick span).
            output_path: destination .wav path.
            vowels: optional list of vowels cycled per note (default all 'a').
            ticks_per_beat / bpm: convert ticks -> seconds.
        Returns the output path.
        """
        sec_per_tick = 60.0 / (bpm * ticks_per_beat)
        events = [e for e in unit.events if e.pitch > 0]
        vowels = vowels or ['a']
        total_ticks = unit.len_ticks() if len(unit) else 0
        total_samples = max(1, int(total_ticks * sec_per_tick * self.sample_rate))
        track = np.zeros(total_samples, dtype=np.float64)

        for i, e in enumerate(events):
            dur_ticks = e.end_tick - e.start_tick
            if dur_ticks <= 0:
                continue
            freq = self.midi_to_freq(e.pitch)
            vowel = vowels[i % len(vowels)]
            carrier = self.generate_carrier(freq, dur_ticks * sec_per_tick)
            vocal = self.apply_formant_filter(carrier, vowel)
            start = int(e.start_tick * sec_per_tick * self.sample_rate)
            end = min(start + len(vocal), total_samples)
            track[start:end] += vocal[:end - start]

        peak = np.max(np.abs(track))
        if peak > 0:
            track = track / peak
        self._write_wav(output_path, track)
        print(f"Guide vocal melody ({len(events)} notes) rendered to {output_path}")
        return output_path


if __name__ == "__main__":
    synth = FormantVocalGuide()
    synth.render_syllable(220.0, 1.5, 'a', "test_vocal_a.wav")
    synth.render_syllable(329.63, 1.5, 'e', "test_vocal_e.wav")
