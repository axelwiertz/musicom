"""Twelve tone equal temperament: Chromatic pitches in helix structure."""
from typing import Tuple
import numpy as np
import matplotlib.pyplot as plt

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

    INTERVAL_NUMBER_QUALITY = {
        0: "P1", 1: "m2", 2: "M2", 3: "m3", 4: "M3", 5: "P4",
        6: "TT", 7: "P5", 8: "m6", 9: "M6", 10: "m7", 11: "M7"
    }

    def __init__(self):
        pass

    @staticmethod
    def interval(self, a: int, b: int) -> int:
        return (a - b) % self.TWELVE



class Direction:
    ASCENDING = 1
    DESCENDING = -1

class Helix:
    POINT = 0
    TURN = 1
    """Represents a 3D helix structure. Each point is defined by (point, turn) indices."""
    def __init__(self,
                points_per_turn: int = 4,  # sampling resolution per turn
                turns: int = 4,  # number of full turns
                vertical_per_turn: float = 1.0,  # vertical advance per full turn (2π radians)
                start_angle: float = 0.0,  # radians
                direction: int = 1  # 1 for right-handed, -1 for left-handed
    ):
        self.turns = turns
        self.points_per_turn = points_per_turn
        self.vertical_per_turn = vertical_per_turn
        self.start_angle = start_angle
        self.direction = direction

        self._data = [(point, turn)
                      for turn in range(turns)
                      for point in range(points_per_turn)]

        self.fig = None
        self.ax = None

    def __len__(self):
        return len(self._data)

    def point_at_index(self, idx):
        # Get (point, turn) at index i in helix
        return self._data[idx % len(self._data)][self.POINT]

    def turn_at_index(self, idx):
        # Get turn at index i in helix
        return self._data[idx % len(self._data)][self.TURN]

    def index_of(self, point, turn):
        # Get index in helix from (point, turn)
        return turn * self.points_per_turn + point

    def get_at(self, idx):
        # Get (point, turn) at index i in helix
        return self._data[idx % len(self._data)]

    def indexes(self):
        return list(range(len(self._data)))

    def total_points(self) -> int:
        return max(1, int(self.points_per_turn * max(0.0, self.turns)))

    def angle_range(self) -> Tuple[float, float]:
        start = self.start_angle
        end = start + self.direction * 2 * np.pi * self.turns
        return start, end

    def points(self, radius: float = 1.0) -> np.ndarray:
        """Return an (N,3) NumPy array of (x,y,z) points sampled along the helix."""
        n = self.total_points()
        if n == 0:
            return np.empty((0, 3), dtype=float)

        start, end = self.angle_range()
        thetas = np.linspace(start, end, n)
        x = radius * np.cos(thetas)
        y = radius * np.sin(thetas)
        # z increases linearly with angle: vertical per full turn (2π)
        z = (self.vertical_per_turn * (thetas - start)) / (2 * np.pi)
        return np.stack((x, y, z), axis=-1)

    def point_at(self, t: float, radius: float = 1.0) -> Tuple[float, float, float]:
        """Return single point at parameter t in [0,1]."""
        t_clamped = min(1.0, max(0.0, t))
        start, end = self.angle_range()
        theta = start + (end - start) * t_clamped
        x = radius * np.cos(theta)
        y = radius * np.sin(theta)
        z = (self.vertical_per_turn * (theta - start)) / (2 * np.pi)
        return float(x), float(y), float(z)

    def show (self,
                radius = 1.0,
            ):
        self.fig = plt.figure(figsize=(6,6))
        self.ax = self.fig.add_subplot(111, projection='3d')

        start, end = self.angle_range()
        theta = np.linspace(start, end, self.total_points())
        x = radius * np.cos(theta)
        y = radius * np.sin(theta)
        z = (self.vertical_per_turn / (2 * np.pi)) * (theta - start)

        self.ax.plot(x, y, z, color='C0', linewidth=2)
        self.ax.set_box_aspect((1,1,self.turns * self.vertical_per_turn / (2*radius)))  # sensible aspect
        self.ax.set_xlabel('X'); self.ax.set_ylabel('Y'); self.ax.set_zlabel('Z')
        self.ax.view_init(elev=30, azim=45)
        plt.tight_layout()
        plt.show()
        #plt.savefig('helix.png', dpi=200)


"""Chromatic pitch helix structure"""
class MusicPitch(Helix):
    OCTAVES = 9  # Number of octaves in the chromatic pitch set
    # General twelve-tone equal temperament constants
    CENTS : float = 100  # Cents in semitone

    # Chromatic pitches in helix
    def __init__(self):
        # Represent as helix of (pitch_class = point, octave = turn): (0, 4)
        super().__init__(MusicPitchClass.TWELVE, self.OCTAVES)

    def transpose(self, i, interval_steps, direction : int  = Direction.ASCENDING):
        # Transpose index i by interval_steps in direction (ASCENDING or DESCENDING)
        return (i + direction*interval_steps) % len(self._data)

    def octave_of (self, i) -> int:
        """Return octave number for given pitch index."""
        if i < 0 or i >= len(self._data):
            raise ValueError("Pitch index out of range")
        return self.turn_at_index(i)

    def pitch_class_of (self, i) -> int:
        """Return pitch class number (0-11) for given pitch index."""
        if i < 0 or i >= len(self._data):
            raise ValueError("Pitch index out of range")
        return self.point_at_index(i)

    def midi_to_pitch (self, midi : int) -> int:
        """Return pitch class number (0-11) for given MIDI note number."""
        if midi < 0 or midi > 127:
            raise ValueError("MIDI number must be in range 0-127")
        return self.index_of(midi % MusicPitchClass.TWELVE, int(midi // MusicPitchClass.TWELVE) - 1)

    def midi (self, i) -> int:
        if i < 0 or i >= len(self._data):
            raise ValueError("Pitch index out of range")
        return self.pitch_class_of(i) + (self.octave_of(i) * MusicPitchClass.TWELVE)


class PitchRange:
    # Chromatic pitch range
    def __init__(self,  pitch_class_start=MusicPitchClass.A,
                        octave_start=0,
                        pitch_class_end=MusicPitchClass.C,
                        octave_end=8):

        self._pitches = MusicPitch()

        self.index_start = self._pitches.index_of(pitch_class_start, octave_start)
        self.index_end = self._pitches.index_of(pitch_class_end, octave_end)


