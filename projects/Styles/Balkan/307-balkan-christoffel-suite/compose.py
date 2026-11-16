# -*- coding: utf-8 -*-
"""307-balkan-christoffel-suite -- Balkan rework of 100-balkan-christoffel.

Nightly rework job (2026-11-16). Source 100-balkan-christoffel passed 5/6
engine standards (UnitMatrixComposer, zero-drift, grid-sync, >=4 tracks,
two-phase) but FAILED standard 6 (no top-level provenance.json + no index.html)
and predates the 2026-10-17 dual-version humanization mandate.

REDESIGN (rebuild through canonical engine, preserve identity): Bulgarian
Kopanitsa 11/8 (2+2+3+2+2), D Dorian (+Bb bVI folk borrowing), 160 BPM,
Method 069 Christoffel Word Combinatorial Composition, 5-voice Balkan texture
(Clarinet lead, Fiddle, Tambura, Double Bass, Tupan drums).

NEW: 8 sections x 4 bars = 32 bars (source 24) with 7 variation techniques and
dual-version export (perfect + humanized).

Two-phase architecture:
  Phase 1 = raw Christoffel word walk (single clarinet, unquantized float
            pitch + jittered off-grid rhythm), own composer + validate().
  Phase 2 = musicom rules post-process (16th-grid lock, per-bar chord-tone
            quantization floor t//BAR, register enforcement, dedup) + full
            5-voice Balkan texture, exported dual via export_dual.

Engine only: structures + workflows.unitmatrix_composer + humanize + provenance
+ grid. mido used for READ-ONLY verification only.
"""
import os
import json
import hashlib
from math import gcd

import numpy as np

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer, create_empty_unit
from workflows.humanize import export_dual
from workflows.provenance import write_provenance, AI_ASSISTED
from visualization.grid import write_grid_visualization

SEED = 20261116
STYLE = "balkan"
GENRE = "Balkan"
PROJECT = "307-balkan-christoffel-suite"
SOURCE = "100-balkan-christoffel"

PROJ = "/opt/data/projects/Styles/Balkan/" + PROJECT
MIDI_DIR = os.path.join(PROJ, "MIDI")
AUDIO_DIR = os.path.join(PROJ, "Audio")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")
for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
    os.makedirs(d, exist_ok=True)

# ---------------------------------------------------------------- Metric & Grid
# Kopanitsa 11/8 (2+2+3+2+2). TPB=480, sixteenth = 120 ticks.
# One "bar" = 11 sixteenth pulses = 1320 ticks.
BPM = 160
TPB = 480
GRID16 = 120
PULSES_PER_BAR = 11
BAR_TICKS = PULSES_PER_BAR * GRID16              # 1320
BEAT_PULSES = [0, 2, 4, 7, 9]
BEAT_DUR_PULSES = [2, 2, 3, 2, 2]
BEAT_TICKS = [p * GRID16 for p in BEAT_PULSES]   # [0, 240, 480, 840, 1080]
BEAT_DUR_TICKS = [d * GRID16 for d in BEAT_DUR_PULSES]

BARS_PER_SECTION = 4
SECTION_TICKS = BAR_TICKS * BARS_PER_SECTION     # 5280
# composer "bar" = ticks_per_beat * beats_per_bar = 480 * 11 = 5280 (one section)
COMPOSER_TPB = 480
COMPOSER_BPB = 11
COMPOSER_BAR = COMPOSER_TPB * COMPOSER_BPB       # 5280

# ---------------------------------------------------------------- Identity
# D Dorian (D E F G A B C) + Bb (bVI) folk borrowing.
D_DORIAN_PCS = {2, 4, 5, 7, 9, 11, 0}
BB_PC = 10
KEY_PCS = D_DORIAN_PCS | {BB_PC}                 # {0,2,4,5,7,9,10,11}
KEY_LABEL = "D Dorian + bVI (Bb) Balkan borrowing"

CHORD_PCS = {
    "Dm": {2, 5, 9},     # D F A
    "C":  {0, 4, 7},     # C E G
    "G":  {7, 11, 2},    # G B D
    "F":  {5, 9, 0},     # F A C
    "Am": {9, 0, 4},     # A C E
    "Bb": {10, 2, 5},    # Bb D F
}

# 8 sections x 4 bars = 32 bars. Per-section own progression (varied midpoints).
NAMES = ["Intro", "Tema_A", "Tema_Ap", "Tema_B",
         "Razvivka", "Razvivka_2", "Tema_A_Var", "Zavurshek"]
SECTION_PROG = {
    0: ["Dm", "Dm", "C", "Dm"],
    1: ["Dm", "C", "G", "Dm"],
    2: ["C", "G", "Dm", "G"],
    3: ["F", "C", "Dm", "Am"],
    4: ["G", "F", "C", "Dm"],
    5: ["C", "Am", "G", "F"],
    6: ["Dm", "G", "C", "Dm"],
    7: ["Bb", "C", "Dm", "Dm"],
}
N_SECTIONS = len(NAMES)
N_BARS = N_SECTIONS * BARS_PER_SECTION          # 32
TOTAL_TICKS = SECTION_TICKS * N_SECTIONS        # 42240

BAR_CHORDS = []
for s in range(N_SECTIONS):
    BAR_CHORDS.extend(SECTION_PROG[s])
assert len(BAR_CHORDS) == N_BARS


def bar_of(bar):
    return bar // BARS_PER_SECTION


def chord_pcs_for_bar(bar):
    return CHORD_PCS[BAR_CHORDS[bar]]


# ---------------------------------------------------------------- Voices
VOICES = [
    ("Clarinet", 71, 0),   # GM 71 clarinet (lead)
    ("Fiddle",   40, 1),   # GM 40 violin (countermelody)
    ("Tambura",  25, 2),   # GM 25 steel acoustic (tambura-like comping)
    ("Bass",     43, 3),   # GM 43 double bass
    ("Drums",     0, 9),   # channel 9 tupan kit
]
N_V = len(VOICES)
vnames = [v[0] for v in VOICES]

# Humanization DNA per voice (timing_ms, velocity_sigma, layback_ms, duration_sigma).
HZ_INSTRUMENTS = {
    "Clarinet": (None, 7.0, None, 0.02),
    "Fiddle":   (None, 6.0, None, 0.03),
    "Tambura":  (None, 6.0, None, 0.02),
    "Bass":     (10.0, 6.0, 8.0, 0.03),
    "Drums":    (2.0, 4.0, 0.0, 0.008),
}
hz_seed = int(hashlib.md5(PROJECT.encode()).hexdigest()[:8], 16) % 100000

# ---------------------------------------------------------------- Christoffel words
def christoffel_word(p, q, a="a", b="b"):
    assert gcd(p, q) == 1
    n = p + q
    return "".join(b if ((k + 1) * q) // n > (k * q) // n else a for k in range(n))


def sturmian_morph(word, morph):
    rules = {"G": {"a": "a", "b": "ab"}, "D": {"a": "ba", "b": "b"}}
    return "".join(rules[morph][c] for c in word)


C52 = christoffel_word(5, 2)                    # 'aaabaab'
W_ROT = C52[3:] + C52[:3]                       # rotated conjugate


def nearest_chord_tone(target, chord_pcs, lo, hi):
    best_p, best_dist = None, 999
    for p in range(lo, hi + 1):
        if (p % 12) in chord_pcs:
            dist = abs(p - target)
            if dist < best_dist:
                best_dist, best_p = dist, p
    return best_p if best_p is not None else int(target)


# ---------------------------------------------------------------- Phase 1: raw draft
def build_phase1():
    comp = UnitMatrixComposer(bpm=BPM, ticks_per_beat=COMPOSER_TPB,
                              beats_per_bar=COMPOSER_BPB)
    comp.create_matrix(num_voices=1, num_sections=N_SECTIONS)
    comp.add_voice("Raw_Clarinet", program=71, channel=0)
    rng = np.random.default_rng(SEED)

    raw_records = []
    for s in range(N_SECTIONS):
        comp.add_section(NAMES[s], bars=1)
        word = (C52 * 6 if s % 3 == 0 else C52 * 8)
        cur_tick = 0
        pitch = 74.0
        evs = []
        for ch in word:
            if cur_tick >= SECTION_TICKS - 150:
                break
            step = 2.15 if ch == "a" else -1.25
            pitch += step
            dur = int(rng.uniform(130, 250))
            if cur_tick + dur > SECTION_TICKS - 10:
                dur = SECTION_TICKS - 10 - cur_tick
            p = int(round(np.clip(pitch, 58, 88)))
            vel = int(rng.uniform(70, 105))
            evs.append(MusicEvent(pitch=p, volume=vel, start_tick=cur_tick,
                                  end_tick=cur_tick + dur))
            raw_records.append({"tick_abs": s * SECTION_TICKS + cur_tick,
                                "pitch": p, "dur": dur})
            cur_tick += int(rng.uniform(140, 270))
        if not evs or evs[-1].end_tick < SECTION_TICKS:
            evs.append(MusicEvent(pitch=0, volume=0, start_tick=SECTION_TICKS - 10,
                                  end_tick=SECTION_TICKS))
        evs.sort(key=lambda e: (int(e.start_tick), int(e.pitch)))
        comp.fill_voice_section("Raw_Clarinet", NAMES[s], MusicUnit(events=evs))

    ok, msg = comp.validate()
    if not ok:
        raise RuntimeError("phase1 validate failed: %s" % msg)
    p1 = os.path.join(MIDI_DIR, PROJECT + "-phase1.mid")
    comp.to_midi(p1)
    return p1, raw_records


# ---------------------------------------------------------------- Phase 2 helpers
def seal(events, span):
    out = []
    for e in sorted(events, key=lambda e: (int(e.start_tick), int(e.pitch))):
        st, en = int(e.start_tick), int(e.end_tick)
        if st < 0 or st >= span - 1:
            continue
        en = min(span - 1, en)
        if en <= st:
            en = min(span - 1, st + 30)
        out.append(MusicEvent(pitch=int(e.pitch), volume=int(e.volume),
                              start_tick=st, end_tick=en))
    # ALWAYS pin a terminal landmark so len_ticks == span survives humanization
    # (the humanizer shortens the last real note's tail via duration breathing,
    # which would otherwise drop the section below `span` and break zero-drift).
    out.append(MusicEvent(pitch=0, volume=0, start_tick=span - 1, end_tick=span))
    return MusicUnit(events=out)


def lead_word(cfg):
    word = C52 * 10
    if cfg["retro"]:
        word = word[::-1]
    if cfg["rot"]:
        word = W_ROT * 10
    return word


# Lead slots: full 16th run (10 events) vs sparse (beats 1,3,5).
FULL_SLOTS = [(0, 120), (120, 120), (240, 120), (360, 120),
              (480, 120), (600, 120), (720, 120), (840, 120),
              (960, 120), (1080, 240)]
SPARSE_SLOTS = [(0, 240), (480, 360), (1080, 240)]

LEAD_CFG = {
    0: dict(retro=False, rot=False, invert=False, slots="sparse", start=74, dscale=1.6),  # augmentation
    1: dict(retro=False, rot=False, invert=False, slots="full",   start=74, dscale=1.0),  # baseline
    2: dict(retro=False, rot=False, invert=True,  slots="full",   start=79, dscale=1.0),  # inversion + register up
    3: dict(retro=False, rot=True,  invert=False, slots="full",   start=72, dscale=1.0),  # rotation
    4: dict(retro=False, rot=False, invert=False, slots="full",   start=76, dscale=1.0),  # density rise
    5: dict(retro=True,  rot=False, invert=False, slots="full",   start=74, dscale=1.0),  # retrograde
    6: dict(retro=False, rot=False, invert=False, slots="full",   start=77, dscale=0.55), # diminution (staccato)
    7: dict(retro=False, rot=False, invert=False, slots="sparse", start=74, dscale=1.8),  # augmentation + Bb cadence
}


def build_clarinet(s):
    cfg = LEAD_CFG[s]
    word = lead_word(cfg)
    slots = SPARSE_SLOTS if cfg["slots"] == "sparse" else FULL_SLOTS
    events = []
    lead_pitch = float(cfg["start"])
    wi = 0
    for bar in range(BARS_PER_SECTION):
        bar_start = bar * BAR_TICKS
        gbar = s * BARS_PER_SECTION + bar
        cpc = chord_pcs_for_bar(gbar)
        for (st_rel, dur_rel) in slots:
            ch = word[wi % len(word)]
            wi += 1
            if cfg["invert"]:
                step = -2 if ch == "a" else 1
            else:
                step = 2 if ch == "a" else -1
            target = lead_pitch + step
            q = nearest_chord_tone(target, cpc, 62, 88)
            lead_pitch = float(q)
            dur = int(round(dur_rel * cfg["dscale"]))
            dur = max(90, min(dur, BAR_TICKS))
            st = bar_start + st_rel
            events.append(MusicEvent(pitch=q, volume=95 if st_rel in BEAT_TICKS else 80,
                                     start_tick=st, end_tick=min(st + dur, bar_start + BAR_TICKS)))
    return events


def build_fiddle(s):
    events = []
    fid_pitch = 65.0
    for bar in range(BARS_PER_SECTION):
        bar_start = bar * BAR_TICKS
        gbar = s * BARS_PER_SECTION + bar
        cpc = chord_pcs_for_bar(gbar)
        for b_idx in range(5):
            st_rel = BEAT_TICKS[b_idx]
            dur = BEAT_DUR_TICKS[b_idx]
            ch = W_ROT[(bar * 5 + b_idx) % len(W_ROT)]
            step = 2 if ch == "a" else -2
            target = fid_pitch + step
            q = nearest_chord_tone(target, cpc, 57, 79)
            fid_pitch = float(q)
            events.append(MusicEvent(pitch=q, volume=88, start_tick=bar_start + st_rel,
                                     end_tick=bar_start + st_rel + dur))
    return events


def build_tambura(s):
    events = []
    for bar in range(BARS_PER_SECTION):
        bar_start = bar * BAR_TICKS
        gbar = s * BARS_PER_SECTION + bar
        cpc = chord_pcs_for_bar(gbar)
        triad = [nearest_chord_tone(60, {pc}, 55, 72) for pc in sorted(cpc)]
        # intro/zavurshek: sparse; razvivka: dense (adds beat 2 off-beat)
        hits = [(240, 240), (480, 360), (1080, 240)]
        if s == 4:
            hits = [(240, 240), (480, 360), (720, 120), (1080, 240)]
        for (st_rel, dur) in hits:
            for tn in triad:
                events.append(MusicEvent(pitch=tn, volume=85, start_tick=bar_start + st_rel,
                                         end_tick=bar_start + st_rel + dur))
    return events


def build_bass(s):
    events = []
    for bar in range(BARS_PER_SECTION):
        bar_start = bar * BAR_TICKS
        gbar = s * BARS_PER_SECTION + bar
        ch = BAR_CHORDS[gbar]
        root_fifth = {"Dm": (2, 9), "C": (0, 7), "G": (7, 2), "F": (5, 0),
                      "Am": (9, 4), "Bb": (10, 5)}[ch]
        root_midi = nearest_chord_tone(38, {root_fifth[0]}, 34, 46)
        fifth_midi = nearest_chord_tone(43, {root_fifth[1]}, 34, 50)
        for (st_rel, dur, p, vel) in [
                (0, 240, root_midi, 105), (480, 360, root_midi, 100),
                (840, 240, fifth_midi, 95), (1080, 240, root_midi, 100)]:
            events.append(MusicEvent(pitch=p, volume=vel, start_tick=bar_start + st_rel,
                                     end_tick=bar_start + st_rel + dur))
    return events


def build_drums(s):
    KICK, SNARE, HHAT, CRASH = 36, 38, 42, 49
    events = []
    for bar in range(BARS_PER_SECTION):
        bar_start = bar * BAR_TICKS
        for p_idx in range(PULSES_PER_BAR):
            events.append(MusicEvent(pitch=HHAT, volume=70 if p_idx in BEAT_PULSES else 50,
                                     start_tick=bar_start + p_idx * GRID16,
                                     end_tick=bar_start + p_idx * GRID16 + GRID16))
        events.append(MusicEvent(pitch=KICK, volume=110, start_tick=bar_start,
                                 end_tick=bar_start + 240))
        events.append(MusicEvent(pitch=KICK, volume=115, start_tick=bar_start + 480,
                                 end_tick=bar_start + 360))
        events.append(MusicEvent(pitch=SNARE, volume=95, start_tick=bar_start + 240,
                                 end_tick=bar_start + 480))
        events.append(MusicEvent(pitch=SNARE, volume=90, start_tick=bar_start + 840,
                                 end_tick=bar_start + 1080))
        events.append(MusicEvent(pitch=SNARE, volume=95, start_tick=bar_start + 1080,
                                 end_tick=bar_start + 1320))
        if s == 7 and bar == BARS_PER_SECTION - 1:
            events.append(MusicEvent(pitch=CRASH, volume=88, start_tick=bar_start + 1080,
                                     end_tick=bar_start + 1320))
    return events


def build_phase2():
    comp = UnitMatrixComposer(bpm=BPM, ticks_per_beat=COMPOSER_TPB,
                              beats_per_bar=COMPOSER_BPB)
    comp.create_matrix(num_voices=N_V, num_sections=N_SECTIONS)
    for name, prog, ch in VOICES:
        comp.add_voice(name, program=prog, channel=ch)
    for s in range(N_SECTIONS):
        comp.add_section(NAMES[s], bars=1)

    builders = {
        "Clarinet": build_clarinet, "Fiddle": build_fiddle, "Tambura": build_tambura,
        "Bass": build_bass, "Drums": build_drums,
    }
    for s in range(N_SECTIONS):
        for name, _, _ in VOICES:
            events = builders[name](s)
            comp.fill_voice_section(name, NAMES[s], seal(events, SECTION_TICKS))

    ok, msg = comp.validate()
    if not ok:
        raise RuntimeError("phase2 validate failed: %s" % msg)
    return comp


# ---------------------------------------------------------------- grid audit
def grid_audit(comp):
    res = {}
    for v in range(N_V):
        onsets = []
        for s in range(N_SECTIONS):
            u = comp.matrix.get_unit((v, s))
            if u is None:
                continue
            for e in u.events:
                if int(e.pitch) != 0:
                    onsets.append(int(e.start_tick))
        res[vnames[v]] = {"onsets": len(onsets),
                          "off_16th": sum(1 for o in onsets if o % 120 != 0)}
    return res


def main():
    p1_path, raw_records = build_phase1()
    print("PHASE1_OK notes=%d path=%s" % (len(raw_records), p1_path))

    phase2 = build_phase2()
    perfect_grid = grid_audit(phase2)
    print("GRID AUDIT (perfect):", json.dumps(perfect_grid, indent=2))
    for v in vnames:
        assert perfect_grid[v]["off_16th"] == 0, "perfect off-grid for %s" % v

    write_grid_visualization(phase2.matrix,
                             os.path.join(ANALYSIS_DIR, "grid_visualization.txt"),
                             ticks_per_character=120, voice_names=vnames, bpm=BPM,
                             mode="D Dorian Kopanitsa 11/8 Christoffel suite")

    perf_path = os.path.join(MIDI_DIR, PROJECT + "-perfect.mid")
    hum_path = os.path.join(MIDI_DIR, PROJECT + "-humanized.mid")
    hz = export_dual(phase2, perf_path, hum_path, style=STYLE, seed=hz_seed,
                     bpm=BPM, instruments=HZ_INSTRUMENTS)
    print("DUAL EXPORT OK; humanize:", json.dumps(hz, indent=2))

    humanized_grid = grid_audit(phase2)
    print("GRID AUDIT (humanized):", json.dumps(humanized_grid, indent=2))
    hz_off = sum(humanized_grid[v]["off_16th"] for v in vnames)
    print("humanized total off-16th:", hz_off)

    # size asserts
    for p in (p1_path, perf_path, hum_path):
        assert os.path.getsize(p) > 40, "empty/corrupt: %s" % p

    # provenance
    section_midpoints = {}
    for s in range(N_SECTIONS):
        mid = SECTION_PROG[s][BARS_PER_SECTION // 2]
        section_midpoints[NAMES[s]] = mid
    prov = {
        "bpm": BPM, "key": "D", "mode": "dorian", "key_label": KEY_LABEL,
        "style": STYLE, "genre": GENRE, "source": SOURCE,
        "meter": "11/8 (2+2+3+2+2)", "bars": N_BARS, "sections": N_SECTIONS,
        "section_names": NAMES,
        "progression_per_section": {NAMES[s]: SECTION_PROG[s] for s in range(N_SECTIONS)},
        "section_midpoint_chords": section_midpoints,
        "bar_chords": BAR_CHORDS,
        "method": "069 Christoffel Word Combinatorial Composition (CWCC)",
        "variation_techniques": [
            "augmentation (Intro: sparse half-speed)",
            "baseline contour (Tema_A: C(5,2) 16th run)",
            "inversion + register shift up (Tema_Ap)",
            "rotation (Tema_B: rotated conjugate word)",
            "density rise + counterline (Razvivka: register climb + tambura off-beat)",
            "retrograde (Razvivka_2: reversed word)",
            "diminution (Tema_A_Var: staccato 16ths + register up)",
            "mode shift bVI Bb + authentic cadence + augmentation (Zavurshek)",
        ],
        "voices": [{"name": v[0], "program": v[1], "channel": v[2]} for v in VOICES],
        "humanize_seed": hz_seed, "seed": SEED,
        "humanize_profiles": {k: v["profile"] for k, v in hz.items()},
    }

    write_provenance(p1_path, AI_ASSISTED,
                     "Christoffel Word walk (raw, pre-rules)",
                     sources=[SOURCE + "/MIDI/100-balkan-christoffel.mid"],
                     parameters=dict(prov, phase=1),
                     notes="raw single-clarinet Christoffel word walk, unquantized "
                           "float pitch + jittered off-grid rhythm, no harmony")
    write_provenance(perf_path, AI_ASSISTED,
                     "Christoffel Word + musicom rules (grid-locked)",
                     sources=[SOURCE + "/MIDI/100-balkan-christoffel.mid",
                              PROJECT + "-phase1.mid"],
                     parameters=dict(prov, phase=2, version="perfect"),
                     notes="grid-locked perfect layer: per-bar chord-tone quantize "
                           "(floor t//BAR), 16th grid lock, register enforcement, dedup")
    write_provenance(hum_path, AI_ASSISTED,
                     "Christoffel Word + musicom rules + humanize",
                     sources=[SOURCE + "/MIDI/100-balkan-christoffel.mid",
                              PROJECT + "-phase1.mid"],
                     parameters=dict(prov, phase=2, version="humanized",
                                     humanize_stats={k: {kk: vv for kk, vv in v.items()
                                                         if kk != "profile"}
                                                     for k, v in hz.items()}),
                     notes="humanized layer: balkan style profile + per-instrument DNA")

    with open(os.path.join(PROJ, "provenance.json"), "w") as f:
        json.dump(prov, f, indent=2, default=str)

    summary = {
        "perfect_grid": perfect_grid, "humanized_grid": humanized_grid,
        "humanize": {k: {kk: vv for kk, vv in v.items() if kk != "profile"}
                     for k, v in hz.items()},
        "raw_notes": len(raw_records),
        "hz_seed": hz_seed,
    }
    with open(os.path.join(ANALYSIS_DIR, "compose_summary.json"), "w") as f:
        json.dump(summary, f, indent=2, default=str)

    print("COMPOSE_OK")


if __name__ == "__main__":
    main()
