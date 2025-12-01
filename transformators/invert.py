from typing import Optional
from structures.unit import MusicUnit


def invert(unit : MusicUnit, r: int, pivot: Optional[float] = None, in_place: bool = True) -> Optional[MusicUnit]:
    """Inverts the pitch nodes of a MusicUnit around a pivot point.

    Args:
        unit (MusicUnit): The music unit to be inverted.
        r (int): The number of semitones to invert around the pivot.
        pivot (Optional[float], optional): The pivot pitch. If None, uses the first pitch node's pitch. Defaults to None.
        in_place (bool, optional): If True, modifies the unit in place. If False, returns a new inverted unit. Defaults to True.

    Returns:
        MusicUnit: The inverted music unit if in_place is False, otherwise None.
    """
    if not in_place:
        unit = unit.clone()

    if pivot is None:
        if not unit.pitch_nodes:
            return unit if not in_place else None
        pivot = unit.pitch_nodes[0]

    for i in range(len(unit)):
        distance = unit.pitch_nodes[i] - pivot
        unit.pitch_nodes[i]  = pivot - distance + r

    return unit if not in_place else None