"""
Music theory
"""
from library import *

# General modules
import numpy as np
import pandas as pd
import itertools

# Music21 modules
from music21 import note, key, scale, interval, meter, tempo
# mp
from musicpy import database

class ChromaticLayer:
    """
    Chromatic pitch set and intervals
    equal temperament scale
    """
    OCTAVES = 9 # Number of octaves in the pitch set
    NUMPITCHCLASS = 12 # Number of pitch classes 0-11
    # Pitch class sets
    PITCHCLASSES_INT = tuple(range (NUMPITCHCLASS))
    PITCHCLASSES_STR = ('C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B')
    # Total number of pitches chromatic pitch set
    NUMPITCH = OCTAVES * NUMPITCHCLASS
    # Pitch MIDI number set
    MIDIPITCHNUMBERS = tuple(range(NUMPITCH))

    PITCHCLASSES_STR_FULL = ()
    PITCHCLASSES_INT_FULL = ()
    PITCHFREQUENCYLIST = ()
    INTERVALLIST = ()

    PITCHCLASS_COMBINATIONS = []

    def __init__(self):
        self.FREQUENCY_A4 = 440  # Frequency of A4
        self.MIDI_PITCH_A4 = 69


        # Create pitch to frequency mapping
        # Chromatic layer - 12-TET
        keys = np.array([x + str(y) for y in range(0, 9) for x in self.PITCHCLASSES_STR])
        # Trim to standard 88 pianokeys
        start = np.where(keys == 'A0')[0][0]
        end = np.where(keys == 'C8')[0][0]
        keys = keys[start:end + 1]

        self.pitch_freqs = dict(zip(keys, [2 ** ((n + 1 - 49) / 12) * self.FREQUENCY_A4 for n in range(len(keys))]))
        self.pitch_freqs[''] = 0.0  # stop

        self.PITCHFREQUENCYLIST = tuple(2 ** ((n - self.MIDI_PITCH_A4) / self.NUMPITCHCLASS) * self.FREQUENCY_A4
                                        for n in self.MIDIPITCHNUMBERS)


        # Multiple octaves
        self.PITCHCLASSES_STR_FULL = tuple(x for _ in range(0, self.OCTAVES) for x in self.PITCHCLASSES_STR)
        self.PITCHCLASSES_INT_FULL = tuple(self.OCTAVES * self.PITCHCLASSES_INT)
        self.INTERVALLIST = (interval.ChromaticInterval(n) for n in range(self.NUMPITCHCLASS))

    def init_sets(self):
        # Combinations: of a set
        num_items = 3
        self.PITCHCLASS_COMBINATIONS = list(itertools.combinations (ChromaticLayer.PITCHCLASSES_INT, num_items))

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
        main_beatcount = self.timesignature.beatCount
        self.beat_duration = self.M21_QUARTER / self.beat_note
        beat_duration2 = self.timesignature.beatDuration.quarterLength


class DiatonicLayer:
    """
    Diatonic patterns: intervals, scales, modes, chords
    """
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



    HEPTAMAJORSCALES = [] # Major scale pitch masks for all tonics (C, C#, D, ..., B)
    HEPTAMINORSCALES = [] # Minor scale pitch masks for all tonics

    DEFAULT_KEY = None
    DEFAULT_SCALE = None
    DEFAULT_PITCHES = []
    DEFAULT_PITCH = None
    DEFAULT_NOTE = None

    def __init__(self):
        self.DEFAULT_KEY = key.Key('C', 'major')
        self.DEFAULT_SCALE = scale.MajorScale('C')
        self.DEFAULT_PITCHES = self.DEFAULT_SCALE.pitches
        self.DEFAULT_PITCH = self.DEFAULT_PITCHES [0]
        self.DEFAULT_NOTE = note.Note(self.DEFAULT_PITCH,duration=MCTime.DEFAULT_DURATION)

        # Pentatonic (5 pitch class) scale
        self.PENTAMODES = sequence_permutations (self.PENTATONIC)
        self.PENTAMODESCHROMATIC = [interval_to_step(self.PENTAMODES[x]) for x in range(len(self.PENTAMODES))]

        # Heptatonic (7 pitch class) scale
        self.HEPTAMODES = sequence_permutations (self.HEPTATONIC)
        self.HEPTAMODESCHROMATIC = [interval_to_step(self.HEPTAMODES[x]) for x in range(len(self.HEPTAMODES))]


        # Major
        self.HEPTAMAJORMODESCHROMATIC = ChromaticLayer.OCTAVES * self.HEPTAMODESCHROMATIC [self.MAJOR_MODE]
        # Minor
        self.HEPTAMINORMODESCHROMATIC = ChromaticLayer.OCTAVES * self.HEPTAMODESCHROMATIC [self.MINOR_MODE]

        # Major scale pitch masks for all tonics (C, C#, D, ..., B)
        self.HEPTAMAJORSCALES = [self.HEPTAMAJORMODESCHROMATIC[-x:]+self.HEPTAMAJORMODESCHROMATIC[:-x] for x in range(ChromaticLayer.NUMPITCHCLASS) ]
        self.HEPTAMINORSCALES = [self.HEPTAMINORMODESCHROMATIC[-x:]+self.HEPTAMINORMODESCHROMATIC[:-x] for x in range(ChromaticLayer.NUMPITCHCLASS) ]

        # chord positions - permutations of intervals
        positions = sequence_permutations(self.TRIAD[self.MAJOR_CHORD])
        # Chromatic steps
        positions_chromatic_steps = [interval_to_step(positions[x]) for x in range(len(positions))]


    def init_sets(self):
        # Permutations: ordered set
        degree_permutations = list(itertools.permutations (self.HEPTATONICDEGREES))


    def save_library_sheet(self):

        # Table of all absolute chromatic data along pitch number set
        chromatic_data = pd.DataFrame ([ChromaticLayer.MIDIPITCHNUMBERS,
                             ChromaticLayer.PITCHCLASSES_INT_FULL,
                             ChromaticLayer.PITCHCLASSES_STR_FULL,
                             ChromaticLayer.PITCHFREQUENCYLIST]+ self.HEPTAMAJORSCALES,
                                  )
        chromatic_data.to_excel(Config.DEFAULT_PATH+'ChromaticLayer.xlsx', index=True, sheet_name='Pitch')

        chromatic_table = chromatic_data.transpose()
        chromatic_table.columns=['Nr','ClassNr','ClassChr', 'Freq'] + list(ChromaticLayer.PITCHCLASSES_STR)
        chromatic_table.to_excel(Config.DEFAULT_PATH+'ChromaticTable.xlsx', index=True, sheet_name='Pitch')

        arrHeptaScale = np.array(self.HEPTAMAJORSCALES)

def main():
    c = ChromaticLayer()
    d = DiatonicLayer()
    m = MCTime()

    d.save_library_sheet ()

    pc_circle = Circle(c.NUMPITCHCLASS, c.PITCHCLASSES_STR, 'Pitch class circle')
    pc_circle.show()

#    pc_circle.show(d.HEPTAMODESCHROMATIC[d.MAJOR_MODE], c.PITCHCLASSES_STR, 'Major circle')



if __name__ == '__main__':
    main()


