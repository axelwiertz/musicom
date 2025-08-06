"""
Music library
"""

# Import
import numpy as np
import pandas as pd
import itertools
import matplotlib.pyplot as plt

# Music21 modules
from music21 import stream, note, key, scale, chord, interval, roman, converter, instrument, serial, harmony
from music21 import meter, tempo, metadata


def interval_to_binary (intervals):
    # Convert a list of intervals to a binary mask with sequential degree numbers
    # Example [2, 3] -> [1, 0, 2, 0, 0, 3]
    binary_with_degrees = []
    degree = 1
    for x in intervals:
        binary_with_degrees.append(degree)
        degree += 1
        for y in range(1,x):
            binary_with_degrees.append(0)
    return binary_with_degrees


'''
Music library - Absolute data: frequency, pitch(class), octave
'''

# Diatonic pitch set, equal temperament scale
FREQUENCY_A4 = 440 # Frequency of A4
MIDIPITCHNUM_A4 = 69 # MIDI number of A4
OCTAVES = 9 # Number of octaves in the pitch set

NUMDIATONICPITCHCLASS = 12 # Number of pitch classes 0-11
# Total number of pitches diatonic pitch set
NUMPITCH = OCTAVES * NUMDIATONICPITCHCLASS
PITCHMIDINUMBERLIST = tuple(range(NUMPITCH)) # Pitch number set


PITCHCLASSNUMBERS = tuple(range (NUMDIATONICPITCHCLASS)) # Pitch class number
PITCHCLASSTEXTS = ('C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B') # Pitch class characters
chromaticRow = serial.TwelveToneRow(PITCHCLASSNUMBERS)
matrixObj = chromaticRow.matrix()

#srsPitchNr = pd.Series (range (NUMPITCH))
# Pitch class
PITCHCLASSTEXTLIST = ([x for y in range(0, OCTAVES) for x in PITCHCLASSTEXTS])
PITCHCLASSNUMBERLIST = (OCTAVES * PITCHCLASSNUMBERS)
PITCHFREQUENCYLIST = tuple(2 ** ((n - MIDIPITCHNUM_A4) / NUMDIATONICPITCHCLASS) * FREQUENCY_A4 for n in range(NUMPITCH)) # Pitch frequencies

# Table of all absolute diatonic data along pitch number set
dfPitch = pd.DataFrame ([PITCHMIDINUMBERLIST, PITCHCLASSNUMBERLIST, PITCHCLASSTEXTLIST, PITCHFREQUENCYLIST]).transpose()
dfPitch.columns=['Nr','ClassNr','ClassChr', 'Freq']


"""
Music library - Pitch ranges of instruments
"""
instr1 = instrument.Piano
instr2 = instrument.Guitar
instr3 = instrument.Ukulele
instrPerc = instrument.Percussion


dctRangeInstr = {
    'Piano': ('A0','C8'), # Piano keyboard
    'Guitar': ('E2','D6'), # Acoustic guitar with standard tuning
    'Ukelele': ('C4', 'C6') # Ukelele
}



"""
Music library - Interval classes
"""
interval01 = interval.ChromaticInterval()

# Diatonic Interval classes
PERFECTINTERVALS = ('P1', 'P4', 'P5', 'P8')
IMPERFECTINTERVALS = ('M2', 'm3', 'M3', 'm6', 'M6', 'm7', 'M7')

interval02 = interval.Interval()

# Check if an interval is perfect
def is_perfect_interval(interval_in: interval.Interval):
    return interval_in.name in PERFECTINTERVALS


'''
Music library - Diatonic chord patterns: triads and sevenths
'''
chord1 = chord.Chord()

h = harmony.ChordSymbol('Dsus4')
h.romanNumeral = 'III'
h.romanNumeral.key = key.Key('B')
h.romanNumeral = roman.RomanNumeral('IV', 'A' )

TRIAD = 3 # Number of pitch classes in a triad
# Patterns: diminished, major, minor, augmented
dctIntervalPattern = {
    'd': (3, 3, 6),
    'M': (4, 3, 5),
    'm': (3, 4, 5),
    'A': (4, 4, 4)
}
intervalsPattern = dctIntervalPattern['M']


# inversions
lstScaleInterval = tuple(intervalsPattern[x:]+intervalsPattern[:x] for x in range(TRIAD) )
# Binary patterns
lstScaleBinary = [interval_to_binary(lstScaleInterval[x]) for x in range(len(lstScaleInterval))] 


"""
Music library - Diatonic scale patterns: pentatonic and heptatonic
"""
# Pentatonic (5 pitch class) scale
PENTA = 5 # Number of pitch classes in a pentatonic scale
lstIntPentaDegree = tuple(range(1, PENTA + 1)) # Pentatonic scale degree number
lstPentaScaleIntervalPattern = (2,2,3,2,3) # Pentatonic interval pattern
lstPentaScaleInterval = tuple(lstPentaScaleIntervalPattern[x:]+lstPentaScaleIntervalPattern[:x] for x in range(PENTA) )
lstPentaScaleBinary = [interval_to_binary(lstPentaScaleInterval[x]) for x in range(len(lstPentaScaleInterval))] # Heptatonic binary patterns

# Heptatonic (7 pitch class) scale
scale01 = scale.Scale()
HEPTA = 7 # Number of pitch classes in a heptatonic scale
lstIntHeptaDegree = tuple(range(1, HEPTA + 1)) # Heptatonic scale degree number
lstHeptaScaleIntervalPattern = (2,2,1,2,2,2,1) # Heptatonic interval pattern
# Modes
lstHeptaScaleInterval = tuple(lstHeptaScaleIntervalPattern[x:]+lstHeptaScaleIntervalPattern[:x] for x in range(HEPTA) )
lstHeptaScaleBinary = [interval_to_binary(lstHeptaScaleInterval[x]) for x in range(len(lstHeptaScaleInterval))] # Heptatonic binary patterns

# Scale pitch mask
# Major
lstScale = OCTAVES * lstHeptaScaleBinary [0] # C scale pitch mask
# Minor
lstScale1 = OCTAVES * lstHeptaScaleBinary [5] # a scale pitch mask

lstHeptaScale = [lstScale[-x:]+lstScale[:-x] for x in range(NUMDIATONICPITCHCLASS) ] # All major scale pitch mask
arrHeptaScale = np.array(lstHeptaScale)


"""
Music library - Chords in scales
"""
# Chord patterns in scale degrees
lstChordDegreePattern = (1,3,5,7,2,4,6) #Heptatonic

lstHeptaScaleChord = [lstChordDegreePattern[x:]+lstChordDegreePattern[:x] for x in range(HEPTA) ]
lstHeptaScaleChord.sort()
lstHeptaScaleChordDegreeIntervalPattern = [2,2,2,2,2,2,2] #Heptatonic

# Permutations: ordered set
lstPermChordDegreePattern = list(itertools.permutations (lstIntHeptaDegree))
# Combinations
lstCombChordDegreePattern = list(itertools.combinations (lstIntHeptaDegree, 3))





"""
Visualization
"""

# To do: Rhythm circle


def pitch_class_circle():
    # Show pitch classes in circle

    # Convert pitch class numbers to angles
    angles = np.linspace(0, 2 * np.pi, NUMDIATONICPITCHCLASS, endpoint=False)

    # Create a figure and axis
    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})

    # Plot the pitch class numbers
    for angle, pitch in zip(angles, PITCHCLASSNUMBERS):
        ax.plot(angle, 1, 'o', markersize=10)
        ax.text(angle, 1.1, str(pitch), ha='center', va='center')

    # Set the title
    ax.set_title('Circle of Pitch Class Numbers')

    # Show the plot
    plt.show()


"""
Rhythm of beats and rests with durations in a measure
"""
BEAT_REST = 0
DURATION = 1
BT = 'b'
RS = 'r'

QUARTER = 0.25

"""
Rhythm library
"""
# Four-beat rhythm
four_rhythmic_pattern = converter.parse('tinynotation: 4/4 c5 c5 c5 c5')
FOUR_RHYTHM = [    [BT, BT, BT, BT],
                [1.0, 1.0, 1.0, 1.0]  ]
# Tresillo rhythm
tresillo_rhythmic_pattern = converter.parse('tinynotation: 4/4 c5 r r c5 r r c5 r')
tresillo_rtm = [[BT, RS, RS, BT, BT, RS, RS, BT, RS],
                [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5 ] ]
# 12/8 Bell rhythm
twelve_8_bell_rhythmic_pattern = converter.parse('tinynotation: 12/8 c5 r c5 r c5 c5 r c5 r c5 r c5')
twelve_8_bell_rtm = [   [BT, RS, BT, RS, BT, BT, RS, BT, RS, BT, RS, BT],
                        [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5 ] ]
# Son Clave
sonclave_rhythmic_pattern = converter.parse('tinynotation: 16/8 c5 r r c5 r r c5 r r r c5 r c5 r r r')
sonclave_rtm = [    [BT, RS, RS, BT, RS, RS, BT, RS, RS, RS, BT, RS, BT, RS, RS, RS],
                    [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5 ] ]


# 3/4 Waltz
waltz_rhythmic_pattern = converter.parse('tinynotation: 3/4 c5 c5 c5')
three_rtm = [   [BT, BT, BT],
                [1.0, 1.0, 1.0] ]

"""
Tools
"""

def part_create_from_stream (stream_in: stream.Stream)\
        -> stream.Part:
    # Transfer notes and rests from the original stream to a new Part
    part_out = stream.Part()
    for note_or_rest in stream_in.notesAndRests:
        part_out.append(note_or_rest)

    return part_out

# Plot
# Note that even in the OO-style, we use `.pyplot.figure` to create the Figure.
#fig, ax = plt.subplots(figsize=(5, 2.7), layout='constrained')
#ax.plot(srsPitchFreq.values, label='pitch frequency') # Plot some data on the Axes.
#ax.set_xlabel('Pitch number')  # Add an x-label to the Axes.
#ax.set_ylabel('Frequency')  # Add a y-label to the Axes.
#ax.set_title("Pitches")  # Add a title to the Axes.
#ax.legend()  # Add a legend.
#plt.show()



