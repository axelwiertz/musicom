from music21 import stream

'''
Music - Rhythm
'''
# modules
import datastructure
#from musicpy import *
#from musicpy.daw import *


# rhythm b = beat 0 = rest - = continue . = dotted
rtm1 = rhythm('b - b. b. b b -', 1)

from music21 import note, stream

# Create a stream for a rhythmic pattern
rhythmic_pattern = stream.Stream()
time_sig_stream.append(meter.TimeSignature('4/4'))

# Add notes and rests to the pattern
rhythmic_pattern.append(note.Note('C4', quarterLength=1.0))
rhythmic_pattern.append(note.Note('D4', quarterLength=0.5))
rhythmic_pattern.append(note.Rest(quarterLength=0.5))
rhythmic_pattern.append(note.Note('E4', quarterLength=1.0))
rhythmic_pattern.append(note.Rest(quarterLength=1.0))

# Show the rhythmic pattern
rhythmic_pattern.show('text')

rhythmic_info = rhythm.RhythmAnalyzer(rhythmic_stream)
rhythmic_info.getRhythm()

# Show the rhythmic information
print(rhythmic_info.getRhythm())

# Rhythm library
# Simple
rtmSimple = rhythm('b b b b', 1, time_signature=[4, 4])
# Tresillo
rtmTresillo = rhythm('b 0 0 b - 0 b 0', 1, beats=8, time_signature=[4, 4])
# 12/8 Bell
rtmBell = rhythm('b 0 b 0 b b 0 b 0 b 0 b', 1, beats=12, time_signature=[12, 8] )
# Son Clave
rtmSonClave = rhythm('b 0 0 b 0 0 b 0 0 0 b 0 b 0 0 0', 1, beats=16)

# 3/4
rtmWaltz = rhythm('b b b', 1, beats=3, time_signature=[3, 4] )

print (rtmTresillo)

rtmSong = rtmBell
chd01 = chord('C4', 1/8, 1/8)*7
chd02 = chd01.apply_rhythm (rtmSong)
play(chd02, wait=True)

'''
lstChdTrack = []
lstIntChannel = []
lstChdTrack.append (chd01.apply_rhythm (rtmSong))
lstIntChannel.append (1)
lstChdTrack.append (chdRhythm.apply_rhythm (rtmSong))
lstIntChannel.append (9)
'''

'''
Music 21 rhythm_and_duration
'''
s = stream.Stream()
s.insert(meter.TimeSignature('4/4'))
# A list representing the durations of notes in a rhythmic sequence
notes_values = [1.5, 0.5, 0.5, 0.25, 0.25, 1]
# Iterate over the list
for note_value in notes_values:
    # Set the new duration to the current note value
    s.append(note.Note('C4', duration=duration.Duration(note_value)) )
    #Insert a several new notes
    new_note_1 = note.Note('C4', duration=duration.Duration(0.75) )
    new_note_2 = note.Note('C4', duration=duration.Duration(0.25) )
    s.insertAndShift([2, new_note_1, 2.75, new_note_2])

s. show()
