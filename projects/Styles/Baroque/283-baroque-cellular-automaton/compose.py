# -*- coding: utf-8 -*-
"""283-baroque-cellular-automaton -- nightly composition 2026-11-03.

Method 021 Cellular Automata Grid Evolution (concrete, Rules-Based, Grid-Locked):
a 1D elementary cellular automaton (Rule 30) drives melodic contour, note
density, and continuo figuration. Phase 2 applies musicom rules: per-bar chord
tone quantization (tiered strong/weak via classify_weight), 8th-note grid snap,
register/range enforcement, and a full Baroque texture (ground bass + continuo
realization + imitative counterpoint + sustained inner pedal).

Form: aba (da capo ternary) -- A1 (8) B (8) A2 (8) = 24 bars, 4/4, D minor
(harmonic/melodic minor mixture: b7 AND leading tone in the declared key).
"""

import os
import json
import importlib.util

import numpy as np

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer
from workflows.provenance import write_provenance, AI_ASSISTED
from workflows.humanize import export_dual
from visualization.grid import write_grid_visualization
from sound.synthesis.scale_quantizer import STRONG_GRID, classify_weight

# ---------------------------------------------------------------- registry
_reg_path = "/opt/data/repos/musicom/projects/Instruments/instrument_registry.py"
_reg_spec = importlib.util.spec_from_file_location("instrument_registry", _reg_path)
_reg = importlib.util.module_from_spec(_reg_spec)
_reg_spec.loader.exec_module(_reg)
VIOLIN = _reg.VIOLIN
OBOE = _reg.OBOE
HARPSICHORD = _reg.HARPSICHORD
VIOLA = _reg.VIOLA
CELLO = _reg.CELLO
DOUBLE_BASS = _reg.DOUBLE_BASS

PROJ = "/opt/data/projects/Styles/Baroque/283-baroque-cellular-automaton"
MIDI_DIR = os.path.join(PROJ, "MIDI")
AUDIO_DIR = os.path.join(PROJ, "Audio")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")
for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
    os.makedirs(d, exist_ok=True)

SEED = 20261103
GEN = "021 Cellular Automata Grid Evolution (CAGE) + musicom rules"

# ---------------------------------------------------------------- metric
TPB = 480
GRID8 = 240                        # eighth note
GRID16 = 120                       # sixteenth (grid audit granularity)
BAR_TICKS = TPB * 4                # 1920
BPM = 96
STRONG_GRID_44 = STRONG_GRID.get("4/4", (0, 960))

BARS_PER_SECTION = 8
SECTIONS = ["A1", "B", "A2"]       # aba (da capo ternary)
N_SECTIONS = len(SECTIONS)
N_BARS = N_SECTIONS * BARS_PER_SECTION   # 24
SECTION_TICKS = BAR_TICKS * BARS_PER_SECTION   # 15360
TOTAL_TICKS = SECTION_TICKS * N_SECTIONS      # 46080
SLOTS_PER_BAR = 8
TOTAL_SLOTS = N_BARS * SLOTS_PER_BAR         # 192

STYLE = "baroque-classical"        # drives humanize profile + LUFS target

# ---------------------------------------------------------------- harmony
# D minor harmonic/melodic-minor mixture: D E F G A Bb C C#
KEY_PCS = {0, 1, 2, 4, 5, 7, 9, 10}

CHORD_PLAN = {
    "A1": ["Dm", "C", "Bb", "A", "Dm", "Gm", "A", "Dm"],
    "B":  ["F", "C", "Dm", "A", "Bb", "Gm", "A", "Dm"],
    "A2": ["Dm", "C", "Bb", "A", "Dm", "Gm", "A", "Dm"],
}

CHORD_PCS = {
    "Dm": {2, 5, 9}, "C": {0, 4, 7}, "Bb": {10, 2, 5},
    "A": {9, 1, 4}, "Gm": {7, 10, 2}, "F": {5, 9, 0},
}
CHORD_ROOT = {"Dm": 2, "C": 0, "Bb": 10, "A": 9, "Gm": 7, "F": 5}
ROOT_FIFTH = {"Dm": (2, 9), "C": (0, 7), "Bb": (10, 5), "A": (9, 4),
              "Gm": (7, 2), "F": (5, 0)}


def chord_for_bar(bar_global):
    sec = SECTIONS[bar_global // BARS_PER_SECTION]
    return CHORD_PLAN[sec][bar_global % BARS_PER_SECTION]


def chord_pcs_for_bar(bar_global):
    return CHORD_PCS[chord_for_bar(bar_global)]


# ---------------------------------------------------------------- helpers
def nearest_pc_tone(target, pcs, low, high):
    best_p, best_d = None, 999
    for p in range(low, high + 1):
        if (p % 12) in pcs:
            d = abs(p - target)
            if d < best_d:
                best_d, best_p = d, p
    return best_p if best_p is not None else target


def pc_to_midi(pc, low, high):
    return nearest_pc_tone(low + 6, {pc}, low, high)


def snap_grid(tick, grid=GRID8):
    return int(round(tick / float(grid))) * grid


def dedup_keep_longest(events):
    best = {}
    for e in events:
        if e.pitch == 0:
            continue
        key = (int(e.start_tick), int(e.pitch))
        if key not in best or e.end_tick > best[key].end_tick:
            best[key] = e
    return sorted(best.values(), key=lambda e: (e.start_tick, e.pitch))


def finish_section(events):
    out = []
    for e in events:
        st = min(snap_grid(e.start_tick), SECTION_TICKS - 1)
        en = min(snap_grid(e.end_tick), SECTION_TICKS)
        if en <= st:
            en = min(st + GRID8, SECTION_TICKS)
        out.append(MusicEvent(pitch=int(e.pitch), volume=int(e.volume),
                              start_tick=st, end_tick=en))
    out = dedup_keep_longest(out)
    out.append(MusicEvent(pitch=0, volume=0,
                          start_tick=SECTION_TICKS - 10, end_tick=SECTION_TICKS))
    return out


# ---------------------------------------------------------------- CA (Rule 30)
def ca_rule30(row):
    W = len(row)
    out = [0] * W
    alive_set = {(1, 0, 0), (0, 1, 1), (0, 1, 0), (0, 0, 1)}
    for i in range(W):
        l, c, r = row[(i - 1) % W], row[i], row[(i + 1) % W]
        out[i] = 1 if (l, c, r) in alive_set else 0
    return out


def evolve_ca(seed, W, steps):
    rng = np.random.default_rng(seed)
    row = [1 if rng.random() < 0.5 else 0 for _ in range(W)]
    grid = [row]
    for _ in range(steps - 1):
        row = ca_rule30(row)
        grid.append(row)
    return grid


CA_W = 24
CA_GRID = evolve_ca(SEED, CA_W, TOTAL_SLOTS)


# ================================================================== PHASE 1
def build_phase1():
    """Raw CA walk, unquantized pitch + rhythm, single violin voice."""
    composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=4)
    composer.create_matrix(num_voices=1, num_sections=N_SECTIONS)
    composer.add_voice("Raw_Violin", program=VIOLIN.midi_program, channel=0)

    rng = np.random.default_rng(SEED + 7)
    for s_idx, s_name in enumerate(SECTIONS):
        composer.add_section(s_name, bars=BARS_PER_SECTION)
        events = []
        cursor = 12
        pitch = 69.0
        for slot in range(BARS_PER_SECTION * SLOTS_PER_BAR):
            row = CA_GRID[s_idx * (BARS_PER_SECTION * SLOTS_PER_BAR) + slot]
            if row[cursor] == 1:
                pitch += 2.0 + rng.uniform(-0.4, 0.4)
            else:
                pitch -= 1.5 + rng.uniform(-0.3, 0.3)
            pitch = float(np.clip(pitch, 60, 88))
            dur = int(rng.uniform(150, 300))
            st = slot * GRID8 + int(rng.uniform(-60, 60))
            st = max(0, st)
            if st + dur > SECTION_TICKS - 10:
                dur = SECTION_TICKS - 10 - st
            if dur <= 0:
                continue
            events.append(MusicEvent(pitch=int(round(pitch)),
                                     volume=int(rng.uniform(70, 100)),
                                     start_tick=st, end_tick=st + dur))
            if rng.random() < 0.10:
                cursor = (cursor + 1) % CA_W
        if not events or events[-1].end_tick < SECTION_TICKS:
            events.append(MusicEvent(pitch=0, volume=0,
                                     start_tick=SECTION_TICKS - 10,
                                     end_tick=SECTION_TICKS))
        composer.fill_voice_section("Raw_Violin", s_name, MusicUnit(events=events))

    ok, msg = composer.validate()
    if not ok:
        raise RuntimeError(f"Phase 1 validate failed: {msg}")
    p1 = os.path.join(MIDI_DIR, "283-baroque-cellular-automaton-phase1.mid")
    composer.to_midi(p1)
    write_provenance(
        p1, AI_ASSISTED, GEN,
        notes="Raw unquantized Rule-30 CA walk, single violin voice "
              "(pre-rules generative draft)",
        parameters={"phase": 1, "seed": SEED, "ticks": TOTAL_TICKS,
                    "ca_rule": "Rule30", "ca_width": CA_W})
    return p1


# ================================================================== PHASE 2
def tiered_snap(raw, onset_tick, chord_pcs, low, high):
    """Weight-aware snap (mirrors tiered_quantize, with the declared harmonic-
    minor key set that the fixed 'minor' ScaleQuantizer mode does not carry)."""
    w = classify_weight(onset_tick, STRONG_GRID_44, bar_ticks=BAR_TICKS)
    if w == "strong":
        return nearest_pc_tone(raw, chord_pcs, low, high)
    return nearest_pc_tone(raw, KEY_PCS, low, high)


def build_lead_section(s_idx):
    """Violin: flowing 8th-note line, CA-driven contour, tiered snap."""
    events = []
    pitch = 74
    cursor = 12
    for bar in range(BARS_PER_SECTION):
        bar_global = s_idx * BARS_PER_SECTION + bar
        bar_start = bar * BAR_TICKS
        chord_pcs = chord_pcs_for_bar(bar_global)
        for k in range(SLOTS_PER_BAR):
            slot = bar_global * SLOTS_PER_BAR + k
            row = CA_GRID[slot]
            st = bar_start + k * GRID8
            pitch += 2 if row[cursor] == 1 else -2
            pitch = max(62, min(86, pitch))
            q = tiered_snap(pitch, st, chord_pcs, 62, 86)
            pitch = q
            w = classify_weight(st, STRONG_GRID_44, bar_ticks=BAR_TICKS)
            events.append(MusicEvent(pitch=q, volume=96 if w == "strong" else 82,
                                     start_tick=st, end_tick=st + GRID8))
            if (slot % 7) == 0:
                cursor = (cursor + 1) % CA_W
    return events


def build_counter_section(s_idx):
    """Oboe: imitative countermelody (inverted CA contour), quarter/half notes."""
    events = []
    pitch = 69
    cursor = 18
    for bar in range(BARS_PER_SECTION):
        bar_global = s_idx * BARS_PER_SECTION + bar
        bar_start = bar * BAR_TICKS
        chord_pcs = chord_pcs_for_bar(bar_global)
        for k in (0, 2, 4, 6):
            slot = bar_global * SLOTS_PER_BAR + k
            row = CA_GRID[slot]
            st = bar_start + k * GRID8
            pitch += -2 if row[cursor] == 1 else 2   # inverted (echo)
            pitch = max(60, min(81, pitch))
            q = tiered_snap(pitch, st, chord_pcs, 60, 81)
            pitch = q
            dur = GRID8 * 2 if k in (0, 4) else GRID8
            events.append(MusicEvent(pitch=q, volume=88,
                                     start_tick=st, end_tick=st + dur))
    return events


def build_continuo_section(s_idx):
    """Harpsichord: block chord on beat 1 + CA-density-gated 8th arpeggio."""
    events = []
    order = [0, 2, 1, 2]   # root, fifth, third, fifth broken-chord cycle
    for bar in range(BARS_PER_SECTION):
        bar_global = s_idx * BARS_PER_SECTION + bar
        bar_start = bar * BAR_TICKS
        chord_pcs = sorted(CHORD_PCS[chord_for_bar(bar_global)])
        triad = [nearest_pc_tone(60, {pc}, 55, 72) for pc in chord_pcs]
        for tn in triad:
            events.append(MusicEvent(pitch=tn, volume=80,
                                     start_tick=bar_start,
                                     end_tick=bar_start + GRID8))
        for k in range(1, SLOTS_PER_BAR):
            slot = bar_global * SLOTS_PER_BAR + k
            row = CA_GRID[slot]
            density = sum(row)
            if density < 6 and k % 2 == 1:
                continue   # CA-sparse bars -> sparser figuration
            st = bar_start + k * GRID8
            tn = triad[order[k % 4]]
            events.append(MusicEvent(pitch=tn, volume=78,
                                     start_tick=st, end_tick=st + GRID8))
    return events


def build_inner_section(s_idx):
    """Viola: sustained chord tone (whole note), smooth voice leading."""
    events = []
    prev = 62
    for bar in range(BARS_PER_SECTION):
        bar_global = s_idx * BARS_PER_SECTION + bar
        bar_start = bar * BAR_TICKS
        chord_pcs = CHORD_PCS[chord_for_bar(bar_global)]
        target = nearest_pc_tone(prev, chord_pcs, 57, 69)
        events.append(MusicEvent(pitch=target, volume=74,
                                 start_tick=bar_start,
                                 end_tick=bar_start + BAR_TICKS))
        prev = target
    return events


def build_bass_section(s_idx):
    """Cello: ground bass, root/fifth quarter notes (Baroque dance lock)."""
    events = []
    for bar in range(BARS_PER_SECTION):
        bar_global = s_idx * BARS_PER_SECTION + bar
        bar_start = bar * BAR_TICKS
        root_pc, fifth_pc = ROOT_FIFTH[chord_for_bar(bar_global)]
        root = pc_to_midi(root_pc, 40, 52)
        fifth = pc_to_midi(fifth_pc, 40, 55)
        hits = [(0, root, 105), (480, fifth, 90), (960, root, 102), (1440, fifth, 88)]
        for off, p, vel in hits:
            st = bar_start + off
            events.append(MusicEvent(pitch=p, volume=vel,
                                     start_tick=st, end_tick=st + GRID8 * 2))
    return events


def build_phase2():
    """Rules-processed 5-voice Baroque texture, grid-locked (the 'perfect' layer)."""
    composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=4)
    composer.create_matrix(num_voices=5, num_sections=N_SECTIONS)

    composer.add_voice("Violin", program=VIOLIN.midi_program, channel=0)
    composer.add_voice("Oboe", program=OBOE.midi_program, channel=1)
    composer.add_voice("Harpsichord", program=HARPSICHORD.midi_program, channel=2)
    composer.add_voice("Viola", program=VIOLA.midi_program, channel=3)
    composer.add_voice("Cello", program=CELLO.midi_program, channel=4)

    builders = {
        "Violin": build_lead_section,
        "Oboe": build_counter_section,
        "Harpsichord": build_continuo_section,
        "Viola": build_inner_section,
        "Cello": build_bass_section,
    }

    for s_idx, s_name in enumerate(SECTIONS):
        composer.add_section(s_name, bars=BARS_PER_SECTION)
        for vname, builder in builders.items():
            raw = builder(s_idx)
            cell = finish_section(raw)
            composer.fill_voice_section(vname, s_name, MusicUnit(events=cell))

    ok, msg = composer.validate()
    if not ok:
        raise RuntimeError(f"Phase 2 (perfect) validate failed: {msg}")

    perfect = os.path.join(MIDI_DIR, "283-baroque-cellular-automaton-perfect.mid")
    humanized = os.path.join(MIDI_DIR, "283-baroque-cellular-automaton-humanized.mid")

    hz_instruments = {
        "Violin": VIOLIN.humanize_dna,
        "Oboe": OBOE.humanize_dna,
        "Harpsichord": HARPSICHORD.humanize_dna,
        "Viola": VIOLA.humanize_dna,
        "Cello": DOUBLE_BASS.humanize_dna,   # bass layback (8 ms) override
    }
    hz = export_dual(composer, perfect, humanized, style=STYLE, seed=SEED,
                     bpm=BPM, instruments=hz_instruments)

    write_provenance(perfect, AI_ASSISTED, GEN,
                     notes="Grid-locked rules-processed layer (no humanization)",
                     parameters={"phase": 2, "version": "perfect", "seed": SEED,
                                 "key": "D minor (harmonic/melodic mixture)",
                                 "bpm": BPM, "style": "baroque", "form": "aba",
                                 "time_signature": "4/4", "bars": N_BARS,
                                 "ticks": TOTAL_TICKS})
    write_provenance(humanized, AI_ASSISTED, GEN,
                     notes="Humanized (style baroque-classical, per-instrument DNA)",
                     parameters={"phase": 2, "version": "humanized", "seed": SEED,
                                 "key": "D minor (harmonic/melodic mixture)",
                                 "bpm": BPM, "style": "baroque",
                                 "humanize_seed": SEED, "humanize_profiles": hz})

    write_grid_visualization(composer.matrix,
                             os.path.join(ANALYSIS_DIR, "grid_visualization.txt"))
    return perfect, humanized, hz, composer


if __name__ == "__main__":
    p1 = build_phase1()
    print(f"phase1:   {p1} ({os.path.getsize(p1)} bytes)")
    perfect, humanized, hz, composer = build_phase2()
    print(f"perfect:  {perfect} ({os.path.getsize(perfect)} bytes)")
    print(f"humanized:{humanized} ({os.path.getsize(humanized)} bytes)")
    print("humanize summary:")
    print(json.dumps(hz, indent=2, default=str))
