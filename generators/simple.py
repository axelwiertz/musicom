# python
from __future__ import annotations
from typing import Callable, Any, Dict, TYPE_CHECKING
from .base import Generator

if TYPE_CHECKING:
    from structures import MusicUnit
else:
    MusicUnit = Any


class SimpleGenerator(Generator):
    """
    Simple generator that calls a provided factory to build a MusicUnit.
    This avoids assumptions about the MusicUnit constructor/signature.
    Example usage:
        gen = SimpleGenerator(factory=MusicUnitFactory, params={...})
        mu = gen.generate()
    """

    def __init__(self, *, factory: Callable[..., "MusicUnit"], params: Dict[str, Any] | None = None, seed: int | None = None) -> None:
        super().__init__()
        self.factory = factory
        self.params = params or {}

    def generate(self) -> "MusicUnit":
        # Any generator logic (randomization, transforms) can be applied to params here
        return self.factory(**self.params)
