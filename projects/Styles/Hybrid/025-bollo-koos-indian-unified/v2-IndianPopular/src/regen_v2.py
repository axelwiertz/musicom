import mido
from mido import Message, MidiFile, MidiTrack

def create_midi():
    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)

    def add_note(pitch, duration, time=0, velocity=64):
        track.append(Message('note_on', note=pitch, velocity=velocity, time=time))
        track.append(Message('note_off', note=pitch, velocity=0, time=duration))

    # SECTION 1: Dutch Folk (Bollo berendans) - Pure
    # Simplified Bollo theme: D E F G | A G F E | D
    bollo_theme = [62, 64, 65, 67, 69, 67, 65, 64, 62]
    for p in bollo_theme:
        add_note(p, 240) # Quarter notes at 480 TPB

    # Gap
    track.append(Message('note_off', note=0, velocity=0, time=960))

    # SECTION 2: Dutch Folk (Koos/Roompot) - Pure
    # Roompot vibe (C-D-E-C jumpy)
    koos_theme = [60, 62, 64, 60, 64, 65, 67]
    for p in koos_theme:
        add_note(p, 240)

    # Gap
    track.append(Message('note_off', note=0, velocity=0, time=960))

    # SECTION 3: Popular Indian (Bollywood) - Rhythms & Pitch (Melisma + Percussive)
    # Typical Bollywood syncopation + Microtonal hints (represented by semitones)
    indian_theme = [62, 63, 62, 65, 66, 65, 69, 70, 69] # D, Eb, D, F, F#, F, A, Bb, A
    for p in indian_theme:
        add_note(p, 120, time=0) # Faster rhythm
        track.append(Message('note_off', note=0, velocity=0, time=60)) # Syncopated gap

    # Gap
    track.append(Message('note_off', note=0, velocity=0, time=960))

    # SECTION 4: BLENDED (Fusion)
    # Bollo theme with Indian Ornamentation + Bollywood Clave
    blended = [62, 63, 62, 64, 65, 67, 68, 67, 69, 70, 69]
    for p in blended:
        add_note(p, 120, velocity=80) 
        
    mid.save('../MIDI/025v2_blended.mid')

if __name__ == "__main__":
    create_midi()
