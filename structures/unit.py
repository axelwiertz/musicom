"""A MusicUnit represents a technical unit of music, defined by sequences of pitches,"""
from typing import List, Tuple
import numpy as np
from utilities.config import Config
from .base import Base

class SoundEvent:
    # A basic sound event with pitch, volume, duration, onset interval, and volume
    def __init__(self,
                 pitch: int = 60,
                 duration: int = 1,
                 onset_interval: int = 1,
                 volume: int = 100):
        self.pitch = pitch
        self.volume = volume

        self.duration = duration
        self.onset_interval = onset_interval

class MusicUnit(Base):
    # A unit of music: a set of MusicSoundEvents
    def __init__(self,
                name: str = 'Unit',
                pitch_nodes : list [int] = (),
                onset_intervals: list[int] = (),
                durations: list[int] = (),
                volumes: list[int] = (),
                ):
        super().__init__(name)
        # Pitch nodes (MIDI note numbers)
        # Initialize the MusicUnit with pitch nodes, onset intervals, durations, and volumes
        self.pitch_nodes = pitch_nodes
        if not volumes or len(volumes) != len(pitch_nodes):
            self.volumes = [Config.DEFAULT_VOLUME] * len(pitch_nodes)
        else:
            self.volumes = volumes

        # Time intervals and durations
        # Ensure all lists have the same length, defaulting to 1 or 100 as needed
        if not onset_intervals or len(onset_intervals) != len(pitch_nodes):
            self.onset_intervals = [Config.DEFAULT_ONSET_INTERVAL] * len(pitch_nodes)
        else:
            self.onset_intervals = onset_intervals
        if not durations or len(durations) != len(pitch_nodes):
            self.durations = [Config.DEFAULT_DURATION] * len(pitch_nodes)
        else:
            self.durations = durations

        self._data = np.array ([self.pitch_nodes,
                                self.onset_intervals,
                                self.durations,
                                self.volumes])

    def __add__(self, other):
        # Combine two musical units
        new_unit = MusicUnit()
        new_unit.pitch_nodes = self.pitch_nodes + other.pitch_nodes
        new_unit.volumes = self.volumes + other.volumes
        new_unit.onset_intervals = self.onset_intervals + other.onset_intervals
        new_unit.durations = self.durations + other.durations
        return new_unit

    def __len__(self):
        return len(self.pitch_nodes)

    def split(self, index: int) -> Tuple['MusicUnit', 'MusicUnit']:
        # Split the MusicUnit at the given index into two MusicUnits
        unit1 = MusicUnit(
            name=self.name + '_part1',
            pitch_nodes=self.pitch_nodes[:index],
            volumes=self.volumes[:index],
            onset_intervals=self.onset_intervals[:index],
            durations=self.durations[:index]
        )
        unit2 = MusicUnit(
            name=self.name + '_part2',
            pitch_nodes=self.pitch_nodes[index:],
            volumes=self.volumes[index:],
            onset_intervals=self.onset_intervals[index:],
            durations=self.durations[index:]
        )
        return unit1, unit2

    @property
    def pitch_intervals(self) -> List[int]:
        if len(self.pitch_nodes) < 2:
            return []
        return [0]+[self.pitch_nodes[i+1]-self.pitch_nodes[i] for i in range(len(self.pitch_nodes)-1)]

    @property
    def timesteps(self):
        # The sum of the onset intervals is the total number of timesteps in MusicTime
        return sum(self.onset_intervals)

    def append(self,
                   pitch : int = 60,
                   duration : int = 1,
                   onset_interval : int = 1,
                   volume: int = 100):
        self.pitch_nodes += [pitch]
        self.volumes += [volume]

        self.onset_intervals += [onset_interval]
        self.durations += [duration]


    def add_pitches_vertical(self, pitches: List[int], duration=4):
        # Add multiple pitches vertically with the same duration
        for p in pitches:
            self.append(pitch=p, duration=duration)

    def clone(self) -> 'MusicUnit':
        # Create an exact copy of this MusicUnit instance
        return MusicUnit(
            name=self.name,
            pitch_nodes=self.pitch_nodes.copy(),
            volumes=self.volumes.copy(),
            onset_intervals=self.onset_intervals.copy(),
            durations=self.durations.copy()
        )

class EmptyMusicUnit(MusicUnit):
    # A MusicUnit representing silence
    def __init__(self, timesteps: int = 4):
        super().__init__(name='EmptyUnit')
        self.onset_intervals = [timesteps]
        self.pitch_nodes = []
        self.durations = []
        self.volumes = []

class MusicUnitGroup(Base):
    # A group of MusicUnits
    def __init__(self,
                 name: str = "UnitGroup",
                 units: List[MusicUnit] = None):
        super().__init__(name)
        self.units = units

    def add_unit(self, unit: MusicUnit):
        self.units.append(unit)

    def get_unit(self, index: int) -> MusicUnit:
        return self.units[index]