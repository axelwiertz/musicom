
import sys
import numpy as np
import wave
import subprocess
import os

# Consolidated Library
sys.path.insert(0, '/opt/data/repos/musicom')
sys.path.append('/opt/data/skills/devops/musicom-theory-kb/scripts')

SAMPLE_RATE = 44100

def get_balfolk_scale():
    # Canonical Balfolk Dorian (MIDI pitches)
    return [62, 64, 65, 67, 69, 71, 72, 74]

def midi_to_hz(midi):
    return 440.0 * (2.0 ** ((midi - 69) / 12.0)) if midi > 0 else 0

def generate_grand_suite():
    from musicom_synthesis import render_wave 
    from pillar2_synthesis_engines import violin_synth, guitar_ks
    
    scale_midi = get_balfolk_scale()
    scale_hz = [midi_to_hz(m) for m in scale_midi]
    
    bpm = 118
    # 6/8
    pulse_dur = 60.0 / (bpm * 2) 
    
    # Sections (8 bars each = 48 pulses/section)
    # 1. Sparse Intro
    intro = [scale_hz[4], 0, 0, scale_hz[5], 0, 0] * 8
    
    # 2. Main Jig
    dance_indices = [0, 2, 4, 3, 3, 5]
    dance = []
    for _ in range(8):
        dance.extend([scale_hz[idx] for idx in dance_indices])
        
    # 3. Harmonic Bridge
    bridge_indices = [0, 3, 6, 2, 4, 1] 
    bridge = []
    for _ in range(8):
        bridge.extend([scale_hz[idx] for idx in bridge_indices])
        
    # 4. Fast Outro
    climax = [scale_hz[i % len(scale_hz)] for i in range(48)]
    
    full_melody = intro + dance + bridge + climax
    
    track = []
    print(f"Synthesizing Grand Suite (32 bars)...")
    
    for i, freq in enumerate(full_melody):
        if freq == 0:
            track.append(np.zeros(int(pulse_dur * SAMPLE_RATE)))
            continue
            
        # Lead
        v = violin_synth(freq, pulse_dur, SAMPLE_RATE)
        # Bass
        is_strong = (i % 3 == 0)
        b_freq = midi_to_hz(38) if (i % 6 < 3) else midi_to_hz(43)
        g = guitar_ks(b_freq, pulse_dur, SAMPLE_RATE) * (0.7 if is_strong else 0.1)
        
        track.append(v + g)
        
    final = np.concatenate(track)
    final = final / (np.max(np.abs(final)) + 1e-6) * 0.9
    
    out_dir = "/opt/data/projects/Styles/Balfolk/030-balfolk-grand-suite/Audio/"
    os.makedirs(out_dir, exist_ok=True)
    wav_path = out_dir + "grand_suite.wav"
    ogg_path = out_dir + "grand_suite.ogg"
    
    with wave.open(wav_path, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        audio_int16 = (np.clip(final, -1.0, 1.0) * 32767).astype(np.int16)
        wf.writeframes(audio_int16.tobytes())
        
    subprocess.run(f"ffmpeg -i {wav_path} -codec:a libopus -application voip -b:a 96k {ogg_path} -y -loglevel error", shell=True)
    return ogg_path

if __name__ == "__main__":
    try:
        path = generate_grand_suite()
        print(f"DONE:{path}")
    except Exception as e:
        print(f"ERROR:{e}")
        import traceback
        traceback.print_exc()
