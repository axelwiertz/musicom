'''
Music - Rhythm
'''
# modules
import musicpy as mp
from musicpy import *
from musicpy.daw import *

'''
:[] settings blok
r:n repeat the beat n times with the equally divided unit duration
R:n repeat the beat n times with the unit duration
b:n change the duration of the beat to the unit duration * n
'''

# drum
drum1 = drum('S[l:.8; i:.; r:4], S[l:.16; i:.], S[l:.8; i:.], S[l:.16; i:.], S[l:.8; i:.], S[l:.8; i:.]')
drum('S[l:.8; i:.; r:4], S[l:.16; i:.], S[l:.8; i:.], S[l:.16; i:.], S[l:.8; i:.], S[l:.8; i:.]')

drum ('K, K;H, S, H, K, K;H;PH, H;S, H')

# rhythm b = beat 0 = rest - = continue . = dotted
rtm1 = rhythm('b - b. b. b b -', 1)
# Simple
rtm = rhythm('b b b b', 1)
# Tresillo
rtm1 = rhythm('b 0 0 b - 0 b 0', 1, beats=8)
# Son Clave
rtm1 = rhythm('b 0 0 b 0 0 b 0 0 0 b 0 b 0 0 0', 1, beats=16)
# 12/8 Bell
rtm1 = rhythm('b 0 b 0 b b 0 b 0 b 0 b', 1, beats=12, time_signature=[12, 8] )



print ('Play : ')
print (rtm1)
chdC5 = chord ('C4, C4, C4, C4, C4, C4, C4, C4, C4, C4, C4, C4, C4, C4, C4, C4, C4, C4, C4, C4, C4, C4, C4, C4')
chd1 = chdC5.apply_rhythm (rtm1) * 3
print (chd1)
play (chd1, wait=True)
