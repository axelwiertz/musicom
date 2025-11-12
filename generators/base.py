# python
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, List

if TYPE_CHECKING:
    from structures import MusicUnit
else:
    MusicUnit = Any


class Generator(ABC):
    """
    Abstract base for generators. Implementations must return a MusicUnit
    instance from `generate`.
    """

    def __init__(self, seed_unit: "MusicUnit" = None) -> None:
        self.seed_unit = seed_unit

    @abstractmethod
    def generate(self) -> List["MusicUnit"]:
        """Produce a set of MusicUnit instances"""
        raise NotImplementedError
