'''
Music MIDI import
'''

# Modules
import musicpy as mp
from musicpy import *
from musicpy.daw import *

import numpy
import matplotlib
import matplotlib.pyplot as plt

'''
Load MIDI
'''

# Location of files
#strMIDIpathIn = 'C:\\temp\\Music\\MIDI\\'
strMIDIpathIn = 'C:\\Users\\92591\\OneDrive\\Music\\'
strMIDIpathOut = strMIDIpathIn
#strMIDIpathOut = 'C:\\temp\\Music\\'
# 'C:\\Users\\axelw\\OneDrive\Music\\'

lstStrMIDIFileName = [
'de-bollo-berendans-(mp3convert.org).mp3.mid',
'SuperTrouper.mid',
'AllThatSheWants.mid',
'AxelTheme.mid',
'BigYellowTaxi01.mid',
'DKDB.mid',
'DKDBMelody.mid',
'berendans.mid'
]


# Read MIDI file
i = 0
strFileIn = lstStrMIDIFileName[i]
strFileIn = 'In.mid'
pceMIDI = read (strMIDIpathIn + strFileIn, get_off_drums=True, split_channels=True)

print ('Piece loaded :')
print (pceMIDI)

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
str5 = analyze_rhythm (trkTrack1[nFrom:nTo])

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
sclSource = scale('Eb', 'major')
# print (sclSource)
sclTarget = scale('C', 'major')

# Modulate
chdTarget = pceMIDI[intTrack].content.modulation(sclSource, sclTarget)


'''
Export
'''
strMIDIFileNameOut = 'out.mid'

print ('Target chord :')
print (chdTarget.notes)
pceTarget = piece (tracks= [chdTarget])
print (pceTarget)
write (pceTarget, name=strMIDIpathOut+ strMIDIFileNameOut)

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

