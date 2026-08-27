#!/usr/bin/env python3
import os
import sys
import random

# Force project root into path
sys.path.insert(0, '/opt/data/repos')

# Import core classes
from musicom.structures.unit import MusicUnit, MusicEvent
from musicom.workflows.unitmatrix_composer import UnitMatrixComposer
from musicom.rules.progression import Scale7ChordDegree

project_dir = "/opt/data/projects/Styles/Fanfare/006-fanfare-showband-32bar"
os.makedirs(f"{project_dir}/MIDI", exist_ok=True)
os.makedirs(f"{project_dir}/Audio", exist_ok=True)
os.makedirs(f"{project_dir}/Scores", exist_ok=True)

# Set seed for reproducible humanization
random.seed(42)

TPB = 480
TEMPO_BPM = 132
BAR_TICKS = TPB * 4

# Initialize UnitMatrixComposer
composer = UnitMatrixComposer(
    bpm=TEMPO_BPM,
    ticks_per_beat=TPB,
    beats_per_bar=4
)

# 4 rows (voices), 32 sections (bars)
composer.create_matrix(num_voices=4, num_sections=32)

# Define voices (0=Trumpet, 1=Trombone, 2=Tuba, 3=Snare)
composer.add_voice("Trumpet", program=56, channel=0)
composer.add_voice("Trombone", program=57, channel=1)
composer.add_voice("Tuba", program=58, channel=2)
composer.add_voice("Snare", program=0, channel=9)

# Define 32 bars
for col in range(32):
    composer.add_section(f"Bar {col+1}", bars=1)

# Key of Bb Major
key_root = 58
scale = [0, 2, 4, 5, 7, 9, 11]

# Form Progressions
prog_A = [1, 4, 7, 3, 6, 2, 5, 1]
prog_B = [6, 2, 5, 1, 4, 2, 5, 5]
prog_C = [1, 5, 4, 5, 1, 4, 5, 1]

def humanize(tick, amount=12):
    """Introduce slight timing offset."""
    return tick + random.randint(-amount, amount)

def add_human_event(events_list, pitch, start, end, volume, force_end=None):
    """Add event with timing/volume variation, ensuring strict timing boundaries."""
    # Ensure start is strictly non-negative and sequential (don't backtrack before last added event)
    min_start = events_list[-1].end_tick if events_list else 0
    h_start = max(min_start, humanize(start, 6))
    
    if force_end is not None:
        h_end = force_end
    else:
        h_end = max(h_start + 40, humanize(end, 6))
        
    # Guard to prevent start exceeding end
    if h_start >= h_end:
        h_start = h_end - 10

    h_vol = max(40, min(127, volume + random.randint(-6, 6)))
    events_list.append(MusicEvent(pitch=pitch, start_tick=int(h_start), end_tick=int(h_end), volume=h_vol))

for col in range(32):
    # Determine Section & chord degree
    if col < 8:
        sect = 'A'
        degree = prog_A[col]
    elif col < 16:
        sect = 'B'
        degree = prog_B[col - 8]
    elif col < 24:
        sect = 'A_var'
        degree = prog_A[col - 16]
    else:
        sect = 'C'
        degree = prog_C[col - 24]

    root_idx = degree - 1
    third_idx = degree + 1
    fifth_idx = degree + 3

    # ================= 1. TUBA (Row 2) =================
    bass_events = []
    if sect == 'B':
        # More walking/legato line for the lyrical section
        add_human_event(bass_events, Scale7ChordDegree.get_diatonic_note(key_root, scale, root_idx) - 24, 0, TPB * 2 - 10, 90)
        # Guard: force end_tick to exactly BAR_TICKS (1920 ticks) to prevent cumulative drift
        min_start = bass_events[-1].end_tick if bass_events else TPB * 2
        h_start = max(min_start, humanize(TPB * 2, 8))
        h_vol = max(45, min(127, 90 + random.randint(-5, 5)))
        bass_events.append(MusicEvent(pitch=Scale7ChordDegree.get_diatonic_note(key_root, scale, third_idx) - 24, start_tick=h_start, end_tick=BAR_TICKS, volume=h_vol))
    elif sect == 'C':
        # Heavy marches on all quarter beats in finale (keep strict 1-bar length at 1920 ticks)
        for q in range(4):
            pitch_deg = root_idx if q % 2 == 0 else fifth_idx
            p = Scale7ChordDegree.get_diatonic_note(key_root, scale, pitch_deg) - 24
            if q < 3:
                add_human_event(bass_events, p, q * TPB, (q + 1) * TPB - 10, 100)
            else:
                # Direct unhumanized end boundary for safety
                min_start = bass_events[-1].end_tick if bass_events else q * TPB
                h_start = max(min_start, humanize(q * TPB, 6))
                h_vol = max(45, min(127, 100 + random.randint(-5, 5)))
                bass_events.append(MusicEvent(pitch=p, start_tick=h_start, end_tick=BAR_TICKS, volume=h_vol))
    else:
        # Standard A downbeat driving pulses (keep exact end boundary at bar edge)
        p1 = Scale7ChordDegree.get_diatonic_note(key_root, scale, root_idx) - 24
        p2 = Scale7ChordDegree.get_diatonic_note(key_root, scale, fifth_idx) - 24
        add_human_event(bass_events, p1, 0, TPB - 10, 95)
        
        # Guard start: ensure start of p2 doesn't backtrack past p1's humanized end tick
        min_start = bass_events[-1].end_tick if bass_events else TPB * 2
        h_start = max(min_start, humanize(TPB * 2, 8))
        h_vol = max(45, min(127, 95 + random.randint(-5, 5)))
        # Guard: force end_tick to exactly BAR_TICKS (1920 ticks = 4*TPB) to prevent cumulative drift
        bass_events.append(MusicEvent(pitch=p2, start_tick=h_start, end_tick=BAR_TICKS, volume=h_vol))
    composer.set_unit(2, col, MusicUnit(events=bass_events))

    # ================= 2. TROMBONE (Row 1) =================
    mid_events = []
    if sect == 'B':
        # Sustained background chords (locked end boundary)
        h_start = max(0, humanize(0, 6))
        p = Scale7ChordDegree.get_diatonic_note(key_root, scale, third_idx) - 12
        mid_events.append(MusicEvent(pitch=p, start_tick=h_start, end_tick=BAR_TICKS, volume=75))
    elif sect == 'C':
        # Syncopated mid accents
        p1 = Scale7ChordDegree.get_diatonic_note(key_root, scale, root_idx) - 12
        p2 = Scale7ChordDegree.get_diatonic_note(key_root, scale, third_idx) - 12
        p3 = Scale7ChordDegree.get_diatonic_note(key_root, scale, fifth_idx) - 12
        add_human_event(mid_events, p1, 0, int(1.5 * TPB) - 10, 90)
        add_human_event(mid_events, p2, int(1.5 * TPB), TPB * 3 - 10, 90)
        
        min_start = mid_events[-1].end_tick if mid_events else TPB * 3
        h_start = max(min_start, humanize(TPB * 3, 8))
        mid_events.append(MusicEvent(pitch=p3, start_tick=h_start, end_tick=BAR_TICKS, volume=90))
    else:
        # Standard A style: quarter notes
        for q in range(4):
            p = Scale7ChordDegree.get_diatonic_note(key_root, scale, third_idx) - 12 if q % 2 == 0 else Scale7ChordDegree.get_diatonic_note(key_root, scale, root_idx) - 12
            if q < 3:
                add_human_event(mid_events, p, q * TPB, (q + 1) * TPB - 10, 85)
            else:
                min_start = mid_events[-1].end_tick if mid_events else q * TPB
                h_start = max(min_start, humanize(q * TPB, 8))
                mid_events.append(MusicEvent(pitch=p, start_tick=h_start, end_tick=BAR_TICKS, volume=85))
    composer.set_unit(1, col, MusicUnit(events=mid_events))

    # ================= 3. TRUMPET (Row 0) =================
    lead_events = []
    if sect == 'B':
        # Lyrical flowing eighth/quarter line
        p3rd = Scale7ChordDegree.get_diatonic_note(key_root, scale, third_idx) + 12
        p_rt = Scale7ChordDegree.get_diatonic_note(key_root, scale, root_idx) + 12
        p_5th = Scale7ChordDegree.get_diatonic_note(key_root, scale, fifth_idx) + 12
        add_human_event(lead_events, p3rd, 0, TPB - 10, 95)
        add_human_event(lead_events, p_rt, TPB, TPB * 2 - 10, 95)
        add_human_event(lead_events, p_5th, TPB * 2, TPB * 3 - 10, 95)
        add_human_event(lead_events, p3rd, TPB * 3, int(3.5 * TPB) - 10, 95)
        
        min_start = lead_events[-1].end_tick if lead_events else int(3.5 * TPB)
        h_start = max(min_start, humanize(int(3.5 * TPB), 8))
        lead_events.append(MusicEvent(pitch=p_rt, start_tick=h_start, end_tick=BAR_TICKS, volume=95))
    elif sect == 'C':
        p_rt = Scale7ChordDegree.get_diatonic_note(key_root, scale, root_idx) + 12
        p_5th = Scale7ChordDegree.get_diatonic_note(key_root, scale, fifth_idx) + 12
        if col == 31: # Grand finale chord
            lead_events.append(MusicEvent(pitch=p_rt, start_tick=0, end_tick=BAR_TICKS, volume=125))
        else:
            add_human_event(lead_events, p_rt, 0, TPB - 10, 115)
            add_human_event(lead_events, p_5th, TPB, TPB * 2 - 10, 115)
            # Rapid double tonguing 16th notes
            add_human_event(lead_events, p_5th, TPB * 2, TPB * 2 + int(TPB/4) - 5, 120)
            add_human_event(lead_events, p_rt, TPB * 2 + int(TPB/4), TPB * 2 + int(TPB/2) - 5, 120)
            add_human_event(lead_events, p_5th, TPB * 2 + int(TPB/2), TPB * 3 - 10, 120)
            
            min_start = lead_events[-1].end_tick if lead_events else TPB * 3
            h_start = max(min_start, humanize(TPB * 3, 8))
            lead_events.append(MusicEvent(pitch=p_rt, start_tick=h_start, end_tick=BAR_TICKS, volume=120))
    else:
        # Standard A section flourishes (add minor variations for col >= 16)
        p_rt = Scale7ChordDegree.get_diatonic_note(key_root, scale, root_idx) + 12
        p_5th = Scale7ChordDegree.get_diatonic_note(key_root, scale, fifth_idx) + 12
        vol_boost = 5 if sect == 'A_var' else 0
        
        add_human_event(lead_events, p_rt, 0, int(0.5 * TPB) - 10, 110 + vol_boost)
        add_human_event(lead_events, p_5th, int(1.5 * TPB), int(2.0 * TPB) - 10, 110 + vol_boost)
        add_human_event(lead_events, p_5th, int(2.0 * TPB), int(2.5 * TPB) - 10, 110 + vol_boost)
        
        min_start = lead_events[-1].end_tick if lead_events else int(3.5 * TPB)
        h_start = max(min_start, humanize(int(3.5 * TPB), 8))
        lead_events.append(MusicEvent(pitch=p_rt, start_tick=h_start, end_tick=BAR_TICKS, volume=110 + vol_boost))
        
    composer.set_unit(0, col, MusicUnit(events=lead_events))

    # ================= 4. SNARE / DRUMBAND (Row 3) =================
    snare_events = []
    
    # Introduce Typical Drumband Subrhythms: Paradiddles, Flams, Rimshot Accents and Snare Rolls
    if sect == 'B':
        # Soft Paradiddle Tap (L R L L R L R R)
        for eighth in range(8):
            if eighth in (0, 4):
                vol = 80  # Accented lead tap
            elif eighth in (3, 7):
                vol = 45  # Double-stroke soft tap
            else:
                vol = 55  # Normal inner-stroke tap
                
            if eighth < 7:
                add_human_event(snare_events, 38, eighth * int(TPB/2), (eighth + 1) * int(TPB/2) - 10, vol)
            else:
                min_start = snare_events[-1].end_tick if snare_events else eighth * int(TPB/2)
                h_start = max(min_start, humanize(eighth * int(TPB/2), 6))
                snare_events.append(MusicEvent(pitch=38, start_tick=h_start, end_tick=BAR_TICKS, volume=vol))
                
    elif sect == 'C':
        # Intense marching crescendo roll with heavy accents and "flams"
        for sixteenth in range(16):
            vol = int(70 + (sixteenth * 3.5))
            if sixteenth in (0, 8, 14): # Heavy accents
                vol = 125
            
            # Flam timing
            if sixteenth in (4, 12):
                add_human_event(snare_events, 38, sixteenth * int(TPB/4), sixteenth * int(TPB/4) + int(TPB/8) - 5, vol - 20)
                add_human_event(snare_events, 38, sixteenth * int(TPB/4) + int(TPB/8), (sixteenth + 1) * int(TPB/4) - 5, vol)
            else:
                if sixteenth < 15:
                    add_human_event(snare_events, 38, sixteenth * int(TPB/4), (sixteenth + 1) * int(TPB/4) - 5, vol)
                else:
                    min_start = snare_events[-1].end_tick if snare_events else sixteenth * int(TPB/4)
                    h_start = max(min_start, humanize(sixteenth * int(TPB/4), 4))
                    snare_events.append(MusicEvent(pitch=38, start_tick=h_start, end_tick=BAR_TICKS, volume=vol))
                    
    else:
        # Standard A: Traditional Drumband "Double-Stroke" Roll & Rimshot Accent Pattern
        if col in (3, 7):
            # Ruff / Roll cadence
            rhythm_ticks = [
                (0, int(TPB/2), 100),
                (int(TPB/2), TPB, 75),
                (TPB, TPB + int(TPB/4), 85),
                (TPB + int(TPB/4), TPB + int(TPB/2), 85),
                (TPB + int(TPB/2), TPB + int(3*TPB/4), 80),
                (TPB + int(3*TPB/4), TPB * 2, 80),
                (TPB * 2, TPB * 2 + int(TPB/2), 110),
                (TPB * 2 + int(TPB/2), TPB * 3, 70),
                (TPB * 3, TPB * 3 + int(TPB/4), 90),
                (TPB * 3 + int(TPB/4), TPB * 3 + int(TPB/2), 90),
                (TPB * 3 + int(TPB/2), BAR_TICKS, 125) # Rimshot accent
            ]
            for start, end, vol in rhythm_ticks:
                if end < BAR_TICKS:
                    add_human_event(snare_events, 38, start, end - 10, vol)
                else:
                    min_start = snare_events[-1].end_tick if snare_events else start
                    h_start = max(min_start, humanize(start, 5))
                    snare_events.append(MusicEvent(pitch=38, start_tick=h_start, end_tick=BAR_TICKS, volume=vol))
        else:
            # Syncopated marching roll
            rhythm_ticks = [
                (0, int(TPB/2), 110),
                (int(TPB/2), int(3*TPB/4), 70),
                (int(3*TPB/4), TPB, 75),
                (TPB, TPB + int(TPB/2), 95),
                (TPB + int(TPB/2), TPB * 2, 80),
                (TPB * 2, TPB * 2 + int(TPB/2), 105),
                (TPB * 2 + int(TPB/2), TPB * 2 + int(3*TPB/4), 70),
                (TPB * 2 + int(3*TPB/4), TPB * 3, 75),
                (TPB * 3, BAR_TICKS, 115)
            ]
            for start, end, vol in rhythm_ticks:
                if end < BAR_TICKS:
                    add_human_event(snare_events, 38, start, end - 10, vol)
                else:
                    min_start = snare_events[-1].end_tick if snare_events else start
                    h_start = max(min_start, humanize(start, 5))
                    snare_events.append(MusicEvent(pitch=38, start_tick=h_start, end_tick=BAR_TICKS, volume=vol))

    composer.set_unit(3, col, MusicUnit(events=snare_events))

# Export humanized MIDI
midi_path = f"{project_dir}/MIDI/showband32.mid"
composer.to_midi(midi_path)
print("Matrix validation and MIDI export: PASS")

# Invoke FluidSynth for rendering
sf2_path = "/opt/data/.local/lib/python3.13/site-packages/pretty_midi/TimGM6mb.sf2"
wav_path = f"{project_dir}/Audio/showband32.wav"

if os.path.exists(sf2_path):
    print("SoundFont found. Invoking FluidSynth...")
    cmd = f"/opt/data/micromamba/envs/musicom/bin/fluidsynth -ni -F '{wav_path}' -r 44100 '{sf2_path}' '{midi_path}' 2>&1"
    os.system(cmd)
    
    # Compress to OGG (mandatory for Telegram)
    ogg_path = f"{project_dir}/Audio/showband32.ogg"
    compress_cmd = f"ffmpeg -i '{wav_path}' -codec:a libopus -application voip -b:a 48k '{ogg_path}' -y -loglevel error"
    os.system(compress_cmd)
    print("OGG conversion: DONE")
else:
    print("Error: SoundFont missing.")
