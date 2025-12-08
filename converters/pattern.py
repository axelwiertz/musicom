""" Converters for MusicPattern to MIDI note numbers """
from typing import List
from base import Constants
from structures import MusicPattern
from .pitch import pitch_to_midi

def pattern_degree_to_midi (pattern: MusicPattern, degree: int, octave: int) -> int:
    """ Convert pattern degree to MIDI note number """
    pitch_class = (pattern.tonic_pitch_class + pattern.pitch_intervals[degree - 1]) % Constants.TWELVE
    return pitch_to_midi (pitch_class, octave)

def pattern_to_pitches (pattern: MusicPattern, octave_: int) -> List[int]:
    """ Convert pattern to list of MIDI note numbers """
    # Start with tonic
    pitches = [(pitch_to_midi(pattern.tonic_pitch_class,octave_))]
    for interval in pattern.pitch_intervals:
        # Calculate pitch class from interval
        pitch_class = (pattern.tonic_pitch_class + interval) % Constants.TWELVE
        # Convert to MIDI note
        midi_note = pitch_to_midi (pitch_class, octave_)
        pitches.append(midi_note)
    return pitches