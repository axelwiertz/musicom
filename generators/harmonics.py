"""
Musicom generators module
harmonic functions
"""
import random
from typing import List
from structures.unit import MusicUnit
from structures.factory import MusicGenerator
from transformators import transpose
from music21 import note, interval

class HarmonicsGenerator(MusicGenerator):
    def __init__(self,
                source_unit      : MusicUnit,
                fundamental_pitch : int,
                harmonic_numbers  : list[int] = range(1,17)
                ):
        super().__init__(source_unit)
        self.fundamental_pitch = fundamental_pitch
        self.harmonic_numbers  = harmonic_numbers

    def generate(self) -> List[MusicUnit]:
        return [self.harmonic_series(self.fundamental_pitch,
                               self.harmonic_numbers)]

    def harmonic_series(self, fundamental_pitch  : int,
                               harmonic_numbers: List[int] = range(1,17)) -> MusicUnit:
        # The harmonic series of a fundamental pitch
        unit = MusicUnit()
        for harmonic in harmonic_numbers:
            new_pitch = note.Pitch(fundamental_pitch).getHarmonic(harmonic)
            unit.append(new_pitch.midi)

        return unit

    def random_bass_harmonics(self):
        # Generate random harmonic chords based on bass pitches in source unit
        for bass_pitch in self.source_unit.pitch_nodes:
            random_harmonics = random.sample(range(4,21), random.randrange(3, 6))
            new_chord = self.harmonic_series(bass_pitch, random_harmonics)
            new_chord.transpose(interval.Interval(new_chord[0],
                                                  note.Pitch(bass_pitch),
                                inPlace=True))

            new_chord.duration = note.Duration(random.choice([self.source_unit.time.M21_QUARTER/2,
                                                              self.source_unit.time.M21_QUARTER/1]))

