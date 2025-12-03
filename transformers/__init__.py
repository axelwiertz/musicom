"""Module for musical transformations."""
from .canon import CanonTransformer
from .pitchsequence import PitchSequenceTransformer, invert
from .transpose import transpose
from .retrograde import retrograde

__all__ = [
    'transpose',
    'invert',
    'retrograde',
    'CanonTransformer',
    'PitchSequenceTransformer',

]