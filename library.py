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
                     meter, tempo, metadata, clef, percussion, midi, analysis)

class Config:
    # Default configuration
    DEFAULT_PATH = 'C:\\temp\\Music\\'
    DEFAULT_MIDI_FILE_IN = 'in.mid'
    DEFAULT_MIDI_FILE_OUT = 'out.mid'


'''
Music library - Chromatic data: frequency, pitch(class), octave
'''
class Chromatic:

    # Chromatic pitch set, equal temperament scale
    FREQUENCY_A4 = 440 # Frequency of A4
    MIDIPITCHNUM_A4 = 69 # MIDI number of A4
    OCTAVES = 9 # Number of octaves in the pitch set

    NUMPITCHCLASS = 12 # Number of pitch classes 0-11
    # Total number of pitches chromatic pitch set
    NUMPITCH = OCTAVES * NUMPITCHCLASS
    PITCHMIDINUMBERLIST = tuple(range(NUMPITCH)) # Pitch number set

    # Chromatic sets
    PITCHCLASSNUMBERS = tuple(range (NUMPITCHCLASS)) # Pitch class numbers
    PITCHCLASSTEXTS = ('C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B') # Pitch class characters

    # Pitch class
    PITCHCLASSTEXTLIST = ([x for y in range(0, OCTAVES) for x in PITCHCLASSTEXTS])
    PITCHCLASSNUMBERLIST = (OCTAVES * PITCHCLASSNUMBERS)
    PITCHFREQUENCYLIST = tuple(2 ** ((n - MIDIPITCHNUM_A4) / NUMPITCHCLASS) * FREQUENCY_A4
                                    for n in range(NUMPITCH)) # Pitch frequencies
    INTERVALLIST = [interval.ChromaticInterval(n) for n in range(NUMPITCHCLASS)]


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""
Music library: Rhythm and meter
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""

class MCTime:
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


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""
Music library - Diatonic data
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""
class Diatonic:
    # Constants
    PENTA = 5 # Number of pitch classes in a pentatonic scale
    HEPTA = 7 # Number of pitch classes in a heptatonic scale

    DEFAULT_KEY = key.Key('C', 'major')
    DEFAULT_SCALE = scale.MajorScale('C')
    DEFAULT_PITCHES = DEFAULT_SCALE.pitches
    DEFAULT_PITCH = DEFAULT_PITCHES [0]
    DEFAULT_NOTE = note.Note(DEFAULT_PITCH,duration=MCTime.DEFAULT_DURATION)

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


def interval_to_sequential (intervals):
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


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""
Music library - Interval patterns: triads and sevenths
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""

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
# Chromatic patterns
lstScaleBinary = [interval_to_sequential(lstScaleInterval[x]) for x in range(len(lstScaleInterval))]


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""
Interval patterns - Diatonic cyclic patterns: pentatonic and heptatonic
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# Pentatonic
lstIntPentaDegree = tuple(range(1, Diatonic.PENTA + 1)) # Pentatonic scale degree number
lstPentaScaleIntervalPattern = (2,2,3,2,3) # Pentatonic interval pattern
lstPentaScaleInterval = tuple(lstPentaScaleIntervalPattern[x:]+lstPentaScaleIntervalPattern[:x] for x in range(Diatonic.PENTA) )
lstPentaScaleChromaticMask = [interval_to_sequential(lstPentaScaleInterval[x]) for x in range(len(lstPentaScaleInterval))] # Heptatonic binary patterns

# Heptatonic (7 pitch class) scale
scale01 = scale.ConcreteScale()
lstIntHeptaDegree = tuple(range(1, Diatonic.HEPTA + 1)) # Heptatonic scale degree number
lstHeptaScaleIntervalPattern = (2,2,1,2,2,2,1) # Heptatonic interval pattern
# Modes
lstHeptaScaleInterval = tuple(lstHeptaScaleIntervalPattern[x:]+lstHeptaScaleIntervalPattern[:x] for x in range(Diatonic.HEPTA) )
# Diatonic heptatonic binary masks for chromatic
lstHeptaScaleChromaticMask = [interval_to_sequential(lstHeptaScaleInterval[x]) for x in range(len(lstHeptaScaleInterval))]

# Diatonic pitch masks for modes:
# 1. Ionian = Major 2. Dorian, 3. Phrygian, 4. Lydian, 5. Mixolydian, 6. Aeolian = Minor, 7. Locrian
IONIAM = MAJOR = 0
DOROIAN = 1
PHRYGIAN = 2
LYDIAN = 3
MIXOLYDIAN = 4
AEOLIAN = MINOR = 5
LOCRIAN = 6
lstScaleMajor = Chromatic.OCTAVES * lstHeptaScaleChromaticMask [MAJOR]
# Minor
lstScaleMinor = Chromatic.OCTAVES * lstHeptaScaleChromaticMask [MINOR]

# Major scale pitch masks for all tonics (C, C#, D, ..., B)
lstHeptaScale = [lstScaleMajor[-x:]+lstScaleMajor[:-x] for x in range(Chromatic.NUMPITCHCLASS) ]
arrHeptaScale = np.array(lstHeptaScale)

# Permutations: ordered set
itemlist = lstIntHeptaDegree
lstPermutations = list(itertools.permutations (itemlist))
# Combinations: of a set
itemlist = Chromatic.PITCHCLASSNUMBERS
num_items = 3
lstCombinations = list(itertools.combinations (itemlist, num_items))

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""
Scale level - Harmonic function and progression of chords in scales
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# Chord patterns in heptatonic scale degrees
# Melody scale degree functions
FUNCTIONS = {
    1: 'tonic',
    2: 'supertonic',
    3: 'mediant',
    4: 'subdominant',
    5: 'dominant',
    6: 'submediant',
    7: 'leading tone'
}

scaledegreepattern = (1,3,5,7,2,4,6) #Heptatonic
lstHeptaScaleChord = [scaledegreepattern[x:]+scaledegreepattern[:x] for x in range(Diatonic.HEPTA) ]
lstHeptaScaleChord.sort()



"""""""""""""""""""""""""""""""""""""""""""""""""""""""""
Visualization
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""

def save_library_sheet():

    # Table of all absolute chromatic data along pitch number set
    chromatic_data = pd.DataFrame ([Chromatic.PITCHMIDINUMBERLIST,
                         Chromatic.PITCHCLASSNUMBERLIST,
                         Chromatic.PITCHCLASSTEXTLIST,
                         Chromatic.PITCHFREQUENCYLIST]+ lstHeptaScale,
                              ).transpose()
#    chromatic_data.columns=['Nr','ClassNr','ClassChr', 'Freq', 'Major', 'Minor']
    chromatic_data.to_excel(Config.DEFAULT_PATH+'chromatic.xlsx', index=True, sheet_name='Pitch')


def rhythm_circle ():
    # SHow rhythm in circle
    show_circle(4, ['Down', 'Up','Down', 'Up'], 'Rhythm')



def show_circle(num_parts: int = 12, labels : tuple | list  = Chromatic.PITCHCLASSTEXTS, title : str = 'Circle of parts and labels' ):
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


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""
Music 21 Tools for streams
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""

def part_create_from_stream (stream_in: stream.Stream,
                             instr: instrument.Instrument = instrument.Piano(),
                             clef_in : clef.Clef = clef.TrebleClef()) -> stream.Part:
    # Transfer notes, rests and chords from the original stream to a new Part
    part_out = stream.Part()
    # Add instrument of part
    part_out.insert(0, instr)
    # Add clef of part
    part_out.insert(0, clef_in)

    # Create a Part and add notes, rests and chords
    for element in stream_in:
        if isinstance(element, (note.Note, note.Rest, chord.Chord)):
            part_out.append(element)

    return part_out


def stream_create(pitches : list[int|str],
                  onset_intervals: list[float],
                  durations : list[float],
                  velocities : list[int] = (100)) -> stream.Stream:
    # Create a part with notes and rests
    stream_out = stream.Stream()

    # Iterate over the list of pitches, intervals and durations
    for i in range(len(pitches)) :
        # Add notes and rests to the stream
        restduration = onset_intervals[i] - durations[i]
        if restduration > 0:
            stream_out.append(note.Rest(quarterLength=restduration))
        else:
            new_note = note.Note(pitch=pitches[i], quarterLength=durations[i])
            new_note.volume.velocity = velocities[i]
            stream_out.append(new_note)

    return stream_out


def main():
    show_circle(Chromatic.NUMPITCHCLASS, Chromatic.PITCHCLASSTEXTS, 'Pitch class circle')
    save_library_sheet ()


if __name__ == '__main__':
    main()



