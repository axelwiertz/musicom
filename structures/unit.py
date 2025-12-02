"""A MusicUnit represents a technical unit of music, defined by sequences of pitches,"""
from typing import List, Tuple
import numpy as np
from utilities.config import Config
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
        # Initialize the MusicUnit with pitch nodes, onset intervals, durations, and volumes
        self.pitch_nodes = pitch_nodes
        # Ensure all lists have the same length, defaulting to 1 or 100 as needed
        if not onset_intervals or len(onset_intervals) != len(pitch_nodes):
            self.onset_intervals = [Config.DEFAULT_ONSET_INTERVAL] * len(pitch_nodes)
        else:
            self.onset_intervals = onset_intervals
        if not durations or len(durations) != len(pitch_nodes):
            self.durations = [Config.DEFAULT_DURATION] * len(pitch_nodes)
        else:
            self.durations = durations
        if not volumes or len(volumes) != len(pitch_nodes):
            self.volumes = [Config.DEFAULT_VOLUME] * len(pitch_nodes)
        else:
            self.volumes = volumes

        self._data = np.array ([self.pitch_nodes,
                                self.onset_intervals,
                                self.durations,
                                self.volumes])

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

    def split(self, index: int) -> Tuple['MusicUnit', 'MusicUnit']:
        # Split the MusicUnit at the given index into two MusicUnits
        unit1 = MusicUnit(
            _id=self._id,
            name=self.name + '_part1',
            pitch_nodes=self.pitch_nodes[:index],
            onset_intervals=self.onset_intervals[:index],
            durations=self.durations[:index],
            volumes=self.volumes[:index]
        )
        unit2 = MusicUnit(
            _id=self._id,
            name=self.name + '_part2',
            pitch_nodes=self.pitch_nodes[index:],
            onset_intervals=self.onset_intervals[index:],
            durations=self.durations[index:],
            volumes=self.volumes[index:]
        )
        return unit1, unit2

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
