# -*- coding: utf-8 -*-
"""311-knight-tour-soul -- Soul ballad via Knight's Tour Composition (method 126).

Nightly composition job (2026-11-18). Selection: style=Soul, method=126
Knight's Tour Composition (Rules-Based, concrete layer), form=verse-chorus
(pick_form("soul") -> Intro/Verse/Chorus/Verse2/Chorus2/Outro,
bars [4,8,8,8,8,4] = 40 bars).

MUSICAL DNA
  - Key F major (ionian) = pc {5,7,9,0,2,4,6}; tonic F.
  - 96 BPM, 4/4, 480 TPB, BAR=1920, 8th=240, 16th=120.
  - Method 126 Knight's Tour: a Hamiltonian path on the knight graph over an
    m x n board (rows = pitch scale degrees, columns = time-slot classes).
    Each cell visited exactly once; each of the 8 rows (scale degrees) visited
    exactly n times (2D aggregate). Knight move |dr|*|dc| = 2 anti-correlates
    melodic leap (|dr|=2) with short duration (|dc|=1) and step (|dr|=1) with
    long duration (|dc|=2). Warnsdorff's rule + backtracking solves in ~O(N).
  - The board TRANSPOSE of a tour is a valid tour = the dual voice (invertible
    counterpoint): the Vox backing line maps the tour's COLUMN coordinate into
    pitch space (time-slot class -> pitch), a distinct melody used in the
    chorus sections.
  - 5-voice Soul texture: Tenor Sax lead (tour melody), Rhodes electric-piano
    comp (voice-led triads), Electric Bass (root/fifth), Choir-Aahs backing
    vox (transpose-tour counter in chorus / sustained pad elsewhere), Drum Kit
    backbeat (kick 1&3, snare 2&4, 8th hats).

TWO-PHASE
  Phase 1 (raw): single-voice knight-tour stream, unquantized float pitch
    (scale-degree row + jitter) + off-grid onsets; own composer + validate().
  Phase 2 (rules): tiered quantize (strong -> chord tone, weak -> scale tone
    via ScaleQuantizer.tiered_quantize), 8th-grid snap, voice-leading on the
    comp triads, register enforcement, 5-voice Soul texture.
  Dual-version: export_dual -> -perfect.mid (grid-locked) + -humanized.mid.
"""
import json
import os
import sys
import hashlib

import numpy as np

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer
from workflows.humanize import export_dual
from workflows.provenance import write_provenance, AI_ASSISTED
from visualization.grid import write_grid_visualization
from rules.progression import Scale7ChordDegree
from rules.voice_leading import VoiceLeadingRules
from sound.synthesis.scale_quantizer import ScaleQuantizer, STRONG_GRID, classify_weight

_INSTR_DIR = "/opt/data/repos/musicom/projects/Instruments"
if _INSTR_DIR not in sys.path:
    sys.path.insert(0, _INSTR_DIR)
from instrument_registry import (  # noqa: E402
    TENOR_SAX, RHODES, ELECTRIC_BASS, CHOIR, DRUM_KIT)

# ---------------------------------------------------------------------------
# Project layout / identity
# ---------------------------------------------------------------------------
GENRE = "Soul"
STYLE = "soul"
PROJECT = "311-knight-tour-soul"
BASE = os.path.join("/opt/data/projects/Styles", GENRE, PROJECT)
MIDI_DIR = os.path.join(BASE, "MIDI")
AUDIO_DIR = os.path.join(BASE, "Audio")
ANALYSIS_DIR = os.path.join(BASE, "Analysis")
for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
    os.makedirs(d, exist_ok=True)

BPM = 96
TPB = 480
BPB = 4
BAR = TPB * BPB                     # 1920
GRID = 240                          # 8th (snap target)
EIGHTH = 240
SIXTEENTH = 120
QUARTER = 480
TOTAL_BARS = 40
TOTAL_TICKS = TOTAL_BARS * BAR

KEY_NAME = "F major"
TONIC_PC = 5                        # F
INTERVALS = [0, 2, 4, 5, 7, 9, 11]  # ionian/major step pattern
KEY_PCS = sorted({(TONIC_PC + iv) % 12 for iv in INTERVALS})  # {0,2,4,5,7,9,11}
TONIC_BASE = 53                     # F3 (triad/pad reference)

# Lead pitch board: 8 rows = one octave of F major, F4..F5.
LEAD_BASE = 65                      # F4
LEAD_OFFSETS = [0, 2, 4, 5, 7, 9, 11, 12]


def lead_pitch(row):
    return LEAD_BASE + LEAD_OFFSETS[row]


# 0-based degree -> triad quality intervals (F major diatonic)
# 0=F, 1=Gm, 2=Am, 3=Bb, 4=C, 5=Dm, 6=Edim
QUALITY = {0: (0, 4, 7), 1: (0, 3, 7), 2: (0, 3, 7), 3: (0, 4, 7),
           4: (0, 4, 7), 5: (0, 3, 7), 6: (0, 3, 6)}
DEGREE_NAMES = {0: "F", 1: "Gm", 2: "Am", 3: "Bb",
                4: "C", 5: "Dm", 6: "Edim"}

# deterministic seeds
hz_seed = int(hashlib.md5(
    (STYLE + KEY_NAME + str(BPM) + str(TOTAL_BARS) + PROJECT).encode()
).hexdigest()[:8], 16) % 100000
raw_seed = 20261118

# ---------------------------------------------------------------------------
# Form (verse-chorus: Intro4 Verse8 Chorus8 Verse2 8 Chorus2 8 Outro4 = 40)
# ---------------------------------------------------------------------------
SECTIONS = [
    ("Intro",   4, [0, 3, 0, 4]),                     # F Bb F C
    ("Verse",   8, [0, 5, 3, 4, 0, 5, 1, 4]),         # F Dm Bb C F Dm Gm C
    ("Chorus",  8, [0, 5, 3, 4, 0, 3, 4, 0]),         # F Dm Bb C F Bb C F
    ("Verse2",  8, [0, 5, 3, 4, 0, 5, 1, 4]),
    ("Chorus2", 8, [0, 5, 3, 4, 0, 3, 4, 0]),
    ("Outro",   4, [0, 3, 4, 0]),                     # F Bb C F
]
SECTION_START = {}
_acc = 0
for name, bars, prog in SECTIONS:
    SECTION_START[name] = _acc
    _acc += bars
assert _acc == TOTAL_BARS
SECTION_BARS = {name: bars for name, bars, prog in SECTIONS}

BAR_DEGREES = []
for name, bars, prog in SECTIONS:
    BAR_DEGREES.extend(prog)
assert len(BAR_DEGREES) == TOTAL_BARS

BAR_TO_SECTION = {}
for name, bars, prog in SECTIONS:
    s0 = SECTION_START[name]
    for b in range(bars):
        BAR_TO_SECTION[s0 + b] = name

VOICES = ["Lead", "Rhodes", "Bass", "Vox", "Drums"]
VOICE_PROGRAMS = [TENOR_SAX.midi_program, RHODES.midi_program,
                  ELECTRIC_BASS.midi_program, CHOIR.midi_program, 0]
VOICE_CHANNELS = [0, 1, 2, 3, 9]

LEAD_LO, LEAD_HI = 60, 81      # tenor sax
RHODES_LO, RHODES_HI = 48, 84
BASS_LO, BASS_HI = 33, 52
VOX_LO, VOX_HI = 48, 76

# Knight-tour config per section (R rows=8 scale degrees, C cols=time slots).
TOUR_CFG = {
    "Intro":   {"R": 8, "C": 4, "start": (0, 0), "seed": 1, "invert": False},
    "Verse":   {"R": 8, "C": 8, "start": (0, 0), "seed": 2, "invert": False},
    "Chorus":  {"R": 8, "C": 8, "start": (3, 2), "seed": 3, "invert": False},
    "Verse2":  {"R": 8, "C": 8, "start": (0, 0), "seed": 4, "invert": True},
    "Chorus2": {"R": 8, "C": 8, "start": (3, 2), "seed": 5, "invert": False},
    "Outro":   {"R": 8, "C": 4, "start": (0, 0), "seed": 6, "invert": True},
}
COUNTER_SECTIONS = ("Chorus", "Chorus2")


# ---------------------------------------------------------------------------
# Method 126: Knight's Tour (Warnsdorff + backtracking, seeded)
# ---------------------------------------------------------------------------
_KNIGHT_DELTAS = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                  (1, -2), (1, 2), (2, -1), (2, 1)]


def find_tour(R, C, start, rng):
    """Hamiltonian knight path visiting all R*C cells exactly once."""
    total = R * C
    visited = [[False] * C for _ in range(R)]
    path = []

    def neighbors(r, c):
        out = []
        for dr, dc in _KNIGHT_DELTAS:
            nr, nc = r + dr, c + dc
            if 0 <= nr < R and 0 <= nc < C and not visited[nr][nc]:
                out.append((nr, nc))
        return out

    def warnsdorff_order(cands):
        # fewest onward moves first (Warnsdorff), tie-break seeded random (Pohl)
        return sorted(cands, key=lambda x: (len(neighbors(*x)), rng.random()))

    def dfs(r, c, step):
        visited[r][c] = True
        path.append((r, c))
        if step == total - 1:
            return True
        for nr, nc in warnsdorff_order(neighbors(r, c)):
            if dfs(nr, nc, step + 1):
                return True
        visited[r][c] = False
        path.pop()
        return False

    ok = dfs(start[0], start[1], 0)
    assert ok, f"no knight tour on {R}x{C} from {start}"
    assert len(path) == total
    return path


def simulate_knight(rng):
    """Walk each section's knight tour -> raw (row, col, pitch, onset) records."""
    records = []
    for name, bars, prog in SECTIONS:
        cfg = TOUR_CFG[name]
        trng = np.random.default_rng(cfg["seed"])
        tour = find_tour(cfg["R"], cfg["C"], cfg["start"], trng)
        s0 = SECTION_START[name]
        for k, (r, c) in enumerate(tour):
            row = (cfg["R"] - 1 - r) if cfg["invert"] else r
            base_tick = s0 * BAR + k * EIGHTH
            jit = int(rng.integers(-25, 26))
            tick_abs = max(0, min(TOTAL_TICKS - 30, base_tick + jit))
            p = float(lead_pitch(row)) + float(rng.normal(0.0, 0.35))
            # knight signature: |dr|=2 (leap) -> |dc|=1 (short); |dr|=1 -> long
            if k > 0:
                dr = abs(row - _prev_row(name))
                dc = abs(c - _prev_col(name))
            else:
                dr, dc = 0, 0
            if dc == 2:
                dur = EIGHTH + SIXTEENTH      # step -> long
            elif dc == 1:
                dur = EIGHTH - SIXTEENTH      # leap -> short
            else:
                dur = EIGHTH
            vel = int(rng.integers(72, 100))
            records.append({"tick_abs": tick_abs, "pitch": p, "dur": dur,
                            "vel": vel, "bar": s0 + k // 8,
                            "degree": prog[min(k // 8, bars - 1)],
                            "row": row, "col": c})
            _set_prev(name, row, c)
    return records


_PREV = {}


def _prev_row(name):
    return _PREV.get(name, (0, 0))[0]


def _prev_col(name):
    return _PREV.get(name, (0, 0))[1]


def _set_prev(name, row, col):
    _PREV[name] = (row, col)


# ---------------------------------------------------------------------------
# Diatonic helpers
# ---------------------------------------------------------------------------
def diatonic(deg_index, base=TONIC_BASE):
    return Scale7ChordDegree.get_diatonic_note(base, INTERVALS, deg_index)


def chord_pcs(d):
    root_pc = (TONIC_PC + INTERVALS[d]) % 12
    return sorted({(root_pc + iv) % 12 for iv in QUALITY[d]})


def chord_tones(d, lo=34, hi=91):
    root_pc = (TONIC_PC + INTERVALS[d]) % 12
    out = set()
    for octv in range(0, 9):
        for iv in QUALITY[d]:
            n = root_pc + 12 * octv + iv
            if lo <= n <= hi:
                out.add(n)
    return sorted(out)


def triad(d, base=TONIC_BASE):
    return sorted([diatonic(d, base), diatonic(d + 2, base),
                   diatonic(d + 4, base)])


# ---------------------------------------------------------------------------
# Phase 1 raw draft (single voice, unquantized)
# ---------------------------------------------------------------------------
def build_phase1(records):
    p1 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BPB)
    p1.create_matrix(num_voices=1, num_sections=len(SECTIONS))
    p1.add_voice("RawKnight", program=TENOR_SAX.midi_program, channel=0)
    for name, bars, prog in SECTIONS:
        p1.add_section(name, bars=bars)

    per_section = {name: [] for name, bars, prog in SECTIONS}
    for r in records:
        sec = BAR_TO_SECTION[r["bar"]]
        per_section[sec].append(r)

    for name, bars, prog in SECTIONS:
        s_ticks = bars * BAR
        s0 = SECTION_START[name] * BAR
        cell = []
        for r in per_section[name]:
            st = r["tick_abs"] - s0
            if st < 0:
                st = 0
            if st >= s_ticks:
                continue
            en = min(s_ticks, st + r["dur"])
            if en <= st:
                en = st + 30
            cell.append(MusicEvent(pitch=int(round(r["pitch"])), volume=r["vel"],
                                   start_tick=st, end_tick=en))
        cell.sort(key=lambda e: (e.start_tick, e.end_tick))
        if not cell or cell[-1].end_tick < s_ticks:
            last_end = cell[-1].end_tick if cell else 0
            cell.append(MusicEvent(pitch=0, volume=0, start_tick=last_end,
                                   end_tick=s_ticks))
        p1.fill_voice_section("RawKnight", name, MusicUnit(events=cell))
    ok, msg = p1.validate()
    if not ok:
        raise RuntimeError(f"phase1 validate failed: {msg}")
    return p1


# ---------------------------------------------------------------------------
# Phase 2 helpers
# ---------------------------------------------------------------------------
def snap_grid(t, grid=GRID):
    return int(round(t / float(grid)) * grid)


def to_register(pitch, lo, hi):
    p = int(pitch)
    while p < lo:
        p += 12
    while p > hi:
        p -= 12
    return p


def weight_of(onset):
    return classify_weight(onset, STRONG_GRID["4/4"], bar_ticks=BAR)


def correct_voice_leading(triads):
    vl = VoiceLeadingRules(style="classical")
    corrected = [sorted(triads[0])]
    fixed = 0
    for i in range(1, len(triads)):
        prev = corrected[-1]
        base = sorted(triads[i])
        cands = [base]
        for rot in range(1, len(base)):
            cands.append(vl._rotate_chord(base, rot))
        cands = cands + [[p + 12 for p in c] for c in cands]
        best, best_score = cands[0], None
        for cand in cands:
            n_viol = len(vl.check_parallel_motion(prev, cand)) + \
                     len(vl.check_hidden_fifths(prev, cand))
            dist = vl.calculate_voice_leading_distance(prev, cand)
            score = (n_viol, dist)
            if best_score is None or score < best_score:
                best_score, best = score, cand
        if best_score[0] > 0:
            fixed += 1
        corrected.append(sorted(best))
    return corrected, fixed


def _dedup_sort(ev):
    best = {}
    for e in ev:
        key = (e.start_tick, e.pitch)
        if key not in best or (e.end_tick - e.start_tick) > \
                (best[key].end_tick - best[key].start_tick):
            best[key] = e
    return sorted(best.values(), key=lambda e: (e.start_tick, e.pitch))


def build_lead_section(name, records, sq):
    nbars = SECTION_BARS[name]
    s_ticks = nbars * BAR
    s0 = SECTION_START[name] * BAR
    ev = []
    for r in records:
        if not (s0 <= r["tick_abs"] < s0 + s_ticks):
            continue
        st_glob = snap_grid(r["tick_abs"], GRID)
        st = st_glob - s0
        if st < 0 or st >= s_ticks - 30:
            continue
        bar = st_glob // BAR
        d = BAR_DEGREES[bar]
        weight = weight_of(st)
        ct = chord_tones(d, LEAD_LO, LEAD_HI)
        pitch = sq.tiered_quantize(r["pitch"], weight=weight, chord_tones=ct)
        pitch = max(LEAD_LO, min(LEAD_HI, pitch))
        en = min(s_ticks - 20, st + GRID - 20)
        ev.append(MusicEvent(pitch=pitch, volume=r["vel"], start_tick=st,
                             end_tick=en))
    return _dedup_sort(ev)


def build_vox_counter_section(name, records, sq):
    """Board-transpose tour (col -> pitch) = the dual voice (counterpoint)."""
    nbars = SECTION_BARS[name]
    s_ticks = nbars * BAR
    s0 = SECTION_START[name] * BAR
    ev = []
    for r in records:
        if not (s0 <= r["tick_abs"] < s0 + s_ticks):
            continue
        st_glob = snap_grid(r["tick_abs"], GRID)
        st = st_glob - s0
        if st < 0 or st >= s_ticks - 30:
            continue
        bar = st_glob // BAR
        d = BAR_DEGREES[bar]
        weight = weight_of(st)
        ct = chord_tones(d, VOX_LO, VOX_HI)
        raw = float(lead_pitch(r["col"]) - 12)   # time-slot class -> pitch, -oct
        pitch = sq.tiered_quantize(raw, weight=weight, chord_tones=ct)
        pitch = max(VOX_LO, min(VOX_HI, pitch))
        en = min(s_ticks - 20, st + GRID - 20)
        ev.append(MusicEvent(pitch=pitch, volume=60, start_tick=st, end_tick=en))
    return _dedup_sort(ev)


def build_rhodes_section(name, corr_triads):
    nbars = SECTION_BARS[name]
    s_ticks = nbars * BAR
    ev = []
    for bi in range(nbars):
        bar = SECTION_START[name] + bi
        r, th, f = corr_triads[bar]
        bs = bi * BAR
        end = min(bs + BAR - 40, s_ticks - 40)
        for p in (r, th, f):
            p = to_register(p, RHODES_LO, RHODES_HI)
            ev.append(MusicEvent(pitch=p, volume=64, start_tick=bs, end_tick=end))
    return ev


def build_vox_pad_section(name, corr_triads):
    nbars = SECTION_BARS[name]
    s_ticks = nbars * BAR
    ev = []
    for bi in range(nbars):
        bar = SECTION_START[name] + bi
        r, th, f = corr_triads[bar]
        bs = bi * BAR
        end = min(bs + BAR - 40, s_ticks - 40)
        root = to_register(r, VOX_LO, VOX_HI)
        fifth = to_register(f, VOX_LO, VOX_HI)
        ev.append(MusicEvent(pitch=root, volume=48, start_tick=bs, end_tick=end))
        ev.append(MusicEvent(pitch=fifth, volume=42, start_tick=bs, end_tick=end))
    return ev


def build_bass_section(name, corr_triads):
    nbars = SECTION_BARS[name]
    s_ticks = nbars * BAR
    ev = []
    for bi in range(nbars):
        bar = SECTION_START[name] + bi
        r, th, f = corr_triads[bar]
        bs = bi * BAR
        root = to_register(r - 12, BASS_LO, BASS_HI)
        fifth = to_register(f - 12, BASS_LO, BASS_HI)
        ev.append(MusicEvent(pitch=root, volume=82,
                             start_tick=bs, end_tick=bs + BAR - 60))
        ev.append(MusicEvent(pitch=fifth, volume=66,
                             start_tick=bs + 960, end_tick=bs + 960 + 400))
    return ev


def build_drums_section(name):
    nbars = SECTION_BARS[name]
    s_ticks = nbars * BAR
    ev = []
    for bi in range(nbars):
        bs = bi * BAR
        ev.append(MusicEvent(pitch=36, volume=100, start_tick=bs, end_tick=bs + 70))
        ev.append(MusicEvent(pitch=36, volume=88, start_tick=bs + 960,
                             end_tick=bs + 1030))
        ev.append(MusicEvent(pitch=38, volume=96, start_tick=bs + 480,
                             end_tick=bs + 550))
        ev.append(MusicEvent(pitch=38, volume=96, start_tick=bs + 1440,
                             end_tick=bs + 1510))
        for off in range(0, 1920, 240):
            hat = 46 if (off // 240) % 4 == 3 else 42
            ev.append(MusicEvent(pitch=hat, volume=68, start_tick=bs + off,
                                 end_tick=bs + off + 40))
    ev.sort(key=lambda e: (e.start_tick, e.pitch))
    return ev


def seal(ev, sec_ticks):
    ev = sorted(ev, key=lambda e: (e.start_tick, e.pitch))
    out = []
    for e in ev:
        if e.start_tick < 0 or e.start_tick >= sec_ticks:
            continue
        en = min(sec_ticks, e.end_tick)
        if en <= e.start_tick:
            en = min(sec_ticks, e.start_tick + 30)
        out.append(MusicEvent(pitch=e.pitch, volume=e.volume,
                              start_tick=e.start_tick, end_tick=en))
    if not out or out[-1].end_tick < sec_ticks:
        last_end = out[-1].end_tick if out else 0
        out.append(MusicEvent(pitch=0, volume=0, start_tick=last_end,
                              end_tick=sec_ticks))
    return MusicUnit(events=out)


def build_phase2(records, corr_triads, sq):
    comp = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BPB)
    comp.create_matrix(num_voices=len(VOICES), num_sections=len(SECTIONS))
    for name, prog, ch in zip(VOICES, VOICE_PROGRAMS, VOICE_CHANNELS):
        comp.add_voice(name, program=prog, channel=ch)
    for name, bars, prog in SECTIONS:
        comp.add_section(name, bars=bars)

    for name, bars, prog in SECTIONS:
        s_ticks = bars * BAR
        comp.fill_voice_section("Lead", name,
                                seal(build_lead_section(name, records, sq), s_ticks))
        comp.fill_voice_section("Rhodes", name,
                                seal(build_rhodes_section(name, corr_triads), s_ticks))
        comp.fill_voice_section("Bass", name,
                                seal(build_bass_section(name, corr_triads), s_ticks))
        if name in COUNTER_SECTIONS:
            vox = build_vox_counter_section(name, records, sq)
        else:
            vox = build_vox_pad_section(name, corr_triads)
        comp.fill_voice_section("Vox", name, seal(vox, s_ticks))
        comp.fill_voice_section("Drums", name,
                                seal(build_drums_section(name), s_ticks))
    ok, msg = comp.validate()
    if not ok:
        raise RuntimeError(f"phase2 validate failed: {msg}")
    return comp


def count_offgrid(events, grid=SIXTEENTH):
    off = sum(1 for e in events if e.pitch > 0 and e.start_tick % grid != 0)
    tot = sum(1 for e in events if e.pitch > 0)
    return off, tot


def main():
    rng = np.random.default_rng(raw_seed)
    records = simulate_knight(rng)
    print("KNIGHT notes =", len(records))
    for name, bars, prog in SECTIONS:
        n = sum(1 for r in records if BAR_TO_SECTION[r["bar"]] == name)
        print(f"  {name}: {n} raw notes")

    # ---- Phase 1 raw draft -------------------------------------------------
    phase1 = build_phase1(records)
    phase1_mid = os.path.join(MIDI_DIR, PROJECT + "-phase1.mid")
    phase1.to_midi(phase1_mid)
    write_provenance(
        phase1_mid, AI_ASSISTED,
        "musicom.knight_tour_phase1",
        parameters={"bpm": BPM, "bars": TOTAL_BARS, "seed": raw_seed,
                    "phase": 1, "quantized": False, "key": KEY_NAME,
                    "form": "verse-chorus", "style": STYLE,
                    "method": "126 Knight's Tour Composition (KTC)",
                    "layer": "concrete", "paradigm": "Rules-Based",
                    "tour_config": TOUR_CFG,
                    "notes": len(records),
                    "rules_applied": "NONE (pre-rules)"},
        notes="Raw knight's-tour draft: single tenor-sax voice, unquantized "
              "float pitch (scale-degree row + jitter) + off-grid onsets, 40 "
              "bars, pre-rules. Method 126 (concrete).")
    write_grid_visualization(phase1.matrix,
                             os.path.join(ANALYSIS_DIR,
                                          "grid_visualization_phase1.txt"),
                             voice_names=["RawKnight"], bpm=BPM)
    print("PHASE1_OK", "raw_notes=", len(records))

    # ---- Phase 2 rules + texture -------------------------------------------
    bar_triads = [triad(d, base=TONIC_BASE) for d in BAR_DEGREES]
    vl = VoiceLeadingRules(style="classical")
    opt_triads = vl.optimize_voice_leading(bar_triads)
    corr_triads, fixed = correct_voice_leading(opt_triads)
    print(f"[voicing] corrected {fixed} chord(s)")

    sq = ScaleQuantizer(root=TONIC_BASE, scale="major")
    phase2 = build_phase2(records, corr_triads, sq)

    # grid audit on perfect layer (pre-humanization)
    all_pitched = []
    for r in range(phase2.matrix.num_rows):
        for c in range(phase2.matrix.num_cols):
            cell = phase2.matrix.get_unit((r, c))
            if cell is None:
                continue
            for e in cell.events:
                if e.pitch > 0:
                    all_pitched.append(e)
    off, tot = count_offgrid(all_pitched)
    print(f"[grid] perfect-layer off-grid (16th): {off}/{tot}")
    assert off == 0, f"perfect layer has {off} off-grid onsets"

    # ---- dual-version export -----------------------------------------------
    hz_instruments = {
        "Lead": TENOR_SAX.humanize_dna,
        "Rhodes": RHODES.humanize_dna,
        "Bass": ELECTRIC_BASS.humanize_dna,
        "Vox": CHOIR.humanize_dna,
        "Drums": DRUM_KIT.humanize_dna,
    }
    perfect_path = os.path.join(MIDI_DIR, PROJECT + "-perfect.mid")
    humanized_path = os.path.join(MIDI_DIR, PROJECT + "-humanized.mid")
    hz = export_dual(phase2, perfect_path, humanized_path,
                     style=STYLE, seed=hz_seed, bpm=BPM, instruments=hz_instruments)

    # ---- provenance sidecars ----------------------------------------------
    prov = {
        "bpm": BPM, "key": "F", "mode": "major", "style": STYLE,
        "form": "verse-chorus", "bars": TOTAL_BARS,
        "sections": [s[0] for s in SECTIONS],
        "section_bars": {s[0]: s[1] for s in SECTIONS},
        "bar_degrees": BAR_DEGREES,
        "degree_names": {str(k): v for k, v in DEGREE_NAMES.items()},
        "method": "126 Knight's Tour Composition (KTC)",
        "layer": "concrete", "paradigm": "Rules-Based",
        "tour_config": {k: {"R": v["R"], "C": v["C"], "start": list(v["start"]),
                            "seed": v["seed"], "invert": v["invert"]}
                        for k, v in TOUR_CFG.items()},
        "counter_sections": list(COUNTER_SECTIONS),
        "voices": [[v, p, ch] for v, p, ch in
                   zip(VOICES, VOICE_PROGRAMS, VOICE_CHANNELS)],
        "voice_leading_corrections": fixed,
        "humanize_seed": hz_seed, "raw_seed": raw_seed,
        "humanize_profiles": {k: v["profile"] for k, v in hz.items()},
    }
    write_provenance(
        perfect_path, AI_ASSISTED,
        "musicom two-phase (phase=2 rules: tiered chord-tone quantization + "
        "8th grid snap + dedup + voice-leading + 5-voice Soul texture) "
        "(method 126 Knight's Tour)",
        sources=[phase1_mid],
        parameters=dict(prov, phase=2, version="perfect", off_grid=0),
        notes="Grid-locked perfect layer (verse-chorus, 40 bars). "
              "Method 126 Knight's Tour (concrete).")
    write_provenance(
        humanized_path, AI_ASSISTED,
        "musicom two-phase (phase=2 + humanization) (method 126 Knight's Tour)",
        sources=[perfect_path],
        parameters=dict(prov, phase=2, version="humanized",
                        humanize_seed=hz_seed,
                        humanize_stats={k: {kk: (float(vv) if isinstance(vv, float) else vv)
                                            for kk, vv in v.items() if kk != "profile"}
                                        for k, v in hz.items()}),
        notes="Humanized layer (style soul + per-instrument DNA).")

    # ---- grid visualization ------------------------------------------------
    write_grid_visualization(phase2.matrix,
                             os.path.join(ANALYSIS_DIR, "grid_visualization.txt"),
                             voice_names=VOICES, bpm=BPM)

    # ---- size asserts ------------------------------------------------------
    for p in (phase1_mid, perfect_path, humanized_path):
        assert os.path.getsize(p) > 40, f"empty/corrupt: {p}"

    summary = {
        "style": STYLE, "genre": GENRE,
        "method": "126 Knight's Tour Composition (KTC)",
        "layer": "concrete", "paradigm": "Rules-Based",
        "form": "verse-chorus", "key": KEY_NAME, "bpm": BPM,
        "bars": TOTAL_BARS, "sections": [s[0] for s in SECTIONS],
        "section_bars": [s[1] for s in SECTIONS],
        "tour_config": TOUR_CFG,
        "counter_sections": list(COUNTER_SECTIONS),
        "raw_notes": len(records),
        "voice_leading_corrections": fixed,
        "phase1_path": phase1_mid, "perfect_path": perfect_path,
        "humanized_path": humanized_path,
        "hz_seed": hz_seed,
        "hz": {k: {kk: vv for kk, vv in v.items() if kk != "profile"}
               for k, v in hz.items()},
        "progression": {s[0]: [DEGREE_NAMES[d] for d in s[2]] for s in SECTIONS},
    }
    with open(os.path.join(ANALYSIS_DIR, "compose_summary.json"), "w") as f:
        json.dump(summary, f, indent=2, default=str)
    print("COMPOSE_OK")
    print(json.dumps(summary, indent=2, default=str))


if __name__ == "__main__":
    main()
