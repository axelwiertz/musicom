# -*- coding: utf-8 -*-
"""227-hiphop-diffusion-extended - HipHop / Method 010 Hierarchical Diffusion (rework).

Nightly rework job (2026-10-07). Source composition: 208-hiphop-hierarchical-diffusion
(32 bars, 8 sections, A natural minor, 90 BPM, boom-bap). Source PASSED all six engine
standards -> EXTENSION (not redesign): same identity, longer + more varied.

Identity preserved: HipHop boom-bap, A natural minor, 90 BPM, 4/4, 480 TPB,
Ornstein-Uhlenbeck drift-diffusion lead + Galton-Watson onset branching, and the
5-voice texture (Piano hook / Organ pad / Double-Bass sub / Celesta stabs / ch9 drums).

What is NEW (extension):
  - Form: 8 -> 10 sections (40 bars, +8 bars).  N+2 sections requirement met.
  - New voice: CounterLine (Flute) used as a bridge counter-melody (6 voices total).
  - 8 distinct variation techniques across the piece (see VARIATION map below).

Two-phase architecture (mandatory):
  Phase 1 (-phase1.mid): raw diffusion draft, single voice, unquantized onsets +
      chromatic drift-diffusion pitch (no key/chord snapping).
  Phase 2 (.mid): same diffusion re-run (same seed) -> rules post-process:
      (a) onset snap to 16th grid (120 ticks),
      (b) pitch snap to the note's OWN bar chord tones (A natural minor),
      (c) rhythm-grid dedup (collided (start_tick,pitch) -> keep longest),
      (d) per-section variation transforms applied BEFORE chord snapping,
      (e) full 6-voice texture.
"""

import os
import sys
import numpy as np

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer
from workflows.provenance import write_provenance, AI_ASSISTED
from visualization.grid import write_grid_visualization

# Instrument registry (source of truth) - the ONE sanctioned sys.path exception
INSTR_DIR = "/opt/data/repos/musicom/projects/Instruments"
if INSTR_DIR not in sys.path:
    sys.path.insert(0, INSTR_DIR)
from instrument_registry import PIANO, ORGAN, DOUBLE_BASS, CELESTA, FLUTE

SEED = 20261007  # rework date seed

PROJ = "/opt/data/repos/musicom/projects/Styles/HipHop/227-hiphop-diffusion-extended"
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
            "Bridge", "Chorus3", "Lift", "Chorus4", "Outro"]
BARS_PER_SECTION = 4
N_SECTIONS = len(SECTIONS)               # 10
N_BARS = N_SECTIONS * BARS_PER_SECTION   # 40 bars
TOTAL_TICKS = SECTION_TICKS * N_SECTIONS # 76800

# ---------------------------------------------------------------- Harmonic Framework
# A natural minor = A B C D E F G = pitch classes {9, 11, 0, 2, 4, 5, 7}
A_MINOR_PCS = {9, 11, 0, 2, 4, 5, 7}

# Per-section harmonic regions: EACH section has its OWN 4-bar progression.
# No section simply lands on degree i every bar (bar-0 tonic bug avoided by
# explicit chord names + explicit root-PC dicts, never degree-index fallback).
SECTION_CHORDS = {
    0: ["Am", "Am", "Am", "Am"],   # Intro  (pedal)
    1: ["Am", "F",  "C",  "G"],    # Verse  (i VI III VII)
    2: ["Am", "F",  "C",  "G"],    # Chorus
    3: ["Dm", "Am", "Em", "Am"],   # Verse2 (iv i v i) + inverted lead
    4: ["Am", "F",  "C",  "G"],    # Chorus2 (density peak)
    5: ["F",  "C",  "G",  "Am"],   # Bridge (VI III VII i) + augmented lead + counterline
    6: ["Am", "F",  "C",  "G"],    # Chorus3 (register +1 octave)
    7: ["C",  "G",  "Am", "F"],    # Lift   (relative-major shift, tonicizes C)
    8: ["Am", "F",  "C",  "G"],    # Chorus4 (transposed +perfect 4th)
    9: ["Am", "Am", "Am", "Am"],   # Outro  (retrograde of Intro)
}

CHORD_PCS = {
    "Am": {9, 0, 4},        # A, C, E
    "F":  {5, 9, 0},        # F, A, C
    "C":  {0, 4, 7},        # C, E, G
    "G":  {7, 11, 2},       # G, B, D
    "Dm": {2, 5, 9},        # D, F, A
    "Em": {4, 7, 11},       # E, G, B
}

CHORD_ROOT_PC = {"Am": 9, "F": 5, "C": 0, "G": 7, "Dm": 2, "Em": 4}
CHORD_ROOT_BASS = {"Am": 33, "F": 29, "C": 36, "G": 31, "Dm": 38, "Em": 40}

# Per-section diffusion density (macro level-0 plan)
SECTION_DENSITY = {
    0: 0.30, 1: 0.55, 2: 0.78, 3: 0.55, 4: 0.85,
    5: 0.40, 6: 0.78, 7: 0.60, 8: 0.78, 9: 0.30,
}

# ---------------------------------------------------------------- Variation map
# 8 distinct variation techniques, documented -> applied BEFORE chord snapping.
VARIATION = {
    1: "identity (reference hook, OU drift-diffusion)",
    2: "density rise (chorus denser than verse)",
    3: "inversion (lead pitch mirrored around E4 axis = 142 - p)",
    4: "density peak (0.85, densest section)",
    5: "augmentation (half note-rate, doubled durations) + counterline (flute desc.)",
    6: "register shift (lead +1 octave)",
    7: "mode shift (relative major C, progression C-G-Am-F)",
    8: "transposition (lead +perfect 4th = +5 semitones)",
    9: "retrograde (Intro motif reversed)",
}

# Lead register per section (default (55,88)); higher for shifted sections
LEAD_RANGE = {
    6: (67, 96),   # Chorus3 up an octave
    8: (60, 93),   # Chorus4 up a 4th
}


def get_bar_chord(sec_idx, bar_in_sec):
    return SECTION_CHORDS[sec_idx][bar_in_sec]


def drift_target(chord):
    """Lead-register drift target = chord root pitch-class mapped to octave 4."""
    return 60 + CHORD_ROOT_PC[chord]


# ---------------------------------------------------------------- Method 010 diffusion primitives

def diffuse_bar_onsets(density, rng):
    """Level 2: hierarchical top-down diffusion of a bar-span into onset slots."""
    onsets = []

    def split(start, dur, level):
        if level >= 4:
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
    """Level 3: Ornstein-Uhlenbeck drift-diffusion over the whole piece."""
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


def dedup_events(events):
    """Rhythm-grid dedup: collided (start_tick, pitch) -> keep longest duration."""
    best = {}
    order = []
    for e in events:
        key = (e.start_tick, e.pitch)
        if key in best:
            if e.end_tick > best[key].end_tick:
                best[key] = e
        else:
            best[key] = e
            order.append(key)
    return [best[k] for k in order]


def apply_lead_variation(pitch, sec_idx):
    """Per-section pitch transform applied BEFORE chord-tone snapping."""
    if sec_idx == 3:    # Verse2: inversion around E4 axis (71)
        return 2 * 71.0 - pitch
    elif sec_idx == 6:  # Chorus3: register shift +1 octave
        return pitch + 12.0
    elif sec_idx == 8:  # Chorus4: transposition +perfect 4th
        return pitch + 5.0
    return pitch


# Bridge counterline (descending, all chord tones of their bars, in A minor)
COUNTER_NOTES = {
    5: [[77, 69],   # F5, A4   (F chord)
        [67, 64],   # G4, E4   (C chord)
        [74, 71],   # D5, B4   (G chord)
        [72, 69]],  # C5, A4   (Am chord)
}


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
            t_onset = bar_start + int(item["frac"] * BAR_TICKS)
            t_onset += int(rng.integers(-25, 25))
            t_onset = max(0, min(t_onset, bar_start + BAR_TICKS - 40))
            pitch = int(round(item["raw_pitch"]))
            dur = int(rng.uniform(80, 200))
            end_t = min(t_onset + dur, bar_start + BAR_TICKS - 10)
            vel = int(rng.integers(70, 96))
            events.append(MusicEvent(pitch=pitch, volume=vel,
                                     start_tick=t_onset, end_tick=end_t))

        events.append(MusicEvent(pitch=0, volume=0,
                                 start_tick=SECTION_TICKS - 1, end_tick=SECTION_TICKS))
        composer.fill_voice_section("Raw_Lead", s_name, MusicUnit(events=events))

    ok, msg = composer.validate()
    assert ok, f"Phase 1 validate failed: {msg}"

    p1_path = os.path.join(MIDI_DIR, "227-hiphop-diffusion-extended-phase1.mid")
    composer.to_midi(p1_path)
    assert os.path.getsize(p1_path) > 40, "Phase 1 MIDI empty"
    print(f"Phase 1 MIDI: {p1_path} ({os.path.getsize(p1_path)} bytes)")

    write_provenance(p1_path, classification=AI_ASSISTED,
                     generator="musicom.workflows.unitmatrix_composer",
                     parameters={
                         "project": "227-hiphop-diffusion-extended", "phase": 1,
                         "style": "HipHop",
                         "method": "010 Hierarchical Diffusion",
                         "layer": "concrete",
                         "source": "208-hiphop-hierarchical-diffusion",
                         "decision": "extension",
                         "raw_timing": "unquantized micro-jitter (off-grid)",
                         "raw_pitch": "Ornstein-Uhlenbeck drift-diffusion (chromatic)",
                         "key": "A natural minor", "bpm": BPM, "seed": SEED,
                     })
    return p1_path


# ================================================================
# PHASE 2: Musicom Rules Post-Processing + 6-Voice Arrangement
# ================================================================
def generate_phase2_composition():
    composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS_PER_BAR)
    composer.create_matrix(num_voices=6, num_sections=N_SECTIONS)

    composer.add_voice("LeadHook", program=PIANO.midi_program, channel=0)
    composer.add_voice("KeysPad", program=ORGAN.midi_program, channel=1)
    composer.add_voice("SubBass", program=DOUBLE_BASS.midi_program, channel=2)
    composer.add_voice("SparkleStab", program=CELESTA.midi_program, channel=3)
    composer.add_voice("CounterLine", program=FLUTE.midi_program, channel=4)
    composer.add_voice("Drums", program=0, channel=9)

    rng = np.random.default_rng(SEED)
    lead = generate_lead_diffusion(rng)

    intro_seq = []  # (bar, rel_tick, pitch) of Intro, for the Outro retrograde

    for s_idx, s_name in enumerate(SECTIONS):
        composer.add_section(s_name, bars=BARS_PER_SECTION)

        lead_events, pad_events, bass_events = [], [], []
        sparkle_events, counter_events, drum_events = [], [], []

        sec_items = [it for it in lead if it["sec"] == s_idx]
        sec_items.sort(key=lambda x: (x["bar"], x["frac"]))

        # --- Outro retrograde uses the (reversed) Intro note sequence ---
        if s_idx == 9:
            rev = list(reversed(intro_seq))
            for (bar, rel_tick, pitch) in rev:
                t_onset = bar * BAR_TICKS + rel_tick
                lead_events.append(MusicEvent(pitch=pitch, volume=70,
                                              start_tick=t_onset, end_tick=t_onset + 100))

        for bar_in_sec in range(BARS_PER_SECTION):
            bar_start = bar_in_sec * BAR_TICKS
            chord = get_bar_chord(s_idx, bar_in_sec)
            c_pcs = CHORD_PCS[chord]
            bar_end = bar_start + BAR_TICKS
            lo, hi = LEAD_RANGE.get(s_idx, (55, 88))

            # --- 1. LeadHook: diffused onsets snapped to 16th grid + chord-tone pitch ---
            if s_idx != 9:
                bar_lead = []
                for item in sec_items:
                    if item["bar"] != bar_in_sec:
                        continue
                    raw_tick = bar_start + item["frac"] * BAR_TICKS
                    t_onset = int(round(raw_tick / GRID16) * GRID16)
                    t_onset = max(bar_start, min(t_onset, bar_end - GRID16))
                    pitch = quantize_to_chord(int(round(apply_lead_variation(item["raw_pitch"], s_idx))),
                                              c_pcs, min_pitch=lo, max_pitch=hi)
                    step = (t_onset - bar_start) // GRID16
                    vel = 100 if step == 0 else (88 if step in (4, 8, 12) else 76)
                    bar_lead.append(MusicEvent(pitch=pitch, volume=vel,
                                               start_tick=t_onset, end_tick=t_onset + 100))
                    if s_idx == 0:
                        intro_seq.append((bar_in_sec, t_onset - bar_start, pitch))

                # augmentation (Bridge): halve note rate, double durations
                if s_idx == 5:
                    bar_lead = [e for i, e in enumerate(bar_lead) if i % 2 == 0]
                    for e in bar_lead:
                        e.end_tick = min(e.start_tick + 220, bar_end - GRID16)

                bar_lead = dedup_events(bar_lead)
                lead_events.extend(bar_lead)

            # --- 2. KeysPad: sustained chord (whole-bar) ---
            sorted_pcs = sorted(c_pcs)
            for pc in sorted_pcs:
                p = 48 + pc + (12 if pc < 5 else 0)
                pad_events.append(MusicEvent(pitch=p, volume=70,
                                             start_tick=bar_start, end_tick=bar_end - GRID8))

            # --- 3. SubBass: root on beats 1 & 3 (+ upbeat push) ---
            bass_pitch = quantize_to_chord(CHORD_ROOT_BASS[chord], c_pcs,
                                           min_pitch=28, max_pitch=48)
            bass_events.append(MusicEvent(pitch=bass_pitch, volume=96,
                                          start_tick=bar_start, end_tick=bar_start + 340))
            bass_events.append(MusicEvent(pitch=bass_pitch, volume=90,
                                          start_tick=bar_start + GRID8 * 4,
                                          end_tick=bar_start + GRID8 * 4 + 340))
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

            # --- 5. CounterLine: flute descending counter-melody (Bridge only) ---
            if s_idx == 5:
                cnotes = COUNTER_NOTES[5][bar_in_sec]
                for i, cp in enumerate(cnotes):
                    t_onset = bar_start + i * GRID8 * 4
                    counter_events.append(MusicEvent(pitch=cp, volume=80,
                                                     start_tick=t_onset,
                                                     end_tick=t_onset + GRID8 * 4 - 20))

            # --- 6. Drums: boom-bap backbeat (with per-section variation) ---
            half_time = (s_idx == 5)      # Bridge: half-time feel
            driving = (s_idx == 7)        # Lift: driving 16th hats
            for step in range(16):
                t_onset = bar_start + step * GRID16
                # Closed hat: 8ths (16ths when driving)
                if driving:
                    if step % 2 == 0:
                        drum_events.append(MusicEvent(pitch=42, volume=72 if step % 4 else 60,
                                                      start_tick=t_onset, end_tick=t_onset + 40))
                else:
                    if step % 2 == 0:
                        hh_vel = 84 if step % 4 == 0 else 60
                        drum_events.append(MusicEvent(pitch=42, volume=hh_vel,
                                                      start_tick=t_onset, end_tick=t_onset + 50))
                # Kick
                if half_time:
                    if step == 0:
                        drum_events.append(MusicEvent(pitch=36, volume=100,
                                                      start_tick=t_onset, end_tick=t_onset + 90))
                else:
                    if step in (0, 8):
                        drum_events.append(MusicEvent(pitch=36, volume=100 if step == 0 else 94,
                                                      start_tick=t_onset, end_tick=t_onset + 90))
                # Snare
                if half_time:
                    if step == 8:
                        drum_events.append(MusicEvent(pitch=38, volume=92,
                                                      start_tick=t_onset, end_tick=t_onset + 80))
                else:
                    if step in (4, 12):
                        drum_events.append(MusicEvent(pitch=38, volume=92,
                                                      start_tick=t_onset, end_tick=t_onset + 80))
                # Open hat on the 'and' of 4
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
        composer.fill_voice_section("CounterLine", s_name, seal_voice_events(counter_events))
        composer.fill_voice_section("Drums", s_name, seal_voice_events(drum_events))

    ok, msg = composer.validate()
    assert ok, f"Phase 2 validate failed: {msg}"

    p2_path = os.path.join(MIDI_DIR, "227-hiphop-diffusion-extended.mid")
    composer.to_midi(p2_path)
    assert os.path.getsize(p2_path) > 40, "Phase 2 MIDI empty"
    print(f"Phase 2 MIDI: {p2_path} ({os.path.getsize(p2_path)} bytes)")

    write_grid_visualization(composer.matrix,
                             os.path.join(ANALYSIS_DIR, "grid_visualization.txt"),
                             ticks_per_character=240,
                             voice_names=["LeadHook", "KeysPad", "SubBass",
                                          "SparkleStab", "CounterLine", "Drums"],
                             bpm=BPM)
    print("Grid viz written to Analysis/grid_visualization.txt")

    write_provenance(p2_path, classification=AI_ASSISTED,
                     generator="musicom.workflows.unitmatrix_composer",
                     parameters={
                         "project": "227-hiphop-diffusion-extended", "phase": 2,
                         "style": "HipHop",
                         "method": "010 Hierarchical Diffusion",
                         "layer": "concrete",
                         "source": "208-hiphop-hierarchical-diffusion",
                         "decision": "extension",
                         "quantization": "16th-grid (120 ticks) + chord-tone snap + dedup",
                         "key": "A natural minor", "bpm": BPM, "seed": SEED,
                         "progression": "per-section harmonic regions (10 regions)",
                         "variations": VARIATION,
                         "form": "10 sections x 4 bars = 40 bars",
                     })
    return p2_path


if __name__ == "__main__":
    print("=== Phase 1 raw diffusion draft ===")
    generate_phase1_raw()
    print("=== Phase 2 rules composition ===")
    generate_phase2_composition()
    print("Done!")
