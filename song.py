'''
Music - Template
'''
from music21 import stream

from datastructure import *

import random

score = stream.Score()
# Create a part object to represent a single instrumental or vocal part
part = stream.Part( )
# Create a part object to represent a bass part
bass_line = stream.Part()
#Create two voice objects to represent the melody and the harmony parts
voice1 = stream.Voice()
voice2 = stream.Voice()
# Define a list of notenames that make up a C major scale
notes = ["C4", "D4", "E4", "F4", "G4", "A4", "B4", "C5"]
# Create a note object for each note and append it to voice
for notename in notes:
    melody_note = note.Note(notename)
    voice1. append(melody_note)


# Select random pitch
intPitch = random.choice (lstPitchNr)
print (dfPitch.values[intPitch])

# Parts
dfForm = pd.DataFrame ([16, 16, 16])
dfParts = pd.DataFrame ([[1, 16],
    [2, 16],
    [3, 16]])


strStream01 = m21.stream.Stream()
prtPart = music21.stream.Part
strStream01.append(m21.note.Note('C4'))
strStream01.append(m21.note.Note('E4'))
strStream01.append(m21.note.Note('G4'))
strStream01.append(m21.note.Note('C5'))


strSongName = 'Patterns'

# Scale
#scl01 = S(str(dctStyleScale['Standard'][0]))

scl01 = mp.S('C major')
# All chord patterns
lstChord01 = lstChordPattern
chd01 = scl01.chord_progression(lstChord01[0])
for i in range(1, len(lstChordPattern)-1):
#    print (lstChordPattern[i])
    chd02 = scl01.chord_progression(lstChord01[i], durations=1 / 2, intervals=0, volumes=None, chords_interval=None)
    chd01 = chd01 + mp.rest(1/2) + chd02

# All chords
lstChdScale = scl01%(1234567, 0.5)
chd01 = lstChdScale[0]
for i in range(1, 7):
#    print (lstChordPattern[i])
    chd01 = chd01 + mp.rest(1/2) + lstChdScale[i]



#print (chd01)
#play (chd01, wait=True)

# Output
lstChdTrack = [chd01] # list of tracks
lstIntChannel = [1] # list of channelnumbers
lstIntStartTimes = [0] # list of starttimes


'''
chd01 = chord('C4', 1/8, 1/8)*100
lstChdTrack = []
lstIntChannel = []
lstChdTrack.append (chd01.apply_rhythm (rtmSong))
lstIntChannel.append (1)
lstChdTrack.append (chdRhythm.apply_rhythm (rtmSong))
lstIntChannel.append (9)
'''






