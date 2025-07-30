"""
Music data - Structure
"""
import itertools


# Import
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from music21 import stream, note, key, scale, chord, interval, meter, roman, converter, instrument, serial, tempo
from showscore import show

import copy


def interval_to_binary (intervals):
    # Convert a list of intervals to a binary mask with sequential degree numbers
    # Example [2, 3] -> [1, 0, 2, 0, 0, 3]
    binary_with_degrees = []
    degree = 1
    for x in intervals:
        binary_with_degrees.append(degree)
        degree += 1
        for y in range(1,x):
            binary_with_degrees.append(0)
    return binary_with_degrees


'''
Music data - Absolute data: frequency, pitch(class), octave
'''

# Diatonic pitch set, equal temperament scale
A4FREQUENCY = 440 # Frequency of A4
A4MIDIPITCHNUM = 69 # MIDI number of A4
OCTAVES = 9 # Number of octaves in the pitch set
NUMDIATONICPITCHCLASS = 12 # Number of pitch classes 0-11
# Total number of pitches diatonic pitch set
NUMPITCH = OCTAVES * NUMDIATONICPITCHCLASS
lstPitchClassNr = tuple(range (NUMDIATONICPITCHCLASS)) # Pitch class number
lstPitchClassChr = ('C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B') # Pitch class characters
lstPitchNr = tuple(range(NUMPITCH)) # Pitch number set
srsPitchNr = pd.Series (range (NUMPITCH))
# Pitch class
srsPitchClassChr = pd.Series ([x for y in range(-1, OCTAVES+1) for x in lstPitchClassChr])
srsPitchClassNr = pd.Series (OCTAVES * lstPitchClassNr)
srsPitchFreq = pd.Series (2 ** ((n - A4MIDIPITCHNUM) / NUMDIATONICPITCHCLASS) * A4FREQUENCY for n in range(NUMPITCH)) # Pitch frequencies

'''
Music data - Diatonic chord patterns: triads and sevenths
'''
chord1 = chord.Chord()

TRIAD = 3 # Number of pitch classes in a triad
interval01 = interval.Interval()
# Patterns: diminished, major, minor, augmented
dctIntervalPattern = {
    'd': (3, 3, 6),
    'M': (4, 3, 5),
    'm': (3, 4, 5),
    'A': (4, 4, 4)
}
intervalsPattern = dctIntervalPattern['M']


# inversions
lstScaleInterval = tuple(intervalsPattern[x:]+intervalsPattern[:x] for x in range(TRIAD) )
# Binary patterns
lstScaleBinary = [interval_to_binary(lstScaleInterval[x]) for x in range(len(lstScaleInterval))] 


"""
Music data - Diatonic scale patterns: pentatonic and heptatonic
"""
# Pentatonic (5 pitch class) scale
PENTA = 5 # Number of pitch classes in a pentatonic scale
lstIntPentaDegree = tuple(range(1,PENTA+1)) # Pentatonic scale degree number
lstPentaScaleIntervalPattern = (2,2,3,2,3) # Pentatonic interval pattern
lstPentaScaleInterval = tuple(lstPentaScaleIntervalPattern[x:]+lstPentaScaleIntervalPattern[:x] for x in range(PENTA) )
lstPentaScaleBinary = [interval_to_binary(lstPentaScaleInterval[x]) for x in range(len(lstPentaScaleInterval))] # Heptatonic binary patterns

# Heptatonic (7 pitch class) scale
scale01 = scale.Scale()
HEPTA = 7 # Number of pitch classes in a heptatonic scale
lstIntHeptaDegree = tuple(range(1,HEPTA+1)) # Heptatonic scale degree number
lstHeptaScaleIntervalPattern = (2,2,1,2,2,2,1) # Heptatonic interval pattern
# Modes
lstHeptaScaleInterval = tuple(lstHeptaScaleIntervalPattern[x:]+lstHeptaScaleIntervalPattern[:x] for x in range(HEPTA) )
lstHeptaScaleBinary = [interval_to_binary(lstHeptaScaleInterval[x]) for x in range(len(lstHeptaScaleInterval))] # Heptatonic binary patterns

# Scale pitch mask
# Major
lstScale = OCTAVES * lstHeptaScaleBinary [0] # C scale pitch mask
# Minor
lstScale1 = OCTAVES * lstHeptaScaleBinary [5] # a scale pitch mask

lstHeptaScale = [lstScale[-x:]+lstScale[:-x] for x in range(NUMDIATONICPITCHCLASS) ] # All major scale pitch mask
arrHeptaScale = np.array(lstHeptaScale)


"""
Music data - Chords in scales
"""
# Chord patterns in scale degrees
lstChordDegreePattern = (1,3,5,7,2,4,6) #Heptatonic

lstHeptaScaleChord = [lstChordDegreePattern[x:]+lstChordDegreePattern[:x] for x in range(HEPTA) ]
lstHeptaScaleChord.sort()
lstHeptaScaleChordDegreeIntervalPattern = [2,2,2,2,2,2,2] #Heptatonic

# Permutations: ordered set
lstPermChordDegreePattern = list(itertools.permutations (lstIntHeptaDegree))
# Combinations
lstCombChordDegreePattern = list(itertools.combinations (lstIntHeptaDegree, 3))


# Table of all diatonic data along pitch number set
dfPitch = pd.DataFrame ([lstPitchNr, srsPitchClassNr.values, srsPitchClassChr.values, srsPitchFreq.values]).transpose()
dfPitch.columns=['Nr','ClassNr','ClassChr', 'Freq']



def create_stream_chords_in_key (chord_progressions: list, key_in: key.Key = key.Key ('C'),  quarterlength_in: int = 1 ) -> stream.Stream:
    # Stream of chord progression patterns in a key
    stream_out = stream.Stream()
    for i in range(1, len(chord_progressions)-1):
        stream_out.append(note.Rest(quarterLength= quarterlength_in))
        for j in range (0, len(chord_progressions[i])):
            chord01 = roman.RomanNumeral (chord_progressions[i][j], key_in)
            chord01.duration.quarterLength = quarterlength_in
            stream_out.append(chord1)

    return stream_out



def create_stream_triads_in_key (key_in: key.Key = key.Key ('C'),  quarterlength_in: int = 1 ) -> stream.Stream:
    # Stream of all triads in a key
    stream_out = stream.Stream()
    for i in range(HEPTA):
        chord1 = roman.RomanNumeral(i+1, key_in)
        chord1.duration.quarterLength = quarterlength_in
        stream_out.append(chord1)
        stream_out.append(note.Rest(quarterLength=quarterlength_in))

    return stream_out





# Plot
# Note that even in the OO-style, we use `.pyplot.figure` to create the Figure.
#fig, ax = plt.subplots(figsize=(5, 2.7), layout='constrained')
#ax.plot(srsPitchFreq.values, label='pitch frequency') # Plot some data on the Axes.
#ax.set_xlabel('Pitch number')  # Add an x-label to the Axes.
#ax.set_ylabel('Frequency')  # Add a y-label to the Axes.
#ax.set_title("Pitches")  # Add a title to the Axes.
#ax.legend()  # Add a legend.
#plt.show()

def pitch_class_circle():


    # Convert pitch class numbers to angles
    angles = np.linspace(0, 2 * np.pi, NUMDIATONICPITCHCLASS, endpoint=False)

    # Create a figure and axis
    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})

    # Plot the pitch class numbers
    for angle, pitch in zip(angles, lstPitchClassNr):
        ax.plot(angle, 1, 'o', markersize=10)
        ax.text(angle, 1.1, str(pitch), ha='center', va='center')

    # Set the title
    ax.set_title('Circle of Pitch Class Numbers')

    # Show the plot
    plt.show()


