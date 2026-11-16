# -*- coding: utf-8 -*-
"""308-physarum-classical-rondo -- Classical rondo via Physarum Polycephalum
Transport Network Optimization (method 035).

Nightly composition job (2026-11-16). Selection: style=Classical, method=035
Physarum (Nature-Led, concrete layer), form=rondo (pick_form -> A B A C A,
bars [4,4,4,4,4] = 20 bars).

MUSICAL DNA
  - Key G major (Ionian) = pc {0,2,4,6,7,9,11}; tonic G.
  - 100 BPM, 4/4, 480 TPB, BAR=1920, 8th=240, 16th=120.
  - Method 035 Physarum: food sources = the bar's chord tones (pitch-coordinate
    nodes) + a tonic attractor. A foraging slime-mold agent streams toward the
    nearest food source, depositing protoplasmic "tube thickness" (flux) on
    revisited pitches. Contractive peristaltic oscillations -> rhythmic density
    (rests when the contraction dips). Thickness -> velocity.
  - Classical 5-voice texture: Violin lead (Physarum path), Flute canon
    (path -12, +1 beat, thinned), Viola inner harmony, Cello bass (root/fifth),
    Piano Alberti-style broken-chord continuo.

TWO-PHASE
  Phase 1 (raw): single-voice Physarum walk, unquantized float pitch (seeded
    diffusion jitter) + off-grid onsets; own composer + validate() gate.
  Phase 2 (rules): tiered quantize (strong->chord tone, weak->scale tone via
    ScaleQuantizer.tiered_quantize), 8th-grid snap, voice-leading on the pad
    triads, register enforcement, 5-voice classical texture.
  Dual-version: export_dual -> -perfect.mid (grid-locked) + -humanized.mid.
"""
import json
import os
import sys
import hashlib
import math

import numpy as np

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer
from workflows.humanize import export_dual
from workflows.provenance import write_provenance, AI_ASSISTED
from visualization.grid import write_grid_visualization
from rules.progression import Scale7ChordDegree
from rules.voice_leading import VoiceLeadingRules
from sound.synthesis.scale_quantizer import ScaleQuantizer

_INSTR_DIR = "/opt/data/repos/musicom/projects/Instruments"
if _INSTR_DIR not in sys.path:
    sys.path.insert(0, _INSTR_DIR)
from instrument_registry import (  # noqa: E402
    VIOLIN, FLUTE, VIOLA, CELLO, PIANO)

# ---------------------------------------------------------------------------
# Project layout / identity
# ---------------------------------------------------------------------------
GENRE = "Classical"
STYLE = "classical"
PROJECT = "308-physarum-classical-rondo"
BASE = os.path.join("/opt/data/projects/Styles", GENRE, PROJECT)
MIDI_DIR = os.path.join(BASE, "MIDI")
AUDIO_DIR = os.path.join(BASE, "Audio")
ANALYSIS_DIR = os.path.join(BASE, "Analysis")
for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
    os.makedirs(d, exist_ok=True)

BPM = 100
TPB = 480
BPB = 4
BAR = TPB * BPB                     # 1920
GRID = 240                          # 8th (snap target)
SIXTEENTH = 120
QUARTER = 480
TOTAL_BARS = 20
TOTAL_TICKS = TOTAL_BARS * BAR      # 38400
SLOTS_PER_BAR = 8
TOTAL_SLOTS = TOTAL_BARS * SLOTS_PER_BAR  # 160

KEY_NAME = "G major (Ionian)"
TONIC_PC = 7                        # G
INTERVALS = [0, 2, 4, 5, 7, 9, 11]
KEY_PCS = sorted({(TONIC_PC + iv) % 12 for iv in INTERVALS})  # [0,2,4,6,7,9,11]
TONIC_BASE = 55                     # G3 (triad/pad reference)

# 0-based degree -> triad quality intervals (G ionian diatonic)
# 0=G, 1=Am, 2=Bm, 3=C, 4=D, 5=Em, 6=F#dim
QUALITY = {0: (0, 4, 7), 1: (0, 3, 7), 2: (0, 3, 7), 3: (0, 4, 7),
           4: (0, 4, 7), 5: (0, 3, 7), 6: (0, 3, 6)}
DEGREE_NAMES = {0: "G", 1: "Am", 2: "Bm", 3: "C",
                4: "D", 5: "Em", 6: "F#dim"}

# deterministic seeds
hz_seed = int(hashlib.md5(PROJECT.encode()).hexdigest()[:8], 16) % 100000
raw_seed = 20261116

# ---------------------------------------------------------------------------
# Form (rondo: A B A C A = 4/4/4/4/4 bars = 20)
# ---------------------------------------------------------------------------
SECTIONS = [
    ("A",  4, [0, 4, 0, 3]),          # G D G C  (tonic area)
    ("B",  4, [4, 5, 1, 4]),          # D Em Am D (dominant excursion, ii-V prep)
    ("A2", 4, [0, 4, 0, 3]),          # G D G C  (recap)
    ("C",  4, [5, 1, 4, 0]),          # Em Am D G (relative-minor contrast)
    ("A3", 4, [0, 4, 0, 0]),          # G D G G  (authentic cadence V->I)
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

VOICES = ["Violin", "Flute", "Viola", "Cello", "Piano"]
VOICE_PROGRAMS = [VIOLIN.midi_program, FLUTE.midi_program, VIOLA.midi_program,
                  CELLO.midi_program, PIANO.midi_program]
VOICE_CHANNELS = [0, 1, 2, 3, 4]

# register windows per voice
VIOLIN_LO, VIOLIN_HI = 67, 91
FLUTE_LO, FLUTE_HI = 60, 84
VIOLA_LO, VIOLA_HI = 55, 69
CELLO_LO, CELLO_HI = 43, 55
PIANO_LO, PIANO_HI = 55, 79
VIOLIN_BASE = 79                    # G5 (Physarum start)


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
# Method 035: Physarum Polycephalum transport network -- Phase 1 raw draft
# ---------------------------------------------------------------------------
def simulate_physarum(rng):
    """Slime-mold foraging -> raw single-voice melodic path.

    Food sources = the bar's chord tones (pitch-coordinate nodes) + a tonic
    attractor. The agent streams toward the nearest source, deposits flux
    (tube thickness) on revisited pitches, and pauses when the peristaltic
    contraction oscillation dips (rests)."""
    trail = {}                       # pitch bin -> tube thickness (flux)
    position = float(VIOLIN_BASE)    # start at tonic G5
    records = []
    for slot in range(TOTAL_SLOTS):
        bar = slot // SLOTS_PER_BAR
        d = BAR_DEGREES[bar]
        foods = chord_tones(d, VIOLIN_LO, VIOLIN_HI)
        foods.append(VIOLIN_BASE)    # tonic attractor (always present)
        # peristaltic contraction oscillation -> rhythmic density
        rho = 0.5 + 0.5 * math.sin(2 * math.pi * slot / 16.0)
        # chemotaxis: nearest food source + exploration noise
        target = min(foods, key=lambda f: abs(f - position) + rng.uniform(0.0, 7.0))
        # protoplasmic streaming + diffusion
        position += (target - position) * 0.35
        position += rng.normal(0.0, 1.3)
        position = float(max(float(VIOLIN_LO), min(float(VIOLIN_HI), position)))
        # deposit flux (revisited pitches thicken)
        k = int(round(position))
        trail[k] = trail.get(k, 0) + 1
        if rho < 0.30:               # contraction dip -> rest
            continue
        rel = (slot % SLOTS_PER_BAR) * GRID
        jit = int(rng.integers(-25, 26))
        st = max(0, min(BAR - 30, rel + jit))
        tick_abs = bar * BAR + st
        dur = int(rng.integers(160, 360))
        vel = int(60 + 35 * min(1.0, trail[k] / 6.0))
        records.append({"tick_abs": tick_abs, "pitch": float(position),
                        "dur": dur, "vel": vel, "bar": bar, "degree": d,
                        "thickness": trail[k]})
    return records


def build_phase1(records):
    p1 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BPB)
    p1.create_matrix(num_voices=1, num_sections=len(SECTIONS))
    p1.add_voice("RawDraft", program=VIOLIN.midi_program, channel=0)
    for name, bars, prog in SECTIONS:
        p1.add_section(name, bars=bars)

    per_section_events = {name: [] for name, bars, prog in SECTIONS}
    for r in records:
        sec = BAR_TO_SECTION[r["bar"]]
        per_section_events[sec].append(r)

    for name, bars, prog in SECTIONS:
        s_ticks = bars * BAR
        s0 = SECTION_START[name] * BAR
        cell = []
        for r in per_section_events[name]:
            st = r["tick_abs"] - s0
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
        p1.fill_voice_section("RawDraft", name, MusicUnit(events=cell))
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
    """Octave-shift a pitch into [lo, hi] preserving pitch class (no clamp)."""
    p = int(pitch)
    while p < lo:
        p += 12
    while p > hi:
        p -= 12
    return p


def weight_of(onset):
    return "strong" if (onset % BAR) in (0, 960) else "weak"


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


def build_violin_section(name, records, sq):
    """Violin lead = Physarum path, tiered-quantized + 8th-grid snapped."""
    nbars = SECTION_BARS[name]
    s_ticks = nbars * BAR
    s0 = SECTION_START[name] * BAR
    ev = []
    for r in records:
        if not (s0 <= r["tick_abs"] < s0 + s_ticks):
            continue
        bar = r["tick_abs"] // BAR
        d = BAR_DEGREES[bar]
        st_glob = snap_grid(r["tick_abs"], GRID)
        st = st_glob - s0
        if st < 0 or st >= s_ticks - 30:
            continue
        weight = weight_of(st)
        ct = chord_tones(d, VIOLIN_LO, VIOLIN_HI)
        pitch = sq.tiered_quantize(r["pitch"], weight=weight, chord_tones=ct)
        pitch = max(VIOLIN_LO, min(VIOLIN_HI, pitch))
        dur = int(r["dur"])
        if name == "A3":
            dur = max(dur, 300)      # sustained final cadence
        en = min(s_ticks - 20, st + dur)
        if en <= st + 30:
            en = st + 120
        ev.append(MusicEvent(pitch=pitch, volume=88, start_tick=st, end_tick=en))
    best = {}
    for e in ev:
        key = (e.start_tick, e.pitch)
        if key not in best or (e.end_tick - e.start_tick) > \
                (best[key].end_tick - best[key].start_tick):
            best[key] = e
    return sorted(best.values(), key=lambda e: (e.start_tick, e.pitch))


def build_flute_section(name, records, sq):
    """Flute canon = Physarum path -12 (octave down), +1 beat, thinned."""
    nbars = SECTION_BARS[name]
    s_ticks = nbars * BAR
    s0 = SECTION_START[name] * BAR
    ev = []
    cnt = 0
    for r in records:
        if not (s0 <= r["tick_abs"] < s0 + s_ticks):
            continue
        cnt += 1
        if cnt % 2 == 0:             # thin the canon to every 2nd note
            continue
        st_glob = snap_grid(r["tick_abs"] + QUARTER, GRID)   # +1 beat delay
        st = st_glob - s0
        if st < 0 or st >= s_ticks - 30:
            continue
        bar = st_glob // BAR         # shifted bar (canon may cross a bar seam)
        d = BAR_DEGREES[bar]
        weight = weight_of(st)
        ct = chord_tones(d, FLUTE_LO, FLUTE_HI)
        pitch = sq.tiered_quantize(r["pitch"] - 12.0, weight=weight, chord_tones=ct)
        pitch = max(FLUTE_LO, min(FLUTE_HI, pitch))
        en = min(s_ticks - 20, st + 240)
        ev.append(MusicEvent(pitch=pitch, volume=70, start_tick=st, end_tick=en))
    return ev


def build_viola_section(name, corr_triads):
    """Viola inner harmony = sustained 3rd+5th (middle of the voice-led triad)."""
    nbars = SECTION_BARS[name]
    s_ticks = nbars * BAR
    ev = []
    for bi in range(nbars):
        bar = SECTION_START[name] + bi
        r, th, f = corr_triads[bar]
        bs = bi * BAR
        end = min(bs + BAR - 30, s_ticks - 30)
        for p, v in ((th, 62), (f, 58)):
            p = to_register(p, VIOLA_LO, VIOLA_HI)
            ev.append(MusicEvent(pitch=p, volume=v, start_tick=bs, end_tick=end))
    return ev


def build_cello_section(name, corr_triads):
    """Cello bass = root (beat 1) + fifth (beat 3), sustained."""
    nbars = SECTION_BARS[name]
    s_ticks = nbars * BAR
    ev = []
    for bi in range(nbars):
        bar = SECTION_START[name] + bi
        r, th, f = corr_triads[bar]
        bs = bi * BAR
        root = to_register(r - 12, CELLO_LO, CELLO_HI)      # G2 region
        fifth = to_register(f - 12, CELLO_LO, CELLO_HI)
        ev.append(MusicEvent(pitch=root, volume=80,
                             start_tick=bs, end_tick=bs + BAR - 60))
        ev.append(MusicEvent(pitch=fifth, volume=68,
                             start_tick=bs + 960, end_tick=bs + 960 + 380))
    return ev


def build_piano_section(name, corr_triads):
    """Piano continuo = Alberti-style broken chord (root-5th-3rd-octave)."""
    nbars = SECTION_BARS[name]
    s_ticks = nbars * BAR
    ev = []
    for bi in range(nbars):
        bar = SECTION_START[name] + bi
        r, th, f = corr_triads[bar]
        bs = bi * BAR
        octv = r + 12
        # all four are chord tones -> strong beats (0,960) in-chord, weak in-scale
        seq = [(r, 0), (f, 480), (th, 960), (octv, 1440)]
        for p, off in seq:
            p = to_register(p, PIANO_LO, PIANO_HI)
            ev.append(MusicEvent(pitch=p, volume=60,
                                 start_tick=bs + off, end_tick=bs + off + 420))
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
        comp.fill_voice_section("Violin", name,
                                seal(build_violin_section(name, records, sq), s_ticks))
        comp.fill_voice_section("Flute", name,
                                seal(build_flute_section(name, records, sq), s_ticks))
        comp.fill_voice_section("Viola", name,
                                seal(build_viola_section(name, corr_triads), s_ticks))
        comp.fill_voice_section("Cello", name,
                                seal(build_cello_section(name, corr_triads), s_ticks))
        comp.fill_voice_section("Piano", name,
                                seal(build_piano_section(name, corr_triads), s_ticks))
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
    records = simulate_physarum(rng)
    print("PHYSARUM notes=", len(records),
          "thickness_range=",
          (min(r["thickness"] for r in records),
           max(r["thickness"] for r in records)) if records else "n/a")

    # ---- Phase 1 raw draft -------------------------------------------------
    phase1 = build_phase1(records)
    phase1_mid = os.path.join(MIDI_DIR, PROJECT + "-phase1.mid")
    phase1.to_midi(phase1_mid)
    write_provenance(
        phase1_mid, AI_ASSISTED,
        "musicom.physarum_phase1",
        parameters={"bpm": BPM, "bars": TOTAL_BARS, "seed": raw_seed,
                    "phase": 1, "quantized": False, "key": KEY_NAME,
                    "form": "rondo", "style": STYLE,
                    "method": "035 Physarum Polycephalum Transport Network Optimization",
                    "layer": "concrete", "paradigm": "Nature-Led",
                    "physarum": {"food_sources": "bar chord tones + tonic attractor",
                                 "streaming": 0.35, "diffusion_sigma": 1.3,
                                 "peristalsis_period_slots": 16,
                                 "rest_threshold": 0.30},
                    "notes": len(records),
                    "rules_applied": "NONE (pre-rules)"},
        notes="Raw Physarum slime-mold draft: single violin voice, unquantized "
              "float pitch (diffusion jitter) + off-grid onsets, 20 bars, "
              "pre-rules. Method 035 (concrete).")
    write_grid_visualization(phase1.matrix,
                             os.path.join(ANALYSIS_DIR,
                                          "grid_visualization_phase1.txt"),
                             voice_names=["RawDraft"], bpm=BPM)
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
        "Violin": VIOLIN.humanize_dna,
        "Flute": FLUTE.humanize_dna,
        "Viola": VIOLA.humanize_dna,
        "Cello": CELLO.humanize_dna,
        "Piano": PIANO.humanize_dna,
    }
    perfect_path = os.path.join(MIDI_DIR, PROJECT + "-perfect.mid")
    humanized_path = os.path.join(MIDI_DIR, PROJECT + "-humanized.mid")
    hz = export_dual(phase2, perfect_path, humanized_path,
                     style=STYLE, seed=hz_seed, bpm=BPM, instruments=hz_instruments)

    # ---- provenance sidecars ----------------------------------------------
    section_midpoints = {}
    for name, bars, prog in SECTIONS:
        mid_idx = bars // 2
        section_midpoints[name] = {"degree": prog[mid_idx],
                                   "chord": DEGREE_NAMES[prog[mid_idx]]}
    prov = {
        "bpm": BPM, "key": "G", "mode": "ionian", "style": STYLE,
        "form": "rondo", "bars": TOTAL_BARS,
        "sections": [s[0] for s in SECTIONS],
        "section_bars": {s[0]: s[1] for s in SECTIONS},
        "section_midpoint_chords": section_midpoints,
        "bar_degrees": BAR_DEGREES,
        "method": "035 Physarum Polycephalum Transport Network Optimization",
        "layer": "concrete", "paradigm": "Nature-Led",
        "physarum": {"food_sources": "bar chord tones + tonic attractor",
                     "streaming": 0.35, "diffusion_sigma": 1.3,
                     "peristalsis_period_slots": 16, "rest_threshold": 0.30,
                     "notes": len(records)},
        "voices": [[v, p, ch] for v, p, ch in
                   zip(VOICES, VOICE_PROGRAMS, VOICE_CHANNELS)],
        "voice_leading_corrections": fixed,
        "humanize_seed": hz_seed, "raw_seed": raw_seed,
        "humanize_profiles": {k: v["profile"] for k, v in hz.items()},
    }
    write_provenance(
        perfect_path, AI_ASSISTED,
        "musicom two-phase (phase=2 rules: tiered chord-tone quantization + "
        "8th grid snap + dedup + voice-leading + 5-voice classical texture) "
        "(method 035 Physarum)",
        sources=[phase1_mid],
        parameters=dict(prov, phase=2, version="perfect", off_grid=0),
        notes="Grid-locked perfect layer (rondo, 20 bars). Method 035 Physarum "
              "(concrete).")
    write_provenance(
        humanized_path, AI_ASSISTED,
        "musicom two-phase (phase=2 + humanization) (method 035 Physarum)",
        sources=[perfect_path],
        parameters=dict(prov, phase=2, version="humanized",
                        humanize_seed=hz_seed,
                        humanize_stats={k: {kk: (float(vv) if isinstance(vv, float) else vv)
                                            for kk, vv in v.items() if kk != "profile"}
                                        for k, v in hz.items()}),
        notes="Humanized layer (style classical + per-instrument string DNA).")

    # ---- grid visualization ------------------------------------------------
    write_grid_visualization(phase2.matrix,
                             os.path.join(ANALYSIS_DIR, "grid_visualization.txt"),
                             voice_names=VOICES, bpm=BPM)

    # ---- size asserts ------------------------------------------------------
    for p in (phase1_mid, perfect_path, humanized_path):
        assert os.path.getsize(p) > 40, f"empty/corrupt: {p}"

    summary = {
        "style": STYLE, "genre": GENRE,
        "method": "035 Physarum Polycephalum Transport Network Optimization",
        "layer": "concrete", "paradigm": "Nature-Led",
        "form": "rondo", "key": KEY_NAME, "bpm": BPM,
        "bars": TOTAL_BARS, "sections": [s[0] for s in SECTIONS],
        "section_bars": [s[1] for s in SECTIONS],
        "physarum": {"streaming": 0.35, "diffusion_sigma": 1.3,
                     "peristalsis_period_slots": 16, "rest_threshold": 0.30,
                     "notes": len(records)},
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
