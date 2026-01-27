"""Converters for MusicUnit to/from DataFrame, Excel, Binary, and MusicPitchClassSet."""
import os
from typing import List
import pandas as pd
from utilities import Config
from structures import MusicUnit

# --- DataFrame / Excel helpers for MusicUnit ---
def unit_to_dataframe(unit: MusicUnit) -> pd.DataFrame:
    """Convert a MusicUnit into a pandas DataFrame.
    """

    df =  pd.DataFrame(unit.data)

    return df


def unit_to_excel(unit: MusicUnit, filename: str | None = None, path: str = Config.DEFAULT_PATH, sheet_name: str | None = None, engine: str | None = 'openpyxl') -> str:
    """Save a MusicUnit to an Excel file and return the filepath.

    - `filename`: if None, a filename is auto-generated.
    - `path`: base directory to save into (defaults to Config.DEFAULT_PATH).
    - `sheet_name`: Excel sheet name (defaults to 'MusicUnit').
    - `engine`: pandas Excel writer engine (defaults to 'openpyxl').
    """
    df = unit_to_dataframe(unit)

    if filename is None:
        # safe filename
        filename = f"MusicUnit_{id(unit)}.xlsx"

    # ensure directory exists
    os.makedirs(path, exist_ok=True)
    filepath = os.path.join(path, filename)

    try:
        df.to_excel(filepath, sheet_name=sheet_name or 'MusicUnit', index=False, engine=engine)
    except TypeError:
        # engine param may not be accepted by older pandas versions
        df.to_excel(filepath, sheet_name=sheet_name or 'MusicUnit', index=False)

    return filepath


pitch_interval_bits = 6  # binary 24 pitch intervals
#max_pitch_interval = pow(2, pitch_interval_bits - 1)
onset_interval_bits = 4  # binary 8 timesteps
duration_bits = 4  # binary 8 timesteps
velocity_bits = 4  # binary 8 levels
total_bits = pitch_interval_bits + duration_bits + onset_interval_bits + velocity_bits

def unit_to_binary (unit: MusicUnit) -> List[int]:
    """Convert a MusicUnit to a binary representation (list of 0,1)."""
    # Binary genome representation

    binary = unit.data.copy()

    return binary

def binary_to_unit(binary: List[int]) -> MusicUnit:
    # Transform a binary into a unit
    # Split binary in parts of 'bits' length
    num_parts = len(binary) % total_bits
    binary_parts = []
    for i in range(num_parts):
        # Extract binary elements
        binary_parts += [binary[(i * total_bits):(i * total_bits) + total_bits]]

    pitches = []
    for binary_part in binary_parts:
        pitch_nr = int(sum([bit * pow(2, i) for i, bit in enumerate(binary_part)]))
        pitches.append(pitch_nr)

    return MusicUnit(pitches=pitches)

