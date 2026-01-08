"""Module for defining musical pitch (class) patterns based on scales, modes and intervals."""
from enum import Enum, auto
from typing import Tuple, FrozenSet, Optional, List
from dataclasses import dataclass
import networkx as nx
from .base import Base
from .pitch import MusicPitchClass, MusicPitch, Direction
from utilities import sequence_rotations, interval_to_step

#TODO: Add methods for pattern manipulation, e.g., inversion, retrograde, etc.


"""1. Pattern Categories and Types"""

class PatternCategory(Enum):
    """Distinct categories of musical patterns."""
    INTERVAL = auto()  # Dyads (2)
    CHORD = auto()  # Triads (3), 7ths (4), extensions (x)
    SCALE = auto()  # Pentatonic (5), Heptatonic (7), Chromatic (12)
    MODE = auto()  # Rotations of scales


class IntervalType(Enum):
    """Interval types (dyads)."""
    UNISON = 0
    MINOR_SECOND = 1
    MAJOR_SECOND = 2
    MINOR_THIRD = 3
    MAJOR_THIRD = 4
    PERFECT_FOURTH = 5
    TRITONE = 6
    PERFECT_FIFTH = 7
    MINOR_SIXTH = 8
    MAJOR_SIXTH = 9
    MINOR_SEVENTH = 10
    MAJOR_SEVENTH = 11
    OCTAVE = 12

    INTERVAL_NUMBER_QUALITY = {
        0: "P1", 1: "m2", 2: "M2", 3: "m3", 4: "M3", 5: "P4",
        6: "TT", 7: "P5", 8: "m6", 9: "M6", 10: "m7", 11: "M7"
    }


class ChordQuality(Enum):
    """Chord qualities."""
    DIMINISHED = auto()
    MINOR = auto()
    MAJOR = auto()
    AUGMENTED = auto()
    DOMINANT = auto()
    HALF_DIMINISHED = auto()
    SUS2 = auto()
    SUS4 = auto()


class ScaleType(Enum):
    """Scale types."""
    CHROMATIC = auto()
    HEPTATONIC = auto()
    PENTATONIC = auto()
    HEXATONIC = auto()
    OCTATONIC = auto()

"""2. Pattern Base Class with Relationships"""

@dataclass(frozen=True)
class PatternDefinition:
    """Immutable pattern definition with relationship metadata."""
    name: str
    intervals: Tuple[int, ...]
    category: PatternCategory
    parent: Optional['PatternDefinition'] = None  # Superset pattern
    degree_indices: Optional[Tuple[int, ...]] = None  # Indices in parent

    @property
    def cardinality(self) -> int:
        return len(self.intervals)

    @property
    def pitch_class_set(self) -> FrozenSet[int]:
        """Return pitch classes as a set (mod 12)."""
        pcs = [0]
        cumulative = 0
        for interval in self.intervals[:-1]:  # Exclude wrap-around
            cumulative += interval
            pcs.append(cumulative % 12)
        return frozenset(pcs)

    def is_subset_of(self, other: 'PatternDefinition') -> bool:
        """Check if this pattern's pitch classes are a subset of another."""
        return self.pitch_class_set.issubset(other.pitch_class_set)

    def extract_degrees(self, degrees: Tuple[int, ...]) -> 'PatternDefinition':
        """Create a subpattern from specific scale degrees (1-based)."""
        # Implementation to extract subset
        pass

"""3. Hierarchical Pattern Registry"""

class PatternRegistry:
    """Central registry for all patterns with relationship tracking."""

    # Scale definitions
    CHROMATIC = PatternDefinition(
        name="Chromatic",
        intervals=(1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1),
        category=PatternCategory.SCALE
    )

    HEPTATONIC_MAJOR = PatternDefinition(
        name="Major Scale",
        intervals=(2, 2, 1, 2, 2, 2, 1),
        category=PatternCategory.SCALE,
        parent=CHROMATIC,
        degree_indices=(0, 2, 4, 5, 7, 9, 11)  # Chromatic indices
    )

    PENTATONIC_MAJOR = PatternDefinition(
        name="Major Pentatonic",
        intervals=(2, 2, 3, 2, 3),
        category=PatternCategory.SCALE,
        parent=HEPTATONIC_MAJOR,
        degree_indices=(1, 2, 3, 5, 6)  # Heptatonic degrees (1-based)
    )

    # Chord definitions derived from scales
    MAJOR_TRIAD = PatternDefinition(
        name="Major Triad",
        intervals=(4, 3, 5),
        category=PatternCategory.CHORD,
        parent=HEPTATONIC_MAJOR,
        degree_indices=(1, 3, 5)  # Scale degrees
    )

    MAJOR_SEVENTH = PatternDefinition(
        name="Major 7th",
        intervals=(4, 3, 4, 1),
        category=PatternCategory.CHORD,
        parent=HEPTATONIC_MAJOR,
        degree_indices=(1, 3, 5, 7)
    )

    # Relationship: MAJOR_TRIAD is subset of MAJOR_SEVENTH
    # MAJOR_TRIAD.is_subset_of(MAJOR_SEVENTH) == True


"""4. Scale Degree Chord Generator"""
class ScaleDegreeChords:
    """Generate chords for each degree of a scale."""

    # Chord qualities for each degree of major scale
    MAJOR_SCALE_TRIADS = {
        1: ChordQuality.MAJOR,  # I
        2: ChordQuality.MINOR,  # ii
        3: ChordQuality.MINOR,  # iii
        4: ChordQuality.MAJOR,  # IV
        5: ChordQuality.MAJOR,  # V
        6: ChordQuality.MINOR,  # vi
        7: ChordQuality.DIMINISHED  # vii°
    }

    MAJOR_SCALE_SEVENTHS = {
        1: (ChordQuality.MAJOR, 'maj7'),  # Imaj7
        2: (ChordQuality.MINOR, 'min7'),  # ii7
        3: (ChordQuality.MINOR, 'min7'),  # iii7
        4: (ChordQuality.MAJOR, 'maj7'),  # IVmaj7
        5: (ChordQuality.DOMINANT, '7'),  # V7
        6: (ChordQuality.MINOR, 'min7'),  # vi7
        7: (ChordQuality.HALF_DIMINISHED, 'ø7')  # viiø7
    }

    @classmethod
    def chord_at_degree(cls,
                        scale: PatternDefinition,
                        degree: int,
                        extension: int = 3) -> PatternDefinition:
        """
        Generate chord at a specific scale degree.

        Args:
            scale: The parent scale
            degree: Scale degree (1-7)
            extension: 3 for triad, 4 for 7th, 5 for 9th
        """
        # Build chord by stacking thirds from the degree
        chord_degrees = []
        current_degree = degree
        for _ in range(extension):
            chord_degrees.append(current_degree)
            current_degree = ((current_degree - 1 + 2) % 7) + 1  # Skip by thirds

        return PatternDefinition(
            name=f"Degree {degree} chord",
            intervals=cls._calculate_intervals(scale, chord_degrees),
            category=PatternCategory.CHORD,
            parent=scale,
            degree_indices=tuple(chord_degrees)
        )




"""MusicPattern pitch(class) patterns: cardinality, intervals, scales, modes, chords"""

class Cardinality:
    # MusicPattern patterns: cardinality, intervals, scales, modes, chords
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

    UNISON = 0
    MINOR_SECOND = 1
    MAJOR_SECOND = 2
    MINOR_THIRD = 3
    MAJOR_THIRD = 4
    PERFECT_FOURTH = 5
    TRITONE = 6
    PERFECT_FIFTH = 7
    MINOR_SIXTH = 8
    MAJOR_SIXTH = 9
    MINOR_SEVENTH = 10
    MAJOR_SEVENTH = 11
    OCTAVE = 12

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


class MusicPattern:
    # Interval patterns for pitch classes
    # pitch_intervals: tuple of interval steps, e.g. (2,2)
    pattern = {
        Cardinality.DYAD: {
            PatternType.MINOR_SECOND    : (1, 11),
            PatternType.MAJOR_SECOND    : (2, 10),
            PatternType.MINOR_THIRD     : (3, 9),
            PatternType.MAJOR_THIRD     : (4, 8),
            PatternType.PERFECT_FOURTH  : (5, 7),
            PatternType.TRITONE         : (6, 6),
            PatternType.PERFECT_FIFTH   : (7, 5),
            PatternType.MINOR_SIXTH     : (8, 4),
            PatternType.MAJOR_SIXTH     : (9, 3),
            PatternType.MINOR_SEVENTH   : (10, 2),
            PatternType.MAJOR_SEVENTH   : (11, 1)
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

    @staticmethod
    def find_pattern_type(cardinality: int, intervals: Tuple[int, ...]) -> int | None:
        """Static method to find pattern type from cardinality and intervals."""
        if cardinality in MusicPattern.pattern:
            for p_type, p_intervals in MusicPattern.pattern[cardinality].items():
                if p_intervals == intervals:
                    return p_type
        if cardinality in MusicPattern.multicycle_patterns:
            for p_type, p_intervals in MusicPattern.multicycle_patterns[cardinality].items():
                if p_intervals == intervals:
                    return p_type
        return None


class MusicPitchPattern(Base):
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


    def create_subpattern(self, degrees: List[int], name: str = "Subpattern") -> 'MusicPitchPattern':
        """
        Create a lower-cardinality subpattern from a subset of this pattern's degrees.

        :param degrees: A list of 1-based degrees to extract from the current pattern.
        :param name: The name for the new subpattern.
        :return: A new MusicPitchPattern instance.
        """
        if not all(1 <= d <= self._cardinality for d in degrees):
            raise ValueError(f"All degrees must be within the range [1, {self._cardinality}]")

        parent_pitch_classes = self.pitch_classes
        sub_pitch_classes = tuple(parent_pitch_classes[d - 1] for d in degrees)

        new_cardinality = len(sub_pitch_classes)
        if new_cardinality >= self._cardinality:
            raise ValueError("Subpattern must have a lower cardinality than the parent pattern.")

        # Calculate new intervals
        intervals = []
        for i in range(new_cardinality):
            start_pc = sub_pitch_classes[i]
            end_pc = sub_pitch_classes[(i + 1) % new_cardinality]
            interval = (end_pc - start_pc + 12) % 12
            if interval == 0 and new_cardinality > 1: # Handle octave for last interval
                 interval = 12 - sum(intervals)
            intervals.append(interval)

        # Correct the last interval for cyclic patterns
        if sum(intervals) != 12 and new_cardinality > 1:
            intervals[-1] = 12 - sum(intervals[:-1])

        new_intervals = tuple(intervals)

        # Find the pattern type for the new intervals
        new_pattern_type = MusicPattern.find_pattern_type(new_cardinality, new_intervals)

        return MusicPitchPattern(
            name=name,
            cardinality=new_cardinality,
            pattern_type=new_pattern_type,
            mode=None,  # Subpatterns like chords don't typically have modes
            tonic_pitch_class=self.tonic_pitch_class,
            tonic_octave=self.tonic_octave
        )

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
    def tonic_octave(self) -> int:
        return self._tonic_octave

    @property
    def pitch_class_intervals(self) -> Tuple[int] | Tuple[()]:
        """Get pitch class intervals for the pattern."""
        if self._cardinality is not None and self._pattern_type is not None:
            return MusicPattern.pattern.get(self._cardinality, {}).get(self._pattern_type, ())
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

    def transpose(self, pitch_interval: int, direction: int = Direction.ASCENDING) -> 'MusicPitchPattern':
        """Return new pattern transposed by pitch_interval on the helix."""
        new_tonic = (self._tonic_pitch_class + direction * pitch_interval) % MusicPitchClass.TWELVE
        new_octave = self._tonic_octave + (self._tonic_pitch_class + direction * pitch_interval) // MusicPitchClass.TWELVE

        return MusicPitchPattern(
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


"""5. Pattern Relationship Graph"""

class PatternGraph:
    """Graph-based pattern relationship manager."""

    def __init__(self):
        self._graph = nx.DiGraph()

    def add_pattern(self, pattern: PatternDefinition):
        """Add pattern to graph."""
        self._graph.add_node(pattern.name, pattern=pattern)
        if pattern.parent:
            self._graph.add_edge(
                pattern.parent.name,
                pattern.name,
                relation='contains'
            )

    def get_subpatterns(self, pattern_name: str) -> List[PatternDefinition]:
        """Get all patterns that are subsets of the given pattern."""
        return [
            self._graph.nodes[n]['pattern']
            for n in self._graph.successors(pattern_name)
        ]

    def get_superpatterns(self, pattern_name: str) -> List[PatternDefinition]:
        """Get all patterns that contain the given pattern."""
        return [
            self._graph.nodes[n]['pattern']
            for n in self._graph.predecessors(pattern_name)
        ]

    def find_common_parent(self,
                           pattern1: str,
                           pattern2: str) -> Optional[PatternDefinition]:
        """Find the smallest common superset of two patterns."""
        ancestors1 = nx.ancestors(self._graph, pattern1)
        ancestors2 = nx.ancestors(self._graph, pattern2)
        common = ancestors1 & ancestors2
        # Return the one closest to both patterns
        if common:
            return min(
                (self._graph.nodes[n]['pattern'] for n in common),
                key=lambda p: (
                    nx.shortest_path_length(self._graph, p.name, pattern1) +
                    nx.shortest_path_length(self._graph, p.name, pattern2)
                )
            )
        return None



