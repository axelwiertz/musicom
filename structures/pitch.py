""" Module for pitch structure """
from enum import Enum

class Direction(Enum):
    ASCENDING = 1
    DESCENDING = -1
    STATIONARY = 0

class MusicPitch:
    def __init__(self, midi: int):
        self.midi = midi
        self.pitch_class = midi % 12
        self.octave = (midi // 12) - 1

class MusicPitchClass:
    def __init__(self, index: int):
        self.index = index % 12

class MusicPitchGrid:
    def __init__(self, pitches: list):
        self.pitches = pitches

class MusicPitchRange:
    def __init__(self, start: int, end: int):
        self.start = start
        self.end = end
