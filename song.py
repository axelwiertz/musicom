'''
Music - Template
'''

import musicpy as mp
from musicpy import *

import harmony
from harmony import *
import rhythm
from rhythm import *


strSongName = 'Song name'

# Parts
lstForm = [16, 16, 16]
lstParts = []
lstParts.append([1, 16])
lstParts.append([2, 16])
lstParts.append([3, 16])

chd01 = chord('C4', 1/8, 1/8)
lstScales = [S('Bb major')]
lstChdTrack = []
lstIntChannel = []
lstChdTrack.append (chd01.apply_rhythm (rtmSong))
lstIntChannel.append (1)
lstChdTrack.append (chdRhythm.apply_rhythm (rtmSong))
lstIntChannel.append (9)






