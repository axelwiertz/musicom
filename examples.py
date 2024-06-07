'''
Music Samples
'''

# modules
from musicpy import *

# Melody creation syntax
c1 = C('CM7', 3, 1 / 4, 1 / 8) ^ 2
c2 = C('CM7')
c2 = C('CM7', 3)
c3 = C('CM7', 5)
c5 = C('CM7', 3, 1 / 4, 1 / 8)
c5 = C('CM7', 3, 1 / 4)
c6 = C('CM7', 3, 1 / 4) ^ 2

melody = (c1 | c2 | c3 * 2 )

chd4 = S('C4 major')%(15654321, 0.4)
chd01 = S('C major').get('1,2,3,4,5,6,7,1.1')

chd5 = S('C major').get('1,1,5,5,6,6,5,-,4,4,3,3,2,2,1,-')
chd6 = S('C major').chord_progression(['IM7', 'Vsus', 'vi7', 'IVM7'])


# Chords
c1 = C('CM7', 3, 1/4, 1/8)^2
c2 = C('G7sus', 2, 1/4, 1/8)^2
chd01 = S('C4 major')%(15654321, 0.4)
print (chd01)
chd03 = S('C major').chord_progression(['IM7', 'Vsus', 'vi7', 'IVM7'])

# Notes
chd02 = S('C major').get('1,1,5,5,6,6,5,-,4,4,3,3,2,2,1,-')


# Scales
s1 = S('C Major')
t1 = s1.get('-,1,-,2') % (1 / 2,)
t1 = s1.get('r,1,r,2')

#1
chd01 = chord ('F2, A2, F3')
chd02 = S('F major').get('1.-2;3.-2;1.-1')
#2
chd03 = chord('C2, C3, E3, G3')


# Melody

# Musical composition examples page 13

s1 = S('F major')

b1 = s1.get('-') + s1.get('1.-1; 3.-1; 1') + s1.get('5.-1; 5   ; 7.-1;2') + s1.get('1.-1; 5.-1; 1   ;3')
b2 = s1.get('6.-1; 4.-1; 1   ;4') + s1.get('1.-1; 3.-1; 1   ;5') + s1.get('6.-1; 3.-1; 1   ;6') + s1.get('5.-1; 5.-1; 2   ;7')
b3 = s1.get('1.-1; 5.-1; 3   ;1.+1')%(1,)


b21 = s1.get('-') + s1.get('1') + s1.get('7.-1; 2') + s1.get('5.-1; 3')
b22 = s1.get('6.-1; 4') + s1.get('3.-1; 5') + s1.get('4.-1; 6') + s1.get('2.-1; 7')
b23 = s1.get('1.-1; 1.+1')%(1,)

play (b1 + b2 + b3, wait=True)
play (b21 + b22 + b23, wait=True)


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



# Play DAW

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


