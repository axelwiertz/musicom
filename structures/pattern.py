"""Module for defining musical patterns based on diatonic scales, modes and intervals."""
from typing import Tuple, List
from structures import MusicPitchClass, MusicPitch, Direction
from rules import DiatonicPatterns
from utilities import sequence_rotations, interval_to_step
from .base import Base


class MusicPattern(Base):
    def __init__(self,
                 name: str = "Pattern",
                 cardinality: int = None,
                 pattern_type: int = None,
                 mode: int = None,
                 tonic_pitch_class: int = None,
                 tonic_octave: int = 4,
                 ):
        super().__init__(name)
        self.cardinality = cardinality
        self.pattern_type = pattern_type
        self.mode = mode
        self.tonic_pitch_class = tonic_pitch_class
        self.tonic_octave = tonic_octave

        self._pitch_class_intervals = []
        self.set_pitch_class_intervals()
        # Connect to chromatic pitch helix
        self._pitches = MusicPitch()

        self._modes = sequence_rotations(self._pitch_class_intervals)
        self._modes_helix = [interval_to_step(m) for m in self._modes]


    @property
    def pitch_class_intervals(self) -> List[int]:
        return self._pitch_class_intervals
    
    def pitch_class_intervals_from_mode(self, mode_index: int) -> List[int]:
        """Get pitch class intervals for a specific mode."""
        if mode_index < 0 or mode_index >= len(self._modes):
            raise ValueError(f"Mode index {mode_index} out of range.")
        return self._modes[mode_index]

    def pitch_class_intervals_to_tonic(self) -> List[int]:
        """Get pitch class intervals starting from the tonic pitch class."""
        if self.tonic_pitch_class is None:
            raise ValueError("Tonic pitch class is not set.")

        # Tonic pitch class
        interval_to_tonic = 0
        intervals_to_tonic = []
        for interval in self._pitch_class_intervals:
            interval_to_tonic += interval
            intervals_to_tonic.append(interval_to_tonic)

        return intervals_to_tonic

    @property
    def pitch_classes(self) -> Tuple[int, ...]:
        """Calculate absolute pitch classes based on tonic and intervals."""
        if self.tonic_pitch_class is None:
            return () # Empty tuple if no tonic
        pitch_classes = []
        for interval in self.pitch_class_intervals_to_tonic():
            pc = (self.tonic_pitch_class + interval) % MusicPitchClass.TWELVE
            pitch_classes.append(pc)

        return tuple(pitch_classes)

    @property
    def helix_indices(self) -> List[int]:
        """Map pattern pitch classes to helix indices with octave tracking."""
        if self.tonic_pitch_class is None:
            return []

        indices = []
        current_octave = self.tonic_octave
        prev_pitch_class = self.tonic_pitch_class

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
        new_tonic = (self.tonic_pitch_class + direction * pitch_interval) % MusicPitchClass.TWELVE
        new_octave = self.tonic_octave + (self.tonic_pitch_class + direction * pitch_interval) // MusicPitchClass.TWELVE

        return MusicPattern(
            name=f"{self.name} (transposed)",
            cardinality=self.cardinality,
            pattern_type=self.pattern_type,
            mode=self.mode,
            tonic_pitch_class=new_tonic,
            tonic_octave=new_octave,
        )

    def degree_to_helix_index(self, degree: int) -> int:
        """Get helix index for a pattern degree (1-based)."""
        if degree < 1 or degree > self.cardinality:
            raise ValueError(f"Degree {degree} out of range [1, {self.cardinality}]")
        return self.helix_indices[degree - 1]

    def set_pitch_class_intervals(self):
        if self.cardinality is not None and self.pattern_type is not None:
            self._pitch_class_intervals = tuple(DiatonicPatterns.dict[self.cardinality][self.pattern_type])


class PatternSequence:
    """ Ordered set of patterns """
    def __init__(self, patterns: list[MusicPattern]):
        self.patterns = patterns