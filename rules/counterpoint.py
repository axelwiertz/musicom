"""Module for analyzing counterpoint rules between two musical units."""
import numpy as np
from structures import MusicUnit

PERFECT_INTERVALS = {0, 5, 7, 12}  # Unison, Perfect Fourth, Perfect Fifth, Octave


def is_perfect(itv) -> bool:
    """Check if an interval is perfect."""
    return abs(itv) in PERFECT_INTERVALS


class Counterpoint:
    """Class for analyzing counterpoint between two musical units."""
    def __init__(self, unit1: MusicUnit, unit2: MusicUnit):
        self._unit1 = unit1
        self._unit2 = unit2
        self._stream1 = None
        self._stream2 = None
        # Ensure the voices are of the same length
        if len(unit1) != len(unit2):
            raise ValueError("Units must be of the same length")


    def has_parallel_perfect_intervals(self):
        """Check for parallel perfect intervals between two musical units."""
        for i in range(len(self._unit1) - 1):
            itv1 = self._unit1.pitch_intervals[i]
            itv2 = self._unit2.pitch_intervals[i]
            if (is_perfect (itv1) and is_perfect (itv2)
                    and (np.sign(itv1) == np.sign(itv2))):
                return True
        return False

    def has_crossing_voices(self) -> bool:
        """Check for crossing voices between two musical units."""
        for i in range(len(self._stream1) - 1):
            node1 = self._unit1.pitch_nodes[i]
            node2 = self._unit2.pitch_nodes[i]
            next_node1 = self._unit1.pitch_nodes[i+1]
            next_node2 = self._unit2.pitch_nodes[i+1]
            if node1 < node2 and next_node1 > next_node2:
                return False
    
        return True
