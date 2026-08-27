# -*- coding: utf-8 -*-
"""072-world-melisma - World style / Markov-Harmony method (M-022).

Two-phase composition:
  Phase 1: raw markov swimming melody, no harmony (single voice).
  Phase 2: chord-tone quantization onto a markov harmony walk, full
           world texture: lead + counter ostinato + pad + drift bass + percussion.

Engine only: structures + workflows.unitmatrix_composer. validate() gate + to_midi().
"""
import os
import random

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import (
    UnitMatrixComposer, create_empty_unit,
)
from generators.markov_constraint import MarkovConstraintGenerator

random.seed(20260818)

# ---------------------------------------------------------------- project dirs
PROJ = "/opt/data/projects/Styles/World/072-world-melisma"
MIDI_DIR = os.path.join(PROJ, "MIDI")
AUDIO_DIR = os.path.join(PROJ, "Audio")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")
for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
    os.makedirs(d, exist_ok=True)

# ---------------------------------------------------------------- concept
BPM = 100
TPB = 480
BEATS = 4
BAR = TPB * BEATS            # 1920
# D dorian (world / travel modal feel)
SCALE = [62, 64, 65, 67, 69, 71, 72, 74, 76]   # D4..D6 diatonic
LEAD_LO, LEAD_HI = 60, 84

# chord-tone triads (D dorian diatonic degrees) keyed by root MIDI
CHORDS = {
    62: [62, 65, 69],   # Dm  i
    64: [64, 67, 71],   # Em  ii
    65: [65, 69, 72],   # F   III
    67: [67, 71, 74],   # G   IV
    69: [69, 72, 76],   # Am  v
}
ROOTS = [62, 64, 65, 67, 69]
BASS = {62: 38, 64: 40, 65: 41, 67: 43, 69: 45}   # octave 2

# markov harmony walk over dorian degrees (i, ii, III, IV, v)
TRANS = {
    "i":  ["IV", "v", "III"],
    "ii": ["v"],
    "III": ["IV", "v"],
    "IV": ["i", "v"],
    "v":  ["i", "IV"],
}
DEG_ROOT = {"i": 62, "ii": 64, "III": 65, "IV": 67, "v": 69}

# ---------------------------------------------------------------- sections
NAMES = ["Intro", "Verse", "Chorus", "Verse2", "Outro"]
BARS_PER = 4
N_SECTIONS = len(NAMES)
N_BARS = N_SECTIONS * BARS_PER            # 20 bars
SECTION_TICKS = BAR * BARS_PER            # 7680

# markov harmony: draw 20 chord roots (one per bar)
def markov_harmony(n_bars):
    walk = []
    state = "i"
    for _ in range(n_bars):
        walk.append(DEG_ROOT[state])
        state = random.choice(TRANS[state])
    return walk

CHORD_WALK = markov_harmony(N_BARS)
CHORD_NAMES = []
for i in range(N_BARS):
    for k, v in DEG_ROOT.items():
        if v == CHORD_WALK[i]:
            CHORD_NAMES.append(k)

def chord_for_bar(bar):
    return CHORDS[CHORD_WALK[bar]]

def quantize_to_chord(pitch, chord_tones):
    """Snap a pitch to nearest chord tone, resolving ties toward lower."""
    return min(chord_tones, key=lambda c: (abs(c - pitch), c))

# ---------------------------------------------------------------- phase 1
# raw markov swimming melody, unquantized to chords, no harmony
phase1 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
phase1.create_matrix(num_voices=1, num_sections=N_SECTIONS)
phase1.add_voice("LeadRaw", program=75, channel=0)  # Pan Flute
for n in NAMES:
    phase1.add_section(n, bars=BARS_PER)

markov = MarkovConstraintGenerator(
    key_pitches=SCALE, default_pitch=74, min_pitch=LEAD_LO, max_pitch=LEAD_HI)
prev = None
for s, name in enumerate(NAMES):
    unit = markov.generate_voice_section(
        section_ticks=SECTION_TICKS, step_ticks=480, density=0.5,
        volume=92, previous_pitch=prev)
    phase1.set_unit(0, s, unit)
    evs = [e for e in unit.events if e.pitch]
    if evs:
        prev = evs[-1].pitch

ok1, msg1 = phase1.validate()
print("PHASE1 validate:", msg1)
P1_MIDI = os.path.join(MIDI_DIR, "072-world-melisma-phase1.mid")
phase1.to_midi(P1_MIDI)
print("phase1 written", P1_MIDI)

# ---------------------------------------------------------------- phase 2
# rules post-process: chord-tone quantized lead + full world texture
phase2 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
VOICES = [
    ("Lead",     75, 0),   # Pan Flute
    ("Counter",  48, 1),   # String Ensemble
    ("Pad",      89, 2),   # Synth Pad (warm)
    ("Bass",     35, 3),   # Fretless Bass
    ("Perc",      0, 9),   # percussion channel
]
N_V = len(VOICES)
phase2.create_matrix(num_voices=N_V, num_sections=N_SECTIONS)
vnames = [v[0] for v in VOICES]
for name, prog, ch in VOICES:
    phase2.add_voice(name, program=prog, channel=ch)
for n in NAMES:
    phase2.add_section(n, bars=BARS_PER)

# --- lead: quantize phase-1 raw events to bar's chord tones ---
for s, name in enumerate(NAMES):
    raw_unit = phase1.matrix.get_unit((0, s))
    q_events = []
    for e in raw_unit.events:
        if e.pitch == 0:
            q_events.append(e)
            continue
        bar = (e.start_tick) // BAR
        tones = chord_for_bar(bar if bar < N_BARS else N_BARS - 1)
        qp = quantize_to_chord(e.pitch, tones)
        q_events.append(MusicEvent(pitch=qp, volume=92, start_tick=e.start_tick, end_tick=e.end_tick))
    # voice-leading: cap leaps to <=8 semitones, drift toward nearest chord tone
    for i in range(1, len(q_events)):
        e = q_events[i]
        if e.pitch == 0:
            continue
        p_prev = q_events[i - 1].pitch if q_events[i - 1].pitch else LEAD_HI
        if abs(e.pitch - p_prev) > 8:
            bar = e.start_tick // BAR
            tones = chord_for_bar(bar if bar < N_BARS else N_BARS - 1)
            e.pitch = min(tones, key=lambda c: (abs(c - p_prev), c))
    phase2.set_unit(0, s, MusicUnit(events=q_events))

# --- counter: high pentatonic ostinato using chord 3rd/5th ---
for bar in range(N_BARS):
    s, b = divmod(bar, BARS_PER)
    tones = chord_for_bar(bar)
    fifth = tones[2] + 12      # up octave
    third = tones[1] + 12
    e = []
    t0 = b * BAR
    # two light pulses per bar: 5th on beat 1, 3rd on beat 3
    e.append(MusicEvent(pitch=fifth, volume=70, start_tick=t0 + 60, end_tick=t0 + 360))
    e.append(MusicEvent(pitch=third, volume=66, start_tick=t0 + 1020, end_tick=t0 + 1440))
    unit = phase2.matrix.get_unit((1, s))
    events = list(unit.events) if unit is not None else []
    events.extend(e)
    phase2.set_unit(1, s, MusicUnit(events=events))

# --- pad: sustained triad per bar ---
for bar in range(N_BARS):
    s, b = divmod(bar, BARS_PER)
    tones = chord_for_bar(bar)
    t0 = b * BAR
    e = [MusicEvent(pitch=p, volume=62, start_tick=t0 + 30, end_tick=t0 + BAR - 60) for p in tones]
    unit = phase2.matrix.get_unit((2, s))
    events = list(unit.events) if unit is not None else []
    events.extend(e)
    phase2.set_unit(2, s, MusicUnit(events=events))

# --- bass: modal root drone (whole-bar) with small lift on beat 3 ---
for bar in range(N_BARS):
    s, b = divmod(bar, BARS_PER)
    root = BASS[CHORD_WALK[bar]]
    t0 = b * BAR
    e = [
        MusicEvent(pitch=root, volume=96, start_tick=t0, end_tick=t0 + BAR),
        MusicEvent(pitch=root + 7, volume=84, start_tick=t0 + 1440, end_tick=t0 + 1920 - 10),
    ]
    unit = phase2.matrix.get_unit((3, s))
    events = list(unit.events) if unit is not None else []
    events.extend(e)
    phase2.set_unit(3, s, MusicUnit(events=events))

# --- drums: world percussion ---
#   35 kick, 41 low floor tom, 50 high tom, 82 shaker, 69 cabasa
SEC_PAD = [0, 1, 2, 3, 4]
DRUMS = {
    0: (0.5,),        # intro: sparse
    1: (0.7,),
    2: (1.0,),
    3: (0.7,),
    4: (0.2,),
}
for s in range(N_SECTIONS):
    evs = []
    dens = DRUMS[s][0]
    if dens <= 0:
        phase2.set_unit(4, s, create_empty_unit(SECTION_TICKS))
        continue
    step = int(240 * (1.0 / dens) / 240) if dens < 1 else 240
    sh = 120 if dens >= 0.7 else 240
    for bar in range(BARS_PER):
        t0 = bar * BAR
        if dens >= 0.7:
            # shaker 8ths
            for k in range(0, 1920, sh):
                evs.append(MusicEvent(pitch=82, volume=52, start_tick=t0 + k, end_tick=t0 + k + 80))
        # low tom on beats 1 & 3, high tom off-beats
        evs.append(MusicEvent(pitch=41, volume=92, start_tick=t0, end_tick=t0 + 140))
        evs.append(MusicEvent(pitch=41, volume=88, start_tick=t0 + 960, end_tick=t0 + 1100))
        if dens == 1.0:
            evs.append(MusicEvent(pitch=50, volume=70, start_tick=t0 + 480, end_tick=t0 + 600))
            evs.append(MusicEvent(pitch=50, volume=66, start_tick=t0 + 1440, end_tick=t0 + 1560))
        if dens >= 0.7 and s in (2, 3):
            evs.append(MusicEvent(pitch=35, volume=100, start_tick=t0, end_tick=t0 + 120))
    phase2.set_unit(4, s, MusicUnit(events=evs))

# --- normalize every cell to exact section boundary (zero-drift invariant) ---
def normalize_cell(unit, total_ticks):
    evs = list(unit.events)
    for e in evs:
        if e.end_tick > total_ticks:
            e.end_tick = total_ticks
    # ensure exact final landmark reaches total_ticks
    has_landmark = any(e.pitch == 0 and e.end_tick == total_ticks for e in evs)
    if not has_landmark:
        evs.append(MusicEvent(pitch=0, volume=0, start_tick=total_ticks - 1, end_tick=total_ticks))
    return MusicUnit(events=evs)

for v in range(N_V):
    for s in range(N_SECTIONS):
        u = phase2.matrix.get_unit((v, s))
        if u is not None and len(u.events) > 0:
            phase2.set_unit(v, s, normalize_cell(u, SECTION_TICKS))

ok2, msg2 = phase2.validate()
print("PHASE2 validate:", msg2)
assert ok1 and ok2, (msg1, msg2)

P2_MIDI = os.path.join(MIDI_DIR, "072-world-melisma.mid")
phase2.to_midi(P2_MIDI)
print("phase2 written", P2_MIDI)

# ---------------------------------------------------------------- analysis
from visualization.grid import write_grid_visualization
grid_path = os.path.join(ANALYSIS_DIR, "grid_visualization.txt")
write_grid_visualization(phase2.matrix, grid_path, ticks_per_character=120,
                         voice_names=vnames, bpm=BPM, mode="D Dorian / markov-harmony")
print("grid written", grid_path)

# provenance
from workflows.provenance import write_provenance, AI_GENERATED
for mid, phase, note in ((P1_MIDI, "1", "raw markov melody, unquantized, single voice"),
                         (P2_MIDI, "2", "chord-tone quantized to markov harmony walk, full world texture")):
    write_provenance(mid, AI_GENERATED, "MarkovConstraintGenerator+M-022 markov-harmony",
                     parameters={"bpm": BPM, "key": "D dorian", "sections": N_SECTIONS,
                                 "bars": N_BARS, "phase": phase,
                                 "chord_walk": CHORD_NAMES, "seed": 20260818},
                     notes=note)
    print("provenance for phase", phase)

# ---------------------------------------------------------------- silence guard metadata
import json
with open(os.path.join(ANALYSIS_DIR, "summary.json"), "w") as f:
    json.dump({
        "project": "072-world-melisma",
        "style": "World",
        "method": "markov-harmony (M-022 Markov-Constraint Wavefront)",
        "bpm": BPM, "key": "D Dorian", "tempo": BPM,
        "bars": N_BARS, "sections": {n: BARS_PER for n in NAMES},
        "chord_walk": CHORD_NAMES,
        "voices": [v[0] for v in VOICES],
        "phase1": os.path.basename(P1_MIDI),
        "phase2": os.path.basename(P2_MIDI),
        "grid": os.path.basename(grid_path),
        "seed": 20260818,
    }, f, indent=2)
print("summary.json written")

# ---------------------------------------------------------------- size asserts
for p in (P1_MIDI, P2_MIDI, grid_path,
          os.path.join(ANALYSIS_DIR, "summary.json")):
    assert os.path.getsize(p) > 40, f"too small: {p}"
print("ALL SIZE ASSERTS PASSED")
print("CHORD_WALK:", CHORD_NAMES)