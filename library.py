"""
Musicom library
"""
#from dataclasses import dataclass


# Import
import numpy as np
import matplotlib.pyplot as plt


class Config:
    # Default configuration
    DEFAULT_PATH = 'C:\\temp\\Music\\'
    DEFAULT_MIDI_FILE_IN = 'in.mid'
    DEFAULT_MIDI_FILE_OUT = 'out.mid'


class MIDIinstrument:

    # General MIDI instrument numbers (0-127)
    PIANO = 1
    CHURCH_ORGAN = 20
    ACOUSTIC_GUITAR = 25
    VIOLIN = 41
    STRING_ENSEMBLE = 49
    TRUMPET = 57
    FLUTE = 74
    SYNTH_PAD = 88

class MIDIchannel:
    PERCUSSION = 10  # Channel 10 (index 9) is reserved for percussion in General MIDI
    PERCUSSION_INDEX = 9

class MIDIpercussion:
    # MIDI percussion mapping (channel 10): 35-81 common drums
    # See https://www.midi.org/specifications-old/item/gm-level-1-s
    BASS_DRUM = 36
    ACOUSTIC_SNARE = 38
    CLOSED_HIHAT = 42
    LOW_TOM = 45
    MID_TOM = 47
    HIGH_TOM = 50
    RIDE_CYMBAL = 51
    CRASH_CYMBAL = 49
    HAND_CLAP = 39
    CLAVES = 75
    MARACAS = 70
    COWBELL = 56
    VIBRASLAP = 58
    WOODBLOCK = 76


def interval_to_step (intervals: list[int]) -> list[int]:
    # Convert a list of intervals to a sequential mask with sequential degree/onset numbers and zeroes
    # Example [2, 3] -> [1, 0, 2, 0, 0, 3]
    steps = []
    sequence_nr = 1
    for x in intervals:
        steps.append(sequence_nr)
        sequence_nr += 1
        for y in range(1,x):
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


def main():
    # Test functions
    rhythm_circle()


if __name__ == '__main__':
    main()



