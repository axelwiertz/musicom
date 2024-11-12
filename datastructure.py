'''
Music - Datastructure
'''
import itertools
import random

# Import
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from harmony import *

#from musicpy.database import *
#print (standard)

def IntervalToBinary (lstInterval):
    lstBinary = []
    intDegree = 1
    for x in lstInterval:
        lstBinary.append(intDegree)
        intDegree += 1
        for y in range(1,x):
            lstBinary.append(0)
    return lstBinary


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
srsPitchNote = pd.Series (degree_to_note(x) for x in range (intTotalNrPitch) ) # Pitch Note instances


# Pentatonic (5 pitch class) scale
intNrDegreePentaScale = 5 # Number of pitch classes in a pentatonic scale
lstIntPentaDegree = tuple(range(1,intNrDegreePentaScale+1)) # Pentatonic scale degree number
lstPentaScaleIntervalPattern = (2,2,3,2,3) # Pentatonic major scale interval pattern
lstPentaScaleInterval = tuple(lstPentaScaleIntervalPattern[x:]+lstPentaScaleIntervalPattern[:x] for x in range(intNrDegreePentaScale) )
lstPentaScaleBinary = [IntervalToBinary(lstPentaScaleInterval[x]) for x in range(len(lstPentaScaleInterval))] # Heptatonic major scale binary patterns
# Heptatonic (7 pitch class) scale
intNrDegreeHeptaScale = 7 # Number of pitch classes in a heptatonic scale
lstIntHeptaDegree = tuple(range(1,intNrDegreeHeptaScale+1)) # Heptatonic scale degree number
lstHeptaScaleIntervalPattern = (2,2,1,2,2,2,1) # Heptatonic major scale interval pattern
# Modes
lstHeptaScaleInterval = tuple(lstHeptaScaleIntervalPattern[x:]+lstHeptaScaleIntervalPattern[:x] for x in range(intNrDegreeHeptaScale) )
lstHeptaScaleBinary = [IntervalToBinary(lstHeptaScaleInterval[x]) for x in range(len(lstHeptaScaleInterval))] # Heptatonic major scale binary patterns

# Scale pitch mask
# To do minor scale
lstScale = intNrOctave * lstHeptaScaleBinary [0] # C Major scale pitch mask
lstHeptaScale = [lstScale[-x:]+lstScale[:-x] for x in range(intNrDiatonicPitchClass) ] # All major scale pitch mask
arrHeptaScale = np.array(lstHeptaScale)

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
dfPitch = pd.DataFrame ([lstPitchNr, srsPitchClassNr.values, srsPitchClassChr.values, srsPitchNote.values, srsPitchFreq.values]).transpose()
dfPitch.columns=['Nr','ClassNr','ClassChr','Note', 'Freq']


# Pitch ranges of instruments
dctRangeInstr = {
    'Piano': ['A0','C8'], # Piano keyboard
    'Guitar': ['E2','D6'], # Acoustic guitar with standard tuning
    'Ukelele': ['C4', 'C6'] # ??
}

# Plot
# Note that even in the OO-style, we use `.pyplot.figure` to create the Figure.
#fig, ax = plt.subplots(figsize=(5, 2.7), layout='constrained')
#ax.plot(srsPitchFreq.values, label='pitch frequency')  # Plot some data on the Axes.
#ax.set_xlabel('Pitch number')  # Add an x-label to the Axes.
#ax.set_ylabel('Frequency')  # Add a y-label to the Axes.
#ax.set_title("Pitches")  # Add a title to the Axes.
#ax.legend()  # Add a legend.
#plt.show()

# Select random pictch
intPitch = random.choice (lstPitchNr)
print (srsPitchNote.values[intPitch])

# Parts
dfForm = pd.DataFrame ([16, 16, 16])
dfParts = pd.DataFrame ([[1, 16],
    [2, 16],
    [3, 16]])



scl01 = S('C major')
# All chord patterns
lstChord01 = lstChordPattern
chd01 = scl01.chord_progression(lstChord01[0])
for i in range(1, len(lstChordPattern)-1):
#    print (lstChordPattern[i])
    chd02 = scl01.chord_progression(lstChord01[i], durations=1 / 2, intervals=0, volumes=None, chords_interval=None)
    chd01 = chd01 + rest(1/2) + chd02

# All chords
lstChdScale = scl01%(1234567, 0.5)
chd01 = lstChdScale[0]
for i in range(1, 7):
#    print (lstChordPattern[i])
    chd01 = chd01 + rest(1/2) + lstChdScale[i]



#print (chd01)
#play (chd01, wait=True)

# Output
lstChdTrack = [chd01] # list of tracks
lstIntChannel = [1] # list of channelnumbers
lstIntStartTimes = [0] # list of starttimes


'''
chd01 = chord('C4', 1/8, 1/8)*100
lstChdTrack = []
lstIntChannel = []
lstChdTrack.append (chd01.apply_rhythm (rtmSong))
lstIntChannel.append (1)
lstChdTrack.append (chdRhythm.apply_rhythm (rtmSong))
lstIntChannel.append (9)
'''