""" Module to create from chords """
from typing import List
from structures import MusicUnit, MusicPitchPattern, MusicEvent
from .base import MusicGenerator
from converters.pattern import pattern_to_pitches

#TODO: Implement melody generator based on triad patterns

class PatternGenerator(MusicGenerator):
    """ Arpeggio generator class """

    def __init__(self,
                 patterns: List[MusicPitchPattern],
                 number_of_voices: int = None,
                 time_interval: int = None,
                 volume_in: int = None
                 ):
        super().__init__()
        if not patterns:
            raise ValueError("At least one pattern must be provided.")
        self.patterns = patterns
        self.number_of_voices = number_of_voices if number_of_voices is not None else 3
        self.timesteps_in = timesteps_in if timesteps_in is not None else 1
        self.volume_in = volume_in if volume_in is not None else 100

    def generate(self) -> List[MusicUnit]:
        """ Generate events based on patterns: parallel (chord) or sequential (arpeggio) """
        units = [MusicUnit() for _ in range(self.number_of_voices)]

        # Pitch generation
        for pattern in self.patterns:
            # Convert pattern to pitches
            pitch_nodes_ = pattern_to_pitches(pattern, pattern.tonic_octave)
            for i in range(self.number_of_voices):
                p = pitch_nodes_[i]
                e = MusicEvent(pitch=p,
                               volume=self.volume_in,
                               start_tick=0,
                               end_tick=self.timesteps_in,
                               )
                units[i].add_event(e)

            # Sequential arpeggio generation
            for pattern in self.patterns:
                # Convert pattern to pitches
                pitch_nodes_ = pattern_to_pitches(pattern, pattern.tonic_octave)
                events = []
                for i, p in enumerate(pitch_nodes_):
                    e = MusicEvent(pitch=p,
                                   volume=self.volume_in,
                                   start_tick=i*self.timesteps_in,
                                   end_tick= (i+1)*self.timesteps_in,
                                   )
                    events.append(e)
                
            units += MusicUnit(events=events)

            # given a pattern, return a list of units(voices),
            # starting in octave octave_in, and ascending
            # all lowest pitches of each pattern form one voice
            # all 2nd pitches of each pattern form a second voice, etc.,
            # event duration is timesteps_in
            for pattern in self.patterns:
                pitch_nodes_ = pattern_to_pitches(pattern, pattern.tonic_octave)
                for i in range(number_of_voices):
                    p = pitch_nodes_[i]
                    e = MusicEvent(pitch=p,
                                   volume=80,
                                   start_tick=0,
                                   end_tick=self.timesteps_in,
                                   )
                    units[i].add_event(e)

        return units

