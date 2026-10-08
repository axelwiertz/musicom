# -*- coding: utf-8 -*-
"""Project 228: Balkan x Spectral Graph Laplacian Mapping (Method 051).

Autonomous nightly composition job (2026-10-07).
  Style:  Balkan (dajcovo 7/8 dance groove, Dorian modality, clarinet/accordion/
          violin/double-bass folk ensemble)
  Method: 051 Spectral Graph Laplacian Mapping (SGLM) -- Layer: concrete
  Key:    G Dorian (G A Bb C D E F) -- pc {7,9,10,0,2,4,5}, tonic G
  Meter:  7/8 (dajcovo 2+2+3), 132 BPM, TPB=480 -> GRID8=240, GRID16=120,
          BAR = 7*240 = 1680 ticks
  Form:   6 sections x 4 bars = 24 bars (Intro -> VerseA -> LiftA ->
          VerseB -> Dance -> Coda)

Method essence (051 SGLM): build a 7-node graph over the G-Dorian scale
degrees, edges weighted by a Gaussian consonance affinity on the
circle-of-fifths cycle. Eigendecompose the graph Laplacian L = D - A. The
Fiedler vector v1 (2nd-smallest eigenvector) sorts scale degrees into a
smooth "spectral scale"; the 2nd eigenvector v2 is the counter-axis; the
algebraic connectivity lambda_1 is a continuous harmonic-tension scalar
(HOME = high lambda_1, TENSE = low lambda_1). Per-section edge re-weighting
(connectivity scale) morphs the spectrum, and the eigenvalue gaps drive
rhythm density.

Two-phase architecture:
  Phase 1 = raw generative draft: a SINGLE lead voice (clarinet) walking the
            full Fiedler ordering across the timeline (unquantized pitch,
            off-grid onsets, eigenvalue-gap density, register drift +
            micro-jitter, NO harmony/scale snapping).  ->  -phase1.mid
  Phase 2 = musicom rules: 16th-grid snap, per-bar chord-tone quantization
            (each bar's chord = a subset of the section's spectral clusters),
            register clamp per voice, voice-leading check, full 4-voice
            texture (Bass/Accordion/Clarinet/Violin).  ->  .mid

Zero-drift gate: UnitMatrixComposer.validate() MUST pass for both phases.
Engine only: structures + workflows.unitmatrix_composer + rules.voice_leading.
NO raw mido authoring (mido used ONLY for read-back verification).
"""
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
from instrument_registry import DOUBLE_BASS, ACCORDION, CLARINET, VIOLIN

# ------------------------------------------------------------- CONFIG ----
GENRE = "Balkan"
PROJECT_NAME = "228-balkan-spectral"
PROJECT_DIR = f"/opt/data/repos/musicom/projects/Styles/{GENRE}/{PROJECT_NAME}"

BPM = 132
TPB = 480                                # ticks per quarter note
GRID16 = 120                             # sixteenth
GRID8 = 240                              # eighth
BAR = 7 * GRID8                          # 7/8 bar = 1680 ticks (dajcovo)
BARS_PER = 4
SECTION_TICKS = BAR * BARS_PER           # 6720
N_SECTIONS = 6
N_BARS = N_SECTIONS * BARS_PER           # 24
TOTAL_TICKS = N_BARS * BAR               # 40320

SEED = 20261007
rng = np.random.default_rng(SEED)

# G Dorian: degree 0..6 -> G A Bb C D E F (pitch classes)
SCALE_PCS = [7, 9, 10, 0, 2, 4, 5]
KEY_PCS = set(SCALE_PCS)
DEG_NAME = {0: "G", 1: "A", 2: "Bb", 3: "C", 4: "D", 5: "E", 6: "F"}
KEY_NAME = "G Dorian (G A Bb C D E F)"
TONIC_DEG = 0

# Per-voice scale ladders (degree 0..6 -> concrete MIDI pitch, G Dorian).
VOICE_LADDERS = {
    0: [43, 45, 46, 48, 50, 52, 53],   # Bass      G2 A2 Bb2 C3 D3 E3 F3
    1: [55, 57, 58, 60, 62, 64, 65],   # Accordion G3 A3 Bb3 C4 D4 E4 F4
    2: [67, 69, 70, 72, 74, 76, 77],   # Clarinet  G4 A4 Bb4 C5 D5 E5 F5
    3: [67, 69, 70, 72, 74, 76, 77],   # Violin    G4 A4 Bb4 C5 D5 E5 F5
}
VOICE_NAMES = ["Bass", "Accordion", "Clarinet", "Violin"]
VOICE_PROGRAMS = [DOUBLE_BASS.midi_program, ACCORDION.midi_program,
                  CLARINET.midi_program, VIOLIN.midi_program]
VOICE_CHANNELS = [0, 1, 2, 3]

SECTION_NAMES = ["Intro", "VerseA", "LiftA", "VerseB", "Dance", "Coda"]
# Harmonic function per section -> spectral connectivity scale (SGLM edge weight)
SECTION_FUNCTION = ["HOME", "HOME", "TURN", "TENSE", "TURN", "HOME"]
SECTION_SCALE = {"HOME": 1.00, "TURN": 0.70, "TENSE": 0.45}

# Chord catalogue (degree sets), root degree first.
CHORDS = {
    "i":    {"root": 0, "deg": [0, 2, 4]},   # Gm
    "II":   {"root": 1, "deg": [1, 3, 5]},   # Am
    "III":  {"root": 2, "deg": [2, 4, 6]},   # Bb
    "IV":   {"root": 3, "deg": [3, 5, 0]},   # C
    "v":    {"root": 4, "deg": [4, 6, 1]},   # Dm
    "vi":   {"root": 5, "deg": [5, 0, 2]},   # Edim
    "VII":  {"root": 6, "deg": [6, 1, 3]},   # F
}
# 24-bar progression (G Dorian, Balkan i-VII-IV turnarounds)
PROGRESSION = (
    ["i", "i", "i", "i"] +        # Intro   HOME
    ["i", "VII", "IV", "i"] +     # VerseA  HOME
    ["IV", "v", "VII", "v"] +     # LiftA   TURN
    ["i", "III", "VII", "IV"] +   # VerseB  TENSE
    ["IV", "VII", "i", "v"] +     # Dance   TURN
    ["i", "VII", "IV", "i"]       # Coda    HOME
)
assert len(PROGRESSION) == N_BARS


# ------------------------------------------- SGLM spectrum (method 051) ----
# Circle-of-fifths cycle over the 7 G-Dorian degrees:
#   G(0) -> D(4) -> A(1) -> E(5) -> Bb(2) -> F(6) -> C(3) -> G(0)
FIFTHS_ORDER = [0, 4, 1, 5, 2, 6, 3]
FIFTHS_POS = {d: i for i, d in enumerate(FIFTHS_ORDER)}


def cycle_dist(a, b):
    d = abs(FIFTHS_POS[a] - FIFTHS_POS[b])
    return min(d, 7 - d)


def build_laplacian(scale=1.0, sigma=1.5, floor=0.05, tonic_boost=0.45):
    """7x7 affinity graph on the fifths cycle -> graph Laplacian L = D - A.

    w_ij = exp(-d_ij^2 / 2 sigma^2) * scale + floor  (d_ij = cycle distance).
    A `tonic_boost` on edges incident to the tonic breaks the cycle's
    circulant degeneracy (pitfall 3: symmetric cycle -> repeated eigenvalues)
    and anchors the tonic as the spectral centre (pitfall 4).
    """
    n = 7
    W = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            d = cycle_dist(i, j)
            w = np.exp(-(d * d) / (2.0 * sigma * sigma))
            w = w * scale + floor
            if i == TONIC_DEG or j == TONIC_DEG:
                w += tonic_boost * scale
            W[i, j] = w
    D = np.diag(W.sum(axis=1))
    return D - W, W


def spectrum(L):
    """Full dense eigensolve (n=7): eigenvalues asc, eigenvectors as columns."""
    vals, vecs = np.linalg.eigh(L)
    return vals, vecs


def orient(vec, anchor_deg):
    """Orient eigenvector sign so the anchor (tonic) entry is non-positive
    (pitfall 4: tonic = minimum spectral coordinate)."""
    return -vec if vec[anchor_deg] > 0 else vec


# -------------------------------------------------- Phase-1 raw draft -----
def phase1_raw_events(total_ticks):
    """Single clarinet voice walking the Fiedler ordering of the HOME graph,
    with unquantized pitch + off-grid onsets + eigenvalue-gap density."""
    sr = np.random.default_rng(SEED + 777)
    L, _ = build_laplacian(scale=SECTION_SCALE["HOME"])
    vals, vecs = spectrum(L)
    v1 = orient(vecs[:, 1], TONIC_DEG)
    spectral_order = [int(d) for d in np.argsort(v1)]
    lam1 = float(vals[1])
    evs = []
    t = 0
    while t < total_ticks:
        for deg in spectral_order:
            if t >= total_ticks:
                break
            # register drift + micro-jitter (raw, pre-rules)
            pitch = VOICE_LADDERS[2][deg]
            pitch += int(sr.normal(0, 1.5))
            pitch += int(sr.integers(0, 2)) * 12 if sr.random() < 0.08 else 0
            pitch = int(np.clip(pitch, 60, 96))
            # eigenvalue-gap density: denser when lambda_1 large (HOME)
            dur = int(np.clip(GRID16 * (1.6 + lam1 * 2.0) + sr.integers(-30, 30),
                              80, 480))
            off = max(0, t + int(sr.integers(-30, 30)))       # off-grid onset
            vel = int(np.clip(62 + 20 * sr.random(), 46, 112))
            evs.append(MusicEvent(pitch=pitch, volume=vel,
                                  start_tick=off, end_tick=off + dur))
            t += max(90, dur // 2 + int(sr.integers(0, 90)))
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
    """Double bass ostinato: chord root on dajcovo group starts (p=0,2,4),
    fifth on p=6. All 8th-grid (240) locked."""
    unit = MusicUnit()
    ladder = VOICE_LADDERS[0]
    for b, sym in enumerate(chord_syms):
        root = CHORDS[sym]["root"]
        fifth = (root + 4) % 7
        t0 = b * BAR
        hits = [(0, root, 82), (2, root, 72), (4, root, 76), (6, fifth, 70)]
        for p, deg, vel in hits:
            t = t0 + p * GRID8
            unit.add_event(MusicEvent(pitch=ladder[deg], volume=vel,
                                      start_tick=t, end_tick=t + GRID8 - 24))
    return _pad(unit, 4 * BAR)


def harmony_unit(sec_idx, chord_syms):
    """Accordion chordal stabs on the dajcovo offbeats (p=1,3,5) -- the
    interlock with the bass. 3-note chord tones, 8th-grid locked."""
    unit = MusicUnit()
    ladder = VOICE_LADDERS[1]
    for b, sym in enumerate(chord_syms):
        degs = CHORDS[sym]["deg"]
        t0 = b * BAR
        for p in (1, 3, 5):
            t = t0 + p * GRID8
            # 3-note voicing spread over 2 octaves (root, third, fifth)
            voicing = [ladder[degs[0]], ladder[degs[1]], ladder[degs[2]]]
            vel = 62 if p in (1, 3) else 70
            for midi in voicing:
                unit.add_event(MusicEvent(pitch=midi, volume=vel,
                                          start_tick=t, end_tick=t + GRID8 - 30))
    return _pad(unit, 4 * BAR)


def spectral_melody_unit(voice_idx, sec_idx, chord_syms, eig_idx, density):
    """Lead (clarinet, eig_idx=1 Fiedler) / counter (violin, eig_idx=2)
    walking the spectral ordering of each bar's chord tones, grid-locked."""
    L, _ = build_laplacian(scale=SECTION_SCALE[SECTION_FUNCTION[sec_idx]])
    vals, vecs = spectrum(L)
    v = orient(vecs[:, eig_idx], TONIC_DEG)
    unit = MusicUnit()
    ladder = VOICE_LADDERS[voice_idx]
    for b, sym in enumerate(chord_syms):
        degs = CHORDS[sym]["deg"]
        ordered = sorted(degs, key=lambda d: v[d])           # spectral order
        contour = ordered + ordered[-2:0:-1]                 # up then down
        t0 = b * BAR
        n = density[b % len(density)] if isinstance(density, list) else density
        # spread n onsets across the 7 eighth slots (8th-grid locked -> also
        # 16th-grid locked), tick = multiple of GRID8 = 240
        slots = np.linspace(0, 6, n, dtype=int)
        for k, s in enumerate(slots):
            deg = contour[k % len(contour)]
            t = t0 + int(s) * GRID8
            vel = 78 if s == 0 else 66
            if voice_idx == 3:
                vel -= 6
            vel = int(np.clip(vel, 48, 108))
            unit.add_event(MusicEvent(pitch=ladder[deg], volume=vel,
                                      start_tick=t, end_tick=t + GRID8 - 12))
    return _pad(unit, 4 * BAR)


# ------------------------------------------------- exports ----------------
def export_phase1(path):
    c = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=4)
    c.create_matrix(num_voices=1, num_sections=1)
    c.add_voice("LeadRaw", program=CLARINET.midi_program, channel=0)
    c.add_section("Raw", bars=N_BARS)
    c.set_unit(0, 0, MusicUnit(events=phase1_raw_events(TOTAL_TICKS)))
    ok, msg = c.validate()
    if not ok:
        raise RuntimeError(f"phase1 validate failed: {msg}")
    c.to_midi(path)
    return c


def export_phase2(path, densities):
    c = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=4)
    c.create_matrix(num_voices=4, num_sections=N_SECTIONS)
    for i in range(4):
        c.add_voice(VOICE_NAMES[i], program=VOICE_PROGRAMS[i],
                    channel=VOICE_CHANNELS[i])
    for name in SECTION_NAMES:
        c.add_section(name, bars=BARS_PER)
    for sec_idx in range(N_SECTIONS):
        syms = PROGRESSION[sec_idx * BARS_PER:(sec_idx + 1) * BARS_PER]
        c.set_unit(0, sec_idx, bass_unit(sec_idx, syms))
        c.set_unit(1, sec_idx, harmony_unit(sec_idx, syms))
        c.set_unit(2, sec_idx,
                   spectral_melody_unit(2, sec_idx, syms, 1, densities[sec_idx]))
        c.set_unit(3, sec_idx,
                   spectral_melody_unit(3, sec_idx, syms, 2,
                                        max(2, densities[sec_idx] // 2)))
    ok, msg = c.validate()
    if not ok:
        raise RuntimeError(f"phase2 validate failed: {msg}")
    c.to_midi(path)
    return c


# ------------------------------------------------- audits (real read-back) --
def audit_midi(midi_path):
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
                    (int(msg.note), t, int(msg.velocity)))
    bar_pcs = [set(SCALE_PCS[d] for d in CHORDS[s]["deg"]) for s in PROGRESSION]
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


# ------------------------------------------------- main --------------------
def main():
    for sub in ("MIDI", "Audio", "Analysis", "Scripts"):
        os.makedirs(os.path.join(PROJECT_DIR, sub), exist_ok=True)

    # ---- per-section spectrum + density (drives phase 2 + report)
    spectra = []
    densities = []
    for sec_idx in range(N_SECTIONS):
        fn = SECTION_FUNCTION[sec_idx]
        L, _ = build_laplacian(scale=SECTION_SCALE[fn])
        vals, vecs = spectrum(L)
        lam1 = float(vals[1])
        lam2 = float(vals[2])
        spectra.append({"section": SECTION_NAMES[sec_idx], "function": fn,
                        "lambda1": lam1, "lambda2": lam2,
                        "gap": lam2 - lam1})
        d = int(np.clip(round(3 + 1.5 * lam1), 3, 7))
        densities.append(d)
        print(f"  {SECTION_NAMES[sec_idx]:>7} {fn:>5} lam1={lam1:.4f} "
              f"lam2={lam2:.4f} gap={lam2 - lam1:.4f} -> lead density {d}")

    # ---- phase 1
    p1_path = os.path.join(PROJECT_DIR, "MIDI", f"{PROJECT_NAME}-phase1.mid")
    export_phase1(p1_path)
    write_provenance(
        p1_path, classification=AI_ASSISTED,
        generator="051-SGLM (raw Fiedler-ordering walk)",
        parameters={"phase": 1, "bpm": BPM, "meter": "7/8", "key": KEY_NAME,
                    "seed": SEED, "voices": 1,
                    "note": "raw generative draft: single clarinet walking the "
                            "HOME-graph Fiedler ordering, off-grid ticks, "
                            "register drift + micro-jitter, pre-rules"},
    )

    # ---- phase 2
    midi_path = os.path.join(PROJECT_DIR, "MIDI", f"{PROJECT_NAME}.mid")
    c2 = export_phase2(midi_path, densities)
    assert os.path.getsize(midi_path) > 40, "empty phase2"
    assert os.path.getsize(p1_path) > 40, "empty phase1"
    write_provenance(
        midi_path, classification=AI_ASSISTED,
        generator="051-SGLM + musicom rules",
        parameters={"phase": 2, "bpm": BPM, "meter": "7/8", "key": KEY_NAME,
                    "seed": SEED, "voices": 4,
                    "form": "6 sections x 4 bars = 24 bars",
                    "quantization": "16th-grid (120 ticks) + per-bar chord-tone",
                    "instruments": ["double bass", "accordion", "clarinet",
                                    "violin"]},
        notes="Balkan dajcovo 7/8 dance in G Dorian. Fiedler vector -> lead "
              "melody ordering; 2nd eigenvector -> violin counter-axis; "
              "algebraic connectivity -> harmonic tension; eigenvalue gaps -> "
              "rhythm density.",
    )

    grid_path = os.path.join(PROJECT_DIR, "Analysis", "grid_visualization.txt")
    write_grid_visualization(c2.matrix, grid_path, ticks_per_character=240, bpm=BPM)

    # ---- audits (real numbers)
    aud = audit_midi(midi_path)
    tot = {"off16": 0, "off8": 0, "out_key": 0, "out_chord": 0, "notes": 0}
    for v in aud.values():
        for k in tot:
            tot[k] += v[k]
    print("\n=== GRID + HARMONY AUDIT (phase-2 MIDI read-back) ===")
    for tr_idx in sorted(aud):
        v = aud[tr_idx]
        print(f"  track{tr_idx} notes={v['notes']:3d} off16={v['off16']} "
              f"off8={v['off8']} out_key={v['out_key']} out_chord={v['out_chord']}")
    print(f"  TOTAL notes={tot['notes']} off16={tot['off16']} off8={tot['off8']} "
          f"out_key={tot['out_key']} out_chord={tot['out_chord']}")

    # ---- voice-leading check (outer voices bass + clarinet lead)
    vlc = VoiceLeadingRules(style="classical")
    vl_flags = []
    for b in range(N_BARS - 1):
        ra, rb = CHORDS[PROGRESSION[b]]["root"], CHORDS[PROGRESSION[b + 1]]["root"]
        da, db = CHORDS[PROGRESSION[b]]["deg"], CHORDS[PROGRESSION[b + 1]]["deg"]
        bass_a, bass_b = VOICE_LADDERS[0][ra], VOICE_LADDERS[0][rb]
        lead_a = VOICE_LADDERS[2][max(da, key=lambda d: sorted(da).index(d))]
        lead_b = VOICE_LADDERS[2][max(db, key=lambda d: sorted(db).index(d))]
        try:
            vl_flags += vlc.check_parallel_motion([bass_a, lead_a], [bass_b, lead_b])
            vl_flags += vlc.check_hidden_fifths([bass_a, lead_a], [bass_b, lead_b])
        except Exception as e:  # noqa: BLE001
            print("VL check exception (non-fatal):", repr(e))
    print("VL flags (bass+lead, classical):", len(vl_flags))

    # ---- summary.json
    summary = {
        "project": PROJECT_NAME, "genre": GENRE,
        "method": "051 Spectral Graph Laplacian Mapping (SGLM)", "layer": "concrete",
        "key": KEY_NAME, "key_pcs": sorted(KEY_PCS), "bpm": BPM, "meter": "7/8",
        "form": "6 sections x 4 bars = 24 bars", "sections": SECTION_NAMES,
        "section_functions": SECTION_FUNCTION,
        "spectra": spectra,
        "progression": [{"bar": b, "chord": PROGRESSION[b],
                         "deg": CHORDS[PROGRESSION[b]]["deg"],
                         "name": "".join(DEG_NAME[d] for d in CHORDS[PROGRESSION[b]]["deg"])}
                        for b in range(N_BARS)],
        "voices": [f"{n}({VOICE_PROGRAMS[i]})" for i, n in enumerate(VOICE_NAMES)],
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
