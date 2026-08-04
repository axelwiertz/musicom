"""Shared utilities - pitch conversion, audio I/O, DSP primitives.

Single source of truth for common operations used across the sound package.
"""

from .pitch import midi_to_freq, freq_to_midi, name_to_midi, midi_to_name, name_to_freq
from .io import read_wav, write_wav, normalize_audio
from .envelope import ADSREnvelope, hanning_window

__all__ = [
    "midi_to_freq", "freq_to_midi", "name_to_midi", "midi_to_name", "name_to_freq",
    "read_wav", "write_wav", "normalize_audio",
    "ADSREnvelope", "hanning_window",
]
