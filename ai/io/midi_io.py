"""
MIDI I/O module using PyPianoroll and Music21.

This module provides MIDI file reading and writing capabilities.
"""

from typing import List, Union, Optional, Tuple
import numpy as np
from pathlib import Path

from musicom.ai.core.structures import Note, Rest, Chord, Phrase, Score, Voice
from musicom.ai.core.tet_system import TimeSignature
from musicom.ai.utils.constants import DEFAULT_TEMPO, DEFAULT_TIME_SIGNATURE
from musicom.ai.utils.exceptions import FileIOError
from musicom.ai.utils.logging_config import get_logger

logger = get_logger('midi_io')


class MIDIReader:
    """Read MIDI files and convert to internal representation."""

    def __init__(self, quantize: bool = False, quantize_resolution: int = 16):
        """
        Initialize MIDI reader.

        Args:
            quantize: Whether to quantize note timings
            quantize_resolution: Quantization resolution (e.g., 16 for sixteenth notes)
        """
        self.quantize = quantize
        self.quantize_resolution = quantize_resolution

    def read(self, filepath: str) -> Union[Phrase, Score]:
        """
        Read MIDI file and return internal representation.

        Args:
            filepath: Path to MIDI file

        Returns:
            Phrase or Score object

        Raises:
            FileIOError: If file cannot be read
        """
        try:
            import music21
        except ImportError:
            raise FileIOError(
                "music21 is required for MIDI reading. Install with: pip install music21"
            )

        try:
            logger.info(f"Reading MIDI file: {filepath}")
            score = music21.converter.parse(filepath)

            # Extract tempo
            tempo = DEFAULT_TEMPO
            for element in score.flatten():
                if isinstance(element, music21.tempo.MetronomeMark):
                    tempo = element.number
                    break

            # Extract time signature
            time_sig = DEFAULT_TIME_SIGNATURE
            for element in score.flatten():
                if isinstance(element, music21.meter.TimeSignature):
                    time_sig = (element.numerator, element.denominator)
                    break

            # Check if multi-part score
            parts = score.parts
            if len(parts) > 1:
                # Multi-voice score
                voices = []
                for i, part in enumerate(parts):
                    phrase = self._parse_part(part, tempo, time_sig)
                    instrument_name = part.partName if hasattr(part, 'partName') else f"Part {i+1}"
                    voice = Voice(phrase, name=instrument_name)
                    voices.append(voice)

                return Score(voices, tempo=tempo, time_signature=time_sig)
            else:
                # Single phrase
                return self._parse_part(parts[0] if parts else score, tempo, time_sig)

        except Exception as e:
            raise FileIOError(f"Failed to read MIDI file {filepath}: {str(e)}") from e

    def _parse_part(
        self,
        part: 'music21.stream.Part',
        tempo: float,
        time_sig: Tuple[int, int]
    ) -> Phrase:
        """
        Parse a Music21 part into a Phrase.

        Args:
            part: Music21 Part object
            tempo: Tempo in BPM
            time_sig: Time signature

        Returns:
            Phrase object
        """
        import music21

        elements = []

        for element in part.flatten().notesAndRests:
            start_time = element.offset

            if isinstance(element, music21.note.Note):
                # Single note
                note = Note(
                    pitch=element.pitch.midi,
                    duration=element.duration.quarterLength,
                    velocity=element.volume.velocity if element.volume.velocity else 64,
                    start_time=start_time
                )
                elements.append(note)

            elif isinstance(element, music21.chord.Chord):
                # Chord
                notes = []
                for pitch in element.pitches:
                    note = Note(
                        pitch=pitch.midi,
                        duration=element.duration.quarterLength,
                        velocity=element.volume.velocity if element.volume.velocity else 64,
                        start_time=start_time
                    )
                    notes.append(note)
                chord = Chord(notes, duration=element.duration.quarterLength)
                elements.append(chord)

            elif isinstance(element, music21.note.Rest):
                # Rest
                rest = Rest(
                    duration=element.duration.quarterLength,
                    start_time=start_time
                )
                elements.append(rest)

        return Phrase(elements, tempo=tempo, time_signature=time_sig)

    def read_to_pianoroll(self, filepath: str) -> np.ndarray:
        """
        Read MIDI file as piano roll array using PyPianoroll.

        Args:
            filepath: Path to MIDI file

        Returns:
            Piano roll array (128 x time_steps)

        Raises:
            FileIOError: If file cannot be read
        """
        try:
            import pypianoroll
        except ImportError:
            raise FileIOError(
                "pypianoroll is required. Install with: pip install pypianoroll"
            )

        try:
            logger.info(f"Reading MIDI file to piano roll: {filepath}")
            multitrack = pypianoroll.read(filepath)

            # Merge all tracks into single piano roll
            if len(multitrack.tracks) > 0:
                # Stack all tracks
                pianoroll = np.zeros((128, multitrack.tracks[0].pianoroll.shape[0]))
                for track in multitrack.tracks:
                    pianoroll = np.maximum(pianoroll, track.pianoroll.T)
                return pianoroll
            else:
                return np.zeros((128, 0))

        except Exception as e:
            raise FileIOError(f"Failed to read MIDI file {filepath}: {str(e)}") from e


class MIDIWriter:
    """Write MIDI files from internal representation."""

    def __init__(
        self,
        tempo: float = DEFAULT_TEMPO,
        time_signature: Tuple[int, int] = DEFAULT_TIME_SIGNATURE
    ):
        """
        Initialize MIDI writer.

        Args:
            tempo: Default tempo in BPM
            time_signature: Default time signature
        """
        self.tempo = tempo
        self.time_signature = time_signature

    def write(
        self,
        element: Union[Phrase, Score, List[Note]],
        filepath: str
    ):
        """
        Write musical element to MIDI file.

        Args:
            element: Phrase, Score, or list of Notes
            filepath: Output file path

        Raises:
            FileIOError: If file cannot be written
        """
        try:
            import music21
        except ImportError:
            raise FileIOError(
                "music21 is required for MIDI writing. Install with: pip install music21"
            )

        try:
            logger.info(f"Writing MIDI file: {filepath}")

            if isinstance(element, Score):
                # Multi-voice score
                score = music21.stream.Score()

                # Add tempo
                score.append(music21.tempo.MetronomeMark(number=element.tempo))

                # Add time signature
                ts = element.time_signature
                score.append(music21.meter.TimeSignature(f"{ts.numerator}/{ts.denominator}"))

                # Add each voice as a part
                for voice in element.voices:
                    part = self._create_part(voice.phrase)
                    if voice.name:
                        part.partName = voice.name
                    score.append(part)

                score.write('midi', fp=filepath)

            elif isinstance(element, Phrase):
                # Single phrase
                part = self._create_part(element)
                part.write('midi', fp=filepath)

            elif isinstance(element, list):
                # List of notes
                phrase = Phrase(element, tempo=self.tempo, time_signature=self.time_signature)
                part = self._create_part(phrase)
                part.write('midi', fp=filepath)

            else:
                raise FileIOError(f"Unsupported element type: {type(element)}")

            logger.info(f"Successfully wrote MIDI file: {filepath}")

        except Exception as e:
            raise FileIOError(f"Failed to write MIDI file {filepath}: {str(e)}") from e

    def _create_part(self, phrase: Phrase) -> 'music21.stream.Part':
        """
        Create Music21 Part from Phrase.

        Args:
            phrase: Phrase object

        Returns:
            Music21 Part object
        """
        import music21

        part = music21.stream.Part()

        # Add tempo
        part.append(music21.tempo.MetronomeMark(number=phrase.tempo))

        # Add time signature
        ts = phrase.time_signature
        part.append(music21.meter.TimeSignature(f"{ts.numerator}/{ts.denominator}"))

        # Add notes and chords
        for element in phrase.elements:
            if isinstance(element, Note):
                m21_note = music21.note.Note(
                    element.get_midi_number(),
                    quarterLength=element.duration
                )
                m21_note.volume.velocity = element.velocity
                m21_note.offset = element.start_time
                part.append(m21_note)

            elif isinstance(element, Chord):
                pitches = [note.get_midi_number() for note in element.notes]
                m21_chord = music21.chord.Chord(
                    pitches,
                    quarterLength=element.duration
                )
                if element.notes:
                    m21_chord.volume.velocity = element.notes[0].velocity
                m21_chord.offset = element.notes[0].start_time if element.notes else 0
                part.append(m21_chord)

            elif isinstance(element, Rest):
                m21_rest = music21.note.Rest(quarterLength=element.duration)
                m21_rest.offset = element.start_time
                part.append(m21_rest)

        return part

    def write_from_pianoroll(
        self,
        pianoroll: np.ndarray,
        filepath: str,
        tempo: Optional[float] = None
    ):
        """
        Write piano roll array to MIDI file using PyPianoroll.

        Args:
            pianoroll: Piano roll array (128 x time_steps)
            filepath: Output file path
            tempo: Optional tempo (uses default if not specified)

        Raises:
            FileIOError: If file cannot be written
        """
        try:
            import pypianoroll
        except ImportError:
            raise FileIOError(
                "pypianoroll is required. Install with: pip install pypianoroll"
            )

        try:
            logger.info(f"Writing piano roll to MIDI file: {filepath}")

            # Create track
            track = pypianoroll.Track(
                pianoroll=pianoroll.T,  # PyPianoroll expects (time_steps x 128)
                program=0,  # Acoustic Grand Piano
                is_drum=False
            )

            # Create multitrack
            multitrack = pypianoroll.Multitrack(
                tracks=[track],
                tempo=np.array([tempo or self.tempo]),
                resolution=24  # Ticks per quarter note
            )

            # Write to file
            pypianoroll.write(filepath, multitrack)

            logger.info(f"Successfully wrote MIDI file: {filepath}")

        except Exception as e:
            raise FileIOError(f"Failed to write MIDI file {filepath}: {str(e)}") from e
