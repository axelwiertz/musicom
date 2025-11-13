import os
import pandas as pd
from utilities import Config
from structures import MusicUnit

# --- DataFrame / Excel helpers for MusicUnit ---
def unit_to_dataframe(unit: MusicUnit) -> pd.DataFrame:
    """Convert a MusicUnit into a pandas DataFrame.

    Columns: pitch_node, pitch_interval, onset_interval, duration, velocity, onset_cumulative
    Handles uneven field lengths by padding with None.
    """
    # lazy import fallback for environments without pandas available at module import
    try:
        import pandas as _pd
    except Exception:
        raise RuntimeError("pandas is required for unit_to_dataframe; please install it (pip install pandas)")

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

    df = _pd.DataFrame(fields)
    # cumulative onset (start times) - treat None as 0
    try:
        df['onset_cumulative'] = (_pd.to_numeric(df['onset_interval'], errors='coerce').fillna(0.0)).cumsum()
    except Exception:
        # best-effort: ignore if conversion fails
        pass

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
