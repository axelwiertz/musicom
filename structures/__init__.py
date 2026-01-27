"""Package for music composition structures."""
from .unit import MusicUnit, MusicEvent
from .time import MusicLinearTime
from .timegrid import MusicTimeGrid, MusicRhythmPattern
from .pitchpattern import (
    MusicPitchClassSet,
    MusicPitchClassPattern,  # Keep for backward compatibility
    Cardinality,
    PatternType,
    PatternRotation,
    PatternGraph
)
from .project import MusicSection, MusicVoice, MusicProject
from .matrix import UnitMatrix
from .instrument import MidiChannel, MidiInstrument, MidiPercussion
from .pitch import MusicPitchClass, MusicPitchGrid, Direction, MusicPitchRange

# Alias for backward compatibility
MusicPitchClassPattern = MusicPitchClassSet

__all__ = [
    "MusicEvent",
    "MusicUnit",
    "MusicTimeGrid",
    "MusicLinearTime",
    "MusicRhythmPattern",
    "MusicPitchClassSet",
    "MusicPitchClassPattern",  # Keep for backward compatibility
    "Cardinality",
    "PatternType",
    "PatternRotation",
    "PatternGraph",

    "MusicSection",
    "MusicVoice",
    "MusicProject",
    "UnitMatrix",

    'MidiInstrument',
    'MidiPercussion',
    'MidiChannel',

    'MusicPitchClass',
    'MusicPitchGrid',
    'Direction',
    'MusicPitchRange',

]