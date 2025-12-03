from typing import Optional
from structures.unit import MusicUnit


def retrograde(unit : MusicUnit, in_place: bool = True) -> Optional[MusicUnit]:
    """Reverses the order of the music unit's elements.

    Args:
        unit (MusicUnit): The music unit to be reversed.
        in_place (bool, optional): If True, modifies the unit in place. If False, returns a new reversed unit. Defaults to True.

    Returns:
        MusicUnit: The reversed music unit if in_place is False, otherwise None.
    """
    if not in_place:
        unit = unit.clone()

    unit.pitch_nodes.reverse()
    unit.onset_intervals.reverse()
    unit.durations.reverse()
    unit.volumes.reverse()

    return unit if not in_place else None
