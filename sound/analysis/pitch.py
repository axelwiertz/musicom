"""Pitch detection from audio using Librosa.

Extracts pitch events (time, frequency, confidence) from audio files.
"""

from typing import List, Tuple
import numpy as np


class PitchDetector:
    """Detect pitches from audio using Librosa."""

    def __init__(
        self,
        sample_rate: int = 22050,
        hop_length: int = 512,
        fmin: float = 65.0,
        fmax: float = 2093.0
    ):
        """
        Initialize pitch detector.

        Args:
            sample_rate: Audio sample rate
            hop_length: Hop length for analysis
            fmin: Minimum frequency (Hz)
            fmax: Maximum frequency (Hz)
        """
        self.sample_rate = sample_rate
        self.hop_length = hop_length
        self.fmin = fmin
        self.fmax = fmax

    def detect(self, audio_path: str) -> List[Tuple[float, float, float]]:
        """
        Detect pitches and return (time, frequency, confidence) tuples.

        Args:
            audio_path: Path to audio file

        Returns:
            List of (time, frequency, confidence) tuples

        Raises:
            ImportError: If librosa is not available
        """
        try:
            import librosa
        except ImportError:
            raise ImportError(
                "librosa is required for pitch detection. Install with: pip install librosa"
            )

        # Load audio
        y, sr = librosa.load(audio_path, sr=self.sample_rate)

        # Pitch detection using pyin
        f0, voiced_flag, voiced_probs = librosa.pyin(
            y,
            fmin=self.fmin,
            fmax=self.fmax,
            sr=sr,
            hop_length=self.hop_length
        )

        # Convert to time, frequency, confidence tuples
        results = []
        for i, (freq, voiced, conf) in enumerate(zip(f0, voiced_flag, voiced_probs)):
            if voiced and not np.isnan(freq):
                time = librosa.frames_to_time(i, sr=sr, hop_length=self.hop_length)
                results.append((time, freq, conf))

        return results

    def to_midi_events(self, audio_path: str) -> List[Tuple[float, int, int]]:
        """
        Detect pitches and convert to MIDI note events.

        Args:
            audio_path: Path to audio file

        Returns:
            List of (time_seconds, midi_note, velocity) tuples
        """
        pitches = self.detect(audio_path)
        
        events = []
        for i, (time, freq, conf) in enumerate(pitches):
            # Convert frequency to MIDI number
            midi_num = int(round(69 + 12 * np.log2(freq / 440.0)))
            
            # Calculate duration (time until next note or end)
            if i < len(pitches) - 1:
                duration = pitches[i + 1][0] - time
            else:
                duration = 0.5  # Default duration for last note
            
            # Convert confidence to velocity
            velocity = int(conf * 127)
            events.append((time, midi_num, velocity))
        
        return events


if __name__ == "__main__":
    detector = PitchDetector()
    print("PitchDetector ready. Call detect(audio_path) to use.")
