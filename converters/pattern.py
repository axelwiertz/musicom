""" Converters for MusicPattern to MIDI note numbers """
from typing import List
from structures import MusicPattern
from .pitch import pitch_to_midi

def pattern_degree_to_midi (pattern: MusicPattern, degree_: int, octave_: int) -> int:
    """ Convert pattern degree to MIDI note number """
    return pitch_to_midi (pattern.pitch_classes[degree_ - 1], octave_)

def pattern_to_pitches (pattern: MusicPattern, octave_: int) -> List[int]:
    """ Convert pattern to list of MIDI note numbers in given octave """
    # Start with tonic
    pitches = []
    for pitch_class in pattern.pitch_classes:
        # Convert to MIDI note
        midi_note = pitch_to_midi (pitch_class, octave_)
        pitches.append(midi_note)
    return pitches