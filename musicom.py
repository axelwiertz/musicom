"""
Music Composition Assistant
"""
import copy
import random
import platform
#import sound
from music21.meter import TimeSignature

# Musical data
from library import *
# Harmony rules
from harmony import *

# Showing score without external programs like Musescore
from showscore import show


"""
Composition - Structure
"""
# Main score
main_score = stream.Score()
MAIN_PATH = 'C:\\temp\\Music\\'

# Three voice score
MELODY_VOICE = 0
HARMONY_VOICE = 1
BASS_VOICE = 2

PART_A = 0
PART_B = 1
PART_C = 2
PART_D = 3



def big_yellow_taxi():
    # Big Yellow Taxi
    main_score = score_create('Bb','4/4')

    tonerow_byt = serial.ToneRow (
        ['B3', 'C#4', 'E4', 'E4', 'F#4', 'C#4', 'E4', 'E4', 'F#4', 'E4', 'G#3', 'B3', 'B3', 'C#4',
        'E4', 'F#4', 'B3', 'B3', 'F#4', 'F#4', 'F#4', 'G#4', 'F#4', 'E4', 'E4'])

    # Analyze score
    score_analyze (main_score)

def berendans():
    # Berendans
    main_score = score_create('Bb','4/4')
    progr = ['I', 'V', 'I']



def load_and_analyze ():
    # Load and analyze a score

    # Load a score
    main_score = converter.parse (MAIN_PATH + 'in.mid')

    # Analyze score
    score_analyze (main_score)


def load_and_transform ():
    # Load a score
    main_score = converter.parse (MAIN_PATH + 'in.mid')


    # Add to score
    # Insert several new notes
    new_note_1 = note.Note('C4', quarterLength=0.75)
    new_note_2 = note.Note('C4', quarterLength=0.25)
    main_score.insertAndShift([2, new_note_1, 2.75, new_note_2])


    # Transform pitch sequence in tomerow
    trw01 = serial.ToneRow()
    trw02 = tonerow_transform (trw01)

def create_new ():
    # Create a new score
    # Form
    parts = 3
    voices = 3
    form = (16, 16, 16)

    main_score = score_create('C','4/4')

    # Rhythm
    rhythm01 = [BT, RS, BT, BT, BT, BT, RS]
    durations01 = [1.0, 1.0, 1.5, 1.5, 1.0, 1.0, 1.0]
    pitch_list01 = ['C4', '', 'C4', 'C4', 'C4', 'C4', '']

    voices = []
    voices [MELODY_VOICE] = part_create(pitch_list01, durations01)

    rtm_example02 = [BT, BT, RS, BT, BT, RS]
    pitch_list02 = ['C4', 'C4', '', 'C4', 'C4', '']
    durations02 = [1.5, 0.5, 0.5, 0.25, 0.25, 1]

    voices [HARMONY_VOICE] = part_create(pitch_list02, durations02 )

    main_score.append(voices)
    #main_score.append(voice_b)
    #main_score.append(voice_c)

    # Instruments of parts
    voices [MELODY_VOICE].insert(0, instrument.Flute())
    voices [HARMONY_VOICE].insert(0, instrument.Violin())
    voices [BASS_VOICE].insert(0, instrument.Bass())

    # Create three voices for melody and accompaniment
    create_three_voice_melody (main_score)

    # for voices ?
    # score3 = stream.Stream.voicesToParts()

    # Set key and time signature typical of Balfolk
    melody_voice, bass_voice = part_create_balfolk()


    rhythm_pattern = FOUR_RHYTHM

    pitch_list = [["C4", "D4", "E4", "F4"],
                    ["G4", "A4", "B4", "C5"]]

    # Unused material
    # Tonerow
    tonerow_base = serial.ToneRow(row = [0,4,7,4])

    for pcs in enumerate (tonerow_base):
        pcs.octave = 3
        voices[0].append(pcs)


    signature : TimeSignature
    signature = main_score.getElementsByClass('TimeSignature')[0]
    # number of beats per measure
    beats = signature.numerator
    # signature in quarterlength
    beatduration = signature.denominator * QUARTER

    # Generate durations
    # 1/32 note
    duration_unit = 0.125
    duration_factor = 8
    duration_new = duration_unit * duration_factor

    counterpoint_voices()



def score_library ():
    # Create a score with library elements

    main_score = create_stream_chords_in_key(lstChordPattern, key.Key('C'), 2)
    # Save score
    main_score.write(fmt='midi', fp=MAIN_PATH + "chordprog_in_key_CM")

    main_score = create_stream_triads_in_key(key.Key('C'), 2)
    # Save score
    main_score.write(fmt='midi', fp=MAIN_PATH + "chordtriad_in_key_CM")




def main():
    # Main: create or transform

    create_new()




"""
Creation
"""
def score_create ( key_in: str = 'C' ,
                   signature_in: str = '4/4' ,
                   bpm_in: int = 120) -> stream.Score:
    # Create a stream to hold the musical elements
    score_out = stream.Score()

    # Set the time signature, key signature and tempo
    score_out.insert(0, key.Key(key_in))
    score_out.insert(0, meter.TimeSignature(signature_in))
    score_out.insert(0, tempo.MetronomeMark(number=bpm_in))

    return score_out



def part_create(pitch_list_in = list[str], durations_in = list[float]) -> stream.Part:
    # Create a part with notes and rests
    part_out = stream.Part()

    # Iterate over the list of pitches
    for i, pitch_str in pitch_list_in:
        # Add beats and rests to the stream
        if pitch_str == '':
            part_out.append(note.Rest(quarterLength=durations_in[i]))
        else:
            part_out.append(note.Note(pitch=pitch_str, quarterLength=durations_in[i]))

    return part_out





def create_three_voice_melody (score_in: stream.Score):
    # Create three voices melody, harmony, and bass

    # Motifs of voices
    pitch_list_list = []
    duration_list_list = []
    pitch_list_list [MELODY_VOICE] = ['C5', 'D5', 'E5', 'F5', 'G5', 'A5', 'B4', 'C5']
    duration_list_list [MELODY_VOICE] = [1, 1, 1, 1, 1, 1, 1, 1]
    pitch_list_list [HARMONY_VOICE] = ['C4', 'E4', 'G4', '', 'F4', 'A4', 'C5', '']
    duration_list_list [HARMONY_VOICE] = [1, 1, 1, 1, 1, 1, 1, 1]
    pitch_list_list [BASS_VOICE] = ['C3', 'G3']
    duration_list_list [BASS_VOICE] = [4, 4]

    for i in range (0, len(pitch_list_list)-1):
        score_in.append(
            part_create(pitch_list_list [i], duration_list_list[i])
        )


def create_random_voice(length,
                        pitch_set: list = ['C4','D4','E4','F4','G4'],
                        duration_set: list = [0.5, 1, 2]):
    # Create a random voice from a list of pitches and durations
    voice = []
    for i in range(length):
        new_pitch = random.choice(pitch_set)  # C4 to B4
        duration = random.choice(duration_set)
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


def score_analyze (score_in: stream.Stream):
    # Analyze score

    #vceVoice.plot('3d')
    score_in.plot('histogram','pitch')
    #vceVoice.show('abc')
    # Key
    key01 = score_in.analyze('key')
    print (key01)

    # Analyze parts ?
    for score_part in main_score.parts:
        score_part


    score_out = stream.Score()

    chordset = score_in.chordify()
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

    return score_out


def score_show (score_in):
    """
    Show or play the stream
    """
    if platform.system() == 'Windows':
        score_in.show('text')
#    score.show('midi')  # Play MIDI
        show(score_in)  # Show musical notation

    elif platform.system() == 'IOS':
        score_in.show('text')

        # Play the result (IOS):
        #player = sound.MIDIPlayer('target.mid')
        #player.play()
        #player.stop()


"""
Transformation
"""

def tonerow_transform (tonerow_in: serial.ToneRow) -> serial.ToneRow:

    tonerow_out = copy.deepcopy(tonerow_in)

    # P I R RI
    transformations = ('P', 'I', 'R', 'RI')
    trans01 = random.choice (transformations)
    # Transform tone row
    tonerow_out = tonerow_in.zeroCenteredTransformation (trans01, 0)

    # Transpose the phrase up by a major third
    tonerow_out = tonerow_in.transpose("M3")
    #tonerow_out = tonerow_in.transpose(4)

    return tonerow_out


if __name__ == '__main__':
    main()
