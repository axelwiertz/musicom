'''
Music data - Structure
'''
import itertools
import random
import os
import time


# Import
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Harmony data
from harmony import *
from music21 import stream, note, key, scale, chord, interval, meter, roman, converter, instrument
from showscore import show

import musicpy as mp



# modules

#from musicpy.daw import *
#from musicpy.database import *
#print (standard)

# Convert a list of intervals to a binary mask
def IntervalToBinary (lstInterval):
    lstBinary = []
    intDegree = 1
    for x in lstInterval:
        lstBinary.append(intDegree)
        intDegree += 1
        for y in range(1,x):
            lstBinary.append(0)
    return lstBinary


'''
Music data - Absolute data: frequency, pitch(class), octave
'''

strSongName = 'Diatonic pitch set'

# Diatonic pitch set, equal temperament scale
intA4Freq = 440 # Frequency of A4
intA4PitchNr = 69 # MIDI number of A4
intNrOctave = 9 # Number of octaves in the pitch set
intNrDiatonicPitchClass = 12 # Number of pitch classes 0-11
# Total number of pitches diatonic pitch set
intTotalNrPitch = intNrOctave * intNrDiatonicPitchClass
lstPitchClassNr = tuple(range (intNrDiatonicPitchClass)) # Pitch class number
lstPitchClassChr = ('C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B') # Pitch class characters
lstPitchNr = tuple(range(intTotalNrPitch)) # Pitch number set
srsPitchNr = pd.Series (range (intTotalNrPitch))
# Pitch class
srsPitchClassChr = pd.Series ([x for y in range(-1, intNrOctave+1) for x in lstPitchClassChr])
srsPitchClassNr = pd.Series (intNrOctave * lstPitchClassNr)
srsPitchFreq = pd.Series (2 ** ((n - intA4PitchNr) / intNrDiatonicPitchClass) * intA4Freq for n in range(intTotalNrPitch)) # Pitch frequencies

'''
Music data - Diatonic patterns: triads
'''
intNrDegreeScale = 3 # Number of pitch classes in a triad
lstIntDegree = tuple(range(1,intNrDegreeScale+1)) # Scale degree numbers
# Patterns: diminished, major, minor, augmented
dctIntervalPattern = {
    'd': (3, 3, 6),
    'M': (4, 3, 5),
    'm': (3, 4, 5),
    'A': (4, 4, 4)
}
lstIntervalPattern = dctIntervalPattern['M']

# inversions
lstScaleInterval = tuple(lstIntervalPattern[x:]+lstIntervalPattern[:x] for x in range(intNrDegreeScale) )
lstScaleBinary = [IntervalToBinary(lstScaleInterval[x]) for x in range(len(lstScaleInterval))] # Binary patterns


'''
Music data - Diatonic patterns: pentatonic and heptatonic scales
'''
# Pentatonic (5 pitch class) scale
intNrDegreePentaScale = 5 # Number of pitch classes in a pentatonic scale
lstIntPentaDegree = tuple(range(1,intNrDegreePentaScale+1)) # Pentatonic scale degree number
lstPentaScaleIntervalPattern = (2,2,3,2,3) # Pentatonic interval pattern
lstPentaScaleInterval = tuple(lstPentaScaleIntervalPattern[x:]+lstPentaScaleIntervalPattern[:x] for x in range(intNrDegreePentaScale) )
lstPentaScaleBinary = [IntervalToBinary(lstPentaScaleInterval[x]) for x in range(len(lstPentaScaleInterval))] # Heptatonic binary patterns

# Heptatonic (7 pitch class) scale
intNrDegreeHeptaScale = 7 # Number of pitch classes in a heptatonic scale
lstIntHeptaDegree = tuple(range(1,intNrDegreeHeptaScale+1)) # Heptatonic scale degree number
lstHeptaScaleIntervalPattern = (2,2,1,2,2,2,1) # Heptatonic interval pattern
# Modes
lstHeptaScaleInterval = tuple(lstHeptaScaleIntervalPattern[x:]+lstHeptaScaleIntervalPattern[:x] for x in range(intNrDegreeHeptaScale) )
lstHeptaScaleBinary = [IntervalToBinary(lstHeptaScaleInterval[x]) for x in range(len(lstHeptaScaleInterval))] # Heptatonic binary patterns

# Scale pitch mask
# Major
lstScale = intNrOctave * lstHeptaScaleBinary [0] # C scale pitch mask
# Minor
lstScale1 = intNrOctave * lstHeptaScaleBinary [5] # a scale pitch mask

lstHeptaScale = [lstScale[-x:]+lstScale[:-x] for x in range(intNrDiatonicPitchClass) ] # All major scale pitch mask
arrHeptaScale = np.array(lstHeptaScale)


'''
Music data - Chords in scales

'''
# Chord patterns in list of scale degrees
lstChordDegreePattern = [1,3,5,7,2,4,6] #Heptatonic

lstHeptaScaleChord = [lstChordDegreePattern[x:]+lstChordDegreePattern[:x] for x in range(intNrDegreeHeptaScale) ]
lstHeptaScaleChord.sort()
lstHeptaScaleChordDegreeIntervalPattern = [2,2,2,2,2,2,2] #Heptatonic

# Permutations: ordered set
lstPermChordDegreePattern = list(itertools.permutations (lstIntHeptaDegree))
# Combinations
lstCombChordDegreePattern = list(itertools.combinations (lstIntHeptaDegree, 3))


# Table of all diatonic data along pitch number set
dfPitch = pd.DataFrame ([lstPitchNr, srsPitchClassNr.values, srsPitchClassChr.values, srsPitchFreq.values]).transpose()
dfPitch.columns=['Nr','ClassNr','ClassChr', 'Freq']


# Plot
# Note that even in the OO-style, we use `.pyplot.figure` to create the Figure.
#fig, ax = plt.subplots(figsize=(5, 2.7), layout='constrained')
#ax.plot(srsPitchFreq.values, label='pitch frequency')  # Plot some data on the Axes.
#ax.set_xlabel('Pitch number')  # Add an x-label to the Axes.
#ax.set_ylabel('Frequency')  # Add a y-label to the Axes.
#ax.set_title("Pitches")  # Add a title to the Axes.
#ax.legend()  # Add a legend.
#plt.show()


# Pitch class numbers
pitch_classes = list(range(12))

# Convert pitch class numbers to angles
angles = np.linspace(0, 2 * np.pi, 12, endpoint=False)

# Create a figure and axis
fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})

# Plot the pitch class numbers
for angle, pitch in zip(angles, pitch_classes):
    ax.plot(angle, 1, 'o', markersize=10)
    ax.text(angle, 1.1, str(pitch), ha='center', va='center')

# Set the title
ax.set_title('Circle of Pitch Class Numbers')

# Show the plot
#plt.show()


