from typing import List
from constants.tuning import TwelveTET
from structures.base import MusicBase
from structures.helix import Helix


class MusicUnit(MusicBase):
    # A musical unit: a sequence of pitches with timing and dynamics
    def __init__(self,
                 _id: int = 0,
                name: str = 'Unit',
                pitch_nodes : list [int] = (),
                onset_intervals: list[float] = (),
                durations: list[float] = (),
                volumes: list[int] = (),
                ):
        super().__init__(_id, name)
        self.pitch_nodes = pitch_nodes
        self.onset_intervals = onset_intervals
        self.durations = durations
        self.volumes = volumes

    def __add__(self, other):
        # Combine two musical units
        new_unit = MusicUnit()
        new_unit.pitch_nodes = self.pitch_nodes + other.pitch_nodes
        new_unit.onset_intervals = self.onset_intervals + other.onset_intervals
        new_unit.durations = self.durations + other.durations
        new_unit.volumes = self.volumes + other.volumes
        return new_unit

    @property
    def timesteps (self):
        # The sum of the onset intervals is the total number of timesteps in MusicTime
        return sum(self.onset_intervals)

    @property
    def pitch_intervals(self) -> List[int]:
        if len(self.pitch_nodes) < 2:
            return []
        return [self.pitch_nodes[i+1]-self.pitch_nodes[i] for i in range(len(self.pitch_nodes)-1)]

    def add_pitch (self, pitch, duration : int = 1, onset_interval : int = 1, volume: int = 100):
        self.pitch_nodes += [pitch]
        self.onset_intervals += [onset_interval]
        self.durations += [duration]
        self.volumes += [volume]

    def add_pitches_vertical (self, pitches, duration=4):
        for p in pitches:
            self.add_pitch(p,0, duration)





class PitchRegister(Helix):
    # Chromatic pitch helix
    ASCENDING = 1
    DESCENDING = -1
    def __init__(self,  pitch_class_start=TwelveTET.A,
                        octave_start=0,
                        pitch_class_end=TwelveTET.C,
                        octave_end=8,
                        num_pitch_classes: int = TwelveTET.TWELVE,
                        num_octaves: int = TwelveTET.OCTAVES,
                      ):
        # Represent as helix of (pitch_class, octave): (0, 4)
        super().__init__(num_pitch_classes, num_octaves)

        self.num_pitch_classes = num_pitch_classes
        self.num_octaves = num_octaves

        self.index_start = self.index_of(pitch_class_start, octave_start)
        self.index_end = self.index_of(pitch_class_end, octave_end)


    def transpose(self, i, interval_steps, direction=ASCENDING):
        # Transpose index i by interval_steps in direction (ASCENDING or DESCENDING)
        return (i + direction*interval_steps) % len(self.helix)

