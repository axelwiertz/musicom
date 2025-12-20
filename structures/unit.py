"""A MusicUnit represents a technical unit of music, defined by sets of MusicEvents,"""
from copy import deepcopy
import numpy as np
from dataclasses import dataclass
from typing import List, Tuple
from .base import Base

@dataclass
class MusicEvent:
    """A basic music event with pitch, volume, start and end ticks."""
    """ equivalent to a Note in music21 """
    PITCH = 0
    VOLUME = 1
    START_TICK = 2
    END_TICK = 3
    def __init__(self,
                pitch: int = None,
                volume: int = None,
                start_tick: int = None,
                end_tick: int = None,
                ):
        self._data = (pitch, volume, start_tick, end_tick)

    @property
    def pitch(self) -> int:
        return self._data[self.PITCH]
    @pitch.setter
    def pitch(self, value: int):
        self._data = (value, self._data[self.VOLUME], self._data[self.START_TICK], self._data[self.END_TICK])
    @property
    def volume(self) -> int:
        return self._data[self.VOLUME]
    @volume.setter
    def volume(self, value: int):
        self._data = (self._data[self.PITCH], value,  self._data[self.START_TICK], self._data[self.END_TICK])
    @property
    def start_tick(self) -> int:
        return self._data[self.START_TICK]
    @start_tick.setter
    def start_tick(self, value: int):
        self._data = (self._data[self.PITCH], self._data[self.VOLUME], value, self._data[self.END_TICK])
    @property
    def end_tick(self) -> int:
        return self._data[self.END_TICK]
    @end_tick.setter
    def end_tick(self, value: int):
        self._data = (self._data[self.PITCH], self._data[self.VOLUME], self._data[self.START_TICK], value)
    @property
    def duration(self) -> int:
        if self._data[self.END_TICK] is not None and self._data[self.START_TICK] is not None:
            return self._data[self.END_TICK] - self._data[self.START_TICK]
        return 0


@dataclass
class MusicEventSequence:
    # A group of MusicEvents
    def __init__(self,
                 events: list[MusicEvent] = None):

        if events is None:
            self._data = []
        else:
            """Internally stores events in a structured numpy array for efficiency"""
            self._data = np.array([
                (e.pitch, e.volume, e.start_tick, e.end_tick)
                for e in self.events
            ], dtype=('uint8', 'uint8', 'uint16', 'uint16'))

    @property
    def events(self) -> list[MusicEvent]:
        return self._data

    def  __len__(self):
        return len(self._data)

    def __add__(self, other) -> 'MusicEventSequence':
        new_sequence = MusicEventSequence(self._data.copy())
        for event in other.events:
            new_sequence.add_event(event)
        return new_sequence

    def append(self, other) -> 'MusicEventSequence':
        for event in other.events:
            self.add_event(event)
        return self

    def add_event(self, event: MusicEvent):
        self._data.append(event)

    def split(self, index: int) -> Tuple['MusicEventSequence', 'MusicEventSequence']:
        seq1 = MusicEventSequence(self._data[:index])
        seq2 = MusicEventSequence(self._data[index:])
        return seq1, seq2

    def __getitem__(self, index):
        return self._data[index]

    def __setitem__(self, index, value):
        self._data[index] = value

    def __repr__(self):
        return f"<MusicEventSequence({len(self._data)} events)>"

    def get_pitches_at_tick(self, tick: int) -> List[int]:
        """Return all pitches active at a given time."""
        pitches = []
        for event in self.events:
            if event.start_tick <= tick < event.end_tick:
                pitches.append(event.pitch)
        return pitches


@dataclass
class MusicUnit(Base):
    # A unit of music: a set of MusicEvents in sequence
    def __init__(self,
                name: str = 'Unit',
                pitch_nodes : List [int] = None,
                onset_intervals: List[int] = None,
                durations: List[int] = None,
                volumes: List[int] = None,
                ):
        super().__init__(name)
        # Pitch nodes (MIDI note numbers)
        # Initialize the MusicUnit with pitch nodes, onset intervals, durations, and volumes
        self._pitch_nodes = pitch_nodes if pitch_nodes else []
        self._volumes = volumes if volumes else []

        # Time intervals and durations
        self._durations = durations if durations else []
        self._onset_intervals = onset_intervals if onset_intervals else []

        self._events = MusicEventSequence()
        for i in range(len(self._pitch_nodes)):
            start_tick = sum(self._onset_intervals[:i]) if i < len(self._onset_intervals) else 0
            end_tick = start_tick + self._durations[i] if i < len(self._durations) else start_tick
            event = MusicEvent(
                pitch=self._pitch_nodes[i],
                volume=self._volumes[i] if i < len(self._volumes) else 100,
                start_tick=start_tick,
                end_tick=end_tick
            )
            self._events.add_event(event)

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

    def clone(self) -> 'MusicUnit':
        # Create a copy of the MusicUnit
        return deepcopy(self)

