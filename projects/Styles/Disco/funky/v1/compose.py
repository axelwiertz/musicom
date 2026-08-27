#!/usr/bin/env python3
"""Funky Disco (1979-82 style)
Methods: Syncopated 16th-note hi-hat, slap bass, wah-wah guitar, horn stabs
Key: E minor | BPM: 118 | 32 bars
"""

import os, sys
from structures import MusicUnit, MusicEvent, UnitMatrix, MidiInstrument, MidiPercussion
from workflows.unitmatrix_composer import (
    UnitMatrixComposer, create_note_unit, create_chord_unit, create_empty_unit,
)
from ai.utils.visualizer import write_grid_visualization
from workflows.provenance import write_provenance, AI_ASSISTED

TPB = 480
BPM = 118
BEATS_PER_BAR = 4
BAR = TPB * BEATS_PER_BAR
SECTION_BARS = 4
SECTION = BAR * SECTION_BARS
TOTAL_SECTIONS = 8

# E minor: E F# G A B C D
# Em7: E G B D = 52 55 59 62
# Am7: A C E G = 57 60 64 67
# Bm7: B D F# A = 59 62 66 69
# Cmaj7: C E G B = 60 64 67 71

CHORDS = {
    'Em7': {'root': 52, 'third': 55, 'fifth': 59, 'flat7': 62,
            'root3': 64, 'third3': 67, 'fifth3': 71, 'flat7_3': 74,
            'bass': 40},
    'Am7': {'root': 57, 'third': 60, 'fifth': 64, 'flat7': 67,
            'root3': 69, 'third3': 72, 'fifth3': 76, 'flat7_3': 79,
            'bass': 45},
    'Bm7': {'root': 59, 'third': 62, 'fifth': 66, 'flat7': 69,
            'root3': 71, 'third3': 74, 'fifth3': 78, 'flat7_3': 81,
            'bass': 47},
    'Cmaj7': {'root': 60, 'third': 64, 'fifth': 67, 'maj7': 71,
              'root3': 72, 'third3': 76, 'fifth3': 79, 'maj7_3': 83,
              'bass': 48},
}

PROGRESSION = [
    ['Em7', 'Am7', 'Em7', 'Bm7'],   # A1
    ['Em7', 'Am7', 'Cmaj7', 'Bm7'], # A2
    ['Am7', 'Bm7', 'Em7', 'Em7'],   # B1
    ['Em7', 'Am7', 'Em7', 'Bm7'],   # A3
    ['Em7', 'Am7', 'Cmaj7', 'Bm7'], # A4
    ['Am7', 'Bm7', 'Em7', 'Em7'],   # B2
    ['Em7', 'Cmaj7', 'Am7', 'Bm7'], # C1
    ['Em7', 'Cmaj7', 'Em7', 'Em7'], # C2
]
SECTION_NAMES = ['A1', 'A2', 'B1', 'A3', 'A4', 'B2', 'C1', 'C2']

def pad_to_section(events):
    if not events or events[-1].end_tick < SECTION:
        events.append(MusicEvent(pitch=0, volume=0, start_tick=SECTION - 10, end_tick=SECTION))

def build_16th_hat_kick(chord_name, section_offset):
    """Four-on-the-floor + 16th-note hi-hat pattern"""
    events = []
    sixteenth = TPB // 4
    for bar in range(4):
        bar_t = bar * BAR
        # Kick on every beat
        for beat in range(4):
            t = bar_t + beat * TPB
            events.append(MusicEvent(pitch=36, volume=115, start_tick=t, end_tick=t + 100))
        # 16th-note hi-hat (accented on offbeats)
        for i in range(16):
            t = bar_t + i * sixteenth
            vol = 75 if i % 4 == 2 else 55  # accent on "and" of each beat
            events.append(MusicEvent(pitch=42, volume=vol, start_tick=t, end_tick=t + 40))
        # Snare on 2 & 4
        events.append(MusicEvent(pitch=38, volume=105, start_tick=bar_t + TPB, end_tick=bar_t + TPB + 100))
        events.append(MusicEvent(pitch=38, volume=105, start_tick=bar_t + 3 * TPB, end_tick=bar_t + 3 * TPB + 100))
        # Open hi-hat on and-of-4
        events.append(MusicEvent(pitch=46, volume=80, start_tick=bar_t + 3 * TPB + TPB // 2, end_tick=bar_t + 3 * TPB + TPB // 2 + 80))
    pad_to_section(events)
    return MusicUnit(events=events)

def build_slap_bass(chord_name, section_offset):
    """Slap bass: octave jumps + ghost notes"""
    c = CHORDS[chord_name]
    events = []
    sixteenth = TPB // 4
    for bar in range(4):
        bar_t = bar * BAR
        # Slap pattern: root (beat 1), octave slap (and-of-2), ghost (beat 3), fifth (and-of-4)
        pattern = [
            (c['bass'], 110, 0),
            (c['bass'] + 12, 95, TPB + TPB // 2),
            (c['bass'] + 2, 60, 2 * TPB),  # ghost
            (c['bass'] + 7, 100, 3 * TPB + TPB // 2),
        ]
        for pitch, vol, offset in pattern:
            t = bar_t + offset
            events.append(MusicEvent(pitch=pitch, volume=vol, start_tick=t, end_tick=t + 160))
    pad_to_section(events)
    return MusicUnit(events=events)

def build_wah_guitar(chord_name, section_offset):
    """Wah-wah guitar: 16th-note funk strumming"""
    c = CHORDS[chord_name]
    events = []
    sixteenth = TPB // 4
    for bar in range(4):
        bar_t = bar * BAR
        # 16th-note strum pattern (muted + open)
        for i in range(16):
            t = bar_t + i * sixteenth
            # Muted scratches on most 16ths, open chord on offbeats
            if i % 4 == 2:  # "and" of each beat
                # Open chord: 3rd, 5th, 7th
                for p in [c['third3'], c['fifth3'], c['flat7_3']]:
                    events.append(MusicEvent(pitch=p, volume=70, start_tick=t, end_tick=t + 80))
            else:
                # Muted scratch
                events.append(MusicEvent(pitch=c['root3'], volume=40, start_tick=t, end_tick=t + 40))
    pad_to_section(events)
    return MusicUnit(events=events)

def build_horn_stabs(chord_name, section_offset):
    """Horn section stabs: syncopated hits"""
    c = CHORDS[chord_name]
    events = []
    for bar in range(4):
        bar_t = bar * BAR
        # Stabs on: beat 1, and-of-2, beat 4
        stab_times = [0, TPB + TPB // 2, 3 * TPB]
        for t_offset in stab_times:
            t = bar_t + t_offset
            # Horn chord: root, 3rd, 5th (bright voicing)
            for p in [c['root3'] + 12, c['third3'] + 12, c['fifth3'] + 12]:
                events.append(MusicEvent(pitch=p, volume=90, start_tick=t, end_tick=t + 140))
    pad_to_section(events)
    return MusicUnit(events=events)

# Build composition
print("Building Funky Disco...")
composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS_PER_BAR)
composer.create_matrix(num_voices=4, num_sections=TOTAL_SECTIONS)

composer.add_voice("Drums", program=0, channel=9)
composer.add_voice("Bass", program=MidiInstrument.BASS, channel=0)
composer.add_voice("Guitar", program=MidiInstrument.ACOUSTIC_GUITAR, channel=1)
composer.add_voice("Horns", program=MidiInstrument.TRUMPET, channel=2)

for i, name in enumerate(SECTION_NAMES):
    composer.add_section(name, bars=SECTION_BARS)

for sec_idx in range(TOTAL_SECTIONS):
    name = SECTION_NAMES[sec_idx]
    chords = PROGRESSION[sec_idx]
    offset = sec_idx * SECTION
    
    drum_unit = build_16th_hat_kick(chords[0], offset)
    bass_unit = build_slap_bass(chords[0], offset)
    guitar_unit = build_wah_guitar(chords[0], offset)
    horn_unit = build_horn_stabs(chords[0], offset)
    
    composer.fill_voice_section("Drums", name, drum_unit)
    composer.fill_voice_section("Bass", name, bass_unit)
    composer.fill_voice_section("Guitar", name, guitar_unit)
    composer.fill_voice_section("Horns", name, horn_unit)

ok, msg = composer.validate()
print(f"Validation: {'PASS' if ok else 'FAIL'} — {msg}")
if not ok:
    sys.exit(1)

out_dir = "/opt/data/projects/Styles/Disco/funky/v1"
midi_path = os.path.join(out_dir, "funky_disco.mid")
composer.to_midi(midi_path)
assert os.path.getsize(midi_path) > 40

grid_path = os.path.join(out_dir, "grid_visualization.txt")
write_grid_visualization(composer.matrix, grid_path, ticks_per_character=480,
                         voice_names=["Drums", "Bass", "Guitar", "Horns"], bpm=BPM)

write_provenance(midi_path, AI_ASSISTED, "disco-funky",
                 parameters={"bpm": BPM, "key": "E minor", "style": "Funky Disco 1979-82",
                            "methods": ["16th-note hi-hat", "slap bass", "wah-wah guitar", "horn stabs"]})

print("Funky Disco done ✓")
