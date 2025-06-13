'''
Music - Template
'''

from datastructure import *

# Parts
dfForm = (16, 16, 16)

# Create a score
score = stream.Score()
# Create a stream
strStream01 = stream.Stream()
# Create a part object to represent a single instrumental or vocal part
part = stream.Part( )
# Create a part object to represent a bass part
bass_line = stream.Part()
# Create two voice objects to represent the melody and the harmony parts
voice1 = stream.Voice()
voice2 = stream.Voice()
# Create a list of notes
# C major scale
notes = ["C4", "D4", "E4", "F4", "G4", "A4", "B4", "C5"]
# Create a note object for each note and append it to voice
for notename in notes:
    melody_note = (note.Note(notename))
    voice1. append(melody_note)


# Select random pitch
intPitch = random.choice (lstPitchNr)
print (dfPitch.values[intPitch])



prtPart = stream.Part()
msrMeasure = stream.Measure()
msrMeasure.append(note.Note('C4'))
prtPart.append(note.Note('E4'))
prtPart.append(note.Note('G4'))
prtPart.append(note.Note('C5'))



# Create a scale
sclCM = scale.MajorScale ('c')
keyCM = key.Key ('C')

# Stream of all chord patterns
lstChordSeqs = lstChordPattern.copy()
strStream = stream.Stream ()

for i in range(1, len(lstChordSeqs)-1):
    strStream.append(note.Rest(quarterLength=2))
    for j in range (0, len(lstChordSeqs[i])):
        chdChord = roman.RomanNumeral (lstChordSeqs[i][j], keyCM)
        chdChord.duration.quarterLength = 2
        strStream.append(chdChord)

# Write stream
strStream.write('midi', fp='C:\\temp\\Music\\out.mid')


# All triads in a key
strStream = stream.Stream()
for i in range(intNrDegreeHeptaScale):
    chdChord = roman.RomanNumeral(i+1, keyCM)
    chdChord.duration.quarterLength = 2
    strStream.append(chdChord)
    strStream.append(note.Rest(quarterLength=2))

# Write stream
#show (strStream)
strStream.write('midi', fp='C:\\temp\\Music\\out.mid')

# Interval classes
lstPerfectIntervals = ('P1', 'P4', 'P5', 'P8')
lstImperfectIntervals = ('M2', 'm3', 'M3', 'm6', 'M6', 'm7', 'M7')


# Define a function to check if an interval is perfect
def is_perfect_interval(ivlInterval: interval.DiatonicInterval):
    return (ivlInterval.perfectable)


def generate_counterpoint(voice1, voice2):
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
show(s)





