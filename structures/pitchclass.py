"""Pitch class patterns: intervals, scales, rotations, chords, definitions"""
from enum import Enum, auto
from typing import Tuple, FrozenSet, Optional, List
from dataclasses import dataclass
import networkx as nx
from .base import Base
from .pitch import MusicPitchClass, MusicPitchGrid

# Lazy import to avoid circular dependencies
def _get_helpers():
    from utilities.helpers import sequence_rotations, interval_to_step
    return sequence_rotations, interval_to_step

#TODO: Add methods for pattern manipulation, e.g., inversion, retrograde, etc.

"""1. Pattern Categories and Types"""
@dataclass(frozen=True)
class Cardinality:
    # Number of pitch classes in pattern
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

@dataclass(frozen=True)
class PatternType(Enum):
    SCALE = auto()

    # Dyad types
    MINOR_SECOND = auto()
    MAJOR_SECOND = auto()
    MINOR_THIRD = auto()
    MAJOR_THIRD = auto()
    PERFECT_FOURTH = auto()
    TRITONE = auto()
    PERFECT_FIFTH = auto()
    MINOR_SIXTH = auto()
    MAJOR_SIXTH = auto()
    MINOR_SEVENTH = auto()
    MAJOR_SEVENTH = auto()

    # Triad types
    DIMINISHED = auto()
    MINOR = auto()
    MAJOR = auto()
    AUGMENTED = auto()
    SUS2 = auto()
    SUS4 = auto()

    # Tetrad types
    MINOR7 = auto()
    MAJOR7 = auto()
    DOMINANT7 = auto()
    AUGMENTED_4 = auto()
    MAJOR6 = auto()
    MINOR6 = auto()
    MINOR7_FLAT5 = auto()
    SUS2_4 = auto()
    SUS4_4 = auto()

    # Extended chords
    NINTH = auto()
    MINOR_NINTH = auto()
    PENTATONIC = auto()
    HEXATONIC = auto()
    HEPTATONIC = auto()
    OCTATONIC = auto()
    CHROMATIC = auto()


@dataclass(frozen=True)
class PatternCategory(Enum):
    """Distinct categories of musical pattern types."""
    INTERVAL = auto()  # Dyads (2)
    CHORD = auto()  # Triads (3), 7ths (4), extensions (x)
    SCALE = auto()  # Pentatonic (5), Heptatonic (7), Chromatic (12)


class PitchInterval:
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


@dataclass(frozen=True)
class PatternRotation:
    """ Modes are rotations of pitch class patterns
        Cardinality determines number of rotations:
        - Dyadic pattern has 2 rotations
        - Triadic pattern has 3 rotations
        - Tetradic pattern has 4 rotations
        - Pentatonic pattern has 5 rotations
        - Heptatonic pattern has 7 rotations """
    # Rotations are indexed from 0
    ionian = major = root = 0
    dorian = first_inversion = 1
    phrygian = second_inversion = 2
    lydian = third_inversion = 3
    mixolydian = 4
    aeolian = minor = 5
    locrian = 6
    rotation_names = {ionian:'major',dorian:'dorian',phrygian:'phrygian',
            lydian:'lydian',mixolydian:'mixolydian',aeolian:'minor',locrian:'locrian'}

    rotation_names_reverse = {v:k for k,v in rotation_names.items()}


class MusicPattern:
    # Interval patterns for pitch classes
    # pitch_intervals: tuple of interval steps, e.g. (2,2)
    dict = {
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
        PatternType.MAJOR_SEVENTH   : (11, 1),
        # 3 Triad scale Patterns
        PatternType.DIMINISHED: (3, 3, 6),
        PatternType.MINOR: (3, 4, 5),
        PatternType.MAJOR: (4, 3, 5),
        PatternType.AUGMENTED: (4, 4, 4),
        PatternType.SUS2: (2, 5, 5),
        PatternType.SUS4: (5, 2, 5),
        PatternType.MINOR7: (3, 4, 3, 2),
        PatternType.MINOR7_FLAT5: (3, 3, 4, 2),
        PatternType.MAJOR7 : (4, 3, 4, 1),
        PatternType.DOMINANT7: (4, 3, 3, 2),
        PatternType.MAJOR6: (4, 3, 2, 3),
        PatternType.MINOR6: (3, 4, 2, 3),
        PatternType.AUGMENTED_4: (4, 4, 3, 1),
        PatternType.SUS2_4: (2, 5, 4, 1),
        PatternType.SUS4_4: (5, 2, 4, 1),


        PatternType.PENTATONIC: (2, 2, 3, 2, 3),
        PatternType.HEPTATONIC : (2, 2, 1, 2, 2, 2, 1),
        PatternType.CHROMATIC: (1,1,1,1,1,1,1,1,1,1,1,1),

        PatternType.NINTH: (4, 3, 3, 4, 10),
        PatternType.MINOR_NINTH: (3, 4, 3, 4, 10)
    }

    @staticmethod
    def find_pattern_type(cardinality: int, intervals: Tuple[int, ...]) -> PatternType | None:
        """Static method to find pattern type from cardinality and intervals."""
        for p_type, p_intervals in MusicPattern.dict.items():
            if len(p_intervals) == cardinality and p_intervals == intervals:
                return p_type
        return None


"""3. Hierarchical Pattern Registry"""

class PatternRegistry:
    """Central registry for all patterns with relationship tracking."""

    # (cardinality, chord_type, parent_pattern, parent_degree)

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

class MusicPitchClassSet(Base):
    """Musical pitch class set representing a collection of pitch classes.
    
    Instances form a subset hierarchy where one set can be a subset of another.
    The subset relationships are managed by PatternGraph.
    """
    def __init__(self,
                 name: str = "Pattern",
                 definition: PatternType = None,
                 rotation: int = None,
                 initial: int = None,
                 ):
        super().__init__(name)
        self._definition = definition

        # Use lazy import for helpers
        sequence_rotations_func, interval_to_step_func = _get_helpers()
        
        self._rotations = sequence_rotations_func(self.pitch_class_intervals)
        self._rotation = rotation

        # Connect to absolute pitches
        self._pitches = MusicPitchGrid()
        self._rotations_pitches = [interval_to_step_func(m) for m in self._rotations]

        self._initial = initial

    def __str__(self) -> str:
        return (f"MusicPitchClassSet(name={self.name}, "
                f"type={self._definition}, "
                f"rotation={self._rotation}, "
                f"initial={self._initial}, "
                f"pitch_classes={self.pitch_classes})")

    def set_rotation_index(self, rotation_index: int):
        """Set the current rotation by index."""
        if rotation_index < 0 or rotation_index >= len(self._rotations):
            raise ValueError(f"Mode index {rotation_index} out of range.")
        self._rotation = rotation_index

    def set_rotation_name(self, rotation_name: str):
        """Set the current rotation by name."""
        if rotation_name not in PatternRotation.rotation_names_reverse:
            raise ValueError(f"Mode name {rotation_name} is not recognized.")
        self._rotation = PatternRotation.rotation_names_reverse[rotation_name]

    def set_initial(self, pitch_class: int):
        """Set the initial (tonic/root) pitch class."""
        if pitch_class < 0 or pitch_class >= MusicPitchClass.SIZE:
            raise ValueError(f"Tonic pitch class {pitch_class} out of range [0, 11].")
        self._initial = pitch_class

    def type(self) -> PatternType:
        """Get the pattern type."""
        return self._definition

    @staticmethod
    def rotation_name(self) -> str:
        """Get the current rotation name."""
        return PatternRotation.rotation_names.get(self._rotation)

    @property
    def initial(self) -> int:
        """Get the initial pitch class."""
        return self._initial

    @property
    def pitch_class_intervals(self) -> Tuple[int] | Tuple[()]:
        """Get pitch class intervals for the pattern."""
        if self._definition is not None:
            return MusicPattern.dict.get(self._definition)
        else:
            return ()

    @property
    def definition(self) -> PatternType:
        """Get the pattern definition type."""
        return self._definition

    @property
    def cardinality(self) -> int:
        """Get the cardinality of the pattern."""
        return len(self.pitch_class_intervals)

    def pitch_class_intervals_from_rotation(self, rotation_index: int) -> List[int]:
        """Get pitch class intervals for a specific rotation."""
        if rotation_index < 0 or rotation_index >= len(self._rotations):
            raise ValueError(f"Mode index {rotation_index} out of range.")
        return self._rotations[rotation_index]

    def pitch_class_intervals_to_initial(self) -> List[int]:
        """Get pitch class intervals starting from the initial pitch class."""
        if self._initial is None:
            raise ValueError("Tonic pitch class is not set.")

        # Tonic pitch class
        interval_to_initial = 0
        intervals_to_initial = []
        for interval in self.pitch_class_intervals:
            interval_to_initial += interval
            intervals_to_initial.append(interval_to_initial)

        return intervals_to_initial

    @property
    def pitch_classes(self) -> Tuple[int, ...]:
        """Calculate pitch classes based on tonic pitch class and intervals."""
        if self._initial is None:
            return () # Empty tuple if no initial
        pitch_classes = []
        for interval in self.pitch_class_intervals_to_initial():
            pc = (self._initial + interval) % MusicPitchClass.SIZE
            pitch_classes.append(pc)

        return tuple(pitch_classes)

    def get_pitches_in_octave(self, octave: int) -> List[int]:
        """Get absolute pitches for the pattern in a specific octave."""
        if self._initial is None:
            raise ValueError("Tonic pitch class is not set.")

        midi_pitches = []
        base_midi = (octave + 1) * MusicPitchClass.SIZE + self._initial
        for interval in self.pitch_class_intervals_to_initial():
            midi_pitch = base_midi + interval
            midi_pitches.append(midi_pitch)

        return midi_pitches

    @staticmethod
    def get_degree(self, degree_: int) -> int:
        """ Pattern degree pitch class """
        return self.pitch_classes[degree_ - 1]

    def is_subset_of(self, other: 'MusicPitchClassSet') -> bool:
        """Check if this pitch class set is a subset of another."""
        if self._initial is None or other._initial is None:
            return False
        self_pcs = set(self.pitch_classes)
        other_pcs = set(other.pitch_classes)
        return self_pcs.issubset(other_pcs)

    def is_superset_of(self, other: 'MusicPitchClassSet') -> bool:
        """Check if this pitch class set is a superset of another."""
        return other.is_subset_of(self)

    def pitch_class_set(self) -> FrozenSet[int]:
        """Return pitch classes as a frozen set."""
        if self._initial is None:
            return frozenset()
        return frozenset(self.pitch_classes)


def create_subpattern(parent_pattern: MusicPitchClassSet,
                      child_pattern: MusicPitchClassSet = None,
                      degrees: List[int] = None,
                      name: str = "Subpattern") -> 'MusicPitchClassSet':
    """
    Create a (lower-cardinality) subpattern from a subset of this pattern's degrees.
    Args:
        parent_pattern: The parent pattern to extract from
        child_pattern: Optional existing child pattern to base on
        degrees: List of scale degrees (1-based) to include in subpattern
        name: Name of the new subpattern
    """
    if not all(1 <= d <= parent_pattern.cardinality for d in degrees):
        raise ValueError(f"All degrees must be within the range [1, {parent_pattern.cardinality}]")

    parent_pitch_classes = parent_pattern.pitch_classes
    sub_pitch_classes = ()
    new_cardinality = 0
    if child_pattern:
        sub_pitch_classes = child_pattern.pitch_classes
        new_cardinality = len(sub_pitch_classes)
    elif degrees:
        sub_pitch_classes = tuple(parent_pitch_classes[d - 1] for d in degrees)
        new_cardinality = len(sub_pitch_classes)
        

    if new_cardinality >= parent_pattern.cardinality:
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

    return MusicPitchClassSet(
        name=name,
        definition=new_pattern_type, # Set pattern type based on intervals
        rotation=None,  # No specific rotation
        initial=sub_pitch_classes[0]  # Set tonic to first pitch class,
    )

"""4. Scale Degree Chord Generator"""
class SubPatterns:
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
                        cardinality: int = 3) -> PatternDefinition:
        """
        Generate chord at a specific scale degree.
        Args:
            scale: The parent scale
            degree: Scale degree (1-7)
            cardinality: 3 for triad, 4 for 7th, 5 for 9th
        """
        # Build chord by stacking thirds from the degree
        chord_degrees = []
        current_degree = degree
        for _ in range(cardinality):
            chord_degrees.append(current_degree)
            current_degree = ((current_degree - 1 + 2) % 7) + 1  # Skip by thirds

        return PatternDefinition(
            name=f"Degree {degree} chord",
            intervals=cls._calculate_intervals(scale, chord_degrees),
            category=PatternCategory.CHORD,
            parent=scale,
            degree_indices=tuple(chord_degrees)
        )

    @classmethod
    def _calculate_intervals(cls,scale, chord_degrees) -> Tuple[int]:
        pass


"""5. Pattern Relationship Graph"""

class PatternGraph:
    """Graph-based pattern relationship manager for MusicPitchClassSet instances.
    
    This directed graph manages the subset hierarchy where edges point from
    supersets to subsets (parent to child relationships).
    """

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

    def add_pitch_class_set(self, pitch_class_set: MusicPitchClassSet):
        """Add a MusicPitchClassSet instance to the graph.
        
        Args:
            pitch_class_set: The pitch class set to add
        """
        node_id = id(pitch_class_set)
        self._graph.add_node(
            node_id,
            pitch_class_set=pitch_class_set,
            name=pitch_class_set.name,
            pitch_classes=pitch_class_set.pitch_class_set()
        )

    def add_subset_relation(self,
                           superset: MusicPitchClassSet,
                           subset: MusicPitchClassSet):
        """Add a subset relationship between two pitch class sets.
        
        Args:
            superset: The larger set (parent)
            subset: The smaller set (child)
        
        Raises:
            ValueError: If subset is not actually a subset of superset
        """
        if not subset.is_subset_of(superset):
            raise ValueError(
                f"{subset.name} is not a subset of {superset.name}"
            )
        
        superset_id = id(superset)
        subset_id = id(subset)
        
        # Ensure both nodes exist
        if superset_id not in self._graph:
            self.add_pitch_class_set(superset)
        if subset_id not in self._graph:
            self.add_pitch_class_set(subset)
        
        # Add directed edge from superset to subset
        self._graph.add_edge(superset_id, subset_id, relation='subset')

    def get_subsets(self, pitch_class_set: MusicPitchClassSet) -> List[MusicPitchClassSet]:
        """Get all direct subsets of the given pitch class set.
        
        Args:
            pitch_class_set: The set to find subsets for
            
        Returns:
            List of pitch class sets that are direct subsets
        """
        node_id = id(pitch_class_set)
        if node_id not in self._graph:
            return []
        
        return [
            self._graph.nodes[n]['pitch_class_set']
            for n in self._graph.successors(node_id)
        ]

    def get_supersets(self, pitch_class_set: MusicPitchClassSet) -> List[MusicPitchClassSet]:
        """Get all direct supersets of the given pitch class set.
        
        Args:
            pitch_class_set: The set to find supersets for
            
        Returns:
            List of pitch class sets that are direct supersets
        """
        node_id = id(pitch_class_set)
        if node_id not in self._graph:
            return []
        
        return [
            self._graph.nodes[n]['pitch_class_set']
            for n in self._graph.predecessors(node_id)
        ]

    def get_all_subsets(self, pitch_class_set: MusicPitchClassSet) -> List[MusicPitchClassSet]:
        """Get all subsets (direct and indirect) of the given pitch class set.
        
        Args:
            pitch_class_set: The set to find all subsets for
            
        Returns:
            List of all pitch class sets in the subset hierarchy
        """
        node_id = id(pitch_class_set)
        if node_id not in self._graph:
            return []
        
        descendants = nx.descendants(self._graph, node_id)
        return [
            self._graph.nodes[n]['pitch_class_set']
            for n in descendants
        ]

    def get_all_supersets(self, pitch_class_set: MusicPitchClassSet) -> List[MusicPitchClassSet]:
        """Get all supersets (direct and indirect) of the given pitch class set.
        
        Args:
            pitch_class_set: The set to find all supersets for
            
        Returns:
            List of all pitch class sets that contain this set
        """
        node_id = id(pitch_class_set)
        if node_id not in self._graph:
            return []
        
        ancestors = nx.ancestors(self._graph, node_id)
        return [
            self._graph.nodes[n]['pitch_class_set']
            for n in ancestors
        ]

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

    def find_common_superset(self,
                            set1: MusicPitchClassSet,
                            set2: MusicPitchClassSet) -> Optional[MusicPitchClassSet]:
        """Find the smallest common superset of two pitch class sets.
        
        Args:
            set1: First pitch class set
            set2: Second pitch class set
            
        Returns:
            The smallest pitch class set that contains both, or None
        """
        id1 = id(set1)
        id2 = id(set2)
        
        if id1 not in self._graph or id2 not in self._graph:
            return None
        
        ancestors1 = nx.ancestors(self._graph, id1)
        ancestors2 = nx.ancestors(self._graph, id2)
        common = ancestors1 & ancestors2
        
        if not common:
            return None
        
        # Return the one closest to both sets (smallest common superset)
        return min(
            (self._graph.nodes[n]['pitch_class_set'] for n in common),
            key=lambda pcs: (
                nx.shortest_path_length(self._graph, id(pcs), id1) +
                nx.shortest_path_length(self._graph, id(pcs), id2)
            )
        )

    def visualize(self) -> str:
        """Generate a string representation of the graph structure.
        
        Returns:
            String showing the hierarchy of pitch class sets
        """
        lines = ["PatternGraph Hierarchy:"]
        
        # Find root nodes (nodes with no predecessors)
        roots = [n for n in self._graph.nodes() if self._graph.in_degree(n) == 0]
        
        def traverse(node, indent=0):
            node_data = self._graph.nodes[node]
            if 'pitch_class_set' in node_data:
                pcs = node_data['pitch_class_set']
                lines.append(f"{'  ' * indent}└─ {pcs.name} {pcs.pitch_class_set()}")
            elif 'pattern' in node_data:
                pattern = node_data['pattern']
                lines.append(f"{'  ' * indent}└─ {pattern.name}")
            
            for child in self._graph.successors(node):
                traverse(child, indent + 1)
        
        for root in roots:
            traverse(root)
        
        return '\n'.join(lines)



