"""Module for defining musical patterns based on diatonic scales, modes and intervals."""
from typing import Tuple, List
from .base import Base
from .pitch import MusicPitchClass, MusicPitch, Direction
from utilities import sequence_rotations, interval_to_step

"""Diatonic musical patterns: cardinality, intervals, scales, modes, chords"""

class Cardinality:
    # Diatonic patterns: cardinality, intervals, scales, modes, chords
    DYAD = 2
    TRIA = 3
    TETRA = 4
    PENTA = 5
    HEXA = 6
    HEPTA = 7
    OCTA = 8
    NONA = 9
    DECA = 10
    UNDECA = 11
    DODECA = 12

class PatternType:
    SCALE = 0

    MINOR_THIRD = 1
    MAJOR_THIRD = 2
    PERFECT_FOURTH = 3
    TRITONE = 4
    PERFECT_FIFTH = 5
    MINOR_SIXTH = 6
    MAJOR_SIXTH = 7

    DIMINISHED = 1
    MINOR = 2
    MAJOR = 3
    AUGMENTED = 4
    SUS2 = 5
    SUS4 = 6

    MINOR7 = 1
    MAJOR7 = 2
    DOMINANT7 = 3
    MAJOR6 = 4
    MINOR6 = 5
    MINOR7_FLAT5 = 6

    NINTH = 1
    MINOR_NINTH = 2

class PatternMode:
    # 7 modes indices:
    ionian = major = 0
    dorian = 1
    phrygian = 2
    lydian = 3
    mixolydian = 4
    aeolian = minor = 5
    locrian = 6
    mode_names = {ionian:'major',dorian:'dorian',phrygian:'phrygian',
            lydian:'lydian',mixolydian:'mixolydian',aeolian:'minor',locrian:'locrian'}

    mode_names_reverse = {v:k for k,v in mode_names.items()}


class Diatonic:
    # Interval patterns for scales and chords
    # pitch_intervals: tuple of interval steps, e.g. (2,2)
    pattern = {
        Cardinality.DYAD: {
            PatternType.MINOR_THIRD     : (3, 9),
            PatternType.MAJOR_THIRD     : (4, 8),
            PatternType.PERFECT_FOURTH  : (5, 7),
            PatternType.TRITONE         : (6, 6),
            PatternType.PERFECT_FIFTH   : (7, 5),
            PatternType.MINOR_SIXTH     : (8, 4),
            PatternType.MAJOR_SIXTH     : (9, 3),
        },
        # 3 Triad scale Patterns
        Cardinality.TRIA:  {
            PatternType.DIMINISHED: (3, 3, 6),
            PatternType.MINOR: (3, 4, 5),
            PatternType.MAJOR: (4, 3, 5),
            PatternType.AUGMENTED: (4, 4, 4),
            PatternType.SUS2: (2, 5, 5),
            PatternType.SUS4: (5, 2, 5),
        },
        Cardinality.TETRA : {
            PatternType.MINOR7: (3, 4, 3, 2),
            PatternType.MINOR7_FLAT5: (3, 3, 4, 2),
            PatternType.MAJOR7 : (4, 3, 4, 1),
            PatternType.DOMINANT7: (4, 3, 3, 2),
            PatternType.MAJOR6: (4, 3, 2, 3),
            PatternType.MINOR6: (3, 4, 2, 3),
            PatternType.AUGMENTED: (4, 4, 3, 1),
            PatternType.SUS2: (2, 5, 4, 1),
            PatternType.SUS4: (5, 2, 4, 1)
        },
        Cardinality.PENTA: {
            PatternType.SCALE: (2, 2, 3, 2, 3),
        },
        Cardinality.HEPTA: {
            PatternType.SCALE : (2, 2, 1, 2, 2, 2, 1)
        },
        Cardinality.NONA: {},
        Cardinality.DECA: {},
        Cardinality.DODECA: {
            PatternType.SCALE: (1,1,1,1,1,1,1,1,1,1,1,1)
        },
    }
    multicycle_patterns = {
        14: {
            PatternType.NINTH: (4, 3, 3, 4, 10),
            PatternType.MINOR_NINTH: (3, 4, 3, 4, 10)
        }
    }


#TODO: Add methods for pattern manipulation, e.g., inversion, retrograde, etc.
#TODO: Patterns are units?

class MusicPattern(Base):
    """Musical pattern based on diatonic scales, modes, and intervals."""

    def __init__(self,
                 name: str = "Pattern",
                 cardinality: int = None,
                 pattern_type: int = None,
                 mode: int = None,
                 tonic_pitch_class: int = None,
                 tonic_octave: int = 4,
                 ):
        super().__init__(name)
        self._cardinality = cardinality
        self._pattern_type = pattern_type

        self._modes = sequence_rotations(self.pitch_class_intervals)
        self._mode = mode

        # Connect to absolute pitches
        self._pitches = MusicPitch()
        self._modes_pitches = [interval_to_step(m) for m in self._modes]

        self._tonic_pitch_class = tonic_pitch_class
        self._tonic_octave = tonic_octave

    def set_mode_index(self, mode_index: int):
        """Set the current mode by index."""
        if mode_index < 0 or mode_index >= len(self._modes):
            raise ValueError(f"Mode index {mode_index} out of range.")
        self._mode = mode_index

    def set_mode_name(self, mode_name: str):
        """Set the current mode by name."""
        if mode_name not in PatternMode.mode_names_reverse:
            raise ValueError(f"Mode name {mode_name} is not recognized.")
        self._mode = PatternMode.mode_names_reverse[mode_name]

    def set_tonic_pitch_class(self, pitch_class: int):
        """Set the tonic pitch class."""
        if pitch_class < 0 or pitch_class >= MusicPitchClass.TWELVE:
            raise ValueError(f"Tonic pitch class {pitch_class} out of range [0, 11].")
        self._tonic_pitch_class = pitch_class

    def cardinality(self) -> int:
        """Get the cardinality of the pattern."""
        return self._cardinality

    def pattern_type(self) -> int:
        """Get the pattern type."""
        return self._pattern_type

    @staticmethod
    def mode_name(self) -> str:
        """Get the current mode name."""
        return PatternMode.mode_names.get(self._mode)

    @property
    def tonic_pitch_class(self) -> int:
        """Get the tonic pitch class."""
        return self._tonic_pitch_class

    @property
    def pitch_class_intervals(self) -> Tuple[int] | Tuple[()]:
        """Get pitch class intervals for the pattern."""
        if self._cardinality is not None and self._pattern_type is not None:
            return Diatonic.pattern.get(self._cardinality, {}).get(self._pattern_type, ())
        else:
            return ()

    def pitch_class_intervals_from_mode(self, mode_index: int) -> List[int]:
        """Get pitch class intervals for a specific mode."""
        if mode_index < 0 or mode_index >= len(self._modes):
            raise ValueError(f"Mode index {mode_index} out of range.")
        return self._modes[mode_index]

    def pitch_class_intervals_to_tonic(self) -> List[int]:
        """Get pitch class intervals starting from the tonic pitch class."""
        if self._tonic_pitch_class is None:
            raise ValueError("Tonic pitch class is not set.")

        # Tonic pitch class
        interval_to_tonic = 0
        intervals_to_tonic = []
        for interval in self.pitch_class_intervals:
            interval_to_tonic += interval
            intervals_to_tonic.append(interval_to_tonic)

        return intervals_to_tonic

    @property
    def pitch_classes(self) -> Tuple[int, ...]:
        """Calculate absolute pitch classes based on tonic and intervals."""
        if self._tonic_pitch_class is None:
            return () # Empty tuple if no tonic
        pitch_classes = []
        for interval in self.pitch_class_intervals_to_tonic():
            pc = (self._tonic_pitch_class + interval) % MusicPitchClass.TWELVE
            pitch_classes.append(pc)

        return tuple(pitch_classes)

    @property
    def helix_indices(self) -> List[int]:
        """Map pattern pitch classes to helix indices with octave tracking."""
        if self._tonic_pitch_class is None:
            return []

        indices = []
        current_octave = self._tonic_octave
        prev_pitch_class = self._tonic_pitch_class

        for pc in self.pitch_classes:
            # Detect octave wrap-around
            if pc < prev_pitch_class:
                current_octave += 1
            idx = self._pitches.index_of(pc, current_octave)
            indices.append(idx)
            prev_pitch_class = pc

        return indices

    def transpose(self, pitch_interval: int, direction: int = Direction.ASCENDING) -> 'MusicPattern':
        """Return new pattern transposed by pitch_interval on the helix."""
        new_tonic = (self._tonic_pitch_class + direction * pitch_interval) % MusicPitchClass.TWELVE
        new_octave = self._tonic_octave + (self._tonic_pitch_class + direction * pitch_interval) // MusicPitchClass.TWELVE

        return MusicPattern(
            name=f"{self.name} (transposed)",
            cardinality=self._cardinality,
            pattern_type=self._pattern_type,
            mode=self._mode,
            tonic_pitch_class=new_tonic,
            tonic_octave=new_octave,
        )

    def degree_to_helix_index(self, degree: int) -> int:
        """Get helix index for a pattern degree (1-based)."""
        if degree < 1 or degree > self._cardinality:
            raise ValueError(f"Degree {degree} out of range [1, {self._cardinality}]")
        return self.helix_indices[degree - 1]



class PatternSequence:
    """ Ordered set of patterns """
    def __init__(self, patterns: list[MusicPattern]):
        self.patterns = patterns