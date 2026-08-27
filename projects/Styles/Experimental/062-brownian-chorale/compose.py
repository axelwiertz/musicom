#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project 062: Reflected Brownian Motion Pitch Diffusion Chorale (Method 048)

Composition method : RBMPD (Method 048, nature-led stochastic diffusion)
  Phase 1 (generative draft) : multi-particle reflected Brownian motion
    - Each voice is a particle diffusing through a pitch corridor bounded
      by reflective barriers (voice register limits). Standard discrete
      random-walk: X(t+1) = X(t) + N(0, sigma^2), with reflection
      X = 2*barrier - X when a barrier is crossed.
    - Drift term biases the walk toward the key tonic (HOME gravity);
      the stochastic term injects organic wandering.
    - Reflections at the scale barriers generate motif repeats and
      neighbor-tone turns (the signature RBMPD behavior).
    - Raw output: a per-voice, per-bar [0,1] pitch contour sampled at the
      rhythm onset grid (no harmonic context yet).
  Phase 2 (musicom rules post-processing):
    - harmonic framework: C aeolian (SCALE_PATTERNS), progression
      i-VI-III-vii-i-VI-III-i built via Scale7ChordDegree.get_diatonic_note
      (canonical helper, no off-by-octave %7 wrappers)
    - quantize raw pitch indices to chord tones of the active bar chord
    - voice leading: VoiceLeadingRules (rules/voice_leading.py,
      classical) -- parallel fifth/octave scan + exhaustive nearest
      voicing search (Bass = chord root)
    - validate_voice_ranges for the 4-voice chorale register

Engine: UnitMatrixComposer workflow (zero-drift gate -> to_midi)
Form  : 8 bars, 4 voices (Soprano/Alto/Tenor/Bass), homophonic chorale
Key   : C aeolian (root 48 = C3), 4 sixteenth-note slots per bar rhythm
DNA   : diffusion-driven rhythm (particle speed threshold + density floor)

Deliverables (MIDI only, per autonomous composition job contract):
  - MIDI/062-brownian-chorale.mid
  - Analysis/grid_visualization.txt
  - provenance.json sidecar
"""
import os
import sys
import random
import itertools

import numpy as np

from structures import MusicUnit, MusicEvent, MidiInstrument
from workflows.unitmatrix_composer import (
    UnitMatrixComposer,
)
from rules.voice_leading import VoiceLeadingRules
from rules.progression import Scale7ChordDegree
from utilities.constants import SCALE_PATTERNS
from visualization.grid import write_grid_visualization
from workflows.provenance import write_provenance, AI_GENERATED

# ---------------------------------------------------------------------------
# Parameters
# ---------------------------------------------------------------------------
BPM = 84
TICKS_PER_BEAT = 480
BEATS_PER_BAR = 4
BAR_TICKS = TICKS_PER_BEAT * BEATS_PER_BAR   # 1920
NUM_BARS = 8
NUM_VOICES = 4
SUB = 4                                       # sixteenth-note rhythm grid

KEY_ROOT = 48          # C3
KEY_NAME = "C aeolian"
SCALE_INTERVALS = SCALE_PATTERNS['aeolian']   # [0,2,3,5,7,8,10]

# Chord plan: scale degrees (1-indexed) per bar, aeolian modal gravity
# i - VI - III - vii - i - VI - III - i  (modal cadence arc)
CHORD_DEGREES = [1, 6, 3, 7, 1, 6, 3, 1]
ROMAN = ["i", "VI", "III", "vii", "i", "VI", "III", "i"]

VOICES = [
    {"name": "Soprano", "program": MidiInstrument.FLUTE, "channel": 0, "lo": 62, "hi": 84},
    {"name": "Alto",    "program": MidiInstrument.FLUTE, "channel": 1, "lo": 53, "hi": 74},
    {"name": "Tenor",   "program": MidiInstrument.FLUTE, "channel": 2, "lo": 48, "hi": 65},
    {"name": "Bass",    "program": MidiInstrument.BASS,  "channel": 3, "lo": 38, "hi": 55},
]

SEED = 4801
random.seed(SEED)
np.random.seed(SEED)

# Brownian parameters (Method 048)
SIGMA0 = 1.6        # per-step diffusion sigma (semitones)
DRIFT_T = 0.12      # tonic pull toward HOME pitch (fraction of distance)
THETA = 0.42        # speed threshold for rhythm onset triggers
DENSITY_FLOOR = 3   # minimum onsets per bar

# ---------------------------------------------------------------------------
# Phase 1 -- Reflected Brownian motion pitch diffusion (method 048)
# ---------------------------------------------------------------------------
def brownian_walk(n_steps, lo, hi, start, sigma, tonic, drift):
    """Reflected Brownian motion in the pitch corridor [lo, hi].

    X(t+1) = X(t) + N(0, sigma^2) + drift*(tonic - X(t)).
    Reflection at barriers: X = 2*barrier - X (elastic mirror), which
    produces the motif-repetition / neighbor-tone turns characteristic
    of RBMPD. Returns the integer pitch trajectory.
    """
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


def raw_brownian_contour(bar, voice_idx, n_onsets):
    """Phase-1 raw material: reflected walk -> [0,1] pitch contour.

    Each voice runs one deterministic seeded walk in its own register
    corridor; the walk is sub-sampled at the onset grid with a per-bar
    phase offset so sections stay voice-coherent but vary. Returns
    normalized floats in [0,1].
    """
    v = VOICES[voice_idx]
    lo, hi = float(v["lo"]), float(v["hi"])
    tonic = float(KEY_ROOT + 12)          # C4 tonic pull (HOME gravity)
    n = max(n_onsets * 4 + 64, 256)
    walk = brownian_walk(n, lo, hi, start=tonic, sigma=SIGMA0, tonic=tonic, drift=DRIFT_T)
    phase = (bar * 149 + voice_idx * 89) % (n - n_onsets)
    idxs = [phase + k * 4 for k in range(n_onsets)]
    seg = np.array([walk[i] for i in idxs], dtype=float)
    lo_s, hi_s = seg.min(), seg.max()
    if hi_s - lo_s < 1e-9:
        return [0.5] * n_onsets
    return ((seg - lo_s) / (hi_s - lo_s)).tolist()


def brownian_rhythm_masks():
    """Per-bar binary rhythm masks (4 sixteenth slots) from walk speed.

    Speed = |X(t+1) - X(t)| of the Soprano register walk. Slots whose
    speed exceeds THETA fire; slot 0 (downbeat) is anchored ON for
    metrical gravity, and a density floor keeps bars from collapsing
    to silence.
    """
    n = 4096
    walk = brownian_walk(n, float(VOICES[0]["lo"]), float(VOICES[0]["hi"]),
                         start=float(KEY_ROOT + 12), sigma=SIGMA0,
                         tonic=float(KEY_ROOT + 12), drift=DRIFT_T)
    d = np.abs(np.diff(walk))
    sp = (d - d.min()) / (d.max() - d.min() + 1e-12)
    masks = []
    for bar in range(NUM_BARS):
        seg = sp[bar * 512:(bar + 1) * 512]
        idxs = np.linspace(0, len(seg) - 1, SUB).astype(int)
        vals = np.array([seg[i] for i in idxs])
        mask = [1 if v > THETA else 0 for v in vals]
        mask[0] = 1                 # downbeat anchor (metrical gravity)
        if sum(mask) < DENSITY_FLOOR:
            order = sorted(range(1, SUB), key=lambda i: -vals[i])
            for i in order:
                if sum(mask) >= DENSITY_FLOOR:
                    break
                mask[i] = 1
        masks.append(mask)
    return masks


# ---------------------------------------------------------------------------
# Diatonic helpers (canonical Scale7ChordDegree only -- no local %7 wrappers)
# ---------------------------------------------------------------------------
def degree_to_midi(degree, base_midi=KEY_ROOT):
    """1-indexed scale degree -> absolute MIDI pitch (canonical helper)."""
    return Scale7ChordDegree.get_diatonic_note(base_midi, SCALE_INTERVALS, degree - 1)


def fold_to_register(midi, voice_idx):
    """Fold an absolute pitch into the voice register (nearest octave)."""
    lo, hi = VOICES[voice_idx]["lo"], VOICES[voice_idx]["hi"]
    mid = (lo + hi) // 2
    while midi > mid + 6:
        midi -= 12
    while midi <= mid - 6:
        midi += 12
    return midi


# ---------------------------------------------------------------------------
# Phase 2 -- musicom rules: chord-tone quantization + voice leading
# ---------------------------------------------------------------------------
def chord_tones_for_voice(bar, voice_idx):
    """The bar chord's tone set for one voice register (phase 2 helper)."""
    deg = CHORD_DEGREES[bar]
    ct_degrees = [(deg - 1 + q) % 7 + 1 for q in (0, 2, 4)]
    tones = []
    for ct in ct_degrees:
        tones.append(fold_to_register(degree_to_midi(ct), voice_idx))
    return tones


def quantize_to_chord_tone(raw01, bar, voice_idx):
    """Phase 2a: map a raw [0,1] pitch index to the nearest chord tone."""
    lo, hi = VOICES[voice_idx]["lo"], VOICES[voice_idx]["hi"]
    target = lo + raw01 * (hi - lo)
    best = min(chord_tones_for_voice(bar, voice_idx), key=lambda p: abs(p - target))
    return max(lo, min(hi, best))


def check_parallel_fifths_octaves(prev_chord, curr_chord):
    """Return list of (upper_voice_index, lower_voice_index, kind).

    Voice-order aware (S/A/T/B). Parallel motion requires both voices to
    move in the SAME direction by the SAME amount while preserving the
    interval class.
    """
    viols = []
    n = min(len(prev_chord), len(curr_chord))
    for i in range(n):
        for j in range(i + 1, n):
            iv1 = (prev_chord[j] - prev_chord[i]) % 12
            iv2 = (curr_chord[j] - curr_chord[i]) % 12
            m1 = curr_chord[i] - prev_chord[i]
            m2 = curr_chord[j] - prev_chord[j]
            same_dir = (m1 > 0 and m2 > 0) or (m1 < 0 and m2 < 0)
            if iv1 == 7 and iv2 == 7 and same_dir and m1 == m2:
                viols.append((j, i, "fifth"))
            if iv1 == 0 and iv2 == 0 and same_dir and m1 == m2:
                viols.append((j, i, "octave"))
    return viols


def _best_voicing(prev_chord, bar):
    """Search all chord-tone voicings of the bar's chord; pick the one that
    minimizes voice-leading distance from prev_chord and breaks parallel
    fifths/octaves. Bass is constrained to the chord ROOT.
    """
    per_voice = [chord_tones_for_voice(bar, vi) for vi in range(NUM_VOICES)]
    bass_root = fold_to_register(degree_to_midi(CHORD_DEGREES[bar]), 3)
    per_voice[3] = [bass_root]

    vlr = VoiceLeadingRules(style='classical')
    best = None
    best_cost = None
    for combo in itertools.product(*per_voice):
        cand = list(combo)
        if any(cand[i] <= cand[i + 1] for i in range(len(cand) - 1)):
            continue
        if any(cand[vi] < VOICES[vi]["lo"] or cand[vi] > VOICES[vi]["hi"]
               for vi in range(NUM_VOICES)):
            continue
        if check_parallel_fifths_octaves(prev_chord, cand):
            continue
        cost = vlr.calculate_voice_leading_distance(prev_chord, cand)
        if cand == prev_chord:
            cost += 8
        if best_cost is None or cost < best_cost:
            best_cost = cost
            best = cand
    if best is not None:
        return best
    # no candidate satisfies all constraints: least-bad (min distance)
    best = None
    best_cost = None
    for combo in itertools.product(*per_voice):
        cand = list(combo)
        if any(cand[i] <= cand[i + 1] for i in range(len(cand) - 1)):
            continue
        if any(cand[vi] < VOICES[vi]["lo"] or cand[vi] > VOICES[vi]["hi"]
               for vi in range(NUM_VOICES)):
            continue
        cost = vlr.calculate_voice_leading_distance(prev_chord, cand)
        if best_cost is None or cost < best_cost:
            best_cost = cost
            best = cand
    return best if best is not None else list(prev_chord)


def resolve_voice_leading(chords):
    """Phase 2b: global per-bar voicing search (Bass = root)."""
    fixed = [list(c) for c in chords]
    fixes = 0
    for bar in range(1, len(fixed)):
        new_voicing = _best_voicing(fixed[bar - 1], bar)
        if new_voicing != fixed[bar]:
            fixes += 1
        fixed[bar] = new_voicing
    return fixed, fixes


# ---------------------------------------------------------------------------
# Composition build
# ---------------------------------------------------------------------------
def build(rhythm_masks, chords):
    composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TICKS_PER_BEAT, beats_per_bar=BEATS_PER_BAR)
    composer.create_matrix(num_voices=NUM_VOICES, num_sections=NUM_BARS)
    for v in VOICES:
        composer.add_voice(v["name"], program=v["program"], channel=v["channel"])
    for b in range(NUM_BARS):
        composer.add_section("Bar%d" % (b + 1), bars=1)

    SUB_TICKS = BAR_TICKS // SUB  # 480 ticks per sixteenth-note
    for bar in range(NUM_BARS):
        mask = rhythm_masks[bar]
        for vi, v in enumerate(VOICES):
            events = []
            chord_pitch = chords[bar][vi]  # voiced chord tone (whole bar)
            for slot in range(SUB):
                if mask[slot]:
                    start = slot * SUB_TICKS
                    end = start + SUB_TICKS - 24   # slight articulation gap
                    events.append(MusicEvent(
                        pitch=chord_pitch, volume=96,
                        start_tick=start, end_tick=end,
                    ))
            # ZERO-DRIFT INVARIANT: every cell must span the full bar.
            # Pad each cell with a silent landmark event ending exactly at
            # BAR_TICKS so MusicUnit.len_ticks() == 1920 for every cell.
            last_end = max((e.end_tick for e in events), default=0)
            if last_end < BAR_TICKS:
                events.append(MusicEvent(
                    pitch=0, volume=0, start_tick=last_end, end_tick=BAR_TICKS,
                ))
            composer.set_unit(vi, bar, MusicUnit(events=events))
    return composer


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    project_dir = "/opt/data/projects/Styles/Experimental/062-brownian-chorale"
    midi_dir = os.path.join(project_dir, "MIDI")
    analysis_dir = os.path.join(project_dir, "Analysis")
    os.makedirs(midi_dir, exist_ok=True)
    os.makedirs(analysis_dir, exist_ok=True)

    print("=" * 68)
    print("PROJECT 062: REFLECTED BROWNIAN MOTION CHORALE (Method 048)")
    print("=" * 68)
    print("Key: %s | BPM: %d | Form: %d-bar chorale" % (KEY_NAME, BPM, NUM_BARS))
    print("Progression: %s" % " - ".join(ROMAN))
    print("Diffusion: sigma=%.2f, drift=%.2f, seed %d" % (SIGMA0, DRIFT_T, SEED))
    print()

    # ---- Phase 1: reflected Brownian motion (method 048)
    print("[Phase 1] Reflected Brownian walks -> raw pitch contours + rhythm...")
    rhythm_masks = brownian_rhythm_masks()
    print("Rhythm DNA masks (%d slots per bar, sixteenth grid):" % SUB)
    for bar in range(NUM_BARS):
        cells = "".join("\u2588" if b else "\u2591" for b in rhythm_masks[bar])
        print("  Bar %d %s: %s" % (bar + 1, ROMAN[bar].rjust(3), cells))
    raw_contours = {}
    for vi, v in enumerate(VOICES):
        raw_contours[v["name"]] = [
            raw_brownian_contour(bar, vi, sum(rhythm_masks[bar]))
            for bar in range(NUM_BARS)
        ]
    print("Raw contour samples (first 8, Soprano bar 1):",
          [round(x, 3) for x in raw_contours["Soprano"][0][:8]])
    print()

    # ---- Phase 2a: chord-tone quantization
    print("[Phase 2a] Quantize raw [0,1] contours to section chord tones...")
    chords = []
    for bar in range(NUM_BARS):
        chord = []
        for vi, v in enumerate(VOICES):
            contour = raw_contours[v["name"]][bar]
            # quantize each onset, keep the most common chord tone as the
            # bar's homophonic pitch (density-weighted)
            qs = [quantize_to_chord_tone(c, bar, vi) for c in contour]
            chord.append(max(set(qs), key=qs.count) if qs else
                         (chords[-1][vi] if chords else degree_to_midi(1)))
        chords.append(chord)
    print("Chord tones per bar (S/A/T/B):")
    for bar in range(NUM_BARS):
        print("  Bar %d %s: %s" % (bar + 1, ROMAN[bar].rjust(3), chords[bar]))
    print()

    # ---- Phase 2b: voice leading correction
    print("[Phase 2b] Voice leading rules (VoiceLeadingRules, classical)...")
    fixed, fixes = resolve_voice_leading(chords)
    print("Voice-leading corrections: %d" % fixes)
    vlr = VoiceLeadingRules(style='classical')
    total_violations = 0
    ranges = {v["name"]: (v["lo"], v["hi"]) for v in VOICES}
    for bar in range(1, NUM_BARS):
        viols = vlr.check_parallel_motion(fixed[bar - 1], fixed[bar])
        total_violations += len(viols)
    for bar in range(NUM_BARS):
        for vi, vname in enumerate([v["name"] for v in VOICES]):
            rv = vlr.validate_voice_ranges([fixed[bar][vi]], {vname: ranges[vname]})
            total_violations += len(rv)
    print("Residual violations after correction: %d" % total_violations)
    print()

    # ---- Phase 3: UnitMatrix
    print("[Phase 3] Build UnitMatrix...")
    composer = build(rhythm_masks, fixed)
    ok, msg = composer.validate()
    print("Zero-drift validation: %s (%s)" % ("PASS" if ok else "FAIL", msg))
    if not ok:
        print("ERROR: %s" % msg)
        sys.exit(1)
    print("Track length: %d ticks = %.1f bars" % (
        composer.get_track_length_ticks(), composer.get_track_length_bars()))
    print()

    # ---- Phase 4: export MIDI
    print("[Phase 4] Export MIDI...")
    midi_path = os.path.join(midi_dir, "062-brownian-chorale.mid")
    composer.to_midi(midi_path)
    fsize = os.path.getsize(midi_path)
    assert fsize > 40, "MIDI too small: %d bytes" % fsize
    print("MIDI: %s (%d bytes)" % (midi_path, fsize))

    # ---- Phase 5: grid visualization
    print("[Phase 5] Grid visualization...")
    grid_path = os.path.join(analysis_dir, "grid_visualization.txt")
    write_grid_visualization(
        composer.matrix, grid_path,
        ticks_per_character=120,
        voice_names=[v["name"] for v in VOICES],
        bpm=BPM,
        mode="C aeolian (Reflected Brownian Motion, Method 048)",
    )
    print("Grid: %s" % grid_path)

    # ---- Phase 6: provenance
    print("[Phase 6] Provenance...")
    prov_path = write_provenance(
        artifact_path=midi_path,
        classification=AI_GENERATED,
        generator="Reflected Brownian Motion Pitch Diffusion (RBMPD) -- Method 048",
        sources=["Research/CompositionMethods/methods_db.md:Method 048",
                 "rules/voice_leading.py:VoiceLeadingRules",
                 "rules/progression.py:Scale7ChordDegree",
                 "utilities/constants.py:SCALE_PATTERNS"],
        parameters={
            "bpm": BPM,
            "key": KEY_NAME,
            "progression": ROMAN,
            "chord_degrees": CHORD_DEGREES,
            "diffusion": {"model": "reflected Brownian motion",
                          "sigma": SIGMA0, "drift": DRIFT_T,
                          "barriers": "voice register limits",
                          "reflection": "elastic mirror (2*barrier - X)"},
            "rhythm": {"grid": "sixteenth notes", "threshold": THETA,
                       "density_floor": DENSITY_FLOOR,
                       "anchors": ["downbeat"],
                       "masks": rhythm_masks},
            "seed": SEED,
            "voices": [v["name"] for v in VOICES],
            "bars": NUM_BARS,
            "voice_leading_fixes": fixes,
            "residual_violations": total_violations,
        },
        notes="Two-phase architecture: reflected Brownian motion pitch "
              "diffusion (per-voice register barriers, tonic drift) -> raw "
              "pitch contours + walk-speed rhythm (Phase 1); chord-tone "
              "quantization + classical voice leading rules (Phase 2).",
    )
    print("Provenance: %s" % prov_path)

    # ---- Report
    print()
    print("=" * 68)
    print("COMPOSITION COMPLETE")
    print("=" * 68)
    print("Project : 062-brownian-chorale")
    print("Method  : 048 - Reflected Brownian Motion Pitch Diffusion")
    print("Voices  : %s" % ", ".join(v["name"] for v in VOICES))
    print("Form    : %d bars, %s (%s)" % (NUM_BARS, KEY_NAME, " - ".join(ROMAN)))
    print("MIDI    : %s" % midi_path)
    print("Grid    : %s" % grid_path)
    print("Prov    : %s" % prov_path)
    print("=" * 68)
    return midi_path


if __name__ == "__main__":
    main()
