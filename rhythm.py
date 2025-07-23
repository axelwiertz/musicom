"""
Music - Rhythm
"""

from datastructure import *

# beat, rest, beat, beat, , , rest
rtm1 = (1.0, 0, 1.5, 1.5, 1, 1, 0)


# Create a stream for a rhythmic pattern
rhythmic_pattern = stream.Stream()
rhythmic_pattern.append(meter.TimeSignature('4/4'))

# Add notes and rests to the pattern
rhythmic_pattern.append(note.Note('C4', quarterLength=1.0))
rhythmic_pattern.append(note.Note('D4', quarterLength=0.5))
rhythmic_pattern.append(note.Rest(quarterLength=0.5))
rhythmic_pattern.append(note.Note('E4', quarterLength=1.0))
rhythmic_pattern.append(note.Rest(quarterLength=1.0))

# Show the rhythmic pattern
rhythmic_pattern.show('text')



# Rhythm library
# Four-beat rhythm
rhythmic_pattern = converter.parse('tinynotation: 4/4 c5 c5 c5 c5')

# Tresillo
tresillo_rhythmic_pattern = converter.parse('tinynotation: 4/4 c5 r r c5 r r c5 r')
# 12/8 Bell
twelve_8_bell_rhythmic_pattern = converter.parse('tinynotation: 12/8 c5 r c5 r c5 c5 r c5 r c5 r c5')
# Son Clave
sonclave_rhythmic_pattern = converter.parse('tinynotation: 16/8 c5 r r c5 r r c5 r r r c5 r c5 r r r')

show(sonclave_rhythmic_pattern)

# 3/4
waltz_rhythmic_pattern = converter.parse('tinynotation: 3/4 c5 c5 c5')




'''
Music 21 rhythm_and_duration
'''
rhythm_stream = stream.Stream()
rhythm_stream.insert(meter.TimeSignature('4/4'))
# A list representing the durations of notes in a rhythmic sequence
durations = [1.5, 0.5, 0.5, 0.25, 0.25, 1]
# Iterate over the list
for duration_value in durations:
    # Set the new duration to the current note value
    rhythm_stream.append(note.Note('C4', quarterLength=duration_value) )

# Insert a several new notes
new_note_1 = note.Note('C4', quarterLength=0.75 )
new_note_2 = note.Note('C4', quarterLength=0.25 )
rhythm_stream.insertAndShift([2, new_note_1, 2.75, new_note_2])

#show(rhythm_stream)
