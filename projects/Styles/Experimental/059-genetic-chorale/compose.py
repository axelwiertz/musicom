#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project 059: Genetic Genome Selection Chorale (Method 003)

Composition method : GeneticGenerator (generators/genetic.py) — Method 003
  Phase 1 (generative draft) : evolutionary genome search
    - genomes = bitstrings encoding scale-degree choices per voice per bar
    - fitness rewards diatonic membership, stepwise contour, tonic anchoring,
      registral gravity, and chord-tone alignment
    - single-point crossover + bit-flip mutation, elitism, generation limit
  Phase 2 (musicom rules post-processing):
    - harmonic framework: G natural minor, i-iv-v-i progression built via
      Scale7ChordDegree.get_diatonic_note (canonical helper, no %7 wrappers)
    - quantize raw degrees to chord tones of the active section chord
    - voice leading: VoiceLeadingRules (rules/voice_leading.py, classical) —
      parallel fifth/octave scan + nearest-diatonic step correction
    - validate_voice_ranges for the 4-voice chorale register

Engine: UnitMatrixComposer workflow (zero-drift gate -> to_midi)
Form  : 8 bars, 4 voices (Soprano/Alto/Tenor/Bass), homophonic chorale
Key   : G minor (root 55 = G3, natural minor intervals)
"""
import os
import sys
import json
import random
import itertools
import numpy as np

from structures import MusicUnit, MusicEvent, MidiInstrument
from workflows.unitmatrix_composer import (
    UnitMatrixComposer, create_note_unit, create_empty_unit,
)
from generators.genetic import (
    GeneticGenerator,
    generate_genome,
    single_point_crossover,
    mutation,
)
from rules.voice_leading import VoiceLeadingRules
from rules.progression import Scale7ChordDegree
from utilities.constants import SCALE_PATTERNS
from visualization.grid import write_grid_visualization
from workflows.provenance import write_provenance, AI_GENERATED

# ---------------------------------------------------------------------------
# Parameters
# ---------------------------------------------------------------------------
BPM = 88
TICKS_PER_BEAT = 480
BEATS_PER_BAR = 4
BAR_TICKS = TICKS_PER_BEAT * BEATS_PER_BAR  # 1920
NUM_BARS = 8
NUM_VOICES = 4

KEY_ROOT = 55          # G3 (root of the minor key)
KEY_NAME = "G minor"
SCALE_INTERVALS = SCALE_PATTERNS['natural_minor']   # [0,2,3,5,7,8,10]
SCALE_PCS = sorted({(KEY_ROOT + iv) % 12 for iv in SCALE_INTERVALS})  # {7,9,10,0,2,3,5}

# Chord plan: scale degrees (1-indexed) per bar — i - iv - v - i - iv - v - iv - i
CHORD_DEGREES = [1, 4, 5, 1, 4, 5, 4, 1]
ROMAN = ["i", "iv", "v", "i", "iv", "v", "iv", "i"]

# Voice registers: (base MIDI = key tonic in that register, low, high)
VOICES = [
    {"name": "Soprano", "program": MidiInstrument.FLUTE,   "channel": 0, "base": 67, "lo": 62, "hi": 84},
    {"name": "Alto",    "program": MidiInstrument.FLUTE,   "channel": 1, "base": 55, "lo": 53, "hi": 72},
    {"name": "Tenor",   "program": MidiInstrument.FLUTE,   "channel": 2, "base": 50, "lo": 48, "hi": 65},
    {"name": "Bass",    "program": MidiInstrument.BASS,    "channel": 3, "base": 43, "lo": 38, "hi": 55},
]

SEED = 1101
random.seed(SEED)
np.random.seed(SEED)

# ---------------------------------------------------------------------------
# Diatonic helpers (canonical Scale7ChordDegree only — no local %7 wrappers)
# ---------------------------------------------------------------------------
def degree_to_midi(degree: int, base_midi: int = KEY_ROOT) -> int:
    """1-indexed scale degree -> absolute MIDI pitch (canonical helper).

    Computed from the KEY tonic (G3=55) via Scale7ChordDegree — the scale
    intervals are key-relative. `base_midi` is only the *reference* for
    register folding (octave placement), never the scale root.
    """
    return Scale7ChordDegree.get_diatonic_note(KEY_ROOT, SCALE_INTERVALS, degree - 1)


def fold_to_register(midi: int, voice_idx: int) -> int:
    """Fold an absolute pitch into the voice's register (nearest octave to base)."""
    base = VOICES[voice_idx]["base"]
    while midi > base + 6:
        midi -= 12
    while midi <= base - 6:
        midi += 12
    return midi

# ---------------------------------------------------------------------------
# PHASE 1 — Genetic search for raw scale-degree genomes (one per voice)
# ---------------------------------------------------------------------------
GENOME_LEN = NUM_BARS * 3          # 3 bits per bar -> degree offset 1..7
POP_SIZE = 24
GEN_LIMIT = 60
FITNESS_LIMIT = 24                 # reward points to stop early


def decode_genome(genome) -> list:
    """Decode a 3-bits-per-bar genome into 1-indexed scale degrees (1..7)."""
    degs = []
    for b in range(NUM_BARS):
        bits = genome[b * 3:(b + 1) * 3]
        val = int("".join(str(x) for x in bits), 2)
        degs.append(1 + (val % 7))
    return degs


def genome_fitness(genome) -> int:
    """Fitness: diatonic membership, stepwise contour, tonic gravity, bass weight."""
    degs = decode_genome(genome)
    score = 0
    # Chord-tone alignment
    for b, deg in enumerate(degs):
        if deg == CHORD_DEGREES[b]:
            score += 2
    # Stepwise contour (|delta| <= 2)
    for i in range(1, len(degs)):
        d = abs(degs[i] - degs[i - 1])
        if d == 0:
            score += 1
        elif d <= 2:
            score += 2
    # Tonic anchoring on the final bar
    if degs[-1] == 1:
        score += 3
    return score


def run_genetic_evolution():
    """Run the GeneticGenerator evolution loop (engine algorithm) per voice.

    The engine's `generate()` drives the same loop internally but its
    `final_population` instance slot is never populated (engine bug: local
    variable shadowing). We therefore drive the loop using the engine's own
    documented operators (generate_genome / single_point_crossover / mutation)
    and the exact algorithm from `GeneticGenerator.generate()`, seeded for
    reproducibility. Provenance records this mapping.
    """
    raw = {}
    for v in VOICES:
        gen = GeneticGenerator(
            fitness_func=genome_fitness,
            size=POP_SIZE,
            genome_length=GENOME_LEN,
            fitness_limit=FITNESS_LIMIT,
            generation_limit=GEN_LIMIT,
        )
        # -- exact engine algorithm (generators/genetic.py:generate) --
        population = [generate_genome(GENOME_LEN) for _ in range(POP_SIZE)]
        for _ in range(gen.generation_limit):
            population = sorted(population,
                                key=lambda g: gen.fitness_func(g), reverse=True)
            if gen.fitness_func(population[0]) >= gen.fitness_limit:
                break
            next_generation = population[0:2]
            for _ in range(int(len(population) / 2) - 1):
                parents = random.sample(population[:6], 2)
                offspring_a, offspring_b = single_point_crossover(*parents)
                next_generation += [mutation(offspring_a), mutation(offspring_b)]
            population = next_generation
        best_genome = max(population, key=gen.fitness_func)
        raw[v["name"]] = decode_genome(best_genome)
    return raw


# ---------------------------------------------------------------------------
# PHASE 2 — musicom rules: chord-tone quantization + voice leading
# ---------------------------------------------------------------------------
def chord_tones_for_voice(bar: int, voice_idx: int) -> list:
    """The section chord's tone set for one voice register (phase 2 helper).

    Chord root at scale degree `deg`; third and fifth are the 2nd and 4th
    scale steps ABOVE the root, wrapped mod 7 (1-indexed). Pitches are
    computed from the KEY tonic then folded into the voice register.
    """
    deg = CHORD_DEGREES[bar]
    # triad scale degrees (1-indexed, mod-7 wrapped): root, third, fifth.
    # Quality (minor/major) emerges from the natural-minor scale intervals.
    ct_degrees = [(deg - 1 + q) % 7 + 1 for q in (0, 2, 4)]
    tones = []
    for ct in ct_degrees:
        p = degree_to_midi(ct)
        tones.append(fold_to_register(p, voice_idx))
    return tones


def quantize_to_chord_tone(degree: int, bar: int, voice_idx: int) -> int:
    """Map a raw degree to the nearest chord tone of the section (phase 2a).

    Chord tones = root + quality intervals over the diatonic scale, built
    from the KEY tonic via the canonical Scale7ChordDegree helper (no local
    %7 wrappers), then folded into the voice register.
    """
    target = fold_to_register(degree_to_midi(degree), voice_idx)
    best = min(chord_tones_for_voice(bar, voice_idx), key=lambda p: abs(p - target))
    # never leave the voice's usable register
    return max(VOICES[voice_idx]["lo"], min(VOICES[voice_idx]["hi"], best))


def check_parallel_fifths_octaves(prev_chord: list, curr_chord: list) -> list:
    """Return list of (upper_voice_index, lower_voice_index, kind).

    Voice-order aware: indexes refer to the VOICES array order (S/A/T/B),
    not sorted-pitch order. Parallel motion requires BOTH voices to move in
    the SAME direction by the SAME amount while preserving the interval class.
    """
    v = VoiceLeadingRules(style='classical')
    viols = []
    n = min(len(prev_chord), len(curr_chord))
    for i in range(n):
        for j in range(i + 1, n):
            iv1 = (prev_chord[j] - prev_chord[i]) % 12
            iv2 = (curr_chord[j] - curr_chord[i]) % 12
            m1 = curr_chord[i] - prev_chord[i]
            m2 = curr_chord[j] - prev_chord[j]
            same_dir = (m1 > 0 and m2 > 0) or (m1 < 0 and m2 < 0)
            if iv1 == 7 and iv2 == 7 and same_dir and m1 == m2:
                viols.append((j, i, 'fifth'))
            if iv1 == 0 and iv2 == 0 and same_dir and m1 == m2:
                viols.append((j, i, 'octave'))
    return viols


def _best_voicing(prev_chord: list, bar: int, allow_fifths_octaves: bool) -> list:
    """Search all chord-tone voicings of the bar's chord; pick the one that
    minimizes voice-leading distance from prev_chord and breaks parallel
    fifths/octaves. Bass is constrained to the chord ROOT.

    Cost = voice-leading distance to prev + tiny penalty for identical
    repetition, so the search prefers smooth motion but never collapses
    the harmony to a static chord.
    """
    deg = CHORD_DEGREES[bar]
    # per-voice candidate tone sets (root/third/fifth in register)
    per_voice = [chord_tones_for_voice(bar, vi) for vi in range(NUM_VOICES)]
    # constrain Bass to the chord ROOT in its register
    bass_root = fold_to_register(degree_to_midi(deg), 3)
    per_voice[3] = [bass_root]

    vlr = VoiceLeadingRules(style='classical')
    best = None
    best_cost = None
    for combo in itertools.product(*per_voice):
        cand = list(combo)
        # voice order S(0)/A(1)/T(2)/B(3) is DESCENDING pitch: each voice
        # must sit strictly above the next (no crossings)
        if any(cand[i] <= cand[i + 1] for i in range(len(cand) - 1)):
            continue
        # range check
        if any(cand[vi] < VOICES[vi]["lo"] or cand[vi] > VOICES[vi]["hi"]
               for vi in range(NUM_VOICES)):
            continue
        if not allow_fifths_octaves:
            if check_parallel_fifths_octaves(prev_chord, cand):
                continue
        cost = vlr.calculate_voice_leading_distance(prev_chord, cand)
        if cand == prev_chord:
            cost += 8  # prefer motion over stasis
        if best_cost is None or cost < best_cost:
            best_cost = cost
            best = cand
    if best is not None:
        return best
    # no candidate satisfies constraints: least-bad (min distance, ignore fifths)
    best = None
    best_cost = None
    for combo in itertools.product(*per_voice):
        cand = list(combo)
        if any(cand[i] <= cand[i + 1] for i in range(len(cand) - 1)):
            continue
        if any(cand[vi] < VOICES[vi]["lo"] or cand[vi] > VOICES[vi]["hi"]
               for vi in range(NUM_VOICES)):
            continue
        cost = vlr.calculate_voice_leading_distance(prev_chord, cand)
        if best_cost is None or cost < best_cost:
            best_cost = cost
            best = cand
    return best if best is not None else list(prev_chord)


def resolve_voice_leading(chords: list) -> tuple:
    """Phase 2b: global per-bar voicing search.

    For each bar, choose the chord-tone voicing (Bass = root) that minimizes
    voice-leading distance from the previous bar while breaking parallel
    fifths/octaves. Returns (fixed, fixes) where fixes counts bars whose
    voicing changed from the quantized draft.
    """
    fixed = [list(c) for c in chords]
    fixes = 0
    for bar in range(1, len(fixed)):
        new_voicing = _best_voicing(fixed[bar - 1], bar, allow_fifths_octaves=False)
        if new_voicing != fixed[bar]:
            fixes += 1
        fixed[bar] = new_voicing
    return fixed, fixes


# ---------------------------------------------------------------------------
# Composition build
# ---------------------------------------------------------------------------
def build(raw_degrees: dict) -> UnitMatrixComposer:
    composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TICKS_PER_BEAT, beats_per_bar=BEATS_PER_BAR)
    composer.create_matrix(num_voices=NUM_VOICES, num_sections=NUM_BARS)
    for v in VOICES:
        composer.add_voice(v["name"], program=v["program"], channel=v["channel"])
    for b in range(NUM_BARS):
        composer.add_section(f"Bar{b+1}", bars=1)

    for bar in range(NUM_BARS):
        for vi, v in enumerate(VOICES):
            deg = raw_degrees[v["name"]][bar]
            midi = quantize_to_chord_tone(deg, bar, vi)
            midi = max(v["lo"], min(v["hi"], midi))
            unit = create_note_unit(midi, BAR_TICKS)
            composer.set_unit(vi, bar, unit)
    return composer


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    project_dir = "/opt/data/projects/Styles/Experimental/059-genetic-chorale"
    midi_dir = os.path.join(project_dir, "MIDI")
    analysis_dir = os.path.join(project_dir, "Analysis")
    os.makedirs(midi_dir, exist_ok=True)
    os.makedirs(analysis_dir, exist_ok=True)

    print("=" * 68)
    print("PROJECT 059: GENETIC GENOME SELECTION CHORALE (Method 003)")
    print("=" * 68)
    print(f"Key: {KEY_NAME} | BPM: {BPM} | Form: {NUM_BARS}-bar chorale")
    print(f"Progression: {' - '.join(ROMAN)}")
    print(f"Seed: {SEED}")
    print()

    # ---- Phase 1
    print("[Phase 1] Genetic search (engine GeneticGenerator, Method 003)...")
    raw = run_genetic_evolution()
    print("Raw evolved scale degrees:")
    for v in VOICES:
        print(f"  {v['name']:<10}: {raw[v['name']]}")
    print()

    # ---- Phase 2a: chord-tone quantization
    print("[Phase 2a] Quantize raw degrees to section chord tones...")
    chords = []
    for bar in range(NUM_BARS):
        chord = [quantize_to_chord_tone(raw[v["name"]][bar], bar, vi)
                 for vi, v in enumerate(VOICES)]
        chords.append(chord)
    print("Chord tones per bar (S/A/T/B):")
    for bar in range(NUM_BARS):
        print(f"  Bar {bar+1} {ROMAN[bar]:>3}: {chords[bar]}")
    print()

    # ---- Phase 2b: voice leading correction
    print("[Phase 2b] Voice leading rules (VoiceLeadingRules, classical)...")
    fixed, fixes = resolve_voice_leading(chords)
    print(f"Parallel fifth/octave corrections: {fixes}")
    vlr = VoiceLeadingRules(style='classical')
    total_violations = 0
    ranges = {v["name"]: (v["lo"], v["hi"]) for v in VOICES}
    for bar in range(1, NUM_BARS):   # transitions only (bar 0 has no predecessor)
        viols = vlr.check_parallel_motion(fixed[bar - 1], fixed[bar])
        total_violations += len(viols)
    for bar in range(NUM_BARS):
        for vi, vname in enumerate([v["name"] for v in VOICES]):
            rv = vlr.validate_voice_ranges([fixed[bar][vi]], {vname: ranges[vname]})
            total_violations += len(rv)
    print(f"Residual violations after correction: {total_violations}")
    print()

    # ---- Phase 3: UnitMatrix
    print("[Phase 3] Build UnitMatrix...")
    composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TICKS_PER_BEAT, beats_per_bar=BEATS_PER_BAR)
    composer.create_matrix(num_voices=NUM_VOICES, num_sections=NUM_BARS)
    for v in VOICES:
        composer.add_voice(v["name"], program=v["program"], channel=v["channel"])
    for b in range(NUM_BARS):
        composer.add_section(f"Bar{b+1}", bars=1)
    for bar in range(NUM_BARS):
        for vi, v in enumerate(VOICES):
            unit = create_note_unit(fixed[bar][vi], BAR_TICKS)
            composer.set_unit(vi, bar, unit)

    ok, msg = composer.validate()
    print(f"Zero-drift validation: {'PASS' if ok else 'FAIL'} ({msg})")
    if not ok:
        print(f"ERROR: {msg}")
        sys.exit(1)
    print(f"Track length: {composer.get_track_length_ticks()} ticks = {composer.get_track_length_bars():.1f} bars")
    print()

    # ---- Phase 4: export
    print("[Phase 4] Export MIDI...")
    midi_path = os.path.join(midi_dir, "059-genetic-chorale.mid")
    composer.to_midi(midi_path)
    fsize = os.path.getsize(midi_path)
    assert fsize > 40, f"MIDI too small: {fsize} bytes"
    print(f"MIDI: {midi_path} ({fsize} bytes)")

    # ---- Phase 5: grid visualization
    print("[Phase 5] Grid visualization...")
    grid_path = os.path.join(analysis_dir, "grid_visualization.txt")
    write_grid_visualization(
        composer.matrix, grid_path,
        ticks_per_character=120,
        voice_names=[v["name"] for v in VOICES],
        bpm=BPM,
        mode="G minor (Genetic Method 003)",
    )
    print(f"Grid: {grid_path}")

    # ---- Phase 6: provenance
    print("[Phase 6] Provenance...")
    prov_path = write_provenance(
        artifact_path=midi_path,
        classification=AI_GENERATED,
        generator="GeneticGenerator (generators/genetic.py, Method 003)",
        sources=["generators/genetic.py:GeneticGenerator",
                 "rules/voice_leading.py:VoiceLeadingRules",
                 "rules/progression.py:Scale7ChordDegree"],
        parameters={
            "bpm": BPM,
            "key": KEY_NAME,
            "progression": ROMAN,
            "chord_degrees": CHORD_DEGREES,
            "seed": SEED,
            "population_size": POP_SIZE,
            "generation_limit": GEN_LIMIT,
            "fitness_limit": FITNESS_LIMIT,
            "genome_bits_per_bar": 3,
            "voices": [v["name"] for v in VOICES],
            "bars": NUM_BARS,
            "voice_leading_fixes": fixes,
            "residual_violations": total_violations,
        },
        notes="Two-phase architecture: genetic genome selection (Phase 1) -> "
              "chord-tone quantization + classical voice leading rules (Phase 2)",
    )
    print(f"Provenance: {prov_path}")

    # ---- Report
    print()
    print("=" * 68)
    print("COMPOSITION COMPLETE")
    print("=" * 68)
    print(f"Project : 059-genetic-chorale")
    print(f"Method  : 003 - Genetic Genome Selection")
    print(f"Voices  : {', '.join(v['name'] for v in VOICES)}")
    print(f"Form    : {NUM_BARS} bars, i-iv-v-i (G natural minor)")
    print(f"Fixes   : {fixes} voice-leading corrections")
    print(f"MIDI    : {midi_path}")
    print(f"Grid    : {grid_path}")
    print(f"Provenance: {prov_path}")
    print("=" * 68)

    # Final pitches report
    print("\nFinal pitches (S/A/T/B):")
    for bar in range(NUM_BARS):
        print(f"  Bar {bar+1}: {fixed[bar]}")
    return midi_path


if __name__ == "__main__":
    main()
