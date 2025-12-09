"""Module for handling pitch sequences and their standard transformations"""
from typing import Any, List, Optional
from structures.unit import MusicUnit
from transformers.base import MusicTransformer
from music21 import serial


class PitchSequenceTransformer(MusicTransformer):
    PRIME = 'P'
    INVERSION = 'I'
    RETROGRADE = 'R'
    RETROGRADE_INVERSION = 'RI'


    def __init__(self,
                 _unit: MusicUnit,
                 method : str = None,
                 index : int = None) -> None:
        super().__init__(_unit)
        self.method = method
        self.index = index
        self.tone_row = serial.ToneRow(self._unit.pitch_nodes)


    def transform(self) -> List["MusicUnit"]:
        # Produce transformed MusicUnit
        self.execute(self.method, self.index)
        return [self._unit]


    def execute(self, trans : str, index : int = 0):
        # Transform tone row
        # m21
        self.tone_row = serial.ToneRow(self._unit.pitch_nodes).zeroCenteredTransformation (trans, index)
        self._unit.pitch_nodes = self.tone_row.pitches.midiNumbers


    def transpose(self, pitch_interval : int) -> None:
        # Transpose the unit's pitches by interval in positive or negative direction (ASCENDING or DESCENDING)
        self.tone_row = serial.ToneRow(self._unit.pitch_nodes).transpose(pitch_interval)
        self._unit.pitch_nodes = self.tone_row.pitches.midiNumbers


    def change_durations(self, factor_or_func: Any) -> None:
        """Changes the duration of the music unit's elements.
        Args:
            factor_or_func (Any): A scaling factor or a function to determine the new duration.
        Returns:
            MusicUnit
        """
        for d in self._unit.durations:
            if callable(factor_or_func):
                factor = factor_or_func(d)
            else:
                factor = factor_or_func
            d *= factor


def invert(unit : MusicUnit, r: int, pivot: Optional[float] = None):
    """Inverts the pitch nodes of a MusicUnit around a pivot point.

    Args:
        unit (MusicUnit): The music unit to be inverted.
        r (int): The number of semitones to invert around the pivot.
        pivot (Optional[float], optional): The pivot pitch. If None, uses the first pitch node's pitch. Defaults to None.
    """
    if pivot is None:
        pivot = unit.pitch_nodes[0]

    for i in range(len(unit)-1):
        distance = unit.pitch_nodes[i] - pivot
        unit.pitch_nodes[i]  = pivot - distance + r
