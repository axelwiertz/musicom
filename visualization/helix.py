"""Helix plotting utilities using matplotlib.

These functions are intentionally decoupled from the core Helix structure
(see structures.pitch.Helix) so that visualization remains an optional,
side-effecting concern.
"""
from typing import Tuple
import matplotlib.pyplot as plt
import numpy as np


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

    def _total_points(self) -> int:
        return max(1, int(self.points_per_turn * max(0.0, self.turns)))


    def angle_range(self) -> Tuple[float, float]:
        start = self.start_angle
        end = start + self.direction * 2 * np.pi * self.turns
        return start, end

    def points(self, radius: float = 1.0) -> np.ndarray:
        """Return an (N,3) NumPy array of (x,y,z) points sampled along the self."""
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


    def plot_3d(self, radius: float = 1.0, highlight_indices: list[int] | None = None):
        """
        Plot the helix in 3D.

        Args:
            radius: Radius of the helix.
            highlight_indices: Optional list of indices to highlight (e.g., MIDI numbers).
                              If None, plots all points.
        """

        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')

        # Generate helix coordinates
        theta = np.linspace(0, 2 * np.pi * self._num_turns, self._total_points)
        z = np.linspace(0, self._num_turns, self._total_points)
        x = radius * np.cos(theta)
        y = radius * np.sin(theta)

        # Plot the helix curve
        ax.plot(x, y, z, 'b-', alpha=0.3, linewidth=0.5)

        if highlight_indices is not None:
            # Only plot highlighted points
            valid_indices = [i for i in highlight_indices if 0 <= i < self._total_points]
            if valid_indices:
                ax.scatter(x[valid_indices], y[valid_indices], z[valid_indices],
                          c='red', s=50, alpha=0.8)
        else:
            # Plot all points
            ax.scatter(x, y, z, c=z, cmap='viridis', s=20, alpha=0.6)

        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Octave')
        ax.set_title('Pitch Helix')

        plt.show()
