"""
Musicom generators module
harmonic functions
"""
from typing import List
from music21 import chord, note, stream, interval
from structures import MusicUnit, PitchRange

from generators import Generator

import random
from base import TwelveTET
from structures.rhythm import MusicTime

class HarmonicFunction(Generator):
    def __init__(self,
                    source_unit      : MusicUnit,
                 fundamental_pitch : int,
                 harmonic_numbers  : list[int] = range(1,17)
                 ):
        super().__init__(source_unit)
        self.fundamental_pitch = fundamental_pitch
        self.harmonic_numbers  = harmonic_numbers

    def generate(self) -> List[MusicUnit]:
        return self.harmonic_series(self.fundamental_pitch,
                               self.harmonic_numbers)

    def harmonic_series (self, fundamental_pitch  : int,
                               harmonic_numbers: List[int] = range(1,17)) -> chord.Chord:
        # The harmonic series of a fundamental pitch

        harmonic_chord = chord.Chord()
        stream_out = stream.Stream()
        for harmonic in harmonic_numbers:
            new_pitch = note.Pitch(fundamental_pitch).getHarmonic(harmonic)
            harmonic_chord.add (note.Note(new_pitch.midi))
            stream_out.append (note.Note(new_pitch))

        return harmonic_chord

    def random_bass_harmonics(self):
        for bass_pitch in self.source_unit.pitch_nodes:
            random_harmonics = random.sample(range(4,21), random.randrange(3, 6))
            new_chord = self.harmonic_series(bass_pitch, random_harmonics)
            new_chord.transpose(interval.Interval(new_chord[0],
                                                  note.Pitch(bass_pitch),
                                inPlace=True))

            new_chord.duration = note.Duration(random.choice([self.source_unit.time.M21_QUARTER/2,
                                                              self.source_unit.time.M21_QUARTER/1]))

