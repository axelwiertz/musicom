"""Chromatic pitch helix and range structures."""
from typing import Tuple
import numpy as np
import matplotlib.pyplot as plt
from base.twelvetone import Constants, PitchClass

class Direction:
    ASCENDING = 1
    DESCENDING = -1

class Helix:
    """
    Represents a 3D helix structure.
    Each point is defined by (point, turn) indices.
    """
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

        self.fig = plt.figure(figsize=(6,6))
        self.ax = self.fig.add_subplot(111, projection='3d')


    def index_of(self, point, turn):
        # Get index in helix from (point, turn)
        return turn * self.turns + point

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
        """
        Return an (N,3) NumPy array of (x,y,z) points sampled along the helix.
        """
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
        """
        Return single point at parameter t in [0,1].
        """
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
        theta = np.linspace(0, 2 * np.pi * self.turns, int(self.points_per_turn * self.turns))
        x = radius * np.cos(theta)
        y = radius * np.sin(theta)
        z = (self.vertical_per_turn / (2 * np.pi)) * theta

        self.ax.plot(x, y, z, color='C0', linewidth=2)
        self.ax.set_box_aspect((1,1,self.turns * self.vertical_per_turn / (2*radius)))  # sensible aspect
        self.ax.set_xlabel('X'); self.ax.set_ylabel('Y'); self.ax.set_zlabel('Z')
        self.ax.view_init(elev=30, azim=45)
        plt.tight_layout()
        plt.show()

    @staticmethod
    def save ():
        plt.savefig('helix.png', dpi=200)


"""Chromatic pitch helix structure"""
class Pitches(Helix):
    # Chromatic pitches in helix
    def __init__(self):
        # Represent as helix of (pitch_class, octave): (0, 4)
        super().__init__(Constants.TWELVE, Constants.OCTAVES)

    def transpose(self, i, interval_steps, direction : int  = Direction.ASCENDING):
        # Transpose index i by interval_steps in direction (ASCENDING or DESCENDING)
        return (i + direction*interval_steps) % len(self._data)


class PitchRange:
    # Chromatic pitch range
    def __init__(self,  pitch_class_start=PitchClass.A,
                        octave_start=0,
                        pitch_class_end=PitchClass.C,
                        octave_end=8):

        self._pitches = Pitches()

        self.index_start = self._pitches.index_of(pitch_class_start, octave_start)
        self.index_end = self._pitches.index_of(pitch_class_end, octave_end)