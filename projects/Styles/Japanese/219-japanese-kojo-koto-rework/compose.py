# -*- coding: utf-8 -*-
"""219-japanese-kojo-koto-rework — extension + variation rework of 103-japanese-kojo-koto.

Source: Japanese/103-japanese-kojo-koto (L-System dragon-curve, A hirajoshi pentatonic).
Rework: extend Jo-Ha-Kyu form 6->8 sections (24->32 bars), add 6 variation techniques,
        two-phase architecture (raw L-system draft -> musicom rules).

Key: A hirajoshi pentatonic = pitch classes {9,10,2,4,7} (A, Bb, D, E, G).
BPM 80, 4/4, 480 TPB -> BAR=1920, 16th=120, 8th=240.
Voices: Koto (107 ch0 lead), Shakuhachi (74 ch1), Shamisen (106 ch2),
        KotoBass (107 ch3 drone), Taiko (ch9 percussion).
"""

import os
import json
import numpy as np

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer
from workflows.provenance import write_provenance, AI_ASSISTED
from visualization.grid import write_grid_visualization
from generators.interval_lsystem import IntervalLSystem

# Instrument programs (verified from instrument_registry: KOTO=107, FLUTE=74, SHAMISEN=106).
KOTO = 107
FLUTE = 74
SHAMISEN = 106

SEED = 20261003
rng = np.random.default_rng(SEED)

PROJ = os.path.dirname(os.path.abspath(__file__))
MIDI_DIR = os.path.join(PROJ, "MIDI")
AUDIO_DIR = os.path.join(PROJ, "Audio")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")
for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
    os.makedirs(d, exist_ok=True)

PROJ_ID = "219-japanese-kojo-koto-rework"

# ------------------------------------------------------------------ Grid & Timing
BPM = 80
TPB = 480
BEATS_PER_BAR = 4
GRID16 = 120
GRID8 = 240
BAR_TICKS = TPB * BEATS_PER_BAR          # 1920
BARS_PER_SECTION = 4
SECTION_TICKS = BAR_TICKS * BARS_PER_SECTION   # 7680

# ------------------------------------------------------------------ Form
# 8 sections x 4 bars = 32 bars (source was 6x4=24).
# (name, method, start_offset, density, lead_min, lead_max)
SECTIONS = [
    ("Jo",        "original",   0,  "quarter",   62, 90),
    ("Ha1",       "original",  24,  "eighth",    62, 90),
    ("Ha2",       "invert",    40,  "eighth",    62, 90),
    ("Bridge",    "arpeggio",   0,  "arp",       62, 88),
    ("Kyu1",      "retrograde", 56, "sixteenth", 62, 90),
    ("Kyu2",      "original",  80,  "sixteenth", 74, 90),   # register shift (high octave)
    ("Interlude", "original", 110,  "eighth",    62, 90),
    ("Jo_Coda",   "original",   0,  "quarter",   62, 90),
]
N_SECTIONS = len(SECTIONS)
N_BARS = N_SECTIONS * BARS_PER_SECTION        # 32
TOTAL_TICKS = SECTION_TICKS * N_SECTIONS      # 61440

# ------------------------------------------------------------------ Harmonic Framework
# A hirajoshi pentatonic: pc {9,10,2,4,7} = A(9) Bb(10) D(2) E(4) G(7).
SCALE_PCS = {9, 10, 2, 4, 7}

# Five 4-note palettes (root + 3 other scale tones, dropping one tone).
# Root pc of each palette IS a member -> bass can sit on the true root.
PALETTES = {
    "A":  {9, 10, 2, 4},    # A  Bb D  E   (drop G)
    "Bb": {10, 2, 4, 7},    # Bb D  E  G   (drop A)
    "D":  {2, 4, 7, 9},     # D  E  G  A   (drop Bb)
    "E":  {4, 7, 9, 10},    # E  G  A  Bb  (drop D)
    "G":  {7, 9, 10, 2},    # G  A  Bb D   (drop E)
}
ROOTS = {"A": 9, "Bb": 10, "D": 2, "E": 4, "G": 7}

# Per-section palette progression (4 bars each). Each section has its OWN region;
# home roots vary (A, G, Bb, D, E, G, A, A) so no all-tonic collapse.
PROGRESSIONS = [
    ["A", "A", "D", "A"],        # Jo        - tonic meditation (augmentation)
    ["A", "G", "Bb", "A"],       # Ha1       - theme
    ["Bb", "D", "E", "Bb"],      # Ha2       - inversion, tension
    ["D", "G", "A", "D"],        # Bridge    - method change (arpeggio)
    ["E", "A", "G", "E"],        # Kyu1      - retrograde + diminution
    ["G", "A", "Bb", "E"],       # Kyu2      - register shift, peak
    ["A", "Bb", "D", "A"],       # Interlude - counterline (canon)
    ["A", "E", "D", "A"],        # Jo_Coda   - resolution
]

def get_bar_palette(sec_idx, bar_in_sec):
    return PALETTES[PROGRESSIONS[sec_idx][bar_in_sec]]

def root_note(pal_name):
    """Bass root = the palette's named root pc, nearest octave in koto low register."""
    pc = ROOTS[pal_name]
    for octv in range(2, 7):
        p = octv * 12 + pc
        if 52 <= p <= 64:
            return p
    return 60

def quantize_to_chord(pitch, chord_pcs, min_pitch=None, max_pitch=None):
    """Nearest pitch whose pitch-class is in chord_pcs (subset of scale)."""
    candidates = []
    for octv in range(2, 9):
        for pc in chord_pcs:
            p = octv * 12 + pc
            if min_pitch is not None and p < min_pitch:
                continue
            if max_pitch is not None and p > max_pitch:
                continue
            candidates.append(p)
    if not candidates:
        for octv in range(2, 9):
            for pc in chord_pcs:
                candidates.append(octv * 12 + pc)
    return min(candidates, key=lambda c: (abs(c - pitch), c))

# ------------------------------------------------------------------ Method 019: L-System
LS_RULES = {"A": "A+B", "B": "A-B"}
LS_SYMBOLS = {"+": 2, "-": -2, "=": 0}
LS_ITER = 8
lsys = IntervalLSystem(axiom="A", rules=LS_RULES, symbols=LS_SYMBOLS)
LS_DELTAS = list(lsys.generate_deltas(iterations=LS_ITER))   # 255 deltas
INVERTED = [-d for d in LS_DELTAS]
RETROGRADE = list(reversed(LS_DELTAS))
RETRO_INV = [-d for d in reversed(LS_DELTAS)]

ARPEGGIO = [69, 70, 74, 76, 79, 76, 74, 70]   # A Bb D E G (hirajoshi arpeggio)

def make_lead_gen(method, start_offset):
    """Return an infinite generator of raw (unquantized) lead pitches."""
    if method == "arpeggio":
        i = 0
        while True:
            yield ARPEGGIO[i % len(ARPEGGIO)]
            i += 1
    else:
        d = {"original": LS_DELTAS, "invert": INVERTED,
             "retrograde": RETROGRADE, "retro_inv": RETRO_INV}[method]
        p = 69
        i = start_offset % len(d)
        while True:
            p += d[i]
            folded = 57 + ((p - 57) % 34)     # fold into koto window [57, 90]
            yield int(folded)
            i = (i + 1) % len(d)

def density_steps(density):
    if density == "quarter":
        return [0, 4, 8, 12]
    if density == "eighth":
        return [0, 2, 4, 6, 8, 10, 12, 14]
    if density == "sixteenth":
        return list(range(16))
    if density == "arp":
        return [0, 2, 4, 6, 8, 10, 12, 14]
    return [0, 4, 8, 12]

def lead_duration(density):
    if density == "quarter":
        return 420
    if density == "eighth" or density == "arp":
        return 200
    return 100

def finalize(events, section_ticks, snap_grid=GRID16):
    """Sort, grid-snap, dedup collisions, clamp, and add the terminal landmark."""
    cleaned = []
    for e in events:
        st = e.start_tick
        # snap onset to nearest 16th grid (already on-grid by construction; safety net)
        snapped = int(round(st / snap_grid)) * snap_grid
        if snapped < 0:
            snapped = 0
        if snapped >= section_ticks:
            snapped = section_ticks - snap_grid
        et = min(e.end_tick, section_ticks)
        if et <= snapped:
            et = min(snapped + snap_grid, section_ticks)
        cleaned.append(MusicEvent(pitch=e.pitch, volume=e.volume,
                                  start_tick=snapped, end_tick=et))
    # dedup collided (start_tick, pitch) keeping longest duration
    best = {}
    for e in cleaned:
        key = (e.start_tick, e.pitch)
        if key not in best or e.end_tick > best[key].end_tick:
            best[key] = e
    out = sorted(best.values(), key=lambda e: (e.start_tick, -e.end_tick))
    # terminal landmark for zero-drift
    out.append(MusicEvent(pitch=0, volume=0,
                          start_tick=section_ticks - 1, end_tick=section_ticks))
    return MusicUnit(events=out)

# ================================================================
# PHASE 1: Raw generative L-System draft (single voice, unquantized)
# ================================================================
def generate_phase1_raw():
    composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS_PER_BAR)
    composer.create_matrix(num_voices=1, num_sections=N_SECTIONS)
    composer.add_voice("Raw_Koto", program=KOTO, channel=0)

    for s_idx, (s_name, method, off, density, lmin, lmax) in enumerate(SECTIONS):
        composer.add_section(s_name, bars=BARS_PER_SECTION)
        gen = make_lead_gen(method, off)
        events = []
        curr_tick = 35                      # micro-offset (off-grid)
        while curr_tick < SECTION_TICKS - 300:
            raw = next(gen)
            dur = int(rng.uniform(150, 280))
            end_t = min(curr_tick + dur, SECTION_TICKS - 50)
            vel = int(rng.integers(70, 95))
            events.append(MusicEvent(pitch=raw, volume=vel,
                                     start_tick=curr_tick, end_tick=end_t))
            curr_tick += int(235 + rng.integers(-25, 25))
        events.append(MusicEvent(pitch=0, volume=0,
                                 start_tick=SECTION_TICKS - 1, end_tick=SECTION_TICKS))
        composer.fill_voice_section("Raw_Koto", s_name, MusicUnit(events=events))

    ok, msg = composer.validate()
    assert ok, f"Phase 1 validate failed: {msg}"

    p1_path = os.path.join(MIDI_DIR, f"{PROJ_ID}-phase1.mid")
    composer.to_midi(p1_path)
    assert os.path.getsize(p1_path) > 40, "Phase 1 MIDI empty"

    write_provenance(
        p1_path,
        classification=AI_ASSISTED,
        generator="musicom.workflows.unitmatrix_composer",
        parameters={
            "project": PROJ_ID,
            "phase": 1,
            "style": "Japanese",
            "method": "019 L-System (dragon-curve) + transforms",
            "layer": "concrete",
            "raw_timing": "unquantized",
            "variation": ["augmentation", "inversion", "arpeggio-method-change",
                          "retrograde", "register-shift", "canon-counterline"],
            "seed": SEED,
            "reworked_from": "103-japanese-kojo-koto",
        },
    )
    print(f"Phase 1 MIDI: {p1_path} ({os.path.getsize(p1_path)} B)")
    return p1_path

# ================================================================
# PHASE 2: musicom rules post-processing + 5-voice arrangement
# ================================================================
def generate_phase2_composition():
    composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS_PER_BAR)
    composer.create_matrix(num_voices=5, num_sections=N_SECTIONS)
    composer.add_voice("Koto", program=KOTO, channel=0)
    composer.add_voice("Shakuhachi", program=FLUTE, channel=1)
    composer.add_voice("Shamisen", program=SHAMISEN, channel=2)
    composer.add_voice("KotoBass", program=KOTO, channel=3)
    composer.add_voice("Taiko", program=0, channel=9)

    for s_idx, (s_name, method, off, density, lmin, lmax) in enumerate(SECTIONS):
        composer.add_section(s_name, bars=BARS_PER_SECTION)
        lead_gen = make_lead_gen(method, off)
        steps = density_steps(density)
        dur = lead_duration(density)

        koto_events = []
        flute_events = []
        shamisen_events = []
        bass_events = []
        taiko_events = []

        for bar_in_sec in range(BARS_PER_SECTION):
            bar_start = bar_in_sec * BAR_TICKS
            pal_name = PROGRESSIONS[s_idx][bar_in_sec]
            pal = PALETTES[pal_name]

            # ---- 1. Koto lead (fractal -> snap to scale+palette) ----
            for step in steps:
                t_onset = bar_start + step * GRID16
                raw = next(lead_gen)
                k_pitch = quantize_to_chord(raw, pal, min_pitch=lmin, max_pitch=lmax)
                vel = 94 if (step % 4 == 0) else 78
                koto_events.append(MusicEvent(
                    pitch=k_pitch, volume=vel,
                    start_tick=t_onset, end_tick=min(t_onset + dur, bar_start + BAR_TICKS)))

            # ---- 2. Shakuhachi sustained counterline ----
            if s_name not in ("Jo",):
                fl_steps = [0, 8] if density not in ("sixteenth",) else [0, 6, 12]
                for fi, step in enumerate(fl_steps):
                    t_onset = bar_start + step * GRID16
                    base = 76 + (fi * 3)
                    f_pitch = quantize_to_chord(base, pal, min_pitch=69, max_pitch=93)
                    fdur = 6 * GRID16 if step == 0 else 4 * GRID16
                    flute_events.append(MusicEvent(
                        pitch=f_pitch, volume=84 if step == 0 else 70,
                        start_tick=t_onset,
                        end_tick=min(t_onset + fdur, bar_start + BAR_TICKS)))

            # ---- 3. Shamisen ----
            if s_name == "Interlude":
                # Canon counterline: echo the koto lead a 16th later, an octave down.
                for ke in koto_events:
                    if ke.pitch == 0 or ke.start_tick < bar_start or ke.start_tick >= bar_start + BAR_TICKS:
                        continue
                    echo_t = ke.start_tick + GRID16
                    if echo_t >= bar_start + BAR_TICKS:
                        continue
                    shamisen_events.append(MusicEvent(
                        pitch=ke.pitch - 12, volume=max(40, ke.volume - 24),
                        start_tick=echo_t, end_tick=min(echo_t + 120, bar_start + BAR_TICKS)))
            else:
                for step in range(8):
                    t_onset = bar_start + step * GRID8
                    if s_name in ("Jo", "Jo_Coda") and step % 2 == 1:
                        continue
                    base = 57 + (step % 3) * 5
                    sh_pitch = quantize_to_chord(base, pal, min_pitch=48, max_pitch=74)
                    vel = 82 if step % 2 == 0 else 66
                    shamisen_events.append(MusicEvent(
                        pitch=sh_pitch, volume=vel,
                        start_tick=t_onset, end_tick=t_onset + 140))

            # ---- 4. KotoBass drone on the true root ----
            bass_root = root_note(pal_name)
            bass_events.append(MusicEvent(
                pitch=bass_root, volume=88,
                start_tick=bar_start, end_tick=bar_start + BAR_TICKS - 20))

            # ---- 5. Taiko (ch9 percussion) ----
            if s_name in ("Jo", "Jo_Coda"):
                hits = [(0, 36, 100), (8, 45, 70)]
            elif density == "sixteenth":
                hits = [(0, 36, 100), (4, 50, 70), (6, 45, 64),
                        (8, 45, 70), (12, 50, 70), (14, 45, 60)]
            else:
                hits = [(0, 36, 100), (4, 50, 64), (8, 45, 70), (12, 45, 64)]
            for step, pitch, vel in hits:
                t_onset = bar_start + step * GRID16
                taiko_events.append(MusicEvent(
                    pitch=pitch, volume=vel,
                    start_tick=t_onset, end_tick=t_onset + 90))

        composer.fill_voice_section("Koto", s_name, finalize(koto_events, SECTION_TICKS))
        composer.fill_voice_section("Shakuhachi", s_name, finalize(flute_events, SECTION_TICKS))
        composer.fill_voice_section("Shamisen", s_name, finalize(shamisen_events, SECTION_TICKS))
        composer.fill_voice_section("KotoBass", s_name, finalize(bass_events, SECTION_TICKS))
        composer.fill_voice_section("Taiko", s_name, finalize(taiko_events, SECTION_TICKS))

    ok, msg = composer.validate()
    assert ok, f"Phase 2 validate failed: {msg}"

    p2_path = os.path.join(MIDI_DIR, f"{PROJ_ID}.mid")
    composer.to_midi(p2_path)
    assert os.path.getsize(p2_path) > 40, "Phase 2 MIDI empty"

    grid_path = os.path.join(ANALYSIS_DIR, "grid_visualization.txt")
    write_grid_visualization(
        composer.matrix, grid_path,
        ticks_per_character=240,
        voice_names=["Koto", "Shakuhachi", "Shamisen", "KotoBass", "Taiko"],
        bpm=BPM,
    )

    write_provenance(
        p2_path,
        classification=AI_ASSISTED,
        generator="musicom.workflows.unitmatrix_composer",
        parameters={
            "project": PROJ_ID,
            "phase": 2,
            "style": "Japanese",
            "method": "019 L-System (dragon-curve) + transforms",
            "layer": "concrete",
            "quantization": "16th/8th grid (120/240 ticks)",
            "key": "A hirajoshi pentatonic",
            "bpm": BPM,
            "form": "Jo-Ha-Kyu (8 sections x 4 bars = 32 bars)",
            "variation": {
                "Jo": "augmentation (quarter-note lead)",
                "Ha2": "inversion (negated deltas)",
                "Bridge": "method change (pentatonic arpeggio)",
                "Kyu1": "retrograde + diminution (16ths)",
                "Kyu2": "register shift (lead 74-90) + diminution",
                "Interlude": "canon counterline (shamisen echo)",
            },
            "seed": SEED,
            "reworked_from": "103-japanese-kojo-koto",
        },
    )

    # Root provenance.json (standard 6)
    root_prov = os.path.join(PROJ, "provenance.json")
    with open(root_prov, "w") as f:
        json.dump({
            "project": PROJ_ID,
            "classification": AI_ASSISTED,
            "generator": "musicom.workflows.unitmatrix_composer",
            "style": "Japanese",
            "key": "A hirajoshi pentatonic",
            "bpm": BPM,
            "form": "Jo-Ha-Kyu 8x4=32 bars",
            "phase1": os.path.basename(p2_path).replace(".mid", "-phase1.mid"),
            "phase2": os.path.basename(p2_path),
            "reworked_from": "103-japanese-kojo-koto",
            "seed": SEED,
        }, f, indent=2)

    print(f"Phase 2 MIDI: {p2_path} ({os.path.getsize(p2_path)} B)")
    print(f"Grid viz: {grid_path} ({os.path.getsize(grid_path)} B)")
    print(f"Root provenance: {root_prov}")
    return p2_path

if __name__ == "__main__":
    print("=== Phase 1: Raw L-System Draft ===")
    p1 = generate_phase1_raw()
    print("=== Phase 2: Rules Composition ===")
    p2 = generate_phase2_composition()
    print("Done!")
