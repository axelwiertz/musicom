"""A MusicUnit represents a technical unit of music, defined by sets of MusicEvents,"""
from typing import List, Tuple
from .base import Base

class MusicEvent:
    # A basic sound event with pitch, duration and volume
    def __init__(self,
                 pitch: int = None,
                 duration: int = None,
                 volume: int = None):
        self.pitch = pitch
        self.duration = duration
        self.volume = volume


class MusicUnit(Base):
    # A unit of music: a set of MusicEvents in sequence
    def __init__(self,
                name: str = 'Unit',
                pitch_nodes : List [int] = None,
                onset_intervals: List[int] = None,
                durations: List[int] = None,
                volumes: List[int] = None,
                onset_times: List[int] = None,
                ):
        super().__init__(name)
        # Pitch nodes (MIDI note numbers)
        # Initialize the MusicUnit with pitch nodes, onset intervals, durations, and volumes
        self._pitch_nodes = pitch_nodes if pitch_nodes else []
        self._volumes = volumes if volumes else []

        # Time intervals and durations
        self._durations = durations if durations else []
        self._onset_intervals = onset_intervals if onset_intervals else []


        self._events = []
        self._onset_times = onset_times if onset_times else []

    @property
    def pitch_nodes(self) -> list[int]:
        return self._pitch_nodes

    @property
    def pitch_intervals(self) -> list[int]:
        if len(self._pitch_nodes) < 2:
            return []
        return [self._pitch_nodes[i+1]-self._pitch_nodes[i] for i in range(len(self._pitch_nodes)-1)]

    @property
    def durations(self) -> list[int]:
        return self._durations

    @property
    def volumes(self) -> list[int]:
        return self._volumes

    @property
    def onset_times(self) -> list[int]:
        # Calculate onset times based on onset intervals
        times = []
        current_time = 0
        for interval in self._onset_intervals:
            times.append(current_time)
            current_time += interval
        return times

    @property
    def onset_intervals(self) -> list[int]:
        return self._onset_intervals



    @property
    def timesteps(self):
        # The sum of the onset intervals is the total number of timesteps in MusicTime
        return sum(self._onset_intervals)

    def add_event(self,
                  pitch: int = None,
                  duration: int = None,
                  volume: int = None,
                  ):        # Add a new MusicEvent to the MusicUnit
        self._events += [MusicEvent(pitch, duration, volume)]

    @property
    def events(self) -> list:
        return self._events

    def __add__(self, other) -> 'MusicUnit':
        # Combine two musical units
        new_unit = MusicUnit()
        for event in self.events:
            new_unit.add_event(event)
        for event in other.events:
            new_unit.add_event(event)

        return new_unit

    def __len__(self) -> int:
        # Return the number of pitch nodes in the MusicUnit 
        return len(self._pitch_nodes)

    def split(self, index: int) -> Tuple['MusicUnit', 'MusicUnit']:
        # Split the MusicUnit at the given index into two MusicUnits
        unit1 = MusicUnit(
            name=self.name + '_part1',
            pitch_nodes=self._pitch_nodes[:index],
            volumes=self._volumes[:index],
            onset_intervals=self._onset_intervals[:index],
            durations=self._durations[:index]
        )
        unit2 = MusicUnit(
            name=self.name + '_part2',
            pitch_nodes=self._pitch_nodes[index:],
            volumes=self._volumes[index:],
            onset_intervals=self._onset_intervals[index:],
            durations=self._durations[index:]
        )
        return unit1, unit2


    def append(self,
                pitch: int = None,
                duration: int = None,
                volume: int = None,
                onset_interval: int = None,
               ):
        self._pitch_nodes += [pitch]
        self._durations += [duration]
        self._volumes += [volume]

        self._onset_intervals += [onset_interval]


    def add_pitches_vertical(self, pitches: list[int], duration: int = 1):
        # Add multiple pitches vertically with the same duration
        for p in pitches:
            self.append(pitch=p, duration=duration)

    def clone(self) -> 'MusicUnit':
        # Create an exact copy of this MusicUnit instance
        return MusicUnit(
            name=self.name,
            pitch_nodes=self._pitch_nodes.copy(),
            volumes=self._volumes.copy(),
            onset_intervals=self._onset_intervals.copy(),
            durations=self._durations.copy()
        )


class MusicUnitGroup(Base):
    # A group of MusicUnits
    def __init__(self,
                 name: str = "UnitGroup",
                 units: list[MusicUnit] = None):
        super().__init__(name)
        self.units = units

    def add_unit(self, unit: MusicUnit):
        self.units.append(unit)

    def get_unit(self, index: int) -> MusicUnit:
        return self.units[index]