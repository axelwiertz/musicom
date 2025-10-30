"""
Music - Harmony
Patterns and rules
"""
from theory import Diatonic, MusicPattern

class OnsetIntervalPattern:
    TWO = (1, 1)
    THREE = (1, 1, 1)
    FOUR =  (1, 1, 1, 1)
    TRESILLO = (3, 3, 2)
    TWELVE_EIGHTH_BELL = (2, 2, 1, 2, 2, 2, 1)
    SON_CLAVE = (3, 3, 4, 2, 4)

class Scale7PitchDegree:
    # Classic style - Voice pitch movement
    # Degrees grouped by function
    priority = {
        1 : [1],            # tonic
        2 : [4, 5, 7],      # dominant
        3 : [2, 3, 6],      # subdominant
    }
    # 1 - 3 - 5 are stable scale degrees
    # 2 - 4 - 6 - 7 are active scale degrees
    activestat = {
        "Active" : [1, 3, 5],       # active scale degrees
        "Inactive" : [2, 4, 6, 7],  # inactive scale degrees
    }
    # movement rules
    # 1 3 5 inactive no rule
    # 2 4 6 7 active
    ANY = 0
    movement_rules = {
        # Active
        1 : ANY,       # tonic
        3 : ANY,       # subdominant
        5 : ANY,       # dominant
        # Inactive
        2 : [-1, 1],   # subdominant
        4 : -1,        # dominant
        6 : -1,        # tonic
        7 : 1,         # dominant
        ANY : [ANY, +2, -2] # any degree
    }


class Scale7ChordDegree:
    # Diatonic chord functions
    TONIC = 0
    DOMINANT = 1
    SUBDOMINANT = 2
    TONIC_PROLONG = 3
    function = {
             TONIC : 1,              # Tonic
             DOMINANT : (7,5),       # Dominant
             SUBDOMINANT : (4,2),    # Subdominant
             TONIC_PROLONG : (3,6)   # Tonic prolongation
             }
    function_progression = {
        TONIC : [TONIC_PROLONG, DOMINANT, SUBDOMINANT], # Tonic can go to any
        DOMINANT : [TONIC],                             # Dominant to Tonic
        SUBDOMINANT : [DOMINANT]                        # Subdominant to Dominant
             }

class Scale7Triad:
    def __init__(self):
        self.pattern_major = MusicPattern (Diatonic.TRIA, Diatonic.MAJOR)
        self.pattern_minor = MusicPattern (Diatonic.TRIA, Diatonic.MINOR)

class Scale7ChordHarmony:
    # Widely used chords sequences (progressions)
    movement_rules = {
        1 : '*',            # tonic to any
        2 : (4, 5, 7),      # subdominant to dominant
        3 : (2, 4, 6),      # tonic prolong to subdominant
        4 : (1, 3, 5, 7),   # subdominant to tonic
        5 : 1,              # dominant to tonic
        6 : (1, 3),         # tonic prolong to tonic
        7 : 1               # dominant to tonic
    }
    majormodenext = {
        '1maj' : '*',
        '2min' : ['1maj', '5maj', '7dim'],
        '3min' : ['1maj', '2min', '4maj', '6min'],
        '4maj' : ['1maj', '2min', '3min', '5maj', '7dim'],
        '5maj' : ['1maj', '6min'],
        '6min' : ['1maj', '2min', '3min', '4maj', '5maj'],
        '7dim' : ['1maj', '3min']
    }
    minormodenext = {
        '1min' : '*',
        '2dim/2maj' : ['1min', '3min', '5maj', '5min', '7dim', '7maj'],
        '3maj/3aug' : ['1min', '4minor', '4maj', '6maj', '#6dim', '7dim', '6maj'],
        '4min/4maj' : ['1min', '5maj', '5minor', '7dim', '7maj'],
        '5maj/5min' : ['1min', '6maj', '#6dim'],
        '6maj/#6dim' : ['1min', '3maj', '3aug', '4min', '4maj', '5maj', '5min', '7dim', '7maj'],
        '7dim/7maj' : ['1min']
        }
    FLAT7CHORD = 'b7' # substitutes 7 and has DOM, SUBDOM and PROLON functions

    MINORPOP = (1, 7, 6, 7)
    BESTSELLER = (1, 5, 6, 4)


    common_progressions = [
    # Analysis of all progressions
        [1, 6, 4, 7, 1] ,   # sensitive
        [1, 6, 2, 7, 1] ,   # sensitive
        [1, 6, 4, 5, 1] ,   # sensitive
        [1, 6, 2, 5, 1] ,   # sensitive
        [5, 'IV6',4] ,      # deceptive
        [5, 4] ,            # plagal
        [4, 'I6', 1] ,      # plagal
    # Common progressions
        [1, 4],             # plagal start
        [1, 5],             # perfect start
        [1, 'V7'],          # perfect start with 7th
        [1, 4, 5],          # perfect
        [1, 4, 'V7'],       # perfect with 7th
        [1, 4, 1, 5],       # plagal to perfect
        [1, 4, 1, 'V7'],    # plagal to perfect with 7th
        [1, 4, 5, 4],       # plagal ending
        [1, 5, 6, 4],       # popular
        [1, 2, 4, 5],       # popular
        [1, 2, 4],          # popular incomplete
        [1, 6, 2, 5],       # popular
        [1, 6, 4, 5],       # popular
        [1, 6, 2, 4, 'V7'], # popular to perfect with 7th
        [1, 6, 2, 'V7', 2], # popular to imperfect
        [4, 1, 4, 5],       # plagal to perfect
        ["ii7", 'V7', 1],   # ii7 - V7 - I
        [1, 4, 1, 'V7', 4, 1],  # plagal to perfect to plagal
        [1, 4, 7, 3, 6, 2, 5, 1] # cyclic fifths
]
    CYCLICFIFTHPROGRESSION = (1,4,7,3,6,2,5)

    # Common ending cadence progressions
    cadence_progressiions = {
    # Perfect cadence
        'Perfect' : (5, 1),     # V to I
    # Plagal cadence
        'Plagal' : (4, 1),      # IV to I
    # Imperfect cadence
        'Imperfect' : ((1, 5), (2, 5), (4, 5), (6, 5)), # any to V
    # Interrupted cadence
        'Interrupted' : ((5, 4), (5, 6), (5, 2), (5, 'V7')) # V to any but I
    }

    # Modulation progression in new key
    PROGRESSION_MODULATION = {
        'Direct' : (),              # direct modulation no pivot chord
        'Dominant' : 'V7',          # dominant to new key
        'Subdominant' : ('iim7', 'V7'), # subdominant to dominant to new key
        'CommonChord' : ('IV', 'V7'),   # common chord to dominant
        }
