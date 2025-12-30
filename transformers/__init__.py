"""Module for musical transformations."""
from .canon import CanonTransformer
from .pitchsequence import PitchSequenceTransformer, invert
from .matrix import transpose
from .retrograde import retrograde

__all__ = [
    'matrix.py',
    'invert',
    'retrograde',
    'CanonTransformer',
    'PitchSequenceTransformer',

]