"""Defines the Project, Section, and Voice classes for the music composition framework."""
from typing import List

from . import MusicLinearTime
from .base import Base
from .matrix import UnitMatrix
from .time import MusicTimeGrid
from .pitchpattern import MusicPitchClassPattern
from .pitch import MusicPitchRange
from .instrument import MidiInstrument
from .timegrid import MusicRhythmPattern


class MusicVoice(Base):
    """Represents a horizontal voice in the project."""
    def __init__(self,
                 name: str = 'Voice',
                 pitch_range: MusicPitchRange = None,
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
        # The `Section` class contains a `UnitMatrix`
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
                 pitch_pattern: MusicPitchClassPattern = None,
                 time_grid: MusicTimeGrid = None,
                 rhythm_pattern : MusicRhythmPattern = None,
                 sections: List[MusicSection] = None,
                 voices: List[MusicVoice] = None,
                 matrix: UnitMatrix = None,
                 time: MusicLinearTime = None,
                 ):
        super().__init__(name)
        self.name = name
        self.pitch_pattern = pitch_pattern
        self.time_grid = time_grid
        self.rhythm_pattern = rhythm_pattern
        self.sections = sections
        self.voices = voices
        self.matrix = matrix
        self.time = time

    def __repr__(self):
        return (f"<MusicProject(name={self.name},"
                f"sections={len(self.sections) if self.sections else 0},"
                f"voices={len(self.voices) if self.voices else 0})>")

