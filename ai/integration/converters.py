"""
Library integration converters.

This module provides converters between musicom_ai internal format and external libraries.
"""

from typing import List, Union, Any
import numpy as np

from musicom.ai.core.structures import Note, Chord, Phrase
from musicom.ai.core.tet_system import PitchClass
from musicom.ai.utils.exceptions import ConversionError
from musicom.ai.utils.logging_config import get_logger

logger = get_logger('converters')


class Music21Converter:
    """Convert between musicom_ai and Music21 formats."""

    @staticmethod
    def note_to_music21(note: Note) -> 'music21.note.Note':
        """
        Convert musicom_ai Note to Music21 Note.

        Args:
            note: musicom_ai Note object

        Returns:
            Music21 Note object
        """
        try:
            import music21
        except ImportError:
            raise ConversionError("music21 is required. Install with: pip install music21")

        m21_note = music21.note.Note(note.get_midi_number())
        m21_note.duration.quarterLength = note.duration
        m21_note.volume.velocity = note.velocity
        m21_note.offset = note.start_time

        return m21_note

    @staticmethod
    def note_from_music21(m21_note: 'music21.note.Note') -> Note:
        """
        Convert Music21 Note to musicom_ai Note.

        Args:
            m21_note: Music21 Note object

        Returns:
            musicom_ai Note object
        """
        return Note(
            pitch=m21_note.pitch.midi,
            duration=m21_note.duration.quarterLength,
            velocity=m21_note.volume.velocity if m21_note.volume.velocity else 64,
            start_time=m21_note.offset
        )

    @staticmethod
    def chord_to_music21(chord: Chord) -> 'music21.chord.Chord':
        """
        Convert musicom_ai Chord to Music21 Chord.

        Args:
            chord: musicom_ai Chord object

        Returns:
            Music21 Chord object
        """
        try:
            import music21
        except ImportError:
            raise ConversionError("music21 is required. Install with: pip install music21")

        pitches = [note.get_midi_number() for note in chord.notes]
        m21_chord = music21.chord.Chord(pitches)
        m21_chord.duration.quarterLength = chord.duration

        if chord.notes:
            m21_chord.volume.velocity = chord.notes[0].velocity

        return m21_chord

    @staticmethod
    def chord_from_music21(m21_chord: 'music21.chord.Chord') -> Chord:
        """
        Convert Music21 Chord to musicom_ai Chord.

        Args:
            m21_chord: Music21 Chord object

        Returns:
            musicom_ai Chord object
        """
        notes = []
        for pitch in m21_chord.pitches:
            note = Note(
                pitch=pitch.midi,
                duration=m21_chord.duration.quarterLength,
                velocity=m21_chord.volume.velocity if m21_chord.volume.velocity else 64
            )
            notes.append(note)

        return Chord(notes, m21_chord.duration.quarterLength)


class MusicPyConverter:
    """Convert between musicom_ai and MusicPy formats."""

    @staticmethod
    def note_to_musicpy(note: Note) -> 'musicpy.note':
        """
        Convert musicom_ai Note to MusicPy note.

        Args:
            note: musicom_ai Note object

        Returns:
            MusicPy note object
        """
        try:
            import musicpy
        except ImportError:
            raise ConversionError("musicpy is required. Install with: pip install musicpy")

        # Convert MIDI number to note name
        pitch_name = f"{note.pitch_class.name}{note.octave}"

        return musicpy.note(
            pitch_name,
            duration=note.duration,
            volume=note.velocity
        )

    @staticmethod
    def note_from_musicpy(mp_note: 'musicpy.note') -> Note:
        """
        Convert MusicPy note to musicom_ai Note.

        Args:
            mp_note: MusicPy note object

        Returns:
            musicom_ai Note object
        """
        # MusicPy note has name and degree (octave)
        pitch_name = str(mp_note.name)
        octave = mp_note.degree if hasattr(mp_note, 'degree') else 4

        return Note(
            pitch=pitch_name,
            duration=mp_note.duration if hasattr(mp_note, 'duration') else 1.0,
            velocity=mp_note.volume if hasattr(mp_note, 'volume') else 64,
            octave=octave
        )

    @staticmethod
    def chord_to_musicpy(chord: Chord) -> 'musicpy.chord':
        """
        Convert musicom_ai Chord to MusicPy chord.

        Args:
            chord: musicom_ai Chord object

        Returns:
            MusicPy chord object
        """
        try:
            import musicpy
        except ImportError:
            raise ConversionError("musicpy is required. Install with: pip install musicpy")

        # Convert notes to MusicPy format
        mp_notes = [MusicPyConverter.note_to_musicpy(note) for note in chord.notes]

        return musicpy.chord(mp_notes)

    @staticmethod
    def chord_from_musicpy(mp_chord: 'musicpy.chord') -> Chord:
        """
        Convert MusicPy chord to musicom_ai Chord.

        Args:
            mp_chord: MusicPy chord object

        Returns:
            musicom_ai Chord object
        """
        notes = [MusicPyConverter.note_from_musicpy(n) for n in mp_chord.notes]
        return Chord(notes)


class PyPianorollConverter:
    """Convert between musicom_ai and PyPianoroll formats."""

    @staticmethod
    def phrase_to_pianoroll(
        phrase: Phrase,
        resolution: int = 24
    ) -> np.ndarray:
        """
        Convert musicom_ai Phrase to piano roll array.

        Args:
            phrase: musicom_ai Phrase object
            resolution: Time resolution (ticks per quarter note)

        Returns:
            Piano roll array (128 x time_steps)
        """
        logger.info("Converting phrase to piano roll")

        # Calculate total duration in ticks
        total_duration = phrase.get_duration()
        num_time_steps = int(total_duration * resolution)

        # Initialize piano roll
        pianoroll = np.zeros((128, num_time_steps), dtype=np.uint8)

        # Fill in notes
        for element in phrase.elements:
            if isinstance(element, Note):
                midi_num = element.get_midi_number()
                start_tick = int(element.start_time * resolution)
                duration_ticks = int(element.duration * resolution)
                end_tick = min(start_tick + duration_ticks, num_time_steps)

                # Set velocity for duration
                pianoroll[midi_num, start_tick:end_tick] = element.velocity

            elif isinstance(element, Chord):
                for note in element.notes:
                    midi_num = note.get_midi_number()
                    start_tick = int(note.start_time * resolution)
                    duration_ticks = int(note.duration * resolution)
                    end_tick = min(start_tick + duration_ticks, num_time_steps)

                    pianoroll[midi_num, start_tick:end_tick] = note.velocity

        return pianoroll

    @staticmethod
    def pianoroll_to_phrase(
        pianoroll: np.ndarray,
        resolution: int = 24,
        tempo: float = 120.0
    ) -> Phrase:
        """
        Convert piano roll array to musicom_ai Phrase.

        Args:
            pianoroll: Piano roll array (128 x time_steps)
            resolution: Time resolution (ticks per quarter note)
            tempo: Tempo in BPM

        Returns:
            musicom_ai Phrase object
        """
        logger.info("Converting piano roll to phrase")

        notes = []

        # Extract notes from piano roll
        for pitch in range(128):
            active = False
            start_tick = 0
            velocity = 0

            for time_step in range(pianoroll.shape[1]):
                if pianoroll[pitch, time_step] > 0 and not active:
                    # Note onset
                    active = True
                    start_tick = time_step
                    velocity = int(pianoroll[pitch, time_step])

                elif pianoroll[pitch, time_step] == 0 and active:
                    # Note offset
                    active = False
                    duration_ticks = time_step - start_tick
                    duration_beats = duration_ticks / resolution
                    start_time_beats = start_tick / resolution

                    note = Note(
                        pitch=pitch,
                        duration=duration_beats,
                        velocity=velocity,
                        start_time=start_time_beats
                    )
                    notes.append(note)

            # Handle notes that extend to the end
            if active:
                duration_ticks = pianoroll.shape[1] - start_tick
                duration_beats = duration_ticks / resolution
                start_time_beats = start_tick / resolution

                note = Note(
                    pitch=pitch,
                    duration=duration_beats,
                    velocity=velocity,
                    start_time=start_time_beats
                )
                notes.append(note)

        # Sort notes by start time
        notes.sort(key=lambda n: n.start_time)

        return Phrase(notes, tempo=tempo)

    @staticmethod
    def notes_to_pianoroll(
        notes: List[Note],
        resolution: int = 24
    ) -> np.ndarray:
        """
        Convert list of Notes to piano roll array.

        Args:
            notes: List of Note objects
            resolution: Time resolution

        Returns:
            Piano roll array
        """
        if not notes:
            return np.zeros((128, 0), dtype=np.uint8)

        # Calculate duration
        max_time = max(n.start_time + n.duration for n in notes)
        num_time_steps = int(max_time * resolution)

        pianoroll = np.zeros((128, num_time_steps), dtype=np.uint8)

        for note in notes:
            midi_num = note.get_midi_number()
            start_tick = int(note.start_time * resolution)
            duration_ticks = int(note.duration * resolution)
            end_tick = min(start_tick + duration_ticks, num_time_steps)

            pianoroll[midi_num, start_tick:end_tick] = note.velocity

        return pianoroll
