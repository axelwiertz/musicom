#!/usr/bin/env python3
"""Modern/Italo Disco (1983-86 style)
Methods: Arpeggiated synth bass, sequenced leads, electronic percussion, sidechain pumping
Key: A minor | BPM: 126 | 32 bars
"""

import os, sys
from structures import MusicUnit, MusicEvent, UnitMatrix, MidiInstrument, MidiPercussion
from workflows.unitmatrix_composer import (
    UnitMatrixComposer, create_note_unit, create_chord_unit, create_empty_unit,
)
from ai.utils.visualizer import write_grid_visualization
from workflows.provenance import write_provenance, AI_ASSISTED

TPB = 480
BPM = 126
BEATS_PER_BAR = 4
BAR = TPB * BEATS_PER_BAR
SECTION_BARS = 4
SECTION = BAR * SECTION_BARS
TOTAL_SECTIONS = 8

# A minor: A B C D E F G
# Am7: A C E G = 57 60 64 67
# Dm7: D F A C = 62 65 69 72
# Em7: E G B D = 64 67 71 74
# Fmaj7: F A C E = 65 69 72 76

CHORDS = {
    'Am7': {'root': 57, 'third': 60, 'fifth': 64, 'flat7': 67,
            'root3': 69, 'third3': 72, 'fifth3': 76, 'flat7_3': 79,
            'bass': 45},
    'Dm7': {'root': 62, 'third': 65, 'fifth': 69, 'flat7': 72,
            'root3': 74, 'third3': 77, 'fifth3': 81, 'flat7_3': 84,
            'bass': 50},
    'Em7': {'root': 64, 'third': 67, 'fifth': 71, 'flat7': 74,
            'root3': 76, 'third3': 79, 'fifth3': 83, 'flat7_3': 86,
            'bass': 52},
    'Fmaj7': {'root': 65, 'third': 69, 'fifth': 72, 'maj7': 76,
              'root3': 77, 'third3': 81, 'fifth3': 84, 'maj7_3': 88,
              'bass': 53},
}

PROGRESSION = [
    ['Am7', 'Dm7', 'Am7', 'Em7'],   # A1
    ['Am7', 'Dm7', 'Fmaj7', 'Em7'], # A2
    ['Dm7', 'Em7', 'Am7', 'Am7'],   # B1
    ['Am7', 'Dm7', 'Am7', 'Em7'],   # A3
    ['Am7', 'Dm7', 'Fmaj7', 'Em7'], # A4
    ['Dm7', 'Em7', 'Am7', 'Am7'],   # B2
    ['Am7', 'Fmaj7', 'Dm7', 'Em7'], # C1
    ['Am7', 'Fmaj7', 'Am7', 'Am7'], # C2
]
SECTION_NAMES = ['A1', 'A2', 'B1', 'A3', 'A4', 'B2', 'C1', 'C2']

def pad_to_section(events):
    if not events or events[-1].end_tick < SECTION:
        events.append(MusicEvent(pitch=0, volume=0, start_tick=SECTION - 10, end_tick=SECTION))

def build_electronic_drums(chord_name, section_offset):
    """Electronic drums: tight kick, clap, 16th hats"""
    events = []
    sixteenth = TPB // 4
    for bar in range(4):
        bar_t = bar * BAR
        # Tight kick on every beat
        for beat in range(4):
            t = bar_t + beat * TPB
            events.append(MusicEvent(pitch=36, volume=120, start_tick=t, end_tick=t + 80))
        # 16th-note hi-hat (closed)
        for i in range(16):
            t = bar_t + i * sixteenth
            vol = 60 if i % 2 == 0 else 45
            events.append(MusicEvent(pitch=42, volume=vol, start_tick=t, end_tick=t + 30))
        # Clap on 2 & 4
        events.append(MusicEvent(pitch=39, volume=105, start_tick=bar_t + TPB, end_tick=bar_t + TPB + 80))
        events.append(MusicEvent(pitch=39, volume=105, start_tick=bar_t + 3 * TPB, end_tick=bar_t + 3 * TPB + 80))
        # Open hat on and-of-4
        events.append(MusicEvent(pitch=46, volume=75, start_tick=bar_t + 3 * TPB + TPB // 2, end_tick=bar_t + 3 * TPB + TPB // 2 + 60))
    pad_to_section(events)
    return MusicUnit(events=events)

def build_arpeggiated_bass(chord_name, section_offset):
    """Arpeggiated synth bass: 16th-note arpeggios"""
    c = CHORDS[chord_name]
    events = []
    sixteenth = TPB // 4
    for bar in range(4):
        bar_t = bar * BAR
        # 16th-note arpeggio pattern: root-3rd-5th-7th-5th-3rd-root-3rd
        arp_pattern = [
            c['bass'], c['root'], c['third'], c['fifth'],
            c['third'], c['root'], c['bass'], c['root']
        ]
        for i in range(16):
            t = bar_t + i * sixteenth
            pitch = arp_pattern[i % 8]
            vol = 95 if i % 4 == 0 else 80
            events.append(MusicEvent(pitch=pitch, volume=vol, start_tick=t, end_tick=t + 100))
    pad_to_section(events)
    return MusicUnit(events=events)

def build_sequenced_lead(chord_name, section_offset):
    """Sequenced synth lead: 8th-note melodic pattern"""
    c = CHORDS[chord_name]
    events = []
    eighth = TPB // 2
    for bar in range(4):
        bar_t = bar * BAR
        # 8th-note sequence: root-5th-3rd-7th pattern
        seq_pattern = [
            c['root3'], c['fifth3'], c['third3'], c['flat7_3'],
            c['root3'], c['third3'], c['fifth3'], c['root3']
        ]
        for i in range(8):
            t = bar_t + i * eighth
            pitch = seq_pattern[i]
            vol = 90 if i % 2 == 0 else 75
            events.append(MusicEvent(pitch=pitch, volume=vol, start_tick=t, end_tick=t + 180))
    pad_to_section(events)
    return MusicUnit(events=events)

def build_synth_pad(chord_name, section_offset):
    """Sustained synth pad with sidechain pumping effect"""
    c = CHORDS[chord_name]
    events = []
    for bar in range(4):
        bar_t = bar * BAR
        # Pad chord sustained, with volume dips on beats (sidechain simulation)
        for beat in range(4):
            t = bar_t + beat * TPB
            # Loud part (between kicks)
            for p in [c['root3'], c['third3'], c['fifth3']]:
                events.append(MusicEvent(pitch=p, volume=85, start_tick=t + 120, end_tick=t + TPB - 40))
            # Quiet part (on kick)
            for p in [c['root3'], c['third3'], c['fifth3']]:
                events.append(MusicEvent(pitch=p, volume=50, start_tick=t, end_tick=t + 120))
    pad_to_section(events)
    return MusicUnit(events=events)

# Build composition
print("Building Modern/Italo Disco...")
composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS_PER_BAR)
composer.create_matrix(num_voices=4, num_sections=TOTAL_SECTIONS)

composer.add_voice("Drums", program=0, channel=9)
composer.add_voice("Bass", program=MidiInstrument.SYNTH_PAD, channel=0)
composer.add_voice("Lead", program=MidiInstrument.FLUTE, channel=1)
composer.add_voice("Pad", program=MidiInstrument.STRING_ENSEMBLE, channel=2)

for i, name in enumerate(SECTION_NAMES):
    composer.add_section(name, bars=SECTION_BARS)

for sec_idx in range(TOTAL_SECTIONS):
    name = SECTION_NAMES[sec_idx]
    chords = PROGRESSION[sec_idx]
    offset = sec_idx * SECTION
    
    drum_unit = build_electronic_drums(chords[0], offset)
    bass_unit = build_arpeggiated_bass(chords[0], offset)
    lead_unit = build_sequenced_lead(chords[0], offset)
    pad_unit = build_synth_pad(chords[0], offset)
    
    composer.fill_voice_section("Drums", name, drum_unit)
    composer.fill_voice_section("Bass", name, bass_unit)
    composer.fill_voice_section("Lead", name, lead_unit)
    composer.fill_voice_section("Pad", name, pad_unit)

ok, msg = composer.validate()
print(f"Validation: {'PASS' if ok else 'FAIL'} — {msg}")
if not ok:
    sys.exit(1)

out_dir = "/opt/data/projects/Styles/Disco/modern/v1"
midi_path = os.path.join(out_dir, "modern_disco.mid")
composer.to_midi(midi_path)
assert os.path.getsize(midi_path) > 40

grid_path = os.path.join(out_dir, "grid_visualization.txt")
write_grid_visualization(composer.matrix, grid_path, ticks_per_character=480,
                         voice_names=["Drums", "Bass", "Lead", "Pad"], bpm=BPM)

write_provenance(midi_path, AI_ASSISTED, "disco-modern",
                 parameters={"bpm": BPM, "key": "A minor", "style": "Modern/Italo Disco 1983-86",
                            "methods": ["arpeggiated bass", "sequenced lead", "electronic drums", "sidechain pad"]})

print("Modern/Italo Disco done ✓")
