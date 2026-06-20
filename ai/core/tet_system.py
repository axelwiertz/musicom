"""
12-Tone Equal Temperament (12TET) System Module.

This module provides fundamental music theory constructs based on 12-tone equal temperament,
including pitch classes, intervals, scales, keys, and time signatures.
"""

from typing import List, Union, Optional, Tuple
from musicom.ai.utils.constants import (
    PITCH_CLASSES,
    ENHARMONIC_MAP,
    INTERVAL_NAMES,
    SCALE_PATTERNS,
    ROMAN_NUMERALS,
    HARMONIC_FUNCTIONS,
)
from musicom.ai.utils.helpers import (
    normalize_pitch_name,
    pitch_class_to_semitone,
    semitone_to_pitch_class,
    transpose_semitones,
    interval_between_pitches,
)
from musicom.ai.utils.validators import (
    validate_pitch_class,
    validate_interval,
    validate_scale_pattern,
    validate_time_signature,
)
from musicom.ai.utils.exceptions import (
    InvalidPitchError,
    InvalidIntervalError,
    ValidationError,
)


class PitchClass:
    """Represents a pitch class in 12-tone equal temperament."""

    def __init__(self, name: Union[str, int]):
        """
        Initialize pitch class from name or MIDI number.

        Args:
            name: Pitch class name (e.g., 'C', 'F#', 'Bb') or MIDI note number

        Raises:
            InvalidPitchError: If pitch class name is invalid
        """
        if isinstance(name, int):
            # Create from MIDI number
            self._semitone = name % 12
            self._name = PITCH_CLASSES[self._semitone]
        else:
            # Create from name
            self._name = normalize_pitch_name(name)
            validate_pitch_class(self._name)
            self._semitone = pitch_class_to_semitone(self._name)

    @property
    def name(self) -> str:
        """Get pitch class name."""
        return self._name

    @property
    def semitone(self) -> int:
        """Get semitone number (0-11)."""
        return self._semitone

    def to_midi_number(self, octave: int = 4) -> int:
        """
        Convert to MIDI note number.

        Args:
            octave: Octave number (default: 4, middle C octave)

        Returns:
            MIDI note number
        """
        return (octave + 1) * 12 + self._semitone

    def transpose(self, semitones: int) -> 'PitchClass':
        """
        Transpose by semitones.

        Args:
            semitones: Number of semitones to transpose

        Returns:
            New transposed PitchClass
        """
        validate_interval(semitones)
        new_semitone = transpose_semitones(self._semitone, semitones)
        return PitchClass(new_semitone)

    def interval_to(self, other: 'PitchClass') -> int:
        """
        Calculate interval in semitones to another pitch class.

        Args:
            other: Target pitch class

        Returns:
            Interval in semitones (0-11)
        """
        return (other.semitone - self._semitone) % 12

    def __str__(self) -> str:
        return self._name

    def __repr__(self) -> str:
        return f"PitchClass('{self._name}')"

    def __eq__(self, other) -> bool:
        if not isinstance(other, PitchClass):
            return False
        return self._semitone == other._semitone

    def __hash__(self) -> int:
        return hash(self._semitone)

    @classmethod
    def from_midi_number(cls, midi_num: int) -> 'PitchClass':
        """
        Create from MIDI note number.

        Args:
            midi_num: MIDI note number

        Returns:
            PitchClass instance
        """
        return cls(midi_num)


class Interval:
    """Represents a musical interval."""

    def __init__(self, semitones: int):
        """
        Initialize interval from semitones.

        Args:
            semitones: Number of semitones

        Raises:
            InvalidIntervalError: If interval is invalid
        """
        validate_interval(semitones)
        self._semitones = semitones

    @property
    def semitones(self) -> int:
        """Get interval in semitones."""
        return self._semitones

    @property
    def name(self) -> str:
        """Get interval name (e.g., 'P5', 'M3')."""
        normalized = abs(self._semitones) % 12
        return INTERVAL_NAMES.get(normalized, f'{normalized}st')

    def invert(self) -> 'Interval':
        """
        Return the interval inversion.

        Returns:
            Inverted interval
        """
        inverted_semitones = 12 - (abs(self._semitones) % 12)
        return Interval(inverted_semitones if self._semitones >= 0 else -inverted_semitones)

    def quality(self) -> str:
        """
        Return interval quality (major, minor, perfect, etc.).

        Returns:
            Interval quality string
        """
        normalized = abs(self._semitones) % 12
        if normalized in [0, 5, 7, 12]:
            return 'Perfect'
        elif normalized in [1, 3, 6, 8, 10]:
            return 'minor'
        elif normalized in [2, 4, 9, 11]:
            return 'Major'
        return 'Unknown'

    def generic_size(self) -> int:
        """
        Return generic interval size (1-8).

        Returns:
            Generic interval size
        """
        # Simplified mapping
        size_map = {0: 1, 1: 2, 2: 2, 3: 3, 4: 3, 5: 4, 6: 4,
                    7: 5, 8: 6, 9: 6, 10: 7, 11: 7, 12: 8}
        return size_map.get(abs(self._semitones) % 13, 1)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"Interval({self._semitones})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Interval):
            return False
        return self._semitones == other._semitones

    def __add__(self, other: 'Interval') -> 'Interval':
        """Add two intervals."""
        return Interval(self._semitones + other._semitones)

    def __sub__(self, other: 'Interval') -> 'Interval':
        """Subtract two intervals."""
        return Interval(self._semitones - other._semitones)


class Scale:
    """Represents a musical scale."""

    def __init__(self, tonic: Union[str, PitchClass], pattern: str = 'major'):
        """
        Initialize scale with tonic and pattern name.

        Args:
            tonic: Tonic pitch class
            pattern: Scale pattern name (e.g., 'major', 'minor', 'dorian')

        Raises:
            ValidationError: If pattern is invalid
        """
        self._tonic = tonic if isinstance(tonic, PitchClass) else PitchClass(tonic)
        validate_scale_pattern(pattern)
        self._pattern = pattern
        self._intervals = SCALE_PATTERNS[pattern]

    @property
    def tonic(self) -> PitchClass:
        """Get tonic pitch class."""
        return self._tonic

    @property
    def pattern(self) -> str:
        """Get scale pattern name."""
        return self._pattern

    def get_pitches(self) -> List[PitchClass]:
        """
        Return all pitch classes in the scale.

        Returns:
            List of PitchClass objects
        """
        return [self._tonic.transpose(interval) for interval in self._intervals]

    def get_degree(self, degree: int) -> PitchClass:
        """
        Get pitch class for scale degree (1-indexed).

        Args:
            degree: Scale degree (1-based)

        Returns:
            PitchClass for the degree

        Raises:
            ValidationError: If degree is out of range
        """
        if not 1 <= degree <= len(self._intervals):
            raise ValidationError(
                f"Scale degree {degree} out of range (1-{len(self._intervals)})"
            )
        return self._tonic.transpose(self._intervals[degree - 1])

    def contains(self, pitch: Union[str, PitchClass]) -> bool:
        """
        Check if pitch class is in scale.

        Args:
            pitch: Pitch class to check

        Returns:
            True if pitch is in scale
        """
        if not isinstance(pitch, PitchClass):
            pitch = PitchClass(pitch)
        scale_pitches = self.get_pitches()
        return any(pitch == sp for sp in scale_pitches)

    def get_chord(self, degree: int, num_notes: int = 3) -> List[PitchClass]:
        """
        Build chord from scale degree.

        Args:
            degree: Scale degree (1-based)
            num_notes: Number of notes in chord (default: 3 for triad)

        Returns:
            List of PitchClass objects forming the chord
        """
        chord_pitches = []
        scale_pitches = self.get_pitches()
        scale_len = len(scale_pitches)

        for i in range(num_notes):
            # Stack thirds (every other scale degree)
            index = (degree - 1 + i * 2) % scale_len
            chord_pitches.append(scale_pitches[index])

        return chord_pitches

    def __str__(self) -> str:
        return f"{self._tonic.name} {self._pattern}"

    def __repr__(self) -> str:
        return f"Scale('{self._tonic.name}', '{self._pattern}')"


class Key:
    """Represents a musical key."""

    def __init__(self, tonic: Union[str, PitchClass], mode: str = 'major'):
        """
        Initialize key with tonic and mode.

        Args:
            tonic: Tonic pitch class
            mode: Mode name (default: 'major')

        Raises:
            ValidationError: If mode is invalid
        """
        self._tonic = tonic if isinstance(tonic, PitchClass) else PitchClass(tonic)

        # Map common mode names to scale patterns
        mode_map = {
            'major': 'major',
            'minor': 'natural_minor',
            'ionian': 'ionian',
            'dorian': 'dorian',
            'phrygian': 'phrygian',
            'lydian': 'lydian',
            'mixolydian': 'mixolydian',
            'aeolian': 'aeolian',
            'locrian': 'locrian',
        }

        if mode not in mode_map:
            raise ValidationError(f"Unknown mode: {mode}")

        self._mode = mode
        self._scale = Scale(self._tonic, mode_map[mode])

    @property
    def tonic(self) -> PitchClass:
        """Get tonic pitch class."""
        return self._tonic

    @property
    def mode(self) -> str:
        """Get mode name."""
        return self._mode

    def get_scale(self) -> Scale:
        """
        Return the scale for this key.

        Returns:
            Scale object
        """
        return self._scale

    def get_relative_key(self) -> 'Key':
        """
        Return relative major/minor key.

        Returns:
            Relative key
        """
        if self._mode == 'major':
            # Relative minor is 3 semitones down
            relative_tonic = self._tonic.transpose(-3)
            return Key(relative_tonic, 'minor')
        elif self._mode == 'minor':
            # Relative major is 3 semitones up
            relative_tonic = self._tonic.transpose(3)
            return Key(relative_tonic, 'major')
        else:
            raise ValidationError(f"Relative key not defined for mode: {self._mode}")

    def get_parallel_key(self) -> 'Key':
        """
        Return parallel major/minor key.

        Returns:
            Parallel key
        """
        if self._mode == 'major':
            return Key(self._tonic, 'minor')
        elif self._mode == 'minor':
            return Key(self._tonic, 'major')
        else:
            raise ValidationError(f"Parallel key not defined for mode: {self._mode}")

    def get_key_signature(self) -> List[PitchClass]:
        """
        Return sharps or flats in key signature.

        Returns:
            List of PitchClass objects representing accidentals
        """
        # Circle of fifths for sharps (starting from C major)
        sharp_keys = ['C', 'G', 'D', 'A', 'E', 'B', 'F#', 'C#']
        sharp_order = ['F#', 'C#', 'G#', 'D#', 'A#', 'E#', 'B#']

        # Circle of fourths for flats (starting from C major)
        flat_keys = ['C', 'F', 'Bb', 'Eb', 'Ab', 'Db', 'Gb', 'Cb']
        flat_order = ['Bb', 'Eb', 'Ab', 'Db', 'Gb', 'Cb', 'Fb']

        tonic_name = self._tonic.name

        # Determine number of sharps or flats
        if tonic_name in sharp_keys:
            num_sharps = sharp_keys.index(tonic_name)
            return [PitchClass(sharp) for sharp in sharp_order[:num_sharps]]
        elif tonic_name in flat_keys:
            num_flats = flat_keys.index(tonic_name)
            return [PitchClass(flat) for flat in flat_order[:num_flats]]
        else:
            return []

    def analyze_chord(self, chord_root: Union[str, PitchClass]) -> str:
        """
        Analyze chord in context of this key (Roman numeral).

        Args:
            chord_root: Root of the chord

        Returns:
            Roman numeral analysis string
        """
        if not isinstance(chord_root, PitchClass):
            chord_root = PitchClass(chord_root)

        scale_pitches = self._scale.get_pitches()

        # Find scale degree
        for i, pitch in enumerate(scale_pitches):
            if pitch == chord_root:
                degree = i + 1
                # Determine if major or minor based on third
                third_interval = self._scale.get_chord(degree, 2)[1].interval_to(chord_root)

                # Major chords: uppercase Roman numerals
                # Minor chords: lowercase Roman numerals
                roman_map = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII']
                roman = roman_map[i]

                if third_interval == 3:  # Minor third
                    roman = roman.lower()

                return roman

        return '?'  # Chord not in key

    def __str__(self) -> str:
        return f"{self._tonic.name} {self._mode}"

    def __repr__(self) -> str:
        return f"Key('{self._tonic.name}', '{self._mode}')"


class TimeSignature:
    """Represents a time signature."""

    def __init__(self, numerator: int = 4, denominator: int = 4):
        """
        Initialize time signature.

        Args:
            numerator: Number of beats per measure
            denominator: Note value that gets one beat

        Raises:
            ValidationError: If time signature is invalid
        """
        validate_time_signature((numerator, denominator))
        self._numerator = numerator
        self._denominator = denominator

    @property
    def numerator(self) -> int:
        """Get numerator (beats per measure)."""
        return self._numerator

    @property
    def denominator(self) -> int:
        """Get denominator (note value per beat)."""
        return self._denominator

    @property
    def beats_per_measure(self) -> int:
        """Get number of beats per measure."""
        return self._numerator

    @property
    def beat_duration(self) -> float:
        """Get duration of one beat in quarter notes."""
        return 4.0 / self._denominator

    def measure_duration(self) -> float:
        """
        Calculate duration of one measure in quarter notes.

        Returns:
            Duration in quarter notes
        """
        return self._numerator * self.beat_duration

    def is_compound(self) -> bool:
        """
        Check if time signature is compound (numerator divisible by 3).

        Returns:
            True if compound meter
        """
        return self._numerator % 3 == 0 and self._numerator > 3

    def is_simple(self) -> bool:
        """
        Check if time signature is simple (not compound).

        Returns:
            True if simple meter
        """
        return not self.is_compound()

    def __str__(self) -> str:
        return f"{self._numerator}/{self._denominator}"

    def __repr__(self) -> str:
        return f"TimeSignature({self._numerator}, {self._denominator})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, TimeSignature):
            return False
        return (self._numerator == other._numerator and
                self._denominator == other._denominator)
