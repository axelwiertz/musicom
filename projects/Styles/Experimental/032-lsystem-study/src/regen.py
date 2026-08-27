#!/usr/bin/env python3
import os
import sys
import random

# Force project root into path
sys.path.insert(0, '/opt/data/repos')

from musicom.structures.unit import MusicUnit, MusicEvent
from musicom.workflows.unitmatrix_composer import UnitMatrixComposer

# Create Project Directory
project_dir = "/opt/data/projects/Styles/Experimental/032-lsystem-study"
os.makedirs(f"{project_dir}/MIDI", exist_ok=True)
os.makedirs(f"{project_dir}/Audio", exist_ok=True)
os.makedirs(f"{project_dir}/Scores", exist_ok=True)

# 1. L-System Grammar Rules & Expansion
# Axiom (Starting string)
axiom = "F"
# Production Rules:
# F -> F+F-F-F+F (Koch-like curve applied to melodic intervals)
rules = {
    "F": "F+F-F-F+F"
}

def expand_lsystem(axiom, rules, iterations):
    current = axiom
    for _ in range(iterations):
        next_str = ""
        for char in current:
            next_str += rules.get(char, char)
        current = next_str
    return current

# Expand 3 iterations to get a complex string pattern
lsystem_string = expand_lsystem(axiom, rules, 3)
print(f"L-System String (Length {len(lsystem_string)}): {lsystem_string[:50]}...")

# 2. Interpretation & Pitch Generation
# Map characters to interval movements or actions
# 'F' -> Step forward (play active note)
# '+' -> Transpose pitch up by a major second (2 semitones)
# '-' -> Transpose pitch down by a minor third (3 semitones)
current_pitch = 60 # Start on C4
pitches = []

for char in lsystem_string:
    if char == "F":
        pitches.append(current_pitch)
    elif char == "+":
        current_pitch += 2
    elif char == "-":
        current_pitch -= 3
    
    # Clip pitch boundaries
    current_pitch = max(36, min(84, current_pitch))

# 3. Setup Composer
TPB = 480
TEMPO_BPM = 110
BAR_TICKS = TPB * 4

composer = UnitMatrixComposer(
    bpm=TEMPO_BPM,
    ticks_per_beat=TPB,
    beats_per_bar=4
)

# 2 rows (Melody, Accompanying Drone) x 8 sections (bars)
composer.create_matrix(num_voices=2, num_sections=8)
composer.add_voice("L-Melody", program=80, channel=0) # Lead Synth
composer.add_voice("Drone", program=88, channel=1)    # Pad Synth

for col in range(8):
    composer.add_section(f"Bar {col+1}", bars=1)

# Generate algorithmic notes from L-System
for col in range(8):
    # Slice pitches for this bar (8 events per bar -> eighth notes)
    bar_pitches = pitches[col*8 : (col+1)*8]
    while len(bar_pitches) < 8:
        bar_pitches.append(60) # fallback/pad
        
    melody_events = []
    for step in range(8):
        pitch = bar_pitches[step]
        start_tick = step * 240
        end_tick = BAR_TICKS if step == 7 else (step + 1) * 240 - 15
        
        # Humanize slightly
        h_start = max(step * 240, start_tick + random.randint(-4, 4))
        if step == 7:
            h_end = BAR_TICKS
        else:
            h_end = max(h_start + 40, end_tick + random.randint(-4, 4))
            
        melody_events.append(MusicEvent(pitch=pitch, start_tick=int(h_start), end_tick=int(h_end), volume=90))
        
    composer.set_unit(0, col, MusicUnit(events=melody_events))

    # Static ambient supporting drone in voice 1
    drone_events = [
        MusicEvent(pitch=48, start_tick=0, end_tick=BAR_TICKS, volume=60) # C3 drone
    ]
    composer.set_unit(1, col, MusicUnit(events=drone_events))

# Validate and Export
composer.validate()
midi_out = f"{project_dir}/MIDI/lsystem_study.mid"
composer.to_midi(midi_out)
print(f"MIDI Export Complete: {midi_out}")
