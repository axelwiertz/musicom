""" Module to create from chords """
from typing import List
from structures import MusicUnit, MusicPattern, MusicEvent
from .base import MusicGenerator
from converters.pattern import pattern_to_pitches


class SequentialPatternGenerator(MusicGenerator):
    """ Arpeggio generator class """

    def __init__(self,
                 patterns: List[MusicPattern],
                 octave_in: int = 4,
                 timesteps_in: int = 1,
                 volume_in: int = 80
                 ):
        super().__init__()
        self.patterns = patterns
        self.octave_in = octave_in
        self.timesteps_in = timesteps_in
        self.volume_in = volume_in

    def generate(self) -> List[MusicUnit]:
        """ Generate sequential events of the patterns (arpeggios) """
        units = []
        for pattern in self.patterns:
            # Convert pattern to pitches
            pitch_nodes_ = pattern_to_pitches(pattern, self.octave_in)
            events = []
            for i, p in enumerate(pitch_nodes_):
                e = MusicEvent(pitch=p,
                               volume=self.volume_in,
                               start_tick=i*self.timesteps_in,
                               end_tick= (i+1)*self.timesteps_in,
                               )
                events.append(e)
                
            units += MusicUnit(events=events)
            
        return units

class ParallelPatternChordGenerator(MusicGenerator):
    """ Chord generator class """

    def __init__(self,
                 patterns: List[MusicPattern],
                 number_of_voices : int = 3,
                 octave_in: int = 4,
                 timesteps_in = 2
                 ):
        super().__init__()
        self.patterns = patterns
        self.number_of_voices = number_of_voices
        self.octave_in = octave_in
        self.timesteps_in = timesteps_in

    def generate(self) -> list[MusicUnit]:
        """ Generate a stream of voices from the chord progression """
        return create_stream_from_chords(self.patterns,
                                         self.number_of_voices,
                                         self.octave_in,
                                         self.timesteps_in
                                         )

# TODO: improve function to handle chords with different number of notes

def create_stream_from_chords (patterns: list[MusicPattern],
                               number_of_voices : int = 3,
                               octave_in: int = 4,
                               timesteps_in = 2) -> list[MusicUnit]:
    # given a pattern, return a list of units(voices),
    # starting in octave octave_in, and ascending
    # all lowest pitches of each pattern form one voice
    # all 2nd pitches of each pattern form a second voice, etc.,
    # event duration is timesteps_in
    voices_units = [MusicUnit() for _ in range(number_of_voices)]
    for pattern in patterns:
        pitch_nodes_ = pattern_to_pitches(pattern, octave_in)
        for i in range(number_of_voices):
            p = pitch_nodes_[i]
            e = MusicEvent(pitch=p,
                           volume=80,
                           start_tick=0,
                           end_tick=timesteps_in,
                           )
            voices_units[i].add_event(e)

    return voices_units

