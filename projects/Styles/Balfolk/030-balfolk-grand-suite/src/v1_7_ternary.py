
import sys
import numpy as np
import wave
import subprocess
import os

sys.path.insert(0, '/opt/data/repos/musicom')
sys.path.append('/opt/data/skills/devops/musicom-theory-kb/scripts')

SAMPLE_RATE = 44100
BPM = 118
PULSE_DUR = 60.0 / (BPM * 2) 

def midi_to_hz(midi):
    return 440.0 * (2.0 ** ((midi - 69) / 12.0)) if midi > 0 else 0

def render_v1_7_ternary():
    from pillar2_synthesis_engines import violin_synth, guitar_ks, piano_synth
    
    scale_midi = [62, 64, 65, 67, 69, 71, 72, 74] 
    scale_hz = [midi_to_hz(m) for m in scale_midi]
    
    # 3-bar sections (18 pulses). Total structure: AABBCCDD = 8 parts.
    # Plus 1 bar rest after AA, BB, CC, DD? 
    # User said "1 bar without melody between parts" -> A(3) A(3) [Rest 1] B(3) B(3) [Rest 1] ...
    
    parts = {
        'A': [scale_hz[0], scale_hz[2], scale_hz[4], scale_hz[3], scale_hz[5], scale_hz[4]] * 3,
        'B': [scale_hz[7], scale_hz[5], scale_hz[4], scale_hz[6], scale_hz[4], scale_hz[2]] * 3,
        'C': [scale_hz[4], scale_hz[3], scale_hz[2], scale_hz[0], scale_hz[1], scale_hz[0]] * 3,
        'D': [scale_hz[0], scale_hz[4], scale_hz[7], 0, scale_hz[4], scale_hz[2]] * 3
    }
    
    # Sequence Construction
    full_melody = []
    for p in ['A', 'A']: full_melody.extend(parts[p]); full_melody.extend([0]*6)
    for p in ['B', 'B']: full_melody.extend(parts[p]); full_melody.extend([0]*6)
    for p in ['C', 'C']: full_melody.extend(parts[p]); full_melody.extend([0]*6)
    for p in ['D', 'D']: full_melody.extend(parts[p]); full_melody.extend([0]*6)
    
    total_pulses = len(full_melody)
    final_mix = np.zeros(int(total_pulses * PULSE_DUR * SAMPLE_RATE) + 100)
    
    for i in range(total_pulses):
        start = int(i * PULSE_DUR * SAMPLE_RATE)
        t = PULSE_DUR
        
        # 1. Lead (Violin)
        if full_melody[i] > 0:
            sig = violin_synth(full_melody[i], t, SAMPLE_RATE) * 0.4
            final_mix[start:start+len(sig)] += sig
            
        # 2. Piano (Syncopated Chords)
        if i % 6 in [0, 3]:
            # Chord every half-bar
            p_hz = [scale_hz[0], scale_hz[2], scale_hz[4]] if (i//18)%2 == 0 else [scale_hz[3], scale_hz[5], scale_hz[0]]
            for hz in p_hz:
                p_sig = piano_synth(hz, t*2, SAMPLE_RATE) * 0.1
                final_mix[start:start+len(p_sig)] += p_sig

        # 3. Bass (Acoustic Guitar)
        # Keeps playing during melody rests
        root = 38 if (i // 18) % 2 == 0 else 43
        if i % 3 == 0:
            b_sig = guitar_ks(midi_to_hz(root), t, SAMPLE_RATE) * 0.4
            final_mix[start:start+len(b_sig)] += b_sig
            
        # 4. Percussion (Tapan)
        # Keeps playing during melody rests
        if i % 6 == 0: # Beat 1
            kick = np.sin(2 * np.pi * 60 * np.linspace(0, t, int(t * SAMPLE_RATE))) * np.exp(-12 * np.linspace(0, 1, int(t * SAMPLE_RATE)))
            final_mix[start:start+len(kick)] += kick * 0.5
        if i % 6 == 3: # Beat 4
            snare = (np.random.rand(int(t * SAMPLE_RATE)) * 2 - 1) * np.exp(-40 * np.linspace(0, 1, int(t * SAMPLE_RATE)))
            final_mix[start:start+len(snare)] += snare * 0.3

    final_mix = final_mix / (np.max(np.abs(final_mix)) + 1e-6) * 0.9
    ogg_path = "/opt/data/projects/Styles/Balfolk/030-balfolk-grand-suite/Audio/grand_suite_v1_7.ogg"
    temp_wav = "/tmp/v1_7.wav"
    with wave.open(temp_wav, 'w') as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SAMPLE_RATE)
        wf.writeframes((np.clip(final_mix, -1.0, 1.0) * 32767).astype(np.int16).tobytes())
    subprocess.run(f"ffmpeg -i {temp_wav} -codec:a libopus -b:a 128k {ogg_path} -y -loglevel error", shell=True)
    return ogg_path

print(f'DONE:{render_v1_7_ternary()}')