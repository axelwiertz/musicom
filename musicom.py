"""
Music Composition Assistant
"""

import random


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
    stm01 = stream_create()

    # Analyze stream
    stream_analyze (stm01)

    # Transform piece
    sce01 = stream_transform (sce01)

    # Save piece
    piece_save (sce01)


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

'''
Save the target file
'''
def piece_save (str01):
    # Location of files
    midi_or_mxl = 'midi'
    path = 'C:\\temp\\Music\\'
    filename = 'out.mid'
    # Write stream to output
    str01.write(midi_or_mxl, fp=path + filename)


'''
Create stream
'''
def stream_create() -> stream.Stream:

    stm01 = stream.Stream()
    # Rhythm
    duration_unit = 0.125
    duration_factor = 8

    base_row = serial.ToneRow(row = [0,4,7,4])
    # P I R RI
    transformations = ('P', 'I', 'R', 'RI')
    trans01 = random.choice (transformations)
    trans_row = base_row.zeroCenteredTransformation (trans01, 0)

    for i, pitch_class in enumerate (trans_row):
        pcs01 = trans_row.pitchClasses(i)
        pcs01.duration = duration_unit * duration_factor
        pcs01.octave = 3
        stm01.append(pcs01)


    return stm01

'''
Analyze stream
'''
def stream_analyze (stm01: stream.Stream):

    show (stm01)
    #vceVoice.plot('3d')
    stm01.plot('histogram','pitch')
    #vceVoice.show('abc')
    print (stm01.analyze('key'))


def stream_transform (stm_in: stream.Stream) -> stream.Stream:

    stm_out = copy.deepcopy(stm_in)

    return stm_out



if __name__ == '__main__':
    main()
