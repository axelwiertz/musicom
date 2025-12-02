"""Module for handling pitch sequences and their transformations using music21 library."""
from typing import Any, List

from music21 import serial

from structures.unit import MusicUnit
from structures.factory import MusicTransformator


class PitchSequenceTransformator(MusicTransformator):
    PRIME = 'P'
    INVERSION = 'I'
    RETROGRADE = 'R'
    RETROGRADE_INVERSION = 'RI'


    def __init__(self,
                 source_unit: MusicUnit,
                 method : str = None,
                 index : int = None) -> None:
        super().__init__(source_unit)
        self.method = method
        self.index = index
        self.tone_row = serial.ToneRow(self.source_unit.pitch_nodes)


    def produce(self) -> List["MusicUnit"]:
        # Produce transformed MusicUnit
        self.transform(self.method, self.index)
        return [self.source_unit]


    def transform(self, trans : str, index : int = 0):
        # Transform tone row
        self.tone_row = serial.ToneRow(self.pitch_nodes).zeroCenteredTransformation (trans, index)
        self.pitch_nodes = self.tone_row.pitches.midiNumbers


    def transpose(self, pitch_interval : int) -> None:
        # Transpose the unit's pitches by interval in positive or negative direction (ASCENDING or DESCENDING)
        self.tone_row = serial.ToneRow(self.pitch_nodes).transpose(pitch_interval)
        self.pitch_nodes = self.tone_row.pitches.midiNumbers


    def change_durations(self, factor_or_func: Any) -> None:
        """Changes the duration of the music unit's elements.
        Args:
            factor_or_func (Any): A scaling factor or a function to determine the new duration.
        Returns:
            MusicUnit
        """
        for d in self.source_unit.durations:
            if callable(factor_or_func):
                factor = factor_or_func(d)
            else:
                factor = factor_or_func
            d *= factor
