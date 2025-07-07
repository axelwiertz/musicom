'''
Music Composition Assistant
'''

# Musical library
from datastructure import *


#m21.configure.run()



'''
Load the source file
'''
def piece_in (strFileName='in.mid'):

# Location of files
    strPath = 'C:\\temp\\Music\\'

    sceSource = converter.parse(strPath + strFileName)

    return sceSource

'''
Save the target file
'''

def piece_out (sceTarget, strFileName='out.mid',strFormat='midi'):

# Location of files
    strPath = 'C:\\temp\\Music\\'

    strStream.write(strFormat, fp=strPath + strFileName)



def piece_analyze (sceScore)

    ssc.show(sceScore)
    prtPart = sceScore.parts[0]

    #vceVoice.plot('3d')
    vceVoice.plot('histogram','pitch')
    #vceVoice.show('abc')

    print (sceScore.analyze('key'))

    return true

'''
Source
'''
lstStrMIDIFileName = (
    'de-bollo-berendans-(mp3convert.org).mp3.mid',
    'SuperTrouper.mid',
    'AllThatSheWants.mid',
    'AxelTheme.mid',
    'BigYellowTaxi01.mid',
    'DKDB.mid',
    'DKDBMelody.mid',
    'berendans.mid',
    'Summer_sunshine__The_Corrs.mid'
)

'''
Load MIDI / MusicXML
'''
# Read MIDI file
i = 8
strMIDIFile = lstStrMIDIFileName[i]
strMIDIFile = 'in.mid'
strMXLFileIn = 'in.mxl'

sceScore = piece_in (strMIDIFile)
print ('Piece loaded :')
print (sceScore)

'''
Select part
'''

'''
Analyze score
'''
piece_analyze (sceScore)

'''
Transform
'''


'''
Target
'''
strMIDIFileNameOut = 'out.mid'
piece_out(sceScore, strMIDIFileNameOut, 'midi')

'''
Play
'''

