#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project 061: Strange Attractor Trajectory Mapping Chorale (Method 043)

Composition method : SATM (Method 043, nature-led deterministic chaos)
  Phase 1 (generative draft) : Lorenz strange attractor trajectory
    - 4th-order Runge-Kutta (RK4) integration of the Lorenz system
      (sigma=10, rho=28, beta=8/3) from a seed near the unstable fixed
      point, transient discarded, per-voice coordinate mappings
      (z -> Soprano, x -> Alto, y -> Tenor, z-24 -> Bass)
    - event onsets triggered by trajectory speed above a threshold
    - raw pitches: attractor coordinates -> [0,1] -> MIDI range
  Phase 2 (musicom rules post-processing):
    - harmonic framework: E dorian (SCALE_PATTERNS), progression
      i-ii-IV-VI built via Scale7ChordDegree.get_diatonic_note
      (canonical helper, no off-by-octave %7 wrappers)
    - quantize raw pitches to chord tones of the active section chord
    - voice leading: VoiceLeadingRules (rules/voice_leading.py,
      classical) -- parallel fifth/octave scan + nearest-diatonic
      correction + exhaustive voicing search (Bass = root)
    - validate_voice_ranges for the 4-voice chorale register

Engine: UnitMatrixComposer workflow (zero-drift gate -> to_midi)
Form  : 8 bars, 4 voices (Soprano/Alto/Tenor/Bass), homophonic chorale
Key   : E dorian (root 52 = E3), 4 eighth-notes per bar rhythm DNA
"""
import os
import sys
import random
import itertools
import numpy as np

from structures import MusicUnit, MusicEvent, MidiInstrument
from workflows.unitmatrix_composer import (
    UnitMatrixComposer, create_note_unit,
)
from rules.voice_leading import VoiceLeadingRules
from rules.progression import Scale7ChordDegree
from utilities.constants import SCALE_PATTERNS
from visualization.grid import write_grid_visualization
from workflows.provenance import write_provenance, AI_GENERATED

# ---------------------------------------------------------------------------
# Parameters
# ---------------------------------------------------------------------------
BPM = 92
TICKS_PER_BEAT = 480
BEATS_PER_BAR = 4
BAR_TICKS = TICKS_PER_BEAT * BEATS_PER_BAR   # 1920
NUM_BARS = 8
NUM_VOICES = 4
SUB = 2                                       # eighth-note rhythm grid

KEY_ROOT = 52          # E3
KEY_NAME = "E dorian"
SCALE_INTERVALS = SCALE_PATTERNS['dorian']    # [0,2,3,5,7,9,10]

# Chord plan: scale degrees (1-indexed) per bar, dorian modal gravity
CHORD_DEGREES = [1, 2, 4, 6, 1, 2, 4, 1]
ROMAN = ["i", "ii", "IV", "VI", "i", "ii", "IV", "i"]

VOICES = [
    {"name": "Soprano", "program": MidiInstrument.FLUTE, "channel": 0, "lo": 62, "hi": 84},
    {"name": "Alto",    "program": MidiInstrument.FLUTE, "channel": 1, "lo": 53, "hi": 74},
    {"name": "Tenor",   "program": MidiInstrument.FLUTE, "channel": 2, "lo": 48, "hi": 65},
    {"name": "Bass",    "program": MidiInstrument.BASS,  "channel": 3, "lo": 38, "hi": 55},
]

SEED = 2201
random.seed(SEED)
np.random.seed(SEED)

# ---------------------------------------------------------------------------
# Phase 1 -- Lorenz strange attractor (RK4), method 043
# ---------------------------------------------------------------------------
LORENZ_SIGMA = 10.0
LORENZ_RHO = 28.0
LORENZ_BETA = 8.0 / 3.0


def lorenz_deriv(state):
    """Lorenz system derivative (sigma=10, rho=28, beta=8/3)."""
    x, y, z = state
    return np.array([
        LORENZ_SIGMA * (y - x),
        x * (LORENZ_RHO - z) - y,
        x * y - LORENZ_BETA * z,
    ])


def rk4_step(state, h):
    """One 4th-order Runge-Kutta integration step."""
    k1 = lorenz_deriv(state)
    k2 = lorenz_deriv(state + 0.5 * h * k1)
    k3 = lorenz_deriv(state + 0.5 * h * k2)
    k4 = lorenz_deriv(state + h * k3)
    return state + (h / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)


def integrate_lorenz(steps, h=0.01, x0=1.0, y0=1.0, z0=1.0):
    """Integrate the Lorenz system for `steps` RK4 steps.

    Returns (N,3) trajectory. Warm-up transient (first 2000 steps) is
    discarded so the path has settled onto the attractor.
    """
    state = np.array([x0, y0, z0], dtype=float)
    traj = []
    for i in range(steps):
        state = rk4_step(state, h)
        if i >= 2000:                 # discard transient
            traj.append(state.copy())
    return np.array(traj)


def normalize(coord):
    """Min-max normalize a coordinate stream to [0,1] (guard zero range)."""
    lo, hi = coord.min(), coord.max()
    if hi - lo < 1e-12:
        return np.zeros_like(coord)
    return (coord - lo) / (hi - lo)


def attractor_raw_pitch_contour(section_idx, voice_idx, n_onsets):
    """Phase-1 raw material: attractor coordinate -> [0,1] pitch contour.

    One continuous Lorenz trajectory (seeded deterministically) is
    integrated once; each voice reads a different coordinate stream
    (z / x / y / z-24), normalized to [0,1], then sub-sampled to the
    onset grid of its section. Returns a list of raw floats in [0,1].
    """
    # 8 bars * 8 eighth-notes + margin, per-section slice stride
    TRAJ_LEN = 4096
    traj = integrate_lorenz(TRAJ_LEN)
    streams = {
        "Soprano": normalize(traj[:, 2]),
        "Alto":    normalize(traj[:, 0]),
        "Tenor":   normalize(traj[:, 1]),
        "Bass":    normalize(traj[:, 2]),
    }
    vname = VOICES[voice_idx]["name"]
    s = streams[vname]
    n = len(s)
    # per-section phase offset + fixed stride -> deterministically varied
    # but attractor-coherent raw contours per section
    phase = (section_idx * 397 + voice_idx * 211) % n
    stride = max(1, n // (NUM_BARS * 8))
    idxs = [(phase + k * stride) % n for k in range(n_onsets)]
    return [float(s[i]) for i in idxs]


# ---------------------------------------------------------------------------
# Diatonic helpers (canonical Scale7ChordDegree only -- no local %7 wrappers)
# ---------------------------------------------------------------------------
def degree_to_midi(degree: int, base_midi: int = KEY_ROOT) -> int:
    """1-indexed scale degree -> absolute MIDI pitch (canonical helper)."""
    return Scale7ChordDegree.get_diatonic_note(KEY_ROOT, SCALE_INTERVALS, degree - 1)


def fold_to_register(midi: int, voice_idx: int) -> int:
    """Fold an absolute pitch into the voice's register (nearest octave)."""
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
def chord_tones_for_voice(bar: int, voice_idx: int) -> list:
    """The section chord's tone set for one voice register (phase 2 helper)."""
    deg = CHORD_DEGREES[bar]
    ct_degrees = [(deg - 1 + q) % 7 + 1 for q in (0, 2, 4)]
    tones = []
    for ct in ct_degrees:
        p = degree_to_midi(ct)
        tones.append(fold_to_register(p, voice_idx))
    return tones


def quantize_to_chord_tone(raw01: float, bar: int, voice_idx: int) -> int:
    """Phase 2a: map a raw [0,1] pitch index to the nearest chord tone.

    Chord tones = root + quality intervals over the diatonic scale, built
    from the KEY tonic via the canonical Scale7ChordDegree helper (no local
    %7 wrappers), then folded into the voice register.
    """
    lo, hi = VOICES[voice_idx]["lo"], VOICES[voice_idx]["hi"]
    target = lo + raw01 * (hi - lo)
    best = min(chord_tones_for_voice(bar, voice_idx), key=lambda p: abs(p - target))
    return max(lo, min(hi, best))


def check_parallel_fifths_octaves(prev_chord: list, curr_chord: list) -> list:
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
                viols.append((j, i, 'fifth'))
            if iv1 == 0 and iv2 == 0 and same_dir and m1 == m2:
                viols.append((j, i, 'octave'))
    return viols


def _best_voicing(prev_chord: list, bar: int) -> list:
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


def resolve_voice_leading(chords: list) -> tuple:
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
# Rhythm: attractor-speed triggers -> eighth-note grid (per-bar binary mask)
# ---------------------------------------------------------------------------
def attractor_rhythm_masks() -> list:
    """Per-bar binary rhythm masks (8 eighth-note slots) from trajectory speed.

    Velocity threshold theta=0.45; each bar's 8-slot mask is derived from
    the same deterministic Lorenz trajectory (speed profile), then snapped
    to the metric grid. The first slot of each bar is forced ON for
    metrical gravity.
    """
    traj = integrate_lorenz(4096)
    d = np.diff(traj, axis=0)
    speed = np.sqrt((d ** 2).sum(axis=1))
    speed_norm = (speed - speed.min()) / (speed.max() - speed.min() + 1e-12)
    n = len(speed_norm)
    masks = []
    for bar in range(NUM_BARS):
        seg = speed_norm[bar * 400:(bar + 1) * 400]
        if len(seg) < 8:
            seg = speed_norm[:8]
        idxs = np.linspace(0, len(seg) - 1, 8).astype(int)
        vals = np.array([seg[i] for i in idxs])
        # lower threshold + density floor: keeps attractor character but
        # avoids near-empty bars
        mask = [1 if v > 0.30 else 0 for v in vals]
        mask[0] = 1            # metrical gravity anchor (downbeat)
        mask[-1] = 1           # bar-end anchor: keeps grid flowing into
                               # the next bar (no mid-bar drift gaps)
        if sum(mask) < 3:      # density floor: at least 3 onsets per bar
            # add the 2 highest-energy remaining slots
            order = sorted(range(1, 7), key=lambda i: -vals[i])
            for i in order:
                if sum(mask) >= 3:
                    break
                mask[i] = 1
        masks.append(mask)
    return masks


# ---------------------------------------------------------------------------
# Composition build
# ---------------------------------------------------------------------------
def build(rhythm_masks: list, chords: list) -> UnitMatrixComposer:
    composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TICKS_PER_BEAT, beats_per_bar=BEATS_PER_BAR)
    composer.create_matrix(num_voices=NUM_VOICES, num_sections=NUM_BARS)
    for v in VOICES:
        composer.add_voice(v["name"], program=v["program"], channel=v["channel"])
    for b in range(NUM_BARS):
        composer.add_section(f"Bar{b+1}", bars=1)

    SUB_TICKS = BAR_TICKS // 8  # 240 ticks per eighth-note
    for bar in range(NUM_BARS):
        mask = rhythm_masks[bar]
        for vi, v in enumerate(VOICES):
            events = []
            chord_pitch = chords[bar][vi]  # voiced chord tone (whole bar)
            for slot in range(8):
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
    project_dir = "/opt/data/projects/Styles/Experimental/061-attractor-chorale"
    midi_dir = os.path.join(project_dir, "MIDI")
    analysis_dir = os.path.join(project_dir, "Analysis")
    os.makedirs(midi_dir, exist_ok=True)
    os.makedirs(analysis_dir, exist_ok=True)

    print("=" * 68)
    print("PROJECT 061: STRANGE ATTRACTOR TRAJECTORY CHORALE (Method 043)")
    print("=" * 68)
    print(f"Key: {KEY_NAME} | BPM: {BPM} | Form: {NUM_BARS}-bar chorale")
    print(f"Progression: {' - '.join(ROMAN)}")
    print(f"Attractor: Lorenz (sigma=10, rho=28, beta=8/3), RK4, seed {SEED}")
    print()

    # ---- Phase 1: attractor trajectory (method 043)
    print("[Phase 1] Lorenz trajectory (RK4) -> raw pitch contours + rhythm...")
    rhythm_masks = attractor_rhythm_masks()
    print("Rhythm DNA masks (8 eighth-note slots per bar):")
    for bar in range(NUM_BARS):
        cells = "".join("█" if b else "░" for b in rhythm_masks[bar])
        print(f"  Bar {bar+1} {ROMAN[bar]:>3}: {cells}")
    raw_contours = {}
    for vi, v in enumerate(VOICES):
        raw_contours[v["name"]] = [
            attractor_raw_pitch_contour(bar, vi, sum(rhythm_masks[bar]))
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
            chord.append(max(set(qs), key=qs.count) if qs else chords[-1][vi] if chords else degree_to_midi(1))
        chords.append(chord)
    print("Chord tones per bar (S/A/T/B):")
    for bar in range(NUM_BARS):
        print(f"  Bar {bar+1} {ROMAN[bar]:>3}: {chords[bar]}")
    print()

    # ---- Phase 2b: voice leading correction
    print("[Phase 2b] Voice leading rules (VoiceLeadingRules, classical)...")
    fixed, fixes = resolve_voice_leading(chords)
    print(f"Voice-leading corrections: {fixes}")
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
    print(f"Residual violations after correction: {total_violations}")
    print()

    # ---- Phase 3: UnitMatrix
    print("[Phase 3] Build UnitMatrix...")
    composer = build(rhythm_masks, fixed)
    ok, msg = composer.validate()
    print(f"Zero-drift validation: {'PASS' if ok else 'FAIL'} ({msg})")
    if not ok:
        print(f"ERROR: {msg}")
        sys.exit(1)
    print(f"Track length: {composer.get_track_length_ticks()} ticks = {composer.get_track_length_bars():.1f} bars")
    print()

    # ---- Phase 4: export MIDI
    print("[Phase 4] Export MIDI...")
    midi_path = os.path.join(midi_dir, "061-attractor-chorale.mid")
    composer.to_midi(midi_path)
    fsize = os.path.getsize(midi_path)
    assert fsize > 40, f"MIDI too small: {fsize} bytes"
    print(f"MIDI: {midi_path} ({fsize} bytes)")

    # ---- Phase 5: grid visualization
    print("[Phase 5] Grid visualization...")
    grid_path = os.path.join(analysis_dir, "grid_visualization.txt")
    write_grid_visualization(
        composer.matrix, grid_path,
        ticks_per_character=120,
        voice_names=[v["name"] for v in VOICES],
        bpm=BPM,
        mode="E dorian (Lorenz attractor, Method 043)",
    )
    print(f"Grid: {grid_path}")

    # ---- Phase 6: provenance
    print("[Phase 6] Provenance...")
    prov_path = write_provenance(
        artifact_path=midi_path,
        classification=AI_GENERATED,
        generator="Strange Attractor Trajectory Mapping (Lorenz, RK4) -- Method 043",
        sources=["Research/CompositionMethods/method_043_satm.md",
                 "rules/voice_leading.py:VoiceLeadingRules",
                 "rules/progression.py:Scale7ChordDegree",
                 "utilities/constants.py:SCALE_PATTERNS"],
        parameters={
            "bpm": BPM,
            "key": KEY_NAME,
            "progression": ROMAN,
            "chord_degrees": CHORD_DEGREES,
            "attractor": {"system": "Lorenz", "sigma": LORENZ_SIGMA,
                          "rho": LORENZ_RHO, "beta": LORENZ_BETA,
                          "integrator": "RK4", "h": 0.01,
                          "transient_discard": 2000},
            "coordinate_mapping": {"Soprano": "z", "Alto": "x",
                                   "Tenor": "y", "Bass": "z-24"},
            "rhythm": {"grid": "eighth notes", "threshold": 0.30,
                       "density_floor": 3, "anchors": ["downbeat", "bar-end"],
                       "masks": rhythm_masks},
            "seed": SEED,
            "voices": [v["name"] for v in VOICES],
            "bars": NUM_BARS,
            "voice_leading_fixes": fixes,
            "residual_violations": total_violations,
        },
        notes="Two-phase architecture: Lorenz strange attractor trajectory "
              "(RK4) -> raw pitch contours + speed-triggered rhythm (Phase 1); "
              "chord-tone quantization + classical voice leading rules (Phase 2).",
    )
    print(f"Provenance: {prov_path}")

    # ---- Report
    print()
    print("=" * 68)
    print("COMPOSITION COMPLETE")
    print("=" * 68)
    print(f"Project : 061-attractor-chorale")
    print(f"Method  : 043 - Strange Attractor Trajectory Mapping (Lorenz)")
    print(f"Voices  : {', '.join(v['name'] for v in VOICES)}")
    print(f"Form    : {NUM_BARS} bars, {KEY_NAME} (i-ii-IV-VI-i-ii-IV-i)")
    print(f"Fixes   : {fixes} voice-leading corrections")
    print(f"MIDI    : {midi_path}")
    print(f"Grid    : {grid_path}")
    print(f"Provenance: {prov_path}")
    print("=" * 68)

    print("\nFinal pitches (S/A/T/B):")
    for bar in range(NUM_BARS):
        print(f"  Bar {bar+1}: {fixed[bar]}")
    return midi_path


if __name__ == "__main__":
    main()
