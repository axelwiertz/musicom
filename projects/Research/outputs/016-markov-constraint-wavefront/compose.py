#!/usr/bin/env python3
"""Method 022: Markov-Constraint Wavefront Sequencing (MCWS) composition.

Phase 1: Generative method (MarkovConstraintGenerator) produces raw pitch sequences
Phase 2: Musicom rules post-processing (voice leading + harmonic progression)

Uses UnitMatrix workflow for zero-drift absolute alignment.
"""
import sys
sys.path.insert(0, '/opt/data/repos/musicom')

from structures import MusicUnit, MusicEvent, UnitMatrix, MidiInstrument
from workflows.unitmatrix_composer import UnitMatrixComposer, create_note_unit, create_chord_unit
from generators.markov_constraint import MarkovConstraintGenerator
from rules.voice_leading import VoiceLeadingRules
from visualization.grid import write_grid_visualization

import json
from datetime import datetime

# ============================================================
# PHASE 1: Generative Method — Markov-Constraint Wavefront
# ============================================================
print("="*60)
print("PHASE 1: Markov-Constraint Wavefront Sequencing (MCWS)")
print("="*60)

TONIC = 69  # A4
A_MINOR_INTERVALS = [0, 2, 3, 5, 7, 8, 10]
key_pitches = [TONIC + i for i in A_MINOR_INTERVALS] + [TONIC + 12 + i for i in A_MINOR_INTERVALS]
key_pitches = [p for p in key_pitches if 48 <= p <= 84]

print(f"Key: A minor (tonic={TONIC})")
print(f"Key pitches: {key_pitches}")

mcg = MarkovConstraintGenerator(
    key_pitches=key_pitches,
    default_pitch=TONIC,
    min_pitch=48,
    max_pitch=84
)

SECTION_TICKS = 1920
STEP_TICKS = 240

sections_config = [
    {"name": "Verse_A", "density": 0.6, "volume": 85},
    {"name": "Chorus_B", "density": 0.85, "volume": 95},
    {"name": "Verse_A2", "density": 0.65, "volume": 85},
    {"name": "Chorus_B2", "density": 0.9, "volume": 98},
]

raw_sections = []
previous_pitch = TONIC

for i, cfg in enumerate(sections_config):
    unit = mcg.generate_voice_section(
        section_ticks=SECTION_TICKS,
        step_ticks=STEP_TICKS,
        previous_pitch=previous_pitch,
        density=cfg["density"],
        volume=cfg["volume"]
    )
    raw_sections.append(unit)
    if unit.events:
        previous_pitch = unit.events[-1].pitch
    print(f"  Section {cfg['name']}: {len(unit.events)} events, density={cfg['density']}")

print(f"\nPhase 1 complete: Generated {len(raw_sections)} sections")

# ============================================================
# PHASE 2: Musicom Rules Post-Processing
# ============================================================
print("\n" + "="*60)
print("PHASE 2: Musicom Rules Post-Processing")
print("="*60)

# Chord voicings: [soprano, alto, bass] within proper ranges
chord_voicings = [
    [69, 60, 52],  # Amin(i): A4, C5, E4
    [71, 68, 52],  # Emaj(V): B4, G#4, E4
    [69, 60, 52],  # Amin(i)
    [71, 68, 52],  # Emaj(V)
]
chord_names = ["Amin(i)", "Emaj(V)", "Amin(i)", "Emaj(V)"]

print("Harmonic progression (A minor):")
for i, (chord, name) in enumerate(zip(chord_voicings, chord_names)):
    print(f"  Section {i} ({sections_config[i]['name']}): {name} soprano={chord[0]} alto={chord[1]} bass={chord[2]}")

# Voice leading check
vl_rules = VoiceLeadingRules(style='classical')
print("\nVoice leading checks (chord-to-chord):")
for i in range(len(chord_voicings) - 1):
    violations = vl_rules.check_parallel_motion(chord_voicings[i], chord_voicings[i+1])
    if violations:
        print(f"  Between {i} and {i+1}: {violations}")
    else:
        print(f"  Between {i} and {i+1}: OK")

# Range check
voice_ranges = {'soprano': (60, 81), 'alto': (53, 74), 'bass': (48, 65)}
for i, chord in enumerate(chord_voicings):
    violations = vl_rules.validate_voice_ranges(chord, voice_ranges)
    if violations:
        print(f"  Section {i} range violations: {violations}")
    else:
        print(f"  Section {i} ranges: OK")

# Quantize melody to chord tones
def nearest_chord_tone(pitch, chord_tones):
    candidates = []
    for ct in chord_tones:
        for octave in [-12, 0, 12, 24]:
            candidates.append(ct + octave)
    return min(candidates, key=lambda x: abs(x - pitch))

melody_sections = []
for i, unit in enumerate(raw_sections):
    chord_tones = chord_voicings[i]
    refined_events = []
    for ev in unit.events:
        if ev.pitch > 0:
            new_pitch = nearest_chord_tone(ev.pitch, chord_tones)
            new_pitch = max(48, min(84, new_pitch))
        else:
            new_pitch = 0
        refined_events.append(MusicEvent(
            pitch=new_pitch,
            volume=ev.volume,
            start_tick=ev.start_tick,
            end_tick=ev.end_tick
        ))
    if refined_events:
        last_end = max(e.end_tick for e in refined_events)
        if last_end < SECTION_TICKS:
            refined_events.append(MusicEvent(pitch=0, volume=0, start_tick=last_end, end_tick=SECTION_TICKS))
    else:
        refined_events.append(MusicEvent(pitch=0, volume=0, start_tick=0, end_tick=SECTION_TICKS))
    refined_unit = MusicUnit(events=refined_events)
    melody_sections.append(refined_unit)
    print(f"  Section {i}: Quantized {len(refined_events)} events to {chord_names[i]}")

# ============================================================
# Phase 3: UnitMatrix Assembly with Zero-Drift Validation
# ============================================================
print("\n" + "="*60)
print("PHASE 3: UnitMatrix Assembly")
print("="*60)

composer = UnitMatrixComposer(bpm=100, ticks_per_beat=480, beats_per_bar=4)
composer.create_matrix(num_voices=4, num_sections=4)

composer.add_voice("Melody", program=MidiInstrument.FLUTE, channel=0)
composer.add_voice("Inner", program=MidiInstrument.STRING_ENSEMBLE, channel=1)
composer.add_voice("Harmony", program=MidiInstrument.STRING_ENSEMBLE, channel=2)
composer.add_voice("Bass", program=MidiInstrument.BASS, channel=3)

for i, cfg in enumerate(sections_config):
    composer.add_section(cfg["name"], bars=4)

# Fill melody
for i, unit in enumerate(melody_sections):
    composer.set_unit(0, i, unit)

# Fill harmony with sustained chords
for i, chord in enumerate(chord_voicings):
    chord_unit = create_chord_unit(chord, SECTION_TICKS)
    composer.set_unit(2, i, chord_unit)

# Fill bass with root notes
for i, chord in enumerate(chord_voicings):
    root = chord[2]
    bass_unit = create_note_unit(root, SECTION_TICKS)
    composer.set_unit(3, i, bass_unit)

# Inner voice: arpeggiated chord tones - fill full duration
for i, chord in enumerate(chord_voicings):
    inner_events = []
    arp_notes = [chord[0], chord[1], chord[2], chord[1]]  # s, a, b, a
    ticks_per_note = SECTION_TICKS // len(arp_notes)
    for j, note in enumerate(arp_notes):
        start = j * ticks_per_note
        end = start + ticks_per_note
        inner_events.append(MusicEvent(
            pitch=note, volume=70,
            start_tick=start, end_tick=end
        ))
    last_end = inner_events[-1].end_tick if inner_events else 0
    if last_end < SECTION_TICKS:
        inner_events.append(MusicEvent(pitch=0, volume=0, start_tick=last_end, end_tick=SECTION_TICKS))
    inner_unit = MusicUnit(events=inner_events)
    composer.set_unit(1, i, inner_unit)

# Validate zero-drift
is_valid, msg = composer.validate()
print(f"Zero-drift validation: {msg}")
assert is_valid, f"Validation failed: {msg}"

print("UnitMatrix assembly complete.")

# ============================================================
# Phase 4: Export
# ============================================================
print("\n" + "="*60)
print("PHASE 4: Export")
print("="*60)

project_dir = "/opt/data/projects/Research/outputs/016-markov-constraint-wavefront"

midi_path = f"{project_dir}/016-markov-constraint-wavefront.mid"
composer.to_midi(midi_path)
print(f"MIDI exported: {midi_path}")

import os
midi_size = os.path.getsize(midi_path)
print(f"MIDI file size: {midi_size} bytes")
assert midi_size > 40, "MIDI file too small!"

grid_viz = write_grid_visualization(composer.matrix, project_dir + "/grid_visualization.txt", ticks_per_character=120, voice_names=["Melody", "Inner", "Harmony", "Bass"], bpm=100, mode="A minor")
print(f"Grid visualization: {grid_viz}")

provenance = {
    "composition_method": "Markov-Constraint Wavefront Sequencing (MCWS) / Method 022",
    "classification": "ai-assisted",
    "generator": "MarkovConstraintGenerator",
    "rules_applied": [
        "voice_leading (classical style)",
        "harmonic_progression (A minor: i - V - i - V)",
        "chord_tone_quantization",
        "zero_drift_validation"
    ],
    "key": "A minor",
    "tonic": TONIC,
    "bpm": 100,
    "ticks_per_beat": 480,
    "form": "A-B-A-B (Verse-Chorus-Verse-Chorus)",
    "sections": [
        {"name": "Verse_A", "density": 0.6, "chord": "Amin(i)"},
        {"name": "Chorus_B", "density": 0.85, "chord": "Emaj(V)"},
        {"name": "Verse_A2", "density": 0.65, "chord": "Amin(i)"},
        {"name": "Chorus_B2", "density": 0.9, "chord": "Emaj(V)"}
    ],
    "voices": ["Melody", "Inner", "Harmony", "Bass"],
    "validation": {
        "zero_drift_passed": is_valid,
        "message": msg
    },
    "timestamp": datetime.utcnow().isoformat() + "Z",
    "source_repos": ["musicom"],
    "phase_architecture": "two-phase (generative MCWS -> musicom rules)"
}

provenance_path = f"{project_dir}/provenance.json"
with open(provenance_path, 'w') as f:
    json.dump(provenance, f, indent=2)
print(f"Provenance: {provenance_path}")

print("\n" + "="*60)
print("COMPOSITION COMPLETE")
print("="*60)
print(f"Project: 016-markov-constraint-wavefront")
print(f"Method: Markov-Constraint Wavefront Sequencing (MCWS)")
print(f"Rules: Voice leading (classical) + Harmonic progression")
print(f"Output: {midi_path}")
print(f"Validation: PASSED (zero-drift)")
print("="*60)
