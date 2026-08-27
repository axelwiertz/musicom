#!/usr/bin/env python3
"""Classic Disco (1977-79 style)
Methods: Four-on-the-floor, syncopated bass, string stabs, brass hits
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

# D minor: D E F G A Bb C
# Dm7: D F A C = 62 65 69 72
# Gm7: G Bb D F = 55 58 62 65
# Am7: A C E G = 57 60 64 67
# C7: C E G Bb = 60 64 67 70

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
    ['Dm7', 'Gm7', 'Dm7', 'Am7'],  # A1
    ['Dm7', 'Gm7', 'C7', 'Dm7'],   # A2
    ['Gm7', 'Am7', 'Dm7', 'Dm7'],  # B1
    ['Dm7', 'Gm7', 'Dm7', 'Am7'],  # A3
    ['Dm7', 'Gm7', 'C7', 'Dm7'],   # A4
    ['Gm7', 'Am7', 'Dm7', 'Dm7'],  # B2
    ['Dm7', 'C7', 'Gm7', 'Am7'],   # C1
    ['Dm7', 'C7', 'Dm7', 'Dm7'],   # C2 (turnaround)
]
SECTION_NAMES = ['A1', 'A2', 'B1', 'A3', 'A4', 'B2', 'C1', 'C2']

def pad_to_section(events):
    if not events or events[-1].end_tick < SECTION:
        events.append(MusicEvent(pitch=0, volume=0, start_tick=SECTION - 10, end_tick=SECTION))

def build_four_on_floor(chord_name, section_offset):
    """Four-on-the-floor kick + offbeat hi-hat"""
    events = []
    for bar in range(4):
        bar_t = bar * BAR
        # Kick on every beat
        for beat in range(4):
            t = bar_t + beat * TPB
            events.append(MusicEvent(pitch=36, volume=110, start_tick=t, end_tick=t + 120))
        # Hi-hat offbeats (and-of-each-beat)
        for beat in range(4):
            t = bar_t + beat * TPB + TPB // 2
            events.append(MusicEvent(pitch=42, volume=70, start_tick=t, end_tick=t + 60))
        # Snare on 2 & 4
        events.append(MusicEvent(pitch=38, volume=100, start_tick=bar_t + TPB, end_tick=bar_t + TPB + 120))
        events.append(MusicEvent(pitch=38, volume=100, start_tick=bar_t + 3 * TPB, end_tick=bar_t + 3 * TPB + 120))
        # Crash on section start
        if bar == 0:
            events.append(MusicEvent(pitch=49, volume=90, start_tick=bar_t, end_tick=bar_t + 960))
    pad_to_section(events)
    return MusicUnit(events=events)

def build_syncopated_bass(chord_name, section_offset):
    """Syncopated disco bass: octave jumps, offbeat accents"""
    c = CHORDS[chord_name]
    events = []
    for bar in range(4):
        bar_t = bar * BAR
        # Pattern: root (beat 1), octave (and-of-2), fifth (beat 3), root (and-of-4)
        pattern = [
            (c['bass'], 100, 0),
            (c['bass'] + 12, 85, TPB + TPB // 2),
            (c['bass'] + 7, 95, 2 * TPB),
            (c['bass'], 90, 3 * TPB + TPB // 2),
        ]
        for pitch, vol, offset in pattern:
            t = bar_t + offset
            events.append(MusicEvent(pitch=pitch, volume=vol, start_tick=t, end_tick=t + 200))
    pad_to_section(events)
    return MusicUnit(events=events)

def build_string_stabs(chord_name, section_offset):
    """String section stabs on offbeats"""
    c = CHORDS[chord_name]
    events = []
    for bar in range(4):
        bar_t = bar * BAR
        # Stabs on and-of-1, and-of-3
        stab_times = [TPB // 2, 2 * TPB + TPB // 2]
        for t_offset in stab_times:
            t = bar_t + t_offset
            # String chord: 3rd, 5th, 7th
            for p in [c['third3'], c['fifth3'], c['flat7_3']]:
                events.append(MusicEvent(pitch=p, volume=80, start_tick=t, end_tick=t + 120))
    pad_to_section(events)
    return MusicUnit(events=events)

def build_brass_hits(chord_name, section_offset):
    """Brass section hits on downbeats"""
    c = CHORDS[chord_name]
    events = []
    for bar in range(4):
        bar_t = bar * BAR
        # Hit on beat 1 of bars 1, 3
        if bar in [0, 2]:
            t = bar_t
            # Brass chord: root, 3rd, 5th (octave up)
            for p in [c['root3'], c['third3'], c['fifth3']]:
                events.append(MusicEvent(pitch=p + 12, volume=95, start_tick=t, end_tick=t + 240))
    pad_to_section(events)
    return MusicUnit(events=events)

# Build composition
print("Building Classic Disco...")
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
    
    drum_unit = build_four_on_floor(chords[0], offset)
    bass_unit = build_syncopated_bass(chords[0], offset)
    string_unit = build_string_stabs(chords[0], offset)
    brass_unit = build_brass_hits(chords[0], offset)
    
    composer.fill_voice_section("Drums", name, drum_unit)
    composer.fill_voice_section("Bass", name, bass_unit)
    composer.fill_voice_section("Strings", name, string_unit)
    composer.fill_voice_section("Brass", name, brass_unit)

ok, msg = composer.validate()
print(f"Validation: {'PASS' if ok else 'FAIL'} — {msg}")
if not ok:
    sys.exit(1)

out_dir = "/opt/data/projects/Styles/Disco/classic/v1"
midi_path = os.path.join(out_dir, "classic_disco.mid")
composer.to_midi(midi_path)
assert os.path.getsize(midi_path) > 40

grid_path = os.path.join(out_dir, "grid_visualization.txt")
write_grid_visualization(composer.matrix, grid_path, ticks_per_character=480,
                         voice_names=["Drums", "Bass", "Strings", "Brass"], bpm=BPM)

write_provenance(midi_path, AI_ASSISTED, "disco-classic",
                 parameters={"bpm": BPM, "key": "D minor", "style": "Classic Disco 1977-79",
                            "methods": ["four-on-the-floor", "syncopated bass", "string stabs", "brass hits"]})

print("Classic Disco done ✓")
