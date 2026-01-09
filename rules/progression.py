"""Module defining chord progression rules and common progressions."""

# TODO: Implementing secondary dominants and modal interchange: borrow chords from parallel keys.

from structures.base import Base
class MusicForm(Base):
    # Common music forms
    common_section_patterns = {
        'Binary' : ('A', 'B'),
        'Ternary' : ('A', 'B', 'A'),
        'Rondo' : ('A', 'B', 'A', 'C', 'A'),
        'Sonata' : ('Exposition', 'Development', 'Recapitulation'),
        'Strophic' : ('Verse1', 'Verse2', 'Verse3'),
        'Verse Chorus' : ('Verse', 'Chorus', 'Verse', 'Chorus', 'Bridge', 'Chorus'),
        '12 Bar Blues' : ('A', 'A', 'A', 'A', 'B', 'A', 'C', 'A'),
        'Pop Song' : ('Intro', 'Verse', 'Chorus', 'Verse', 'Chorus', 'Bridge', 'Chorus', 'Outro'),
        '32 Bar Blues' : ('A', 'A', 'A', 'A', 'B', 'A', 'C', 'A', 'D', 'A', 'E', 'A', 'F', 'A', 'G', 'A'),
    }

    def __init__(self,
                 name: str,
                 section_pattern: tuple):
        super().__init__(name)
        self.section_pattern = section_pattern


class PatternMovementRules:
    # Widely used triad move (progressions)
    movement_rules = {
        1 : '*',            # tonic to any
        2 : (4, 5, 7),      # subdominant to dominant
        3 : (2, 4, 6),      # tonic prolong to subdominant
        4 : (1, 3, 5, 7),   # subdominant to tonic
        5 : 1,              # dominant to tonic
        6 : (1, 3),         # tonic prolong to tonic
        7 : 1               # dominant to tonic
    }
    major_mode_next = {
        '1maj' : '*',
        '2min' : ['1maj', '5maj', '7dim'],
        '3min' : ['1maj', '2min', '4maj', '6min'],
        '4maj' : ['1maj', '2min', '3min', '5maj', '7dim'],
        '5maj' : ['1maj', '6min'],
        '6min' : ['1maj', '2min', '3min', '4maj', '5maj'],
        '7dim' : ['1maj', '3min']
    }
    minor_mode_next = {
        '1min' : '*',
        '2dim/2maj' : ['1min', '3min', '5maj', '5min', '7dim', '7maj'],
        '3maj/3aug' : ['1min', '4minor', '4maj', '6maj', '#6dim', '7dim', '6maj'],
        '4min/4maj' : ['1min', '5maj', '5minor', '7dim', '7maj'],
        '5maj/5min' : ['1min', '6maj', '#6dim'],
        '6maj/#6dim' : ['1min', '3maj', '3aug', '4min', '4maj', '5maj', '5min', '7dim', '7maj'],
        '7dim/7maj' : ['1min']
        }
    FLAT7CHORD = 'b7' # substitutes 7 and has DOM, SUBDOM and PROLON functions


class PatternMovement:
    # Common chord progressions in scale degrees
    minor_pop_progression = (1, 7, 6, 7)
    bestseller_progression = (1, 5, 6, 4)
    fifties_progression = (1, 6, 2, 5)
    fifths_down_progression = (1, 4, 7, 3, 6, 2, 5)
    # (TRIA,2,MAJOR), (TRIA,5,MAJOR), (TRIA,1,MAJOR)
    bossa_nova_progression2 = ['Imaj7', 'II7', 'iim7']

    flamenco_progression = (1, 7, 6, 5)

    loungejazz_progression1 = (7, 3, 6, 2, 5, 1)

    loungejazz_progression2 = (4, 2, 5, 1),


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

    # Common ending cadence progressions
    cadence_progressions = {
    # Perfect cadence
        'Perfect' : (5, 1),     # V to I
    # Plagal cadence
        'Plagal' : (4, 1),      # IV to I
    # Imperfect cadence
        'Imperfect' : ((1, 5), (2, 5), (4, 5), (6, 5)), # any to V
    # Interrupted cadence
        'Interrupted' : ((5, 4), (5, 6), (5, 2), (5, 'V7')) # V to any but I
    }

class Modulation:
    # Modulation progression in new key
    modulation_progression = {
        'Direct' : (),              # direct modulation no pivot chord
        'Dominant' : 'V7',          # dominant to new key
        'Subdominant' : ('iim7', 'V7'), # subdominant to dominant to new key
        'CommonChord' : ('IV', 'V7'),   # common chord to dominant
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


class Scale7TriadDegree:
    # 7 Hepta scale - Triad degrees
    triad_degrees = {1: ("I", "i"), 2: ('ii', 'ii0'), 3: ('iii', 'III'), 4: ('IV', 'iv'), 5: ('V', 'V'),
                     6: ('vi', 'VI'), 7: ('vii0', 'vii0')}


class Scale7SeventhDegree:
    # 7 Hepta scale - Seventh chord degrees
    seventh_degrees = {1: ("I7", "i7"), 2: ('ii7', 'iiø7'), 3: ('iii7', 'III7'), 4: ('IV7', 'iv7'),
                       5: ('V7', 'V7'), 6: ('vi7', 'viø7'), 7: ('viiø7', 'viiø7')}



class PatternProgressions:

    blues8_major_progression = [
        (1, 4, 1, 6),
        (4, 4, 1, 1),
        (2, 5, 1, 1)
    ]

    blues12_major_progression = [
        (1, 1, 1, 1),
        (4, 4, 1, 1),
        (5, 4, 1, 1)
    ]
    blues12_minor_progression = [
        (1, 4, 1, 5),
        (4, 4, 1, 6),
        (2, 5, 1, 1)]

    blues12_minor_progression2 = [
        (1, 1, 1, 1),
        (4, 4, 1, 1),
        (5, 4, 1, 1)
    ]

    blues16_major_progression = [
        (1, 1, 1, 1),
        (4, 4, 1, 1),
        (5, 4, 5, 4),
        (5, 4, 1, 1)
    ]

    blues24_major_progression = [
        (1, 1, 1, 1),
        (1, 1, 1, 1),
        (4, 4, 4, 4),
        (1, 1, 1, 1),
        (5, 5, 4, 4),
        (1, 1, 1, 1)
    ]

    blues32_major_progression = [
        (1, 1, 1, 1),
        (1, 1, 1, 1),
        (4, 4, 4, 4),
        (1, 1, 1, 1),
        (5, 5, 4, 4),
        (1, 1, 1, 1),
        (5, 5, 4, 4),
        (1, 1, 1, 1)
    ]
