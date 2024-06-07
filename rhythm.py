'''
Music - Rhythm
'''
# modules
import musicpy as mp
from musicpy import *
from musicpy.daw import *


# rhythm b = beat 0 = rest - = continue . = dotted
rtm1 = rhythm('b - b. b. b b -', 1)
# Simple
rtmSimple = rhythm('b b b b', 1)

# Tresillo
rtmTresillo = rhythm('b 0 0 b - 0 b 0', 1, beats=8)
# 12/8 Bell
rtmBell = rhythm('b 0 b 0 b b 0 b 0 b 0 b', 1, beats=12, time_signature=[12, 8] )
# Son Clave
rtmSonClave = rhythm('b 0 0 b 0 0 b 0 0 0 b 0 b 0 0 0', 1, beats=16)

# 3/4
rtmWaltz = rhythm('b b b', 1, beats=3, time_signature=[3, 4] )







