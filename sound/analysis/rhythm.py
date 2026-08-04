"""Beat tracking and onset detection using Librosa.

Extracts tempo, beat times, and note onsets from audio files.
"""

from typing import Tuple
import numpy as np


class BeatTracker:
    """Track beats and tempo from audio."""

    def __init__(self, sample_rate: int = 22050, hop_length: int = 512):
        """
        Initialize beat tracker.

        Args:
            sample_rate: Audio sample rate
            hop_length: Hop length for analysis
        """
        self.sample_rate = sample_rate
        self.hop_length = hop_length

    def extract_beats(self, audio_path: str) -> Tuple[float, np.ndarray]:
        """
        Extract beat times and tempo from audio.

        Args:
            audio_path: Path to audio file

        Returns:
            Tuple of (tempo, beat_times)

        Raises:
            ImportError: If librosa is not available
        """
        try:
            import librosa
        except ImportError:
            raise ImportError(
                "librosa is required. Install with: pip install librosa"
            )

        # Load audio
        y, sr = librosa.load(audio_path, sr=self.sample_rate)

        # Beat tracking
        tempo, beat_frames = librosa.beat.beat_track(
            y=y,
            sr=sr,
            hop_length=self.hop_length
        )

        # Convert frames to time
        beat_times = librosa.frames_to_time(beat_frames, sr=sr, hop_length=self.hop_length)

        return (float(tempo), beat_times)


class OnsetDetector:
    """Detect note onsets from audio."""

    def __init__(self, sample_rate: int = 22050, hop_length: int = 512):
        """
        Initialize onset detector.

        Args:
            sample_rate: Audio sample rate
            hop_length: Hop length for analysis
        """
        self.sample_rate = sample_rate
        self.hop_length = hop_length

    def detect_onsets(self, audio_path: str) -> np.ndarray:
        """
        Detect note onset times.

        Args:
            audio_path: Path to audio file

        Returns:
            Array of onset times in seconds

        Raises:
            ImportError: If librosa is not available
        """
        try:
            import librosa
        except ImportError:
            raise ImportError(
                "librosa is required. Install with: pip install librosa"
            )

        # Load audio
        y, sr = librosa.load(audio_path, sr=self.sample_rate)

        # Onset detection
        onset_frames = librosa.onset.onset_detect(
            y=y,
            sr=sr,
            hop_length=self.hop_length
        )

        # Convert to time
        onset_times = librosa.frames_to_time(onset_frames, sr=sr, hop_length=self.hop_length)

        return onset_times


if __name__ == "__main__":
    tracker = BeatTracker()
    detector = OnsetDetector()
    print("BeatTracker and OnsetDetector ready.")
