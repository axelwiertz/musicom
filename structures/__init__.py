"""Package for music composition structures."""
from .unit import MusicUnit
from .time import MusicTime, Circle
from .pattern import MusicPattern
from .project import MusicSection, MusicVoice, MusicProject
from .matrix import MusicMatrix
from .factory import MusicFactory, MusicGenerator, MusicTransformer

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
    "MusicTransformer"
]