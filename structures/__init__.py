"""Package for music composition structures."""
from .unit import MusicUnit, MusicEvent
from .time import MusicTime
from .pattern import MusicPattern, Cardinality, PatternType, PatternMode
from .project import MusicSection, MusicVoice, MusicProject
from .matrix import UnitMatrix
from .instrument import MidiChannel, MidiInstrument, MidiPercussion
from .pitch import MusicPitchClass, MusicPitch, Direction, PitchRange


__all__ = [
    "MusicUnit",
    "MusicTime",
    "MusicEvent",
    "MusicPattern",
    "Cardinality",
    "PatternType",
    "PatternMode",

    "MusicSection",
    "MusicVoice",
    "MusicProject",
    "UnitMatrix",

    'MidiInstrument',
    'MidiPercussion',
    'MidiChannel',

    'MusicPitchClass',
    'MusicPitch',
    'Direction',
    'PitchRange',

]