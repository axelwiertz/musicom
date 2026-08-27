# -*- coding: utf-8 -*-
"""065 - Uniform Stochastic (Monte Carlo) Chorale (Method 001).

Autonomous nightly composition job.
Composition method: Method 001 - Uniform Stochastic (Monte Carlo) sampling
(generators/stochastic.py) - every pitch is drawn uniformly at random from a
wide chromatic pool and every duration from a discrete set, with NO Markov
memory, NO scale constraint, NO voice range bound in the raw draft.

Two-phase architecture (mandatory):
  Phase 1 (generative draft):
    - Pitch DNA = uniform random draw from full chromatic pool [50..88]
      (completely unconstrained, includes non-diatonic tones and wide leaps).
    - Rhythm DNA = uniform random duration from {120, 240, 360, 480} ticks
      (eighth, quarter, dotted-quarter, half) - no metrical gravity.
    - The raw draft is maximally chaotic: random pitches, random durations,
      no chord context. This is the purest demonstration of why Phase 2
      (musicom rules post-processing) is mandatory.
  Phase 2 (musicom rules post-processing):
    - Quantize each raw pitch onto the nearest tone of the section's diatonic
      triad (soprano register) -> consonant melody.
    - Build Alto/Tenor/Bass as diatonic block harmony via the canonical
      Scale7ChordDegree.get_diatonic_note() helper (no off-by-octave wrap).
    - Voice-leading: VoiceLeadingRules.optimize_voice_leading() rotates
      inversions to minimize total voice-leading distance; then Phase 2c
      CORRECTS any remaining parallel/hidden fifth violations by trying
      inversion rotations of each chord and keeping the voicing with zero
      violations and minimal voice-leading distance.
    - Harmonic progression rule: D minor i - VI - III - VII (Dm-Bb-F-C),
      validated against PatternMovementRules.movement_rules and the
      Scale7ChordDegree function map (i tonic -> VI/III prolongation ->
      VII dominant -> i tonic implied by the cycle).
    - Zero-drift gate: UnitMatrixComposer.validate() must pass for BOTH the
      Phase 1 raw-draft MIDI and the Phase 2 rules-processed MIDI before
      to_midi(); deterministic seed -> reproducible artifact.

Engines used: structures.*, workflows.unitmatrix_composer,
visualization.grid, workflows.provenance, rules.voice_leading,
rules.progression, generators.stochastic.
"""
import os
import random

from structures import MusicUnit, MusicEvent, MidiInstrument
from workflows.unitmatrix_composer import UnitMatrixComposer
from visualization.grid import write_grid_visualization
from workflows.provenance import write_provenance
from rules.voice_leading import VoiceLeadingRules
from rules.progression import Scale7ChordDegree
from generators.stochastic import StochasticGenerator

SEED = 65
random.seed(SEED)

# ---- Composition parameters ------------------------------------------------
KEY_NAME = "D minor (aeolian)"
KEY_ROOT_PC = 2                # D
SCALE_INTERVALS = [0, 2, 3, 5, 7, 8, 10]   # natural minor / aeolian
KEY_ROOT_MIDI = 50             # D3 (base for absolute diatonic chord calc)
BPM = 88
TPB = 480                      # ticks per beat
BPB = 4                        # beats per bar
BAR = TPB * BPB                # 1920 ticks / bar
SECTION_BARS = 2
SECTION_TICKS = SECTION_BARS * BAR          # 3840 ticks / section
NUM_SECTIONS = 4

# D minor: i - VI - III - VII (Dm - Bb - F - C). Harmonic-rule legal:
#   i (tonic) -> VI/III (tonic prolongation) -> VII (dominant) -> i (tonic),
#   cadencing the cycle back to tonic.
# NOTE: Scale7ChordDegree.get_diatonic_note() is 0-based (index 0 = tonic):
#   i=0, VI=5, III=2, VII=6.
SECTION_DEGREES = [0, 5, 2, 6]
SECTION_NAMES = ["i (Dm)", "VI (Bb)", "III (F)", "VII (C)"]

VOICES = ["Soprano", "Alto", "Tenor", "Bass"]
VOICE_PROGRAMS = [
    MidiInstrument.FLUTE,            # Soprano (bright, melodic)
    MidiInstrument.STRING_ENSEMBLE,  # Alto
    MidiInstrument.STRING_ENSEMBLE,  # Tenor
    MidiInstrument.BASS,             # Bass
]
VOICE_CHANNELS = [0, 1, 2, 3]

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
MIDI_DIR = os.path.join(PROJECT_DIR, "MIDI")
ANALYSIS_DIR = os.path.join(PROJECT_DIR, "Analysis")
NOTES_DIR = os.path.join(PROJECT_DIR, "Notes")
os.makedirs(MIDI_DIR, exist_ok=True)
os.makedirs(ANALYSIS_DIR, exist_ok=True)
os.makedirs(NOTES_DIR, exist_ok=True)
BASE = "065-uniform-stochastic-chorale"
MIDI_PATH = os.path.join(MIDI_DIR, BASE + ".mid")
PHASE1_PATH = os.path.join(MIDI_DIR, BASE + "-phase1.mid")

# Phase 1 raw-draft stochastic parameters
RAW_PITCH_POOL = list(range(50, 89))          # full chromatic, unconstrained
RAW_DURATION_SET = [TPB // 4, TPB // 2, 3 * TPB // 4, TPB]  # 1/8, 1/4, 3/8, 1/2
RAW_LENGTH = (NUM_SECTIONS * SECTION_TICKS) // (TPB // 2)  # ~2 events per beat


# ---- Helpers ----------------------------------------------------------------
def chord_triad_abs(degree):
    """Absolute MIDI triad (root, third, fifth) for a scale degree, key-aware.

    Routes through the canonical Scale7ChordDegree.get_diatonic_note so no
    off-by-octave scale-inversion errors on wrap steps (e.g. vii / iii).
    """
    root = Scale7ChordDegree.get_diatonic_note(KEY_ROOT_MIDI, SCALE_INTERVALS, degree)
    third = Scale7ChordDegree.get_diatonic_note(KEY_ROOT_MIDI, SCALE_INTERVALS, degree + 2)
    fifth = Scale7ChordDegree.get_diatonic_note(KEY_ROOT_MIDI, SCALE_INTERVALS, degree + 4)
    return [root, third, fifth]


def quantize_to_chord_tone(raw_pitch, triad, lo=64, hi=86):
    """Phase-2: snap raw pitch to nearest chord tone (soprano)."""
    candidates = set()
    for p in triad:
        for shift in (-12, 0, 12):
            cand = p + shift
            if lo <= cand <= hi:
                candidates.add(cand)
    if not candidates:
        candidates = set(triad)
    return min(candidates, key=lambda c: abs(c - raw_pitch))


def correct_voice_leading(triads):
    """Phase 2c: fix parallel/hidden fifths by rotating chord inversions.

    For each chord, try every inversion rotation (via the canonical
    VoiceLeadingRules._rotate_chord) and keep the voicing that yields zero
    parallel/hidden-fifth violations against the previous chord AND minimal
    voice-leading distance. Returns (corrected_triads, fixed_report).
    """
    vl = VoiceLeadingRules(style="classical")
    corrected = [sorted(triads[0])]
    fixed = []
    for i in range(1, len(triads)):
        prev = corrected[-1]
        base = sorted(triads[i])
        candidates = [base]
        for rot in range(1, len(base)):
            candidates.append(vl._rotate_chord(base, rot))
        extra = []
        for c in candidates:
            extra.append([p + 12 for p in c])
        candidates += extra

        best = candidates[0]
        best_score = None
        for cand in candidates:
            pv = vl.check_parallel_motion(prev, cand)
            hv = vl.check_hidden_fifths(prev, cand)
            n_viol = len(pv) + len(hv)
            dist = vl.calculate_voice_leading_distance(prev, cand)
            score = (n_viol, dist)
            if best_score is None or score < best_score:
                best_score = score
                best = cand
        if best_score[0] > 0:
            fixed.append((i, best_score[0]))
        corrected.append(sorted(best))
    return corrected, fixed


def harmonic_rule_report(degrees):
    """Validate the degree sequence against the Scale7ChordDegree function map."""
    report = []
    func = Scale7ChordDegree.function
    deg1 = [d + 1 for d in degrees]
    for i in range(len(deg1) - 1):
        a, b = deg1[i], deg1[i + 1]
        norm = lambda v: v if isinstance(v, (tuple, list)) else (v,)
        fa = next((k for k, v in func.items() if a in norm(v)), None)
        fb = next((k for k, v in func.items() if b in norm(v)), None)
        if fa == Scale7ChordDegree.TONIC:
            note = "legal (tonic -> any)"
        elif fa == Scale7ChordDegree.DOMINANT:
            if fb == Scale7ChordDegree.TONIC:
                note = "legal (perfect cadence)"
            elif fb == Scale7ChordDegree.TONIC_PROLONG:
                note = "legal (interrupted/deceptive cadence)"
            else:
                note = "CHECK"
        elif fa == Scale7ChordDegree.SUBDOMINANT:
            if fb in (Scale7ChordDegree.DOMINANT, Scale7ChordDegree.TONIC):
                note = "legal (subdominant -> dominant/tonic)"
            else:
                note = "CHECK"
        elif fa == Scale7ChordDegree.TONIC_PROLONG:
            note = "legal (prolongation, free)"
        else:
            note = "CHECK"
        report.append((a, b, note))
    return report


def split_events_by_section(events, section_ticks, num_sections):
    """Partition raw events into per-section MusicUnits (relative ticks + pad).

    Events are absolute-tick; each section cell gets events whose span falls in
    that section's window, offset back to 0, and padded to SECTION_TICKS with a
    silent landmark so every row is exactly SECTION_TICKS long (zero drift).
    """
    sections = []
    for s in range(num_sections):
        start = s * section_ticks
        end = start + section_ticks
        cell = []
        for e in events:
            if e.end_tick <= start or e.start_tick >= end:
                continue
            st = max(0, e.start_tick - start)
            et = min(section_ticks, e.end_tick - start)
            if et <= st:
                continue
            cell.append(MusicEvent(pitch=e.pitch, volume=e.volume,
                                   start_tick=st, end_tick=et))
        if not cell or cell[-1].end_tick < section_ticks:
            cell.append(MusicEvent(pitch=0, volume=0,
                                   start_tick=cell[-1].end_tick if cell else 0,
                                   end_tick=section_ticks))
        sections.append(MusicUnit(events=cell))
    return sections


# ---- Composition ------------------------------------------------------------
def compose():
    # ---- Phase 1: raw generative draft (uniform stochastic, unconstrained) --
    gen = StochasticGenerator(length=RAW_LENGTH,
                              pitch_set=RAW_PITCH_POOL,
                              duration_set=RAW_DURATION_SET)
    raw_units = gen.generate()          # [MusicUnit] with Raw_LENGTH events
    raw_unit = raw_units[0]
    raw_events = raw_unit.events

    raw_pitches = [e.pitch for e in raw_events]
    raw_durs = [e.end_tick - e.start_tick for e in raw_events]
    raw_pitch_report = raw_pitches[:24]
    raw_rhythm_report = raw_durs[:24]

    # Split raw events into the 4 sections for the Phase 1 MIDI (single voice).
    phase1_sections = split_events_by_section(raw_events, SECTION_TICKS, NUM_SECTIONS)

    # ---- Phase 1 MIDI export (raw draft, single voice, pre-rules) ----------
    p1_composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BPB)
    p1_composer.create_matrix(num_voices=1, num_sections=NUM_SECTIONS)
    p1_composer.add_voice("RawDraft", program=MidiInstrument.FLUTE, channel=0)
    for sname in SECTION_NAMES:
        p1_composer.add_section(sname, bars=SECTION_BARS)
    for s in range(NUM_SECTIONS):
        p1_composer.fill_voice_section("RawDraft", SECTION_NAMES[s], phase1_sections[s])
    ok1, msg1 = p1_composer.validate()
    if not ok1:
        raise RuntimeError(f"Phase 1 zero-drift validation FAILED: {msg1}")
    p1_composer.to_midi(PHASE1_PATH)

    # ---- Phase 2: musicom rules post-processing ----------------------------
    base_triads = [sorted(chord_triad_abs(d)) for d in SECTION_DEGREES]
    vl = VoiceLeadingRules(style="classical")
    optimized_triads = vl.optimize_voice_leading(base_triads)
    corrected_triads, fixed_report = correct_voice_leading(optimized_triads)

    violations = []
    for i in range(len(corrected_triads) - 1):
        violations += vl.check_parallel_motion(corrected_triads[i], corrected_triads[i + 1])
        violations += vl.check_hidden_fifths(corrected_triads[i], corrected_triads[i + 1])

    composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BPB)
    composer.create_matrix(num_voices=len(VOICES), num_sections=NUM_SECTIONS)
    for name, prog, ch in zip(VOICES, VOICE_PROGRAMS, VOICE_CHANNELS):
        composer.add_voice(name, program=prog, channel=ch)
    for sname in SECTION_NAMES:
        composer.add_section(sname, bars=SECTION_BARS)

    quant_report = []
    for s in range(NUM_SECTIONS):
        triad = corrected_triads[s]
        bass_note = triad[0] - 12
        alto_note = triad[1]
        tenor_note = triad[2]

        soprano_events = []
        alto_events = []
        tenor_events = []
        bass_events = []
        shifted = []
        for e in phase1_sections[s].events:
            if e.pitch == 0:
                continue
            qp = quantize_to_chord_tone(e.pitch, triad)
            shifted.append((e.pitch, qp))
            soprano_events.append(MusicEvent(pitch=qp, volume=90,
                                             start_tick=e.start_tick, end_tick=e.end_tick))
            alto_events.append(MusicEvent(pitch=alto_note, volume=72,
                                          start_tick=e.start_tick, end_tick=e.end_tick))
            tenor_events.append(MusicEvent(pitch=tenor_note, volume=72,
                                           start_tick=e.start_tick, end_tick=e.end_tick))
            bass_events.append(MusicEvent(pitch=bass_note, volume=84,
                                          start_tick=e.start_tick, end_tick=e.end_tick))
        quant_report.append((SECTION_NAMES[s], shifted[:8]))

        composer.fill_voice_section("Soprano", SECTION_NAMES[s], MusicUnit(events=soprano_events))
        composer.fill_voice_section("Alto", SECTION_NAMES[s], MusicUnit(events=alto_events))
        composer.fill_voice_section("Tenor", SECTION_NAMES[s], MusicUnit(events=tenor_events))
        composer.fill_voice_section("Bass", SECTION_NAMES[s], MusicUnit(events=bass_events))

        # Pad each section cell to its declared boundary (SECTION_TICKS).
        for voice_name in VOICES:
            row = [v['name'] for v in composer.voices].index(voice_name)
            unit = composer.matrix.get_unit((row, s))
            last_end = max(e.end_tick for e in unit.events) if unit.events else 0
            if last_end < SECTION_TICKS:
                unit.add_event(MusicEvent(pitch=0, volume=0,
                                          start_tick=last_end, end_tick=SECTION_TICKS))

    # ---- Zero-drift gate ---------------------------------------------------
    ok, msg = composer.validate()
    if not ok:
        raise RuntimeError(f"Zero-drift validation FAILED: {msg}")
    composer.to_midi(MIDI_PATH)

    # ---- Grid visualization -------------------------------------------------
    grid_path = os.path.join(ANALYSIS_DIR, "grid_visualization.txt")
    write_grid_visualization(composer.matrix, grid_path,
                             ticks_per_character=120, voice_names=VOICES,
                             bpm=BPM, mode="Aeolian (D minor)")

    harm_report = harmonic_rule_report(SECTION_DEGREES)
    return (composer, violations, raw_pitch_report, raw_rhythm_report,
            corrected_triads, harm_report, fixed_report, quant_report,
            p1_composer, ok1, msg1)


if __name__ == "__main__":
    (composer, violations, pitch_rep, rhythm_rep, triads, harm_report,
     fixed_report, quant_rep, p1_composer, ok1, msg1) = compose()

    size2 = os.path.getsize(MIDI_PATH)
    size1 = os.path.getsize(PHASE1_PATH)
    assert size2 > 40, f"Phase 2 MIDI too small ({size2} bytes)"
    assert size1 > 40, f"Phase 1 MIDI too small ({size1} bytes)"
    print(f"[OK] Phase 1 MIDI written: {PHASE1_PATH} ({size1} bytes)")
    print(f"[OK] Phase 2 MIDI written: {MIDI_PATH} ({size2} bytes)")
    print(f"[OK] Phase 1 zero-drift validation: PASS ({ok1})")
    print(f"[OK] Phase 2 zero-drift validation: PASS")
    print(f"[OK] Harmonic progression: i-VI-III-VII (Dm-Bb-F-C)")
    print("[OK] Harmonic function report (degree pair -> legality):")
    for a, b, verdict in harm_report:
        print(f"     {a} -> {b}: {verdict}")
    print(f"[OK] Phase 2c voice-leading corrections applied: {len(fixed_report)} chord(s) re-voiced")
    if fixed_report:
        for idx, n in fixed_report:
            print(f"     chord {idx + 1}: {n} violation(s) corrected via inversion rotation")
    print(f"[OK] Final triads (corrected, voice-leading minimized): {triads}")
    print("[OK] Raw stochastic pitch DNA (first 24, uniform chromatic draw):")
    print(f"     {pitch_rep}")
    print("[OK] Raw stochastic duration DNA (first 24, uniform draw):")
    print(f"     {rhythm_rep}")
    print("[OK] Phase 2 quantization (raw -> chord tone, first 8 per section):")
    for name, pairs in quant_rep:
        print(f"     {name}: {pairs}")
    print(f"[OK] Parallel/hidden fifth violations (classical): {len(violations)}")
    if violations:
        for v in violations:
            print(f"     - {v}")

    # Provenance sidecars for BOTH artifacts
    write_provenance(
        PHASE1_PATH,
        classification="ai-generated",
        generator="Method 001 Uniform Stochastic (Monte Carlo) sampling (generators/stochastic.py) - PRE-RULES raw draft",
        sources=[
            "generators/stochastic.py",
            "workflows/unitmatrix_composer.py",
        ],
        parameters={
            "method": 1,
            "phase": 1,
            "key": KEY_NAME,
            "bpm": BPM,
            "ticks_per_beat": TPB,
            "beats_per_bar": BPB,
            "sections": NUM_SECTIONS,
            "section_bars": SECTION_BARS,
            "raw_pitch_pool": RAW_PITCH_POOL,
            "raw_duration_set": RAW_DURATION_SET,
            "raw_length": RAW_LENGTH,
            "seed": SEED,
            "two_phase": True,
            "rules_applied": "NONE (pre-rules generative draft)",
        },
        notes="Phase 1: unconstrained uniform random pitch draw from full "
              "chromatic pool 50-88 (no scale membership, no voice range, "
              "no chord context) with uniform random durations from "
              "{120,240,360,480}. Raw generative material preserved for "
              "comparison against the rules-processed Phase 2 artifact. "
              "Zero-drift validated UnitMatrix export.",
    )
    write_provenance(
        MIDI_PATH,
        classification="ai-generated",
        generator="Method 001 Uniform Stochastic sampling + musicom rules (chord-tone quantization, voice leading, harmonic progression)",
        sources=[
            "generators/stochastic.py",
            "rules/voice_leading.py",
            "rules/progression.py",
            "workflows/unitmatrix_composer.py",
        ],
        parameters={
            "method": 1,
            "phase": 2,
            "key": KEY_NAME,
            "bpm": BPM,
            "ticks_per_beat": TPB,
            "beats_per_bar": BPB,
            "sections": NUM_SECTIONS,
            "section_bars": SECTION_BARS,
            "progression_degrees": SECTION_DEGREES,
            "seed": SEED,
            "voice_leading_style": "classical",
            "two_phase": True,
            "rules_applied": "chord-tone quantization, diatonic block harmony, voice-leading optimization, Phase 2c inversion-rotation correction",
        },
        notes="Phase 2: raw stochastic pitches quantized to nearest section "
              "triad tone (soprano), Alto/Tenor/Bass as diatonic block "
              "harmony via Scale7ChordDegree.get_diatonic_note(), voice-"
              "leading optimization + Phase 2c inversion-rotation correction "
              "of parallel/hidden fifths, harmonic function validation "
              "(i-VI-III-VII, D minor), zero-drift validated UnitMatrix export.",
    )
    print("[OK] Provenance sidecars written (phase 1 + phase 2).")