"""Module for musical transformations."""
from .canon import CanonTransformer
from .pitchsequence import PitchSequenceTransformer
from .humanize import (
    HumanizeProfile,
    HumanizeTransformer,
    STYLE_HUMANIZE,
    STYLE_HUMANIZE_DEFAULT,
    humanize_events,
    humanize_unit,
    profile_for_style,
)

__all__ = [
    'CanonTransformer',
    'PitchSequenceTransformer',
    'HumanizeTransformer',
    'HumanizeProfile',
    'profile_for_style',
    'humanize_events',
    'humanize_unit',
    'STYLE_HUMANIZE',
    'STYLE_HUMANIZE_DEFAULT',
]