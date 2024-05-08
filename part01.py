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
# Big Yellow Taxi
chdMelody01 = chord('B3, C#4, E4, E4, F#4, C#4, E4, E4, F#4, E4, G#3, B3, B3, C#4, E4, F#4, B3, B3, F#4, F#4, F#4, G#4, F#4, E4, E4', 1/8, 1/8)


print (chdMelody01.notes)
print (chdMelody01.interval)

# Compose
# editor
chd01 = S('C4 major')%(15654321, 0.4)
chd02 = S('C major').get('1,1,5,5,6,6,5,-,4,4,3,3,2,2,1,-')
chd03 = S('C major').chord_progression(['IM7', 'Vsus', 'vi7', 'IVM7'])


guitar = (C('CM7', 3, 1 / 4, 1 / 8) ^ 2 |
          C('G7sus', 2, 1 / 4, 1 / 8) ^ 2 |
          C('A7sus', 2, 1 / 4, 1 / 8) ^ 2 |
          C('Em7', 2, 1 / 4, 1 / 8) ^ 2 |
          C('FM7', 2, 1 / 4, 1 / 8) ^ 2 |
          C('CM7', 3, 1 / 4, 1 / 8) @ 1 |
          C('AbM7', 2, 1 / 4, 1 / 8) ^ 2 |
          C('G7sus', 2, 1 / 4, 1 / 8) ^ 2) * 2

# play (guitar, bpm=100, instrument=25, wait=True)

c1 = C('CM7', 3, 1 / 4, 1 / 8) ^ 2
c2 = C('CM7')
c2 = C('CM7', 3)
c3 = C('CM7', 5)
c5 = C('CM7', 3, 1 / 4, 1 / 8)
c5 = C('CM7', 3, 1 / 4)
c6 = C('CM7', 3, 1 / 4) ^ 2

# Bossa Nova
chd1 = S('C major').chord_progression(['ii', 'V', 'I'])
chd2 = S('C major') % 251
chd3 = S('C major').chord_progression(['Imaj7', 'II7', 'iim7'])

# Lounge / Jazz
s1 = S('C major')
chd4 = s1 % 4251
chd5 = s1 % 736251

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
strSFpath = os.getcwd() + '\\Soundfont\\'
# Piano
strSFname = 'Emu 9ftgrand.sf2'
strSFname = 'R-piano.sf2'
# Guitar
strSFname = 'Sessgit.sf2'
strSFname = 'Seagull_Acoustic_Guitar.SF2'


daw1 = daw(3, name='Song 01')
daw1.load(0, strSFpath + strSFname)
p1 = P(tracks=[chdMelody01],channels=[1])
print (p1)
daw1.play(p1, wait=True)
