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
strMIDIpath = 'C:\\temp\\Music\\MIDI\\'
# 'C:\\Users\\axelw\\OneDrive\Music\\'

strMIDIFileName = 'SuperTrouper.mid'
strMIDIFileName = 'AllThatSheWants.mid'
strMIDIFileName = 'bossa-nova.mid'
strMIDIFileName = 'AxelTheme.mid'
strMIDIFileName = 'BigYellowTaxi01.mid'
strMIDIFileName = 'DKDB.mid'


# Read
pceMIDI = read(strMIDIpath + strMIDIFileName, split_channels=True)
print (pceMIDI)
# Select
intTrack = 3
nFrom = 0
nTo = 3

intNumTracks = len(pceMIDI.tracks)
trkTrack1 = pceMIDI(intTrack)
print (trkTrack1)
print (trkTrack1[nFrom:nTo])

lisNotes = pceMIDI(intTrack).notes
intNumNotes = len (lisNotes)
print (lisNotes)
print (intNumNotes)

print (pceMIDI[intTrack].content)
print (pceMIDI[intTrack].content.notes)


# Play
intTrack = 0
intInstr = 1
intBPM = 92
#play (pceMIDI, wait=True)
play (pceMIDI[intTrack], instrument=intInstr, wait=True)
# play (pceMIDI[intTrack].content, bpm=intBPM, instrument=intInstr)

# Analyis
str1 = mp.alg.detect (pceMIDI(intTrack)[nFrom:nTo])
str2 = mp.alg.chord_analysis (pceMIDI(intTrack))

str3 = mp.alg.detect (pceMIDI[intTrack].content[nFrom:nTo])

print (str1)
print (str2)
print (str3)
