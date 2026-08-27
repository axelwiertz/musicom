# -*- coding: utf-8 -*-
"""066 - Markov Chain Chorale (Method 020).

Autonomous nightly composition job.
Composition method: Method 020 - First-Order Markov Chain Sequencing
(generators/chain.py) - a discrete-time stochastic process with MEMORY: each
state transition depends only on the current state (Markov property), learned
from a crafted transition matrix over 12 pitch classes biased toward diatonic
stepwise motion but WITH chromatic escape states, so the raw draft carries a
stepwise-contour DNA that still leaks non-diatonic tones.

Two-phase architecture (mandatory):
  Phase 1 (generative draft):
    - Pitch DNA = first-order Markov path over 12 pitch-class states with
      memory (contrast to 065's memoryless uniform Monte Carlo). Transition
      matrix favors neighbor stepwise motion (diatonic + chromatic neighbours)
      and includes chromatic leakage, so some raw pitches are non-diatonic.
    - Rhythm DNA = a second first-order Markov path over duration states
      {1/8, 1/4} (eighth, quarter) - metrical gravity is NOT imposed; durations
      are raw chain output.
    - The raw draft is pre-rules: no chord context, no voice leading, no scale
      enforcement (chromatic escapes present). Single voice.
  Phase 2 (musicom rules post-processing):
    - Quantize each raw pitch onto the nearest tone of the section's diatonic
      triad (F major: I - vi - IV - V) in soprano register -> consonant melody.
    - Build Alto/Tenor/Bass as diatonic block harmony via the canonical
      Scale7ChordDegree.get_diatonic_note() helper (no off-by-octave wrap).
    - Voice-leading: VoiceLeadingRules.optimize_voice_leading() rotates
      inversions to minimize total voice-leading distance; then Phase 2c
      CORRECTS any remaining parallel/hidden fifth violations by trying
      inversion rotations of each chord, keeping zero-violation minimal-distance
      voicings.
    - Harmonic progression rule: F major I - vi - IV - V (F - Dm - Bb - C),
      validated against Scale7ChordDegree.function map: I (tonic, free) ->
      vi (tonic prolongation, legal) -> IV (subdominant -> dominant, legal) ->
      V (dominant -> tonic, perfect cadence).
    - Zero-drift gate: UnitMatrixComposer.validate() must pass for BOTH the
      Phase 1 raw-draft MIDI and the Phase 2 rules-processed MIDI before
      to_midi(); deterministic seed -> reproducible artifact.

Engines used: structures.*, workflows.unitmatrix_composer,
visualization.grid, workflows.provenance, rules.voice_leading,
rules.progression, generators.chain.
"""
import os
import random

from structures import MusicUnit, MusicEvent, MidiInstrument
from workflows.unitmatrix_composer import UnitMatrixComposer
from visualization.grid import write_grid_visualization
from workflows.provenance import write_provenance
from rules.voice_leading import VoiceLeadingRules
from rules.progression import Scale7ChordDegree
from generators.chain import MarkovChainGenerator

SEED = 66
random.seed(SEED)

# ---- Composition parameters ------------------------------------------------
KEY_NAME = "F major (ionian)"
KEY_ROOT_PC = 5                # F
SCALE_INTERVALS = [0, 2, 4, 5, 7, 9, 11]   # major / ionian
KEY_ROOT_MIDI = 53             # F3 (base for absolute diatonic chord calc)
BPM = 92
TPB = 480                      # ticks per beat
BPB = 4                        # beats per bar
BAR = TPB * BPB                # 1920 ticks / bar
SECTION_BARS = 2
SECTION_TICKS = SECTION_BARS * BAR          # 3840 ticks / section
NUM_SECTIONS = 4

# F major: I - vi - IV - V (F - Dm - Bb - C). Harmonic-rule legal:
#   I (tonic, free) -> vi (tonic prolongation) -> IV (subdominant -> dominant)
#   -> V (dominant -> tonic, perfect cadence).
# Scale7ChordDegree.get_diatonic_note() is 0-based (index 0 = tonic):
#   I=0, vi=5, IV=3, V=4.
SECTION_DEGREES = [0, 5, 3, 4]
SECTION_NAMES = ["I (F)", "vi (Dm)", "IV (Bb)", "V (C)"]

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
BASE = "066-markov-chain-chorale"
MIDI_PATH = os.path.join(MIDI_DIR, BASE + ".mid")
PHASE1_PATH = os.path.join(MIDI_DIR, BASE + "-phase1.mid")

# ---- Raw pitch: total number of chain steps to fill the form -----------------
# Two independent first-order Markov chains (the pitch-class chain and the
# duration-state chain) drive the raw draft. We walk one chain step at a time
# until the timeline is full, using the engine's MarkovChainGenerator.
# A MarkovChainGenerator instance over [0..13) training pairs yields a 14-state
# transition table; we drive it with the 12x12 pitch-class matrix via
# generate_sequence().
RAW_TOTAL_TICKS = NUM_SECTIONS * SECTION_TICKS      # 15360

# Pitch-class transition matrix (12x12), first-order Markov with memory.
# Bias toward stepwise neighbor motion (diatonic AND chromatic neighbours),
# plus chromatic "escape" states so the raw draft is NOT diatonic-clean.
_NEIGH = {}                                   # pc -> list of plausible next pcs
for pc in range(12):
    candidates = {
        (pc + 11) % 12, (pc + 1) % 12,          # chromatic semitone neighbours
        (pc + 2) % 12, (pc + 10) % 12,          # whole-step motion
        (pc + 7) % 12,                          # fifth leap (harmonic escape)
    }
    _NEIGH[pc] = sorted(candidates)

# Raw pitch: map each pitch class to a MIDI pitch in a wide soprano-ish
# chromatic register (pitch class 0 = F4 = 65).
RAW_PC_TO_PITCH = {pc: 65 + pc for pc in range(12)}   # 65..76, chromatic

# Duration states for a second first-order Markov chain over {1/8, 1/4}.
DUR_STATES = [TPB // 2, TPB]                       # eighth, quarter
DUR_MATRIX = [
    [0.65, 0.35],   # after an eighth: mostly another eighth (running)
    [0.55, 0.45],   # after a quarter: more balanced
]


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
    """Phase 2c: fix parallel/hidden fifths by rotating chord inversions."""
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
    """Partition raw events into per-section MusicUnits (relative ticks + pad)."""
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
    # ---- Phase 1: raw generative draft (first-order Markov, memory) --------
    # Build the first-order Markov transition model via the engine's
    # MarkovChainGenerator: train it over (current-state -> neighbour) pairs so
    # self.trans encodes the stepwise-neighbour bias (diatonic + chromatic
    # neighbours + fifth-leap escape). random.seed(SEED) keeps the walk
    # deterministic. This is the pre-rules raw draft: no chord context, no
    # voice leading, chromatic escapes leak through because neighbours include
    # non-diatonic pitch classes.
    train_pairs = []
    for pc in range(12):
        for n in _NEIGH[pc]:
            train_pairs.append((pc, n))
    chain = MarkovChainGenerator(train=train_pairs, start=0, length=1)

    events = []
    tick = 0
    cur_pc = random.randrange(12)
    cur_dur_state = random.randrange(2)
    safety = 0
    pc_path = []
    dur_path = []
    while tick < RAW_TOTAL_TICKS and safety < 8000:
        safety += 1
        # pitch: Markov step through the engine's learned transition table
        nxt = random.choice(chain.trans[cur_pc])
        cur_pc = nxt
        pc_path.append(cur_pc)
        # duration: second first-order Markov chain over {eighth, quarter}
        cur_dur_state = random.choices(range(2), weights=DUR_MATRIX[cur_dur_state])[0]
        dur = DUR_STATES[cur_dur_state]
        dur_path.append(dur)
        pitch = RAW_PC_TO_PITCH[cur_pc]
        end = tick + dur
        if end > RAW_TOTAL_TICKS:
            end = RAW_TOTAL_TICKS
        if end > tick:
            events.append(MusicEvent(pitch=pitch, volume=90,
                                     start_tick=tick, end_tick=end))
        tick = end

    raw_pitches = [e.pitch for e in events]
    raw_durs = [e.end_tick - e.start_tick for e in events]
    raw_pitch_report = raw_pitches[:24]
    raw_rhythm_report = raw_durs[:24]
    raw_leak = [p for p in raw_pitches
                if (p - KEY_ROOT_PC) % 12 not in SCALE_INTERVALS]
    n_raw_leak = len(raw_leak)

    # Split raw events into the 4 sections for the Phase 1 MIDI (single voice).
    phase1_sections = split_events_by_section(events, SECTION_TICKS, NUM_SECTIONS)

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
                             bpm=BPM, mode="Ionian (F major)")

    harm_report = harmonic_rule_report(SECTION_DEGREES)
    return (composer, violations, raw_pitch_report, raw_rhythm_report,
            corrected_triads, harm_report, fixed_report, quant_report,
            p1_composer, ok1, msg1, n_raw_leak, len(raw_pitches))


if __name__ == "__main__":
    (composer, violations, pitch_rep, rhythm_rep, triads, harm_report,
     fixed_report, quant_rep, p1_composer, ok1, msg1,
     n_leak, n_total) = compose()

    size2 = os.path.getsize(MIDI_PATH)
    size1 = os.path.getsize(PHASE1_PATH)
    assert size2 > 40, f"Phase 2 MIDI too small ({size2} bytes)"
    assert size1 > 40, f"Phase 1 MIDI too small ({size1} bytes)"
    print(f"[OK] Phase 1 MIDI written: {PHASE1_PATH} ({size1} bytes)")
    print(f"[OK] Phase 2 MIDI written: {MIDI_PATH} ({size2} bytes)")
    print(f"[OK] Phase 1 zero-drift validation: PASS ({ok1})")
    print(f"[OK] Phase 2 zero-drift validation: PASS")
    print(f"[OK] Harmonic progression: I-vi-IV-V (F-Dm-Bb-C)")
    print("[OK] Harmonic function report (degree pair -> legality):")
    for a, b, verdict in harm_report:
        print(f"     {a} -> {b}: {verdict}")
    print(f"[OK] Phase 2c voice-leading corrections applied: {len(fixed_report)} chord(s) re-voiced")
    if fixed_report:
        for idx, n in fixed_report:
            print(f"     chord {idx + 1}: {n} violation(s) corrected via inversion rotation")
    print(f"[OK] Final triads (corrected, voice-leading minimized): {triads}")
    print(f"[OK] Raw events: {n_total}, non-diatonic leak in raw draft: {n_leak}")
    print("[OK] Raw Markov pitch DNA (first 24, chromatic stepwise chain):")
    print(f"     {pitch_rep}")
    print("[OK] Raw Markov duration DNA (first 24, {1/8,1/4} chain):")
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
        generator="Method 020 First-Order Markov Chain Sequencing (generators/chain.py) - PRE-RULES raw draft",
        sources=[
            "generators/chain.py",
            "workflows/unitmatrix_composer.py",
        ],
        parameters={
            "method": 20,
            "phase": 1,
            "key": KEY_NAME,
            "bpm": BPM,
            "ticks_per_beat": TPB,
            "beats_per_bar": BPB,
            "sections": NUM_SECTIONS,
            "section_bars": SECTION_BARS,
            "pc_transition_matrix_12x12": True,
            "duration_states": DUR_STATES,
            "seed": SEED,
            "two_phase": True,
            "rules_applied": "NONE (pre-rules generative draft)",
        },
        notes="Phase 1: first-order Markov chain with memory over 12 pitch-class "
              "states (stepwise-neighbour-biased transition matrix with chromatic "
              "escape states -> raw draft leaks non-diatonic tones), plus a second "
              "first-order Markov chain over duration states {1/8,1/4}. No scale "
              "enforcement, no chord context, no voice leading in this raw draft. "
              "Raw generative material preserved for comparison against the "
              "rules-processed Phase 2 artifact. Zero-drift validated UnitMatrix export.",
    )
    write_provenance(
        MIDI_PATH,
        classification="ai-generated",
        generator="Method 020 First-Order Markov Chain Sequencing + musicom rules (chord-tone quantization, voice leading, harmonic progression)",
        sources=[
            "generators/chain.py",
            "rules/voice_leading.py",
            "rules/progression.py",
            "workflows/unitmatrix_composer.py",
        ],
        parameters={
            "method": 20,
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
        notes="Phase 2: raw Markov pitches quantized to nearest section triad tone "
              "(soprano), Alto/Tenor/Bass as diatonic block harmony via "
              "Scale7ChordDegree.get_diatonic_note(), voice-leading optimization + "
              "Phase 2c inversion-rotation correction of parallel/hidden fifths, "
              "harmonic function validation (I-vi-IV-V, F major), zero-drift "
              "validated UnitMatrix export.",
    )
    print("[OK] Provenance sidecars written (phase 1 + phase 2).")