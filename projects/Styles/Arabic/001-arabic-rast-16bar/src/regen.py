#!/usr/bin/env python3
import os
import sys
import random

# Force project root into path
sys.path.insert(0, '/opt/data/repos')

# Import core classes
from musicom.structures.unit import MusicUnit, MusicEvent
from musicom.workflows.unitmatrix_composer import UnitMatrixComposer

project_dir = "/opt/data/projects/Styles/Arabic/001-arabic-rast-16bar"
os.makedirs(f"{project_dir}/MIDI", exist_ok=True)
os.makedirs(f"{project_dir}/Audio", exist_ok=True)
os.makedirs(f"{project_dir}/Scores", exist_ok=True)

# Set seed for reproducible humanization
random.seed(42)

TPB = 480
TEMPO_BPM = 120
BAR_TICKS = TPB * 4

# Initialize UnitMatrixComposer
composer = UnitMatrixComposer(
    bpm=TEMPO_BPM,
    ticks_per_beat=TPB,
    beats_per_bar=4
)

# 4 rows (voices), 16 sections (bars)
composer.create_matrix(num_voices=4, num_sections=16)

# Define voices (0=Oud/Melody, 1=Qanun/Arpeggios, 2=Ney/Sustained, 3=Darbuka/Percussion)
composer.add_voice("Oud", program=24, channel=0)    # Nylon guitar as Oud
composer.add_voice("Qanun", program=107, channel=1) # Koto or synth harp as Qanun
composer.add_voice("Ney", program=73, channel=2)     # Flute/Ney
composer.add_voice("Darbuka", program=0, channel=9)  # Percussion channel 10

# Define 16 bars
for col in range(16):
    composer.add_section(f"Bar {col+1}", bars=1)

# Maqam Rast on D pitches (Equal Tempered approximation)
# D4=62, E(half-flat ~ E4)=64, F4=65, G4=67, A4=69, B(half-flat ~ Bb4)=70, C5=72, D5=74
rast_pitches = [62, 64, 65, 67, 69, 70, 72, 74]

# Melodic phrases (8 steps, half-note or quarter-note based)
melody_phrases = [
    [62, 64, 65, 67, 69, 67, 65, 64], # Phrase A (rising/falling lower Jins)
    [67, 69, 70, 72, 74, 72, 70, 69], # Phrase B (upper Jins focus)
    [74, 72, 70, 69, 67, 65, 64, 62], # Phrase C (descending resolving)
    [62, 65, 67, 69, 62, 65, 64, 62]  # Cadence
]

def humanize(tick, amount=8):
    return tick + random.randint(-amount, amount)

def add_human_event(events_list, pitch, start, end, volume, force_end=None):
    min_start = events_list[-1].end_tick if events_list else 0
    h_start = max(min_start, humanize(start, 4))
    
    if force_end is not None:
        h_end = force_end
    else:
        h_end = max(h_start + 40, humanize(end, 4))
        
    if h_start >= h_end:
        h_start = h_end - 10

    h_vol = max(40, min(127, volume + random.randint(-4, 4)))
    events_list.append(MusicEvent(pitch=pitch, start_tick=int(h_start), end_tick=int(h_end), volume=h_vol))

# Maqsum rhythmic cycle: Dum (36) and Tek (40)
# Step grid of 8 eighth notes: D . T . . T D . T . -> Dum Tek Tek Dum Tek
maqsum_grid = [36, None, 40, 40, None, 36, 40, None]

for col in range(16):
    # Determine musical form progression: A A B C - A A B C - B B C D...
    if col % 4 == 0:
        phrase = melody_phrases[0]
    elif col % 4 == 1:
        phrase = melody_phrases[0] if col < 8 else melody_phrases[1]
    elif col % 4 == 2:
        phrase = melody_phrases[1] if col < 8 else melody_phrases[2]
    else:
        phrase = melody_phrases[3]

    # 1. OUD LEAD MELODY (Row 0)
    oud_events = []
    for step in range(8):
        note = phrase[step]
        start_tick = step * 240
        
        if step == 7:
            end_tick = BAR_TICKS
        else:
            end_tick = (step + 1) * 240 - 15
        
        # 30% ornamentation: double strike as sixteenth notes
        if random.random() < 0.3:
            mid_tick = start_tick + 120
            add_human_event(oud_events, note, start_tick, mid_tick - 10, 95)
            if step == 7:
                add_human_event(oud_events, note, mid_tick, end_tick, 85, force_end=BAR_TICKS)
            else:
                add_human_event(oud_events, note, mid_tick, end_tick, 85)
        else:
            if step == 7:
                add_human_event(oud_events, note, start_tick, end_tick, 95, force_end=BAR_TICKS)
            else:
                add_human_event(oud_events, note, start_tick, end_tick, 95)
    composer.set_unit(0, col, MusicUnit(events=oud_events))

    # 2. QANUN ARPEGGIOS (Row 1)
    qanun_events = []
    chord_tones = [phrase[0], phrase[2], phrase[4]]
    # Fill standard 1920 ticks timeline per cell by ensuring last note reaches BAR_TICKS or placing a final anchor
    for step in range(8):
        if step % 2 == 0:
            pitch = chord_tones[(step // 2) % len(chord_tones)]
            start_tick = step * 240
            if step == 6:
                end_tick = BAR_TICKS
                add_human_event(qanun_events, pitch + 12, start_tick, end_tick, 75, force_end=BAR_TICKS)
            else:
                end_tick = start_tick + 180
                add_human_event(qanun_events, pitch + 12, start_tick, end_tick, 75)
    composer.set_unit(1, col, MusicUnit(events=qanun_events))

    # 3. NEY SUSTAIN (Row 2)
    ney_events = []
    add_human_event(ney_events, phrase[0], 0, BAR_TICKS, 60, force_end=BAR_TICKS)
    composer.set_unit(2, col, MusicUnit(events=ney_events))

    # 4. DARBUKA PERCUSSION (Row 3)
    perc_events = []
    # Make sure to anchor last event of darbuka track at BAR_TICKS
    for step in range(8):
        drum_note = maqsum_grid[step]
        if drum_note is not None:
            start_tick = step * 240
            if step == 6:
                end_tick = BAR_TICKS
                add_human_event(perc_events, drum_note, start_tick, end_tick, 100, force_end=BAR_TICKS)
            else:
                end_tick = start_tick + 120
                add_human_event(perc_events, drum_note, start_tick, end_tick, 100)
    composer.set_unit(3, col, MusicUnit(events=perc_events))

# Validate and save outputs
composer.validate()

# Output Paths
midi_out_path = f"{project_dir}/MIDI/arabic_rast_16bar.mid"
composer.to_midi(midi_out_path)
print(f"MIDI Export Complete: {midi_out_path}")
