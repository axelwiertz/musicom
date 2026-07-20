"""Module for analyzing counterpoint rules between two musical units."""
import numpy as np
from structures.unit import MusicUnit

PERFECT_INTERVALS = {0, 5, 7, 12}  # Unison, Perfect Fourth, Perfect Fifth, Octave


def is_perfect(itv) -> bool:
    """Check if an interval is perfect."""
    return abs(itv) in PERFECT_INTERVALS


class Counterpoint:
    """Class for analyzing counterpoint between two musical units."""
    def __init__(self, unit1: MusicUnit, unit2: MusicUnit):
        self._unit1 = unit1
        self._unit2 = unit2
        self.set_units(unit1, unit2)

    def set_units(self, unit1: MusicUnit, unit2: MusicUnit):
        """Set the musical units for counterpoint analysis."""
        self._unit1 = unit1
        self._unit2 = unit2
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
        """Return True if the two voices cross between any adjacent positions.

        Voices cross when their relative order flips: one voice starts below
        the other and ends above it (or vice versa) across a step.
        """
        for i in range(len(self._unit1) - 1):
            pitch1 = self._unit1.pitches[i]
            pitch2 = self._unit2.pitches[i]
            next_pitch1 = self._unit1.pitches[i + 1]
            next_pitch2 = self._unit2.pitches[i + 1]
            if (pitch1 < pitch2 and next_pitch1 > next_pitch2) or \
               (pitch1 > pitch2 and next_pitch1 < next_pitch2):
                return True
        return False
