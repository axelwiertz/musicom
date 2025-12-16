""" Converters for MusicPattern to MIDI note numbers """
from typing import List
import pandas as pd
from utilities import Config
from structures import MusicPattern
from converters import pitch_to_midi

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

def pattern_to_excel (pattern : MusicPattern) :
    # Save pattern modes to Excel files
    pd_modes = pd.DataFrame(pattern.modes)
    pd_modes_helix = pd.DataFrame(pattern.modes_helix)

    pd_modes.to_excel(Config.DEFAULT_PATH + 'interval_patternModes.xlsx', index=True, sheet_name='MusicPattern')
    pd_modes_helix.to_excel(Config.DEFAULT_PATH + 'interval_patternModesHelix.xlsx', index=True, sheet_name='MusicPattern')
