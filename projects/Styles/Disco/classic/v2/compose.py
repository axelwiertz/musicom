#!/usr/bin/env python3
"""Classic Disco v2 — Method 011: Euclidean Groove
Uses Bjorklund's algorithm to generate optimal rhythmic patterns.
E(5,16) = kick pattern, E(7,16) = hi-hat, E(3,8) = snare
Key: D minor | BPM: 120 | 32 bars
"""

import os, sys
from structures import MusicUnit, MusicEvent, UnitMatrix, MidiInstrument, MidiPercussion
from workflows.unitmatrix_composer import (
    UnitMatrixComposer, create_note_unit, create_chord_unit, create_empty_unit,
)
from ai.utils.visualizer import write_grid_visualization
from workflows.provenance import write_provenance, AI_ASSISTED

TPB = 480
BPM = 120
BEATS_PER_BAR = 4
BAR = TPB * BEATS_PER_BAR
SECTION_BARS = 4
SECTION = BAR * SECTION_BARS
TOTAL_SECTIONS = 8

# === EUCLIDEAN RHYTHM GENERATOR (Bjorklund's Algorithm) ===
def euclidean(pulses, steps):
    """Generate Euclidean rhythm pattern.
    E(pulses, steps) distributes 'pulses' as evenly as possible across 'steps'.
    Returns list of 1s (hits) and 0s (rests).
    """
    if pulses >= steps:
        return [1] * steps
    if pulses == 0:
        return [0] * steps
    
    # Bjorklund's algorithm
    counts = []
    remainders = []
    divisor = steps
    remainder = pulses
    
    while True:
        counts.append(divisor // remainder)
        new_remainder = divisor % remainder
        remainders.append(new_remainder)
        divisor = remainder
        remainder = new_remainder
        if remainder <= 1:
            break
    
    # Build pattern
    def build(level):
        if level == -1:
            return [0]
        elif level == -2:
            return [1]
        else:
            return build(level - 1) * counts[level] + build(level - 2)
    
    pattern = build(len(counts) - 1)
    
    # Pad to exact length if needed
    while len(pattern) < steps:
        pattern.append(0)
    
    return pattern[:steps]

def rotate_pattern(pattern, offset):
    """Rotate pattern by offset positions."""
    n = len(pattern)
    return pattern[offset:] + pattern[:offset]

# Euclidean patterns for disco
# E(4,16) = classic four-on-the-floor variant
# E(5,16) = syncopated kick
# E(7,16) = busy hi-hat
# E(3,8) = snare on 2&4 (classic backbeat)
# E(5,8) = busy percussion

KICK_E5 = euclidean(5, 16)      # Syncopated kick
KICK_E4 = euclidean(4, 16)      # Four-on-the-floor
HAT_E7 = euclidean(7, 16)       # Busy hi-hat
HAT_E9 = euclidean(9, 16)       # Very busy hi-hat
SNARE_E2 = euclidean(2, 8)      # Sparse snare
SNARE_E3 = euclidean(3, 8)      # Classic backbeat
PERC_E5 = euclidean(5, 8)       # Busy percussion

# Chords: Dm7, Gm7, Am7, C7
CHORDS = {
    'Dm7': {'root': 50, 'third': 53, 'fifth': 57, 'flat7': 60,
            'root3': 62, 'third3': 65, 'fifth3': 69, 'flat7_3': 72,
            'bass': 38},
    'Gm7': {'root': 43, 'third': 46, 'fifth': 50, 'flat7': 53,
            'root3': 55, 'third3': 58, 'fifth3': 62, 'flat7_3': 65,
            'bass': 43},
    'Am7': {'root': 45, 'third': 48, 'fifth': 52, 'flat7': 55,
            'root3': 57, 'third3': 60, 'fifth3': 64, 'flat7_3': 67,
            'bass': 45},
    'C7': {'root': 48, 'third': 52, 'fifth': 55, 'flat7': 58,
           'root3': 60, 'third3': 64, 'fifth3': 67, 'flat7_3': 70,
           'bass': 48},
}

PROGRESSION = [
    ['Dm7', 'Gm7', 'Dm7', 'Am7'],
    ['Dm7', 'Gm7', 'C7', 'Dm7'],
    ['Gm7', 'Am7', 'Dm7', 'Dm7'],
    ['Dm7', 'Gm7', 'Dm7', 'Am7'],
    ['Dm7', 'Gm7', 'C7', 'Dm7'],
    ['Gm7', 'Am7', 'Dm7', 'Dm7'],
    ['Dm7', 'C7', 'Gm7', 'Am7'],
    ['Dm7', 'C7', 'Dm7', 'Dm7'],
]
SECTION_NAMES = ['A1', 'A2', 'B1', 'A3', 'A4', 'B2', 'C1', 'C2']

def pad_to_section(events):
    if not events or events[-1].end_tick < SECTION:
        events.append(MusicEvent(pitch=0, volume=0, start_tick=SECTION - 10, end_tick=SECTION))

def build_euclidean_drums(chord_name, section_offset, section_idx):
    """Euclidean rhythm drums: different patterns per section"""
    events = []
    sixteenth = TPB // 4
    
    # Vary patterns by section
    if section_idx % 4 == 0:  # A sections
        kick_pattern = KICK_E4  # Four-on-the-floor
        hat_pattern = HAT_E7
        snare_pattern = SNARE_E3
    elif section_idx % 4 == 1:  # B sections
        kick_pattern = KICK_E5  # Syncopated
        hat_pattern = HAT_E9
        snare_pattern = SNARE_E3
    else:  # C sections
        kick_pattern = KICK_E4
        hat_pattern = HAT_E7
        snare_pattern = SNARE_E2
    
    for bar in range(4):
        bar_t = bar * BAR
        
        # Kick (16th resolution)
        for i, hit in enumerate(kick_pattern):
            if hit:
                t = bar_t + i * sixteenth
                events.append(MusicEvent(pitch=36, volume=110, start_tick=t, end_tick=t + 120))
        
        # Hi-hat (16th resolution)
        for i, hit in enumerate(hat_pattern):
            if hit:
                t = bar_t + i * sixteenth
                vol = 70 if i % 2 == 0 else 55
                events.append(MusicEvent(pitch=42, volume=vol, start_tick=t, end_tick=t + 60))
        
        # Snare (8th resolution, rotated for backbeat)
        snare_rotated = rotate_pattern(snare_pattern, 2)  # Rotate to hit on 2&4
        for i, hit in enumerate(snare_rotated):
            if hit:
                t = bar_t + i * (TPB // 2)
                events.append(MusicEvent(pitch=38, volume=100, start_tick=t, end_tick=t + 120))
        
        # Percussion (8th resolution) on B sections
        if section_idx % 4 == 1:
            perc_pattern = PERC_E5
            for i, hit in enumerate(perc_pattern):
                if hit:
                    t = bar_t + i * (TPB // 2)
                    events.append(MusicEvent(pitch=75, volume=65, start_tick=t, end_tick=t + 80))
        
        # Crash on section start
        if bar == 0:
            events.append(MusicEvent(pitch=49, volume=90, start_tick=bar_t, end_tick=bar_t + 960))
    
    pad_to_section(events)
    return MusicUnit(events=events)

def build_euclidean_bass(chord_name, section_offset, section_idx):
    """Euclidean bass rhythm: syncopated pattern"""
    c = CHORDS[chord_name]
    events = []
    sixteenth = TPB // 4
    
    # Bass rhythm: E(5,16) for syncopation
    bass_pattern = KICK_E5  # Same as syncopated kick
    bass_pitches = [c['bass'], c['bass'] + 12, c['bass'] + 7, c['bass'], c['bass'] + 12]
    
    for bar in range(4):
        bar_t = bar * BAR
        pitch_idx = 0
        
        for i, hit in enumerate(bass_pattern):
            if hit:
                t = bar_t + i * sixteenth
                pitch = bass_pitches[pitch_idx % len(bass_pitches)]
                vol = 100 if i % 4 == 0 else 85
                events.append(MusicEvent(pitch=pitch, volume=vol, start_tick=t, end_tick=t + 200))
                pitch_idx += 1
    
    pad_to_section(events)
    return MusicUnit(events=events)

def build_string_stabs_euclidean(chord_name, section_offset, section_idx):
    """String stabs on Euclidean rhythm"""
    c = CHORDS[chord_name]
    events = []
    eighth = TPB // 2
    
    # String stab pattern: E(3,8)
    stab_pattern = SNARE_E3
    
    for bar in range(4):
        bar_t = bar * BAR
        
        for i, hit in enumerate(stab_pattern):
            if hit:
                t = bar_t + i * eighth
                # String chord: 3rd, 5th, 7th
                for p in [c['third3'], c['fifth3'], c['flat7_3']]:
                    events.append(MusicEvent(pitch=p, volume=80, start_tick=t, end_tick=t + 120))
    
    pad_to_section(events)
    return MusicUnit(events=events)

def build_brass_hits_euclidean(chord_name, section_offset, section_idx):
    """Brass hits on Euclidean rhythm"""
    c = CHORDS[chord_name]
    events = []
    
    # Brass pattern: E(2,4) = hits on beat 1 and 3
    brass_pattern = [1, 0, 1, 0]
    
    for bar in range(4):
        bar_t = bar * BAR
        
        for i, hit in enumerate(brass_pattern):
            if hit:
                t = bar_t + i * TPB
                # Brass chord: root, 3rd, 5th (octave up)
                for p in [c['root3'], c['third3'], c['fifth3']]:
                    events.append(MusicEvent(pitch=p + 12, volume=95, start_tick=t, end_tick=t + 240))
    
    pad_to_section(events)
    return MusicUnit(events=events)

# Build composition
print("Building Classic Disco v2 — Method 011: Euclidean Groove...")
print(f"Euclidean patterns: E(4,16) kick, E(5,16) bass, E(7,16) hat, E(3,8) snare/stabs")

composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS_PER_BAR)
composer.create_matrix(num_voices=4, num_sections=TOTAL_SECTIONS)

composer.add_voice("Drums", program=0, channel=9)
composer.add_voice("Bass", program=MidiInstrument.BASS, channel=0)
composer.add_voice("Strings", program=MidiInstrument.STRING_ENSEMBLE, channel=1)
composer.add_voice("Brass", program=MidiInstrument.TRUMPET, channel=2)

for i, name in enumerate(SECTION_NAMES):
    composer.add_section(name, bars=SECTION_BARS)

for sec_idx in range(TOTAL_SECTIONS):
    name = SECTION_NAMES[sec_idx]
    chords = PROGRESSION[sec_idx]
    offset = sec_idx * SECTION
    
    drum_unit = build_euclidean_drums(chords[0], offset, sec_idx)
    bass_unit = build_euclidean_bass(chords[0], offset, sec_idx)
    string_unit = build_string_stabs_euclidean(chords[0], offset, sec_idx)
    brass_unit = build_brass_hits_euclidean(chords[0], offset, sec_idx)
    
    composer.fill_voice_section("Drums", name, drum_unit)
    composer.fill_voice_section("Bass", name, bass_unit)
    composer.fill_voice_section("Strings", name, string_unit)
    composer.fill_voice_section("Brass", name, brass_unit)

ok, msg = composer.validate()
print(f"Validation: {'PASS' if ok else 'FAIL'} — {msg}")
if not ok:
    sys.exit(1)

out_dir = "/opt/data/projects/Styles/Disco/classic/v2"
os.makedirs(out_dir, exist_ok=True)
midi_path = os.path.join(out_dir, "classic_disco_v2.mid")
composer.to_midi(midi_path)
assert os.path.getsize(midi_path) > 40

grid_path = os.path.join(out_dir, "grid_visualization.txt")
write_grid_visualization(composer.matrix, grid_path, ticks_per_character=480,
                         voice_names=["Drums", "Bass", "Strings", "Brass"], bpm=BPM)

write_provenance(midi_path, AI_ASSISTED, "disco-classic-v2",
                 parameters={"bpm": BPM, "key": "D minor", "style": "Classic Disco",
                            "method": "011 Euclidean Groove (Bjorklund's algorithm)",
                            "patterns": {"kick": "E(4,16)/E(5,16)", "bass": "E(5,16)",
                                        "hat": "E(7,16)/E(9,16)", "snare": "E(3,8)",
                                        "stabs": "E(3,8)", "brass": "E(2,4)"}})

print("Classic Disco v2 (Euclidean) done ✓")
