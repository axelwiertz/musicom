"""A MusicUnit represents a technical unit of music, defined by sequences of pitches,"""
from typing import List
from structures.base import MusicBase

class MusicUnit(MusicBase):
    # A technical unit of music: a sequence of pitches with onset intervals, durations, and volumes
    def __init__(self,
                 _id: int = 0,
                name: str = 'Unit',
                pitch_nodes : list [int] = (),
                onset_intervals: list[int] = (),
                durations: list[int] = (),
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

    def __len__(self):
        return len(self.pitch_nodes)

    @property
    def pitch_intervals(self) -> List[int]:
        if len(self.pitch_nodes) < 2:
            return []
        return [self.pitch_nodes[i+1]-self.pitch_nodes[i] for i in range(len(self.pitch_nodes)-1)]

    @property
    def timesteps (self):
        # The sum of the onset intervals is the total number of timesteps in MusicTime
        return sum(self.onset_intervals)

    def append (self,
                   pitch : int = 60,
                   duration : int = 1,
                   onset_interval : int = 1,
                   volume: int = 100):
        self.pitch_nodes += [pitch]
        self.onset_intervals += [onset_interval]
        self.durations += [duration]
        self.volumes += [volume]


    def add_pitches_vertical (self, pitches, duration=4):
        for p in pitches:
            self.append(pitch=p, duration=duration)

    def clone(self) -> 'MusicUnit':
        # Create a copy of this MusicUnit
        return MusicUnit(
            _id=self._id,
            name=self.name,
            pitch_nodes=self.pitch_nodes.copy(),
            onset_intervals=self.onset_intervals.copy(),
            durations=self.durations.copy(),
            volumes=self.volumes.copy()
        )
