"""Abstract base class for music transformers."""
from abc import ABC, abstractmethod
from typing import List, Callable
from structures.unit import MusicUnit


class MusicTransformer(ABC):
    """
    Abstract base for a transformator. Implementations can start with a MusicUnit and must return a (list of) MusicUnit
    instance from `transform`.
    """

    def __init__(self, unit_ : MusicUnit) -> None:
        self._unit = unit_
        self._method = None
        self._function = None

    def set_unit(self, unit: MusicUnit) -> None:
        self._unit = unit

    def set_method(self, method: str) -> None:
        self._method = method

    def set_function(self, function: Callable[..., List["MusicUnit"]]) -> None:
        self._function = function

    @abstractmethod
    def transform(self) -> List["MusicUnit"]:
        """Produce a set of MusicUnit instances"""
        raise NotImplementedError


