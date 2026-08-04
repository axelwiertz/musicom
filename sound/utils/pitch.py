"""Pitch conversion utilities - single source of truth.

Consolidates pitch/frequency/midi/note conversions from across the codebase.
"""

from math import log2, pow


# Standard tuning reference
A4_FREQ = 440.0
A4_MIDI = 69
C0_MIDI = 12


def midi_to_freq(midi_note: int) -> float:
    """Convert MIDI note number to frequency in Hz.
    
    Args:
        midi_note: MIDI note number (0-127)
        
    Returns:
        Frequency in Hz
    """
    return A4_FREQ * pow(2.0, (midi_note - A4_MIDI) / 12.0)


def freq_to_midi(freq: float) -> int:
    """Convert frequency in Hz to nearest MIDI note number.
    
    Args:
        freq: Frequency in Hz
        
    Returns:
        MIDI note number (rounded to nearest integer)
    """
    return int(round(A4_MIDI + 12.0 * log2(freq / A4_FREQ)))


def name_to_midi(note_name: str) -> int:
    """Convert note name (e.g., 'C4', 'F#3') to MIDI note number.
    
    Args:
        note_name: Note name with octave (e.g., 'C4', 'F#3', 'Bb5')
        
    Returns:
        MIDI note number
    """
    note_map = {
        'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3,
        'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8,
        'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11
    }
    
    # Parse note name and octave
    if len(note_name) < 2:
        raise ValueError(f"Invalid note name: {note_name}")
    
    note = note_name[0].upper()
    offset = 0
    idx = 1
    
    # Handle sharps/flats
    if idx < len(note_name) and note_name[idx] == '#':
        offset = 1
        idx += 1
    elif idx < len(note_name) and note_name[idx] == 'b':
        offset = -1
        idx += 1
    
    # Get octave
    octave = int(note_name[idx:])
    
    # Calculate MIDI note
    pitch_class = note_map[note + ('#' if offset == 1 else 'b' if offset == -1 else '')]
    return C0_MIDI + pitch_class + (octave * 12)


def midi_to_name(midi_note: int) -> str:
    """Convert MIDI note number to note name.
    
    Args:
        midi_note: MIDI note number (0-127)
        
    Returns:
        Note name with octave (e.g., 'C4', 'F#3')
    """
    pitch_class = (midi_note - C0_MIDI) % 12
    octave = (midi_note - C0_MIDI) // 12
    
    name_map = {
        0: 'C', 1: 'C#', 2: 'D', 3: 'D#', 4: 'E', 5: 'F',
        6: 'F#', 7: 'G', 8: 'G#', 9: 'A', 10: 'A#', 11: 'B'
    }
    
    return f"{name_map[pitch_class]}{octave}"


def name_to_freq(note_name: str) -> float:
    """Convert note name to frequency in Hz.
    
    Args:
        note_name: Note name with octave (e.g., 'C4', 'F#3')
        
    Returns:
        Frequency in Hz
    """
    return midi_to_freq(name_to_midi(note_name))


__all__ = [
    "midi_to_freq",
    "freq_to_midi",
    "name_to_midi",
    "midi_to_name",
    "name_to_freq",
    "A4_FREQ",
    "A4_MIDI",
    "C0_MIDI",
]
