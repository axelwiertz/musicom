"""
Music library
"""

# Import
import numpy as np
import pandas as pd
import itertools
import matplotlib.pyplot as plt

# Music21 modules
from music21 import (stream, note, key, scale, chord, interval,
                     roman, converter, instrument, serial, harmony,
                     meter, tempo, metadata, percussion, analysis)
from music21.common import pitchList


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
Music library - Chromatic data: frequency, pitch(class), octave
'''

# Chromatic pitch set, equal temperament scale
FREQUENCY_A4 = 440 # Frequency of A4
MIDIPITCHNUM_A4 = 69 # MIDI number of A4
OCTAVES = 9 # Number of octaves in the pitch set

NUMCHROMATICPITCHCLASS = 12 # Number of pitch classes 0-11
# Total number of pitches diatonic pitch set
NUMPITCH = OCTAVES * NUMCHROMATICPITCHCLASS
PITCHMIDINUMBERLIST = tuple(range(NUMPITCH)) # Pitch number set


CHROMATICPITCHCLASSNUMBERS = tuple(range (NUMCHROMATICPITCHCLASS)) # Pitch class numbers
CHROMATICPITCHCLASSTEXTS = ('C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B') # Pitch class characters


# Pitch class
CHROMATICPITCHCLASSTEXTLIST = ([x for y in range(0, OCTAVES) for x in CHROMATICPITCHCLASSTEXTS])
CHROMATICPITCHCLASSNUMBERLIST = (OCTAVES * CHROMATICPITCHCLASSNUMBERS)
CHROMATICPITCHFREQUENCYLIST = tuple(2 ** ((n - MIDIPITCHNUM_A4) / NUMCHROMATICPITCHCLASS) * FREQUENCY_A4
                                    for n in range(NUMPITCH)) # Pitch frequencies

# Table of all absolute chromatic data along pitch number set
dfPitch = pd.DataFrame ([PITCHMIDINUMBERLIST,
                         CHROMATICPITCHCLASSNUMBERLIST,
                         CHROMATICPITCHCLASSTEXTLIST,
                         CHROMATICPITCHFREQUENCYLIST]).transpose()
dfPitch.columns=['Nr','ClassNr','ClassChr', 'Freq']


"""
Music library - Pitch ranges of instruments
"""
instr1 = instrument.Piano
instr2 = instrument.Guitar
instr3 = instrument.Ukulele
instrPerc = instrument.Percussion


"""
Music library - Diatonic interval classes
"""

# Diatonic Interval classes
perfectintervallist = [interval.DiatonicInterval(interval.Specifier.PERFECT, 1),
                interval.DiatonicInterval(interval.Specifier.PERFECT, 4),
                interval.DiatonicInterval(interval.Specifier.PERFECT, 5),
                interval.DiatonicInterval(interval.Specifier.PERFECT, 8)]
PERFECTINTERVALS = ('P1', 'P4', 'P5', 'P8')

intervallist = [interval.DiatonicInterval(interval.Specifier.MAJOR, 2),
                interval.DiatonicInterval(interval.Specifier.MINOR, 3)
                ]
IMPERFECTINTERVALS = ('M2', 'm3', 'M3', 'm6', 'M6', 'm7', 'M7')



'''
Music library - Interval patterns: diatonic triads and sevenths
'''
chromaticintervallist = [interval.ChromaticInterval(n) for n in range(NUMCHROMATICPITCHCLASS)]

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
Interval patterns - Diatonic cyclic patterns: pentatonic and heptatonic
"""
# Pentatonic
PENTA = 5 # Number of pitch classes in a pentatonic scale
lstIntPentaDegree = tuple(range(1, PENTA + 1)) # Pentatonic scale degree number
lstPentaScaleIntervalPattern = (2,2,3,2,3) # Pentatonic interval pattern
lstPentaScaleInterval = tuple(lstPentaScaleIntervalPattern[x:]+lstPentaScaleIntervalPattern[:x] for x in range(PENTA) )
lstPentaScaleBinary = [interval_to_binary(lstPentaScaleInterval[x]) for x in range(len(lstPentaScaleInterval))] # Heptatonic binary patterns

# Heptatonic (7 pitch class) scale
scale01 = scale.ConcreteScale()
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

lstHeptaScale = [lstScale[-x:]+lstScale[:-x] for x in range(NUMCHROMATICPITCHCLASS) ] # All major scale pitch mask
arrHeptaScale = np.array(lstHeptaScale)

# Permutations: ordered set
itemlist = lstIntHeptaDegree
lstPermutations = list(itertools.permutations (itemlist))
# Combinations: of a set
itemlist = CHROMATICPITCHCLASSNUMBERS
num_items = 3
lstCombinations = list(itertools.combinations (itemlist, num_items))

"""
Scale level - Harmonic function and progression of chords in scales
"""
# Chord patterns in heptatonic scale degrees
scaledegreepattern = (1,3,5,7,2,4,6) #Heptatonic
lstHeptaScaleChord = [scaledegreepattern[x:]+scaledegreepattern[:x] for x in range(HEPTA) ]
lstHeptaScaleChord.sort()
TONIC = 0
DOMINANT = 1
SUBDOMINANT = 2
TONICPROLONG = 3
harmonicchordfunctions = {[TONIC, (1)],
                     DOMINANT, (7,5),
                     SUBDOMINANT, (4,2),
                     TONICPROLONG, (3,6)}
POPROCKCHORD = '7-' # substitues 7 and has DOM, SUBDOM and PROLON functions

harmonicchordprogressions =\
    {[TONIC, TONICPROLONG],
    [TONIC, DOMINANT],
    [TONIC, SUBDOMINANT],
    [DOMINANT, TONIC],
    [SUBDOMINANT, DOMINANT]}
# not becessary
#lstHeptaScaleChordDegreeIntervalPattern = [2,2,2,2,2,2,2] #Heptaton





"""
Visualization
"""

# To do: Rhythm circle


def show_circle(num_parts: int = 12, labels : list = CHROMATICPITCHCLASSTEXTS, title : str = 'Circle of parts and values' ):
    # Show parts (angles) and labels in circle

    # Convert parts to angles
    angles = np.linspace(0, 2 * np.pi, num_parts, endpoint=False)

    # Create a figure and axis
    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})

    # Plot the labels
    for angle, label in zip(angles, labels):
        ax.plot(angle, 1, 'o', markersize=10)
        ax.text(angle, 1.1, str(label), ha='center', va='center')

    # Set the title
    ax.set_title(title)

    # Show the plot
    plt.show()

def show_plot(yvalues: list):
    # Plot
    # Note that even in the OO-style, we use `.pyplot.figure` to create the Figure.
    fig, ax = plt.subplots(figsize=(5, 2.7), layout='constrained')
    ax.plot(yvalues, label='pitch frequency') # Plot some data on the Axes.
    ax.set_xlabel('Pitch number')  # Add an x-label to the Axes.
    ax.set_ylabel('Frequency')  # Add a y-label to the Axes.
    ax.set_title("Pitches")  # Add a title to the Axes.
    ax.legend()  # Add a legend.
    plt.show()



"""
Rhythm of beats and rests with durations in a measure
"""
BEAT_REST = 0
DURATION = 1
BT = 'b'
RS = 'r'


"""
Absolute rhythm library
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
Rhythm intervals
"""



"""
Music 21 Tools for streams
"""

def part_create_from_stream (stream_in: stream.Stream,
                             instr: instrument.Instrument = instrument.Piano()) -> stream.Part:
    # Transfer notes and rests from the original stream to a new Part
    part_out = stream.Part()
    # Add instrument of part
    part_out.insert(0, instr)

    for note_or_rest in stream_in.notesAndRests:
        part_out.append(note_or_rest)

    return part_out


def part_create(pitches : list[str],
                durations : list[float],
                instr: instrument.Instrument = instrument.Piano()
                ) -> stream.Part:
    # Create a part with notes and rests
    part_out = stream.Part()
    # Add instrument of part
    part_out.insert(0, instr)

    # Iterate over the list of pitches
    for i in range(len(pitches)) :
        # Add beats and rests to the stream
        if pitches[i] == '':
            part_out.append(note.Rest(quarterLength=durations[i]))
        else:
            part_out.append(note.Note(pitch=pitches[i], quarterLength=durations[i]))

    return part_out


def main():
    show_circle(NUMCHROMATICPITCHCLASS, CHROMATICPITCHCLASSTEXTS, 'Pitch class circle')


if __name__ == '__main__':
    main()



