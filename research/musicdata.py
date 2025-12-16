"""Module for generating and storing musical data structures such as scales and intervals."""
import pandas as pd
import numpy as np

from converters.unit import pattern_to_excel
from structures import MusicPitch, MusicPitchClass
from rules import Cardinality, PatternMode, PatternType
from utilities import Config
from converters import name_to_midi
from structures import MusicPattern

from music21 import interval

def unit_data():
    pass

def music_interval_data():
    m21intervals = list(interval.ChromaticInterval(n) for n in MusicPitchClass.NUMBERS)

def pitch_data():
    pitch_numbers = np.array([x + str(y) for y in range(MusicPitch.OCTAVES) for x in MusicPitchClass.NAMES_SHARP])

    pitch_dataframe = pd.DataFrame({
        'PitchIndex': range(len(pitch_numbers)),
        'PitchName': pitch_numbers
    })
    pitch_dataframe.to_excel(Config.DEFAULT_PATH + 'chromaticpitches.xlsx', index=False, sheet_name='Pitches')

    # Create pitches

    def pitch_to_freq(pitch_name: str) -> float:
        if pitch_name == '':
            return 0.0
        midi_number = name_to_midi(pitch_name)
        freq = 2 ** ((midi_number - 69) / 12) * 440
        return freq



def music_data():
    # Heptatonic modes mapped to chromatic pitch helix
    scale7 = MusicPattern("Heptatonic scale", Cardinality.HEPTA, PatternType.SCALE)

    scale7.set_mode (PatternMode.major_mode)  # Major scale

    pattern_to_excel(scale7)




def main():
    music_interval_data()
    pitch_data()
    music_data()

if __name__ == '__main__':
    main()