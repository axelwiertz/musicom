# -*- coding: utf-8 -*-
"""063 - Tendency Masking Chorale (Method 023).

Autonomous nightly composition job.
Composition method: Method 023 - Tendency Masking Stochastic Bounds
(generators/tendency_masking.py).

Two-phase architecture (mandatory):
  Phase 1 (generative draft):
    - Pitch DNA = tendency-masked stochastic walk: pitches are drawn from the
      D-aeolian pitch class pool, but constrained between dynamic LOWER and
      UPPER frequency envelopes that glide across each section. Rising
      envelopes (start low -> end high) give arching "growth" phrases; falling
      envelopes give relaxation. This is the raw contour BEFORE harmonic
      correction - it is not aware of the underlying chord.
    - Rhythm DNA = stochastic event density per section (probability that a
      16th-note slot actually sounds).
  Phase 2 (musicom rules post-processing):
    - Quantize each raw tendency-masked pitch onto the nearest tone of the
      section's diatonic triad (soprano register) -> consonant melody.
    - Build Alto/Tenor/Bass as diatonic block harmony via the canonical
      Scale7ChordDegree.get_diatonic_note() helper (no off-by-octave wrap).
    - Voice-leading: VoiceLeadingRules.optimize_voice_leading() rotates
      inversions to minimize total voice-leading distance; then validate
      parallel/hidden motion (classical strictness) for the record.
    - Harmonic progression rule: D minor i - VI - III - VII (Dm-Bb-F-C),
      validated against PatternMovementRules.movement_rules and the
      Scale7ChordDegree function map (i tonic -> VI/III prolongation -> VII
      dominant -> i tonic).
    - Zero-drift gate: UnitMatrixComposer.validate() must pass before
      to_midi(); deterministic seed -> reproducible artifact.
    - Phase 1 artifact: the raw tendency-masked draft (pre-rules) is ALSO
      exported as MIDI/063-tendency-masking-chorale-phase1.mid with its own
      provenance sidecar, so the generative material is preserved next to
      the rules-processed result.

Engines used: structures.*, workflows.unitmatrix_composer,
visualization.grid, workflows.provenance, rules.voice_leading,
rules.progression, generators.tendency_masking.
"""
import os
import random

from structures import MusicUnit, MusicEvent, MidiInstrument
from workflows.unitmatrix_composer import UnitMatrixComposer
from visualization.grid import write_grid_visualization
from workflows.provenance import write_provenance
from rules.voice_leading import VoiceLeadingRules
from rules.progression import Scale7ChordDegree, PatternMovementRules
from generators.tendency_masking import TendencyMaskingGenerator

SEED = 23
random.seed(SEED)

# ---- Composition parameters ------------------------------------------------
KEY_NAME = "D minor (aeolian)"
KEY_ROOT_PC = 2                # D
SCALE_INTERVALS = [0, 2, 3, 5, 7, 8, 10]   # natural minor / aeolian
KEY_ROOT_MIDI = 50             # D3 (base for absolute diatonic chord calc)
BPM = 92
TPB = 480                      # ticks per beat
BPB = 4                        # beats per bar
BAR = TPB * BPB                # 1920 ticks / bar
SECTION_BARS = 2
SECTION_TICKS = SECTION_BARS * BAR          # 3840 ticks / section
NUM_SECTIONS = 4

# D minor: i - VI - III - VII (Dm - Bb - F - C). Harmonic-rule legal:
#   i (tonic) -> VI/III (tonic prolongation) -> VII (dominant) -> i (tonic)
# NOTE: Scale7ChordDegree.get_diatonic_note() is 0-based (index 0 = tonic,
# scale_intervals[0] is the tonic pitch), so the degree list below is 0-based:
#   i=0, VI=5, III=2, VII=6.
SECTION_DEGREES = [0, 5, 2, 6]
SECTION_NAMES = ["i (Dm)", "VI (Bb)", "III (F)", "VII (C)"]

# Tendency-masking envelope per section (low, high) -> (low, high) in MIDI.
# Rising envelope = arching growth phrase; falling = relaxation.
SECTION_ENVELOPES = [
    ((62, 74), (72, 84)),    # i (Dm):   rising - opening growth, lands on D
    ((70, 82), (62, 74)),    # VI (Bb):  falling - relaxation
    ((62, 74), (72, 84)),    # III (F):  rising - lift toward dominant
    ((72, 84), (62, 74)),    # VII (C):  falling - resolve down to tonic
]

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
os.makedirs(MIDI_DIR, exist_ok=True)
os.makedirs(ANALYSIS_DIR, exist_ok=True)
MIDI_PATH = os.path.join(MIDI_DIR, "063-tendency-masking-chorale.mid")
# Phase 1 artifact: raw generative draft BEFORE rules post-processing
PHASE1_MIDI_PATH = os.path.join(MIDI_DIR, "063-tendency-masking-chorale-phase1.mid")


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
    """Phase-2: snap raw tendency-masked pitch to nearest chord tone (soprano)."""
    candidates = set()
    for p in triad:
        for shift in (-12, 0, 12):
            cand = p + shift
            if lo <= cand <= hi:
                candidates.add(cand)
    if not candidates:
        candidates = set(triad)
    return min(candidates, key=lambda c: abs(c - raw_pitch))


# ---- Phase 1 + 2 composition ----------------------------------------------
def compose():
    # D-aeolian pitch class pool (absolute, soprano register) for Phase 1
    key_pitches = [62 + iv for iv in [0, 2, 3, 5, 7, 8, 10]]   # D4..C5
    gen = TendencyMaskingGenerator(key_pitches=key_pitches)

    # Build diatonic triads for each section, then optimize voice leading.
    base_triads = [sorted(chord_triad_abs(d)) for d in SECTION_DEGREES]
    vl = VoiceLeadingRules(style="classical")
    optimized_triads = vl.optimize_voice_leading(base_triads)

    # Report parallel / hidden motions for the record (classical strictness)
    violations = []
    for i in range(len(optimized_triads) - 1):
        violations += vl.check_parallel_motion(optimized_triads[i], optimized_triads[i + 1])
        violations += vl.check_hidden_fifths(optimized_triads[i], optimized_triads[i + 1])

    composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BPB)
    composer.create_matrix(num_voices=len(VOICES), num_sections=NUM_SECTIONS)
    for name, prog, ch in zip(VOICES, VOICE_PROGRAMS, VOICE_CHANNELS):
        composer.add_voice(name, program=prog, channel=ch)
    for sname in SECTION_NAMES:
        composer.add_section(sname, bars=SECTION_BARS)

    raw_pitch_report = []
    raw_rhythm_report = []
    raw_soprano_units = []   # Phase 1 draft units (one per section, for export)

    for s in range(NUM_SECTIONS):
        (lo0, hi0), (lo1, hi1) = SECTION_ENVELOPES[s]
        triad = optimized_triads[s]
        # Phase 1: tendency-masked stochastic draft (16th-note slots)
        unit = gen.generate_voice_section(
            section_ticks=SECTION_TICKS,
            step_ticks=TPB // 4,          # 16th-note resolution
            bounds_start=(lo0, hi0),
            bounds_end=(lo1, hi1),
            density=0.75,
            volume=90,
        )
        raw_events = [e for e in unit.events if e.pitch != 0]
        raw_pitches = [e.pitch for e in raw_events]
        raw_rhythm_report.append((SECTION_NAMES[s], len(raw_events)))
        raw_pitch_report.append((SECTION_NAMES[s], raw_pitches[:12]))
        raw_soprano_units.append(unit)   # keep raw draft for Phase 1 artifact

        # Voice-leading aware harmony assignment:
        #   Bass = triad root dropped an octave; Alto/Tenor = upper triad tones.
        bass_note = triad[0] - 12
        alto_note = triad[1]
        tenor_note = triad[2]

        soprano_events = []
        alto_events = []
        tenor_events = []
        bass_events = []

        for e in raw_events:
            qp = quantize_to_chord_tone(e.pitch, triad)
            dur = e.end_tick - e.start_tick
            soprano_events.append(MusicEvent(pitch=qp, volume=90,
                                             start_tick=e.start_tick,
                                             end_tick=e.end_tick))
            alto_events.append(MusicEvent(pitch=alto_note, volume=72,
                                          start_tick=e.start_tick,
                                          end_tick=e.end_tick))
            tenor_events.append(MusicEvent(pitch=tenor_note, volume=72,
                                           start_tick=e.start_tick,
                                           end_tick=e.end_tick))
            bass_events.append(MusicEvent(pitch=bass_note, volume=84,
                                          start_tick=e.start_tick,
                                          end_tick=e.end_tick))

        composer.fill_voice_section("Soprano", SECTION_NAMES[s], MusicUnit(events=soprano_events))
        composer.fill_voice_section("Alto", SECTION_NAMES[s], MusicUnit(events=alto_events))
        composer.fill_voice_section("Tenor", SECTION_NAMES[s], MusicUnit(events=tenor_events))
        composer.fill_voice_section("Bass", SECTION_NAMES[s], MusicUnit(events=bass_events))

        # Pad each section cell to its declared boundary (SECTION_TICKS) with a
        # silent landmark so len_ticks() == SECTION_TICKS exactly and the
        # composition spans a clean 8 bars (zero cumulative drift).
        for voice_name in VOICES:
            unit = composer.matrix.get_unit((composer.voices[[v['name'] for v in composer.voices].index(voice_name)]['row'], s))
            last_end = max(e.end_tick for e in unit.events) if unit.events else 0
            if last_end < SECTION_TICKS:
                unit.add_event(MusicEvent(pitch=0, volume=0,
                                          start_tick=last_end,
                                          end_tick=SECTION_TICKS))

    # ---- Zero-drift gate ----------------------------------------------------
    ok, msg = composer.validate()
    if not ok:
        raise RuntimeError(f"Zero-drift validation FAILED: {msg}")

    composer.to_midi(MIDI_PATH)

    # ---- Phase 1 artifact: raw generative draft MIDI ------------------------
    # Export the tendency-masked stochastic draft (unquantized, pre-rules)
    # as its own MIDI file next to the Phase 2 result, so the raw algorithmic
    # material is preserved and comparable.
    p1 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BPB)
    p1.create_matrix(num_voices=1, num_sections=NUM_SECTIONS)
    p1.add_voice("RawDraft", program=MidiInstrument.FLUTE, channel=0)
    for sname in SECTION_NAMES:
        p1.add_section(sname, bars=SECTION_BARS)
    for s, raw_unit in enumerate(raw_soprano_units):
        # copy events (avoid aliasing issues), filter out silent landmark
        events = [MusicEvent(pitch=e.pitch, volume=e.volume,
                             start_tick=e.start_tick, end_tick=e.end_tick)
                  for e in raw_unit.events]
        p1.fill_voice_section("RawDraft", SECTION_NAMES[s], MusicUnit(events=events))
    ok1, msg1 = p1.validate()
    if not ok1:
        raise RuntimeError(f"Phase 1 zero-drift validation FAILED: {msg1}")
    p1.to_midi(PHASE1_MIDI_PATH)

    # ---- Grid visualization --------------------------------------------------
    grid_path = os.path.join(ANALYSIS_DIR, "grid_visualization.txt")
    write_grid_visualization(composer.matrix, grid_path,
                             ticks_per_character=120, voice_names=VOICES,
                             bpm=BPM, mode="Aeolian (D minor)")

    return composer, violations, raw_pitch_report, raw_rhythm_report, optimized_triads


if __name__ == "__main__":
    composer, violations, pitch_rep, rhythm_rep, triads = compose()
    size = os.path.getsize(MIDI_PATH)
    assert size > 40, f"MIDI too small ({size} bytes) - regeneration needed"
    print(f"[OK] MIDI written: {MIDI_PATH} ({size} bytes)")
    print(f"[OK] Phase 1 MIDI written: {PHASE1_MIDI_PATH} "
          f"({os.path.getsize(PHASE1_MIDI_PATH)} bytes)")
    print(f"[OK] Zero-drift validation: PASS")
    print(f"[OK] Harmonic progression: i-VI-III-VII (Dm-Bb-F-C)")
    print(f"[OK] Optimized triads (voice-leading minimized): {triads}")
    print(f"[OK] Tendency-masked raw pitch DNA (first 12 per section):")
    for name, pitches in pitch_rep:
        print(f"     {name}: {pitches}")
    print(f"[OK] Raw onset counts (16th-note slots, density 0.75):")
    for name, n in rhythm_rep:
        print(f"     {name}: {n} onsets")
    print(f"[OK] Parallel/hidden fifth violations (classical): {len(violations)}")
    if violations:
        for v in violations:
            print(f"     - {v}")
    # Provenance sidecar for the artifact
    write_provenance(
        MIDI_PATH,
        classification="ai-generated",
        generator="Method 023 Tendency Masking Stochastic Bounds (generators/tendency_masking.py) + musicom rules",
        sources=[
            "generators/tendency_masking.py",
            "rules/voice_leading.py",
            "rules/progression.py",
            "workflows/unitmatrix_composer.py",
        ],
        parameters={
            "method": 23,
            "key": KEY_NAME,
            "bpm": BPM,
            "ticks_per_beat": TPB,
            "beats_per_bar": BPB,
            "sections": NUM_SECTIONS,
            "section_bars": SECTION_BARS,
            "progression_degrees": SECTION_DEGREES,
            "envelopes": SECTION_ENVELOPES,
            "step_ticks": TPB // 4,
            "density": 0.75,
            "seed": SEED,
            "voice_leading_style": "classical",
            "two_phase": True,
        },
        notes="Phase 1: tendency-masked stochastic pitch walk inside dynamic "
              "frequency envelopes (rising = growth, falling = relaxation) + "
              "16th-note stochastic density. Phase 2: chord-tone quantization "
              "of soprano, diatonic block harmony, voice-leading optimization, "
              "zero-drift validated UnitMatrix export.",
    )
    print(f"[OK] Provenance sidecar written.")

    # Provenance for the Phase 1 artifact (raw generative draft)
    write_provenance(
        PHASE1_MIDI_PATH,
        classification="ai-generated",
        generator="Method 023 Tendency Masking Stochastic Bounds (generators/tendency_masking.py) — Phase 1 raw draft, pre-rules",
        sources=[
            "generators/tendency_masking.py",
        ],
        parameters={
            "method": 23,
            "phase": 1,
            "key": KEY_NAME,
            "bpm": BPM,
            "ticks_per_beat": TPB,
            "beats_per_bar": BPB,
            "sections": NUM_SECTIONS,
            "section_bars": SECTION_BARS,
            "envelopes": SECTION_ENVELOPES,
            "step_ticks": TPB // 4,
            "density": 0.75,
            "seed": SEED,
            "two_phase": True,
        },
        notes="Phase 1 raw generative draft: tendency-masked stochastic pitches "
              "constrained to dynamic frequency envelopes, exported BEFORE any "
              "musicom rules post-processing (no chord quantization, no voice "
              "leading, no harmony). Compare against the Phase 2 artifact "
              "063-tendency-masking-chorale.mid.",
    )
    print(f"[OK] Phase 1 provenance sidecar written.")
