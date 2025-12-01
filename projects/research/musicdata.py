"""Module for generating and storing musical data structures such as scales and intervals."""
import pandas as pd
import numpy as np

from base import MidiPitch
from utilities import Config

from base.twelvetone import TwelveTET
from structures.pattern import MusicPattern
from regularity.diatonic import Diatonic

from music21 import interval

def music_interval_data():
    m21intervals = list(interval.ChromaticInterval(n) for n in TwelveTET.PITCH_CLASS_NUMBERS)

def pitch_data():
    pitch_numbers = np.array([x + str(y) for y in range(TwelveTET.OCTAVES) for x in TwelveTET.PITCH_CLASS_NAMES_SHARP])

    pitch_dataframe = pd.DataFrame({
        'PitchIndex': range(len(pitch_numbers)),
        'PitchName': pitch_numbers
    })
    pitch_dataframe.to_excel(Config.DEFAULT_PATH + 'chromaticpitches.xlsx', index=False, sheet_name='Pitches')

    # Create pitches

    pitch_freqs = dict(
        zip(pitch_numbers,
            [2 ** ((n + 1 - 49) / 12) * TwelveTET.A4_FREQ for n in range(len(pitch_numbers))]
            )
    )
    pitch_freqs[''] = 0.0  # stop
    pitch_freqs = tuple(2 ** ((n - MidiPitch.A4) / TwelveTET.TWELVE) * TwelveTET.A4_FREQ
                             for n in TwelveTET.PITCH_CLASS_NUMBERS)


def music_data():
    # Heptatonic modes mapped to chromatic pitch helix
    interval_pattern7 = MusicPattern(Diatonic.HEPTA, Diatonic.SCALE)
    # Major
    major_mode_helix = TwelveTET.OCTAVES * interval_pattern7.modes_helix[Diatonic.major_mode]
    # Minor
    minor_mode_helix = TwelveTET.OCTAVES * interval_pattern7.modes_helix[Diatonic.minor_mode]

    # Major mode pitch helixes for all tonics (C, C#, D, ..., B)
    major_scales = [major_mode_helix[-x:] + major_mode_helix[:-x] for x in range(TwelveTET.TWELVE)]
    minor_scales = [minor_mode_helix[-x:] + minor_mode_helix[:-x] for x in range(TwelveTET.TWELVE)]

    major_scales_data = pd.DataFrame(major_scales)
    major_scales_data.to_excel(Config.DEFAULT_PATH + 'majorscales.xlsx', index=True, sheet_name='Pitch')

    major_scales_table = major_scales_data.transpose()
    #chromatic_table.columns = ['Nr', 'ClassNr', 'ClassChr', 'Freq'] + list(TwelveTET.PITCH_CLASS_NAMES_SHARP)
    major_scales_table.to_excel(Config.DEFAULT_PATH + 'majorscales_table.xlsx', index=True, sheet_name='Pitch')

    hepta_major_arr = np.array(major_scales)


def main():
    music_interval_data()
    pitch_data()
    music_data()

if __name__ == '__main__':
    main()