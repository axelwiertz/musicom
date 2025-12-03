"""Abstract base class for music factories."""
from abc import ABC, abstractmethod
from typing import List, Callable, Any, Dict, Optional
from structures.unit import MusicUnit


class MusicFactory(ABC):
    """
    Abstract base for factories. Implementations can start with a MusicUnit and must return a (list of) MusicUnit
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
    def produce(self) -> List["MusicUnit"]:
        """Produce a set of MusicUnit instances"""
        raise NotImplementedError


class MusicGenerator(MusicFactory):
    """
    Abstract base for generators. Implementations must return a (list of) MusicUnit
    instance from `produce`.
    """
    def __init__(self)-> None:
        super().__init__()

    @abstractmethod
    def produce(self) -> List["MusicUnit"]:
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

    def produce(self) -> Optional[List["MusicUnit"]]:
        # Any generator logic (randomization, transforms) can be applied to params here
        return self._function(**self._params)


class MusicTransformer(MusicFactory):
    """
    Abstract base for a transformator. Implementations can start with a MusicUnit and must return a (list of) MusicUnit
    instance from `transform`.
    """
    def __init__(self, unit) -> None:
        super().__init__()
        self.set_unit(unit)

    @abstractmethod
    def produce(self) -> List["MusicUnit"]:
        """Produce a set of MusicUnit instances"""
        raise NotImplementedError


