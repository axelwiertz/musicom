""" Conon transformator """
from typing import List
from structures.unit import MusicUnit
from structures.factory import MusicTransformator


class CanonTransformator(MusicTransformator):
    # Voices in a canon
    VOICE1 = 0
    VOICE2 = 1
    VOICE3 = 2
    VOICE4 = 3
    VOICE5 = 4

    def __init__(self, source_unit : MusicUnit,
                 timesteps_delay: int = 4,
                 number_of_voices: int = 5,
                 transpositions : List[int] = (0,0,-12,-24,-12)
                 ):
        super().__init__(source_unit)
        self.timesteps_delay = timesteps_delay
        self.number_of_voices = number_of_voices
        # extra transpositions for different voices (e.g. +12, -24, ...)
        self.transpositions = transpositions

    def produce(self) -> List[MusicUnit]:
        # and turn it into a canon. Add extra transpositions to some number_of_voices to create some diversity
        units = []

        #TODO: Add delay_time
        initial_rests = [i * self.timesteps_delay for i in range(self.number_of_voices)]

        stacking = 3
        canonized = self.number_of_voices * stacking
        for v in range(self.number_of_voices):
            #TODO: Add initial rests to each voice
            #TODO : Add stacking logic
            #TODO: Adjust onsets to accomodate delays
            units.append(self.source_unit.clone().transpose(self.transpositions[v]))

        return units