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
lstParts = []
lstParts.append([1, 16])
lstParts.append([2, 16])
lstParts.append([3, 16])

scl01 = S(str(dctScaleStyle['Standard'][0]))
chd01 = scl01.chord_progression(lstChordPattern[0])
for i in range(1, len(lstChordPattern)-1):
#    print (lstChordPattern[i])
    chd02 = scl01.chord_progression(lstChordPattern[i])
    chd01 = chd01 + rest(1/2) + chd02

#print (chd01)
#play (chd01, wait=True)

# Output
lstChdTrack = [chd01] # list of tracks
lstIntChannel = [0] # list of channelnumbers
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






