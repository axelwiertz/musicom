"""
Music Composition Assistant
"""

import random
import platform
#import sound
import matplotlib.pyplot as plt

# Musical data
from datastructure import *
# Harmony rules
from harmony import *



#m21.configure.run()

def main():
    # Create a score
    main_score = stream.Score()
    # Create a scale
    main_scale = scale.MajorScale('c')

    # Load a score
    load_score = score_load()

    # Analyze score
    stream_analyze (load_score)

    # Analyze parts
    for i in range (0, len(load_score.parts)-1):
        stream_analyze (load_score.parts[i])

    # Create stream
    # Form
    form = (16, 16, 16)
    melody = part_create_melody()

    # Create the score and parts
    chord_progressions_stream = create_stream_chords_in_key(lstChordPattern, key.Key('C'), 2)
    triads_stream = create_stream_triads_in_key(key.Key('C'), 2)

    # Create voices for melody and accompaniment
    melody_voice, harmony_voice, bass_voice = create_melody_harmony_bass()

    score3 = stream.Stream.voicesToParts()

    # Instruments of parts
    melody_voice.insert(0, instrument.Flute())
    harmony_voice.insert(0, instrument.Violin())
    bass_voice.insert(0, instrument.Bass())

    # Meter
    melody_voice.append(tempo.MetronomeMark(number=100))
    for part in [melody_voice, harmony_voice, bass_voice]:
        part.append(meter.TimeSignature('4/4'))

    # Set key and time signature typical of Balfolk
    melody_voice, bass_voice = part_create_balfolk()

    # Add parts to score
    # Combine parts
    main_score.insert(0, melody_voice)
    main_score.insert(0, harmony_voice)
    main_score.insert(0, bass_voice)

    # Analyze stream
    stream_analyze (main_score)

    # Transform pitch sequence
    trw01 = serial.ToneRow()
    trw02 = tonerow_transform (trw01)

    # Play stream

    # Save piece
    stream_save (main_score)


'''
Load MIDI / MusicXML
'''
def score_load() -> stream.Score:
    # Source file
    path = 'C:\\temp\\Music\\'
    filename = 'in.mid'
    #filename = 'in.mxl'
    # Location of files
    sce01 = converter.parse (path + filename)

    return sce01

def stream_save (stm01):
    """
    Save the target file
    """

    # Location of files
    midi_or_mxl = 'midi'
    path = 'C:\\temp\\Music\\'
    filename = 'out.mid'
    # Write stream to output
    stm01.write(midi_or_mxl, fp=path + filename)


"""
Creation
"""
def create_stream () -> stream.Stream:
    # Create a stream to hold the musical elements
    stream_out = stream.Stream()

    # Create a series of notes
    note1 = note.Note("C4", quarterLength=1.0)
    note2 = note.Note("D4", quarterLength=1.0)
    note3 = note.Note("E4", quarterLength=1.0)
    note4 = note.Note("F4")

    # Add the notes to the stream
    stream_out.append(note1)
    stream_out.append(note2)
    stream_out.append(note3)
    stream_out.append(note4)

    # Insert several new notes
    new_note_1 = note.Note('C4', quarterLength=0.75)
    new_note_2 = note.Note('C4', quarterLength=0.25)
    stream_out.insertAndShift([2, new_note_1, 2.75, new_note_2])

    # Set the time signature and key signature
    stream_out.insert(0, meter.TimeSignature("4/4"))
    stream_out.insert(0, key.Key("C"))


    return stream_out

def part_create_melody() -> stream.Part:
    """
    Create stream
    """
    part_out = stream.Part()
    # Rhythm
    duration_unit = 0.125
    duration_factor = 8

    base_row = serial.ToneRow(row = [0,4,7,4])

    for i, pitch_class in enumerate (base_row):
        pcs01 = base_row.pitchClasses (i)
        pcs01.duration = duration_unit * duration_factor
        pcs01.octave = 3
        part_out.append(pcs01)

        # Rhythm
        rtm_example01 = [[BT, RS, BT, BT, BT, BT, RS],
                     [1.0, 1.0, 1.5, 1.5, 1.0, 1.0, 1.0]]
        stream_rhythm = create_rhythmic_stream(rtm_example01)

        rtm_example02 = [[BT, BT, RS, BT, BT, RS],
                     [1.5, 0.5, 0.5, 0.25, 0.25, 1]]

    return part_out


def create_melody_harmony_bass () -> (stream.Part, stream.Part, stream.Part):
    # Add 40 measures of melody, harmony, and bass
    melody, harmony, bass = stream.Part()

    for i in range(40):
        melody_notes = ['C5', 'D5', 'E5', 'F5'] if i % 2 == 0 else ['G5', 'A5', 'B4', 'C5']
        harmony_chord = ['C4', 'E4', 'G4'] if i % 2 == 0 else ['F4', 'A4', 'C5']
        bass_note = 'C3' if i % 2 == 0 else 'G2'

        m1 = stream.Measure()
        for not01 in melody_notes:
            m1.append(note.Note(not01, quarterLength=1))
        melody.append(m1)

        m2 = stream.Measure()
        m2.append(chord.Chord(harmony_chord, quarterLength=4))
        harmony.append(m2)

        m3 = stream.Measure()
        m3.append(note.Note(bass_note, quarterLength=4))
        bass.append(m3)

    return melody, harmony, bass



def part_create_balfolk () -> (stream.Part, stream.Part):
    # Create a Balfolk style melody and bass
    melody_part = stream.Part()
    bass_part = stream.Part()

    key_signature = key.KeySignature(0)  # C major/A minor
    time_signature = meter.TimeSignature('6/8')

    melody_part.append(key_signature)
    melody_part.append(time_signature)
    bass_part.append(key_signature)
    bass_part.append(time_signature)

# Bourrée-inspired melody (typical Balfolk rhythm)
    melody_notes = [
        ['C4', 'E4', 'G4'],
        ['D4', 'F4', 'A4'],
        ['E4', 'G4', 'B4'],
        ['F4', 'A4', 'C5']
    ]

    # Create melody with rhythmic variation
    for i in range(16):  # 4 measures
        # Choose a random melodic fragment
        fragment = random.choice(melody_notes)

        # Create notes with Balfolk-style rhythm
        for note_name in fragment:
            n = note.Note(note_name)
            n.duration.type = 'eighth'
            melody_part.append(n)

    # Create accompaniment (drone/rhythmic support)
    bass_notes = ['C3', 'G3']
    for i in range(32):  # matching melody length
        bass_note = note.Note(random.choice(bass_notes))
        bass_note.duration.type = 'eighth'
        bass_part.append(bass_note)


    return melody_part, bass_part

"""
Analysis and visualization
"""

# To do: Rhythm circle


def pitch_class_circle():
    # Show pitch classes in circle

    # Convert pitch class numbers to angles
    angles = np.linspace(0, 2 * np.pi, NUMDIATONICPITCHCLASS, endpoint=False)

    # Create a figure and axis
    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})

    # Plot the pitch class numbers
    for angle, pitch in zip(angles, lstPitchClassNr):
        ax.plot(angle, 1, 'o', markersize=10)
        ax.text(angle, 1.1, str(pitch), ha='center', va='center')

    # Set the title
    ax.set_title('Circle of Pitch Class Numbers')

    # Show the plot
    plt.show()


def stream_analyze (stream_in: stream.Stream):
    # Analyze stream
    show (stream_in)
    #vceVoice.plot('3d')
    stream_in.plot('histogram','pitch')
    #vceVoice.show('abc')
    # Key
    key01 = stream_in.analyze('key')
    print (key01)

    sce01 = stream.Score()

    chordset = stream_in.chordify()
    # Check for specific chords
    for chd01 in chordset.recurse().getElementsByClass(chord.Chord):
        if chd01.isDominantSeventh():
            print(chd01.measureNumber, chd01.beatStr, chd01)

    # All chords
    for chd01 in chordset.recurse().getElementsByClass(chord.Chord):
        # Put chord in closed position
        chd01.closedPosition(forceOctave=4, inPlace=True)
        # Annotate chord intervals
        chd01.annotateIntervals(inPlace=True)
        # Add Roman numerals in lyrics
        rn = roman.romanNumeralFromChord(chd01, key01)
        chd01.addLyric(str(rn.figure))


    sce01.insert (0, chordset)
    sce01.show()

def stream_show (stream_in):
    """
    Show or play the stream
    """
    if platform.system() == 'Windows':
        stream_in.show('text')
#    score.show('midi')  # Play MIDI
        stream_in.show()  # Show musical notation

    elif platform.system() == 'IOS':
        stream_in.show('text')

        # Play the result (IOS):
        #player = sound.MIDIPlayer('target.mid')
        #player.play()
        #player.stop()


"""
Transformation
"""

def tonerow_transform (stream_in: serial.ToneRow) -> serial.ToneRow:

    stream_out = copy.deepcopy(stream_in)

    # P I R RI
    transformations = ('P', 'I', 'R', 'RI')
    trans01 = random.choice (transformations)
    # Transform tone row
    stream_out = stream_in.zeroCenteredTransformation (trans01, 0)

    # Transpose the phrase up by a major third
    stream_out = stream_in.transpose("M3")
    #stream_out = stream_in.transpose(4)

    return stream_out


if __name__ == '__main__':
    main()
