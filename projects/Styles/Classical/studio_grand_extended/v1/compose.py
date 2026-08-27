#!/usr/bin/env python3
"""Studio Grand Extended — 32-bar multi-instrument arrangement
Source: /opt/data/projects/in/studio_grand.mid (8 bars, C major, 110 BPM)
Structure: Intro (4) + Verse (8) + Chorus (8) + Verse (8) + Outro (4)
"""

import os, sys
from structures import MusicUnit, MusicEvent, UnitMatrix, MidiInstrument, MidiPercussion
from workflows.unitmatrix_composer import (
    UnitMatrixComposer, create_note_unit, create_chord_unit, create_empty_unit,
)
from ai.utils.visualizer import write_grid_visualization
from workflows.provenance import write_provenance, AI_ASSISTED

TPB = 480
BPM = 110
BEATS_PER_BAR = 4
BAR = TPB * BEATS_PER_BAR  # 1920
SECTION = BAR * 4  # 7680 (4 bars per section)

# Timing constants
WHOLE = BAR
HALF = BAR // 2
QUARTER = BAR // 4
EIGHTH = BAR // 8
SIXTEENTH = BAR // 16

# Source chord voicings (extracted from MIDI, transposed to 480 TPB)
# Original: C4=48, G4=55, C5=60, E5=64 → C major triad
# G2=43, D3=50, G3=55, B3=59 → G major
# F2=41, C3=48, F3=53, A3=57 → F major

CHORDS = {
    'C': {'bass': 36, 'notes': [48, 55, 60, 64]},  # C3 G3 C4 E4
    'G': {'bass': 43, 'notes': [43, 50, 55, 59]},  # G2 D3 G3 B3
    'F': {'bass': 41, 'notes': [41, 48, 53, 57]},  # F2 C3 F3 A3
    'Am': {'bass': 45, 'notes': [45, 52, 57, 60]}, # A2 E3 A3 C4
}

# Progression per section (4 bars each)
PROGRESSION = [
    # Intro (4 bars): sparse, building
    ['C', 'C', 'G', 'G'],
    # Verse 1 (8 bars): main theme
    ['C', 'C', 'G', 'G'],
    ['C', 'C', 'F', 'C'],
    # Chorus (8 bars): fuller
    ['F', 'C', 'G', 'Am'],
    ['F', 'C', 'G', 'C'],
    # Verse 2 (8 bars): variation
    ['C', 'Am', 'G', 'G'],
    ['C', 'Am', 'F', 'C'],
    # Outro (4 bars): resolving
    ['F', 'C', 'G', 'C'],
]

SECTION_NAMES = ['Intro', 'V1a', 'V1b', 'ChA', 'ChB', 'V2a', 'V2b', 'Outro']

def pad_to_section(events):
    # Clamp all end_ticks to SECTION
    for e in events:
        if e.end_tick > SECTION:
            e.end_tick = SECTION
    if not events or events[-1].end_tick < SECTION:
        events.append(MusicEvent(pitch=0, volume=0, start_tick=SECTION - 10, end_tick=SECTION))

# === PIANO (original chords, whole notes) ===
def build_piano(chord_name, section_offset, section_idx, section_name):
    c = CHORDS[chord_name]
    events = []
    
    for bar in range(4):
        bar_t = bar * BAR
        chord = c['notes']
        
        # Intro: sparse, half notes
        if section_name == 'Intro':
            events.append(MusicEvent(pitch=c['bass'], volume=60, start_tick=bar_t, end_tick=bar_t + HALF))
            for p in chord:
                events.append(MusicEvent(pitch=p, volume=55, start_tick=bar_t, end_tick=bar_t + HALF))
            # Rest, then repeat softer
            for p in chord:
                events.append(MusicEvent(pitch=p, volume=45, start_tick=bar_t + HALF, end_tick=bar_t + BAR))
        
        # Verse: whole notes, moderate
        elif section_name.startswith('V'):
            events.append(MusicEvent(pitch=c['bass'], volume=75, start_tick=bar_t, end_tick=bar_t + BAR - 100))
            for p in chord:
                events.append(MusicEvent(pitch=p, volume=70, start_tick=bar_t, end_tick=bar_t + BAR - 100))
        
        # Chorus: fuller, accent on beat 1
        elif section_name.startswith('Ch'):
            # Accent
            events.append(MusicEvent(pitch=c['bass'], volume=90, start_tick=bar_t, end_tick=bar_t + QUARTER))
            for p in chord:
                events.append(MusicEvent(pitch=p, volume=85, start_tick=bar_t, end_tick=bar_t + QUARTER))
            # Sustain
            events.append(MusicEvent(pitch=c['bass'], volume=70, start_tick=bar_t + QUARTER, end_tick=bar_t + BAR - 100))
            for p in chord:
                events.append(MusicEvent(pitch=p, volume=65, start_tick=bar_t + QUARTER, end_tick=bar_t + BAR - 100))
        
        # Outro: ritardando, longer notes
        # Piano plays all 4 bars
        elif section_name == 'Outro':
            dur = BAR + bar * 200  # Gradually longer
            events.append(MusicEvent(pitch=c['bass'], volume=65 - bar * 8, start_tick=bar_t, end_tick=bar_t + dur))
            for p in chord:
                events.append(MusicEvent(pitch=p, volume=60 - bar * 8, start_tick=bar_t, end_tick=bar_t + dur))
    
    pad_to_section(events)
    return MusicUnit(events=events)

# === STRINGS (sustained pad, varied per section) ===
def build_strings(chord_name, section_offset, section_idx, section_name):
    c = CHORDS[chord_name]
    events = []
    
    # Variation pattern per section
    # Intro: fade in, sustained
    # V1a: sustained pad
    # V1b: staccato chords
    # ChA: sustained + tremolo
    # ChB: staccato chords
    # V2a: sustained pad
    # V2b: staccato chords
    # Outro: sustained, then silent
    
    for bar in range(4):
        bar_t = bar * BAR
        
        # Intro: fade in, last 2 bars only
        if section_name == 'Intro':
            if bar >= 2:
                vol = 40 + (bar - 2) * 10
                for p in c['notes']:
                    events.append(MusicEvent(pitch=p + 12, volume=vol, start_tick=bar_t, end_tick=bar_t + BAR))
        
        # V1a, V2a: sustained pad
        elif section_name in ['V1a', 'V2a']:
            vol = 60 if section_idx < 4 else 65
            for p in c['notes']:
                events.append(MusicEvent(pitch=p + 12, volume=vol, start_tick=bar_t, end_tick=bar_t + BAR))
        
        # V1b, V2b, ChB: staccato chords (quarter notes)
        elif section_name in ['V1b', 'V2b', 'ChB']:
            vol = 65
            for beat in range(4):
                t = bar_t + beat * QUARTER
                for p in c['notes']:
                    events.append(MusicEvent(pitch=p + 12, volume=vol, start_tick=t, end_tick=t + QUARTER // 2))
        
        # ChA: sustained + tremolo effect
        elif section_name == 'ChA':
            vol_base = 80
            for beat in range(8):  # 8 eighth notes
                t = bar_t + beat * EIGHTH
                vol = vol_base + (10 if beat % 2 == 0 else -10)  # Tremolo
                for p in c['notes']:
                    events.append(MusicEvent(pitch=p + 12, volume=vol, start_tick=t, end_tick=t + EIGHTH))
        
        # Outro: first 3 bars only (drops out after bar 2)
        elif section_name == 'Outro':
            if bar < 3:
                vol = 60
                for p in c['notes']:
                    events.append(MusicEvent(pitch=p + 12, volume=vol, start_tick=bar_t, end_tick=bar_t + BAR))
    
    pad_to_section(events)
    return MusicUnit(events=events)

# === BASS (root notes, simple pattern) ===
def build_bass(chord_name, section_offset, section_idx, section_name):
    c = CHORDS[chord_name]
    events = []
    
    for bar in range(4):
        bar_t = bar * BAR
        
        # Intro: silent
        if section_name == 'Intro':
            pass
        
        # Verse: half notes
        elif section_name.startswith('V'):
            events.append(MusicEvent(pitch=c['bass'], volume=85, start_tick=bar_t, end_tick=bar_t + HALF))
            events.append(MusicEvent(pitch=c['bass'], volume=75, start_tick=bar_t + HALF, end_tick=bar_t + BAR))
        
        # Chorus: quarter notes
        elif section_name.startswith('Ch'):
            for beat in range(4):
                t = bar_t + beat * QUARTER
                vol = 90 if beat == 0 else 80
                events.append(MusicEvent(pitch=c['bass'], volume=vol, start_tick=t, end_tick=t + QUARTER - 50))
        
        # Outro: bars 0-2 only (drops out after bar 2)
        elif section_name == 'Outro':
            if bar < 3:
                vol = 70
                events.append(MusicEvent(pitch=c['bass'], volume=vol, start_tick=bar_t, end_tick=bar_t + BAR))
    
    pad_to_section(events)
    return MusicUnit(events=events)

# === DRUMS (beat patterns) ===
def build_drums(chord_name, section_offset, section_idx, section_name):
    events = []
    
    for bar in range(4):
        bar_t = bar * BAR
        
        # Intro: silent
        if section_name == 'Intro':
            pass
        
        # Verse: simple beat
        elif section_name.startswith('V'):
            # Kick on 1, 3
            events.append(MusicEvent(pitch=36, volume=100, start_tick=bar_t, end_tick=bar_t + 120))
            events.append(MusicEvent(pitch=36, volume=100, start_tick=bar_t + HALF, end_tick=bar_t + HALF + 120))
            # Snare on 2, 4
            events.append(MusicEvent(pitch=38, volume=90, start_tick=bar_t + QUARTER, end_tick=bar_t + QUARTER + 120))
            events.append(MusicEvent(pitch=38, volume=90, start_tick=bar_t + HALF + QUARTER, end_tick=bar_t + HALF + QUARTER + 120))
            # Hi-hat 8ths
            for i in range(8):
                t = bar_t + i * EIGHTH
                vol = 60 if i % 2 == 0 else 45
                events.append(MusicEvent(pitch=42, volume=vol, start_tick=t, end_tick=t + 60))
        
        # Chorus: fuller beat
        elif section_name.startswith('Ch'):
            # Kick on 1, 3, and-of-3
            events.append(MusicEvent(pitch=36, volume=110, start_tick=bar_t, end_tick=bar_t + 120))
            events.append(MusicEvent(pitch=36, volume=110, start_tick=bar_t + HALF, end_tick=bar_t + HALF + 120))
            events.append(MusicEvent(pitch=36, volume=95, start_tick=bar_t + HALF + EIGHTH, end_tick=bar_t + HALF + EIGHTH + 120))
            # Snare on 2, 4
            events.append(MusicEvent(pitch=38, volume=100, start_tick=bar_t + QUARTER, end_tick=bar_t + QUARTER + 120))
            events.append(MusicEvent(pitch=38, volume=100, start_tick=bar_t + HALF + QUARTER, end_tick=bar_t + HALF + QUARTER + 120))
            # Hi-hat 16ths
            for i in range(16):
                t = bar_t + i * SIXTEENTH
                vol = 65 if i % 4 == 0 else 50
                events.append(MusicEvent(pitch=42, volume=vol, start_tick=t, end_tick=t + 40))
            # Crash on bar 1
            if bar == 0:
                events.append(MusicEvent(pitch=49, volume=85, start_tick=bar_t, end_tick=bar_t + 960))
        
        # Outro: bars 0-2 only (drops out after bar 2)
        elif section_name == 'Outro':
            if bar < 3:
                # Kick on 1, 3
                events.append(MusicEvent(pitch=36, volume=100, start_tick=bar_t, end_tick=bar_t + 120))
                events.append(MusicEvent(pitch=36, volume=100, start_tick=bar_t + HALF, end_tick=bar_t + HALF + 120))
                # Snare on 2, 4
                events.append(MusicEvent(pitch=38, volume=90, start_tick=bar_t + QUARTER, end_tick=bar_t + QUARTER + 120))
                events.append(MusicEvent(pitch=38, volume=90, start_tick=bar_t + HALF + QUARTER, end_tick=bar_t + HALF + QUARTER + 120))
    
    pad_to_section(events)
    return MusicUnit(events=events)

# === LEAD MELODY (simple motif) ===
def build_lead(chord_name, section_offset, section_idx, section_name):
    c = CHORDS[chord_name]
    events = []
    
    # Simple ascending/descending motif based on chord
    root = c['notes'][0]
    
    for bar in range(4):
        bar_t = bar * BAR
        
        # Intro: silent
        if section_name == 'Intro':
            pass
        
        # Verse: simple melody
        elif section_name.startswith('V'):
            # Ascending pattern
            melody = [root + 12, root + 14, root + 16, root + 17]  # Scale degrees
            for i, note in enumerate(melody):
                t = bar_t + i * HALF
                events.append(MusicEvent(pitch=note, volume=75, start_tick=t, end_tick=t + HALF - 100))
        
        # Chorus: fuller melody
        elif section_name.startswith('Ch'):
            # More active
            melody = [root + 12, root + 16, root + 14, root + 19,
                     root + 17, root + 14, root + 12, root + 10]
            for i, note in enumerate(melody):
                t = bar_t + i * QUARTER
                vol = 85 if i % 2 == 0 else 75
                events.append(MusicEvent(pitch=note, volume=vol, start_tick=t, end_tick=t + QUARTER - 80))
        
        # Outro: bars 0-1 only (drops after bar 1)
        elif section_name == 'Outro':
            if bar < 2:
                melody = [root + 17, root + 16, root + 14, root + 12]
                vol_base = 70
                for i, note in enumerate(melody):
                    t = bar_t + i * HALF
                    events.append(MusicEvent(pitch=note, volume=vol_base, start_tick=t, end_tick=t + HALF - 100))
    
    pad_to_section(events)
    return MusicUnit(events=events)

# === COUNTERMELODY — Method 032: Isorhythmic Talea-Color (ITCM) ===
# Talea (rhythm cycle, length 5) and Color (pitch cycle, length 7) are coprime
# → non-repeating pattern over 35 notes before cycling
TALEA = [QUARTER, EIGHTH, HALF, EIGHTH, QUARTER]  # 5 durations
COLOR_C = [64, 67, 69, 72, 71, 69, 67]  # E4 G4 A4 C5 B4 A4 G4 (descending arc)
COLOR_G = [67, 69, 71, 74, 72, 71, 69]  # G4 A4 B4 D5 C5 B4 A4
COLOR_F = [65, 67, 69, 72, 71, 69, 67]  # F4 G4 A4 C5 B4 A4 G4
COLOR_AM = [64, 67, 69, 72, 71, 69, 67] # E4 G4 A4 C5 B4 A4 G4

COLORS = {'C': COLOR_C, 'G': COLOR_G, 'F': COLOR_F, 'Am': COLOR_AM}

def build_countermelody(chord_name, section_offset, section_idx, section_name):
    """Method 032: Isorhythmic Talea-Color mapping.
    Rhythm cycle (talea) length 5, pitch cycle (color) length 7.
    Coprime → pattern shifts phase each cycle = organic non-repetition.
    Phase offset per section to avoid monotony.
    """
    events = []
    color = COLORS[chord_name]
    talea_pos = 0
    color_pos = (section_idx * 3) % len(COLOR_C)  # Phase shift per section
    
    t = 0
    while t < SECTION:
        # Get duration from talea cycle
        dur = TALEA[talea_pos % len(TALEA)]
        # Get pitch from color cycle
        pitch = color[color_pos % len(color)]
        
        # Dynamic: louder in chorus, softer in verse, silent intro/outro
        if section_name == 'Intro' or section_name == 'Outro':
            vol = 0  # Silent
        elif section_name.startswith('Ch'):
            vol = 85
        elif section_name.startswith('V'):
            vol = 65 if section_idx >= 4 else 55  # V2 louder than V1
        else:
            vol = 60
        
        if vol > 0 and t + dur <= SECTION:
            events.append(MusicEvent(pitch=pitch, volume=vol, start_tick=t, end_tick=t + dur - 40))
        
        t += dur
        talea_pos += 1
        color_pos += 1
    
    pad_to_section(events)
    return MusicUnit(events=events)

# Build composition
print("Building Studio Grand Extended...")
print(f"Source: 8 bars C major → Extended: 32 bars multi-instrument")

composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS_PER_BAR)
composer.create_matrix(num_voices=6, num_sections=8)

composer.add_voice("Piano", program=MidiInstrument.PIANO, channel=0)
composer.add_voice("Strings", program=MidiInstrument.STRING_ENSEMBLE, channel=1)
composer.add_voice("Bass", program=MidiInstrument.BASS, channel=2)
composer.add_voice("Drums", program=0, channel=9)
composer.add_voice("Lead", program=MidiInstrument.FLUTE, channel=3)
composer.add_voice("Countermelody", program=MidiInstrument.FLUTE, channel=4)

for i, name in enumerate(SECTION_NAMES):
    bars = 4
    composer.add_section(name, bars=bars)

for sec_idx in range(8):
    name = SECTION_NAMES[sec_idx]
    chords = PROGRESSION[sec_idx]
    offset = sec_idx * SECTION
    
    piano_unit = build_piano(chords[0], offset, sec_idx, name)
    strings_unit = build_strings(chords[0], offset, sec_idx, name)
    bass_unit = build_bass(chords[0], offset, sec_idx, name)
    drum_unit = build_drums(chords[0], offset, sec_idx, name)
    lead_unit = build_lead(chords[0], offset, sec_idx, name)
    counter_unit = build_countermelody(chords[0], offset, sec_idx, name)
    
    composer.fill_voice_section("Piano", name, piano_unit)
    composer.fill_voice_section("Strings", name, strings_unit)
    composer.fill_voice_section("Bass", name, bass_unit)
    composer.fill_voice_section("Drums", name, drum_unit)
    composer.fill_voice_section("Lead", name, lead_unit)
    composer.fill_voice_section("Countermelody", name, counter_unit)

ok, msg = composer.validate()
print(f"Validation: {'PASS' if ok else 'FAIL'} — {msg}")
if not ok:
    sys.exit(1)

out_dir = "/opt/data/projects/Styles/Classical/studio_grand_extended/v1"
midi_path = os.path.join(out_dir, "studio_grand_extended.mid")
composer.to_midi(midi_path)
assert os.path.getsize(midi_path) > 40

grid_path = os.path.join(out_dir, "grid_visualization.txt")
write_grid_visualization(composer.matrix, grid_path, ticks_per_character=480,
                         voice_names=["Piano", "Strings", "Bass", "Drums", "Lead"], bpm=BPM)

write_provenance(midi_path, AI_ASSISTED, "studio_grand_extended",
                 parameters={"bpm": BPM, "key": "C major", "bars": 32,
                            "source": "studio_grand.mid (8 bars)",
                            "structure": "Intro(4) + V1(8) + Chorus(8) + V2(8) + Outro(4)"})

print("Studio Grand Extended done ✓")
