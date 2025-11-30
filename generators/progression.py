"""
Musicom generators module - scale library
Module for generating musical scales and chords.
"""
from typing import List
from structures.unit import MusicUnit
from structures.pattern import MusicPattern
from structures.time import MusicTime
from music21 import roman, stream
from converters.mp import pattern_to_mpscale
from converters.m21 import pattern_to_m21scale
from converters.time import timestep_duration_to_quarter_length
from converters.mp import chord_to_unit
from converters.m21 import stream_to_unit

from generators import Generator

class ProgressionGenerator (Generator):
    """ ScaleLibrary generator"""
    def __init__(self,
                 seed_unit: MusicUnit,
                 time : MusicTime,
                 pattern : MusicPattern,
                 chord_progression_degrees : List[int]):
        super().__init__(seed_unit)
        self.time = time
        self.pattern = pattern
        self.chord_progression_degrees = chord_progression_degrees

    def generate(self) -> MusicUnit:
        """Generate a MusicUnit with the chord progression."""
        # mp
        unit = chord_to_unit (pattern_to_mpscale(self.pattern).chord_progression(
                self.chord_progression_degrees,
                durations=1,
                intervals=0,
                volumes=None,
                chords_interval=None))
        # m21
        stream1 = stream.Stream()
        for i in range (len(self.chord_progression_degrees)):
            # m21 Create chord from Roman numeral
            chord01 = roman.RomanNumeral (self.chord_progression_degrees[i],
                                          keyOrScale=pattern_to_m21scale(self.pattern))
            chord01.duration.quarterLength = timestep_duration_to_quarter_length(self.time, 1)
            stream1.append(chord01)

        unit += stream_to_unit(stream1)

        return unit