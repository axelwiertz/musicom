"""Module for handling pitch sequences and their standard transformations"""
from typing import List
from structures.unit import MusicUnit
from transformers.base import MusicTransformer
from music21 import serial


class PitchSequenceTransformer(MusicTransformer):
    PRIME = 'P'
    INVERSION = 'I'
    RETROGRADE = 'R'
    RETROGRADE_INVERSION = 'RI'
    """Handles pitch sequence transformations such as prime, inversion, retrograde, and retrograde inversion."""
    def __init__(self,
                 _unit: MusicUnit,
                 method : str = None,
                 index : int = None) -> None:
        super().__init__(_unit)
        self.method = method
        self.index = index
        self.tone_row = serial.ToneRow(self._unit.pitches)

    def transform(self) -> List["MusicUnit"]:
        # Produce transformed MusicUnit
        self.execute(self.method, self.index)
        return [self._unit]

    def execute(self, trans : str, index : int = 0):
        # Transform tone row
        # m21
        self.tone_row = serial.ToneRow(self._unit.pitches).zeroCenteredTransformation (trans, index)
        self._unit = MusicUnit(pitches=[p.midi for p in self.tone_row.pitches])
