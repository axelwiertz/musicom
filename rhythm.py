'''
Music - Rhythm
'''
# modules
import musicpy as mp
from musicpy import *
from musicpy.daw import *


# rhythm b = beat 0 = rest - = continue . = dotted
rtm1 = rhythm('b - b. b. b b -', 1)


# Rhythm library
# Simple
rtmSimple = rhythm('b b b b', 1, time_signature=[4, 4])
# Tresillo
rtmTresillo = rhythm('b 0 0 b - 0 b 0', 1, beats=8, time_signature=[4, 4])
# 12/8 Bell
rtmBell = rhythm('b 0 b 0 b b 0 b 0 b 0 b', 1, beats=12, time_signature=[12, 8] )
# Son Clave
rtmSonClave = rhythm('b 0 0 b 0 0 b 0 0 0 b 0 b 0 0 0', 1, beats=16)

# 3/4
rtmWaltz = rhythm('b b b', 1, beats=3, time_signature=[3, 4] )

print (rtmTresillo)

rtmSong = rtmBell
chd01 = chord('C4', 1/8, 1/8)*7
chd02 = chd01.apply_rhythm (rtmSong)
play(chd02, wait=True)

'''
lstChdTrack = []
lstIntChannel = []
lstChdTrack.append (chd01.apply_rhythm (rtmSong))
lstIntChannel.append (1)
lstChdTrack.append (chdRhythm.apply_rhythm (rtmSong))
lstIntChannel.append (9)
'''


