# -*- coding: utf-8 -*-
"""306-lsystem-fanfare — Fanfare via L-System Algorithmic Composition (method 019).

Nightly composition job (2026-11-15). Selection: style=Fanfare, method=019
L-System (concrete layer), form=cinematic-build (Intro/Build/Rise/Peak/Resolve
= 4/8/8/8/4 bars = 32 bars).

MUSICAL DNA
  - Key Bb major (Ionian) = pc {10,0,2,3,5,7,9}; tonic Bb.
  - 120 BPM, 4/4, 480 TPB, BAR=1920, 8th=240.
  - L-System (D0L, deterministic): alphabet {A,B,C,R}, axiom "C",
    rules A->ABA, B->BC, C->RA, R->R. A=step-up (+1 degree), B=step-down,
    C=leap (+2 degrees), R=rest. Self-similar ternary fanfare contour
    (rise-fall-rise), expanded to >=256 symbols = 32 bars of 8ths.
  - Brass texture: Trumpet lead (L-system melody), French Horn canon
    (rotated string, lower register), Brass Section pad (voice-led triads),
    Tuba bass, Timpani (pitched), Drums (snare/kick/crash march).

TWO-PHASE
  Phase 1 (raw): single-voice L-system walk, unquantized float pitch (seeded
    jitter) + off-grid onsets; own composer + validate() gate.
  Phase 2 (rules): tiered quantize (strong->chord tone, weak->scale tone via
    ScaleQuantizer.tiered_quantize), 8th-grid snap, voice-leading on pad
    triads, register enforcement, 6-voice brass texture.
  Dual-version: export_dual -> -perfect.mid (grid-locked) + -humanized.mid.
"""
import json
import os
import sys
import hashlib

import numpy as np

from structures import MusicUnit, MusicEvent, MidiPercussion
from workflows.unitmatrix_composer import UnitMatrixComposer
from workflows.humanize import export_dual
from workflows.provenance import write_provenance, AI_ASSISTED
from visualization.grid import write_grid_visualization
from rules.progression import Scale7ChordDegree
from rules.voice_leading import VoiceLeadingRules
from sound.synthesis.scale_quantizer import ScaleQuantizer, STRONG_GRID

_INSTR_DIR = "/opt/data/repos/musicom/projects/Instruments"
if _INSTR_DIR not in sys.path:
    sys.path.insert(0, _INSTR_DIR)
from instrument_registry import (  # noqa: E402
    TRUMPET, FRENCH_HORN, BRASS_SECTION, TUBA, TIMPANI, DRUM_KIT)

# ---------------------------------------------------------------------------
# Project layout / identity
# ---------------------------------------------------------------------------
GENRE = "Fanfare"
STYLE = "fanfare"
PROJECT = "306-lsystem-fanfare"
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
TOTAL_BARS = 32
TOTAL_TICKS = TOTAL_BARS * BAR      # 61440
SLOTS_PER_BAR = 8                   # eighths
TOTAL_SLOTS = TOTAL_BARS * SLOTS_PER_BAR  # 256

KEY_NAME = "Bb major (Ionian)"
TONIC_PC = 10                       # Bb
INTERVALS = [0, 2, 4, 5, 7, 9, 11]  # ionian offsets
KEY_PCS = sorted({(TONIC_PC + iv) % 12 for iv in INTERVALS})  # [0,2,3,5,7,9,10]
TONIC_BASE = 46                     # Bb2 (pad/triad reference)
LEAD_BASE = 70                      # Bb4 (trumpet reference)
HORN_BASE = 58                      # Bb3 (horn canon reference)
BASS_BASE = 46                      # Bb2 -> bass root = 34 (Bb1) via -12

# 0-based degree -> triad quality intervals (Bb ionian diatonic)
# 0=Bb, 1=Cm, 2=Dm, 3=Eb, 4=F, 5=Gm, 6=Adim
QUALITY = {0: (0, 4, 7), 1: (0, 3, 7), 2: (0, 3, 7), 3: (0, 4, 7),
           4: (0, 4, 7), 5: (0, 3, 7), 6: (0, 3, 6)}
DEGREE_NAMES = {0: "Bb", 1: "Cm", 2: "Dm", 3: "Eb",
                4: "F", 5: "Gm", 6: "Adim"}

# deterministic seeds
hz_seed = int(hashlib.md5(PROJECT.encode()).hexdigest()[:8], 16) % 100000
raw_seed = 20261115                  # nightly selection seed

# ---------------------------------------------------------------------------
# Form (cinematic-build: Intro/Build/Rise/Peak/Resolve = 4/8/8/8/4 = 32 bars)
# ---------------------------------------------------------------------------
SECTIONS = [
    ("Intro",   4, [0, 0, 0, 0]),            # Bb pedal
    ("Build",   8, [0, 0, 3, 3, 4, 4, 0, 0]), # Bb->Eb->F->Bb
    ("Rise",    8, [3, 3, 4, 4, 5, 5, 4, 4]), # Eb->F->Gm->F (tension)
    ("Peak",    8, [0, 0, 3, 4, 0, 5, 4, 0]), # Bb->Eb->F->Bb->Gm->F->Bb
    ("Resolve", 4, [4, 4, 0, 0]),            # F->Bb (authentic cadence)
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

# bar index -> section name
BAR_TO_SECTION = {}
for name, bars, prog in SECTIONS:
    s0 = SECTION_START[name]
    for b in range(bars):
        BAR_TO_SECTION[s0 + b] = name

VOICES = ["Trumpet", "FrenchHorn", "Brass", "Tuba", "Timpani", "Drums"]
VOICE_PROGRAMS = [TRUMPET.midi_program, FRENCH_HORN.midi_program,
                  BRASS_SECTION.midi_program, TUBA.midi_program,
                  TIMPANI.midi_program, 0]
VOICE_CHANNELS = [0, 1, 2, 3, 4, 9]


# ---------------------------------------------------------------------------
# L-System (method 019)
# ---------------------------------------------------------------------------
L_RULES = {"A": "ABA", "B": "BC", "C": "RA", "R": "R"}
L_AXIOM = "C"
# interpretation: A +1 degree, B -1 degree, C +2 degrees, R = rest
INTERP = {"A": +1, "B": -1, "C": +2, "R": None}


def expand_lsystem(axiom, rules, min_len):
    """Expand a D0L L-system until the string reaches min_len symbols."""
    s = axiom
    while len(s) < min_len:
        s = "".join(rules.get(ch, ch) for ch in s)
    return s


def diatonic(deg_index, base=TONIC_BASE):
    return Scale7ChordDegree.get_diatonic_note(base, INTERVALS, deg_index)


def chord_pcs(d):
    root_pc = (TONIC_PC + INTERVALS[d]) % 12
    return sorted({(root_pc + iv) % 12 for iv in QUALITY[d]})


def chord_tones(d, lo=34, hi=88):
    root_pc = (TONIC_PC + INTERVALS[d]) % 12
    out = set()
    for octv in range(0, 9):
        for iv in QUALITY[d]:
            n = root_pc + 12 * octv + iv
            if lo <= n <= hi:
                out.add(n)
    return sorted(out)


def bar_of_slot(slot):
    return slot // SLOTS_PER_BAR


# ---------------------------------------------------------------------------
# Phase 1: raw single-voice L-system draft (unquantized pitch + off-grid onset)
# ---------------------------------------------------------------------------
def build_phase1(symbols):
    p1 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BPB)
    p1.create_matrix(num_voices=1, num_sections=len(SECTIONS))
    p1.add_voice("RawDraft", program=TRUMPET.midi_program, channel=0)
    for name, bars, prog in SECTIONS:
        p1.add_section(name, bars=bars)

    rng = np.random.default_rng(raw_seed)
    raw_records = []
    degree = 0.0                       # float scale-degree position
    pitch = float(LEAD_BASE)           # float MIDI pitch walk

    per_section_events = {name: [] for name, bars, prog in SECTIONS}

    for slot, sym in enumerate(symbols):
        bar = bar_of_slot(slot)
        sec = BAR_TO_SECTION[bar]
        rel = (slot % SLOTS_PER_BAR) * GRID   # 8th-grid onset (pre-jitter)
        step = INTERP.get(sym)
        if step is None:               # rest
            degree += 0.0
            continue
        degree += float(step)
        degree = max(0.0, min(8.0, degree))
        # raw float pitch: diatonic degree -> semitone, then seeded jitter
        deg_i = int(round(degree))
        base_pitch = diatonic(deg_i, base=LEAD_BASE) + (degree - deg_i) * 2.0
        pitch = base_pitch + float(rng.normal(0.0, 1.5))
        pitch = max(52.0, min(88.0, pitch))
        # off-grid onset jitter + variable duration
        jit = int(rng.integers(-25, 26))
        st = max(0, min(BAR - 30, rel + jit))
        dur = int(rng.integers(180, 420))
        per_section_events[sec].append({
            "tick_abs": bar * BAR + st, "pitch": pitch, "dur": dur,
            "degree": degree, "sym": sym})
        raw_records.append({"tick_abs": bar * BAR + st, "pitch": pitch,
                            "dur": dur, "degree": degree, "sym": sym})

    for name, bars, prog in SECTIONS:
        s_ticks = bars * BAR
        s0 = SECTION_START[name] * BAR
        cell = []
        for r in per_section_events[name]:
            st = r["tick_abs"] - s0
            en = min(s_ticks, st + r["dur"])
            if en <= st:
                en = st + 30
            cell.append(MusicEvent(pitch=int(round(r["pitch"])), volume=86,
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
    return p1, raw_records


# ---------------------------------------------------------------------------
# Phase 2 helpers
# ---------------------------------------------------------------------------
def snap_grid(t, grid=GRID):
    return int(round(t / float(grid)) * grid)


def tiered_pitch(raw_pitch, bar, sq):
    d = BAR_DEGREES[bar]
    onset_strong = (0, 960)  # 4/4 beats 1&3
    # weight from the raw onset grid is approximated here by strong beats;
    # the raw draft's jitter is discarded in phase 2 (grid snap first).
    return sq, d


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


def build_lead_section(name, raw_records, sq):
    """Trumpet lead = L-system melody, tiered-quantized + grid-snapped."""
    nbars = SECTION_BARS[name]
    s_ticks = nbars * BAR
    s0 = SECTION_START[name] * BAR
    ev = []
    for r in raw_records:
        if not (s0 <= r["tick_abs"] < s0 + s_ticks):
            continue
        bar = r["tick_abs"] // BAR
        d = BAR_DEGREES[bar]
        st_glob = snap_grid(r["tick_abs"], GRID)
        st = st_glob - s0
        if st < 0 or st >= s_ticks - 30:
            continue
        weight = "strong" if (st % BAR) in (0, 960) else "weak"
        ct = chord_tones(d, lo=54, hi=86)
        pitch = sq.tiered_quantize(r["pitch"], weight=weight, chord_tones=ct)
        pitch = max(54, pitch)
        dur = int(r["dur"])
        if name == "Resolve":
            dur = max(dur, 300)
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


def build_horn_section(name, raw_records, sq):
    """French Horn canon = rotated L-system, lower register, thinned to 8ths."""
    nbars = SECTION_BARS[name]
    s_ticks = nbars * BAR
    s0 = SECTION_START[name] * BAR
    ev = []
    if name in ("Intro",):
        # pedal fanfare drone Bb3
        ev.append(MusicEvent(pitch=HORN_BASE, volume=72,
                             start_tick=0, end_tick=min(s_ticks - 40, BAR * 2)))
        ev.append(MusicEvent(pitch=HORN_BASE + 7, volume=68,
                             start_tick=BAR * 2, end_tick=s_ticks - 40))
        return ev
    for r in raw_records:
        if not (s0 <= r["tick_abs"] < s0 + s_ticks):
            continue
        bar = r["tick_abs"] // BAR
        d = BAR_DEGREES[bar]
        st_glob = snap_grid(r["tick_abs"], GRID)
        st = st_glob - s0
        if st < 0 or st >= s_ticks - 30:
            continue
        weight = "strong" if (st % BAR) in (0, 960) else "weak"
        # register-shift the raw pitch down by a 4th region (degree -2)
        ct = chord_tones(d, lo=50, hi=74)
        shifted = r["pitch"] - 12.0
        pitch = sq.tiered_quantize(shifted, weight=weight, chord_tones=ct)
        pitch = max(50, min(74, pitch))
        en = min(s_ticks - 20, st + 220)
        ev.append(MusicEvent(pitch=pitch, volume=72, start_tick=st, end_tick=en))
    return ev


def build_pad_section(name, corr_triads):
    nbars = SECTION_BARS[name]
    s_ticks = nbars * BAR
    ev = []
    for bi in range(nbars):
        bar = SECTION_START[name] + bi
        r, th, f = corr_triads[bar]
        bs = bi * BAR
        end = bs + BAR - 30
        for p, v in ((r, 62), (th, 58), (f, 58)):
            ev.append(MusicEvent(pitch=p, volume=v, start_tick=bs,
                                 end_tick=min(end, s_ticks - 30)))
        if name == "Peak":
            ev.append(MusicEvent(pitch=r + 12, volume=54, start_tick=bs,
                                 end_tick=min(bs + BAR - 30, s_ticks - 30)))
    return ev


def build_bass_section(name, corr_triads):
    nbars = SECTION_BARS[name]
    s_ticks = nbars * BAR
    ev = []
    for bi in range(nbars):
        bar = SECTION_START[name] + bi
        r, th, f = corr_triads[bar]
        bs = bi * BAR
        root = r - 12                   # Bb1 region (chord tone, tuba range)
        fifth = f - 12
        ev.append(MusicEvent(pitch=root, volume=80,
                             start_tick=bs, end_tick=bs + BAR - 60))
        ev.append(MusicEvent(pitch=fifth, volume=70,
                             start_tick=bs + 960, end_tick=bs + 960 + 380))
        if name in ("Peak", "Rise"):
            ev.append(MusicEvent(pitch=root, volume=74,
                                 start_tick=bs + 480, end_tick=bs + 480 + 220))
    return ev


def build_timpani_section(name, corr_triads):
    nbars = SECTION_BARS[name]
    s_ticks = nbars * BAR
    ev = []
    for bi in range(nbars):
        bar = SECTION_START[name] + bi
        r, th, f = corr_triads[bar]
        bs = bi * BAR
        # timpani pitch = chord tone of the bar in the 41-55 sweet range
        cands = [t for t in (r - 12, th - 12, f - 12, r - 24, th - 24, f - 24)
                 if 41 <= t <= 55]
        tp = min(cands, key=lambda t: abs(t - 48)) if cands else r - 12
        ev.append(MusicEvent(pitch=tp, volume=78, start_tick=bs,
                             end_tick=bs + 220))
        ev.append(MusicEvent(pitch=tp, volume=64, start_tick=bs + 240,
                             end_tick=bs + 300))
        if name in ("Peak", "Resolve") and bi % 2 == 0:
            # timpani roll (16ths) at climax/cadence
            for k in range(1, 8):
                ev.append(MusicEvent(pitch=tp, volume=52,
                                     start_tick=bs + k * SIXTEENTH,
                                     end_tick=bs + k * SIXTEENTH + 80))
    return ev


def build_drums_section(name):
    nbars = SECTION_BARS[name]
    s_ticks = nbars * BAR
    ev = []
    kick = MidiPercussion.BASS_DRUM
    snare = MidiPercussion.ACOUSTIC_SNARE
    crash = MidiPercussion.CRASH_CYMBAL
    low_tom = MidiPercussion.LOW_TOM
    for bi in range(nbars):
        bs = bi * BAR
        ev.append(MusicEvent(pitch=kick, volume=76, start_tick=bs,
                             end_tick=bs + 80))
        ev.append(MusicEvent(pitch=snare, volume=70, start_tick=bs + 960,
                             end_tick=bs + 1030))
        if name in ("Peak", "Resolve"):
            ev.append(MusicEvent(pitch=snare, volume=60, start_tick=bs + 480,
                                 end_tick=bs + 540))
        if name == "Peak" and bi % 4 == 0:
            ev.append(MusicEvent(pitch=crash, volume=80, start_tick=bs,
                                 end_tick=bs + 220))
        if name == "Resolve" and bi % 2 == 0:
            ev.append(MusicEvent(pitch=low_tom, volume=62, start_tick=bs,
                                 end_tick=bs + 120))
        if name == "Intro":
            ev.append(MusicEvent(pitch=low_tom, volume=56, start_tick=bs + 480,
                                 end_tick=bs + 540))
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


def build_phase2(raw_records, corr_triads, sq):
    comp = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BPB)
    comp.create_matrix(num_voices=len(VOICES), num_sections=len(SECTIONS))
    for name, prog, ch in zip(VOICES, VOICE_PROGRAMS, VOICE_CHANNELS):
        comp.add_voice(name, program=prog, channel=ch)
    for name, bars, prog in SECTIONS:
        comp.add_section(name, bars=bars)

    for name, bars, prog in SECTIONS:
        s_ticks = bars * BAR
        comp.fill_voice_section("Trumpet", name,
                                seal(build_lead_section(name, raw_records, sq), s_ticks))
        comp.fill_voice_section("FrenchHorn", name,
                                seal(build_horn_section(name, raw_records, sq), s_ticks))
        comp.fill_voice_section("Brass", name,
                                seal(build_pad_section(name, corr_triads), s_ticks))
        comp.fill_voice_section("Tuba", name,
                                seal(build_bass_section(name, corr_triads), s_ticks))
        comp.fill_voice_section("Timpani", name,
                                seal(build_timpani_section(name, corr_triads), s_ticks))
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
    # ---- L-system expansion ------------------------------------------------
    symbols = expand_lsystem(L_AXIOM, L_RULES, TOTAL_SLOTS)[:TOTAL_SLOTS]
    print("L-SYSTEM len=", len(symbols),
          "counts=", {c: symbols.count(c) for c in "ABCR"})

    # ---- Phase 1 raw draft -------------------------------------------------
    phase1, raw_records = build_phase1(symbols)
    phase1_mid = os.path.join(MIDI_DIR, PROJECT + "-phase1.mid")
    phase1.to_midi(phase1_mid)
    write_provenance(
        phase1_mid, AI_ASSISTED,
        "musicom.lsystem_phase1",
        parameters={"bpm": BPM, "bars": TOTAL_BARS, "seed": raw_seed,
                    "phase": 1, "quantized": False, "key": KEY_NAME,
                    "form": "cinematic-build", "style": STYLE,
                    "method": "019 L-System Algorithmic Composition",
                    "layer": "concrete",
                    "lsystem": {"axiom": L_AXIOM, "rules": L_RULES,
                                "alphabet": "ABCR",
                                "interpretation": "A=+1,B=-1,C=+2,R=rest",
                                "symbols": len(symbols)},
                    "notes": len(raw_records),
                    "rules_applied": "NONE (pre-rules)"},
        notes="Raw L-system draft: single trumpet voice, unquantized float "
              "pitch (seeded jitter) + off-grid onsets, 32 bars, pre-rules. "
              "Method 019 (concrete).")
    write_grid_visualization(phase1.matrix,
                             os.path.join(ANALYSIS_DIR,
                                          "grid_visualization_phase1.txt"),
                             voice_names=["RawDraft"], bpm=BPM)
    print("PHASE1_OK", "raw_notes=", len(raw_records))

    # ---- Phase 2 rules + texture -------------------------------------------
    bar_triads = [sorted([diatonic(d, base=TONIC_BASE),
                          diatonic(d + 2, base=TONIC_BASE),
                          diatonic(d + 4, base=TONIC_BASE)])
                  for d in BAR_DEGREES]
    vl = VoiceLeadingRules(style="classical")
    opt_triads = vl.optimize_voice_leading(bar_triads)
    corr_triads, fixed = correct_voice_leading(opt_triads)
    print(f"[voicing] corrected {fixed} chord(s)")

    sq = ScaleQuantizer(root=LEAD_BASE, scale="major")
    phase2 = build_phase2(raw_records, corr_triads, sq)

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
        "Trumpet": TRUMPET.humanize_dna,
        "FrenchHorn": FRENCH_HORN.humanize_dna,
        "Brass": BRASS_SECTION.humanize_dna,
        "Tuba": TUBA.humanize_dna,
        "Timpani": TIMPANI.humanize_dna,
        "Drums": DRUM_KIT.humanize_dna,
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
        "bpm": BPM, "key": "Bb", "mode": "ionian", "style": STYLE,
        "form": "cinematic-build", "bars": TOTAL_BARS,
        "sections": [s[0] for s in SECTIONS],
        "section_bars": {s[0]: s[1] for s in SECTIONS},
        "section_midpoint_chords": section_midpoints,
        "bar_degrees": BAR_DEGREES,
        "method": "019 L-System Algorithmic Composition", "layer": "concrete",
        "paradigm": "Rules-Based",
        "lsystem": {"axiom": L_AXIOM, "rules": L_RULES,
                    "interpretation": "A=+1 deg, B=-1 deg, C=+2 deg, R=rest",
                    "symbols": len(symbols),
                    "symbol_counts": {c: symbols.count(c) for c in "ABCR"}},
        "voices": [[v, p, ch] for v, p, ch in
                   zip(VOICES, VOICE_PROGRAMS, VOICE_CHANNELS)],
        "voice_leading_corrections": fixed,
        "humanize_seed": hz_seed, "raw_seed": raw_seed,
        "humanize_profiles": {k: v["profile"] for k, v in hz.items()},
    }
    write_provenance(
        perfect_path, AI_ASSISTED,
        "musicom two-phase (phase=2 rules: tiered chord-tone quantization + "
        "8th grid snap + dedup + voice-leading + 6-voice brass texture) "
        "(method 019 L-System)",
        sources=[phase1_mid],
        parameters=dict(prov, phase=2, version="perfect", off_grid=0),
        notes="Grid-locked perfect layer (cinematic-build, 32 bars). "
              "Method 019 L-System (concrete).")
    write_provenance(
        humanized_path, AI_ASSISTED,
        "musicom two-phase (phase=2 + humanization) (method 019 L-System)",
        sources=[perfect_path],
        parameters=dict(prov, phase=2, version="humanized",
                        humanize_seed=hz_seed,
                        humanize_stats={k: {kk: (float(vv) if isinstance(vv, float) else vv)
                                            for kk, vv in v.items() if kk != "profile"}
                                        for k, v in hz.items()}),
        notes="Humanized layer (style fanfare + per-instrument brass DNA).")

    # ---- grid visualization ------------------------------------------------
    write_grid_visualization(phase2.matrix,
                             os.path.join(ANALYSIS_DIR, "grid_visualization.txt"),
                             voice_names=VOICES, bpm=BPM)

    # ---- size asserts ------------------------------------------------------
    for p in (phase1_mid, perfect_path, humanized_path):
        assert os.path.getsize(p) > 40, f"empty/corrupt: {p}"

    summary = {
        "style": STYLE, "genre": GENRE,
        "method": "019 L-System Algorithmic Composition", "layer": "concrete",
        "form": "cinematic-build", "key": KEY_NAME, "bpm": BPM,
        "bars": TOTAL_BARS, "sections": [s[0] for s in SECTIONS],
        "section_bars": [s[1] for s in SECTIONS],
        "lsystem": {"axiom": L_AXIOM, "rules": L_RULES,
                    "symbols": len(symbols),
                    "symbol_counts": {c: symbols.count(c) for c in "ABCR"}},
        "raw_notes": len(raw_records),
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
