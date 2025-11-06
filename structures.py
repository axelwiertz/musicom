"""
Musicom structures module
Music composition structures using music21 and musicpy
"""
from typing import Tuple, List, Optional
import numpy as np
import matplotlib.pyplot as plt
import copy

from constants import TwelveTET, MIDIinstrument
from theory import MusicScale, Diatonic, PitchRegister
from rhythm import MusicTime

# Music21 modules: music notation and analysis
from music21 import stream, clef, metadata, tempo, instrument
# MusicPy modules: computational music structures and algorithms
from musicpy import structures

class MusicUnit:
    # A musical unit: a sequence of pitches with timing and dynamics
    def __init__(self,
                time: MusicTime = MusicTime(),
                register: PitchRegister = PitchRegister(),
                pitch_nodes : list [int] = (),
                onset_intervals: list[float] = (),
                durations: list[float] = (),
                velocities: list[int] = (),
                ):
        self.time = time
        self.register = register
        self.pitch_nodes = pitch_nodes
        # The sum of the intervals is the total number of timesteps in MusicTime
        self.onset_intervals = onset_intervals
        self.durations = durations
        self.velocities = velocities
        #self.refresh()
        self.timesteps = sum(self.onset_intervals)

        # m21
        self.stream =  stream.Stream()
        # mp
        self.chord = structures.chord([])

    def __add__(self, other):
        # Combine two musical units
        new_unit = MusicUnit()
        new_unit.pitch_nodes = self.pitch_nodes + other.pitch_nodes
        new_unit.onset_intervals = self.onset_intervals + other.onset_intervals
        new_unit.durations = self.durations + other.durations
        new_unit.velocities = self.velocities + other.velocities

        # m21
        new_unit.stream = copy.deepcopy(self.stream)
        new_unit.stream.append(other.stream)
        # mp
        new_unit.chord = self.chord + other.chord

        new_unit.refresh()
        return new_unit

    def refresh (self):
        # Refresh derived attributes
        self.timesteps = sum(self.onset_intervals)

    @property
    def pitch_intervals(self) -> List[int]:
        if len(self.pitch_nodes) < 2:
            return []
        return [self.pitch_nodes[i+1]-self.pitch_nodes[i] for i in range(len(self.pitch_nodes)-1)]

    def intervals_to_nodes(self, start_pitch_node: int = 0):
        self.pitch_nodes = []
        current_pitch = start_pitch_node
        self.pitch_nodes.append(current_pitch)
        for pitch_interval in self.pitch_intervals:
            current_pitch += pitch_interval
            self.pitch_nodes.append(current_pitch)


    def modulate (self,
                    scale_source : structures.scale,
                    scale_target : structures.scale):
        # Modulate
        self.chord = self.chord.modulation(scale_source, scale_target)

    def add_pitch (self, pitch, duration : int = 1, onset_interval : int = 1, velocity: int = 100):
        self.pitch_nodes += [pitch]
        self.onset_intervals += [onset_interval]
        self.durations += [duration]
        self.velocities += [velocity]

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

        self.track = structures.track([], track_name=name,instrument=midi_instrument)
        self.part = stream.Part()

    def track_notes(self, i: int = 0, j: int = 4):
        return self.track[i:j]


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

    def refresh(self):
        for u in self.units:
            if hasattr(u, 'refresh'):
                u.refresh()

    def total_timesteps(self) -> int:
        """Return total timesteps across all contained units."""
        total = 0
        for u in self.units:
            # prefer timesteps attribute, fall back to onset_intervals
            if hasattr(u, 'timesteps') and u.timesteps is not None:
                total += int(u.timesteps)
            elif hasattr(u, 'onset_intervals'):
                total += int(sum(getattr(u, 'onset_intervals', [])))
        return total

    def to_stream(self) -> stream.Stream:
        """Concatenate the music21 streams from contained units into a single Stream."""
        s = stream.Stream()
        for u in self.units:
            if hasattr(u, 'stream') and u.stream is not None:
                # deep copy to avoid side effects when appending
                s.append(copy.deepcopy(u.stream))
        return s

    def to_track(self):
        """Build a musicpy track by concatenating unit chords if available."""
        t = structures.track([], track_name=self.name)
        for u in self.units:
            if hasattr(u, 'chord') and u.chord is not None:
                try:
                    t = t + u.chord
                except Exception:
                    # fall back to extend if addition is not supported
                    try:
                        t.extend(u.chord)
                    except Exception:
                        pass
        return t

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

        # Music21 score
        self.score = stream.Score()
        self.score.metadata = metadata.Metadata()
        self.score.metadata.title = title
        self.score.metadata.composer = 'Musicom'

        # MusicPy piece
        self.piece = structures.piece

    def score_set_time(self, time : MusicTime):
        # Set the time signature, key signature and tempo
        self.score.insert(0, time.timesignature)
        self.score.insert(0, tempo.MetronomeMark(number=time.bpm))



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
