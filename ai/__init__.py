"""
musicom.ai - AI-driven composition extension for the Musicom framework.

Provides generators (melody, harmony, rhythm), I/O (MIDI, MusicXML, audio analysis),
transformers (pitch, rhythm), rules (harmonic, voice leading), and an integration
bridge to Music21, MusicPy, and PyPianoroll.
"""

__version__ = "0.1.0"

# Core imports
from musicom.ai.core.tet_system import PitchClass, Interval, Scale, Key, TimeSignature
from musicom.ai.core.structures import Note, Rest, Chord, Phrase, Progression, Voice, Score

# Utility imports
from musicom.ai.utils.exceptions import (
    MusicomAIException,
    InvalidPitchError,
    InvalidIntervalError,
    ConversionError,
    ValidationError,
)

__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__email__",
    # Core classes
    "PitchClass",
    "Interval",
    "Scale",
    "Key",
    "TimeSignature",
    "Note",
    "Rest",
    "Chord",
    "Phrase",
    "Progression",
    "Voice",
    "Score",
    # Exceptions
    "MusicomAIException",
    "InvalidPitchError",
    "InvalidIntervalError",
    "ConversionError",
    "ValidationError",
]
