"""Defines the Project, Section, and Voice classes for the music composition framework."""
from typing import List
from .base import Base
from .matrix import MusicMatrix
from .time import MusicTime
from .pattern import MusicPattern
from structures import PitchRange, MidiInstrument

class MusicVoice(Base):
    """Represents a horizontal voice in the project."""
    def __init__(self,
                 name: str = 'Voice',
                 pitch_range: PitchRange = None,
                 midi_instrument: int = MidiInstrument.PIANO,
                 ):
        super().__init__(name)
        self.pitch_range = pitch_range
        self.midi_instrument = midi_instrument


class MusicSection (Base):
    """Represents a project section, containing a matrix."""
    def __init__(self,
                 name: str = "Section",
                 time : MusicTime = None,
                 matrix: MusicMatrix = None):
        super().__init__(name)
        # The `Section` class contains a `MusicMatrix`
        self._time = time
        self._matrix = matrix

    @property
    def time(self) -> MusicTime:
        return self._time

    @property
    def matrix(self) -> MusicMatrix:
        return self._matrix

    def __repr__(self):
        return f"Section(name='{self.name}', time={self.time}, matrix={self.matrix})"

# The `Project` class is the top-level container for a list of `Section` objects.
class MusicProject (Base):
    """Represents the entire project, containing multiple sections."""
    def __init__(self,
                 name: str = None,
                 pattern: MusicPattern = None,
                 sections: List[MusicSection] = None,
                 voices: List[MusicVoice] = None,
                 ):
        super().__init__(name)
        self.name = name if name is not None else "Project"
        self.pattern = pattern if pattern is not None else MusicPattern()
        self.sections = sections if sections is not None else []
        self.voices = voices if voices is not None else []

    def __repr__(self):
        return f"Project(name='{self.name}', pattern={self.pattern}, sections={len(self.sections)}, voices={len(self.voices)})"

