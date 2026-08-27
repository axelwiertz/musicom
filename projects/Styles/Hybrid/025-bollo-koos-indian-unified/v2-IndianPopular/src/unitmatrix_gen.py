import mido
import numpy as np
from mido import Message, MidiFile, MidiTrack

def create_rich_midi():
    mid = MidiFile()
    
    # 3 Voices: Melody (Piano), Rhythm Accent (Sitar-ish/Synth), Drone (Tanpura-ish)
    voice_melody = MidiTrack()
    voice_rhythm = MidiTrack()
    voice_drone = MidiTrack()
    mid.tracks.extend([voice_melody, voice_rhythm, voice_drone])

    def add_note(track, pitch, duration, time=0, vel=64):
        track.append(Message('note_on', note=pitch, velocity=vel, time=time))
        track.append(Message('note_off', note=pitch, velocity=0, time=duration))

    # UnitMatrix Logic: 4 Measures, 4 beats each (total 16 units)
    # Unit 1-4: Bollo (Dutch)
    # Unit 5-8: Koos (Dutch)
    # Unit 9-12: Indian (Ornamented)
    # Unit 13-16: Blended (Fusion)

    # Bollo: D-E-F-D (Simple)
    melody_pitches = [62, 64, 65, 62] 
    # Koos: C-G-E-C (Jumpy)
    melody_pitches += [60, 67, 64, 60]
    # Indian: D-Eb-D-F-F#-G-F (Chromatic Ornament)
    melody_pitches += [62, 63, 62, 66] 
    # Blended: Bollo Theme with Indian Ornamentation
    melody_pitches += [62, 63, 65, 66]

    # Render Melody
    for p in melody_pitches:
        add_note(voice_melody, p, 480) # Quarter notes

    # Render Indian Rhythm DNA (Clave) on Rhythm Track
    # Bollywood Clave: █ ░ █ █ ░ █ ░ ░ (3+2+3 feel)
    clave = [1, 0, 1, 1, 0, 1, 0, 0] * 2
    for strike in clave:
        if strike:
            add_note(voice_rhythm, 42, 120, vel=80) # Percussive pitch
        else:
            voice_rhythm.append(Message('note_off', note=0, velocity=0, time=120))

    # Drone: Constant D2
    for _ in range(8):
        add_note(voice_drone, 38, 960, vel=30)

    mid.save('../MIDI/025v2_unitmatrix.mid')

if __name__ == "__main__":
    create_rich_midi()
