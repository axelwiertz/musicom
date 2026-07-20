"""Defines MusicEvent and MusicUnit classes for representing musical events and sequences."""
import numpy as np
from numpy import ndarray
from dataclasses import dataclass
from typing import List, Tuple
from .timegrid import MusicTimeGrid

@dataclass
class MusicEvent:
    """A basic music event with pitch, volume, start and end ticks."""
    PITCH = 0
    VOLUME = 1
    START_TICK = 2
    END_TICK = 3
    DTYPE = np.dtype([
        ('pitch', 'uint8'),
        ('volume', 'uint8'),
        ('start_tick', 'uint16'),
        ('end_tick', 'uint16'),
    ])  # pitch, volume, start_tick, end_tick

    def __init__(self,
                pitch: int = 0,
                volume: int = 100,
                start_tick: int = 0,
                end_tick: int = 0,
                ):
        self.data = (pitch, volume, start_tick, end_tick)

    @property
    def pitch(self) -> int:
        return self.data[self.PITCH]
    @pitch.setter
    def pitch(self, value: int):
        self.data = (value, self.data[self.VOLUME], self.data[self.START_TICK], self.data[self.END_TICK])
    @property
    def volume(self) -> int:
        return self.data[self.VOLUME]
    @volume.setter
    def volume(self, value: int):
        self.data = (self.data[self.PITCH], value,  self.data[self.START_TICK], self.data[self.END_TICK])
    @property
    def start_tick(self) -> int:
        return self.data[self.START_TICK]
    @start_tick.setter
    def start_tick(self, value: int):
        self.data = (self.data[self.PITCH], self.data[self.VOLUME], value, self.data[self.END_TICK])
    @property
    def end_tick(self) -> int:
        return self.data[self.END_TICK]
    @end_tick.setter
    def end_tick(self, value: int):
        self.data = (self.data[self.PITCH], self.data[self.VOLUME], self.data[self.START_TICK], value)
    @property
    def duration(self) -> int:
        if self.data[self.END_TICK] > self.data[self.START_TICK]:
            return self.data[self.END_TICK] - self.data[self.START_TICK]
        return 0

@dataclass
class MusicUnit:
    """A MusicUnit represents a technical unit of music, defined by sets of MusicEvents,"""
    # A unit of music: a set of MusicEvents in sequence
    def __init__(self,
                events: list[MusicEvent] | ndarray = None,
                pitches: List[int] = None,
                time_grid : MusicTimeGrid = None,
                ):

        """Internally stores events in a structured numpy array for efficiency"""
        self.data = np.empty(0, dtype=MusicEvent.DTYPE)
        self.time_grid = time_grid
        if events is not None:
            if isinstance(events, ndarray):
                arr = events
                # If already structured with correct dtype, keep it
                if arr.dtype == MusicEvent.DTYPE:
                    self.data = arr
                else:
                    arr = np.asarray(arr)
                    # Convert from plain (n,4) numeric array to structured
                    if arr.ndim == 2 and arr.shape[1] == 4:
                        self.data = np.array([tuple(row) for row in arr], dtype=MusicEvent.DTYPE)
                    else:
                        # Attempt a safe cast for other ndarray shapes
                        self.data = arr.astype(MusicEvent.DTYPE, copy=False)
            else:
                self.data = np.array(
                    [(e.pitch, e.volume, e.start_tick, e.end_tick) for e in events],
                    dtype=MusicEvent.DTYPE)
        else:
            if pitches is not None:
                # Initialize from a list of pitches with default values
                for i, pitch in enumerate(pitches):
                    self.add_event(MusicEvent(pitch=pitch, volume=100, start_tick=i, end_tick=(i+1)))

    @property
    def events(self) -> list[MusicEvent]:
        return [MusicEvent(pitch=e[MusicEvent.PITCH],
                           volume=e[MusicEvent.VOLUME],
                           start_tick=e[MusicEvent.START_TICK],
                           end_tick=e[MusicEvent.END_TICK]) for e in self.data]

    def  __len__(self):
        return len(self.data)

    def __add__(self, other) -> 'MusicUnit':
        """Concatenate two MusicUnits."""
        new_seq = MusicUnit()
        new_seq.data = np.concatenate((self.data, other.data))
        return new_seq

    def add_event(self, event: MusicEvent | ndarray):
        """Add a MusicEvent to the sequence."""
        if isinstance(event, MusicEvent):
            self.data = np.append(self.data, np.array(
                [(event.pitch, event.volume, event.start_tick, event.end_tick)],
                dtype=MusicEvent.DTYPE
            ))
        elif isinstance(event, ndarray):
            self.data = np.append(self.data, event)

    def split(self, index: int) -> Tuple['MusicUnit', 'MusicUnit']:
        """Split the sequence at the given index into two sequences."""
        seq1 = MusicUnit(self.data[:index])
        seq2 = MusicUnit(self.data[index:])
        return seq1, seq2

    def __getitem__(self, index):
        return self.data[index]

    def __setitem__(self, index, value):
        self.data[index] = value

    def __repr__(self):
        return f"<MusicUnit({len(self.data)} events)>"

    def get_pitches_at_tick(self, tick: int) -> List[int]:
        """Return all pitches active at a given time."""
        pitches = []
        for event in self.events:
            if event.start_tick <= tick < event.end_tick:
                pitches.append(event.pitch)
        return pitches

    def len_ticks(self):
        """Return the length of the sequence in ticks."""
        if len(self.data) == 0:
            return 0
        return max(event.end_tick for event in self.events)

    @property
    def pitches(self) -> List[int]:
        """Return a list of all pitches in the unit."""
        return [event.pitch for event in self.events]

    @property
    def pitch_intervals(self) -> List[int]:
        """Return a list of pitch intervals between consecutive events."""
        pitches = self.pitches
        if len(pitches) < 2:
            return []
        else:
            intervals = []
            for i in range(len(pitches) - 1):
                # cast to int: MusicEvent.pitch is uint8; raw subtraction overflows
                intervals.append(int(pitches[i + 1]) - int(pitches[i]))
        return intervals
    @property
    def volumes(self) -> List[int]:
        """Return a list of all volumes in the sequence."""
        return [event.volume for event in self.events]
    @property
    def durations(self) -> List[int]:
        """Return a list of all durations in the sequence."""
        return [event.duration for event in self.events]
    @property
    def onset_intervals(self) -> List[int]:
        """Return a list of onset intervals between consecutive events."""
        onsets = [event.start_tick for event in self.events]
        if len(onsets) < 2:
            return []
        else:
            intervals = []
            for i in range(len(onsets)-1):
                intervals.append(onsets[i+1] - onsets[i])

        return intervals

    def clone(self) -> 'MusicUnit':
        # Create a copy of the MusicUnit
        return MusicUnit(self.data.copy())


    """Operations"""

    def transpose(self, interval_: int):
        """Transpose the pitches of a MusicUnit by a given interval."""
        for e in self.data:
            e[MusicEvent.PITCH] += interval_

    def retrograde(self):
        """Reverse the order of the events in the unit"""
        self.data = self.data[::-1]

    def invert(self, pivot: int):
        """Invert the pitches of a MusicUnit around a given pivot pitch."""
        for e in self.data:
            e[MusicEvent.PITCH] = pivot + (pivot - e[MusicEvent.PITCH])

    def augment(self, factor: float):
        """Augment the durations of the events by a given factor."""
        for e in self.data:
            duration = e[MusicEvent.END_TICK] - e[MusicEvent.START_TICK]
            new_duration = int(duration * factor)
            e[MusicEvent.END_TICK] = e[MusicEvent.START_TICK] + new_duration