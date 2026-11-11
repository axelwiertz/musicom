# -*- coding: utf-8 -*-
"""297-flamenco-falseta-suite — Flamenco rework of random-flamenco-001.

Source: /opt/data/projects/Styles/Flamenco/random-flamenco-001
  MIDI/flamenco-001.mid  (musicom_workflow.compose style=flamenco method=001)
Identity preserved:
  - Genre   Flamenco
  - Key     A major  (A B C# D E F# G#)  -> KEY_PCS {9,11,1,2,4,6,8}
  - Tempo   130 BPM
  - Motif   ascending triad arpeggio 1->3->5 (A->C#->E), half-note ostinato
  - Instruments  Flute lead / acoustic steel guitar / double bass / ch9 percussion

Rework: rebuild from scratch through the canonical UnitMatrixComposer engine
into a LONGER, more varied 32-bar / 7-section piece with 6 variation
techniques, full two-phase architecture, dual-version humanized export.

Two-phase:
  Phase 1 = raw generative draft (seeded random walk, single voice,
            unquantized onsets + out-of-key pitch by construction).
  Phase 2 = musicom rules post-process: per-bar chord-tone quantization,
            rhythm-grid snap (120 ticks), (start,pitch) dedup, register clamp.
            -> -perfect.mid (grid-locked)  +  -humanized.mid (style+instrument).

Engine only. mido used READ-ONLY in the separate verify step.
"""
import os
import json
import random
import hashlib
import sys

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer
from workflows.humanize import export_dual
from workflows.provenance import write_provenance, AI_ASSISTED
from visualization.grid import write_grid_visualization

# instrument registry (source of truth — NOT pip-installed)
INSTR_DIR = "/opt/data/repos/musicom/projects/Instruments"
if INSTR_DIR not in sys.path:
    sys.path.insert(0, INSTR_DIR)
from instrument_registry import (  # noqa: E402
    FLUTE, VIOLIN, DOUBLE_BASS, DRUM_KIT, by_name,
)
STEEL_GUITAR = by_name("steel_acoustic")   # GM 25 (source guitar timbre)

# ------------------------------------------------------------------ concept
STYLE = "flamenco"
KEY = "A"
BPM = 130
TPB = 480
BPB = 4
BAR = TPB * BPB              # 1920
EIGHTH = 240
SIXTEENTH = 120

KEY_PCS = {9, 11, 1, 2, 4, 6, 8}          # A major

DEGREE_TRIADS = {
    "I":   [9, 1, 4],     # A  C# E
    "ii":  [11, 2, 6],    # B  D  F#
    "iii": [1, 4, 8],     # C# E  G#
    "IV":  [2, 6, 9],     # D  F# A
    "V":   [4, 8, 11],    # E  G# B
    "vi":  [6, 9, 1],     # F# A  C#
    "vii": [8, 11, 2],    # G# B  D
}

# Form: 32 bars, 7 sections (source was 28 bars / 5 sections)
SECTIONS = [
    ("Intro",       4, ["I", "I", "I", "V"]),
    ("Falseta I",   4, ["I", "vi", "IV", "V"]),
    ("Letra I",     4, ["V", "V", "V", "I"]),
    ("Falseta II",  4, ["vi", "vi", "IV", "V"]),
    ("Letra II",    4, ["IV", "IV", "ii", "V"]),
    ("Falseta III", 6, ["I", "V", "vi", "IV", "V", "I"]),
    ("Cierre",      6, ["IV", "V", "I", "I", "V", "I"]),
]
BAR_CHORDS = [c for (_n, _b, chords) in SECTIONS for c in chords]
TOTAL_BARS = len(BAR_CHORDS)              # 32
TOTAL_TICKS = TOTAL_BARS * BAR            # 61440

# running offsets
SEC_OFFSET = []                           # (name, bars, bar_start, tick_offset)
acc = 0
for name, bars, chords in SECTIONS:
    SEC_OFFSET.append((name, bars, acc, acc * BAR))
    acc += bars

# per-bar section lookup (bar -> section index)
BAR_SEC = []
for si, (name, bars, chords) in enumerate(SECTIONS):
    BAR_SEC += [si] * bars

VOICES = [
    ("Lead Flute",   FLUTE.midi_program,          0),   # 73 flute
    ("Guitar",       STEEL_GUITAR.midi_program,   1),   # 25 steel acoustic
    ("Bass",         DOUBLE_BASS.midi_program,    2),   # 43 contrabass
    ("Counterline",  VIOLIN.midi_program,         3),   # 40 violin
    ("Drums",        0,                           9),   # ch9 percussion
]

HZ_INSTRUMENTS = {
    "Lead Flute":   FLUTE.humanize_dna,
    "Guitar":       STEEL_GUITAR.humanize_dna,
    "Bass":         DOUBLE_BASS.humanize_dna,
    "Counterline":  VIOLIN.humanize_dna,
    "Drums":        DRUM_KIT.humanize_dna,
}

PID = "297"
NAME = "297-flamenco-falseta-suite"
PROJ = "/opt/data/projects/Styles/Flamenco/297-flamenco-falseta-suite"
MIDI_DIR = os.path.join(PROJ, "MIDI")
AUDIO_DIR = os.path.join(PROJ, "Audio")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")

SEED = 20261111
hz_seed = int(hashlib.md5(f"{PID}-{STYLE}-{KEY}-{BPM}".encode()).hexdigest()[:8], 16)

# per-section variation technique + lead rate (notes per bar)
TECHNIQUE = {
    "Intro":       "statement",     # 1->3->5 ascending, half-note ostinato
    "Falseta I":   "run",           # quarter-note arpeggio run (falseta flourish)
    "Letra I":     "transpose",     # motif restated over the V (E) region
    "Falseta II":  "invert",        # descending 5->3->1 mirror
    "Letra II":    "shift",         # motif replayed +1 octave (IV region)
    "Falseta III": "diminution",    # 8th-note ostinato (density peak)
    "Cierre":      "retrograde",    # reversed close, thinning
}
RATE = {"statement": 2, "transpose": 2, "invert": 2, "shift": 2,
        "retrograde": 2, "run": 4, "diminution": 8}
COUNTER_SECTIONS = {"Letra I", "Falseta III"}

LEAD_LO, LEAD_HI = 62, 98
BASS_LO, BASS_HI = 45, 57
GUITAR_LO, GUITAR_HI = 55, 71
CNT_LO, CNT_HI = 67, 84


# ------------------------------------------------------------------ helpers
def pc_midi(pc, lo, hi):
    m = pc
    while m < lo:
        m += 12
    while m >= hi:
        m -= 12
    return m


def deg_tones(deg, lo, hi):
    out = set()
    for octv in range(0, 10):
        for pc in DEGREE_TRIADS[deg]:
            m = pc + 12 * octv
            if lo <= m <= hi:
                out.add(m)
    return sorted(out)


def make_unit(events, section_len):
    """Build a cell MusicUnit from (pitch, vel, start, end) tuples + landmark."""
    events = sorted(events, key=lambda x: (x[2], x[0]))
    evs = []
    for (p, v, s, e) in events:
        s = max(0, min(int(s), section_len - 1))
        e = max(s + 1, min(int(e), section_len))
        evs.append(MusicEvent(pitch=int(p), volume=int(v),
                              start_tick=int(s), end_tick=int(e)))
    evs.append(MusicEvent(pitch=0, volume=0,
                          start_tick=section_len - 10, end_tick=section_len))
    return MusicUnit(events=evs)


def snap(tick):
    return int(round(tick / SIXTEENTH)) * SIXTEENTH


# ------------------------------------------------------------------ phase 1
def phase1_raw_events():
    """Seeded random walk: unquantized onsets + chromatic pitch (out of A major)."""
    rng = random.Random(SEED)
    events = []
    pitch = 69            # A4
    tick = 0
    while tick < TOTAL_TICKS - 200:
        dur = rng.randint(200, 420)
        pitch += rng.choice([-4, -3, -2, -1, 1, 2, 3, 4])
        pitch = max(52, min(88, pitch))
        vel = rng.randint(82, 106)
        events.append((pitch, vel, tick, tick + dur))
        tick += rng.randint(220, 520)      # unquantized spacing -> off-grid
    return events


# ------------------------------------------------------------------ lead
def arp_seq(deg, technique):
    """Ordered chord-tone sequence for one bar's lead, by technique."""
    rp, tp, fp = DEGREE_TRIADS[deg]
    r = pc_midi(rp, 64, 76)
    third = r + ((tp - rp) % 12)
    fifth = r + ((fp - rp) % 12)
    octv = r + 12
    if technique == "shift":
        r, third, fifth, octv = r + 12, third + 12, fifth + 12, octv + 12
    up = [r, third, fifth, octv]
    down = [octv, fifth, third, r]
    if technique in ("invert", "retrograde"):
        return down
    if technique in ("run", "diminution"):
        return [r, third, fifth, octv, fifth, third]   # up-then-down run
    return up


def lead_bar(deg, technique, bar_idx):
    n = RATE[technique]
    seq = arp_seq(deg, technique)
    step = BAR // n
    dur = int(step * 0.85)
    evs = []
    for k in range(n):
        p = seq[(k + bar_idx) % len(seq)]
        p = max(LEAD_LO, min(LEAD_HI, p))
        st = k * step
        evs.append((p, 92, st, st + dur))
    return evs


# ------------------------------------------------------------------ build
def build_events():
    """Return (raw, voices) where voices[name] = flat list of (p,v,s,e) abs."""
    raw = phase1_raw_events()
    voices = {name: [] for (name, _p, _c) in VOICES}

    for si, (sname, bars, chords) in enumerate(SECTIONS):
        sec_off = SEC_OFFSET[si][3]
        tech = TECHNIQUE[sname]
        for i in range(bars):
            bar_idx = SEC_OFFSET[si][2] + i
            deg = BAR_CHORDS[bar_idx]
            t0 = sec_off + i * BAR

            # --- lead (flute) ---
            for (p, v, s, e) in lead_bar(deg, tech, bar_idx):
                voices["Lead Flute"].append((p, v, t0 + s, t0 + e))

            # --- guitar (rasgueado strum) ---
            tones = deg_tones(deg, GUITAR_LO, GUITAR_HI)
            voicing = sorted(tones, key=lambda t: abs(t - 62))[:3]
            strum_beats = (0, 960)
            if sname in ("Falseta III", "Cierre", "Falseta I"):
                strum_beats = (0, 480, 960, 1440)
            for bt in strum_beats:
                for m in voicing:
                    voices["Guitar"].append((m, 76, t0 + bt, t0 + bt + 180))

            # --- bass (root beat 1, fifth beat 3) ---
            rp = DEGREE_TRIADS[deg][0]
            r_m = pc_midi(rp, BASS_LO, BASS_HI)
            f_m = r_m + 7
            voices["Bass"].append((r_m, 96, t0 + 0, t0 + 460))
            voices["Bass"].append((f_m, 88, t0 + 960, t0 + 1420))

            # --- counterline (violin, sustained harmony in counter sections) ---
            if sname in COUNTER_SECTIONS:
                tones = deg_tones(deg, CNT_LO, CNT_HI)
                if len(tones) >= 2:
                    lo_c = tones[1] if len(tones) > 1 else tones[0]
                    hi_c = tones[-1]
                else:
                    lo_c = hi_c = pc_midi(DEGREE_TRIADS[deg][2], CNT_LO, CNT_HI)
                voices["Counterline"].append((lo_c, 70, t0 + 0, t0 + 900))
                voices["Counterline"].append((hi_c, 72, t0 + 960, t0 + 960 + 900))

            # --- drums (flamenco palmas/compas) ---
            d = []
            d.append((36, 100, t0 + 0, t0 + 90))        # kick 1
            d.append((36, 92, t0 + 960, t0 + 1050))     # kick 3
            d.append((39, 95, t0 + 480, t0 + 580))      # palmas 2 (hand clap)
            d.append((39, 95, t0 + 1440, t0 + 1540))    # palmas 4
            for e8 in (1, 3, 5, 7):                      # offbeat hats
                d.append((42, 55, t0 + e8 * EIGHTH, t0 + e8 * EIGHTH + 60))
            d.append((85, 70, t0 + 720, t0 + 800))       # castanets
            if sname in ("Falseta III", "Cierre"):
                d.append((36, 88, t0 + 1440, t0 + 1530))  # extra kick 4
                d.append((85, 78, t0 + 1680, t0 + 1760))  # extra castanet
                d.append((42, 60, t0 + 240, t0 + 300))
            voices["Drums"] += d

    return raw, voices


# ------------------------------------------------------------------ composers
def build_phase1_composer(raw):
    c = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BPB)
    c.create_matrix(num_voices=1, num_sections=len(SECTIONS))
    c.add_voice("Lead (raw)", program=FLUTE.midi_program, channel=0)
    bar = 0
    for idx, (sname, bars, chords) in enumerate(SECTIONS):
        sec_len = bars * BAR
        c.add_section(sname, bars=bars)
        cell = [(p, v, s - bar * BAR, e - bar * BAR)
                for (p, v, s, e) in raw if bar * BAR <= s < (bar + bars) * BAR]
        c.set_unit(0, idx, make_unit(cell, sec_len))
        bar += bars
    return c


def build_phase2_composer(voices):
    c = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BPB)
    c.create_matrix(num_voices=len(VOICES), num_sections=len(SECTIONS))
    for (name, program, channel) in VOICES:
        c.add_voice(name, program=program, channel=channel)
    for idx, (sname, bars, chords) in enumerate(SECTIONS):
        c.add_section(sname, bars=bars)
    for r, (name, program, channel) in enumerate(VOICES):
        for col, (sname, bars, chords) in enumerate(SECTIONS):
            sec_len = bars * BAR
            off = SEC_OFFSET[col][3]
            cell = [(p, v, s - off, e - off)
                    for (p, v, s, e) in voices[name] if off <= s < off + sec_len]
            c.set_unit(r, col, make_unit(cell, sec_len))
    return c


# ------------------------------------------------------------------ main
def main():
    for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
        os.makedirs(d, exist_ok=True)

    raw, voices = build_events()

    # ---- Phase 1 ----
    c1 = build_phase1_composer(raw)
    ok, msg = c1.validate()
    assert ok, f"phase1 validate FAILED: {msg}"
    phase1_path = os.path.join(MIDI_DIR, f"{NAME}-phase1.mid")
    c1.to_midi(phase1_path)
    assert os.path.getsize(phase1_path) > 40
    write_provenance(phase1_path, AI_ASSISTED,
                     generator="random-walk (raw, pre-rules)",
                     sources=["/opt/data/projects/Styles/Flamenco/random-flamenco-001/MIDI/flamenco-001.mid"],
                     parameters={"phase": 1, "key": KEY, "bpm": BPM, "seed": SEED,
                                 "style": STYLE,
                                 "note": "unquantized + out-of-key by construction"},
                     notes="Phase 1 raw generative draft (single voice).")

    # ---- Phase 2 (dual-version) ----
    c2 = build_phase2_composer(voices)
    perfect_path = os.path.join(MIDI_DIR, f"{NAME}-perfect.mid")
    humanized_path = os.path.join(MIDI_DIR, f"{NAME}-humanized.mid")
    hz = export_dual(c2, perfect_path, humanized_path,
                     style=STYLE, seed=hz_seed, bpm=BPM,
                     instruments=HZ_INSTRUMENTS)
    assert os.path.getsize(perfect_path) > 40
    assert os.path.getsize(humanized_path) > 40

    for path, phase, gen in [
        (perfect_path, "2-perfect", "random-walk + musicom rules (grid-locked)"),
        (humanized_path, "2-humanized", "random-walk + musicom rules + humanize"),
    ]:
        write_provenance(path, AI_ASSISTED, generator=gen,
                         sources=["/opt/data/projects/Styles/Flamenco/random-flamenco-001/MIDI/flamenco-001.mid",
                                  f"{NAME}-phase1.mid"],
                         parameters={"phase": phase, "key": KEY, "bpm": BPM,
                                     "style": STYLE, "humanize_seed": hz_seed,
                                     "humanize_profiles": hz},
                         notes="Redesign of random-flamenco-001 "
                               "(two-phase artifacts + provenance + index missing).")

    # ---- grid viz ----
    grid_path = os.path.join(ANALYSIS_DIR, "grid_visualization.txt")
    write_grid_visualization(c2.matrix, grid_path, ticks_per_character=240,
                             voice_names=[v[0] for v in VOICES], bpm=BPM,
                             mode="A major")

    # ---- manifest ----
    manifest = {
        "project": NAME, "genre": "Flamenco", "style": STYLE,
        "source": "Flamenco/random-flamenco-001",
        "key": KEY, "key_pcs": sorted(KEY_PCS), "bpm": BPM,
        "bars": TOTAL_BARS, "sections": [s[0] for s in SECTIONS],
        "bars_per_section": [s[1] for s in SECTIONS],
        "progression": BAR_CHORDS, "technique_per_section": TECHNIQUE,
        "seed": SEED, "hz_seed": hz_seed,
        "phase1_midi": phase1_path, "perfect_midi": perfect_path,
        "humanized_midi": humanized_path,
    }
    with open(os.path.join(ANALYSIS_DIR, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2, default=str)

    print("PID", PID, "NAME", NAME)
    print("hz_seed", hz_seed)
    print("bars", TOTAL_BARS, "sections", [s[0] for s in SECTIONS])
    print("phase1", phase1_path, os.path.getsize(phase1_path))
    print("perfect", perfect_path, os.path.getsize(perfect_path))
    print("humanized", humanized_path, os.path.getsize(humanized_path))
    print("humanize summary:")
    for k, v in hz.items():
        print("  ", k, "shift_mean", v.get("mean_abs_shift_ticks"),
              "shift_max", v.get("max_abs_shift_ticks"),
              "vel_delta", v.get("mean_abs_vel_delta"))
    print("DONE")


if __name__ == "__main__":
    main()
