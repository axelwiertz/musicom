'''
Music - Datastructure
'''

# Import
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import random

from harmony import *

#from musicpy.database import *
#print (standard)

strSongName = 'Diatonic pitch set'

# Diatonic pitch set, equal temperament scale
intA4Freq = 440 # Frequency of A4
intA4PitchNr = 69 # MIDI number of A4
intNrOctave = 9 # Number of octaves in the pitch set
intNrDiatonicPitchClass = 12 # Number of pitch classes 0-11
# Total number of pitches diatonic pitch set
intTotalNrPitch = intNrOctave * intNrDiatonicPitchClass
lstPitchClassNr = list(range (intNrDiatonicPitchClass)) # Pitch class number
lstPitchClassChr = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'] # Pitch class characters
lstPitchNr = list(range(intTotalNrPitch)) # Pitch number set
srsPitchNr = pd.Series (range (intTotalNrPitch))
# Pitch class
srsPitchClassChr = pd.Series ([x + str(y) for y in range(-1, intNrOctave+1) for x in lstPitchClassChr])
srsPitchClassNr = pd.Series (intNrOctave * lstPitchClassNr)
srsPitchFreq = pd.Series (2 ** ((n - intA4PitchNr) / intNrDiatonicPitchClass) * intA4Freq for n in range(intTotalNrPitch)) # Pitch frequencies
srsPitchNote = pd.Series (degree_to_note(x) for x in range (intTotalNrPitch) ) # Pitch Note instances


# Heptatonic scale
intNrDegreeHeptaScale = 7 # Number of pitch classes in a heptatonic scale
lstDegree = list(range(1,intNrDegreeHeptaScale+1)) # Heptatonic scale degree number
lstHeptaScaleIntervalPattern = [2,2,1,2,2,2,1] # Heptatonic major scale interval pattern
lstHeptaScaleInterval = [lstHeptaScaleIntervalPattern[x:]+lstHeptaScaleIntervalPattern[:x] for x in range(intNrDegreeHeptaScale) ]

def IntervalToBinary (lstInterval):
    lstBinary = []
    for x in lstInterval:
        lstBinary.append(1)
        for y in range(1,x):
            lstBinary.append(0)
    return lstBinary

lstHeptaScaleBinary = [IntervalToBinary(lstHeptaScaleInterval[x]) for x in range(len(lstHeptaScaleInterval))] # Heptatonic major scale binary patterns


lstScale = intNrOctave * lstHeptaScaleBinary [0]

lstHeptaScaleChordDegreePattern = [1,3,5,7,2,4,6] #Heptatonic
# Pentatonic scale
intNrDegreePentaScale = 5 # Number of pitch classes in a pentatonic scale


# Table of all diatonic data along pitch number set
dfPitch = pd.DataFrame ([lstPitchNr, srsPitchClassNr.values, srsPitchClassChr.values, srsPitchNote.values, srsPitchFreq.values, lstScale]).transpose()
dfPitch.columns=['Nr','ClassNr','ClassChr','Note', 'Freq', "Scale"]

lstRangeInstr = [note('A', 0).degree ,note('C', 8).degree]



# Note that even in the OO-style, we use `.pyplot.figure` to create the Figure.
fig, ax = plt.subplots(figsize=(5, 2.7), layout='constrained')
ax.plot(srsPitchFreq.values, label='pitch frequency')  # Plot some data on the Axes.
ax.set_xlabel('Pitch number')  # Add an x-label to the Axes.
ax.set_ylabel('Frequency')  # Add a y-label to the Axes.
ax.set_title("Pitches")  # Add a title to the Axes.
ax.legend()  # Add a legend.
plt.show()

print (random.choice (lstPitchNr))

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






