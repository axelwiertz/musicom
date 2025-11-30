""" Movement regularity for diatonic scale degrees """

import itertools
from base.tuning import TwelveTET

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
    active_stat = {
        "Active" : [1, 3, 5],       # active scale degrees
        "Inactive" : [2, 4, 6, 7],  # inactive scale degrees
    }
    # movement regularity
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

class PitchClassSpace:
    def __init__(self, num_items=3):

        # Combinations: and permutations of a set
        self.combinations = list(itertools.combinations (TwelveTET.PITCH_CLASS_NUMBERS, num_items))
        self.permutations = list(itertools.permutations (TwelveTET.PITCH_CLASS_NUMBERS, num_items))



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
