"""Converters for MusicUnit to/from DataFrame, Excel, Binary, and MusicPattern."""
import os
from typing import List
import pandas as pd
from utilities.config import Config
from structures.unit import MusicUnit
from structures.pattern import MusicPattern

# --- DataFrame / Excel helpers for MusicUnit ---
def unit_to_dataframe(unit: MusicUnit) -> pd.DataFrame:
    """Convert a MusicUnit into a pandas DataFrame.

    Columns: pitch_node, pitch_interval, onset_interval, duration, velocity, onset_cumulative
    Handles uneven field lengths by padding with None.
    """

    fields = {
        'pitch_node': list(getattr(unit, 'pitch_nodes', []) or []),
        'pitch_interval': list(getattr(unit, 'pitch_intervals', []) or []),
        'onset_interval': list(getattr(unit, 'onset_intervals', []) or []),
        'duration': list(getattr(unit, 'durations', []) or []),
        'velocity': list(getattr(unit, 'volumes', []) or []),
    }

    n = max((len(v) for v in fields.values()), default=0)
    for k, v in fields.items():
        if len(v) < n:
            fields[k] = v + [None] * (n - len(v))

    df = pd.DataFrame(fields)
    # cumulative onset (start times) - treat None as 0
    df['onset_cumulative'] = (pd.to_numeric(df['onset_interval'], errors='coerce').fillna(0.0)).cumsum()

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

    binary = []
    for i in range(len(unit.pitch_nodes)):
        pitch_nr = unit.pitch_nodes[i]
        duration = unit.durations[i] if i < len (unit.durations) else 1
        onset_interval = unit.onset_intervals[i] if i < len (unit.onset_intervals) else 1
        volume = unit.volumes[i] if i < len (unit.volumes) else 100

        # Convert to binary parts
        pitch_bits = [(pitch_nr >> j) & 1 for j in range(pitch_interval_bits)]
        duration_bits_list = [(duration >> j) & 1 for j in range(duration_bits)]
        onset_bits = [(onset_interval >> j) & 1 for j in range(onset_interval_bits)]
        volume_bits = [(volume >> j) & 1 for j in range(velocity_bits)]

        # Concatenate all bits
        binary += pitch_bits + duration_bits_list + onset_bits + volume_bits

    return binary

def binary_to_unit(binary: List[int]) -> MusicUnit:
    # Transform a binary into a unit
    # Split binary in parts of 'bits' length
    num_parts = len(binary) % total_bits
    binary_parts = []
    for i in range(num_parts):
        # Extract binary elements
        binary_parts += [binary[(i * total_bits):(i * total_bits) + total_bits]]

    unit = MusicUnit(0, "FromBinary")
    for binary_part in binary_parts:
        pitch_nr = int(sum([bit * pow(2, i) for i, bit in enumerate(binary_part)]))
        unit.pitch_nodes += [pitch_nr]  

    return unit

def pattern_to_unit (pattern : MusicPattern) -> MusicUnit :
    # Convert a MusicPattern to a MusicUnit
    unit = MusicUnit(0,'Pattern Unit')
    for interval in pattern.pitch_intervals:
        unit.pitch_nodes += [pattern.tonic + interval]
        unit.durations += [1]  # default duration
        unit.onset_intervals += [1]  # default onset interval
        unit.volumes += [100]  # default volume

    return unit
    
def pattern_to_excel (pattern : MusicPattern) :
    # Save pattern modes to Excel files
    pd_modes = pd.DataFrame(pattern.modes)
    pd_modes_helix = pd.DataFrame(pattern.modes_helix)

    pd_modes.to_excel(Config.DEFAULT_PATH + 'interval_patternModes.xlsx', index=True, sheet_name='MusicPattern')
    pd_modes_helix.to_excel(Config.DEFAULT_PATH + 'interval_patternModesHelix.xlsx', index=True, sheet_name='MusicPattern')
