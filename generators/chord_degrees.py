"""
Musicom generators module - scale library
Module for generating musical scales and chords.
"""
from typing import List
from structures import MusicUnit, MusicPitchPattern, MusicTimeGrid
from converters.musicpy_converter import pattern_to_mpscale
from converters.music21_score import pattern_to_m21scale
from converters.time import ticks_to_quarter_length
from converters.musicpy_converter import chord_to_unit
from converters.music21_score import stream_to_unit
from music21 import roman, stream

from .base import MusicGenerator

class ChordDegreeGenerator (MusicGenerator):
    """ Chord generator """
    """Generate chords based on chord degrees within a given musical pattern."""
    def __init__(self,
                 time : MusicTimeGrid,
                 pattern : MusicPitchPattern,
                 chord_degrees : List[int]):
        super().__init__()
        self.time = time
        self.pattern = pattern
        self.chord_degrees = chord_degrees

    def generate(self) -> MusicUnit:
        """Generate a MusicUnit with the chords corresponding to the specified chord degrees."""
        # mp
        unit = chord_to_unit (pattern_to_mpscale(self.pattern).chord_progression(
                self.chord_degrees,
                durations=1,
                intervals=0,
                volumes=None,
                chords_interval=None))
        # m21
        stream1 = stream.Stream()
        for i in range (len(self.chord_degrees)):
            # m21 Create chord from Roman numeral
            chord01 = roman.RomanNumeral (self.chord_degrees[i],
                                          keyOrScale=pattern_to_m21scale(self.pattern))
            chord01.duration.quarterLength = ticks_to_quarter_length(self.time, 1)
            stream1.append(chord01)

        unit += stream_to_unit(stream1)

        return unit