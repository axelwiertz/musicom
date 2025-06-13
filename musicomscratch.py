from music21 import stream, key, meter, note

# Create a stream to hold the musical elements
stream = stream.Stream()

# Create a series of notes
note1 = note.Note("C4", quarterLength=1.0)
note2 = note.Note("D4", quarterLength=1.0)
note3 = note.Note("E4", quarterLength=1.0)
note4 = note.Note("F4")

# Add the notes to the stream
stream.append(note1)
stream.append(note2)
stream.append(note3)
stream.append(note4)

# Set the time signature and key signature
stream.insert(0, meter.TimeSignature("4/4"))
stream.insert(0, key.Key("C"))

# Transpose the phrase up by a major third
transposed_stream = stream.transpose("M3")

# Display the musical score
print (transposed_stream)
print (note4)
stream.show ('MIDI')
