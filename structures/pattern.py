"""Module for defining musical patterns based on diatonic scales, modes and intervals."""

from typing import Tuple
from utilities.helpers import sequence_rotations, interval_to_step
from base.diatonic import get_pitch_intervals

class MusicPattern:
    def __init__(self,
                cardinality: int = None,
                interval_pattern: int = None,
                tonic: int = None,
                mode : int = None
    ):
        self.cardinality = cardinality
        self.interval_pattern = interval_pattern
        self.tonic = tonic
        self.mode = mode

        self.pitch_intervals = get_pitch_intervals(cardinality, interval_pattern)

        # Pattern modes = scale modes and chord positions - rotations of interval sequence
        self.modes = sequence_rotations(self.pitch_intervals)
        # Modes on pitch helix
        self.modes_helix = [interval_to_step(m) for m in self.modes]

    def degrees (self) -> Tuple [int]:
        # Scale degrees: ordered set
        return tuple(range(1, self.cardinality + 1))


class PatternSequence:
    """ Ordered set of patterns """
    def __init__(self, patterns: list[MusicPattern]):
        self.patterns = patterns