"""Chroma feature extraction and chord recognition using Librosa.

Extracts chroma features and recognizes chord progressions from audio.
"""

from typing import List, Tuple, Optional
import numpy as np


class ChromaExtractor:
    """Extract chroma features and recognize chords."""

    def __init__(self, sample_rate: int = 22050, hop_length: int = 512):
        """
        Initialize chroma extractor.

        Args:
            sample_rate: Audio sample rate
            hop_length: Hop length for analysis
        """
        self.sample_rate = sample_rate
        self.hop_length = hop_length

    def extract_chroma(self, audio_path: str) -> np.ndarray:
        """
        Extract chroma features from audio.

        Args:
            audio_path: Path to audio file

        Returns:
            Chroma feature array (12 x time_frames)

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

        # Extract chroma
        chroma = librosa.feature.chroma_cqt(
            y=y,
            sr=sr,
            hop_length=self.hop_length
        )

        return chroma

    def extract_chords(
        self,
        audio_path: str,
        chord_vocabulary: Optional[List[str]] = None
    ) -> List[Tuple[float, str]]:
        """
        Extract chord sequence with timestamps.

        Args:
            audio_path: Path to audio file
            chord_vocabulary: Optional list of chord symbols to recognize

        Returns:
            List of (time, chord_symbol) tuples

        Raises:
            ImportError: If librosa is not available
        """
        try:
            import librosa
        except ImportError:
            raise ImportError(
                "librosa is required. Install with: pip install librosa"
            )

        # Extract chroma
        chroma = self.extract_chroma(audio_path)

        # Simple chord recognition based on chroma peaks
        chords = []
        pitch_classes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

        for frame_idx in range(chroma.shape[1]):
            frame = chroma[:, frame_idx]

            # Find dominant pitch classes (threshold)
            threshold = np.mean(frame) + np.std(frame)
            active_pcs = [pitch_classes[i] for i, val in enumerate(frame) if val > threshold]

            if active_pcs:
                # Simple chord naming (just use root for now)
                chord_symbol = active_pcs[0]  # Use strongest pitch class as root

                # Determine quality based on active pitch classes
                if len(active_pcs) >= 3:
                    chord_symbol += 'maj'  # Simplified

                time = librosa.frames_to_time(frame_idx, sr=self.sample_rate, hop_length=self.hop_length)
                chords.append((time, chord_symbol))

        return chords


if __name__ == "__main__":
    extractor = ChromaExtractor()
    print("ChromaExtractor ready. Call extract_chroma(audio_path) or extract_chords(audio_path).")
