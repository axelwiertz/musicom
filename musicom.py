"""
Music Composition Assistant
"""
import copy
import random
import platform
#import sound
import matplotlib.pyplot as plt

# Musical data
from library import *
# Harmony rules
from harmony import *

# Showing score without external programs like Musescore
from showscore import show


"""
Main score
"""
main_score = stream.Score()


def big_yellow_taxi():
    # 'Big Yellow Taxi'
    tonerow_byt = serial.Tonerow (
        'B3, C#4, E4, E4, F#4, C#4, E4, E4, F#4, E4, G#3, B3, B3, C#4, E4, F#4, B3, B3, F#4, F#4, F#4, G#4, F#4, E4, E4')
    lstScales = ['Bb major']

def berendans():
    # Berendans
    lstScales = ['Bb major']
    progr = ['I', 'V', 'I']


def main():
    # Create a score
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
    create_three_voice_melody (main_score)

    # for voices ?
    score3 = stream.Stream.voicesToParts()



    # Set key and time signature typical of Balfolk
    melody_voice, bass_voice = part_create_balfolk()


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
    score_out = converter.parse (path + filename)

    return score_out

def stream_save (stream_in):
    """
    Save the target file
    """

    # Location of files
    midi_or_mxl = 'midi'
    path = 'C:\\temp\\Music\\'
    filename = 'out.mid'
    # Write stream to output
    stream_in.write(midi_or_mxl, fp=path + filename)


"""
Creation
"""
def create_stream (signature_in: meter.TimeSignature = meter.TimeSignature("4/4"),
                   key_in: key.Key= key.Key("C"),
                   bpm_in: int = 120) -> stream.Stream:
    # Create a stream to hold the musical elements
    stream_out = stream.Stream()

    # Set the time signature and key signature
    stream_out.insert(0, signature_in)
    stream_out.insert(0, key_in)
    tempo_stream = tempo.MetronomeMark(number=bpm_in)

    notes = ["C4", "D4", "E4", "F4", "G4", "A4", "B4", "C5"]
    durations = [1,1,1,1,1,1,1,1]

    # Create a note object for each note and append it to stream
    for i in len(notes)-1:
        stream_note = (note.Note(pitch=notes[i], quarterLength=durations[i]))
        # Add the notes to the stream
        stream_out.append(stream_note)

    # Select random pitch
    pitch_midi_number = random.choice(PITCH_MIDI_NUMBERS)

    stream_out.append(note.Note(pitch_midi_number))

    # Insert several new notes
    new_note_1 = note.Note('C4', quarterLength=0.75)
    new_note_2 = note.Note('C4', quarterLength=0.25)
    stream_out.insertAndShift([2, new_note_1, 2.75, new_note_2])

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


def create_three_voice_melody (score_in: stream.Score, nummeasure: int = 20):
    # Create three voices melody, harmony, and bass
    score_in = stream.Score()
    score_in.append(stream.Part())
    score_in.append(stream.Part())
    score_in.append(stream.Part())

    # Instruments of parts
    score_in.parts (MELODY_VOICE).insert(0, instrument.Flute())
    score_in.parts (HARMONY_VOICE).insert(0, instrument.Violin())
    score_in.parts (BASS_VOICE).insert(0, instrument.Bass())


    # Motifs of voices
    pitch_classes =
         [
            [['C5', 'D5', 'E5', 'F5'],
             ['G5', 'A5', 'B4', 'C5']],
            [['C4', 'E4', 'G4'],
             ['F4', 'A4', 'C5']],
            [['C3'],
             ['G3']]
        ]
    for i in range(nummeasures):
        # Alternating motifs
        motif = i % len(pitch_classes[1])
        for melody_pc in pitch_classes [MELODY_VOICE, motif]:
            score_in.parts (MELODY_VOICE).append(note.Note(not01, quarterLength=1))

        score_in.parts (HARMONY_VOICE).append(chord.Chord(pitch_classes [HARMONY_VOICE, motif], quarterLength=4))

        score_in.parts (BASS_VOICE).append(note.Note(pitch_classes [BASS_VOICE, motif], quarterLength=4))

    return true



def create_random_voice(length, pitch_range: tuple = (60, 72), durations: list = [0.5, 1, 2]):
    # Create a random list of notes
    voice = []
    for i in range(length):
        new_pitch = random.choice(range(pitch_range))  # C4 to B4
        duration = random.choice(durations)
        new_note = note.Note(pitch= new_pitch, quarterLength=duration)
        voice.append(new_note)
    return voice


def generate_counterpoint(voice1, voice2):
    # Generate two counterpoint voices
    # Ensure the voices are of the same length
    if len(voice1) != len(voice2):
        raise ValueError("Voices must be of the same length")

    # Check for parallel perfect intervals
    for i in range(len(voice1) - 1):
        intv1 = interval.Interval(voice1[i], voice1[i + 1])
        intv2 = interval.Interval(voice2[i], voice2[i + 1])
        if is_perfect_interval(intv1) and is_perfect_interval(intv2) and intv1.direction == intv2.direction:
            return False

    # Check for hidden parallels
    for i in range(len(voice1) - 1):
        intv1 = interval.Interval(voice1[i], voice1[i + 1])
        intv2 = interval.Interval(voice2[i], voice2[i + 1])
        if is_perfect_interval(intv1) and is_perfect_interval(intv2) and intv1.direction == intv2.direction:
            return False

    # Check for crossing voices
    for i in range(len(voice1)):
        if voice1[i].pitch < voice2[i].pitch and voice1[i + 1].pitch > voice2[i + 1].pitch:
            return False

    return True


def counterpoint_voices():

    length = 16  # Length of the counterpoint
    voice1 = create_random_voice(length)
    voice2 = create_random_voice(length)

    while not generate_counterpoint(voice1, voice2):
        voice2 = create_random_voice(length)



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

    score_out = stream.Score()

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


    score_out.insert (0, chordset)
    score_out.show()

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
