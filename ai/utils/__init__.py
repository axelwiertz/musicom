"""Utility modules for musicom_ai."""

from musicom.ai.utils.exceptions import (
    MusicomAIException,
    InvalidPitchError,
    InvalidIntervalError,
    ConversionError,
    ValidationError,
)
from musicom.ai.utils.constants import (
    PITCH_CLASSES,
    ENHARMONIC_MAP,
    INTERVAL_NAMES,
    SCALE_PATTERNS,
    CHORD_QUALITIES,
    DEFAULT_TEMPO,
    DEFAULT_TIME_SIGNATURE,
    DEFAULT_VELOCITY,
    DEFAULT_OCTAVE,
    MIDI_RANGE,
    VELOCITY_RANGE,
)

__all__ = [
    # Exceptions
    "MusicomAIException",
    "InvalidPitchError",
    "InvalidIntervalError",
    "ConversionError",
    "ValidationError",
    # Constants
    "PITCH_CLASSES",
    "ENHARMONIC_MAP",
    "INTERVAL_NAMES",
    "SCALE_PATTERNS",
    "CHORD_QUALITIES",
    "DEFAULT_TEMPO",
    "DEFAULT_TIME_SIGNATURE",
    "DEFAULT_VELOCITY",
    "DEFAULT_OCTAVE",
    "MIDI_RANGE",
    "VELOCITY_RANGE",
]
