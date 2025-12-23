"""Convert score to visual representation or sound playback based on platform."""
import matplotlib.pyplot as plt
import platform
from showscore import show
from music21 import stream

def score_to_visual(score: stream.Score):
    """
    Show or play the score depending on the platform.
    1. On Windows, display text and musical notation.
    2. On iOS, display text (MIDI playback code is commented out).
    """
    if platform.system() == 'Windows':
        # score.show('text')
        #    score.show('midi')  # Play MIDI
        # Showing score without external programs like Musescore
        show(score)  # Show musical notation

    elif platform.system() == 'IOS':
        score.show('text')


def score_to_sound(score: stream.Score):
    # Play or show the score depending on the platform.
    if platform.system() == 'Windows':
        score.show('text')
        # score.show('midi')  # Play MIDI
        show(score)  # Show musical notation

    elif platform.system() == 'IOS':
        # Pythonista may not support direct MIDI playback; try to import sound module if available
        import importlib
        try:
            sound = importlib.import_module('sound')
        except ImportError:
            sound = None
        # Play the result (IOS) when sound module is available
        score.show('text')
        player = sound.MIDIPlayer('target.mid')
        player.play()
        player.stop()


def show_plot(y_values: list):
    # Plot
    # Note that even in the OO-style, we use `.pyplot.figure` to create the Figure.
    fig, ax = plt.subplots(figsize=(5, 2.7), layout='constrained')
    ax.plot(y_values, label='pitch frequency') # Plot some data on the Axes.
    ax.set_xlabel('Pitch number')  # Add an x-label to the Axes.
    ax.set_ylabel('Frequency')  # Add a y-label to the Axes.
    ax.set_title("Pitches")  # Add a title to the Axes.
    ax.legend()  # Add a legend.
    plt.show()
