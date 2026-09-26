# -*- coding: utf-8 -*-
"""206-ragtime-skeleton-refinement - Ragtime style / Method 001 Skeleton-First Refinement.

Autonomous nightly composition job (date: 2026-09-26).
Style: Ragtime (solo piano stride, Scott Joplin idiom)
Method: 001 Skeleton-First Refinement
Layer: concrete

Two-phase architecture:
  Phase 1: Raw generative draft - single voice (Melody) driven by the
           deterministic structural skeleton (scale-degree line). Unquantized
           micro-timing, NO harmony (no chord snapping, no bass/comp), exported
           as <project>-phase1.mid with its own zero-drift gate.
  Phase 2: Musicom rules post-processing - strict 16th-grid snap, per-bar
           chord-tone quantization, syncopated 16th elaboration, stride bass +
           chord comp (full piano texture), exported as <project>.mid.

Key: C major (pitch classes {0,2,4,5,7,9,11}).
Form: Intro(4) | A(8) | B(8) | A2(8) | Trio(8) | Coda(4)  = 40 bars
BPM 120, 4/4, 480 TPB.
"""

import os
import sys
import json
import numpy as np

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer
from workflows.provenance import write_provenance, AI_ASSISTED
from visualization.grid import write_grid_visualization

# Instrument registry (source of truth)
INSTR_DIR = "/opt/data/repos/musicom/projects/Instruments"
if INSTR_DIR not in sys.path:
    sys.path.insert(0, INSTR_DIR)
from instrument_registry import PIANO

SEED = 20260926
rng = np.random.default_rng(SEED)

PROJ = "/opt/data/repos/musicom/projects/Styles/Ragtime/206-ragtime-skeleton-refinement"
MIDI_DIR = os.path.join(PROJ, "MIDI")
AUDIO_DIR = os.path.join(PROJ, "Audio")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")
for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
    os.makedirs(d, exist_ok=True)

# ---------------------------------------------------------------- Grid & Timing
BPM = 120
TPB = 480
BEATS_PER_BAR = 4
GRID16 = 120
GRID8 = 240
BAR_TICKS = TPB * BEATS_PER_BAR       # 1920

SECTIONS = ["Intro", "A", "B", "A2", "Trio", "Coda"]
BARS = [4, 8, 8, 8, 8, 4]            # per-section bar counts
N_SECTIONS = len(SECTIONS)
N_BARS = sum(BARS)                    # 40

# ---------------------------------------------------------------- Harmonic Framework
# Key: C major.  Scale pitch classes (C D E F G A B).
SCALE_PCS = [0, 2, 4, 5, 7, 9, 11]
SCALE_SET = set(SCALE_PCS)

# Diatonic chords (name -> pitch-class set), all subsets of C major.
CHORDS = {
    "C":     {0, 4, 7},
    "Cmaj7": {0, 4, 7, 11},
    "Dm":    {2, 5, 9},
    "Dm7":   {2, 5, 9, 0},
    "Em7":   {4, 7, 11, 2},
    "F":     {5, 9, 0},
    "Fmaj7": {5, 9, 0, 4},
    "G7":    {7, 11, 2, 5},
    "Am":    {9, 0, 4},
    "Am7":   {9, 0, 4, 7},
}

# Chord root pitch class (for stride bass).
CHORD_ROOT = {
    "C": 0, "Cmaj7": 0, "Dm": 2, "Dm7": 2, "Em7": 4,
    "F": 5, "Fmaj7": 5, "G7": 7, "Am": 9, "Am7": 9,
}

# Per-section progression (one chord name per bar).
SECTION_CHORDS = {
    "Intro": ["G7", "G7", "G7", "G7"],
    "A":     ["C", "Cmaj7", "Am", "Dm7", "G7", "C", "F", "G7"],
    "B":     ["F", "Fmaj7", "Dm", "G7", "Em7", "Am", "Dm7", "G7"],
    "A2":    ["C", "Cmaj7", "Am", "Dm7", "G7", "C", "G7", "C"],
    "Trio":  ["F", "F", "Dm", "G7", "C", "Am", "F", "G7"],
    "Coda":  ["C", "G7", "C", "C"],
}

# Flat per-bar chord-name list + per-bar chord PC set + per-bar root PC.
BAR_CHORD_NAMES = []
for s in SECTIONS:
    BAR_CHORD_NAMES.extend(SECTION_CHORDS[s])
assert len(BAR_CHORD_NAMES) == N_BARS, (len(BAR_CHORD_NAMES), N_BARS)
BAR_CHORD_PCS = [CHORDS[n] for n in BAR_CHORD_NAMES]
BAR_ROOT_PC = [CHORD_ROOT[n] for n in BAR_CHORD_NAMES]

# ---------------------------------------------------------------- Method 001: Skeleton
# The "skeleton" = a deterministic structural line of SCALE DEGREES (deep structure),
# one degree per HALF-BAR.  Refinement (phase 2) elaborates each degree into a
# syncopated 16th chord-tone figure.  Scale degree d (1..8): 1=C,2=D,...,7=B,8=C'.
SKELETON = {
    "Intro": [5, 5, 4, 3, 2, 7, 5, 5],
    "A":     [1, 3, 5, 6, 5, 3, 2, 1, 3, 5, 6, 8, 6, 5, 3, 2],
    "B":     [5, 8, 7, 5, 3, 1, 3, 5, 6, 5, 3, 2, 1, 2, 3, 5],
    "A2":    [1, 3, 5, 6, 5, 3, 2, 1, 3, 5, 6, 8, 6, 5, 3, 2],
    "Trio":  [1, 2, 3, 5, 3, 2, 1, 5, 1, 2, 3, 5, 8, 7, 6, 5],
    "Coda":  [3, 2, 1, 5, 3, 2, 1, 1],
}
SKELETON_FLAT = []
for s in SECTIONS:
    SKELETON_FLAT.extend(SKELETON[s])
assert len(SKELETON_FLAT) == 2 * N_BARS, (len(SKELETON_FLAT), 2 * N_BARS)

# Section start bar index (for reporting).
SECTION_BAR0 = []
acc = 0
for b in BARS:
    SECTION_BAR0.append(acc)
    acc += b


def degree_to_pitch(deg, octave=5):
    """Scale degree (1-indexed) -> diatonic MIDI pitch in C major."""
    d = deg - 1
    pc = SCALE_PCS[d % 7]
    octv = octave + d // 7
    return octv * 12 + pc


def chord_tones_in(register):
    """Map: chord-name -> sorted list of MIDI pitches in [register[0], register[1]]."""
    out = {}
    for name, pcs in CHORDS.items():
        tones = []
        for octv in range(1, 10):
            for pc in sorted(pcs):
                p = octv * 12 + pc
                if register[0] <= p <= register[1]:
                    tones.append(p)
        out[name] = sorted(set(tones))
    return out


def nearest_chord_tone(pitch, tones):
    return min(tones, key=lambda t: (abs(t - pitch), t))


# ---------------------------------------------------------------- PHASE 1
def generate_phase1_raw():
    composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS_PER_BAR)
    composer.create_matrix(num_voices=1, num_sections=N_SECTIONS)
    composer.add_voice("Raw_Melody", program=PIANO.midi_program, channel=0)

    skel = iter(SKELETON_FLAT)

    for s_idx, s_name in enumerate(SECTIONS):
        composer.add_section(s_name, bars=BARS[s_idx])
        sec_ticks = BARS[s_idx] * BAR_TICKS
        events = []
        curr = 47                       # off-grid initial micro-offset
        n_hb = BARS[s_idx] * 2          # half-bars in this section

        for _ in range(n_hb):
            deg = next(skel)
            raw = degree_to_pitch(deg, 5)
            folded = 60 + ((raw - 60) % 29)   # fold into ~2.4-octave window
            dur = int(rng.uniform(200, 430))
            end_t = min(curr + dur, sec_ticks - 50)
            events.append(MusicEvent(
                pitch=int(folded), volume=int(rng.integers(72, 96)),
                start_tick=curr, end_tick=end_t
            ))
            # nominal half-beat (480) + unquantized jitter -> off-grid onsets
            curr += 480 + int(rng.integers(-70, 70))

        events.append(MusicEvent(pitch=0, volume=0,
                                 start_tick=sec_ticks - 1, end_tick=sec_ticks))
        composer.fill_voice_section("Raw_Melody", s_name, MusicUnit(events=events))

    ok, msg = composer.validate()
    assert ok, f"Phase 1 validate failed: {msg}"

    p1_path = os.path.join(MIDI_DIR, "206-ragtime-skeleton-refinement-phase1.mid")
    composer.to_midi(p1_path)
    assert os.path.getsize(p1_path) > 40, "Phase 1 MIDI empty"
    print(f"Phase 1 MIDI: {p1_path} ({os.path.getsize(p1_path)} bytes)")

    write_provenance(
        p1_path, classification=AI_ASSISTED,
        generator="musicom.workflows.unitmatrix_composer",
        parameters={
            "project": "206-ragtime-skeleton-refinement",
            "phase": 1,
            "style": "Ragtime",
            "method": "001 Skeleton-First Refinement",
            "layer": "concrete",
            "skeleton": "scale-degree structural line (1 deg / half-bar)",
            "raw_timing": "unquantized (off-grid micro-timing)",
            "harmony": "none (raw structural line only)",
            "key": "C major",
            "bpm": BPM,
            "seed": SEED,
        })
    return p1_path


# ---------------------------------------------------------------- PHASE 2
def generate_phase2_composition():
    composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS_PER_BAR)
    composer.create_matrix(num_voices=3, num_sections=N_SECTIONS)

    composer.add_voice("Melody", program=PIANO.midi_program, channel=0)
    composer.add_voice("Bass", program=PIANO.midi_program, channel=1)
    composer.add_voice("Comp", program=PIANO.midi_program, channel=2)

    mel_tones = chord_tones_in((60, 90))    # melody register
    comp_tones = chord_tones_in((55, 76))   # comp register

    # Syncopation patterns: onset slots (16ths) within a half-bar (0..7).
    SYNC = [[0, 3, 6], [0, 2, 4, 6], [0, 3, 5, 7], [0, 4, 6]]
    sync_i = 0

    skel = iter(SKELETON_FLAT)

    for s_idx, s_name in enumerate(SECTIONS):
        composer.add_section(s_name, bars=BARS[s_idx])
        sec_ticks = BARS[s_idx] * BAR_TICKS
        mel_ev = []
        bass_ev = []
        comp_ev = []

        for bar_in_sec in range(BARS[s_idx]):
            bar_abs = SECTION_BAR0[s_idx] + bar_in_sec
            bar_start = bar_in_sec * BAR_TICKS
            chord_name = BAR_CHORD_NAMES[bar_abs]
            chord_pcs = BAR_CHORD_PCS[bar_abs]
            root_pc = BAR_ROOT_PC[bar_abs]
            m_tones = mel_tones[chord_name]
            c_tones = comp_tones[chord_name]

            # ---- Melody: two half-bar syncopated figures ----
            for hb in range(2):
                deg = next(skel)
                target = degree_to_pitch(deg, 5)
                t = nearest_chord_tone(target, m_tones)
                ti = m_tones.index(t)
                up = m_tones[min(len(m_tones) - 1, ti + 1)]
                dn = m_tones[max(0, ti - 1)]
                pat = SYNC[sync_i % len(SYNC)]
                sync_i += 1
                hb_start = bar_start + hb * (2 * TPB)   # 960 ticks
                onsets = [hb_start + slot * GRID16 for slot in pat]
                for k, on in enumerate(onsets):
                    pitch = [t, up, t, dn][k % 4]
                    end = onsets[k + 1] if k + 1 < len(onsets) else on + 120
                    vel = 100 if (k == 0 and hb == 0 and slot_of(pat, k) == 0) else (90 if k == 0 else 74)
                    mel_ev.append(MusicEvent(
                        pitch=pitch, volume=vel,
                        start_tick=on, end_tick=min(end, bar_start + BAR_TICKS)))

            # ---- Bass: stride root (beats 1 & 3) ----
            for slot, vel in ((0, 92), (8, 86)):
                on = bar_start + slot * GRID16
                root_pitch = 48 + root_pc          # octave 3 (C3=48)
                bass_ev.append(MusicEvent(
                    pitch=root_pitch, volume=vel,
                    start_tick=on, end_tick=on + 200))

            # ---- Comp: chord stab (beats 2 & 4), root-position close voicing ----
            for slot, vel in ((4, 74), (12, 70)):
                on = bar_start + slot * GRID16
                stab = c_tones[:3]                  # 3 lowest chord tones
                for p in stab:
                    comp_ev.append(MusicEvent(
                        pitch=p, volume=vel,
                        start_tick=on, end_tick=on + 180))

        def seal(ev_list):
            ev_list.sort(key=lambda e: (e.start_tick, e.end_tick))
            ev_list.append(MusicEvent(pitch=0, volume=0,
                                      start_tick=sec_ticks - 1, end_tick=sec_ticks))
            return MusicUnit(events=ev_list)

        composer.fill_voice_section("Melody", s_name, seal(mel_ev))
        composer.fill_voice_section("Bass", s_name, seal(bass_ev))
        composer.fill_voice_section("Comp", s_name, seal(comp_ev))

    ok, msg = composer.validate()
    assert ok, f"Phase 2 validate failed: {msg}"

    p2_path = os.path.join(MIDI_DIR, "206-ragtime-skeleton-refinement.mid")
    composer.to_midi(p2_path)
    assert os.path.getsize(p2_path) > 40, "Phase 2 MIDI empty"
    print(f"Phase 2 MIDI: {p2_path} ({os.path.getsize(p2_path)} bytes)")

    grid_path = os.path.join(ANALYSIS_DIR, "grid_visualization.txt")
    write_grid_visualization(
        composer.matrix, grid_path,
        ticks_per_character=240,
        voice_names=["Melody", "Bass", "Comp"],
        bpm=BPM)
    print(f"Grid visualization: {grid_path} ({os.path.getsize(grid_path)} bytes)")

    write_provenance(
        p2_path, classification=AI_ASSISTED,
        generator="musicom.workflows.unitmatrix_composer",
        parameters={
            "project": "206-ragtime-skeleton-refinement",
            "phase": 2,
            "style": "Ragtime",
            "method": "001 Skeleton-First Refinement",
            "layer": "concrete",
            "quantization": "16th grid (120 ticks) + chord-tone snap",
            "key": "C major",
            "form": "Intro|A|B|A2|Trio|Coda (40 bars)",
            "bpm": BPM,
            "seed": SEED,
        })
    return p2_path


def slot_of(pat, k):
    return pat[k]


if __name__ == "__main__":
    print("=== Phase 1: Raw Skeleton Draft ===")
    p1 = generate_phase1_raw()
    print("=== Phase 2: Rules Composition ===")
    p2 = generate_phase2_composition()
    print("Done!")
