"""Validation functions for musicom_ai."""

from typing import Union, List, Optional
from musicom.ai.utils.constants import (
    PITCH_CLASSES,
    MIDI_RANGE,
    VELOCITY_RANGE,
    SCALE_PATTERNS,
    CHORD_QUALITIES,
)
from musicom.ai.utils.exceptions import (
    InvalidPitchError,
    InvalidDurationError,
    ValidationError,
)
from musicom.ai.utils.helpers import normalize_pitch_name


def validate_pitch_class(pitch_class: str) -> bool:
    """
    Validate pitch class name.
    
    Args:
        pitch_class: Pitch class name to validate
        
    Returns:
        True if valid
        
    Raises:
        InvalidPitchError: If pitch class is invalid
    """
    try:
        normalized = normalize_pitch_name(pitch_class)
        pitch_only = normalized.rstrip('0123456789')
        if pitch_only not in PITCH_CLASSES:
            raise InvalidPitchError(f"Invalid pitch class: {pitch_class}")
        return True
    except Exception as e:
        raise InvalidPitchError(f"Invalid pitch class: {pitch_class}") from e


def validate_midi_number(midi_number: int) -> bool:
    """
    Validate MIDI note number.
    
    Args:
        midi_number: MIDI note number to validate
        
    Returns:
        True if valid
        
    Raises:
        InvalidPitchError: If MIDI number is out of range
    """
    if not isinstance(midi_number, int):
        raise InvalidPitchError(f"MIDI number must be an integer, got {type(midi_number)}")
    
    if not MIDI_RANGE[0] <= midi_number <= MIDI_RANGE[1]:
        raise InvalidPitchError(
            f"MIDI number {midi_number} out of range {MIDI_RANGE}"
        )
    
    return True


def validate_velocity(velocity: int) -> bool:
    """
    Validate MIDI velocity.
    
    Args:
        velocity: Velocity to validate
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If velocity is out of range
    """
    if not isinstance(velocity, int):
        raise ValidationError(f"Velocity must be an integer, got {type(velocity)}")
    
    if not VELOCITY_RANGE[0] <= velocity <= VELOCITY_RANGE[1]:
        raise ValidationError(
            f"Velocity {velocity} out of range {VELOCITY_RANGE}"
        )
    
    return True


def validate_duration(duration: float) -> bool:
    """
    Validate duration value.
    
    Args:
        duration: Duration in beats to validate
        
    Returns:
        True if valid
        
    Raises:
        InvalidDurationError: If duration is invalid
    """
    if not isinstance(duration, (int, float)):
        raise InvalidDurationError(
            f"Duration must be a number, got {type(duration)}"
        )
    
    if duration <= 0:
        raise InvalidDurationError(
            f"Duration must be positive, got {duration}"
        )
    
    return True


def validate_tempo(tempo: float) -> bool:
    """
    Validate tempo value.
    
    Args:
        tempo: Tempo in BPM to validate
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If tempo is invalid
    """
    if not isinstance(tempo, (int, float)):
        raise ValidationError(f"Tempo must be a number, got {type(tempo)}")
    
    if tempo <= 0:
        raise ValidationError(f"Tempo must be positive, got {tempo}")
    
    if tempo > 500:
        raise ValidationError(f"Tempo {tempo} is unreasonably high (>500 BPM)")
    
    return True


def validate_time_signature(time_signature: tuple) -> bool:
    """
    Validate time signature.
    
    Args:
        time_signature: Time signature as (numerator, denominator)
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If time signature is invalid
    """
    if not isinstance(time_signature, tuple) or len(time_signature) != 2:
        raise ValidationError(
            f"Time signature must be a tuple of (numerator, denominator), got {time_signature}"
        )
    
    numerator, denominator = time_signature
    
    if not isinstance(numerator, int) or not isinstance(denominator, int):
        raise ValidationError(
            f"Time signature values must be integers, got {time_signature}"
        )
    
    if numerator <= 0:
        raise ValidationError(
            f"Time signature numerator must be positive, got {numerator}"
        )
    
    # Denominator should be a power of 2
    if denominator not in [1, 2, 4, 8, 16, 32, 64]:
        raise ValidationError(
            f"Time signature denominator must be a power of 2, got {denominator}"
        )
    
    return True


def validate_scale_pattern(pattern: str) -> bool:
    """
    Validate scale pattern name.
    
    Args:
        pattern: Scale pattern name to validate
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If pattern is invalid
    """
    if pattern not in SCALE_PATTERNS:
        raise ValidationError(
            f"Unknown scale pattern: {pattern}. "
            f"Available patterns: {list(SCALE_PATTERNS.keys())}"
        )
    
    return True


def validate_chord_quality(quality: str) -> bool:
    """
    Validate chord quality name.
    
    Args:
        quality: Chord quality name to validate
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If quality is invalid
    """
    if quality not in CHORD_QUALITIES:
        raise ValidationError(
            f"Unknown chord quality: {quality}. "
            f"Available qualities: {list(CHORD_QUALITIES.keys())}"
        )
    
    return True


def validate_octave(octave: int) -> bool:
    """
    Validate octave number.
    
    Args:
        octave: Octave number to validate
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If octave is out of reasonable range
    """
    if not isinstance(octave, int):
        raise ValidationError(f"Octave must be an integer, got {type(octave)}")
    
    if not -1 <= octave <= 9:
        raise ValidationError(
            f"Octave {octave} out of reasonable range (-1 to 9)"
        )
    
    return True


def validate_interval(semitones: int) -> bool:
    """
    Validate interval in semitones.
    
    Args:
        semitones: Interval in semitones to validate
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If interval is invalid
    """
    if not isinstance(semitones, int):
        raise ValidationError(
            f"Interval must be an integer, got {type(semitones)}"
        )
    
    # Allow any interval, but warn if very large
    if abs(semitones) > 48:  # More than 4 octaves
        import warnings
        warnings.warn(
            f"Interval of {semitones} semitones is very large (>4 octaves)"
        )
    
    return True
