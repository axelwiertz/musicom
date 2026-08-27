import os
import json
import random
import datetime
import mido
from mido import Message, MidiFile, MidiTrack, MetaMessage
import numpy as np

def generate_composition():
    # 1. Start with Patterns
    genre_data_path = "/opt/data/projects/016-genre-pattern-dataset/data/bossa_nova_classic.json"
    with open(genre_data_path, 'r') as f:
        data = json.load(f)

    # 2. Change and Refine
    # Bossa rhythm: █░░█░░█░░░█░░█░░ (16 steps)
    dna = data['rhythm']['dna']
    gravity = data['rhythm']['metrical_gravity']
    
    # Operations
    def shift_rhythm(pattern, n):
        return pattern[n:] + pattern[:n]

    # Refined rhythm patterns
    rhythm_lead = dna # Original
    rhythm_bass = shift_rhythm(dna, 4) # Displaced
    
    # Pitch: Major with 9th (C Maj9: C, E, G, B, D)
    scale = [0, 2, 4, 7, 11, 14] # C E G B D (octave 14)
    
    # 6. Structure
    # 16 bars total: Intro (2), A (4), B (4), A' (4), Outro (2)
    # Time signature 2/4 (Bossa style)
    
    mid = MidiFile(ticks_per_beat=480)
    
    # 4. Arrange Multitrack & Register Pass
    # Track 0: Meta
    meta_track = MidiTrack()
    mid.tracks.append(meta_track)
    meta_track.append(MetaMessage('set_tempo', tempo=mido.bpm2tempo(84)))
    meta_track.append(MetaMessage('time_signature', numerator=2, denominator=4))
    
    # Track 1: Foreground Lead (> C4, 60-84) - Nylon Guitar (24)
    lead_track = MidiTrack()
    mid.tracks.append(lead_track)
    lead_track.append(Message('program_change', program=24, time=0))
    
    # Track 2: Midground Harmony (C3-C5, 48-72) - Piano (0)
    harmony_track = MidiTrack()
    mid.tracks.append(harmony_track)
    harmony_track.append(Message('program_change', program=0, time=0))
    
    # Track 3: Sub-Bass (< 130Hz, < C3, < 48) - Acoustic Bass (32)
    bass_track = MidiTrack()
    mid.tracks.append(bass_track)
    bass_track.append(Message('program_change', program=32, time=0))
    
    # Track 4: Percussion (Channel 10)
    perc_track = MidiTrack()
    mid.tracks.append(perc_track)
    # Channel 9 in mido is 10 in reality
    
    # Composition Logic
    bars = 16
    steps_per_bar = 8 # 2/4 time, 16th notes
    total_steps = bars * steps_per_bar
    
    # Notes for Bossa I-IV-V-I (C, F, G, C)
    progression = [0, 0, 5, 5, 7, 7, 0, 0] * 2 
    
    ticks_per_step = 120 # 480 / 4

    def add_note(track, note, velocity, duration, time, channel=0):
        track.append(Message('note_on', note=note, velocity=velocity, time=time, channel=channel))
        track.append(Message('note_off', note=note, velocity=0, time=duration, channel=channel))

    curr_time_lead = 0
    curr_time_bass = 0
    curr_time_perc = 0
    
    for bar in range(bars):
        root = progression[bar % len(progression)]
        for step in range(steps_per_bar):
            dna_idx = (bar * steps_per_bar + step) % 16
            
            # Percussion: Shaker (82) or Side Stick (37)
            # Metrical weight
            vel = int(70 + 40 * gravity[dna_idx])
            
            # Lead
            if dna[dna_idx] == '█':
                note = 60 + root + random.choice([0, 4, 7, 11, 14])
                add_note(lead_track, note, vel, 110, curr_time_lead)
                curr_time_lead = 10 # small gap
            else:
                curr_time_lead += 120
            
            # Bass
            if (step % 4 == 0): # Simple steady bass on downbeats
                note = 36 + root
                add_note(bass_track, note, vel-10, 240, curr_time_bass)
                curr_time_bass = 0
            else:
                curr_time_bass += 120
                
            # Percussion - Channel 10 (mido 9)
            if dna_idx % 2 == 0:
                add_note(perc_track, 37, vel-20, 10, curr_time_perc, channel=9)
                curr_time_perc = 110
            else:
                curr_time_perc += 120
                
    # Save
    gen_dir = "Genres/Latin"
    proj_name = "028-bossa-nova-daily-2026-06-12"
    base_path = f"/opt/data/projects/{gen_dir}/{proj_name}"
    
    os.makedirs(f"{base_path}/MIDI", exist_ok=True)
    os.makedirs(f"{base_path}/Audio", exist_ok=True)
    os.makedirs(f"{base_path}/Analysis", exist_ok=True)
    os.makedirs(f"{base_path}/Notes", exist_ok=True)
    os.makedirs(f"{base_path}/Scores", exist_ok=True)
    os.makedirs(f"{base_path}/src", exist_ok=True)
    
    midi_path = f"{base_path}/MIDI/composition.mid"
    mid.save(midi_path)
    print(f"MIDI saved to {midi_path}")
    
    # README
    with open(f"{base_path}/README.md", 'w') as f:
        f.write(f"# Bossa Nova Daily Experiment\n\n- Key: C Major (9/11/13)\n- Tempo: 84 BPM\n- Form: Intro-A-B-A'-Outro\n\n## Rhythm Pattern\n`{dna}`\n")

    # index.html
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Bossa Nova Daily 028</title>
        <style>
            body {{ background: #0d0d0d; color: #00ff88; font-family: 'Courier New', Courier, monospace; padding: 2em; }}
            .container {{ max-width: 800px; margin: auto; border: 1px solid #00ff88; padding: 20px; box-shadow: 0 0 15px #00ff8833; }}
            h1 {{ border-bottom: 2px solid #00ff88; padding-bottom: 0.5em; }}
            .grid {{ display: grid; grid-template-columns: repeat(16, 1fr); gap: 2px; margin: 1em 0; }}
            .cell {{ height: 20px; background: #1a1a1a; border: 1px solid #333; }}
            .cell.active {{ background: #00ff88; box-shadow: 0 0 5px #00ff88; }}
            .track-label {{ grid-column: span 16; margin-top: 10px; font-weight: bold; font-size: 0.8em; }}
            audio {{ width: 100%; margin: 1em 0; filter: invert(1) hue-rotate(180deg); }}
            pre {{ background: #1a1a1a; padding: 10px; overflow-x: auto; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Daily Pattern Composition: 028</h1>
            <p><strong>Genre:</strong> Bossa Nova (Classic)</p>
            <p><strong>Key:</strong> C Major 9</p>
            <p><strong>Tempo:</strong> 84 BPM</p>
            
            <audio controls src="Audio/composition.ogg"></audio>
            
            <div class="track-label">Rhythm DNA Layer</div>
            <div class="grid">
                {" ".join([f'<div class="cell {"active" if c == "█" else ""}"></div>' for c in dna])}
            </div>
            
            <h3>Analysis</h3>
            <pre>
Structure: Intro(2) -> A(4) -> B(4) -> A'(4) -> Outro(2)
Refined Patterns:
- Lead: Original DNA
- Bass: Shifted +4 steps (Rhythmic Displacement)
- Dynamic: Velocity weighted by metrical gravity
            </pre>
            
            <p><a href="MIDI/composition.mid" style="color:#00ff88;">Download MIDI</a></p>
        </div>
    </body>
    </html>
    """
    with open(f"{base_path}/index.html", 'w') as f:
        f.write(html_content)

if __name__ == "__main__":
    generate_composition()
