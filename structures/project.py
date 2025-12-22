"""Defines the Project, Section, and Voice classes for the music composition framework."""
from typing import List
from .base import Base
from .matrix import MusicMatrix
from .time import MusicTime
from .pattern import MusicPattern
from .pitch import PitchRange
from .instrument import MidiInstrument

class MusicVoice(Base):
    """Represents a horizontal voice in the project."""
    def __init__(self,
                 name: str = 'Voice',
                 pitch_range: PitchRange = None,
                 midi_instrument: int = MidiInstrument.PIANO,
                 row_index: int = None,
                 ):
        super().__init__(name)
        self.pitch_range = pitch_range
        self.midi_instrument = midi_instrument
        self.row_index = row_index


class MusicSection (Base):
    """Represents a project section, containing columns of a matrix."""
    def __init__(self,
                 name: str = None,
                 start_col_index: int = None,
                 end_col_index: int = None,
                 ):
        super().__init__(name)
        # The `Section` class contains a `MusicMatrix`
        self._start_col_index = start_col_index
        self._end_col_index = end_col_index

    @property
    def start_col_index(self) -> int:
        return self._start_col_index
    @property
    def end_col_index(self) -> int:
        return self._end_col_index


# The `Project` class is the top-level container
class MusicProject (Base):
    """Represents the entire project structure."""
    def __init__(self,
                 name: str = None,
                 pattern: MusicPattern = None,
                 time: MusicTime = None,
                 sections: List[MusicSection] = None,
                 voices: List[MusicVoice] = None,
                 matrix: MusicMatrix = None,
                 ):
        super().__init__(name)
        self.name = name
        self.pattern = pattern
        self.time = time
        self.sections = sections
        self.voices = voices
        self.matrix = matrix

    def __repr__(self):
        return f"<MusicProject(name={self.name}, sections={len(self.sections) if self.sections else 0}, voices={len(self.voices) if self.voices else 0})>"

