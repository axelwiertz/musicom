'''
Music - Rhythm
'''
# modules
import musicpy as mp
from musicpy import *
from musicpy.daw import *

'''
r:n repeat the beat n times with the equally divided unit duration
R:n repeat the beat n times with the unit duration
b:n change the duration of the beat to the unit duration * n
'''

# drum
drum1 = drum('S[l:.8; i:.; r:4], S[l:.16; i:.], S[l:.8; i:.], S[l:.16; i:.], S[l:.8; i:.], S[l:.8; i:.]')
drum('S[l:.8; i:.; r:4], S[l:.16; i:.], S[l:.8; i:.], S[l:.16; i:.], S[l:.8; i:.], S[l:.8; i:.]')

drum ('K, K;H, S, H, K, K;H;PH, H;S, H')

# rhythm
rhythm('b - b. b. b b -', 1)

