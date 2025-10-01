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

def interval_to_step (intervals: list(int)):
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

def sequence_permutations (length: int, sequence: list(int)) -> (list,list):
    permutations = tuple(sequence[x:]+sequence[:x] for x in range(length))
    return permutations

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

"""
Diatonic scale - Chord degrees
"""
class MCChord:
    """
    Chords and progressions
    """
    chord1 = chord.Chord()

    h = harmony.ChordSymbol('Dsus4')
    h.romanNumeral = 'III'
    h.romanNumeral.key = key.Key('B')
    h.romanNumeral = roman.RomanNumeral('IV', 'A')

    # Diatonic scale - Chord degrees
    NUMTOROMAN = {
        1: ("I","i"),
        2: ('ii','ii0'),
        3: ('iii','III'),
        4: ('IV','iv'),
        5: ('V','V'),
        6: ('vi','VI'),
        7: ('vii0','vii0')
}


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""
Music library - Intervals: triads and sevenths
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""
class MCInterval:

    PENTATONIC = (2,2,3,2,3) # sequence of 5 intervals
    HEPTATONIC = (2,2,1,2,2,2,1) # sequence of 7 intervals

    TRIAD = 2 # Number intervals in a triad
    SEVENTH = 3 # Number of pitch classes in a seventh
    # Patterns:
    DIMINISHED = 0
    MINOR = 1
    MAJOR = 2
    AUGMENTED = 3
    CHORDINTERVALS = {
        DIMINISHED : (3, 3, 6),
        MINOR: (3, 4, 5),
        MAJOR : (4, 3, 5),
        AUGMENTED: (4, 4, 4)
    }
    intervalsPattern = CHORDINTERVALS[MAJOR]

    # inversions
    positions = sequence_permutations(TRIAD, CHORDINTERVALS[MAJOR])
    # Chromatic steps
    positions_chromatic_steps = [interval_to_step(positions[x]) for x in range(len(positions))]


class MCScale:
    """
    Interval patterns - Diatonic cyclic patterns: pentatonic and heptatonic
    """
    PENTA = 5 # Number of pitch classes in a pentatonic scale
    PENTATONICDEGREES = tuple(range(1, PENTA + 1)) # Pentatonic scale degree number

    HEPTA = 7 # Number of pitch classes in a heptatonic scale
    HEPTATONICDEGREES = tuple(range(1, Diatonic.HEPTA + 1)) # Heptatonic scale degree number

    scale01 = scale.ConcreteScale()


    # Pentatonic (5 pitch class) scale
    PENTAMODES = sequence_permutations (PENTA, MCInterval.PENTATONIC)
    PENTAMODESCHROMATIC = [interval_to_step(PENTAMODES[x]) for x in range(len(PENTAMODES))]

    # Heptatonic (7 pitch class) scale
    HEPTAMODES = sequence_permutations (HEPTA, MCInterval.HEPTATONIC)
    HEPTAMODESCHROMATIC = [interval_to_step(HEPTAMODES[x]) for x in range(len(HEPTAMODES))]


    # Chromatic pitch masks for modes:
    # 1. Ionian = Major 2. Dorian, 3. Phrygian, 4. Lydian, 5. Mixolydian, 6. Aeolian = Minor, 7. Locrian
    IONIAM = MAJOR = 0
    DOROIAN = 1
    PHRYGIAN = 2
    LYDIAN = 3
    MIXOLYDIAN = 4
    AEOLIAN = MINOR = 5
    LOCRIAN = 6
    lstScaleMajor = Chromatic.OCTAVES * HEPTAMODESCHROMATIC [MAJOR]
    # Minor
    lstScaleMinor = Chromatic.OCTAVES * HEPTAMODESCHROMATIC [MINOR]

    # Major scale pitch masks for all tonics (C, C#, D, ..., B)
    HEPTAMAJORSCALES = [lstScaleMajor[-x:]+lstScaleMajor[:-x] for x in range(Chromatic.NUMPITCHCLASS) ]
    arrHeptaScale = np.array(HEPTAMAJORSCALES)

class MCSet:
    # Permutations: ordered set
    itemlist = MCScale.HEPTATONICDEGREES
    lstPermutations = list(itertools.permutations (itemlist))
    # Combinations: of a set
    itemlist = Chromatic.PITCHCLASSNUMBERS
    num_items = 3
    lstCombinations = list(itertools.combinations (itemlist, num_items))

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""
Scale level - Harmonic function and progression of chords in scales
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# Chord patterns in heptatonic scale degrees


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
                         Chromatic.PITCHFREQUENCYLIST]+ MCScale.HEPTAMAJORSCALES,
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



