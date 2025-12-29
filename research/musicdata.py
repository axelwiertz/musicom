"""Module for generating and storing musical data structures such as scales and intervals."""
import pandas as pd
import numpy as np

from structures import MusicPitch, MusicPitchClass, MusicPitchPattern
from converters import pattern_to_excel
from rules import Cardinality, PatternMode, PatternType
from utilities import Config

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



def music_data():
    # Heptatonic modes mapped to chromatic pitch helix
    scale7 = MusicPitchPattern("Heptatonic scale", Cardinality.HEPTA, PatternType.SCALE)

    scale7.set_mode (PatternMode.major_mode)  # Major scale

    pattern_to_excel(scale7)




def main():
    music_interval_data()
    pitch_data()
    music_data()

if __name__ == '__main__':
    main()