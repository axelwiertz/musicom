"""
Musicom generators module - scale library
Module for generating musical scales and chords.
"""
from typing import List
from structures import MusicScale, MusicUnit
from converters import chord_to_unit, stream_to_unit
from structures.composition import MusicTime
from analysis.music21 import roman, stream

from generators import Generator

class ProgressionGenerator (Generator):
    """ ScaleLibrary generator"""
    def __init__(self, seed_unit: MusicUnit, time : MusicTime,
                 musicscale : MusicScale,
                 chord_progression_degrees : List[int]):
        super().__init__(seed_unit)
        self.time = time
        self.musicscale = musicscale
        self.chord_progression_degrees = chord_progression_degrees

    def generate(self) -> MusicUnit:
        """Generate a MusicUnit with the chord progression."""
        return self.progression()

    def progression(self) -> MusicUnit:
        # Chord progression patterns in a key
        # mp
        unit = chord_to_unit (self.musicscale.mpscale.chord_progression(
                self.chord_progression_degrees,
                durations=self.seed_unit.time.beat_duration,
                intervals=0,
                volumes=None,
                chords_interval=None))
        # m21
        stream1 = stream.Stream()
        for i in range (len(self.chord_progression_degrees)):
            # m21 Create chord from Roman numeral
            chord01 = roman.RomanNumeral (self.chord_progression_degrees[i], keyOrScale=self.musicscale.m21scale)
            chord01.duration.quarterLength = self.seed_unit.time.beat_duration
            stream1.append(chord01)

        unit = stream_to_unit(stream1)

        return unit

