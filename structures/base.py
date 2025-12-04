"""Module defining the base class for musical structures."""
from abc import ABC


class Base(ABC):
    # Base class for project structures
    def __init__(self, name: str = 'MusicBase'):
        self.name = name

    def __repr__(self):
        return f"Instance(class='{self.__class__}', name='{self.name}')"


