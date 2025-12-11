"""Package for music composition structures."""
from .unit import MusicUnit
from .time import MusicTime, Circle
from .pattern import MusicPattern
from .project import MusicSection, MusicVoice, MusicProject
from .matrix import MusicMatrix
from transformers.base import MusicFactory, MusicGenerator, MusicTransformer
from .instrument import MidiChannel, MidiInstrument, MidiPercussion
from .pitch import Constants, MusicPitchClass, MusicPitch, Direction, PitchRange, Helix


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
    'MusicPitchClass',
    'MusicPitch',
    'Direction',
    'PitchRange',
    'Helix',

]