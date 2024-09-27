'''
Music - Datastructure
'''
import random

# Import
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from harmony import *

strSongName = 'Data structure'

# Parts
dfForm = pd.DataFrame ([16, 16, 16])
dfParts = pd.DataFrame ([[1, 16],
    [2, 16],
    [3, 16]])

intNrOctaves = 10
intNrDiatonic = 12

note01 = N ('C9')
print (note01.degree)

arrPitch = np.arange(intNrOctaves * intNrDiatonic).reshape(intNrOctaves, intNrDiatonic) + intNrDiatonic
dfPitch = pd.DataFrame (arrPitch)
print (random.choice (arrPitch))

x = np.linspace(0, 2, 100)  # Sample data.

# Note that even in the OO-style, we use `.pyplot.figure` to create the Figure.
fig, ax = plt.subplots(figsize=(5, 2.7), layout='constrained')
ax.plot(x, x, label='linear')  # Plot some data on the Axes.
ax.set_xlabel('x label')  # Add an x-label to the Axes.
ax.set_ylabel('y label')  # Add a y-label to the Axes.
ax.set_title("Simple Plot")  # Add a title to the Axes.
ax.legend()  # Add a legend.
plt.show()



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






