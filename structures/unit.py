"""A MusicUnit represents a technical unit of music, defined by sets of MusicEvents,"""
from copy import deepcopy
import numpy as np
from numpy import ndarray
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
    DTYPE = ('uint8', 'uint8', 'uint16', 'uint16')  # pitch, volume, start_tick, end_tick
    def __init__(self,
                 events: list[MusicEvent] | ndarray = None):

        if events is not None:
            """Internally stores events in a structured numpy array for efficiency"""
            self._data = np.array(
                object=[(e.pitch, e.volume, e.start_tick, e.end_tick) for e in self.events],
                dtype=self.DTYPE)
        else:
            self._data = np.array(object=[], dtype=self.DTYPE)

    @property
    def events(self) -> list[MusicEvent]:
        return [MusicEvent(pitch=e[MusicEvent.PITCH],
                           volume=e[MusicEvent.VOLUME],
                           start_tick=e[MusicEvent.START_TICK],
                           end_tick=e[MusicEvent.END_TICK]) for e in self._data]
    @property
    def data(self) -> ndarray:
        return self._data

    def  __len__(self):
        return len(self._data)

    def __add__(self, other) -> 'MusicEventSequence':
        new_seq = MusicEventSequence()
        new_seq._data = np.concatenate((self._data, other.data))
        return new_seq

    def add_event(self, event: MusicEvent | ndarray):
        self._data = np.append(self._data, np.array(
            [(event.pitch, event.volume, event.start_tick, event.end_tick)],
            dtype=self.DTYPE
        ))

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

    def len_ticks(self):
        """Return the length of the sequence in ticks."""
        if len(self._data) == 0:
            return 0
        return max(event.end_tick for event in self.events)

    @property
    def pitches(self) -> List[int]:
        """Return a list of all pitches in the sequence."""
        return [event.pitch for event in self.events]

    @property
    def pitch_intervals(self) -> List[int]:
        """Return a list of pitch intervals between consecutive events."""
        pitches = self.pitches
        if len(pitches) < 2:
            return []
        return [pitches[i+1] - pitches[i] for i in range(len(pitches)-1)]

    @property
    def volumes(self) -> List[int]:
        """Return a list of all volumes in the sequence."""
        return [event.volume for event in self.events]

    def durations(self) -> List[int]:
        """Return a list of all durations in the sequence."""
        return [event.duration for event in self.events]

@dataclass
class MusicUnit(Base, MusicEventSequence):
    # A unit of music: a set of MusicEvents in sequence
    def __init__(self,
                name: str = 'Unit',
                events: MusicEventSequence = None,
                 pitches: List[int] = None,
                ):
        super(Base).__init__(name)
        super(MusicEventSequence).__init__(events)

        if pitches is not None:
            # Initialize from a list of pitches with default values
            for pitch in pitches:
                self.add_event(MusicEvent(pitch=pitch))

    def old_set(self,
                   pitch_nodes: List[int] = None,         # Pitches (MIDI note numbers)
                   onset_intervals: List[int] = None,
                   durations: List[int] = None,
                   volumes: List[int] = None,
                   ):
        for i in range(len(pitch_nodes)):
            start_tick = sum(onset_intervals[:i]) if i < len(onset_intervals) else 0
            end_tick = start_tick + durations[i] if i < len(durations) else start_tick
            event = MusicEvent(
                pitch=pitch_nodes[i],
                volume=volumes[i] if i < len(volumes) else 100,
                start_tick=start_tick,
                end_tick=end_tick
            )
            self.add_event(event)


    def clone(self) -> 'MusicUnit':
        # Create a copy of the MusicUnit
        return deepcopy(self)

