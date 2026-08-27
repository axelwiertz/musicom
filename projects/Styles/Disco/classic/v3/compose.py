#!/usr/bin/env python3
"""Classic Disco v3 — Method 011 + 026 Hybrid
Euclidean rhythm foundation + DPSM phase-shifted arpeggios for continuous flow.
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

# === EUCLIDEAN RHYTHM ===
def euclidean(pulses, steps):
    if pulses >= steps:
        return [1] * steps
    if pulses == 0:
        return [0] * steps
    counts, remainders = [], []
    divisor, remainder = steps, pulses
    while True:
        counts.append(divisor // remainder)
        new_remainder = divisor % remainder
        remainders.append(new_remainder)
        divisor, remainder = remainder, new_remainder
        if remainder <= 1:
            break
    def build(level):
        if level == -1: return [0]
        elif level == -2: return [1]
        else: return build(level - 1) * counts[level] + build(level - 2)
    pattern = build(len(counts) - 1)
    while len(pattern) < steps:
        pattern.append(0)
    return pattern[:steps]

def rotate_pattern(pattern, offset):
    n = len(pattern)
    return pattern[offset:] + pattern[:offset]

KICK_E4 = euclidean(4, 16)
KICK_E5 = euclidean(5, 16)
HAT_E7 = euclidean(7, 16)
SNARE_E3 = euclidean(3, 8)

# Chords
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

# === METHOD 011: EUCLIDEAN DRUMS ===
def build_euclidean_drums(chord_name, section_offset, section_idx):
    events = []
    sixteenth = TPB // 4
    
    kick_pattern = KICK_E4 if section_idx % 4 != 1 else KICK_E5
    hat_pattern = HAT_E7
    snare_rotated = rotate_pattern(SNARE_E3, 2)
    
    for bar in range(4):
        bar_t = bar * BAR
        for i, hit in enumerate(kick_pattern):
            if hit:
                t = bar_t + i * sixteenth
                events.append(MusicEvent(pitch=36, volume=110, start_tick=t, end_tick=t + 120))
        for i, hit in enumerate(hat_pattern):
            if hit:
                t = bar_t + i * sixteenth
                vol = 70 if i % 2 == 0 else 55
                events.append(MusicEvent(pitch=42, volume=vol, start_tick=t, end_tick=t + 60))
        for i, hit in enumerate(snare_rotated):
            if hit:
                t = bar_t + i * (TPB // 2)
                events.append(MusicEvent(pitch=38, volume=100, start_tick=t, end_tick=t + 120))
        if bar == 0:
            events.append(MusicEvent(pitch=49, volume=90, start_tick=bar_t, end_tick=bar_t + 960))
    
    pad_to_section(events)
    return MusicUnit(events=events)

# === METHOD 011: EUCLIDEAN BASS (enhanced with passing tones) ===
def build_euclidean_bass(chord_name, section_offset, section_idx):
    c = CHORDS[chord_name]
    events = []
    sixteenth = TPB // 4
    bass_pattern = KICK_E5
    
    for bar in range(4):
        bar_t = bar * BAR
        # Add walking bass fills between Euclidean hits
        for i, hit in enumerate(bass_pattern):
            if hit:
                t = bar_t + i * sixteenth
                pitch = c['bass'] if i % 2 == 0 else c['bass'] + 12
                vol = 100 if i % 4 == 0 else 85
                events.append(MusicEvent(pitch=pitch, volume=vol, start_tick=t, end_tick=t + 200))
        
        # Fill gaps with walking tones
        for beat in range(4):
            beat_t = bar_t + beat * TPB
            # Add passing tone on and-of-beat if no Euclidean hit
            if not bass_pattern[beat * 4 + 2]:  # Check "and" position
                passing = c['bass'] + 7 if beat % 2 == 0 else c['bass'] + 5
                events.append(MusicEvent(pitch=passing, volume=70, 
                                        start_tick=beat_t + TPB // 2, 
                                        end_tick=beat_t + TPB // 2 + 160))
    
    pad_to_section(events)
    return MusicUnit(events=events)

# === METHOD 026: DPSM PHASE-SHIFTED ARPEGGIOS ===
def build_dpsm_arpeggios(chord_name, section_offset, section_idx):
    """Continuous flowing arpeggios with phase-shifted patterns.
    Multiple voices offset by different phases create polyrhythmic flow.
    """
    c = CHORDS[chord_name]
    events = []
    
    # Arpeggio notes (chord tones)
    arp_notes = [c['root3'], c['third3'], c['fifth3'], c['flat7_3']]
    
    # Three phase-shifted layers
    phases = [0, TPB // 3, 2 * TPB // 3]  # Offset by third of beat
    eighth = TPB // 2
    
    for layer, phase_offset in enumerate(phases):
        # Each layer plays continuous 8th notes, phase-shifted
        for bar in range(4):
            bar_t = bar * BAR
            for i in range(8):  # 8 eighth notes per bar
                t = bar_t + i * eighth + phase_offset
                # Clamp to section boundary
                if t + eighth - 20 > SECTION:
                    break
                # Cycle through arpeggio notes
                pitch = arp_notes[(i + layer) % len(arp_notes)]
                # Vary velocity for organic feel
                vol = 65 + (i % 3) * 5
                events.append(MusicEvent(pitch=pitch, volume=vol, 
                                        start_tick=t, end_tick=t + eighth - 20))
    
    pad_to_section(events)
    return MusicUnit(events=events)

# === CONTINUOUS STRING PAD ===
def build_string_pad(chord_name, section_offset, section_idx):
    """Sustained string chords for harmonic bed (100% density)."""
    c = CHORDS[chord_name]
    events = []
    
    # Change chord every 2 bars
    for bar in range(4):
        bar_t = bar * BAR
        if bar % 2 == 0:
            # Sustained chord for 2 bars
            for p in [c['root3'], c['third3'], c['fifth3'], c['flat7_3']]:
                events.append(MusicEvent(pitch=p, volume=75, 
                                        start_tick=bar_t, 
                                        end_tick=bar_t + 2 * BAR))
    
    pad_to_section(events)
    return MusicUnit(events=events)

# Build composition
print("Building Classic Disco v3 — Method 011 + 026 Hybrid...")
print("Euclidean rhythm + DPSM phase-shifted arpeggios + sustained pad")

composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS_PER_BAR)
composer.create_matrix(num_voices=5, num_sections=TOTAL_SECTIONS)

composer.add_voice("Drums", program=0, channel=9)
composer.add_voice("Bass", program=MidiInstrument.BASS, channel=0)
composer.add_voice("Arpeggios", program=MidiInstrument.SYNTH_PAD, channel=1)
composer.add_voice("Strings", program=MidiInstrument.STRING_ENSEMBLE, channel=2)
composer.add_voice("Brass", program=MidiInstrument.TRUMPET, channel=3)

for i, name in enumerate(SECTION_NAMES):
    composer.add_section(name, bars=SECTION_BARS)

for sec_idx in range(TOTAL_SECTIONS):
    name = SECTION_NAMES[sec_idx]
    chords = PROGRESSION[sec_idx]
    offset = sec_idx * SECTION
    
    drum_unit = build_euclidean_drums(chords[0], offset, sec_idx)
    bass_unit = build_euclidean_bass(chords[0], offset, sec_idx)
    arp_unit = build_dpsm_arpeggios(chords[0], offset, sec_idx)
    pad_unit = build_string_pad(chords[0], offset, sec_idx)
    
    # Brass hits on Euclidean pattern (E(2,4))
    brass_events = []
    c = CHORDS[chords[0]]
    for bar in range(4):
        bar_t = bar * BAR
        if bar % 2 == 0:  # E(2,4) pattern
            t = bar_t
            for p in [c['root3'], c['third3'], c['fifth3']]:
                brass_events.append(MusicEvent(pitch=p + 12, volume=95, 
                                              start_tick=t, end_tick=t + 240))
    pad_to_section(brass_events)
    brass_unit = MusicUnit(events=brass_events)
    
    composer.fill_voice_section("Drums", name, drum_unit)
    composer.fill_voice_section("Bass", name, bass_unit)
    composer.fill_voice_section("Arpeggios", name, arp_unit)
    composer.fill_voice_section("Strings", name, pad_unit)
    composer.fill_voice_section("Brass", name, brass_unit)

ok, msg = composer.validate()
print(f"Validation: {'PASS' if ok else 'FAIL'} — {msg}")
if not ok:
    sys.exit(1)

out_dir = "/opt/data/projects/Styles/Disco/classic/v3"
os.makedirs(out_dir, exist_ok=True)
midi_path = os.path.join(out_dir, "classic_disco_v3.mid")
composer.to_midi(midi_path)
assert os.path.getsize(midi_path) > 40

grid_path = os.path.join(out_dir, "grid_visualization.txt")
write_grid_visualization(composer.matrix, grid_path, ticks_per_character=480,
                         voice_names=["Drums", "Bass", "Arpeggios", "Strings", "Brass"], bpm=BPM)

write_provenance(midi_path, AI_ASSISTED, "disco-classic-v3",
                 parameters={"bpm": BPM, "key": "D minor", "style": "Classic Disco (flowing)",
                            "methods": ["011 Euclidean Groove", "026 DPSM Phase-Shift Minimalism"],
                            "layers": ["Euclidean drums", "Euclidean bass + walking fills",
                                      "DPSM 3-phase arpeggios", "Sustained string pad", "Euclidean brass"]})

print("Classic Disco v3 (Euclidean + DPSM hybrid) done ✓")
