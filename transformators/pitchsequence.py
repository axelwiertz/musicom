"""
Musicom transformators
Transform musical pitch sequences using serial techniques.
"""

from music21 import serial

class PitchSequence:
    PRIME = 'P'
    INVERSION = 'I'
    RETROGRADE = 'R'
    RETROGRADE_INVERSION = 'RI'

    def __init__(self, pitch_nodes: list[int]):
        self.pitch_nodes = pitch_nodes
        self.tonerow = serial.ToneRow(self.pitch_nodes)

    def transform (self, trans : str, index : int = 0):
        # Transform tone row
        self.tonerow = serial.ToneRow(self.pitch_nodes).zeroCenteredTransformation (trans, index)
        self.pitch_nodes = self.tonerow.pitches.midiNumbers

    def transpose (self, pitch_interval : int):
        # Transpose the unit's pitches by interval in positive or negative direction (ASCENDING or DESCENDING)
        self.tonerow = serial.ToneRow(self.pitch_nodes).transpose(pitch_interval)
        self.pitch_nodes = self.tonerow.pitches.midiNumbers
