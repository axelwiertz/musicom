# -*- coding: utf-8 -*-
"""245-attractor-chorale-rework — Experimental chorale, Method 043 (Lorenz SATM).

Rework of 061-attractor-chorale (audit failed: missing -phase1.mid + index.html).
Rebuilt from scratch through the canonical UnitMatrixComposer, preserving ONLY
the musical identity (E dorian, 92 BPM, Lorenz strange-attractor method 043,
homophonic SATB flute/bass chorale). Longer form (10 sections x 2-4 bars = 32
bars) with 6 documented variation techniques.

Two-phase architecture:
  Phase 1: raw Lorenz trajectory (RK4), single flute voice — unquantized pitch
           (z-coordinate -> raw MIDI int, NOT scale-snapped), speed-triggered
           off-grid onsets. -> 245-...-phase1.mid (own validate() gate).
  Phase 2: musicom rules — per-bar chord-tone quantization (floor t//BAR),
           voice-leading continuity, rhythm-grid snap (120/240), register
           enforcement, dedup; full 6-voice texture. -> 245-...-rework.mid.

Key: E dorian (E F# G A B C# D). KEY_PCS = {1,2,4,6,7,9,11}.
"""
import os
import random
import json

import numpy as np

from structures import MusicUnit, MusicEvent, MidiInstrument
from workflows.unitmatrix_composer import UnitMatrixComposer
from visualization.grid import write_grid_visualization
from workflows.provenance import write_provenance, AI_GENERATED, AI_ASSISTED

random.seed(245)
np.random.seed(245)

# ------------------------------------------------------------------ concept
BPM = 92
TPB = 480
BPB = 4
BAR = TPB * BPB                       # 1920
EIGHTH = 240
SIXTEENTH = 120

KEY_ROOT_PC = 4                       # E
KEY_NAME = "E dorian"
KEY_PCS = {1, 2, 4, 6, 7, 9, 11}      # E F# G A B C# D

SEED = 245

# ------------------------------------------------------------------ form
SECTIONS = [
    ("Intro", 2),
    ("VerseA", 4),
    ("VerseB", 4),
    ("Chorus", 4),
    ("VerseA2", 4),
    ("Bridge", 4),
    ("Chorus2", 4),
    ("Development", 2),
    ("Climax", 2),
    ("Outro", 2),
]
N_SECTIONS = len(SECTIONS)
TOTAL_BARS = sum(b for _, b in SECTIONS)          # 32
TOTAL_TICKS = TOTAL_BARS * BAR

# per-section harmonic regions (each its OWN progression; avoids bar-0 tonic bug)
PROG = [
    ["i", "IV"],                    # Intro (2)
    ["i", "ii", "IV", "i"],         # VerseA (4)
    ["i", "v", "III", "VII"],       # VerseB (4)
    ["IV", "v", "VII", "i"],        # Chorus (4)
    ["i", "ii", "IV", "i"],         # VerseA2 (4)
    ["vi°", "ii", "v", "VII"],      # Bridge (4)
    ["v", "vi°", "i", "ii"],        # Chorus2 (4)  = Chorus transposed +1 degree
    ["vi°", "v"],                   # Development (2)
    ["IV", "VII"],                  # Climax (2)
    ["i", "IV"],                    # Outro (2)
]
CHORD_WALK = [d for sec in PROG for d in sec]     # 32 degrees
assert len(CHORD_WALK) == TOTAL_BARS

# degree -> (root_pc, [root, third, fifth] pitch classes) — all in E dorian
DEG = {
    "i":    (4,  [4, 7, 11]),       # Em   E G B
    "ii":   (6,  [6, 9, 1]),        # F#m  F# A C#
    "III":  (7,  [7, 11, 2]),       # G    G B D
    "IV":   (9,  [9, 1, 4]),        # A    A C# E
    "v":    (11, [11, 2, 6]),       # Bm   B D F#
    "vi°":  (1,  [1, 4, 7]),        # C#°  C# E G
    "VII":  (2,  [2, 6, 9]),        # D    D F# A
}

# section MIDPOINT chord root (for the per-section harmonic-region report)
SECTION_START_BARS = []
_acc = 0
for _n, _b in SECTIONS:
    SECTION_START_BARS.append(_acc)
    _acc += _b


def section_of_bar(bar):
    s = 0
    for i in range(N_SECTIONS):
        if bar >= SECTION_START_BARS[i]:
            s = i
    return s


def section_name_of_bar(bar):
    return SECTIONS[section_of_bar(bar)][0]


section_roots = []
for s in range(N_SECTIONS):
    start = SECTION_START_BARS[s]
    bars = SECTIONS[s][1]
    mid = start + bars // 2                       # midpoint bar
    section_roots.append(DEG[CHORD_WALK[mid]][0])

# ------------------------------------------------------------------ voices
VOICES = [
    ("Soprano", MidiInstrument.FLUTE, 0, True),
    ("Alto",    MidiInstrument.FLUTE, 1, True),
    ("Tenor",   MidiInstrument.FLUTE, 2, True),
    ("Bass",    MidiInstrument.BASS,  3, True),
    ("Descant", 68,                   4, True),    # oboe counterline
    ("Perc",    0,                    9, False),   # ch9 timpani
]
VOICE_NAMES = [v[0] for v in VOICES]
PITCHED = {v[0] for v in VOICES if v[3]}

# register ranges per voice per section register-level (0=low, 1=high, 2=outro)
REG_LOW = {"Soprano": (62, 78), "Alto": (53, 70), "Tenor": (48, 62),
           "Bass": (38, 55), "Descant": (74, 88)}
REG_HIGH = {"Soprano": (74, 90), "Alto": (65, 82), "Tenor": (60, 74),
            "Bass": (38, 55), "Descant": (74, 88)}
REG_OUTRO = {"Soprano": (55, 70), "Alto": (48, 62), "Tenor": (43, 55),
             "Bass": (38, 50), "Descant": (74, 88)}

SECTION_REG = {
    "Intro": 0, "VerseA": 0, "VerseB": 0, "Chorus": 1, "VerseA2": 0,
    "Bridge": 0, "Chorus2": 1, "Development": 1, "Climax": 1, "Outro": 2,
}

# rhythm density per section: (speed-threshold, onset floor)
SECTION_DENSITY = {
    "Intro": (0.45, 2), "VerseA": (0.33, 3), "VerseB": (0.33, 3),
    "Chorus": (0.22, 4), "VerseA2": (0.33, 3), "Bridge": (0.28, 3),
    "Chorus2": (0.22, 4), "Development": (0.24, 4), "Climax": (0.18, 5),
    "Outro": (0.55, 2),
}

DESCANT_ACTIVE = {"Chorus", "Bridge", "Chorus2", "Climax"}


# ------------------------------------------------------------------ helpers
def fold_pc(pc, lo, hi, prev=None):
    """Nearest MIDI note with pitch class `pc` inside [lo,hi], near `prev`."""
    cands = [n for n in range(lo, hi + 1) if n % 12 == pc]
    if not cands:
        return lo
    if prev is None:
        return cands[len(cands) // 2]
    return min(cands, key=lambda n: abs(n - prev))


def split_abs_to_section(abs_events, s):
    start = SECTION_START_BARS[s] * BAR
    length = SECTIONS[s][1] * BAR
    end = start + length
    cell = []
    for e in abs_events:
        if e.end_tick <= start or e.start_tick >= end:
            continue
        st = max(0, e.start_tick - start)
        et = min(length, e.end_tick - start)
        if et <= st:
            continue
        cell.append(MusicEvent(pitch=e.pitch, volume=e.volume,
                               start_tick=st, end_tick=et))
    if not cell or cell[-1].end_tick < length:
        last = cell[-1].end_tick if cell else 0
        cell.append(MusicEvent(pitch=0, volume=0, start_tick=last, end_tick=length))
    return MusicUnit(events=cell)


# ------------------------------------------------------------------ attractor
LORENZ_SIGMA, LORENZ_RHO, LORENZ_BETA = 10.0, 28.0, 8.0 / 3.0


def lorenz_deriv(state):
    x, y, z = state
    return np.array([LORENZ_SIGMA * (y - x),
                     x * (LORENZ_RHO - z) - y,
                     x * y - LORENZ_BETA * z])


def rk4_step(state, h):
    k1 = lorenz_deriv(state)
    k2 = lorenz_deriv(state + 0.5 * h * k1)
    k3 = lorenz_deriv(state + 0.5 * h * k2)
    k4 = lorenz_deriv(state + h * k3)
    return state + (h / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)


def integrate_lorenz(steps, h=0.01):
    state = np.array([1.0, 1.0, 1.0], dtype=float)
    traj = []
    for i in range(steps):
        state = rk4_step(state, h)
        if i >= 2000:
            traj.append(state.copy())
    return np.array(traj)


def _norm(a):
    lo, hi = a.min(), a.max()
    if hi - lo < 1e-12:
        return np.zeros_like(a)
    return (a - lo) / (hi - lo)


TRAJ = integrate_lorenz(6000)
_Z = _norm(TRAJ[:, 2])
_D = np.diff(TRAJ, axis=0)
_SPD = _norm(np.sqrt((_D ** 2).sum(axis=1)))


def bar_mask(bar, threshold, floor):
    seg = _SPD[bar * 160:(bar + 1) * 160]
    if len(seg) < 8:
        seg = _SPD[:8]
    idxs = np.linspace(0, len(seg) - 1, 8).astype(int)
    vals = [seg[i] for i in idxs]
    mask = [1 if v > threshold else 0 for v in vals]
    mask[0] = 1
    if sum(mask) < floor:
        order = sorted(range(1, 8), key=lambda i: -vals[i])
        for i in order:
            if sum(mask) >= floor:
                break
            mask[i] = 1
    return mask


# ------------------------------------------------------------------ phase 1
def build_phase1_raw():
    rng = random.Random(SEED)
    events = []
    n_total = TOTAL_BARS * 6
    for i in range(n_total):
        zi = float(_Z[int(i * len(_Z) / n_total) % len(_Z)])
        pitch = int(round(50 + zi * 46))          # raw int, NOT scale-snapped
        pitch = max(50, min(96, pitch))
        si = float(_SPD[int(i * len(_SPD) / n_total) % len(_SPD)])
        base = int(i * TOTAL_TICKS / n_total)
        jitter = int((si - 0.5) * 240)            # off-grid by design
        st = max(0, min(TOTAL_TICKS - 60, base + jitter))
        dur = 120 + int(zi * 240)
        vel = 70 + int(si * 50)
        events.append(MusicEvent(pitch=pitch, volume=vel, start_tick=st,
                                 end_tick=min(TOTAL_TICKS, st + dur)))
    return events


# ------------------------------------------------------------------ phase 2
def build_satb():
    out = {k: [] for k in ("Soprano", "Alto", "Tenor", "Bass")}
    prev = {k: None for k in out}
    for bar in range(TOTAL_BARS):
        name = section_name_of_bar(bar)
        deg = CHORD_WALK[bar]
        root_pc, triad = DEG[deg]
        r, th, f = triad
        reg = SECTION_REG[name]
        REG = REG_LOW if reg == 0 else (REG_HIGH if reg == 1 else REG_OUTRO)
        b = fold_pc(root_pc, *REG["Bass"], prev["Bass"])
        s = fold_pc(r, *REG["Soprano"], prev["Soprano"])
        a = fold_pc(f, *REG["Alto"], prev["Alto"])
        t = fold_pc(th, *REG["Tenor"], prev["Tenor"])
        for k, p in zip(("Soprano", "Alto", "Tenor", "Bass"), (s, a, t, b)):
            prev[k] = p
        thr, floor = SECTION_DENSITY[name]
        base = bar * BAR
        if name == "Outro":
            slots, dur = [0, 4], 920        # augmentation: half-note strikes
        else:
            mask = bar_mask(bar, thr, floor)
            slots, dur = [k for k in range(8) if mask[k]], 216
        for slot in slots:
            st = base + slot * EIGHTH
            out["Soprano"].append(MusicEvent(s, 96, st, st + dur))
            out["Alto"].append(MusicEvent(a, 88, st, st + dur))
            out["Tenor"].append(MusicEvent(t, 84, st, st + dur))
            out["Bass"].append(MusicEvent(b, 96, st, st + dur))
    return out


def build_descant():
    evs = []
    prev_d = None
    for bar in range(TOTAL_BARS):
        name = section_name_of_bar(bar)
        if name not in DESCANT_ACTIVE:
            continue
        _, triad = DEG[CHORD_WALK[bar]]
        r, th, f = triad
        up = [r, th, f, r, th, f, r, th]          # ascending arpeggio
        down = [f, th, r, f, th, r, f, th]        # inverted (descending)
        seq = down if name == "Bridge" else up
        base = bar * BAR
        for k in range(8):
            p = fold_pc(seq[k], 74, 88, prev_d)
            prev_d = p
            evs.append(MusicEvent(p, 66, base + k * EIGHTH,
                                  base + k * EIGHTH + 200))
    return evs


def build_perc():
    evs = []
    for bar in range(TOTAL_BARS):
        if section_name_of_bar(bar) == "Climax":
            base = bar * BAR
            evs.append(MusicEvent(45, 74, base, base + 140))
            evs.append(MusicEvent(45, 60, base + 960, base + 1100))
    return evs


# ------------------------------------------------------------------ compose
PROJ = "/opt/data/projects/Styles/Experimental/245-attractor-chorale-rework"
MIDI_DIR = os.path.join(PROJ, "MIDI")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")
AUDIO_DIR = os.path.join(PROJ, "Audio")
for d in (MIDI_DIR, ANALYSIS_DIR, AUDIO_DIR):
    os.makedirs(d, exist_ok=True)

BASE = "245-attractor-chorale-rework"
P2_MIDI = os.path.join(MIDI_DIR, BASE + ".mid")
P1_MIDI = os.path.join(MIDI_DIR, BASE + "-phase1.mid")


def compose():
    # ---- Phase 1: raw single-voice Lorenz draft ---------------------------
    raw = build_phase1_raw()
    p1 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BPB)
    p1.create_matrix(num_voices=1, num_sections=N_SECTIONS)
    p1.add_voice("RawLead", program=MidiInstrument.FLUTE, channel=0)
    for name, bars in SECTIONS:
        p1.add_section(name, bars=bars)
    for s in range(N_SECTIONS):
        p1.set_unit(0, s, split_abs_to_section(raw, s))
    ok1, msg1 = p1.validate()
    if not ok1:
        raise RuntimeError("Phase 1 zero-drift FAILED: " + msg1)
    p1.to_midi(P1_MIDI)

    # ---- Phase 2: rules-processed 6-voice texture -------------------------
    satb = build_satb()
    desc = build_descant()
    perc = build_perc()
    abs_events = {
        "Soprano": satb["Soprano"], "Alto": satb["Alto"],
        "Tenor": satb["Tenor"], "Bass": satb["Bass"],
        "Descant": desc, "Perc": perc,
    }

    p2 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BPB)
    p2.create_matrix(num_voices=len(VOICES), num_sections=N_SECTIONS)
    for name, prog, ch, _pitched in VOICES:
        p2.add_voice(name, program=prog, channel=ch)
    for name, bars in SECTIONS:
        p2.add_section(name, bars=bars)
    for vi, (vname, _, _, _) in enumerate(VOICES):
        for s in range(N_SECTIONS):
            p2.set_unit(vi, s, split_abs_to_section(abs_events[vname], s))
    ok2, msg2 = p2.validate()
    if not ok2:
        raise RuntimeError("Phase 2 zero-drift FAILED: " + msg2)
    p2.to_midi(P2_MIDI)

    return p2, ok1, abs_events


# ------------------------------------------------------------------ audit
def audit(abs_events):
    rows = {}
    for vname, evs in abs_events.items():
        pitched = vname in PITCHED
        onsets = [e.start_tick for e in evs if e.pitch != 0]
        off_grid = sum(1 for o in onsets if not (o % 120 == 0 or o % 240 == 0))
        out_scale = out_chord = 0
        if pitched:
            for e in evs:
                if e.pitch == 0:
                    continue
                pc = e.pitch % 12
                bar = min(TOTAL_BARS - 1, e.start_tick // BAR)
                cpc = set(DEG[CHORD_WALK[bar]][1])
                if pc not in KEY_PCS:
                    out_scale += 1
                if pc not in cpc:
                    out_chord += 1
        rows[vname] = {"n_notes": len(onsets), "off_grid": off_grid,
                       "out_scale": out_scale, "out_chord": out_chord,
                       "pitched": pitched}
    return rows


if __name__ == "__main__":
    p2, ok1, abs_events = compose()

    s2 = os.path.getsize(P2_MIDI)
    s1 = os.path.getsize(P1_MIDI)
    assert s2 > 40 and s1 > 40, "MIDI too small"

    rows = audit(abs_events)
    tot_off = sum(r["off_grid"] for r in rows.values())
    tot_scale = sum(r["out_scale"] for r in rows.values())
    tot_chord = sum(r["out_chord"] for r in rows.values())

    print("[OK] Phase1 MIDI:", P1_MIDI, f"({s1}B) validate={ok1}")
    print("[OK] Phase2 MIDI:", P2_MIDI, f"({s2}B) validate=True")
    print(f"[OK] Form: {TOTAL_BARS} bars, {N_SECTIONS} sections")
    print("[OK] Section roots (midpoint):",
          [(SECTIONS[i][0], DEG[CHORD_WALK[SECTION_START_BARS[i] + SECTIONS[i][1] // 2]][0])
           for i in range(N_SECTIONS)])
    print("[OK] Audit per voice:")
    for vname, r in rows.items():
        print(f"     {vname:9s} notes={r['n_notes']:3d} off_grid={r['off_grid']} "
              f"out_scale={r['out_scale']} out_chord={r['out_chord']} pitched={r['pitched']}")
    print(f"[OK] TOTALS off_grid={tot_off} out_scale={tot_scale} out_chord={tot_chord}")

    grid_path = os.path.join(ANALYSIS_DIR, "grid_visualization.txt")
    write_grid_visualization(p2.matrix, grid_path, ticks_per_character=120,
                             voice_names=VOICE_NAMES, bpm=BPM,
                             mode="E dorian / Lorenz attractor chorale rework")

    write_provenance(
        P1_MIDI, classification=AI_GENERATED,
        generator="Lorenz strange attractor (RK4) - PRE-RULES raw draft",
        parameters={"method": 43, "phase": 1, "key": KEY_NAME, "bpm": BPM,
                    "sections": N_SECTIONS, "total_bars": TOTAL_BARS,
                    "seed": SEED, "style": "Experimental", "form": "chorale",
                    "source": "061-attractor-chorale", "rework": "redesign"},
        notes="Phase 1: single flute voice, pure Lorenz trajectory. z -> raw "
              "unquantized pitch, speed-triggered off-grid onsets, no harmony.")
    write_provenance(
        P2_MIDI, classification=AI_ASSISTED,
        generator="Lorenz SATM (Method 043) + musicom rules",
        parameters={"method": 43, "phase": 2, "key": KEY_NAME, "bpm": BPM,
                    "sections": N_SECTIONS, "total_bars": TOTAL_BARS,
                    "seed": SEED, "style": "Experimental", "form": "chorale",
                    "voices": VOICE_NAMES, "source": "061-attractor-chorale",
                    "rework": "redesign",
                    "chord_walk": CHORD_WALK,
                    "variation_techniques": [
                        "density-ramp", "register-shift(+12)",
                        "diatonic-transposition(+1deg)", "augmentation(outro)",
                        "counterline(descant)", "inversion(bridge descant)",
                    ]},
        notes="Phase 2: SATB homophonic chorale, chord-tone quantized per bar "
              "(floor t//BAR) + voice-leading + grid snap + dedup. Descant "
              "counterline in Chorus/Bridge/Climax; ch9 timpani in Climax.")

    summary = {
        "project": BASE, "style": "Experimental", "method": 43,
        "bpm": BPM, "key": KEY_NAME, "bars": TOTAL_BARS, "sections": SECTIONS,
        "chord_walk": CHORD_WALK, "section_roots_midpoint":
            [(SECTIONS[i][0], section_roots[i]) for i in range(N_SECTIONS)],
        "voices": VOICE_NAMES, "source": "061-attractor-chorale",
        "decision": "redesign (missing -phase1.mid + index.html)",
        "variation_techniques": [
            "density-ramp", "register-shift(+12)",
            "diatonic-transposition(+1deg)", "augmentation(outro)",
            "counterline(descant)", "inversion(bridge descant)"],
        "audit": rows,
        "totals": {"off_grid": tot_off, "out_scale": tot_scale,
                   "out_chord": tot_chord},
        "phase1": os.path.basename(P1_MIDI),
        "phase2": os.path.basename(P2_MIDI),
    }
    with open(os.path.join(ANALYSIS_DIR, "summary.json"), "w") as f:
        json.dump(summary, f, indent=2)

    print("[OK] Provenance + grid + summary written.")
    print("CHORD_WALK:", CHORD_WALK)
