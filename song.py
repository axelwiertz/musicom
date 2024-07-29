'''
Music - Template
'''

import musicpy as mp
from musicpy import *

import harmony
from harmony import *
import rhythm
from rhythm import *


strSongName = 'Patterns'

# Parts
lstForm = [16, 16, 16]
lstParts = [
    [1, 16],
    [2, 16],
    [3, 16]
]
# Scale
#scl01 = S(str(dctStyleScale['Standard'][0]))
scl01 = S('A major')
# All chord patterns
chd01 = scl01.chord_progression(lstChordPattern[0])
for i in range(1, len(lstChordPattern)-1):
#    print (lstChordPattern[i])
    chd02 = scl01.chord_progression(lstChordPattern[i], durations=1 / 2, intervals=0, volumes=None, chords_interval=None)
    chd01 = chd01 + rest(1/2) + chd02

# All chords
lstChdScale = scl01%(1234567, 0.5)
chd01 = lstChdScale[0]
for i in range(1, 6):
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






