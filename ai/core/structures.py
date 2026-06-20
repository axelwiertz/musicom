"""
Musical data structures module.

This module provides core musical data structures including Note, Rest, Chord,
Phrase, Progression, Voice, and Score.
"""

from typing import List, Union, Optional, Tuple, Dict, Any
from musicom.ai.core.tet_system import PitchClass, Interval, Scale, Key, TimeSignature
from musicom.ai.utils.constants import (
    DEFAULT_VELOCITY,
    DEFAULT_OCTAVE,
    DEFAULT_TEMPO,
    DEFAULT_TIME_SIGNATURE,
    CHORD_QUALITIES,
)
from musicom.ai.utils.helpers import (
    normalize_pitch_name,
    parse_chord_symbol,
    beats_to_seconds,
    seconds_to_beats,
)
from musicom.ai.utils.validators import (
    validate_midi_number,
    validate_velocity,
    validate_duration,
    validate_tempo,
    validate_octave,
)
from musicom.ai.utils.exceptions import (
    InvalidPitchError,
    InvalidDurationError,
    InvalidChordError,
    ValidationError,
)


class Note:
    """Represents a musical note."""

    def __init__(
        self,
        pitch: Union[str, PitchClass, int],
        duration: float,
        velocity: int = DEFAULT_VELOCITY,
        octave: int = DEFAULT_OCTAVE,
        articulation: Optional[str] = None,
        start_time: float = 0.0
    ):
        """
        Initialize note with pitch, duration, and properties.

        Args:
            pitch: Pitch as string, PitchClass, or MIDI number
            duration: Duration in beats
            velocity: MIDI velocity (0-127)
            octave: Octave number (used if pitch is string or PitchClass)
            articulation: Optional articulation marking
            start_time: Start time in beats

        Raises:
            InvalidPitchError: If pitch is invalid
            InvalidDurationError: If duration is invalid
            ValidationError: If velocity is invalid
        """
        # Handle pitch
        if isinstance(pitch, int):
            validate_midi_number(pitch)
            self._midi_number = pitch
            self._pitch_class = PitchClass.from_midi_number(pitch)
            self._octave = (pitch // 12) - 1
        elif isinstance(pitch, PitchClass):
            validate_octave(octave)
            self._pitch_class = pitch
            self._octave = octave
            self._midi_number = pitch.to_midi_number(octave)
        else:
            # String pitch name
            self._pitch_class = PitchClass(pitch)
            validate_octave(octave)
            self._octave = octave
            self._midi_number = self._pitch_class.to_midi_number(octave)

        # Validate and set other properties
        validate_duration(duration)
        validate_velocity(velocity)

        self._duration = duration
        self._velocity = velocity
        self._articulation = articulation
        self._start_time = start_time

    @property
    def pitch_class(self) -> PitchClass:
        """Get pitch class."""
        return self._pitch_class

    @property
    def octave(self) -> int:
        """Get octave number."""
        return self._octave

    @property
    def duration(self) -> float:
        """Get duration in beats."""
        return self._duration

    @property
    def velocity(self) -> int:
        """Get MIDI velocity."""
        return self._velocity

    @property
    def articulation(self) -> Optional[str]:
        """Get articulation marking."""
        return self._articulation

    @property
    def start_time(self) -> float:
        """Get start time in beats."""
        return self._start_time

    @start_time.setter
    def start_time(self, value: float):
        """Set start time in beats."""
        self._start_time = value

    def get_midi_number(self) -> int:
        """
        Get MIDI note number.

        Returns:
            MIDI note number (0-127)
        """
        return self._midi_number

    def transpose(self, semitones: int) -> 'Note':
        """
        Transpose note by semitones.

        Args:
            semitones: Number of semitones to transpose

        Returns:
            New transposed Note
        """
        new_midi = self._midi_number + semitones
        return Note(
            new_midi,
            self._duration,
            self._velocity,
            articulation=self._articulation,
            start_time=self._start_time
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary representation.

        Returns:
            Dictionary with note properties
        """
        return {
            'pitch': self._midi_number,
            'duration': self._duration,
            'velocity': self._velocity,
            'start_time': self._start_time,
            'articulation': self._articulation,
            'pitch_class': str(self._pitch_class),
            'octave': self._octave,
        }

    def __str__(self) -> str:
        return f"{self._pitch_class.name}{self._octave} ({self._duration} beats)"

    def __repr__(self) -> str:
        return f"Note('{self._pitch_class.name}', {self._duration}, octave={self._octave})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Note):
            return False
        return (self._midi_number == other._midi_number and
                abs(self._duration - other._duration) < 0.001)


class Rest:
    """Represents a musical rest (silence)."""

    def __init__(self, duration: float, start_time: float = 0.0):
        """
        Initialize rest with duration.

        Args:
            duration: Duration in beats
            start_time: Start time in beats

        Raises:
            InvalidDurationError: If duration is invalid
        """
        validate_duration(duration)
        self._duration = duration
        self._start_time = start_time

    @property
    def duration(self) -> float:
        """Get duration in beats."""
        return self._duration

    @property
    def start_time(self) -> float:
        """Get start time in beats."""
        return self._start_time

    @start_time.setter
    def start_time(self, value: float):
        """Set start time in beats."""
        self._start_time = value

    def __str__(self) -> str:
        return f"Rest ({self._duration} beats)"

    def __repr__(self) -> str:
        return f"Rest({self._duration})"


class Chord:
    """Represents a musical chord."""

    def __init__(
        self,
        notes: List[Note],
        duration: Optional[float] = None,
        root: Optional[PitchClass] = None
    ):
        """
        Initialize chord from notes.

        Args:
            notes: List of Note objects
            duration: Optional duration (uses first note's duration if not specified)
            root: Optional explicit root pitch class

        Raises:
            InvalidChordError: If chord is invalid
        """
        if not notes:
            raise InvalidChordError("Chord must contain at least one note")

        self._notes = sorted(notes, key=lambda n: n.get_midi_number())
        self._duration = duration if duration is not None else notes[0].duration
        self._root = root if root is not None else self._notes[0].pitch_class

    @property
    def notes(self) -> List[Note]:
        """Get list of notes in chord."""
        return self._notes

    @property
    def duration(self) -> float:
        """Get chord duration."""
        return self._duration

    @property
    def root(self) -> PitchClass:
        """Get chord root."""
        return self._root

    def get_pitch_classes(self) -> List[PitchClass]:
        """
        Get unique pitch classes in chord.

        Returns:
            List of PitchClass objects
        """
        seen = set()
        pitch_classes = []
        for note in self._notes:
            pc = note.pitch_class
            if pc.semitone not in seen:
                seen.add(pc.semitone)
                pitch_classes.append(pc)
        return pitch_classes

    def get_intervals(self) -> List[Interval]:
        """
        Get intervals from root.

        Returns:
            List of Interval objects
        """
        intervals = []
        root_semitone = self._root.semitone
        for pc in self.get_pitch_classes():
            interval_semitones = (pc.semitone - root_semitone) % 12
            intervals.append(Interval(interval_semitones))
        return intervals

    def get_quality(self) -> str:
        """
        Determine chord quality (major, minor, diminished, etc.).

        Returns:
            Chord quality string
        """
        intervals = [i.semitones for i in self.get_intervals()]
        intervals.sort()

        # Match against known chord qualities
        for quality, pattern in CHORD_QUALITIES.items():
            if intervals == sorted(pattern):
                return quality

        return 'unknown'

    def get_inversion(self) -> int:
        """
        Determine chord inversion (0=root position).

        Returns:
            Inversion number
        """
        if not self._notes:
            return 0

        bass_pc = self._notes[0].pitch_class
        pitch_classes = self.get_pitch_classes()

        for i, pc in enumerate(pitch_classes):
            if pc == bass_pc:
                return i

        return 0

    def invert(self, inversion: int = 1) -> 'Chord':
        """
        Return inverted chord.

        Args:
            inversion: Inversion number (1=first inversion, 2=second, etc.)

        Returns:
            New inverted Chord
        """
        if not self._notes or inversion == 0:
            return self

        new_notes = []
        for note in self._notes:
            # Move notes up by octaves based on inversion
            midi = note.get_midi_number()
            pc_index = note.pitch_class.semitone

            # Determine how many octaves to shift
            root_index = self._root.semitone
            relative_position = (pc_index - root_index) % 12

            if relative_position < inversion * 3:  # Rough heuristic
                midi += 12

            new_notes.append(Note(
                midi,
                note.duration,
                note.velocity,
                articulation=note.articulation
            ))

        return Chord(new_notes, self._duration, self._root)

    def transpose(self, semitones: int) -> 'Chord':
        """
        Transpose chord by semitones.

        Args:
            semitones: Number of semitones to transpose

        Returns:
            New transposed Chord
        """
        new_notes = [note.transpose(semitones) for note in self._notes]
        new_root = self._root.transpose(semitones)
        return Chord(new_notes, self._duration, new_root)

    @classmethod
    def from_symbol(cls, symbol: str, duration: float = 1.0, octave: int = 4) -> 'Chord':
        """
        Create chord from symbol (e.g., 'Cmaj7', 'Dm7b5').

        Args:
            symbol: Chord symbol
            duration: Duration in beats
            octave: Base octave for chord

        Returns:
            Chord object
        """
        root_name, quality = parse_chord_symbol(symbol)
        root = PitchClass(root_name)

        if quality not in CHORD_QUALITIES:
            quality = 'major'  # Default to major

        intervals = CHORD_QUALITIES[quality]
        notes = []

        for interval in intervals:
            pitch_class = root.transpose(interval)
            note = Note(pitch_class, duration, octave=octave)
            notes.append(note)

        return cls(notes, duration, root)

    def __str__(self) -> str:
        pitch_names = [n.pitch_class.name for n in self._notes]
        return f"Chord({', '.join(pitch_names)})"

    def __repr__(self) -> str:
        return f"Chord({len(self._notes)} notes, root={self._root.name})"


class Phrase:
    """Represents a musical phrase."""

    def __init__(
        self,
        elements: List[Union[Note, Chord, Rest]],
        tempo: float = DEFAULT_TEMPO,
        time_signature: Tuple[int, int] = DEFAULT_TIME_SIGNATURE
    ):
        """
        Initialize phrase with musical elements.

        Args:
            elements: List of Note, Chord, or Rest objects
            tempo: Tempo in BPM
            time_signature: Time signature as (numerator, denominator)

        Raises:
            ValidationError: If tempo or time signature is invalid
        """
        validate_tempo(tempo)
        self._elements = elements
        self._tempo = tempo
        self._time_signature = TimeSignature(*time_signature)

        # Calculate start times if not set
        current_time = 0.0
        for element in self._elements:
            if element.start_time == 0.0:
                element.start_time = current_time
            current_time = element.start_time + element.duration

    @property
    def elements(self) -> List[Union[Note, Chord, Rest]]:
        """Get list of musical elements."""
        return self._elements

    @property
    def tempo(self) -> float:
        """Get tempo in BPM."""
        return self._tempo

    @property
    def time_signature(self) -> TimeSignature:
        """Get time signature."""
        return self._time_signature

    def get_duration(self) -> float:
        """
        Calculate total duration in beats.

        Returns:
            Total duration in beats
        """
        if not self._elements:
            return 0.0
        return max(e.start_time + e.duration for e in self._elements)

    def get_notes(self) -> List[Note]:
        """
        Get all notes in phrase (expanding chords).

        Returns:
            List of Note objects
        """
        notes = []
        for element in self._elements:
            if isinstance(element, Note):
                notes.append(element)
            elif isinstance(element, Chord):
                notes.extend(element.notes)
        return notes

    def get_contour(self) -> List[int]:
        """
        Return melodic contour as list of directions.

        Returns:
            List of integers: 1 (up), 0 (same), -1 (down)
        """
        notes = [e for e in self._elements if isinstance(e, Note)]
        if len(notes) < 2:
            return []

        contour = []
        for i in range(1, len(notes)):
            prev_midi = notes[i-1].get_midi_number()
            curr_midi = notes[i].get_midi_number()

            if curr_midi > prev_midi:
                contour.append(1)
            elif curr_midi < prev_midi:
                contour.append(-1)
            else:
                contour.append(0)

        return contour

    def get_range(self) -> Tuple[int, int]:
        """
        Return pitch range (lowest, highest MIDI numbers).

        Returns:
            Tuple of (lowest, highest) MIDI numbers
        """
        notes = self.get_notes()
        if not notes:
            return (0, 0)

        midi_numbers = [n.get_midi_number() for n in notes]
        return (min(midi_numbers), max(midi_numbers))

    def transpose(self, semitones: int) -> 'Phrase':
        """
        Transpose entire phrase.

        Args:
            semitones: Number of semitones to transpose

        Returns:
            New transposed Phrase
        """
        new_elements = []
        for element in self._elements:
            if isinstance(element, (Note, Chord)):
                new_elements.append(element.transpose(semitones))
            else:
                new_elements.append(element)

        return Phrase(new_elements, self._tempo, (self._time_signature.numerator, self._time_signature.denominator))

    def __str__(self) -> str:
        return f"Phrase({len(self._elements)} elements, {self.get_duration()} beats)"

    def __repr__(self) -> str:
        return f"Phrase({len(self._elements)} elements)"


class Progression:
    """Represents a harmonic progression."""

    def __init__(
        self,
        chords: List[Chord],
        key: Key,
        roman_numerals: Optional[List[str]] = None
    ):
        """
        Initialize progression with chords and key.

        Args:
            chords: List of Chord objects
            key: Key context
            roman_numerals: Optional list of Roman numeral analyses
        """
        self._chords = chords
        self._key = key
        self._roman_numerals = roman_numerals

    @property
    def chords(self) -> List[Chord]:
        """Get list of chords."""
        return self._chords

    @property
    def key(self) -> Key:
        """Get key context."""
        return self._key

    def analyze(self) -> List[str]:
        """
        Analyze progression and return Roman numerals.

        Returns:
            List of Roman numeral strings
        """
        if self._roman_numerals:
            return self._roman_numerals

        roman_numerals = []
        for chord in self._chords:
            roman = self._key.analyze_chord(chord.root)
            roman_numerals.append(roman)

        return roman_numerals

    def transpose(self, semitones: int) -> 'Progression':
        """
        Transpose entire progression.

        Args:
            semitones: Number of semitones to transpose

        Returns:
            New transposed Progression
        """
        new_chords = [chord.transpose(semitones) for chord in self._chords]
        new_key_tonic = self._key.tonic.transpose(semitones)
        new_key = Key(new_key_tonic, self._key.mode)

        return Progression(new_chords, new_key, self._roman_numerals)

    def __str__(self) -> str:
        analysis = self.analyze()
        return f"Progression in {self._key}: {' - '.join(analysis)}"

    def __repr__(self) -> str:
        return f"Progression({len(self._chords)} chords, key={self._key})"


class Voice:
    """Represents a single melodic line."""

    def __init__(
        self,
        phrase: Phrase,
        name: Optional[str] = None,
        instrument: Optional[str] = None
    ):
        """
        Initialize voice with phrase.

        Args:
            phrase: Phrase object
            name: Optional voice name
            instrument: Optional instrument name
        """
        self._phrase = phrase
        self._name = name
        self._instrument = instrument

    @property
    def phrase(self) -> Phrase:
        """Get phrase."""
        return self._phrase

    @property
    def name(self) -> Optional[str]:
        """Get voice name."""
        return self._name

    @property
    def instrument(self) -> Optional[str]:
        """Get instrument name."""
        return self._instrument

    def __str__(self) -> str:
        name_str = f" ({self._name})" if self._name else ""
        return f"Voice{name_str}: {self._phrase}"

    def __repr__(self) -> str:
        return f"Voice(name='{self._name}')"


class Score:
    """Represents a multi-voice composition."""

    def __init__(
        self,
        voices: List[Voice],
        title: Optional[str] = None,
        composer: Optional[str] = None,
        tempo: float = DEFAULT_TEMPO,
        time_signature: Tuple[int, int] = DEFAULT_TIME_SIGNATURE,
        key: Optional[Key] = None
    ):
        """
        Initialize score with voices and metadata.

        Args:
            voices: List of Voice objects
            title: Optional title
            composer: Optional composer name
            tempo: Tempo in BPM
            time_signature: Time signature
            key: Optional key signature
        """
        self._voices = voices
        self._title = title
        self._composer = composer
        self._tempo = tempo
        self._time_signature = TimeSignature(*time_signature)
        self._key = key

    @property
    def voices(self) -> List[Voice]:
        """Get list of voices."""
        return self._voices

    @property
    def title(self) -> Optional[str]:
        """Get title."""
        return self._title

    @property
    def composer(self) -> Optional[str]:
        """Get composer."""
        return self._composer

    @property
    def tempo(self) -> float:
        """Get tempo."""
        return self._tempo

    @property
    def time_signature(self) -> TimeSignature:
        """Get time signature."""
        return self._time_signature

    @property
    def key(self) -> Optional[Key]:
        """Get key signature."""
        return self._key

    def get_duration(self) -> float:
        """
        Get total duration of score.

        Returns:
            Duration in beats
        """
        if not self._voices:
            return 0.0
        return max(voice.phrase.get_duration() for voice in self._voices)

    def __str__(self) -> str:
        title_str = f'"{self._title}"' if self._title else "Untitled"
        return f"Score {title_str} ({len(self._voices)} voices)"

    def __repr__(self) -> str:
        return f"Score(voices={len(self._voices)}, title='{self._title}')"
