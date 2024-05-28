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
drm1 = drum('S[l:.8; i:.; r:4], S[l:.16; i:.], S[l:.8; i:.], S[l:.16; i:.], S[l:.8; i:.], S[l:.8; i:.]')
drm2 = drum('S[l:.8; i:.; r:4], S[l:.16; i:.], S[l:.8; i:.], S[l:.16; i:.], S[l:.8; i:.], S[l:.8; i:.]')

drm3 =  drum ('K, K;H, S, H, K, K;H;PH, H;S, H')

print (drm3)

# rhythm b = beat 0 = rest - = continue . = dotted
rtm1 = rhythm('b - b. b. b b -', 1)
# Simple
rtm1 = rhythm('b b b b', 1)

# Tresillo
rtm1 = rhythm('b 0 0 b - 0 b 0', 1, beats=8)
# 12/8 Bell
rtm1 = rhythm('b 0 b 0 b b 0 b 0 b 0 b', 1, beats=12, time_signature=[12, 8] )
# Son Clave
rtm1 = rhythm('b 0 0 b 0 0 b 0 0 0 b 0 b 0 0 0', 1, beats=16)

# 3/4
rtm1 = rhythm('b b b', 1, beats=3, time_signature=[3, 4] )


chdC5 = chord ('C3, C2, C2, C2, C2, C2, C2, C2, C2, C2, C2')
chdRhythm = chdC5.apply_rhythm (rtm1)


intDAWChannel = 9
intPiano = 1

pceRhythm = piece ([chdRhythm], [intPiano], channels=[intDAWChannel])

intNumChannels = 10
strSongName = 'Percussion 001'
daw1 = daw(intNumChannels, name=strSongName)



# Play rhythm
print ('Play : ')
print (rtm1)
print (chdRhythm)
# play (chdRhythm, wait=True)
play (pceRhythm, wait=True)




print (daw1)
daw1.play(pceRhythm, wait=True)



