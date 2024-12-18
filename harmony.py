'''
Music - Harmony
Patterns and rules
'''

'''
Chords
'''
# Chords
# Chord ladder
dctChordLadder = {
    'Major': [['I','vi'],['V', 'vii0'],['ii', 'IV'],['vi'],['iii']],
    'Minor': [['i','VI'],['V', 'vii0'],['ii0', 'iv'],['VI'],['III']]
}
# Widely used chrod progressions
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
    ['iv', 'I6', 'I'] ,
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

'''
Ending cadence
'''
dctCadencePattern = {
# Perfect cadence
    'Perfect' : ['V', 'I'],
# Plagal cadence
    'Plagal' : ['IV', 'I'],
# Imperfect cadence
    'Imperfect' : [['I', 'V'], ['ii', 'V'], ['IV', 'V'], ['vi', 'V']],
# Interrupted cadence
    'Interrupted' : [['V', 'IV'], ['V', 'vi'], ['V', 'ii'], ['V', 'V7']]
}

'''
Scales in styles
'''
dctStyleScale = {
# Standard
    'Standard' : ['C major'],
# Fantasy
    'Fantasy' : ['A minor', 'C major'],
# Bossa Nova
    'Bossa Nova' : ['C major']
}

'''
Chord progression patterns in styles
'''
dctStyleChordPattern = {
    'Fantasy' :  [
# I II VI II
    ['I7', 'II7', 'VI7', 'II7'],
# i II bi bIV
    ['i7', 'II7', 'isus', 'IVsus'],
# I VI I VI
    ['I7', 'VI7', 'I7', 'VI7'],
# i v VI V
    ['i7', 'v7', 'VI7', 'V7'],
# I II I II
    ['I7', 'II7', 'I7', 'II7'],
# i II iv V
    ['i7', 'II7', 'iv7', 'V7']
    ],

'Bossa Nova' : [
    ['ii', 'V', 'I'],
    ['Imaj7', 'II7', 'iim7']
    ],

'Lounge/Jazz' : [
    [4, 2, 5, 1],
    [7, 3, 6, 2, 5, 1]
    ]
}

'''
Voice movement
'''

# Melody scale degrees notes
dctScaleNotes = {
    1 : 'tonic',
    2 : 'supertonic',
    3 : 'mediant',
    4 : 'subdominant',
    5 : 'dominant',
    6 : 'submediant',
    7 : 'leading tone'
}

dctScaleDegrPrio = {
    1 : [1],
    2 : [4, 5, 7],
    3 : [2, 3, 6],
}
dctScaleDegrAct = {
    "Active" : [1, 3, 5],
    "Inactive" : [2, 4, 6, 7],
}
# melody degree step movement rules
# 1 3 5 inactive no rule
# 2 4 6 7 active
dctScaleDegrMove = {
# 0 = any scale degree
    # Active
    1 : 0,
    3 : 0,
    5 : 0,
    # Inactive
    2 : -1,
    2 : 1,
    4 : -1,
    6 : -1,
    7 : 1,
    0 : 0,
    0 : +2,
    0 : -2
}

'''
Pitch ranges of instruments
'''
dctRangeInstr = {
    'Piano': ['A0','C8'], # Piano keyboard
    'Guitar': ['E2','D6'], # Acoustic guitar with standard tuning
    'Ukelele': ['C4', 'C6'] # ??
}
