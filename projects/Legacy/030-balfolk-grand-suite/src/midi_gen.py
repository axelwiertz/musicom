
import sys
import os
import mido
import math

# Point to library
sys.path.insert(0, '/opt/data/repos/musicom')

def generate_030_midi():
    mid = mido.MidiFile()
    track_lead = mido.MidiTrack()
    track_bass = mido.MidiTrack()
    mid.tracks.append(track_lead)
    mid.tracks.append(track_bass)
    
    # 118 BPM
    tempo = mido.bpm2tempo(118)
    track_lead.append(mido.MetaMessage('set_tempo', tempo=tempo))
    track_lead.append(mido.MetaMessage('track_name', name='Violin Lead'))
    track_bass.append(mido.MetaMessage('track_name', name='Guitar Bass'))
    
    # Scale indices (D Dorian)
    scale = [62, 64, 65, 67, 69, 71, 72, 74]
    
    ticks_per_pulse = 240 # Eighth note in mido default (480 tpb)
    
    # 1. Intro
    intro = [scale[4], 0, 0, scale[5], 0, 0] * 8
    # 2. Main Jig
    dance_indices = [0, 2, 4, 3, 3, 5]
    dance = []
    for _ in range(8):
        dance.extend([scale[idx] for idx in dance_indices])
    # 3. Bridge
    bridge_indices = [0, 3, 6, 2, 4, 1] 
    bridge = []
    for _ in range(8):
        bridge.extend([scale[idx] for idx in bridge_indices])
    # 4. Outro
    climax = [scale[i % len(scale)] for i in range(48)]
    
    full_melody = intro + dance + bridge + climax
    
    # Lead Rendering
    time_accum = 0
    for p in full_melody:
        if p == 0:
            time_accum += ticks_per_pulse
            continue
        track_lead.append(mido.Message('note_on', note=p, velocity=90, time=time_accum))
        track_lead.append(mido.Message('note_off', note=p, velocity=0, time=ticks_per_pulse))
        time_accum = 0
        
    # Bass Rendering (Pulse 1 and 4)
    time_accum_b = 0
    for i in range(len(full_melody)):
        is_strong = (i % 3 == 0)
        if not is_strong:
            time_accum_b += ticks_per_pulse
            continue
            
        p_bass = 38 if (i % 6 < 3) else 43 # D2 or G2
        track_bass.append(mido.Message('note_on', note=p_bass, velocity=100, time=time_accum_b))
        track_bass.append(mido.Message('note_off', note=p_bass, velocity=0, time=ticks_per_pulse))
        time_accum_b = 0

    out_path = "/opt/data/projects/Styles/Balfolk/030-balfolk-grand-suite/MIDI/grand_suite.mid"
    mid.save(out_path)
    return out_path

if __name__ == "__main__":
    p = generate_030_midi()
    print(f"DONE:{p}")
