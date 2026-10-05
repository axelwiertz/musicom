# -*- coding: utf-8 -*-
"""223-rock-euclidean-extended - REWORK of 093-rock-euclidean (Rock x Method 012).

Source: Styles/Rock/093-rock-euclidean (2026-09-11) - 6 sections / 6 voices / 24 bars.
Rework decision: audit FAILED exactly one standard (index.html missing). All other
standards pass (engine-authored, zero-drift, grid-locked, 6 tracks, two-phase,
provenance present). Rebuilt LONGER + MORE VARIED while preserving musical identity.

Identity preserved: Rock, E aeolian, 128 BPM, 4/4, Euclidean Groove Locking
(method 012), fiddle-lead texture + guitar chank + piano stab + organ pad +
double-bass drive + GM kit.

WHAT CHANGED (rework -> longer + more variation):
  - Form: 6 -> 8 sections (Intro/Verse/Verse2/Chorus/Bridge/Chorus2/Solo/Outro)
         24 -> 32 bars.
  - +1 voice: Flute counterline (contrary-motion chord arpeggio) in
         Chorus/Chorus2/Solo.
  - Variation techniques (6, all diatonic-safe within E aeolian):
        1. AUGMENTATION  - Intro + Outro lead rhythm: euclidian(6,16)@120
                           -> euclidian(3,4)@480 (half-note spacing).
        2. TRANSPOSITION - Verse2 lead contour shifted +5 scale degrees (E4->C5).
        3. REGISTER SHIFT - Chorus/Chorus2 lead moves up one octave (72-96 pool).
        4. INVERSION     - Bridge lead contour = negated motif deltas.
        5. DIMINUTION    - Solo lead rhythm: euclidian(8,8)@240 (8th-note run).
        6. RETROGRADE    - Outro lead contour = reversed motif.
  - Density rise across the drum kit (kick-only -> kick+hat -> +snare -> full
         +crash -> +tom fills -> sparse outro).
  - Per-section harmonic regions: every section has its OWN 4-bar progression
    (no all-tonic bar-0 bug); section roots read from the MIDPOINT chord.

Engine only: structures + workflows.unitmatrix_composer + generators.rhythm +
rules.progression + rules.voice_leading. NO raw mido authoring, NO
sys.path.insert (instruments referenced by raw GM program numbers / engine
MidiInstrument enum / MidiPercussion constants).
"""
import itertools
import json
import os

import numpy as np

from structures import (MusicUnit, MusicEvent, MidiInstrument, MidiPercussion)
from workflows.unitmatrix_composer import UnitMatrixComposer, create_empty_unit
from generators.rhythm import euclidian              # method 012 implementation
from rules.progression import Scale7ChordDegree      # canonical diatonic helper
from rules.voice_leading import VoiceLeadingRules

SEED = 20261005
rng = np.random.default_rng(SEED)

# ---------------------------------------------------------------- project dirs
PROJ = "/opt/data/projects/Styles/Rock/223-rock-euclidean-extended"
MIDI_DIR = os.path.join(PROJ, "MIDI")
AUDIO_DIR = os.path.join(PROJ, "Audio")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")
for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
    os.makedirs(d, exist_ok=True)

# ---------------------------------------------------------------- concept
BPM = 128
TPB = 480
BEATS = 4
BAR = TPB * BEATS            # 1920
GRID16 = 120
GRID8 = 240
BARS_PER = 4
SECTION_TICKS = BAR * BARS_PER          # 7680
NAMES = ["Intro", "Verse", "Verse2", "Chorus", "Bridge", "Chorus2", "Solo", "Outro"]
N_SECTIONS = len(NAMES)                 # 8
N_BARS = N_SECTIONS * BARS_PER          # 32
TOTAL_TICKS = N_BARS * BAR              # 61440

# E aeolian (natural minor): E F# G A B C D ; key root = E4 (MIDI 64)
KEY_ROOT = 64
AEOLIAN = [0, 2, 3, 5, 7, 8, 10]
SCALE_PCS = {(KEY_ROOT + i) % 12 for i in AEOLIAN}     # {4,6,7,9,11,0,2}
SCALE_PITCHES = [p for p in range(36, 97) if p % 12 in SCALE_PCS]


def degree_note(d):
    """Canonical diatonic note (no local % 7 wrapper)."""
    return Scale7ChordDegree.get_diatonic_note(KEY_ROOT, AEOLIAN, d)


def degree_pc(d):
    return degree_note(d) % 12


def degree_triad_pcs(d):
    return {degree_note(d + k) % 12 for k in (0, 2, 4)}


# 32-bar rock progression (E aeolian, 0-based scale degrees).
# Each 4-bar section is its OWN short progression. Section roots are read from
# the MIDPOINT chord (bar index 2), never the bar-0 tonic, so no all-tonic bug.
PROG_DEG = (
    [0, 0, 5, 6] +    # Intro   i  i  VI VII
    [0, 5, 2, 6] +    # Verse   i  VI III VII
    [5, 2, 6, 0] +    # Verse2  VI III VII i   (transposed)
    [5, 6, 0, 0] +    # Chorus  VI VII i  i
    [3, 5, 2, 6] +    # Bridge  iv VI III VII
    [5, 6, 0, 0] +    # Chorus2 VI VII i  i
    [0, 2, 6, 5] +    # Solo    i  III VII VI
    [0, 0, 5, 0])     # Outro   i  i  VI i
assert len(PROG_DEG) == N_BARS, (len(PROG_DEG), N_BARS)
DEG_NAME = {0: "i", 1: "ii", 2: "III", 3: "iv", 4: "v", 5: "VI", 6: "VII"}
PC_NAME = {4: "E", 6: "F#", 7: "G", 9: "A", 11: "B", 0: "C", 2: "D"}
BAR_LABELS = [PC_NAME[degree_pc(d)] + DEG_NAME[d] for d in PROG_DEG]

# section roots = MIDPOINT chord degree (bar index 2 of each 4-bar section)
SECTION_MIDPOINT_DEG = [PROG_DEG[s * BARS_PER + 2] for s in range(N_SECTIONS)]


def chord_tones(deg, lo, hi):
    """Chord tones (diatonic triad) of degree `deg` inside [lo, hi]."""
    pcs = degree_triad_pcs(deg)
    return sorted(p for p in range(lo, hi + 1) if p % 12 in pcs)


def nearest_pc_pitch(pc, lo, hi, anchor=None):
    cands = [p for p in range(lo, hi + 1) if p % 12 == pc]
    if not cands:
        return None
    if anchor is None:
        return min(cands, key=lambda p: (abs(p - (lo + hi) // 2), p))
    return min(cands, key=lambda p: (abs(p - anchor), p))


# ---------------------------------------------------------------- method 012
def euclid_onsets(k, n, unit, rot=0):
    """Onset ticks inside ONE metric cycle (method 012, engine generator)."""
    ivs = euclidian(k, n)
    pos, t = [], 0
    for i in ivs:
        pos.append(t)
        t += i
    total = t
    ons = sorted({((p + rot) % total) * unit for p in pos})
    return ons, total * unit


# Euclidean pattern (k, n, step_ticks). All are metric -> grid-locked by
# construction (integer step positions * unit => multiples of GRID16/GRID8).
PATTERNS = {
    "lead":    (6, 16, GRID16),   # 0 360 720 1080 1440 (syncopated 16th lock)
    "lead_dim": (8, 8, GRID8),    # 0 240 ... 1680       (8th-note run, diminution)
    "lead_aug": (3, 4, TPB),      # 0 960               (half-note, augmentation)
    "lead_sparse": (3, 8, GRID8), # 0 720 1440           (sparse)
    "guitar":  (4, 16, GRID16),   # 0 480 960 1440       (quarter chank)
    "piano":   (3, 8, GRID8),     # 0 720 1440           (offbeat stabs)
    "bass":    (8, 8, GRID8),     # 0 240 ... 1680       (8th drive)
    "kick":    (4, 16, GRID16),   # 0 480 960 1440
    "snare":   (2, 8, GRID8),     # rot 2 -> 480 1440    (backbeat)
    "hat":     (8, 16, GRID16),   # 0 240 ... 1680
    "organ":   (1, 4, TPB),       # 0                    (whole-bar sustain)
}
for _lbl, (_k, _n, _u) in PATTERNS.items():
    _ons, _cyc = euclid_onsets(_k, _n, _u)
    assert _cyc == BAR, (_lbl, _k, _n, _u, _cyc)
    assert all(o % GRID16 == 0 for o in _ons), (_lbl, _ons)

# ---------------------------------------------------------------- phase 1
# Raw generative draft: single voice, Euclidean intervals at a FRACTIONAL tick
# unit (off-grid by construction) + unquantized pitch walk. No scale, no chord,
# no harmony, no other voices.
P1_PAIRS = [(6, 16), (3, 8), (4, 16), (7, 16), (2, 8), (6, 16), (8, 8), (3, 4)]
P1_N = {0: 26, 1: 34, 2: 34, 3: 34, 4: 34, 5: 34, 6: 40, 7: 26}
P1_C = {0: 74.0, 1: 76.0, 2: 78.0, 3: 79.0, 4: 77.0, 5: 79.0, 6: 78.0, 7: 74.0}


def raw_euclid_melody(seed, section_ticks, n_events, center0):
    r = np.random.default_rng(seed)
    k, n = P1_PAIRS[seed % len(P1_PAIRS)]
    ivs = euclidian(k, n)
    cycle_steps = sum(ivs)
    unit = section_ticks / float(cycle_steps * max(1, n_events / cycle_steps))
    evs = []
    tick = 0.0
    center = center0
    i = 0
    while len(evs) < n_events:
        d = ivs[i % len(ivs)]
        step = unit * d * (0.94 + 0.12 * r.random())
        dur = max(60, int(round(step)) - 47)
        if tick + step > section_ticks:
            break
        p = center + r.choice([-5, -3, -2, -1, 1, 2, 3, 4, 7]) + 0.9 * r.normal(0, 1.0)
        p = max(55.0, min(96.0, p))
        vel = int(np.clip(66 + 24 * abs(np.sin(i * 1.13)), 50, 108))
        evs.append(MusicEvent(pitch=int(round(p)), volume=vel,
                              start_tick=int(round(tick)),
                              end_tick=int(round(tick)) + dur))
        tick += step
        center += r.normal(0.0, 0.9)
        i += 1
    return evs


phase1 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
phase1.create_matrix(num_voices=1, num_sections=N_SECTIONS)
phase1.add_voice("LeadRaw", program=110, channel=0)

for s, name in enumerate(NAMES):
    phase1.add_section(name, bars=BARS_PER)
    evs = raw_euclid_melody(SEED + s, SECTION_TICKS, P1_N[s], P1_C[s])
    if not evs or evs[-1].end_tick < SECTION_TICKS:
        evs.append(MusicEvent(pitch=0, volume=0,
                              start_tick=SECTION_TICKS - 1,
                              end_tick=SECTION_TICKS))
    phase1.set_unit(0, s, MusicUnit(events=evs))

ok1, msg1 = phase1.validate()
print("PHASE1 validate:", ok1, msg1)
assert ok1, msg1
P1_MIDI = os.path.join(MIDI_DIR, "223-rock-euclidean-extended-phase1.mid")
phase1.to_midi(P1_MIDI)
print("phase1 written", P1_MIDI, os.path.getsize(P1_MIDI), "bytes")

# ---------------------------------------------------------------- phase 2
# 7 voices. Raw GM program numbers (instrument registry is not pip-installed;
# engine MidiInstrument enum + raw programs, no sys.path.insert).
VOICES = [
    ("Lead",    110, 0),                    # Fiddle (rock lead)
    ("Counter", 74,  1),                    # Flute (counterline)
    ("Guitar",  25,  2),                    # Acoustic guitar (chank)
    ("Piano",   0,   3),                    # Acoustic grand piano
    ("Organ",   20,  4),                    # Church organ pad
    ("Bass",    43,  5),                    # Double bass
    ("Drums",   0,   9),                    # GM kit (ch 9)
]
N_V = len(VOICES)

phase2 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
phase2.create_matrix(num_voices=N_V, num_sections=N_SECTIONS)
for name, prog, ch in VOICES:
    phase2.add_voice(name, program=prog, channel=ch)
for n in NAMES:
    phase2.add_section(n, bars=BARS_PER)

# lead melodic DNA: base motif = scale-degree deltas (mostly stepwise + a few
# 3rds/4ths). Section transforms applied to this contour (see docstring).
MOTIF = [0, 1, 2, 1, -1, 0, 2, 3, -1, -2, 1, 0]
LEAD_POOL_LO = [p for p in SCALE_PITCHES if 60 <= p <= 96]
LEAD_POOL_HI = [p for p in SCALE_PITCHES if 72 <= p <= 96]

# per-section lead plan: (rhythm_key, pool, start_pool_idx, contour_transform)
LEAD_PLAN = {
    "Intro":   ("lead_aug",    "lo", 2, "base"),        # augmentation
    "Verse":   ("lead",        "lo", 2, "base"),
    "Verse2":  ("lead",        "lo", 7, "transpose"),   # +5 scale degrees
    "Chorus":  ("lead",        "hi", 2, "register"),    # octave up
    "Bridge":  ("lead_sparse", "lo", 4, "invert"),
    "Chorus2": ("lead",        "hi", 2, "register"),    # octave up
    "Solo":    ("lead_dim",    "lo", 2, "diminish"),    # 8th-note run
    "Outro":   ("lead_aug",    "lo", 2, "retrograde"),
}


def contour_steps(transform):
    if transform == "invert":
        return [-x for x in MOTIF]
    if transform == "retrograde":
        return MOTIF[::-1]
    return MOTIF          # base / transpose / register / augment / diminish


def lead_duration(rhythm_key):
    return 360 if rhythm_key == "lead_aug" else 118


# --- row 0 LEAD
for s in range(N_SECTIONS):
    name = NAMES[s]
    rkey, pool, start_idx, transform = LEAD_PLAN[name]
    k, n, unit = PATTERNS[rkey]
    pool_list = LEAD_POOL_HI if pool == "hi" else LEAD_POOL_LO
    steps = contour_steps(transform)
    dur = lead_duration(rkey)
    evs = []
    idx = start_idx
    gcount = 0
    for b in range(BARS_PER):
        t0 = b * BAR
        bar = s * BARS_PER + b
        deg = PROG_DEG[bar]
        lo = pool_list[0]
        hi = pool_list[-1]
        tones = chord_tones(deg, lo, hi) or [degree_note(deg) + 24]
        rot = (b + s) % 3
        ons, _ = euclid_onsets(k, n, unit, rot=rot)
        for j, off in enumerate(ons):
            step = steps[gcount % len(steps)]
            idx = max(0, min(len(pool_list) - 1, idx + step))
            p = pool_list[idx]
            qp = min(tones, key=lambda c: (abs(c - p), c))
            accent = 0 if off % 480 == 0 else (1 if off % 240 == 0 else 2)
            vel = (92, 82, 74)[accent]
            evs.append(MusicEvent(pitch=qp, volume=vel,
                                  start_tick=t0 + off, end_tick=t0 + off + dur))
            gcount += 1
    evs.sort(key=lambda e: e.start_tick)
    # voice leading: cap leaps > 10 semitones toward the nearest chord tone
    for i in range(1, len(evs)):
        if abs(evs[i].pitch - evs[i - 1].pitch) > 10:
            bar = s * BARS_PER + min(evs[i].start_tick // BAR, BARS_PER - 1)
            tones = chord_tones(PROG_DEG[bar], pool_list[0], pool_list[-1])
            if tones:
                evs[i].pitch = min(tones, key=lambda c: (abs(c - evs[i - 1].pitch), c))
    for i in range(len(evs) - 1):               # monophonic legato
        if evs[i].end_tick > evs[i + 1].start_tick:
            evs[i].end_tick = evs[i + 1].start_tick
    phase2.set_unit(0, s, MusicUnit(events=evs))

# --- row 1 COUNTER (Flute): contrary-motion chord arpeggio (quarter notes) in
# Chorus / Chorus2 / Solo; silent elsewhere.
for s in range(N_SECTIONS):
    evs = []
    if NAMES[s] in ("Chorus", "Chorus2", "Solo"):
        for b in range(BARS_PER):
            t0 = b * BAR
            deg = PROG_DEG[s * BARS_PER + b]
            tones = chord_tones(deg, 72, 96) or [degree_note(deg) + 24]
            root = tones[0]
            # root -> 3rd -> 5th -> 3rd (quarter-note step, 480 ticks)
            seq = [root, tones[1] if len(tones) > 1 else root,
                   tones[2] if len(tones) > 2 else root,
                   tones[1] if len(tones) > 1 else root]
            for j, p in enumerate(seq):
                evs.append(MusicEvent(pitch=p, volume=64 + 4 * j,
                                      start_tick=t0 + j * 480,
                                      end_tick=t0 + j * 480 + 400))
    phase2.set_unit(1, s, MusicUnit(events=evs))

# --- row 2 GUITAR: Euclidean quarter-note chank (root + fifth dyads)
for s in range(N_SECTIONS):
    k, n, unit = PATTERNS["guitar"]
    evs = []
    for b in range(BARS_PER):
        t0 = b * BAR
        deg = PROG_DEG[s * BARS_PER + b]
        tones = chord_tones(deg, 40, 84) or [52]
        root = min(tones, key=lambda c: abs(c - 52))
        cands = [t for t in tones if t > root and (t - root) % 12 in (7, 5)]
        if not cands:
            cands = [t for t in tones if t > root]
        if not cands:
            cands = [root]
        fifth = min(cands, key=lambda c: abs(c - (root + 7)))
        ons, _ = euclid_onsets(k, n, unit)
        for j, off in enumerate(ons):
            vel = 92 if off % 480 == 0 else 76
            evs.append(MusicEvent(pitch=root, volume=vel,
                                  start_tick=t0 + off, end_tick=t0 + off + 110))
            evs.append(MusicEvent(pitch=fifth, volume=vel - 8,
                                  start_tick=t0 + off, end_tick=t0 + off + 110))
    phase2.set_unit(2, s, MusicUnit(events=evs))

# --- row 3 PIANO: Euclidean offbeat stabs E(3,8)
for s in range(N_SECTIONS):
    k, n, unit = PATTERNS["piano"]
    evs = []
    for b in range(BARS_PER):
        t0 = b * BAR
        deg = PROG_DEG[s * BARS_PER + b]
        tones = chord_tones(deg, 55, 79) or [64]
        ons, _ = euclid_onsets(k, n, unit, rot=(s + b) % 3)
        for j, off in enumerate(ons):
            p = tones[(j + b) % len(tones)]
            evs.append(MusicEvent(pitch=p, volume=62,
                                  start_tick=t0 + off, end_tick=t0 + off + 110))
    phase2.set_unit(3, s, MusicUnit(events=evs))

# --- row 4 ORGAN: whole-bar sustained triad (widened an octave in Chorus2)
for s in range(N_SECTIONS):
    k, n, unit = PATTERNS["organ"]
    evs = []
    widen = (NAMES[s] == "Chorus2")
    for b in range(BARS_PER):
        t0 = b * BAR
        deg = PROG_DEG[s * BARS_PER + b]
        tones = chord_tones(deg, 55, 79) or [64]
        pad = tones[:3]
        if widen:
            pad = pad + [pad[0] + 12]
        for j, p in enumerate(pad):
            evs.append(MusicEvent(pitch=p, volume=44 + 4 * j,
                                  start_tick=t0, end_tick=t0 + BAR - 60))
    phase2.set_unit(4, s, MusicUnit(events=evs))

# --- row 5 BASS: Euclidean 8th-note drive (root + octave)
for s in range(N_SECTIONS):
    k, n, unit = PATTERNS["bass"]
    evs = []
    for b in range(BARS_PER):
        t0 = b * BAR
        deg = PROG_DEG[s * BARS_PER + b]
        root = nearest_pc_pitch(degree_pc(deg), 33, 50, anchor=40) or 40
        ons, _ = euclid_onsets(k, n, unit)
        for j, off in enumerate(ons):
            p = root if j % 2 == 0 else min(root + 12, 62)
            evs.append(MusicEvent(pitch=p,
                                  volume=94 if off % 480 == 0 else 78,
                                  start_tick=t0 + off, end_tick=t0 + off + 200))
    phase2.set_unit(5, s, MusicUnit(events=evs))

# --- row 6 DRUMS: Euclidean kit with a density-rise plan (variation technique 6)
KICK = MidiPercussion.BASS_DRUM        # 36
SNARE = MidiPercussion.ACOUSTIC_SNARE   # 38
HAT = MidiPercussion.CLOSED_HI_HAT      # 42
CRASH = MidiPercussion.CRASH_CYMBAL     # 49
TOM_LO = MidiPercussion.LOW_TOM         # 45
TOM_MID = MidiPercussion.MID_TOM        # 47
TOM_HI = MidiPercussion.HIGH_TOM        # 50

DRUM_PLAN = {
    0: dict(kick=96,  snare=None, hat=None, crash=False, toms=False),   # Intro: kick only
    1: dict(kick=104, snare=None, hat=56,   crash=False, toms=False),   # Verse: +hat
    2: dict(kick=110, snare=88,  hat=60,   crash=False, toms=False),    # Verse2: +snare
    3: dict(kick=118, snare=96,  hat=70,   crash=True,  toms=False),    # Chorus: full+crash
    4: dict(kick=104, snare=None, hat=56,   crash=False, toms=True),    # Bridge: +toms
    5: dict(kick=118, snare=96,  hat=72,   crash=True,  toms=False),    # Chorus2: full
    6: dict(kick=118, snare=96,  hat=72,   crash=True,  toms=True),     # Solo: full+toms
    7: dict(kick=96,  snare=None, hat=52,   crash=False, toms=False),   # Outro: sparse
}

for s in range(N_SECTIONS):
    plan = DRUM_PLAN[s]
    kk, kn, ku = PATTERNS["kick"]
    sk, sn, su = PATTERNS["snare"]
    hk, hn, hu = PATTERNS["hat"]
    evs = []
    for b in range(BARS_PER):
        t0 = b * BAR
        for off in euclid_onsets(kk, kn, ku)[0]:
            evs.append(MusicEvent(pitch=KICK, volume=plan["kick"],
                                  start_tick=t0 + off, end_tick=t0 + off + 120))
        if plan["hat"] is not None:
            for off in euclid_onsets(hk, hn, hu)[0]:
                evs.append(MusicEvent(pitch=HAT, volume=plan["hat"],
                                      start_tick=t0 + off, end_tick=t0 + off + 60))
        if plan["snare"] is not None:
            for off in euclid_onsets(sk, sn, su, rot=2)[0]:
                evs.append(MusicEvent(pitch=SNARE, volume=plan["snare"],
                                      start_tick=t0 + off, end_tick=t0 + off + 120))
        if plan["crash"] and b == 0:
            evs.append(MusicEvent(pitch=CRASH, volume=98,
                                  start_tick=t0, end_tick=t0 + 240))
        if plan["toms"] and b == BARS_PER - 1:
            # 16th-note fill on beat 4 (all on-grid)
            fill = [(1440, TOM_HI), (1560, TOM_MID), (1680, TOM_LO), (1800, TOM_LO)]
            for off, p in fill:
                evs.append(MusicEvent(pitch=p, volume=86,
                                      start_tick=t0 + off, end_tick=t0 + off + 100))
    phase2.set_unit(6, s, MusicUnit(events=evs))

# --- voice-leading check/correction (outer voices = bass + lead)
vlc = VoiceLeadingRules(style="classical")
vl_flags = []
for bar in range(N_BARS - 1):
    s, b = divmod(bar, BARS_PER)
    deg_a, deg_b = PROG_DEG[bar], PROG_DEG[bar + 1]
    bass_a = nearest_pc_pitch(degree_pc(deg_a), 33, 50, anchor=40) or 40
    bass_b = nearest_pc_pitch(degree_pc(deg_b), 33, 50, anchor=40) or 40
    s2, b2 = (s, b + 1) if b + 1 < BARS_PER else (s + 1, 0)
    if s2 >= N_SECTIONS:
        continue

    def bar_evs(sec, bb, row=0):
        u = phase2.matrix.get_unit((row, sec))
        return [e for e in u.events
                if e.pitch > 0 and bb * BAR <= e.start_tick < (bb + 1) * BAR]

    evs, evs_next = bar_evs(s, b), bar_evs(s2, b2)
    if evs and evs_next:
        # int() casts defeat numpy uint8 underflow in the rules module arithmetic
        viol = vlc.check_parallel_motion([int(bass_a), int(evs[0].pitch)],
                                         [int(bass_b), int(evs_next[0].pitch)])
        if viol:
            vl_flags.append((bar, "parallel", viol))
        hid = vlc.check_hidden_fifths([int(bass_a), int(evs[0].pitch)],
                                      [int(bass_b), int(evs_next[0].pitch)])
        if hid:
            vl_flags.append((bar, "hidden", hid))
print("VL flags (bass+lead, classical):", len(vl_flags))


def fix_outer_voice(bar_target):
    s, b = divmod(bar_target, BARS_PER)
    u = phase2.matrix.get_unit((0, s))
    evs = list(u.events)
    target = None
    for e in evs:
        if e.pitch > 0 and b * BAR <= e.start_tick < (b + 1) * BAR:
            target = e
            break
    if target is None:
        return False
    tp = int(target.pitch)
    tones = chord_tones(PROG_DEG[bar_target], 60, 96)
    bass = nearest_pc_pitch(degree_pc(PROG_DEG[bar_target]), 33, 50,
                            anchor=40) or 40
    cands = [t for t in tones if (t - bass) % 12 not in (0, 7)]
    cands = [t for t in cands if abs(t - tp) <= 10]
    if not cands:
        return False
    target.pitch = min(cands, key=lambda c: (abs(c - tp), c))
    phase2.set_unit(0, s, MusicUnit(events=evs))
    return True


n_fixed = 0
for (bar, _kind, _v) in list(vl_flags):
    if fix_outer_voice(bar + 1):
        n_fixed += 1
print("VL fixes applied:", n_fixed)

# --- normalize every cell to the exact section boundary (zero-drift invariant)
def normalize_cell(unit, total_ticks):
    evs = list(unit.events)
    for e in evs:
        if e.end_tick > total_ticks:
            e.end_tick = total_ticks
        if e.start_tick >= total_ticks:
            e.start_tick = total_ticks - 10
        if e.start_tick < 0:
            e.start_tick = 0
        if e.end_tick <= e.start_tick:
            e.end_tick = min(total_ticks, e.start_tick + 60)
    if not evs or evs[-1].end_tick < total_ticks:
        evs.append(MusicEvent(pitch=0, volume=0, start_tick=total_ticks - 1,
                              end_tick=total_ticks))
    return MusicUnit(events=sorted(evs, key=lambda e: (e.start_tick, e.pitch)))


for s in range(N_SECTIONS):
    for v in range(N_V):
        u = phase2.matrix.get_unit((v, s))
        if u is None:
            phase2.set_unit(v, s, create_empty_unit(SECTION_TICKS))
            continue
        phase2.set_unit(v, s, normalize_cell(u, SECTION_TICKS))

ok2, msg2 = phase2.validate()
print("PHASE2 validate:", ok2, msg2)
assert ok2, msg2
P2_MIDI = os.path.join(MIDI_DIR, "223-rock-euclidean-extended.mid")
phase2.to_midi(P2_MIDI)
print("phase2 written", P2_MIDI, os.path.getsize(P2_MIDI), "bytes")

# --- provenance sidecars
from workflows.provenance import write_provenance, AI_ASSISTED  # noqa: E402
write_provenance(P1_MIDI, classification=AI_ASSISTED,
                 generator="generators.rhythm.euclidian (method 012)",
                 parameters={"phase": 1, "seed": SEED, "bpm": BPM,
                             "key": "E aeolian", "method": "012 Euclidean Groove Locking",
                             "sections": N_SECTIONS, "bars": N_BARS},
                 notes="Raw Euclidean draft: euclidian() intervals at a fractional "
                       "(off-grid) tick unit + unquantized pitch walk. Single voice, "
                       "no harmony.")
write_provenance(P2_MIDI, classification=AI_ASSISTED,
                 generator="generators.rhythm.euclidian + musicom rules layer",
                 parameters={"phase": 2, "seed": SEED, "bpm": BPM,
                             "key": "E aeolian", "method": "012 Euclidean Groove Locking",
                             "sections": N_SECTIONS, "bars": N_BARS,
                             "rework_of": "093-rock-euclidean",
                             "variation": ["augmentation", "transposition",
                                           "register_shift", "inversion",
                                           "diminution", "retrograde",
                                           "density_rise"]},
                 notes="Rework of 093-rock-euclidean (audit: index.html missing). "
                       "Extended 6->8 sections, 24->32 bars, +1 flute counterline, "
                       "6 variation techniques, per-section harmonic regions.")

# --- grid visualization
from visualization.grid import write_grid_visualization  # noqa: E402
write_grid_visualization(phase2.matrix,
                         os.path.join(ANALYSIS_DIR, "grid_visualization.txt"),
                         ticks_per_character=240,
                         voice_names=[v[0] for v in VOICES],
                         bpm=BPM, mode="E aeolian")
print("grid viz written")

# --- summary numbers for the report
print("\n=== SUMMARY ===")
print("sections:", N_SECTIONS, "bars:", N_BARS, "total_ticks:", TOTAL_TICKS)
print("progression per bar:", BAR_LABELS)
print("section midpoint degrees:", [DEG_NAME[d] for d in SECTION_MIDPOINT_DEG])
print("voices:", [v[0] for v in VOICES])
print("variation: augmentation, transposition, register_shift, inversion, "
      "diminution, retrograde, density_rise")
print("vl_flags:", len(vl_flags), "vl_fixes:", n_fixed)
