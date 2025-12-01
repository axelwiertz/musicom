"""Abstract base class for music generators."""
from abc import ABC, abstractmethod
from typing import List
from structures.unit import MusicUnit

class Generator(ABC):
    """
    Abstract base for generators. Implementations must start with a MusicUnit must return a (list of) MusicUnit
    instance from `generate`.
    """

    def __init__(self)-> None:
        self.source_unit = None
        self.method = None

    def set_source_unit(self, source_unit: MusicUnit) -> None:
        self.source_unit = source_unit

    def set_method(self, method: int) -> None:
        self.method = method

    @abstractmethod
    def generate(self) -> List["MusicUnit"]:
        """Produce a set of MusicUnit instances"""
        raise NotImplementedError
