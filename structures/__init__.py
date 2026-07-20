"""Package for music composition structures."""
from .unit import MusicUnit, MusicEvent
from .time import MusicLinearTime, TempoRange, TimeConverter
from .timegrid import MusicTimeGrid, MusicRhythmPattern
from .pitchclass import (
    MusicPitchClassSet,
    MusicPitchClassSet,  # Keep for backward compatibility
    Cardinality,
    PatternType,
    PatternRotation,
    PatternGraph
)
from .project import MusicSection, MusicVoice, MusicProject
from .matrix import UnitMatrix
from .instrument import MidiChannel, MidiInstrument, MidiPercussion
from .pitch import MusicPitch, MusicPitchClass, MusicPitchGrid, Direction, MusicPitchRange

# Alias for backward compatibility
MusicPitchClassSet = MusicPitchClassSet

__all__ = [
    "MusicEvent",
    "MusicUnit",
    "MusicTimeGrid",
    "MusicLinearTime",
    "TempoRange",
    "TimeConverter",
    "MusicRhythmPattern",
    "MusicPitchClassSet",
    "MusicPitchClassSet",  # Keep for backward compatibility
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
    'MusicPitch',
    'MusicPitchGrid',
    'Direction',
    'MusicPitchRange',

]