#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project 203: Brownian Chorale Variations (rework of 062-brownian-chorale)

Rework decision : REDESIGN (source 062 failed audit: missing phase1 MIDI,
                  project provenance.json, index.html). Rebuilt from scratch
                  through canonical UnitMatrixComposer, preserving identity:
                  C aeolian, 84 BPM, Reflected Brownian Motion Pitch Diffusion
                  (Method 048 / RBMPD), 4-voice homophonic chorale.

Longer + more varied : 16 bars across 4 regions (Intro/Verse/Chorus/Bridge),
                  each region its own 4-bar harmonic region (midpoint-chord
                  rooted), 5 variation techniques, added violin counterline
                  (bars 9-16) and ch9 drum pulse.

Two-phase : Phase 1 = raw reflected-Brownian draft (single voice, unquantized
                  pitch walk + rhythm). Phase 2 = musicom rules: chord-tone
                  quantization per bar, classical voice leading, rhythm-grid
                  snap, register enforcement.
"""
import os
import sys
import random
import itertools
import json
import datetime

import numpy as np

from structures import MusicUnit, MusicEvent, MidiInstrument, MidiPercussion
from workflows.unitmatrix_composer import UnitMatrixComposer
from rules.voice_leading import VoiceLeadingRules
from rules.progression import Scale7ChordDegree
from utilities.constants import SCALE_PATTERNS
from visualization.grid import write_grid_visualization
from workflows.provenance import write_provenance, AI_GENERATED

# ---------------------------------------------------------------------------
# Global parameters
# ---------------------------------------------------------------------------
BPM = 84
TICKS_PER_BEAT = 480
BEATS_PER_BAR = 4
BAR_TICKS = TICKS_PER_BEAT * BEATS_PER_BAR   # 1920

KEY_ROOT = 48          # C3
KEY_NAME = "C aeolian"
SCALE = SCALE_PATTERNS["aeolian"]            # [0,2,3,5,7,8,10]
KEY_PCS = sorted({(KEY_ROOT + i) % 12 for i in SCALE})

SEED = 9007
random.seed(SEED)
np.random.seed(SEED)

# 4 regions x 4 bars = 16 bars. Each region = own harmonic region.
REGIONS = [
    {"name": "Intro",  "degrees": [1, 6, 3, 7]},   # i  VI  III  VII  (source anchor)
    {"name": "Verse",  "degrees": [3, 7, 1, 6]},   # III VII i   VI   (harmonic rotation)
    {"name": "Chorus", "degrees": [4, 7, 6, 3]},   # iv  VII VI  III  (tension shift)
    {"name": "Bridge", "degrees": [5, 4, 7, 1]},   # v   iv  VII i    (plagal arc home)
]
DEGREES = [d for r in REGIONS for d in r["degrees"]]   # 16 entries
ROMAN_LABEL = {1: "i", 2: "ii-", 3: "III", 4: "iv", 5: "v", 6: "VI", 7: "VII"}


def region_for_bar(bar):
    if bar < 4:
        return "Intro"
    if bar < 8:
        return "Verse"
    if bar < 12:
        return "Chorus"
    return "Bridge"


def region_index(bar):
    return bar // 4


def midpoint_degree(bar):
    r = REGIONS[region_index(bar)]
    return r["degrees"][1]          # 2nd bar of region = midpoint chord


# ---------------------------------------------------------------------------
# Voices
# ---------------------------------------------------------------------------
# Pitched chorale quartet (rows 0-3), counterline (row 4), drums (row 5)
PITCHED = [
    {"name": "Soprano", "program": MidiInstrument.FLUTE, "channel": 0, "lo": 62, "hi": 84},
    {"name": "Alto",    "program": MidiInstrument.FLUTE, "channel": 1, "lo": 53, "hi": 74},
    {"name": "Tenor",   "program": MidiInstrument.FLUTE, "channel": 2, "lo": 48, "hi": 65},
    {"name": "Bass",    "program": MidiInstrument.BASS,  "channel": 3, "lo": 38, "hi": 55},
]
COUNTER = {"name": "Counterline", "program": MidiInstrument.VIOLIN, "channel": 4, "lo": 60, "hi": 76}
DRUMS = {"name": "Drums", "program": 0, "channel": 9}

# Brownian parameters (Method 048)
SIGMA0 = 1.6
DRIFT_T = 0.12
THETA = 0.42
DENSITY_FLOOR = 3


# ---------------------------------------------------------------------------
# Phase 1 -- Reflected Brownian motion (method 048)
# ---------------------------------------------------------------------------
def brownian_walk(n_steps, lo, hi, start, sigma, tonic, drift):
    x = float(start)
    traj = []
    for _ in range(n_steps):
        x = x + np.random.normal(0.0, sigma) + drift * (tonic - x)
        if x < lo:
            x = 2.0 * lo - x
        if x > hi:
            x = 2.0 * hi - x
        traj.append(int(round(x)))
    return traj


def _speed_series():
    n = 8192
    walk = brownian_walk(n, 62.0, 84.0, start=72.0, sigma=SIGMA0, tonic=72.0, drift=DRIFT_T)
    d = np.abs(np.diff(walk))
    return (d - d.min()) / (d.max() - d.min() + 1e-12)


def rhythm_mask(bar, speed):
    region = region_for_bar(bar)
    sub = 2 if region == "Chorus" else 4      # Chorus = augmentation (8ths)
    seg = speed[bar * 512:(bar + 1) * 512]
    idxs = np.linspace(0, len(seg) - 1, sub).astype(int)
    vals = np.array([seg[i] for i in idxs])
    theta = THETA if region != "Bridge" else THETA * 0.55   # Bridge denser
    mask = [1 if v > theta else 0 for v in vals]
    mask[0] = 1
    if sum(mask) < DENSITY_FLOOR:
        order = sorted(range(1, sub), key=lambda i: -vals[i])
        for i in order:
            if sum(mask) >= DENSITY_FLOOR:
                break
            mask[i] = 1
    return mask, sub


def raw_contour(bar, voice_idx, n_onsets):
    """Per-bar normalized [0,1] raw pitch contour (Phase 1 material)."""
    v = PITCHED[voice_idx]
    lo, hi = float(v["lo"]), float(v["hi"])
    tonic = float(KEY_ROOT + 12)
    n = max(n_onsets * 4 + 64, 256)
    walk = brownian_walk(n, lo, hi, start=tonic, sigma=SIGMA0, tonic=tonic, drift=DRIFT_T)
    phase = (bar * 149 + voice_idx * 89) % (n - n_onsets)
    idxs = [phase + k * 4 for k in range(n_onsets)]
    seg = np.array([walk[i] for i in idxs], dtype=float)
    lo_s, hi_s = seg.min(), seg.max()
    if hi_s - lo_s < 1e-9:
        return [0.5] * n_onsets
    return ((seg - lo_s) / (hi_s - lo_s)).tolist()


# ---------------------------------------------------------------------------
# Diatonic helpers (canonical Scale7ChordDegree only -- no local %7 wrappers)
# ---------------------------------------------------------------------------
def degree_to_midi(degree):
    return Scale7ChordDegree.get_diatonic_note(KEY_ROOT, SCALE, degree - 1)


def chord_tones(degree):
    """Absolute triad tones for a scale degree (diatonic stacked thirds)."""
    return [Scale7ChordDegree.get_diatonic_note(KEY_ROOT, SCALE, (degree - 1 + off) % 7)
            for off in (0, 2, 4)]


def fold_to_register(midi, lo, hi):
    mid = (lo + hi) // 2
    while midi > mid + 6:
        midi -= 12
    while midi <= mid - 6:
        midi += 12
    while midi > hi:
        midi -= 12
    while midi < lo:
        midi += 12
    return midi


def chord_tones_for_voice(bar, vi):
    deg = DEGREES[bar]
    v = PITCHED[vi]
    return sorted({fold_to_register(t, v["lo"], v["hi"]) for t in chord_tones(deg)})


# ---------------------------------------------------------------------------
# Phase 2a -- voice-leading anchors (classical rules)
# ---------------------------------------------------------------------------
def check_parallel_fifths_octaves(prev, curr):
    viols = []
    n = min(len(prev), len(curr))
    for i in range(n):
        for j in range(i + 1, n):
            iv1 = (prev[j] - prev[i]) % 12
            iv2 = (curr[j] - curr[i]) % 12
            m1 = curr[i] - prev[i]
            m2 = curr[j] - prev[j]
            same_dir = (m1 > 0 and m2 > 0) or (m1 < 0 and m2 < 0)
            if iv1 == 7 and iv2 == 7 and same_dir and m1 == m2:
                viols.append((j, i, "fifth"))
            if iv1 == 0 and iv2 == 0 and same_dir and m1 == m2:
                viols.append((j, i, "octave"))
    return viols


def _best_voicing(prev, bar):
    per_voice = [chord_tones_for_voice(bar, vi) for vi in range(4)]
    bass_root = fold_to_register(degree_to_midi(DEGREES[bar]), PITCHED[3]["lo"], PITCHED[3]["hi"])
    per_voice[3] = [bass_root]
    vlr = VoiceLeadingRules(style="classical")

    def valid(cand):
        if any(cand[i] <= cand[i + 1] for i in range(3)):
            return False
        if any(cand[vi] < PITCHED[vi]["lo"] or cand[vi] > PITCHED[vi]["hi"] for vi in range(4)):
            return False
        return True

    best = None
    best_cost = None
    for combo in itertools.product(*per_voice):
        cand = list(combo)
        if not valid(cand):
            continue
        if check_parallel_fifths_octaves(prev, cand):
            continue
        cost = vlr.calculate_voice_leading_distance(prev, cand)
        if cand == prev:
            cost += 8
        if best_cost is None or cost < best_cost:
            best_cost, best = cost, cand
    if best is not None:
        return best
    for combo in itertools.product(*per_voice):
        cand = list(combo)
        if not valid(cand):
            continue
        cost = vlr.calculate_voice_leading_distance(prev, cand)
        if best_cost is None or cost < best_cost:
            best_cost, best = cost, cand
    return best if best is not None else list(prev)


def seed_voicing(bar):
    """Descending S>A>T>B voicing built from in-scale chord tones only."""
    bass = fold_to_register(degree_to_midi(DEGREES[bar]), PITCHED[3]["lo"], PITCHED[3]["hi"])

    def pick(tones, floor, hi):
        cands = [t for t in sorted(tones) if floor < t <= hi]
        return cands[0] if cands else floor + 3

    tenor = pick(chord_tones_for_voice(bar, 2), bass, PITCHED[2]["hi"])
    alto = pick(chord_tones_for_voice(bar, 1), tenor, PITCHED[1]["hi"])
    sop = pick(chord_tones_for_voice(bar, 0), alto, PITCHED[0]["hi"])
    return [sop, alto, tenor, bass]


def resolve_anchors():
    anchors = []
    prev = None
    for bar in range(16):
        if prev is None:
            prev = seed_voicing(bar)
            anchors.append(prev)
            continue
        prev = _best_voicing(prev, bar)
        anchors.append(prev)
    return anchors


# ---------------------------------------------------------------------------
# Phase 2b -- build events per voice
# ---------------------------------------------------------------------------
def snap(tick):
    """Snap to the 16th (120) / 8th (240) grid (redundant safety)."""
    if tick % 240 == 0:
        return tick
    if tick % 120 == 0:
        return tick
    return int(round(tick / 120.0)) * 120


def dedup(events):
    """Collided (start_tick, pitch) -> keep longest duration."""
    seen = {}
    out = []
    for e in events:
        key = (e.start_tick, e.pitch)
        if key in seen:
            if e.end_tick > seen[key].end_tick:
                seen[key] = e
        else:
            seen[key] = e
            out.append(e)
    return [seen[k] for k in sorted(seen, key=lambda k: (k[0], k[1]))]


def build_cell_events(bar, mask, sub, anchors, speed):
    """Return dict voice_name -> list[MusicEvent] for one bar."""
    region = region_for_bar(bar)
    slot_ticks = BAR_TICKS // sub
    n_onsets = sum(mask)
    events = {v["name"]: [] for v in PITCHED}
    events[COUNTER["name"]] = []
    events[DRUMS["name"]] = []

    S, A, T, B = anchors[bar]

    # ---- Soprano melodic line (moves among chord tones) ----
    contour = raw_contour(bar, 0, n_onsets)
    tones = chord_tones_for_voice(bar, 0)
    lo_s = A + 2
    hi_s = PITCHED[0]["hi"]
    valid_tones = sorted({t for t in tones if lo_s <= t <= hi_s}) or [A + 4]
    # variation: Verse -> register lift, Bridge -> retrograde contour
    if region == "Verse":
        valid_tones = sorted({t for t in valid_tones if t >= lo_s + 3} or valid_tones)
    if region == "Bridge":
        contour = list(reversed(contour))     # retrograde
    onset_idx = 0
    s_events = []
    for slot in range(sub):
        if not mask[slot]:
            continue
        c = contour[min(onset_idx, len(contour) - 1)]
        pitch = min(valid_tones, key=lambda t: abs(t - (lo_s + c * (hi_s - lo_s))))
        pitch = max(lo_s, min(hi_s, pitch))
        start = snap(slot * slot_ticks)
        end = start + slot_ticks - 24
        s_events.append(MusicEvent(pitch=pitch, volume=96, start_tick=start, end_tick=end))
        onset_idx += 1
    events["Soprano"] = s_events

    # ---- Alto / Tenor / Bass: hold anchor chord tone (homophonic support) ----
    for vname, anchor in (("Alto", A), ("Tenor", T), ("Bass", B)):
        evs = []
        for slot in range(sub):
            if not mask[slot]:
                continue
            start = snap(slot * slot_ticks)
            end = start + slot_ticks - 24
            evs.append(MusicEvent(pitch=anchor, volume=88, start_tick=start, end_tick=end))
        events[vname] = evs

    # ---- Counterline (bars 9-16): long chord tones, inverted motion ----
    if bar >= 8:
        ct = chord_tones(DEGREES[bar])
        ctones = sorted({fold_to_register(t, COUNTER["lo"], COUNTER["hi"]) for t in ct})
        n_notes = 2 if region == "Bridge" else 1
        for k in range(n_notes):
            start = snap(k * (BAR_TICKS // n_notes))
            end = start + (BAR_TICKS // n_notes) - 24
            pitch = ctones[(k + (bar % 2)) % len(ctones)]
            events[COUNTER["name"]].append(
                MusicEvent(pitch=pitch, volume=90, start_tick=start, end_tick=end))

    # ---- Drums (ch9): downbeat pulse + sparse HH in Chorus/Bridge ----
    d = []
    d.append(MusicEvent(pitch=MidiPercussion.BASS_DRUM, volume=100, start_tick=0, end_tick=120))
    if region in ("Chorus", "Bridge"):
        for k in (1, 2, 3):
            d.append(MusicEvent(pitch=MidiPercussion.CLOSED_HI_HAT, volume=70,
                                start_tick=k * 480, end_tick=k * 480 + 120))
        d.append(MusicEvent(pitch=MidiPercussion.ACOUSTIC_SNARE, volume=80,
                            start_tick=960, end_tick=1080))
    events[DRUMS["name"]] = d

    # zero-drift landmark: every cell ends exactly at BAR_TICKS
    for vname, evs in events.items():
        last_end = max((e.end_tick for e in evs), default=0)
        if last_end < BAR_TICKS:
            evs.append(MusicEvent(pitch=0, volume=0, start_tick=last_end, end_tick=BAR_TICKS))
        events[vname] = dedup(evs)
    return events


# ---------------------------------------------------------------------------
# Phase 1 export -- raw draft (single voice, unquantized)
# ---------------------------------------------------------------------------
def build_phase1():
    composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TICKS_PER_BEAT, beats_per_bar=BEATS_PER_BAR)
    composer.create_matrix(num_voices=1, num_sections=16)
    composer.add_voice("RawBrownian", program=MidiInstrument.FLUTE, channel=0)
    for b in range(16):
        composer.add_section("RawBar%d" % (b + 1), bars=1)
    speed = _speed_series()
    for bar in range(16):
        mask, sub = rhythm_mask(bar, speed)
        slot_ticks = BAR_TICKS // sub
        n_onsets = sum(mask)
        # raw unquantized walk mapped straight to MIDI ints (48..84)
        walk = brownian_walk(max(n_onsets * 4 + 64, 256), 48.0, 84.0,
                             start=float(KEY_ROOT + 12), sigma=SIGMA0,
                             tonic=float(KEY_ROOT + 12), drift=DRIFT_T)
        phase = (bar * 149) % (len(walk) - n_onsets)
        idxs = [phase + k * 4 for k in range(n_onsets)]
        evs = []
        oi = 0
        for slot in range(sub):
            if not mask[slot]:
                continue
            pitch = int(walk[idxs[oi]])
            oi += 1
            start = snap(slot * slot_ticks)
            end = start + slot_ticks - 24
            evs.append(MusicEvent(pitch=pitch, volume=96, start_tick=start, end_tick=end))
        last_end = max((e.end_tick for e in evs), default=0)
        if last_end < BAR_TICKS:
            evs.append(MusicEvent(pitch=0, volume=0, start_tick=last_end, end_tick=BAR_TICKS))
        composer.set_unit(0, bar, MusicUnit(events=dedup(evs)))
    return composer


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
PROJECT_DIR = "/opt/data/projects/Styles/Experimental/203-brownian-chorale-variations"
MIDI_DIR = os.path.join(PROJECT_DIR, "MIDI")
AUDIO_DIR = os.path.join(PROJECT_DIR, "Audio")
ANALYSIS_DIR = os.path.join(PROJECT_DIR, "Analysis")
for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
    os.makedirs(d, exist_ok=True)


def main():
    print("=" * 70)
    print("PROJECT 203: BROWNIAN CHORALE VARIATIONS (rework of 062)")
    print("=" * 70)
    print("Key %s | BPM %d | 16 bars | 4 regions x 4 bars" % (KEY_NAME, BPM))
    print("Regions:")
    for r in REGIONS:
        print("  %-7s %s" % (r["name"], " - ".join(ROMAN_LABEL[d] for d in r["degrees"])))

    speed = _speed_series()
    masks = {}
    subs = {}
    print("\nRhythm DNA (16th grid, 8th in Chorus):")
    for bar in range(16):
        m, sub = rhythm_mask(bar, speed)
        masks[bar] = m
        subs[bar] = sub
        cells = "".join("\u2588" if b else "\u2591" for b in m)
        print("  %-6s %2d  %-6s %s" % (region_for_bar(bar), bar + 1,
                                       ROMAN_LABEL[DEGREES[bar]], cells))

    # Phase 2a anchors
    print("\n[Phase 2a] voice-leading anchors ...")
    anchors = resolve_anchors()

    # Phase 2b events
    print("[Phase 2b] build events ...")
    composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TICKS_PER_BEAT, beats_per_bar=BEATS_PER_BAR)
    voice_names = [v["name"] for v in PITCHED] + [COUNTER["name"], DRUMS["name"]]
    composer.create_matrix(num_voices=len(voice_names), num_sections=16)
    for v in PITCHED:
        composer.add_voice(v["name"], program=v["program"], channel=v["channel"])
    composer.add_voice(COUNTER["name"], program=COUNTER["program"], channel=COUNTER["channel"])
    composer.add_voice(DRUMS["name"], program=DRUMS["program"], channel=DRUMS["channel"])
    for b in range(16):
        composer.add_section("%s%d" % (region_for_bar(b), (b % 4) + 1), bars=1)

    for bar in range(16):
        cell = build_cell_events(bar, masks[bar], subs[bar], anchors, speed)
        for vi, vname in enumerate(voice_names):
            composer.set_unit(vi, bar, MusicUnit(events=cell[vname]))

    ok, msg = composer.validate()
    print("Zero-drift validation: %s (%s)" % ("PASS" if ok else "FAIL", msg))
    if not ok:
        print("ERROR:", msg)
        sys.exit(1)
    print("Track length: %d ticks = %.1f bars" % (
        composer.get_track_length_ticks(), composer.get_track_length_bars()))

    # ---- Phase 2 MIDI ----
    phase2_midi = os.path.join(MIDI_DIR, "203-brownian-chorale-variations.mid")
    composer.to_midi(phase2_midi)
    assert os.path.getsize(phase2_midi) > 40, "phase2 MIDI too small"

    # ---- Phase 1 MIDI ----
    p1 = build_phase1()
    ok1, msg1 = p1.validate()
    if not ok1:
        raise RuntimeError("phase1 validate failed: " + msg1)
    phase1_midi = os.path.join(MIDI_DIR, "203-brownian-chorale-variations-phase1.mid")
    p1.to_midi(phase1_midi)
    assert os.path.getsize(phase1_midi) > 40, "phase1 MIDI too small"

    # ---- grid visualization ----
    grid_path = os.path.join(ANALYSIS_DIR, "grid_visualization.txt")
    write_grid_visualization(composer.matrix, grid_path, ticks_per_character=120,
                             voice_names=voice_names, bpm=BPM,
                             mode="C aeolian - RBMPD variations")

    # ---- provenance sidecars ----
    prov2 = write_provenance(
        artifact_path=phase2_midi, classification=AI_GENERATED,
        generator="Reflected Brownian Motion Pitch Diffusion (RBMPD) Method 048 + musicom rules",
        sources=["Research/CompositionMethods/methods_db.md:Method 048",
                 "rules/voice_leading.py:VoiceLeadingRules",
                 "rules/progression.py:Scale7ChordDegree",
                 "utilities/constants.py:SCALE_PATTERNS"],
        parameters={"bpm": BPM, "key": KEY_NAME, "seed": SEED, "bars": 16,
                    "regions": [r["name"] for r in REGIONS],
                    "progression": [ROMAN_LABEL[d] for d in DEGREES],
                    "variations": ["harmonic_rotation", "register_lift",
                                   "augmentation", "retrograde", "counterline",
                                   "density_rise"],
                    "voices": voice_names},
        notes="Phase 2 (rules): chord-tone quantization per bar, classical voice "
              "leading, rhythm-grid snap, register enforcement.")
    prov1 = write_provenance(
        artifact_path=phase1_midi, classification=AI_GENERATED,
        generator="Reflected Brownian Motion Pitch Diffusion (RBMPD) Method 048 (raw)",
        sources=["Research/CompositionMethods/methods_db.md:Method 048"],
        parameters={"bpm": BPM, "key": KEY_NAME, "seed": SEED, "bars": 16,
                    "quantized": False, "voice": "single raw"},
        notes="Phase 1 (pre-rules): raw reflected-Brownian pitch walk, unquantized, "
              "single voice. No harmonic/scale constraints applied.")

    # ---- project-level provenance.json (audit standard #6) ----
    project_prov = {
        "project": "203-brownian-chorale-variations",
        "genre": "Experimental",
        "rework_of": "062-brownian-chorale",
        "decision": "redesign",
        "created_utc": datetime.datetime.utcnow().isoformat() + "Z",
        "phase1": os.path.basename(phase1_midi),
        "phase2": os.path.basename(phase2_midi),
        "key": KEY_NAME,
        "bpm": BPM,
        "bars": 16,
        "seed": SEED,
    }
    with open(os.path.join(PROJECT_DIR, "provenance.json"), "w") as f:
        json.dump(project_prov, f, indent=2)

    print("\nOutputs:")
    print("  phase2 MIDI :", phase2_midi, "(%d B)" % os.path.getsize(phase2_midi))
    print("  phase1 MIDI :", phase1_midi, "(%d B)" % os.path.getsize(phase1_midi))
    print("  grid        :", grid_path)
    print("  provenance  :", prov2)
    print("  provenance  :", prov1)
    print("  project prov:", os.path.join(PROJECT_DIR, "provenance.json"))
    print("=" * 70)
    print("COMPOSITION COMPLETE")


if __name__ == "__main__":
    main()
