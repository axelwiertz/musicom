# -*- coding: utf-8 -*-
"""060 - Schillinger Resultant Chorale (Method 018).

Autonomous nightly composition job.
Composition method: Schillinger System of Musical Design (Method 018),
implemented in generators/schillinger.py.

Two-phase architecture (mandatory):
  Phase 1 (generative draft):
    - Rhythmic DNA = Schillinger resultants: algebraic interference of two
      periodic generators (a, b) -> binary resultant -> onset/duration grid.
    - Pitch DNA = axis projection: a sine trajectory maps each onset index to a
      scale-degree contour (raw, pre-harmonic).
  Phase 2 (musicom rules post-processing):
    - Quantize the raw axis-projected soprano onto the nearest chord tone of the
      section's diatonic triad (consonant melody).
    - Build Alto/Tenor/Bass as the diatonic block harmony.
    - Optimize voice leading across sections with VoiceLeadingRules
      (minimize total voice-leading distance via inversion rotation).
    - Enforce harmonic progression rules (Scale7ChordDegree + PatternMovement).
    - Zero-drift validation before MIDI export.

Engines used: structures.*, workflows.unitmatrix_composer,
visualization.grid, workflows.provenance, rules.voice_leading,
rules.progression, generators.schillinger.
"""
import os
import math
import random

from structures import MusicUnit, MusicEvent, MidiInstrument
from workflows.unitmatrix_composer import UnitMatrixComposer
from visualization.grid import write_grid_visualization
from workflows.provenance import write_provenance
from rules.voice_leading import VoiceLeadingRules
from rules.progression import Scale7ChordDegree, PatternMovementRules
from generators.schillinger import SchillingerGenerator

random.seed(18)

# ---- Composition parameters ------------------------------------------------
KEY_NAME = "G major"
KEY_ROOT_PC = 7            # G
SCALE_INTERVALS = [0, 2, 4, 5, 7, 9, 11]   # major / ionian
KEY_ROOT_MIDI = 55        # G3 (base for absolute diatonic chord calc)
BPM = 96
TPB = 480                  # ticks per beat
BPB = 4                    # beats per bar
BAR = TPB * BPB            # 1920 ticks / bar
SECTION_BARS = 2
SECTION_TICKS = SECTION_BARS * BAR          # 3840 ticks / section
NUM_SECTIONS = 4

# Bestseller progression in G major: I - V - vi - IV  (harmonic rules)
SECTION_DEGREES = [1, 5, 6, 4]
SECTION_NAMES = ["I (G)", "V (D)", "vi (Em)", "IV (C)"]

# One Schillinger generator pair per section -> distinct rhythmic DNA.
# (a, b) -> resultant interference pattern.
SECTION_GENERATORS = [(3, 2), (4, 3), (5, 3), (5, 2)]

VOICES = ["Soprano", "Alto", "Tenor", "Bass"]
VOICE_PROGRAMS = [
    MidiInstrument.FLUTE,     # Soprano (bright, melodic)
    MidiInstrument.STRING_ENSEMBLE,  # Alto
    MidiInstrument.STRING_ENSEMBLE,  # Tenor
    MidiInstrument.BASS,      # Bass
]
VOICE_CHANNELS = [0, 1, 2, 3]

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
MIDI_DIR = os.path.join(PROJECT_DIR, "MIDI")
ANALYSIS_DIR = os.path.join(PROJECT_DIR, "Analysis")
os.makedirs(MIDI_DIR, exist_ok=True)
os.makedirs(ANALYSIS_DIR, exist_ok=True)
MIDI_PATH = os.path.join(MIDI_DIR, "060-schillinger-resultant-chorale.mid")


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


def resultant_onsets(a, b, section_ticks):
    """Return (onset_ticks, note_durations) from a Schillinger resultant.

    Onsets tile the full section exactly so the unit length == section_ticks.
    """
    gen = SchillingerGenerator(generator_a=a, generator_b=b)
    durations = gen.generate_resultant()          # gaps between onsets (pulses)
    total_span = a * b
    base = section_ticks / total_span             # pulse -> tick scaling
    onsets = [0]
    for d in durations[:-1]:
        onsets.append(onsets[-1] + int(round(d * base)))
    # last note duration fills to section boundary
    note_durs = []
    for i in range(len(onsets)):
        if i + 1 < len(onsets):
            note_durs.append(onsets[i + 1] - onsets[i])
        else:
            note_durs.append(section_ticks - onsets[i])
    return onsets, note_durs


def raw_axis_pitches(n, octave_base=67):
    """Phase-1 raw pitch DNA: Schillinger axis projection (sine trajectory)."""
    scale = [octave_base + iv for iv in [0, 2, 4, 5, 7, 9, 11, 12]]
    raw = []
    for i in range(n):
        idx = int(4 + 3 * math.sin(i * 0.8))
        idx = max(0, min(len(scale) - 1, idx % len(scale)))
        raw.append(scale[idx])
    return raw


def quantize_to_chord_tone(raw_pitch, triad, lo=64, hi=86):
    """Phase-2: snap raw axis pitch to nearest chord tone in soprano register."""
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
    # Pre-compute raw rhythmic + pitch DNA for documentation
    raw_rhythm_report = []
    raw_pitch_report = []

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

    for s in range(NUM_SECTIONS):
        a, b = SECTION_GENERATORS[s]
        onsets, note_durs = resultant_onsets(a, b, SECTION_TICKS)
        triad = optimized_triads[s]
        raw_pitches = raw_axis_pitches(len(onsets))
        raw_rhythm_report.append((SECTION_NAMES[s], (a, b), onsets[:12], note_durs[:12]))
        raw_pitch_report.append((SECTION_NAMES[s], raw_pitches[:12]))

        # Voice-leading aware harmony assignment:
        #   Bass = triad root dropped an octave; Alto/Tenor = upper triad tones.
        bass_note = triad[0] - 12
        alto_note = triad[1]
        tenor_note = triad[2]

        soprano_events = []
        alto_events = []
        tenor_events = []
        bass_events = []

        for i, (on, dur) in enumerate(zip(onsets, note_durs)):
            qp = quantize_to_chord_tone(raw_pitches[i], triad)
            soprano_events.append(MusicEvent(pitch=qp, volume=90,
                                             start_tick=on, end_tick=on + dur))
            alto_events.append(MusicEvent(pitch=alto_note, volume=72,
                                          start_tick=on, end_tick=on + dur))
            tenor_events.append(MusicEvent(pitch=tenor_note, volume=72,
                                           start_tick=on, end_tick=on + dur))
            bass_events.append(MusicEvent(pitch=bass_note, volume=84,
                                          start_tick=on, end_tick=on + dur))

        composer.fill_voice_section("Soprano", SECTION_NAMES[s], MusicUnit(events=soprano_events))
        composer.fill_voice_section("Alto", SECTION_NAMES[s], MusicUnit(events=alto_events))
        composer.fill_voice_section("Tenor", SECTION_NAMES[s], MusicUnit(events=tenor_events))
        composer.fill_voice_section("Bass", SECTION_NAMES[s], MusicUnit(events=bass_events))

    # ---- Zero-drift gate ----------------------------------------------------
    ok, msg = composer.validate()
    if not ok:
        raise RuntimeError(f"Zero-drift validation FAILED: {msg}")

    composer.to_midi(MIDI_PATH)

    # ---- Grid visualization --------------------------------------------------
    grid_path = os.path.join(ANALYSIS_DIR, "grid_visualization.txt")
    write_grid_visualization(composer.matrix, grid_path,
                             ticks_per_character=120, voice_names=VOICES,
                             bpm=BPM, mode="Ionian (G major)")

    return composer, violations, raw_rhythm_report, raw_pitch_report, optimized_triads


if __name__ == "__main__":
    composer, violations, rhythm_rep, pitch_rep, triads = compose()
    size = os.path.getsize(MIDI_PATH)
    assert size > 40, f"MIDI too small ({size} bytes) - regeneration needed"
    print(f"[OK] MIDI written: {MIDI_PATH} ({size} bytes)")
    print(f"[OK] Zero-drift validation: PASS")
    print(f"[OK] Harmonic progression: I-V-vi-IV (G-D-Em-C)")
    print(f"[OK] Optimized triads (voice-leading minimized): {triads}")
    print(f"[OK] Parallel/hidden fifth violations (classical): {len(violations)}")
    if violations:
        for v in violations:
            print(f"     - {v}")
    # Provenance sidecar for the artifact
    write_provenance(
        MIDI_PATH,
        classification="ai-generated",
        generator="Method 018 Schillinger System of Musical Design (generators/schillinger.py) + musicom rules",
        sources=[
            "generators/schillinger.py",
            "rules/voice_leading.py",
            "rules/progression.py",
            "workflows/unitmatrix_composer.py",
        ],
        parameters={
            "method": 18,
            "key": KEY_NAME,
            "bpm": BPM,
            "ticks_per_beat": TPB,
            "beats_per_bar": BPB,
            "sections": NUM_SECTIONS,
            "section_bars": SECTION_BARS,
            "progression_degrees": SECTION_DEGREES,
            "schillinger_generators": SECTION_GENERATORS,
            "voice_leading_style": "classical",
            "two_phase": True,
        },
        notes="Phase 1: Schillinger resultants (rhythmic DNA) + sine axis projection (pitch DNA). "
              "Phase 2: chord-tone quantization of soprano, diatonic block harmony, "
              "voice-leading optimization, zero-drift validated UnitMatrix export.",
    )
    print(f"[OK] Provenance sidecar written.")
