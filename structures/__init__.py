"""Package for music composition structures."""
from .unit import MusicUnit, MusicEvent
from .time import MusicTimePattern
from .timepattern import MusicTimePattern, MusicRhythmPattern
from .pitchpattern import MusicPitchPattern, Cardinality, PatternType, PatternMode
from .project import MusicSection, MusicVoice, MusicProject
from .matrix import UnitMatrix
from .instrument import MidiChannel, MidiInstrument, MidiPercussion
from .pitch import MusicPitchClass, MusicPitch, Direction, PitchRange


__all__ = [
    "MusicEvent",
    "MusicUnit",
    "MusicTimePattern",
    "MusicRhythmPattern",
    "MusicPitchPattern",
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