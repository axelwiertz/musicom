"""Module for generating random music21 streams."""
from random import choice, randint
from typing import List
from generators.base import Generator
from structures.unit import MusicUnit

class StochasticGenerator(Generator):
    """Class for generating stochastic music21 streams."""

    def __init__(self,
                 seed_unit: MusicUnit,
                 length: int,
                 pitch_set: List[int],
                 duration_set: List[int]
                 ):
        super().__init__(seed_unit)
        self.length = length
        self.pitch_set = pitch_set
        self.duration_set = duration_set

    def generate(self) -> MusicUnit:
        for i in range(self.length):
            self.seed_unit.add_pitch(choice(self.pitch_set),
                          choice(self.duration_set),
                            onset_interval=1,
                            volume=randint(60, 100)
                          )

        return self.seed_unit

