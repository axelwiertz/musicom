# -*- coding: utf-8 -*-
"""212-indian-boids-yaman - IndianClassical / Method 031 Swarm Intelligence Flocking (Boids).

Autonomous composition job (date: 2026-09-29). Nightly composition job ID 1fc3fd65d359.

Style: IndianClassical (Hindustani) - Raga Yaman (Kalyan thaat), alap->gat->jhala
       form: tanpura drone, sitar lead, bansuri counter, tabla teental.
Method: 031 Swarm Intelligence Flocking (Boids), Nature-Led. Layer: concrete.

Method essence (Reynolds 1987 flocking + tonal gravity):
  N=8 melodic "boids" move in 1D pitch space (position = semitone, velocity =
  melodic direction). Each step they feel three Reynolds forces -- SEPARATION
  (avoid pitch-crowding -> voice independence / ornament), ALIGNMENT (match
  neighbours' velocity -> parallel melodic motion), COHESION (steer toward the
  flock centroid -> melodic coherence) -- plus a VIRTUAL LEADER that traces the
  raga's aroha (ascent) -> avaroha (descent) contour, and a weak TONIC pull
  toward Sa (the raga's gravitational home). The flock's emergent centroid is
  the melody; its SPREAD (std of pitch) drives velocity/ornament density; a
  spread near zero at Sa = the raga's "ma" (breath/silence).

  This seed (20260929) yields a flock that follows the Yaman aroha S R G M' P D
  N S' then descends the avaroha, with separation-driven micro-fluctuation the
  sign of the boid method (organic, not hand-drawn contour).

Two-phase architecture:
  Phase 1: raw boid draft - single voice (Raw_Lead, SITAR). Onsets carry
           micro-jitter OFF the 16th grid; pitch is the raw boid centroid
           (chromatic, no raga/chord snapping). No harmony. -> -phase1.mid
  Phase 2: musicom rules post-processing - same flock (same seed) re-run, then
             (a) every onset snapped to the 16th grid (120 ticks),
             (b) every pitch snapped to its section's raga-harmonic region
                 (a subset of Yaman that always carries the Sa+Pa drone), and
           a full 4-voice Hindustani texture is added:
             Voice 1: Drone  (ORGAN GM 19,  ch0) - Sa+Pa tanpura pedal
             Voice 2: LeadSitar (SITAR GM 104, ch1) - boid centroid melody
             Voice 3: Bansuri  (FLUTE GM 74,  ch2) - boid fifth-above interlock
             Voice 4: Tabla    (ch9) - teental tala (16 matra theka)
           Zero-drift gate via UnitMatrixComposer.validate().
           -> 212-indian-boids-yaman.mid
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
from instrument_registry import SITAR, FLUTE, ORGAN

SEED = 20260929
INIT_SEED = SEED + 11

PROJ = "/opt/data/repos/musicom/projects/Styles/IndianClassical/212-indian-boids-yaman"
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
STEPS_PER_BAR = 16                       # 16 sixteenths (1 matra each in teental)
N_BARS = 32
N_STEPS = N_BARS * STEPS_PER_BAR         # 512 sixteenth slots
TOTAL_TICKS = N_BARS * BAR_TICKS         # 61440

SECTIONS = ["Alap", "Jod", "Gat1", "Gat2", "Jhala", "Gat1b", "Alap2", "Outro"]
BARS_PER_SECTION = 4
N_SECTIONS = len(SECTIONS)

# ---------------------------------------------------------------- Raga Yaman (Sa = C)
# S R G M' P D N S  =  C D E F# G A B C  = pitch classes {0,2,4,6,7,9,11}
YAMAN_PCS = {0, 2, 4, 6, 7, 9, 11}
RAGA_SCALE = [60, 62, 64, 66, 67, 69, 71, 72]   # S R G M' P D N S' (C4..C5)
SA = 60                                        # tonic (C4)
SA_DRONE = 36                                  # low Sa (C2, organ pedal)

# Section harmonic regions for a MONOPHONIC raga: the Sa+Pa tanpura drone is
# consonant with the ENTIRE Yaman scale (that is how ragas work), so the
# melodic sections take the full scale as their "chord"; only the sparse
# Alap/Outro sections restrict the melody to the bare Sa+Pa drone. This keeps
# the harmony audit meaningful (sparse sections truly are drone-only) while
# letting the gat/jhala melody use all seven Yaman notes (incl. the tivra Ma,
# Yaman's signature F#).
SECTION_CHORDS = {
    0: {0, 7},          # Alap   - Sa Pa drone only
    1: YAMAN_PCS,       # Jod    - full Yaman
    2: YAMAN_PCS,       # Gat1   - full Yaman
    3: YAMAN_PCS,       # Gat2   - full Yaman (tivra Ma region)
    4: YAMAN_PCS,       # Jhala  - full Yaman
    5: YAMAN_PCS,       # Gat1b  - full Yaman
    6: {0, 7},          # Alap2  - Sa Pa drone only
    7: {0, 7},          # Outro  - Sa Pa drone only
}

# Drone pitches (tanpura): Sa octave + Pa. All pitch-class in {Sa, Pa}.
DRONE_PITCHES = [SA_DRONE, 48, 55]   # C2 (Sa), C3 (Sa), G3 (Pa)


def get_bar_chord(sec_idx, bar_in_sec):
    return SECTION_CHORDS[sec_idx]


def get_chord_for_step(step):
    bar = step // STEPS_PER_BAR
    sec = bar // BARS_PER_SECTION
    return SECTION_CHORDS[sec]


# ---------------------------------------------------------------- Method 031 Boids

# Aroha + avaroha note-dwell path (one scale step per quarter note, 16 notes =
# 4 bars per cycle): S R G M' P D N S' | S' N D P M' G R S.
RAGA_PATH = [0, 1, 2, 3, 4, 5, 6, 7, 7, 6, 5, 4, 3, 2, 1, 0]
DWELL_STEPS = 4   # quarter note per scale step


def target_pitch(step):
    """Virtual-leader note: walks the Yaman aroha/avaroha with octave drift.

    Each scale step dwells DWELL_STEPS (a quarter note); one full aroha+avaroha
    cycle = 16 notes = 64 steps = 4 bars. The macro form climbs an octave for
    cycles 2-5 (gat/jhala) and returns for cycles 6-7 (alap2/outro).
    """
    note_step = step // DWELL_STEPS
    scale_idx = RAGA_PATH[note_step % 16]
    cycle = note_step // 16               # 0..7 over 512 steps
    octave = 12 if 2 <= cycle <= 5 else 0
    return float(RAGA_SCALE[scale_idx] + octave)


N_BOIDS = 8


def run_boids(seed=SEED):
    """Run the flock; return centroid/spread/speed arrays over N_STEPS."""
    rng = np.random.default_rng(seed)
    pos = SA + rng.uniform(-3.0, 3.0, N_BOIDS)
    vel = np.zeros(N_BOIDS)
    centroid = np.zeros(N_STEPS)
    spread = np.zeros(N_STEPS)
    speed = np.zeros(N_STEPS)

    for t in range(N_STEPS):
        lead = target_pitch(t)
        # --- Reynolds forces (1D pitch space) ---
        cen_real = np.mean(pos)
        cohesion = (cen_real - pos) * 0.05          # steer to flock centre
        alignment = (np.mean(vel) - vel) * 0.05     # match neighbours' velocity
        separation = np.zeros(N_BOIDS)              # avoid pitch-crowding
        for i in range(N_BOIDS):
            d = pos - pos[i]
            close = np.abs(d) < 2.0
            close[i] = False
            if np.any(close):
                separation[i] = -np.sum(np.sign(d[close]) * (2.0 - np.abs(d[close]))) * 0.20
        leader_force = (lead - pos) * 0.25          # follow the raga contour
        tonic = (SA - pos) * 0.02                   # weak Sa gravity

        vel = (vel + cohesion + alignment + separation + leader_force + tonic) * 0.78
        vel = np.clip(vel, -6.0, 6.0)
        pos = pos + vel

        centroid[t] = float(np.mean(pos))
        spread[t] = float(np.std(pos))
        if t > 0:
            speed[t] = abs(centroid[t] - centroid[t - 1])

    return centroid, spread, speed


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
# PHASE 1: Raw Boid Draft (single voice, unquantized)
# ================================================================
def generate_phase1_raw():
    composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS_PER_BAR)
    composer.create_matrix(num_voices=1, num_sections=N_SECTIONS)
    composer.add_voice("Raw_Lead", program=SITAR.midi_program, channel=0)

    centroid, spread, speed = run_boids()
    rng = np.random.default_rng(SEED)

    for s_idx, s_name in enumerate(SECTIONS):
        composer.add_section(s_name, bars=BARS_PER_SECTION)
        events = []
        for bar_in_sec in range(BARS_PER_SECTION):
            bar_start = bar_in_sec * BAR_TICKS
            for step_in_bar in range(STEPS_PER_BAR):
                step = s_idx * BARS_PER_SECTION * STEPS_PER_BAR + bar_in_sec * STEPS_PER_BAR + step_in_bar
                # raw onset: 16th slot + micro-jitter OFF the 120/240 grid
                t_onset = bar_start + step_in_bar * GRID16 + int(rng.integers(-18, 18))
                t_onset = max(bar_start, min(t_onset, bar_start + BAR_TICKS - 40))
                # raw pitch: boid centroid, chromatic (no raga/chord snap)
                pitch = int(round(centroid[step]))
                pitch = int(np.clip(pitch, 52, 96))
                dur = int(rng.integers(80, 160))
                end_t = min(t_onset + dur, bar_start + BAR_TICKS - 10)
                vel = int(np.clip(52 + spread[step] * 7, 52, 105))
                events.append(MusicEvent(pitch=pitch, volume=vel,
                                         start_tick=t_onset, end_tick=end_t))
        # zero-drift terminal landmark
        events.append(MusicEvent(pitch=0, volume=0,
                                 start_tick=SECTION_TICKS - 1, end_tick=SECTION_TICKS))
        composer.fill_voice_section("Raw_Lead", s_name, MusicUnit(events=events))

    ok, msg = composer.validate()
    assert ok, f"Phase 1 validate failed: {msg}"

    p1_path = os.path.join(MIDI_DIR, "212-indian-boids-yaman-phase1.mid")
    composer.to_midi(p1_path)
    assert os.path.getsize(p1_path) > 40, "Phase 1 MIDI empty"
    print(f"Phase 1 MIDI: {p1_path} ({os.path.getsize(p1_path)} bytes)")

    write_provenance(p1_path, classification=AI_ASSISTED,
                     generator="musicom.workflows.unitmatrix_composer",
                     parameters={
                         "project": "212-indian-boids-yaman", "phase": 1,
                         "style": "IndianClassical", "raga": "Yaman (Sa=C)",
                         "method": "031 Swarm Intelligence Flocking (Boids)",
                         "layer": "concrete",
                         "raw_timing": "unquantized micro-jitter (off-grid)",
                         "raw_pitch": "raw boid centroid (chromatic, no raga/chord snap)",
                         "boids": {"n": N_BOIDS, "seed": SEED,
                                   "forces": "separation/alignment/cohesion + virtual raga leader + Sa gravity"},
                         "key": "Raga Yaman on C", "bpm": BPM,
                     })
    return p1_path


# ================================================================
# PHASE 2: Musicom Rules Post-Processing + 4-Voice Arrangement
# ================================================================
def section_density(s_name):
    """Rhythmic density of the lead by section (gat-style 16th runs)."""
    if s_name in ("Alap", "Alap2", "Outro"):
        return "sparse"   # quarter notes (steps 0,4,8,12)
    if s_name == "Jhala":
        return "dense"    # every 16th
    return "gat"          # 16ths with a breath on step%4==3


def generate_phase2_composition():
    composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS_PER_BAR)
    composer.create_matrix(num_voices=4, num_sections=N_SECTIONS)

    composer.add_voice("Drone", program=ORGAN.midi_program, channel=0)
    composer.add_voice("LeadSitar", program=SITAR.midi_program, channel=1)
    composer.add_voice("Bansuri", program=FLUTE.midi_program, channel=2)
    composer.add_voice("Tabla", program=0, channel=9)

    centroid, spread, speed = run_boids()

    # teental theka (16 matras): bayan (bass) anchors + dayan (treble) strokes.
    KICK_MATRAS = (0, 4, 8, 12)           # bayan "Dha/Ta" bass anchors
    DAYAN_MATRAS = (1, 2, 3, 5, 6, 7, 9, 10, 11, 13, 14, 15)
    TIN_MATRAS = (9, 10)                   # open "Tin" strokes

    for s_idx, s_name in enumerate(SECTIONS):
        composer.add_section(s_name, bars=BARS_PER_SECTION)
        chord = SECTION_CHORDS[s_idx]
        dense = section_density(s_name)

        drone_events, lead_events, bansuri_events, tabla_events = [], [], [], []

        for bar_in_sec in range(BARS_PER_SECTION):
            bar_start = bar_in_sec * BAR_TICKS
            bar_end = bar_start + BAR_TICKS

            # --- 1. Drone (tanpura): Sa octave + Pa, sustained per bar ---
            for dp in DRONE_PITCHES:
                drone_events.append(MusicEvent(pitch=dp, volume=72,
                                               start_tick=bar_start, end_tick=bar_end - 10))

            # --- 2. LeadSitar: boid centroid melody (16th grid, raga-harmony) ---
            # --- 3. Bansuri: boid fifth-above interlock (off 16ths in gat/jhala) ---
            for step_in_bar in range(STEPS_PER_BAR):
                step = s_idx * BARS_PER_SECTION * STEPS_PER_BAR + bar_in_sec * STEPS_PER_BAR + step_in_bar
                t = bar_start + step_in_bar * GRID16  # snapped to 16th grid
                fire_lead = False
                if dense == "sparse":
                    fire_lead = (step_in_bar % 4 == 0)
                elif dense == "dense":
                    fire_lead = True
                else:  # gat
                    fire_lead = (step_in_bar % 4 != 3)

                if fire_lead:
                    raw = centroid[step]
                    lp = quantize_to_chord(raw, chord, min_pitch=60, max_pitch=84)
                    vel = int(np.clip(64 + spread[step] * 7 + (10 if s_name == "Jhala" else 0),
                                      64, 108))
                    lead_events.append(MusicEvent(pitch=lp, volume=vel,
                                                  start_tick=t, end_tick=t + 110))

                # bansuri interlock: off 16ths in the melodic (gat/jhala) sections
                if dense in ("gat", "dense") and (step_in_bar % 2 == 1):
                    raw = centroid[step] + 7.0  # fifth above (Pa relation)
                    bp = quantize_to_chord(raw, chord, min_pitch=67, max_pitch=88)
                    bansuri_events.append(MusicEvent(pitch=bp, volume=80,
                                                     start_tick=t, end_tick=t + 90))

            # --- 4. Tabla: teental theka ---
            if s_name in ("Alap",):           # alap = drone only (free rhythm)
                pass
            elif s_name in ("Alap2", "Outro"):  # sparse: soft bayan on beat 1 only
                tabla_events.append(MusicEvent(pitch=36, volume=70,
                                               start_tick=bar_start, end_tick=bar_start + 100))
            else:
                for m in range(STEPS_PER_BAR):
                    t = bar_start + m * GRID16
                    if m in KICK_MATRAS:
                        tabla_events.append(MusicEvent(pitch=36, volume=100 if m == 0 else 90,
                                                       start_tick=t, end_tick=t + 90))
                    if m in DAYAN_MATRAS:
                        tabla_events.append(MusicEvent(pitch=38, volume=84,
                                                       start_tick=t, end_tick=t + 60))
                    if m in TIN_MATRAS:
                        tabla_events.append(MusicEvent(pitch=42, volume=70,
                                                       start_tick=t, end_tick=t + 50))
                    if s_name == "Jhala" and m % 2 == 0:
                        # double-time dayan sparkle in the climax
                        tabla_events.append(MusicEvent(pitch=38, volume=60,
                                                       start_tick=t, end_tick=t + 40))

        def seal(ev_list):
            ev_list.sort(key=lambda e: (e.start_tick, e.end_tick))
            ev_list.append(MusicEvent(pitch=0, volume=0,
                                      start_tick=SECTION_TICKS - 1, end_tick=SECTION_TICKS))
            return MusicUnit(events=ev_list)

        composer.fill_voice_section("Drone", s_name, seal(drone_events))
        composer.fill_voice_section("LeadSitar", s_name, seal(lead_events))
        composer.fill_voice_section("Bansuri", s_name, seal(bansuri_events))
        composer.fill_voice_section("Tabla", s_name, seal(tabla_events))

    ok, msg = composer.validate()
    assert ok, f"Phase 2 validate failed: {msg}"

    p2_path = os.path.join(MIDI_DIR, "212-indian-boids-yaman.mid")
    composer.to_midi(p2_path)
    assert os.path.getsize(p2_path) > 40, "Phase 2 MIDI empty"
    print(f"Phase 2 MIDI: {p2_path} ({os.path.getsize(p2_path)} bytes)")

    write_grid_visualization(composer.matrix,
                             os.path.join(ANALYSIS_DIR, "grid_visualization.txt"),
                             ticks_per_character=240,
                             voice_names=["Drone", "LeadSitar", "Bansuri", "Tabla"],
                             bpm=BPM)
    print("Grid viz written to Analysis/grid_visualization.txt")

    write_provenance(p2_path, classification=AI_ASSISTED,
                     generator="musicom.workflows.unitmatrix_composer",
                     parameters={
                         "project": "212-indian-boids-yaman", "phase": 2,
                         "style": "IndianClassical", "raga": "Yaman (Sa=C)",
                         "method": "031 Swarm Intelligence Flocking (Boids)",
                         "layer": "concrete",
                         "quantization": "16th-grid (120 ticks) + raga-harmonic-region snap",
                         "boids": {"n": N_BOIDS, "seed": SEED,
                                   "forces": "separation/alignment/cohesion + virtual raga leader + Sa gravity"},
                         "key": "Raga Yaman on C", "bpm": BPM,
                         "progression": "Alap(SaPa drone) -> Jod/Gat1/Gat2/Jhala/Gat1b (full Yaman) -> Alap2/Outro(SaPa drone)",
                     })
    return p2_path


if __name__ == "__main__":
    centroid, spread, speed = run_boids()
    print(f"Boids: n={N_BOIDS} | centroid range [{centroid.min():.1f}, {centroid.max():.1f}] "
          f"| spread mean {spread.mean():.2f} | speed mean {speed.mean():.3f}")
    print("=== Phase 1 raw boid draft ===")
    generate_phase1_raw()
    print("=== Phase 2 rules composition ===")
    generate_phase2_composition()
    print("Done!")
