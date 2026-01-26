""" Module to create from chords """
from typing import List
from structures import MusicUnit, MusicPitchClassPattern, MusicEvent
from .base import MusicGenerator
from converters.pattern import get_pitches_in_octave

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
        for i, pattern in enumerate(self.patterns):
            # Convert pattern to pitches
            pitches = get_pitches_in_octave(pattern, self.tonic_octaves[i])
            for j in range(self.number_of_voices):
                p = pitches[j]
                e = MusicEvent(pitch=p,
                               volume=self.volume_in,
                               start_tick=0,
                               end_tick=self.time_interval,
                               )
                units[j].add_event(e)

        # Sequential arpeggio generation
        for i, pattern in enumerate(self.patterns):
            # Convert pattern to pitches
            pitches = get_pitches_in_octave(pattern, self.tonic_octaves[i])
            events = []
            for j, pitch in enumerate(pitches):
                e = MusicEvent(pitch=pitch,
                               volume=self.volume_in,
                               start_tick=j*self.time_interval,
                               end_tick= (j+1)*self.time_interval,
                               )
                events.append(e)

            units += MusicUnit(events=events)

        # given a pattern, return a list of units(voices),
        # starting in octave octave_in, and ascending
        # all lowest pitches of each pattern form one voice
        # all 2nd pitches of each pattern form a second voice, etc.,
        # event duration is timesteps_in
        for i, pattern in enumerate(self.patterns):
            # Convert pattern to pitches
            pitches = get_pitches_in_octave(pattern, self.tonic_octaves[i])
            for v in range(self.number_of_voices):
                # Get pitch for the current voice
                p = pitches[v]
                e = MusicEvent(pitch=p,
                               volume=80,
                               start_tick=0,
                               end_tick=self.time_interval,
                               )
                units[v].add_event(e)

        return units

