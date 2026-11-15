# -*- coding: utf-8 -*-
"""305-minimalism-phase-variations — Minimalism rework of 001-minimalism-phase-study.

Nightly rework job (2026-11-15). Source: 001-minimalism-phase-study (Minimalism,
Steve Reich "Clapping Music"-style phase piece, E(5,12) Euclidean marimba cell,
two marimba voices phase-walking +1 beat/section).

Audit result: standards 1-4 pass (engine=UnitMatrixComposer, zero-drift 5x46080,
grid-sync 0 off-grid, 5-voice setup). Standards 5-6 FAIL -> REDESIGN
(two-phase artifacts missing, index.html missing, no dual-version export).

Identity preserved from source (redesign keeps DNA, discards non-compliant code):
  genre Minimalism · key C major (source C pentatonic DNA C D E G A re-expressed
  as chord-tone arpeggios under the rules layer) · 120 BPM · 4/4 · 480 TPB ·
  BAR 1920 · E(5,12) Euclidean cell (5 pulses / 12 quarter steps) · two marimba
  voices phase-walking · pad + bass pedal + sparse percussion.

Extended + varied (32 bars, 10 sections, was 24 bars / 8 sections):
  Intro(2) Phase1(4) Phase2(4) Phase3(4) Phase4(4) Phase5(4) Bridge(4)
  Phase6(2) Resolve(2) Coda(2).

Variation techniques (7, each key-safe in C major):
  T1 PHASE-WALK      (identity) MarimbaB rotates the E(5,12) cell +1 beat/section.
  T2 RETROGRADE      Phase5: MarimbaB pitch sequence reversed.
  T3 INVERSION       Bridge: MarimbaB mirrored around axis C5 (=72).
  T4 AUGMENTATION    Coda: MarimbaB durations x2 -> spacious fade.
  T5 REGISTER SHIFT  Phase4 +12 / Intro-Resolve-Coda -12.
  T6 DENSITY/DIMINUTION Phase4+Phase6: MarimbaA cell step 8th-note (x2 density).
  T7 RELATIVE-MINOR  Bridge: harmonic center re-orients to vi (Am) region.

Two-phase architecture:
  Phase 1 (raw): E(5,12) phase cell, single marimba voice, unquantized float
    pitch (seeded random walk) + off-grid onsets (jitter), own composer +
    validate() gate.
  Phase 2 (rules): per-bar chord-tone quantization (floor bar attribution),
    8th-grid snap + dedup, voice-leading optimization (pad triads), register
    enforcement, 5-voice texture + variation techniques.
  Dual-version contract: export_dual -> -perfect.mid (grid-locked) +
    -humanized.mid (style minimalism + per-instrument DNA).
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

_INSTR_DIR = "/opt/data/repos/musicom/projects/Instruments"
if _INSTR_DIR not in sys.path:
    sys.path.insert(0, _INSTR_DIR)
from instrument_registry import MARIMBA, STRING_ENSEMBLE, ACOUSTIC_BASS  # noqa: E402

# ---------------------------------------------------------------------------
# Project layout / identity
# ---------------------------------------------------------------------------
GENRE = "Minimalism"
STYLE = "minimalism"
PROJECT = "305-minimalism-phase-variations"
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
GRID = 120                          # 16th
EIGHTH = 240                        # 8th
QUARTER = 480                       # quarter
TOTAL_BARS = 32
TOTAL_TICKS = TOTAL_BARS * BAR      # 61440

KEY_NAME = "C major (Ionian)"
TONIC_PC = 0                        # C
KEY_PCS = {0, 2, 4, 5, 7, 9, 11}    # C D E F G A B
INTERVALS = [0, 2, 4, 5, 7, 9, 11]  # ionian offsets from C
TONIC_BASE = 60                     # C4 (pad reference)
MARIMBA_BASE = 72                   # C5 (marimba reference)
AXIS = 72                           # inversion axis C5

# 0-based degree -> triad quality intervals (C ionian diatonic)
# 0=C, 1=Dm, 2=Em, 3=F, 4=G, 5=Am, 6=Bdim
QUALITY = {0: (0, 4, 7), 1: (0, 3, 7), 2: (0, 3, 7), 3: (0, 4, 7),
           4: (0, 4, 7), 5: (0, 3, 7), 6: (0, 3, 6)}
DEGREE_NAMES = {0: "C", 1: "Dm", 2: "Em", 3: "F", 4: "G", 5: "Am", 6: "Bdim"}

# deterministic seeds
hz_seed = int(hashlib.md5(PROJECT.encode()).hexdigest()[:8], 16) % 100000
raw_seed = 20261115                  # nightly selection seed

# ---------------------------------------------------------------------------
# Form (32 bars, 10 sections). (name, bars, per-bar 0-based degrees)
# ---------------------------------------------------------------------------
SECTIONS = [
    ("Intro",   2, [0, 0]),          # i i
    ("Phase1",  4, [0, 0, 0, 0]),    # unison (phase 0) static i
    ("Phase2",  4, [0, 3, 0, 5]),    # i IV i vi
    ("Phase3",  4, [0, 4, 0, 3]),    # i V i IV
    ("Phase4",  4, [0, 1, 4, 0]),    # i ii V i  (peak)
    ("Phase5",  4, [5, 4, 1, 5]),    # vi V ii vi
    ("Bridge",  4, [5, 1, 5, 0]),    # vi ii vi i (vi-centric)
    ("Phase6",  2, [4, 5]),          # V vi
    ("Resolve", 2, [0, 0]),          # i i
    ("Coda",    2, [0, 0]),          # i i
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

# MarimbaB phase-walk offset in quarter-step units per section
PHASE_BEATS = {"Intro": 0, "Phase1": 0, "Phase2": 1, "Phase3": 2,
               "Phase4": 3, "Phase5": 4, "Bridge": 5, "Phase6": 6,
               "Resolve": 0, "Coda": 0}
# register shift (semitones) per section
SECTION_OCT = {"Intro": -12, "Phase1": 0, "Phase2": 0, "Phase3": 0,
               "Phase4": 12, "Phase5": 0, "Bridge": 0, "Phase6": 0,
               "Resolve": -12, "Coda": -12}
# MarimbaA cell step: quarter normally, 8th for density/diminution sections
CELL_STEP = {"Phase4": EIGHTH, "Phase6": EIGHTH}
# MarimbaB pitch transform per section
SECTION_LEAD_TRANSFORM = {"Phase5": "retrograde", "Bridge": "inversion"}
# MarimbaB duration mode per section
SECTION_LEAD_DUR = {"Coda": "augment"}
# variation technique per section (for provenance + REPORT)
SECTION_TECHNIQUE = {
    "Intro": "register-shift (-12), MarimbaA only",
    "Phase1": "baseline unison (phase 0)",
    "Phase2": "phase-walk +1 beat",
    "Phase3": "phase-walk +2 beats",
    "Phase4": "phase-walk +3 + register-shift (+12) + density-rise (8th cell)",
    "Phase5": "phase-walk +4 + retrograde",
    "Bridge": "phase-walk +5 + inversion counter-line + relative-minor (vi)",
    "Phase6": "phase-walk +6 + diminution (8th cell)",
    "Resolve": "phase re-lock + register-shift (-12)",
    "Coda": "augmentation (dur x2) fade",
}

VOICES = ["MarimbaA", "MarimbaB", "Pad", "Bass", "Drums"]
VOICE_PROGRAMS = [MARIMBA.midi_program, MARIMBA.midi_program,
                  STRING_ENSEMBLE.midi_program, ACOUSTIC_BASS.midi_program, 0]
VOICE_CHANNELS = [0, 1, 2, 3, 9]


# ---------------------------------------------------------------------------
# Euclidean + diatonic / chord helpers
# ---------------------------------------------------------------------------
def euclidean(pulses, steps):
    out = []
    bucket = 0.0
    for _ in range(steps):
        bucket += pulses
        if bucket >= steps:
            bucket -= steps
            out.append(True)
        else:
            out.append(False)
    return out


def diatonic(deg_index, base=MARIMBA_BASE):
    return Scale7ChordDegree.get_diatonic_note(base, INTERVALS, deg_index)


def chord_tones(d, lo=36, hi=96):
    root_pc = (TONIC_PC + INTERVALS[d]) % 12
    out = set()
    for octv in range(-3, 11):
        for iv in QUALITY[d]:
            n = root_pc + 12 * octv + iv
            if lo <= n <= hi:
                out.add(n)
    return sorted(out)


def chord_pcs(d):
    root_pc = (TONIC_PC + INTERVALS[d]) % 12
    return sorted({(root_pc + iv) % 12 for iv in QUALITY[d]})


def quantize_to_chord_tone(raw_pitch, d, lo=55, hi=96):
    cands = chord_tones(d, lo=lo, hi=hi)
    if not cands:
        cands = [int(round(raw_pitch))]
    return min(cands, key=lambda c: abs(c - raw_pitch))


def snap_grid(t, grid=EIGHTH):
    return int(round(t / float(grid)) * grid)


def bar_arpeggio(d, octave=0):
    """5 ascending chord tones (root 3rd 5th octave 10th) from degree d.

    Each candidate is snapped to the NEAREST chord tone of the bar's degree so
    a register shift can never clamp to a foreign pitch-class (e.g. clamping
    100 -> C7 would break a Dm bar)."""
    base = MARIMBA_BASE + octave
    cands = [diatonic(d, base), diatonic(d + 2, base), diatonic(d + 4, base),
             diatonic(d + 7, base), diatonic(d + 9, base)]
    tones = chord_tones(d, lo=48, hi=96)
    out = []
    for c in cands:
        out.append(min(tones, key=lambda t: abs(t - c)))
    return out


def cell_hits(s_ticks, phase_steps=0, step=QUARTER):
    """E(5,12) cell onsets in [0, s_ticks), rotated by phase_steps steps."""
    pattern = euclidean(5, 12)
    nsteps = s_ticks // step
    out = []
    for i in range(nsteps):
        idx = phase_steps + i
        if pattern[idx % 12]:
            out.append(i * step)
    return out


# ---------------------------------------------------------------------------
# Phase 1: raw single-voice draft (E(5,12) phase cell, unquantized)
# ---------------------------------------------------------------------------
def build_phase1():
    p1 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BPB)
    p1.create_matrix(num_voices=1, num_sections=len(SECTIONS))
    p1.add_voice("RawDraft", program=MARIMBA.midi_program, channel=0)
    for name, bars, prog in SECTIONS:
        p1.add_section(name, bars=bars)

    rng = np.random.default_rng(raw_seed)
    raw_records = []
    pitch_walk = 72.0
    for name, bars, prog in SECTIONS:
        s0 = SECTION_START[name] * BAR
        s_ticks = bars * BAR
        phase = PHASE_BEATS[name]
        cell = []
        for t0 in cell_hits(s_ticks, phase, step=QUARTER):
            j = int(rng.integers(-40, 41))              # off-grid jitter
            st = max(0, min(s_ticks - 30, t0 + j))
            pitch_walk += float(rng.normal(0, 2.5))     # unquantized float walk
            pitch_walk = max(55.0, min(96.0, pitch_walk))
            dur = int(rng.integers(200, 600))
            en = min(s_ticks, st + dur)
            if en <= st:
                en = st + 30
            cell.append(MusicEvent(pitch=int(round(pitch_walk)), volume=86,
                                   start_tick=st, end_tick=en))
            raw_records.append({"tick_abs": s0 + st, "pitch": pitch_walk,
                                "dur": dur})
        cell.sort(key=lambda e: (e.start_tick, e.end_tick))
        if not cell or cell[-1].end_tick < s_ticks:
            cell.append(MusicEvent(pitch=0, volume=0,
                                   start_tick=cell[-1].end_tick if cell else 0,
                                   end_tick=s_ticks))
        p1.fill_voice_section("RawDraft", name, MusicUnit(events=cell))
    ok, msg = p1.validate()
    if not ok:
        raise RuntimeError(f"phase1 validate failed: {msg}")
    return p1, raw_records


# ---------------------------------------------------------------------------
# Phase 2: rules + variation techniques
# ---------------------------------------------------------------------------
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


def build_marimbaA_section(name):
    """Fixed anchor cell: E(5,12), pitch = ascending chord-tone arpeggio."""
    nbars = SECTION_BARS[name]
    s_ticks = nbars * BAR
    s0 = SECTION_START[name]
    octave = SECTION_OCT[name]
    step = CELL_STEP.get(name, QUARTER)
    ev = []
    h = 0
    for t0 in cell_hits(s_ticks, 0, step=step):
        abs_bar = s0 + (t0 // BAR)
        d = BAR_DEGREES[abs_bar]
        arp = bar_arpeggio(d, octave)
        pitch = arp[h % 5]
        ev.append(MusicEvent(pitch=pitch, volume=80,
                             start_tick=t0, end_tick=t0 + EIGHTH))
        h += 1
    return ev


def build_marimbaB_section(name, raw_records):
    """Phase-walked cell, pitch quantized from raw draft + section transform."""
    nbars = SECTION_BARS[name]
    s_ticks = nbars * BAR
    s0 = SECTION_START[name] * BAR
    octave = SECTION_OCT[name]
    transform = SECTION_LEAD_TRANSFORM.get(name)
    durmode = SECTION_LEAD_DUR.get(name)

    recs = [r for r in raw_records if s0 <= r["tick_abs"] < s0 + s_ticks]
    pitches = [r["pitch"] + octave for r in recs]
    if transform == "retrograde":
        pitches = list(reversed(pitches))
    elif transform == "inversion":
        pitches = [int(2 * AXIS - p) for p in pitches]

    events = []
    for r, p in zip(recs, pitches):
        st_glob = snap_grid(r["tick_abs"], EIGHTH)
        if st_glob < s0 or st_glob >= s0 + s_ticks:
            continue
        bar = st_glob // BAR
        d = BAR_DEGREES[bar]
        qp = quantize_to_chord_tone(p, d, lo=55, hi=96)
        qp = max(48, min(96, qp))
        st = st_glob - s0
        if st >= s_ticks - 30:
            continue
        dur = r["dur"]
        if durmode == "augment":
            dur = dur * 2.0
        en = min(s_ticks - 20, st + int(dur))
        if en <= st + 30:
            en = st + 120
        events.append(MusicEvent(pitch=qp, volume=82, start_tick=st, end_tick=en))

    best = {}
    for e in events:
        key = (e.start_tick, e.pitch)
        if key not in best or (e.end_tick - e.start_tick) > \
                (best[key].end_tick - best[key].start_tick):
            best[key] = e
    return sorted(best.values(), key=lambda e: (e.start_tick, e.pitch))


def build_pad_section(name, corr_triads):
    nbars = SECTION_BARS[name]
    s_ticks = nbars * BAR
    ev = []
    for bi in range(nbars):
        bar = SECTION_START[name] + bi
        r, th, f = corr_triads[bar]
        bs = bi * BAR
        if name == "Coda":
            end = bs + BAR * 2 - 30                       # augmentation: held longer
        else:
            end = bs + BAR - 30
        for p, v in ((r, 64), (th, 60), (f, 60)):
            ev.append(MusicEvent(pitch=p, volume=v,
                                 start_tick=bs, end_tick=min(end, s_ticks - 30)))
        if name in ("Phase4", "Bridge", "Phase6"):
            ev.append(MusicEvent(pitch=r + 12, volume=58, start_tick=bs,
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
        ev.append(MusicEvent(pitch=r - 12, volume=76,
                             start_tick=bs, end_tick=bs + BAR - 40))
        ev.append(MusicEvent(pitch=f - 12, volume=68,
                             start_tick=bs + 960, end_tick=bs + 960 + 400))
        if name in ("Phase4", "Bridge"):
            ev.append(MusicEvent(pitch=r - 12, volume=72,
                                 start_tick=bs + 480, end_tick=bs + 480 + 200))
    return ev


def build_drums_section(name):
    nbars = SECTION_BARS[name]
    s_ticks = nbars * BAR
    ev = []
    kick = MidiPercussion.BASS_DRUM
    low_tom = MidiPercussion.LOW_TOM
    crash = MidiPercussion.CRASH_CYMBAL
    for bi in range(nbars):
        bs = bi * BAR
        if name in ("Phase1", "Phase2", "Phase3", "Phase4", "Phase5", "Bridge"):
            ev.append(MusicEvent(pitch=kick, volume=72, start_tick=bs,
                                 end_tick=bs + 80))
            ev.append(MusicEvent(pitch=low_tom, volume=68, start_tick=bs + 960,
                                 end_tick=bs + 1030))
        if name in ("Phase4", "Bridge"):
            ev.append(MusicEvent(pitch=low_tom, volume=64, start_tick=bs + 480,
                                 end_tick=bs + 540))
        if name == "Phase4" and bi % 2 == 0:
            ev.append(MusicEvent(pitch=crash, volume=78, start_tick=bs,
                                 end_tick=bs + 200))
        if name == "Coda" and bi % 2 == 0:
            ev.append(MusicEvent(pitch=low_tom, volume=56, start_tick=bs,
                                 end_tick=bs + 100))
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


def build_phase2(raw_records, corr_triads):
    comp = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BPB)
    comp.create_matrix(num_voices=len(VOICES), num_sections=len(SECTIONS))
    for name, prog, ch in zip(VOICES, VOICE_PROGRAMS, VOICE_CHANNELS):
        comp.add_voice(name, program=prog, channel=ch)
    for name, bars, prog in SECTIONS:
        comp.add_section(name, bars=bars)

    for name, bars, prog in SECTIONS:
        s_ticks = bars * BAR
        comp.fill_voice_section("MarimbaA", name,
                                seal(build_marimbaA_section(name), s_ticks))
        comp.fill_voice_section("MarimbaB", name,
                                seal(build_marimbaB_section(name, raw_records),
                                     s_ticks))
        comp.fill_voice_section("Pad", name,
                                seal(build_pad_section(name, corr_triads), s_ticks))
        comp.fill_voice_section("Bass", name,
                                seal(build_bass_section(name, corr_triads), s_ticks))
        comp.fill_voice_section("Drums", name,
                                seal(build_drums_section(name), s_ticks))
    ok, msg = comp.validate()
    if not ok:
        raise RuntimeError(f"phase2 validate failed: {msg}")
    return comp


# ---------------------------------------------------------------------------
# Audit helper (pre-export, on event lists)
# ---------------------------------------------------------------------------
def count_offgrid(events, grid=120):
    off = sum(1 for e in events if e.pitch > 0 and e.start_tick % grid != 0)
    tot = sum(1 for e in events if e.pitch > 0)
    return off, tot


def main():
    # ---- Phase 1 raw draft -----------------------------------------------
    phase1, raw_records = build_phase1()
    phase1_mid = os.path.join(MIDI_DIR, PROJECT + "-phase1.mid")
    phase1.to_midi(phase1_mid)
    write_provenance(
        phase1_mid, AI_ASSISTED,
        "musicom.euclidean_phase_cell_phase1",
        sources=["/opt/data/projects/Styles/Minimalism/001-minimalism-phase-study/"
                 "MIDI/minimalism-phase.mid"],
        parameters={"bpm": BPM, "bars": TOTAL_BARS, "seed": raw_seed,
                    "phase": 1, "quantized": False, "key": KEY_NAME,
                    "form": "intro-phase1-6-bridge-resolve-coda",
                    "style": STYLE, "method": "E(5,12) Euclidean phase cell",
                    "notes": len(raw_records),
                    "rules_applied": "NONE (pre-rules)"},
        notes="Raw E(5,12) phase-cell draft: single marimba voice, unquantized "
              "float pitch (seeded random walk) + off-grid onsets, 32 bars, "
              "pre-rules. Rework source: 001-minimalism-phase-study (redesign).")
    write_grid_visualization(phase1.matrix,
                             os.path.join(ANALYSIS_DIR,
                                          "grid_visualization_phase1.txt"),
                             voice_names=["RawDraft"], bpm=BPM)
    print("PHASE1_OK", "raw_notes=", len(raw_records))

    # ---- Phase 2 rules + variation ---------------------------------------
    bar_triads = [sorted([diatonic(d, base=TONIC_BASE),
                          diatonic(d + 2, base=TONIC_BASE),
                          diatonic(d + 4, base=TONIC_BASE)])
                  for d in BAR_DEGREES]
    vl = VoiceLeadingRules(style="classical")
    opt_triads = vl.optimize_voice_leading(bar_triads)
    corr_triads, fixed = correct_voice_leading(opt_triads)
    print(f"[voicing] corrected {fixed} chord(s)")

    phase2 = build_phase2(raw_records, corr_triads)

    # gather all pitched events from the phase-2 matrix (perfect layer)
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
    print(f"[grid] perfect-layer off-grid (pitched): {off}/{tot}")
    assert off == 0, f"perfect layer has {off} off-grid onsets"

    # ---- dual-version export ---------------------------------------------
    hz_instruments = {
        "MarimbaA": MARIMBA.humanize_dna,
        "MarimbaB": MARIMBA.humanize_dna,
        "Pad": STRING_ENSEMBLE.humanize_dna,
        "Bass": ACOUSTIC_BASS.humanize_dna,
        "Drums": None,
    }
    perfect_path = os.path.join(MIDI_DIR, PROJECT + "-perfect.mid")
    humanized_path = os.path.join(MIDI_DIR, PROJECT + "-humanized.mid")
    hz = export_dual(phase2, perfect_path, humanized_path,
                     style=STYLE, seed=hz_seed, bpm=BPM, instruments=hz_instruments)

    # ---- provenance sidecars ---------------------------------------------
    section_midpoints = {}
    for name, bars, prog in SECTIONS:
        mid_idx = bars // 2
        section_midpoints[name] = {"degree": prog[mid_idx],
                                   "chord": DEGREE_NAMES[prog[mid_idx]]}
    prov = {
        "bpm": BPM, "key": "C", "mode": "ionian", "style": STYLE,
        "form": "intro-phase1-6-bridge-resolve-coda",
        "bars": TOTAL_BARS, "sections": [s[0] for s in SECTIONS],
        "section_bars": {s[0]: s[1] for s in SECTIONS},
        "section_techniques": SECTION_TECHNIQUE,
        "section_midpoint_chords": section_midpoints,
        "bar_degrees": BAR_DEGREES,
        "method": "E(5,12) Euclidean phase cell", "layer": "concrete",
        "paradigm": "Process",
        "rework": {"source": "001-minimalism-phase-study", "decision": "redesign",
                   "standard_failures": ["phase1 missing", "index.html missing",
                                         "dual-version missing"]},
        "variation_techniques": {
            "phase_walk": "MarimbaB rotates E(5,12) cell +1 beat/section (identity)",
            "retrograde": "Phase5 MarimbaB pitch sequence reversed",
            "inversion": "Bridge MarimbaB mirrored around C5 (=72)",
            "augmentation": "Coda MarimbaB durations x2",
            "register_shift": "Phase4 +12 / Intro-Resolve-Coda -12",
            "density_diminution": "Phase4+Phase6 MarimbaA cell 8th-note (x2 density)",
            "relative_minor": "Bridge harmonic center -> vi (Am) region",
        },
        "voices": [[v, p, ch] for v, p, ch in
                   zip(VOICES, VOICE_PROGRAMS, VOICE_CHANNELS)],
        "humanize_seed": hz_seed, "raw_seed": raw_seed,
        "humanize_profiles": {k: v["profile"] for k, v in hz.items()},
    }
    write_provenance(
        perfect_path, AI_ASSISTED,
        "musicom two-phase (phase=2 rules: chord-tone quantization + 8th grid "
        "snap + dedup + voice-leading + variation techniques) (E(5,12) phase cell)",
        sources=[phase1_mid],
        parameters=dict(prov, phase=2, version="perfect", off_grid=0),
        notes="Grid-locked perfect layer (intro-phase1-6-bridge-resolve-coda, "
              "32 bars). Redesign of 001-minimalism-phase-study.")
    write_provenance(
        humanized_path, AI_ASSISTED,
        "musicom two-phase (phase=2 + humanization) (E(5,12) phase cell)",
        sources=[perfect_path],
        parameters=dict(prov, phase=2, version="humanized",
                        humanize_seed=hz_seed,
                        humanize_stats={k: {kk: (float(vv) if isinstance(vv, float) else vv)
                                            for kk, vv in v.items() if kk != "profile"}
                                        for k, v in hz.items()}),
        notes="Humanized layer (style minimalism + per-instrument DNA).")

    # ---- grid visualization ----------------------------------------------
    write_grid_visualization(phase2.matrix,
                             os.path.join(ANALYSIS_DIR, "grid_visualization.txt"),
                             voice_names=VOICES, bpm=BPM)

    # ---- size asserts ----------------------------------------------------
    for p in (phase1_mid, perfect_path, humanized_path):
        assert os.path.getsize(p) > 40, f"empty/corrupt: {p}"

    summary = {
        "style": STYLE, "genre": GENRE, "method": "E(5,12) Euclidean phase cell",
        "form": "intro-phase1-6-bridge-resolve-coda",
        "key": KEY_NAME, "bpm": BPM, "bars": TOTAL_BARS,
        "sections": [s[0] for s in SECTIONS],
        "section_bars": [s[1] for s in SECTIONS],
        "section_techniques": SECTION_TECHNIQUE,
        "raw_notes": len(raw_records),
        "voice_leading_corrections": fixed,
        "phase1_path": phase1_mid, "perfect_path": perfect_path,
        "humanized_path": humanized_path,
        "hz_seed": hz_seed,
        "hz": {k: {kk: vv for kk, vv in v.items() if kk != "profile"}
               for k, v in hz.items()},
        "progression": {s[0]: [DEGREE_NAMES[d] for d in s[2]] for s in SECTIONS},
        "rework_source": "001-minimalism-phase-study",
        "rework_decision": "redesign",
    }
    with open(os.path.join(ANALYSIS_DIR, "compose_summary.json"), "w") as f:
        json.dump(summary, f, indent=2, default=str)
    print("COMPOSE_OK")
    print(json.dumps(summary, indent=2, default=str))


if __name__ == "__main__":
    main()
