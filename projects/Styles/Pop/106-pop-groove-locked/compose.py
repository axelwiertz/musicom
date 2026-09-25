# -*- coding: utf-8 -*-
"""106-pop-groove-locked - Pop style / Method 016 Groove-Locked Pattern Writing.

Autonomous composition job (date: 2026-09-25).
Style: Pop (catchy, verse/chorus, backbeat-driven)
Method: 016 Groove-Locked Pattern Writing (Rules-Based, Rhythm/Texture)
Layer: concrete

Method essence: a strict rhythmic groove anchor (a fixed 16th-note onset
pattern) LOCKs the whole piece; melodic pitch material is written ON TOP of
that repeating groove, never fighting it. The groove is the DNA, the pitches
ride it.

Two-phase architecture:
  Phase 1: Raw groove-locked walk - single voice (Lead). The 16th-note groove
           pattern dictates ONSETS, but pitches are a raw unquantized random
           walk (chromatic drift) with micro-timing jitter OFF the 120/240
           grid. No chord-tone quantization, no harmony. Exported as
           106-pop-groove-locked-phase1.mid.
  Phase 2: Musicom rules post-processing - strict 16th-grid quantization
           (120 ticks), diatonic C-major + per-bar chord-tone snapping to the
           I-V-vi-IV pop progression across 8 sections (32 bars), full pop
           texture:
             Voice 1: Lead Piano (PIANO, GM 1, ch 0)
             Voice 2: Rhythm Guitar (ACOUSTIC_GUITAR, GM 25, ch 1)
             Voice 3: Pop Bass (DOUBLE_BASS, GM 43, ch 2)
             Voice 4: Sparkle Arp (CELESTA, GM 8, ch 3)
             Voice 5: Drums (DRUM_KIT, ch 9)
           Zero-drift gate via UnitMatrixComposer.validate().
           Exported as 106-pop-groove-locked.mid.
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
from instrument_registry import PIANO, ACOUSTIC_GUITAR, DOUBLE_BASS, CELESTA

SEED = 20260925
rng = np.random.default_rng(SEED)

PROJ = "/opt/data/repos/musicom/projects/Styles/Pop/106-pop-groove-locked"
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
BAR_TICKS = TPB * BEATS_PER_BAR  # 1920

SECTIONS = ["Intro", "Verse", "PreChorus", "Chorus", "Verse2",
            "Chorus2", "Bridge", "Outro"]
BARS_PER_SECTION = 4
N_SECTIONS = len(SECTIONS)
N_BARS = N_SECTIONS * BARS_PER_SECTION  # 32 bars
SECTION_TICKS = BAR_TICKS * BARS_PER_SECTION  # 7680
TOTAL_TICKS = SECTION_TICKS * N_SECTIONS  # 61440

# ---------------------------------------------------------------- Harmonic Framework
# C major scale PCS
C_MAJOR_PCS = {0, 2, 4, 5, 7, 9, 11}

# Chord progression per section (4 bars each), classic I-V-vi-IV pop cycle
SECTION_CHORDS = {
    0: ["C", "G", "Am", "F"],   # Intro
    1: ["C", "G", "Am", "F"],   # Verse
    2: ["F", "G", "Am", "G"],   # PreChorus
    3: ["C", "G", "Am", "F"],   # Chorus
    4: ["C", "G", "Am", "F"],   # Verse2
    5: ["C", "G", "Am", "F"],   # Chorus2
    6: ["Am", "F", "C", "G"],   # Bridge
    7: ["C", "F", "C", "C"],    # Outro
}

CHORD_PCS = {
    "C":  {0, 4, 7},        # C, E, G
    "G":  {7, 11, 2},       # G, B, D
    "Am": {9, 0, 4},        # A, C, E
    "F":  {5, 9, 0},        # F, A, C
}


def get_bar_chord(sec_idx, bar_in_sec):
    return SECTION_CHORDS[sec_idx][bar_in_sec]


# ---------------------------------------------------------------- Method 016: Groove-Locked Pattern
# The groove anchor: a fixed 16th-note onset pattern (0-15 steps) that repeats
# every bar. This is the LOCK that the whole piece is written against.
# A syncopated pop groove with off-beat pushes and a strong downbeat.
GROOVE_LEAD = [0, 3, 4, 6, 8, 11, 12, 14]

# Bass groove (locks to kick: beats 1 and 3 + an upbeat push)
GROOVE_BASS = [0, 8, 14]

# Guitar strum groove (8th-note backbeat emphasis)
GROOVE_GUITAR = [0, 2, 4, 6, 8, 10, 12, 14]

print(f"Groove-locked lead onsets (16th steps): {GROOVE_LEAD}")
print(f"Groove-locked bass onsets (16th steps): {GROOVE_BASS}")


def quantize_to_chord(pitch, chord_pcs, target_octave=4, min_pitch=None, max_pitch=None):
    """Nearest pitch whose pitch-class is in chord_pcs, optionally bounded."""
    candidates = []
    for octv in range(target_octave - 3, target_octave + 4):
        for pc in chord_pcs:
            p = octv * 12 + pc
            if min_pitch is not None and p < min_pitch:
                continue
            if max_pitch is not None and p > max_pitch:
                continue
            candidates.append(p)
    if not candidates:
        for octv in range(target_octave - 2, target_octave + 3):
            for pc in chord_pcs:
                candidates.append(octv * 12 + pc)
    return min(candidates, key=lambda c: (abs(c - pitch), c))


# ================================================================
# PHASE 1: Raw Groove-Locked Draft (Single Voice, unquantized pitch)
# ================================================================
def generate_phase1_raw():
    composer_p1 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS_PER_BAR)
    composer_p1.create_matrix(num_voices=1, num_sections=N_SECTIONS)
    composer_p1.add_voice("Raw_Lead", program=PIANO.midi_program, channel=0)

    for s_idx, s_name in enumerate(SECTIONS):
        composer_p1.add_section(s_name, bars=BARS_PER_SECTION)
        events = []

        # Raw walk: onsets LOCKED to the groove, but pitch is an unquantized
        # random walk (chromatic), and onsets carry off-grid micro-jitter.
        raw_pitch = 67  # G4 start
        for bar_in_sec in range(BARS_PER_SECTION):
            bar_start = bar_in_sec * BAR_TICKS
            for step in GROOVE_LEAD:
                # Groove LOCK: onset is at step*GRID16, but add micro-jitter
                jitter = int(rng.integers(-20, 20))
                t_onset = bar_start + step * GRID16 + jitter
                t_onset = max(0, min(t_onset, bar_start + BAR_TICKS - 50))
                # Raw chromatic random walk (unquantized to key/chord)
                raw_pitch += int(rng.integers(-4, 5))
                raw_pitch = int(np.clip(raw_pitch, 55, 88))
                dur = int(rng.uniform(90, 220))
                end_t = min(t_onset + dur, bar_start + BAR_TICKS - 20)
                vel = int(rng.integers(70, 96))
                events.append(MusicEvent(
                    pitch=raw_pitch, volume=vel,
                    start_tick=t_onset, end_tick=end_t
                ))

        # Zero-drift terminal landmark
        events.append(MusicEvent(
            pitch=0, volume=0,
            start_tick=SECTION_TICKS - 1, end_tick=SECTION_TICKS
        ))
        unit = MusicUnit(events=events)
        composer_p1.fill_voice_section("Raw_Lead", s_name, unit)

    ok, msg = composer_p1.validate()
    assert ok, f"Phase 1 validate failed: {msg}"

    p1_path = os.path.join(MIDI_DIR, "106-pop-groove-locked-phase1.mid")
    composer_p1.to_midi(p1_path)
    assert os.path.getsize(p1_path) > 40, "Phase 1 MIDI empty"
    print(f"Phase 1 MIDI: {p1_path} ({os.path.getsize(p1_path)} bytes)")

    write_provenance(
        p1_path, classification=AI_ASSISTED,
        generator="musicom.workflows.unitmatrix_composer",
        parameters={
            "project": "106-pop-groove-locked", "phase": 1,
            "style": "Pop", "method": "016 Groove-Locked Pattern Writing",
            "layer": "concrete", "raw_timing": "unquantized micro-jitter",
            "raw_pitch": "chromatic random walk", "seed": SEED,
        })
    return p1_path


# ================================================================
# PHASE 2: Musicom Rules Post-Processing & Multi-Voice Arrangement
# ================================================================
def generate_phase2_composition():
    composer_p2 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS_PER_BAR)
    composer_p2.create_matrix(num_voices=5, num_sections=N_SECTIONS)

    composer_p2.add_voice("LeadPiano", program=PIANO.midi_program, channel=0)
    composer_p2.add_voice("RhythmGuitar", program=ACOUSTIC_GUITAR.midi_program, channel=1)
    composer_p2.add_voice("PopBass", program=DOUBLE_BASS.midi_program, channel=2)
    composer_p2.add_voice("SparkleArp", program=CELESTA.midi_program, channel=3)
    composer_p2.add_voice("Drums", program=0, channel=9)

    # Melodic hook (interval contour) mapped onto the groove lock
    HOOK = [0, 4, 7, 12, 9, 7, 4, 2]  # chord-tone pop hook shape

    for s_idx, s_name in enumerate(SECTIONS):
        composer_p2.add_section(s_name, bars=BARS_PER_SECTION)

        lead_events, guitar_events, bass_events, arp_events, drum_events = [], [], [], [], []

        for bar_in_sec in range(BARS_PER_SECTION):
            bar_start = bar_in_sec * BAR_TICKS
            chord_name = get_bar_chord(s_idx, bar_in_sec)
            c_pcs = CHORD_PCS[chord_name]
            bar_end = bar_start + BAR_TICKS

            # --- 1. Lead Piano: groove-locked, chord-quantized hook ---
            for gi, step in enumerate(GROOVE_LEAD):
                t_onset = bar_start + step * GRID16
                # Hook pitch relative to chord root, cycled
                hook_interval = HOOK[gi % len(HOOK)]
                root_pitch = 60  # C4 reference
                raw = root_pitch + hook_interval
                # Push lead register up for chorus
                if s_name in ("Chorus", "Chorus2"):
                    raw += 12
                lead_pitch = quantize_to_chord(raw, c_pcs, target_octave=5,
                                               min_pitch=60, max_pitch=88)
                dur = 100
                vel = 100 if step == 0 else (88 if step in (4, 8, 12) else 78)
                lead_events.append(MusicEvent(
                    pitch=lead_pitch, volume=vel,
                    start_tick=t_onset, end_tick=t_onset + dur
                ))

            # --- 2. Rhythm Guitar: 8th-note backbeat strum ---
            for step in GROOVE_GUITAR:
                t_onset = bar_start + step * GRID16
                sorted_pcs = sorted(c_pcs)
                if step % 2 == 0:
                    # downbeat strum: fuller voicing
                    for i, pc in enumerate(sorted_pcs):
                        p = 48 + pc + (12 if pc < 5 else 0)
                        guitar_events.append(MusicEvent(
                            pitch=p, volume=int(78 if i == 0 else 70),
                            start_tick=t_onset, end_tick=t_onset + 170
                        ))
                else:
                    # upstroke: single tone
                    p = quantize_to_chord(55, c_pcs, target_octave=4)
                    guitar_events.append(MusicEvent(
                        pitch=p, volume=66, start_tick=t_onset, end_tick=t_onset + 110
                    ))

            # --- 3. Pop Bass: groove-locked root/fifth ---
            for gi, step in enumerate(GROOVE_BASS):
                t_onset = bar_start + step * GRID16
                if gi == 0:
                    b_pitch = quantize_to_chord(36, c_pcs, target_octave=2,
                                                min_pitch=28, max_pitch=48)
                    dur, vel = 340, 96
                elif gi == 1:
                    b_pitch = quantize_to_chord(43, c_pcs, target_octave=3,
                                                min_pitch=28, max_pitch=55)
                    dur, vel = 340, 88
                else:
                    b_pitch = quantize_to_chord(41, c_pcs, target_octave=3,
                                                min_pitch=28, max_pitch=55)
                    dur, vel = 180, 80
                bass_events.append(MusicEvent(
                    pitch=b_pitch, volume=vel,
                    start_tick=t_onset, end_tick=t_onset + dur
                ))

            # --- 4. Sparkle Arp (Celesta): 16th-note chord arpeggio ---
            for step in (0, 4, 8, 12, 6, 14):
                t_onset = bar_start + step * GRID16
                arp_pc = sorted(c_pcs)[(step // 2) % 3]
                arp_pitch = 72 + arp_pc + (12 if arp_pc < 5 else 0)
                arp_events.append(MusicEvent(
                    pitch=arp_pitch, volume=74,
                    start_tick=t_onset, end_tick=t_onset + 90
                ))

            # --- 5. Drums: pop backbeat ---
            for step in range(16):
                t_onset = bar_start + step * GRID16
                # Hi-hat 8ths
                if step % 2 == 0:
                    hh_vel = 82 if step % 4 == 0 else 62
                    drum_events.append(MusicEvent(
                        pitch=42, volume=hh_vel,
                        start_tick=t_onset, end_tick=t_onset + 50
                    ))
                # Kick beats 1 and 3
                if step in (0, 8):
                    drum_events.append(MusicEvent(
                        pitch=36, volume=100 if step == 0 else 92,
                        start_tick=t_onset, end_tick=t_onset + 90
                    ))
                # Snare beats 2 and 4
                if step in (4, 12):
                    drum_events.append(MusicEvent(
                        pitch=38, volume=90,
                        start_tick=t_onset, end_tick=t_onset + 80
                    ))
                # Open hat on the 'and' of 4
                if step == 14:
                    drum_events.append(MusicEvent(
                        pitch=46, volume=70,
                        start_tick=t_onset, end_tick=t_onset + 70
                    ))

        def seal_voice_events(ev_list):
            ev_list.sort(key=lambda e: (e.start_tick, e.end_tick))
            ev_list.append(MusicEvent(
                pitch=0, volume=0,
                start_tick=SECTION_TICKS - 1, end_tick=SECTION_TICKS
            ))
            return MusicUnit(events=ev_list)

        composer_p2.fill_voice_section("LeadPiano", s_name, seal_voice_events(lead_events))
        composer_p2.fill_voice_section("RhythmGuitar", s_name, seal_voice_events(guitar_events))
        composer_p2.fill_voice_section("PopBass", s_name, seal_voice_events(bass_events))
        composer_p2.fill_voice_section("SparkleArp", s_name, seal_voice_events(arp_events))
        composer_p2.fill_voice_section("Drums", s_name, seal_voice_events(drum_events))

    ok, msg = composer_p2.validate()
    assert ok, f"Phase 2 validate failed: {msg}"

    p2_path = os.path.join(MIDI_DIR, "106-pop-groove-locked.mid")
    composer_p2.to_midi(p2_path)
    assert os.path.getsize(p2_path) > 40, "Phase 2 MIDI empty"
    print(f"Phase 2 MIDI: {p2_path} ({os.path.getsize(p2_path)} bytes)")

    write_grid_visualization(
        composer_p2.matrix,
        os.path.join(ANALYSIS_DIR, "grid_visualization.txt"),
        ticks_per_character=240,
        voice_names=["LeadPiano", "RhythmGuitar", "PopBass", "SparkleArp", "Drums"],
        bpm=BPM)
    print(f"Grid viz written to Analysis/grid_visualization.txt")

    write_provenance(
        p2_path, classification=AI_ASSISTED,
        generator="musicom.workflows.unitmatrix_composer",
        parameters={
            "project": "106-pop-groove-locked", "phase": 2,
            "style": "Pop", "method": "016 Groove-Locked Pattern Writing",
            "layer": "concrete", "quantization": "16th-grid (120 ticks)",
            "key": "C Major", "bpm": BPM, "seed": SEED,
            "progression": "I-V-vi-IV",
        })
    return p2_path


if __name__ == "__main__":
    print("=== Phase 1 raw draft ===")
    generate_phase1_raw()
    print("=== Phase 2 rules composition ===")
    generate_phase2_composition()
    print("Done!")
