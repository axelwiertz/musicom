"""
Music theory
"""
from library import *

# General modules
from math import pow, log2
import numpy as np
import pandas as pd
import itertools

# Music21 modules
from music21 import interval, meter, tempo, key, scale, note
# MusicPy modules
from musicpy import structures

class MusicalTime:
    # Rhythm and meter
    # Timestep is the smallest rhythm relative unit, represented as integer

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
    TWELVE = 12  # Number of pitch classes 0-11
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
    PITCH_CLASS_NUMBERS = (C, C_SHARP, D, D_SHARP, E, F, F_SHARP, G, G_SHARP, A, A_SHARP, B)
    CYCLES = 9  # Number of octaves in the pitch set

    PITCH_CLASS_NAMES_SHARP = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    PITCH_CLASS_NAMES_FLATMAP = {'D': 'C#', 'E': 'D#', 'G': 'F#', 'A': 'G#', 'B': 'A#', 'C': 'B', 'F': 'E'}

    CENTS : float = 100  # Cents in semitone

    def __init__(self, a4_freq=440.0, a4_midi=69):
        self.a4_freq = float(a4_freq)
        self.a4_midi = int(a4_midi)

    def midi_to_freq(self, midi):
        """Return frequency (Hz) for given MIDI note number (integer or float)."""
        return self.a4_freq * pow(2.0, (midi - self.a4_midi) / float(self.TWELVE))

    def freq_to_midi(self, freq):
        """Return MIDI note number (can be fractional) for a given frequency (Hz)."""
        return self.a4_midi + float(self.TWELVE) * log2(freq / self.a4_freq)

    def semitone_ratio(self, n=1):
        """Return frequency ratio for n semitones: 2^(n/12)."""
        return pow(2.0, n / float(self.TWELVE))

    def cents_between(self, f1, f2):
        """Return difference in cents from f1 to f2 (positive if f2 > f1)."""
        return float(self.TWELVE) * log2(f2 / f1)

    def interval_cents(self, semitones):
        """Return cents value for given semitone interval."""
        return semitones * self.CENTS

    def midi_to_name(self, midi):
        """Return note name (e.g., C4, A4) for integer MIDI. If non-integer, rounds to nearest."""
        m = int(round(midi))
        name = self.PITCH_CLASS_NAMES_SHARP[m % self.TWELVE]
        octave = (m // self.TWELVE) - 1
        return f"{name}{octave}"

    def name_to_midi(self, name):
        """Parse note name like 'C#4' or 'A4' to MIDI number. Accepts flats as 'Bb'."""
        s = name.strip()
        # handle optional accidental and octave
        base = s[0].upper()
        accidental = ''
        rest = s[1:]
        if rest and rest[0] in ('#', 'b'):
            accidental = rest[0]
            rest = rest[1:]
        octave = int(rest) if rest else 4
        idx = base
        if accidental == '#':
            idx += '#'
        elif accidental == 'b':
            # convert flat to equivalent sharp
            idx = self.PITCH_CLASS_NAMES_FLATMAP.get(base, base)
        semitone_index = self.PITCH_CLASS_NAMES_SHARP.index(idx)
        return (octave + 1) * self.TWELVE + semitone_index


class PitchHelix(TwelveTET):
    # Chromatic pitch helix
    ASCENDING = 1
    DESCENDING = -1
    def __init__(self):
        super().__init__()
        # Represent as list of (pitchclass, octave): (0, 4)
        self.ring = [(pitch_class, octave_idx)
                     for octave_idx in range(self.CYCLES)
                     for pitch_class in range(self.TWELVE)]

        # Create pitch to frequency mapping
        keys = np.array([x + str(y) for y in range(self.CYCLES) for x in self.PITCH_CLASS_NAMES_SHARP])

        self.pitch_freqs = dict(
                            zip(keys,
                                [2 ** ((n + 1 - 49) / 12) * self.a4_freq for n in range(len(keys))]
                                )
                            )
        self.pitch_freqs[''] = 0.0  # stop
        self.pitch_freqs = tuple(2 ** ((n - self.a4_midi) / self.TWELVE) * self.a4_freq
                                        for n in self.PITCH_CLASS_NUMBERS)


    @staticmethod
    def index_of(pitchclass, octave_idx):
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


    THIRD = 0
    FOURTH = 1
    FIFTH = 2

    SCALE = 0

    DIMINISHED = 0
    MINOR = 1
    MAJOR = 2
    AUGMENTED = 3
    SUS2 = 4
    SUS4 = 5

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


class PitchIntervalPattern(Patterns):
    def __init__(self,
                 pitch_intervals : tuple = None):
        super().__init__()

        self.pitch_intervals = pitch_intervals
        self.degrees = tuple(range(1, len(pitch_intervals) + 1))


        # Scale modes and chord positions - permutations of interval sequence
        self.modes = self.sequence_rotations (self.pitch_intervals)

        # Pitch ring steps
        self.modeschromatic = [interval_to_step(self.modes[x]) for x in range(len(self.modes))]

        # Permutations: ordered set
        self.degree_permutations = list(itertools.permutations (self.degrees ) )

    @staticmethod
    def sequence_rotations (sequence: list | tuple) -> list:
        rotations = [sequence[x:]+sequence[:x] for x in range(len(sequence))]
        return rotations

class MusicalScale(PitchIntervalPattern):
    def __init__(self,
                cardinality: int = None,
                pattern: int = None,
                 tonic : int = None,
                 mode : int = None):
        super().__init__(Patterns.pitch_intervals_dict[cardinality][pattern])
        self.tonic = tonic
        self.mode = mode

        # MusicPy structures
        self.mpscale = structures.scale(str(self.tonic), str(self.mode))

        # Music21 structures
        self.m21key = key.Key(note.Pitch(midi=tonic), mode=self.mode)
        self.m21scale = scale.ConcreteScale(key=self.m21key)


class Triad (MusicalScale):
    # 3 Triad scale Patterns
    def __init__(self):
        # 3 Tria patterns:
        super().__init__(Patterns.TRIA, Patterns.MAJOR)


class TetraChord (MusicalScale):
    # 4 Tetra scale Patterns
    def __init__(self):
        # 4 Tetra patterns:
        super().__init__(Patterns.TETRA, Patterns.MAJOR7)


class Pentatonic(MusicalScale):
    def __init__(self):
        # 5 Penta patterns:
        super().__init__(self.PENTA, self.SCALE)

class Heptatonic(MusicalScale):
    # Heptatonic (7 pitch class) scale
    # 7 Hepta scale modes:
    # 1. Ionian = Major 2. Dorian, 3. Phrygian, 4. Lydian, 5. Mixolydian, 6. Aeolian = Minor, 7. Locrian
    ionian = major_mode = 0
    dorian = 1
    phrygian = 2
    lydian = 3
    myxolydian = 4
    aeolian = minor_mode = 5
    locrian = 6

    # 7 Hepta scale degree functions
    degree_functions = {1: 'tonic', 2: 'supertonic', 3: 'mediant', 4: 'subdominant', 5: 'dominant', 6: 'submediant',
                        7: 'leading tone'}

    # 7 Hepta scale - Triad degrees
    triad_degrees = {1: ("I", "i"), 2: ('ii', 'ii0'), 3: ('iii', 'III'), 4: ('IV', 'iv'), 5: ('V', 'V'),
                     6: ('vi', 'VI'), 7: ('vii0', 'vii0')}

    def __init__(self):
        # 7 Hepta patterns:
        super().__init__(self.HEPTA, self.SCALE)

        # Pitch rings for heptatonic modes
        # Major
        self.majormodechromatic = TwelveTET.CYCLES * self.modeschromatic[self.major_mode]
        # Minor
        self.minormodechromatic = TwelveTET.CYCLES * self.modeschromatic[self.minor_mode]
        
        # Major pitch rings for all tonics (C, C#, D, ..., B)
        self.majorscales = [self.majormodechromatic[-x:] + self.majormodechromatic[:-x] for x in range(TwelveTET.TWELVE)]
        self.minorscales = [self.minormodechromatic[-x:] + self.minormodechromatic[:-x] for x in range(TwelveTET.TWELVE)]

class MusicalInterval:
    # Musical intervals
    def __init__(self, semitones=0):
        self.semitones = semitones
        self.cents = TwelveTET().interval_cents(semitones)

        # 7 Hepta Interval classes
        perfectintervals = ('P1', 'P4', 'P5', 'P8')
        imperfectintervals = ('M2', 'm3', 'M3', 'm6', 'M6', 'm7', 'M7')

        perfectintervallist = [interval.DiatonicInterval(interval.Specifier.PERFECT, 1),
                               interval.DiatonicInterval(interval.Specifier.PERFECT, 4),
                               interval.DiatonicInterval(interval.Specifier.PERFECT, 5),
                               interval.DiatonicInterval(interval.Specifier.PERFECT, 8)]

        intervallist = [interval.DiatonicInterval(interval.Specifier.MAJOR, 2),
                        interval.DiatonicInterval(interval.Specifier.MINOR, 3)]


class Register(PitchHelix):
    def __init__(self, pitchclass_start=TwelveTET.A, octave_start=0, pitchclass_end=TwelveTET.C, octave_end=8):
        super().__init__()  
        self.index_start = self.index_of(pitchclass_start, octave_start)
        self.index_end = self.index_of(pitchclass_end, octave_end) + 1
        self.register = self.ring[self.index_start:self.index_end]


class PitchClassSet:
    def __init__(self, num_items=3):

        # Combinations: and permutations of a set
        self.combinations = list(itertools.combinations (TwelveTET.PITCH_CLASS_NUMBERS, num_items))
        self.permutations = list(itertools.permutations (TwelveTET.PITCH_CLASS_NUMBERS, num_items))


def main():
    
    t = TwelveTET()
    print("A4 ->", t.midi_to_freq(69))
    print("C4 ->", t.midi_to_freq(t.name_to_midi("C4")))
    print("440 Hz -> MIDI", t.freq_to_midi(440.0))
    print("Cents between 440 and 466.16:", t.cents_between(440.0, 466.1637615180899))

    
    time = MusicalTime()
    pr = PitchHelix()

    # Piano register from A0 to C8
    reg = Register(t.A, 0, t.C, 8)
    
    pos = pr.index_of(3, 7)  # octave 3, pitchclass 7 -> index
    next_pos = pr.transpose(pos,pr.ASCENDING)  # next pitchclass
    octave_pitchclass = pr.get_at(next_pos)

    pcs = PitchClassSet()

    triad = Triad()
    pcp5 = Pentatonic()
    pcp7 = Heptatonic()

    m21intervals = list(interval.ChromaticInterval(n) for n in TwelveTET.PITCH_CLASS_NUMBERS)

    # Table of all absolute chromatic data along pitch number set
    chromatic_data = pd.DataFrame(pcp7.majorscales)
    chromatic_data.to_excel(Config.DEFAULT_PATH + 'ChromaticLayer.xlsx', index=True, sheet_name='Pitch')

    chromatic_table = chromatic_data.transpose()
    #chromatic_table.columns = ['Nr', 'ClassNr', 'ClassChr', 'Freq'] + list(TwelveTET.PITCH_CLASS_NAMES_SHARP)
    chromatic_table.to_excel(Config.DEFAULT_PATH + 'ChromaticTable.xlsx', index=True, sheet_name='Pitch')

    hepta_major_arr = np.array(pcp7.majorscales)

    pc_circle = Circle(TwelveTET.TWELVE, TwelveTET.PITCH_CLASS_NAMES_SHARP, 'Pitch class circle')
    pc_circle.show()

#    pc_circle.show(pcp7.majormodeschromatic, TwelveTET.PITCH_CLASS_NAMES_SHARP, 'Major circle')



if __name__ == '__main__':
    main()


