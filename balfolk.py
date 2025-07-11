from music21 import *
import random

def create_balfolk_melody():
    # Create a score
    score = stream.Score()
    
    # Create parts for melody and accompaniment
    melody_part = stream.Part()
    accompaniment_part = stream.Part()
    
    # Set key and time signature typical of Balfolk
    key_signature = key.KeySignature(0)  # C major/A minor
    time_signature = meter.TimeSignature('6/8')
    
    melody_part.append(key_signature)
    melody_part.append(time_signature)
    accompaniment_part.append(key_signature)
    accompaniment_part.append(time_signature)
    
    # Bourrée-inspired melody (typical Balfolk rhythm)
    melody_notes = [
        ['C4', 'E4', 'G4'],
        ['D4', 'F4', 'A4'],
        ['E4', 'G4', 'B4'],
        ['F4', 'A4', 'C5']
    ]
    
    # Create melody with rhythmic variation
    for i in range(16):  # 4 measures
        # Choose a random melodic fragment
        fragment = random.choice(melody_notes)
        
        # Create notes with Balfolk-style rhythm
        for note_name in fragment:
            n = note.Note(note_name)
            n.duration.type = 'eighth'
            melody_part.append(n)
    
    # Create accompaniment (drone/rhythmic support)
    bass_notes = ['C3', 'G3']
    for i in range(32):  # matching melody length
        bass_note = note.Note(random.choice(bass_notes))
        bass_note.duration.type = 'eighth'
        accompaniment_part.append(bass_note)
    
    # Add parts to score
    score.insert(0, melody_part)
    score.insert(0, accompaniment_part)
    
    return score

# Generate and show the Balfolk-inspired composition
score = create_balfolk_melody()
strPathOut = 'C:\\temp\\Music\\'
score.write('midi', fp=strPathOut+'target.mid')

score.show('text')
# Play the result (IOS):
#player = sound.MIDIPlayer('target.mid')
#player.play()
#player.stop()
score.show('midi')  # Play MIDI
score.show()  # Show musical notation
