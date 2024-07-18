'''
Music - Harmony
Patterns and rules
'''
# modules
import musicpy as mp
from musicpy import *


# Chords
# Progression rules
dctChordProgr = {
    'I': ['*'],
    'ii' : ['IV', 'V', 'vii0'],
    'iii' : ['ii', 'IV', 'vi'],
    'IV' : ['I', 'iii', 'V', 'vii0'],
    'V' : ['I'],
    'vi' : ['I', 'iii']
}

lstChordPattern = [
    # Analysis of all progressions
    ['I', 'vi', 'IV', 'viio', 'I'] ,
    ['I', 'vi', 'ii', 'viio', 'I'] ,
    ['I', 'vi', 'IV', 'V', 'I'] ,
    ['I', 'vi', 'ii', 'V', 'I'] ,
    ['V', 'IV6','IV'] ,
    ['v', 'iv'] ,
    ['iv', 'I6', 'I']
# Common progressions
    ["I", 'IV'],
    ["I", 'V'],
    ["I", 'IV', 'V'],
    ["I", 'IV', 'V7'],
    ["I", 'IV', 'I', 'V'],
    ["I", 'IV', 'I', 'V7'],
    ["I", 'IV', 'V', 'IV'],
    ["I", 'V', 'vi', 'IV'],
    ["I", 'ii', 'IV', 'V'],
    ["I", 'ii', 'IV'],
    ["I", 'vi', 'ii', 'V'],
    ["I", 'vi', 'IV', 'V'],
    ["I", 'vi', 'ii', 'IV', 'V7'],
    ["I", 'vi', 'ii', 'V7', 'ii'],
    ["IV", 'I', 'IV', 'V'],
    ["ii7", 'V7', 'I'],
    ["I", 'IV', 'I', 'V7', 'IV', 'I'],
    ["I", 'IV', 'vii0', 'iii', 'vi', 'ii', 'V', 'I']
]
#print(lstChordPattern)

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
