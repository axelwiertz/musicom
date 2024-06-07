'''
Music - Berendans
'''

import musicpy as mp
from musicpy import *

import harmony
from harmony import *
import rhythm
from rhythm import *


chdRhythm = chord ('C3, C2, C2, C2, C2, C2, C2, C2, C2, C2, C2')
rtmSong = rtmSimple

strSongName = 'Berendans'
chdRhythm = chord ('C3, C2, C2, C2, C2, C2, C2, C2, C2, C2, C2')
rtmSong = rtmSimple
lstScales = [S('Bb major')]
lstChdTrack = []
lstIntChannel = []
chd01 = lstScales[0].chord_progression(['I', 'V', 'I'])
lstChdTrack.append (chd01.apply_rhythm (rtmSong))
lstIntChannel.append (1)
lstChdTrack.append (chdRhythm.apply_rhythm (rtmSong))
lstIntChannel.append (9)
