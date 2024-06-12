'''
Music - Harmony
Patterns and rules
'''
# modules
import musicpy as mp
from musicpy import *


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
#print(lstChordPattern)

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
dctCadencePattern = {}

# Perfect cadence
dctCadencePattern ['Perfect'] = ['V', 'I']
# Plagal cadence
dctCadencePattern ['Plagal'] = ['IV', 'I']
# Imperfect cadence
dctCadencePattern ['Imperfect1'] = ['I', 'V']
dctCadencePattern ['Imperfect2'] = ['ii', 'V']
dctCadencePattern ['Imperfect3'] = ['IV', 'V']
dctCadencePattern ['Imperfect4'] = ['vi', 'V']
# Interrupted cadence
dctCadencePattern ['Interrupted1'] = ['V', 'IV']
dctCadencePattern ['Interrupted2'] = ['V', 'vi']
dctCadencePattern ['Interrupted3'] = ['V', 'ii']
dctCadencePattern ['Interrupted4'] = ['V', 'V7']

dctScaleStyle = {}
# Standard
dctScaleStyle ['Standard'] = ['C major']


# Fantasy
dctScaleStyle ['Fantasy'] = ['A minor', 'C major']

lstFantasysChordPattern = []

# I II VI II
lstFantasysChordPattern.append(['I7', 'II7', 'VI7', 'II7'])
# i II bi bIV
lstFantasysChordPattern.append(['i7', 'II7', 'isus', 'IVsus'])
# I VI I VI
lstFantasysChordPattern.append(['I7', 'VI7', 'I7', 'VI7'])
# i v VI V
lstFantasysChordPattern.append(['i7', 'v7', 'VI7', 'V7'])
# I II I II
lstFantasysChordPattern.append(['I7', 'II7', 'I7', 'II7'])
# i II iv V
lstFantasysChordPattern.append(['i7', 'II7', 'iv7', 'V7'])

# Bossa Nova
dctScaleStyle ['Bossa Nova'] = ['C major']

lstBNChordPattern = []

lstBNChordPattern.append(['ii', 'V', 'I'])
lstBNChordPattern.append(['Imaj7', 'II7', 'iim7'])

# Lounge / Jazz
s1 = S('C major')
chd4 = s1 % 4251
chd5 = s1 % 736251


# Melody scale degrees notes
dctScaleNotes = {}
dctScaleNotes [1] = [1, 'tonic']
dctScaleNotes [2] = [3, 'supertonic']
dctScaleNotes [3] = [3, 'mediant']
dctScaleNotes [4] = [2, 'subdominant']
dctScaleNotes [5] = [2, 'dominant']
dctScaleNotes [6] = [3, 'submediamt']
dctScaleNotes [7] = [2, 'leading tone']
