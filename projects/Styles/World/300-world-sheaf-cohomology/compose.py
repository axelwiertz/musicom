# -*- coding: utf-8 -*-
"""300-world-sheaf-cohomology -- World / Method 134 Cellular Sheaf Cohomology
Composition (CSCC), abstract layer.

LAYERED METHODOLOGY: abstract (weekly ~1/7 cadence -> abstract->concrete
interpretation path). The abstract layer builds a CELLULAR SHEAF over the
section graph and computes real cohomology numbers (H^0 coherence budget,
H^1 rigidity, Euler-Poincare, holonomy, spanning-tree cadence cuts, and a
least-squares repair residual = tension). The concrete layer realizes each
section's harmonic state (stalk) as a World texture.

Two-phase architecture:
  Phase 1: raw generative draft. A single voice walks chromatically, pulled
           toward the section's chord tones (the stalk), with off-grid onset
           jitter and unquantized pitch. No harmony.
  Phase 2: musicom rules post-process -- grid-lock to 8th, tiered snap
           (strong beat -> chord tone, weak -> D-minor scale tone), full
           World texture (shakuhachi lead, koto counter, sitar drone,
           acoustic bass, taiko-flavoured drums), zero-drift landmark,
           validate() on BOTH phases, export_dual -> -perfect + -humanized.

Engine only. mido used READ-ONLY in a separate verify step.

Key: D natural minor {0,2,4,5,7,9,10} (D E F G A Bb C).
Form: intro-verse-chorus-verse-chorus-outro (6 sections, 32 bars).
"""
import os
import json
import sys
from fractions import Fraction

import numpy as np

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer
from visualization.grid import write_grid_visualization
from workflows.provenance import write_provenance, AI_ASSISTED
from workflows.humanize import export_dual
from workflows.musicom_workflow import pick_form, form_to_sections
from sound.synthesis.scale_quantizer import (
    ScaleQuantizer, classify_weight, STRONG_GRID,
)
from workflows.pitch_audit import audit_voice

# instrument registry (source of truth - NOT pip-installed)
INSTR_DIR = "/opt/data/repos/musicom/projects/Instruments"
if INSTR_DIR not in sys.path:
    sys.path.insert(0, INSTR_DIR)
from instrument_registry import by_name  # noqa: E402

SEED = 20261112
HZ_SEED = SEED * 13 + 300
FORM_SEED = SEED * 10 + 7

PROJ = "/opt/data/projects/Styles/World/300-world-sheaf-cohomology"
MIDI_DIR = os.path.join(PROJ, "MIDI")
AUDIO_DIR = os.path.join(PROJ, "Audio")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")
for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
    os.makedirs(d, exist_ok=True)

# ------------------------------------------------------------------- concept
BPM = 100
TPB = 480
BEATS = 4
BAR = TPB * BEATS                # 1920
GRID16 = 120
GRID8 = 240

_form = pick_form("world", rng=np.random.default_rng(FORM_SEED))
while _form in ("loop", "loop4", "loop16"):
    _form = pick_form("world", rng=np.random.default_rng(FORM_SEED + 1))
FORM = _form
NAMES, BARS_PER = form_to_sections(FORM)
N_SECTIONS = len(NAMES)
N_BARS = sum(BARS_PER)

SEC_BAR_OFFSET = []
acc = 0
for b in BARS_PER:
    SEC_BAR_OFFSET.append(acc)
    acc += b

# D natural minor
KEY = "D natural minor"
KEY_PCS = {0, 2, 4, 5, 7, 9, 10}
TONIC = 50                      # D3
SCALE_ROOT = 50

# ------------------------------------------------------------------- harmony
# One chord per section (the harmonic state = a sheaf stalk over the section).
CHORDS = {
    "Dm7":    {"pcs": {2, 5, 9, 0},   "root": 38, "name": "Dm7"},
    "Gm7":    {"pcs": {7, 10, 2, 5},  "root": 43, "name": "Gm7"},
    "Bbmaj7": {"pcs": {10, 2, 5, 9},  "root": 46, "name": "Bbmaj7"},
    "Fmaj7":  {"pcs": {5, 9, 0, 4},   "root": 41, "name": "Fmaj7"},
}

# section -> chord arc (i7 - iv7 - VImaj7 - IIImaj7 - VImaj7 - i7)
SECTION_CHORD = ["Dm7", "Gm7", "Bbmaj7", "Fmaj7", "Bbmaj7", "Dm7"]
# cumulative lift (register push) per section: HOME -> LIFT -> TENSE -> relax
# -> TENSE -> HOME
SECTION_LIFT = [0, 2, 3, 2, 3, 0]
# signed seam pull between consecutive sections (LIFT +, RELEASE -)
SEAM_LIFT = [2, 1, -1, 1, -3, 0]
assert N_SECTIONS == 6 == len(SECTION_CHORD) == len(SECTION_LIFT) == len(SEAM_LIFT), \
    (NAMES, SECTION_CHORD)
assert len(NAMES) == 6

BAR_PROG = []
for s in range(N_SECTIONS):
    BAR_PROG += [SECTION_CHORD[s]] * BARS_PER[s]
assert len(BAR_PROG) == N_BARS

CHORD_PCS_BY_BAR = {bar: sorted(CHORDS[BAR_PROG[bar]]["pcs"])
                    for bar in range(N_BARS)}
ROOT_BY_BAR = {bar: CHORDS[BAR_PROG[bar]]["root"] for bar in range(N_BARS)}

# =====================================================================
# ABSTRACT LAYER -- Cellular Sheaf Cohomology (Method 134)
# =====================================================================
# Section graph: 6 vertices (sections) in a CYCLE C6.
# Stalks = 4-dim pc-indicator vectors (one coordinate per chord tone).
# Seams = common-tone gluing (R1): each seam demands its shared pcs agree.
# Demand b = SEAM_LIFT magnitude on each shared pc (the tension grammar).
# =====================================================================

VERTEX_CHORDS = [sorted(CHORDS[c]["pcs"]) for c in SECTION_CHORD]

SHEAF_EDGES = [(i, (i + 1) % N_SECTIONS) for i in range(N_SECTIONS)]  # C6
DV = 4                                              # stalk dim per vertex


def exact_rank(M):
    A = [[Fraction(x) for x in row] for row in M]
    rows, cols = len(A), (len(A[0]) if A else 0)
    r = 0
    for c in range(cols):
        piv = next((i for i in range(r, rows) if A[i][c] != 0), None)
        if piv is None:
            continue
        A[r], A[piv] = A[piv], A[r]
        p = A[r][c]
        A[r] = [x / p for x in A[r]]
        for i in range(rows):
            if i != r and A[i][c] != 0:
                f = A[i][c]
                A[i] = [a - f * b for a, b in zip(A[i], A[r])]
        r += 1
        if r == rows:
            break
    return r


def restriction_matrix(vertex_pcs, common_pcs):
    M = [[0] * len(vertex_pcs) for _ in range(len(common_pcs))]
    for i, c in enumerate(common_pcs):
        M[i][vertex_pcs.index(c)] = 1
    return M


def compute_sheaf():
    D = []
    seam_commons = []
    for (u, v) in SHEAF_EDGES:
        common = sorted(set(VERTEX_CHORDS[u]).intersection(set(VERTEX_CHORDS[v])))
        seam_commons.append(common)
        Ru = restriction_matrix(VERTEX_CHORDS[u], common)
        Rv = restriction_matrix(VERTEX_CHORDS[v], common)
        for row in range(len(common)):
            r = [0] * (N_SECTIONS * DV)
            for j in range(DV):
                if Ru[row][j]:
                    r[u * DV + j] += 1
            for j in range(DV):
                if Rv[row][j]:
                    r[v * DV + j] -= 1
            D.append(r)
    de_total = sum(len(c) for c in seam_commons)
    dv_total = N_SECTIONS * DV
    rk = exact_rank(D)
    h0 = dv_total - rk
    h1 = de_total - rk
    assert h0 - h1 == dv_total - de_total, "Euler-Poincare violated"

    # demand b: SEAM_LIFT on every shared pc of that seam
    DEMAND = [[SEAM_LIFT[e]] * len(seam_commons[e]) for e in range(N_SECTIONS)]

    # least-squares repair residual = tension curve
    A = np.array([[int(x) for x in row] for row in D], dtype=float)
    b = np.array([x for d in DEMAND for x in d], dtype=float)
    x, *_ = np.linalg.lstsq(A, b, rcond=None)
    res = A @ x - b
    idx = 0
    seam_residual = []
    for d in DEMAND:
        seg = res[idx:idx + len(d)]
        idx += len(d)
        seam_residual.append(round(float(np.linalg.norm(seg)), 4))

    return {
        "vertices": SECTION_CHORD,
        "vertex_pcs": [list(c) for c in VERTEX_CHORDS],
        "edges": SHEAF_EDGES,
        "seam_commons": seam_commons,
        "stalk_dim": DV,
        "sum_dv": dv_total,
        "sum_de": de_total,
        "rank_delta": rk,
        "dim_H0": h0,
        "dim_H1": h1,
        "euler_poincare": f"{h0}-{h1}={h0 - h1} (sum dv - sum de = {dv_total - de_total})",
        "holonomy": "identity (T_0) -- loop closes, Outro returns to Intro chord",
        "spanning_trees_C6": 6,     # tau(C6) = 6 cadence-cut choices
        "seam_lift": SEAM_LIFT,
        "demand_per_seam": DEMAND,
        "seam_residual": seam_residual,
        "section_lift": SECTION_LIFT,
    }


SHEAF = compute_sheaf()
print("SHEAF:", json.dumps(SHEAF, indent=2, default=str))

TENSION = SECTION_LIFT            # per section index [0..5], register/density arc


def chord_tones(bar, lo, hi):
    tones = set()
    for base in (36, 48, 60, 72, 84, 96):
        for pc in CHORD_PCS_BY_BAR[bar]:
            p = base + pc
            if lo <= p <= hi:
                tones.add(p)
    return sorted(tones)


def scale_tones(lo, hi):
    return [p for p in range(lo, hi + 1) if p % 12 in KEY_PCS]


def sec_of_bar(bar):
    s = 0
    while s < N_SECTIONS - 1 and bar >= SEC_BAR_OFFSET[s] + BARS_PER[s]:
        s += 1
    return s


# ------------------------------------------------------------------- registers
LEAD_LO, LEAD_HI = 57, 84
KOTO_LO, KOTO_HI = 53, 84
DRONE_LO, DRONE_HI = 48, 74
BASS_LO, BASS_HI = 30, 55

sq = ScaleQuantizer(root=SCALE_ROOT, scale="minor")
STRONG = STRONG_GRID.get("4/4", (0, 960))


# ------------------------------------------------------------------- Phase-1 walk
def raw_stalk_walk(span, chord_pc, tension, seed, lo=55, hi=88):
    """Single-voice raw draft: chromatic walk pulled toward the section's
    chord tones (the sheaf stalk). Off-grid onset jitter + unquantized pitch."""
    rng = np.random.default_rng(seed)
    n_slots = max(1, int(span // GRID8))
    lo = int(lo + 4 * tension)
    hi = min(96, int(hi + 6 * tension))
    tones = sorted({b + pc for b in (48, 60, 72, 84, 96)
                    for pc in chord_pc if lo <= b + pc <= hi})
    events = []
    pitch = min(tones, key=lambda x: abs(x - (58 + 4 * tension))) if tones else 60
    onset = 0.0
    for _ in range(n_slots):
        if tones and rng.random() < 0.55:
            target = tones[int(rng.integers(0, len(tones)))]
            pitch = int(np.clip(pitch + (target - pitch) // 2
                                + int(rng.integers(-2, 3)), lo, hi))
        else:
            pitch = int(np.clip(pitch + int(rng.integers(-5, 6)), lo, hi))
        st = int(round(onset + rng.normal(0, 16)))
        st = max(0, min(st, span - 40))
        dur = int(round(200 + rng.normal(0, 40)))
        en = min(st + dur, span - 1)
        if en <= st:
            en = st + 1
        vel = int(np.clip(70 + rng.normal(0, 10) + tension * 6, 40, 105))
        events.append(MusicEvent(pitch=pitch, volume=vel,
                                 start_tick=st, end_tick=en))
        onset += GRID8 + rng.normal(0, 18)
    return events


# ------------------------------------------------------------ PHASE 1: raw
phase1 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
phase1.create_matrix(num_voices=1, num_sections=N_SECTIONS)
phase1.add_voice("Sheaf_Raw", program=by_name("shakuhachi").midi_program, channel=0)

P1_OFFGRID = 0
P1_MEAN = {}
for s, name in enumerate(NAMES):
    phase1.add_section(name, bars=BARS_PER[s])
    span = BARS_PER[s] * BAR
    evs = raw_stalk_walk(span, VERTEX_CHORDS[s], TENSION[s], SEED + s)
    if not any(e.pitch == 0 and e.end_tick == span for e in evs):
        evs.append(MusicEvent(pitch=0, volume=0, start_tick=span - 1,
                              end_tick=span))
    P1_OFFGRID += sum(1 for e in evs if e.pitch != 0 and e.start_tick % GRID16 != 0)
    pitches = [e.pitch for e in evs if e.pitch != 0]
    P1_MEAN[name] = round(float(np.mean(pitches)), 2) if pitches else 0.0
    phase1.set_unit(0, s, MusicUnit(events=evs))

ok1, msg1 = phase1.validate()
if not ok1:
    raise RuntimeError("phase1 validate FAIL: " + msg1)
P1_MIDI = os.path.join(MIDI_DIR, "300-world-sheaf-cohomology-phase1.mid")
phase1.to_midi(P1_MIDI)
assert os.path.getsize(P1_MIDI) > 40
print("PHASE1 validate:", msg1, "| off-grid onsets:", P1_OFFGRID)
print("PHASE1 per-section mean pitch:", P1_MEAN)


# ------------------------------------------------------------ PHASE 2: rules
phase2 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
VOICES = [
    ("Lead", by_name("shakuhachi").midi_program, 0),   # stalk-walk lead
    ("Bass", by_name("acoustic_bass").midi_program, 1),  # root/fifth
    ("Drone", by_name("sitar").midi_program, 2),        # sustained chord tones
    ("Koto", by_name("koto").midi_program, 3),          # plucked counter
    ("Drums", 0, 9),                                     # taiko-flavour kit
]
N_V = len(VOICES)
phase2.create_matrix(num_voices=N_V, num_sections=N_SECTIONS)
for name, prog, ch in VOICES:
    phase2.add_voice(name, program=prog, channel=ch)
for i, name in enumerate(NAMES):
    phase2.add_section(name, bars=BARS_PER[i])


def grid_lock_dedup(events, grid=GRID8):
    by_key = {}
    out = []
    for e in events:
        if e.pitch == 0:
            out.append(e)
            continue
        st = int(round(e.start_tick / grid) * grid)
        st = max(0, st)
        en = max(st + 1, int(e.end_tick))
        key = (st, e.pitch)
        if key in by_key:
            if en > by_key[key].end_tick:
                by_key[key] = MusicEvent(pitch=e.pitch,
                                         volume=max(e.volume, by_key[key].volume),
                                         start_tick=st, end_tick=en)
        else:
            by_key[key] = MusicEvent(pitch=e.pitch, volume=e.volume,
                                     start_tick=st, end_tick=en)
    for key in sorted(by_key):
        out.append(by_key[key])
    return out


def landmark(events, span):
    out = []
    for e in events:
        if e.start_tick >= span:
            continue
        st = min(int(e.start_tick), span - 1)
        en = min(int(e.end_tick), span)
        if en <= st:
            en = st + 1
        out.append(MusicEvent(pitch=e.pitch, volume=e.volume,
                              start_tick=st, end_tick=en))
    out.sort(key=lambda e: (e.start_tick, 0 if e.pitch == 0 else 1))
    if not any(e.pitch == 0 and e.end_tick == span for e in out):
        out.append(MusicEvent(pitch=0, volume=0, start_tick=span - 1,
                              end_tick=span))
    return out


def snap(e, bar, lo, hi):
    w = classify_weight(e.start_tick, STRONG, BAR)
    if w == "strong":
        tones = chord_tones(bar, lo=lo, hi=hi)
        return sq.tiered_quantize(e.pitch, weight="strong", chord_tones=tones)
    p = sq.quantize(e.pitch)
    if p < lo or p > hi:
        cands = scale_tones(lo, hi)
        if cands:
            p = min(cands, key=lambda x: abs(x - p))
    return p


# ---- lead: stalk walk, grid-locked + tiered snap --------------------------
for s, name in enumerate(NAMES):
    span = BARS_PER[s] * BAR
    lo, hi = LEAD_LO, LEAD_HI
    evs = raw_stalk_walk(span, VERTEX_CHORDS[s], TENSION[s], SEED + s,
                         lo=lo, hi=hi)
    evs = grid_lock_dedup(evs)
    out = []
    seen = {}
    for e in evs:
        if e.pitch == 0:
            continue
        if e.start_tick >= span:
            continue
        bar = SEC_BAR_OFFSET[s] + (e.start_tick // BAR)
        bar = min(bar, N_BARS - 1)
        pitch = snap(e, bar, lo, hi)
        key = (e.start_tick, pitch)
        if key in seen:
            if e.end_tick > seen[key].end_tick:
                seen[key] = MusicEvent(pitch=pitch,
                                       volume=max(e.volume, seen[key].volume),
                                       start_tick=e.start_tick, end_tick=e.end_tick)
        else:
            seen[key] = MusicEvent(pitch=pitch, volume=e.volume,
                                   start_tick=e.start_tick, end_tick=e.end_tick)
    for key in sorted(seen):
        out.append(seen[key])
    phase2.set_unit(0, s, MusicUnit(events=landmark(out, span)))


# ---- bass: root (beat 1) + fifth (beat 3), sustained ----------------------
for bar in range(N_BARS):
    s = sec_of_bar(bar)
    t0 = (bar - SEC_BAR_OFFSET[s]) * BAR
    root = ROOT_BY_BAR[bar]
    fifth = root + 7
    unit = phase2.matrix.get_unit((1, s))
    events = list(unit.events) if unit is not None else []
    events.append(MusicEvent(pitch=root, volume=96, start_tick=t0,
                             end_tick=t0 + int(BAR * 0.9)))
    events.append(MusicEvent(pitch=fifth, volume=78, start_tick=t0 + 960,
                             end_tick=t0 + 960 + int(BAR * 0.85)))
    phase2.set_unit(1, s, MusicUnit(events=events))


# ---- drone (sitar): sustained chord tones, low velocity -------------------
for bar in range(N_BARS):
    s = sec_of_bar(bar)
    t0 = (bar - SEC_BAR_OFFSET[s]) * BAR
    tones = chord_tones(bar, lo=DRONE_LO, hi=DRONE_HI)
    unit = phase2.matrix.get_unit((2, s))
    events = list(unit.events) if unit is not None else []
    for k, p in enumerate(tones):
        events.append(MusicEvent(pitch=p, volume=40 + 3 * k,
                                 start_tick=t0, end_tick=t0 + BAR - 60))
    phase2.set_unit(2, s, MusicUnit(events=events))


# ---- koto: 8th-note plucked arpeggio (denser/hotter when tense) -----------
for bar in range(N_BARS):
    s = sec_of_bar(bar)
    t0 = (bar - SEC_BAR_OFFSET[s]) * BAR
    tones = chord_tones(bar, lo=KOTO_LO, hi=KOTO_HI)
    unit = phase2.matrix.get_unit((3, s))
    events = list(unit.events) if unit is not None else []
    dense = TENSION[s] >= 2.5
    for k in range(8):
        if not dense and k % 2 == 1:
            continue
        t = t0 + k * GRID8
        p = tones[(k + bar) % len(tones)]
        events.append(MusicEvent(pitch=p, volume=(56 if dense else 46),
                                 start_tick=t, end_tick=t + int(GRID8 * 0.6)))
    phase2.set_unit(3, s, MusicUnit(events=events))


# ---- drums: taiko-flavoured kick + toms + optional shaker -----------------
for bar in range(N_BARS):
    s = sec_of_bar(bar)
    t0 = (bar - SEC_BAR_OFFSET[s]) * BAR
    tense = TENSION[s] >= 2.5
    unit = phase2.matrix.get_unit((4, s))
    events = list(unit.events) if unit is not None else []
    events.append(MusicEvent(pitch=36, volume=(74 if tense else 64),
                             start_tick=t0, end_tick=t0 + 90))
    if tense:
        events.append(MusicEvent(pitch=36, volume=68, start_tick=t0 + 960,
                                 end_tick=t0 + 960 + 90))
    for beat, tom in ((480, 48), (1440, 47)):
        events.append(MusicEvent(pitch=tom, volume=58,
                                 start_tick=t0 + beat, end_tick=t0 + beat + 70))
    if tense:
        for e8 in range(8):
            events.append(MusicEvent(pitch=54, volume=38,
                                     start_tick=t0 + e8 * GRID8,
                                     end_tick=t0 + e8 * GRID8 + 40))
    phase2.set_unit(4, s, MusicUnit(events=events))


# finalize bass/drone/koto/drums cells with landmark
for s in range(N_SECTIONS):
    span = BARS_PER[s] * BAR
    for row in (1, 2, 3, 4):
        unit = phase2.matrix.get_unit((row, s))
        events = list(unit.events) if unit is not None else []
        phase2.set_unit(row, s, MusicUnit(events=landmark(events, span)))

ok2, msg2 = phase2.validate()
if not ok2:
    raise RuntimeError("phase2 validate FAIL: " + msg2)
print("PHASE2 validate:", msg2)


# ------------------------------------------------------------------ audits
def global_notes(row):
    notes = []
    for s in range(N_SECTIONS):
        unit = phase2.matrix.get_unit((row, s))
        if unit is None:
            continue
        for e in unit.events:
            if e.pitch == 0:
                continue
            notes.append({"pitch": e.pitch,
                          "start_tick": SEC_BAR_OFFSET[s] * BAR + e.start_tick,
                          "end_tick": SEC_BAR_OFFSET[s] * BAR + e.end_tick})
    return notes


PITCHED = [(0, "Lead"), (1, "Bass"), (2, "Drone"), (3, "Koto")]
grid_audit = {}
harmony_audit = {}
for row, vname in PITCHED:
    notes = global_notes(row)
    onsets = [n["start_tick"] for n in notes]
    for grid_name, grid in (("16th", 120), ("8th", 240)):
        off = [o for o in onsets if o % grid != 0]
        grid_audit[f"{vname}:{grid_name}"] = f"{len(off)}/{len(onsets)}"
    r = audit_voice(notes, sorted(KEY_PCS), chord_pcs_by_bar=CHORD_PCS_BY_BAR,
                    strong_grid=STRONG, bar_ticks=BAR, grid=GRID8)
    harmony_audit[vname] = {
        "passes": r.passes, "audible": r.audible,
        "strong_ok": r.strong_ok, "weak_in_scale": r.weak_in_scale,
        "tagged": r.tagged_ornaments, "resolving": r.tagged_resolving,
        "non_resolving": r.tagged_non_resolving,
        "untagged_out_of_scale": r.untagged_out_of_scale,
        "strong_violations": r.strong_violations,
        "collisions": r.collisions,
    }
    print(f"AUDIT {vname}: {r.summary()}")

for k, v in grid_audit.items():
    print("GRID", k, v)
assert all(r["passes"] for r in harmony_audit.values()), "harmony audit FAIL"
assert all(int(x.split("/")[0]) == 0 for k, x in grid_audit.items()
           if k.endswith(":16th")), "grid audit FAIL (16th must be 0 off-grid)"


# ------------------------------------------------------------------ export
perfect_mid = os.path.join(MIDI_DIR, "300-world-sheaf-cohomology-perfect.mid")
human_mid = os.path.join(MIDI_DIR, "300-world-sheaf-cohomology-humanized.mid")

hz_instruments = {
    "Lead": by_name("shakuhachi").humanize_dna,
    "Koto": by_name("koto").humanize_dna,
    "Drone": by_name("sitar").humanize_dna,
    "Bass": by_name("acoustic_bass").humanize_dna,
    "Drums": by_name("drum_kit").humanize_dna,
}
hz = export_dual(phase2, perfect_mid, human_mid,
                 style="world", seed=HZ_SEED, bpm=BPM,
                 instruments=hz_instruments)
print("export_dual OK; hz summary:")
print(json.dumps(hz, indent=2, default=str))


# ------------------------------------------------------------------ provenance
write_provenance(P1_MIDI, AI_ASSISTED,
                 "Cellular Sheaf Cohomology Composition (Method 134) -- raw draft",
                 parameters={"phase": "1", "layer": "raw", "style": "world",
                             "key": KEY, "bpm": BPM, "seed": SEED,
                             "sections": N_SECTIONS, "bars": N_BARS,
                             "form": FORM,
                             "sheaf": SHEAF,
                             "section_mean_pitch": P1_MEAN},
                 notes="phase1 raw draft: single-voice chromatic walk pulled "
                       "toward each section's chord tones (the sheaf stalk); "
                       "off-grid onset jitter + unquantized pitch; no harmony.")
write_provenance(perfect_mid, AI_ASSISTED,
                 "Cellular Sheaf Cohomology 134 + musicom rules (phase 2, grid-locked)",
                 parameters={"phase": "2", "layer": "perfect", "style": "world",
                             "key": KEY, "bpm": BPM, "seed": SEED,
                             "humanize_seed": HZ_SEED,
                             "sections": N_SECTIONS, "bars": N_BARS,
                             "form": FORM,
                             "progression": BAR_PROG,
                             "sheaf": SHEAF},
                 notes="grid-locked concrete layer; off-grid onsets == 0; "
                       "tiered snap (strong->chord tone, weak->D-minor scale).")
write_provenance(human_mid, AI_ASSISTED,
                 "Cellular Sheaf Cohomology 134 + rules + humanize (phase 2, humanized)",
                 parameters={"phase": "2", "layer": "humanized", "style": "world",
                             "key": KEY, "bpm": BPM, "seed": SEED,
                             "humanize_seed": HZ_SEED,
                             "humanize_profiles": {
                                 k: (v.get("profile") if isinstance(v, dict) else v)
                                 for k, v in hz.items()}},
                 notes="style-derived seeded humanization (default profile + "
                       "per-instrument DNA).")


# ------------------------------------------------------------------ grid viz + manifest
gv = os.path.join(ANALYSIS_DIR, "grid_visualization.txt")
write_grid_visualization(phase2.matrix, gv, ticks_per_character=120,
                         voice_names=[v[0] for v in VOICES], bpm=BPM)
print("grid viz written", gv)

manifest = {
    "project": "300-world-sheaf-cohomology",
    "genre": "World",
    "method": "134 Cellular Sheaf Cohomology Composition (CSCC)",
    "paradigm": "Rules-Based",
    "layer": "abstract",
    "form": FORM,
    "key": KEY,
    "key_pcs": sorted(KEY_PCS),
    "bpm": BPM,
    "bars": N_BARS,
    "sections": NAMES,
    "bars_per_section": BARS_PER,
    "section_chord": SECTION_CHORD,
    "progression": BAR_PROG,
    "sheaf": SHEAF,
    "section_mean_pitch_phase1": P1_MEAN,
    "seed": SEED,
    "hz_seed": HZ_SEED,
    "form_seed": FORM_SEED,
    "phase1_midi": P1_MIDI,
    "perfect_midi": perfect_mid,
    "humanized_midi": human_mid,
    "phase1_offgrid": P1_OFFGRID,
    "grid_audit": grid_audit,
    "harmony_audit": harmony_audit,
    "hz_summary": hz,
}
with open(os.path.join(ANALYSIS_DIR, "manifest.json"), "w") as f:
    json.dump(manifest, f, indent=2, default=str)
print("DONE")
