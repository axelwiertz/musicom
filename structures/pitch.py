"""Twelve tone equal temperament: Chromatic pitches in helix structure."""
import numpy as np
from visualization import Helix
from typing import Tuple, FrozenSet, Optional, List
from dataclasses import dataclass

"""Twelve-tone equal temperament constants and pitch class definitions"""


""" TODO: Add
Equal‑tempered constants
12‑TET interval ratios
Equal temperament ratios
Semitone ratio (for the base constant: 2^(1/12))
Twelfth‑root‑of‑2 constant
Step ratio (12‑tone equal temperament)
Equal‑tempered step size
Pitch‑class ratios (12‑TET)
Frequency ratio for a semitone
Log‑frequency increment (12‑TET)
"""

@dataclass(frozen=True)
class MusicPitchClass:
    TWELVE = 12  # Number of pitch classes 0-11
    # Pitch class numbers and names
    C = 0
    C_SHARP = D_FLAT = 1
    D = 2
    D_SHARP = E_FLAT = 3
    E = 4
    F = 5
    F_SHARP = G_FLAT = 6
    G = 7
    G_SHARP = A_FLAT = 8
    A = 9
    A_SHARP = B_FLAT = 10
    B = 11
    # 12-tone pitch class numbers and names
    NUMBERS = (C, C_SHARP, D, D_SHARP, E, F, F_SHARP, G, G_SHARP, A, A_SHARP, B)
    NAMES_SHARP = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    NAMES_FLATMAP = {'D': 'C#', 'E': 'D#', 'F': 'E', 'G': 'F#', 'A': 'G#', 'B': 'A#', 'C': 'B'}


    def __init__(self):
        pass

    @staticmethod
    def interval(self, a: int, b: int) -> int:
        return (a - b) % self.TWELVE


class Direction:
    ASCENDING = 1
    DESCENDING = -1


"""Chromatic pitches """
class MusicPitches:
    OCTAVES = 9  # Number of octaves in the chromatic pitch set
    # General twelve-tone equal temperament constants
    CENTS: float = 100  # Cents in semitone

    def __init__(self):
        # Contain a Helix as internal data structure
        # Represent as helix of (pitch_class = point, octave = turn): (0, 4)
        self._helix = Helix(MusicPitchClass.TWELVE, self.OCTAVES)

        self._data = np.array(range(MusicPitchClass.TWELVE, self.OCTAVES))

    def __len__(self):
        return len(self._helix)

    @property
    def helix(self) -> Helix:
        """Access the underlying helix structure."""
        return self._helix

    def transpose(self, i, interval_steps, direction: int = Direction.ASCENDING):
        # Transpose index i by interval_steps in direction (ASCENDING or DESCENDING)
        return (i + direction * interval_steps) % len(self._helix)

    def octave_of(self, i) -> int:
        """Return octave number for given pitch index."""
        if i < 0 or i >= len(self._helix):
            raise ValueError("Pitch index out of range")
        return self._helix.turn_at_index(i)

    def pitch_class_of(self, i) -> int:
        """Return pitch class number (0-11) for given pitch index."""
        if i < 0 or i >= len(self._helix):
            raise ValueError("Pitch index out of range")
        return self._helix.point_at_index(i)

    def index_of(self, pitch_class: int, octave: int) -> int:
        """Return the pitch index for a given pitch class and octave."""
        return self._helix.index_of(pitch_class, octave)

    def get_at(self, idx):
        """Get (pitch_class, octave) at index idx."""
        return self._helix.get_at(idx)

    def midi_to_pitch(self, midi: int) -> int:
        """Return pitch index for given MIDI note number."""
        if midi < 0 or midi > 127:
            raise ValueError("MIDI number must be in range 0-127")
        return self._helix.index_of(midi % MusicPitchClass.TWELVE, int(midi // MusicPitchClass.TWELVE) - 1)

    def midi(self, i) -> int:
        """Return MIDI note number for given pitch index."""
        if i < 0 or i >= len(self._helix):
            raise ValueError("Pitch index out of range")
        return self.pitch_class_of(i) + (self.octave_of(i) * MusicPitchClass.TWELVE)

    def show(self, radius: float = 1.0):
        """Visualize the pitch helix """
        self._helix.plot_3d(radius=radius)

    @property
    def helix_indices(self) -> List[int]:
        """Map pattern pitches to helix indices with octave tracking."""
        if self._tonic_pitch_class is None:
            return []

        indices = []
        current_octave = self._tonic_octave
        prev_pitch_class = self._tonic_pitch_class

        for pc in self.pitch_classes:
            # Detect octave wrap-around
            if pc < prev_pitch_class:
                current_octave += 1
            idx = self._pitches.index_of(pc, current_octave)
            indices.append(idx)
            prev_pitch_class = pc

        return indices


class PitchRange:
    # Chromatic pitch range
    def __init__(self,  pitch_class_start=MusicPitchClass.A,
                        octave_start=0,
                        pitch_class_end=MusicPitchClass.C,
                        octave_end=8):

        self._pitches = MusicPitches()

        self.index_start = self._pitches.index_of(pitch_class_start, octave_start)
        self.index_end = self._pitches.index_of(pitch_class_end, octave_end)
