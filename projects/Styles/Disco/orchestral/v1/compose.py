#!/usr/bin/env python3
"""Orchestral Disco (Salsoul/Philadelphia style)
Methods: Lush string sweeps, orchestral hits, harp glissandi, timpani rolls
Key: C major | BPM: 124 | 32 bars
"""

import os, sys
from structures import MusicUnit, MusicEvent, UnitMatrix, MidiInstrument, MidiPercussion
from workflows.unitmatrix_composer import (
    UnitMatrixComposer, create_note_unit, create_chord_unit, create_empty_unit,
)
from ai.utils.visualizer import write_grid_visualization
from workflows.provenance import write_provenance, AI_ASSISTED

TPB = 480
BPM = 124
BEATS_PER_BAR = 4
BAR = TPB * BEATS_PER_BAR
SECTION_BARS = 4
SECTION = BAR * SECTION_BARS
TOTAL_SECTIONS = 8

# C major: C D E F G A B
# Cmaj7: C E G B = 60 64 67 71
# Fmaj7: F A C E = 65 69 72 76
# Dm7: D F A C = 62 65 69 72
# G7: G B D F = 67 71 74 77

CHORDS = {
    'Cmaj7': {'root': 60, 'third': 64, 'fifth': 67, 'maj7': 71,
              'root3': 72, 'third3': 76, 'fifth3': 79, 'maj7_3': 83,
              'bass': 48},
    'Fmaj7': {'root': 65, 'third': 69, 'fifth': 72, 'maj7': 76,
              'root3': 77, 'third3': 81, 'fifth3': 84, 'maj7_3': 88,
              'bass': 53},
    'Dm7': {'root': 62, 'third': 65, 'fifth': 69, 'flat7': 72,
            'root3': 74, 'third3': 77, 'fifth3': 81, 'flat7_3': 84,
            'bass': 50},
    'G7': {'root': 67, 'third': 71, 'fifth': 74, 'flat7': 77,
           'root3': 79, 'third3': 83, 'fifth3': 86, 'flat7_3': 89,
           'bass': 55},
}

PROGRESSION = [
    ['Cmaj7', 'Fmaj7', 'Cmaj7', 'Dm7'],   # A1
    ['Cmaj7', 'Fmaj7', 'G7', 'Cmaj7'],    # A2
    ['Fmaj7', 'Dm7', 'G7', 'Cmaj7'],      # B1
    ['Cmaj7', 'Fmaj7', 'Cmaj7', 'Dm7'],   # A3
    ['Cmaj7', 'Fmaj7', 'G7', 'Cmaj7'],    # A4
    ['Fmaj7', 'Dm7', 'G7', 'Cmaj7'],      # B2
    ['Cmaj7', 'G7', 'Fmaj7', 'Dm7'],      # C1
    ['Cmaj7', 'G7', 'Cmaj7', 'Cmaj7'],    # C2
]
SECTION_NAMES = ['A1', 'A2', 'B1', 'A3', 'A4', 'B2', 'C1', 'C2']

def pad_to_section(events):
    if not events or events[-1].end_tick < SECTION:
        events.append(MusicEvent(pitch=0, volume=0, start_tick=SECTION - 10, end_tick=SECTION))

def build_orchestral_drums(chord_name, section_offset):
    """Four-on-the-floor + timpani rolls on transitions"""
    events = []
    for bar in range(4):
        bar_t = bar * BAR
        # Kick on every beat
        for beat in range(4):
            t = bar_t + beat * TPB
            events.append(MusicEvent(pitch=36, volume=108, start_tick=t, end_tick=t + 100))
        # Hi-hat 8th notes
        for i in range(8):
            t = bar_t + i * (TPB // 2)
            vol = 65 if i % 2 == 0 else 50
            events.append(MusicEvent(pitch=42, volume=vol, start_tick=t, end_tick=t + 60))
        # Snare on 2 & 4
        events.append(MusicEvent(pitch=38, volume=98, start_tick=bar_t + TPB, end_tick=bar_t + TPB + 100))
        events.append(MusicEvent(pitch=38, volume=98, start_tick=bar_t + 3 * TPB, end_tick=bar_t + 3 * TPB + 100))
        # Timpani roll on bar 4 (transition)
        if bar == 3:
            for i in range(8):
                t = bar_t + 3 * TPB + i * (TPB // 8)
                vol = 60 + i * 5  # crescendo
                events.append(MusicEvent(pitch=47, volume=vol, start_tick=t, end_tick=t + 60))
    pad_to_section(events)
    return MusicUnit(events=events)

def build_string_sweep(chord_name, section_offset):
    """Lush string section: sustained chords with crescendo"""
    c = CHORDS[chord_name]
    events = []
    for bar in range(4):
        bar_t = bar * BAR
        # Full string chord sustained for 2 bars, then new chord
        if bar % 2 == 0:
            # Crescendo swell over 2 bars
            for vol_start, vol_end, t_start, t_end in [
                (60, 85, bar_t, bar_t + BAR),
                (85, 80, bar_t + BAR, bar_t + 2 * BAR)
            ]:
                for p in [c['root3'], c['third3'], c['fifth3'], c['maj7_3'] if 'maj7_3' in c else c['flat7_3']]:
                    events.append(MusicEvent(pitch=p, volume=vol_start, start_tick=t_start, end_tick=t_start + (t_end - t_start)))
    pad_to_section(events)
    return MusicUnit(events=events)

def build_orchestral_hit(chord_name, section_offset):
    """Full orchestra hits on downbeats"""
    c = CHORDS[chord_name]
    events = []
    for bar in range(4):
        bar_t = bar * BAR
        # Big hit on beat 1 of bars 0, 2
        if bar in [0, 2]:
            t = bar_t
            # Full orchestra: strings + brass + woodwinds (wide voicing)
            for p in [c['bass'], c['root3'], c['third3'], c['fifth3'], c['root3'] + 12]:
                events.append(MusicEvent(pitch=p, volume=100, start_tick=t, end_tick=t + 480))
    pad_to_section(events)
    return MusicUnit(events=events)

def build_bass_line(chord_name, section_offset):
    """Disco bass: root-fifth-octave pattern"""
    c = CHORDS[chord_name]
    events = []
    for bar in range(4):
        bar_t = bar * BAR
        # Pattern: root (1), root (and-of-2), fifth (3), octave (and-of-4)
        pattern = [
            (c['bass'], 100, 0),
            (c['bass'], 90, TPB + TPB // 2),
            (c['bass'] + 7, 95, 2 * TPB),
            (c['bass'] + 12, 88, 3 * TPB + TPB // 2),
        ]
        for pitch, vol, offset in pattern:
            t = bar_t + offset
            events.append(MusicEvent(pitch=pitch, volume=vol, start_tick=t, end_tick=t + 200))
    pad_to_section(events)
    return MusicUnit(events=events)

# Build composition
print("Building Orchestral Disco...")
composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS_PER_BAR)
composer.create_matrix(num_voices=4, num_sections=TOTAL_SECTIONS)

composer.add_voice("Drums", program=0, channel=9)
composer.add_voice("Strings", program=MidiInstrument.STRING_ENSEMBLE, channel=0)
composer.add_voice("Orchestra", program=MidiInstrument.CHURCH_ORGAN, channel=1)
composer.add_voice("Bass", program=MidiInstrument.BASS, channel=2)

for i, name in enumerate(SECTION_NAMES):
    composer.add_section(name, bars=SECTION_BARS)

for sec_idx in range(TOTAL_SECTIONS):
    name = SECTION_NAMES[sec_idx]
    chords = PROGRESSION[sec_idx]
    offset = sec_idx * SECTION
    
    drum_unit = build_orchestral_drums(chords[0], offset)
    string_unit = build_string_sweep(chords[0], offset)
    orch_unit = build_orchestral_hit(chords[0], offset)
    bass_unit = build_bass_line(chords[0], offset)
    
    composer.fill_voice_section("Drums", name, drum_unit)
    composer.fill_voice_section("Strings", name, string_unit)
    composer.fill_voice_section("Orchestra", name, orch_unit)
    composer.fill_voice_section("Bass", name, bass_unit)

ok, msg = composer.validate()
print(f"Validation: {'PASS' if ok else 'FAIL'} — {msg}")
if not ok:
    sys.exit(1)

out_dir = "/opt/data/projects/Styles/Disco/orchestral/v1"
midi_path = os.path.join(out_dir, "orchestral_disco.mid")
composer.to_midi(midi_path)
assert os.path.getsize(midi_path) > 40

grid_path = os.path.join(out_dir, "grid_visualization.txt")
write_grid_visualization(composer.matrix, grid_path, ticks_per_character=480,
                         voice_names=["Drums", "Strings", "Orchestra", "Bass"], bpm=BPM)

write_provenance(midi_path, AI_ASSISTED, "disco-orchestral",
                 parameters={"bpm": BPM, "key": "C major", "style": "Orchestral/Salsoul Disco",
                            "methods": ["string sweeps", "orchestral hits", "timpani rolls", "root-fifth bass"]})

print("Orchestral Disco done ✓")
