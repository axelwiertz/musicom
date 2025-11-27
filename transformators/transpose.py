from typing import Optional
from structures.unit import MusicUnit

def transpose(unit : MusicUnit, r: int, in_place: bool = True) -> Optional[MusicUnit]:
    """Transpose the pitches of a MusicUnit by a given interval.

    Args:
        unit (MusicUnit): The musical unit to transpose.
        r (int): The interval by which to transpose the pitches.
        in_place (bool, optional): If True, modify the unit in place. If False, return a new transposed unit. Defaults to True.

    Returns:
        Optional[MusicUnit]: The transposed MusicUnit if in_place is False, otherwise None.
    """
    if in_place:
        unit.pitch_nodes = [p + r for p in unit.pitch_nodes]
    else:
        new_unit = unit.clone()
        new_unit.pitch_nodes = [p + r for p in new_unit.pitch_nodes]
        return new_unit
    return None
