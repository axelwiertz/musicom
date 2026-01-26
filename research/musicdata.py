"""Module for generating and storing musical data structures such as scales and intervals."""
import pandas as pd

from structures import MusicPitchGrid, MusicPitchClass, MusicPitchClassPattern
from structures import MusicUnit
from structures import PatternRotation, PatternType
from converters.pattern import pattern_to_excel
from converters.unit import unit_to_dataframe
from utilities import Config


def unit_data():
    # Example unit: C Major triad in octave 4
    c_major_triad = MusicPitchClassPattern(
        name="C Major Chord",
        definition=PatternType.MAJOR,
        initial=MusicPitchClass.C
    )
    pitches = c_major_triad.get_pitches_in_octave(4)
    unit = MusicUnit(time_grid=None, pitches=pitches)
    dataframe = unit_to_dataframe(unit)
    dataframe.to_excel(Config.DEFAULT_PATH + 'unit_data.xlsx', index=False)


def pitch_grid_data():

    pitch_grid = MusicPitchGrid()
    pitch_dataframe = pd.DataFrame({
        'PitchIndex': len(pitch_grid),
        'PitchName': pitch_grid.midi_array
    })
    pitch_dataframe.to_excel(Config.DEFAULT_PATH + 'pitch_grid.xlsx', index=False, sheet_name='Pitches')


def music_data():
    # Heptatonic modes mapped to chromatic pitch helix
    scale7 = MusicPitchClassPattern(name="Heptatonic scale",
                                    definition=PatternType.HEPTATONIC,
                                    rotation=PatternRotation.major
                                    )

    pattern_to_excel(scale7)

def main():
    pitch_grid_data()
    music_data()

if __name__ == '__main__':
    main()