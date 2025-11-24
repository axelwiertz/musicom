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
                 units: List[MusicUnit] = (),
                 midi_instrument: int = MidiInstrument.PIANO,
                 ):
        super().__init__(name)
        self.midi_instrument = midi_instrument
        self.units = units

class MusicComposition:
    # A full musical composition
    def __init__(self,
                 title: str = "Composition",
                 voices : list[MusicVoice] = (),
                 sections: list[MusicSection] = ()
                ):
        self.title = title
        self.voices = voices
        self.sections = sections

