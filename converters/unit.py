"""Converters for MusicUnit to/from DataFrame, Excel, Binary, and MusicPitchClassSet."""
import os
from typing import List
import pandas as pd
from utilities import Config
from structures import MusicUnit, MusicEvent

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
    # Split binary in parts of 'total_bits' length
    num_parts = len(binary) // total_bits
    binary_parts = []
    for i in range(num_parts):
        # Extract binary elements
        binary_parts += [binary[(i * total_bits):(i * total_bits) + total_bits]]

    events = []
    tick = 0
    for binary_part in binary_parts:
        # Decode: 6 bits pitch interval (relative), 4 bits onset interval, 4 bits duration, 4 bits velocity
        pitch_bits = binary_part[0:6]
        onset_bits = binary_part[6:10]
        duration_bits = binary_part[10:14]
        velocity_bits = binary_part[14:18]

        pitch_nr = int(sum([bit * pow(2, i) for i, bit in enumerate(pitch_bits)]))
        onset = int(sum([bit * pow(2, i) for i, bit in enumerate(onset_bits)]))
        duration = int(sum([bit * pow(2, i) for i, bit in enumerate(duration_bits)]))
        velocity = int(sum([bit * pow(2, i) for i, bit in enumerate(velocity_bits)]))

        pitch = 24 + (pitch_nr % 72)  # map to MIDI 24..95
        tick += onset * 120           # onset in sixteenth steps
        vel = min(velocity * 8 + 20, 127)
        dur = max(duration * 60 + 30, 60)

        events.append(MusicEvent(
            pitch=pitch,
            volume=vel,
            start_tick=tick,
            end_tick=tick + dur,
        ))

    return MusicUnit(events=events)

