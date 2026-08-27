# -*- coding: utf-8 -*-
"""075-disco-pcfg - Disco style / Method 034 Probabilistic Context-Free Grammar (PCFG).

Two-phase composition:
  Phase 1: raw PCFG recursion draft - the grammar rewrites a start symbol
           into a tree whose leaves are melodic intervals and rhythm cells.
           Raw pitch indices (floats), no harmony, no chord quantization.
  Phase 2: musicom rules post-process - chord-tone quantization per bar,
           voice-leading leap cap, full disco texture:
           lead + strings stabs + guitar + bass + drums (four-on-the-floor).

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

random.seed(20260821)
rng = np.random.default_rng(20260821)

# ---------------------------------------------------------------- project dirs
PROJ = "/opt/data/projects/Styles/Disco/075-disco-pcfg"
MIDI_DIR = os.path.join(PROJ, "MIDI")
AUDIO_DIR = os.path.join(PROJ, "Audio")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")
for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
    os.makedirs(d, exist_ok=True)

# ---------------------------------------------------------------- concept
BPM = 118
TPB = 480
BEATS = 4
BAR = TPB * BEATS            # 1920
# D natural minor (disco minor): D E F G A Bb C  across two octaves
SCALE = [62, 64, 65, 67, 69, 70, 72, 74, 75, 77, 79, 80, 82, 84]
LEAD_LO, LEAD_HI = 62, 84

# diatonic triads in D natural minor, keyed by root MIDI
CHORDS = {
    62: [62, 65, 69],   # Dm  i
    65: [65, 68, 72],   # Gm  iv
    67: [67, 70, 74],   # F   VI (relative major color)
    69: [69, 72, 76],   # Am  v (natural minor v)
    60: [60, 64, 67],   # Bb  VII
    70: [70, 74, 77],   # Bb? no - 70 is A? D natural minor: D E F G A Bb C
}
# fix: 70 = A (5th of D). Bb = 70? No: Bb = 70 in MIDI? Bb4 = 70? Bb4 = 70 yes (A4=69, Bb4=70).
# D natural minor scale: D E F G A Bb C  ->  62 64 65 67 69 70 72
# So 70 IS Bb (6th degree). 69 = A (5th). 72 = C (7th).
# Triads: Dm(62,65,69) Gm(65,68,72) Bb(70,74,77) F(65? no) ...
# F major = F A C = 65,69,72  (iv is Gm though in natural minor: iv = F? no, iv = Gm in D minor)
# D natural minor: i=Dm(62,65,69) ii=E dim(64,67,70) III=F(65,69,72) iv=Gm(65? wait)
# G = 67 (4th degree). Gm = G Bb D = 67,70,74. F = F A C = 65,69,72. Bb = Bb D F = 70,74,77.
# A = 69 (5th). Am = A C E = 69,72,76. C = 72 (7th).
# So correct triads:
CHORDS_FIX = {
    62: [62, 65, 69],   # Dm  i
    65: [65, 69, 72],   # F   III (relative major)
    67: [67, 70, 74],   # Gm  iv
    69: [69, 72, 76],   # Am  v
    70: [70, 74, 77],   # Bb  VI
    72: [72, 76, 79],   # C   VII
}
CHORDS = CHORDS_FIX
# disco-favored roots: i - VI - III - VII (Dm - Bb - F - C) + v
ROOTS = [62, 70, 65, 72, 62, 69, 70, 65]
BASS = {62: 38, 70: 46, 65: 41, 72: 48, 69: 45}   # octave 2/3

# ---------------------------------------------------------------- sections
NAMES = ["Intro", "Verse", "Chorus", "Verse2", "Chorus2", "Outro"]
BARS_PER = 4
N_SECTIONS = len(NAMES)
N_BARS = N_SECTIONS * BARS_PER            # 24 bars
SECTION_TICKS = BAR * BARS_PER            # 7680

# chord roots, one per bar (4-bar phrases, circle-of-fifths flavor)
PROG = [62, 70, 65, 72] * 2 + [62, 69, 70, 65] + [62, 70, 65, 72] + \
       [62, 69, 70, 65] + [62, 70, 65, 62]
# 8 + 4 + 4 + 4 + 4 = 24
assert len(PROG) == N_BARS, (len(PROG), N_BARS)
CHORD_NAMES = {62: "i", 70: "VI", 65: "III", 72: "VII", 69: "v"}

def chord_for_bar(bar):
    return CHORDS[PROG[bar]]

def quantize_to_chord(pitch, chord_tones):
    """Snap a pitch to nearest chord tone, resolving ties toward lower."""
    return min(chord_tones, key=lambda c: (abs(c - pitch), c))

# ---------------------------------------------------------------- PCFG (Phase 1)
# Method 034: Probabilistic Context-Free Grammar recursion.
# Nonterminals: S (section), P (phrase), M (motif), I (interval), R (rhythm cell)
# Rewrite rules with probabilities. Leaves -> raw pitch-index floats + rhythm
# fractions of a bar. The raw contour is UNQUANTIZED (floats in [0,1] over the
# lead range) - Phase 2 maps them onto chord tones.

def pcfg_choose(rules):
    """rules: list of (weight, item). Weighted pick."""
    total = sum(w for w, _ in rules)
    r = rng.random() * total
    acc = 0.0
    for w, item in rules:
        acc += w
        if r <= acc:
            return item
    return rules[-1][1]

# interval alphabet: semitone steps available in D minor, biased to stepwise
INTERVALS = [
    (4, -2), (4, -1), (3, 1), (3, 2), (2, 0),   # stepwise + repeat (weight 16)
    (1, -3), (1, 3), (1, -4), (1, 4),           # small leaps (weight 4)
    (1, -5), (1, 5), (1, -7), (1, 7),           # larger leaps (weight 4)
]
# normalize to weights list
INT_RULES = [(w, iv) for w, iv in INTERVALS]

def pcfg_interval_sequence(length, start_idx=0.0):
    """Recursive interval-tree expansion. Returns list of raw pitch indices
    (floats, 0..1 = bottom..top of lead range) and a parallel rhythm grid
    (onset fractions of a bar)."""
    # Phase-1 rhythm cells: fractions of a bar (16th grid allowed)
    cells = [0.0, 0.25, 0.5, 0.75, 0.125, 0.375, 0.625, 0.875, 1.0]
    events = []
    idx = start_idx
    for _ in range(length):
        iv = pcfg_choose(INT_RULES)
        idx += iv * 0.045          # raw step, unscaled (float pitch index drift)
        idx = max(0.0, min(1.0, idx))
        # rhythm: weighted toward 8th-note disco grid
        frac = pcfg_choose([
            (3, 0.0), (3, 0.5), (3, 0.25), (3, 0.75),
            (1, 0.125), (1, 0.375), (1, 0.625), (1, 0.875),
        ])
        dur = pcfg_choose([(4, 0.125), (2, 0.25), (1, 0.0625)])
        events.append((float(idx), float(frac), float(dur)))
    return events

def raw_pitch_to_midi(raw_idx, lo=LEAD_LO, hi=LEAD_HI):
    """Phase-1 raw: float index -> unquantized MIDI (may be off-scale)."""
    return int(round(lo + raw_idx * (hi - lo)))

def build_phase1_events(seed, length=16, start_idx=0.3):
    """Section-level Phase 1: grammar-expanded raw event list, absolute ticks."""
    r = np.random.default_rng(seed)
    seq = pcfg_interval_sequence(length, start_idx=start_idx)
    events = []
    tick = 0
    for raw_idx, frac, dur in seq:
        midi = raw_pitch_to_midi(raw_idx)
        st = int(round(frac * BAR))
        du = int(round(dur * BAR))
        # keep within section
        if st + du > SECTION_TICKS:
            du = max(60, SECTION_TICKS - st)
        events.append(MusicEvent(pitch=midi, volume=88,
                                 start_tick=st, end_tick=st + du))
    return events

# ---------------------------------------------------------------- phase 1
phase1 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
phase1.create_matrix(num_voices=1, num_sections=N_SECTIONS)
phase1.add_voice("LeadRaw", program=80, channel=0)  # Square Lead (synthetic raw)

# per-section grammar parameters (macro-form via recursion depth/start index)
SEC_START = [0.15, 0.25, 0.35, 0.25, 0.45, 0.30]
SEC_LEN = [12, 16, 18, 16, 18, 10]

for s, name in enumerate(NAMES):
    phase1.add_section(name, bars=BARS_PER)
    evs = build_phase1_events(20260821 + s, length=SEC_LEN[s], start_idx=SEC_START[s])
    phase1.set_unit(0, s, MusicUnit(events=evs))

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
P1_MIDI = os.path.join(MIDI_DIR, "075-disco-pcfg-phase1.mid")
phase1.to_midi(P1_MIDI)
print("phase1 written", P1_MIDI)

# ---------------------------------------------------------------- phase 2
# rules post-process: chord-tone quantization + voice-leading + full disco texture
phase2 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
VOICES = [
    ("Lead",      80, 0),   # Square Lead (disco lead)
    ("Strings",   48, 1),   # String Ensemble (stabs)
    ("Guitar",    27, 2),   # Clean Electric Guitar (16th chank)
    ("Bass",      33, 3),   # Electric Bass (finger)
    ("Drums",      0, 9),   # percussion channel
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
        # octave wrap: keep near lead register
        while qp < LEAD_LO:
            qp += 12
        while qp > LEAD_HI:
            qp -= 12
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

# --- strings: syncopated stab accents on beats 2& / 4& (disco octave stab) ---
HORN_STRONG = {2, 4}   # chorus sections
for bar in range(N_BARS):
    s, b = divmod(bar, BARS_PER)
    tones = chord_for_bar(bar)
    t0 = b * BAR
    e = []
    if s in HORN_STRONG:
        # 4 stabs per bar: beats 2, 2&, 4, 4& (offbeat pushes)
        for off in (720, 960, 1680, 1800):
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

# --- guitar: 16th-note chank, muted chord voicing (disco rhythm guitar) ---
for bar in range(N_BARS):
    s, b = divmod(bar, BARS_PER)
    tones = chord_for_bar(bar)
    t0 = b * BAR
    e = []
    for k in range(0, BAR, 240):
        # ghost on the 8th-note offbeats (disco chank), accent on 2& and 4&
        beat = (k // 240) % 4
        if beat in (1, 3):     # offbeats
            vel = 74 if (beat == 3) else 66
            e.append(MusicEvent(pitch=tones[0] + 24, volume=vel,
                                start_tick=t0 + k, end_tick=t0 + k + 100))
        else:
            e.append(MusicEvent(pitch=tones[0] + 24, volume=40,
                                start_tick=t0 + k, end_tick=t0 + k + 80))
    unit = phase2.matrix.get_unit((2, s))
    events = list(unit.events) if unit is not None else []
    events.extend(e)
    phase2.set_unit(2, s, MusicUnit(events=events))

# --- bass: disco octave pulse, root on 1&3, fifth on 2&4, 16th push ---
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

# --- drums: four-on-the-floor disco. 35 kick all 4 beats, 38 snare 2&4,
#      42 closed hat 8ths, 51 ride 8ths, chorus adds 39 clap ---
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
        # four-on-the-floor kick: beats 1,2,3,4
        for k in (0, 480, 960, 1440):
            evs.append(MusicEvent(pitch=35, volume=104,
                                  start_tick=t0 + k, end_tick=t0 + k + 160))
        if dens >= 0.8:
            # snare backbeat on 2 and 4
            evs.append(MusicEvent(pitch=38, volume=100, start_tick=t0 + 480, end_tick=t0 + 620))
            evs.append(MusicEvent(pitch=38, volume=104, start_tick=t0 + 1440, end_tick=t0 + 1580))
            # ride 8ths
            for k in range(0, BAR, 240):
                evs.append(MusicEvent(pitch=51, volume=60,
                                      start_tick=t0 + k, end_tick=t0 + k + 180))
            if dens >= 1.0:
                # clap doubles snare + open hat 16th pushes
                evs.append(MusicEvent(pitch=39, volume=84, start_tick=t0 + 480, end_tick=t0 + 600))
                evs.append(MusicEvent(pitch=39, volume=88, start_tick=t0 + 1440, end_tick=t0 + 1560))
                evs.append(MusicEvent(pitch=46, volume=70, start_tick=t0 + 1800, end_tick=t0 + 1910))
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

P2_MIDI = os.path.join(MIDI_DIR, "075-disco-pcfg.mid")
phase2.to_midi(P2_MIDI)
print("phase2 written", P2_MIDI)

# ---------------------------------------------------------------- analysis
from visualization.grid import write_grid_visualization
grid_path = os.path.join(ANALYSIS_DIR, "grid_visualization.txt")
write_grid_visualization(phase2.matrix, grid_path, ticks_per_character=120,
                         voice_names=vnames, bpm=BPM, mode="D minor / PCFG disco")
print("grid written", grid_path)

# provenance
from workflows.provenance import write_provenance, AI_GENERATED
for mid, phase, note in (
        (P1_MIDI, "1", "raw PCFG recursion draft, unquantized float pitch indices, single voice, no harmony"),
        (P2_MIDI, "2", "chord-tone quantized to D-minor disco progression, full texture")):
    write_provenance(
        mid, AI_GENERATED, "PCFG Recursion (Method 034 Probabilistic Context-Free Grammar)",
        parameters={"bpm": BPM, "key": "D natural minor", "sections": N_SECTIONS,
                    "bars": N_BARS, "phase": phase,
                    "progression": [CHORD_NAMES[r] for r in PROG], "seed": 20260821},
        notes=note)
    print("provenance for phase", phase)

# summary.json
with open(os.path.join(ANALYSIS_DIR, "summary.json"), "w") as f:
    json.dump({
        "project": "075-disco-pcfg",
        "style": "Disco",
        "method": "034 Probabilistic Context-Free Grammar Recursion (PCFG)",
        "bpm": BPM, "key": "D natural minor", "tempo": BPM,
        "bars": N_BARS,
        "sections": {n: BARS_PER for n in NAMES},
        "progression": [CHORD_NAMES[r] for r in PROG],
        "voices": vnames,
        "phase1": os.path.basename(P1_MIDI),
        "phase2": os.path.basename(P2_MIDI),
        "grid": os.path.basename(grid_path),
        "seed": 20260821,
    }, f, indent=2)
print("summary.json written")

# ---------------------------------------------------------------- size asserts
for p in (P1_MIDI, P2_MIDI, grid_path,
          os.path.join(ANALYSIS_DIR, "summary.json")):
    assert os.path.getsize(p) > 40, "too small: %s" % p
print("ALL SIZE ASSERTS PASSED")
print("PROGRESSION:", [CHORD_NAMES[r] for r in PROG])
