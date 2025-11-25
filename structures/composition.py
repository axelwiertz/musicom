"""
Musicom structures module
Music composition structures
"""

from typing import List
from constants.midi import MidiInstrument
from structures.base import MusicBase
from structures.unit import MusicUnit



class MusicSection (MusicBase):
    """A section is a vertical collection of MusicUnit objects"""
    def __init__(self,
                 _id: int = 0,
                 name: str = 'Section',
                 units: List[MusicUnit] = ()):
        super().__init__(_id, name)
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
    """Represents a voice in the project."""
    # A horizontal musical voice
    def __init__(self,
                 _id: int,
                 name: str = 'Piano voice',
                 midi_instrument: int = MidiInstrument.PIANO,
                 ):
        super().__init__(_id, name)
        self.midi_instrument = midi_instrument


class MusicComposition (MusicBase):
    # A full musical composition
    def __init__(self,
                    _id: int = 0,
                 name: str = "Composition",
                 voices : list[MusicVoice] = (),
                 sections: list[MusicSection] = ()
                ):
        super().__init__(_id, name)
        self.voices = voices
        self.sections = sections

