'''
Part template
'''
import os
# Initialize
import time
import musicpy as mp
from musicpy import *
from musicpy.daw import *



# Chords
c1 = C('CM7', 3, 1/4, 1/8)^2
c2 = C('G7sus', 2, 1/4, 1/8)^2

# Melody
m1 = chord('B3, C#4, E4, E4, F#4, C#4, E4, E4, F#4, E4, G#3, B3, B3, C#4, E4, F#4, B3, B3, F#4, F#4, F#4, G#4, F#4, E4, E4', 1/8, 1/8)
play (m1, wait=True)


print (m1.notes)
print (m1.interval)

# Compose
# editor
S('C4 major')%(15654321, 0.4)
S('C major').get('1,1,5,5,6,6,5,-,4,4,3,3,2,2,1,-')
/S('C major').chord_progression(['IM7', 'Vsus', 'vi7', 'IVM7'])


guitar = (C('CM7', 3, 1 / 4, 1 / 8) ^ 2 |
          C('G7sus', 2, 1 / 4, 1 / 8) ^ 2 |
          C('A7sus', 2, 1 / 4, 1 / 8) ^ 2 |
          C('Em7', 2, 1 / 4, 1 / 8) ^ 2 |
          C('FM7', 2, 1 / 4, 1 / 8) ^ 2 |
          C('CM7', 3, 1 / 4, 1 / 8) @ 1 |
          C('AbM7', 2, 1 / 4, 1 / 8) ^ 2 |
          C('G7sus', 2, 1 / 4, 1 / 8) ^ 2) * 2

play(guitar, bpm=100, instrument=25)
play(guitar, bpm=100)
play(guitar, bpm=100, instrument=24)
play(guitar, bpm=100, instrument=25)
c1 = C('CM7', 3, 1 / 4, 1 / 8) ^ 2
c2 = C('CM7')
c2 = C('CM7', 3)
c3 = C('CM7', 5)
c5 = C('CM7', 3, 1 / 4, 1 / 8)
c5 = C('CM7', 3, 1 / 4)
c6 = C('CM7', 3, 1 / 4) ^ 2

# Bossa Nova
S('C major').chord_progression(['ii', 'V', 'I'])
S('C major') % 251
/ S('C major').chord_progression(['Imaj7', 'II7', 'iim7'])

# Lounge / Jazz
s1 = S('C major')
s1 % 4251
s1 % 736251

# drum
drum1 = drum('S[l:.8; i:.; r:4], S[l:.16; i:.], S[l:.8; i:.], S[l:.16; i:.], S[l:.8; i:.], S[l:.8; i:.]')
drum('S[l:.8; i:.; r:4], S[l:.16; i:.], S[l:.8; i:.], S[l:.16; i:.], S[l:.8; i:.], S[l:.8; i:.]')

drum('K, K;H, S, H, K, K;H;PH, H;S, H')

# Instruments
# Play all MIDI instruments
''' 
for i in range(1, 127):
    play(c1, bpm=100, instrument=i)
    print i
    time.sleep(3)
'''



# Create piece
# p1 = P(tracks=[c1, c1],channels=[0, 1], instruments=[1,10])

# DAW
curpath = os.getcwd() + '\\Soundfont\\'
daw1 = daw(3, name='Song 1')
daw1.load(0, curpath + 'Emu 9ftgrand.sf2')
#daw1.load(1, curpath + 'R-piano.sf2')
p1 = P(tracks=[m1],channels=[0])
print (p1)
daw1.play(p1, wait=True)
