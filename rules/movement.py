""" Movement rules for diatonic scale degrees """

class Scale7DegreeFunction:
    # 7 Hepta scale degree functions
    degree_functions = {1: 'tonic', 2: 'supertonic', 3: 'mediant', 4: 'subdominant', 5: 'dominant', 6: 'submediant',
                        7: 'leading tone'}


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



class Scale7TriadDegree:
    # 7 Hepta scale - Triad degrees
    triad_degrees = {1: ("I", "i"), 2: ('ii', 'ii0'), 3: ('iii', 'III'), 4: ('IV', 'iv'), 5: ('V', 'V'),
                     6: ('vi', 'VI'), 7: ('vii0', 'vii0')}


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
