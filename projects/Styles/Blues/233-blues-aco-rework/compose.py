# -*- coding: utf-8 -*-
"""233-blues-aco-rework -- Rework of 214-blues-antcolony (nightly rework agent).

Source: Blues/214-blues-antcolony. Audit FAILED standard 6 (no top-level
provenance.json, no index.html). Decision: REDESIGN from scratch through the
canonical UnitMatrixComposer workflow, preserving identity only:

  Blues / E blues scale {2,4,7,9,10,11} / 100 BPM / 4-4 / Method 041 ACOPF /
  5-voice band (Piano, Bass, Harmonica, Trumpet, Drums ch9).

New (longer + more varied): 32 bars = 8 sections x 4 bars (source: 24 = 6).
Variation techniques (6): augmentation, transposition (+5), register shift
(+12), inversion, retrograde, density rise/fall -- each mapped to a section.
"""
import os
import json
import numpy as np

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer
from workflows.provenance import write_provenance, AI_ASSISTED
from visualization.grid import write_grid_visualization

# Instrument registry (source of truth; NOT pip-installed)
INSTR_DIR = "/opt/data/repos/musicom/projects/Instruments"
import sys
if INSTR_DIR not in sys.path:
    sys.path.insert(0, INSTR_DIR)
from instrument_registry import PIANO, DOUBLE_BASS, HARMONICA, TRUMPET, DRUM_KIT

SEED = 20261010
PROJ = "/opt/data/projects/Styles/Blues/233-blues-aco-rework"
MIDI_DIR = os.path.join(PROJ, "MIDI")
AUDIO_DIR = os.path.join(PROJ, "Audio")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")
for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
    os.makedirs(d, exist_ok=True)

BPM = 100
TPB = 480
BEATS_PER_BAR = 4
GRID16 = 120
GRID8 = 240
BAR_TICKS = TPB * BEATS_PER_BAR          # 1920
SECTION_TICKS = BAR_TICKS * 4            # 7680
EIGHTHS_PER_BAR = 8

# ------------------------------------------------------------- Blues in E
BLUES_PCS = {2, 4, 7, 9, 10, 11}
TONIC = 64                                # E4

# Chord-tone subsets of the E-blues scale (blues sus-dominant voicings):
CHORD_PCS = {
    "I":  {4, 11, 2, 7},        # E B D G
    "IV": {9, 4, 2, 7},         # A E D G
    "V":  {11, 9, 2, 4},        # B A D E
}
ROOT_MIDI = {"I": 40, "IV": 45, "V": 47}
COMP_VOICING = {
    "I":  [52, 55, 59, 62],     # E3 G3 B3 D4
    "IV": [45, 52, 55, 62],     # A2 E3 G3 D4
    "V":  [59, 57, 62, 64],     # B3 A3 D4 E4
}
BASS_POOL = {
    "I":  [38, 40, 43, 47],     # D2 E2 G2 B2
    "IV": [38, 40, 43, 45],     # D2 E2 G2 A2
    "V":  [38, 40, 45, 47],     # D2 E2 A2 B2
}

# ------------------------------------------------------- 8 sections x 4 bars
SECTIONS = ["Intro", "Verse1", "Verse2", "Chorus", "Solo1", "Solo2", "Bridge", "Outro"]
N_SECTIONS = len(SECTIONS)                 # 8
N_BARS = N_SECTIONS * 4                    # 32
N_SLOTS = N_BARS * EIGHTHS_PER_BAR         # 256 eighth-note slots

# Per-bar harmonic function (each section its own short progression).
BAR_FUNC = [
    "I", "IV", "I", "V",          # Intro  (midpoint IV)
    "I", "I", "IV", "I",          # Verse1 (midpoint I)
    "IV", "IV", "I", "I",         # Verse2 (midpoint IV)
    "V", "IV", "I", "V",          # Chorus (midpoint IV)
    "I", "IV", "V", "IV",         # Solo1  (midpoint IV)
    "IV", "I", "V", "I",          # Solo2  (midpoint I)
    "V", "V", "IV", "I",          # Bridge (midpoint V)
    "I", "V", "IV", "I",          # Outro  (midpoint V)
]
assert len(BAR_FUNC) == N_BARS

# Section midpoint degree (bar index 1 of each section) -> section root.
SECTION_MID_DEG = [BAR_FUNC[s * 4 + 1] for s in range(N_SECTIONS)]
SECTION_ROOTS = [ROOT_MIDI[d] for d in SECTION_MID_DEG]

# Lead variation style per section (6 distinct techniques).
LEAD_STYLE = [
    "aug",         # Intro:    augmentation (half-speed, sparse)
    "identity",    # Verse1:   head statement
    "identity",    # Verse2:   call-response
    "identity",    # Chorus:   full, higher register
    "reg+12",      # Solo1:    register shift +1 octave
    "trans+5",     # Solo2:    transposition +5 (up a perfect 4th)
    "inv_aug",     # Bridge:   inversion + augmentation
    "retro_thin",  # Outro:    retrograde + thinning
]
LEAD_REG = {      # (min, max) quantize register per section
    0: (55, 79), 1: (55, 79), 2: (55, 79), 3: (60, 84),
    4: (67, 91), 5: (60, 84), 6: (55, 79), 7: (55, 79),
}


def bar_function(bar_idx):
    return BAR_FUNC[bar_idx]


def quantize_to_chord(pitch, chord_pcs, min_pitch=55, max_pitch=84):
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


# --------------------------------------------------------------- ACO (041)
PITCH_LO, PITCH_HI = 52, 76
NODES = list(range(PITCH_LO, PITCH_HI + 1))
N_NODES = len(NODES)                      # 25
N_ANTS = 8
N_ITER = 60
ALPHA = 1.0
BETA = 2.5
RHO = 0.15
Q = 200.0
TAU_INIT = 1.0

REG_CENTER = np.full(N_SLOTS, 64.0)
REG_CENTER[:N_SLOTS // 3] = 62.0
REG_CENTER[2 * N_SLOTS // 3:] = 65.0


def run_aco(seed=SEED):
    rng = np.random.default_rng(seed)
    tau = np.full((N_SLOTS, N_NODES), TAU_INIT, dtype=np.float64)
    best_fit = -1.0
    best_tour = None

    def heuristic(step, prev_node, node):
        smooth = 1.0 / (1.0 + abs(node - prev_node))
        reg = 1.0 / (1.0 + 0.06 * abs(node - REG_CENTER[step]))
        return smooth * reg

    def fitness(tour):
        intervals = np.abs(np.diff(np.asarray(tour, dtype=np.float64)))
        sm = intervals.mean()
        rc = np.abs(np.asarray(tour, dtype=np.float64) - REG_CENTER).mean()
        return 1.0 / (1.0 + 0.5 * sm + 0.08 * rc)

    for _ in range(N_ITER):
        tours, fits = [], []
        for _ in range(N_ANTS):
            tour = np.empty(N_SLOTS, dtype=np.int32)
            prev = int(rng.integers(0, N_NODES))
            tour[0] = prev
            for step in range(1, N_SLOTS):
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
        ib = int(np.argmax(fits))
        if fits[ib] > best_fit:
            best_fit = fits[ib]
            best_tour = tours[ib].copy()
        for tour, f in zip(tours, fits):
            tau[np.arange(N_SLOTS), tour] += Q * f
        tau *= (1.0 - RHO)
        if tau.max() < 1e-6:
            tau += 1e-3
    return best_tour, best_fit


# ------------------------------------------------- PHASE 1: raw ACO draft
def generate_phase1_raw():
    composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS_PER_BAR)
    composer.create_matrix(num_voices=1, num_sections=N_SECTIONS)
    composer.add_voice("Raw_Lead", program=HARMONICA.midi_program, channel=0)
    best_tour, best_fit = run_aco()
    rng = np.random.default_rng(SEED)

    for s_idx, s_name in enumerate(SECTIONS):
        composer.add_section(s_name, bars=4)
        events = []
        for bar_in_sec in range(4):
            bar_start = bar_in_sec * BAR_TICKS
            for e_in_bar in range(EIGHTHS_PER_BAR):
                slot = s_idx * 32 + bar_in_sec * EIGHTHS_PER_BAR + e_in_bar
                t_onset = bar_start + e_in_bar * GRID8 + int(rng.integers(-18, 18))
                t_onset = max(bar_start, min(t_onset, bar_start + BAR_TICKS - 40))
                pitch = int(NODES[int(best_tour[slot])])
                dur = int(rng.integers(80, 170))
                end_t = min(t_onset + dur, bar_start + BAR_TICKS - 10)
                vel = int(rng.integers(68, 98))
                events.append(MusicEvent(pitch=pitch, volume=vel,
                                         start_tick=t_onset, end_tick=end_t))
        events.append(MusicEvent(pitch=0, volume=0,
                                 start_tick=SECTION_TICKS - 1, end_tick=SECTION_TICKS))
        composer.fill_voice_section("Raw_Lead", s_name, MusicUnit(events=events))

    ok, msg = composer.validate()
    assert ok, "Phase 1 validate failed: " + msg
    p1_path = os.path.join(MIDI_DIR, "233-blues-aco-rework-phase1.mid")
    composer.to_midi(p1_path)
    assert os.path.getsize(p1_path) > 40, "Phase 1 MIDI empty"
    write_provenance(p1_path, classification=AI_ASSISTED,
                     generator="musicom.workflows.unitmatrix_composer",
                     parameters={
                         "project": "233-blues-aco-rework", "phase": 1,
                         "style": "Blues", "key": "E (blues scale)",
                         "method": "041 ACOPF", "layer": "concrete",
                         "raw_timing": "unquantized micro-jitter (off-grid)",
                         "raw_pitch": "raw ACO best-tour nodes (chromatic)",
                         "aco": {"n_ants": N_ANTS, "n_iter": N_ITER,
                                 "alpha": ALPHA, "beta": BETA, "rho": RHO,
                                 "seed": SEED, "best_fitness": round(float(best_fit), 5)},
                         "bpm": BPM})
    print("Phase 1 MIDI:", p1_path, os.path.getsize(p1_path), "bytes")
    return p1_path, best_tour


# -------------------------------------------------- PHASE 2: rules + band
def transform_raw(raw, style):
    if "trans+5" in style:
        return raw + 5
    if "reg+12" in style:
        return raw + 12
    if "inv" in style:
        return 2 * TONIC - raw
    return raw


def generate_phase2_composition(best_tour):
    composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS_PER_BAR)
    composer.create_matrix(num_voices=5, num_sections=N_SECTIONS)
    composer.add_voice("Piano", program=PIANO.midi_program, channel=0)
    composer.add_voice("Bass", program=DOUBLE_BASS.midi_program, channel=1)
    composer.add_voice("Harmonica", program=HARMONICA.midi_program, channel=2)
    composer.add_voice("Trumpet", program=TRUMPET.midi_program, channel=3)
    composer.add_voice("Drums", program=0, channel=9)

    # Pre-compute per-section raw contour (32 chromatic pitches), section-level
    # transforms (retrograde) applied here; note-level transforms in the loop.
    section_raw = {}
    for s_idx in range(N_SECTIONS):
        sl = [float(NODES[int(best_tour[s_idx * 32 + k])]) for k in range(32)]
        if "retro" in LEAD_STYLE[s_idx]:
            sl = sl[::-1]
        section_raw[s_idx] = sl

    roots_per_bar = []

    for s_idx, s_name in enumerate(SECTIONS):
        composer.add_section(s_name, bars=4)
        style = LEAD_STYLE[s_idx]
        lo, hi = LEAD_REG[s_idx]
        piano_ev, bass_ev, harm_ev, trp_ev, drums_ev = [], [], [], [], []

        for bar_in_sec in range(4):
            bar_start = bar_in_sec * BAR_TICKS
            bar_end = bar_start + BAR_TICKS
            bar_idx = s_idx * 4 + bar_in_sec
            func = bar_function(bar_idx)
            chord = CHORD_PCS[func]
            roots_per_bar.append(ROOT_MIDI[func])

            # Piano comp: block chord beats 2 & 4 (backbeat)
            for beat in (1, 3):
                t = bar_start + beat * 480
                for p in COMP_VOICING[func]:
                    piano_ev.append(MusicEvent(pitch=p, volume=78,
                                               start_tick=t, end_tick=t + 200))

            # Bass: walking quarters (root, top, root, mid)
            pool = BASS_POOL[func]
            root = ROOT_MIDI[func]
            walk = [root, pool[-1], root, pool[2]]
            for beat in range(4):
                t = bar_start + beat * 480
                bass_ev.append(MusicEvent(pitch=walk[beat], volume=96,
                                          start_tick=t, end_tick=t + 440))

            # Harmonica lead (ACO contour, transformed + chord-snapped + grid)
            for e_in_bar in range(EIGHTHS_PER_BAR):
                idx = bar_in_sec * EIGHTHS_PER_BAR + e_in_bar
                raw = transform_raw(section_raw[s_idx][idx], style)
                t = bar_start + e_in_bar * GRID8            # 8th grid
                accent = 88 if e_in_bar in (0, 6) else 80
                if "aug" in style:
                    # rhythmic augmentation: only even 8ths, double duration
                    if e_in_bar % 2 == 0:
                        pitch = quantize_to_chord(raw, chord, min_pitch=lo, max_pitch=hi)
                        harm_ev.append(MusicEvent(pitch=pitch, volume=84,
                                                  start_tick=t, end_tick=t + 2 * GRID8))
                elif "thin" in style:
                    # thinning: quarter-note feel (slots 0,2,4,6)
                    if e_in_bar in (0, 2, 4, 6):
                        pitch = quantize_to_chord(raw, chord, min_pitch=lo, max_pitch=hi)
                        harm_ev.append(MusicEvent(pitch=pitch, volume=80,
                                                  start_tick=t, end_tick=t + 150))
                else:
                    pitch = quantize_to_chord(raw, chord, min_pitch=lo, max_pitch=hi)
                    harm_ev.append(MusicEvent(pitch=pitch, volume=accent,
                                              start_tick=t, end_tick=t + 150))

            # Trumpet call-response / counterline
            if "aug" in style:
                # slow sustained counterline (augmented) in Bridge/Intro
                for e_in_bar in (1, 5):
                    idx = bar_in_sec * EIGHTHS_PER_BAR + e_in_bar
                    raw = transform_raw(section_raw[s_idx][idx], style)
                    t = bar_start + e_in_bar * GRID8
                    pitch = quantize_to_chord(raw, chord, min_pitch=60, max_pitch=81)
                    trp_ev.append(MusicEvent(pitch=pitch, volume=74,
                                             start_tick=t, end_tick=t + 2 * GRID8))
            else:
                if s_idx == 4:      # Solo1: trumpet answers dense (register up)
                    call_slots = (2, 5, 7)
                elif s_idx == 5:    # Solo2: trumpet answers dense
                    call_slots = (2, 5, 7)
                elif s_idx == 3:    # Chorus: answer both off-beats
                    call_slots = (3, 7)
                else:
                    call_slots = (7,)
                for e_in_bar in call_slots:
                    idx = bar_in_sec * EIGHTHS_PER_BAR + e_in_bar
                    raw = transform_raw(section_raw[s_idx][idx], style)
                    t = bar_start + e_in_bar * GRID8
                    pitch = quantize_to_chord(raw, chord, min_pitch=60, max_pitch=81)
                    trp_ev.append(MusicEvent(pitch=pitch, volume=84,
                                             start_tick=t, end_tick=t + 210))

            # Drums: shuffle-lite backbeat with per-section density
            dense = {"Intro": 0, "Verse1": 1, "Verse2": 1, "Chorus": 2,
                     "Solo1": 2, "Solo2": 2, "Bridge": 0, "Outro": 0}[s_name]
            for beat in (0, 2):
                if dense >= 1 or beat == 0:
                    t = bar_start + beat * 480
                    drums_ev.append(MusicEvent(pitch=36, volume=100 if beat == 0 else 92,
                                               start_tick=t, end_tick=t + 90))
            for beat in (1, 3):
                if dense >= 1:
                    t = bar_start + beat * 480
                    drums_ev.append(MusicEvent(pitch=38, volume=90,
                                               start_tick=t, end_tick=t + 80))
            for e8 in range(8):
                if dense >= 1:
                    t = bar_start + e8 * GRID8
                    v = 62 if e8 % 2 == 1 else 52
                    drums_ev.append(MusicEvent(pitch=42, volume=v,
                                               start_tick=t, end_tick=t + 50))
            t = bar_start + 7 * GRID8
            drums_ev.append(MusicEvent(pitch=46, volume=66 if dense >= 1 else 50,
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
    assert ok, "Phase 2 validate failed: " + msg

    p2_path = os.path.join(MIDI_DIR, "233-blues-aco-rework.mid")
    composer.to_midi(p2_path)
    assert os.path.getsize(p2_path) > 40, "Phase 2 MIDI empty"

    write_grid_visualization(composer.matrix,
                             os.path.join(ANALYSIS_DIR, "grid_visualization.txt"),
                             ticks_per_character=240,
                             voice_names=["Piano", "Bass", "Harmonica", "Trumpet", "Drums"],
                             bpm=BPM)

    write_provenance(p2_path, classification=AI_ASSISTED,
                     generator="musicom.workflows.unitmatrix_composer",
                     parameters={
                         "project": "233-blues-aco-rework", "phase": 2,
                         "style": "Blues", "key": "E (blues scale)",
                         "method": "041 ACOPF", "layer": "concrete",
                         "quantization": "8th-grid (240) + blues chord-tone snap",
                         "aco": {"n_ants": N_ANTS, "n_iter": N_ITER,
                                 "alpha": ALPHA, "beta": BETA, "rho": RHO, "seed": SEED},
                         "key_pcs": sorted(BLUES_PCS),
                         "per_section_roots": SECTION_ROOTS,
                         "bpm": BPM})

    print("Phase 2 MIDI:", p2_path, os.path.getsize(p2_path), "bytes")
    print("roots_per_bar (32):", roots_per_bar)
    print("section_midpoint_degrees:", SECTION_MID_DEG)
    print("section_roots:", SECTION_ROOTS)
    return p2_path


# ------------------------------------------------ top-level sidecars (std6)
def write_sidecars(best_fit):
    prov = {
        "project": "233-blues-aco-rework",
        "source": "Blues/214-blues-antcolony (redesign: std6 provenance.json + index.html missing)",
        "decision": "redesign",
        "genre": "Blues", "key": "E blues scale {2,4,7,9,10,11}",
        "bpm": BPM, "meter": "4/4", "bars": N_BARS, "sections": SECTIONS,
        "method": "041 ACOPF", "seed": SEED, "best_fitness": round(float(best_fit), 5),
        "variation_techniques": {
            "Intro": "augmentation (half-speed sparse)",
            "Solo1": "register shift (+12, octave up)",
            "Solo2": "transposition (+5, perfect 4th)",
            "Bridge": "inversion + augmentation",
            "Outro": "retrograde + thinning",
            "Chorus": "density rise (full band)",
        },
        "per_section_roots": SECTION_ROOTS,
        "per_section_midpoint_degree": SECTION_MID_DEG,
        "engine": "musicom.workflows.unitmatrix_composer",
    }
    with open(os.path.join(PROJ, "provenance.json"), "w") as f:
        json.dump(prov, f, indent=2)
    print("Wrote provenance.json")


if __name__ == "__main__":
    tour, fit = run_aco()
    print("ACO: slots=%d nodes=%d ants=%d iter=%d | best fit %.5f | range [%d,%d]"
          % (N_SLOTS, N_NODES, N_ANTS, N_ITER, fit, NODES[tour.min()], NODES[tour.max()]))
    print("=== Phase 1 raw ACO draft ===")
    generate_phase1_raw()
    print("=== Phase 2 rules composition ===")
    generate_phase2_composition(tour)
    write_sidecars(fit)
    print("Done!")
