# -*- coding: utf-8 -*-
"""309-celtic-sieve-set -- Celtic reel-set via Xenakis Sieve Theory (method 025).

Nightly composition job (2026-11-17). Selection: style=Celtic, method=025
Xenakis Sieve Theory (Rules-Based, concrete layer), form=through-composed
(pick_form("celtic") -> S1..S6, bars [4,4,4,4,4,4] = 24 bars).

MUSICAL DNA
  - Key D Mixolydian = pc {2,4,6,7,9,11,0}; tonic D (the Irish reel mode).
  - 120 BPM, 4/4, 480 TPB, BAR=1920, 8th=240, 16th=120.
  - Method 025 Xenakis Sieve: pitch = modular congruence subset of chromatic
    space (e.g. mod-4 residues {0,2} -> whole-tone hexachord); rhythm = modular
    congruence subset of the 16th grid. Each of the 6 sections uses a distinct
    pitch-sieve + rhythm-sieve (a "sieve set" = tune-set of sieve variations).
  - Celtic 5-voice texture: Violin fiddle lead (sieve melody), Flute canon
    (octave-down, +1 beat, thinned), Bagpipe regulator-style sustained
    chord-root+fifth, Harp broken-chord ripple, Double Bass root/fifth.

TWO-PHASE
  Phase 1 (raw): single-voice sieve walk, unquantized float pitch (jitter) +
    off-grid onsets; own composer + validate() gate.
  Phase 2 (rules): tiered quantize (strong->chord tone, weak->scale tone via
    ScaleQuantizer.tiered_quantize), 8th-grid snap, voice-leading on the pad
    triads, register enforcement, 5-voice Celtic texture.
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
    VIOLIN, FLUTE, BAGPIPE, HARP, DOUBLE_BASS)

# ---------------------------------------------------------------------------
# Project layout / identity
# ---------------------------------------------------------------------------
GENRE = "Celtic"
STYLE = "celtic"
PROJECT = "309-celtic-sieve-set"
BASE = os.path.join("/opt/data/projects/Styles", GENRE, PROJECT)
MIDI_DIR = os.path.join(BASE, "MIDI")
AUDIO_DIR = os.path.join(BASE, "Audio")
ANALYSIS_DIR = os.path.join(BASE, "Analysis")
for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
    os.makedirs(d, exist_ok=True)

BPM = 120
TPB = 480
BPB = 4
BAR = TPB * BPB                     # 1920
GRID = 240                          # 8th (snap target)
SIXTEENTH = 120
QUARTER = 480
TOTAL_BARS = 24
TOTAL_TICKS = TOTAL_BARS * BAR      # 46080
SLOTS_PER_BAR = 16

KEY_NAME = "D Mixolydian"
TONIC_PC = 2                        # D
INTERVALS = [0, 2, 4, 5, 7, 9, 10]  # mixolydian step pattern
KEY_PCS = sorted({(TONIC_PC + iv) % 12 for iv in INTERVALS})  # [0,2,4,6,7,9,11]
TONIC_BASE = 50                     # D3 (triad/pad reference)

# 0-based degree -> triad quality intervals (D mixolydian diatonic)
# 0=D, 1=Em, 2=F#dim, 3=G, 4=Am, 5=Bm, 6=C(bVII)
QUALITY = {0: (0, 4, 7), 1: (0, 3, 7), 2: (0, 3, 6), 3: (0, 4, 7),
           4: (0, 3, 7), 5: (0, 3, 7), 6: (0, 4, 7)}
DEGREE_NAMES = {0: "D", 1: "Em", 2: "F#dim", 3: "G",
                4: "Am", 5: "Bm", 6: "C"}

# deterministic seeds
hz_seed = int(hashlib.md5(PROJECT.encode()).hexdigest()[:8], 16) % 100000
raw_seed = 20261117

# ---------------------------------------------------------------------------
# Form (through-composed: S1..S6 = 4 bars each = 24)
# ---------------------------------------------------------------------------
SECTIONS = [
    ("S1", 4, [0, 0, 3, 0]),          # D D G D    (tonic area)
    ("S2", 4, [3, 0, 4, 0]),          # G D Am D   (lift to IV, minor-v cadence)
    ("S3", 4, [1, 0, 3, 4]),          # Em D G Am  (ii motion)
    ("S4", 4, [5, 3, 0, 4]),          # Bm G D Am  (vi -> IV)
    ("S5", 4, [3, 1, 5, 4]),          # G Em Bm Am (sequential chain)
    ("S6", 4, [0, 3, 4, 0]),          # D G Am D   (authentic-ish cadence)
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

VOICES = ["Violin", "Flute", "Bagpipe", "Harp", "DoubleBass"]
VOICE_PROGRAMS = [VIOLIN.midi_program, FLUTE.midi_program, BAGPIPE.midi_program,
                  HARP.midi_program, DOUBLE_BASS.midi_program]
VOICE_CHANNELS = [0, 1, 2, 3, 4]

# register windows per voice
VIOLIN_LO, VIOLIN_HI = 67, 96
FLUTE_LO, FLUTE_HI = 60, 84
BAGPIPE_LO, BAGPIPE_HI = 50, 74
HARP_LO, HARP_HI = 55, 88
BASS_LO, BASS_HI = 40, 55

# Xenakis sieves per section: pitch = (modulus, residues) over chromatic pc
# space; rhythm = (modulus, residues) over the 16th-step grid.
SIEVES = {
    "S1": {"pitch_mod": 4, "pitch_res": [0, 2], "rhythm_mod": 4, "rhythm_res": [0, 3], "dir": +1},
    "S2": {"pitch_mod": 3, "pitch_res": [0, 1], "rhythm_mod": 3, "rhythm_res": [0, 2], "dir": -1},
    "S3": {"pitch_mod": 5, "pitch_res": [0, 2], "rhythm_mod": 5, "rhythm_res": [0, 2], "dir": +1},
    "S4": {"pitch_mod": 4, "pitch_res": [1, 3], "rhythm_mod": 4, "rhythm_res": [1, 2], "dir": +1},
    "S5": {"pitch_mod": 3, "pitch_res": [0, 2], "rhythm_mod": 3, "rhythm_res": [0],   "dir": -1},
    "S6": {"pitch_mod": 7, "pitch_res": [0, 4], "rhythm_mod": 4, "rhythm_res": [0, 3], "dir": +1},
}


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
# Method 025: Xenakis Sieve -- Phase 1 raw draft
# ---------------------------------------------------------------------------
def sieve_pitches(lo, hi, modulus, residues):
    """All MIDI pitches in [lo, hi] satisfying the modular sieve."""
    return [p for p in range(lo, hi + 1) if (p % modulus) in residues]


def simulate_sieve(rng):
    """Walk each section's pitch sieve over its rhythm sieve -> raw line."""
    records = []
    for name, bars, prog in SECTIONS:
        sv = SIEVES[name]
        pm, pres = sv["pitch_mod"], sv["pitch_res"]
        rm, rres = sv["rhythm_mod"], sv["rhythm_res"]
        allowed = sieve_pitches(VIOLIN_LO, VIOLIN_HI, pm, pres)
        if sv["dir"] < 0:
            allowed = allowed[::-1]
        steps = bars * SLOTS_PER_BAR          # 64 sixteenths per 4-bar section
        s0 = SECTION_START[name]
        pi = 0
        for step in range(steps):
            if (step % rm) not in rres:        # rhythm sieve: only these sound
                continue
            bar_off = step // SLOTS_PER_BAR
            sixteenth = step % SLOTS_PER_BAR
            base_tick = (s0 + bar_off) * BAR + sixteenth * SIXTEENTH
            jit = int(rng.integers(-25, 26))   # raw off-grid character
            tick_abs = max(0, min(TOTAL_TICKS - 30, base_tick + jit))
            p = float(allowed[pi % len(allowed)]) + float(rng.normal(0.0, 0.4))
            pi += 1
            dur = int(rng.integers(160, 360))
            vel = int(rng.integers(70, 100))
            records.append({"tick_abs": tick_abs, "pitch": p, "dur": dur,
                            "vel": vel, "bar": s0 + bar_off, "degree": prog[bar_off]})
    return records


def build_phase1(records):
    p1 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BPB)
    p1.create_matrix(num_voices=1, num_sections=len(SECTIONS))
    p1.add_voice("RawSieve", program=VIOLIN.midi_program, channel=0)
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
            if st < 0:
                st = 0                    # negative jitter at section seam -> clamp
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
        p1.fill_voice_section("RawSieve", name, MusicUnit(events=cell))
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


def build_violin_section(name, records, sq):
    """Violin fiddle lead = sieve path, tiered-quantized + 8th-grid snapped."""
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
        bar = st_glob // BAR          # snapped bar (snap may cross a seam)
        d = BAR_DEGREES[bar]
        weight = weight_of(st)
        ct = chord_tones(d, VIOLIN_LO, VIOLIN_HI)
        pitch = sq.tiered_quantize(r["pitch"], weight=weight, chord_tones=ct)
        pitch = max(VIOLIN_LO, min(VIOLIN_HI, pitch))
        dur = int(r["dur"])
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
    """Flute canon = sieve path -12 (octave down), +1 beat, thinned 1/2."""
    nbars = SECTION_BARS[name]
    s_ticks = nbars * BAR
    s0 = SECTION_START[name] * BAR
    ev = []
    cnt = 0
    for r in records:
        if not (s0 <= r["tick_abs"] < s0 + s_ticks):
            continue
        cnt += 1
        if cnt % 2 == 0:                 # thin the canon
            continue
        st_glob = snap_grid(r["tick_abs"] + QUARTER, GRID)   # +1 beat delay
        st = st_glob - s0
        if st < 0 or st >= s_ticks - 30:
            continue
        bar = st_glob // BAR
        d = BAR_DEGREES[bar]
        weight = weight_of(st)
        ct = chord_tones(d, FLUTE_LO, FLUTE_HI)
        pitch = sq.tiered_quantize(r["pitch"] - 12.0, weight=weight, chord_tones=ct)
        pitch = max(FLUTE_LO, min(FLUTE_HI, pitch))
        en = min(s_ticks - 20, st + 240)
        ev.append(MusicEvent(pitch=pitch, volume=70, start_tick=st, end_tick=en))
    return ev


def build_bagpipe_section(name, corr_triads):
    """Bagpipe regulator-style sustained chord root+fifth (voice-led)."""
    nbars = SECTION_BARS[name]
    s_ticks = nbars * BAR
    ev = []
    for bi in range(nbars):
        bar = SECTION_START[name] + bi
        r, th, f = corr_triads[bar]
        bs = bi * BAR
        end = min(bs + BAR - 40, s_ticks - 40)
        root = to_register(r, BAGPIPE_LO, BAGPIPE_HI)
        fifth = to_register(f, BAGPIPE_LO, BAGPIPE_HI)
        ev.append(MusicEvent(pitch=root, volume=68, start_tick=bs, end_tick=end))
        ev.append(MusicEvent(pitch=fifth, volume=58, start_tick=bs, end_tick=end))
    return ev


def build_harp_section(name, corr_triads):
    """Harp = Celtic broken-chord ripple (r f th oct th f r f, 8th grid)."""
    nbars = SECTION_BARS[name]
    s_ticks = nbars * BAR
    ev = []
    for bi in range(nbars):
        bar = SECTION_START[name] + bi
        r, th, f = corr_triads[bar]
        bs = bi * BAR
        octv = r + 12
        seq = [r, f, th, octv, th, f, r, f]
        offs = [0, 240, 480, 720, 960, 1200, 1440, 1680]
        for p, off in zip(seq, offs):
            p = to_register(p, HARP_LO, HARP_HI)
            ev.append(MusicEvent(pitch=p, volume=62,
                                 start_tick=bs + off, end_tick=bs + off + 220))
    return ev


def build_bass_section(name, corr_triads):
    """Double bass = root (beat 1) + fifth (beat 3), sustained."""
    nbars = SECTION_BARS[name]
    s_ticks = nbars * BAR
    ev = []
    for bi in range(nbars):
        bar = SECTION_START[name] + bi
        r, th, f = corr_triads[bar]
        bs = bi * BAR
        root = to_register(r - 12, BASS_LO, BASS_HI)
        fifth = to_register(f - 12, BASS_LO, BASS_HI)
        ev.append(MusicEvent(pitch=root, volume=80,
                             start_tick=bs, end_tick=bs + BAR - 60))
        ev.append(MusicEvent(pitch=fifth, volume=66,
                             start_tick=bs + 960, end_tick=bs + 960 + 380))
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
        comp.fill_voice_section("Bagpipe", name,
                                seal(build_bagpipe_section(name, corr_triads), s_ticks))
        comp.fill_voice_section("Harp", name,
                                seal(build_harp_section(name, corr_triads), s_ticks))
        comp.fill_voice_section("DoubleBass", name,
                                seal(build_bass_section(name, corr_triads), s_ticks))
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
    records = simulate_sieve(rng)
    print("SIEVE notes=", len(records))
    # per-section raw note count
    for name, bars, prog in SECTIONS:
        n = sum(1 for r in records if BAR_TO_SECTION[r["bar"]] == name)
        print(f"  {name}: {n} raw notes")

    # ---- Phase 1 raw draft -------------------------------------------------
    phase1 = build_phase1(records)
    phase1_mid = os.path.join(MIDI_DIR, PROJECT + "-phase1.mid")
    phase1.to_midi(phase1_mid)
    write_provenance(
        phase1_mid, AI_ASSISTED,
        "musicom.xenakis_sieve_phase1",
        parameters={"bpm": BPM, "bars": TOTAL_BARS, "seed": raw_seed,
                    "phase": 1, "quantized": False, "key": KEY_NAME,
                    "form": "through-composed", "style": STYLE,
                    "method": "025 Xenakis Sieve Theory",
                    "layer": "concrete", "paradigm": "Rules-Based",
                    "sieves": SIEVES,
                    "notes": len(records),
                    "rules_applied": "NONE (pre-rules)"},
        notes="Raw Xenakis sieve draft: single violin voice, unquantized "
              "float pitch (modular-congruence sieve walk + jitter) + "
              "off-grid onsets, 24 bars, pre-rules. Method 025 (concrete).")
    write_grid_visualization(phase1.matrix,
                             os.path.join(ANALYSIS_DIR,
                                          "grid_visualization_phase1.txt"),
                             voice_names=["RawSieve"], bpm=BPM)
    print("PHASE1_OK", "raw_notes=", len(records))

    # ---- Phase 2 rules + texture -------------------------------------------
    bar_triads = [triad(d, base=TONIC_BASE) for d in BAR_DEGREES]
    vl = VoiceLeadingRules(style="classical")
    opt_triads = vl.optimize_voice_leading(bar_triads)
    corr_triads, fixed = correct_voice_leading(opt_triads)
    print(f"[voicing] corrected {fixed} chord(s)")

    sq = ScaleQuantizer(root=TONIC_BASE, scale="mixolydian")
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
        "Bagpipe": BAGPIPE.humanize_dna,
        "Harp": HARP.humanize_dna,
        "DoubleBass": DOUBLE_BASS.humanize_dna,
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
        "bpm": BPM, "key": "D", "mode": "mixolydian", "style": STYLE,
        "form": "through-composed", "bars": TOTAL_BARS,
        "sections": [s[0] for s in SECTIONS],
        "section_bars": {s[0]: s[1] for s in SECTIONS},
        "section_midpoint_chords": section_midpoints,
        "bar_degrees": BAR_DEGREES,
        "method": "025 Xenakis Sieve Theory",
        "layer": "concrete", "paradigm": "Rules-Based",
        "sieves": SIEVES,
        "voices": [[v, p, ch] for v, p, ch in
                   zip(VOICES, VOICE_PROGRAMS, VOICE_CHANNELS)],
        "voice_leading_corrections": fixed,
        "humanize_seed": hz_seed, "raw_seed": raw_seed,
        "humanize_profiles": {k: v["profile"] for k, v in hz.items()},
    }
    write_provenance(
        perfect_path, AI_ASSISTED,
        "musicom two-phase (phase=2 rules: tiered chord-tone quantization + "
        "8th grid snap + dedup + voice-leading + 5-voice Celtic texture) "
        "(method 025 Xenakis Sieve)",
        sources=[phase1_mid],
        parameters=dict(prov, phase=2, version="perfect", off_grid=0),
        notes="Grid-locked perfect layer (through-composed, 24 bars). "
              "Method 025 Xenakis Sieve (concrete).")
    write_provenance(
        humanized_path, AI_ASSISTED,
        "musicom two-phase (phase=2 + humanization) (method 025 Xenakis Sieve)",
        sources=[perfect_path],
        parameters=dict(prov, phase=2, version="humanized",
                        humanize_seed=hz_seed,
                        humanize_stats={k: {kk: (float(vv) if isinstance(vv, float) else vv)
                                            for kk, vv in v.items() if kk != "profile"}
                                        for k, v in hz.items()}),
        notes="Humanized layer (style celtic + per-instrument DNA).")

    # ---- grid visualization ------------------------------------------------
    write_grid_visualization(phase2.matrix,
                             os.path.join(ANALYSIS_DIR, "grid_visualization.txt"),
                             voice_names=VOICES, bpm=BPM)

    # ---- size asserts ------------------------------------------------------
    for p in (phase1_mid, perfect_path, humanized_path):
        assert os.path.getsize(p) > 40, f"empty/corrupt: {p}"

    summary = {
        "style": STYLE, "genre": GENRE,
        "method": "025 Xenakis Sieve Theory",
        "layer": "concrete", "paradigm": "Rules-Based",
        "form": "through-composed", "key": KEY_NAME, "bpm": BPM,
        "bars": TOTAL_BARS, "sections": [s[0] for s in SECTIONS],
        "section_bars": [s[1] for s in SECTIONS],
        "sieves": SIEVES,
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
