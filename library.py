"""
Musicom library
"""
from dataclasses import dataclass
from typing import Tuple
# Import
import numpy as np
import matplotlib.pyplot as plt

"""
Data structures
"""
def sequence_rotations(sequence: list | tuple) -> list:
    #
    rotations = [sequence[x:] + sequence[:x] for x in range(len(sequence))]
    return rotations


def interval_to_step(intervals: list[int]) -> list[int]:
    # Convert a list of n intervals to a sequential mask with n+1 sequential degree/onset numbers and zeroes
    # Example [2, 3] -> [1, 0, 2, 0, 0, 3]
    steps = []
    sequence_nr = 1
    for x in intervals:
        steps.append(sequence_nr)
        sequence_nr += 1
        for y in range(1, x):
            steps.append(0)
    return steps


"""
Visualization
"""
class Circle:
    def __init__(self, num_parts: int = 12,
                labels : tuple | list  = None,
                title : str = 'Circle of parts and labels'):
        self.num_parts = num_parts
        self.labels = labels
        self.title = title

    def show(self):
        # Show parts (angles) and labels in circle

        # Convert parts to angles
        angles = np.linspace(0, 2 * np.pi, self.num_parts, endpoint=False)

        # Create a figure and axis
        fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})

        # Plot the labels
        for angle, label in zip(angles, self.labels):
            ax.plot(angle, 1, 'o', markersize=10)
            ax.text(angle, 1.1, str(label), ha='center', va='center')

        # Set the title
        ax.set_title(self.title)

        # Show the plot
        plt.show()

def show_plot(yvalues: list):
    # Plot
    # Note that even in the OO-style, we use `.pyplot.figure` to create the Figure.
    fig, ax = plt.subplots(figsize=(5, 2.7), layout='constrained')
    ax.plot(yvalues, label='pitch frequency') # Plot some data on the Axes.
    ax.set_xlabel('Pitch number')  # Add an x-label to the Axes.
    ax.set_ylabel('Frequency')  # Add a y-label to the Axes.
    ax.set_title("Pitches")  # Add a title to the Axes.
    ax.legend()  # Add a legend.
    plt.show()

def rhythm_circle ():
    # SHow rhythm in circle
    rc = Circle(4, ['Down', 'Up','Down', 'Up'], 'Rhythm')
    rc.show()


@dataclass
class Helix:
    def __init__(self,
                 turns: int = 4,  # number of full turns
                points_per_turn: int = 12,  # sampling resolution per turn
                vertical_per_turn: float = 1.0,  # vertical advance per full turn (2π radians)
                start_angle: float = 0.0,  # radians
                direction: int = 1  # 1 for right-handed, -1 for left-handed
    ):
        self.turns = turns
        self.points_per_turn = points_per_turn
        self.vertical_per_turn = vertical_per_turn
        self.start_angle = start_angle
        self.direction = direction

        self.helix = [(point, turn)
                      for turn in range(turns)
                      for point in range(points_per_turn)]

    def index_of(self, point, turn):
        # Get index in helix from (point, turn)
        return turn * self.turns + point

    def get_at(self, idx):
        # Get (point, turn) at index i in helix
        return self.helix[idx % len(self.helix)]

    def length(self):
        # Length of helix
        return len(self.helix)

    def indexes(self):
        return list(range(len(self.helix)))

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

        fig = plt.figure(figsize=(6,6))
        ax = fig.add_subplot(111, projection='3d')
        ax.plot(x, y, z, color='C0', linewidth=2)
        ax.set_box_aspect((1,1,self.turns * self.vertical_per_turn / (2*radius)))  # sensible aspect
        ax.set_xlabel('X'); ax.set_ylabel('Y'); ax.set_zlabel('Z')
        ax.view_init(elev=30, azim=45)
        plt.tight_layout()
        plt.savefig('helix.png', dpi=200)
        plt.show()


def main():
    h = Helix()
    h.show()
    # Test functions
    rhythm_circle()


if __name__ == '__main__':
    main()



