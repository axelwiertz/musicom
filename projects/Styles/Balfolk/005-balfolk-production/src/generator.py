import numpy as np
import os
import subprocess
import sys

# Path to our synthesis scripts
sys.path.append('/opt/data/skills/devops/musicom-theory-kb/scripts')
from musicom_synthesis import render_wave
from pillar2_synthesis_engines import violin_synth, guitar_ks

# --- MARKOV TRANSITION MATRIX (G MAJOR FOLK) ---
# Transition probabilities to favor movement to adjacent scale degrees (jig feel)
transitions = {
    392.00: [440.00, 493.88, 587.33, 493.88, 392.00],    # G4
    440.00: [392.00, 493.88, 440.00, 392.00],           # A4
    493.88: [440.00, 523.25, 392.00, 523.25, 493.88],    # B4
    523.25: [493.88, 587.33, 523.25, 587.33],           # C5
    587.33: [392.00, 523.25, 659.25, 587.33],           # D5
    659.25: [587.33, 739.99, 659.25],                   # E5
    739.99: [659.25, 392.00]                             # F#5
}

def generate_markov_melody(start_freq, length):
    melody = [start_freq]
    curr = start_freq
    for _ in range(length - 1):
        # Pick from available transitions, fallback to Root
        curr = np.random.choice(transitions.get(curr, [392.00]))
        melody.append(curr)
    return melody

def main():
    sr = 44100
    bpm = 118
    # 6/8 Jig: 6 pulses (eighth notes) per measure
    pulse_dur = 60.0 / (bpm * 2) 
    measures = 16
    total_pulses = measures * 6
    
    # Intelligence: Generate 16 measures of melody
    melody = generate_markov_melody(392.00, total_pulses)
    
    track = []
    print(f"Synthesizing {measures} measures of Balfolk Markov Jig...")
    
    for i, freq in enumerate(melody):
        # Progress logging
        if i % 6 == 0:
            print(f"Processing Measure {i//6 + 1}/16")
            
        # Violin (Lead)
        v = violin_synth(freq, pulse_dur, sr)
        
        # Bass/rhythm management for 6/8 (Strength on 1 and 4)
        is_strong = (i % 3 == 0)
        # G3 or D3 for the bass
        g_freq = 196.00 if (i % 6 < 3) else 146.83
        
        g = guitar_ks(g_freq, pulse_dur, sr) * (0.85 if is_strong else 0.2)
        
        track.append(v + g)
        
    final = np.concatenate(track)
    # Normalize with headroom
    final = final / (np.max(np.abs(final)) + 1e-6) * 0.95
    
    out_dir = "/tmp/musicom/balfolk_full/"
    os.makedirs(out_dir, exist_ok=True)
    wav_path = out_dir + "full_markov_jig.wav"
    ogg_path = out_dir + "full_markov_jig.ogg"
    
    render_wave(final, wav_path)
    subprocess.run(f"ffmpeg -i {wav_path} -codec:a libopus -application voip -b:a 48k {ogg_path} -y -loglevel error", shell=True)
    print(f"RESULT_OGG:{ogg_path}")

if __name__ == "__main__":
    main()
