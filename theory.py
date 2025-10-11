"""
Music theory
"""
from library import Config, Circle, MCMIDI

# General modules
import numpy as np
import pandas as pd
import itertools

from soundlayer import SoundLayer

# Music21 modules
from music21 import (stream, note, key, scale, chord, interval,
                     roman, converter, instrument, serial, harmony,
                     meter, tempo, metadata, clef, percussion, analysis)
# mp
from musicpy import database


def interval_to_step (intervals: list[int]) -> list[int]:
    # Convert a list of intervals to a sequential mask with sequential degree/onset numbers and zeroes
    # Example [2, 3] -> [1, 0, 2, 0, 0, 3]
    steps = []
    degree = 1
    for x in intervals:
        steps.append(degree)
        degree += 1
        for y in range(1,x):
            steps.append(0)
    return steps

def sequence_permutations (sequence: list | tuple) -> list:
    permutations = [sequence[x:]+sequence[:x] for x in range(len(sequence))]
    return permutations

class ChromaticLayer:
    """
    Chromatic pitch set and intervals
    equal temperament scale
    """
    OCTAVES = 9 # Number of octaves in the pitch set
    NUMPITCHCLASS = 12 # Number of pitch classes 0-11
    # Total number of pitches chromatic pitch set
    NUMPITCH = OCTAVES * NUMPITCHCLASS
    # Pitch MIDI number set
    PITCHMIDINUMBERLIST = tuple(range(NUMPITCH))
    # Chromatic pitch class sets
    # One octave
    PITCHCLASSES_INT = tuple(range (NUMPITCHCLASS))
    PITCHCLASSES_STR = ('C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B')

    PITCHCLASSES_STR_FULL = ()
    PITCHCLASSES_INT_FULL = ()
    PITCHFREQUENCYLIST = ()
    INTERVALLIST = ()

    PITCHCLASS_COMBINATIONS = []

    def __init__(self):
        soundlayer = SoundLayer()
        # Multiple octaves
        self.PITCHCLASSES_STR_FULL = tuple(x for _ in range(0, self.OCTAVES) for x in self.PITCHCLASSES_STR)
        self.PITCHCLASSES_INT_FULL = tuple(self.OCTAVES * self.PITCHCLASSES_INT)
        self.PITCHFREQUENCYLIST = tuple(2 ** ((n - MCMIDI.MIDI_PITCH_A4) / self.NUMPITCHCLASS) * soundlayer.FREQUENCY_A4
                                        for n in range(self.NUMPITCH))
        self.INTERVALLIST = (interval.ChromaticInterval(n) for n in range(self.NUMPITCHCLASS))

    def init_sets(self):
        # Combinations: of a set
        num_items = 3
        self.PITCHCLASS_COMBINATIONS = list(itertools.combinations (ChromaticLayer.PITCHCLASSES_INT, num_items))

class MCTime:
    """
    Rhythm and meter
    """
    # Defaults
    DEFAULT_TEMPO = 100
    DEFAULT_TIMESIGNATURE = meter.TimeSignature('4/4')

    # Meter unit is quarter note
    QUARTER = 4

    DEFAULT_DURATION = note.Duration(QUARTER/4)
    DEFAULT_DURATIONS = [[note.Duration(d)] for d in [QUARTER/8, QUARTER/4, QUARTER/2]]

    # Rhythm - onset time intervals

    # Four-beat rhythm
    four_rhythmic_pattern = converter.parse('tinynotation: 4/4 c5 c5 c5 c5')
    FOUR_RHYTHM =  (1, 1, 1, 1)
    # Tresillo rhythm
    tresillo_rhythmic_pattern = converter.parse('tinynotation: 4/4 c5 r r c5 r r c5 r')
    TRESILLO_RTM = (3, 3, 2)
    # 12/8 Bell rhythm
    twelve_eigth_bell_rhythmic_pattern = converter.parse('tinynotation: 12/8 c5 r c5 r c5 c5 r c5 r c5 r c5')
    TWELVE_EIGTH_BELL_RHYTHM = (2, 2, 1, 2, 2, 2, 1)
    # Son Clave
    son_clave_rhythmic_pattern = converter.parse('tinynotation: 16/8 c5 r r c5 r r c5 r r r c5 r c5 r r r')
    SON_CLAVE_RHYTHM = (3, 3, 4, 2, 4)
    # 3/4 Waltz
    waltz_rhythmic_pattern = converter.parse('tinynotation: 3/4 c5 c5 c5')
    three_rtm = (1, 1, 1)


class DiatonicLayer:
    """
    Diatonic scale - Notes, intervals and functions
    """
    PENTATONIC = (2,2,3,2,3) # sequence of 5 intervalsteps
    HEPTATONIC = (2,2,1,2,2,2,1) # sequence of 7 intervalsteps
"""
2 — di / dy- (e.g., dioxide, dynamo)
3 — tri / tria- (triangle, tricycle)
4 — tetra- (tetrahedron, tetrapod)
5 — penta- (pentagon, pentathlon)
6 — hexa- (hexagon, hexapod)
7 — hepta- (heptagon, heptathlon)
"""
	# 7 Hepta 
    # Melody scale degree functions
    FUNCTIONS = {1:'tonic', 2:'supertonic', 3:'mediant', 4:'subdominant', 5:'dominant', 6:'submediant', 7:'leading tone'}
    # Diatonic Interval classes
    PERFECTINTERVALS = ('P1','P4','P5','P8')
    IMPERFECTINTERVALS = ('M2','m3','M3','m6','M6','m7','M7')

    perfectintervallist = [interval.DiatonicInterval(interval.Specifier.PERFECT, 1),
                interval.DiatonicInterval(interval.Specifier.PERFECT, 4),
                interval.DiatonicInterval(interval.Specifier.PERFECT, 5),
                interval.DiatonicInterval(interval.Specifier.PERFECT, 8)]

    intervallist = [interval.DiatonicInterval(interval.Specifier.MAJOR, 2),
                interval.DiatonicInterval(interval.Specifier.MINOR, 3) ]

    # 7 Hepta scale - 3 Tria and 4 TetraChord degrees
    INT_ROMAN = {1:("I","i"), 2:('ii','ii0'), 3:('iii','III'), 4:('IV','iv'), 5:('V','V'), 6:('vi','VI'), 7: ('vii0','vii0')}

    """
    Diatonic cyclic patterns: pentatonic and heptatonic
    """
    PENTA = 5 # Number of pitch classes in a pentatonic scale
    PENTATONICDEGREES = tuple(range(1, PENTA + 1)) # Pentatonic scale degree number

    HEPTA = 7 # Number of pitch classes in a heptatonic scale
    HEPTATONICDEGREES = tuple(range(1, HEPTA + 1)) # Heptatonic scale degree number


    # Pentatonic (5 pitch class) scale
    PENTAMODES = []
    PENTAMODESCHROMATIC = []

    # Heptatonic (7 pitch class) scale
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

    """
    Interval patterns - Chord interval patterns and permutations
    n pitch classes = root (key) + n+1 interval classes (scale)
    """
    NUMTRIADINTERVALS = 2 # Number intervals to compose a triad
    SEVENTH = 3 # Number of intervals to compose a seventh
    # Patterns:
    DIMINISHED_CHORD = 0
    MINOR_CHORD = 1
    MAJOR_CHORD = 2
    AUGMENTED_CHORD = 3
    SUS2_CHORD = 4
    SUS4_CHORD = 5
    CHORDINTERVALS = {
        DIMINISHED_CHORD : (3, 3, 6),
        MINOR_CHORD: (3, 4, 5),
        MAJOR_CHORD : (4, 3, 5),
        AUGMENTED_CHORD: (4, 4, 4),
        SUS2_CHORD: (2, 5, 5),
        SUS4_CHORD: (5, 2, 5)
    }

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
        positions = sequence_permutations(self.CHORDINTERVALS[self.MAJOR_CHORD])
        # Chromatic steps
        positions_chromatic_steps = [interval_to_step(positions[x]) for x in range(len(positions))]


    def init_sets(self):
        # Permutations: ordered set
        degree_permutations = list(itertools.permutations (self.HEPTATONICDEGREES))


    def save_library_sheet(self):

        # Table of all absolute chromatic data along pitch number set
        chromatic_data = pd.DataFrame ([ChromaticLayer.PITCHMIDINUMBERLIST,
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


