"""
Musicom structures module
Music composition structures
"""
from typing import Tuple, List
import numpy as np
import matplotlib.pyplot as plt

from constants import TwelveTET, MIDIinstrument
from converters import unit_to_chord
from theory import MusicScale, Diatonic, PitchRegister
from rhythm import MusicTime

# Music21 modules: music notation and analysis
from music21 import clef, instrument
# MusicPy modules: computational music structures and algorithms
from musicpy import structures

class MusicUnit:
    # A musical unit: a sequence of pitches with timing and dynamics
    def __init__(self,
                time: MusicTime = MusicTime(),
                pitch_nodes : list [int] = (),
                onset_intervals: list[float] = (),
                durations: list[float] = (),
                volumes: list[int] = (),
                ):
        self.time = time
        self.pitch_nodes = pitch_nodes
        self.onset_intervals = onset_intervals
        self.durations = durations
        self.volumes = volumes

    def __add__(self, other):
        # Combine two musical units
        new_unit = MusicUnit()
        new_unit.pitch_nodes = self.pitch_nodes + other.pitch_nodes
        new_unit.onset_intervals = self.onset_intervals + other.onset_intervals
        new_unit.durations = self.durations + other.durations
        new_unit.volumes = self.volumes + other.volumes
        return new_unit

    @property
    def timesteps (self):
        # The sum of the onset intervals is the total number of timesteps in MusicTime
        return sum(self.onset_intervals)

    @property
    def pitch_intervals(self) -> List[int]:
        if len(self.pitch_nodes) < 2:
            return []
        return [self.pitch_nodes[i+1]-self.pitch_nodes[i] for i in range(len(self.pitch_nodes)-1)]

    def modulate (self,
                    scale_source : structures.scale,
                    scale_target : structures.scale):
        # Modulate
        self.pitch_nodes = unit_to_chord(self).modulation(scale_source, scale_target).pitches

    def add_pitch (self, pitch, duration : int = 1, onset_interval : int = 1, volume: int = 100):
        self.pitch_nodes += [pitch]
        self.onset_intervals += [onset_interval]
        self.durations += [duration]
        self.volumes += [volume]

    def add_pitches_vertical (self, pitches, duration=4):
        for p in pitches:
            self.add_pitch(p,0, duration)

class MusicVoice:
    # A musical voice
    def __init__(self,
                 name: str = 'Voice',
                 units: list[MusicUnit] = (),
                 midi_instrument: int = MIDIinstrument.PIANO,
                 ):
        self.name = name
        self.midi_instrument = midi_instrument
        self.units = units

# --- new: MusicSection ---
class MusicSection:
    """A section is an ordered collection of MusicUnit objects with helpers.

    Minimal contract:
    - inputs: list of MusicUnit (optional)
    - outputs: query methods (length, total_timesteps), conversions (to_stream, to_track)
    - error modes: accepts empty lists; methods raise IndexError for invalid indices where appropriate.
    """
    def __init__(self, name: str = 'Section', units: list[MusicUnit] | None = None):
        self.name = name
        self.units = list(units) if units is not None else []

    def append(self, unit: MusicUnit):
        """Append a MusicUnit to the section."""
        self.units.append(unit)

    def extend(self, units: list[MusicUnit]):
        """Extend section with an iterable of MusicUnit."""
        self.units.extend(units)

    def insert(self, index: int, unit: MusicUnit):
        self.units.insert(index, unit)

    def remove_at(self, index: int):
        """Remove and return unit at index."""
        return self.units.pop(index)

    def __len__(self):
        return len(self.units)

    def __iter__(self):
        return iter(self.units)

    def __getitem__(self, idx):
        return self.units[idx]

    def __add__(self, other: 'MusicSection') -> 'MusicSection':
        return MusicSection(name=f"{self.name}+{other.name}", units=self.units + other.units)


class MusicComposition:
    #
    def __init__(self,
                 title: str = "Composition",
                 main_scale: MusicScale = MusicScale(Diatonic.HEPTA, Diatonic.SCALE, TwelveTET.C, Diatonic.major_mode),
                 voices : list[MusicVoice] = (),
                 main_progression: list = (),
                 form: list = ()
                ):

        self.title = title
        self.form = form
        self.main_scale = main_scale
        self.main_progression = main_progression
        self.voices = voices


class PercussionUnit(MusicUnit):

    def __init__(self):
        super().__init__()
        self.clef = clef.PercussionClef()
        self.instrument = instrument.Woodblock()

"""
Visualization
"""
class Circle:
    def __init__(self,
                 num_parts: int = 4,
                labels : list[str] = ('1','2','3','4')):
        self.num_parts = num_parts
        self.labels = labels

    def show(self,
                title : str = 'Circle of parts and labels'):
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
        ax.set_title(title)

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
    rc = Circle(4, ['Down', 'Up','Down', 'Up'])
    rc.show()


class Helix:
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
