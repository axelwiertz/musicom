from typing import List

from base.tuning import TwelveTET
from base.midi import MidiInstrument
from base.chromatic import ChromaticPitches
from structures.base import MusicBase
from structures.matrix import MusicMatrix

class PitchRange:
    # Chromatic pitch range
    def __init__(self,  pitch_class_start=TwelveTET.A,
                        octave_start=0,
                        pitch_class_end=TwelveTET.C,
                        octave_end=8):

        self.chromatic = ChromaticPitches()

        self.index_start = self.chromatic.index_of(pitch_class_start, octave_start)
        self.index_end = self.chromatic.index_of(pitch_class_end, octave_end)


class MusicVoice(MusicBase):
    """Represents a voice in the project."""
    # A horizontal musical voice
    def __init__(self,
                 _id: int,
                 name: str = 'Voice',
                 pitch_range: PitchRange = None,
                 midi_instrument: int = MidiInstrument.PIANO,
                 ):
        super().__init__(_id, name)
        self.pitch_range = pitch_range
        self.midi_instrument = midi_instrument


# The `Section` class contains a `MusicMatrix`
class MusicSection (MusicBase):
    """Represents a project section, containing a matrix."""
    def __init__(self,
                 _id: int = 0,
                 name: str = "Section",
                 matrix: MusicMatrix = None):
        super().__init__(_id, name)
        self.matrix = matrix

    def __repr__(self):
        return f"Section(name='{self.name}', matrix={self.matrix})"

# The `Project` class is the top-level container for a list of `Section` objects.

class MusicProject (MusicBase):
    """Represents the entire project, containing multiple sections."""
    def __init__(self,
                 _id: int = 0,
                 name: str = "Project",
                 ):
        super().__init__(_id, name)
        self.name = name
        self.sections: List[MusicSection] = []
        self.voices: List[MusicVoice] = []


    def __repr__(self):
        return f"Project(name='{self.name}', sections={len(self.sections)}, voices={len(self.voices)})"

