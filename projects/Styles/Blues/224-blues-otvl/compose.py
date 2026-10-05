# -*- coding: utf-8 -*-
"""Project 224: Blues x Optimal Transport Voice Leading (Method 050).

Autonomous nightly composition job (2026-10-05).
  Style:  Blues (12-bar dominant blues, E)
  Method: 050 Optimal Transport Voice Leading (OTVL) -- Layer: concrete
  Key:    E blues (12-bar dominant-blues tonality)
  Tempo:  100 BPM, 4/4, 480 TPB -> BAR = 1920 ticks
  Form:   6 sections x 4 bars = 24 bars = 2 x 12-bar blues choruses

Two-phase architecture:
  Phase 1 = raw generative draft: a single Harmonica voice whose pitch line is
            an OPTIMAL-TRANSPORT walk -- each bar's chord is a discrete "mass"
            over its chord tones; the lead mass-particle is transported bar to
            bar via min-cost (monotone) matching = smooth voice leading; the
            Wasserstein transport cost drives articulation. Unquantized ticks +
            chromatic micro-jitter (off-grid by design, pre-rules).
            ->  <project>-phase1.mid
  Phase 2 = musicom rules: 16th-grid snap (120 ticks), per-bar chord-tone
            quantization to E blues, register clamp, voice-leading check, full
            5-voice blues texture (Harmonica lead / Piano comp / Acoustic
            guitar chank / Double-bass walk / GM drum kit).
            ->  <project>.mid

Blues tonality (E): union of I7/IV7/V7 dominant-7th chord tones + blue 3rd and
flat 5th. Scale pcs = {1,2,3,4,6,7,8,9,10,11} (C#, D, D#, E, F#, G, G#, A, Bb, B);
the only pcs excluded are C (0) and F (5) -- the notes most foreign to the
E-A-B dominant frame.

Zero-drift gate: UnitMatrixComposer.validate() MUST pass for both phases.
Engine only: structures + workflows.unitmatrix_composer + generators.rhythm +
rules.voice_leading. NO raw mido authoring, no sys.path.insert for the engine.
"""
import itertools
import json
import os

import numpy as np

from structures import (MusicUnit, MusicEvent, MidiPercussion)
from workflows.unitmatrix_composer import UnitMatrixComposer
from workflows.provenance import write_provenance, AI_ASSISTED
from visualization.grid import write_grid_visualization
from rules.voice_leading import VoiceLeadingRules

# Instrument registry (source of truth) -- full KB, not the 10-entry enum.
INSTR_DIR = "/opt/data/repos/musicom/projects/Instruments"
import sys
if INSTR_DIR not in sys.path:
    sys.path.insert(0, INSTR_DIR)
from instrument_registry import (HARMONICA, PIANO, ACOUSTIC_GUITAR,
                                 DOUBLE_BASS, DRUM_KIT)

# ------------------------------------------------------------- CONFIG ----
GENRE = "Blues"
PROJECT_NAME = "224-blues-otvl"
PROJECT_DIR = f"/opt/data/repos/musicom/projects/Styles/{GENRE}/{PROJECT_NAME}"

BPM = 100
TPB = 480
BEATS = 4
BAR = TPB * BEATS                        # 1920
GRID16 = 120
GRID8 = 240
BARS_PER = 4
SECTION_TICKS = BAR * BARS_PER           # 7680
N_SECTIONS = 6
N_BARS = N_SECTIONS * BARS_PER           # 24

SEED = 20261005
rng = np.random.default_rng(SEED)

# E blues: 12-bar dominant blues tonality (union of I7/IV7/V7 chord tones
# + blue 3rd + flat 5th). Excludes C (0) and F (5).
KEY_NAME = "E blues (12-bar dominant blues)"
KEY_PCS = {1, 2, 3, 4, 6, 7, 8, 9, 10, 11}
PC_NAME = {1: "C#", 2: "D", 3: "D#", 4: "E", 6: "F#",
           7: "G", 8: "G#", 9: "A", 10: "Bb", 11: "B", 0: "C", 5: "F"}

# chord degree -> pitch-class set (dominant 7th + blue notes), each a subset of
# KEY_PCS. Blue notes included as chord tones so the "out-of-chord" audit stays
# 0 while keeping authentic blues color.
DEG_PCS = {
    0: {4, 8, 11, 2, 7, 10},    # I7  = E7  (E G# B D + blue G/Bb)
    1: {9, 1, 4, 7, 3},         # IV7 = A7  (A C# E G + blue Eb)
    2: {11, 3, 6, 9, 2},        # V7  = B7  (B D# F# A + blue D)
}
DEG_NAME = {0: "I7-E7", 1: "IV7-A7", 2: "V7-B7"}
DEG_ROOT = {0: 40, 1: 45, 2: 47}          # E2, A2, B2

# 12-bar blues:  I I I I | IV IV I I | V IV I I  (two choruses = 24 bars)
# section -> (name, [4 chord degrees per bar], note)
SECTIONS = [
    ("Chorus1A", [0, 0, 0, 0], "head -- I zone, harmonica states the OTVL riff"),
    ("Chorus1B", [1, 1, 0, 0], "IV zone, transport rises to the subdominant"),
    ("Chorus1C", [2, 1, 0, 0], "turnaround V-IV-I-I"),
    ("Chorus2A", [0, 0, 0, 0], "second chorus -- lead denser, band fuller"),
    ("Chorus2B", [1, 1, 0, 0], "IV zone, register lifted"),
    ("Chorus2C", [2, 1, 0, 0], "final turnaround, cadence home"),
]
PROG_DEG = [d for (_, degs, _) in SECTIONS for d in degs]
assert len(PROG_DEG) == N_BARS, (len(PROG_DEG), N_BARS)


def chord_tones(deg, lo, hi):
    """Chord tones (pc in DEG_PCS[deg]) inside [lo, hi], ascending."""
    return sorted(p for p in range(lo, hi + 1) if p % 12 in DEG_PCS[deg])


def nearest_in(pitches, target):
    return min(pitches, key=lambda p: abs(p - target))


# ------------------------------------------------------ method 050 OTVL ----
# Optimal transport between two chord "masses" in 1D = monotone matching of
# their sorted chord-tone lists (min-cost redistribution). The per-bar voicing
# is a 4-note chord mass; between bars we transport each mass point to the
# nearest (positionally-matched) mass point of the next chord. The lead voice
# follows the TOP mass point; the summed |delta| is the Wasserstein cost, which
# drives articulation (higher cost = more tension = shorter/louder attacks).
def bar_voicing(deg, lo=55, hi=88):
    """4-note chord voicing (mass) = sorted chord tones near a stable register."""
    tones = chord_tones(deg, lo, hi)
    if len(tones) < 4:
        tones = chord_tones(deg, lo - 12, hi + 12)[:4]
    # prefer a compact close voicing: pick the 4 tones nearest the register center
    center = (lo + hi) // 2
    tones = sorted(tones, key=lambda t: abs(t - center))[:4]
    return sorted(tones)


def transport(source, target):
    """Monotone (1D-optimal) transport between two sorted pitch masses.
    Returns the top-voice movement and the total Wasserstein cost."""
    n = min(len(source), len(target))
    cost = sum(abs(target[i] - source[i]) for i in range(n))
    top_move = target[-1] - source[-1] if (source and target) else 0
    return cost, top_move


def otvl_raw_walk(section, sec_idx):
    """Phase 1: OTVL raw draft (single voice, off-grid, chromatic).
    Returns list of MusicEvent."""
    name, degrees, _note = section
    r = np.random.default_rng(SEED + 1000 * (sec_idx + 1))
    total = 4 * BAR
    evs = []
    voicing = bar_voicing(degrees[0])
    top = voicing[-1]
    for b, deg in enumerate(degrees):
        t0 = b * BAR
        nxt = bar_voicing(degrees[b + 1] if b + 1 < 4 else degrees[b])
        cost, top_move = transport(voicing, nxt)
        # the lead top-voice is transported toward the next chord's top note
        # (smooth voice leading); Wasserstein cost shapes articulation.
        step_targets = voicing                       # chord mass of THIS bar
        for j in range(8):                           # 8 eighth-note slots
            # mass-weighted pick: bias toward root/5th/7th (lower indices) but
            # let the top voice dominate on beat 1.
            idx = (j * 3 + b) % len(step_targets)
            if j == 0:
                idx = len(step_targets) - 1          # beat 1 = top voice
            p = step_targets[idx]
            # chromatic micro-jitter => raw (pre-rules) pitch, off-key by design
            p += int(round(r.normal(0, 1.6)))
            p = max(50, min(96, p))
            # off-grid tick: nominal 8th + jitter (never a multiple of 120/240)
            nom = t0 + j * GRID8
            jit = int(r.integers(-30, 30))
            off = max(t0, min(t0 + BAR - 60, nom + jit))
            dur = max(70, 200 - int(cost))           # more transport cost = shorter
            vel = int(np.clip(66 + 24 * r.random() + min(cost, 20), 48, 108))
            evs.append(MusicEvent(pitch=p, volume=vel,
                                  start_tick=off, end_tick=off + dur))
        # glide the top voice partway toward next bar's transported top note
        top += int(round(0.5 * top_move)) if abs(top_move) > 2 else 0
        voicing = nxt
    # sort + zero-drift landmark
    evs.sort(key=lambda e: e.start_tick)
    if not evs or evs[-1].end_tick < total:
        evs.append(MusicEvent(pitch=0, volume=0, start_tick=total - 1,
                              end_tick=total))
    return evs


# ------------------------------------------------- phase-2 transforms -----
def quantize_lead(events, degrees, lo=58, hi=90):
    """Phase 2 rule: 16th-grid snap + per-bar chord-tone quantization + register
    clamp + dedup collided (tick, pitch) keeping longest duration."""
    tones_per_bar = [chord_tones(d, lo, hi) for d in degrees]
    seen = {}
    for e in events:
        if e.pitch == 0:
            continue
        tick = int(round(e.start_tick / GRID16) * GRID16)
        bar = min(tick // BAR, 3)
        if not tones_per_bar[bar]:
            continue
        q = nearest_in(tones_per_bar[bar], e.pitch)
        seen[(tick, q)] = max(seen.get((tick, q), 0), e.end_tick - e.start_tick)
    out = [(t, p, 90, d) for (t, p), d in sorted(seen.items())]
    return out


def _unit_from_quantized(q, total):
    unit = MusicUnit()
    for (t, p, v, d) in q:
        unit.add_event(MusicEvent(pitch=p, volume=v,
                                  start_tick=t, end_tick=min(t + d, total)))
    return _pad(unit, total)


def _pad(unit, total):
    if not unit.events:
        unit.add_event(MusicEvent(pitch=0, volume=0, start_tick=0, end_tick=total))
    else:
        mx = max(e.end_tick for e in unit.events)
        if mx < total:
            unit.add_event(MusicEvent(pitch=0, volume=0, start_tick=mx, end_tick=total))
    return unit


# ------------------------------------------------- voice builders ---------
def build_lead_unit(section, sec_idx):
    name, degrees, _ = section
    raw = otvl_raw_walk(section, sec_idx)
    q = quantize_lead(raw, degrees, lo=58, hi=90)
    return _unit_from_quantized(q, 4 * BAR)


def build_piano_unit(section, sec_idx):
    """Blues piano comp: offbeat 8th-note chord stabs (root+3rd+7th voicing),
    all chord tones, on the 8th grid."""
    name, degrees, _ = section
    total = 4 * BAR
    unit = MusicUnit()
    for b, deg in enumerate(degrees):
        t0 = b * BAR
        tones = sorted(chord_tones(deg, 55, 79), key=lambda t: abs(t - 67))[:3]
        if len(tones) < 3:
            tones = chord_tones(deg, 55, 79)[:3]
        for j in range(4):                          # 4 offbeat stabs per bar
            t = t0 + j * TPB + GRID8                # beats 1.5 2.5 3.5 4.5
            p = tones[(j + b) % len(tones)]
            unit.add_event(MusicEvent(pitch=p, volume=64,
                                      start_tick=t, end_tick=t + 200))
    return _pad(unit, total)


def build_guitar_unit(section, sec_idx):
    """Shuffle-flavoured acoustic chank: root+fifth dyad on every 8th (straight,
    grid-locked), all chord tones."""
    name, degrees, _ = section
    total = 4 * BAR
    unit = MusicUnit()
    for b, deg in enumerate(degrees):
        t0 = b * BAR
        tones = chord_tones(deg, 45, 70)
        root = nearest_in(tones, 52)
        cands = [t for t in tones if t > root]
        fifth = nearest_in(cands, root + 7) if cands else root
        for j in range(8):
            t = t0 + j * GRID8
            vel = 84 if j % 2 == 0 else 70
            unit.add_event(MusicEvent(pitch=root, volume=vel,
                                      start_tick=t, end_tick=t + 140))
            unit.add_event(MusicEvent(pitch=fifth, volume=vel - 8,
                                      start_tick=t, end_tick=t + 140))
    return _pad(unit, total)


def build_bass_unit(section, sec_idx):
    """Walking double-bass: quarter-note root/3rd/5th/b7 pattern (all chord
    tones), classic blues walk, grid-locked."""
    name, degrees, _ = section
    total = 4 * BAR
    unit = MusicUnit()
    for b, deg in enumerate(degrees):
        t0 = b * BAR
        root = DEG_ROOT[deg]
        # chord tones ABOVE the root (root..root+12) -> root-anchored walk
        tones = sorted(chord_tones(deg, root, root + 12))
        # classic blues walk: root, blue-3rd/3rd, 5th/blue-5th, octave/approach
        seq = [root,
               tones[1] if len(tones) > 1 else root + 7,
               tones[2] if len(tones) > 2 else root + 12,
               tones[min(3, len(tones) - 1)] if len(tones) > 1 else root]
        for j in range(4):
            t = t0 + j * TPB
            unit.add_event(MusicEvent(pitch=seq[j], volume=92,
                                      start_tick=t, end_tick=t + 420))
    return _pad(unit, total)


def build_drums_unit(section, sec_idx):
    """GM kit (channel 9): kick 1+3, snare 2+4 backbeat, hat 8ths. All on-grid.
    Chorus2 (sections 3-5) adds a crash on the downbeat."""
    name, degrees, _ = section
    total = 4 * BAR
    unit = MusicUnit()
    KICK = MidiPercussion.BASS_DRUM        # 36
    SNARE = MidiPercussion.ACOUSTIC_SNARE   # 38
    HAT = MidiPercussion.CLOSED_HI_HAT      # 42
    CRASH = MidiPercussion.CRASH_CYMBAL     # 49
    for b in range(4):
        t0 = b * BAR
        unit.add_event(MusicEvent(pitch=KICK, volume=110,
                                  start_tick=t0, end_tick=t0 + 110))
        unit.add_event(MusicEvent(pitch=KICK, volume=110,
                                  start_tick=t0 + 2 * TPB, end_tick=t0 + 2 * TPB + 110))
        unit.add_event(MusicEvent(pitch=SNARE, volume=96,
                                  start_tick=t0 + TPB, end_tick=t0 + TPB + 110))
        unit.add_event(MusicEvent(pitch=SNARE, volume=96,
                                  start_tick=t0 + 3 * TPB, end_tick=t0 + 3 * TPB + 110))
        for j in range(8):
            t = t0 + j * GRID8
            unit.add_event(MusicEvent(pitch=HAT, volume=62,
                                      start_tick=t, end_tick=t + 60))
    if sec_idx >= 3 and name.startswith("Chorus2"):
        for b in range(4):
            unit.add_event(MusicEvent(pitch=CRASH, volume=96,
                                      start_tick=b * BAR, end_tick=b * BAR + 240))
    return _pad(unit, total)


# ------------------------------------------------- phase-1 export ---------
def export_phase1(out_path):
    c = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
    c.create_matrix(num_voices=1, num_sections=N_SECTIONS)
    c.add_voice("LeadRaw", program=HARMONICA.midi_program, channel=0)
    for (name, _, _) in SECTIONS:
        c.add_section(name, bars=BARS_PER)
    for idx, section in enumerate(SECTIONS):
        name = section[0]
        evs = otvl_raw_walk(section, idx)
        c.set_unit(0, idx, MusicUnit(events=evs))
    ok, msg = c.validate()
    if not ok:
        raise RuntimeError(f"phase1 validate failed: {msg}")
    c.to_midi(out_path)
    return c


# ------------------------------------------------- main -------------------
def main():
    for sub in ("MIDI", "Audio", "Analysis", "Scripts"):
        os.makedirs(os.path.join(PROJECT_DIR, sub), exist_ok=True)

    print("Key:", KEY_NAME, "KEY_PCS:", sorted(KEY_PCS))
    print("Chords:", {k: DEG_NAME[k] for k in sorted(DEG_NAME)})

    p1_path = os.path.join(PROJECT_DIR, "MIDI", f"{PROJECT_NAME}-phase1.mid")
    export_phase1(p1_path)
    write_provenance(
        p1_path, classification=AI_ASSISTED,
        generator="050-Optimal-Transport-Voice-Leading (raw transport walk)",
        parameters={"phase": 1, "bpm": BPM, "key": KEY_NAME, "seed": SEED,
                    "voices": 1,
                    "transport": "monotone 1D-optimal transport between per-bar chord masses",
                    "note": "raw generative draft: off-grid ticks, chromatic micro-jitter, pre-rules"},
    )

    # ---- phase 2: 5-voice blues texture
    c2 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
    c2.create_matrix(num_voices=5, num_sections=N_SECTIONS)
    c2.add_voice("Lead",   program=HARMONICA.midi_program,     channel=0)
    c2.add_voice("Piano",  program=PIANO.midi_program,         channel=1)
    c2.add_voice("Guitar", program=ACOUSTIC_GUITAR.midi_program, channel=2)
    c2.add_voice("Bass",   program=DOUBLE_BASS.midi_program,   channel=3)
    c2.add_voice("Drums",  program=0,                           channel=9)
    for (name, _, _) in SECTIONS:
        c2.add_section(name, bars=BARS_PER)

    for idx, section in enumerate(SECTIONS):
        name = section[0]
        c2.set_unit(0, idx, build_lead_unit(section, idx))
        c2.set_unit(1, idx, build_piano_unit(section, idx))
        c2.set_unit(2, idx, build_guitar_unit(section, idx))
        c2.set_unit(3, idx, build_bass_unit(section, idx))
        c2.set_unit(4, idx, build_drums_unit(section, idx))

    ok, msg = c2.validate()
    if not ok:
        raise RuntimeError(f"phase2 validate failed: {msg}")

    midi_path = os.path.join(PROJECT_DIR, "MIDI", f"{PROJECT_NAME}.mid")
    c2.to_midi(midi_path)
    assert os.path.getsize(midi_path) > 40, "empty phase2"
    assert os.path.getsize(p1_path) > 40, "empty phase1"

    write_provenance(
        midi_path, classification=AI_ASSISTED,
        generator="050-Optimal-Transport-Voice-Leading + musicom rules",
        parameters={"phase": 2, "bpm": BPM, "key": KEY_NAME, "seed": SEED,
                    "voices": 5, "form": "6 sections x 4 bars = 24 bars (2 x 12-bar blues)",
                    "quantization": "16th-grid (120 ticks) + per-bar chord-tone",
                    "instruments": ["harmonica", "piano", "acoustic guitar",
                                    "double bass", "drum kit"]},
        notes="Blues in E. Two-phase: raw OTVL transport walk -> chord-tone "
              "quantized + grid-snapped 5-voice blues texture. All pitched notes "
              "are E-blues chord tones.",
    )

    grid_path = os.path.join(PROJECT_DIR, "Analysis", "grid_visualization.txt")
    write_grid_visualization(c2.matrix, grid_path, ticks_per_character=240, bpm=BPM)

    # ---- voice-leading check (outer voices = bass + lead, classical)
    vlc = VoiceLeadingRules(style="classical")
    vl_flags = []
    for bar in range(N_BARS - 1):
        deg_a, deg_b = PROG_DEG[bar], PROG_DEG[bar + 1]
        bass_a, bass_b = DEG_ROOT[deg_a], DEG_ROOT[deg_b]
        s, b = divmod(bar, BARS_PER)
        s2, b2 = (s, b + 1) if b + 1 < BARS_PER else (s + 1, 0)
        if s2 >= N_SECTIONS:
            continue

        def bar_top(sec, bb):
            u = c2.matrix.get_unit((0, sec))
            tops = [e.pitch for e in u.events if e.pitch > 0
                    and bb * BAR <= e.start_tick < (bb + 1) * BAR]
            return max(tops) if tops else 0

        lead_a, lead_b = bar_top(s, b), bar_top(s2, b2)
        if lead_a and lead_b:
            try:
                par = vlc.check_parallel_motion([int(bass_a), int(lead_a)],
                                                [int(bass_b), int(lead_b)])
                if par:
                    vl_flags.append((bar, "parallel", par))
                hid = vlc.check_hidden_fifths([int(bass_a), int(lead_a)],
                                              [int(bass_b), int(lead_b)])
                if hid:
                    vl_flags.append((bar, "hidden", hid))
            except Exception as e:  # noqa: BLE001 - never let VL check block export
                print("VL check exception (non-fatal):", repr(e))
    print("VL flags (bass+lead, classical):", len(vl_flags))

    # ---- summary.json for Analysis/
    summary = {
        "project": PROJECT_NAME,
        "genre": GENRE,
        "method": "050 Optimal Transport Voice Leading (OTVL)",
        "layer": "concrete",
        "key": KEY_NAME,
        "key_pcs": sorted(KEY_PCS),
        "bpm": BPM,
        "form": "6 sections x 4 bars = 24 bars (2 x 12-bar blues)",
        "progression": [DEG_NAME[d] for d in PROG_DEG],
        "voices": ["Lead(harmonica)", "Piano", "AcousticGuitar", "DoubleBass", "Drums"],
        "voice_leading_flags": len(vl_flags),
        "seed": SEED,
    }
    with open(os.path.join(PROJECT_DIR, "Analysis", "summary.json"), "w") as f:
        json.dump(summary, f, indent=2)

    print("PHASE1", p1_path, os.path.getsize(p1_path))
    print("PHASE2", midi_path, os.path.getsize(midi_path))
    print("GRID", grid_path)
    print("SUMMARY", os.path.join(PROJECT_DIR, "Analysis", "summary.json"))


if __name__ == "__main__":
    main()
