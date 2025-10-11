"""
Musicom library
"""
#from dataclasses import dataclass

import platform
# Showing score without external programs like Musescore
from showscore import show

# Import
import numpy as np
import matplotlib.pyplot as plt

# Music21 modules
from music21 import stream, note, key, scale, chord, interval,
                     roman, converter, instrument, serial, harmony,
                     meter, tempo, metadata, clef, percussion, midi, analysis)

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

class MCMIDIchannel:
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

    # Helper to create an unpitched percussion note by MIDI pitch number
    # General MIDI percussion mapping (channel 10): 35-81 common drums

    def perc_note(self, midi_pitch, dur=0.5, velocity=100):
#        n = note.Unpitched()
        n = note.Note(pitch=midi_pitch, duration=dur)
        # set volume (velocity) for MIDI export
        n.volume.velocity = velocity
        return n

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


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""
Music 21 Tools for streams
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""




def score_show (score_in):
    """
    Show or play the stream
    """
    if platform.system() == 'Windows':
        score_in.show('text')
#    score.show('midi')  # Play MIDI
        show(score_in)  # Show musical notation

    elif platform.system() == 'IOS':
        score_in.show('text')

        # Play the result (IOS):
        #player = sound.MIDIPlayer('target.mid')
        #player.play()
        #player.stop()

def rhythm_circle ():
    # SHow rhythm in circle
    rhythm_circle = Circle(4, ['Down', 'Up','Down', 'Up'], 'Rhythm')
    rhythm_circle.show()


def main():
    # Test functions
    rhythm_circle()


if __name__ == '__main__':
    main()



