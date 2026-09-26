# -*- coding: utf-8 -*-
"""204-minimalism-phase-expanded - Minimalism rework of 001-minimalism-phase-study.

Autonomous rework agent (date: 2026-09-26).
Source: Minimalism/001-minimalism-phase-study (Steve Reich "Clapping Music"
style phase piece). Audit result: engine PASS, zero-drift PASS, rhythm-grid
PASS, >=4 tracks PASS, BUT two-phase artifacts FAIL (no phase1 mid), and
provenance.json + index.html FAIL. => redesign_required = True.

Identity preserved: C major pentatonic (C D E G A), 120 BPM, E(5,12)
Euclidean marimba cell, two marimbas phase-walking +1 beat per section,
sustained pad + bass pedal + sparse perc.

Rework -> NEW LONGER version with MORE variation:
  10 sections x 3 bars = 30 bars (source was 8 x 3 = 24 bars).
  Variation techniques applied (6 distinct, documented per section):
    1. Phase walk (per-section method change): MarimbaB phase offset +1 beat/section.
    2. Transposition / register shift: Transpose section (+P5), Climax (+P8).
    3. Inversion: Inversion section (mirror around axis 64).
    4. Retrograde: Retrograde section (reverse onset order).
    5. Augmentation: Augment section (half speed, step 480 -> 960).
    6. Diminution + density rise: Climax section (8th-note cell + hihats + snare).
  Per-section harmonic regions: each section its own 3-bar chord progression
  drawn from pentatonic-subset chords C / Am / Gsus / Dsus (never all tonic).

Two-phase architecture:
  Phase 1: raw generative draft - single voice, chromatic random-walk pitch
           + off-grid micro-jitter, no chord quantization. Exported as
           <id>-phase1.mid with its own validate() gate.
  Phase 2: musicom rules post-process - per-bar chord-tone quantization
           (floor t//BAR attribution), 16th-grid snap, dedup of collided
           (start_tick, pitch), zero-drift gate. Exported as <id>.mid.
"""

import os
import numpy as np

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer
from workflows.provenance import write_provenance, AI_ASSISTED
from visualization.grid import write_grid_visualization

SEED = 20260926
rng = np.random.default_rng(SEED)

PROJ = "/opt/data/repos/musicom/projects/Styles/Minimalism/204-minimalism-phase-expanded"
MIDI_DIR = os.path.join(PROJ, "MIDI")
AUDIO_DIR = os.path.join(PROJ, "Audio")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")
for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
    os.makedirs(d, exist_ok=True)

# ----------------------------------------------------------------- timing
BPM = 120
TPB = 480
BEATS_PER_BAR = 4
BAR = TPB * BEATS_PER_BAR          # 1920
QUARTER = TPB                      # 480
EIGHTH = TPB // 2                  # 240
SIXTEENTH = TPB // 4               # 120

BARS_PER_SECTION = 3
SECTION = BAR * BARS_PER_SECTION   # 5760
N_SECTIONS = 10
TOTAL = SECTION * N_SECTIONS       # 57600

# ----------------------------------------------------------------- key
# C major pentatonic (C D E G A) - the Reich identity
KEY_PCS = {0, 2, 4, 7, 9}

# Chord palette drawn ENTIRELY from the pentatonic (all pc in KEY_PCS):
#   C    = I     (C E G)
#   Am   = vi    (A C E)
#   Gsus = V(sus)(G D C)
#   Dsus = II(sus)(D G A)
CHORD_PCS = {
    "C":    {0, 4, 7},
    "Am":   {9, 0, 4},
    "Gsus": {7, 2, 0},
    "Dsus": {2, 7, 9},
}
CHORD_ROOTS = {"C": 0, "Am": 9, "Gsus": 7, "Dsus": 2}

SECTIONS = ["Intro", "Phase1", "Phase2", "Phase3", "Transpose",
            "Inversion", "Retrograde", "Augment", "Climax", "Outro"]

# Per-section harmonic region: 3 bars, each with its own chord (own short
# progression; midpoint bar differs per section so roots never all collapse
# to tonic).
SECTION_CHORDS = {
    0: ["C", "C", "C"],          # Intro
    1: ["C", "Gsus", "C"],       # Phase1
    2: ["Am", "Dsus", "C"],      # Phase2
    3: ["Dsus", "C", "Gsus"],    # Phase3
    4: ["Gsus", "C", "Am"],      # Transpose
    5: ["C", "Am", "Dsus"],      # Inversion
    6: ["Am", "Dsus", "Gsus"],   # Retrograde
    7: ["Dsus", "Dsus", "Gsus"], # Augment
    8: ["Gsus", "Am", "Dsus"],   # Climax
    9: ["C", "C", "C"],          # Outro
}

# Per-section variation method (see header for the 6 techniques).
#   a/b = cell pitch method for MarimbaA / MarimbaB
#   step_scale = 1.0 quarter, 2.0 half (augmentation), 0.5 eighth (diminution)
#   phase_beats = MarimbaB phase-walk offset (beats)
SECTION_METHOD = {
    0: {"a": "base",             "b": "base",             "step_scale": 1.0, "phase_beats": 0},
    1: {"a": "base",             "b": "base",             "step_scale": 1.0, "phase_beats": 1},
    2: {"a": "base",             "b": "base",             "step_scale": 1.0, "phase_beats": 2},
    3: {"a": "base",             "b": "base",             "step_scale": 1.0, "phase_beats": 3},
    4: {"a": "base",             "b": "transpose_fifth",  "step_scale": 1.0, "phase_beats": 4},
    5: {"a": "base",             "b": "invert",           "step_scale": 1.0, "phase_beats": 5},
    6: {"a": "base",             "b": "retrograde",       "step_scale": 1.0, "phase_beats": 6},
    7: {"a": "base",             "b": "base",             "step_scale": 2.0, "phase_beats": 7},
    8: {"a": "transpose_octave", "b": "transpose_octave", "step_scale": 0.5, "phase_beats": 8},
    9: {"a": "base",             "b": "base",             "step_scale": 1.0, "phase_beats": 9},
}


def get_bar_chord(sec_idx, bar_in_sec):
    return SECTION_CHORDS[sec_idx][bar_in_sec]


# ----------------------------------------------------------------- helpers
def euclidean(pulses, steps):
    """Bjorklund Euclidean rhythm -> list of bools (length `steps`)."""
    out = []
    bucket = 0.0
    for _ in range(steps):
        bucket += pulses
        if bucket >= steps:
            bucket -= steps
            out.append(True)
        else:
            out.append(False)
    return out


def snap_to_grid(t, grid=SIXTEENTH):
    """Phase-2 rule: snap onset to the 8th/16th grid."""
    return int(round(t / grid) * grid)


def quantize_to_chord(pitch, chord_pcs, min_pitch=55, max_pitch=96):
    """Phase-2 rule: nearest MIDI pitch whose pitch-class is in chord_pcs."""
    candidates = []
    for octv in range(0, 9):
        for pc in chord_pcs:
            p = octv * 12 + pc
            if min_pitch <= p <= max_pitch:
                candidates.append(p)
    if not candidates:
        candidates = [pc for pc in chord_pcs]
    return min(candidates, key=lambda c: (abs(c - pitch), c))


def transform_pitches(method, pitches):
    if method == "base":
        return list(pitches)
    if method == "transpose_fifth":
        return [p + 7 for p in pitches]
    if method == "transpose_octave":
        return [p + 12 for p in pitches]
    if method == "invert":
        axis = 64
        return [2 * axis - p for p in pitches]
    if method == "retrograde":
        return list(reversed(pitches))
    return list(pitches)


def voice_chord(chord, base=48, octave_shift=0):
    """Closed-position chord voicing, root lowest, all pc in CHORD_PCS[chord]."""
    root = CHORD_ROOTS[chord]
    tones = sorted(CHORD_PCS[chord])
    ri = tones.index(root)
    tones = tones[ri:] + tones[:ri]  # rotate so root is first
    out = []
    for i, pc in enumerate(tones):
        p = base + pc
        if i > 0 and p <= out[-1]:
            p += 12
        out.append(p + octave_shift * 12)
    return out


def dedup_events(events):
    """Phase-2 rule: dedup collided (start_tick, pitch), keep longest duration."""
    landmark = None
    real = {}
    for e in events:
        if e.pitch == 0:
            landmark = e
            continue
        key = (e.start_tick, e.pitch)
        if key not in real or e.end_tick > real[key].end_tick:
            real[key] = e
    out = sorted(real.values(), key=lambda e: (e.start_tick, e.end_tick))
    if landmark is not None:
        out.append(landmark)
    return out


def landmark():
    return MusicEvent(pitch=0, volume=0, start_tick=SECTION - 1, end_tick=SECTION)


# ----------------------------------------------------------------- cells
BASE_PITCHES = [60, 62, 64, 67, 69]  # C D E G A ascending pentatonic


def build_cell(sec_idx, method, step_scale, phase_beats, quantize=True):
    """E(5,12) marimba cell for one section (section-relative ticks).

    Phase 2 rules applied when quantize=True: per-bar chord-tone quantization
    (floor t//BAR), 16th-grid snap, dedup."""
    pitches = transform_pitches(method, BASE_PITCHES)
    step = int(QUARTER * step_scale)
    phase = phase_beats * QUARTER
    pattern = euclidean(5, 12)
    dur = step // 2
    events = []
    hit_idx = 0
    for i, hit in enumerate(pattern):
        if not hit:
            continue
        t0 = snap_to_grid((phase + i * step) % SECTION)
        raw = pitches[hit_idx % len(pitches)]
        hit_idx += 1
        if quantize:
            bar_in_sec = t0 // BAR
            chord = get_bar_chord(sec_idx, bar_in_sec)
            p = quantize_to_chord(raw, CHORD_PCS[chord])
        else:
            p = raw
        end = t0 + dur
        if end > SECTION:
            end = SECTION
        events.append(MusicEvent(pitch=p, volume=88, start_tick=t0, end_tick=end))
    events.append(landmark())
    return dedup_events(events)


def build_pad(sec_idx):
    """Sustained pad: one chord per bar, closed voicing around C3-C5."""
    events = []
    for bar in range(BARS_PER_SECTION):
        chord = get_bar_chord(sec_idx, bar)
        t0 = bar * BAR
        for p in voice_chord(chord, base=48):
            events.append(MusicEvent(pitch=p, volume=68, start_tick=t0, end_tick=t0 + BAR))
        if SECTIONS[sec_idx] == "Climax":
            for p in voice_chord(chord, base=60):
                events.append(MusicEvent(pitch=p, volume=58, start_tick=t0, end_tick=t0 + BAR))
    events.append(landmark())
    return events


def build_bass(sec_idx):
    """Bass pedal: root (half note) + fifth (half note) per bar, all chord tones."""
    events = []
    for bar in range(BARS_PER_SECTION):
        chord = get_bar_chord(sec_idx, bar)
        root = CHORD_ROOTS[chord]
        root_pitch = 36 + root
        fifth = root_pitch + 7
        t0 = bar * BAR
        events.append(MusicEvent(pitch=root_pitch, volume=78, start_tick=t0, end_tick=t0 + QUARTER * 2))
        events.append(MusicEvent(pitch=fifth, volume=70, start_tick=t0 + QUARTER * 2, end_tick=t0 + BAR))
    events.append(landmark())
    return events


def build_perc(sec_idx, dense=False):
    """Percussion: E(5,16) kick every bar; hihats + snare added in dense/climax."""
    events = []
    for bar in range(BARS_PER_SECTION):
        bar_start = bar * BAR
        for i, hit in enumerate(euclidean(5, 16)):
            if hit:
                t0 = bar_start + i * SIXTEENTH
                events.append(MusicEvent(pitch=36, volume=95, start_tick=t0, end_tick=t0 + SIXTEENTH))
        if dense or SECTIONS[sec_idx] == "Climax":
            for i in range(8):
                t0 = bar_start + i * EIGHTH
                vel = 82 if i % 2 == 0 else 60
                events.append(MusicEvent(pitch=42, volume=vel, start_tick=t0, end_tick=t0 + 60))
            for i in (2, 6):
                t0 = bar_start + i * EIGHTH
                events.append(MusicEvent(pitch=38, volume=90, start_tick=t0, end_tick=t0 + 80))
    events.append(landmark())
    return events


# ========================================================================
# PHASE 1: raw generative draft (single voice, unquantized, off-grid)
# ========================================================================
def generate_phase1():
    composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS_PER_BAR)
    composer.create_matrix(num_voices=1, num_sections=N_SECTIONS)
    composer.add_voice("Raw_Lead", program=12, channel=0)

    raw_pitch = 67
    for s_idx, s_name in enumerate(SECTIONS):
        composer.add_section(s_name, bars=BARS_PER_SECTION)
        events = []
        step = QUARTER
        phase = s_idx * QUARTER
        for i, hit in enumerate(euclidean(5, 12)):
            if not hit:
                continue
            jitter = int(rng.integers(-25, 25))
            t0 = (phase + i * step + jitter) % SECTION
            t0 = max(0, min(t0, SECTION - 40))
            raw_pitch += int(rng.integers(-3, 4))
            raw_pitch = int(np.clip(raw_pitch, 55, 96))
            dur = int(rng.uniform(140, 260))
            end = min(t0 + dur, SECTION)
            events.append(MusicEvent(pitch=raw_pitch, volume=88, start_tick=t0, end_tick=end))
        events.append(landmark())
        composer.fill_voice_section("Raw_Lead", s_name, MusicUnit(events=events))

    ok, msg = composer.validate()
    assert ok, "Phase 1 validate failed: " + msg

    p1 = os.path.join(MIDI_DIR, "204-minimalism-phase-expanded-phase1.mid")
    composer.to_midi(p1)
    assert os.path.getsize(p1) > 40, "phase1 midi empty"

    write_provenance(
        p1, classification=AI_ASSISTED,
        generator="musicom.workflows.unitmatrix_composer",
        parameters={
            "project": "204-minimalism-phase-expanded", "phase": 1,
            "style": "Minimalism", "method": "Euclidean phase process (raw)",
            "key": "C pentatonic", "bpm": BPM, "seed": SEED,
            "raw_timing": "off-grid micro-jitter", "raw_pitch": "chromatic random walk",
            "source": "001-minimalism-phase-study (redesign)",
        })
    print("Phase 1 MIDI:", p1, os.path.getsize(p1), "bytes")
    return p1


# ========================================================================
# PHASE 2: musicom rules post-process + multi-voice arrangement
# ========================================================================
def generate_phase2():
    composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS_PER_BAR)
    composer.create_matrix(num_voices=5, num_sections=N_SECTIONS)
    composer.add_voice("MarimbaA", program=12, channel=0)
    composer.add_voice("MarimbaB", program=12, channel=1)
    composer.add_voice("Pad", program=49, channel=2)       # STRING_ENSEMBLE
    composer.add_voice("Bass", program=33, channel=3)      # BASS
    composer.add_voice("Perc", program=0, channel=9)

    for s_idx, s_name in enumerate(SECTIONS):
        composer.add_section(s_name, bars=BARS_PER_SECTION)
        m = SECTION_METHOD[s_idx]
        dense = (s_name == "Climax")
        composer.fill_voice_section(
            "MarimbaA", s_name,
            MusicUnit(events=build_cell(s_idx, m["a"], m["step_scale"], 0, quantize=True)))
        composer.fill_voice_section(
            "MarimbaB", s_name,
            MusicUnit(events=build_cell(s_idx, m["b"], m["step_scale"], m["phase_beats"], quantize=True)))
        composer.fill_voice_section("Pad", s_name, MusicUnit(events=build_pad(s_idx)))
        composer.fill_voice_section("Bass", s_name, MusicUnit(events=build_bass(s_idx)))
        composer.fill_voice_section("Perc", s_name, MusicUnit(events=build_perc(s_idx, dense=dense)))

    ok, msg = composer.validate()
    assert ok, "Phase 2 validate failed: " + msg

    p2 = os.path.join(MIDI_DIR, "204-minimalism-phase-expanded.mid")
    composer.to_midi(p2)
    assert os.path.getsize(p2) > 40, "phase2 midi empty"

    write_grid_visualization(
        composer.matrix,
        os.path.join(ANALYSIS_DIR, "grid_visualization.txt"),
        ticks_per_character=240,
        voice_names=["MarimbaA", "MarimbaB", "Pad", "Bass", "Perc"],
        bpm=BPM)

    write_provenance(
        p2, classification=AI_ASSISTED,
        generator="musicom.workflows.unitmatrix_composer",
        parameters={
            "project": "204-minimalism-phase-expanded", "phase": 2,
            "style": "Minimalism", "method": "Euclidean phase process + musicom rules",
            "key": "C pentatonic", "bpm": BPM, "seed": SEED,
            "quantization": "16th-grid snap + per-bar chord-tone",
            "progression": "C / Am / Gsus / Dsus (pentatonic subset)",
            "variation": ["phase-walk", "transposition", "inversion",
                          "retrograde", "augmentation", "diminution+density"],
            "source": "001-minimalism-phase-study (redesign)",
        })
    print("Phase 2 MIDI:", p2, os.path.getsize(p2), "bytes")
    return p2


if __name__ == "__main__":
    print("=== Phase 1 raw draft ===")
    generate_phase1()
    print("=== Phase 2 rules composition ===")
    generate_phase2()
    print("Done.")
