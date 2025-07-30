"""
Music Composition Assistant
"""

import random
import platform
#import sound

# Musical data
from datastructure import *
# Harmony rules
from harmony import *



#m21.configure.run()

def main():
    # Create datastructure
    main_score = stream.Score()
    # Create a scale
    scale1 = scale.MajorScale('c')

    # Load score
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
    score2 = stream.Score()
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

def stream_show (stm01):
    """
    Show or play the stream
    """
    if platform.system() == 'Windows':
        stm01.show('text')
#    score.show('midi')  # Play MIDI
        stm01.show()  # Show musical notation

    elif platform.system() == 'IOS':
        stm01.show('text')

        # Play the result (IOS):
        #player = sound.MIDIPlayer('target.mid')
        #player.play()
        #player.stop()


def create_stream () -> stream.Stream:
    # Create a stream to hold the musical elements
    stm01 = stream.Stream()

    # Create a series of notes
    note1 = note.Note("C4", quarterLength=1.0)
    note2 = note.Note("D4", quarterLength=1.0)
    note3 = note.Note("E4", quarterLength=1.0)
    note4 = note.Note("F4")

    # Add the notes to the stream
    stm01.append(note1)
    stm01.append(note2)
    stm01.append(note3)
    stm01.append(note4)

    # Set the time signature and key signature
    stm01.insert(0, meter.TimeSignature("4/4"))
    stm01.insert(0, key.Key("C"))


    return stm01

def part_create_melody() -> stream.Part:
    """
    Create stream
    """
    prt01 = stream.Part()
    # Rhythm
    duration_unit = 0.125
    duration_factor = 8

    base_row = serial.ToneRow(row = [0,4,7,4])

    for i, pitch_class in enumerate (base_row):
        pcs01 = base_row.pitchClasses (i)
        pcs01.duration = duration_unit * duration_factor
        pcs01.octave = 3
        prt01.append(pcs01)


    return prt01


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
    """
    Create Balfolk melody
    """
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


def stream_analyze (stm01: stream.Stream):
    """
    Analyze stream
    """
    show (stm01)
    #vceVoice.plot('3d')
    stm01.plot('histogram','pitch')
    #vceVoice.show('abc')
    # Key
    key01 = stm01.analyze('key')
    print (key01)

    sce01 = stream.Score()

    chordset = stm01.chordify()
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

def tonerow_transform (stm_in: serial.ToneRow) -> serial.ToneRow:

    #stm_out = copy.deepcopy(stm_in)

    # P I R RI
    transformations = ('P', 'I', 'R', 'RI')
    trans01 = random.choice (transformations)
    # Transform tone row
    stm_out = stm_in.zeroCenteredTransformation (trans01, 0)

    # Transpose the phrase up by a major third
    stm_out = stm_in.transpose("M3")
    #stm_out = stm_in.transpose(4)

    return stm_out



if __name__ == '__main__':
    main()
