'''
Music - Datastructure
'''
# Import
import matplotlib
import numpy as np

import musicpy as mp
from musicpy import *

import harmony
from harmony import *
import rhythm
from rhythm import *


strSongName = 'Data structure'

# Parts
lstForm = [16, 16, 16]
lstParts = [
    [1, 16],
    [2, 16],
    [3, 16]
]

intNrOctaves = 10
intNrDiatonic = 12

note01 = N ('C9')
print (note01.degree)

arrPitch = np.arange(intNrOctaves * intNrDiatonic).reshape(intNrOctaves, intNrDiatonic) + intNrDiatonic


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






