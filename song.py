'''
Music - Template
'''
import music21.scale
from music21 import stream
from music21 import scale

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
    melody_note = (note.Note(notename))
    voice1. append(melody_note)


# Select random pitch
intPitch = random.choice (lstPitchNr)
print (dfPitch.values[intPitch])

# Parts
dfForm = (16, 16, 16)


strStream01 = stream.Stream()
prtPart = stream.Part()
msrMeasure = stream.Measure()
msrMeasure.append(note.Note('C4'))
prtPart.append(note.Note('E4'))
prtPart.append(note.Note('G4'))
prtPart.append(note.Note('C5'))


strSongName = 'Patterns'

# Scale
#scl01 = S(str(dctStyleScale['Standard'][0]))
sclScale01 = scale.Scale
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


def generate_counterpoint(voice1, voice2):
    # Ensure the voices are of the same length
    if len(voice1) != len(voice2):
        raise ValueError("Voices must be of the same length")

    # Check for parallel perfect intervals
    for i in range(len(voice1) - 1):
        intv1 = interval.Interval(voice1[i], voice1[i + 1])
        intv2 = interval.Interval(voice2[i], voice2[i + 1])
        if intv1.isPerfect and intv2.isPerfect and intv1.direction == intv2.direction:
            return False

    # Check for hidden parallels
    for i in range(len(voice1) - 1):
        intv1 = interval.Interval(voice1[i], voice1[i + 1])
        intv2 = interval.Interval(voice2[i], voice2[i + 1])
        if intv1.isPerfect and intv2.isPerfect and intv1.direction == intv2.direction:
            return False

    # Check for crossing voices
    for i in range(len(voice1)):
        if voice1[i].pitch < voice2[i].pitch and voice1[i + 1].pitch > voice2[i + 1].pitch:
            return False

    return True

def create_random_voice(length):
    voice = []
    for _ in range(length):
        pitch = random.choice(range(60, 72))  # C4 to B4
        duration = random.choice([0.5, 1, 2])
        n = note.Note(pitch, quarterLength=duration)
        voice.append(n)
    return voice

length = 16  # Length of the counterpoint
voice1 = create_random_voice(length)
voice2 = create_random_voice(length)

while not generate_counterpoint(voice1, voice2):
    voice2 = create_random_voice(length)

# Create a stream to hold the voices
s = stream.Stream()
s.append(voice1)
s.append(voice2)

# Show the counterpoint
s.show('text')





