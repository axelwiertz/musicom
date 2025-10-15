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
    # Chromatic pitch octave ring
    ASCENDING = 1
    DESCENDING = -1
    def __init__(self):
        # Represent as list of (pitchclass, octave): (0, 4)
        self.ring = [(pitch_class, octave_idx)
                     for octave_idx in range(TwelveTET.CYCLES)
                     for pitch_class in range(TwelveTET.OCTAVE)]

        # Create pitch to frequency mapping
        keys = np.array([x + str(y) for y in range(TwelveTET.CYCLES) for x in TwelveTET.STRINGS])

        self.pitch_freqs = dict(zip(keys, [2 ** ((n + 1 - 49) / 12) * TwelveTET.FREQUENCY_A4 for n in range(len(keys))]))
        self.pitch_freqs[''] = 0.0  # stop
        self.pitch_freqs = tuple(2 ** ((n - MIDIpitch.A4) / TwelveTET.OCTAVE) * TwelveTET.FREQUENCY_A4
                                        for n in MIDIpitch.NUMBERS)


    def index_of(self, pitchclass, octave_idx):
        # Get index in pitch ring from (pitchclass, octave)
        return octave_idx * TwelveTET.CYCLES + pitchclass

    def get_at(self, i):
        # Get (pitchclass, octave) at index i in pitch ring
        return self.ring[i % len(self.ring)]

    def transpose(self, i, interval_steps, direction=ASCENDING):
        # Transpose index i by interval_steps in direction (ASCENDING or DESCENDING)
        return (i + direction*interval_steps) % len(self.ring)

    def length(self):
        # Length of pitch ring
        return len(self.ring)

    def indexes(self):
        return list(range(len(self.ring)))


class Patterns:
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

    DIMINISHED = 0
    MINOR = 1
    MAJOR = 2
    AUGMENTED = 3
    SUS2 = 4
    SUS4 = 5
    
    THIRD = 0
    FOURTH = 1
    FIFTH = 2

    # Interval patterns for scales and chords
    # pitch_intervals: tuple of interval steps, e.g. (2,2)
    pitch_intervals_dict = {
        DI: {
            THIRD: (3, 9),
            FOURTH: (6, 6),
            FIFTH: (7, 5)
        },
        TRIA:  {
            DIMINISHED: (3, 3, 6),
            MINOR: (3, 4, 5),
            MAJOR: (4, 3, 5),
            AUGMENTED: (4, 4, 4),
            SUS2: (2, 5, 5),
            SUS4: (5, 2, 5)
        },
        TETRA : {
            MINOR: (3, 4, 3, 2),
            MAJOR : (4, 3, 4, 1),
            AUGMENTED: (4, 4, 3, 1),
            SUS2: (2, 5, 4, 1),
            SUS4: (5, 2, 4, 1)
        },
        PENTA: (2, 2, 3, 2, 3),
        HEPTA: (2, 2, 1, 2, 2, 2, 1),
        DODECA: (1,1,1,1,1,1,1,1,1,1,1,1)
        }


class PitchIntervalPattern(PitchRing):
    def __init__(self,
                 pitch_intervals : tuple = None):
        super().__init__()

        self.pitch_intervals = pitch_intervals
        self.degrees = tuple(range(1, len(pitch_intervals) + 1))


        # Scale modes and chord positions - permutations of interval sequence
        self.modes = sequence_permutations (self.pitch_intervals)
        
        # Pitch ring steps
        self.modeschromatic = [interval_to_step(self.modes[x]) for x in range(len(self.modes))]

        # Permutations: ordered set
        self.degree_permutations = list(itertools.permutations (range(1,len(pitch_intervals)) ) )


class Triad (PitchIntervalPattern):
    # 3 Triad scale Patterns
    def __init__(self):
        # 3 Tria patterns:
        super().__init__(Patterns.pitch_intervals_dict[Patterns.TRIA][Patterns.MAJOR])


class TetraChord (PitchIntervalPattern):
    # 4 Tetra scale Patterns
    def __init__(self):
        # 4 Tetra patterns:
        super().__init__(Patterns.pitch_intervals_dict[Patterns.TETRA][Patterns.MAJOR])


class Pentatonic(PitchIntervalPattern):
    def __init__(self):
        # 4 Tetra patterns:
        super().__init__(Patterns.pitch_intervals_dict[Patterns.PENTA])

class Heptatonic(PitchIntervalPattern):
    # Heptatonic (7 pitch class) scale
    def __init__(self):
        # 4 Tetra patterns:
        super().__init__(Patterns.pitch_intervals_dict[Patterns.HEPTA])

        # Heptatonic modes:
        # 1. Ionian = Major 2. Dorian, 3. Phrygian, 4. Lydian, 5. Mixolydian, 6. Aeolian = Minor, 7. Locrian
        ionian = major_mode = 0
        dorian = 1
        phrygian = 2
        lydian = 3
        myxolydian = 4
        aeolian = minor_mode = 5
        locrian = 6
        modes = {
            ionian : 'Ionian',
            dorian : 'Dorian',
            phrygian : 'Phrygian',
            lydian : 'Lydian',
            myxolydian : 'Mixolydian',
            aeolian : 'Aeolian',
            locrian : 'Locrian' }
    
        # 7 Hepta scale degree functions
        functions = {1:'tonic', 2:'supertonic', 3:'mediant', 4:'subdominant', 5:'dominant', 6:'submediant', 7:'leading tone'}
        # 7 Hepta Interval classes
        perfectintervals = ('P1','P4','P5','P8')
        imperfectintervals = ('M2','m3','M3','m6','M6','m7','M7')
    
        perfectintervallist = [interval.DiatonicInterval(interval.Specifier.PERFECT, 1),
                    interval.DiatonicInterval(interval.Specifier.PERFECT, 4),
                    interval.DiatonicInterval(interval.Specifier.PERFECT, 5),
                    interval.DiatonicInterval(interval.Specifier.PERFECT, 8)]
    
        intervallist = [interval.DiatonicInterval(interval.Specifier.MAJOR, 2),
                    interval.DiatonicInterval(interval.Specifier.MINOR, 3) ]
    
        # 7 Hepta scale - Triad degrees
        triad_degrees = {1:("I","i"), 2:('ii','ii0'), 3:('iii','III'), 4:('IV','iv'), 5:('V','V'), 6:('vi','VI'), 7: ('vii0','vii0')}
    
    
        # Pitch rings for heptatonic modes
        # Major
        self.majormodeschromatic = TwelveTET.CYCLES * self.modeschromatic[major_mode]
        # Minor
        self.minormodeschromatic = TwelveTET.CYCLES * self.modeschromatic[minor_mode]
        
        # Major pitch rings for all tonics (C, C#, D, ..., B)
        self.majorscales = [self.majormodeschromatic[-x:] + self.majormodeschromatic[:-x] for x in range(TwelveTET.OCTAVE)]
        self.minorscales = [self.minormodeschromatic[-x:] + self.minormodeschromatic[:-x] for x in range(TwelveTET.OCTAVE)]


class Register(PitchRing):
    def __init__(self, pitchclass_start=TwelveTET.A, octave_start=0, pitchclass_end=TwelveTET.C, octave_end=8):
        super().__init__()  
        self.index_start = self.index_of(pitchclass_start, octave_start)
        self.index_end = self.index_of(pitchclass_end, octave_end) + 1
        self.register = self.ring[self.index_start:self.index_end]


class PitchClassSet:
    def __init__(self):

        # Combinations: of a set
        num_items = 3
        self.PITCHCLASS_COMBINATIONS = list(itertools.combinations (TwelveTET.INTEGERS, num_items))


def main():
    time = MusicalTime()
    pr = PitchRing()

    # Piano register from A0 to C8
    reg = Register(TwelveTET.A, 0, TwelveTET.C, 8)
    
    pos = pr.index_of(3, 7)  # octave 3, pitchclass 7 -> index
    next_pos = pr.transpose(pos,pr.ASCENDING)  # next pitchclass
    octave_pitchclass = pr.get_at(next_pos)

    pcs = PitchClassSet()

    triad = Triad()
    pcp5 = Pentatonic()
    pcp7 = Heptatonic()

    m21intervals = (interval.ChromaticInterval(n) for n in TwelveTET.INTEGERS)

    # Table of all absolute chromatic data along pitch number set
    chromatic_data = pd.DataFrame([idx for idx in pr.indexes() ]
                                    + pcp7.majorscales,
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


