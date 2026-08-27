import mido
from mido import Message, MidiFile, MidiTrack, MetaMessage

def text_to_midi(text, output_path, base_note=60, tempo=120):
    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)
    
    # 120 BPM
    tempo_val = mido.bpm2tempo(tempo)
    track.append(MetaMessage('set_tempo', tempo=tempo_val))
    
    # Basic mapping: 
    # . = long pause, ? = rising pitch, ! = high velocity
    words = text.split()
    current_note = base_note
    
    for word in words:
        clean_word = word.strip(",.?!")
        duration = 480 # Quarter note
        velocity = 80
        
        # Prosody Rules
        if word.endswith("?"):
            current_note += 2 # Rising interval
        elif word.endswith("."):
            duration = 960 # Half note
            current_note = base_note # Resolve to tonic
        elif "!" in word:
            velocity = 110 # Emphasize
            
        # Add note
        track.append(Message('note_on', note=current_note, velocity=velocity, time=0))
        track.append(Message('note_off', note=current_note, velocity=velocity, time=duration))
        
        # Reset relative shifts for next word unless structural
        if not word.endswith("?"):
            current_note = base_note + (len(clean_word) % 7) # Basic variation

    mid.save(output_path)

if __name__ == "__main__":
    test_text = "Is this a question? Yes it is! End of story."
    text_to_midi(test_text, "/opt/data/projects/Styles/Poetry/002-lyric-prosody-test/MIDI/prosody_test.mid")
