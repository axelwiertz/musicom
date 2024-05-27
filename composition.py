'''
Music - Compose
'''
# modules
import musicpy as mp
from musicpy import *
from musicpy.daw import *

import harmony
import rhythm


# Compose

# Guitar example
guitar = (c1 | c2 | c3 * 2 )

# Melody creation syntax
c1 = C('CM7', 3, 1 / 4, 1 / 8) ^ 2
c2 = C('CM7')
c2 = C('CM7', 3)
c3 = C('CM7', 5)
c5 = C('CM7', 3, 1 / 4, 1 / 8)
c5 = C('CM7', 3, 1 / 4)
c6 = C('CM7', 3, 1 / 4) ^ 2


# Chords
c1 = C('CM7', 3, 1/4, 1/8)^2
c2 = C('G7sus', 2, 1/4, 1/8)^2


# Scale
# Chords
chd01 = S('C4 major')%(15654321, 0.4)
chd03 = S('C major').chord_progression(['IM7', 'Vsus', 'vi7', 'IVM7'])

# Notes
chd02 = S('C major').get('1,1,5,5,6,6,5,-,4,4,3,3,2,2,1,-')


# Melody
# Big Yellow Taxi
chdMelody01 = chord('B3, C#4, E4, E4, F#4, C#4, E4, E4, F#4, E4, G#3, B3, B3, C#4, E4, F#4, B3, B3, F#4, F#4, F#4, G#4, F#4, E4, E4', 1/8, 1/8)

# Bossa Nova
chd1 = S('C major').chord_progression(['ii', 'V', 'I'])
chd2 = S('C major') % 251
chd3 = S('C major').chord_progression(['Imaj7', 'II7', 'iim7'])

# Lounge / Jazz
s1 = S('C major')
chd4 = s1 % 4251
chd5 = s1 % 736251

# Berendans
sclEb = S('Bb major')
scl1 = sclEb
chd1 = scl1.chord_progression(['I', 'V', 'I'])

print (scl1)
print ('Play :')
print (chd1)
play (chd1, wait=True)




# editor
chd4 = S('C4 major')%(15654321, 0.4)
chd5 = S('C major').get('1,1,5,5,6,6,5,-,4,4,3,3,2,2,1,-')
chd6 = S('C major').chord_progression(['IM7', 'Vsus', 'vi7', 'IVM7'])



chdMelody01 = chdFant02
# chdFant01 + chdFant02 + chdFant03 + chdFant04 + chdFant05 + chdFant06
print ('Notes : ' + str(chdMelody01.notes))
print ('Interval : ' + str(chdMelody01.interval))

play (chdMelody01, bpm=60, wait=True)

# Chords
chd01 = S('C major').get('1,2,3,4,5,6,7,1.1')

# Melody
chdMelody = [chd01, chd01, chd01]

# Tracks

# Piece
pce01 = P(tracks=[chdMelody[0], chdMelody[1], chdMelody[2]],channels=[0, 1, 2], start_times=[0, 2, 4, 6])
print (pce01)
