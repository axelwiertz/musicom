# -*- coding: utf-8 -*-
"""277 - Abelian Sandpile Avalanche (Method 036 ASAR, two-phase architecture).

Nightly composition job (2026-10-31). Selection (seed = nightly date 20261031):
  style   = Experimental  (random draw from 47 genre dirs)
  method  = 036 Abelian Sandpile Avalanche Rhythmics (ASAR)  [concrete, Nature-Led]
  key     = D minor (aeolian)
  form    = through-composed  (S1..S6, 4 bars each = 24 bars)
  bpm     = 88

Two-phase architecture:
  Phase 1 (raw): the Bak-Tang-Wiesenfeld abelian sandpile on a 2D lattice
    (14 pitch rows x 192 eighth-note columns). A "composer's hand" advances the
    drop site down the time columns and arches it across the pitch register
    (per-section drop density 4/6/8/10/8/4 -> sparse intro, dense peak, sparse
    coda). Each cell toppling (>= 4 grains -> 1 grain to each of 4 neighbours,
    boundary dissipates) is a musical event: row -> diatonic pitch, column ->
    time. The avalanche cascade IS the rhythm (power-law bursts) and the 2D
    diffusion spreads it across adjacent scale degrees (stepwise runs) and
    adjacent time slots. Raw: float pitch + chromatic jitter, off-grid onsets,
    single voice, NO harmony -> own composer + validate() gate.

  Phase 2 (rules): weight-aware tiered pitch discipline (classify_weight ->
    tiered_quantize: strong = scale+chord, weak = scale), 16th grid snap,
    dedup, voice-leading (parallel 5th/octave break), tagged chromatic approach
    ornaments on the lead, and a 5-voice experimental texture:
      Lead=Marimba (avalanche cascade), Counter=Celesta (descending off-beat
      aftershock), Harmony=Piano (strong-beat chord stabs), Pad=String
      Ensemble (sustained), Bass=Double Bass (root pedal). No channel-9 drums.

  Dual-version contract: export_dual -> -perfect.mid (grid-locked) +
    -humanized.mid (style experimental + per-instrument DNA).
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
from sound.synthesis.scale_quantizer import (ScaleQuantizer, STRONG_GRID,
                                             classify_weight)
from workflows.pitch_audit import audit_voice

INSTR_DIR = "/opt/data/repos/musicom/projects/Instruments"
if INSTR_DIR not in sys.path:
    sys.path.insert(0, INSTR_DIR)
from instrument_registry import (MARIMBA, CELESTA, PIANO,  # noqa: E402
                                 STRING_ENSEMBLE, DOUBLE_BASS)

# ---------------------------------------------------------------------------
# Project layout / identity
# ---------------------------------------------------------------------------
GENRE = "Experimental"
STYLE = "experimental"
PROJECT = "277-abelian-sandpile-avalanche"
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
TOTAL_BARS = 24
TOTAL_TICKS = TOTAL_BARS * BAR            # 46080
STRONG = STRONG_GRID["4/4"]               # (0, 960) beats 1 & 3

KEY_NAME = "D minor (aeolian)"
TONIC_PC = 2                              # D
KEY_PCS = {2, 4, 5, 7, 9, 10, 0}          # D E F G A Bb C
INTERVALS = [0, 2, 3, 5, 7, 8, 10]        # natural-minor offsets from D
TONIC_BASE = 50                           # D3 (diatonic reference + quantizer root)

# 1-based degree -> triad quality intervals (D minor diatonic)
QUALITY = {1: (0, 3, 7), 2: (0, 3, 6), 3: (0, 4, 7), 4: (0, 3, 7),
           5: (0, 3, 7), 6: (0, 4, 7), 7: (0, 4, 7)}
DEGREE_NAMES = {1: "Dm", 2: "Edim", 3: "F", 4: "Gm", 5: "Am", 6: "Bb", 7: "C"}

# deterministic seeds
hz_seed = int(hashlib.md5(PROJECT.encode()).hexdigest()[:8], 16) % 100000
raw_seed = 20261031                        # the nightly selection seed
RNG = random.Random(raw_seed)              # phase-2 post-processing (thinning/ornaments)
NPRNG = np.random.default_rng(raw_seed)    # phase-1 generative drive

# ---------------------------------------------------------------------------
# Form: through-composed S1..S6 (4 bars each = 24 bars).
# (name, bars, progression [1-based degrees], drop_center row, grains/column)
# drop_center arches the sandpile "hand" across pitch registers; grains/column
# sets the avalanche density arc (sparse -> dense -> sparse).
# ---------------------------------------------------------------------------
SECTIONS = [
    ("S1", 4, [1, 3, 6, 7], 2, 4),    # i - III - VI - VII  (sparse low)
    ("S2", 4, [1, 4, 1, 5], 4, 6),    # i - iv - i - v
    ("S3", 4, [6, 7, 1, 5], 6, 8),    # VI - VII - i - v
    ("S4", 4, [4, 1, 7, 6], 9, 10),   # iv - i - VII - VI   (peak high)
    ("S5", 4, [1, 6, 4, 5], 7, 8),    # i - VI - iv - v
    ("S6", 4, [1, 4, 7, 1], 3, 4),    # i - iv - VII - i    (sparse low coda)
]
SECTION_START = {}
_acc = 0
for name, bars, prog, dc, g in SECTIONS:
    SECTION_START[name] = _acc
    _acc += bars
assert _acc == TOTAL_BARS

BAR_DEGREES = []
for name, bars, prog, dc, g in SECTIONS:
    BAR_DEGREES.extend(prog)
assert len(BAR_DEGREES) == TOTAL_BARS


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
H = 14   # pitch rows (two octaves of D minor: D3..C5)
W = 192  # time columns (one eighth note each -> 24 bars)


def build_drive():
    """Drop-site schedule: advancing column + register arch, density per section."""
    drop_rows = []
    grains = []
    for name, bars, prog, dc, gpc in SECTIONS:
        cur = dc
        for _k in range(bars * 8):            # 4 bars x 8 eighths = 32 columns
            cur = max(0, min(H - 1, cur + int(NPRNG.choice([-1, 0, 0, 1]))))
            drop_rows.append(cur)
            grains.append(gpc)
    return drop_rows, grains


def simulate_sandpile(drop_rows, grains, threshold=4):
    """BTW abelian sandpile: drop grains, relax synchronously to stability.

    Each toppling cell loses `threshold` grains and gives 1 to each of its 4
    lattice neighbours (up/down/left/right); grains reaching the boundary
    dissipate. Returns (events, final_grid) where events = [(row, col), ...]
    in avalanche order. Deterministic given drop_rows/grains.
    """
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


def build_raw_lead(events):
    """Phase 1: single raw voice. Front + tail topple per column -> note.

    Off-grid onset (jittered), float pitch with chromatic jitter, velocity
    scaled by the column's avalanche size. No harmony, no quantize.
    """
    by_col = {}
    for r, c in events:
        by_col.setdefault(c, []).append(r)
    raw = []
    for c in sorted(by_col):
        rows = by_col[c]
        front, tail = rows[0], rows[-1]
        col_t = c * EIGHTH
        n = len(rows)
        for sub, row in ((0, front), (1, tail)):
            if sub == 1 and tail == front:
                continue
            onset = col_t + sub * GRID + RNG.randint(-40, 40)
            p = float(pitch_row(row) + RNG.choice([-1, 0, 0, 1]))
            vel = int(min(110, 58 + n * 4))
            dur = EIGHTH if sub == 0 else GRID
            raw.append({"pitch": p, "start": onset, "dur": dur,
                        "vel": vel, "row": row, "col": c})
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
    # silent terminal landmark (zero-drift anchor; humanizer passes untouched)
    out.append(MusicEvent(pitch=0, volume=0,
                          start_tick=max(0, s_len - 10), end_tick=s_len))
    return out


def build_phase1(raw_events):
    """Phase 1: single voice (Lead), raw unquantized units, own composer."""
    comp = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS_PER_BAR)
    comp.create_matrix(num_voices=1, num_sections=len(SECTIONS))
    comp.add_voice("Lead", program=MARIMBA.midi_program, channel=0)
    for name, bars, prog, dc, g in SECTIONS:
        comp.add_section(name, bars=bars)

    for name, bars, prog, dc, g in SECTIONS:
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
# Phase 2: rules post-process (weight-aware tiered pitch discipline)
# ---------------------------------------------------------------------------
SQ = ScaleQuantizer(root=TONIC_BASE, scale="minor")   # D natural minor


def process_lead(raw_events):
    """Tiered quantize (strong=scale+chord, weak=scale) + grid snap + ornaments."""
    events = []
    for e in raw_events:
        s = snap(e["start"])
        s = max(0, min(TOTAL_TICKS - GRID, s))
        bar = min(TOTAL_BARS - 1, s // BAR)
        degree = BAR_DEGREES[bar]
        w = classify_weight(s, STRONG, BAR)
        ct = chord_tones(degree, lo=48, hi=88)
        p = SQ.tiered_quantize(e["pitch"], weight=w, chord_tones=ct)
        p = max(48, min(88, p))
        ev = MusicEvent(pitch=p, volume=e["vel"], start_tick=s,
                        end_tick=min(TOTAL_TICKS, s + GRID))
        ev.weight = w                       # dropped by to_midi, read by audit
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
    events = fixed

    # tagged chromatic approach ornaments (lead MAY carry tagged ornaments):
    # a half-step-below approach into strong chord tones, only when chromatic
    # and the prior 16th slot is free. Deterministic (every 2nd eligible).
    used_slots = {e.start_tick for e in events}
    ornaments = []
    eligible = 0
    for e in events:
        if classify_weight(e.start_tick, STRONG, BAR) != "strong":
            continue
        approach = e.pitch - 1
        if (approach % 12) in KEY_PCS:
            continue                      # not chromatic, skip
        slot = e.start_tick - GRID
        if slot < 0 or slot in used_slots:
            continue
        eligible += 1
        if eligible % 2 != 0:
            continue                      # keep sparse: every 2nd eligible
        oe = MusicEvent(pitch=approach, volume=max(50, e.volume - 10),
                        start_tick=slot, end_tick=e.start_tick)
        oe.weight = "weak"
        oe.ornament = "approach"
        oe.resolve_pitch = e.pitch
        ornaments.append(oe)
        used_slots.add(slot)
    return sorted(events + ornaments, key=lambda e: (e.start_tick, e.pitch))


def build_counter():
    """Celesta 'aftershock': descending off-beat chord-tone arpeggios."""
    events = []
    for bar in range(TOTAL_BARS):
        d = BAR_DEGREES[bar]
        tones = chord_tones(d, lo=72, hi=96)
        t0 = bar * BAR
        for i, slot in enumerate((2, 6, 10, 14)):     # 'and' of each beat
            t = t0 + slot * GRID
            p = tones[(len(tones) - 1 - i) % len(tones)]
            events.append(MusicEvent(pitch=p, volume=56, start_tick=t,
                                     end_tick=t + GRID))
    return events


def build_harmony():
    """Piano chord stabs on strong beats 1 & 3 (grid-locked, in-chord)."""
    events = []
    for bar in range(TOTAL_BARS):
        d = BAR_DEGREES[bar]
        tones = chord_tones(d, lo=53, hi=72)
        voicing = tones[:3]
        t0 = bar * BAR
        for beat in (0, 960):
            t = t0 + beat
            for n in voicing:
                events.append(MusicEvent(pitch=n, volume=62, start_tick=t,
                                         end_tick=t + EIGHTH))
    return events


def build_pad():
    """String ensemble sustained whole-bar chord (harmonic anchor)."""
    events = []
    for bar in range(TOTAL_BARS):
        d = BAR_DEGREES[bar]
        tones = chord_tones(d, lo=48, hi=72)
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


def build_phase2(lead_ev, counter_ev, harmony_ev, pad_ev, bass_ev):
    comp = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS_PER_BAR)
    comp.create_matrix(num_voices=5, num_sections=len(SECTIONS))
    comp.add_voice("Lead", program=MARIMBA.midi_program, channel=0)
    comp.add_voice("Counter", program=CELESTA.midi_program, channel=1)
    comp.add_voice("Harmony", program=PIANO.midi_program, channel=2)
    comp.add_voice("Pad", program=STRING_ENSEMBLE.midi_program, channel=3)
    comp.add_voice("Bass", program=DOUBLE_BASS.midi_program, channel=4)

    for name, bars, prog, dc, g in SECTIONS:
        comp.add_section(name, bars=bars)

    vmap = {"Lead": lead_ev, "Counter": counter_ev, "Harmony": harmony_ev,
            "Pad": pad_ev, "Bass": bass_ev}
    for name, bars, prog, dc, g in SECTIONS:
        s_start = SECTION_START[name] * BAR
        s_ticks = bars * BAR
        for vname, all_ev in vmap.items():
            seg = [e for e in all_ev if s_start <= e.start_tick < s_start + s_ticks]
            comp.fill_voice_section(vname, name,
                                    MusicUnit(events=rel_events(seg, s_start, s_ticks)))
    ok, msg = comp.validate()
    if not ok:
        raise RuntimeError(f"phase2 validate failed: {msg}")
    return comp


def run_tiered_audit(lead_ev, counter_ev, harmony_ev, pad_ev, bass_ev):
    """Tiered pitch discipline audit (Phase 3 P1) on the 5 pitched voices."""
    scale_pcs = sorted(KEY_PCS)
    chord_by_bar = {b: chord_pcs(BAR_DEGREES[b]) for b in range(TOTAL_BARS)}
    voices = {"Lead": lead_ev, "Counter": counter_ev, "Harmony": harmony_ev,
              "Pad": pad_ev, "Bass": bass_ev}
    report = {}
    all_pass = True
    for vname, ev in voices.items():
        r = audit_voice(ev, scale_pcs, chord_pcs_by_bar=chord_by_bar,
                        strong_grid=STRONG, bar_ticks=BAR, grid=EIGHTH)
        report[vname] = {
            "audible": r.audible,
            "strong_ok": r.strong_ok,
            "weak_in_scale": r.weak_in_scale,
            "tagged_ornaments": r.tagged_ornaments,
            "tagged_resolving": r.tagged_resolving,
            "tagged_non_resolving": r.tagged_non_resolving,
            "untagged_out_of_scale": r.untagged_out_of_scale,
            "strong_violations": r.strong_violations,
            "passes": r.passes,
        }
        if not r.passes:
            all_pass = False
    report["all_pass"] = all_pass
    return report


def count_offgrid(events, grid=120):
    off = sum(1 for e in events if e.pitch > 0 and e.start_tick % grid != 0)
    return off, sum(1 for e in events if e.pitch > 0)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    drop_rows, grains = build_drive()
    events, grid = simulate_sandpile(drop_rows, grains)
    print("Sandpile topplings:", len(events))

    raw_events = build_raw_lead(events)
    print("Phase-1 raw lead events:", len(raw_events))

    # ---- Phase 1 raw draft (single voice) ----------------------------------
    phase1 = build_phase1(raw_events)
    phase1_mid = os.path.join(MIDI_DIR, PROJECT + "-phase1.mid")
    phase1.to_midi(phase1_mid)
    write_provenance(
        phase1_mid, AI_ASSISTED,
        "musicom.method.036_abelian_sandpile_phase1",
        sources=[],
        parameters={"bpm": BPM, "bars": TOTAL_BARS, "seed": raw_seed,
                    "phase": 1, "quantized": False, "key": KEY_NAME,
                    "form": "through-composed S1..S6", "style": STYLE,
                    "method": "036 ASAR (BTW abelian sandpile, 14x192 lattice)"},
        notes="Raw BTW abelian sandpile: advancing drop site arches the "
              "register, per-section grain density 4/6/8/10/8/4. Float pitch "
              "+ chromatic jitter, off-grid onsets, single voice, pre-rules.")
    write_grid_visualization(
        phase1.matrix,
        os.path.join(ANALYSIS_DIR, "grid_visualization_phase1.txt"),
        voice_names=["Lead"], bpm=BPM)

    # ---- Phase 2 rules post-process (5 voices) ----------------------------
    lead_ev = process_lead(raw_events)
    counter_ev = build_counter()
    harmony_ev = build_harmony()
    pad_ev = build_pad()
    bass_ev = build_bass()

    phase2 = build_phase2(lead_ev, counter_ev, harmony_ev, pad_ev, bass_ev)

    # ---- tiered pitch-discipline audit (Phase 3 P1) -----------------------
    tiered = run_tiered_audit(lead_ev, counter_ev, harmony_ev, pad_ev, bass_ev)
    if not tiered["all_pass"]:
        print("TIERED_AUDIT_FAIL:", json.dumps(tiered, indent=2))
        raise RuntimeError("tiered pitch audit failed — see pitch_audit.json")
    with open(os.path.join(ANALYSIS_DIR, "pitch_audit.json"), "w") as f:
        json.dump(tiered, f, indent=2)
    print("TIERED_AUDIT:", json.dumps(tiered, indent=2))

    # ---- grid audit on the phase-2 event lists (perfect layer) ------------
    off, tot = count_offgrid(lead_ev + counter_ev + harmony_ev + pad_ev + bass_ev)
    print(f"Perfect-layer off-grid (pitched): {off}/{tot}")
    assert off == 0, f"perfect layer has {off} off-grid onsets"

    # ---- dual-version export (perfect + humanized) ------------------------
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

    # ---- provenance sidecars ----------------------------------------------
    provenance_params = {
        "bpm": BPM, "key": "D", "mode": "aeolian", "style": STYLE,
        "form": "through-composed S1..S6", "bars": TOTAL_BARS,
        "sections": [s[0] for s in SECTIONS],
        "method": "036 ASAR", "layer": "concrete", "paradigm": "Nature-Led",
        "voices": [["Lead", "Marimba", MARIMBA.midi_program],
                   ["Counter", "Celesta", CELESTA.midi_program],
                   ["Harmony", "Piano", PIANO.midi_program],
                   ["Pad", "String Ensemble", STRING_ENSEMBLE.midi_program],
                   ["Bass", "Double Bass", DOUBLE_BASS.midi_program]],
        "humanize_seed": hz_seed, "raw_seed": raw_seed,
        "humanize_profiles": {k: v["profile"] for k, v in hz.items()},
    }
    write_provenance(
        perfect_path, AI_ASSISTED,
        "musicom two-phase (phase=2 rules: tiered quantize + grid snap + "
        "dedup + voice-leading + tagged ornaments) (method 036 ASAR)",
        sources=[phase1_mid],
        parameters=dict(provenance_params, phase=2, version="perfect", off_grid=0),
        notes="Grid-locked perfect layer (through-composed, 24 bars).")
    write_provenance(
        humanized_path, AI_ASSISTED,
        "musicom two-phase (phase=2 + humanization) (method 036 ASAR)",
        sources=[perfect_path],
        parameters=dict(provenance_params, phase=2, version="humanized",
                        humanize_seed=hz_seed,
                        humanize_stats={k: {kk: (float(vv) if isinstance(vv, float) else vv)
                                            for kk, vv in v.items() if kk != "profile"}
                                        for k, v in hz.items()}),
        notes="Humanized layer (style experimental + per-instrument DNA).")

    # ---- grid visualization ------------------------------------------------
    write_grid_visualization(
        phase2.matrix,
        os.path.join(ANALYSIS_DIR, "grid_visualization.txt"),
        voice_names=["Lead", "Counter", "Harmony", "Pad", "Bass"], bpm=BPM)

    # ---- size asserts ------------------------------------------------------
    for p in (phase1_mid, perfect_path, humanized_path):
        assert os.path.getsize(p) > 40, f"empty/corrupt: {p}"

    # ---- summary -----------------------------------------------------------
    summary = {
        "style": STYLE, "genre": GENRE,
        "method": "036 ASAR", "method_layer": "concrete",
        "method_paradigm": "Nature-Led",
        "form": "through-composed S1..S6", "key": KEY_NAME, "bpm": BPM,
        "bars": TOTAL_BARS, "sections": [s[0] for s in SECTIONS],
        "sandpile_topplings": len(events),
        "raw_events": len(raw_events),
        "phase1_path": phase1_mid,
        "perfect_path": perfect_path,
        "humanized_path": humanized_path,
        "hz_seed": hz_seed,
        "hz": {k: {kk: vv for kk, vv in v.items() if kk != "profile"}
               for k, v in hz.items()},
        "progression": {s[0]: [DEGREE_NAMES[d] for d in s[2]] for s in SECTIONS},
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
