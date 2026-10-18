#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""250-hirajoshi-ma-rework — rework of 001-japanese-hirajoshi.

Two-phase rework of a D-hirajoshi hōgaku study (koto / shakuhachi / shamisen /
taiko, ma structural). Source was engine-compliant but pre-phase1 + pre-index.html.

NEW version: 8 sections x 4 bars = 32 bars (source: 16). Five variation
techniques across the piece. Per-section harmonic regions (quartal trichords on
hirajoshi scale degrees) with the section root taken from the MIDPOINT chord —
never the bar-0 tonic.

Phase 1 (raw generative): seeded stochastic contour walk -> unquantized
pitch_index + onset/duration, single voice, exported as -phase1.mid.

Phase 2 (musicom rules): chord-tone quantization per bar (floor t//BAR),
16th-grid onset snap + dedup, register/range enforcement, light voice-leading
check/correction, 4-voice UnitMatrix -> validate() -> dual export
(-perfect.mid grid-locked, -humanized.mid style+instrument humanized).
"""
import hashlib
import json
import os
import sys

import numpy as np

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer
from visualization.grid import write_grid_visualization
from workflows.provenance import write_provenance, AI_ASSISTED
from workflows.humanize import export_dual

# Instrument registry (source of truth; lives under /opt/data/projects/Instruments,
# NOT pip-installed — the sanctioned sys.path.insert is for the registry only).
_INSTR_DIR = "/opt/data/projects/Instruments"
if _INSTR_DIR not in sys.path:
    sys.path.insert(0, _INSTR_DIR)
from instrument_registry import by_name  # noqa: E402

# ---------------------------------------------------------------- timing
TPB = 480
BEATS = 4
BAR = TPB * BEATS            # 1920
Q = TPB                       # quarter 480
E = TPB // 2                  # eighth 240
S = TPB // 4                  # sixteenth 120
BPM = 70
SECTION_BARS = 4
SECTION_LEN = SECTION_BARS * BAR   # 7680

# ---------------------------------------------------------------- key: D hirajoshi
KEY_ROOT = 50                 # D3
HIRA_IVLS = [0, 1, 5, 6, 10]  # D Eb G Ab C (semitones from root)
KEY_PCS = sorted({(KEY_ROOT + iv) % 12 for iv in HIRA_IVLS})
KEY_NAME = "D hirajoshi"


def scale_pitch(deg, root=KEY_ROOT):
    """Pentatonic diatonic pitch: octave via //5, step via %5. No wrap bug.

    Mirrors rules.progression.Scale7ChordDegree.get_diatonic_note but for a
    5-note scale (hirajoshi is pentatonic, not heptatonic).
    """
    return root + (deg // 5) * 12 + HIRA_IVLS[deg % 5]


def chord_tones_pcs(deg):
    """Quartal trichord pitch classes: root + 4th + 7th of the hirajoshi scale."""
    return {scale_pitch(deg) % 12, scale_pitch(deg + 2) % 12, scale_pitch(deg + 4) % 12}


def chord_tones_in_band(deg, low, high):
    out = []
    for octv in range(low // 12, high // 12 + 1):
        for pc in sorted(chord_tones_pcs(deg)):
            p = octv * 12 + pc
            if low <= p <= high:
                out.append(p)
    return out


def nearest_chord_tone(pitch, deg, low, high):
    cands = chord_tones_in_band(deg, low, high)
    return min(cands, key=lambda p: abs(p - pitch))


def fold_into(pitch, low, high):
    while pitch < low:
        pitch += 12
    while pitch > high:
        pitch -= 12
    return pitch


# ---------------------------------------------------------------- form + harmony
# (section name, chord degree per bar x4) — per-section harmonic regions.
SECTIONS = [
    ("Jo",      [0, 0, 4, 4]),   # intro, ma, tonic -> tension
    ("Ha",      [0, 2, 4, 0]),   # theme A
    ("Ha2",     [3, 2, 0, 4]),   # theme A transposed (register +12)
    ("Kyu",     [4, 3, 2, 1]),   # climax B (density + register)
    ("Bridge",  [1, 2, 3, 4]),   # augmentation (rising region)
    ("Kyu2",    [4, 3, 2, 1]),   # B return (inversion)
    ("Develop", [2, 1, 4, 3]),   # retrograde + re-harmonize
    ("Jo2",     [0, 0, 0, 0]),   # outro, ma, tonic close
]
N_SECTIONS = len(SECTIONS)
GLOBAL_DEG = []
for _name, degs in SECTIONS:
    GLOBAL_DEG.extend(degs)
assert len(GLOBAL_DEG) == N_SECTIONS * SECTION_BARS == 32

# section root = MIDPOINT chord degree (bar 1 of 4) — never bar-0 tonic.
SECTION_ROOTS = [degs[1] for _name, degs in SECTIONS]

PROJ = os.path.dirname(os.path.abspath(__file__))
MIDI_DIR = os.path.join(PROJ, "MIDI")
AUDIO_DIR = os.path.join(PROJ, "Audio")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")

SEED = int(hashlib.md5(b"250-hirajoshi-ma-rework").hexdigest()[:8], 16)

# instrument constants (registry source of truth)
KOTO = by_name("koto")            # program 107
SHAKUHACHI = by_name("shakuhachi")  # program 77
SHAMISEN = by_name("shamisen")    # program 106


# ================================================================ helpers
def make_unit(events, sec):
    """Clamp events into [0, sec] and append a terminal landmark (pitch 0) at sec.

    Events are SORTED by start_tick first — the zero-drift + humanizer invariants
    both require chronological order (the humanizer forward-clamps against the
    previous onset, so a retrograde/descending event list would collapse).
    Guarantees MusicUnit.len_ticks() == sec for every cell -> zero-drift.
    """
    out = []
    for e in sorted(events, key=lambda x: int(x.start_tick)):
        st = max(0, min(int(e.start_tick), sec - 1))
        en = max(st + 1, min(int(e.end_tick), sec))
        out.append(MusicEvent(pitch=int(e.pitch), volume=int(e.volume),
                              start_tick=st, end_tick=en))
    out.append(MusicEvent(pitch=0, volume=0, start_tick=sec - 1, end_tick=sec))
    return MusicUnit(events=out)


# ================================================================ PHASE 1
def gen_phase1_raw(seed):
    """Seeded stochastic contour walk -> raw (unquantized) events."""
    rng = np.random.default_rng(seed)
    raw = []
    degree = 8.0  # continuous scale-degree walk position (mid register)
    for s, (name, _degs) in enumerate(SECTIONS):
        base = s * SECTION_LEN
        for b in range(SECTION_BARS):
            bar_start = base + b * BAR
            n = int(rng.integers(2, 4))          # 2-3 notes / bar (sparse, ma)
            for _k in range(n):
                step = float(rng.choice([-1, 0, 1, 1, 2],
                                        p=[0.25, 0.25, 0.30, 0.15, 0.05]))
                degree = degree + step
                # gentle elastic pull toward centre (register discipline)
                degree = 8.0 + (degree - 8.0) * 0.85 + float(rng.normal(0, 0.25))
                pi = (degree % 5.0) / 5.0
                onset = bar_start + float(rng.uniform(0, BAR * 0.9))
                dur = float(rng.uniform(Q, BAR * 1.5))
                vel = int(rng.integers(58, 96))
                raw.append({
                    "section": s, "section_name": name, "bar": b,
                    "tick": onset, "pitch_index": pi,
                    "velocity": vel, "duration": dur,
                })
    return raw


def export_phase1(raw, path):
    """Raw single-voice draft -> phase1.mid (pre-rules), own validate() gate."""
    comp = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
    comp.create_matrix(num_voices=1, num_sections=N_SECTIONS)
    comp.add_voice("RawLead", program=SHAKUHACHI.midi_program, channel=0)
    for s, (name, _degs) in enumerate(SECTIONS):
        comp.add_section(name, bars=SECTION_BARS)
        ev = []
        for r in raw:
            if r["section"] != s:
                continue
            local = int(r["tick"]) - s * SECTION_LEN
            pitch = scale_pitch(int(r["pitch_index"] * 5) + 8)
            dur = max(S, int(r["duration"]))
            ev.append(MusicEvent(pitch=pitch, volume=r["velocity"],
                                 start_tick=max(0, local),
                                 end_tick=min(max(0, local) + dur, SECTION_LEN)))
        comp.fill_voice_section("RawLead", name, make_unit(ev, SECTION_LEN))
    ok, msg = comp.validate()
    if not ok:
        raise RuntimeError(f"phase1 validate failed: {msg}")
    comp.to_midi(path)
    return path


# ================================================================ PHASE 2 (rules)
def build_lead(s, degs, raw_sec):
    """Shakuhachi lead: quantize raw contour -> chord tones + grid + dedup,
    then apply the section's variation technique, then a voice-leading fix."""
    band = (60, 84)
    if s in (2, 3):            # register shift up (transposition / climax)
        band = (72, 96)
    notes = []                 # [onset, pitch, vel, end]
    for r in raw_sec:
        onset_local = r["tick"] - s * SECTION_LEN
        bar_local = int(max(0, onset_local) // BAR)
        bar_local = min(bar_local, SECTION_BARS - 1)
        deg = degs[bar_local]
        raw_pitch = scale_pitch(int(r["pitch_index"] * 5) + 8)
        if s in (2, 3):
            raw_pitch += 12
        pitch = nearest_chord_tone(raw_pitch, deg, band[0], band[1])
        snap = int(round(onset_local / S)) * S
        snap = max(0, min(snap, SECTION_LEN - S))
        dur = max(S, int(r["duration"]))
        if s == 4:              # augmentation (bridge): hold notes twice as long
            dur *= 2
        end = snap + dur
        if end > SECTION_LEN:
            end = SECTION_LEN
        notes.append([snap, pitch, int(r["velocity"]), end])

    if s == 5:                  # inversion around axis 74, re-quantized to chord
        for n in notes:
            bl = min(n[0] // BAR, SECTION_BARS - 1)
            n[1] = nearest_chord_tone(2 * 74 - n[1], degs[bl], band[0], band[1])
    if s == 6:                  # retrograde: reverse pitch sequence, re-quantize
        rev = [n[1] for n in notes][::-1]
        for i, n in enumerate(notes):
            bl = min(n[0] // BAR, SECTION_BARS - 1)
            n[1] = nearest_chord_tone(rev[i], degs[bl], band[0], band[1])

    # voice-leading fix: fold any >octave leap, re-quantize to bar chord
    vl_fixed = 0
    prev = None
    for n in sorted(notes, key=lambda x: x[0]):
        if prev is not None and abs(n[1] - prev[1]) > 12:
            while n[1] - prev[1] > 12:
                n[1] -= 12
            while prev[1] - n[1] > 12:
                n[1] += 12
            bl = min(n[0] // BAR, SECTION_BARS - 1)
            n[1] = nearest_chord_tone(n[1], degs[bl], band[0], band[1])
            vl_fixed += 1
        prev = n

    # dedup (onset, pitch) keep longest duration
    best = {}
    for n in notes:
        key = (n[0], n[1])
        if key not in best or (n[3] - n[0]) > (best[key][3] - best[key][0]):
            best[key] = n
    return sorted(best.values(), key=lambda x: x[0]), vl_fixed


def build_koto(s, degs):
    """Koto plucks on chord tones; per-section technique. Every pluck uses the
    chord of the bar it actually lands in (no cross-bar spill)."""
    ev = []

    if s in (0, 7):                      # sparse / ma: root on beat 1 of each bar
        for b in range(SECTION_BARS):
            deg = degs[b]
            cts = chord_tones_in_band(deg, 55, 84)
            ev.append(MusicEvent(cts[0], 80 if s == 0 else 60, b * BAR, b * BAR + 3 * Q))
    elif s in (1, 2):                    # sparse motif (source DNA)
        motif = [(0.0, 0), (2.5, 2), (3.5, 1), (4.0, 0), (6.5, 2)]
        for beat, ci in motif:
            bar_idx = int(beat // 4)
            deg = degs[bar_idx]
            cts = chord_tones_in_band(deg, 55, 84)
            t = bar_idx * BAR + int((beat % 4) * Q)
            ev.append(MusicEvent(cts[ci % len(cts)], 82, t, t + Q))
    elif s in (3, 5):                    # arpeggio roll (density rise)
        for b in range(SECTION_BARS):
            deg = degs[b]
            cts = chord_tones_in_band(deg, 55, 84)
            for k in range(8):
                t = b * BAR + k * E
                ev.append(MusicEvent(cts[k % len(cts)], 76, t, t + E))
    elif s == 4:                         # augmentation (half speed)
        for b in range(SECTION_BARS):
            deg = degs[b]
            cts = chord_tones_in_band(deg, 55, 84)
            for k in range(2):
                t = b * BAR + k * (2 * Q)
                ev.append(MusicEvent(cts[k % len(cts)], 74, t, t + Q))
    elif s == 6:                         # retrograde motif (time-reversed)
        motif = [(0.0, 0), (2.5, 2), (3.5, 1), (4.0, 0), (6.5, 2)]
        for beat, ci in reversed(motif):
            bar_idx = int(beat // 4)
            deg = degs[bar_idx]
            cts = chord_tones_in_band(deg, 55, 84)
            t = bar_idx * BAR + int((beat % 4) * Q)
            ev.append(MusicEvent(cts[ci % len(cts)], 78, t, t + Q))
    return ev


def build_shamisen(s, degs):
    """Shamisen ostinato: root + 4th, density per section."""
    ev = []
    for b in range(SECTION_BARS):
        deg = degs[b]
        bar = b * BAR
        root = fold_into(scale_pitch(deg), 57, 79)
        fourth = fold_into(scale_pitch(deg + 2), 57, 79)
        if s in (0, 7):                       # sparse quarter pulse (root only)
            for k in range(4):
                ev.append(MusicEvent(root, 58, bar + k * Q, bar + k * Q + Q))
        elif s in (3, 5):                     # 16th ostinato (density rise)
            for k in range(16):
                p = root if k % 2 == 0 else fourth
                ev.append(MusicEvent(p, 60, bar + k * S, bar + k * S + S))
        elif s == 4:                          # quarter (sparse, augmentation feel)
            for k in range(4):
                p = root if k % 2 == 0 else fourth
                ev.append(MusicEvent(p, 56, bar + k * Q, bar + k * Q + 2 * Q))
        else:                                 # 8th ostinato (source DNA)
            for k in range(8):
                p = root if k % 2 == 0 else fourth
                ev.append(MusicEvent(p, 60, bar + k * E, bar + k * E + E))
    return ev


def build_taiko(s):
    """Taiko on channel 9 kit (skipped by pitch/scale/grid audits)."""
    ev = []
    for b in range(SECTION_BARS):
        bar = b * BAR
        if s in (0, 4, 7):                    # sparse: beat 1 only
            vel = 100 if s == 0 else (92 if s == 4 else 60)   # fade in outro
            ev.append(MusicEvent(36, vel, bar, bar + Q))
        elif s in (3, 5):                     # dense: 1 + 3 + accents
            ev.append(MusicEvent(36, 100, bar, bar + Q))
            ev.append(MusicEvent(45, 84, bar + 2 * Q, bar + 2 * Q + Q))
            ev.append(MusicEvent(38, 70, bar + 3 * Q, bar + 3 * Q + E))
        else:                                 # beat 1 + beat 3
            ev.append(MusicEvent(36, 96, bar, bar + Q))
            ev.append(MusicEvent(45, 78, bar + 2 * Q, bar + 2 * Q + Q))
    return ev


# ================================================================ main
def main():
    for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
        os.makedirs(d, exist_ok=True)

    # ---- Phase 1 ----
    raw = gen_phase1_raw(SEED)
    with open(os.path.join(ANALYSIS_DIR, "phase1_raw.json"), "w") as f:
        json.dump(raw, f, indent=2, default=lambda x: round(float(x), 4))
    phase1_path = os.path.join(MIDI_DIR, "250-hirajoshi-ma-rework-phase1.mid")
    export_phase1(raw, phase1_path)
    assert os.path.getsize(phase1_path) > 40
    write_provenance(phase1_path, AI_ASSISTED,
                     "hirajoshi stochastic contour walk (raw) + musicom rules (phase2)",
                     parameters={"phase": 1, "seed": SEED, "bpm": BPM,
                                 "key": KEY_NAME, "style": "japanese hogaku",
                                 "notes": "pre-rules raw generative draft (single voice)"},
                     sources=["Japanese/001-japanese-hirajoshi"])

    # ---- Phase 2 ----
    comp = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
    comp.create_matrix(num_voices=4, num_sections=N_SECTIONS)
    comp.add_voice("Koto", program=KOTO.midi_program, channel=0)
    comp.add_voice("Shakuhachi", program=SHAKUHACHI.midi_program, channel=1)
    comp.add_voice("Shamisen", program=SHAMISEN.midi_program, channel=2)
    comp.add_voice("Taiko", program=0, channel=9)

    vl_total = 0
    for s, (name, degs) in enumerate(SECTIONS):
        comp.add_section(name, bars=SECTION_BARS)
        raw_sec = [r for r in raw if r["section"] == s]
        lead, vl = build_lead(s, degs, raw_sec)
        vl_total += vl
        comp.fill_voice_section("Shakuhachi", name, make_unit(
            [MusicEvent(p, v, st, en) for (st, p, v, en) in lead], SECTION_LEN))
        comp.fill_voice_section("Koto", name, make_unit(build_koto(s, degs), SECTION_LEN))
        comp.fill_voice_section("Shamisen", name, make_unit(build_shamisen(s, degs), SECTION_LEN))
        comp.fill_voice_section("Taiko", name, make_unit(build_taiko(s), SECTION_LEN))

    # ---- dual-version export (perfect + humanized) ----
    hz_instruments = {
        "Koto": KOTO.humanize_dna,
        "Shakuhachi": SHAKUHACHI.humanize_dna,
        "Shamisen": SHAMISEN.humanize_dna,
        "Taiko": by_name("taiko").humanize_dna,   # drum anchor (2.0,4.0,0.0,0.008)
    }
    perfect_path = os.path.join(MIDI_DIR, "250-hirajoshi-ma-rework-perfect.mid")
    humanized_path = os.path.join(MIDI_DIR, "250-hirajoshi-ma-rework-humanized.mid")
    hz = export_dual(comp, perfect_path, humanized_path,
                     style="classical", seed=SEED, bpm=BPM,
                     instruments=hz_instruments)
    assert os.path.getsize(perfect_path) > 40
    assert os.path.getsize(humanized_path) > 40

    # ---- provenance ----
    write_provenance(perfect_path, AI_ASSISTED,
                     "hirajoshi stochastic contour walk + musicom rules",
                     parameters={"phase": 2, "variant": "perfect", "seed": SEED,
                                 "bpm": BPM, "key": KEY_NAME,
                                 "style": "japanese hogaku",
                                 "humanize_seed": SEED, "humanize": "off"},
                     sources=["Japanese/001-japanese-hirajoshi"])
    write_provenance(humanized_path, AI_ASSISTED,
                     "hirajoshi stochastic contour walk + musicom rules + humanize",
                     parameters={"phase": 2, "variant": "humanized", "seed": SEED,
                                 "bpm": BPM, "key": KEY_NAME,
                                 "style": "japanese hogaku",
                                 "humanize_seed": SEED, "humanize": "style+instrument"},
                     sources=["Japanese/001-japanese-hirajoshi"])

    # ---- grid visualization ----
    write_grid_visualization(
        comp.matrix, os.path.join(ANALYSIS_DIR, "grid_visualization.txt"),
        ticks_per_character=240,
        voice_names=["Koto", "Shakuhachi", "Shamisen", "Taiko"], bpm=BPM)

    # ---- summary (numbers for REPORT + provenance) ----
    summary = {
        "seed": SEED, "bpm": BPM, "key": KEY_NAME,
        "sections": N_SECTIONS, "bars": N_SECTIONS * SECTION_BARS,
        "section_roots_midpoint": SECTION_ROOTS,
        "global_deg": GLOBAL_DEG,
        "voice_leading_fixed": vl_total,
        "humanize": hz,
        "variations": {
            "Jo": "sparse ma intro", "Ha": "theme A (quantized raw contour)",
            "Ha2": "transposition / register +12",
            "Kyu": "climax: register +12, koto arpeggio, shamisen 16th (density rise)",
            "Bridge": "augmentation (durations x2, half-speed koto)",
            "Kyu2": "inversion around axis 74, re-quantized",
            "Develop": "retrograde + re-harmonize",
            "Jo2": "sparse ma outro, fade",
        },
    }
    with open(os.path.join(ANALYSIS_DIR, "composition_summary.json"), "w") as f:
        json.dump(summary, f, indent=2)
    print("SUMMARY", json.dumps(summary, indent=2))
    print(f"OK phase1={phase1_path}")
    print(f"OK perfect={perfect_path}")
    print(f"OK humanized={humanized_path}")


if __name__ == "__main__":
    main()
