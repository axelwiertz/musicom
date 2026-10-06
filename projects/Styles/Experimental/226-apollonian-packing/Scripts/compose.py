# -*- coding: utf-8 -*-
"""Project 226: Experimental x Apollonian Circle Packing Composition (Method 094).

Autonomous nightly composition job (2026-10-06).
  Style:  Experimental (sacred-minimalist fractal counterpoint)
  Method: 094 Apollonian Circle Packing Composition (ACPC) -- Layer: concrete
  Key:    D Dorian (D E F G A B C) -- pc {0,2,4,5,7,9,11}, tonic D
  Tempo:  90 BPM, 4/4, 480 TPB -> BAR = 1920 ticks
  Form:   6 sections x 4 bars = 24 bars (Seed -> Growth -> Branching ->
          Canopy -> Micro -> Coda)

Method essence (094 ACPC): recursive integral Apollonian circle packings under
Descartes' kissing-circle theorem. Root quadruple v0 = (-1,2,2,3) (the -1 is
the enclosing bounding circle). Each Descartes quadruple (k1,k2,k3,k4) of
mutually-tangent curvatures satisfies (k1+k2+k3+k4)^2 = 2*sum ki^2; Vieta gives
the Apollonian reflection k_i' = 2*sum_{j!=i} k_j - k_i, so every child circle
has exact integer curvature. Curvature k -> scale degree (k mod 7); radius
r = 1/k -> fractal note duration (big circle = long, small circle = dense).
Mutually tangent quadruple = 4-voice consonant chord; reflections = parsimonious
single-voice pivots (3 voices hold, 1 moves).

Two-phase architecture:
  Phase 1 = raw generative draft: a SINGLE "born-circle" lead voice walking the
            sequence of new curvatures introduced by the Apollonian reflections
            (unquantized pitch, off-grid ticks, fractal durations, micro-jitter,
            NO harmony/scale snapping).  ->  <project>-phase1.mid
  Phase 2 = musicom rules: 16th-grid snap, per-bar chord-tone quantization to
            the Descartes-quadruple chord, register clamp per voice, voice-
            leading check, full 4-voice texture (Bass/Tenor/Alto/Soprano).
            ->  <project>.mid

Zero-drift gate: UnitMatrixComposer.validate() MUST pass for both phases.
Engine only: structures + workflows.unitmatrix_composer + rules.voice_leading.
NO raw mido authoring (mido used ONLY for read-back verification).
"""
import itertools
import json
import os
import sys

import numpy as np

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer
from workflows.provenance import write_provenance, AI_ASSISTED
from visualization.grid import write_grid_visualization
from rules.voice_leading import VoiceLeadingRules

# Instrument registry (source of truth) -- full KB, not the 10-entry enum.
INSTR_DIR = "/opt/data/repos/musicom/projects/Instruments"
if INSTR_DIR not in sys.path:
    sys.path.insert(0, INSTR_DIR)
from instrument_registry import DOUBLE_BASS, CELLO, VIOLIN, FLUTE

# ------------------------------------------------------------- CONFIG ----
GENRE = "Experimental"
PROJECT_NAME = "226-apollonian-packing"
PROJECT_DIR = f"/opt/data/repos/musicom/projects/Styles/{GENRE}/{PROJECT_NAME}"

BPM = 90
TPB = 480
BEATS = 4
BAR = TPB * BEATS                        # 1920
GRID16 = 120
GRID8 = 240
BARS_PER = 4
SECTION_TICKS = BAR * BARS_PER           # 7680
N_SECTIONS = 6
N_BARS = N_SECTIONS * BARS_PER           # 24
TOTAL_TICKS = N_BARS * BAR               # 46080

SEED = 20261006
rng = np.random.default_rng(SEED)

# D Dorian scale: degree 0..6 -> D E F G A B C (pc)
SCALE_PCS = [2, 4, 5, 7, 9, 11, 0]
KEY_PCS = set(SCALE_PCS)
DEG_NAME = {0: "D", 1: "E", 2: "F", 3: "G", 4: "A", 5: "B", 6: "C"}
KEY_NAME = "D Dorian (D E F G A B C)"
TONIC_DEG = 0

# Per-voice scale ladders (degree 0..6 -> concrete MIDI pitch, D Dorian).
VOICE_LADDERS = {
    0: [38, 40, 41, 43, 45, 47, 48],   # Bass   D2 E2 F2 G2 A2 B2 C3
    1: [50, 52, 53, 55, 57, 59, 60],   # Tenor  D3 E3 F3 G3 A3 B3 C4
    2: [62, 64, 65, 67, 69, 71, 72],   # Alto   D4 E4 F4 G4 A4 B4 C5
    3: [74, 76, 77, 79, 81, 83, 84],   # Soprano D5 E5 F5 G5 A5 B5 C6
}
VOICE_NAMES = ["Bass", "Tenor", "Alto", "Soprano"]
VOICE_PROGRAMS = [DOUBLE_BASS.midi_program, CELLO.midi_program,
                  VIOLIN.midi_program, FLUTE.midi_program]
VOICE_CHANNELS = [0, 1, 2, 3]

SECTION_NAMES = ["Seed", "Growth", "Branching", "Canopy", "Micro", "Coda"]


# ------------------------------------------- Apollonian packing (method 094) ----
def generate_apollonian(root=(-1, 2, 2, 3), max_depth=5):
    """BFS the Apollonian reflection tree. Returns ordered list of
    (quad tuple, depth, born_curvature) where born_curvature is the single
    new circle introduced by the reflection that produced this quadruple
    (None for the root)."""
    visited = {tuple(sorted(root))}
    queue = [(np.array(root, dtype=int), 0, -1, None)]
    out = []
    while queue:
        q, depth, last_axis, born = queue.pop(0)
        out.append((tuple(int(x) for x in q), depth, born))
        if depth < max_depth:
            s = int(np.sum(q))
            for i in range(4):
                if i == last_axis:
                    continue
                nk = 2 * (s - int(q[i])) - int(q[i])
                nq = np.array(q)
                nq[i] = nk
                sk = tuple(sorted(int(x) for x in nq))
                if sk not in visited:
                    visited.add(sk)
                    queue.append((nq, depth + 1, i, nk))
    return out


def build_arc(max_depth=5):
    """Order quads into a 24-bar arc: 20 bars of monotonically rising fractal
    density (sort by depth, then max curvature) then 4 bars returning to the
    spacious root/seed region (coda)."""
    quads = generate_apollonian(root=(-1, 2, 2, 3), max_depth=max_depth)
    # sort by (depth, max curvature) -> increasing density
    ordered = sorted(quads, key=lambda q: (q[1], max(q[0])))
    build = ordered[:20]
    coda = ordered[:4]                    # root + simplest -> resolve
    return build + coda


def quad_degrees(quad):
    """Descartes-quadruple -> sorted set of scale degrees (k<=0 -> tonic 0)."""
    return sorted({(k % 7) if k > 0 else TONIC_DEG for k in quad})


def subdivision(k):
    """Radius r=1/k -> rhythmic subdivision (grid step in ticks). Big circle
    (small k) = long/half-note; small circle (large k) = 16th."""
    if k <= 0:
        return BAR, 1            # pedal: whole bar
    if k <= 5:
        return 2 * GRID8, 2      # half notes
    if k <= 15:
        return TPB, 4            # quarter notes
    if k <= 40:
        return GRID8, 8          # eighths
    return GRID16, 16            # sixteenths


# ------------------------------------------------- Phase-1 raw draft ------
def phase1_raw_events(total_ticks):
    """Single 'born-circle' lead voice walking a DEEP Apollonian curvature
    stream (every positive curvature in BFS order, depth 7). Unquantized pitch
    (register drifts up with depth/log k + micro-jitter), off-grid onsets,
    fractal durations. No scale/chord snapping by design."""
    quads = generate_apollonian(root=(-1, 2, 2, 3), max_depth=7)
    stream = [(k, d) for (q, d, born) in quads for k in q if k > 0]
    evs = []
    t = 0
    sr = np.random.default_rng(SEED + 777)
    for (k, depth) in stream:
        if t >= total_ticks:
            break
        degree = k % 7
        # register drifts up as the packing deepens (the "canopy")
        center = 56 + min(26, int(5 * np.log2(max(1, k)))) + depth * 3
        base = VOICE_LADDERS[3][degree]      # start from soprano ladder pc
        pitch = base
        while pitch > center + 12:
            pitch -= 12
        while pitch < center - 12:
            pitch += 12
        pitch += int(round(sr.normal(0, 1.5)))       # raw micro-jitter
        pitch = int(np.clip(pitch, 48, 96))
        # fractal duration from radius r = 1/k
        dur = max(100, int(BAR / (1.0 + np.log(max(1, k)))))
        dur += int(sr.integers(-50, 50))
        dur = max(90, dur)
        off = t + int(sr.integers(-30, 30))           # off-grid onset
        off = max(0, off)
        vel = int(np.clip(58 + 18 * sr.random() + depth * 4, 46, 112))
        evs.append(MusicEvent(pitch=pitch, volume=vel,
                              start_tick=off, end_tick=off + dur))
        t += max(90, dur // 2 + int(sr.integers(0, 80)))
    evs.sort(key=lambda e: e.start_tick)
    # trim any event overrunning the timeline, then terminal pad
    evs = [e for e in evs if e.start_tick < total_ticks]
    if evs:
        evs = [e for e in evs if e.end_tick > e.start_tick]
        for e in evs:
            if e.end_tick > total_ticks:
                e.end_tick = total_ticks
    if not evs or evs[-1].end_tick < total_ticks:
        evs.append(MusicEvent(pitch=0, volume=0, start_tick=total_ticks - 1,
                              end_tick=total_ticks))
    return evs


# ------------------------------------------------- Phase-2 voice builders ----
def _pad(unit, total):
    if not unit.events:
        unit.add_event(MusicEvent(pitch=0, volume=0, start_tick=0, end_tick=total))
    else:
        mx = max(e.end_tick for e in unit.events)
        if mx < total:
            unit.add_event(MusicEvent(pitch=0, volume=0, start_tick=mx, end_tick=total))
    return unit


def build_voice_unit(voice_idx, section_quads, sec_idx):
    """One voice's cell for a 4-bar section. Each bar = one Descartes quadruple.
    The voice holds its circle's chord tone on strong slots and exchanges into
    neighbour chord tones on weak slots (all within the bar's chord), at a
    radius-derived subdivision. Every onset is grid-locked."""
    total = 4 * BAR
    unit = MusicUnit()
    ladder = VOICE_LADDERS[voice_idx]
    for b, (quad, depth, born) in enumerate(section_quads):
        k = quad[voice_idx]
        degs = quad_degrees(quad)
        own_deg = (k % 7) if k > 0 else TONIC_DEG
        grid, n_slots = subdivision(k)
        t0 = b * BAR
        if n_slots == 1:
            # pedal: sustained whole-bar tone (the bounding/root circle)
            p = ladder[own_deg]
            unit.add_event(MusicEvent(pitch=p, volume=74,
                                      start_tick=t0, end_tick=t0 + BAR - 30))
            continue
        gap = max(24, grid // 4)
        for s in range(n_slots):
            if s % 2 == 0:
                dg = own_deg
            else:
                dg = degs[(s // 2 + voice_idx + b) % len(degs)]
            p = ladder[dg]
            t = t0 + s * grid
            # accent downbeats + subdivision head
            vel = 66 + (10 if s == 0 else 0) + (6 if s % 2 == 0 else 0)
            if voice_idx == 0:
                vel += 6
            if voice_idx == 3:
                vel -= 4
            vel = int(np.clip(vel, 48, 108))
            unit.add_event(MusicEvent(pitch=p, volume=vel,
                                      start_tick=t, end_tick=t + grid - gap))
    return _pad(unit, total)


# ------------------------------------------------- exports -----------------
def export_phase1(path, arc):
    c = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
    c.create_matrix(num_voices=1, num_sections=1)
    c.add_voice("LeadRaw", program=FLUTE.midi_program, channel=0)
    c.add_section("Raw", bars=N_BARS)
    evs = phase1_raw_events(TOTAL_TICKS)
    c.set_unit(0, 0, MusicUnit(events=evs))
    ok, msg = c.validate()
    if not ok:
        raise RuntimeError(f"phase1 validate failed: {msg}")
    c.to_midi(path)
    return c


def export_phase2(path, arc):
    c = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
    c.create_matrix(num_voices=4, num_sections=N_SECTIONS)
    for i in range(4):
        c.add_voice(VOICE_NAMES[i], program=VOICE_PROGRAMS[i],
                    channel=VOICE_CHANNELS[i])
    for name in SECTION_NAMES:
        c.add_section(name, bars=BARS_PER)
    for sec_idx in range(N_SECTIONS):
        quads = arc[sec_idx * BARS_PER:(sec_idx + 1) * BARS_PER]
        for v in range(4):
            c.set_unit(v, sec_idx, build_voice_unit(v, quads, sec_idx))
    ok, msg = c.validate()
    if not ok:
        raise RuntimeError(f"phase2 validate failed: {msg}")
    c.to_midi(path)
    return c


# ------------------------------------------------- audits (real read-back) --
def audit_midi(midi_path, arc):
    """Read back the phase-2 MIDI with mido (reading is allowed) and audit
    every pitched voice: grid adherence, in-key, in-chord per bar."""
    import mido  # READING ONLY (analysis) — mido used to verify, never to author
    mf = mido.MidiFile(midi_path)
    per_track = {}
    for tr_idx, track in enumerate(mf.tracks):
        t = 0
        for msg in track:
            t += msg.time
            if msg.type == "note_on" and msg.velocity > 0 and msg.note > 0:
                per_track.setdefault(tr_idx, []).append(
                    (int(msg.note), t, int(msg.velocity)))
    # chord-degree -> pc set per bar
    bar_deg = [quad_degrees(q[0]) for q in arc]      # arc item = (quad, depth, born)
    bar_pcs = [set(SCALE_PCS[d] for d in dg) for dg in bar_deg]
    report = {}
    for tr_idx, notes in per_track.items():
        n = len(notes)
        off16 = sum(1 for (p, t, v) in notes if t % GRID16 != 0)
        off8 = sum(1 for (p, t, v) in notes if t % GRID8 != 0)
        out_key = sum(1 for (p, t, v) in notes if p % 12 not in KEY_PCS)
        out_chord = 0
        for (p, t, v) in notes:
            b = min(t // BAR, N_BARS - 1)
            if p % 12 not in bar_pcs[b]:
                out_chord += 1
        report[tr_idx] = {"notes": n, "off16": off16, "off8": off8,
                          "out_key": out_key, "out_chord": out_chord}
    return report


# ------------------------------------------------- main ---------------------
def main():
    for sub in ("MIDI", "Audio", "Analysis", "Scripts"):
        os.makedirs(os.path.join(PROJECT_DIR, sub), exist_ok=True)

    arc = build_arc(max_depth=5)
    assert len(arc) == N_BARS, len(arc)
    bar_deg = [quad_degrees(q[0]) for q in arc]
    print("Key:", KEY_NAME, "KEY_PCS:", sorted(KEY_PCS))
    print("Arc (24 bars): depth / quad / chord-degrees:")
    for b, (quad, depth, born) in enumerate(arc):
        dg = quad_degrees(quad)
        names = "".join(DEG_NAME[d] for d in dg)
        print(f"  bar {b:2d} {SECTION_NAMES[b//4]:>9} d={depth} "
              f"{str(quad):>20} -> [{names}]  born={born}")

    # ---- phase 1
    p1_path = os.path.join(PROJECT_DIR, "MIDI", f"{PROJECT_NAME}-phase1.mid")
    export_phase1(p1_path, arc)
    write_provenance(
        p1_path, classification=AI_ASSISTED,
        generator="094-Apollonian-Circle-Packing (raw curvature-stream walk)",
        parameters={"phase": 1, "bpm": BPM, "key": KEY_NAME, "seed": SEED,
                    "voices": 1,
                    "note": "raw generative draft: single lead voice walking a deep "
                            "Apollonian curvature stream (every positive curvature, "
                            "depth 7), off-grid ticks, fractal radii durations, "
                            "register drift + micro-jitter, pre-rules"},
    )

    # ---- phase 2
    midi_path = os.path.join(PROJECT_DIR, "MIDI", f"{PROJECT_NAME}.mid")
    c2 = export_phase2(midi_path, arc)
    assert os.path.getsize(midi_path) > 40, "empty phase2"
    assert os.path.getsize(p1_path) > 40, "empty phase1"
    write_provenance(
        midi_path, classification=AI_ASSISTED,
        generator="094-Apollonian-Circle-Packing + musicom rules",
        parameters={"phase": 2, "bpm": BPM, "key": KEY_NAME, "seed": SEED,
                    "voices": 4, "form": "6 sections x 4 bars = 24 bars",
                    "quantization": "16th-grid (120 ticks) + per-bar Descartes-quadruple chord-tone",
                    "instruments": ["double bass", "cello", "violin", "flute"]},
        notes="Experimental sacred-minimal fractal counterpoint in D Dorian. "
              "Descartes quadruples -> 4-voice chords; Apollonian reflections "
              "-> parsimonious single-voice pivots; radii -> fractal durations.",
    )

    grid_path = os.path.join(PROJECT_DIR, "Analysis", "grid_visualization.txt")
    write_grid_visualization(c2.matrix, grid_path, ticks_per_character=240, bpm=BPM)

    # ---- audits (real numbers)
    aud = audit_midi(midi_path, arc)
    tot_off16 = sum(v["off16"] for v in aud.values())
    tot_off8 = sum(v["off8"] for v in aud.values())
    tot_outkey = sum(v["out_key"] for v in aud.values())
    tot_outchord = sum(v["out_chord"] for v in aud.values())
    tot_notes = sum(v["notes"] for v in aud.values())
    print("\n=== GRID + HARMONY AUDIT (phase-2 MIDI read-back) ===")
    for tr_idx in sorted(aud):
        v = aud[tr_idx]
        print(f"  track{tr_idx} notes={v['notes']:3d} off16={v['off16']} "
              f"off8={v['off8']} out_key={v['out_key']} out_chord={v['out_chord']}")
    print(f"  TOTAL notes={tot_notes} off16={tot_off16} off8={tot_off8} "
          f"out_key={tot_outkey} out_chord={tot_outchord}")

    # ---- voice-leading check (outer voices bass + soprano)
    vlc = VoiceLeadingRules(style="classical")
    vl_flags = []
    for b in range(N_BARS - 1):
        quad_a, quad_b = arc[b][0], arc[b + 1][0]
        bass_a = VOICE_LADDERS[0][(quad_a[0] % 7) if quad_a[0] > 0 else 0]
        bass_b = VOICE_LADDERS[0][(quad_b[0] % 7) if quad_b[0] > 0 else 0]
        sop_a = VOICE_LADDERS[3][(quad_a[3] % 7) if quad_a[3] > 0 else 0]
        sop_b = VOICE_LADDERS[3][(quad_b[3] % 7) if quad_b[3] > 0 else 0]
        try:
            if vlc.check_parallel_motion([int(bass_a), int(sop_a)],
                                         [int(bass_b), int(sop_b)]):
                vl_flags.append((b, "parallel"))
            if vlc.check_hidden_fifths([int(bass_a), int(sop_a)],
                                       [int(bass_b), int(sop_b)]):
                vl_flags.append((b, "hidden"))
        except Exception as e:  # noqa: BLE001
            print("VL check exception (non-fatal):", repr(e))
    print("VL flags (bass+soprano, classical):", len(vl_flags))

    # ---- summary.json
    summary = {
        "project": PROJECT_NAME,
        "genre": GENRE,
        "method": "094 Apollonian Circle Packing Composition (ACPC)",
        "layer": "concrete",
        "key": KEY_NAME,
        "key_pcs": sorted(KEY_PCS),
        "bpm": BPM,
        "form": "6 sections x 4 bars = 24 bars",
        "sections": SECTION_NAMES,
        "progression": [{"bar": b, "quad": list(arc[b][0]),
                         "depth": arc[b][1],
                         "chord": "".join(DEG_NAME[d] for d in bar_deg[b]),
                         "born": arc[b][2]}
                        for b in range(N_BARS)],
        "voices": [f"{n}({VOICE_PROGRAMS[i]})" for i, n in enumerate(VOICE_NAMES)],
        "audit": {"total_notes": tot_notes, "off16": tot_off16,
                  "off8": tot_off8, "out_key": tot_outkey,
                  "out_chord": tot_outchord, "per_track": aud},
        "voice_leading_flags": len(vl_flags),
        "seed": SEED,
    }
    with open(os.path.join(PROJECT_DIR, "Analysis", "summary.json"), "w") as f:
        json.dump(summary, f, indent=2)

    print("\nPHASE1", p1_path, os.path.getsize(p1_path))
    print("PHASE2", midi_path, os.path.getsize(midi_path))
    print("GRID", grid_path)
    print("SUMMARY", os.path.join(PROJECT_DIR, "Analysis", "summary.json"))


if __name__ == "__main__":
    main()
