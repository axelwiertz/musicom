"""Helper functions for musicom_ai."""

from typing import Union, List, Optional
from musicom.ai.utils.constants import PITCH_CLASSES, ENHARMONIC_MAP, MIDI_RANGE
from musicom.ai.utils.exceptions import InvalidPitchError


def normalize_pitch_name(pitch_name: str) -> str:
    """
    Normalize pitch name to use sharps instead of flats.
    
    Args:
        pitch_name: Pitch name (e.g., 'C', 'Db', 'F#')
        
    Returns:
        Normalized pitch name using sharps
        
    Raises:
        InvalidPitchError: If pitch name is invalid
    """
    pitch_name = pitch_name.strip()
    
    # Handle enharmonic equivalents
    if pitch_name in ENHARMONIC_MAP:
        pitch_name = ENHARMONIC_MAP[pitch_name]
    
    # Extract just the pitch class (without octave)
    pitch_class = pitch_name.rstrip('0123456789')
    
    if pitch_class not in PITCH_CLASSES:
        raise InvalidPitchError(f"Invalid pitch name: {pitch_name}")
    
    return pitch_name


def midi_to_pitch_class(midi_number: int) -> str:
    """
    Convert MIDI note number to pitch class name.
    
    Args:
        midi_number: MIDI note number (0-127)
        
    Returns:
        Pitch class name (e.g., 'C', 'F#')
        
    Raises:
        InvalidPitchError: If MIDI number is out of range
    """
    if not MIDI_RANGE[0] <= midi_number <= MIDI_RANGE[1]:
        raise InvalidPitchError(f"MIDI number {midi_number} out of range {MIDI_RANGE}")
    
    return PITCH_CLASSES[midi_number % 12]


def midi_to_octave(midi_number: int) -> int:
    """
    Get octave number from MIDI note number.
    
    Args:
        midi_number: MIDI note number (0-127)
        
    Returns:
        Octave number
        
    Raises:
        InvalidPitchError: If MIDI number is out of range
    """
    if not MIDI_RANGE[0] <= midi_number <= MIDI_RANGE[1]:
        raise InvalidPitchError(f"MIDI number {midi_number} out of range {MIDI_RANGE}")
    
    return (midi_number // 12) - 1


def pitch_class_to_semitone(pitch_class: str) -> int:
    """
    Convert pitch class name to semitone number (0-11).
    
    Args:
        pitch_class: Pitch class name (e.g., 'C', 'F#')
        
    Returns:
        Semitone number (0-11)
        
    Raises:
        InvalidPitchError: If pitch class is invalid
    """
    normalized = normalize_pitch_name(pitch_class)
    pitch_only = normalized.rstrip('0123456789')
    
    if pitch_only not in PITCH_CLASSES:
        raise InvalidPitchError(f"Invalid pitch class: {pitch_class}")
    
    return PITCH_CLASSES.index(pitch_only)


def semitone_to_pitch_class(semitone: int) -> str:
    """
    Convert semitone number to pitch class name.
    
    Args:
        semitone: Semitone number (0-11)
        
    Returns:
        Pitch class name
    """
    return PITCH_CLASSES[semitone % 12]


def transpose_semitones(semitone: int, interval: int) -> int:
    """
    Transpose a semitone by an interval.
    
    Args:
        semitone: Original semitone (0-11)
        interval: Interval in semitones
        
    Returns:
        Transposed semitone (0-11)
    """
    return (semitone + interval) % 12


def interval_between_pitches(pitch1: str, pitch2: str) -> int:
    """
    Calculate interval in semitones between two pitch classes.
    
    Args:
        pitch1: First pitch class
        pitch2: Second pitch class
        
    Returns:
        Interval in semitones (0-11)
    """
    sem1 = pitch_class_to_semitone(pitch1)
    sem2 = pitch_class_to_semitone(pitch2)
    return (sem2 - sem1) % 12


def validate_midi_number(midi_number: int) -> bool:
    """
    Validate MIDI note number.
    
    Args:
        midi_number: MIDI note number to validate
        
    Returns:
        True if valid, False otherwise
    """
    return MIDI_RANGE[0] <= midi_number <= MIDI_RANGE[1]


def clamp_midi_number(midi_number: int) -> int:
    """
    Clamp MIDI number to valid range.
    
    Args:
        midi_number: MIDI note number
        
    Returns:
        Clamped MIDI number
    """
    return max(MIDI_RANGE[0], min(midi_number, MIDI_RANGE[1]))


def beats_to_seconds(beats: float, tempo: float) -> float:
    """
    Convert beats to seconds.
    
    Args:
        beats: Duration in beats
        tempo: Tempo in BPM
        
    Returns:
        Duration in seconds
    """
    return (beats * 60.0) / tempo


def seconds_to_beats(seconds: float, tempo: float) -> float:
    """
    Convert seconds to beats.
    
    Args:
        seconds: Duration in seconds
        tempo: Tempo in BPM
        
    Returns:
        Duration in beats
    """
    return (seconds * tempo) / 60.0


def quantize_duration(duration: float, resolution: int = 16) -> float:
    """
    Quantize duration to nearest subdivision.
    
    Args:
        duration: Duration in beats
        resolution: Subdivision resolution (e.g., 16 for sixteenth notes)
        
    Returns:
        Quantized duration
    """
    quantum = 1.0 / resolution
    return round(duration / quantum) * quantum


def parse_chord_symbol(symbol: str) -> tuple:
    """
    Parse chord symbol into root and quality.
    
    Args:
        symbol: Chord symbol (e.g., 'Cmaj7', 'Dm7', 'G7')
        
    Returns:
        Tuple of (root, quality)
        
    Examples:
        >>> parse_chord_symbol('Cmaj7')
        ('C', 'major7')
        >>> parse_chord_symbol('Dm7')
        ('D', 'minor7')
    """
    # Extract root (first 1-2 characters)
    if len(symbol) > 1 and symbol[1] in ['#', 'b']:
        root = symbol[:2]
        quality_str = symbol[2:]
    else:
        root = symbol[0]
        quality_str = symbol[1:]
    
    # Normalize root
    root = normalize_pitch_name(root)
    
    # Parse quality
    quality_map = {
        '': 'major',
        'm': 'minor',
        'maj': 'major',
        'min': 'minor',
        'dim': 'diminished',
        'aug': 'augmented',
        '7': 'dominant7',
        'maj7': 'major7',
        'm7': 'minor7',
        'dim7': 'diminished7',
        'm7b5': 'half_diminished7',
        'sus2': 'sus2',
        'sus4': 'sus4',
        '6': 'major6',
        'm6': 'minor6',
        '9': 'dominant9',
        'maj9': 'major9',
        'm9': 'minor9',
        '11': 'dominant11',
        'maj11': 'major11',
        'm11': 'minor11',
        '13': 'dominant13',
        'maj13': 'major13',
        'm13': 'minor13',
    }
    
    quality = quality_map.get(quality_str, 'major')
    
    return root, quality
