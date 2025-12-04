"""Module for defining musical patterns based on diatonic scales, modes and intervals."""

from typing import Tuple, List
from utilities import sequence_rotations, interval_to_step
from base import DiatonicPatterns
from .base import Base

class MusicPattern(Base):
    def __init__(self,
                name: str = "Pattern",
                cardinality: int = None,
                pattern_type: int = None,
                mode : int = None,
                tonic_pitch_class: int = None,
    ):
        super().__init__(name)
        self.cardinality = cardinality # Number of pitches in the pattern
        self.pattern_type = pattern_type # Interval pattern identifier
        self.mode = mode # Mode index
        self.tonic_pitch_class = tonic_pitch_class # Tonic pitch class

        self._pitch_intervals = []
        self.set_pitch_intervals()

        # Pattern modes = scale modes and chord positions - rotations of interval sequence
        self.modes = sequence_rotations(self.pitch_intervals)
        # Modes on pitch helix
        self.modes_helix = [interval_to_step(m) for m in self.modes]

    @property
    def pitch_intervals(self) -> List [int]:
        # Return the pitch intervals as a tuple
        return self._pitch_intervals

    @property
    def degrees (self) -> Tuple [int]:
        # Scale degrees: ordered set
        return tuple(range(1, self.cardinality + 1))


    def set_pitch_intervals(self):
        """ Set custom pitch intervals """
        if self.cardinality is not None and self.pattern_type is not None:
            self._pitch_intervals = tuple(DiatonicPatterns.dict[self.cardinality][self.pattern_type])


class PatternSequence:
    """ Ordered set of patterns """
    def __init__(self, patterns: list[MusicPattern]):
        self.patterns = patterns