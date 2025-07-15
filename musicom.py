"""
Music Composition Assistant
"""

import random
import platform
#import sound

# Musical library
from datastructure import *


#m21.configure.run()

def main():

    # Load piece
    sce01 = score_load()
    print('Score loaded :')
    print(sce01)

    stream_analyze (sce01)

    # Analyze parts
    for i in range (0, len(sce01.parts)-1):
        stream_analyze (sce01.parts[i])


    # Create stream
    melody_part = part_create_melody()

    # Create parts for melody and accompaniment
    melody_part = stream.Part()
    accompaniment_part = stream.Part()

    # Set key and time signature typical of Balfolk
    melody_part, bass_part = part_create_balfolk()

    # Add parts to score
    # Create a score
    sce01 = stream.Score()
    sce01.insert(0, melody_part)
    sce01.insert(0, bass_part)

    # Analyze stream
    stream_analyze (sce01)

    # Transform piece
    sce01 = stream_transform (sce01)

    # Play stream

    # Save piece
    stream_save (sce01)


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
    print (stm01.analyze('key'))


def stream_transform (stm_in: stream.Stream) -> stream.Stream:

    #stm_out = copy.deepcopy(stm_in)

    # P I R RI
    transformations = ('P', 'I', 'R', 'RI')
    trans01 = random.choice (transformations)
    # Transform tone row
    stm_out = stm_in.zeroCenteredTransformation (trans01, 0)


    return stm_out



if __name__ == '__main__':
    main()
