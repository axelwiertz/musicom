"""
Music theory
"""
from library import *

# General modules
import numpy as np
import pandas as pd
import itertools

# Music21 modules
from music21 import interval, meter, tempo

class MusicalTime:
    TWO = (1, 1)
    THREE = (1, 1, 1)
    FOUR =  (1, 1, 1, 1)
    TRESILLO = (3, 3, 2)
    TWELVE_EIGHTH_BELL = (2, 2, 1, 2, 2, 2, 1)
    SON_CLAVE = (3, 3, 4, 2, 4)

    # Rhythm and meter
    def __init__(self,
                 timesteps: int = 8,
                 beat_note: int = 4,
                 beats_in_measure: int = 4,
                 bpm: int = 100):

        # Linking timesteps to meter beats
        self.timesteps = timesteps
        # Meter: measure cycle of beats
        self.beats_in_measure = beats_in_measure
        self.beat_note = beat_note
        self.bpm = bpm

        # m21 meter
        # unit is quarter note
        self.M21_QUARTER = 4
        self.timesignature = meter.TimeSignature(str(self.beats_in_measure) + '/' + str(self.beat_note))
        # main_beatcount = self.timesignature.beatCount
        self.beat_duration = self.M21_QUARTER / self.beat_note
        # beat_duration2 = self.timesignature.beatDuration.quarterLength
        self.tempo = tempo.MetronomeMark(number=self.bpm)


class TwelveTET:
    # 12-Tone Equal Temperament tuning system
    FREQUENCY_A4 = 440
    OCTAVE = 12  # Number of pitch classes 0-11
    C = 0
    C_SHARP = D_FLAT = 1
    D = 2
    D_SHARP = E_FLAT = 3
    E = 4
    F = 5
    F_SHARP = G_FLAT = 6
    G = 7
    G_SHARP = A_FLAT = 8
    A = 9
    A_SHARP = B_FLAT = 10
    B = 11
    INTEGERS = (C, C_SHARP, D, D_SHARP, E, F, F_SHARP, G, G_SHARP, A, A_SHARP, B)
    STRINGS = ('C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B')
    CYCLES = 9  # Number of octaves in the pitch set


class PitchRing:
    ASCENDING = 1
    DESCENDING = -1
    """
    Chromatic pitch octave ring
    """
    def __init__(self):
        # Represent as list of (octave, pitchclass)
        self.ring = [(octave_idx, pitch_class)
                     for octave_idx in range(TwelveTET.CYCLES)
                     for pitch_class in range(TwelveTET.OCTAVE)]

        index_A0 = self.index_of(0, TwelveTET.A)
        index_C8 = self.index_of(8, TwelveTET.C)
        self.piano_ring = self.ring[index_A0:index_C8 + 1]

        # Create pitch to frequency mapping
        keys = np.array([x + str(y) for y in range(TwelveTET.CYCLES) for x in TwelveTET.STRINGS])
        # Trim to standard 88 pianokeys
        start = np.where(keys == 'A0')[0][0]
        end = np.where(keys == 'C8')[0][0]
        keys = keys[start:end + 1]

        self.pitch_freqs = dict(zip(keys, [2 ** ((n + 1 - 49) / 12) * TwelveTET.FREQUENCY_A4 for n in range(len(keys))]))
        self.pitch_freqs[''] = 0.0  # stop

        self.PITCHFREQUENCYLIST = tuple(2 ** ((n - MIDIpitch.A4) / TwelveTET.OCTAVE) * TwelveTET.FREQUENCY_A4
                                        for n in MIDIpitch.NUMBERS)


        # Multiple octaves
        self.PITCHCLASSES_STR_FULL = tuple(x for _ in range(0, TwelveTET.CYCLES) for x in TwelveTET.STRINGS)
        self.PITCHCLASSES_INT_FULL = tuple(TwelveTET.CYCLES * TwelveTET.INTEGERS)

        self.INTERVALLIST = (interval.ChromaticInterval(n) for n in TwelveTET.INTEGERS)

    def index_of(self, octave_idx, pitchclass):
        return octave_idx * TwelveTET.CYCLES + pitchclass

    def get_at(self, i):
        return self.ring[i % len(self.ring)]

    def transpose(self, i, interval_steps, direction=ASCENDING):
        return (i + direction*interval_steps) % len(self.ring)


class PitchClassSet:
    def __init__(self):

        # Combinations: of a set
        num_items = 3
        self.PITCHCLASS_COMBINATIONS = list(itertools.combinations (TwelveTET.INTEGERS, num_items))


class DiatonicLayer:
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

    # 3 Tria patterns:
    DIMINISHED_CHORD = 0
    MINOR_CHORD = 1
    MAJOR_CHORD = 2
    AUGMENTED_CHORD = 3
    SUS2_CHORD = 4
    SUS4_CHORD = 5
    TRIAD = {
        DIMINISHED_CHORD : (3, 3, 6),
        MINOR_CHORD: (3, 4, 5),
        MAJOR_CHORD : (4, 3, 5),
        AUGMENTED_CHORD: (4, 4, 4),
        SUS2_CHORD: (2, 5, 5),
        SUS4_CHORD: (5, 2, 5)
    }
    # 4 Tetra scale Patterns
    TETRACHORD = {
        MINOR_CHORD: (3, 4, 3, 2),
        MAJOR_CHORD : (4, 3, 4, 1),
        AUGMENTED_CHORD: (4, 4, 3, 1),
        SUS2_CHORD: (2, 5, 4, 1),
        SUS4_CHORD: (5, 2, 4, 1)
    }


    # Pentatonic (5 pitch class) scale
    PENTATONICDEGREES = tuple(range(1, PENTA + 1)) # Pentatonic scale degree number
    PENTATONIC = (2,2,3,2,3) # sequence of 5 intervalsteps
    PENTAMODES = []
    PENTAMODESCHROMATIC = []

    # Heptatonic (7 pitch class) scale
    HEPTATONICDEGREES = tuple(range(1, HEPTA + 1)) # Heptatonic scale degree number
    HEPTATONIC = (2,2,1,2,2,2,1) # sequence of 7 intervalsteps
    HEPTAMODES = []
    HEPTAMODESCHROMATIC = []

    # Chromatic pitch masks for modes:
    # 1. Ionian = Major 2. Dorian, 3. Phrygian, 4. Lydian, 5. Mixolydian, 6. Aeolian = Minor, 7. Locrian
    IONIAN_MODE = MAJOR_MODE = 0
    DORIAN_MODE = 1
    PHRYGIAN_MODE = 2
    LYDIAN_MODE = 3
    MIXOLYDIAN_MODE = 4
    AEOLIAN_MODE = MINOR_MODE = 5
    LOCRIAN_MODE = 6
    MODES = {
        IONIAN_MODE : 'Ionian',
        DORIAN_MODE : 'Dorian',
        PHRYGIAN_MODE : 'Phrygian',
        LYDIAN_MODE : 'Lydian',
        MIXOLYDIAN_MODE : 'Mixolydian',
        AEOLIAN_MODE : 'Aeolian',
        LOCRIAN_MODE : 'Locrian' }

    # 7 Hepta scale degree functions
    FUNCTIONS = {1:'tonic', 2:'supertonic', 3:'mediant', 4:'subdominant', 5:'dominant', 6:'submediant', 7:'leading tone'}
    # 7 Hepta Interval classes
    PERFECTINTERVALS = ('P1','P4','P5','P8')
    IMPERFECTINTERVALS = ('M2','m3','M3','m6','M6','m7','M7')

    perfectintervallist = [interval.DiatonicInterval(interval.Specifier.PERFECT, 1),
                interval.DiatonicInterval(interval.Specifier.PERFECT, 4),
                interval.DiatonicInterval(interval.Specifier.PERFECT, 5),
                interval.DiatonicInterval(interval.Specifier.PERFECT, 8)]

    intervallist = [interval.DiatonicInterval(interval.Specifier.MAJOR, 2),
                interval.DiatonicInterval(interval.Specifier.MINOR, 3) ]

    # 7 Hepta scale - Triad degrees
    INT_ROMAN = {1:("I","i"), 2:('ii','ii0'), 3:('iii','III'), 4:('IV','iv'), 5:('V','V'), 6:('vi','VI'), 7: ('vii0','vii0')}


class PitchClassPattern:
    # Diatonic patterns: intervals, scales, modes, chords
    def __init__(self,
                 pitch_intervals : tuple = DiatonicLayer.HEPTATONIC):
        self.pitch_intervals = pitch_intervals

        # Scale modes and chord positions - permutations of interval sequence
        self.modes = sequence_permutations (self.pitch_intervals)
        # Pitch ring steps
        self.modeschromatic = [interval_to_step(self.modes[x]) for x in range(len(self.modes))]

        # Pitch ring masks for specific modes
        # Major
        self.majormodeschromatic = TwelveTET.CYCLES * self.modeschromatic [DiatonicLayer.MAJOR_MODE]
        # Minor
        self.minormodeschromatic = TwelveTET.CYCLES * self.modeschromatic [DiatonicLayer.MINOR_MODE]

        # Major pitch ring masks for all tonics (C, C#, D, ..., B)
        self.majorscales = [self.majormodeschromatic[-x:]+self.majormodeschromatic[:-x] for x in range(TwelveTET.OCTAVE) ]
        self.minorscales = [self.minormodeschromatic[-x:]+self.minormodeschromatic[:-x] for x in range(TwelveTET.OCTAVE) ]

        # Permutations: ordered set
        self.degree_permutations = list(itertools.permutations (range(1,len(pitch_intervals)) ) )


def main():
    time = MusicalTime()
    pr = PitchRing()
    pos = pr.index_of(3, 7)  # octave 3, pitchclass 7 -> index
    next_pos = pr.transpose(pos,pr.ASCENDING)  # next pitchclass
    octave_pitchclass = pr.get_at(next_pos)

    pcs = PitchClassSet()

    pcp3 = PitchClassPattern(DiatonicLayer.TRIAD[DiatonicLayer.MAJOR_CHORD])
    pcp5 = PitchClassPattern(DiatonicLayer.PENTATONIC)
    pcp7 = PitchClassPattern(DiatonicLayer.HEPTATONIC)

    # Table of all absolute chromatic data along pitch number set
    chromatic_data = pd.DataFrame([MIDIpitch.NUMBERS,
                                   pr.PITCHCLASSES_INT_FULL,
                                   pr.PITCHCLASSES_STR_FULL,
                                   pr.PITCHFREQUENCYLIST] + pcp7.majorscales,
                                  )
    chromatic_data.to_excel(Config.DEFAULT_PATH + 'ChromaticLayer.xlsx', index=True, sheet_name='Pitch')

    chromatic_table = chromatic_data.transpose()
    chromatic_table.columns = ['Nr', 'ClassNr', 'ClassChr', 'Freq'] + list(TwelveTET.STRINGS)
    chromatic_table.to_excel(Config.DEFAULT_PATH + 'ChromaticTable.xlsx', index=True, sheet_name='Pitch')

    arrHeptaScale = np.array(pcp7.majorscales)

    pc_circle = Circle(TwelveTET.OCTAVE, TwelveTET.STRINGS, 'Pitch class circle')
    pc_circle.show()

#    pc_circle.show(pcp7.majormodeschromatic, TwelveTET.STRINGS, 'Major circle')



if __name__ == '__main__':
    main()


