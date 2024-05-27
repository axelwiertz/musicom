# modules
import musicpy as mp
from musicpy import *
from musicpy.daw import *

# Compose
# Chords
# Progression rules
dctChordProgr = {}
dctChordProgr ['I'] = ['*']
dctChordProgr ['ii'] = ['IV', 'V', 'vii0']
dctChordProgr ['iii'] = ['ii', 'IV', 'vi']
dctChordProgr ['IV'] = ['I', 'iii', 'V', 'vii0']
dctChordProgr ['V'] = ['I']
dctChordProgr ['vi'] = ['I', 'iii']

lstChordPattern = []
# Analysis of all progressions
lstChordPattern.append( ['I', 'vi', 'IV', 'viio', 'I'] )
lstChordPattern.append( ['I', 'vi', 'ii', 'viio', 'I'] )
lstChordPattern.append( ['I', 'vi', 'IV', 'V', 'I'] )
lstChordPattern.append( ['I', 'vi', 'ii', 'V', 'I'] )
lstChordPattern.append( ['V', 'IV6','IV'] )
lstChordPattern.append( ['v', 'iv'] )
lstChordPattern.append( ['iv', 'I6', 'I'] )
# Common progressions
lstChordPattern.append( ["I", 'IV'] )
lstChordPattern.append( ["I", 'V'] )
lstChordPattern.append( ["I", 'IV', 'V'] )
lstChordPattern.append( ["I", 'IV', 'V7'] )
lstChordPattern.append( ["I", 'IV', 'I', 'V'] )
lstChordPattern.append( ["I", 'IV', 'I', 'V7'] )
lstChordPattern.append( ["I", 'IV', 'V', 'IV'] )
lstChordPattern.append( ["I", 'V', 'vi', 'IV'] )
lstChordPattern.append( ["I", 'ii', 'IV', 'V'] )
lstChordPattern.append( ["I", 'ii', 'IV'] )
lstChordPattern.append( ["I", 'vi', 'ii', 'V'] )
lstChordPattern.append( ["I", 'vi', 'IV', 'V'] )
lstChordPattern.append( ["I", 'vi', 'ii', 'IV', 'V7'] )
lstChordPattern.append( ["I", 'vi', 'ii', 'V7', 'ii'] )
lstChordPattern.append( ["IV", 'I', 'IV', 'V'] )
lstChordPattern.append( ["ii7", 'V7', 'I'] )
lstChordPattern.append( ["I", 'IV', 'I', 'V7', 'IV', 'I'] )
lstChordPattern.append( ["I", 'IV', 'vii0', 'iii', 'vi', 'ii', 'V', 'I'] )
#print (lstChordPattern)

# Ending cadence
lstCadencePattern = []
# Perfect cadence
lstCadence = ['V', 'I']
# Plagal cadence
lstCadence = ['IV', 'I']
# Imperfect cadence
lstCadence = ['I', 'V']
lstCadence = ['ii', 'V']
lstCadence = ['IV', 'V']
lstCadence = ['vi', 'V']
# Interrupted cadence
lstCadence = ['V', 'IV']
lstCadence = ['V', 'vi']
lstCadence = ['V', 'ii']
lstCadence = ['V', 'V7']


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


# Compose from scale
chd01 = S('C4 major')%(15654321, 0.4)
chd02 = S('C major').get('1,1,5,5,6,6,5,-,4,4,3,3,2,2,1,-')
chd03 = S('C major').chord_progression(['IM7', 'Vsus', 'vi7', 'IVM7'])


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


# drum                                                                                                                                
drum1 = drum('S[l:.8; i:.; r:4], S[l:.16; i:.], S[l:.8; i:.], S[l:.16; i:.], S[l:.8; i:.], S[l:.8; i:.]')
drum('S[l:.8; i:.; r:4], S[l:.16; i:.], S[l:.8; i:.], S[l:.16; i:.], S[l:.8; i:.], S[l:.8; i:.]')

drum ('K, K;H, S, H, K, K;H;PH, H;S, H')

# rhythm


# editor
chd4 = S('C4 major')%(15654321, 0.4)
chd5 = S('C major').get('1,1,5,5,6,6,5,-,4,4,3,3,2,2,1,-')
chd6 = S('C major').chord_progression(['IM7', 'Vsus', 'vi7', 'IVM7'])

# Fantasy
scla = S('A minor', 3)
sclC = S('C major')
#print (scla)

# a I II VI II
chdFant01 = scla.chord_progression(['I7', 'II7', 'VI7', 'II7'])
# a i II bi bIV
chdFant02 = scla.chord_progression(['i7', 'II7', 'isus', 'IVsus'])
# a I VI I VI
chdFant03 = scla.chord_progression(['I7', 'VI7', 'I7', 'VI7'])
# a i v VI V
chdFant04 = scla.chord_progression(['i7', 'v7', 'VI7', 'V7'])
# a I II I II
chdFant05 = scla.chord_progression(['I7', 'II7', 'I7', 'II7'])
# a i II iv V
chdFant06 = scla.chord_progression(['i7', 'II7', 'iv7', 'V7'])


chdMelody01 = chdFant02
# chdFant01 + chdFant02 + chdFant03 + chdFant04 + chdFant05 + chdFant06
print ('Notes : ' + str(chdMelody01.notes))
print ('Interval : ' + str(chdMelody01.interval))

play (chdMelody01, bpm=60, wait=True)