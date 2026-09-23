# -*- coding: utf-8 -*-
"""103-japanese-kojo-koto - Japanese style / Method 019 L-System Algorithmic Composition.

Autonomous nightly composition job (date: 2026-09-23).
Style: Japanese (koto + shakuhachi + shamisen + taiko, Jo-Ha-Kyu form)
Method: 019 L-System Algorithmic Composition (dragon-curve / paperfolding grammar)
Layer: concrete

Two-phase architecture:
  Phase 1: Raw generative draft - single voice (Koto) driven by the L-system
           dragon-curve interval fractal. Unquantized micro-rhythm, no scale or
           chord snapping (whole-tone stepwise contour preserved), exported as
           <project>-phase1.mid with its own zero-drift gate.
  Phase 2: Musicom rules post-processing - strict 16th/8th grid quantization,
           diatonic A-hirajoshi pentatonic + bar-by-bar palette (chord-tone)
           snapping, voice-leading-safe arrangement across 5 voices, exported
           as <project>.mid.

Key: A hirajoshi pentatonic (A Bb D E G) = pitch classes {9, 10, 2, 4, 7}.
Form: Jo | Ha1 | Ha2 | Kyu1 | Kyu2 | Jo_Coda  (6 sections x 4 bars = 24 bars)
BPM 80, 4/4, 480 TPB.
"""

import os
import sys
import json
import numpy as np

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer
from workflows.provenance import write_provenance, AI_ASSISTED
from visualization.grid import write_grid_visualization
from generators.interval_lsystem import IntervalLSystem

# Instrument registry (source of truth)
INSTR_DIR = "/opt/data/repos/musicom/projects/Instruments"
if INSTR_DIR not in sys.path:
    sys.path.insert(0, INSTR_DIR)
from instrument_registry import KOTO, FLUTE, SHAMISEN

SEED = 20260923
rng = np.random.default_rng(SEED)

PROJ = "/opt/data/repos/musicom/projects/Styles/Japanese/103-japanese-kojo-koto"
MIDI_DIR = os.path.join(PROJ, "MIDI")
AUDIO_DIR = os.path.join(PROJ, "Audio")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")
for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
    os.makedirs(d, exist_ok=True)

# ---------------------------------------------------------------- Grid & Timing
BPM = 80
TPB = 480
BEATS_PER_BAR = 4
GRID16 = 120
GRID8 = 240
BAR_TICKS = TPB * BEATS_PER_BAR       # 1920
SECTIONS = ["Jo", "Ha1", "Ha2", "Kyu1", "Kyu2", "Jo_Coda"]
BARS_PER_SECTION = 4
N_SECTIONS = len(SECTIONS)
N_BARS = N_SECTIONS * BARS_PER_SECTION  # 24
SECTION_TICKS = BAR_TICKS * BARS_PER_SECTION  # 7680
TOTAL_TICKS = SECTION_TICKS * N_SECTIONS      # 46080

# ---------------------------------------------------------------- Harmonic Framework
# A hirajoshi pentatonic: A(9), Bb(10), D(2), E(4), G(7)
SCALE_PCS = {9, 10, 2, 4, 7}

# Pentatonic "palettes" (4-note subsets of the scale, one per bar).
# Each palette drops one scale tone -> the dropped tone is the out-of-chord note,
# giving the harmony audit real teeth while staying fully diatonic.
PALETTES = {
    "A":  {9, 10, 2, 4},   # A  Bb D  E   (drop G)
    "G":  {9, 10, 2, 7},   # A  Bb D  G   (drop E)
    "Bb": {10, 2, 4, 7},   # Bb D  E  G   (drop A)
    "E":  {9, 10, 4, 7},   # A  Bb E  G   (drop D)
}

# Progression per section (4 bars each), Jo-Ha-Kyu arc:
SECTION_PALETTES = {
    0: ["A", "A", "G", "A"],      # Jo      - sparse tonic meditation
    1: ["A", "G", "Bb", "A"],     # Ha1     - opening out
    2: ["Bb", "G", "E", "Bb"],    # Ha2     - developing tension
    3: ["E", "Bb", "A", "E"],     # Kyu1    - fastening, brighter
    4: ["A", "G", "Bb", "A"],     # Kyu2    - peak, return of theme
    5: ["A", "E", "A", "A"],      # Jo_Coda - resolve to tonic drone
}

def get_bar_palette(sec_idx, bar_in_sec):
    return PALETTES[SECTION_PALETTES[sec_idx][bar_in_sec]]

def quantize_to_chord(pitch, chord_pcs, min_pitch=None, max_pitch=None):
    """Nearest pitch whose pitch-class is in chord_pcs, optionally bounded."""
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

# ---------------------------------------------------------------- Method 019: L-System
# Dragon-curve / paperfolding grammar: "A" -> "A+B", "B" -> "A-B"
# '+' = +2 semitones, '-' = -2 semitones. Balanced (+/- within 1 of each other),
# bounded, and self-similar -> a clean fractal melodic contour.
LS_RULES = {"A": "A+B", "B": "A-B"}
LS_SYMBOLS = {"+": 2, "-": -2, "=": 0}
LS_ITER = 8  # -> 255 deltas

lsys = IntervalLSystem(axiom="A", rules=LS_RULES, symbols=LS_SYMBOLS)
LS_DELTAS = lsys.generate_deltas(iterations=LS_ITER)
print(f"L-System: {len(LS_DELTAS)} deltas (dragon curve, iter={LS_ITER})")

def lsystem_stream():
    """Yield a continuous sequence of raw pitches (folded into koto range)."""
    pitch = 69  # A4
    while True:
        for d in LS_DELTAS:
            pitch += d
            # fold into a bounded 3-octave koto window, preserving contour direction
            folded = 57 + ((pitch - 57) % 34)
            yield int(folded)

# ================================================================
# PHASE 1: Raw Generative L-System Draft (Single Voice)
# ================================================================
def generate_phase1_raw():
    composer_p1 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS_PER_BAR)
    composer_p1.create_matrix(num_voices=1, num_sections=N_SECTIONS)
    composer_p1.add_voice("Raw_Koto", program=KOTO.midi_program, channel=0)

    stream = lsystem_stream()

    for s_idx, s_name in enumerate(SECTIONS):
        composer_p1.add_section(s_name, bars=BARS_PER_SECTION)
        events = []
        curr_tick = 35  # initial micro-offset (off-grid)

        while curr_tick < SECTION_TICKS - 300:
            raw_pitch = next(stream)
            dur = int(rng.uniform(150, 280))
            end_t = min(curr_tick + dur, SECTION_TICKS - 50)
            vel = int(rng.integers(70, 95))
            events.append(MusicEvent(
                pitch=raw_pitch, volume=vel,
                start_tick=curr_tick, end_tick=end_t
            ))
            advance = int(235 + rng.integers(-25, 25))
            curr_tick += advance

        # Terminal landmark for zero-drift
        events.append(MusicEvent(
            pitch=0, volume=0,
            start_tick=SECTION_TICKS - 1, end_tick=SECTION_TICKS
        ))
        composer_p1.fill_voice_section("Raw_Koto", s_name, MusicUnit(events=events))

    ok, msg = composer_p1.validate()
    assert ok, f"Phase 1 validate failed: {msg}"

    p1_path = os.path.join(MIDI_DIR, "103-japanese-kojo-koto-phase1.mid")
    composer_p1.to_midi(p1_path)
    assert os.path.getsize(p1_path) > 40, "Phase 1 MIDI empty"
    print(f"Phase 1 MIDI: {p1_path} ({os.path.getsize(p1_path)} bytes)")

    write_provenance(
        p1_path,
        classification=AI_ASSISTED,
        generator="musicom.workflows.unitmatrix_composer",
        parameters={
            "project": "103-japanese-kojo-koto",
            "phase": 1,
            "style": "Japanese",
            "method": "019 L-System Algorithmic Composition",
            "layer": "concrete",
            "grammar": "dragon-curve A->A+B, B->A-B (+2/-2 semitones)",
            "raw_timing": "unquantized",
            "seed": SEED,
        }
    )
    return p1_path

# ================================================================
# PHASE 2: Musicom Rules Post-Processing & Multi-Voice Arrangement
# ================================================================
def generate_phase2_composition():
    composer_p2 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS_PER_BAR)
    composer_p2.create_matrix(num_voices=5, num_sections=N_SECTIONS)

    composer_p2.add_voice("Koto", program=KOTO.midi_program, channel=0)
    composer_p2.add_voice("Shakuhachi", program=FLUTE.midi_program, channel=1)
    composer_p2.add_voice("Shamisen", program=SHAMISEN.midi_program, channel=2)
    composer_p2.add_voice("KotoBass", program=KOTO.midi_program, channel=3)
    composer_p2.add_voice("Taiko", program=0, channel=9)

    # Continuous L-system stream for the lead (fractal continuity across sections)
    lead_stream = lsystem_stream()

    for s_idx, s_name in enumerate(SECTIONS):
        composer_p2.add_section(s_name, bars=BARS_PER_SECTION)

        koto_events = []
        flute_events = []
        shamisen_events = []
        bass_events = []
        taiko_events = []

        # Lead density per section (Jo-Ha-Kyu acceleration arc)
        if s_name == "Jo":
            lead_steps = [0, 4, 8, 12]                       # quarter notes
        elif s_name == "Jo_Coda":
            lead_steps = [0, 2, 6, 8, 12]                    # gentle
        elif s_name in ("Ha1", "Ha2"):
            lead_steps = [0, 2, 4, 6, 8, 10, 12, 14]         # 8th notes
        else:  # Kyu1 / Kyu2
            lead_steps = list(range(16))                     # 16th runs

        for bar_in_sec in range(BARS_PER_SECTION):
            bar_start = bar_in_sec * BAR_TICKS
            pal = get_bar_palette(s_idx, bar_in_sec)

            # --- 1. Koto (lead) ---
            # Fractal melody: advance the L-system stream, snap to scale+palette.
            for step in lead_steps:
                t_onset = bar_start + step * GRID16
                raw = next(lead_stream)
                # snap raw whole-tone pitch to nearest hirajoshi scale tone,
                # then to the bar's palette (palette subset of scale).
                k_pitch = quantize_to_chord(raw, pal, min_pitch=62, max_pitch=90)
                dur = GRID16 if s_name in ("Kyu1", "Kyu2") and step % 2 == 0 else 100
                vel = 94 if (step % 4 == 0) else 78
                koto_events.append(MusicEvent(
                    pitch=k_pitch, volume=vel,
                    start_tick=t_onset, end_tick=t_onset + dur
                ))

            # --- 2. Shakuhachi (flute counterline, sustained) ---
            # Long airy tones in upper register, active in Ha/Kyu sections.
            if s_name in ("Ha1", "Ha2", "Kyu1", "Kyu2", "Jo_Coda"):
                fl_steps = [0, 8] if s_name not in ("Kyu1", "Kyu2") else [0, 6, 12]
                for fi, step in enumerate(fl_steps):
                    t_onset = bar_start + step * GRID16
                    base = 76 + (fi * 3)
                    f_pitch = quantize_to_chord(base, pal, min_pitch=69, max_pitch=93)
                    dur = 6 * GRID16 if step == 0 else 4 * GRID16
                    flute_events.append(MusicEvent(
                        pitch=f_pitch, volume=84 if step == 0 else 70,
                        start_tick=t_onset,
                        end_tick=min(t_onset + dur, bar_start + BAR_TICKS)
                    ))

            # --- 3. Shamisen (rhythmic pluck ostinato) ---
            # 8th-note plucks, palette-bound, syncopated accent on the off-8th.
            for step in range(8):
                t_onset = bar_start + step * GRID8
                if s_name in ("Jo", "Jo_Coda") and step % 2 == 1:
                    continue  # sparser in framing sections
                base = 57 + (step % 3) * 5
                sh_pitch = quantize_to_chord(base, pal, min_pitch=48, max_pitch=74)
                vel = 82 if step % 2 == 0 else 66
                shamisen_events.append(MusicEvent(
                    pitch=sh_pitch, volume=vel,
                    start_tick=t_onset, end_tick=t_onset + 140
                ))

            # --- 4. KotoBass (low drone) ---
            # Whole-note palette root in the koto's low register.
            bass_pcs = sorted(pal)
            bass_root = quantize_to_chord(57, pal, min_pitch=52, max_pitch=64)
            bass_events.append(MusicEvent(
                pitch=bass_root, volume=88,
                start_tick=bar_start, end_tick=bar_start + BAR_TICKS - 20
            ))

            # --- 5. Taiko (percussion, ch9) ---
            # Low tom thumps (taiko feel) + soft rim texture, sparse.
            for step, pitch, vel in [(0, 41, 100), (8, 43, 84), (4, 50, 70), (12, 45, 64)]:
                t_onset = bar_start + step * GRID16
                taiko_events.append(MusicEvent(
                    pitch=pitch, volume=vel,
                    start_tick=t_onset, end_tick=t_onset + 90
                ))

        def seal(ev_list):
            ev_list.sort(key=lambda e: (e.start_tick, e.end_tick))
            ev_list.append(MusicEvent(
                pitch=0, volume=0,
                start_tick=SECTION_TICKS - 1, end_tick=SECTION_TICKS
            ))
            return MusicUnit(events=ev_list)

        composer_p2.fill_voice_section("Koto", s_name, seal(koto_events))
        composer_p2.fill_voice_section("Shakuhachi", s_name, seal(flute_events))
        composer_p2.fill_voice_section("Shamisen", s_name, seal(shamisen_events))
        composer_p2.fill_voice_section("KotoBass", s_name, seal(bass_events))
        composer_p2.fill_voice_section("Taiko", s_name, seal(taiko_events))

    ok, msg = composer_p2.validate()
    assert ok, f"Phase 2 validate failed: {msg}"

    p2_path = os.path.join(MIDI_DIR, "103-japanese-kojo-koto.mid")
    composer_p2.to_midi(p2_path)
    assert os.path.getsize(p2_path) > 40, "Phase 2 MIDI empty"
    print(f"Phase 2 MIDI: {p2_path} ({os.path.getsize(p2_path)} bytes)")

    grid_path = os.path.join(ANALYSIS_DIR, "grid_visualization.txt")
    write_grid_visualization(
        composer_p2.matrix, grid_path,
        ticks_per_character=240,
        voice_names=["Koto", "Shakuhachi", "Shamisen", "KotoBass", "Taiko"],
        bpm=BPM
    )
    print(f"Grid visualization: {grid_path} ({os.path.getsize(grid_path)} bytes)")

    write_provenance(
        p2_path,
        classification=AI_ASSISTED,
        generator="musicom.workflows.unitmatrix_composer",
        parameters={
            "project": "103-japanese-kojo-koto",
            "phase": 2,
            "style": "Japanese",
            "method": "019 L-System Algorithmic Composition",
            "layer": "concrete",
            "quantization": "16th/8th grid (120/240 ticks)",
            "key": "A hirajoshi pentatonic",
            "bpm": BPM,
            "seed": SEED,
        }
    )
    return p2_path

if __name__ == "__main__":
    print("=== Phase 1: Raw L-System Draft ===")
    p1 = generate_phase1_raw()
    print("=== Phase 2: Rules Composition ===")
    p2 = generate_phase2_composition()
    print("Done!")
