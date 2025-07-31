"""
Music - Rhythm
"""

from datastructure import *

"""
Rhythm of beats and rests with durations in a measure
"""
BEAT_REST = 1
DURATION = 2
BT = 'b'
RS = 'r'

stream_rhythm = create_rhythmic_stream (rtm1)

def create_rhythmic_stream (measure_pattern, signature : meter.TimeSignature = meter.TimeSignature('4/4')) -> stream.Stream[]
    # Create a stream for a rhythmic pattern
    rhythmic_stream = stream.Stream()
    rhythmic_stream.append(signature)

    measure_length = 0
    for i in len(measure_pattern-1)
        # Add beats and rests to the pattern
        measure_length += measure_pattern [DURATION][i]
        if measure_pattern [BEAT_REST][i] = BT
            rhythmic_stream.append(note.Note('C4', quarterLength=measure_pattern [DURATION][i]))

        if measure_pattern[BEAT_REST][i] = RS
            rhythmic_stream.append(note.Rest(quarterLength=measure_pattern [DURATION][i]))

    return rhythmic_pattern

rtm1 = [
    [BT, RS, BT, BT,BT, BT, RS],
    [1.0, 1.0, 1.5, 1.5, 1.0, 1.0, 1.0]
]


# Rhythm library
# Four-beat rhythm
four_rhythmic_pattern = converter.parse('tinynotation: 4/4 c5 c5 c5 c5')
four_rtm = [
    [BT, BT, BT, BT],
    [1.0, 1.0, 1.0, 1.0]
]

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
