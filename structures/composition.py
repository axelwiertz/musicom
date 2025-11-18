"""
Musicom structures module
Music composition structures
"""
from typing import List

from constants.twelvetet import TwelveTET
from constants.midi import MIDIinstrument
from structures.helix import Helix
from structures.circle import Circle

class MusicTime (Circle):
    # Rhythm and meter
    def __init__(self,
                 timesteps: int = 8, # Number of timesteps (ticks) per cycle
                 beats_in_measure: int = 4,
                 beat_note: int = 4,
                 bpm: int = 100):
        # Timestep is the smallest rhythm relative unit, represented as integer
        self.timesteps = timesteps
        super().__init__(timesteps, labels=[str(i+1) for i in range(timesteps)])
        # Meter: measure cycle of beats
        self.beats_in_measure = beats_in_measure
        self.beat_note = beat_note
        self.bpm = bpm


class MusicBase:
    # Base class for musical structures
    def __init__(self, name: str = 'MusicBase'):
        self.name = name


class MusicUnit(MusicBase):
    # A musical unit: a sequence of pitches with timing and dynamics
    def __init__(self,
                 name: str = 'Unit',
                time: MusicTime = MusicTime(),
                pitch_nodes : list [int] = (),
                onset_intervals: list[float] = (),
                durations: list[float] = (),
                volumes: list[int] = (),
                ):
        super().__init__(name)
        self.time = time
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

# --- new: MusicSection ---
class MusicSection (MusicBase):
    """A section is an vertical collection of MusicUnit objects
    Minimal contract:
    - inputs: list of MusicUnit (optional)
    - outputs: query methods (length, total_timesteps)
    """
    def __init__(self,
                 name: str = 'Section',
                 units: List[MusicUnit] = ()):
        super().__init__(name)
        self.units = units

    def append(self, unit: MusicUnit):
        """Append a MusicUnit to the section."""
        self.units.append(unit)

    def extend(self, units: list[MusicUnit]):
        """Extend section with an iterable of MusicUnit."""
        self.units.extend(units)

    def insert(self, index: int, unit: MusicUnit):
        self.units.insert(index, unit)

    def remove_at(self, index: int):
        """Remove and return unit at index."""
        return self.units.pop(index)

    def __len__(self):
        return len(self.units)

    def __iter__(self):
        return iter(self.units)

    def __getitem__(self, idx):
        return self.units[idx]


class MusicVoice(MusicBase):
    # A horizontal musical voice
    def __init__(self,
                 name: str = 'Voice',
                 sections: List[MusicSection] = (),
                 midi_instrument: int = MIDIinstrument.PIANO,
                 ):
        super().__init__(name)
        self.midi_instrument = midi_instrument
        self.sections = sections


class MusicComposition:
    # A full musical composition
    def __init__(self,
                 title: str = "Composition",
                 voices : list[MusicVoice] = (),
                 sections: list[MusicSection] = (),
                ):
        self.title = title
        self.voices = voices
        self.sections = sections


class PitchRegister(Helix):
    # Chromatic pitch helix
    ASCENDING = 1
    DESCENDING = -1
    def __init__(self,  pitchclass_start=TwelveTET.A,
                        octave_start=0,
                        pitchclass_end=TwelveTET.C,
                        octave_end=8,
                        num_pitchclasses: int = TwelveTET.TWELVE,
                        num_octaves: int = TwelveTET.OCTAVES,
                      ):
        # Represent as helix of (pitchclass, octave): (0, 4)
        super().__init__(num_pitchclasses, num_octaves)

        self.num_pitchclasses = num_pitchclasses
        self.num_octaves = num_octaves

        self.index_start = self.index_of(pitchclass_start, octave_start)
        self.index_end = self.index_of(pitchclass_end, octave_end)

        self.tt = TwelveTET()
        self.midi = [self.tt.name_to_midi(self.tt.PITCH_CLASS_NAMES_SHARP[pitchclass]+str(octave))
                for (pitchclass, octave) in self.helix]

    def transpose(self, i, interval_steps, direction=ASCENDING):
        # Transpose index i by interval_steps in direction (ASCENDING or DESCENDING)
        return (i + direction*interval_steps) % len(self.helix)

