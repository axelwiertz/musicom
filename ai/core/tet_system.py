"""12-Tone Equal Temperament (12TET) System Module."""
from typing import List, Union, Optional, Tuple

PITCH_CLASS_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

class PitchClass:
    def __init__(self, name_or_index: Union[str, int]):
        if isinstance(name_or_index, int):
            self._index = name_or_index % 12
            self._name = PITCH_CLASS_NAMES[self._index]
        else:
            name = str(name_or_index).strip().upper()
            enharmonic = {
                'DB': 'C#', 'EB': 'D#', 'FB': 'E', 'GB': 'F#',
                'AB': 'G#', 'BB': 'A#', 'CB': 'B',
                'E#': 'F', 'B#': 'C',
            }
            name = enharmonic.get(name, name)
            self._index = PITCH_CLASS_NAMES.index(name) if name in PITCH_CLASS_NAMES else 0
            self._name = PITCH_CLASS_NAMES[self._index]

    @property
    def index(self) -> int:
        return self._index

    @property
    def name(self) -> str:
        return self._name

    @property
    def semitone(self) -> int:
        return self._index

    @classmethod
    def from_midi_number(cls, midi: int) -> 'PitchClass':
        return cls(midi % 12)

    def to_midi_number(self, octave: int) -> int:
        return (octave + 1) * 12 + self._index

    def transpose(self, semitones: int) -> 'PitchClass':
        return PitchClass((self._index + semitones) % 12)


class Interval:
    def __init__(self, semitones: int):
        self.semitones = semitones


class Scale:
    def __init__(self, tonic: str, pattern: List[int]):
        self.tonic = PitchClass(tonic) if isinstance(tonic, str) else PitchClass(0)
        self.pattern = pattern

    def get_pitches(self) -> List[PitchClass]:
        pitches = []
        current = 0
        for step in self.pattern:
            current += step
            pitches.append(self.tonic.transpose(current))
        return pitches

    def get_degree(self, degree: int) -> PitchClass:
        if degree <= 1:
            interval = 0
        else:
            idx = min(degree - 1, len(self.pattern))
            interval = sum(self.pattern[:idx])
        return self.tonic.transpose(interval)


class Key:
    def __init__(self, tonic: str, mode: str):
        self.tonic = PitchClass(tonic) if isinstance(tonic, str) else PitchClass(0)
        self.mode = mode


class TimeSignature:
    def __init__(self, numerator: int, denominator: int):
        self.numerator = numerator
        self.denominator = denominator
