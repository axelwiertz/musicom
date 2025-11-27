"""Package for music composition structures."""
from structures.unit import MusicUnit
from structures.time import MusicTime
from structures.pattern import MusicPattern
from structures.project import MusicSection, MusicVoice, MusicProject
from structures.matrix import MusicMatrix

__all__ = [
    "MusicUnit",
    "MusicTime",
    "MusicPattern",
    "MusicSection",
    "MusicVoice",
    "MusicProject",
    "MusicMatrix",
]