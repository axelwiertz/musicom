"""
MusicXML I/O module using Music21.

This module provides MusicXML file reading and writing capabilities.
"""

from typing import Union, Optional
from pathlib import Path

from musicom.ai.core.structures import Note, Chord, Phrase, Score, Voice
from musicom.ai.core.tet_system import Key
from musicom.ai.utils.constants import DEFAULT_TEMPO, DEFAULT_TIME_SIGNATURE
from musicom.ai.utils.exceptions import FileIOError
from musicom.ai.utils.logging_config import get_logger

logger = get_logger('musicxml_io')


class MusicXMLReader:
    """Read MusicXML files and convert to internal representation."""

    def __init__(self):
        """Initialize MusicXML reader."""
        pass

    def read(self, filepath: str) -> Union[Phrase, Score]:
        """
        Read MusicXML file and return internal representation.

        Args:
            filepath: Path to MusicXML file

        Returns:
            Phrase or Score object

        Raises:
            FileIOError: If file cannot be read
        """
        try:
            import music21
        except ImportError:
            raise FileIOError(
                "music21 is required for MusicXML reading. Install with: pip install music21"
            )

        try:
            logger.info(f"Reading MusicXML file: {filepath}")
            score = music21.converter.parse(filepath)

            # Extract metadata
            tempo = DEFAULT_TEMPO
            for element in score.flatten():
                if isinstance(element, music21.tempo.MetronomeMark):
                    tempo = element.number
                    break

            time_sig = DEFAULT_TIME_SIGNATURE
            for element in score.flatten():
                if isinstance(element, music21.meter.TimeSignature):
                    time_sig = (element.numerator, element.denominator)
                    break

            # Extract key
            key = None
            for element in score.flatten():
                if isinstance(element, music21.key.Key):
                    key = Key(element.tonic.name, element.mode)
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

                title = score.metadata.title if score.metadata else None
                composer = score.metadata.composer if score.metadata else None

                return Score(
                    voices,
                    title=title,
                    composer=composer,
                    tempo=tempo,
                    time_signature=time_sig,
                    key=key
                )
            else:
                # Single phrase
                return self._parse_part(parts[0] if parts else score, tempo, time_sig)

        except Exception as e:
            raise FileIOError(f"Failed to read MusicXML file {filepath}: {str(e)}") from e

    def _parse_part(self, part, tempo, time_sig):
        """Parse Music21 part into Phrase."""
        import music21

        elements = []

        for element in part.flatten().notesAndRests:
            start_time = element.offset

            if isinstance(element, music21.note.Note):
                note = Note(
                    pitch=element.pitch.midi,
                    duration=element.duration.quarterLength,
                    velocity=element.volume.velocity if element.volume.velocity else 64,
                    start_time=start_time
                )
                elements.append(note)

            elif isinstance(element, music21.chord.Chord):
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

        return Phrase(elements, tempo=tempo, time_signature=time_sig)


class MusicXMLWriter:
    """Write MusicXML files from internal representation."""

    def __init__(
        self,
        tempo: float = DEFAULT_TEMPO,
        time_signature: tuple = DEFAULT_TIME_SIGNATURE
    ):
        """
        Initialize MusicXML writer.

        Args:
            tempo: Default tempo in BPM
            time_signature: Default time signature
        """
        self.tempo = tempo
        self.time_signature = time_signature

    def write(
        self,
        element: Union[Phrase, Score],
        filepath: str,
        title: Optional[str] = None,
        composer: Optional[str] = None
    ):
        """
        Write musical element to MusicXML file.

        Args:
            element: Phrase or Score to write
            filepath: Output file path
            title: Optional title
            composer: Optional composer name

        Raises:
            FileIOError: If file cannot be written
        """
        try:
            import music21
        except ImportError:
            raise FileIOError(
                "music21 is required for MusicXML writing. Install with: pip install music21"
            )

        try:
            logger.info(f"Writing MusicXML file: {filepath}")

            if isinstance(element, Score):
                # Multi-voice score
                score = music21.stream.Score()

                # Add metadata
                if title or element.title:
                    score.metadata = music21.metadata.Metadata()
                    score.metadata.title = title or element.title
                    if composer or element.composer:
                        score.metadata.composer = composer or element.composer

                # Add tempo
                score.append(music21.tempo.MetronomeMark(number=element.tempo))

                # Add time signature
                ts = element.time_signature
                score.append(music21.meter.TimeSignature(f"{ts.numerator}/{ts.denominator}"))

                # Add key if available
                if element.key:
                    score.append(music21.key.Key(element.key.tonic.name, element.key.mode))

                # Add each voice as a part
                for voice in element.voices:
                    part = self._create_part(voice.phrase)
                    if voice.name:
                        part.partName = voice.name
                    score.append(part)

                score.write('musicxml', fp=filepath)

            elif isinstance(element, Phrase):
                # Single phrase
                part = self._create_part(element)

                # Add metadata if provided
                if title or composer:
                    part.metadata = music21.metadata.Metadata()
                    if title:
                        part.metadata.title = title
                    if composer:
                        part.metadata.composer = composer

                part.write('musicxml', fp=filepath)

            logger.info(f"Successfully wrote MusicXML file: {filepath}")

        except Exception as e:
            raise FileIOError(f"Failed to write MusicXML file {filepath}: {str(e)}") from e

    def _create_part(self, phrase: Phrase):
        """Create Music21 Part from Phrase."""
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
                    m21_chord.offset = element.notes[0].start_time
                part.append(m21_chord)

        return part
