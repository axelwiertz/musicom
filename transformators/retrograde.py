from typing import Optional
from structures.unit import MusicUnit


def retrograde(unit : MusicUnit, r: int, in_place: bool = True) -> Optional[MusicUnit]:
    """Reverses the order of the music unit's elements.

    Args:
        unit (MusicUnit): The music unit to be reversed.
        r (int): An integer parameter (not used in this function).
        in_place (bool, optional): If True, modifies the unit in place. If False, returns a new reversed unit. Defaults to True.

    Returns:
        MusicUnit: The reversed music unit if in_place is False, otherwise None.
    """
    if not in_place:
        unit = unit.clone()

    unit.elements.reverse()

    if not in_place:
        return unit
