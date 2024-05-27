'''
Music - Harmony
Scales and chords
'''
# modules
import musicpy as mp
from musicpy import *
from musicpy.daw import *


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

# Fantasy chords
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
