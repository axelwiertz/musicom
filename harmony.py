"""
Music - Harmony
Patterns and rules
"""

class OnsetIntervalPattern:
    TWO = (1, 1)
    THREE = (1, 1, 1)
    FOUR =  (1, 1, 1, 1)
    TRESILLO = (3, 3, 2)
    TWELVE_EIGHTH_BELL = (2, 2, 1, 2, 2, 2, 1)
    SON_CLAVE = (3, 3, 4, 2, 4)


class ChordHarmony:
    # Chord ladder
    LADDER = (
        (1, 6), # Tonic
        (5, 7), # Dominant
        (2, 4), # Pre-dominant
        6, 3
    )
    # Widely used chords sequences (progressions)
    PROGRESSION_NEXT = {
        1 : '*',
        2 : (4, 5, 7),
        3 : (2, 4, 6),
        4 : (1, 3, 5, 7),
        5 : 1,
        6 : (1, 3),
        7 : 1
    }
    # Diatonic chord functions
    TONIC = 0
    DOMINANT = 1
    SUBDOMINANT = 2
    TONIC_PROLONG = 3

    FUNCTIONS = {  TONIC : 1,
                   DOMINANT : (7,5),
                   SUBDOMINANT : (4,2),
                   TONIC_PROLONG : (3,6)
                }
    FLATVIICHORD = 'b7' # substitues 7 and has DOM, SUBDOM and PROLON functions

    FUNCTIONPROGRESSION = {
        TONIC : [TONIC_PROLONG, DOMINANT, SUBDOMINANT],
        DOMINANT : [TONIC],
        SUBDOMINANT : [DOMINANT]
    }
    MINORPOP = (1, 7, 6, 7)
    BESTSELLER = (1, 5, 6, 4)

    CYCLICFIFTHPROGRESSION = (1,4,7,3,6,2,5)

    PROGRESSIONS = [
    # Analysis of all progressions
        [1, 6, 4, 7, 1] ,
        [1, 6, 2, 7, 1] ,
        [1, 6, 4, 5, 1] ,
        [1, 6, 2, 5, 1] ,
        [5, 'IV6',4] ,
        [5, 4] ,
        [4, 'I6', 1] ,
    # Common progressions
        [1, 4],
        [1, 5],
        [1, 4, 5],
        [1, 4, 'V7'],
        [1, 4, 1, 5],
        [1, 4, 1, 'V7'],
        [1, 4, 5, 4],
        [1, 5, 6, 4],
        [1, 2, 4, 5],
        [1, 2, 4],
        [1, 6, 2, 5],
        [1, 6, 4, 5],
        [1, 6, 2, 4, 'V7'],
        [1, 6, 2, 'V7', 2],
        [4, 1, 4, 5],
        ["ii7", 'V7', 1],
        [1, 4, 1, 'V7', 4, 1],
        [1, 4, 7, 3, 6, 2, 5, 1]
]


class MCCadence:
    """
    Ending cadence
    """

    dctCadencePattern = {
    # Perfect cadence
        'Perfect' : (5, 1),
    # Plagal cadence
        'Plagal' : (4, 1),
    # Imperfect cadence
        'Imperfect' : ((1, 5), (2, 5), (4, 5), (6, 5)),
    # Interrupted cadence
        'Interrupted' : ((5, 4), (5, 6), (5, 2), (5, 'V7'))
    }

class MCModulation:
    """
    Modulation progression in new key
    """
    dctModulationPattern = {
        'Direct' : (),
        'Dominant' : 'V7',
        'Subdominant' : ('iim7', 'V7'),
}


class MCVoiceMovement:
    # Classic style - Voice movement

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
        2 : [-1, 1],
        4 : -1,
        6 : -1,
        7 : 1,
        0 : [0, +2, -2]
    }
