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

from theory import ChromaticLayer, DiatonicLayer, MCTime

# Music21 modules
from music21 import (stream, note, key, scale, chord, interval,
                     roman, converter, instrument, serial, harmony,
                     meter, tempo, metadata, clef, percussion, midi, analysis)

class Config:
    # Default configuration
    DEFAULT_PATH = 'C:\\temp\\Music\\'
    DEFAULT_MIDI_FILE_IN = 'in.mid'
    DEFAULT_MIDI_FILE_OUT = 'out.mid'


"""
Visualization
"""

def show_circle(num_parts: int = 12, labels : tuple | list  = ChromaticLayer.PITCHCLASSES_STR, title : str = 'Circle of parts and labels' ):
    # Show parts (angles) and labels in circle

    # Convert parts to angles
    angles = np.linspace(0, 2 * np.pi, num_parts, endpoint=False)

    # Create a figure and axis
    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})

    # Plot the labels
    for angle, label in zip(angles, labels):
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


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""
Music 21 Tools for streams
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""

def part_create_from_stream (stream_in: stream.Stream,
                             instr: instrument.Instrument = instrument.Piano(),
                             clef_in : clef.Clef = clef.TrebleClef()) -> stream.Part:
    # Transfer notes, rests and chords from the original stream to a new Part
    part_out = stream.Part()
    # Add instrument of part
    part_out.insert(0, instr)
    # Add clef of part
    part_out.insert(0, clef_in)

    # Create a Part and add notes, rests and chords
    for element in stream_in:
        if isinstance(element, (note.Note, note.Rest, chord.Chord)):
            part_out.append(element)

    return part_out


def stream_create(pitches : list[int|str],
                  onset_intervals: list[float],
                  durations : list[float],
                  velocities : list[int] = (100)) -> stream.Stream:
    # Create a part with notes and rests
    stream_out = stream.Stream()

    # Iterate over the list of pitches, intervals and durations
    for i in range(len(pitches)) :
        # Add notes and rests to the stream
        restduration = onset_intervals[i] - durations[i]
        if restduration > 0:
            stream_out.append(note.Rest(quarterLength=restduration))
        else:
            new_note = note.Note(pitch=pitches[i], quarterLength=durations[i])
            new_note.volume.velocity = velocities[i]
            stream_out.append(new_note)

    return stream_out

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
    show_circle(4, ['Down', 'Up','Down', 'Up'], 'Rhythm')


def main():
    # Test functions
    rhythm_circle()


if __name__ == '__main__':
    main()



