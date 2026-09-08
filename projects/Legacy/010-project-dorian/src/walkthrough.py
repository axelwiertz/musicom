import numpy as np
import sys
import os

# Import our synthesis engine logic
sys.path.append('/opt/data/skills/devops/musicom-theory-kb/scripts')
from musicom_synthesis import render_wave, generate_subtractive_synth, generate_euclidean_percussion

def project_dorian_example():
    print("--- Phase 1: The Seed ---")
    root = 62 # D4
    scale = [0, 2, 3, 5, 7, 9, 10] # Dorian: 1 2 b3 4 5 6 b7
    pitches = [root + p for p in scale]
    print(f"Project: Dorian Example (Root D, Scale D-Dorian)")

    print("--- Phase 2: Pillars (Generation) ---")
    # Pillar 1: Harmonic progression (i7 -> IV7 -> i7 -> V7)
    # Dm7, G7, Dm7, Am7
    progression = [
        [62, 65, 69, 72], # Dm7
        [67, 71, 74, 77], # G7
        [62, 65, 69, 72], # Dm7
        [69, 72, 76, 79]  # Am7
    ]
    
    # Pillar 2: Rhythm (Euclidean 3,8 groove)
    bpm = 124
    
    print("--- Phase 3: Synthesis & Audition ---")
    sample_rate = 44100
    ensemble = []
    
    # Generate Chord Beds
    chord_audio = []
    for chord in progression:
        chord_audio.extend(generate_subtractive_synth(chord, duration=1.0)) # 1 second per chord
    
    # Generate Percussion (Tresillo 3,8)
    percussion = []
    for _ in range(4): # 4 bars
        percussion.extend(generate_euclidean_percussion(3, 8, bpm=bpm))
    
    # Mix (Scale to ensure chord_audio and percussion are aligned)
    min_len = min(len(chord_audio), len(percussion))
    mixed = (np.array(chord_audio[:min_len]) * 0.4) + (np.array(percussion[:min_len]) * 0.3)
    
    output_path = "/opt/data/projects/010-project-dorian/dorian_audition.wav"
    render_wave(mixed, output_path)
    print(f"Audition rendered to: {output_path}")

if __name__ == "__main__":
    project_dorian_example()
