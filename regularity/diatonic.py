"""Diatonic patterns: intervals, scales, modes, chords"""
from music21 import interval
from structures.pattern import MusicPattern

class Diatonic:
    # Diatonic patterns: cardinality, intervals, scales, modes, chords
    DYAD = 2
    TRIA = 3
    TETRA = 4
    PENTA = 5
    HEXA = 6
    HEPTA = 7
    OCTA = 8
    NONA = 9
    DECA = 10
    UNDECA = 11
    DODECA = 12

    MINOR_THIRD = 1
    MAJOR_THIRD = 2
    PERFECT_FOURTH = 3
    TRITONE = 4
    PERFECT_FIFTH = 5
    MINOR_SIXTH = 6
    MAJOR_SIXTH = 7

    SCALE = 0

    DIMINISHED = 1
    MINOR = 2
    MAJOR = 3
    AUGMENTED = 4
    SUS2 = 5
    SUS4 = 6

    MINOR7 = 1
    MAJOR7 = 2
    DOMINANT7 = 3
    MAJOR6 = 4
    MINOR6 = 5
    MINOR7_FLAT5 = 6

    NINTH = 1
    MINOR_NINTH = 2

    # Interval patterns for scales and chords
    # pitch_intervals: tuple of interval steps, e.g. (2,2)
    pitch_intervals_dict = {
        DYAD: {
            MINOR_THIRD     : (3, 9),
            MAJOR_THIRD     : (4, 8),
            PERFECT_FOURTH  : (5, 7),
            TRITONE         : (6, 6),
            PERFECT_FIFTH   : (7, 5),
            MINOR_SIXTH     : (8, 4),
            MAJOR_SIXTH     : (9, 3),
        },
        # 3 Triad scale Patterns
        TRIA:  {
            DIMINISHED: (3, 3, 6),
            MINOR: (3, 4, 5),
            MAJOR: (4, 3, 5),
            AUGMENTED: (4, 4, 4),
            SUS2: (2, 5, 5),
            SUS4: (5, 2, 5),
        },
        TETRA : {
            MINOR7: (3, 4, 3, 2),
            MINOR7_FLAT5: (3, 3, 4, 2),
            MAJOR7 : (4, 3, 4, 1),
            DOMINANT7: (4, 3, 3, 2),
            MAJOR6: (4, 3, 2, 3),
            MINOR6: (3, 4, 2, 3),
            AUGMENTED: (4, 4, 3, 1),
            SUS2: (2, 5, 4, 1),
            SUS4: (5, 2, 4, 1)
        },
        PENTA: {
            SCALE: (2, 2, 3, 2, 3),
        },
        HEPTA: {
            SCALE : (2, 2, 1, 2, 2, 2, 1)
        },
        NONA: {},
        DECA: {},
        DODECA: {
            SCALE: (1,1,1,1,1,1,1,1,1,1,1,1)
        },
    }
    multicycle_patterns = {
        14: {
            NINTH: (4, 3, 3, 4, 10),
            MINOR_NINTH: (3, 4, 3, 4, 10)
        }
    }

    # 7 Heptatonic scale modes:
    ionian = major_mode = 0
    dorian = 1
    phrygian = 2
    lydian = 3
    mixolydian = 4
    aeolian = minor_mode = 5
    locrian = 6
    mode_names = {ionian:'ionian',dorian:'dorian',phrygian:'phrygian',
            lydian:'lydian',mixolydian:'mixolydian',aeolian:'aeolian',locrian:'locrian'}


    # 7 Hepta scale degree functions
    degree_functions = {1: 'tonic', 2: 'supertonic', 3: 'mediant', 4: 'subdominant', 5: 'dominant', 6: 'submediant',
                        7: 'leading tone'}

    # 7 Hepta scale - Triad degrees
    triad_degrees = {1: ("I", "i"), 2: ('ii', 'ii0'), 3: ('iii', 'III'), 4: ('IV', 'iv'), 5: ('V', 'V'),
                     6: ('vi', 'VI'), 7: ('vii0', 'vii0')}


    # 7 Hepta Interval classes
    perfect_interval_classes = ('P1', 'P4', 'P5', 'P8')
    imperfect_interval_classes = ('M2', 'm3', 'M3', 'm6', 'M6', 'm7', 'M7')

    perfect_interval_class_list = [interval.DiatonicInterval(interval.Specifier.PERFECT, 1),
                           interval.DiatonicInterval(interval.Specifier.PERFECT, 4),
                           interval.DiatonicInterval(interval.Specifier.PERFECT, 5),
                           interval.DiatonicInterval(interval.Specifier.PERFECT, 8)]

    imperfect_interval_class_list = [interval.DiatonicInterval(interval.Specifier.MAJOR, 2),
                    interval.DiatonicInterval(interval.Specifier.MINOR, 3)]


class Scale7Triad:
    def __init__(self):
        self.pattern_major = MusicPattern(Diatonic.TRIA, Diatonic.MAJOR)
        self.pattern_minor = MusicPattern(Diatonic.TRIA, Diatonic.MINOR)