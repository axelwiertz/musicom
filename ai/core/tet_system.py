"""
12-Tone Equal Temperament (12TET) System Module.
"""
from typing import List, Union, Optional, Tuple

class PitchClass:
    def __init__(self, name_or_index: Union[str, int]):
        self.index = name_or_index % 12 if isinstance(name_or_index, int) else 0

class Interval:
    def __init__(self, semitones: int):
        self.semitones = semitones

class Scale:
    def __init__(self, tonic: str, pattern: List[int]):
        self.tonic = tonic
        self.pattern = pattern

class Key:
    def __init__(self, tonic: str, mode: str):
        self.tonic = tonic
        self.mode = mode

class TimeSignature:
    def __init__(self, numerator: int, denominator: int):
        self.numerator = numerator
        self.denominator = denominator
