"""Module for musical transformations."""
from .canon import CanonTransformator
from .pitchsequence import PitchSequenceTransformator
from .transpose import transpose
from .invert import invert
from .retrograde import retrograde

__all__ = [
    'transpose',
    'invert',
    'retrograde',
           ]