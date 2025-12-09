"""Base classes for music generators."""
from abc import ABC, abstractmethod
from typing import List, Callable, Any, Dict, Optional
from structures.unit import MusicUnit


class MusicGenerator(ABC):
    """
    Abstract base for generators. Implementations must return a (list of) MusicUnit
    instance from `produce`.
    """
    def __init__(self)-> None:
        self._unit = None
        self._method = None
        self._function = None

    def set_unit(self, unit : MusicUnit) -> None:
        self._unit = unit

    def set_method(self, method: str) -> None:
        self._method = method

    def set_function(self, function: Callable[..., List["MusicUnit"]]) -> None:
        self._function = function

    @abstractmethod
    def generate(self) -> List["MusicUnit"]:
        """Produce a set of MusicUnit instances"""
        raise NotImplementedError


class FunctionGenerator(MusicGenerator):
    """
    Generator that calls a provided function to build a MusicUnit.
    This avoids assumptions about the MusicUnit constructor/signature.
    Example usage:
        gen = FunctionGenerator(function=MusicUnitFactory, params={...})
        mu = gen.produce()
    """

    def __init__(self, *, function: Callable[..., List["MusicUnit"]], params: Dict[str, Any] | None = None) -> None:
        super().__init__()
        self._function = function
        self._params = params or {}

    def generate(self) -> Optional[List["MusicUnit"]]:
        # Any generator logic (randomization, transforms) can be applied to params here
        return self._function(**self._params)

