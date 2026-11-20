# -*- coding: utf-8 -*-
"""314 - Abelian Sandpile Suite (Method 036 ASAR, two-phase architecture).

Nightly REWORK job (2026-11-20). Source identity preserved from
277-abelian-sandpile-avalanche (D minor, 88 BPM, Method 036 abelian sandpile,
5-voice Marimba/Celesta/Piano/Strings/DoubleBass). Redesign (audit standard 6:
missing root provenance.json + index.html) + extension (24 -> 32 bars,
6 -> 8 sections) + 6 variation techniques.

Two-phase architecture:
  Phase 1 (raw): Bak-Tang-Wiesenfeld abelian sandpile on a 14x256 lattice
    (14 pitch rows = D3..C5; 256 time columns = one eighth each -> 32 bars).
    Per-section variation transforms applied to the raw (row, col) topple
    stream BEFORE decode: transposition (+4 diatonic), inversion (diatonic
    mirror), retrograde (section time-reversal), augmentation (duration
    doubling + thinning). Raw: float pitch + chromatic jitter, off-grid
    onsets, single voice, no harmony -> own composer + validate() gate.

  Phase 2 (rules): STRICT chord discipline (every note snaps to its own bar's
    chord tone -> scale AND chord violation counts == 0), 16th grid snap,
    dedup, voice-leading (parallel 5th/octave break), 5-voice texture.
    Dual-version contract: export_dual -> -perfect.mid + -humanized.mid.
"""
import json
import os
import hashlib
import random
import sys

import numpy as np

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer
from workflows.humanize import export_dual
from workflows.provenance import write_provenance, AI_ASSISTED
from visualization.grid import write_grid_visualization
from rules.progression import Scale7ChordDegree

INSTR_DIR = "/opt/data/repos/musicom/projects/Instruments"
if INSTR_DIR not in sys.path:
    sys.path.insert(0, INSTR_DIR)
from instrument_registry import (MARIMBA, CELESTA, PIANO,  # noqa: E402
                                 STRING_ENSEMBLE, DOUBLE_BASS)

# ---------------------------------------------------------------------------
# Project layout / identity (preserved from source)
# ---------------------------------------------------------------------------
GENRE = "Experimental"
STYLE = "experimental"
PROJECT = "314-abelian-sandpile-suite"
SOURCE = "/opt/data/projects/Styles/Experimental/277-abelian-sandpile-avalanche"
BASE = os.path.join("/opt/data/projects/Styles", GENRE, PROJECT)
MIDI_DIR = os.path.join(BASE, "MIDI")
AUDIO_DIR = os.path.join(BASE, "Audio")
ANALYSIS_DIR = os.path.join(BASE, "Analysis")
for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
    os.makedirs(d, exist_ok=True)

BPM = 88
TPB = 480
BEATS_PER_BAR = 4
BAR = TPB * BEATS_PER_BAR                 # 1920
GRID = 120                                # 16th note (8th = 240)
EIGHTH = 240
TOTAL_BARS = 32
TOTAL_TICKS = TOTAL_BARS * BAR            # 61440

KEY_NAME = "D minor (aeolian)"
TONIC_PC = 2                              # D
KEY_PCS = {2, 4, 5, 7, 9, 10, 0}          # D E F G A Bb C
INTERVALS = [0, 2, 3, 5, 7, 8, 10]        # natural-minor offsets from D
TONIC_BASE = 50                           # D3

# 1-based degree -> triad quality intervals (D minor diatonic)
QUALITY = {1: (0, 3, 7), 2: (0, 3, 6), 3: (0, 4, 7), 4: (0, 3, 7),
           5: (0, 3, 7), 6: (0, 4, 7), 7: (0, 4, 7)}
DEGREE_NAMES = {1: "Dm", 2: "Edim", 3: "F", 4: "Gm", 5: "Am", 6: "Bb", 7: "C"}

# deterministic seeds
hz_seed = int(hashlib.md5(PROJECT.encode()).hexdigest()[:8], 16) % 100000
raw_seed = 20261120                        # the nightly selection seed
RNG = random.Random(raw_seed)              # phase-1 jitter / phase-2 post-process
NPRNG = np.random.default_rng(raw_seed)    # phase-1 generative drive

# ---------------------------------------------------------------------------
# Form: through-composed S1..S8 (4 bars each = 32 bars).
# (name, bars, progression [1-based degrees], drop_center, grains/col, variation)
# variation techniques: original | transpose(+4 diatonic) | invert(diatonic
# mirror) | retrograde(section time-reversal) | augment(dur doubling + thin)
# ---------------------------------------------------------------------------
SECTIONS = [
    ("S1", 4, [1, 3, 6, 7], 2, 3, "original"),    # i  III VI  VII  (sparse low)
    ("S2", 4, [1, 4, 1, 5], 4, 5, "original"),    # i  iv  i   v
    ("S3", 4, [6, 7, 1, 5], 6, 7, "original"),    # VI VII i   v
    ("S4", 4, [4, 1, 7, 6], 9, 11, "transpose"),  # iv i  VII VI  (peak, +4th)
    ("S5", 4, [1, 6, 4, 5], 7, 7, "invert"),      # i  VI iv  v   (mirror)
    ("S6", 4, [3, 7, 1, 6], 8, 9, "original"),    # III VII i VI  (density)
    ("S7", 4, [1, 3, 6, 7], 4, 5, "retrograde"),  # i  III VI VII (recap reversed)
    ("S8", 4, [1, 4, 7, 1], 2, 3, "augment"),     # i  iv VII i   (coda half-time)
]
SECTION_START = {}
_acc = 0
for name, bars, prog, dc, g, var in SECTIONS:
    SECTION_START[name] = _acc
    _acc += bars
assert _acc == TOTAL_BARS

BAR_DEGREES = []
for name, bars, prog, dc, g, var in SECTIONS:
    BAR_DEGREES.extend(prog)
assert len(BAR_DEGREES) == TOTAL_BARS

# 1-bar section spec for the humanized composer: the humanizer clamps its
# boundary at SECTION span. With 4-bar sections, timing jitter can move a note
# across an internal BAR line and re-attribute it to the wrong bar's chord.
# Using 1-bar sections makes the humanizer's boundary-clamp == bar boundary,
# so no note ever leaves its bar -> per-bar chord violations stay 0.
BAR_SECTIONS = []
for name, bars, prog, dc, g, var in SECTIONS:
    for b in range(bars):
        BAR_SECTIONS.append((f"{name}-b{b + 1}", 1))
assert len(BAR_SECTIONS) == TOTAL_BARS

# per-section midpoint chord (bar index floor of section midpoint) -> degree
MIDPOINT_DEGREE = {}
for name, bars, prog, dc, g, var in SECTIONS:
    mid = SECTION_START[name] + bars // 2
    MIDPOINT_DEGREE[name] = BAR_DEGREES[mid]


def diatonic(deg_index, base=TONIC_BASE):
    """Canonical diatonic note (Scale7ChordDegree) — no %7 wrapper."""
    return Scale7ChordDegree.get_diatonic_note(base, INTERVALS, deg_index)


def chord_tones(d, lo=36, hi=96):
    """Absolute chord-tone set for 1-based degree d in [lo, hi]."""
    root_pc = (TONIC_PC + INTERVALS[d - 1]) % 12
    out = set()
    for octv in range(-3, 11):
        for iv in QUALITY[d]:
            n = root_pc + 12 * octv + iv
            if lo <= n <= hi:
                out.add(n)
    return sorted(out)


def chord_pcs(d):
    root_pc = (TONIC_PC + INTERVALS[d - 1]) % 12
    return sorted({(root_pc + iv) % 12 for iv in QUALITY[d]})


def pitch_row(r):
    """Sandpile lattice row -> diatonic pitch (14 rows = D3..C5)."""
    return Scale7ChordDegree.get_diatonic_note(TONIC_BASE, INTERVALS, r)


def snap(t):
    return int(round(t / float(GRID)) * GRID)


# ---------------------------------------------------------------------------
# Phase 1: Abelian Sandpile (Bak-Tang-Wiesenfeld) -> raw toppling events
# ---------------------------------------------------------------------------
H = 14                                    # pitch rows (D3..C5)
COLS_PER_SECTION = 32                     # 4 bars x 8 eighths
W = TOTAL_BARS * 8                        # 256 time columns


def build_drive():
    """Drop-site schedule: advancing column + register arch + density arc."""
    drop_rows = []
    grains = []
    for name, bars, prog, dc, gpc, var in SECTIONS:
        cur = dc
        for _k in range(bars * 8):
            cur = max(0, min(H - 1, cur + int(NPRNG.choice([-1, 0, 0, 1]))))
            drop_rows.append(cur)
            grains.append(gpc)
    return drop_rows, grains


def simulate_sandpile(drop_rows, grains, threshold=4):
    """BTW abelian sandpile: drop grains, relax synchronously to stability."""
    grid = np.zeros((H, W), dtype=np.int64)
    events = []
    for c in range(W):
        r = drop_rows[c]
        for _ in range(grains[c]):
            grid[r, c] += 1
            while True:
                over = grid >= threshold
                if not over.any():
                    break
                rs, cs = np.nonzero(over)
                grid[over] -= threshold
                for r_, c_ in zip(rs.tolist(), cs.tolist()):
                    events.append((r_, c_))
                    if r_ > 0:
                        grid[r_ - 1, c_] += 1
                    if r_ < H - 1:
                        grid[r_ + 1, c_] += 1
                    if c_ > 0:
                        grid[r_, c_ - 1] += 1
                    if c_ < W - 1:
                        grid[r_, c_ + 1] += 1
    return events, grid


def transform_events(events):
    """Apply per-section variation to the raw (row, col) topple stream.

    Returns list of dicts {row, col, sub, dur, n} where sub 0=front, 1=tail
    topple of a column. Variation: transpose (+4 diatonic rows), invert
    (diatonic mirror 13-row), retrograde (column time-reversal within section),
    augment (duration doubled + tail thinned = half-time).
    """
    by_col = {}
    for r, c in events:
        by_col.setdefault(c, []).append(r)
    out = []
    for c in sorted(by_col):
        sec_i = min(c // COLS_PER_SECTION, len(SECTIONS) - 1)
        name, bars, prog, dc, gpc, var = SECTIONS[sec_i]
        s_start = sec_i * COLS_PER_SECTION
        s_end = s_start + COLS_PER_SECTION
        rows = by_col[c]
        front, tail = rows[0], rows[-1]
        n = len(rows)
        if var == "transpose":
            frow = min(H - 1, front + 4)
            trow = min(H - 1, tail + 4)
        elif var == "invert":
            frow = H - 1 - front
            trow = H - 1 - tail
        else:
            frow, trow = front, tail
        cc = c
        if var == "retrograde":
            cc = s_start + (s_end - 1 - c)
        dur0 = 2 * EIGHTH if var == "augment" else EIGHTH
        for sub, row in ((0, frow), (1, trow)):
            if var == "augment" and sub == 1:
                continue                      # thin: front only
            if sub == 1 and trow == frow:
                continue
            out.append({"row": row, "col": cc, "sub": sub,
                        "dur": dur0 if sub == 0 else GRID, "n": n})
    out.sort(key=lambda e: (e["col"], e["sub"], e["row"]))
    return out


def build_raw_lead(trans):
    """Phase 1: single raw voice, off-grid + jittered, from varied topplings."""
    raw = []
    for t in trans:
        col_t = t["col"] * EIGHTH
        onset = col_t + t["sub"] * GRID + RNG.randint(-40, 40)
        p = float(pitch_row(t["row"]) + RNG.choice([-1, 0, 0, 1]))
        vel = int(min(110, 58 + t["n"] * 4))
        raw.append({"pitch": p, "start": onset, "dur": t["dur"],
                    "vel": vel, "row": t["row"], "col": t["col"]})
    raw.sort(key=lambda e: (e["start"], e["pitch"]))
    return raw


def rel_events(abs_events, s_start, s_len):
    """Shift absolute events into a section's relative tick frame + landmark."""
    out = []
    for e in abs_events:
        s = e.start_tick - s_start
        en = e.end_tick - s_start
        if en <= 0 or s >= s_len:
            continue
        s = max(0, s)
        en = min(s_len, en)
        if en <= s:
            en = min(s_len, s + GRID)
        out.append(MusicEvent(pitch=e.pitch, volume=e.volume,
                              start_tick=s, end_tick=en))
    out.sort(key=lambda e: e.start_tick)
    out.append(MusicEvent(pitch=0, volume=0,
                          start_tick=max(0, s_len - 10), end_tick=s_len))
    return out


def build_phase1(raw_events):
    """Phase 1: single voice (Lead), raw unquantized units, own composer."""
    comp = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS_PER_BAR)
    comp.create_matrix(num_voices=1, num_sections=len(SECTIONS))
    comp.add_voice("Lead", program=MARIMBA.midi_program, channel=0)
    for name, bars, prog, dc, g, var in SECTIONS:
        comp.add_section(name, bars=bars)

    for name, bars, prog, dc, g, var in SECTIONS:
        s_start = SECTION_START[name] * BAR
        s_ticks = bars * BAR
        seg = []
        for e in raw_events:
            if s_start <= e["start"] < s_start + s_ticks:
                p = int(round(e["pitch"]))
                p = max(36, min(96, p))
                seg.append(MusicEvent(pitch=p, volume=e["vel"],
                                      start_tick=int(round(e["start"])),
                                      end_tick=int(round(e["start"] + e["dur"]))))
        seg.sort(key=lambda e: e.start_tick)
        comp.fill_voice_section("Lead", name,
                                MusicUnit(events=rel_events(seg, s_start, s_ticks)))
    ok, msg = comp.validate()
    if not ok:
        raise RuntimeError(f"phase1 validate failed: {msg}")
    return comp


# ---------------------------------------------------------------------------
# Phase 2: STRICT chord discipline (every note = its bar's chord tone)
# ---------------------------------------------------------------------------
def process_lead(raw_events):
    """Grid snap + strict nearest-chord-tone quantize + dedup + voice-leading.

    STRICT (no scale-only weak notes, no tagged ornaments): every note snaps to
    the nearest CHORD tone of its own bar -> scale AND chord violations == 0.
    """
    events = []
    for e in raw_events:
        s = snap(e["start"])
        s = max(0, min(TOTAL_TICKS - GRID, s))
        bar = min(TOTAL_BARS - 1, s // BAR)
        degree = BAR_DEGREES[bar]
        ct = chord_tones(degree, lo=48, hi=88)
        p = min(ct, key=lambda t: abs(t - e["pitch"]))
        p = max(48, min(88, p))
        ev = MusicEvent(pitch=p, volume=e["vel"], start_tick=s,
                        end_tick=min(TOTAL_TICKS, s + e["dur"]))
        events.append(ev)

    # dedup collided (start_tick, pitch) -> keep longest
    best = {}
    for e in events:
        key = (e.start_tick, e.pitch)
        if key not in best or e.end_tick > best[key].end_tick:
            best[key] = e
    events = sorted(best.values(), key=lambda e: (e.start_tick, e.pitch))

    # voice-leading: break parallel perfect 5ths/octaves (adjacent onsets)
    fixed = []
    for e in events:
        if fixed:
            prev = fixed[-1]
            gap = e.start_tick - prev.end_tick
            if abs(e.pitch - prev.pitch) in (5, 7, 12) and gap < TPB:
                bar = min(TOTAL_BARS - 1, e.start_tick // BAR)
                tones = chord_tones(BAR_DEGREES[bar], lo=48, hi=88)
                cands = [t for t in tones
                         if t != e.pitch and abs(t - prev.pitch) not in (5, 7, 12)]
                if cands:
                    e.pitch = min(cands, key=lambda t: abs(t - e.pitch))
        fixed.append(e)
    return fixed


def build_counter():
    """Celesta 'aftershock': off-beat chord-tone arpeggios, varied per section.

    S4 transpose -> ascending; S5 invert -> ascending shifted 'e' slots;
    S6 density -> 8th-note continuous; else descending off-beat.
    """
    events = []
    for bar in range(TOTAL_BARS):
        sec_i = bar // 4
        var = SECTIONS[sec_i][5]
        d = BAR_DEGREES[bar]
        tones = chord_tones(d, lo=72, hi=96)
        t0 = bar * BAR
        if var == "transpose":
            slots, dirn = (2, 6, 10, 14), +1
        elif var == "invert":
            slots, dirn = (3, 7, 11, 15), +1
        elif sec_i == 5:
            slots, dirn = (0, 2, 4, 6, 8, 10, 12, 14), -1
        else:
            slots, dirn = (2, 6, 10, 14), -1
        order = list(range(len(slots)))
        if dirn < 0:
            order = order[::-1]
        for i, slot in enumerate(slots):
            t = t0 + slot * GRID
            p = tones[order[i] % len(tones)]
            events.append(MusicEvent(pitch=p, volume=56, start_tick=t,
                                     end_tick=t + GRID))
    return events


def build_harmony():
    """Piano chord stabs (grid-locked, in-chord). Density varies per section:
    default beats 1&3; S4 peak adds beats 2&4; S8 coda drops to beat 1 only."""
    events = []
    for bar in range(TOTAL_BARS):
        sec_i = bar // 4
        var = SECTIONS[sec_i][5]
        d = BAR_DEGREES[bar]
        tones = chord_tones(d, lo=53, hi=72)
        voicing = tones[:3]
        t0 = bar * BAR
        if var == "augment":
            beats = (0,)
        elif var == "transpose":
            beats = (0, 480, 960, 1440)
        else:
            beats = (0, 960)
        for beat in beats:
            t = t0 + beat
            for n in voicing:
                events.append(MusicEvent(pitch=n, volume=62, start_tick=t,
                                         end_tick=t + EIGHTH))
    return events


def build_pad():
    """String ensemble sustained whole-bar chord; S4 peak shifts +12 register."""
    events = []
    for bar in range(TOTAL_BARS):
        sec_i = bar // 4
        var = SECTIONS[sec_i][5]
        d = BAR_DEGREES[bar]
        lo, hi = (48, 72)
        if var == "transpose":
            lo, hi = (60, 84)
        tones = chord_tones(d, lo=lo, hi=hi)
        t0 = bar * BAR
        for n in tones[:3]:
            events.append(MusicEvent(pitch=n, volume=46, start_tick=t0,
                                     end_tick=t0 + BAR))
    return events


def build_bass():
    """Double bass root pedal, whole note per bar."""
    events = []
    for bar in range(TOTAL_BARS):
        d = BAR_DEGREES[bar]
        root = diatonic(d - 1, base=38)          # D2 region
        t0 = bar * BAR
        events.append(MusicEvent(pitch=root, volume=70, start_tick=t0,
                                 end_tick=t0 + BAR))
    return events


def build_phase2(lead_ev, counter_ev, harmony_ev, pad_ev, bass_ev, sections_spec):
    """Fill a 5-voice composer. sections_spec = [(name, bars), ...].

    Passed SECTIONS (8 x 4 bars) for the logical form, or BAR_SECTIONS
    (32 x 1 bar) when the humanizer needs bar-accurate boundary clamping.
    """
    comp = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS_PER_BAR)
    comp.create_matrix(num_voices=5, num_sections=len(sections_spec))
    comp.add_voice("Lead", program=MARIMBA.midi_program, channel=0)
    comp.add_voice("Counter", program=CELESTA.midi_program, channel=1)
    comp.add_voice("Harmony", program=PIANO.midi_program, channel=2)
    comp.add_voice("Pad", program=STRING_ENSEMBLE.midi_program, channel=3)
    comp.add_voice("Bass", program=DOUBLE_BASS.midi_program, channel=4)

    for name, bars in sections_spec:
        comp.add_section(name, bars=bars)

    vmap = {"Lead": lead_ev, "Counter": counter_ev, "Harmony": harmony_ev,
            "Pad": pad_ev, "Bass": bass_ev}
    acc = 0
    for name, bars in sections_spec:
        s_start = acc * BAR
        s_ticks = bars * BAR
        for vname, all_ev in vmap.items():
            seg = [e for e in all_ev if s_start <= e.start_tick < s_start + s_ticks]
            comp.fill_voice_section(vname, name,
                                    MusicUnit(events=rel_events(seg, s_start, s_ticks)))
        acc += bars
    ok, msg = comp.validate()
    if not ok:
        raise RuntimeError(f"phase2 validate failed: {msg}")
    return comp


def count_offgrid(events, grid=120):
    off = sum(1 for e in events if e.pitch > 0 and e.start_tick % grid != 0)
    return off, sum(1 for e in events if e.pitch > 0)


def count_violations(events):
    """STRICT: out-of-scale + out-of-chord counts over pitched events."""
    scale = chord = 0
    for e in events:
        if e.pitch <= 0:
            continue
        pc = e.pitch % 12
        bar = min(TOTAL_BARS - 1, e.start_tick // BAR)
        if pc not in KEY_PCS:
            scale += 1
        if pc not in chord_pcs(BAR_DEGREES[bar]):
            chord += 1
    return scale, chord


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    drop_rows, grains = build_drive()
    events, grid = simulate_sandpile(drop_rows, grains)
    trans = transform_events(events)
    print("Sandpile topplings:", len(events), "varied events:", len(trans))

    raw_events = build_raw_lead(trans)
    print("Phase-1 raw lead events:", len(raw_events))

    # ---- Phase 1 raw draft (single voice) ----------------------------------
    phase1 = build_phase1(raw_events)
    phase1_mid = os.path.join(MIDI_DIR, PROJECT + "-phase1.mid")
    phase1.to_midi(phase1_mid)
    write_provenance(
        phase1_mid, AI_ASSISTED,
        "musicom rework 314 (phase=1 raw, method 036 ASAR + variation)",
        sources=[SOURCE + "/MIDI/277-abelian-sandpile-avalanche-phase1.mid"],
        parameters={"bpm": BPM, "bars": TOTAL_BARS, "seed": raw_seed,
                    "phase": 1, "quantized": False, "key": KEY_NAME,
                    "form": "through-composed S1..S8", "style": STYLE,
                    "method": "036 ASAR (BTW abelian sandpile, 14x256 lattice)",
                    "variation": [s[5] for s in SECTIONS]},
        notes="Raw BTW abelian sandpile + per-section variation (transpose/"
              "invert/retrograde/augment). Off-grid, float pitch + jitter, "
              "single voice, pre-rules.")
    write_grid_visualization(
        phase1.matrix,
        os.path.join(ANALYSIS_DIR, "grid_visualization_phase1.txt"),
        voice_names=["Lead"], bpm=BPM)

    # ---- Phase 2 rules post-process (5 voices) -----------------------------
    lead_ev = process_lead(raw_events)
    counter_ev = build_counter()
    harmony_ev = build_harmony()
    pad_ev = build_pad()
    bass_ev = build_bass()

    # Humanized export uses 1-bar sections so the humanizer's boundary clamp is
    # bar-accurate (no jittered note crosses a bar line -> chord violations 0).
    phase2 = build_phase2(lead_ev, counter_ev, harmony_ev, pad_ev, bass_ev,
                          BAR_SECTIONS)

    # ---- STRICT discipline audit on phase-2 event lists --------------------
    all_ev = lead_ev + counter_ev + harmony_ev + pad_ev + bass_ev
    off, tot = count_offgrid(all_ev)
    scale_v, chord_v = count_violations(all_ev)
    print(f"Perfect-layer off-grid (pitched): {off}/{tot}")
    print(f"STRICT scale violations: {scale_v}  chord violations: {chord_v}")
    assert off == 0, f"perfect layer has {off} off-grid onsets"
    assert scale_v == 0, f"scale violations: {scale_v}"
    assert chord_v == 0, f"chord violations: {chord_v}"

    # grid visualization on the PERFECT (grid-locked) matrix, pre-humanization
    write_grid_visualization(
        phase2.matrix,
        os.path.join(ANALYSIS_DIR, "grid_visualization.txt"),
        voice_names=["Lead", "Counter", "Harmony", "Pad", "Bass"], bpm=BPM)

    # ---- dual-version export (perfect + humanized) -------------------------
    hz_instruments = {
        "Lead": MARIMBA.humanize_dna,
        "Counter": CELESTA.humanize_dna,
        "Harmony": PIANO.humanize_dna,
        "Pad": STRING_ENSEMBLE.humanize_dna,
        "Bass": DOUBLE_BASS.humanize_dna,
    }
    perfect_path = os.path.join(MIDI_DIR, PROJECT + "-perfect.mid")
    humanized_path = os.path.join(MIDI_DIR, PROJECT + "-humanized.mid")
    hz = export_dual(phase2, perfect_path, humanized_path,
                     style=STYLE, seed=hz_seed, bpm=BPM,
                     instruments=hz_instruments)

    # ---- provenance sidecars ------------------------------------------------
    provenance_params = {
        "bpm": BPM, "key": "D", "mode": "aeolian", "style": STYLE,
        "form": "through-composed S1..S8", "bars": TOTAL_BARS,
        "sections": [s[0] for s in SECTIONS],
        "section_variation": {s[0]: s[5] for s in SECTIONS},
        "method": "036 ASAR", "layer": "concrete", "paradigm": "Nature-Led",
        "rework": "redesign+extension", "source": "277-abelian-sandpile-avalanche",
        "voices": [[v, n, o.midi_program] for v, n, o in [
            ("Lead", "Marimba", MARIMBA), ("Counter", "Celesta", CELESTA),
            ("Harmony", "Piano", PIANO), ("Pad", "String Ensemble", STRING_ENSEMBLE),
            ("Bass", "Double Bass", DOUBLE_BASS)]],
        "humanize_seed": hz_seed, "raw_seed": raw_seed,
        "humanize_profiles": {k: v["profile"] for k, v in hz.items()},
    }
    write_provenance(
        perfect_path, AI_ASSISTED,
        "musicom rework 314 (phase=2 strict chord discipline: grid snap + "
        "chord-tone quantize + dedup + voice-leading) (method 036 ASAR)",
        sources=[phase1_mid],
        parameters=dict(provenance_params, phase=2, version="perfect",
                        off_grid=0, scale_violations=0, chord_violations=0),
        notes="Grid-locked perfect layer (through-composed, 32 bars, 8 sections).")
    write_provenance(
        humanized_path, AI_ASSISTED,
        "musicom rework 314 (phase=2 + humanization) (method 036 ASAR)",
        sources=[perfect_path],
        parameters=dict(provenance_params, phase=2, version="humanized",
                        humanize_seed=hz_seed,
                        humanize_stats={k: {kk: (float(vv) if isinstance(vv, float) else vv)
                                            for kk, vv in v.items() if kk != "profile"}
                                        for k, v in hz.items()}),
        notes="Humanized layer (style experimental + per-instrument DNA).")


    # ---- size asserts --------------------------------------------------------
    for p in (phase1_mid, perfect_path, humanized_path):
        assert os.path.getsize(p) > 40, f"empty/corrupt: {p}"

    # ---- root provenance.json (standard-6 fix) ------------------------------
    root_prov = dict(provenance_params)
    root_prov.update({
        "project": PROJECT, "genre": GENRE, "key_name": KEY_NAME,
        "tonic_pc": TONIC_PC, "key_pcs": sorted(KEY_PCS),
        "bars": TOTAL_BARS, "ticks": TOTAL_TICKS,
        "sections": [{"name": s[0], "bars": s[1], "progression": s[2],
                      "progression_names": [DEGREE_NAMES[d] for d in s[2]],
                      "midpoint_degree": MIDPOINT_DEGREE[s[0]],
                      "variation": s[5]} for s in SECTIONS],
        "variation_techniques": {
            "transposition": "S4 lead +4 diatonic steps (perfect 4th up)",
            "inversion": "S5 lead diatonic mirror around tonic",
            "retrograde": "S7 avalanche cascade time-reversed within section",
            "augmentation": "S8 durations doubled + tail thinned (half-time)",
            "register_shift": "S4 pad +12, S4/S6 drop-center arch high",
            "density_arc": "grains/col 3/5/7/11/7/9/5/3",
            "counterline_variation": "S4/S5 ascending, S6 8th-note density",
        },
        "audit": {"standard_failures": ["6: missing root provenance.json + "
                                        "index.html (source 277)"],
                  "redesign_required": True,
                  "source_identity": {"genre": "Experimental",
                                      "key": "D minor (aeolian)", "bpm": 88,
                                      "method": "036 ASAR",
                                      "voices": 5, "bars": 24}},
        "hz_seed": hz_seed, "raw_seed": raw_seed,
        "humanize_profiles": {k: v["profile"] for k, v in hz.items()},
        "generator": "musicom rework agent (nightly) 2026-11-20",
        "classification": "ai-assisted",
    })
    with open(os.path.join(BASE, "provenance.json"), "w") as f:
        json.dump(root_prov, f, indent=2, default=str)

    # ---- summary --------------------------------------------------------------
    summary = {
        "style": STYLE, "genre": GENRE, "project": PROJECT,
        "method": "036 ASAR", "form": "through-composed S1..S8",
        "key": KEY_NAME, "bpm": BPM, "bars": TOTAL_BARS,
        "sections": [s[0] for s in SECTIONS],
        "variation": {s[0]: s[5] for s in SECTIONS},
        "sandpile_topplings": len(events), "varied_events": len(trans),
        "raw_events": len(raw_events),
        "phase1_path": phase1_mid, "perfect_path": perfect_path,
        "humanized_path": humanized_path,
        "off_grid": off, "scale_violations": scale_v, "chord_violations": chord_v,
        "hz_seed": hz_seed,
        "hz": {k: {kk: vv for kk, vv in v.items() if kk != "profile"}
               for k, v in hz.items()},
        "progression": {s[0]: [DEGREE_NAMES[d] for d in s[2]] for s in SECTIONS},
        "midpoint_degree": MIDPOINT_DEGREE,
    }
    print("COMPOSE_OK")
    print(json.dumps(summary, indent=2, default=str))
    with open(os.path.join(ANALYSIS_DIR, "compose_summary.json"), "w") as f:
        json.dump(summary, f, indent=2, default=str)

    print("LEAD:", len(lead_ev), "COUNTER:", len(counter_ev),
          "HARMONY:", len(harmony_ev), "PAD:", len(pad_ev),
          "BASS:", len(bass_ev))


if __name__ == "__main__":
    main()
