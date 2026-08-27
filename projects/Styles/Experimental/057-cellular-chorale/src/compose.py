# -*- coding: utf-8 -*-
"""
Project 057: Cellular Automaton Chorale
Composition Method: Rule 30 Elementary Cellular Automaton
Two-Phase Architecture:
  Phase 1: Rule 30 CA generates raw scale-degree choices per voice per bar
  Phase 2: Voice leading rules (parallel fifths/octaves check + correction)

Key: Eb Major (I-IV-V-vi-ii-V-I cadential plan)
Voices: Soprano (Flute), Alto (Oboe), Tenor (Clarinet), Bass (Bassoon)
Form: 8 bars, homophonic chorale texture
"""
import os
import sys
import json
import numpy as np

# musicom engine (installed editable)
from structures import MusicUnit, MusicEvent, UnitMatrix, MidiInstrument
from workflows.unitmatrix_composer import (
    UnitMatrixComposer, create_note_unit, create_chord_unit, create_empty_unit,
)
from ai.utils.visualizer import write_grid_visualization

# ── Parameters ──────────────────────────────────────────────────────────────
BPM = 96
KEY_ROOT = 3   # Eb = pitch class 3
# Eb major scale degrees (semitone offsets from Eb): 0,2,4,5,7,9,11
SCALE_INTERVALS = [0, 2, 4, 5, 7, 9, 11]
BASE_OCTAVE = 60  # C4 = MIDI 60; Eb4 = 63

# Chord plan: scale degrees (1-indexed) for each of 8 bars
CHORD_DEGREES = [1, 4, 5, 6, 2, 5, 4, 1]  # I-IV-V-vi-ii-V-IV-I

# Rule 30 CA parameters
CA_WIDTH = 8   # one cell per bar
CA_SEED = 0b00010100  # arbitrary seed

# Voice ranges (MIDI)
VOICE_RANGES = {
    'Soprano': (63, 79),   # Eb4-G5
    'Alto':    (55, 69),   # G3-A4
    'Tenor':   (48, 62),   # C3-D4
    'Bass':    (39, 55),   # Gb2-G3
}

VOICE_BASE = {
    'Soprano': 63,  # Eb4
    'Alto':    55,  # G3
    'Tenor':   50,  # D3
    'Bass':    43,  # G2
}


def rule30_step(left, center, right):
    """Rule 30: new_state = left XOR (center OR right)"""
    return left ^ (center | right)


def run_ca(seed, width, steps):
    """Run Rule 30 CA. Returns (steps x width) binary grid."""
    grid = np.zeros((steps, width), dtype=int)
    # Decompose seed into individual bits (MSB first)
    for i in range(width):
        grid[0, i] = (seed >> (width - 1 - i)) & 1
    for t in range(1, steps):
        for i in range(width):
            left = grid[t-1, (i-1) % width]
            center = grid[t-1, i]
            right = grid[t-1, (i+1) % width]
            grid[t, i] = rule30_step(left, center, right)
    return grid


def ca_to_scale_degrees(ca_row, chord_degree, num_scale_degrees=7):
    """Map CA binary row to a scale degree near the chord tone.
    
    Uses 3 bits to pick an offset (-3..+3) from chord root degree.
    """
    # Interpret 3 bits as signed offset
    bits = int(''.join(str(b) for b in ca_row[:3]), 2)
    offset = bits - 3  # range -3..+3
    degree = chord_degree + offset
    # Clamp to 1..7
    degree = max(1, min(num_scale_degrees, degree))
    return degree


def degree_to_midi(degree, base_midi):
    """Convert 1-indexed scale degree to MIDI note, relative to base."""
    # degree 1 = base, degree 2 = base + scale_intervals[1], etc.
    idx = (degree - 1) % len(SCALE_INTERVALS)
    octave_shift = ((degree - 1) // len(SCALE_INTERVALS)) * 12
    return base_midi + SCALE_INTERVALS[idx] + octave_shift


# ── Phase 1: CA generates raw degrees ───────────────────────────────────────
def phase1_generate_raw():
    """Run CA and produce raw voice assignments per bar."""
    voice_names = ['Soprano', 'Alto', 'Tenor', 'Bass']
    num_bars = len(CHORD_DEGREES)
    
    # Run CA with 4 rows (one per voice), each row = num_bars wide
    ca_rows = {}
    for i, vname in enumerate(voice_names):
        seed = CA_SEED >> i  # shift seed per voice for variety
        grid = run_ca(seed & 0xFF, num_bars, 4)  # 4 timesteps, take last
        ca_rows[vname] = grid[-1]  # last row
    
    # Convert to scale degrees
    raw_degrees = {}
    for vname in voice_names:
        degrees = []
        for bar_idx in range(num_bars):
            chord_deg = CHORD_DEGREES[bar_idx]
            deg = ca_to_scale_degrees(ca_rows[vname][bar_idx:bar_idx+3], chord_deg)
            degrees.append(deg)
        raw_degrees[vname] = degrees
    
    return raw_degrees, ca_rows


# ── Phase 2: Voice leading rules ───────────────────────────────────────────
def check_parallel_fifths_octaves(midi_chord_prev, midi_chord_curr):
    """Check for parallel fifths and octaves between adjacent voices."""
    violations = []
    if len(midi_chord_prev) < 2 or len(midi_chord_curr) < 2:
        return violations
    
    # Sort both chords by pitch
    prev_sorted = sorted(enumerate(midi_chord_prev), key=lambda x: x[1])
    curr_sorted = sorted(enumerate(midi_chord_curr), key=lambda x: x[1])
    
    for i in range(len(prev_sorted)):
        for j in range(i+1, len(prev_sorted)):
            vi, p1 = prev_sorted[i]
            vj, p2 = prev_sorted[j]
            # Find same voices in current
            ci = next(x[1] for x in curr_sorted if x[0] == vi)
            cj = next(x[1] for x in curr_sorted if x[0] == vj)
            
            interval1 = abs(p2 - p1) % 12
            interval2 = abs(cj - ci) % 12
            motion_i = ci - p1
            motion_j = cj - p2
            
            # Parallel fifths
            if interval1 == 7 and interval2 == 7 and motion_i == motion_j and motion_i != 0:
                violations.append(('fifth', vi, vj))
            # Parallel octaves
            if interval1 == 0 and interval2 == 0 and motion_i == motion_j and motion_i != 0:
                violations.append(('octave', vi, vj))
    
    return violations


def fix_violations(raw_degrees, voice_names):
    """Fix voice leading violations by adjusting degrees by step."""
    fixed = {v: list(d) for v, d in raw_degrees.items()}
    num_bars = len(CHORD_DEGREES)
    total_fixes = 0
    
    for bar_idx in range(1, num_bars):
        midi_prev = [degree_to_midi(fixed[v][bar_idx-1], VOICE_BASE[v]) for v in voice_names]
        midi_curr = [degree_to_midi(fixed[v][bar_idx], VOICE_BASE[v]) for v in voice_names]
        
        violations = check_parallel_fifths_octaves(midi_prev, midi_curr)
        
        for vtype, vi, vj in violations:
            # Try moving the upper voice by one step
            vname = voice_names[vj] if vj > vi else voice_names[vi]
            old_deg = fixed[vname][bar_idx]
            # Try +1 or -1
            for delta in [+1, -1]:
                new_deg = old_deg + delta
                if 1 <= new_deg <= 7:
                    fixed[vname][bar_idx] = new_deg
                    # Re-check
                    midi_curr_new = [degree_to_midi(fixed[v][bar_idx], VOICE_BASE[v]) for v in voice_names]
                    new_violations = check_parallel_fifths_octaves(midi_prev, midi_curr_new)
                    if not new_violations:
                        total_fixes += 1
                        break
            else:
                fixed[vname][bar_idx] = old_deg  # revert if no fix found
    
    return fixed, total_fixes


# ── Build UnitMatrix ────────────────────────────────────────────────────────
def build_composition(fixed_degrees):
    """Build UnitMatrix composition from fixed degrees."""
    voice_names = ['Soprano', 'Alto', 'Tenor', 'Bass']
    num_bars = len(CHORD_DEGREES)
    
    composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=480, beats_per_bar=4)
    composer.create_matrix(num_voices=4, num_sections=num_bars)
    
    # Add voices with GM programs
    composer.add_voice('Soprano', program=MidiInstrument.FLUTE, channel=0)
    composer.add_voice('Alto', program=MidiInstrument.FLUTE, channel=1)  # oboe=68 but limited
    composer.add_voice('Tenor', program=MidiInstrument.FLUTE, channel=2)
    composer.add_voice('Bass', program=MidiInstrument.BASS, channel=3)
    
    # Add sections (1 bar each)
    for i in range(num_bars):
        composer.add_section(f"Bar{i+1}", bars=1)
    
    # Fill matrix
    bar_ticks = 480 * 4  # 1920 ticks per bar
    
    for col, bar_idx in enumerate(range(num_bars)):
        for row, vname in enumerate(voice_names):
            deg = fixed_degrees[vname][bar_idx]
            midi = degree_to_midi(deg, VOICE_BASE[vname])
            # Clamp to range
            lo, hi = VOICE_RANGES[vname]
            midi = max(lo, min(hi, midi))
            unit = create_note_unit(midi, bar_ticks)
            composer.set_unit(row, col, unit)
    
    return composer


# ── Main ────────────────────────────────────────────────────────────────────
def main():
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    midi_dir = os.path.join(project_dir, 'MIDI')
    analysis_dir = os.path.join(project_dir, 'Analysis')
    os.makedirs(midi_dir, exist_ok=True)
    os.makedirs(analysis_dir, exist_ok=True)
    
    print("=" * 60)
    print("PROJECT 057: Cellular Automaton Chorale")
    print("Method: Rule 30 Elementary CA + Voice Leading Rules")
    print("=" * 60)
    
    # Phase 1
    print("\n[Phase 1] Running Rule 30 CA...")
    raw_degrees, ca_rows = phase1_generate_raw()
    voice_names = ['Soprano', 'Alto', 'Tenor', 'Bass']
    print("Raw CA degrees:")
    for v in voice_names:
        print(f"  {v}: {raw_degrees[v]}")
    
    # Phase 2
    print("\n[Phase 2] Applying voice leading rules...")
    fixed_degrees, num_fixes = fix_violations(raw_degrees, voice_names)
    print(f"Fixed {num_fixes} voice leading violations")
    print("Final degrees:")
    for v in voice_names:
        print(f"  {v}: {fixed_degrees[v]}")
    
    # Build composition
    print("\n[Build] Creating UnitMatrix...")
    composer = build_composition(fixed_degrees)
    
    # Validate
    ok, msg = composer.validate()
    print(f"Validation: {'PASS' if ok else 'FAIL'} - {msg}")
    assert ok, f"Zero-drift validation failed: {msg}"
    
    # Export MIDI
    midi_path = os.path.join(midi_dir, '057-cellular-chorale.mid')
    composer.to_midi(midi_path)
    
    # Verify
    fsize = os.path.getsize(midi_path)
    assert fsize > 40, f"MIDI file too small: {fsize} bytes"
    print(f"\nMIDI exported: {midi_path} ({fsize} bytes)")
    
    # Grid visualization
    grid_path = os.path.join(analysis_dir, 'grid_visualization.txt')
    write_grid_visualization(
        composer.matrix, grid_path,
        ticks_per_character=120,
        voice_names=voice_names,
        bpm=BPM,
        mode="Eb Major (Rule 30 CA)"
    )
    print(f"Grid visualization: {grid_path}")
    
    # Provenance
    provenance = {
        "project": "057-cellular-chorale",
        "classification": "ai-generated",
        "generator": "Rule 30 Elementary Cellular Automaton",
        "phase1_method": "Rule 30 CA (seed=0b00010100, 4 timesteps)",
        "phase2_rules": "VoiceLeadingRules (parallel fifths/octaves check + step correction)",
        "key": "Eb Major",
        "form": "8-bar chorale (I-IV-V-vi-ii-V-IV-I)",
        "voices": ["Soprano (Flute)", "Alto (Flute)", "Tenor (Flute)", "Bass (Bass)"],
        "bpm": BPM,
        "ticks_per_beat": 480,
        "total_bars": 8,
        "voice_leading_fixes": num_fixes,
        "validation": {"zero_drift": ok, "message": msg},
        "midi_file": "057-cellular-chorale.mid",
        "midi_size_bytes": fsize,
        "ca_seed": CA_SEED,
        "ca_width": CA_WIDTH,
        "chord_plan": CHORD_DEGREES,
        "scale_intervals": SCALE_INTERVALS,
    }
    
    prov_path = os.path.join(midi_dir, '057-cellular-chorale.mid.provenance.json')
    with open(prov_path, 'w') as f:
        json.dump(provenance, f, indent=2)
    print(f"Provenance: {prov_path}")
    
    # Print CA grid for analysis
    print("\n[CA Grid] Rule 30 evolution:")
    grid = run_ca(CA_SEED, CA_WIDTH, 4)
    for t in range(4):
        row_str = ''.join(['#' if b else '.' for b in grid[t]])
        print(f"  t={t}: {row_str}")
    
    # Print MIDI pitches
    print("\n[Final MIDI pitches]")
    for v in voice_names:
        pitches = [degree_to_midi(fixed_degrees[v][i], VOICE_BASE[v]) for i in range(8)]
        lo, hi = VOICE_RANGES[v]
        pitches = [max(lo, min(hi, p)) for p in pitches]
        print(f"  {v}: {pitches}")
    
    print("\n[DONE] Project 057 complete.")
    return midi_path


if __name__ == '__main__':
    main()
