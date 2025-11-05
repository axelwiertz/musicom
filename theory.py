"""
Music theory
"""
from config import Config
from constants import TwelveTET
from structures import Circle, Helix, sequence_rotations, interval_to_step

# General modules
import numpy as np
import pandas as pd
import itertools

# Music21 modules
from music21 import interval, key, scale, note, serial
# MusicPy modules
from musicpy import structures

class PitchRegister(Helix):
    # Chromatic pitch helix
    ASCENDING = 1
    DESCENDING = -1
    def __init__(self,  pitchclass_start=TwelveTET.A,
                        octave_start=0,
                        pitchclass_end=TwelveTET.C,
                        octave_end=8,
                        num_pitchclasses: int = TwelveTET.TWELVE,
                        num_octaves: int = TwelveTET.OCTAVES,
                      ):
        # Represent as helix of (pitchclass, octave): (0, 4)
        super().__init__(num_pitchclasses, num_octaves)

        self.num_pitchclasses = num_pitchclasses
        self.num_octaves = num_octaves

        self.index_start = self.index_of(pitchclass_start, octave_start)
        self.index_end = self.index_of(pitchclass_end, octave_end)

        self.tt = TwelveTET()
        self.midi = [self.tt.name_to_midi(self.tt.PITCH_CLASS_NAMES_SHARP[pitchclass]+str(octave))
                for (pitchclass, octave) in self.helix]

    def transpose(self, i, interval_steps, direction=ASCENDING):
        # Transpose index i by interval_steps in direction (ASCENDING or DESCENDING)
        return (i + direction*interval_steps) % len(self.helix)


class Diatonic:
    # Diatonic patterns: intervals, scales, modes, chords
    DI = 2
    TRIA = 3
    TETRA = 4
    PENTA = 5
    HEXA = 6
    HEPTA = 7
    OCTA = 8
    NONA = 9
    DECA = 10
    UNDA = 11
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
        DI: {
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

    # 7 Hepta scale modes:
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
    perfectintervals = ('P1', 'P4', 'P5', 'P8')
    imperfectintervals = ('M2', 'm3', 'M3', 'm6', 'M6', 'm7', 'M7')

    perfectintervallist = [interval.DiatonicInterval(interval.Specifier.PERFECT, 1),
                           interval.DiatonicInterval(interval.Specifier.PERFECT, 4),
                           interval.DiatonicInterval(interval.Specifier.PERFECT, 5),
                           interval.DiatonicInterval(interval.Specifier.PERFECT, 8)]

    intervallist = [interval.DiatonicInterval(interval.Specifier.MAJOR, 2),
                    interval.DiatonicInterval(interval.Specifier.MINOR, 3)]


class MusicPattern:
    def __init__(self,
                 cardinality: int = None,
                 interval_pattern: int = None
                 ):
        self.pitch_intervals = Diatonic.pitch_intervals_dict[cardinality][interval_pattern]
        self.degrees = tuple(range(1, cardinality + 1))
        # Permutations: ordered set
        self.degree_permutations = list(itertools.permutations(self.degrees))

        # Scale modes and chord positions - rotations of interval sequence
        self.modes = sequence_rotations(self.pitch_intervals)
        # Modes on pitch helix
        self.modeshelix = [interval_to_step(m) for m in self.modes]

    def save (self):
        pdmodes = pd.DataFrame(self.modes)
        pdmodeshelix = pd.DataFrame(self.modeshelix)

        pdmodes.to_excel(Config.DEFAULT_PATH + 'interval_patternModes.xlsx', index=True, sheet_name='MusicPattern')
        pdmodeshelix.to_excel(Config.DEFAULT_PATH + 'interval_patternModesHelix.xlsx', index=True, sheet_name='MusicPattern')

class MusicScale(MusicPattern):
    def __init__(self,
                cardinality: int = None,
                interval_pattern: int = None,
                tonic : int = None,
                mode : int = None
                 ):
        super().__init__(cardinality, interval_pattern)
        self.tonic = tonic
        self.mode = mode

        # Heptatonic (7 pitch class) scale
        if cardinality == Diatonic.HEPTA and interval_pattern == Diatonic.SCALE:
            # MusicPy structures
            self.mpscale = structures.scale(TwelveTET.PITCH_CLASS_NAMES_SHARP[self.tonic], interval=self.modes[self.mode])

            # Music21 structures
            self.m21key = key.Key(note.Pitch(tonic), mode=Diatonic.mode_names[self.mode])
            self.m21scale = scale.ConcreteScale(key=self.m21key)


class MusicalInterval:
    # Musical intervals
    def __init__(self, semitones=0):
        self.semitones = semitones
        self.cents = TwelveTET().interval_cents(semitones)

class PatternSequence:
    """
    Ordered set of patterns
    """
    def __init__(self, patterns: list[MusicPattern]):
        self.patterns = patterns


class PitchClassSet:
    def __init__(self, num_items=3):

        # Combinations: and permutations of a set
        self.combinations = list(itertools.combinations (TwelveTET.PITCH_CLASS_NUMBERS, num_items))
        self.permutations = list(itertools.permutations (TwelveTET.PITCH_CLASS_NUMBERS, num_items))




def main():
    # Piano register from A0 to C8
    reg = PitchRegister(TwelveTET.A, 0, TwelveTET.C, 8)
    reg.show()

    pos = reg.index_of(3, 7)  # octave 3, pitchclass 7 -> index
    next_pos = reg.transpose(pos,reg.ASCENDING)  # next pitchclass
    octave_pitchclass = reg.get_at(next_pos)
    print (f'PitchRegister: pos {pos} -> next pos {next_pos} -> (octave, pitchclass) {octave_pitchclass}')

    pcs = PitchClassSet()
    print(f'PitchClassSet combinations: {len(pcs.combinations)}')

    scale5cmajor = MusicScale(Diatonic.PENTA, Diatonic.SCALE,
                              tonic=TwelveTET.C, mode=Diatonic.major_mode)
    scale7cmajor = MusicScale(Diatonic.HEPTA, Diatonic.SCALE,
                              tonic=TwelveTET.C, mode=Diatonic.major_mode)

    m21intervals = list(interval.ChromaticInterval(n) for n in TwelveTET.PITCH_CLASS_NUMBERS)

    # Table of all absolute chromatic data along pitch number set
    interval_pattern7 = MusicPattern(Diatonic.HEPTA, Diatonic.SCALE)
    interval_pattern7.save()
    scale7 = MusicScale(Diatonic.HEPTA, Diatonic.SCALE, tonic=TwelveTET.C, mode=Diatonic.major_mode)

    # Pitch helixes for heptatonic modes
    # Major
    majormodehelix = TwelveTET.OCTAVES * interval_pattern7.modeshelix[Diatonic.major_mode]
    # Minor
    minormodehelix = TwelveTET.OCTAVES * interval_pattern7.modeshelix[Diatonic.minor_mode]

    # Major mode pitch helixes for all tonics (C, C#, D, ..., B)
    majorscales = [majormodehelix[-x:] + majormodehelix[:-x] for x in range(TwelveTET.TWELVE)]
    minorscales = [minormodehelix[-x:] + minormodehelix[:-x] for x in range(TwelveTET.TWELVE)]

    chromatic_data = pd.DataFrame(majorscales)
    chromatic_data.to_excel(Config.DEFAULT_PATH + 'ChromaticLayer.xlsx', index=True, sheet_name='Pitch')

    chromatic_table = chromatic_data.transpose()
    #chromatic_table.columns = ['Nr', 'ClassNr', 'ClassChr', 'Freq'] + list(TwelveTET.PITCH_CLASS_NAMES_SHARP)
    chromatic_table.to_excel(Config.DEFAULT_PATH + 'ChromaticTable.xlsx', index=True, sheet_name='Pitch')

    hepta_major_arr = np.array(majorscales)

    pc_circle = Circle(TwelveTET.TWELVE, TwelveTET.PITCH_CLASS_NAMES_SHARP)
    pc_circle.show()

#    pc_circle.show(pcp7.majormodeschromatic, TwelveTET.PITCH_CLASS_NAMES_SHARP, 'Major circle')



if __name__ == '__main__':
    main()


