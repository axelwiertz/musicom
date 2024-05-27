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


# Location of files
strMIDIpathIn = 'C:\\temp\\Music\\MIDI\\'
strMIDIpathOut = 'C:\\temp\\Music\\'
# 'C:\\Users\\axelw\\OneDrive\Music\\'

strMIDIFileName = 'SuperTrouper.mid'
strMIDIFileName = 'AllThatSheWants.mid'
strMIDIFileName = 'bossa-nova.mid'
strMIDIFileName = 'AxelTheme.mid'
strMIDIFileName = 'BigYellowTaxi01.mid'
strMIDIFileName = 'DKDB.mid'
strMIDIFileName = 'DKDBMelody.mid'
strMIDIFileName = 'berendans.mid'

strMIDIFileNameOut = 'track.mid'

# Read MIDI file
pceMIDI = read (strMIDIpathIn + strMIDIFileName, get_off_drums=True, split_channels=True)

# Select track and part
intTrack = 0
nFrom = 0
nTo = 900
nTo = 220

intNumTracks = len(pceMIDI.tracks)
trkTrack1 = pceMIDI(intTrack)
lisNotes = trkTrack1.notes[nFrom:nTo]
intNumNotes = len (lisNotes)

# Scales
sclSource = scale('Eb', 'major')
print (sclSource)
sclTarget = scale('C', 'major')

# Modulate
chdTarget = pceMIDI[intTrack].content.modulation(sclSource, sclTarget)
# Slice
chdTarget = trkTrack1[nFrom:nTo]

print (pceMIDI)
print ('Track :')
print (trkTrack1)
print ('Track part from ' + str(nFrom) + ' to ' + str(nTo) + ' :')
print (trkTrack1[nFrom:nTo])
print ('Notes from track : '+ str(lisNotes))
print ('Number of notes : ' + str(intNumNotes))

print (pceMIDI[intTrack].content)
print (pceMIDI[intTrack].content.notes)

print ('Target chord :')
print (chdTarget.notes)

# Export
pceTarget = piece (tracks= [chdTarget])
print (pceTarget)
write (pceTarget, name=strMIDIpathOut+ strMIDIFileNameOut)

# Play
intInstr = 1
intBPM = 100
print ('Play :')
play(pceTarget, wait=True)
#play (pceMIDI, wait=True)
#play (pceMIDI[intTrack], instrument=intInstr, wait=True)
# play (pceMIDI[intTrack].content, bpm=intBPM, instrument=intInstr)
#play (chdTarget, wait=True)
#play (chdTarget, wait=true)

# Analyis
#str1 = mp.alg.detect (pceMIDI(intTrack))
#str2 = mp.alg.detect (lisNotes)
#str3 = mp.alg.chord_analysis (pceMIDI(intTrack))
#str4 = mp.alg.chord_analysis (lisNotes)
str5 = analyze_rhythm (pceMIDI(intTrack))

#print (str1)
#print (str2)
#print (str3)
#print (str4)
