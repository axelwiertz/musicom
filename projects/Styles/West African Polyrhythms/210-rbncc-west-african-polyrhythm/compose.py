# -*- coding: utf-8 -*-
"""210-rbncc-west-african-polyrhythm - West African Polyrhythms / Method 082 RBNCC.

Autonomous composition job (date: 2026-09-28). Nightly composition job ID 1fc3fd65d359.

Style: West African Polyrhythms (Ewe/Ghana timeline ensemble: gankogui double
bell, kalimba/kora lead, balafon counter, dunun bass, djembe/shaker drums).
Method: 082 Random Boolean Network Criticality Composition (RBNCC), Nature-Led.
Layer: concrete.

Method essence (Kauffman RBN at the critical point):
  A synchronous random Boolean network (N=16 nodes, K=2 inputs, output bias
  p=0.5 -> Kc = 1/[2p(1-p)] = 2, i.e. the edge of chaos). The deterministic
  state trajectory falls into an attractor CYCLE; the pre-attractor TRANSIENT
  is connective/tension material; FROZEN nodes (bits that never flip across
  the cycle) are the harmonic scaffold; UNSTABLE nodes are melodic figuration.

  This seed (20260928, init seed+7) yields transient=1, cycle=12. A 12-step
  cycle cycled against the 16-sixteenth bar yields a 3:4 cross-rhythm (the
  lead contour repeats every 12 sixteenths = 3 beats while the bar is 4 beats)
  -- a method-derived West African polyrhythm.

Two-phase architecture:
  Phase 1: raw RBN draft - single voice (Raw_Lead). Onsets carry micro-jitter
           OFF the 16th grid; pitch is raw chromatic (no key/chord snapping).
           No harmony, no chord-tone quantization. -> -phase1.mid
  Phase 2: musicom rules post-processing - same RBN (same seed) re-run, then:
             (a) every onset snapped to the 16th grid (120 ticks),
             (b) every pitch snapped to its bar's chord tones (G major),
           and a full 5-voice West African polyrhythmic texture is added:
             Voice 1: Gankogui  (MARIMBA GM 12,  ch0) - 2-pitch timeline bell
             Voice 2: LeadKora  (KALIMBA GM 108, ch1) - RBN attractor melody
             Voice 3: BassDunun (DOUBLE_BASS GM 43, ch2) - root pulse (3+3+2)
             Voice 4: Balafon   (XYLOPHONE GM 13, ch3) - RBN interlocking counter
             Voice 5: Drums     (ch9) - dunun kick, djembe slap, RBN shaker
           Zero-drift gate via UnitMatrixComposer.validate().
           -> 210-rbncc-west-african-polyrhythm.mid
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
from instrument_registry import MARIMBA, KALIMBA, DOUBLE_BASS, XYLOPHONE

SEED = 20260928
INIT_SEED = SEED + 7

PROJ = "/opt/data/repos/musicom/projects/Styles/West African Polyrhythms/210-rbncc-west-african-polyrhythm"
MIDI_DIR = os.path.join(PROJ, "MIDI")
AUDIO_DIR = os.path.join(PROJ, "Audio")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")
for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
    os.makedirs(d, exist_ok=True)

# ---------------------------------------------------------------- Grid & Timing
BPM = 112
TPB = 480
BEATS_PER_BAR = 4
GRID16 = 120
GRID8 = 240
BAR_TICKS = TPB * BEATS_PER_BAR          # 1920
SECTION_TICKS = BAR_TICKS * 4            # 7680
STEPS_PER_BAR = 16                       # 16 sixteenths
N_BARS = 32
N_STEPS = N_BARS * STEPS_PER_BAR         # 512 sixteenth slots
TOTAL_TICKS = N_BARS * BAR_TICKS         # 61440

SECTIONS = ["Intro", "Verse", "Chorus", "Verse2", "Chorus2",
            "Break", "Chorus3", "Outro"]
BARS_PER_SECTION = 4
N_SECTIONS = len(SECTIONS)

# ---------------------------------------------------------------- Harmonic Framework
# G major = G A B C D E F# = pitch classes {7, 9, 11, 0, 2, 4, 6}
G_MAJOR_PCS = {7, 9, 11, 0, 2, 4, 6}

# Chord progression per section (4 bars each): I-IV-V-I with vi for lift.
SECTION_CHORDS = {
    0: ["G", "G", "G", "G"],    # Intro  (sparse pedal)
    1: ["G", "C", "D", "G"],    # Verse  (I IV V I)
    2: ["G", "Em", "C", "D"],   # Chorus (I vi IV V)
    3: ["G", "C", "D", "G"],    # Verse2
    4: ["G", "Em", "C", "D"],   # Chorus2
    5: ["Em", "C", "G", "D"],   # Break  (vi IV I V - darker turn)
    6: ["G", "Em", "C", "D"],   # Chorus3
    7: ["G", "G", "G", "G"],    # Outro  (sparse pedal)
}

CHORD_PCS = {
    "G": {7, 11, 2},   # G  B  D
    "C": {0, 4, 7},    # C  E  G
    "D": {2, 6, 9},    # D  F# A
    "Em": {4, 7, 11},  # E  G  B
}

# Chord root pitch-class + bass register root (DOUBLE_BASS sweet 40-55)
CHORD_ROOT_PC = {"G": 7, "C": 0, "D": 2, "Em": 4}
CHORD_ROOT_BASS = {"G": 43, "C": 36, "D": 38, "Em": 40}  # G2 C2 D2 E2

# Gankogui double bell (two pitches): low = chord root, high = chord fifth.
BELL_LOW = {"G": 79, "C": 72, "D": 74, "Em": 76}   # G5 C5 D5 E5
BELL_HIGH = {"G": 86, "C": 79, "D": 81, "Em": 83}  # D6 G5 A5 B5


def get_bar_chord(sec_idx, bar_in_sec):
    return SECTION_CHORDS[sec_idx][bar_in_sec]


def get_chord_for_step(step):
    """Global 16th-step -> chord name."""
    bar = step // STEPS_PER_BAR
    sec = bar // BARS_PER_SECTION
    bar_in_sec = bar % BARS_PER_SECTION
    return get_bar_chord(sec, bar_in_sec)


# ---------------------------------------------------------------- Method 082 RBN primitives

def build_rbn(n=16, k=2, p=0.5, seed=SEED):
    """Build a synchronous random Boolean network (Kauffman model).

    n nodes, each with k distinct inputs (no self-loops) and a random Boolean
    function (truth table of 2^k bits, each 1 with probability p). p=0.5, k=2
    -> Kc = 1/[2p(1-p)] = 2 -> critical (edge of chaos).
    """
    rng = np.random.default_rng(seed)
    inputs, funcs = [], []
    for i in range(n):
        cand = [j for j in range(n) if j != i]
        inputs.append(sorted(rng.choice(cand, size=k, replace=False).tolist()))
        funcs.append((rng.random(size=2 ** k) < p).astype(np.uint8))
    return inputs, funcs


def rbn_step(state, inputs, funcs):
    new = np.zeros_like(state)
    for i in range(len(state)):
        idx = 0
        for b, src in enumerate(inputs[i]):
            idx |= int(state[src]) << b
        new[i] = funcs[i][idx]
    return new


def run_rbn(n=16, k=2, p=0.5, seed=SEED, init_seed=INIT_SEED, n_steps=N_STEPS):
    """Run the RBN for n_steps; return trajectory, transient_len, cycle, frozen."""
    inputs, funcs = build_rbn(n, k, p, seed)
    state = (np.random.default_rng(init_seed).random(n) < 0.5).astype(np.uint8)
    init_state = state.copy()

    # First: find attractor (transient + cycle) for reporting/frozen-node analysis.
    seen, states = {}, []
    transient_len, cycle = None, None
    s = init_state.copy()
    for t in range(200000):
        key = tuple(int(x) for x in s)
        if key in seen:
            transient_len = seen[key]
            cycle = states[transient_len:]
            break
        seen[key] = t
        states.append(s.copy())
        s = rbn_step(s, inputs, funcs)

    # Then: emit the full deterministic trajectory for the piece.
    trajectory = []
    s = init_state.copy()
    for _ in range(n_steps):
        trajectory.append(s.copy())
        s = rbn_step(s, inputs, funcs)

    frozen = []
    if cycle:
        arr = np.array(cycle)
        frozen = [i for i in range(n) if len(np.unique(arr[:, i])) == 1]

    return trajectory, transient_len, len(cycle) if cycle else None, frozen


def bits_to_int(state, lo, hi):
    """Inclusive bit-slice lo..hi (bit 0 = LSB) -> int."""
    v = 0
    for b in range(lo, hi + 1):
        v |= int(state[b]) << (b - lo)
    return v


# Bit-field decode (16-bit state, bit 0 = LSB):
#   [0:4]  lead_deg  0-15 pitch index for lead melody (>=12 -> rest)
#   [4:6]  lead_art  0-3  articulation (unused gate; kept for method fidelity)
#   [6:9]  lead_vel  0-7  velocity
#   [9:12] bal_deg   0-7  pitch index for balafon counter
#   [12:14] bal_gate 0-3  fire gate for balafon (==1 -> fire)
#   [14:16] shake    0-3  shaker density (==3 -> extra RBN shaker)
def decode(state):
    return {
        "lead_deg": bits_to_int(state, 0, 3),
        "lead_art": bits_to_int(state, 4, 5),
        "lead_vel": bits_to_int(state, 6, 8),
        "bal_deg": bits_to_int(state, 9, 11),
        "bal_gate": bits_to_int(state, 12, 13),
        "shake": bits_to_int(state, 14, 15),
    }


def quantize_to_chord(pitch, chord_pcs, min_pitch=None, max_pitch=None):
    """Nearest pitch whose pitch-class is in chord_pcs, bounded to [min,max]."""
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


# ================================================================
# PHASE 1: Raw RBN Draft (single voice, unquantized)
# ================================================================
def generate_phase1_raw():
    composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS_PER_BAR)
    composer.create_matrix(num_voices=1, num_sections=N_SECTIONS)
    composer.add_voice("Raw_Lead", program=KALIMBA.midi_program, channel=0)

    traj, transient_len, cycle_len, frozen = run_rbn()
    rng = np.random.default_rng(SEED)

    for s_idx, s_name in enumerate(SECTIONS):
        composer.add_section(s_name, bars=BARS_PER_SECTION)
        events = []
        for bar_in_sec in range(BARS_PER_SECTION):
            bar_start = bar_in_sec * BAR_TICKS
            for step_in_bar in range(STEPS_PER_BAR):
                step = s_idx * BARS_PER_SECTION * STEPS_PER_BAR + bar_in_sec * STEPS_PER_BAR + step_in_bar
                d = decode(traj[step])
                if d["lead_deg"] >= 12:
                    continue  # rest
                # RAW onset: 16th slot + micro-jitter OFF the 120/240 grid
                t_onset = bar_start + step_in_bar * GRID16 + int(rng.integers(-18, 18))
                t_onset = max(bar_start, min(t_onset, bar_start + BAR_TICKS - 40))
                # RAW pitch: unquantized chromatic (no key/chord snapping)
                pitch = 48 + d["lead_deg"] * 3
                dur = int(rng.integers(80, 160))
                end_t = min(t_onset + dur, bar_start + BAR_TICKS - 10)
                vel = 56 + d["lead_vel"] * 7
                events.append(MusicEvent(pitch=int(pitch), volume=int(vel),
                                         start_tick=t_onset, end_tick=end_t))

        # Zero-drift terminal landmark
        events.append(MusicEvent(pitch=0, volume=0,
                                 start_tick=SECTION_TICKS - 1, end_tick=SECTION_TICKS))
        composer.fill_voice_section("Raw_Lead", s_name, MusicUnit(events=events))

    ok, msg = composer.validate()
    assert ok, f"Phase 1 validate failed: {msg}"

    p1_path = os.path.join(MIDI_DIR, "210-rbncc-west-african-polyrhythm-phase1.mid")
    composer.to_midi(p1_path)
    assert os.path.getsize(p1_path) > 40, "Phase 1 MIDI empty"
    print(f"Phase 1 MIDI: {p1_path} ({os.path.getsize(p1_path)} bytes)")

    write_provenance(p1_path, classification=AI_ASSISTED,
                     generator="musicom.workflows.unitmatrix_composer",
                     parameters={
                         "project": "210-rbncc-west-african-polyrhythm", "phase": 1,
                         "style": "West African Polyrhythms",
                         "method": "082 Random Boolean Network Criticality Composition",
                         "layer": "concrete",
                         "raw_timing": "unquantized micro-jitter (off-grid)",
                         "raw_pitch": "raw chromatic (48 + deg*3), no key/chord snap",
                         "rbn": {"n": 16, "k": 2, "p": 0.5, "transient": transient_len,
                                 "cycle_len": cycle_len, "frozen_nodes": frozen},
                         "key": "G major", "bpm": BPM, "seed": SEED,
                     })
    return p1_path


# ================================================================
# PHASE 2: Musicom Rules Post-Processing + 5-Voice Arrangement
# ================================================================
def generate_phase2_composition():
    composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS_PER_BAR)
    composer.create_matrix(num_voices=5, num_sections=N_SECTIONS)

    composer.add_voice("Gankogui", program=MARIMBA.midi_program, channel=0)
    composer.add_voice("LeadKora", program=KALIMBA.midi_program, channel=1)
    composer.add_voice("BassDunun", program=DOUBLE_BASS.midi_program, channel=2)
    composer.add_voice("Balafon", program=XYLOPHONE.midi_program, channel=3)
    composer.add_voice("Drums", program=0, channel=9)

    traj, transient_len, cycle_len, frozen = run_rbn()

    # Gankogui bell timeline (5-stroke 3-2 clave; 6th stroke in chorus/break)
    BELL_STEPS = (0, 3, 6, 10, 12)

    for s_idx, s_name in enumerate(SECTIONS):
        composer.add_section(s_name, bars=BARS_PER_SECTION)

        bell_events, lead_events, bass_events, bal_events, drum_events = [], [], [], [], []

        for bar_in_sec in range(BARS_PER_SECTION):
            bar_start = bar_in_sec * BAR_TICKS
            chord = get_bar_chord(s_idx, bar_in_sec)
            c_pcs = CHORD_PCS[chord]
            bar_end = bar_start + BAR_TICKS
            dense = s_name in ("Chorus", "Chorus2", "Chorus3", "Break")

            # --- 1. Gankogui bell: two-pitch timeline (low=root, high=fifth) ---
            for j, step in enumerate(BELL_STEPS):
                t = bar_start + step * GRID16
                pitch = BELL_LOW[chord] if j % 2 == 0 else BELL_HIGH[chord]
                bell_events.append(MusicEvent(pitch=pitch, volume=100 if j == 0 else 88,
                                              start_tick=t, end_tick=t + 90))
            if dense:
                t = bar_start + 14 * GRID16
                bell_events.append(MusicEvent(pitch=BELL_HIGH[chord], volume=78,
                                              start_tick=t, end_tick=t + 80))

            # --- 2. LeadKora: RBN attractor melody (16th grid, chord-tone) ---
            # --- 3. Balafon: RBN interlocking counter (16th grid, chord-tone) ---
            # --- 5a. Drums shaker: RBN-driven extra hits (collected below) ---
            for step_in_bar in range(STEPS_PER_BAR):
                step = s_idx * BARS_PER_SECTION * STEPS_PER_BAR + bar_in_sec * STEPS_PER_BAR + step_in_bar
                d = decode(traj[step])
                t = bar_start + step_in_bar * GRID16  # snapped to 16th grid

                # Lead: fire when lead_deg < 12 (RBN rests are deg>=12)
                if d["lead_deg"] < 12:
                    raw = 48 + d["lead_deg"] * 3
                    lp = quantize_to_chord(raw, c_pcs, min_pitch=60, max_pitch=90)
                    vel = 56 + d["lead_vel"] * 7
                    lead_events.append(MusicEvent(pitch=lp, volume=vel,
                                                  start_tick=t, end_tick=t + 110))

                # Balafon: fire when bal_gate == 1
                if d["bal_gate"] == 1:
                    raw = 60 + d["bal_deg"] * 4
                    bp = quantize_to_chord(raw, c_pcs, min_pitch=67, max_pitch=96)
                    bal_events.append(MusicEvent(pitch=bp, volume=84,
                                                 start_tick=t, end_tick=t + 100))

            # --- 4. BassDunun: root pulse, 3+3+2 syncopation ---
            root_bass = CHORD_ROOT_BASS[chord]
            for j, step in enumerate((0, 6, 10)):
                t = bar_start + step * GRID16
                bass_events.append(MusicEvent(pitch=root_bass, volume=(100, 86, 86)[j],
                                              start_tick=t, end_tick=t + 160))

            # --- 5. Drums (ch9): dunun kick, djembe slap, shaker (8ths + RBN) ---
            for step_in_bar in range(STEPS_PER_BAR):
                t = bar_start + step_in_bar * GRID16
                # shaker: steady 8ths (even 16ths) + RBN extra on shake==3 (odd 16ths)
                if step_in_bar % 2 == 0:
                    sh_vel = 70 if step_in_bar % 4 == 0 else 52
                    drum_events.append(MusicEvent(pitch=42, volume=sh_vel,
                                                  start_tick=t, end_tick=t + 40))
                else:
                    step = s_idx * BARS_PER_SECTION * STEPS_PER_BAR + bar_in_sec * STEPS_PER_BAR + step_in_bar
                    if decode(traj[step])["shake"] == 3:
                        drum_events.append(MusicEvent(pitch=42, volume=60,
                                                      start_tick=t, end_tick=t + 40))
                # kick (dunun): beats 1 + "and of 3"
                if step_in_bar in (0, 10):
                    drum_events.append(MusicEvent(pitch=36, volume=(100 if step_in_bar == 0 else 90),
                                                  start_tick=t, end_tick=t + 90))
                # djembe slap: beats 2 & 4 (+ ghost on the 'e' of 4)
                if step_in_bar in (4, 12):
                    drum_events.append(MusicEvent(pitch=38, volume=92,
                                                  start_tick=t, end_tick=t + 80))
                if step_in_bar == 14:
                    drum_events.append(MusicEvent(pitch=38, volume=55,
                                                  start_tick=t, end_tick=t + 50))

        def seal(ev_list):
            ev_list.sort(key=lambda e: (e.start_tick, e.end_tick))
            ev_list.append(MusicEvent(pitch=0, volume=0,
                                      start_tick=SECTION_TICKS - 1, end_tick=SECTION_TICKS))
            return MusicUnit(events=ev_list)

        composer.fill_voice_section("Gankogui", s_name, seal(bell_events))
        composer.fill_voice_section("LeadKora", s_name, seal(lead_events))
        composer.fill_voice_section("BassDunun", s_name, seal(bass_events))
        composer.fill_voice_section("Balafon", s_name, seal(bal_events))
        composer.fill_voice_section("Drums", s_name, seal(drum_events))

    ok, msg = composer.validate()
    assert ok, f"Phase 2 validate failed: {msg}"

    p2_path = os.path.join(MIDI_DIR, "210-rbncc-west-african-polyrhythm.mid")
    composer.to_midi(p2_path)
    assert os.path.getsize(p2_path) > 40, "Phase 2 MIDI empty"
    print(f"Phase 2 MIDI: {p2_path} ({os.path.getsize(p2_path)} bytes)")

    write_grid_visualization(composer.matrix,
                             os.path.join(ANALYSIS_DIR, "grid_visualization.txt"),
                             ticks_per_character=240,
                             voice_names=["Gankogui", "LeadKora", "BassDunun", "Balafon", "Drums"],
                             bpm=BPM)
    print("Grid viz written to Analysis/grid_visualization.txt")

    write_provenance(p2_path, classification=AI_ASSISTED,
                     generator="musicom.workflows.unitmatrix_composer",
                     parameters={
                         "project": "210-rbncc-west-african-polyrhythm", "phase": 2,
                         "style": "West African Polyrhythms",
                         "method": "082 Random Boolean Network Criticality Composition",
                         "layer": "concrete",
                         "quantization": "16th-grid (120 ticks) + chord-tone snap",
                         "rbn": {"n": 16, "k": 2, "p": 0.5, "transient": transient_len,
                                 "cycle_len": cycle_len, "frozen_nodes": frozen},
                         "key": "G major", "bpm": BPM, "seed": SEED,
                         "progression": "I-IV-V-I / I-vi-IV-V (G major)",
                     })
    return p2_path


if __name__ == "__main__":
    traj, transient_len, cycle_len, frozen = run_rbn()
    print(f"RBN: n=16 k=2 p=0.5 | transient={transient_len} cycle={cycle_len} frozen={frozen}")
    print("=== Phase 1 raw RBN draft ===")
    generate_phase1_raw()
    print("=== Phase 2 rules composition ===")
    generate_phase2_composition()
    print("Done!")
