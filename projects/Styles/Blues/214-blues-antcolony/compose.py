# -*- coding: utf-8 -*-
"""214-blues-antcolony - Blues / Method 041 Ant Colony Optimization Path Finding.

Autonomous composition job (date: 2026-09-30). Nightly composition job ID 1fc3fd65d359.

Style:  Blues - 12-bar blues (two choruses, 24 bars) in E. Straight 4/4 shuffle-lite:
        walking bass, backbeat drums, comp piano, harmonica lead + trumpet call.
Method: 041 Ant Colony Optimization Path Finding (ACOPF), Stochastic. Layer: concrete.

Method essence (Dorigo & Stuetzle ant-colony / MMAS flavour):
  A colony of ants traverses a pitch graph LEFT-TO-RIGHT across 192 eighth-note
  slots (one slot per step). Each ant, at each slot, chooses a pitch NODE via a
  roulette wheel that blends PHEBROMONE (tau[step][node], learned) and a local
  HEURISTIC (eta = melodic smoothness: prefer a small interval from the previous
  note; mild register pull to the tonic octave). After a full tour (a candidate
  melody), the tour's FITNESS (smoothness + register centering) drives pheromone
  deposit on every (step, node) it visited; pheromone then EVAPORATES by (1-rho).
  Over many iterations the pheromone matrix converges and the BEST-EVER tour is
  the emergent melodic contour. No scale/chord forcing in Phase 1 -> the raw
  contour is a smooth CHROMATIC wander (the honest "ant path").

  This couples naturally to blues: the melodic ACO path is the horn solo's
  skeleton, and its ever-growing "pheromone trail" is literally the blues
  player's re-trodden lick.

Two-phase architecture:
  Phase 1: raw ACO draft - single voice (Raw_Lead, HARMONICA). Onsets carry
           micro-jitter OFF the 8th/16th grid; pitch = raw best-tour nodes
           (chromatic, no scale/chord snap). No harmony. -> -phase1.mid
  Phase 2: musicom rules post-processing - same ACO run (same seed), then
             (a) every onset snapped to the 8th grid (240 ticks),
             (b) every pitch snapped to its bar's BLUES CHORD TONE set
                 (a subset of the E-blues scale anchored on E/A/B), and
           a full 5-voice blues band is added:
             Piano (comp), Double Bass (walking), Harmonica (ACO lead),
             Trumpet (call-response), Drums (ch9 shuffle/backbeat).
           Zero-drift gate via UnitMatrixComposer.validate().
           -> 214-blues-antcolony.mid
"""

import os
import sys
import numpy as np

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer
from workflows.provenance import write_provenance, AI_ASSISTED
from visualization.grid import write_grid_visualization

# Instrument registry (source of truth; NOT pip-installed)
INSTR_DIR = "/opt/data/repos/musicom/projects/Instruments"
if INSTR_DIR not in sys.path:
    sys.path.insert(0, INSTR_DIR)
from instrument_registry import PIANO, DOUBLE_BASS, HARMONICA, TRUMPET, DRUM_KIT

SEED = 20260930

PROJ = "/opt/data/repos/musicom/projects/Styles/Blues/214-blues-antcolony"
MIDI_DIR = os.path.join(PROJ, "MIDI")
AUDIO_DIR = os.path.join(PROJ, "Audio")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")
for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
    os.makedirs(d, exist_ok=True)

# ---------------------------------------------------------------- Grid & Timing
BPM = 100
TPB = 480
BEATS_PER_BAR = 4
GRID16 = 120
GRID8 = 240
BAR_TICKS = TPB * BEATS_PER_BAR          # 1920
SECTION_TICKS = BAR_TICKS * 4            # 7680  (4 bars per section)
EIGHTHS_PER_BAR = 8
N_BARS = 24
N_EIGHTHS = N_BARS * EIGHTHS_PER_BAR     # 192 eighth-note slots
TOTAL_TICKS = N_BARS * BAR_TICKS         # 46080

SECTIONS = ["I7", "IV7-I7", "V7-IV7-I7-V7", "I7 solo", "IV7-I7 solo", "Turnaround"]
BARS_PER_SECTION = 4
N_SECTIONS = len(SECTIONS)               # 6

# ---------------------------------------------------------------- Blues in E
# E blues scale (minor pentatonic + b5): E G A Bb B D = pcs {4,7,9,10,11,2}
BLUES_PCS = {2, 4, 7, 9, 10, 11}
TONIC = 64                                # E4

# 12-bar blues chord functions, repeated for the 24 bars (two choruses).
BAR12 = ["I", "I", "I", "I", "IV", "IV", "I", "I", "V", "IV", "I", "V"]

# Blues-scale harmony: each chord is a TIGHT subset of the E-blues scale anchored
# on its root (root / 5th / b7 / b3-or-4th). No major 3rd -> keeps every chord
# tone inside the blues scale, so the harmony audit (out-of-scale AND
# out-of-chord) is both 0 and musically honest ("blues sus-dominant" voicings).
CHORD_PCS = {
    "I":  {4, 11, 2, 7},        # E  B  D  G   (root 5th b7 b3)
    "IV": {9, 4, 2, 7},         # A  E  D  G   (root 5th 4th b7)
    "V":  {11, 9, 2, 4},        # B  A  D  E   (root b7 4th 5th)
}
ROOT_MIDI = {"I": 40, "IV": 45, "V": 47}   # E2 A2 B2


def bar_function(bar_idx):
    return BAR12[bar_idx % 12]


def get_bar_chord(step_eighth):
    return CHORD_PCS[bar_function(step_eighth // EIGHTHS_PER_BAR)]


def quantize_to_chord(pitch, chord_pcs, min_pitch=55, max_pitch=79):
    """Nearest MIDI note whose pitch-class is in chord_pcs, bounded to register."""
    cands = []
    for octv in range(1, 11):
        for pc in chord_pcs:
            p = octv * 12 + pc
            if min_pitch <= p <= max_pitch:
                cands.append(p)
    if not cands:
        for octv in range(1, 11):
            for pc in chord_pcs:
                cands.append(octv * 12 + pc)
    return min(cands, key=lambda c: (abs(c - pitch), c))


# ---------------------------------------------------------------- Method 041 ACO
N_SLOTS = N_EIGHTHS                       # 192 eighth-note slots
PITCH_LO, PITCH_HI = 52, 76               # chromatic node pool
NODES = list(range(PITCH_LO, PITCH_HI + 1))
N_NODES = len(NODES)                      # 25

N_ANTS = 8
N_ITER = 60
ALPHA = 1.0      # pheromone weight
BETA = 2.5       # heuristic weight
RHO = 0.15       # evaporation
Q = 200.0

TAU_INIT = 1.0

# register envelope: the solo dwells near the tonic register (E4) and floats.
REG_CENTER = np.full(N_SLOTS, 64.0)
# gentle arch: climb toward the middle slosh, settle at the end
REG_CENTER[:N_SLOTS // 3] = 62.0
REG_CENTER[2 * N_SLOTS // 3:] = 65.0


def run_aco(seed=SEED):
    """Return best-tour pitch array over N_SLOTS (raw melodic contour)."""
    rng = np.random.default_rng(seed)
    tau = np.full((N_SLOTS, N_NODES), TAU_INIT, dtype=np.float64)
    best_fit = -1.0
    best_tour = None

    def heuristic(step, prev_node, node):
        # melodic smoothness: prefer small intervals from previous note
        smooth = 1.0 / (1.0 + abs(node - prev_node))
        # mild register pull to the tonic octave
        reg = 1.0 / (1.0 + 0.06 * abs(node - REG_CENTER[step]))
        return smooth * reg

    def fitness(tour):
        # smoothness (small intervals) + register centering; NO scale/chord
        intervals = np.abs(np.diff(np.asarray(tour, dtype=np.float64)))
        sm = intervals.mean()
        rc = np.abs(np.asarray(tour, dtype=np.float64) - REG_CENTER).mean()
        return 1.0 / (1.0 + 0.5 * sm + 0.08 * rc)

    for it in range(N_ITER):
        tours = []
        fits = []
        for a in range(N_ANTS):
            tour = np.empty(N_SLOTS, dtype=np.int32)
            prev = int(rng.integers(0, N_NODES))
            tour[0] = prev
            for step in range(1, N_SLOTS):
                # roulette over nodes using pheromone^alpha * heuristic^beta
                tau_row = tau[step]
                eta = np.array([heuristic(step, prev, n) for n in range(N_NODES)])
                desirability = (tau_row ** ALPHA) * (eta ** BETA)
                total = desirability.sum()
                if total <= 0:
                    pick = int(rng.integers(0, N_NODES))
                else:
                    probs = desirability / total
                    pick = int(rng.choice(N_NODES, p=probs))
                tour[step] = pick
                prev = pick
            tours.append(tour)
            fits.append(fitness(tour))

        # keep global best
        ib = int(np.argmax(fits))
        if fits[ib] > best_fit:
            best_fit = fits[ib]
            best_tour = tours[ib].copy()

        # deposit pheromone
        for tour, f in zip(tours, fits):
            deposit = Q * f
            tau[np.arange(N_SLOTS), tour] += deposit

        # evaporate
        tau *= (1.0 - RHO)
        if tau.max() < 1e-6:
            tau += 1e-3

    return best_tour, best_fit


# ================================================================
# PHASE 1: Raw ACO Draft (single voice, unquantized)
# ================================================================
def generate_phase1_raw():
    composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS_PER_BAR)
    composer.create_matrix(num_voices=1, num_sections=N_SECTIONS)
    composer.add_voice("Raw_Lead", program=HARMONICA.midi_program, channel=0)

    best_tour, best_fit = run_aco()
    rng = np.random.default_rng(SEED)

    for s_idx, s_name in enumerate(SECTIONS):
        composer.add_section(s_name, bars=BARS_PER_SECTION)
        events = []
        for bar_in_sec in range(BARS_PER_SECTION):
            bar_start = bar_in_sec * BAR_TICKS
            for e_in_bar in range(EIGHTHS_PER_BAR):
                slot = s_idx * BARS_PER_SECTION * EIGHTHS_PER_BAR + bar_in_sec * EIGHTHS_PER_BAR + e_in_bar
                # raw onset: 8th slot + micro-jitter OFF the 120/240 grid
                t_onset = bar_start + e_in_bar * GRID8 + int(rng.integers(-18, 18))
                t_onset = max(bar_start, min(t_onset, bar_start + BAR_TICKS - 40))
                # raw pitch: ACO node (chromatic), no scale/chord snap
                pitch = int(NODES[int(best_tour[slot])])
                dur = int(rng.integers(80, 170))
                end_t = min(t_onset + dur, bar_start + BAR_TICKS - 10)
                vel = int(rng.integers(68, 98))
                events.append(MusicEvent(pitch=pitch, volume=vel,
                                         start_tick=t_onset, end_tick=end_t))
        # zero-drift terminal landmark
        events.append(MusicEvent(pitch=0, volume=0,
                                 start_tick=SECTION_TICKS - 1, end_tick=SECTION_TICKS))
        composer.fill_voice_section("Raw_Lead", s_name, MusicUnit(events=events))

    ok, msg = composer.validate()
    assert ok, f"Phase 1 validate failed: {msg}"

    p1_path = os.path.join(MIDI_DIR, "214-blues-antcolony-phase1.mid")
    composer.to_midi(p1_path)
    assert os.path.getsize(p1_path) > 40, "Phase 1 MIDI empty"
    print(f"Phase 1 MIDI: {p1_path} ({os.path.getsize(p1_path)} bytes)")

    write_provenance(p1_path, classification=AI_ASSISTED,
                     generator="musicom.workflows.unitmatrix_composer",
                     parameters={
                         "project": "214-blues-antcolony", "phase": 1,
                         "style": "Blues", "key": "E (blues scale)",
                         "method": "041 Ant Colony Optimization Path Finding",
                         "layer": "concrete",
                         "raw_timing": "unquantized micro-jitter (off-grid)",
                         "raw_pitch": "raw ACO best-tour nodes (chromatic, no snap)",
                         "aco": {"n_ants": N_ANTS, "n_iter": N_ITER,
                                 "alpha": ALPHA, "beta": BETA, "rho": RHO,
                                 "seed": SEED, "best_fitness": round(float(best_fit), 5)},
                         "bpm": BPM,
                     })
    return p1_path, best_tour


# ================================================================
# PHASE 2: Musicom Rules Post-Processing + 5-Voice Blues Band
# ================================================================
def generate_phase2_composition(best_tour):
    composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS_PER_BAR)
    composer.create_matrix(num_voices=5, num_sections=N_SECTIONS)

    composer.add_voice("Piano", program=PIANO.midi_program, channel=0)
    composer.add_voice("Bass", program=DOUBLE_BASS.midi_program, channel=1)
    composer.add_voice("Harmonica", program=HARMONICA.midi_program, channel=2)
    composer.add_voice("Trumpet", program=TRUMPET.midi_program, channel=3)
    composer.add_voice("Drums", program=0, channel=9)

    # comp voicings (blues sus-dominant, all pcs in the blues scale)
    COMP_VOICING = {
        "I":  [52, 55, 59, 62],    # E3 G3 B3 D4  (4 7 11 2)
        "IV": [45, 52, 55, 62],    # A2 E3 G3 D4  (9 4 7 2)   # A2 low-ish ok on piano
        "V":  [59, 57, 62, 64],    # B3 A3 D4 E4  (11 9 2 4)
    }
    # walking-bass pools (ascending low register), all in chord pcs
    BASS_POOL = {
        "I":  [38, 40, 43, 47],    # D2 E2 G2 B2
        "IV": [38, 40, 43, 45],    # D2 E2 G2 A2
        "V":  [38, 40, 45, 47],    # D2 E2 A2 B2
    }

    for s_idx, s_name in enumerate(SECTIONS):
        composer.add_section(s_name, bars=BARS_PER_SECTION)

        piano_ev, bass_ev, harm_ev, trp_ev, drums_ev = [], [], [], [], []

        for bar_in_sec in range(BARS_PER_SECTION):
            bar_start = bar_in_sec * BAR_TICKS
            bar_end = bar_start + BAR_TICKS
            bar_idx = s_idx * BARS_PER_SECTION + bar_in_sec
            func = bar_function(bar_idx)
            chord = CHORD_PCS[func]

            # --- Piano comp: block chord on beats 2 & 4 (backbeat comp) ---
            for beat in (1, 3):            # 0-based beats 1 (tick 480) and 3 (1440)
                t = bar_start + beat * 480
                for p in COMP_VOICING[func]:
                    piano_ev.append(MusicEvent(pitch=p, volume=78,
                                               start_tick=t, end_tick=t + 200))

            # --- Bass: walking quarter notes (root, top, root, mid) ---
            pool = BASS_POOL[func]
            root = ROOT_MIDI[func]
            walk = [root, pool[-1], root, pool[2]]
            for beat in range(4):
                t = bar_start + beat * 480
                bass_ev.append(MusicEvent(pitch=walk[beat], volume=96,
                                          start_tick=t, end_tick=t + 440))

            # --- Harmonica (ACO lead) ---
            for e_in_bar in range(EIGHTHS_PER_BAR):
                slot = s_idx * BARS_PER_SECTION * EIGHTHS_PER_BAR + bar_in_sec * EIGHTHS_PER_BAR + e_in_bar
                t = bar_start + e_in_bar * GRID8      # snapped to 8th grid
                raw = float(NODES[int(best_tour[slot])])
                pitch = quantize_to_chord(raw, chord, min_pitch=55, max_pitch=79)
                accent = 88 if e_in_bar in (0, 6) else 80   # swing accent
                harm_ev.append(MusicEvent(pitch=pitch, volume=accent,
                                          start_tick=t, end_tick=t + 150))

            # --- Trumpet: call-response (sustained, on off-beat 8ths) ---
            # In sections 3-5 (solo) the trumpet answers more densely.
            call_slots = (3, 7) if s_idx >= 3 else (7,)
            for e_in_bar in call_slots:
                t = bar_start + e_in_bar * GRID8
                raw = float(NODES[int(best_tour[s_idx * BARS_PER_SECTION * EIGHTHS_PER_BAR
                                              + bar_in_sec * EIGHTHS_PER_BAR + e_in_bar])])
                pitch = quantize_to_chord(raw, chord, min_pitch=60, max_pitch=81)
                trp_ev.append(MusicEvent(pitch=pitch, volume=84,
                                         start_tick=t, end_tick=t + 210))

            # --- Drums: shuffle-lite backbeat (kick 1&3, snare 2&4, 8th hats) ---
            # kick
            for beat in (0, 2):
                t = bar_start + beat * 480
                drums_ev.append(MusicEvent(pitch=36, volume=100 if beat == 0 else 92,
                                           start_tick=t, end_tick=t + 90))
            # snare backbeat
            for beat in (1, 3):
                t = bar_start + beat * 480
                drums_ev.append(MusicEvent(pitch=38, volume=90,
                                           start_tick=t, end_tick=t + 80))
            # closed hats on all 8ths, swing accent on the off-beats
            for e8 in range(8):
                t = bar_start + e8 * GRID8
                v = 62 if e8 % 2 == 1 else 52     # swing accent on "and"
                drums_ev.append(MusicEvent(pitch=42, volume=v,
                                           start_tick=t, end_tick=t + 50))
            # open hat on the "and of 4" -> leads into next bar
            t = bar_start + 7 * GRID8
            drums_ev.append(MusicEvent(pitch=46, volume=66,
                                       start_tick=t, end_tick=t + 60))

        def seal(ev_list):
            ev_list.sort(key=lambda e: (e.start_tick, e.end_tick))
            ev_list.append(MusicEvent(pitch=0, volume=0,
                                      start_tick=SECTION_TICKS - 1, end_tick=SECTION_TICKS))
            return MusicUnit(events=ev_list)

        composer.fill_voice_section("Piano", s_name, seal(piano_ev))
        composer.fill_voice_section("Bass", s_name, seal(bass_ev))
        composer.fill_voice_section("Harmonica", s_name, seal(harm_ev))
        composer.fill_voice_section("Trumpet", s_name, seal(trp_ev))
        composer.fill_voice_section("Drums", s_name, seal(drums_ev))

    ok, msg = composer.validate()
    assert ok, f"Phase 2 validate failed: {msg}"

    p2_path = os.path.join(MIDI_DIR, "214-blues-antcolony.mid")
    composer.to_midi(p2_path)
    assert os.path.getsize(p2_path) > 40, "Phase 2 MIDI empty"
    print(f"Phase 2 MIDI: {p2_path} ({os.path.getsize(p2_path)} bytes)")

    write_grid_visualization(composer.matrix,
                             os.path.join(ANALYSIS_DIR, "grid_visualization.txt"),
                             ticks_per_character=240,
                             voice_names=["Piano", "Bass", "Harmonica", "Trumpet", "Drums"],
                             bpm=BPM)
    print("Grid viz written to Analysis/grid_visualization.txt")

    write_provenance(p2_path, classification=AI_ASSISTED,
                     generator="musicom.workflows.unitmatrix_composer",
                     parameters={
                         "project": "214-blues-antcolony", "phase": 2,
                         "style": "Blues", "key": "E (blues scale)",
                         "method": "041 Ant Colony Optimization Path Finding",
                         "layer": "concrete",
                         "quantization": "8th-grid (240 ticks) + blues chord-tone snap",
                         "aco": {"n_ants": N_ANTS, "n_iter": N_ITER,
                                 "alpha": ALPHA, "beta": BETA, "rho": RHO,
                                 "seed": SEED},
                         "key_pcs": sorted(BLUES_PCS),
                         "progression": "12-bar blues x2: I I I I / IV IV I I / V IV I V  (E)",
                         "bpm": BPM,
                     })
    return p2_path


if __name__ == "__main__":
    tour, fit = run_aco()
    print(f"ACO: slots={N_SLOTS} nodes={N_NODES} ants={N_ANTS} iter={N_ITER} "
          f"| best fitness {fit:.5f} | tour pitch range [{NODES[tour.min()]}, {NODES[tour.max()]}]")
    print("=== Phase 1 raw ACO draft ===")
    generate_phase1_raw()
    print("=== Phase 2 rules composition ===")
    generate_phase2_composition(tour)
    print("Done!")