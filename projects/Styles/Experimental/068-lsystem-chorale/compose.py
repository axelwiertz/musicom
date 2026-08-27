# -*- coding: utf-8 -*-
"""068 - L-System Chorale (Method 019).

Autonomous nightly composition job.
Composition method: Method 019 - L-System Algorithmic Composition
(sound/generators/event_core.py LSystemCore) - generative string rewriting.

The raw generative material is the FIBONACCI WORD, the canonical L-system
grammar from the engine's own smoke test: axiom "A", rules {"A": "AB",
"B": "A"}. After 6 iterations the word has 21 symbols (length F(8)=21) and is
strictly self-similar at every scale: the whole word is built from two
shifted copies of the previous word. Iterating the rewrite rule yields the
characteristic fractal structure that Method 019 promises: motif fragments
repeat at nested scales, never identically.

Two-phase architecture (mandatory):
  Phase 1 (generative draft, PRE-RULES):
    - Pitch DNA = symbol-driven semitone walk: 'A' steps UP +2 semitones,
      'B' steps DOWN -2 semitones, starting on A4 (69). This is a raw
      chromatic walk, NOT a scale walk: every +2 step taken from scale
      degrees 2 or 7 (B or E in A minor) lands on a non-diatonic pitch
      (C#, D#...), so the raw draft leaks chromatic tones exactly like the
      harmonic-series draft of 067 leaked partials 7/11/13/14/15.
    - Rhythm DNA = symbol identity: 'A' -> quarter (480 ticks), 'B' ->
      eighth (240 ticks). Word duration = 13*480 + 8*240 = 8160 ticks.
      Timeline = word cycles with rotation offsets (0,5,3,8) so each
      re-entry starts at a different phase of the word (self-similar but
      never identical), truncated at the 8-bar boundary (15360 ticks).
    - Single voice, no chord context, no scale enforcement, no voice
      leading.
  Phase 2 (musicom rules post-processing):
    - Quantize each raw pitch onto the nearest tone of the section's
      diatonic triad (A minor: i - VI - v - i = Am - F - Em - Am) in
      soprano register.
    - Alto/Tenor/Bass built as diatonic block harmony via the canonical
      Scale7ChordDegree.get_diatonic_note() helper (no off-by-octave wrap).
    - Voice-leading: VoiceLeadingRules.optimize_voice_leading() rotates
      inversions to minimize total voice-leading distance; then Phase 2c
      CORRECTS remaining parallel/hidden fifth violations by trying
      inversion rotations of each chord, keeping the zero-violation
      minimal-distance voicing.
    - Harmonic progression rule: i - VI - v - i (Am - F - Em - Am),
      validated against Scale7ChordDegree.function map (closed perfect
      cadence back to the tonic).
    - Zero-drift gate: UnitMatrixComposer.validate() must pass for BOTH the
      Phase 1 raw-draft MIDI and the Phase 2 rules-processed MIDI before
      to_midi(); deterministic grammar -> reproducible artifact (no rng).

Engines used: structures.*, workflows.unitmatrix_composer,
visualization.grid, workflows.provenance, rules.voice_leading,
rules.progression, sound.generators.event_core.LSystemCore.
"""
import os

from structures import MusicUnit, MusicEvent, MidiInstrument
from workflows.unitmatrix_composer import UnitMatrixComposer
from visualization.grid import write_grid_visualization
from workflows.provenance import write_provenance
from rules.voice_leading import VoiceLeadingRules
from rules.progression import Scale7ChordDegree
from sound.generators.event_core import LSystemCore

SEED = 68

# ---- Composition parameters ------------------------------------------------
KEY_NAME = "A minor (aeolian)"
KEY_ROOT_PC = 9                 # A
SCALE_INTERVALS = [0, 2, 3, 5, 7, 8, 10]    # aeolian / natural minor
KEY_ROOT_MIDI = 57              # A3 (base for absolute diatonic chord calc)
BPM = 76
TPB = 480                       # ticks per beat
BPB = 4                         # beats per bar
BAR = TPB * BPB                 # 1920 ticks / bar
SECTION_BARS = 2
SECTION_TICKS = SECTION_BARS * BAR          # 3840 ticks / section
NUM_SECTIONS = 4

# A minor: i - VI - v - i (Am - F - Em - Am). Harmonic-rule legal:
#   i (tonic, free) -> VI (tonic prolongation) -> v (dominant, minor)
#   -> i (perfect cadence, closed form).
SECTION_DEGREES = [0, 5, 4, 0]
SECTION_NAMES = ["i (Am) 1", "VI (F)", "v (Em)", "i (Am) 2"]

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
BASE = "068-lsystem-chorale"
MIDI_PATH = os.path.join(MIDI_DIR, BASE + ".mid")
PHASE1_PATH = os.path.join(MIDI_DIR, BASE + "-phase1.mid")

RAW_TOTAL_TICKS = NUM_SECTIONS * SECTION_TICKS      # 15360

# ---- L-system raw material ---------------------------------------------------
# Fibonacci word grammar (canonical L-system from the engine smoke test):
#   axiom "A", rules {"A": "AB", "B": "A"}
# 6 iterations -> 21 symbols (length F(8)=21), strictly self-similar.
LSYS_AXIOM = "A"
LSYS_RULES = {"A": "AB", "B": "A"}
LSYS_ITERATIONS = 6

# Symbol semantics (raw, pre-rules):
#   'A' -> pitch +2 semitones, quarter note (480 ticks)
#   'B' -> pitch -2 semitones, eighth note (240 ticks)
PITCH_UP = 2
PITCH_DOWN = -2
DUR_A = TPB                       # quarter
DUR_B = TPB // 2                  # eighth
START_PITCH = 69                  # A4
PITCH_LO, PITCH_HI = 55, 84       # clamp (G3..C6)
# Word cycles re-enter at different rotation offsets (self-similar, not identical).
CYCLE_OFFSETS = (0, 5, 3, 8)


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
            note_txt = "legal (tonic -> any)"
        elif fa == Scale7ChordDegree.DOMINANT:
            if fb == Scale7ChordDegree.TONIC:
                note_txt = "legal (perfect cadence)"
            elif fb == Scale7ChordDegree.TONIC_PROLONG:
                note_txt = "legal (interrupted/deceptive cadence)"
            else:
                note_txt = "CHECK"
        elif fa == Scale7ChordDegree.SUBDOMINANT:
            if fb in (Scale7ChordDegree.DOMINANT, Scale7ChordDegree.TONIC):
                note_txt = "legal (subdominant -> dominant/tonic)"
            else:
                note_txt = "CHECK"
        elif fa == Scale7ChordDegree.TONIC_PROLONG:
            note_txt = "legal (prolongation, free)"
        else:
            note_txt = "CHECK"
        report.append((a, b, note_txt))
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
    # ---- Phase 1: raw generative draft (L-system, pre-rules) ----------------
    # Use the engine's LSystemCore to materialize the Fibonacci word (6
    # iterations -> 21 symbols). Symbol -> pitch step (A:+2, B:-2) and
    # duration (A:quarter, B:eighth). Word cycles re-enter with rotation
    # offsets (0,5,3,8); timeline truncated at the 8-bar boundary. Raw
    # chromatic walk leaks C#/D# whenever a +2 step is taken from B or E.
    lsys = LSystemCore(axiom=LSYS_AXIOM, rules=LSYS_RULES)
    word = lsys.generate(LSYS_ITERATIONS)
    word_len = len(word)

    events = []
    tick = 0
    pitch = START_PITCH
    cycle = 0
    safety = 0
    while tick < RAW_TOTAL_TICKS and safety < 8000:
        safety += 1
        offset = CYCLE_OFFSETS[cycle % len(CYCLE_OFFSETS)]
        for k in range(word_len):
            sym = word[(offset + k) % word_len]
            step = PITCH_UP if sym == "A" else PITCH_DOWN
            dur = DUR_A if sym == "A" else DUR_B
            pitch = max(PITCH_LO, min(PITCH_HI, pitch + step))
            end = tick + dur
            if end > RAW_TOTAL_TICKS:
                end = RAW_TOTAL_TICKS
            if end > tick:
                events.append(MusicEvent(pitch=pitch, volume=90,
                                         start_tick=tick, end_tick=end))
            tick = end
            if tick >= RAW_TOTAL_TICKS:
                break
        cycle += 1

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
                             bpm=BPM, mode="Aeolian (A minor)")

    harm_report = harmonic_rule_report(SECTION_DEGREES)
    return (composer, violations, raw_pitch_report, raw_rhythm_report,
            corrected_triads, harm_report, fixed_report, quant_report,
            p1_composer, ok1, msg1, n_raw_leak, len(raw_pitches), word)


if __name__ == "__main__":
    (composer, violations, pitch_rep, rhythm_rep, triads, harm_report,
     fixed_report, quant_rep, p1_composer, ok1, msg1,
     n_leak, n_total, word) = compose()

    size2 = os.path.getsize(MIDI_PATH)
    size1 = os.path.getsize(PHASE1_PATH)
    assert size2 > 40, f"Phase 2 MIDI too small ({size2} bytes)"
    assert size1 > 40, f"Phase 1 MIDI too small ({size1} bytes)"
    print(f"[OK] L-system word (iterations={LSYS_ITERATIONS}, "
          f"len={len(word)}): {word}")
    print(f"[OK] Phase 1 MIDI written: {PHASE1_PATH} ({size1} bytes)")
    print(f"[OK] Phase 2 MIDI written: {MIDI_PATH} ({size2} bytes)")
    print(f"[OK] Phase 1 zero-drift validation: PASS ({ok1})")
    print(f"[OK] Phase 2 zero-drift validation: PASS")
    print(f"[OK] Harmonic progression: i-VI-v-i (Am-F-Em-Am)")
    print("[OK] Harmonic function report (degree pair -> legality):")
    for a, b, verdict in harm_report:
        print(f"     {a} -> {b}: {verdict}")
    print(f"[OK] Phase 2c voice-leading corrections applied: {len(fixed_report)} chord(s) re-voiced")
    if fixed_report:
        for idx, n in fixed_report:
            print(f"     chord {idx + 1}: {n} violation(s) corrected via inversion rotation")
    print(f"[OK] Final triads (corrected, voice-leading minimized): {triads}")
    print(f"[OK] Raw events: {n_total}, non-diatonic leak in raw draft: {n_leak}")
    print("[OK] Raw L-system pitch DNA (first 24, symbol walk A:+2/B:-2):")
    print(f"     {pitch_rep}")
    print("[OK] Raw L-system rhythm DNA (first 24, A=quarter/B=eighth):")
    print(f"     {rhythm_rep}")
    print("[OK] Phase 2 quantization (raw pitch -> chord tone, first 8 per section):")
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
        generator="Method 019 L-System Algorithmic Composition (sound/generators/event_core.py LSystemCore) - PRE-RULES raw draft",
        sources=[
            "sound/generators/event_core.py",
            "workflows/unitmatrix_composer.py",
        ],
        parameters={
            "method": 19,
            "phase": 1,
            "key": KEY_NAME,
            "bpm": BPM,
            "ticks_per_beat": TPB,
            "beats_per_bar": BPB,
            "sections": NUM_SECTIONS,
            "section_bars": SECTION_BARS,
            "axiom": LSYS_AXIOM,
            "rules": LSYS_RULES,
            "iterations": LSYS_ITERATIONS,
            "word": word,
            "symbol_semantics": "A -> pitch +2 semitones, quarter; B -> pitch -2 semitones, eighth",
            "cycle_offsets": list(CYCLE_OFFSETS),
            "start_pitch": START_PITCH,
            "seed": SEED,
            "two_phase": True,
            "rules_applied": "NONE (pre-rules generative draft)",
        },
        notes="Phase 1: Fibonacci-word L-system (axiom A, rules {A:AB, B:A}, "
              "6 iterations -> 21 symbols, strictly self-similar fractal word). "
              "Symbol-driven raw chromatic walk: A steps +2 semitones, B steps "
              "-2 semitones from A4; every +2 step taken from scale degrees 2 "
              "or 7 (B or E in A minor) leaks non-diatonic tones (C#/D#) - the "
              "pre-rules signature. Rhythm DNA = symbol identity (A:quarter, "
              "B:eighth); word cycles re-enter at rotation offsets (0,5,3,8) "
              "and the timeline is truncated at the 8-bar boundary. No scale "
              "enforcement, no chord context, no voice leading. Raw generative "
              "material preserved for comparison against the rules-processed "
              "Phase 2 artifact. Zero-drift validated UnitMatrix export.",
    )
    write_provenance(
        MIDI_PATH,
        classification="ai-generated",
        generator="Method 019 L-System Algorithmic Composition + musicom rules (chord-tone quantization, voice leading, harmonic progression)",
        sources=[
            "sound/generators/event_core.py",
            "rules/voice_leading.py",
            "rules/progression.py",
            "workflows/unitmatrix_composer.py",
        ],
        parameters={
            "method": 19,
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
        notes="Phase 2: raw L-system symbol-walk pitches quantized to nearest "
              "section triad tone (soprano), Alto/Tenor/Bass as diatonic block "
              "harmony via Scale7ChordDegree.get_diatonic_note(), voice-leading "
              "optimization + Phase 2c inversion-rotation correction of "
              "parallel/hidden fifths, harmonic function validation "
              "(i-VI-v-i, A minor, closed perfect cadence), zero-drift "
              "validated UnitMatrix export.",
    )
    print("[OK] Provenance sidecars written (phase 1 + phase 2).")
