# -*- coding: utf-8 -*-
"""096-trap-skeleton-seoul - Trap x Method 001 (Skeleton-First Refinement).

Trap (half-time, dark): 140 BPM felt half-time (~70), C phrygian darkness,
808-style sub bass, rolling hats, snare on 3, minor-key bell/pad motif.
Method 001 = form-first: deterministic structural skeleton (section bar-plan
+ section-level harmonic skeleton + per-section density map) fixed FIRST;
micro-variation (ornament, hat rolls, lead octave pops) added only inside
the skeleton afterwards.

Phase 1: raw generative draft (single marimba voice). Pre-rules material:
  Rhythm = straight 8th-slot walk at FRACTIONAL UNIT1 (311 ticks, NOT a
  120/240 multiple) + dropout rests -> off-grid by construction.
  Pitch  = unquantized chromatic walk from C5 with drift (no phrygian snap,
  no chord context, no harmony).
Phase 2: musicom rules post-process:
  1. 16th-grid lock (project 078 mandatory rule): every onset snapped to
     120-grid -> 0 off-grid.
  2. C-phrygian scale snap -> bar chord-tone quantize through canonical
     Scale7ChordDegree.get_diatonic_note (no % 7 wrappers).
  3. Voice-leading check/correction (rules.voice_leading, classical) on
     outer voices (808 bass root + bell lead).
  4. Full 6-voice trap texture: marimba bell lead / violin counter /
     piano chord stabs / double-bass 808 sub / trumpet brass stabs /
     drum kit (half-time trap kit: kick pattern, snare on 3, 16th hats
     with section-density rolls).

Engine only: structures + workflows.unitmatrix_composer +
generators.base.FunctionGenerator (method 001 skeleton) + rules.progression
+ rules.voice_leading. mido imported READ-ONLY in audit/summary scripts
(never for authoring).
"""
import json
import os
import sys

import numpy as np

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer
from generators.base import FunctionGenerator
from rules.progression import Scale7ChordDegree
from rules.voice_leading import VoiceLeadingRules

INSTR_DIR = "/opt/data/repos/musicom/projects/Instruments"
if INSTR_DIR not in sys.path:
    sys.path.insert(0, INSTR_DIR)
from instrument_registry import (
    MARIMBA, VIOLIN, PIANO, DOUBLE_BASS, TRUMPET, DRUM_KIT,
)
from Percussion.drum_kit.drum_kit import KIT

SEED = 20260915
rng = np.random.default_rng(SEED)

PROJ = ("/opt/data/repos/musicom/projects/Styles/Trap/"
        "096-trap-skeleton-seoul")
MIDI_DIR = os.path.join(PROJ, "MIDI")
AUDIO_DIR = os.path.join(PROJ, "Audio")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")
SCRIPTS_DIR = os.path.join(PROJ, "Scripts")
for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR, SCRIPTS_DIR):
    os.makedirs(d, exist_ok=True)

BPM = 140
TPB = 480
BEATS = 4
BAR = TPB * BEATS            # 1920
GRID16 = 120
GRID8 = 240
SECTION_TICKS = BAR * 4      # 7680 (4 bars per section)
NAMES = ["Intro", "VerseA", "HookB", "Bridge", "HookB2", "Outro"]
BARS_PER = 4
N_SECTIONS = len(NAMES)
N_BARS = N_SECTIONS * BARS_PER          # 24

# C phrygian: C Db Eb F G Ab Bb ; bell C5 (MIDI 72)
KEY_ROOT = 60
PHRYGIAN = [0, 1, 3, 5, 7, 8, 10]
SCALE_PCS = {(KEY_ROOT + i) % 12 for i in PHRYGIAN}
SCALE_PITCHES = [p for p in range(36, 100) if p % 12 in SCALE_PCS]


def degree_note(d):
    """Canonical diatonic note (no local % 7 wrapper)."""
    return Scale7ChordDegree.get_diatonic_note(KEY_ROOT, PHRYGIAN, d)


def degree_pc(d):
    return degree_note(d) % 12


def degree_triad_pcs(d):
    return {degree_note(d + k) % 12 for k in (0, 2, 4)}


# ---------------------------------------------------------------- method 001
# SKELETON (fixed first, deterministic): section bar-plan + per-section
# harmonic skeleton (0-based phrygian degrees) + density map. The skeleton
# generator below builds this exact plan; micro-variation happens later.
#
# 24-bar trap skeleton, diatonic to C phrygian:
#   Intro   i  i  bII i    | A  i  bII bvii bII | B  bvii bII i  i
#   Bridge  bVII iv  bII bII| B2 bvii bII i  i  | Outro i  bII i  i
PROG_DEG = ([0, 1, 1, 0] + [0, 1, 6, 1] + [6, 1, 0, 0] +
            [6, 3, 1, 1] + [6, 1, 0, 0] + [0, 1, 0, 0])
assert len(PROG_DEG) == N_BARS, (len(PROG_DEG), N_BARS)
DEG_NAME = {0: "i", 1: "bII", 2: "bIII", 3: "iv",
            4: "v", 5: "bV", 6: "bvii"}
PC_NAME = {0: "C", 1: "Db", 3: "Eb", 5: "F", 7: "G", 8: "Ab", 10: "Bb"}
BAR_LABELS = [PC_NAME[degree_pc(d)] + DEG_NAME[d] for d in PROG_DEG]

# Per-section density skeleton (method 001 structure-first): hat activity,
# lead activity, drum intensity fixed per section before any notes exist.
SKEL = {
    "Intro":   dict(hat="sparse8", lead="half",  drums="lite",  bass="long"),
    "VerseA":  dict(hat="16",      lead="full",  drums="half",  bass="half"),
    "HookB":   dict(hat="16roll",  lead="full",  drums="full",  bass="full"),
    "Bridge":  dict(hat="sparse8", lead="half",  drums="lite",  bass="long"),
    "HookB2":  dict(hat="16roll",  lead="full",  drums="full",  bass="full"),
    "Outro":   dict(hat="sparse8", lead="half",  drums="lite",  bass="long"),
}
assert list(SKEL) == NAMES


def skeleton_plan():
    """Method-001 skeleton builder (called through FunctionGenerator)."""
    return [{"section": n, "bars": BARS_PER,
             "degrees": PROG_DEG[i * BARS_PER:(i + 1) * BARS_PER],
             "density": SKEL[n]} for i, n in enumerate(NAMES)]


SKEL_GEN = FunctionGenerator(function=skeleton_plan, params={})
SKELETON = SKEL_GEN.generate()
assert [r["section"] for r in SKELETON] == NAMES
assert [r["degrees"] for r in SKELETON] == [
    PROG_DEG[i * BARS_PER:(i + 1) * BARS_PER] for i in range(N_SECTIONS)]


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


# ---------------------------------------------------------------- phase 1
# Raw draft: single marimba voice. 8th slots at fractional UNIT1 (311 ticks:
# NOT a 120/240 multiple) + dropout rests + unquantized chromatic walk.
UNIT1 = 311
P1_STEPS = [-5, -3, -2, -1, -1, 1, 2, 2, 3, 4, -4]
P1_N = {0: 20, 1: 28, 2: 32, 3: 22, 4: 32, 5: 18}
P1_C = {0: 70.0, 1: 73.0, 2: 74.0, 3: 71.0, 4: 74.0, 5: 69.0}
P1_REST_P = 0.18


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
        if r.random() < P1_REST_P:
            tick += step
            i += 1
            continue
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
phase1.add_voice("LeadRaw", program=MARIMBA.midi_program, channel=0)

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
P1_MIDI = os.path.join(MIDI_DIR, "096-trap-skeleton-seoul-phase1.mid")
phase1.to_midi(P1_MIDI)
print("phase1 written", P1_MIDI, os.path.getsize(P1_MIDI), "bytes")

# ---------------------------------------------------------------- phase 2
VOICES = [
    ("BellLead",  MARIMBA.midi_program,      0),
    ("ViolinCtr", VIOLIN.midi_program,       1),
    ("PianoStab", PIANO.midi_program,        2),
    ("Sub808",    DOUBLE_BASS.midi_program,  4),
    ("BrassStab", TRUMPET.midi_program,      5),
    ("Drums",     DRUM_KIT.midi_program,     9),
]
N_V = len(VOICES)

phase2 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
phase2.create_matrix(num_voices=N_V, num_sections=N_SECTIONS)
for name, prog, ch in VOICES:
    phase2.add_voice(name, program=prog, channel=ch)
for n in NAMES:
    phase2.add_section(n, bars=BARS_PER)

B_LO, B_HI = 62, 91        # marimba bell lead register (sweet 60-84 core)
C_LO, C_HI = 62, 86        # violin counter register (range 55-103)
# Phrygian bell contour in SCALE-DEGREE steps (method-001 motif inside the
# skeleton; skeleton supplies rhythm slots, contour supplies trap shape).
MOTIF_STEPS = [0, 1, 1, -1, 0, -2, 1, 0, 2, -1, -1, 0]
B_POOL = [p for p in SCALE_PITCHES if B_LO <= p <= B_HI]
C_POOL = [p for p in SCALE_PITCHES if C_LO <= p <= C_HI]


def bar_slots(kind):
    """Onset slots per bar from the section density skeleton (all % 120)."""
    if kind == "sparse8":
        return [0, 480, 960, 1440]
    if kind == "16":
        return list(range(0, BAR, 240))
    if kind == "16roll":
        # Hook pickup: one extra 16th before the downbeat (BAR-120 % 120 == 0).
        # 32nd rolls (60/30-tick) are NOT 16th-grid -> forbidden in phase 2.
        return list(range(0, BAR, 240)) + [BAR - 120]
    if kind == "half":
        return [0, 960]
    return list(range(0, BAR, 240))


# --- rows 0+1 BELL LEAD + VIOLIN COUNTER: the rules-layer melodic core
b_center = min(range(len(B_POOL)), key=lambda i: abs(B_POOL[i] - 74))
c_center = min(range(len(C_POOL)), key=lambda i: abs(C_POOL[i] - 69))
gcount = 0
for s in range(N_SECTIONS):
    raw = sorted((e for e in phase1.matrix.get_unit((0, s)).events
                  if e.pitch > 0), key=lambda e: e.start_tick)
    raw_mean = (float(np.mean([e.pitch for e in raw])) if raw else 74.0)
    b_center = min(range(len(B_POOL)),
                   key=lambda i: abs(B_POOL[i] - raw_mean))
    kind = SKELETON[s]["density"]["lead"]
    b_evs, c_evs = [], []
    for b in range(BARS_PER):
        t0 = b * BAR
        bar = s * BARS_PER + b
        deg = PROG_DEG[bar]
        tones = chord_tones(deg, B_LO, B_HI) or [degree_note(deg) + 24]
        ctones = chord_tones(deg, C_LO, C_HI) or [degree_note(deg) + 12]
        for off in bar_slots(kind if kind in ("half", "full") else "full"):
            step = MOTIF_STEPS[(s * BARS_PER * 8 + gcount) % len(MOTIF_STEPS)]
            b_center = max(0, min(len(B_POOL) - 1, b_center + step))
            p = B_POOL[b_center]
            qp = min(tones, key=lambda c: (abs(c - p), c))
            vel = 96 if off % 480 == 0 else (86 if off % 240 == 0 else 78)
            dur = 200 if off % 480 == 0 else 110
            b_evs.append(MusicEvent(pitch=qp, volume=vel,
                                    start_tick=t0 + off,
                                    end_tick=t0 + off + dur))
            # counter: contrary-ish shadow a third-ish below, chord-locked
            cp = min(ctones, key=lambda c: (abs(c - (qp - 4)), c))
            c_evs.append(MusicEvent(pitch=cp, volume=vel - 14,
                                    start_tick=t0 + off,
                                    end_tick=t0 + off + max(90, dur - 20)))
            gcount += 1
    b_evs.sort(key=lambda e: e.start_tick)
    c_evs.sort(key=lambda e: e.start_tick)
    # voice-leading: cap leaps > 10 toward nearest chord tone
    for seq, lo, hi in ((b_evs, B_LO, B_HI), (c_evs, C_LO, C_HI)):
        for i in range(1, len(seq)):
            if abs(seq[i].pitch - seq[i - 1].pitch) > 10:
                bar = s * BARS_PER + min(seq[i].start_tick // BAR,
                                         BARS_PER - 1)
                tones = chord_tones(PROG_DEG[bar], lo, hi)
                if tones:
                    seq[i].pitch = min(
                        tones, key=lambda c: (abs(c - seq[i - 1].pitch), c))
    for seq in (b_evs, c_evs):
        for i in range(len(seq) - 1):
            if seq[i].end_tick > seq[i + 1].start_tick:
                seq[i].end_tick = seq[i + 1].start_tick
    phase2.set_unit(0, s, MusicUnit(events=b_evs))
    phase2.set_unit(1, s, MusicUnit(events=c_evs))

# --- row 2 PIANO: dark chord stabs (root+third+fifth, on-beat quarters)
for s in range(N_SECTIONS):
    evs = []
    for b in range(BARS_PER):
        t0 = b * BAR
        deg = PROG_DEG[s * BARS_PER + b]
        tones = chord_tones(deg, 48, 72) or [60]
        root = min(tones, key=lambda c: abs(c - 55))
        tri = sorted({root} | {t for t in tones if t != root})[:3]
        while len(tri) < 3:
            tri.append(tri[-1] + 12 if tri[-1] + 12 <= 84 else tri[-1] - 12)
        for off in (0, 480, 960, 1440):
            vel = 84 if off % 960 == 0 else 70
            for p in tri:
                evs.append(MusicEvent(pitch=p, volume=vel,
                                      start_tick=t0 + off,
                                      end_tick=t0 + off + 200))
    phase2.set_unit(2, s, MusicUnit(events=evs))

# --- row 3 SUB808: half-time 808 (root longs + chord-locked fills)
for s in range(N_SECTIONS):
    kind = SKELETON[s]["density"]["bass"]
    evs = []
    for b in range(BARS_PER):
        t0 = b * BAR
        deg = PROG_DEG[s * BARS_PER + b]
        tones = chord_tones(deg, 28, 62) or [36]
        root = nearest_pc_pitch(degree_pc(deg), 28, 45, anchor=36) or 36
        if kind == "long":
            evs.append(MusicEvent(pitch=root, volume=96,
                                  start_tick=t0, end_tick=t0 + BAR - 120))
        else:
            evs.append(MusicEvent(pitch=root, volume=98,
                                  start_tick=t0, end_tick=t0 + 440))
            evs.append(MusicEvent(pitch=root, volume=88,
                                  start_tick=t0 + 1440,
                                  end_tick=t0 + 1440 + 400))
            p = min(tones, key=lambda c: (abs(c - (root + 7)), c))
            if p < 28 or p > 62:
                p = root
            evs.append(MusicEvent(pitch=p, volume=80,
                                  start_tick=t0 + 960,
                                  end_tick=t0 + 960 + 200))
    phase2.set_unit(3, s, MusicUnit(events=evs))

# --- row 4 BRASS: trap horn stabs (offbeat 8ths, chord tones 60-80)
for s in range(N_SECTIONS):
    evs = []
    for b in range(BARS_PER):
        t0 = b * BAR
        deg = PROG_DEG[s * BARS_PER + b]
        tones = chord_tones(deg, 60, 80) or [67]
        for j, off in enumerate((240, 720, 1200, 1680)):
            p = tones[(j + b + s) % len(tones)]
            evs.append(MusicEvent(pitch=p, volume=80,
                                  start_tick=t0 + off,
                                  end_tick=t0 + off + 110))
        if s in (1, 2, 4) and b == BARS_PER - 1:
            evs.append(MusicEvent(pitch=tones[0], volume=88,
                                  start_tick=t0 + BAR - 120,
                                  end_tick=t0 + BAR - 20))
    phase2.set_unit(4, s, MusicUnit(events=evs))

# --- row 5 DRUMS: half-time trap kit (kick syncopation, snare on 3 = 960)
DRUM_PLAN = {
    0: dict(kick=100, snare=None, hat=56, crash=True),
    1: dict(kick=108, snare=90, hat=62, crash=False),
    2: dict(kick=114, snare=96, hat=68, crash=True),
    3: dict(kick=106, snare=88, hat=58, crash=True),
    4: dict(kick=114, snare=96, hat=68, crash=False),
    5: dict(kick=100, snare=None, hat=54, crash=True),
}
for s in range(N_SECTIONS):
    plan = DRUM_PLAN[s]
    hkind = SKELETON[s]["density"]["hat"]
    dkind = SKELETON[s]["density"]["drums"]
    evs = []
    for b in range(BARS_PER):
        t0 = b * BAR
        # kick: half-time syncopation (beat 1 + 8th pickup at 720, on-grid)
        for off in (0, 720) if dkind != "lite" else (0,):
            evs.append(MusicEvent(pitch=KIT["kick"], volume=plan["kick"],
                                  start_tick=t0 + off,
                                  end_tick=t0 + off + 120))
        # snare: beat 3 (half-time backbeat) + lite sections keep it
        if plan["snare"] is not None or dkind == "lite":
            evs.append(MusicEvent(pitch=KIT["snare"],
                                  volume=plan["snare"] or 84,
                                  start_tick=t0 + 960,
                                  end_tick=t0 + 960 + 120))
        # hats per skeleton density (Hook pickup = extra on-grid 16th)
        if hkind == "sparse8":
            hat_offs = [0, 480, 960, 1440]
        elif hkind == "16":
            hat_offs = list(range(0, BAR, 240))
        else:
            hat_offs = list(range(0, BAR, 240)) + [BAR - 120]
        for off in hat_offs:
            evs.append(MusicEvent(pitch=KIT["hat_closed"], volume=plan["hat"],
                                  start_tick=t0 + off,
                                  end_tick=t0 + off + 60))
        if plan["crash"] and b == 0:
            evs.append(MusicEvent(pitch=KIT["crash"], volume=94,
                                  start_tick=t0, end_tick=t0 + 240))
    phase2.set_unit(5, s, MusicUnit(events=evs))

# --- voice-leading check/correction (outer voices = 808 root + bell lead)
vlc = VoiceLeadingRules(style="classical")
vl_flags = []
for bar in range(N_BARS - 1):
    s, b = divmod(bar, BARS_PER)
    deg_a, deg_b = PROG_DEG[bar], PROG_DEG[bar + 1]
    bass_a = nearest_pc_pitch(degree_pc(deg_a), 28, 45, anchor=36) or 36
    bass_b = nearest_pc_pitch(degree_pc(deg_b), 28, 45, anchor=36) or 36
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
print("VL flags (bass+bell, classical):", len(vl_flags))


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
    tones = chord_tones(PROG_DEG[bar_target], B_LO, B_HI)
    bass = nearest_pc_pitch(degree_pc(PROG_DEG[bar_target]), 28, 45,
                            anchor=36) or 36
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
    bass_a = nearest_pc_pitch(degree_pc(PROG_DEG[bar]), 28, 45, anchor=36) or 36
    bass_b = nearest_pc_pitch(degree_pc(PROG_DEG[bar + 1]), 28, 45, anchor=36) or 36

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
        phase2.set_unit(v, s, normalize_cell(u, SECTION_TICKS))

ok2, msg2 = phase2.validate()
print("PHASE2 validate:", ok2, msg2)
assert ok2, msg2
P2_MIDI = os.path.join(MIDI_DIR, "096-trap-skeleton-seoul.mid")
phase2.to_midi(P2_MIDI)
print("phase2 written", P2_MIDI, os.path.getsize(P2_MIDI), "bytes")

from workflows.provenance import write_provenance, AI_ASSISTED

write_provenance(P1_MIDI, classification=AI_ASSISTED,
                 generator="unquantized chromatic walk at fractional unit (method 001 pre-rules)",
                 parameters={"phase": 1, "seed": SEED, "unit1_ticks": UNIT1,
                             "steps": P1_STEPS, "bpm": BPM,
                             "key": "C phrygian (raw, unsnapped)",
                             "method": "001 Skeleton-First Refinement (pre-rules draft)"},
                 notes="Raw draft: fractional-tick walk + unquantized pitch. "
                       "Single marimba voice, no mode, no harmony.")
write_provenance(P2_MIDI, classification=AI_ASSISTED,
                 generator="generators.base.FunctionGenerator skeleton + musicom rules layer",
                 parameters={"phase": 2, "seed": SEED, "bpm": BPM,
                             "key": "C phrygian",
                             "grid": "16th (120 @ 480 TPB)",
                             "progression": BAR_LABELS,
                             "skeleton": SKEL,
                             "motif_steps": MOTIF_STEPS,
                             "method": "001 Skeleton-First Refinement + rules"})
print("DONE")

from visualization.grid import write_grid_visualization

write_grid_visualization(phase2.matrix,
                         os.path.join(ANALYSIS_DIR, "matrix_grid.txt"),
                         ticks_per_character=120, bpm=BPM,
                         mode="C phrygian / Skeleton-First trap")
print("matrix_grid.txt written")

with open(os.path.join(ANALYSIS_DIR, "concept.json"), "w") as f:
    json.dump({"project": "096-trap-skeleton-seoul", "genre": "Trap",
               "method": "001 Skeleton-First Refinement",
               "method_impl": "generators.base.FunctionGenerator",
               "layer": "concrete", "seed": SEED, "bpm": BPM,
               "key": "C phrygian", "grid_16th": GRID16,
               "progression": BAR_LABELS,
               "skeleton": SKEL,
               "motif_steps": MOTIF_STEPS,
               "sections": NAMES,
               "voices": [v[0] for v in VOICES],
               "vl_flags": len(vl_flags), "vl_fixes": n_fixed}, f, indent=2)
print("concept.json written")
