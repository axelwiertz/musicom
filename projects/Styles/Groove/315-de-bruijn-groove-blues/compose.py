# -*- coding: utf-8 -*-
"""315-de-bruijn-groove-blues -- Groove via De Bruijn Universal Cycle (DBUC).

Nightly composition job (2026-11-20). Selection: style=Groove, method=077
De Bruijn Universal Cycle Composition (DBUC, CONCRETE layer), form=blues-12
(pick_form("groove") -> "Blues" single section, 12 bars).

MUSICAL DNA
  - Key E minor (aeolian) = pc {E,F#,G,A,B,C,D} = {4,6,7,9,11,0,2}; tonic E.
  - 104 BPM, 4/4, 480 TPB, BAR=1920, 8th=240, 16th=120.
  - Method 077 DBUC: a de Bruijn sequence B(k,n) is a cyclic word of length
    n^k whose every length-n window over a k-symbol alphabet appears exactly
    once. Two sequences drive the piece:
        PITCH_SEQ = B(7,2)  -> 49 symbols over the 7 diatonic degrees of
                      E minor (every ordered degree pair appears once) --
                      this is the melodic pitch DNA.
        RHYTHM_SEQ = B(2,3) -> 8 binary symbols (every length-3 binary
                      window once) -- the onset gate (1 = hit, 0 = rest).
    The lead walks PITCH_SEQ over the piece's 8th-note grid (96 slots =
    12 bars x 8 eighths; PITCH_SEQ cycles), gated by RHYTHM_SEQ (period 8 =
    one bar). Every ordered degree pair -> an exact, exhaustive, non-repeating
    melodic contour. The 12-bar blues progression supplies the harmonic
    regions (macro-form) that the chord-tone snap quantizes against.
  - 5-voice Groove texture: Clavinet lead (de Bruijn melody), Muted Guitar
    funk comp (16th chuck), Rhodes backbeat stabs, Electric Bass root/octave
    funk line, Drum Kit backbeat groove.

TWO-PHASE
  Phase 1 (raw): single Clavinet voice, the raw de Bruijn degree stream --
    jittered pitch (float + chromatic jitter), off-grid onsets, single voice,
    no harmony; own composer + validate().
  Phase 2 (rules): STRICT chord discipline (every note snaps to its own bar's
    chord tone -> in-scale AND in-chord), 16th grid snap, 5-voice texture.
  Dual-version: export_dual -> -perfect.mid (grid-locked) + -humanized.mid.
"""
import json
import os
import sys
import hashlib
import itertools

import numpy as np

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer
from workflows.humanize import export_dual
from workflows.provenance import write_provenance, AI_ASSISTED
from workflows.pitch_audit import audit_voice
from visualization.grid import write_grid_visualization
from rules.progression import Scale7ChordDegree

_INSTR_DIR = "/opt/data/repos/musicom/projects/Instruments"
if _INSTR_DIR not in sys.path:
    sys.path.insert(0, _INSTR_DIR)
from instrument_registry import (  # noqa: E402
    CLAVI, MUTED_GUITAR, RHODES, ELECTRIC_BASS, DRUM_KIT)

# ---------------------------------------------------------------------------
# Project layout / identity
# ---------------------------------------------------------------------------
GENRE = "Groove"
STYLE = "groove"
PROJECT = "315-de-bruijn-groove-blues"
BASE = os.path.join("/opt/data/projects/Styles", GENRE, PROJECT)
MIDI_DIR = os.path.join(BASE, "MIDI")
AUDIO_DIR = os.path.join(BASE, "Audio")
ANALYSIS_DIR = os.path.join(BASE, "Analysis")
for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
    os.makedirs(d, exist_ok=True)

BPM = 104
TPB = 480
BPB = 4
BAR = TPB * BPB                     # 1920
GRID = 120                          # 16th
EIGHTH = 240
QUARTER = 480
TOTAL_BARS = 12
TOTAL_TICKS = TOTAL_BARS * BAR      # 23040

KEY_NAME = "E minor (aeolian)"
TONIC_PC = 4                        # E
INTERVALS = [0, 2, 3, 5, 7, 8, 10]  # aeolian / natural-minor step pattern
KEY_PCS = sorted({(TONIC_PC + iv) % 12 for iv in INTERVALS})  # {0,2,4,6,7,9,11}

# 1-based degree -> triad quality intervals (E natural minor diatonic)
QUALITY = {1: (0, 3, 7), 2: (0, 3, 6), 3: (0, 4, 7), 4: (0, 3, 7),
           5: (0, 3, 7), 6: (0, 4, 7), 7: (0, 4, 7)}
DEGREE_NAMES = {1: "Em", 2: "F#dim", 3: "G", 4: "Am", 5: "Bm", 6: "C", 7: "D"}

# deterministic seeds
hz_seed = int(hashlib.md5(
    (STYLE + KEY_NAME + str(BPM) + str(TOTAL_BARS) + PROJECT).encode()
).hexdigest()[:8], 16) % 100000
raw_seed = 20261120
RNG = __import__("random").Random(raw_seed)
NPRNG = np.random.default_rng(raw_seed)

# ---------------------------------------------------------------------------
# Form: 12-bar blues (single logical "Blues" section, 12 bars).
# Progression (1-based degrees): i i i i | iv iv i i | v iv i v
# ---------------------------------------------------------------------------
BLUES_DEGREES = [1, 1, 1, 1, 4, 4, 1, 1, 5, 4, 1, 5]
assert len(BLUES_DEGREES) == TOTAL_BARS
LOGICAL_SECTIONS = [("Blues", TOTAL_BARS)]
# 1-bar sections for the humanized composer: the humanizer's boundary clamp
# == bar boundary, so jitter never re-attributes a note to the wrong bar's
# chord (per-bar chord violations stay 0).
BAR_SECTIONS = [(f"Blues-b{b + 1}", 1) for b in range(TOTAL_BARS)]

# ---------------------------------------------------------------------------
# Voices + registers
# ---------------------------------------------------------------------------
VOICES = ["Lead", "Guitar", "Rhodes", "Bass", "Drums"]
VOICE_PROGRAMS = [CLAVI.midi_program, MUTED_GUITAR.midi_program,
                  RHODES.midi_program, ELECTRIC_BASS.midi_program, 0]
VOICE_CHANNELS = [0, 1, 2, 3, 9]

LEAD_BASE = 64                      # E4
LEAD_LO, LEAD_HI = 52, 76           # clavinet sweet spot (48-72) + margin
GUITAR_LO, GUITAR_HI = 45, 69       # muted guitar sweet (40-64)
RHODES_LO, RHODES_HI = 55, 79       # rhodes sweet (60-79)
BASS_BASE = 40                      # E2
BASS_LO, BASS_HI = 36, 60


# ---------------------------------------------------------------------------
# Diatonic helpers (canonical Scale7ChordDegree -- no %7 wrapper)
# ---------------------------------------------------------------------------
def diatonic(deg_index, base=LEAD_BASE):
    return Scale7ChordDegree.get_diatonic_note(base, INTERVALS, deg_index)


def chord_pcs(d):
    root_pc = (TONIC_PC + INTERVALS[d - 1]) % 12
    return sorted({(root_pc + iv) % 12 for iv in QUALITY[d]})


def chord_tones(d, lo=36, hi=96):
    root_pc = (TONIC_PC + INTERVALS[d - 1]) % 12
    out = set()
    for octv in range(-3, 11):
        for iv in QUALITY[d]:
            n = root_pc + 12 * octv + iv
            if lo <= n <= hi:
                out.add(n)
    return sorted(out)


def to_register(pitch, lo, hi):
    p = int(pitch)
    while p < lo:
        p += 12
    while p > hi:
        p -= 12
    return p


# ---------------------------------------------------------------------------
# De Bruijn sequence generation (FKM "prefer-smallest" + verification)
# ---------------------------------------------------------------------------
def de_bruijn(k, n):
    """Lexicographically smallest de Bruijn sequence B(n,k): a cyclic word of
    length k**n over alphabet [0,k) where every length-n window appears once."""
    a = [0] * (k * n)
    seq = []

    def db(t, p):
        if t > n:
            if n % p == 0:
                seq.extend(a[1:p + 1])
        else:
            a[t] = a[t - p]
            db(t + 1, p)
            for j in range(a[t - p] + 1, k):
                a[t] = j
                db(t + 1, t)

    db(1, 1)
    return seq


def verify_de_bruijn(seq, k, n):
    """Assert the de Bruijn property: every length-n window over [0,k) appears
    exactly once (cyclic)."""
    assert len(seq) == k ** n, f"length {len(seq)} != {k ** n}"
    windows = [tuple(seq[(i + j) % len(seq)] for j in range(n))
               for i in range(len(seq))]
    assert len(set(windows)) == k ** n, \
        f"only {len(set(windows))} distinct windows (expected {k ** n})"
    assert set(windows) == set(itertools.product(range(k), repeat=n)), \
        "windows do not cover the full alphabet"


PITCH_SEQ = de_bruijn(7, 2)          # 49 symbols over 7 diatonic degrees
RHYTHM_SEQ = de_bruijn(2, 3)         # 8 binary symbols (onset gate)
verify_de_bruijn(PITCH_SEQ, 7, 2)
verify_de_bruijn(RHYTHM_SEQ, 2, 3)
PITCH_LEN = len(PITCH_SEQ)           # 49
RHYTHM_LEN = len(RHYTHM_SEQ)         # 8
N_SLOTS = TOTAL_BARS * 8             # 96 eighth-note slots


# ---------------------------------------------------------------------------
# Phase 1: raw de Bruijn walk (single voice, jittered, off-grid)
# ---------------------------------------------------------------------------
def build_raw_lead():
    raw = []
    for slot in range(N_SLOTS):
        gate = RHYTHM_SEQ[slot % RHYTHM_LEN]
        if gate == 0:
            continue
        degree = PITCH_SEQ[slot % PITCH_LEN]
        onset = slot * EIGHTH + RNG.randint(-40, 40)
        p = float(diatonic(degree, LEAD_BASE)) + float(RNG.choice([-1, 0, 0, 1]))
        vel = int(RNG.randint(72, 100))
        raw.append({"pitch": p, "start": max(0, onset), "dur": EIGHTH,
                    "vel": vel, "slot": slot, "degree": degree})
    raw.sort(key=lambda e: (e["start"], e["pitch"]))
    return raw


def rel_events(abs_events, s_start, s_len):
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
    comp = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BPB)
    comp.create_matrix(num_voices=1, num_sections=len(LOGICAL_SECTIONS))
    comp.add_voice("RawClavi", program=CLAVI.midi_program, channel=0)
    for name, bars in LOGICAL_SECTIONS:
        comp.add_section(name, bars=bars)

    s_ticks = TOTAL_BARS * BAR
    seg = []
    for e in raw_events:
        p = int(round(e["pitch"]))
        p = max(36, min(96, p))
        seg.append(MusicEvent(pitch=p, volume=e["vel"],
                              start_tick=int(round(e["start"])),
                              end_tick=int(round(e["start"] + e["dur"]))))
    seg.sort(key=lambda e: e.start_tick)
    comp.fill_voice_section("RawClavi", "Blues",
                            MusicUnit(events=rel_events(seg, 0, s_ticks)))
    ok, msg = comp.validate()
    if not ok:
        raise RuntimeError(f"phase1 validate failed: {msg}")
    return comp


# ---------------------------------------------------------------------------
# Phase 2 builders (STRICT chord discipline -- every note = its bar's chord
# tone -> in-scale AND in-chord)
# ---------------------------------------------------------------------------
def snap_grid(t, grid=GRID):
    return int(round(t / float(grid)) * grid)


def build_lead():
    """Clavinet: de Bruijn degree stream gated by the binary de Bruijn cycle,
    each onset chord-tone snapped (nearest chord tone of its own bar)."""
    events = []
    for slot in range(N_SLOTS):
        gate = RHYTHM_SEQ[slot % RHYTHM_LEN]
        if gate == 0:
            continue
        bar = slot // 8
        degree = PITCH_SEQ[slot % PITCH_LEN]
        d = BLUES_DEGREES[bar]
        ct = chord_tones(d, LEAD_LO, LEAD_HI)
        raw_note = diatonic(degree, LEAD_BASE)
        raw_note = to_register(raw_note, LEAD_LO, LEAD_HI)
        p = min(ct, key=lambda t: abs(t - raw_note))
        onset = snap_grid(slot * EIGHTH)
        onset = max(0, min(TOTAL_TICKS - GRID, onset))
        vel = 84 + (slot % 3) * 6
        events.append(MusicEvent(pitch=p, volume=vel, start_tick=onset,
                                 end_tick=min(TOTAL_TICKS, onset + 200)))
    return events


def build_guitar():
    """Muted guitar funk comp: 16th-note chucks, syncopated (1, and-of-2, 3,
    4, and-of-4 pickup). Chord voicing root+3rd+7th (3 notes), short chucks."""
    events = []
    HITS = (0, 6, 8, 12, 14)         # 16th slots: 1, and-of-2, 3, 4, pickup
    for bar in range(TOTAL_BARS):
        d = BLUES_DEGREES[bar]
        tones = chord_tones(d, GUITAR_LO, GUITAR_HI)
        voicing = tones[:3]
        t0 = bar * BAR
        for h in HITS:
            t = t0 + h * GRID
            vel = 78 if h in (0, 8) else 62
            for n in voicing:
                events.append(MusicEvent(pitch=n, volume=vel, start_tick=t,
                                         end_tick=t + 100))
    events.sort(key=lambda e: (e.start_tick, e.pitch))
    return events


def build_rhodes():
    """Rhodes backbeat stabs on beats 2 & 4, sustained half-ish length."""
    events = []
    for bar in range(TOTAL_BARS):
        d = BLUES_DEGREES[bar]
        tones = chord_tones(d, RHODES_LO, RHODES_HI)
        voicing = tones[:3]
        t0 = bar * BAR
        for beat in (480, 1440):
            t = t0 + beat
            for n in voicing:
                events.append(MusicEvent(pitch=n, volume=70, start_tick=t,
                                         end_tick=t + 360))
    events.sort(key=lambda e: (e.start_tick, e.pitch))
    return events


def build_bass():
    """Electric bass funk line: root (1) -> octave (and-of-2) -> fifth (3)
    -> approach-to-next-root (and-of-4 pickup). All 16th-aligned."""
    events = []
    for bar in range(TOTAL_BARS):
        d = BLUES_DEGREES[bar]
        ct = chord_tones(d, BASS_LO, BASS_HI)
        root = diatonic(d - 1, BASS_BASE)
        root = to_register(root, BASS_LO, BASS_HI)
        octv = to_register(root + 12, BASS_LO, BASS_HI)
        fifth = to_register(root + 7, BASS_LO, BASS_HI)
        # pickup: nearest chord tone of THIS bar to the next bar's root - 2
        # (a step below next root) -> always in-chord (STRICT discipline)
        next_d = BLUES_DEGREES[(bar + 1) % TOTAL_BARS]
        next_root = diatonic(next_d - 1, BASS_BASE)
        approach_target = to_register(next_root - 2, BASS_LO, BASS_HI)
        approach = min(ct, key=lambda t: abs(t - approach_target))
        t0 = bar * BAR
        events.append(MusicEvent(pitch=root, volume=90, start_tick=t0,
                                 end_tick=t0 + 400))
        events.append(MusicEvent(pitch=octv, volume=72, start_tick=t0 + 720,
                                 end_tick=t0 + 820))
        events.append(MusicEvent(pitch=fifth, volume=78, start_tick=t0 + 960,
                                 end_tick=t0 + 1320))
        events.append(MusicEvent(pitch=approach, volume=60,
                                 start_tick=t0 + 1680, end_tick=t0 + 1780))
    events.sort(key=lambda e: e.start_tick)
    return events


def build_drums():
    """Funk backbeat: kick 1 & 3 (+ and-of-4 push), snare 2 & 4, hats 8ths
    (open on off-beats)."""
    events = []
    for bar in range(TOTAL_BARS):
        t0 = bar * BAR
        events.append(MusicEvent(pitch=36, volume=100, start_tick=t0,
                                 end_tick=t0 + 60))
        events.append(MusicEvent(pitch=36, volume=92, start_tick=t0 + 960,
                                 end_tick=t0 + 1020))
        events.append(MusicEvent(pitch=36, volume=70, start_tick=t0 + 1680,
                                 end_tick=t0 + 1740))
        events.append(MusicEvent(pitch=38, volume=90, start_tick=t0 + 480,
                                 end_tick=t0 + 540))
        events.append(MusicEvent(pitch=38, volume=90, start_tick=t0 + 1440,
                                 end_tick=t0 + 1500))
        for off in range(0, 1920, 240):
            hat = 46 if (off // 240) % 2 == 1 else 42
            events.append(MusicEvent(pitch=hat, volume=60, start_tick=t0 + off,
                                     end_tick=t0 + off + 40))
    events.sort(key=lambda e: (e.start_tick, e.pitch))
    return events


def build_phase2(vmap, sections_spec):
    comp = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BPB)
    comp.create_matrix(num_voices=len(VOICES), num_sections=len(sections_spec))
    for name, prog, ch in zip(VOICES, VOICE_PROGRAMS, VOICE_CHANNELS):
        comp.add_voice(name, program=prog, channel=ch)
    for name, bars in sections_spec:
        comp.add_section(name, bars=bars)

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


# ---------------------------------------------------------------------------
# Audits
# ---------------------------------------------------------------------------
def count_offgrid(events, grid=GRID):
    off = sum(1 for e in events if e.pitch > 0 and e.start_tick % grid != 0)
    return off, sum(1 for e in events if e.pitch > 0)


def count_violations(events):
    scale = chord = 0
    for e in events:
        if e.pitch <= 0:
            continue
        pc = e.pitch % 12
        bar = min(TOTAL_BARS - 1, e.start_tick // BAR)
        if pc not in KEY_PCS:
            scale += 1
        if pc not in chord_pcs(BLUES_DEGREES[bar]):
            chord += 1
    return scale, chord


CHORD_PCS_BY_BAR = {b: chord_pcs(BLUES_DEGREES[b]) for b in range(TOTAL_BARS)}


def tiered_audit(events):
    return audit_voice(events, KEY_PCS, chord_pcs_by_bar=CHORD_PCS_BY_BAR,
                       strong_grid=(0, 960), bar_ticks=BAR, grid=EIGHTH)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    # ---- Phase 1 raw draft -------------------------------------------------
    raw_events = build_raw_lead()
    print("Phase-1 raw lead events:", len(raw_events))
    phase1 = build_phase1(raw_events)
    phase1_mid = os.path.join(MIDI_DIR, PROJECT + "-phase1.mid")
    phase1.to_midi(phase1_mid)
    write_provenance(
        phase1_mid, AI_ASSISTED,
        "musicom composition 315 (phase=1 raw, method 077 DBUC)",
        parameters={"bpm": BPM, "bars": TOTAL_BARS, "seed": raw_seed,
                    "phase": 1, "quantized": False, "key": KEY_NAME,
                    "form": "blues-12 (12-bar)", "style": STYLE,
                    "method": "077 DBUC (de Bruijn B(7,2) x B(2,3))",
                    "pitch_seq_len": PITCH_LEN, "rhythm_seq_len": RHYTHM_LEN},
        notes="Raw de Bruijn degree walk (B(7,2) pitch x B(2,3) gate), "
              "off-grid, float pitch + jitter, single voice, pre-rules.")
    write_grid_visualization(
        phase1.matrix,
        os.path.join(ANALYSIS_DIR, "grid_visualization_phase1.txt"),
        voice_names=["RawClavi"], bpm=BPM)

    # ---- Phase 2 rules post-process (5 voices) -----------------------------
    lead_ev = build_lead()
    guitar_ev = build_guitar()
    rhodes_ev = build_rhodes()
    bass_ev = build_bass()
    drums_ev = build_drums()
    vmap = {"Lead": lead_ev, "Guitar": guitar_ev, "Rhodes": rhodes_ev,
            "Bass": bass_ev, "Drums": drums_ev}

    phase2 = build_phase2(vmap, BAR_SECTIONS)

    # ---- STRICT discipline audit on pitched voices -------------------------
    pitched = lead_ev + guitar_ev + rhodes_ev + bass_ev
    off, tot = count_offgrid(pitched)
    scale_v, chord_v = count_violations(pitched)
    print(f"Perfect-layer off-grid (pitched): {off}/{tot}")
    print(f"STRICT scale violations: {scale_v}  chord violations: {chord_v}")
    assert off == 0, f"perfect layer has {off} off-grid onsets"
    assert scale_v == 0, f"scale violations: {scale_v}"
    assert chord_v == 0, f"chord violations: {chord_v}"

    # ---- tiered audit_voice (P1 invariant) per pitched voice ---------------
    tiered = {}
    for vname in ("Lead", "Guitar", "Rhodes", "Bass"):
        r = tiered_audit(vmap[vname])
        tiered[vname] = {
            "audible": r.audible,
            "strong_ok": r.strong_ok,
            "weak_in_scale": r.weak_in_scale,
            "untagged_out_of_scale": r.untagged_out_of_scale,
            "tagged_non_resolving": r.tagged_non_resolving,
            "strong_violations": r.strong_violations,
            "passes": r.passes,
        }
        assert r.passes, f"tiered audit failed for {vname}: {r.summary()}"
        print(f"  {vname}: {r.summary()}")

    write_grid_visualization(
        phase2.matrix,
        os.path.join(ANALYSIS_DIR, "grid_visualization.txt"),
        voice_names=VOICES, bpm=BPM)

    # ---- dual-version export (perfect + humanized) -------------------------
    hz_instruments = {
        "Lead": CLAVI.humanize_dna,
        "Guitar": MUTED_GUITAR.humanize_dna,
        "Rhodes": RHODES.humanize_dna,
        "Bass": ELECTRIC_BASS.humanize_dna,
        "Drums": DRUM_KIT.humanize_dna,
    }
    perfect_path = os.path.join(MIDI_DIR, PROJECT + "-perfect.mid")
    humanized_path = os.path.join(MIDI_DIR, PROJECT + "-humanized.mid")
    hz = export_dual(phase2, perfect_path, humanized_path,
                     style=STYLE, seed=hz_seed, bpm=BPM,
                     instruments=hz_instruments)

    # ---- provenance sidecars ------------------------------------------------
    prov_params = {
        "bpm": BPM, "key": "E", "mode": "aeolian", "style": STYLE,
        "form": "blues-12 (12-bar)", "bars": TOTAL_BARS,
        "method": "077 DBUC", "layer": "concrete", "paradigm": "Rules-Based",
        "progression": [DEGREE_NAMES[d] for d in BLUES_DEGREES],
        "de_bruijn": {"pitch_seq": PITCH_SEQ, "rhythm_seq": RHYTHM_SEQ},
        "voices": [[v, n, o.midi_program] for v, n, o in [
            ("Lead", "Clavinet", CLAVI), ("Guitar", "Muted Guitar", MUTED_GUITAR),
            ("Rhodes", "Rhodes", RHODES), ("Bass", "Electric Bass", ELECTRIC_BASS),
            ("Drums", "Drum Kit", DRUM_KIT)]],
        "humanize_seed": hz_seed, "raw_seed": raw_seed,
        "humanize_profiles": {k: v["profile"] for k, v in hz.items()},
    }
    write_provenance(
        perfect_path, AI_ASSISTED,
        "musicom composition 315 (phase=2 strict chord discipline) (method 077 DBUC)",
        sources=[phase1_mid],
        parameters=dict(prov_params, phase=2, version="perfect",
                        off_grid=0, scale_violations=0, chord_violations=0),
        notes="Grid-locked perfect layer (12-bar blues, 5 voices).")
    write_provenance(
        humanized_path, AI_ASSISTED,
        "musicom composition 315 (phase=2 + humanization) (method 077 DBUC)",
        sources=[perfect_path],
        parameters=dict(prov_params, phase=2, version="humanized",
                        humanize_seed=hz_seed,
                        humanize_stats={k: {kk: (float(vv) if isinstance(vv, float) else vv)
                                            for kk, vv in v.items() if kk != "profile"}
                                        for k, v in hz.items()}),
        notes="Humanized layer (style groove + per-instrument DNA).")

    for p in (phase1_mid, perfect_path, humanized_path):
        assert os.path.getsize(p) > 40, f"empty/corrupt: {p}"

    # ---- root provenance.json ----------------------------------------------
    root_prov = dict(prov_params)
    root_prov.update({
        "project": PROJECT, "genre": GENRE, "key_name": KEY_NAME,
        "tonic_pc": TONIC_PC, "key_pcs": KEY_PCS,
        "bars": TOTAL_BARS, "ticks": TOTAL_TICKS,
        "form": "blues-12 (12-bar)", "progression_names": [DEGREE_NAMES[d] for d in BLUES_DEGREES],
        "pitch_seq_len": PITCH_LEN, "rhythm_seq_len": RHYTHM_LEN,
        "tiered_audit": tiered,
        "hz_seed": hz_seed, "raw_seed": raw_seed,
        "humanize_profiles": {k: v["profile"] for k, v in hz.items()},
        "generator": "musicom composition agent (nightly) 2026-11-20",
        "classification": "ai-assisted",
    })
    with open(os.path.join(BASE, "provenance.json"), "w") as f:
        json.dump(root_prov, f, indent=2, default=str)

    # ---- summary -------------------------------------------------------------
    summary = {
        "style": STYLE, "genre": GENRE, "project": PROJECT,
        "method": "077 DBUC", "layer": "concrete", "form": "blues-12",
        "key": KEY_NAME, "bpm": BPM, "bars": TOTAL_BARS,
        "progression": [DEGREE_NAMES[d] for d in BLUES_DEGREES],
        "pitch_seq_len": PITCH_LEN, "rhythm_seq_len": RHYTHM_LEN,
        "raw_events": len(raw_events),
        "phase1_path": phase1_mid, "perfect_path": perfect_path,
        "humanized_path": humanized_path,
        "off_grid": off, "scale_violations": scale_v, "chord_violations": chord_v,
        "tiered_audit": tiered,
        "hz_seed": hz_seed,
        "hz": {k: {kk: vv for kk, vv in v.items() if kk != "profile"}
               for k, v in hz.items()},
    }
    print("COMPOSE_OK")
    print(json.dumps(summary, indent=2, default=str))
    with open(os.path.join(ANALYSIS_DIR, "compose_summary.json"), "w") as f:
        json.dump(summary, f, indent=2, default=str)

    print("LEAD:", len(lead_ev), "GUITAR:", len(guitar_ev),
          "RHODES:", len(rhodes_ev), "BASS:", len(bass_ev),
          "DRUMS:", len(drums_ev))


if __name__ == "__main__":
    main()
