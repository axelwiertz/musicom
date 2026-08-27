# -*- coding: utf-8 -*-
"""073-soul-rbmpd - Soul style / Method 048 Reflected Brownian Motion Pitch Diffusion.

Two-phase composition:
  Phase 1: raw RBMPD single-voice pitch diffusion (continuous semitone walk,
           no harmony, no quantization) - the pure generative draft.
  Phase 2: musicom rules post-process - chord-tone quantization per bar,
           voice-leading leap cap, full soul texture:
           lead + horns stabs + Rhodes pad + bass + drums.

Engine only: structures + workflows.unitmatrix_composer. validate() gate + to_midi().
"""
import os
import json
import random

import numpy as np

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import (
    UnitMatrixComposer, create_empty_unit,
)

random.seed(20260819)
rng = np.random.default_rng(20260819)

# ---------------------------------------------------------------- project dirs
PROJ = "/opt/data/projects/Styles/Soul/073-soul-rbmpd"
MIDI_DIR = os.path.join(PROJ, "MIDI")
AUDIO_DIR = os.path.join(PROJ, "Audio")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")
for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
    os.makedirs(d, exist_ok=True)

# ---------------------------------------------------------------- concept
BPM = 92
TPB = 480
BEATS = 4
BAR = TPB * BEATS            # 1920
# C minor soul:  C D Eb F G Ab Bb  (natural minor) across two octaves
SCALE = [60, 62, 63, 65, 67, 68, 70, 72, 74, 75, 77, 79, 80, 82, 84]
LEAD_LO, LEAD_HI = 60, 84

# diatonic triads in C natural minor, keyed by root MIDI
CHORDS = {
    60: [60, 63, 67],   # Cm  i
    65: [65, 68, 72],   # Fm  iv
    67: [67, 70, 74],   # G   V (major - harmonic lift)
    63: [63, 67, 70],   # Eb  III
    68: [68, 72, 75],   # Ab  VI
    62: [62, 65, 69],   # Dm  ii (dorian color)
}
ROOTS = [60, 65, 67, 63, 68]
BASS = {60: 36, 65: 41, 67: 43, 63: 39, 68: 44}   # octave 2

# ---------------------------------------------------------------- sections
NAMES = ["Intro", "Verse", "Chorus", "Verse2", "Chorus2", "Outro"]
BARS_PER = 4
N_SECTIONS = len(NAMES)
N_BARS = N_SECTIONS * BARS_PER            # 24 bars
SECTION_TICKS = BAR * BARS_PER            # 7680

# chord roots, one per bar: i iv V III | i iv V VI | i V i VI | i iv V i | ...
PROG = [60, 65, 67, 63] * 2 + [60, 67, 60, 68] + [60, 65, 67, 60] + \
       [60, 65, 67, 63] + [60, 67, 65, 60]
# 8 + 4 + 4 + 4 + 4 = 24
assert len(PROG) == N_BARS, (len(PROG), N_BARS)
CHORD_NAMES = {60: "i", 65: "iv", 67: "V", 63: "III", 68: "VI"}

def chord_for_bar(bar):
    return CHORDS[PROG[bar]]

def quantize_to_chord(pitch, chord_tones):
    """Snap a pitch to nearest chord tone, resolving ties toward lower."""
    return min(chord_tones, key=lambda c: (abs(c - pitch), c))

# ---------------------------------------------------------------- phase 1
# raw RBMPD single voice: reflected Brownian walk, continuous semitones,
# onsets where |dP| > threshold. NO harmony, NO chord quantization.
def simulate_reflected_brownian_voice(
    drift=0.0, volatility=1.0, boundary_low=-12.0, boundary_high=12.0,
    duration_ticks=7680, dt=1.0, seed=None, on_threshold=1.0,
):
    """One voice as reflected Brownian motion. Returns P, onsets, velocities."""
    r = np.random.default_rng(seed)
    P = np.zeros(duration_ticks)
    P[0] = (boundary_low + boundary_high) / 2.0
    for t in range(1, duration_ticks):
        dP = drift * dt + volatility * np.sqrt(dt) * r.standard_normal()
        new_P = P[t - 1] + dP
        # Skorokhod reflection with soft zone (1 semitone inward bias)
        if new_P < boundary_low:
            new_P = boundary_low + (boundary_low - new_P) + 0.05
        elif new_P > boundary_high:
            new_P = boundary_high - (new_P - boundary_high) - 0.05
        P[t] = new_P
    dP_dt = np.abs(np.diff(P, prepend=P[0]))
    onsets = np.where(dP_dt > on_threshold)[0]
    # soft-knee velocity: fast motion louder, tanh compressor
    velocities = np.clip(60 + 30 * np.tanh(dP_dt[onsets] / 2.0), 40, 112).astype(int)
    return P, onsets, velocities

# section drift / volatility schedule (macro-form via diffusion params)
# Intro: free wandering (mu=0), low vol; Verse: pull to tonic; Chorus: strong tonic
SEC_MU = [0.0, -0.15, -0.35, -0.15, -0.35, -0.6]
SEC_SIG = [1.4, 1.7, 2.1, 1.7, 2.1, 1.2]
SEC_TAU = [0.7, 0.8, 0.9, 0.8, 0.9, 0.7]

phase1 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
phase1.create_matrix(num_voices=1, num_sections=N_SECTIONS)
phase1.add_voice("LeadRaw", program=75, channel=0)  # Pan Flute
for n in NAMES:
    phase1.add_section(n, bars=BARS_PER)

P1_EVENTS = []
for s, name in enumerate(NAMES):
    P, onsets, vels = simulate_reflected_brownian_voice(
        drift=SEC_MU[s], volatility=SEC_SIG[s],
        boundary_low=-10.0, boundary_high=10.0,
        duration_ticks=SECTION_TICKS, dt=1.0, seed=20260819 + s,
        on_threshold=SEC_TAU[s],
    )
    events = []
    for tick, p, v in zip(onsets, P[onsets], vels):
        # octave-tracking: keep around 72 (C5) center
        midi = int(round(72 + p))
        midi = max(LEAD_LO, min(LEAD_HI, midi))
        dur = 240
        events.append(MusicEvent(pitch=midi, volume=int(v),
                                 start_tick=int(tick), end_tick=int(tick) + dur))
    if events:
        last = events[-1].end_tick
        if last > SECTION_TICKS:
            events[-1].end_tick = SECTION_TICKS
    # phase-1 cell keeps raw pitches: NO chord quantization
    P1_EVENTS.extend(events)
    phase1.set_unit(0, s, MusicUnit(events=events))

# zero-drift landmark padding for phase 1 (exact section boundary)
for s in range(N_SECTIONS):
    u = phase1.matrix.get_unit((0, s))
    evs = list(u.events)
    has_landmark = any(e.pitch == 0 and e.end_tick == SECTION_TICKS for e in evs)
    if not has_landmark:
        evs.append(MusicEvent(pitch=0, volume=0, start_tick=SECTION_TICKS - 1,
                              end_tick=SECTION_TICKS))
    phase1.set_unit(0, s, MusicUnit(events=evs))

ok1, msg1 = phase1.validate()
print("PHASE1 validate:", msg1)
P1_MIDI = os.path.join(MIDI_DIR, "073-soul-rbmpd-phase1.mid")
phase1.to_midi(P1_MIDI)
print("phase1 written", P1_MIDI)

# ---------------------------------------------------------------- phase 2
# rules post-process: chord-tone quantization + voice-leading + full soul texture
phase2 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
VOICES = [
    ("Lead",     75, 0),   # Pan Flute (soul lead)
    ("Horns",    61, 1),   # Brass Section (stabs)
    ("Rhodes",   4,  2),   # Electric Piano (pad/comp)
    ("Bass",     33, 3),   # Electric Bass (finger)
    ("Drums",     0, 9),   # percussion channel
]
N_V = len(VOICES)
phase2.create_matrix(num_voices=N_V, num_sections=N_SECTIONS)
vnames = [v[0] for v in VOICES]
for name, prog, ch in VOICES:
    phase2.add_voice(name, program=prog, channel=ch)
for n in NAMES:
    phase2.add_section(n, bars=BARS_PER)

# --- lead: quantize phase-1 raw events to each bar's chord tones ---
for s, name in enumerate(NAMES):
    raw_unit = phase1.matrix.get_unit((0, s))
    q_events = []
    for e in raw_unit.events:
        if e.pitch == 0:
            q_events.append(e)
            continue
        bar = e.start_tick // BAR
        tones = chord_for_bar(bar if bar < N_BARS else N_BARS - 1)
        qp = quantize_to_chord(e.pitch, tones)
        q_events.append(MusicEvent(pitch=qp, volume=e.volume,
                                   start_tick=e.start_tick, end_tick=e.end_tick))
    # voice-leading: cap leaps to <= 9 semitones, drift toward nearest chord tone
    for i in range(1, len(q_events)):
        e = q_events[i]
        if e.pitch == 0:
            continue
        p_prev = q_events[i - 1].pitch if q_events[i - 1].pitch else LEAD_HI
        if abs(e.pitch - p_prev) > 9:
            bar = e.start_tick // BAR
            tones = chord_for_bar(bar if bar < N_BARS else N_BARS - 1)
            e.pitch = min(tones, key=lambda c: (abs(c - p_prev), c))
    phase2.set_unit(0, s, MusicUnit(events=q_events))

# --- horns: syncopated stab accents on beats 2& / 4& (soul classic) ---
HORN_STRONG = {0, 2, 4, 5}   # chorus + final chorus sections
for bar in range(N_BARS):
    s, b = divmod(bar, BARS_PER)
    tones = chord_for_bar(bar)
    t0 = b * BAR
    e = []
    if s in HORN_STRONG:
        # 4 stabs per bar: beats 2, 2&, 4, 4& (offbeat pushes)
        for off in (720, 960, 1680, 1920 - 240):
            for p in tones:
                e.append(MusicEvent(pitch=p + 12, volume=76,
                                    start_tick=t0 + off, end_tick=t0 + off + 120))
    else:
        # lighter: 2 stabs per bar on 2& and 4
        for off in (960, 1680):
            e.append(MusicEvent(pitch=tones[1] + 12, volume=66,
                                start_tick=t0 + off, end_tick=t0 + off + 120))
    unit = phase2.matrix.get_unit((1, s))
    events = list(unit.events) if unit is not None else []
    events.extend(e)
    phase2.set_unit(1, s, MusicUnit(events=events))

# --- rhodes: sustained comp per bar, 3rd+7th color, light 8th rhythm ---
for bar in range(N_BARS):
    s, b = divmod(bar, BARS_PER)
    tones = chord_for_bar(bar)
    t0 = b * BAR
    third = tones[1] + 12
    seventh = tones[2] + 12
    e = []
    for k in range(0, BAR, 480):
        if k % 960 == 0:
            e.append(MusicEvent(pitch=third, volume=58,
                                start_tick=t0 + k, end_tick=t0 + k + 420))
        else:
            e.append(MusicEvent(pitch=seventh, volume=52,
                                start_tick=t0 + k, end_tick=t0 + k + 380))
    unit = phase2.matrix.get_unit((2, s))
    events = list(unit.events) if unit is not None else []
    events.extend(e)
    phase2.set_unit(2, s, MusicUnit(events=events))

# --- bass: soul octave pulse, root on 1&3, fifth on 2&4, syncopated 16th push ---
for bar in range(N_BARS):
    s, b = divmod(bar, BARS_PER)
    root = BASS[PROG[bar]]
    fifth = root + 7
    t0 = b * BAR
    e = [
        MusicEvent(pitch=root, volume=100, start_tick=t0, end_tick=t0 + 360),
        MusicEvent(pitch=fifth, volume=88, start_tick=t0 + 480, end_tick=t0 + 840),
        MusicEvent(pitch=root, volume=100, start_tick=t0 + 960, end_tick=t0 + 1320),
        MusicEvent(pitch=fifth, volume=88, start_tick=t0 + 1440, end_tick=t0 + 1800),
    ]
    if s in (2, 4):   # chorus: 16th push into next bar
        e.append(MusicEvent(pitch=root, volume=92, start_tick=t0 + 1800,
                            end_tick=t0 + 1920 - 10))
    unit = phase2.matrix.get_unit((3, s))
    events = list(unit.events) if unit is not None else []
    events.extend(e)
    phase2.set_unit(3, s, MusicUnit(events=events))

# --- drums: backbeat soul. 35 kick 1&3, 38 snare 2&4, 42 closed hat 8ths,
#      chorus adds 51 ride + 39 clap on 2&4 ---
SEC_DENS = [0.4, 0.8, 1.0, 0.8, 1.0, 0.5]
for s in range(N_SECTIONS):
    dens = SEC_DENS[s]
    evs = []
    if dens <= 0:
        phase2.set_unit(4, s, create_empty_unit(SECTION_TICKS))
        continue
    for bar in range(BARS_PER):
        t0 = bar * BAR
        # closed hat 8ths (always)
        for k in range(0, BAR, 240):
            evs.append(MusicEvent(pitch=42, volume=48,
                                  start_tick=t0 + k, end_tick=t0 + k + 90))
        # kick on 1 and 3
        evs.append(MusicEvent(pitch=35, volume=104, start_tick=t0, end_tick=t0 + 160))
        evs.append(MusicEvent(pitch=35, volume=100, start_tick=t0 + 960, end_tick=t0 + 1120))
        if dens >= 0.8:
            # snare backbeat on 2 and 4
            evs.append(MusicEvent(pitch=38, volume=100, start_tick=t0 + 480, end_tick=t0 + 620))
            evs.append(MusicEvent(pitch=38, volume=104, start_tick=t0 + 1440, end_tick=t0 + 1580))
            if dens >= 1.0:
                # clap doubles snare + ride cymbal on beat 1
                evs.append(MusicEvent(pitch=39, volume=84, start_tick=t0 + 480, end_tick=t0 + 600))
                evs.append(MusicEvent(pitch=39, volume=88, start_tick=t0 + 1440, end_tick=t0 + 1560))
                evs.append(MusicEvent(pitch=51, volume=70, start_tick=t0, end_tick=t0 + 600))
    phase2.set_unit(4, s, MusicUnit(events=evs))

# --- normalize every cell to exact section boundary (zero-drift invariant) ---
def normalize_cell(unit, total_ticks):
    evs = list(unit.events)
    for e in evs:
        if e.end_tick > total_ticks:
            e.end_tick = total_ticks
    has_landmark = any(e.pitch == 0 and e.end_tick == total_ticks for e in evs)
    if not has_landmark:
        evs.append(MusicEvent(pitch=0, volume=0, start_tick=total_ticks - 1,
                              end_tick=total_ticks))
    return MusicUnit(events=evs)

for v in range(N_V):
    for s in range(N_SECTIONS):
        u = phase2.matrix.get_unit((v, s))
        if u is not None and len(u.events) > 0:
            phase2.set_unit(v, s, normalize_cell(u, SECTION_TICKS))

ok2, msg2 = phase2.validate()
print("PHASE2 validate:", msg2)
assert ok1 and ok2, (msg1, msg2)

P2_MIDI = os.path.join(MIDI_DIR, "073-soul-rbmpd.mid")
phase2.to_midi(P2_MIDI)
print("phase2 written", P2_MIDI)

# ---------------------------------------------------------------- analysis
from visualization.grid import write_grid_visualization
grid_path = os.path.join(ANALYSIS_DIR, "grid_visualization.txt")
write_grid_visualization(phase2.matrix, grid_path, ticks_per_character=120,
                         voice_names=vnames, bpm=BPM, mode="C minor / RBMPD soul")
print("grid written", grid_path)

# provenance
from workflows.provenance import write_provenance, AI_GENERATED
for mid, phase, note in (
        (P1_MIDI, "1", "raw RBMPD pitch diffusion, unquantized, single voice, no harmony"),
        (P2_MIDI, "2", "chord-tone quantized to C-minor soul progression, full texture")):
    write_provenance(
        mid, AI_GENERATED, "RBMPD (Method 048 Reflected Brownian Motion Pitch Diffusion)",
        parameters={"bpm": BPM, "key": "C natural minor", "sections": N_SECTIONS,
                    "bars": N_BARS, "phase": phase,
                    "progression": [CHORD_NAMES[r] for r in PROG], "seed": 20260819},
        notes=note)
    print("provenance for phase", phase)

# summary.json
with open(os.path.join(ANALYSIS_DIR, "summary.json"), "w") as f:
    json.dump({
        "project": "073-soul-rbmpd",
        "style": "Soul",
        "method": "048 Reflected Brownian Motion Pitch Diffusion (RBMPD)",
        "bpm": BPM, "key": "C natural minor", "tempo": BPM,
        "bars": N_BARS,
        "sections": {n: BARS_PER for n in NAMES},
        "progression": [CHORD_NAMES[r] for r in PROG],
        "voices": vnames,
        "phase1": os.path.basename(P1_MIDI),
        "phase2": os.path.basename(P2_MIDI),
        "grid": os.path.basename(grid_path),
        "seed": 20260819,
    }, f, indent=2)
print("summary.json written")

# ---------------------------------------------------------------- size asserts
for p in (P1_MIDI, P2_MIDI, grid_path,
          os.path.join(ANALYSIS_DIR, "summary.json")):
    assert os.path.getsize(p) > 40, "too small: %s" % p
print("ALL SIZE ASSERTS PASSED")
print("PROGRESSION:", [CHORD_NAMES[r] for r in PROG])
