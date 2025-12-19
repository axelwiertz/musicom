"""Module for pitch manipulation in MIDI data."""

from structures import MusicPitch

def pitch_shift:(pitch: int, semitones: int) -> int:
    """Shift a MIDI pitch by a number of semitones."""
    return pitch + semitones