""" Module to create from chords """
from typing import List
from structures import MusicUnit, MusicPitchClassPattern, MusicEvent
from .base import MusicGenerator
from converters.pattern import pattern_to_pitches

#TODO: Implement melody generator based on triad patterns

class PatternGenerator(MusicGenerator):
    """ Arpeggio generator class """

    def __init__(self,
                 patterns: List[MusicPitchClassPattern],
                 tonic_octaves: List[int] = None,
                 number_of_voices: int = None,
                 time_interval: int = None,
                 volume_in: int = None
                 ):
        super().__init__()
        if not patterns:
            raise ValueError("At least one pattern must be provided.")
        self.patterns = patterns
        self.tonic_octaves = tonic_octaves if tonic_octaves is not None else [4 for _ in patterns]
        self.number_of_voices = number_of_voices if number_of_voices is not None else 3
        self.time_interval = time_interval if time_interval is not None else 1
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
                               end_tick=self.time_interval,
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
                               start_tick=i*self.time_interval,
                               end_tick= (i+1)*self.time_interval,
                               )
                events.append(e)

            units += MusicUnit(events=events)

        # given a pattern, return a list of units(voices),
        # starting in octave octave_in, and ascending
        # all lowest pitches of each pattern form one voice
        # all 2nd pitches of each pattern form a second voice, etc.,
        # event duration is timesteps_in
        for p, pattern in enumerate(self.patterns):
            pitch_nodes_ = pattern_to_pitches(pattern, self.tonic_octaves[p])
            for v in range(self.number_of_voices):
                p = pitch_nodes_[v]
                e = MusicEvent(pitch=p,
                               volume=80,
                               start_tick=0,
                               end_tick=self.time_interval,
                               )
                units[v].add_event(e)

        return units

