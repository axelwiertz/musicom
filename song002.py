'''
Music - Template
'''

import musicpy as mp
from musicpy import *

import harmony
from harmony import *
import rhythm
from rhythm import *


strSongName = 'Big Yellow Taxi'
chd01 = chord('B3, C#4, E4, E4, F#4, C#4, E4, E4, F#4, E4, G#3, B3, B3, C#4, E4, F#4, B3, B3, F#4, F#4, F#4, G#4, F#4, E4, E4', 1/8, 1/8)
chdRhythm = chord ('C3, C2, C2, C2, C2, C2, C2, C2, C2, C2, C2')
rtmSong = rtmSimple
lstScales = [S('Bb major')]
lstChdTrack = []
lstIntChannel = []
lstChdTrack.append (chd01.apply_rhythm (rtmSong))
lstIntChannel.append (1)
lstChdTrack.append (chdRhythm.apply_rhythm (rtmSong))
lstIntChannel.append (9)
