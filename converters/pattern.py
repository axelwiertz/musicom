""" Converters for MusicPitchClassSet to MIDI note numbers """
import pandas as pd
from utilities import Config
from structures import MusicPitchClassSet


def pattern_to_excel (pattern : MusicPitchClassSet) :
    """ Save pattern pitch classes and modes to Excel files """
    pd_modes = pd.DataFrame(pattern.modes)
    pd_modes_helix = pd.DataFrame(pattern.modes_helix)

    pd_modes.to_excel(Config.DEFAULT_PATH + 'interval_PatternRotations.xlsx', index=True, sheet_name='MusicPitchClassSet')
    pd_modes_helix.to_excel(Config.DEFAULT_PATH + 'interval_PatternRotationsHelix.xlsx', index=True, sheet_name='MusicPitchClassSet')
