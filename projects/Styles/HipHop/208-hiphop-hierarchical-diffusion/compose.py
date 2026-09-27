# -*- coding: utf-8 -*-
"""208-hiphop-hierarchical-diffusion - HipHop style / Method 010 Hierarchical Diffusion.

Autonomous composition job (date: 2026-09-27).
Style: HipHop (boom-bap backbeat, sub bass, chord stabs, swung 16ths)
Method: 010 Hierarchical Diffusion (Stochastic, Structure/Texture)
Layer: concrete

Method essence: multi-level top-down step-wise expansion from macro plans to
MIDI events. A macro form plan (section densities) is diffused down the
hierarchy:
  Level 0 (macro form): 8 sections, each with a density target + harmonic region.
  Level 1 (section -> bars): each 4-bar section expands to 4 bars, each bar a chord.
  Level 2 (bar -> onset slots): recursive binary split (Galton-Watson branching)
       of the bar-span into onset positions - top-down diffusion.
  Level 3 (onset -> pitch): Ornstein-Uhlenbeck drift-diffusion - a pitch random
       walk with a restoring drift toward the current chord root (diffusion +
       drift = the stochastic "spread" of material).

Two-phase architecture:
  Phase 1: Raw diffusion draft - single voice (Raw_Lead). Onsets carry
           micro-jitter OFF the 16th grid; pitch is a raw unquantized
           chromatic drift-diffusion walk. No harmony, no chord-tone
           quantization. Exported as 208-hiphop-hierarchical-diffusion-phase1.mid.
  Phase 2: Musicom rules post-processing - the SAME diffusion (same seed) is
           re-run and then:
             (a) every onset snapped to the 16th grid (120 ticks),
             (b) every pitch snapped to its bar's chord tones (A natural minor),
           and a full 5-voice hip-hop texture is added:
             Voice 1: LeadHook  (PIANO, GM 1, ch 0)   - diffused chord-tone hook
             Voice 2: KeysPad   (ORGAN, GM 19, ch 1)  - sustained chord pad
             Voice 3: SubBass   (DOUBLE_BASS, GM 43, ch 2) - deep root bass
             Voice 4: SparkleStab (CELESTA, GM 8, ch 3) - high chord stabs
             Voice 5: Drums     (ch 9)                - boom-bap backbeat
           Zero-drift gate via UnitMatrixComposer.validate().
           Exported as 208-hiphop-hierarchical-diffusion.mid.
"""

import os
import sys
import numpy as np

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer
from workflows.provenance import write_provenance, AI_ASSISTED
from visualization.grid import write_grid_visualization

# Instrument registry (source of truth)
INSTR_DIR = "/opt/data/repos/musicom/projects/Instruments"
if INSTR_DIR not in sys.path:
    sys.path.insert(0, INSTR_DIR)
from instrument_registry import PIANO, ORGAN, DOUBLE_BASS, CELESTA

SEED = 20260927

PROJ = "/opt/data/repos/musicom/projects/Styles/HipHop/208-hiphop-hierarchical-diffusion"
MIDI_DIR = os.path.join(PROJ, "MIDI")
AUDIO_DIR = os.path.join(PROJ, "Audio")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")
for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
    os.makedirs(d, exist_ok=True)

# ---------------------------------------------------------------- Grid & Timing
BPM = 90
TPB = 480
BEATS_PER_BAR = 4
GRID16 = 120
GRID8 = 240
BAR_TICKS = TPB * BEATS_PER_BAR          # 1920
SECTION_TICKS = BAR_TICKS * 4            # 7680

SECTIONS = ["Intro", "Verse", "Chorus", "Verse2", "Chorus2",
            "Bridge", "Chorus3", "Outro"]
BARS_PER_SECTION = 4
N_SECTIONS = len(SECTIONS)
N_BARS = N_SECTIONS * BARS_PER_SECTION   # 32 bars
TOTAL_TICKS = SECTION_TICKS * N_SECTIONS  # 61440

# ---------------------------------------------------------------- Harmonic Framework
# A natural minor = A B C D E F G = pitch classes {9, 11, 0, 2, 4, 5, 7}
A_MINOR_PCS = {9, 11, 0, 2, 4, 5, 7}

# Chord progression per section (4 bars each): i - VI - III - VII (+ iv for color)
SECTION_CHORDS = {
    0: ["Am", "Am", "Am", "Am"],   # Intro  (sparse)
    1: ["Am", "F",  "C",  "G"],    # Verse  (i VI III VII)
    2: ["Am", "F",  "C",  "G"],    # Chorus
    3: ["Am", "F",  "C",  "G"],    # Verse2
    4: ["Am", "F",  "C",  "G"],    # Chorus2
    5: ["F",  "C",  "G",  "Am"],   # Bridge (VI III VII i - darker turn)
    6: ["Am", "F",  "C",  "G"],    # Chorus3
    7: ["Am", "Am", "Am", "Am"],   # Outro  (sparse)
}

CHORD_PCS = {
    "Am": {9, 0, 4},        # A, C, E
    "F":  {5, 9, 0},        # F, A, C
    "C":  {0, 4, 7},        # C, E, G
    "G":  {7, 11, 2},       # G, B, D
}

# Chord root pitch-class (for drift-diffusion target) + bass register root
CHORD_ROOT_PC = {"Am": 9, "F": 5, "C": 0, "G": 7}
CHORD_ROOT_BASS = {"Am": 33, "F": 29, "C": 36, "G": 31}  # A1, F1, C2, G1

# Per-section diffusion density (macro level-0 plan): drives onset branching
SECTION_DENSITY = {
    0: 0.35,   # Intro sparse
    1: 0.55,   # Verse
    2: 0.78,   # Chorus (densest)
    3: 0.55,   # Verse2
    4: 0.82,   # Chorus2
    5: 0.48,   # Bridge
    6: 0.78,   # Chorus3
    7: 0.30,   # Outro
}


def get_bar_chord(sec_idx, bar_in_sec):
    return SECTION_CHORDS[sec_idx][bar_in_sec]


def drift_target(chord):
    """Lead-register drift target = chord root pitch-class mapped to octave 4."""
    return 60 + CHORD_ROOT_PC[chord]


# ---------------------------------------------------------------- Method 010 diffusion primitives

def diffuse_bar_onsets(density, rng):
    """Level 2: hierarchical top-down diffusion of a bar-span into onset slots.

    Recursive binary split (Galton-Watson branching): a token splits into two
    children with probability p = density * 0.9^level, else it becomes a leaf
    onset at a jittered position inside its span. Deeper levels -> fewer splits.
    Returns fractional bar positions in [0,1) (unquantized).
    """
    onsets = []

    def split(start, dur, level):
        if level >= 4:  # down to 16th-note depth
            onsets.append(start + dur * rng.uniform(0.3, 0.7))
            return
        p = density * (0.9 ** level)
        if rng.random() < p:
            split(start, dur / 2.0, level + 1)
            split(start + dur / 2.0, dur / 2.0, level + 1)
        else:
            onsets.append(start + dur * rng.uniform(0.3, 0.7))

    split(0.0, 1.0, 0)
    return onsets


def generate_lead_diffusion(rng):
    """Run the full hierarchical-diffusion lead generation over the whole piece.

    Level 3 pitch: Ornstein-Uhlenbeck drift-diffusion - pitch random walk with
    a restoring drift toward the current chord root. Returns a list of dicts
    {sec, bar, frac (onset position 0..1 within bar), raw_pitch (float)}.
    Deterministic given the seed.
    """
    out = []
    raw_pitch = None
    for s_idx in range(N_SECTIONS):
        density = SECTION_DENSITY[s_idx]
        for bar in range(BARS_PER_SECTION):
            chord = get_bar_chord(s_idx, bar)
            target = drift_target(chord)
            fracs = diffuse_bar_onsets(density, rng)
            fracs.sort()
            for frac in fracs:
                if raw_pitch is None:
                    raw_pitch = float(target)
                # Ornstein-Uhlenbeck step: restoring drift + diffusion noise
                raw_pitch += 0.30 * (target - raw_pitch) + float(rng.normal(0.0, 2.5))
                raw_pitch = float(np.clip(raw_pitch, 50.0, 90.0))
                out.append({"sec": s_idx, "bar": bar,
                            "frac": frac, "raw_pitch": raw_pitch})
    return out


def quantize_to_chord(pitch, chord_pcs, min_pitch=None, max_pitch=None):
    """Nearest pitch whose pitch-class is in chord_pcs, bounded to [min,max]."""
    candidates = []
    for octv in range(2, 8):
        for pc in chord_pcs:
            p = octv * 12 + pc
            if min_pitch is not None and p < min_pitch:
                continue
            if max_pitch is not None and p > max_pitch:
                continue
            candidates.append(p)
    if not candidates:
        for octv in range(2, 8):
            for pc in chord_pcs:
                candidates.append(octv * 12 + pc)
    return min(candidates, key=lambda c: (abs(c - pitch), c))


# ================================================================
# PHASE 1: Raw Hierarchical-Diffusion Draft (single voice)
# ================================================================
def generate_phase1_raw():
    composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS_PER_BAR)
    composer.create_matrix(num_voices=1, num_sections=N_SECTIONS)
    composer.add_voice("Raw_Lead", program=PIANO.midi_program, channel=0)

    rng = np.random.default_rng(SEED)
    lead = generate_lead_diffusion(rng)

    for s_idx, s_name in enumerate(SECTIONS):
        composer.add_section(s_name, bars=BARS_PER_SECTION)
        events = []
        for item in lead:
            if item["sec"] != s_idx:
                continue
            bar_start = item["bar"] * BAR_TICKS
            # RAW onset: unquantized (jitter OFF the 120/240 grid)
            t_onset = bar_start + int(item["frac"] * BAR_TICKS)
            t_onset += int(rng.integers(-25, 25))
            t_onset = max(0, min(t_onset, bar_start + BAR_TICKS - 40))
            # RAW pitch: unquantized chromatic drift-diffusion (no chord snapping)
            pitch = int(round(item["raw_pitch"]))
            dur = int(rng.uniform(80, 200))
            end_t = min(t_onset + dur, bar_start + BAR_TICKS - 10)
            vel = int(rng.integers(70, 96))
            events.append(MusicEvent(pitch=pitch, volume=vel,
                                     start_tick=t_onset, end_tick=end_t))

        # Zero-drift terminal landmark
        events.append(MusicEvent(pitch=0, volume=0,
                                 start_tick=SECTION_TICKS - 1, end_tick=SECTION_TICKS))
        composer.fill_voice_section("Raw_Lead", s_name, MusicUnit(events=events))

    ok, msg = composer.validate()
    assert ok, f"Phase 1 validate failed: {msg}"

    p1_path = os.path.join(MIDI_DIR, "208-hiphop-hierarchical-diffusion-phase1.mid")
    composer.to_midi(p1_path)
    assert os.path.getsize(p1_path) > 40, "Phase 1 MIDI empty"
    print(f"Phase 1 MIDI: {p1_path} ({os.path.getsize(p1_path)} bytes)")

    write_provenance(p1_path, classification=AI_ASSISTED,
                     generator="musicom.workflows.unitmatrix_composer",
                     parameters={
                         "project": "208-hiphop-hierarchical-diffusion", "phase": 1,
                         "style": "HipHop",
                         "method": "010 Hierarchical Diffusion",
                         "layer": "concrete",
                         "raw_timing": "unquantized micro-jitter (off-grid)",
                         "raw_pitch": "Ornstein-Uhlenbeck drift-diffusion (chromatic)",
                         "key": "A natural minor", "bpm": BPM, "seed": SEED,
                     })
    return p1_path


# ================================================================
# PHASE 2: Musicom Rules Post-Processing + Multi-Voice Arrangement
# ================================================================
def generate_phase2_composition():
    composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS_PER_BAR)
    composer.create_matrix(num_voices=5, num_sections=N_SECTIONS)

    composer.add_voice("LeadHook", program=PIANO.midi_program, channel=0)
    composer.add_voice("KeysPad", program=ORGAN.midi_program, channel=1)
    composer.add_voice("SubBass", program=DOUBLE_BASS.midi_program, channel=2)
    composer.add_voice("SparkleStab", program=CELESTA.midi_program, channel=3)
    composer.add_voice("Drums", program=0, channel=9)

    # Same diffusion (same seed) -> identical raw material, then rules-quantized
    rng = np.random.default_rng(SEED)
    lead = generate_lead_diffusion(rng)

    for s_idx, s_name in enumerate(SECTIONS):
        composer.add_section(s_name, bars=BARS_PER_SECTION)

        lead_events, pad_events, bass_events, sparkle_events, drum_events = [], [], [], [], []

        for bar_in_sec in range(BARS_PER_SECTION):
            bar_start = bar_in_sec * BAR_TICKS
            chord = get_bar_chord(s_idx, bar_in_sec)
            c_pcs = CHORD_PCS[chord]
            bar_end = bar_start + BAR_TICKS

            # --- 1. LeadHook: diffused onsets snapped to 16th grid + chord-tone pitch ---
            for item in lead:
                if item["sec"] != s_idx or item["bar"] != bar_in_sec:
                    continue
                raw_tick = bar_start + item["frac"] * BAR_TICKS
                t_onset = int(round(raw_tick / GRID16) * GRID16)
                t_onset = max(bar_start, min(t_onset, bar_end - GRID16))
                lead_pitch = quantize_to_chord(int(round(item["raw_pitch"])),
                                               c_pcs, min_pitch=55, max_pitch=88)
                dur = 100
                step = (t_onset - bar_start) // GRID16
                vel = 100 if step == 0 else (88 if step in (4, 8, 12) else 76)
                lead_events.append(MusicEvent(pitch=lead_pitch, volume=vel,
                                              start_tick=t_onset, end_tick=t_onset + dur))

            # --- 2. KeysPad: sustained chord (whole-bar) ---
            sorted_pcs = sorted(c_pcs)
            for i, pc in enumerate(sorted_pcs):
                p = 48 + pc + (12 if pc < 5 else 0)   # octave 3-4 voicing
                pad_events.append(MusicEvent(pitch=p, volume=70,
                                             start_tick=bar_start, end_tick=bar_end - GRID8))

            # --- 3. SubBass: root on beats 1 & 3 (+ upbeat push) ---
            root_low = CHORD_ROOT_BASS[chord]
            bass_pitch = quantize_to_chord(root_low, c_pcs, min_pitch=28, max_pitch=48)
            bass_events.append(MusicEvent(pitch=bass_pitch, volume=96,
                                          start_tick=bar_start, end_tick=bar_start + 340))
            bass_events.append(MusicEvent(pitch=bass_pitch, volume=90,
                                          start_tick=bar_start + GRID8 * 4,
                                          end_tick=bar_start + GRID8 * 4 + 340))
            # upbeat push on the 'and' of 4
            bass_events.append(MusicEvent(pitch=bass_pitch, volume=78,
                                          start_tick=bar_start + GRID8 * 7,
                                          end_tick=bar_start + GRID8 * 7 + 160))

            # --- 4. SparkleStab: high chord stabs on off-beats ---
            for step in (6, 14):
                t_onset = bar_start + step * GRID16
                pc = sorted_pcs[(step // 2) % len(sorted_pcs)]
                sp_pitch = 72 + pc + (12 if pc < 5 else 0)
                sparkle_events.append(MusicEvent(pitch=sp_pitch, volume=74,
                                                 start_tick=t_onset, end_tick=t_onset + 90))

            # --- 5. Drums: boom-bap backbeat ---
            for step in range(16):
                t_onset = bar_start + step * GRID16
                # Closed hat: 8ths (accent on the beat)
                if step % 2 == 0:
                    hh_vel = 84 if step % 4 == 0 else 60
                    drum_events.append(MusicEvent(pitch=42, volume=hh_vel,
                                                  start_tick=t_onset, end_tick=t_onset + 50))
                # Kick: beats 1 and 3
                if step in (0, 8):
                    drum_events.append(MusicEvent(pitch=36, volume=100 if step == 0 else 94,
                                                  start_tick=t_onset, end_tick=t_onset + 90))
                # Snare: beats 2 and 4 (backbeat)
                if step in (4, 12):
                    drum_events.append(MusicEvent(pitch=38, volume=92,
                                                  start_tick=t_onset, end_tick=t_onset + 80))
                # Open hat: on the 'and' of 4
                if step == 14:
                    drum_events.append(MusicEvent(pitch=46, volume=70,
                                                  start_tick=t_onset, end_tick=t_onset + 70))

        def seal_voice_events(ev_list):
            ev_list.sort(key=lambda e: (e.start_tick, e.end_tick))
            ev_list.append(MusicEvent(pitch=0, volume=0,
                                      start_tick=SECTION_TICKS - 1, end_tick=SECTION_TICKS))
            return MusicUnit(events=ev_list)

        composer.fill_voice_section("LeadHook", s_name, seal_voice_events(lead_events))
        composer.fill_voice_section("KeysPad", s_name, seal_voice_events(pad_events))
        composer.fill_voice_section("SubBass", s_name, seal_voice_events(bass_events))
        composer.fill_voice_section("SparkleStab", s_name, seal_voice_events(sparkle_events))
        composer.fill_voice_section("Drums", s_name, seal_voice_events(drum_events))

    ok, msg = composer.validate()
    assert ok, f"Phase 2 validate failed: {msg}"

    p2_path = os.path.join(MIDI_DIR, "208-hiphop-hierarchical-diffusion.mid")
    composer.to_midi(p2_path)
    assert os.path.getsize(p2_path) > 40, "Phase 2 MIDI empty"
    print(f"Phase 2 MIDI: {p2_path} ({os.path.getsize(p2_path)} bytes)")

    write_grid_visualization(composer.matrix,
                             os.path.join(ANALYSIS_DIR, "grid_visualization.txt"),
                             ticks_per_character=240,
                             voice_names=["LeadHook", "KeysPad", "SubBass", "SparkleStab", "Drums"],
                             bpm=BPM)
    print("Grid viz written to Analysis/grid_visualization.txt")

    write_provenance(p2_path, classification=AI_ASSISTED,
                     generator="musicom.workflows.unitmatrix_composer",
                     parameters={
                         "project": "208-hiphop-hierarchical-diffusion", "phase": 2,
                         "style": "HipHop",
                         "method": "010 Hierarchical Diffusion",
                         "layer": "concrete",
                         "quantization": "16th-grid (120 ticks) + chord-tone snap",
                         "key": "A natural minor", "bpm": BPM, "seed": SEED,
                         "progression": "i-VI-III-VII (Am-F-C-G)",
                     })
    return p2_path


if __name__ == "__main__":
    print("=== Phase 1 raw diffusion draft ===")
    generate_phase1_raw()
    print("=== Phase 2 rules composition ===")
    generate_phase2_composition()
    print("Done!")
