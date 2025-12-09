"""Package for music composition structures."""
from .unit import MusicUnit
from .time import MusicTime, Circle
from .pattern import MusicPattern
from .project import MusicSection, MusicVoice, MusicProject
from .matrix import MusicMatrix
from .factory import MusicFactory, MusicGenerator, MusicTransformer
from .instrument import MidiChannel, MidiInstrument, MidiPercussion
from .pitch import Constants, PitchClass, MusicPitches, Direction, PitchRange, Helix


__all__ = [
    "MusicUnit",
    "MusicTime",
    "Circle",
    "MusicPattern",
    "MusicSection",
    "MusicVoice",
    "MusicProject",
    "MusicMatrix",
    "MusicFactory",
    "MusicGenerator",
    "MusicTransformer",

    'MidiInstrument',
    'MidiPercussion',
    'MidiChannel',

    'Constants',
    'PitchClass',
    'MusicPitches',
    'Direction',
    'PitchRange',
    'Helix',

]