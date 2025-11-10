"""
Musicom generators module.
Base class for all generator implementations.
"""
from typing import List
from structures import MusicUnit

class Generator:
    def __init__(self,
                 source_unit: MusicUnit = None) -> None:
        self.source_unit = source_unit
        self.target_units : list[MusicUnit] = []

    def generate(self) -> List[MusicUnit]:
        raise NotImplementedError("Subclasses should implement this method.")