""" Module for transforming musical streams with various note transformations. """
import random
from copy import deepcopy
from structures import MusicUnit
from .base import MusicTransformer
from music21 import stream, note, scale

class EmbellishmentTransformer(MusicTransformer):
    def transform(self, unit: MusicUnit) -> MusicUnit:
        new_unit = deepcopy(unit)
        # Basic pass-through implementation
        return new_unit
