import sys
import os
import mido

# Add musicom to path
sys.path.insert(0, '/root/musicom')
sys.path.insert(0, '/root/musicom_ai')

# Manual MIDI construction since Musicom paths are complex in this env
def create_laika_midi(path):
    mid = mido.MidiFile()
    track = mido.MidiTrack()
    mid.tracks.append(track)
    
    # Hijaz D4 scale fragment
    # D: 62, Eb: 63, F#: 66, G: 67, A: 69, Bb: 70, C: 72, D: 74
    hijaz = [62, 63, 66, 67, 69, 70, 72, 74]
    
    tempo = mido.bpm2tempo(120)
    track.append(mido.MetaMessage('set_tempo', tempo=tempo))
    track.append(mido.Message('program_change', program=105, time=0)) # Banjo for Bouzouki
    
    # 8 bars of Hasapiko rhythm (4/4)
    # Melodic motif: 1 2 3 4 | 5 4 3 2
    pattern = [0, 1, 2, 3, 4, 3, 2, 1]
    
    for bar in range(16):
        for i in range(4):
            note = hijaz[pattern[i + (bar*4 % 8)]]
            track.append(mido.Message('note_on', note=note, velocity=90, time=0))
            track.append(mido.Message('note_off', note=note, velocity=90, time=240))
            # rest
            track.append(mido.Message('note_on', note=note-12, velocity=60, time=0))
            track.append(mido.Message('note_off', note=note-12, velocity=60, time=240))
            
    mid.save(path)

PROJECT_NAME = "cretan-laika-daily-2026-06-07"
OUTPUT_DIR = f"/opt/data/projects/{PROJECT_NAME}"
os.makedirs(f"{OUTPUT_DIR}/MIDI", exist_ok=True)
create_laika_midi(f"{OUTPUT_DIR}/MIDI/composition.mid")
print(f"MIDI created: {OUTPUT_DIR}/MIDI/composition.mid")
