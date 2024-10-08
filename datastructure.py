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

n = N ('A4')
print(n.degree)

strSongName = 'Data structure'

# Parts
dfForm = pd.DataFrame ([16, 16, 16])
dfParts = pd.DataFrame ([[1, 16],
    [2, 16],
    [3, 16]])


intA4Freq = 440
intA4PitchNr = 69
intNrOctave = 9
intNrDiatonicPitchClass = 12
intNrPitch = intNrOctave * intNrDiatonicPitchClass

lstPitchClassNr = [x for x in range(intNrDiatonicPitchClass)]
srsPitchNr = pd.Series (range (intNrPitch))
lstPitchClassChr = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
srsPitchChr = pd.Series ([x + str(y) for y in range(-1, intNrOctave+1) for x in lstPitchClassChr])
srsPitchClassNr = pd.Series (intNrOctave * lstPitchClassNr)
srsPitchFreq = pd.Series (2 ** ((n - intA4PitchNr) / intNrDiatonicPitchClass) * intA4Freq for n in range(intNrPitch))
srsPitchNote = pd.Series (degree_to_note(x) for x in range (intNrPitch) )

dfPitch = pd.DataFrame ([srsPitchNr.values, srsPitchClassNr.values, srsPitchChr.values, srsPitchNote.values, srsPitchFreq.values]).transpose()
dfPitch.columns=['Nr','ClassNr','ClassChr','Note', 'Freq']

arrPitch = np.arange(intNrOctave * intNrDiatonicPitchClass).reshape(intNrOctave, intNrDiatonicPitchClass) + intNrDiatonicPitchClass
dfPitch = pd.DataFrame (arrPitch)

octave = ['C', 'c', 'D', 'd', 'E', 'F', 'f', 'G', 'g', 'A', 'a', 'B']
arrKeys = np.array([x, y] for y in range(0, 9) for x in octave)
keys = np.array([x + str(y) for y in range(0, 9) for x in octave])
# Trim to standard 88 keys
start = np.where(keys == 'A0')[0][0]
end = np.where(keys == 'C8')[0][0]
keys = keys[start:end + 1]

base_freq = 440  # Frequency of Note A4
note_freqs = dict(zip(keys, [2 ** ((n + 1 - 49) / 12) * base_freq for n in range(len(keys))]))
note_freqs[''] = 0.0  # stop

x = np.linspace(0, 2, 100)  # Sample data.

# Note that even in the OO-style, we use `.pyplot.figure` to create the Figure.
fig, ax = plt.subplots(figsize=(5, 2.7), layout='constrained')
ax.plot(dfPitch, label='linear')  # Plot some data on the Axes.
ax.set_xlabel('x label')  # Add an x-label to the Axes.
ax.set_ylabel('y label')  # Add a y-label to the Axes.
ax.set_title("Simple Plot")  # Add a title to the Axes.
ax.legend()  # Add a legend.
plt.show()

print (random.choice (dfPitch))


#for intOctave in range (intNrOctaves) :
#    for intDiatonicNr in range (intNrDiatonic) :
#        lstPitch.append note01.degree = (intOctave+1)*12 + intDiatonicNr



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






