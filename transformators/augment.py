from typing import Any, Optional
from structures.unit import MusicUnit

def augment(unit : MusicUnit, factor_or_func: Any, in_place: bool = True) -> Optional[MusicUnit]:
    """Augments the duration of the music unit's elements.

    Args:
        unit (MusicUnit): The music unit to be augmented.
        factor_or_func (Any): A scaling factor or a function to determine the new duration.
        in_place (bool, optional): If True, modifies the unit in place. If False, returns a new augmented unit. Defaults to True.

    Returns:
        MusicUnit: The augmented music unit if in_place is False, otherwise None.
    """
    if not in_place:
        unit = unit.clone()

    for d in unit.durations:
        if callable(factor_or_func):
            factor = factor_or_func(d)
        else:
            factor = factor_or_func
        d *= factor

    return unit if in_place else None


