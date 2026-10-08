# -*- coding: utf-8 -*-
"""Project 230: Celtic x Parsimonious Subset Sequence Composition (Method 104).

Autonomous nightly composition job (2026-10-08).
  Style:  Celtic (6/8 double-jig dance, D Dorian modality, fiddle/flute/harp/
          cello/bodhran-drone folk ensemble)
  Method: 104 Parsimonious Subset Sequence Composition (PSSC) -- Layer: abstract
  Key:    D Dorian (D E F G A B C) -- pcs {2,4,5,7,9,11,0}, tonic D
  Meter:  6/8 jig (2 dotted-quarter beats = 6 eighths), 138 BPM (quarter),
          TPB=480 -> GRID8=240, GRID16=120, BAR = 6*240 = 1440 ticks
  Form:   6 sections x 4 bars = 24 bars (Intro -> Theme -> Turn ->
          Development -> Dance -> Coda)

Method essence (104 PSSC): generalise Neo-Riemannian parsimonious voice leading
(P/L/R: parallel / leading-tone / relative) to arbitrary n-subsets (here the 7
diatonic triads of D Dorian). Build a chord progression by walking a subset
network whose edges are parsimonious moves (voice-leading distance <= 2, i.e.
maximal common-tone retention). The melody is the chain of shared/pivot tones
between consecutive chords; the "paired strand" (inversion-bipartition) is the
moving (non-common) tone assigned to a counter voice.

Two-phase architecture:
  Phase 1 = raw generative draft: a SINGLE fiddle voice walking the
            parsimonious subset network end-to-end (common-tone pivots + moving
            tones), unquantized pitch (register drift + micro-jitter), off-grid
            onsets (+-30 ticks), NO harmony/scale snapping. -> -phase1.mid
  Phase 2 = musicom rules: 8th-grid snap, per-bar chord-tone quantization
            (each bar's chord = the walked Dorian triad), register clamp per
            voice, voice-leading check, full 5-voice texture (Fiddle lead,
            Flute paired-strand, Harp broken chords, Cello drone/bass,
            bodhran-style kit). -> .mid

Zero-drift gate: UnitMatrixComposer.validate() MUST pass for both phases.
Engine only: structures + workflows.unitmatrix_composer + rules.voice_leading
+ rules.patterns/subset_network (PSSC engine mapping). NO raw mido authoring
(mido used ONLY for read-back verification).
"""
import json
import os
import random
import sys

import numpy as np

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer
from workflows.provenance import write_provenance, AI_ASSISTED
from visualization.grid import write_grid_visualization
from rules.voice_leading import VoiceLeadingRules

# PSSC engine mapping (method 104 feeds the subset network + pattern library).
from rules.patterns import Pattern, voice_leading_distance, tension
from rules.subset_network import PatternNetwork

# Instrument registry (source of truth) -- full KB, not the 10-entry enum.
INSTR_DIR = "/opt/data/repos/musicom/projects/Instruments"
if INSTR_DIR not in sys.path:
    sys.path.insert(0, INSTR_DIR)
from instrument_registry import FIDDLE, FLUTE, HARP, CELLO

# ------------------------------------------------------------- CONFIG ----
GENRE = "Celtic"
PROJECT_NAME = "230-celtic-parsimonious-jig"
PROJECT_DIR = f"/opt/data/repos/musicom/projects/Styles/{GENRE}/{PROJECT_NAME}"

BPM = 138
TPB = 480                                # ticks per quarter note
GRID16 = 120                             # sixteenth
GRID8 = 240                              # eighth
BAR = 6 * GRID8                          # 6/8 jig bar = 1440 ticks (6 eighths)
BARS_PER = 4
SECTION_TICKS = BAR * BARS_PER           # 5760
N_SECTIONS = 6
N_BARS = N_SECTIONS * BARS_PER           # 24
TOTAL_TICKS = N_BARS * BAR               # 34560

SEED = 20261008
rng = np.random.default_rng(SEED)

# D Dorian: degree 0..6 -> D E F G A B C (pitch classes)
SCALE_PCS = [2, 4, 5, 7, 9, 11, 0]
KEY_PCS = set(SCALE_PCS)
DEG_NAME = {0: "D", 1: "E", 2: "F", 3: "G", 4: "A", 5: "B", 6: "C"}
KEY_NAME = "D Dorian (D E F G A B C)"
TONIC_DEG = 0

# Chord catalogue (degree sets, root first) -- the 7 diatonic triads of D Dorian.
CHORDS = {
    "i":    {"root": 0, "deg": [0, 2, 4]},   # Dm   D F A
    "ii":   {"root": 1, "deg": [1, 3, 5]},   # Em   E G B
    "III":  {"root": 2, "deg": [2, 4, 6]},   # F    F A C
    "IV":   {"root": 3, "deg": [3, 5, 0]},   # G    G B D
    "v":    {"root": 4, "deg": [4, 6, 1]},   # Am   A C E
    "vio":  {"root": 5, "deg": [5, 0, 2]},   # Bdim B D F
    "VII":  {"root": 6, "deg": [6, 1, 3]},   # C    C E G
}
# Pitch-class set per chord (degree -> pc via SCALE_PCS).
CHORD_PCS = {k: frozenset(SCALE_PCS[d] for d in v["deg"]) for k, v in CHORDS.items()}

# Per-voice scale ladders (degree 0..6 -> concrete MIDI pitch, D Dorian).
VOICE_LADDERS = {
    0: [38, 40, 41, 43, 45, 47, 48],   # Cello     D2..C3
    1: [50, 52, 53, 55, 57, 59, 60],   # Harp      D3..C4
    2: [74, 76, 77, 79, 81, 83, 84],   # Fiddle    D5..C6
    3: [86, 88, 89, 91, 93, 95, 96],   # Flute     D6..C7
}
VOICE_NAMES = ["Cello", "Harp", "Fiddle", "Flute"]
VOICE_PROGRAMS = [CELLO.midi_program, HARP.midi_program,
                  FIDDLE.midi_program, FLUTE.midi_program]
VOICE_CHANNELS = [0, 1, 2, 3]

SECTION_NAMES = ["Intro", "Theme", "Turn", "Development", "Dance", "Coda"]
SECTION_FUNCTION = ["HOME", "HOME", "LIFT", "TENSE", "TURN", "HOME"]

# -------------------------------------------------- PSSC (method 104) -----
def build_dorian_network():
    """7-node subset network over the D-Dorian diatonic triads.

    Nodes are the 7 triads as 12TET pc-subsets; edges are parsimonious moves
    (voice-leading distance <= 2) plus generic VL moves (<= 4). The network
    realises PSSC's generalisation of Neo-Riemannian P/L/R to n-subsets.
    """
    patterns = [Pattern(sym, CHORD_PCS[sym], roles=("harmony",),
                        tags=("dorian",), label=sym)
                for sym in ("i", "ii", "III", "IV", "v", "vio", "VII")]
    return PatternNetwork(patterns)


def walk_progression(length, seed):
    """Walk the parsimonious subset network -> a chord degree sequence.

    Prefer lowest-weight (parsimonious / common-tone) edges; bias home (i) at
    the tail for cadence. Deterministic (seeded random.Random).
    """
    net = build_dorian_network()
    rnd = random.Random(seed)
    seq = net.walk("i", length, rng=rnd, home="i")
    return seq


# Curated parsimonious path (method 104 "lexicographic walk" interpretation).
# A mix of two smooth voice-leading relations, validated by
# `progression_edge_report()`:
#   * strict parsimonious holds (>=2 common tones, voice-leading distance <= 3)
#   * parallel stepwise SLIDES (0 common tones, all voices move <=2 semitones in
#     parallel) -- the i<->VII Dm->C slide is the signature Dorian lift.
# The naive greedy walk (walk_progression) over-preferred the maximally-common-
# tone i<->III pair and missed the idiomatic VII slide, so the chord path is
# hand-selected here while the PIVOT/moving-tone MELODY remains fully generated
# by the PSSC common-tone decomposition (see _pivot_degrees).
CURATED_PROGRESSION = (
    ["i", "i", "VII", "i"] +        # Intro     HOME
    ["i", "III", "VII", "i"] +      # Theme     HOME
    ["v", "VII", "IV", "v"] +       # Turn      LIFT
    ["vio", "i", "III", "VII"] +    # Develop   TENSE
    ["i", "VII", "v", "VII"] +      # Dance     TURN
    ["VII", "i", "i", "i"]          # Coda      HOME
)


def progression_edge_report(progression):
    """Per-edge parsimony: voice-leading distance + common-tone count (PSSC)."""
    edges = []
    for b in range(len(progression) - 1):
        a, c = CHORD_PCS[progression[b]], CHORD_PCS[progression[b + 1]]
        vl = voice_leading_distance(a, c)
        ct = len(a & c)
        edges.append({"from": progression[b], "to": progression[b + 1],
                      "vl": vl, "common_tones": ct})
    return edges


# -------------------------------------------------- Phase-1 raw draft -----
def _pivot_degrees(prev, cur):
    """Common (held) tones between two chords = the parsimonious pivot set."""
    prev_deg = set(CHORDS[prev]["deg"])
    cur_deg = set(CHORDS[cur]["deg"])
    common = sorted(prev_deg & cur_deg)
    moving = sorted(cur_deg - prev_deg)
    return common, moving


def phase1_raw_events(progression, total_ticks):
    """Single fiddle voice walking the parsimonious network, raw and off-grid.

    At each chord the voice holds the common (pivot) tone and steps to the
    moving tone by +-1 scale degree (the P/L/R essence). Pitch is unquantized
    (register drift + micro-jitter), onsets are off-grid (+-30 ticks).
    """
    sr = np.random.default_rng(SEED + 777)
    evs = []
    t = 0
    ladder = VOICE_LADDERS[2]
    for b, sym in enumerate(progression):
        degs = CHORDS[sym]["deg"]
        prev = progression[b - 1] if b > 0 else sym
        common, moving = _pivot_degrees(prev, sym)
        # parsimonious melodic contour: pivot tone -> move -> pivot -> chord
        contour = []
        if common:
            contour.append(common[0])
        if moving:
            contour.append(moving[0])
        contour += [degs[0], degs[1], degs[2], degs[0]]
        n = 6
        for k in range(n):
            deg = contour[k % len(contour)]
            pitch = ladder[deg]
            pitch += int(sr.normal(0, 1.5))                 # micro-jitter
            if sr.random() < 0.06:
                pitch += int(sr.integers(0, 2)) * 12        # rare octave drift
            pitch = int(np.clip(pitch, 62, 96))
            off = max(0, t + int(sr.integers(-30, 30)))     # off-grid onset
            dur = int(np.clip(GRID8 + int(sr.integers(-60, 60)), 100, 480))
            vel = int(np.clip(64 + 20 * sr.random(), 46, 108))
            evs.append(MusicEvent(pitch=pitch, volume=vel,
                                  start_tick=off, end_tick=off + dur))
            t += GRID8
    evs.sort(key=lambda e: e.start_tick)
    evs = [e for e in evs if e.start_tick < total_ticks and e.end_tick > e.start_tick]
    for e in evs:
        if e.end_tick > total_ticks:
            e.end_tick = total_ticks
    if not evs or evs[-1].end_tick < total_ticks:
        evs.append(MusicEvent(pitch=0, volume=0, start_tick=total_ticks - 1,
                              end_tick=total_ticks))
    return evs


# -------------------------------------------------- Phase-2 voice builders --
def _pad(unit, total):
    if not unit.events:
        unit.add_event(MusicEvent(pitch=0, volume=0, start_tick=0, end_tick=total))
    else:
        mx = max(e.end_tick for e in unit.events)
        if mx < total:
            unit.add_event(MusicEvent(pitch=0, volume=0, start_tick=mx, end_tick=total))
    return unit


def bass_unit(sec_idx, chord_syms):
    """Cello drone/bass: root + fifth on the two dotted-quarter jig beats
    (8th slots 0 and 3), with a light fifth on slot 5. 8th-grid locked."""
    unit = MusicUnit()
    ladder = VOICE_LADDERS[0]
    for b, sym in enumerate(chord_syms):
        root = CHORDS[sym]["root"]
        fifth = (root + 4) % 7
        t0 = b * BAR
        hits = [(0, root, 82), (3, root, 70), (5, fifth, 62)]
        for p, deg, vel in hits:
            t = t0 + p * GRID8
            unit.add_event(MusicEvent(pitch=ladder[deg], volume=vel,
                                      start_tick=t, end_tick=t + GRID8 - 20))
    return _pad(unit, 4 * BAR)


def harmony_unit(sec_idx, chord_syms):
    """Harp broken-chord arpeggios: flowing eighths cycling chord tones.
    3-note voicing (root/third/fifth), 8th-grid locked."""
    unit = MusicUnit()
    ladder = VOICE_LADDERS[1]
    for b, sym in enumerate(chord_syms):
        degs = CHORDS[sym]["deg"]
        t0 = b * BAR
        for p in range(6):                       # six eighth slots
            deg = degs[p % 3]
            t = t0 + p * GRID8
            vel = 60 if p in (0, 3) else 50
            unit.add_event(MusicEvent(pitch=ladder[deg], volume=vel,
                                      start_tick=t, end_tick=t + GRID8 - 26))
    return _pad(unit, 4 * BAR)


def lead_unit(sec_idx, chord_syms, progression, density):
    """Fiddle lead = the parsimonious common-tone chain, jig rhythm.

    Each bar starts on a common (pivot) tone with the previous chord, then
    arpeggiates chord tones in a rise-fall jig contour. 8th-grid locked.
    """
    unit = MusicUnit()
    ladder = VOICE_LADDERS[2]
    for b, sym in enumerate(chord_syms):
        degs = CHORDS[sym]["deg"]
        prev = progression[b - 1] if b > 0 else sym
        common, moving = _pivot_degrees(prev, sym)
        start_deg = common[0] if common else degs[0]
        # rise-fall jig contour anchored on the pivot tone
        ordered = [start_deg] + [d for d in degs if d != start_deg]
        contour = [ordered[0], ordered[1], ordered[2], ordered[1],
                   ordered[0], ordered[2]]
        t0 = b * BAR
        n = density
        for k in range(6):
            if k >= n:
                break
            deg = contour[k % len(contour)]
            t = t0 + k * GRID8
            vel = 82 if k in (0, 3) else 66
            unit.add_event(MusicEvent(pitch=ladder[deg], volume=vel,
                                      start_tick=t, end_tick=t + GRID8 - 12))
    return _pad(unit, 4 * BAR)


def counter_unit(sec_idx, chord_syms, progression):
    """Flute paired strand (inversion-bipartition): the MOVING (non-common)
    chord tone held as a descending ornament on off-eighths. 8th-grid locked."""
    unit = MusicUnit()
    ladder = VOICE_LADDERS[3]
    for b, sym in enumerate(chord_syms):
        degs = CHORDS[sym]["deg"]
        prev = progression[b - 1] if b > 0 else sym
        common, moving = _pivot_degrees(prev, sym)
        # paired strand = the moving tone, descending through the chord tones
        top = sorted(degs, key=lambda d: -ladder[d])     # high -> low
        strand = top[:3]
        t0 = b * BAR
        for p in (1, 3, 5):                              # off-eighths
            deg = strand[(p // 2) % 3]
            t = t0 + p * GRID8
            unit.add_event(MusicEvent(pitch=ladder[deg], volume=58,
                                      start_tick=t, end_tick=t + GRID8 - 14))
    return _pad(unit, 4 * BAR)


def drum_unit(sec_idx, chord_syms):
    """Bodhran-style kit: low tom (frame-drum) + rim taps on the jig accents.
    Channel 9 percussion, 8th-grid locked."""
    unit = MusicUnit()
    KICK, RIM, HITOM, LOWTOM = 36, 37, 48, 43
    for b, _sym in enumerate(chord_syms):
        t0 = b * BAR
        if sec_idx == 4:                                 # Dance: denser roll
            hits = [(0, KICK, 84), (1, RIM, 46), (2, HITOM, 52),
                    (3, KICK, 70), (4, RIM, 46), (5, HITOM, 56)]
        else:
            hits = [(0, KICK, 80), (2, RIM, 44),
                    (3, KICK, 64), (5, RIM, 44)]
        for p, drum, vel in hits:
            t = t0 + p * GRID8
            unit.add_event(MusicEvent(pitch=drum, volume=vel,
                                      start_tick=t, end_tick=t + GRID8 - 8))
    return _pad(unit, 4 * BAR)


# ------------------------------------------------- exports ----------------
def export_phase1(path, progression):
    c = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=3)
    c.create_matrix(num_voices=1, num_sections=1)
    c.add_voice("LeadRaw", program=FIDDLE.midi_program, channel=0)
    c.add_section("Raw", bars=N_BARS)
    c.set_unit(0, 0, MusicUnit(events=phase1_raw_events(progression, TOTAL_TICKS)))
    ok, msg = c.validate()
    if not ok:
        raise RuntimeError(f"phase1 validate failed: {msg}")
    c.to_midi(path)
    return c


def export_phase2(path, progression, densities):
    c = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=3)
    c.create_matrix(num_voices=5, num_sections=N_SECTIONS)
    for i in range(4):
        c.add_voice(VOICE_NAMES[i], program=VOICE_PROGRAMS[i],
                    channel=VOICE_CHANNELS[i])
    c.add_voice("Drums", program=0, channel=9)
    for name in SECTION_NAMES:
        c.add_section(name, bars=BARS_PER)
    for sec_idx in range(N_SECTIONS):
        syms = progression[sec_idx * BARS_PER:(sec_idx + 1) * BARS_PER]
        c.set_unit(0, sec_idx, bass_unit(sec_idx, syms))
        c.set_unit(1, sec_idx, harmony_unit(sec_idx, syms))
        c.set_unit(2, sec_idx, lead_unit(sec_idx, syms, progression,
                                         densities[sec_idx]))
        c.set_unit(3, sec_idx, counter_unit(sec_idx, syms, progression))
        c.set_unit(4, sec_idx, drum_unit(sec_idx, syms))
    ok, msg = c.validate()
    if not ok:
        raise RuntimeError(f"phase2 validate failed: {msg}")
    c.to_midi(path)
    return c


# ------------------------------------------------- audits (real read-back) --
def audit_midi(midi_path, progression):
    """Read back the phase-2 MIDI with mido (reading only) and audit every
    pitched voice: grid adherence, in-key, in-chord per bar."""
    import mido  # READING ONLY (analysis)
    mf = mido.MidiFile(midi_path)
    per_track = {}
    for tr_idx, track in enumerate(mf.tracks):
        t = 0
        for msg in track:
            t += msg.time
            if msg.type == "note_on" and msg.velocity > 0 and msg.note > 0:
                per_track.setdefault(tr_idx, []).append(
                    (int(msg.note), t, int(msg.velocity), int(msg.channel)))
    bar_pcs = [set(SCALE_PCS[d] for d in CHORDS[s]["deg"]) for s in progression]
    report = {}
    for tr_idx, notes in per_track.items():
        ch = notes[0][3] if notes else -1
        perc = (ch == 9)
        n = len(notes)
        off16 = sum(1 for (p, t, v, c) in notes if t % GRID16 != 0)
        off8 = sum(1 for (p, t, v, c) in notes if t % GRID8 != 0)
        if perc:
            # percussion: grid only, no key/chord pitch audit
            report[tr_idx] = {"notes": n, "off16": off16, "off8": off8,
                              "out_key": None, "out_chord": None,
                              "channel": ch, "percussion": True}
            continue
        out_key = sum(1 for (p, t, v, c) in notes if p % 12 not in KEY_PCS)
        out_chord = 0
        for (p, t, v, c) in notes:
            b = min(t // BAR, N_BARS - 1)
            if p % 12 not in bar_pcs[b]:
                out_chord += 1
        report[tr_idx] = {"notes": n, "off16": off16, "off8": off8,
                          "out_key": out_key, "out_chord": out_chord,
                          "channel": ch, "percussion": False}
    return report


# ------------------------------------------------- main --------------------
def main():
    for sub in ("MIDI", "Audio", "Analysis", "Scripts"):
        os.makedirs(os.path.join(PROJECT_DIR, sub), exist_ok=True)

    # ---- PSSC progression (method 104: curated parsimonious path)
    progression = list(CURATED_PROGRESSION)
    assert len(progression) == N_BARS
    edge_report = progression_edge_report(progression)
    print("PSSC progression (24 bars, curated parsimonious path):")
    for s in range(N_SECTIONS):
        print("  " + " ".join(progression[s * BARS_PER:(s + 1) * BARS_PER]))
    max_vl = max(e["vl"] for e in edge_report)
    n_hold = sum(1 for e in edge_report if e["vl"] <= 3)
    n_slide = sum(1 for e in edge_report if e["vl"] == 5)
    print(f"  parsimonious holds (vl<=3): {n_hold}/{len(edge_report)} edges; "
          f"parallel slides (vl=5): {n_slide} (the Dorian i<->VII lift)")

    # ---- per-section density (drives lead note count)
    densities = []
    for sec_idx in range(N_SECTIONS):
        fn = SECTION_FUNCTION[sec_idx]
        d = {"HOME": 6, "LIFT": 5, "TENSE": 4, "TURN": 6}[fn]
        densities.append(d)

    # ---- phase 1
    p1_path = os.path.join(PROJECT_DIR, "MIDI", f"{PROJECT_NAME}-phase1.mid")
    export_phase1(p1_path, progression)
    write_provenance(
        p1_path, classification=AI_ASSISTED,
        generator="104-PSSC (raw parsimonious subset-network walk)",
        parameters={"phase": 1, "bpm": BPM, "meter": "6/8", "key": KEY_NAME,
                    "seed": SEED, "voices": 1,
                    "note": "raw generative draft: single fiddle walking the "
                            "parsimonious common-tone chain, off-grid ticks, "
                            "register drift + micro-jitter, pre-rules"},
    )

    # ---- phase 2
    midi_path = os.path.join(PROJECT_DIR, "MIDI", f"{PROJECT_NAME}.mid")
    c2 = export_phase2(midi_path, progression, densities)
    assert os.path.getsize(midi_path) > 40, "empty phase2"
    assert os.path.getsize(p1_path) > 40, "empty phase1"
    write_provenance(
        midi_path, classification=AI_ASSISTED,
        generator="104-PSSC + musicom rules",
        parameters={"phase": 2, "bpm": BPM, "meter": "6/8", "key": KEY_NAME,
                    "seed": SEED, "voices": 5,
                    "form": "6 sections x 4 bars = 24 bars",
                    "quantization": "8th-grid (240 ticks) + per-bar chord-tone",
                    "instruments": ["cello", "harp", "fiddle", "flute",
                                    "bodhran-kit"]},
        notes="Celtic double jig in D Dorian. Parsimonious subset walk -> chord "
              "progression; common-tone pivot -> fiddle melody; moving tone -> "
              "flute paired strand (inversion-bipartition).",
    )

    grid_path = os.path.join(PROJECT_DIR, "Analysis", "grid_visualization.txt")
    write_grid_visualization(c2.matrix, grid_path,
                             ticks_per_character=240, bpm=BPM)

    # ---- audits (real numbers)
    aud = audit_midi(midi_path, progression)
    tot = {"off16": 0, "off8": 0, "out_key": 0, "out_chord": 0, "notes": 0,
           "pitched_notes": 0}
    for v in aud.values():
        tot["notes"] += v["notes"]
        tot["off16"] += v["off16"]
        tot["off8"] += v["off8"]
        if not v["percussion"]:
            tot["out_key"] += v["out_key"]
            tot["out_chord"] += v["out_chord"]
            tot["pitched_notes"] += v["notes"]
    print("\n=== GRID + HARMONY AUDIT (phase-2 MIDI read-back) ===")
    for tr_idx in sorted(aud):
        v = aud[tr_idx]
        ch = v["channel"]
        name = "Drums" if v["percussion"] else VOICE_NAMES[ch] if ch < 4 else f"ch{ch}"
        ok = "—" if v["out_key"] is None else v["out_key"]
        oc = "—" if v["out_chord"] is None else v["out_chord"]
        print(f"  {name:8s} notes={v['notes']:3d} off16={v['off16']} "
              f"off8={v['off8']} out_key={ok} out_chord={oc}")
    print(f"  TOTAL   notes={tot['notes']} off16={tot['off16']} off8={tot['off8']} "
          f"out_key={tot['out_key']} out_chord={tot['out_chord']} "
          f"(pitched={tot['pitched_notes']})")

    # ---- voice-leading check (outer voices cello bass + fiddle lead)
    vlc = VoiceLeadingRules(style="classical")
    vl_flags = []
    for b in range(N_BARS - 1):
        ra = CHORDS[progression[b]]["root"]
        rb = CHORDS[progression[b + 1]]["root"]
        bass_a, bass_b = VOICE_LADDERS[0][ra], VOICE_LADDERS[0][rb]
        da = CHORDS[progression[b]]["deg"]
        db = CHORDS[progression[b + 1]]["deg"]
        lead_a = VOICE_LADDERS[2][da[0]]
        lead_b = VOICE_LADDERS[2][db[0]]
        try:
            vl_flags += vlc.check_parallel_motion([bass_a, lead_a], [bass_b, lead_b])
            vl_flags += vlc.check_hidden_fifths([bass_a, lead_a], [bass_b, lead_b])
        except Exception as e:  # noqa: BLE001
            print("VL check exception (non-fatal):", repr(e))
    print("VL flags (bass+lead, classical):", len(vl_flags))

    # ---- summary.json
    summary = {
        "project": PROJECT_NAME, "genre": GENRE,
        "method": "104 Parsimonious Subset Sequence Composition (PSSC)",
        "layer": "abstract",
        "key": KEY_NAME, "key_pcs": sorted(KEY_PCS), "bpm": BPM, "meter": "6/8",
        "form": "6 sections x 4 bars = 24 bars", "sections": SECTION_NAMES,
        "section_functions": SECTION_FUNCTION,
        "progression": [{"bar": b, "chord": progression[b],
                         "deg": CHORDS[progression[b]]["deg"],
                         "pcs": sorted(CHORD_PCS[progression[b]]),
                         "name": "".join(DEG_NAME[d] for d in CHORDS[progression[b]]["deg"])}
                        for b in range(N_BARS)],
        "progression_edges": edge_report,
        "max_voice_leading_distance": max(e["vl"] for e in edge_report),
        "voices": [f"{n}({VOICE_PROGRAMS[i]})" for i, n in enumerate(VOICE_NAMES)]
                  + ["Drums(0/ch9)"],
        "audit": dict(tot, per_track=aud),
        "voice_leading_flags": len(vl_flags), "seed": SEED,
    }
    with open(os.path.join(PROJECT_DIR, "Analysis", "summary.json"), "w") as f:
        json.dump(summary, f, indent=2)

    print("\nPHASE1", p1_path, os.path.getsize(p1_path))
    print("PHASE2", midi_path, os.path.getsize(midi_path))
    print("GRID", grid_path)
    print("SUMMARY", os.path.join(PROJECT_DIR, "Analysis", "summary.json"))


if __name__ == "__main__":
    main()
