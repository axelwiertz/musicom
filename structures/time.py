"""Music time representation: rhythm and meter as circular structures."""
import numpy as np
import matplotlib.pyplot as plt

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


class MusicTime (Circle):
    # Horizontal time: rhythmic cycles and tempo
    def __init__(self,
                 timesteps: int = 8, # Number of timesteps (ticks) per cycle (measure, bar)
                 beats_in_measure: int = 4, # Number of beats in a measure
                 beat_note: int = 4, # Note value that gets the beat (e.g., 4 = quarter note)
                 bpm: int = 100, # Tempo in beats per minute
                 ):
        # Timestep (tick) is the smallest relative unit, represented as integer
        self.timesteps = timesteps
        super().__init__(timesteps, labels=[str(i+1) for i in range(timesteps)])
        # Meter: measure cycle of beats
        self.beats_in_measure = beats_in_measure
        self.beat_note = beat_note
        # Linear time: real time / play
        # tempo
        self.bpm = bpm
        self.seconds_per_beat = 60.0 / bpm