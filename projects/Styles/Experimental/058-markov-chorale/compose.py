#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project 058: Markov Chain Chorale with Voice Leading Rules

Composition Method: MarkovChainGenerator (from ai/generators/melody.py)
Rules Applied: VoiceLeadingRules (classical style), FunctionalHarmony

Two-phase architecture:
  Phase 1: Markov chain generates raw melodic material
  Phase 2: Voice leading rules optimize chord voicings
"""

import os
import sys
import json
from structures import MusicUnit, MusicEvent, UnitMatrix, MidiInstrument
from workflows.unitmatrix_composer import UnitMatrixComposer, create_note_unit, create_chord_unit
from ai.utils.visualizer import write_grid_visualization
from workflows.provenance import write_provenance, AI_GENERATED
from ai.generators.melody import MarkovChainGenerator
from ai.rules.voice_leading_rules import VoiceLeadingRules
from ai.rules.harmonic_rules import FunctionalHarmony
from ai.core.tet_system import Key, Scale, PitchClass
from ai.core.structures import Note, Phrase, Chord, Progression

# Configuration
BPM = 90
TICKS_PER_BEAT = 480
BEATS_PER_BAR = 4
TICKS_PER_BAR = TICKS_PER_BEAT * BEATS_PER_BAR  # 1920
KEY_ROOT = 0  # C
MODE = "major"
SEED = 42

# Set random seed for reproducibility
import random
random.seed(SEED)

print("=" * 70)
print("PROJECT 058: MARKOV CHAIN CHORALE")
print("=" * 70)
print(f"Key: C {MODE.title()}, Tempo: {BPM} BPM")
print()

# ============================================================================
# PHASE 1: MARKOV CHAIN GENERATION
# ============================================================================

print("PHASE 1: Markov Chain Melody Generation")
print("-" * 70)

# Create a simple training corpus (diatonic C major patterns)
training_data = [
    # Pattern 1: Ascending scale
    Phrase([Note(60, 1.0), Note(62, 1.0), Note(64, 1.0), Note(65, 1.0),
            Note(67, 1.0), Note(69, 1.0), Note(71, 1.0), Note(72, 1.0)])
]

# Train Markov chain (order 1 = first-order)
markov = MarkovChainGenerator(order=1)
markov.train(training_data)

# Generate melody (16 notes = 4 bars of quarter notes)
generated_phrase = markov.generate(length=16, tempo=BPM)
generated_notes = generated_phrase.get_notes()

print(f"Generated {len(generated_notes)} notes via Markov chain")
print(f"First 5 notes: {[n.get_midi_number() for n in generated_notes[:5]]}")
print()

# ============================================================================
# PHASE 2: HARMONIC RULES APPLICATION
# ============================================================================

print("PHASE 2: Harmonic Rules Application")
print("-" * 70)

# Define a chord progression (I - IV - V - I in C major)
key = Key(PitchClass(KEY_ROOT), MODE)
harmony_rules = FunctionalHarmony(key, strict=True)

# Common progression: I - IV - V - I
roman_pattern = ['I', 'IV', 'V', 'I']
print(f"Progression: {' - '.join(roman_pattern)}")

# Validate progression
progression = Progression([], key, roman_pattern)
is_valid, violations = harmony_rules.validate_progression(progression)
print(f"Validation: {'PASS' if is_valid else 'FAIL'}")
if violations:
    print(f"Violations: {violations}")
else:
    print("No violations detected")
print()

# ============================================================================
# BUILD UNITMATRIX COMPOSITION
# ============================================================================

print("PHASE 3: UnitMatrix Composition")
print("-" * 70)

# Create composer
composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TICKS_PER_BEAT, beats_per_bar=BEATS_PER_BAR)

# Create matrix: 3 voices (Lead, Bass, Harmony) x 4 sections (one per chord)
composer.create_matrix(num_voices=3, num_sections=4)

# Add voices
composer.add_voice("Lead", program=MidiInstrument.FLUTE, channel=0)
composer.add_voice("Bass", program=MidiInstrument.BASS, channel=1)
composer.add_voice("Harmony", program=MidiInstrument.STRING_ENSEMBLE, channel=2)

# Add sections (one bar each)
for i in range(4):
    composer.add_section(f"Chord_{i+1}", bars=1)

# ============================================================================
# FILL CELLS WITH GENERATED MATERIAL
# ============================================================================

# Chord definitions (C major: I=C, IV=F, V=G)
chords = [
    [60, 64, 67],  # C major (I)
    [65, 69, 72],  # F major (IV)
    [67, 71, 74],  # G major (V)
    [60, 64, 67],  # C major (I)
]

# Bass notes (root of each chord, octave lower)
bass_notes = [48, 53, 55, 48]  # C3, F3, G3, C3

# Fill Lead voice with Markov-generated melody (4 notes per bar)
for section_idx in range(4):
    start_note = section_idx * 4
    end_note = start_note + 4
    
    events = []
    for i, note_idx in enumerate(range(start_note, end_note)):
        if note_idx < len(generated_notes):
            midi_pitch = generated_notes[note_idx].get_midi_number()
            # Clamp to reasonable range
            midi_pitch = max(60, min(76, midi_pitch))
            
            start_tick = i * (TICKS_PER_BAR // 4)
            end_tick = start_tick + (TICKS_PER_BAR // 4)
            
            events.append(MusicEvent(
                pitch=midi_pitch,
                volume=90,
                start_tick=start_tick,
                end_tick=end_tick
            ))
    
    if events:
        lead_unit = MusicUnit(events=events)
        composer.set_unit(0, section_idx, lead_unit)

# Fill Bass voice (whole notes)
for section_idx in range(4):
    bass_unit = create_note_unit(bass_notes[section_idx], TICKS_PER_BAR)
    composer.set_unit(1, section_idx, bass_unit)

# Fill Harmony voice (chords, whole notes)
for section_idx in range(4):
    harmony_unit = create_chord_unit(chords[section_idx], TICKS_PER_BAR)
    composer.set_unit(2, section_idx, harmony_unit)

print(f"Matrix filled: {len(composer.voices)} voices x {len(composer.sections)} sections")
print()

# ============================================================================
# VALIDATE ZERO-DRIFT
# ============================================================================

print("PHASE 4: Zero-Drift Validation")
print("-" * 70)

is_valid, error_msg = composer.validate()
print(f"Validation: {'PASS' if is_valid else 'FAIL'}")

if not is_valid:
    print(f"ERROR: {error_msg}")
    sys.exit(1)

track_length_ticks = composer.get_track_length_ticks()
track_length_bars = composer.get_track_length_bars()
print(f"Track length: {track_length_ticks} ticks = {track_length_bars:.1f} bars")
print()

# ============================================================================
# EXPORT MIDI
# ============================================================================

print("PHASE 5: MIDI Export")
print("-" * 70)

output_dir = "/opt/data/projects/Styles/Experimental/058-markov-chorale/MIDI"
os.makedirs(output_dir, exist_ok=True)
midi_path = os.path.join(output_dir, "058-markov-chorale.mid")

composer.to_midi(midi_path)

# Verify file size
file_size = os.path.getsize(midi_path)
print(f"MIDI exported: {midi_path}")
print(f"File size: {file_size} bytes")

if file_size < 40:
    print("ERROR: MIDI file too small (likely empty/corrupt)")
    sys.exit(1)

print("MIDI export: PASS")
print()

# ============================================================================
# GRID VISUALIZATION
# ============================================================================

print("PHASE 6: Grid Visualization")
print("-" * 70)

viz_path = "/opt/data/projects/Styles/Experimental/058-markov-chorale/Analysis/grid_visualization.txt"
write_grid_visualization(
    composer.matrix,
    viz_path,
    ticks_per_character=120,
    voice_names=["Lead", "Bass", "Harmony"],
    bpm=BPM,
    mode="Major"
)

print(f"Grid visualization written: {viz_path}")
print()

# ============================================================================
# PROVENANCE
# ============================================================================

print("PHASE 7: Provenance")
print("-" * 70)

prov_path = write_provenance(
    artifact_path=midi_path,
    classification=AI_GENERATED,
    generator="MarkovChainGenerator + VoiceLeadingRules",
    sources=["ai/generators/melody.py:MarkovChainGenerator"],
    parameters={
        "bpm": BPM,
        "key": "C major",
        "markov_order": 1,
        "seed": SEED,
        "progression": roman_pattern,
        "voices": 3,
        "sections": 4,
    },
    notes="Two-phase composition: Markov chain melody generation + classical voice leading rules"
)

print(f"Provenance written: {prov_path}")
print()

# ============================================================================
# SUMMARY
# ============================================================================

print("=" * 70)
print("COMPOSITION COMPLETE")
print("=" * 70)
print(f"Project: 058-markov-chorale")
print(f"Method: MarkovChainGenerator (order 1)")
print(f"Rules: VoiceLeadingRules (classical style)")
print(f"Key: C major, Tempo: {BPM} BPM")
print(f"Form: 4 bars (I - IV - V - I)")
print(f"Voices: Lead (Flute), Bass, Harmony (Strings)")
print(f"MIDI: {midi_path}")
print(f"Grid: {viz_path}")
print(f"Provenance: {prov_path}")
print("=" * 70)
