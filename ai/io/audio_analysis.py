"""
Audio analysis module using Librosa.

This module provides audio feature extraction and analysis capabilities.
"""

from typing import List, Tuple, Optional
import numpy as np

from musicom.ai.core.structures import Note, Phrase, Chord
from musicom.ai.core.tet_system import PitchClass
from musicom.ai.utils.constants import DEFAULT_TEMPO
from musicom.ai.utils.exceptions import AudioAnalysisError
from musicom.ai.utils.logging_config import get_logger

logger = get_logger('audio_analysis')


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
            AudioAnalysisError: If analysis fails
        """
        try:
            import librosa
        except ImportError:
            raise AudioAnalysisError(
                "librosa is required for audio analysis. Install with: pip install librosa"
            )

        try:
            logger.info(f"Detecting pitches in: {audio_path}")

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

            logger.info(f"Detected {len(results)} pitch events")
            return results

        except Exception as e:
            raise AudioAnalysisError(f"Pitch detection failed: {str(e)}") from e

    def to_phrase(self, audio_path: str, tempo: float = DEFAULT_TEMPO) -> Phrase:
        """
        Convert audio to Phrase object.

        Args:
            audio_path: Path to audio file
            tempo: Tempo for phrase

        Returns:
            Phrase object

        Raises:
            AudioAnalysisError: If conversion fails
        """
        logger.info(f"Converting audio to phrase: {audio_path}")

        pitches = self.detect(audio_path)

        if not pitches:
            return Phrase([], tempo=tempo)

        notes = []
        for i, (time, freq, conf) in enumerate(pitches):
            # Convert frequency to MIDI number
            midi_num = int(round(69 + 12 * np.log2(freq / 440.0)))

            # Calculate duration (time until next note or end)
            if i < len(pitches) - 1:
                duration = pitches[i + 1][0] - time
            else:
                duration = 0.5  # Default duration for last note

            # Convert time to beats
            start_time_beats = time * tempo / 60.0
            duration_beats = duration * tempo / 60.0

            # Create note with confidence as velocity
            velocity = int(conf * 127)
            note = Note(midi_num, duration_beats, velocity, start_time=start_time_beats)
            notes.append(note)

        return Phrase(notes, tempo=tempo)


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
            AudioAnalysisError: If extraction fails
        """
        try:
            import librosa
        except ImportError:
            raise AudioAnalysisError(
                "librosa is required. Install with: pip install librosa"
            )

        try:
            logger.info(f"Extracting beats from: {audio_path}")

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

            logger.info(f"Detected tempo: {tempo} BPM, {len(beat_times)} beats")
            return (float(tempo), beat_times)

        except Exception as e:
            raise AudioAnalysisError(f"Beat extraction failed: {str(e)}") from e


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
            AudioAnalysisError: If extraction fails
        """
        try:
            import librosa
        except ImportError:
            raise AudioAnalysisError(
                "librosa is required. Install with: pip install librosa"
            )

        try:
            logger.info(f"Extracting chroma from: {audio_path}")

            # Load audio
            y, sr = librosa.load(audio_path, sr=self.sample_rate)

            # Extract chroma
            chroma = librosa.feature.chroma_cqt(
                y=y,
                sr=sr,
                hop_length=self.hop_length
            )

            logger.info(f"Extracted chroma: shape {chroma.shape}")
            return chroma

        except Exception as e:
            raise AudioAnalysisError(f"Chroma extraction failed: {str(e)}") from e

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
            AudioAnalysisError: If extraction fails
        """
        try:
            import librosa
        except ImportError:
            raise AudioAnalysisError(
                "librosa is required. Install with: pip install librosa"
            )

        try:
            logger.info(f"Extracting chords from: {audio_path}")

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

            logger.info(f"Extracted {len(chords)} chord events")
            return chords

        except Exception as e:
            raise AudioAnalysisError(f"Chord extraction failed: {str(e)}") from e


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
            AudioAnalysisError: If detection fails
        """
        try:
            import librosa
        except ImportError:
            raise AudioAnalysisError(
                "librosa is required. Install with: pip install librosa"
            )

        try:
            logger.info(f"Detecting onsets in: {audio_path}")

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

            logger.info(f"Detected {len(onset_times)} onsets")
            return onset_times

        except Exception as e:
            raise AudioAnalysisError(f"Onset detection failed: {str(e)}") from e
