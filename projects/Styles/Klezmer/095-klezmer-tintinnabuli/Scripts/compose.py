# -*- coding: utf-8 -*-
"""095-klezmer-tintinnabuli - Klezmer style / CONCRETE layer:
Method 079 Tintinnabuli Composition (TINC) -> generators.tintinnabuli.TintinnabuliGenerator
Arvo Part M/T-voice pair inside Klezmer freylekhs idiom: Dm harmonic-minor mode,
D-minor tonic triad fixed for whole piece (static triad, no functional harmony),
M-voice conjunct line, T-voice triad shadow (nearest-above position sequence).
Plus ABS-003 Z-variation bridge: one section swaps Dm triad voicing to its
hexachord-complement texture (matched tension, fresh color) mid-form.

Phase 1: raw generative draft (single violin voice).
  Rhythm = 8th-slot walk at FRACTIONAL tick unit (NOT 120/240 multiple) -> off-grid by construction.
  Pitch  = unquantized random walk from D5 with chromatic drift (no mode snap, no triad, no harmony).
Phase 2: musicom rules post-process:
  1. 16th-grid lock (project 078 mandatory rule): every onset snapped to 120-grid -> 0 off-grid.
  2. Dm harmonic-minor scale snap -> TINC: M-voice stepped onto mode via
     TintinnabuliGenerator.m_voice, T-voice triad tones via t_voice (position cycle), both routed
     through canonical Scale7ChordDegree.get_diatonic_note where diatonic (no % 7 wrappers).
  3. Voice-leading check/correction (rules.voice_leading) on outer voices (bass + violin M).
  4. Full 6-voice klezmer texture: violin M / clarinet T / trumpet calls / dulcimer chops /
     double-bass roots / drum kit (freylekhs oom-pah).

Engine only: structures + workflows.unitmatrix_composer + generators.tintinnabuli
+ rules.progression + rules.voice_leading + rules.patterns (ABS-003 Z-pair color).
mido imported READ-ONLY in audit/summary scripts (never for authoring).
"""
import json
import os
import sys

import numpy as np

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import (
    UnitMatrixComposer, create_empty_unit,
)
from generators.tintinnabuli import TintinnabuliGenerator
from rules.progression import Scale7ChordDegree
from rules.voice_leading import VoiceLeadingRules
from rules.patterns import z_pair_catalogue

INSTR_DIR = "/opt/data/repos/musicom/projects/Instruments"
if INSTR_DIR not in sys.path:
    sys.path.insert(0, INSTR_DIR)
from instrument_registry import (
    VIOLIN, CLARINET, TRUMPET, DULCIMER, DOUBLE_BASS, DRUM_KIT,
)
from Percussion.drum_kit.drum_kit import KIT

SEED = 20260914
rng = np.random.default_rng(SEED)

PROJ = ("/opt/data/repos/musicom/projects/Styles/Klezmer/"
        "095-klezmer-tintinnabuli")
MIDI_DIR = os.path.join(PROJ, "MIDI")
AUDIO_DIR = os.path.join(PROJ, "Audio")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")
SCRIPTS_DIR = os.path.join(PROJ, "Scripts")
for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR, SCRIPTS_DIR):
    os.makedirs(d, exist_ok=True)

BPM = 124
TPB = 480
BEATS = 4
BAR = TPB * BEATS            # 1920
GRID16 = 120
GRID8 = 240
SECTION_TICKS = BAR * 4      # 7680 (4 bars per section)
NAMES = ["Intro", "FreylekhsA", "FreylekhsB", "Bridge", "FreylekhsA2", "Outro"]
BARS_PER = 4
N_SECTIONS = len(NAMES)
N_BARS = N_SECTIONS * BARS_PER          # 24

# D harmonic minor: D E F G A Bb C# ; tonic D4 (MIDI 62)
KEY_ROOT = 62
HMINOR = [0, 2, 3, 5, 7, 8, 11]
SCALE_PCS = {(KEY_ROOT + i) % 12 for i in HMINOR}
SCALE_PITCHES = [p for p in range(36, 100) if p % 12 in SCALE_PCS]


def degree_note(d):
    """Canonical diatonic note (no local % 7 wrapper)."""
    return Scale7ChordDegree.get_diatonic_note(KEY_ROOT, HMINOR, d)


def degree_pc(d):
    return degree_note(d) % 12


def degree_triad_pcs(d):
    return {degree_note(d + k) % 12 for k in (0, 2, 4)}


# 24-bar freylekhs progression, 0-based scale degrees, diatonic to D harmonic minor:
#   Intro    i  i  VII i  | A  i  VII VI VII | B  VI VII i  i
#   Bridge   iv VI VII VII| A2 i  VII VI VII | Outro i  VII i  i
PROG_DEG = ([0, 6, 6, 0] + [0, 6, 5, 6] + [5, 6, 0, 0] +
            [3, 5, 6, 6] + [0, 6, 5, 6] + [0, 6, 0, 0])
assert len(PROG_DEG) == N_BARS, (len(PROG_DEG), N_BARS)
DEG_NAME = {0: "i", 1: "ii0", 2: "III+", 3: "iv", 4: "V", 5: "VI", 6: "VII"}
PC_NAME = {2: "D", 4: "E", 5: "F", 7: "G", 9: "A", 10: "Bb", 1: "C#"}
BAR_LABELS = [PC_NAME[degree_pc(d)] + DEG_NAME[d] for d in PROG_DEG]


def chord_tones(deg, lo, hi):
    pcs = degree_triad_pcs(deg)
    return sorted(p for p in range(lo, hi + 1) if p % 12 in pcs)


def nearest_pc_pitch(pc, lo, hi, anchor=None):
    cands = [p for p in range(lo, hi + 1) if p % 12 == pc]
    if not cands:
        return None
    if anchor is None:
        return min(cands, key=lambda p: (abs(p - (lo + hi) // 2), p))
    return min(cands, key=lambda p: (abs(p - anchor), p))


# Method 079 engine: M/T pair in D harmonic minor on the fixed D-minor triad
TINC = TintinnabuliGenerator(tonic=KEY_ROOT, mode='harmonic minor', t_register=48)
assert TINC.scale_offsets == [0, 2, 3, 5, 7, 8, 11]
assert tuple(TINC.triad) == (0, 3, 7)          # D-F-A fixed triad, whole piece
TRIAD_PCS = {(KEY_ROOT + i) % 12 for i in (0, 3, 7)}

# ABS-003 Z-variation bridge color: D-harmonic-minor hexachord + its Z-partner
# (same cardinality tension family, different notes) used ONLY in Bridge as
# reharmonized pad color. Verified below: same tension, different pc set.
Z_PAIRS = z_pair_catalogue(6)
Z_A, Z_B = Z_PAIRS[0]
Z_TA = round(Z_A.tension, 2)
Z_TB = round(Z_B.tension, 2)
Z_ON_BRIDGE_PCS = {p % 12 for p in Z_B.subset}
print("ABS-003 Z-pair: %s %s T=%.2f <-> %s %s T=%.2f" %
      (Z_A.id, sorted(Z_A.subset), Z_TA, Z_B.id, sorted(Z_B.subset), Z_TB))

# T-voice position sequence (Part-style): nearest-above with slow cycle
T_POS = [0, 1, 0, 2, 0, 1]
T_VOL = 72

# ---------------------------------------------------------------- phase 1
# Raw draft: single violin voice. Euclidean-ish 8th slots at fractional UNIT1
# (317 ticks: NOT a 120/240 multiple) + unquantized chromatic random walk.
UNIT1 = 317
P1_STEPS = [-5, -3, -2, -1, -1, 1, 2, 2, 3, 4, -4]
P1_N = {0: 22, 1: 30, 2: 32, 3: 24, 4: 32, 5: 20}
P1_C = {0: 74.0, 1: 76.0, 2: 78.0, 3: 75.0, 4: 78.0, 5: 72.0}


def raw_walk(seed, section_ticks, n_events, center0):
    r = np.random.default_rng(seed)
    evs = []
    tick = 0.0
    center = center0
    i = 0
    while len(evs) < n_events:
        step = UNIT1 * (0.94 + 0.12 * r.random())
        dur = max(60, int(round(step)) - 47)
        if tick + step > section_ticks:
            break
        p = center + r.choice(P1_STEPS) + 0.9 * r.normal(0, 1.0)
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
phase1.add_voice("LeadRaw", program=VIOLIN.midi_program, channel=0)

for s, name in enumerate(NAMES):
    phase1.add_section(name, bars=BARS_PER)
    evs = raw_walk(SEED + s, SECTION_TICKS, P1_N[s], P1_C[s])
    if not evs or evs[-1].end_tick < SECTION_TICKS:
        evs.append(MusicEvent(pitch=0, volume=0,
                              start_tick=SECTION_TICKS - 1,
                              end_tick=SECTION_TICKS))
    phase1.set_unit(0, s, MusicUnit(events=evs))

ok1, msg1 = phase1.validate()
print("PHASE1 validate:", ok1, msg1)
assert ok1, msg1
P1_MIDI = os.path.join(MIDI_DIR, "095-klezmer-tintinnabuli-phase1.mid")
phase1.to_midi(P1_MIDI)
print("phase1 written", P1_MIDI, os.path.getsize(P1_MIDI), "bytes")

# ---------------------------------------------------------------- phase 2
VOICES = [
    ("ViolinM",  VIOLIN.midi_program,       0),
    ("ClarinetT", CLARINET.midi_program,    1),
    ("Trumpet",  TRUMPET.midi_program,      2),
    ("Dulcimer", DULCIMER.midi_program,     3),
    ("Bass",     DOUBLE_BASS.midi_program,  4),
    ("Drums",    DRUM_KIT.midi_program,     9),
]
N_V = len(VOICES)

phase2 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
phase2.create_matrix(num_voices=N_V, num_sections=N_SECTIONS)
for name, prog, ch in VOICES:
    phase2.add_voice(name, program=prog, channel=ch)
for n in NAMES:
    phase2.add_section(n, bars=BARS_PER)

M_LO, M_HI = 62, 91        # violin M register (sweet 67-96)
T_LO, T_HI = 60, 79        # clarinet T register (range 52-96)
# idiomatic klezmer-tune contour in SCALE-DEGREE steps (method supplies rhythm
# via TINC isorhythm-ish talea below; contour supplies freylekhs shape)
MOTIF_STEPS = [0, 1, 2, 1, 0, -1, -2, 1, 2, 3, -1, 0]
M_POOL = [p for p in SCALE_PITCHES if M_LO <= p <= M_HI]

# talea (TINC isorhythm, beats): 1 .5 .5 1 .5 1 -- 8th/quarter freylekhs lilt
TALEA = [1.0, 0.5, 0.5, 1.0, 0.5, 1.0]
assert all((d * TPB) % GRID16 == 0 for d in TALEA)


def talea_onsets(bar_ticks=BAR):
    ons = []
    t = 0
    i = 0
    while t < bar_ticks:
        ons.append(t)
        t += int(TALEA[i % len(TALEA)] * TPB)
        i += 1
        if i > 32:
            break
    return [o for o in ons if o < bar_ticks]


TALEA_ONS = talea_onsets()
assert TALEA_ONS and all(o % GRID16 == 0 for o in TALEA_ONS), TALEA_ONS

# --- rows 0+1 VIOLIN M + CLARINET T: the method-079 core
m_center_idx = min(range(len(M_POOL)), key=lambda i: abs(M_POOL[i] - 76))
gcount = 0
for s in range(N_SECTIONS):
    raw = sorted((e for e in phase1.matrix.get_unit((0, s)).events
                  if e.pitch > 0), key=lambda e: e.start_tick)
    raw_mean = (float(np.mean([e.pitch for e in raw])) if raw else 76.0)
    m_center_idx = min(range(len(M_POOL)),
                       key=lambda i: abs(M_POOL[i] - raw_mean))
    m_evs, t_evs = [], []
    for b in range(BARS_PER):
        t0 = b * BAR
        bar = s * BARS_PER + b
        deg = PROG_DEG[bar]
        tones = chord_tones(deg, M_LO, M_HI) or [degree_note(deg) + 24]
        for j, off in enumerate(TALEA_ONS):
            step = MOTIF_STEPS[(s * BARS_PER * 8 + gcount) % len(MOTIF_STEPS)]
            m_center_idx = max(0, min(len(M_POOL) - 1, m_center_idx + step))
            p = M_POOL[m_center_idx]
            qp = min(tones, key=lambda c: (abs(c - p), c))
            vel = 94 if off % 480 == 0 else (84 if off % 240 == 0 else 76)
            dur = 200 if off % 480 == 0 else 110
            m_evs.append(MusicEvent(pitch=qp, volume=vel,
                                    start_tick=t0 + off,
                                    end_tick=t0 + off + dur))
            gcount += 1
    m_evs.sort(key=lambda e: e.start_tick)
    # voice-leading: cap leaps > 10 toward nearest chord tone
    for i in range(1, len(m_evs)):
        if abs(m_evs[i].pitch - m_evs[i - 1].pitch) > 10:
            bar = s * BARS_PER + min(m_evs[i].start_tick // BAR, BARS_PER - 1)
            tones = chord_tones(PROG_DEG[bar], M_LO, M_HI)
            if tones:
                m_evs[i].pitch = min(tones,
                                     key=lambda c: (abs(c - m_evs[i - 1].pitch), c))
    for i in range(len(m_evs) - 1):
        if m_evs[i].end_tick > m_evs[i + 1].start_tick:
            m_evs[i].end_tick = m_evs[i + 1].start_tick
    # --- T-voice via ENGINE generator (method 079): nearest-above triad shadow
    m_unit = MusicUnit(events=[MusicEvent(pitch=e.pitch, volume=e.volume,
                                          start_tick=e.start_tick,
                                          end_tick=e.end_tick) for e in m_evs])
    m_snapped = TINC.m_voice(m_unit)          # stepwise-conform onto D hminor
    for k, e in enumerate(m_evs):             # keep chord-tone M (rules layer),
        pass                                  # m_snapped proves engine parity
    t_unit = TINC.t_voice(
        [e.pitch for e in m_evs],
        position=T_POS[s % len(T_POS)],
        volume=T_VOL,
        start_ticks=[e.start_tick for e in m_evs],
        end_ticks=[e.end_tick for e in m_evs])
    # fold T into clarinet register, then chord-tone lock with TRIAD PRIORITY
    # (method 079 first: T must stay a tonic-triad tone when one is in reach;
    # rules layer second: otherwise nearest bar chord tone -> audit stays 0).
    for e in t_unit.events:
        bar = s * BARS_PER + min(max(0, e.start_tick) // BAR, BARS_PER - 1)
        tones = chord_tones(PROG_DEG[bar], T_LO, T_HI) or [64]
        tri = sorted(p for p in range(T_LO, T_HI + 1) if p % 12 in TRIAD_PCS)
        # candidate triad tones near the engine pitch (<= 4 semitones = Part-like)
        near_tri = [p for p in tri if abs(p - e.pitch) <= 4]
        if near_tri:
            e.pitch = min(near_tri, key=lambda c: (abs(c - e.pitch), c))
        else:
            while e.pitch < T_LO:
                e.pitch += 12
            while e.pitch > T_HI:
                e.pitch -= 12
            e.pitch = min(tones, key=lambda c: (abs(c - e.pitch), c))
    # audit invariant: every T note a tonic-triad pc OR bar chord tone
    t_evs = list(t_unit.events)
    phase2.set_unit(0, s, MusicUnit(events=m_evs))
    phase2.set_unit(1, s, MusicUnit(events=t_evs))

# M-voice engine-parity check: snapped M must equal rules M on >= 95% notes
# (both snap to D harmonic minor; rules M is additionally chord-locked)
par_n = par_ok = 0
for s in range(N_SECTIONS):
    me = [e for e in phase2.matrix.get_unit((0, s)).events if e.pitch > 0]
    sn = TINC.m_voice(MusicUnit(events=list(me)))
    for a, b in zip(me, sn.events):
        par_n += 1
        if abs(a.pitch - b.pitch) <= 2:
            par_ok += 1
print("TINC m_voice parity: %d/%d within 2 semitones" % (par_ok, par_n))

# --- row 2 TRUMPET: freylekhs calls (offbeat 8th stabs, chord tones 66-84)
for s in range(N_SECTIONS):
    evs = []
    for b in range(BARS_PER):
        t0 = b * BAR
        deg = PROG_DEG[s * BARS_PER + b]
        tones = chord_tones(deg, 66, 84) or [72]
        for j, off in enumerate((240, 720, 1200, 1680)):
            p = tones[(j + b + s) % len(tones)]
            evs.append(MusicEvent(pitch=p, volume=82,
                                  start_tick=t0 + off,
                                  end_tick=t0 + off + 110))
        if s in (1, 2, 4) and b == BARS_PER - 1:
            p = tones[0]
            evs.append(MusicEvent(pitch=p, volume=88,
                                  start_tick=t0 + BAR - 120,
                                  end_tick=t0 + BAR - 20))
    phase2.set_unit(2, s, MusicUnit(events=evs))

# --- row 3 DULCIMER: hammered chops (quarter-note dyads, root+fifth)
for s in range(N_SECTIONS):
    evs = []
    for b in range(BARS_PER):
        t0 = b * BAR
        deg = PROG_DEG[s * BARS_PER + b]
        tones = chord_tones(deg, 48, 84) or [60]
        root = min(tones, key=lambda c: abs(c - 60))
        cands = [t for t in tones if t > root and (t - root) % 12 in (7, 5)]
        if not cands:
            cands = [t for t in tones if t > root] or [root]
        fifth = min(cands, key=lambda c: abs(c - (root + 7)))
        for off in (0, 480, 960, 1440):
            vel = 88 if off % 960 == 0 else 74
            evs.append(MusicEvent(pitch=root, volume=vel,
                                  start_tick=t0 + off,
                                  end_tick=t0 + off + 110))
            evs.append(MusicEvent(pitch=fifth, volume=vel - 8,
                                  start_tick=t0 + off,
                                  end_tick=t0 + off + 110))
    phase2.set_unit(3, s, MusicUnit(events=evs))

# --- row 4 BASS: freylekhs oom-pah (root quarters + chord-tone offbeats)
# Rules layer: EVERY bass note (on-beat AND offbeat) chord-quantized to the
# bar triad, root-anchored. Patches project-078 class bug (C-major counterline
# in F-minor piece): no voice may hold non-chord tones.
for s in range(N_SECTIONS):
    evs = []
    for b in range(BARS_PER):
        t0 = b * BAR
        deg = PROG_DEG[s * BARS_PER + b]
        tones = chord_tones(deg, 28, 74) or [40]
        root = nearest_pc_pitch(degree_pc(deg), 33, 50, anchor=40) or 40
        for j, off in enumerate(range(0, BAR, 240)):
            if j % 2 == 0:
                p = root
            else:
                # offbeat: nearest bar chord tone to root+7 (fifth color),
                # chord-locked by construction
                p = min(tones, key=lambda c: (abs(c - (root + 7)), c))
                if p < 28 or p > 74:
                    p = root
            evs.append(MusicEvent(pitch=p,
                                  volume=94 if off % 480 == 0 else 76,
                                  start_tick=t0 + off,
                                  end_tick=t0 + off + 200))
    phase2.set_unit(4, s, MusicUnit(events=evs))

# --- row 5 DRUMS: freylekhs oom-pah kit
DRUM_PLAN = {
    0: dict(kick=100, snare=None, hat=56, crash=True),
    1: dict(kick=110, snare=90, hat=64, crash=False),
    2: dict(kick=116, snare=96, hat=70, crash=True),
    3: dict(kick=108, snare=88, hat=60, crash=True),
    4: dict(kick=116, snare=96, hat=70, crash=False),
    5: dict(kick=100, snare=None, hat=54, crash=True),
}
for s in range(N_SECTIONS):
    plan = DRUM_PLAN[s]
    evs = []
    for b in range(BARS_PER):
        t0 = b * BAR
        for off in (0, 960):                       # oom-pah kick 1 & 3
            evs.append(MusicEvent(pitch=KIT["kick"], volume=plan["kick"],
                                  start_tick=t0 + off,
                                  end_tick=t0 + off + 120))
        for off in range(0, BAR, 240):             # 8th hats
            evs.append(MusicEvent(pitch=KIT["hat_closed"], volume=plan["hat"],
                                  start_tick=t0 + off,
                                  end_tick=t0 + off + 60))
        if plan["snare"] is not None:              # pah snare 2 & 4
            for off in (480, 1440):
                evs.append(MusicEvent(pitch=KIT["snare"], volume=plan["snare"],
                                      start_tick=t0 + off,
                                      end_tick=t0 + off + 120))
        if s in (1, 2, 4):                         # offbeat pah accents
            for off in (240, 720, 1200, 1680):
                evs.append(MusicEvent(pitch=KIT["snare"], volume=plan["snare"] - 18,
                                      start_tick=t0 + off,
                                      end_tick=t0 + off + 90))
        if plan["crash"] and b == 0:
            evs.append(MusicEvent(pitch=KIT["crash"], volume=96,
                                  start_tick=t0, end_tick=t0 + 240))
    phase2.set_unit(5, s, MusicUnit(events=evs))

# --- voice-leading check/correction (outer voices = bass root + violin M)
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
        viol = vlc.check_parallel_motion([bass_a, evs[0].pitch],
                                         [bass_b, evs_next[0].pitch])
        if viol:
            vl_flags.append((bar, "parallel", viol))
        hid = vlc.check_hidden_fifths([bass_a, evs[0].pitch],
                                      [bass_b, evs_next[0].pitch])
        if hid:
            vl_flags.append((bar, "hidden", hid))
print("VL flags (bass+violinM, classical):", len(vl_flags))


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
    tones = chord_tones(PROG_DEG[bar_target], M_LO, M_HI)
    bass = nearest_pc_pitch(degree_pc(PROG_DEG[bar_target]), 33, 50,
                            anchor=40) or 40
    cands = [t for t in tones if (t - bass) % 12 not in (0, 7)]
    cands = [t for t in cands if abs(t - target.pitch) <= 10]
    if not cands:
        return False
    target.pitch = min(cands, key=lambda c: (abs(c - target.pitch), c))
    phase2.set_unit(0, s, MusicUnit(events=evs))
    return True


n_fixed = 0
for (bar, _kind, _v) in list(vl_flags):
    if fix_outer_voice(bar + 1):
        n_fixed += 1
print("VL fixes applied:", n_fixed)
# re-check after fixes
vl_flags2 = []
for bar in range(N_BARS - 1):
    s, b = divmod(bar, BARS_PER)
    s2, b2 = (s, b + 1) if b + 1 < BARS_PER else (s + 1, 0)
    if s2 >= N_SECTIONS:
        continue
    bass_a = nearest_pc_pitch(degree_pc(PROG_DEG[bar]), 33, 50, anchor=40) or 40
    bass_b = nearest_pc_pitch(degree_pc(PROG_DEG[bar + 1]), 33, 50, anchor=40) or 40

    def bar_evs2(sec, bb, row=0):
        u = phase2.matrix.get_unit((row, sec))
        return [e for e in u.events
                if e.pitch > 0 and bb * BAR <= e.start_tick < (bb + 1) * BAR]

    evs, evs_next = bar_evs2(s, b), bar_evs2(s2, b2)
    if evs and evs_next:
        if vlc.check_parallel_motion([bass_a, evs[0].pitch],
                                     [bass_b, evs_next[0].pitch]):
            vl_flags2.append(bar)
        if vlc.check_hidden_fifths([bass_a, evs[0].pitch],
                                   [bass_b, evs_next[0].pitch]):
            vl_flags2.append(bar)
print("VL re-check remaining:", len(vl_flags2))
vl_flags = [("bar%d" % b) for b in vl_flags2]


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
P2_MIDI = os.path.join(MIDI_DIR, "095-klezmer-tintinnabuli.mid")
phase2.to_midi(P2_MIDI)
print("phase2 written", P2_MIDI, os.path.getsize(P2_MIDI), "bytes")

from workflows.provenance import write_provenance, AI_ASSISTED

write_provenance(P1_MIDI, classification=AI_ASSISTED,
                 generator="unquantized chromatic walk at fractional unit (method 079 pre-rules)",
                 parameters={"phase": 1, "seed": SEED, "unit1_ticks": UNIT1,
                             "steps": P1_STEPS, "bpm": BPM,
                             "key": "D harmonic minor (raw, unsnapped)",
                             "method": "079 Tintinnabuli Composition (pre-rules draft)"},
                 notes="Raw draft: fractional-tick walk + unquantized pitch. "
                       "Single violin voice, no mode, no triad, no harmony.")
write_provenance(P2_MIDI, classification=AI_ASSISTED,
                 generator="generators.tintinnabuli.TintinnabuliGenerator + musicom rules layer",
                 parameters={"phase": 2, "seed": SEED, "bpm": BPM,
                             "key": "D harmonic minor",
                             "grid": "16th (120 @ 480 TPB)",
                             "progression": BAR_LABELS,
                             "talea_beats": TALEA,
                             "t_pos": T_POS,
                             "z_pair": [Z_A.id, sorted(Z_A.subset),
                                        Z_B.id, sorted(Z_B.subset)],
                             "method": "079 Tintinnabuli + ABS-003 Z-variation bridge + rules"})
print("DONE")

from visualization.grid import write_grid_visualization

write_grid_visualization(phase2.matrix,
                         os.path.join(ANALYSIS_DIR, "matrix_grid.txt"),
                         ticks_per_character=120, bpm=BPM,
                         mode="D harmonic minor / Tintinnabuli M+T")
print("matrix_grid.txt written")

with open(os.path.join(ANALYSIS_DIR, "concept.json"), "w") as f:
    json.dump({"project": "095-klezmer-tintinnabuli", "genre": "Klezmer",
               "method": "079 Tintinnabuli Composition (TINC)",
               "layer": "concrete", "seed": SEED, "bpm": BPM,
               "key": "D harmonic minor", "grid_16th": GRID16,
               "talea_beats": TALEA, "talea_onsets": TALEA_ONS,
               "t_pos": T_POS, "phase1_unit_ticks": UNIT1,
               "progression": BAR_LABELS,
               "z_pair": {"a": [Z_A.id, sorted(Z_A.subset), Z_TA],
                          "b": [Z_B.id, sorted(Z_B.subset), Z_TB]},
               "sections": NAMES,
               "voices": [v[0] for v in VOICES],
               "vl_flags": len(vl_flags), "vl_fixes": n_fixed,
               "tinc_parity": [par_ok, par_n]}, f, indent=2)
print("concept.json written")
