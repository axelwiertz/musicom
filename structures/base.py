"""Module defining the base classes for musical structures."""
from typing import Tuple
import numpy as np
import matplotlib.pyplot as plt

class MusicBase:
    # Base class for musical structures
    def __init__(self, _id: int = 0, name: str = 'MusicBase'):
        self._id = _id
        self.name = name

    def __repr__(self):
        return f"Instance(class='{self.__class__}', id={self._id}, name='{self.name}')"


