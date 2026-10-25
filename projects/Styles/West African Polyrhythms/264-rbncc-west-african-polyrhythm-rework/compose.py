# -*- coding: utf-8 -*-
"""264-rbncc-west-african-polyrhythm-rework — nightly rework (2026-10-25).

Source: 210-rbncc-west-african-polyrhythm (G major, 112 BPM, Method 082 RBNCC,
5-voice West African timeline ensemble). REBUILD from scratch through the
canonical UnitMatrixComposer engine, preserving musical identity
(West African Polyrhythms / G major / 112 BPM / 3:4 cross-rhythm from the
12-step RBN attractor cycle / gankogui bell + kalimba lead + dunun bass +
balafon counter + drums) but:

  * LONGER form: 10 sections x 4 bars = 40 bars (source had 8 x 4 = 32).
  * MORE variation: 8 distinct techniques (transposition, inversion,
    retrograde, augmentation, diminution, register shift, density rise,
    counterline) mapped per section.
  * Per-section harmonic regions with MIDPOINT chord root (no bar-0 tonic bug).
  * Humanization + dual-version export (perfect / humanized) via export_dual.
  * index.html dashboard + root provenance (the source's audit failures).

Two-phase architecture:
  Phase 1 (raw): single-voice RBN draft. Off-grid micro-jitter onsets, raw
    chromatic pitch (48 + lead_deg*3). No harmony, no chord-tone snap.
  Phase 2 (rules): snap to 16th grid -> degree -> nearest chord tone of the
    bar its snapped onset lands in (floor t//BAR) -> per-section variation
    transform -> voice-leading cap -> register/range enforcement -> dedupe
    collisions -> full 5-voice texture -> zero-drift terminal landmark.

Engine-only: structures + workflows.unitmatrix_composer + workflows.humanize.
mido used READ-ONLY for audits only. Instruments from the importable registry.
"""
import json
import os
import sys
from pathlib import Path

import numpy as np

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer
from workflows.provenance import write_provenance
from workflows.humanize import export_dual
from visualization.grid import write_grid_visualization

INSTR_DIR = "/opt/data/repos/musicom/projects/Instruments"
if INSTR_DIR not in sys.path:
    sys.path.insert(0, INSTR_DIR)
from instrument_registry import (  # noqa: E402
    MARIMBA, KALIMBA, DOUBLE_BASS, XYLOPHONE, DRUM_KIT,
)

# ---- concept ----------------------------------------------------------------
GENRE = "West African Polyrhythms"
NAME = "264-rbncc-west-african-polyrhythm-rework"
ROOT = Path(f"/opt/data/repos/musicom/projects/Styles/{GENRE}/{NAME}")
for sub in ("MIDI", "Audio", "Analysis"):
    (ROOT / sub).mkdir(parents=True, exist_ok=True)

SEED = 20260928                  # preserve source RBN seed (identity)
INIT_SEED = SEED + 7             # 20260935
KEY_NAME = "G major"
G_SCALE = [7, 9, 11, 0, 2, 4, 6]   # G A B C D E F# (index 0..6)
SCALE_PCS = set(G_SCALE)
BPM = 112
TPB = 480
BAR = 1920
EIGHTH = 240
SIXTEENTH = 120
BEAT = 480
STEPS_PER_BAR = 16

# ---- form: 10 sections x 4 bars = 40 bars ----------------------------------
FORM = [("Intro", 4), ("Verse", 4), ("Chorus", 4), ("Verse2", 4),
        ("Chorus2", 4), ("Break", 4), ("Bridge", 4), ("Chorus3", 4),
        ("Finale", 4), ("Coda", 4)]
N_SECTIONS = len(FORM)
N_BARS = sum(b for _, b in FORM)
N_STEPS = N_BARS * STEPS_PER_BAR
TOTAL_TICKS = N_BARS * BAR

SECTION_BAR_OFF = {}
SECTION_TICKS = {}
_acc = 0
for s, nb in FORM:
    SECTION_BAR_OFF[s] = _acc
    SECTION_TICKS[s] = (nb * BAR, _acc * BAR)
    _acc += nb


def section_of_bar(b):
    for sname, nb in FORM:
        off = SECTION_BAR_OFF[sname]
        if off <= b < off + nb:
            return sname
    return FORM[-1][0]


# ---- harmony: per-section regions, diatonic G-major triads -----------------
DEG_NAMES = ["I", "ii", "iii", "IV", "V", "vi", "vii"]
DEG_LABELS = ["G", "Am", "Bm", "C", "D", "Em", "F#dim"]
DEG_QUALITIES = ["maj", "min", "min", "maj", "maj", "min", "dim"]

PROG = {
    "Intro":   [0, 0, 4, 0],
    "Verse":   [0, 3, 4, 0],
    "Chorus":  [0, 5, 3, 4],
    "Verse2":  [0, 3, 4, 0],
    "Chorus2": [5, 3, 0, 4],
    "Break":   [5, 3, 1, 0],
    "Bridge":  [5, 1, 2, 4],
    "Chorus3": [0, 5, 3, 4],
    "Finale":  [0, 3, 4, 0],
    "Coda":    [0, 0, 0, 0],
}

CHORD_SPECS = []                 # per-bar degree
for b in range(N_BARS):
    s = section_of_bar(b)
    CHORD_SPECS.append(PROG[s][b - SECTION_BAR_OFF[s]])


def chord_pcs(deg):
    idx = [deg % 7, (deg + 2) % 7, (deg + 4) % 7]
    return frozenset(G_SCALE[i] for i in idx)


def pc_to_pitch(pc, floor):
    for p in range(floor, floor + 12):
        if p % 12 == pc:
            return p
    return floor


def chord_tones(deg, floor, ceil):
    pcs = chord_pcs(deg)
    out = []
    for pc in sorted(pcs):
        p = pc_to_pitch(pc, floor)
        while p <= ceil:
            out.append(p)
            p += 12
    return sorted(out)


# register pools per bar (chord tones realized per voice register)
LEAD_POOL = {b: chord_tones(CHORD_SPECS[b], 60, 90) for b in range(N_BARS)}
BAL_POOL = {b: chord_tones(CHORD_SPECS[b], 67, 96) for b in range(N_BARS)}
BASS_POOL = {b: chord_tones(CHORD_SPECS[b], 36, 50) for b in range(N_BARS)}

section_roots = {}
for sname, nb in FORM:
    mid = SECTION_BAR_OFF[sname] + nb // 2
    section_roots[sname] = CHORD_SPECS[mid]


def snap16(t):
    return int(round(t / SIXTEENTH) * SIXTEENTH)


# ============================================================================
# RBN primitives (Method 082, identical seed -> same attractor cycle)
# ============================================================================
def build_rbn(n=16, k=2, p=0.5, seed=SEED):
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
    inputs, funcs = build_rbn(n, k, p, seed)
    state = (np.random.default_rng(init_seed).random(n) < 0.5).astype(np.uint8)
    init_state = state.copy()

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
    v = 0
    for b in range(lo, hi + 1):
        v |= int(state[b]) << (b - lo)
    return v


def decode(state):
    return {
        "lead_deg": bits_to_int(state, 0, 3),
        "lead_art": bits_to_int(state, 4, 5),
        "lead_vel": bits_to_int(state, 6, 8),
        "bal_deg": bits_to_int(state, 9, 11),
        "bal_gate": bits_to_int(state, 12, 13),
        "shake": bits_to_int(state, 14, 15),
    }


traj, transient_len, cycle_len, frozen = run_rbn()
DECODED = [decode(traj[s]) for s in range(N_STEPS)]


def unit_from(events, sec_len):
    u = MusicUnit()
    for e in events:
        if e.end_tick > e.start_tick:
            u.add_event(e)
    u.add_event(MusicEvent(0, 0, sec_len, sec_len))  # zero-drift terminal landmark
    return u


# ============================================================================
# PHASE 1 — RAW RBN DRAFT (single voice, off-grid, chromatic)
# ============================================================================
def generate_phase1():
    rng = np.random.default_rng(SEED)
    p1 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=4)
    p1.create_matrix(num_voices=1, num_sections=N_SECTIONS)
    p1.add_voice("RawLead", program=KALIMBA.midi_program, channel=0)
    for sname, nb in FORM:
        p1.add_section(sname, bars=nb)

    for sname, (slen, soff) in SECTION_TICKS.items():
        evs = []
        nb = dict(FORM)[sname]
        for bar_in_sec in range(nb):
            bar_start = bar_in_sec * BAR
            for step_in_bar in range(STEPS_PER_BAR):
                step = (SECTION_BAR_OFF[sname] + bar_in_sec) * STEPS_PER_BAR + step_in_bar
                d = DECODED[step]
                if d["lead_deg"] >= 12:
                    continue
                t_onset = bar_start + step_in_bar * SIXTEENTH + int(rng.integers(-18, 18))
                t_onset = max(bar_start, min(t_onset, bar_start + BAR - 40))
                pitch = 48 + d["lead_deg"] * 3        # raw chromatic
                dur = int(rng.integers(80, 160))
                end_t = min(t_onset + dur, bar_start + BAR - 10)
                evs.append(MusicEvent(pitch=int(pitch), volume=56 + d["lead_vel"] * 7,
                                      start_tick=t_onset, end_tick=end_t))
        p1.fill_voice_section("RawLead", sname, unit_from(evs, slen))
    ok, msg = p1.validate()
    assert ok, f"phase1 validate failed: {msg}"
    path = ROOT / "MIDI" / f"{NAME}-phase1.mid"
    p1.to_midi(str(path))
    write_provenance(str(path), "ai-generated", f"musicom nightly {NAME}",
                     sources=["methods_db:082 RBNCC", f"style:{GENRE}",
                              "phase:1 raw draft", f"source:210-rbncc-west-african-polyrhythm"],
                     parameters={"phase": 1, "seed": SEED, "init_seed": INIT_SEED,
                                 "key": KEY_NAME, "bpm": BPM,
                                 "form": [s for s, _ in FORM],
                                 "rbn": {"n": 16, "k": 2, "p": 0.5,
                                         "transient": transient_len,
                                         "cycle_len": cycle_len,
                                         "frozen_nodes": frozen},
                                 "notes": "raw RBN pitch-index, off-grid, chromatic"})
    assert path.stat().st_size > 40, "phase1 empty"
    print("phase1 midi:", path, path.stat().st_size, "bytes")
    return path


# ============================================================================
# PHASE 2 — RULES POST-PROCESS (grid + chord quant + variation + texture)
# ============================================================================
def deg_transpose(d, k=2):
    return (d + k) % 7


def deg_invert(d, pivot=4):
    return (2 * pivot - d) % 7


DENSE = {"Chorus", "Chorus2", "Chorus3", "Break", "Finale"}


def lead_events():
    notes = []
    for sname, nb in FORM:
        soff = SECTION_BAR_OFF[sname]
        slots = []
        seq = []                        # (is_note, degree, vel) in time order
        for bar_in_sec in range(nb):
            for step_in_bar in range(STEPS_PER_BAR):
                step = (soff + bar_in_sec) * STEPS_PER_BAR + step_in_bar
                d = DECODED[step]
                sl = bar_in_sec * STEPS_PER_BAR + step_in_bar
                slots.append(sl)
                seq.append((d["lead_deg"] < 12, d["lead_deg"] % 7, d["lead_vel"]))
        # per-section degree transform (transpose / invert)
        def t(deg):
            if sname == "Verse2":
                return deg_transpose(deg)
            if sname == "Chorus2":
                return deg_invert(deg)
            return deg
        seq = [(n, t(deg) if n else deg, vel) for n, deg, vel in seq]
        # retrograde: reverse the melodic sequence, keep the slot (rhythm) grid
        if sname in ("Break", "Coda"):
            seq = seq[::-1]
        reg_floor = {"Intro": 60, "Bridge": 74}.get(sname, 62)
        for sl, (is_note, deg, vel) in zip(slots, seq):
            if not is_note:
                continue
            bar_in_sec = sl // STEPS_PER_BAR
            bar = soff + bar_in_sec
            pool = LEAD_POOL[bar]
            st = bar * BAR + (sl % STEPS_PER_BAR) * SIXTEENTH
            vel_v = 56 + vel * 7
            if sname == "Chorus3":
                dur = EIGHTH * 2                      # augmentation
            elif sname == "Finale":
                dur = SIXTEENTH                       # diminution (16th runs)
                vel_v = min(127, vel_v + 8)
            elif sname == "Coda":
                dur = SIXTEENTH                       # diminution fragment
                vel_v = max(30, vel_v - 28)           # fade
            elif sname == "Intro":
                dur = EIGHTH * 2                      # sparse, ring
            else:
                dur = EIGHTH
            target = pc_to_pitch(G_SCALE[deg], reg_floor)
            best = min(pool, key=lambda p: abs(p - target))
            for cand in (best - 12, best + 12):
                if abs(cand - target) < abs(best - target):
                    best = cand
            pitch = max(48, min(91, best))
            notes.append(MusicEvent(pitch=pitch, volume=int(vel_v),
                                    start_tick=st,
                                    end_tick=min(st + dur, (bar + 1) * BAR - 1)))
    return notes


def balafon_events():
    evs = []
    for sname, nb in FORM:
        soff = SECTION_BAR_OFF[sname]
        for bar_in_sec in range(nb):
            bar = soff + bar_in_sec
            bar0 = bar * BAR
            pool = BAL_POOL[bar]
            for step_in_bar in range(STEPS_PER_BAR):
                step = bar * STEPS_PER_BAR + step_in_bar
                d = DECODED[step]
                if d["bal_gate"] != 1:
                    continue
                st = bar0 + step_in_bar * SIXTEENTH
                raw = 60 + d["bal_deg"] * 4
                best = min(pool, key=lambda p: abs(p - raw))
                if sname == "Bridge":   # counterline: mirror register (high)
                    best = max(pool)
                evs.append(MusicEvent(pitch=best, volume=84,
                                      start_tick=st, end_tick=st + 100))
    return evs


def bell_events():
    BELL_STEPS = (0, 3, 6, 10, 12)
    evs = []
    for sname, nb in FORM:
        soff = SECTION_BAR_OFF[sname]
        for bar_in_sec in range(nb):
            bar = soff + bar_in_sec
            bar0 = bar * BAR
            deg = CHORD_SPECS[bar]
            root_pc = G_SCALE[deg % 7]
            fifth_pc = G_SCALE[(deg + 2) % 7]
            low = pc_to_pitch(root_pc, 72)
            high = pc_to_pitch(fifth_pc, 79)
            dense = sname in DENSE
            for j, step in enumerate(BELL_STEPS):
                t = bar0 + step * SIXTEENTH
                pitch = low if j % 2 == 0 else high
                evs.append(MusicEvent(pitch=pitch, volume=100 if j == 0 else 88,
                                      start_tick=t, end_tick=t + 90))
            if dense:
                evs.append(MusicEvent(pitch=high, volume=78,
                                      start_tick=bar0 + 14 * SIXTEENTH,
                                      end_tick=bar0 + 14 * SIXTEENTH + 80))
    return evs


def bass_events():
    evs = []
    for sname, nb in FORM:
        soff = SECTION_BAR_OFF[sname]
        for bar_in_sec in range(nb):
            bar = soff + bar_in_sec
            bar0 = bar * BAR
            tones = BASS_POOL[bar]
            root = tones[0]
            if sname in ("Intro", "Coda"):     # sparse pedal: root holds
                evs.append(MusicEvent(pitch=root, volume=86,
                                      start_tick=bar0, end_tick=bar0 + 900))
                continue
            for j, step in enumerate((0, 6, 10)):   # 3+3+2 dunun pulse
                t = bar0 + step * SIXTEENTH
                evs.append(MusicEvent(pitch=root, volume=(100, 86, 86)[j],
                                      start_tick=t, end_tick=t + 160))
    return evs


def drums_events():
    evs = []
    for sname, nb in FORM:
        soff = SECTION_BAR_OFF[sname]
        for bar_in_sec in range(nb):
            bar = soff + bar_in_sec
            bar0 = bar * BAR
            dense = sname in DENSE
            for step_in_bar in range(STEPS_PER_BAR):
                t = bar0 + step_in_bar * SIXTEENTH
                step = bar * STEPS_PER_BAR + step_in_bar
                if step_in_bar % 2 == 0:
                    sh_vel = 70 if step_in_bar % 4 == 0 else 52
                    evs.append(MusicEvent(pitch=42, volume=sh_vel,
                                          start_tick=t, end_tick=t + 40))
                elif DECODED[step]["shake"] == 3 or dense:
                    evs.append(MusicEvent(pitch=42, volume=60,
                                          start_tick=t, end_tick=t + 40))
                if step_in_bar in (0, 10):
                    evs.append(MusicEvent(pitch=36, volume=100 if step_in_bar == 0 else 90,
                                          start_tick=t, end_tick=t + 90))
                if step_in_bar in (4, 12):
                    evs.append(MusicEvent(pitch=38, volume=92,
                                          start_tick=t, end_tick=t + 80))
                if step_in_bar == 14:
                    evs.append(MusicEvent(pitch=38, volume=55,
                                          start_tick=t, end_tick=t + 50))
    return evs


def finalize_pitched(events, pool_by_bar):
    out = []
    for e in events:
        if e.pitch == 0:
            out.append(e)
            continue
        st = snap16(e.start_tick)
        if st < 0:
            st = 0
        bar = min(st // BAR, N_BARS - 1)
        pool = pool_by_bar[bar]
        best = min(pool, key=lambda p: abs(p - e.pitch))
        for cand in (best - 12, best + 12):
            if abs(cand - e.pitch) < abs(best - e.pitch):
                best = cand
        out.append(MusicEvent(pitch=best, volume=int(e.volume),
                              start_tick=st, end_tick=max(st + 1, e.end_tick)))
    seen = {}
    res = []
    for e in out:
        if e.pitch == 0:
            res.append(e)
            continue
        key = (e.start_tick, e.pitch)
        if key in seen:
            seen[key].end_tick = max(seen[key].end_tick, e.end_tick)
        else:
            seen[key] = e
            res.append(e)
    res.sort(key=lambda e: (e.start_tick, e.pitch))
    return res


def cap_leaps(events, pool_by_bar, max_leap=10):
    evs = sorted([e for e in events if e.pitch], key=lambda e: e.start_tick)
    for i in range(1, len(evs)):
        prev, cur = evs[i - 1], evs[i]
        if cur.start_tick - prev.start_tick <= BAR and abs(cur.pitch - prev.pitch) > max_leap:
            bar = min(cur.start_tick // BAR, N_BARS - 1)
            pool = pool_by_bar[bar]
            target = prev.pitch + max_leap if cur.pitch > prev.pitch else prev.pitch - max_leap
            best = min(pool, key=lambda p: (abs(p - target), abs(p - cur.pitch)))
            cur.pitch = best
    return evs


lead_q = cap_leaps(finalize_pitched(lead_events(), LEAD_POOL), LEAD_POOL)
bal_q = finalize_pitched(balafon_events(), BAL_POOL)
bell_q = finalize_pitched(bell_events(), LEAD_POOL)   # bell low/high are chord tones
bass_q = finalize_pitched(bass_events(), BASS_POOL)
drums_q = drums_events()

VOICES = [
    ("Gankogui", MARIMBA.midi_program, 0),
    ("LeadKora", KALIMBA.midi_program, 1),
    ("BassDunun", DOUBLE_BASS.midi_program, 2),
    ("Balafon", XYLOPHONE.midi_program, 3),
    ("Drums", 0, 9),
]
events_by_voice = {
    "Gankogui": bell_q, "LeadKora": lead_q, "BassDunun": bass_q,
    "Balafon": bal_q, "Drums": drums_q,
}

composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=4)
composer.create_matrix(num_voices=len(VOICES), num_sections=N_SECTIONS)
for vname, prog, ch in VOICES:
    composer.add_voice(vname, program=prog, channel=ch)
for sname, nb in FORM:
    composer.add_section(sname, bars=nb)

for vname, prog, ch in VOICES:
    evs = events_by_voice[vname]
    for sname, (slen, soff) in SECTION_TICKS.items():
        seg = sorted([e for e in evs if soff <= e.start_tick < soff + slen],
                     key=lambda e: (e.start_tick, e.pitch))
        for e in seg:
            e.start_tick -= soff
            e.end_tick -= soff
            if e.end_tick > slen:
                e.end_tick = slen
            if e.end_tick <= e.start_tick:
                e.end_tick = e.start_tick + 1
        composer.fill_voice_section(vname, sname, unit_from(seg, slen))

# ---- dual-version export (perfect then humanized) --------------------------
hz_seed = SEED + 1
hz_instruments = {
    "Gankogui": MARIMBA.humanize_dna,
    "LeadKora": KALIMBA.humanize_dna,
    "BassDunun": DOUBLE_BASS.humanize_dna,
    "Balafon": XYLOPHONE.humanize_dna,
    "Drums": DRUM_KIT.humanize_dna,
}
perfect_path = ROOT / "MIDI" / f"{NAME}-perfect.mid"
humanized_path = ROOT / "MIDI" / f"{NAME}-humanized.mid"
hz = export_dual(composer, str(perfect_path), str(humanized_path),
                 style=GENRE, seed=hz_seed, bpm=BPM, instruments=hz_instruments)

for path, phase, note in ((perfect_path, "2-perfect", "grid-locked, no jitter"),
                          (humanized_path, "2-humanized", "style+instrument humanized")):
    write_provenance(str(path), "ai-generated", f"musicom nightly {NAME}",
                     sources=["methods_db:082 RBNCC", f"style:{GENRE}",
                              "phase:2 rules", f"humanize_seed:{hz_seed}",
                              "source:210-rbncc-west-african-polyrhythm"],
                     parameters={"phase": phase, "seed": SEED, "key": KEY_NAME,
                                 "bpm": BPM, "form": [s for s, _ in FORM],
                                 "humanize": hz, "note": note,
                                 "rbn": {"n": 16, "k": 2, "p": 0.5,
                                         "transient": transient_len,
                                         "cycle_len": cycle_len,
                                         "frozen_nodes": frozen}})
print("perfect midi:", perfect_path, perfect_path.stat().st_size, "bytes")
print("humanized midi:", humanized_path, humanized_path.stat().st_size, "bytes")

# ---- grid visualization + summary ------------------------------------------
try:
    write_grid_visualization(composer.matrix,
                             str(ROOT / "Analysis" / "grid_visualization.txt"),
                             ticks_per_character=240,
                             voice_names=[v for v, _, _ in VOICES],
                             bpm=BPM)
except Exception as exc:
    print("grid viz skipped:", exc)

summary = {
    "project": NAME, "genre": GENRE, "key": KEY_NAME, "bpm": BPM,
    "form": [s for s, _ in FORM], "bars": N_BARS, "total_ticks": TOTAL_TICKS,
    "source": "210-rbncc-west-african-polyrhythm",
    "decision": "redesign (provenance.json + index.html missing)",
    "rbn": {"n": 16, "k": 2, "p": 0.5, "transient": transient_len,
            "cycle_len": cycle_len, "frozen_nodes": frozen},
    "variations": {
        "Intro": "register shift (low) + sparse",
        "Verse": "base motif (3:4 polyrhythm)",
        "Chorus": "density rise (tutti)",
        "Verse2": "transposition (+2 degrees)",
        "Chorus2": "inversion (pivot degree 4)",
        "Break": "retrograde + darker progression (vi-IV-ii-I)",
        "Bridge": "register shift (high) + balafon counterline",
        "Chorus3": "augmentation (x2 durations)",
        "Finale": "diminution (16th runs) + density rise",
        "Coda": "retrograde recap + diminution fragment + fade",
    },
    "section_roots_midpoint": {s: DEG_LABELS[section_roots[s]] for s, _ in FORM},
    "voices": [v for v, _, _ in VOICES],
    "humanize_seed": hz_seed,
}
with open(ROOT / "Analysis" / "summary.json", "w") as f:
    json.dump(summary, f, indent=2)

# export phase-1 raw draft (its own composer, own validate gate)
generate_phase1()
print("DONE compose")
