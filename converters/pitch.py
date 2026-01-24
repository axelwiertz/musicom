"""Pitch and frequency conversion utilities."""

from math import pow, log2
from typing import Any

from librosa import midi_to_hz, hz_to_midi, note_to_midi, midi_to_note
from numpy import floating

from structures.pitch import MusicPitchClass

# Constants
C0_MIDI = 12  # MIDI number for C0
A4_MIDI = 69  # MIDI number for A4
A4_FREQ = 440.0  # Frequency of A4 in Hz


def name_to_freq(pitch_name: str) -> float | floating[Any]:
    """Convert pitch name to frequency in Hz."""
    if pitch_name == '':
        return 0.0
    midi_number = name_to_midi(pitch_name)
    return midi_to_hz(float(midi_number))


def midi_to_pitch_class(i: int) -> int:
    """Convert MIDI number to pitch class (0-11)."""
    return i % MusicPitchClass.SIZE


def name_to_pitch_class(name: str) -> int:
    """Convert note name (e.g., C4, A#3) to pitch class number (0-11)."""
    return midi_to_pitch_class(name_to_midi(name))


def midi_to_freq(midi: int | float) -> floating[Any]:
    """Return frequency (Hz) for given MIDI note number."""
    return midi_to_hz(midi)


def freq_to_midi(freq: float) -> floating[Any]:
    """Return MIDI note number (can be fractional) for a given frequency (Hz)."""
    return hz_to_midi(freq)


def semitone_ratio(n: int = 1) -> float:
    """Return frequency ratio for n semitones: 2^(n/12)."""
    return pow(2.0, n / float(MusicPitchClass.SIZE))


def cents_between(f1: float, f2: float) -> float:
    """Return difference in cents from f1 to f2 (positive if f2 > f1)."""
    return 1200.0 * log2(f2 / f1)


def interval_cents(semitones: int | float) -> float:
    """Return cents value for given semitone interval."""
    return semitones * 100.0


def midi_to_name(midi: int | float) -> str:
    """Return note name (e.g., C4, A4) for MIDI number."""
    return midi_to_note(midi)


def name_to_midi(name: list[str] | str) -> list[int] | int:
    """Parse note name like 'C#4' or 'A4' to MIDI number."""
    if isinstance(name, list):
        return [note_to_midi(n) for n in name]
    return note_to_midi(name)


__all__ = [
    "name_to_freq",
    "midi_to_freq",
    "freq_to_midi",
    "semitone_ratio",
    "cents_between",
    "interval_cents",
    "midi_to_name",
    "name_to_midi",
    "midi_to_pitch_class",
    "name_to_pitch_class",
]
