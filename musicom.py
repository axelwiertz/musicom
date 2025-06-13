'''
Music Composition Assistant
'''

# Musical library
from datastructure import *


#m21.configure.run()


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
strMIDIFile = 'In.mid'
strMXLFileIn = 'In.mxl'
sceScore = score_in (strMIDIFile)
print ('Piece loaded :')
print (sceScore)


def score_in (strFileName):

# Location of files
    strPathIn = 'C:\\temp\\Music\\'
    strPathOut = 'C:\\temp\\Music\\'

    sceSource = converter.parse(strPathIn + strFileName)
    #pceMIDI = mp.read (strPathIn + strFileName, get_off_drums=True, split_channels=True)

    return sceSource






def piece_analyze (sceScore)

    ssc.show(sceScore)
    prtPart = sceScore.parts[0]

    #vceVoice.plot('3d')
    vceVoice.plot('histogram','pitch')
    #vceVoice.show('abc')

    print (sceScore.analyze('key'))

    return true

'''
Select track and part
'''
intTrack = 0
nFrom = 0
nTo = 4
#nTo = 47

intNumTracks = len(pceMIDI.tracks)
trkTrack1 = pceMIDI(intTrack)
lstNotes = trkTrack1.notes[nFrom:nTo]
intNumNotes = len (lstNotes)

print ('Track selected :')
print (trkTrack1)
print ('Track part from :' + str(nFrom) + ' to ' + str(nTo) + ' :')
print (trkTrack1[nFrom:nTo])
print ('Notes from track : '+ str(lstNotes))
print ('Number of notes : ' + str(intNumNotes))

print (pceMIDI[intTrack].content)
print (pceMIDI[intTrack].content.notes)

intInstr = 1
print ('Play selected track :')
#play(trkTrack1[nFrom:nTo], instrument=intInstr)
#, wait=True)



'''
Analyze track
'''
str1 = mp.alg.detect (pceMIDI(intTrack))
str2 = mp.alg.detect (trkTrack1[nFrom:nTo])
str3 = mp.alg.chord_analysis (pceMIDI(intTrack))
str4 = mp.alg.chord_analysis (trkTrack1[nFrom:nTo])
str5 = mp.alg.analyze_rhythm (trkTrack1[nFrom:nTo])

print (str1)
print (str2)
print (str3)
print (str4)
print (str5)


'''
Transform
'''

# Slice
chdTarget = trkTrack1[nFrom:nTo]

# Scales
sclSource = mp.scale('Bb', 'major')
# print (sclSource)
sclTarget = mp.scale('C', 'major')

# Modulate
chdTarget = pceMIDI[intTrack].content.modulation(sclSource, sclTarget)


'''
Target
'''
strMIDIFileNameOut = 'out.mid'

print ('Target chord :')
print (chdTarget.notes)
pceTarget = mp.piece (tracks= [chdTarget])
print (pceTarget)
mp.write (pceTarget, name=strPathOut+ strMIDIFileNameOut)

'''
Play
'''
intInstr = 1
intBPM = 100
print ('Play :')
#play(pceTarget, wait=True)
#play (pceMIDI, wait=True)
#play (pceMIDI[intTrack], instrument=intInstr, wait=True)
# play (pceMIDI[intTrack].content, bpm=intBPM, instrument=intInstr)
#play (chdTarget, wait=True)

