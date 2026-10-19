# -*- coding: utf-8 -*-
"""Project 252: Balkan x Spectral Graph Laplacian Mapping -- EXTENDED REWORK.

Autonomous nightly REWORK job (2026-10-19).
  Source:   228-balkan-spectral (Method 051 SGLM, 6x4=24 bars, G Dorian 7/8)
  Rework:   NEW LONGER + MORE VARIED version, 8x4=32 bars, same identity.
  Identity preserved: genre (Balkan dajcovo 7/8), key (G Dorian), tempo (132),
                       method (051 SGLM), instrumentation (double bass /
                       accordion / clarinet / violin).
  Variations added (6 distinct techniques):
    1. Register shift UP   (+12)  -> LiftA clarinet octave
    2. Counterline prominence      -> VerseB violin takes eig2 lead
    3. Diminution (16th subdiv)    -> Dance section
    4. Retrograde contour +        -> Bridge section
    5. Augmentation (sustain x2)   -> Climax section
    6. Octave doubling             -> Climax section
  Form: 8 sections x 4 bars = 32 bars (Intro/VerseA/LiftA/VerseB/Dance/Bridge/
        Climax/Coda). Per-section harmonic regions (each section own
        progression, varied starting degrees -- NOT all tonic).

Two-phase architecture (MANDATORY):
  Phase 1 = raw single-voice clarinet draft (off-grid, unquantized, jitter).
  Phase 2 = musicom rules: 8th/16th grid snap, per-bar chord-tone quantize,
            register clamp, dedup collided onsets, 4-voice texture.

Dual-version export (always-on humanization): -perfect + -humanized via
workflows.humanize.export_dual.

Engine only: structures + workflows.unitmatrix_composer. NO raw mido authoring
(mido used ONLY for read-back audit).
"""
import json
import os

import numpy as np

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer
from workflows.provenance import write_provenance, AI_ASSISTED
from workflows.humanize import export_dual
from visualization.grid import write_grid_visualization

# Instrument registry (source of truth) -- not pip-installed, flat module.
_INSTR_DIR = "/opt/data/repos/musicom/projects/Instruments"
import sys as _sys
if _INSTR_DIR not in _sys.path:
    _sys.path.insert(0, _INSTR_DIR)
from instrument_registry import DOUBLE_BASS, ACCORDION, CLARINET, VIOLIN
del _sys

# ------------------------------------------------------------ CONFIG -----
GENRE = "Balkan"
PROJECT_ID = 252
PROJECT_NAME = "252-balkan-spectral-extended"
PROJECT_DIR = f"/opt/data/projects/Styles/{GENRE}/{PROJECT_NAME}"
SOURCE = "228-balkan-spectral"
SOURCE_DIR = "/opt/data/projects/Styles/Balkan/228-balkan-spectral"

BPM = 132
TPB = 480
GRID16 = 120
GRID8 = 240
BAR = 7 * GRID8                      # 7/8 bar = 1680 ticks (dajcovo)
BARS_PER = 4
SECTION_TICKS = BAR * BARS_PER       # 6720
N_BARS = 32                          # 8 sections x 4 bars
TOTAL_TICKS = N_BARS * BAR           # 53760

SEED = 20261007
HZ_SEED = SEED + PROJECT_ID * 1000   # deterministic humanize seed
STYLE = "folk"                       # Balkan = folk dance -> loose organic profile
rng = np.random.default_rng(SEED)

SCALE_PCS = [7, 9, 10, 0, 2, 4, 5]   # G Dorian pitch classes
KEY_PCS = set(SCALE_PCS)
DEG_NAME = {0: "G", 1: "A", 2: "Bb", 3: "C", 4: "D", 5: "E", 6: "F"}
KEY_NAME = "G Dorian (G A Bb C D E F)"

VOICE_LADDERS = {
    0: [43, 45, 46, 48, 50, 52, 53],   # Bass      G2..F3
    1: [55, 57, 58, 60, 62, 64, 65],   # Accordion G3..F4
    2: [67, 69, 70, 72, 74, 76, 77],   # Clarinet  G4..F5
    3: [67, 69, 70, 72, 74, 76, 77],   # Violin    G4..F5
}
VOICE_NAMES = ["Bass", "Accordion", "Clarinet", "Violin"]
VOICE_PROGRAMS = [DOUBLE_BASS.midi_program, ACCORDION.midi_program,
                  CLARINET.midi_program, VIOLIN.midi_program]
VOICE_CHANNELS = [0, 1, 2, 3]
INSTR_NAMES = ["Double Bass", "Accordion", "Clarinet", "Violin"]

SECTION_FUNCTION = ["HOME", "HOME", "TURN", "TENSE", "TURN", "TENSE", "HOME", "HOME"]
SECTION_NAMES = ["Intro", "VerseA", "LiftA", "VerseB", "Dance", "Bridge",
                 "Climax", "Coda"]
SECTION_SCALE = {"HOME": 1.00, "TURN": 0.70, "TENSE": 0.45}

# Chord catalogue (degree sets), root degree first (G Dorian).
CHORDS = {
    "i":   {"root": 0, "deg": [0, 2, 4]},   # Gm
    "II":  {"root": 1, "deg": [1, 3, 5]},   # Am
    "III": {"root": 2, "deg": [2, 4, 6]},   # Bb
    "IV":  {"root": 3, "deg": [3, 5, 0]},   # C
    "v":   {"root": 4, "deg": [4, 6, 1]},   # Dm
    "vi":  {"root": 5, "deg": [5, 0, 2]},   # Edim
    "VII": {"root": 6, "deg": [6, 1, 3]},   # F
}

# Per-section harmonic regions: each section its OWN progression with varied
# starting degree (NOT all tonic -> avoids the bar-0 "always i" trap). The
# starting roots are [0,0,3,2,4,6,3,0] -- five distinct section openings.
PROGRESSION_PER_SECTION = [
    ["i", "i", "VII", "VII"],        # Intro  (start i)
    ["i", "VII", "IV", "i"],         # VerseA (start i)
    ["IV", "II", "VII", "v"],        # LiftA  (start IV)
    ["III", "VII", "IV", "i"],       # VerseB (start III)
    ["v", "IV", "II", "VII"],        # Dance  (start v)
    ["VII", "IV", "II", "v"],        # Bridge (start VII)
    ["IV", "VII", "i", "IV"],        # Climax (start IV)
    ["i", "VII", "IV", "i"],         # Coda   (start i)
]
PROGRESSION = [c for sec in PROGRESSION_PER_SECTION for c in sec]
assert len(PROGRESSION) == N_BARS

# Melody variation table per section:
#   (lead_reg, lead_reverse, lead_subdiv, lead_sustain, lead_oct_double,
#    lead_density, counter_density)  + technique label
SECTION_SPEC = [
    (0, False, 8,  1, False, 4, 0, "sparse intro (counter tacet)"),
    (0, False, 8,  1, False, 6, 3, "baseline full texture"),
    (+12, False, 8,  1, False, 6, 3, "register shift UP (+12)"),
    (0, False, 8,  1, False, 4, 5, "counterline prominence (violin eig2 lead)"),
    (0, False, 16, 1, False, 9, 4, "diminution (16th subdivision)"),
    (-12, True, 8,  1, False, 4, 3, "retrograde contour + register DOWN (-12)"),
    (0, False, 8,  2, True,  4, 3, "augmentation (sustain x2) + octave doubling"),
    (0, False, 8,  1, False, 3, 2, "diminution fade to tonic"),
]


# ------------------------------------------- SGLM spectrum (method 051) ----
FIFTHS_ORDER = [0, 4, 1, 5, 2, 6, 3]
FIFTHS_POS = {d: i for i, d in enumerate(FIFTHS_ORDER)}


def cycle_dist(a, b):
    d = abs(FIFTHS_POS[a] - FIFTHS_POS[b])
    return min(d, 7 - d)


def build_laplacian(scale=1.0, sigma=1.5, floor=0.05, tonic_boost=0.45):
    n = 7
    W = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            d = cycle_dist(i, j)
            w = np.exp(-(d * d) / (2.0 * sigma * sigma))
            w = w * scale + floor
            if i == 0 or j == 0:          # tonic-incident edges
                w += tonic_boost * scale
            W[i, j] = w
    D = np.diag(W.sum(axis=1))
    return D - W, W


def spectrum(L):
    vals, vecs = np.linalg.eigh(L)
    return vals, vecs


def orient(vec, anchor_deg):
    return -vec if vec[anchor_deg] > 0 else vec


def spectral_order(chord_sym, eig_idx, sec_idx):
    """Chord degrees ordered by the section graph eigenvector (lead/counter)."""
    L, _ = build_laplacian(scale=SECTION_SCALE[SECTION_FUNCTION[sec_idx]])
    _vals, vecs = spectrum(L)
    v = orient(vecs[:, eig_idx], 0)
    degs = CHORDS[chord_sym]["deg"]
    return [int(d) for d in sorted(degs, key=lambda d: v[d])]


# -------------------------------------------------- Phase-1 raw draft -----
def phase1_raw_events(total_ticks):
    sr = np.random.default_rng(SEED + 777)
    L, _ = build_laplacian(scale=SECTION_SCALE["HOME"])
    vals, vecs = spectrum(L)
    v1 = orient(vecs[:, 1], 0)
    spectral_order_full = [int(d) for d in np.argsort(v1)]
    lam1 = float(vals[1])
    evs = []
    t = 0
    while t < total_ticks:
        for deg in spectral_order_full:
            if t >= total_ticks:
                break
            pitch = VOICE_LADDERS[2][deg]
            pitch += int(sr.normal(0, 1.5))
            pitch += int(sr.integers(0, 2)) * 12 if sr.random() < 0.08 else 0
            pitch = int(np.clip(pitch, 60, 96))
            dur = int(np.clip(GRID16 * (1.6 + lam1 * 2.0) + sr.integers(-30, 30), 80, 480))
            off = max(0, t + int(sr.integers(-30, 30)))
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
    # Always add a terminal landmark (pitch 0, passed through the humanizer
    # untouched) so the cell ends EXACTLY at `total` and the zero-drift
    # invariant survives humanization. Notes are already clamped <= total.
    unit.add_event(MusicEvent(pitch=0, volume=0, start_tick=total - 1, end_tick=total))
    return unit


def _dedup(unit):
    """Dedup collided (start_tick, pitch) keeping the LONGEST duration."""
    longest = {}
    for e in unit.events:
        key = (int(e.start_tick), int(e.pitch))
        d = int(e.end_tick) - int(e.start_tick)
        prev = longest.get(key)
        if prev is None or d > (int(prev.end_tick) - int(prev.start_tick)):
            longest[key] = e
    seen = set()
    keep = []
    for e in unit.events:
        key = (int(e.start_tick), int(e.pitch))
        if key in seen:
            continue
        seen.add(key)
        keep.append(longest[key])
    unit.data = np.array([(int(e.pitch), int(e.volume), int(e.start_tick),
                           int(e.end_tick)) for e in keep], dtype=MusicEvent.DTYPE)
    return unit


def bass_unit(chord_syms):
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


def harmony_unit(chord_syms, dense=False):
    unit = MusicUnit()
    ladder = VOICE_LADDERS[1]
    for b, sym in enumerate(chord_syms):
        degs = CHORDS[sym]["deg"]
        t0 = b * BAR
        positions = [1, 3, 5] if not dense else [1, 2, 3, 4, 5]
        for p in positions:
            t = t0 + p * GRID8
            voicing = [ladder[degs[0]], ladder[degs[1]], ladder[degs[2]]]
            vel = 62 if p in (1, 3) else 70
            for midi in voicing:
                unit.add_event(MusicEvent(pitch=midi, volume=vel,
                                          start_tick=t, end_tick=t + GRID8 - 30))
    return _pad(unit, 4 * BAR)


def melody_unit(voice_idx, sec_idx, chord_syms, eig_idx, density, register=0,
                reverse=False, subdiv=8, sustain=1, oct_double=False):
    """Lead (clarinet) / counter (violin) spectral melody, grid-locked + in-chord.

    Variation knobs: register (semitone shift), reverse (retrograde contour),
    subdiv (8th vs 16th grid), sustain (augmentation), oct_double (octave up).
    """
    unit = MusicUnit()
    ladder = VOICE_LADDERS[voice_idx]
    step = GRID8 if subdiv == 8 else GRID16
    nslots = 7 if subdiv == 8 else 14
    gap = 24 if subdiv == 8 else 12
    for b, sym in enumerate(chord_syms):
        ordered = spectral_order(sym, eig_idx, sec_idx)
        contour = ordered + ordered[-2:0:-1]      # up then down
        if reverse:
            contour = contour[::-1]               # retrograde
        t0 = b * BAR
        n = int(min(density, nslots))
        slots = [int(round(x)) for x in np.linspace(0, nslots - 1, n)]
        # ensure distinct
        slots = sorted(set(slots))
        for k, s in enumerate(slots):
            try:
                deg = contour[k % len(contour)]
            except IndexError:
                deg = contour[0]
            t = t0 + s * step
            dur = sustain * step - gap
            end = min(t + dur, t0 + BAR)
            if end <= t:
                end = t + step - gap
            vel = 78 if s == 0 else 66
            if voice_idx == 3:
                vel -= 8
            vel = int(np.clip(vel, 44, 104))
            pitch = ladder[deg] + register
            pitch = int(np.clip(pitch, 21, 108))
            unit.add_event(MusicEvent(pitch=pitch, volume=vel,
                                      start_tick=t, end_tick=end))
            if oct_double:
                unit.add_event(MusicEvent(pitch=int(np.clip(pitch + 12, 21, 108)),
                                          volume=vel - 6,
                                          start_tick=t, end_tick=end))
    _dedup(unit)
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


def build_phase2_composer():
    # beats_per_bar=14 => ticks_per_bar = 480*14 = 6720 = one SECTION
    # (4 x 7/8 bars). This makes the humanizer's per-section `span` equal the
    # section content length exactly, so notes clamp to the 6720-tick seam and
    # the zero-drift invariant holds after humanization.
    c = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=14)
    c.create_matrix(num_voices=4, num_sections=len(SECTION_NAMES))
    for i in range(4):
        c.add_voice(VOICE_NAMES[i], program=VOICE_PROGRAMS[i],
                    channel=VOICE_CHANNELS[i])
    for name in SECTION_NAMES:
        c.add_section(name, bars=1)
    for sec_idx in range(len(SECTION_NAMES)):
        syms = PROGRESSION_PER_SECTION[sec_idx]
        (lreg, lrev, lsub, lsus, loct, lden, cden, _tech) = SECTION_SPEC[sec_idx]
        dense = (lsub == 16)
        c.set_unit(0, sec_idx, bass_unit(syms))
        c.set_unit(1, sec_idx, harmony_unit(syms, dense=dense))
        c.set_unit(2, sec_idx, melody_unit(2, sec_idx, syms, 1, lden,
                                           register=lreg, reverse=lrev,
                                           subdiv=lsub, sustain=lsus,
                                           oct_double=loct))
        # violin counter: eig2 axis. If counter_density==0 -> pad-only (tacet)
        if cden > 0:
            c.set_unit(3, sec_idx, melody_unit(3, sec_idx, syms, 2, cden,
                                               register=0, reverse=False,
                                               subdiv=lsub, sustain=1,
                                               oct_double=False))
        else:
            c.set_unit(3, sec_idx, _pad(MusicUnit(), 4 * BAR))
    ok, msg = c.validate()
    if not ok:
        raise RuntimeError(f"phase2 validate failed: {msg}")
    return c


# ------------------------------------------------- audits (read-back) ------
def audit_midi(midi_path):
    import mido  # READING ONLY (analysis)
    mf = mido.MidiFile(midi_path)
    bar_pcs = [set(SCALE_PCS[d] for d in CHORDS[s]["deg"]) for s in PROGRESSION]
    per_track = {}
    for tr_idx, track in enumerate(mf.tracks):
        t = 0
        notes = []
        for msg in track:
            t += msg.time
            if msg.type == "note_on" and msg.velocity > 0 and msg.note > 0:
                notes.append((int(msg.note), t, int(msg.velocity)))
        if notes:
            per_track[tr_idx] = notes
    report = {}
    for tr_idx, notes in per_track.items():
        off16 = sum(1 for (p, t, v) in notes if t % GRID16 != 0)
        off8 = sum(1 for (p, t, v) in notes if t % GRID8 != 0)
        out_key = sum(1 for (p, t, v) in notes if p % 12 not in KEY_PCS)
        out_chord = 0
        for (p, t, v) in notes:
            b = min(t // BAR, N_BARS - 1)
            if p % 12 not in bar_pcs[b]:
                out_chord += 1
        report[tr_idx] = {"notes": len(notes), "off16": off16, "off8": off8,
                          "out_key": out_key, "out_chord": out_chord}
    return report


def _zero_drift(midi_path):
    import mido  # READING ONLY (analysis)
    mf = mido.MidiFile(midi_path)
    spans = [sum(msg.time for msg in tr) for tr in mf.tracks[1:]]
    return spans, len(spans)


# ------------------------------------------------- main --------------------
def main():
    for sub in ("MIDI", "Audio", "Analysis", "Scripts"):
        os.makedirs(os.path.join(PROJECT_DIR, sub), exist_ok=True)

    # ---- per-section spectrum (reported, not density-driving)
    spectra = []
    for sec_idx in range(len(SECTION_NAMES)):
        fn = SECTION_FUNCTION[sec_idx]
        L, _ = build_laplacian(scale=SECTION_SCALE[fn])
        vals, _vecs = spectrum(L)
        spectra.append({"section": SECTION_NAMES[sec_idx], "function": fn,
                        "lambda1": float(vals[1]), "lambda2": float(vals[2]),
                        "gap": float(vals[2] - vals[1])})

    # ---- phase 1
    p1_path = os.path.join(PROJECT_DIR, "MIDI", f"{PROJECT_NAME}-phase1.mid")
    export_phase1(p1_path)
    write_provenance(
        p1_path, classification=AI_ASSISTED,
        generator="051-SGLM (raw Fiedler walk)", 
        parameters={"phase": 1, "bpm": BPM, "meter": "7/8", "key": KEY_NAME,
                    "seed": SEED, "voices": 1, "bars": N_BARS,
                    "note": "raw generative draft (single clarinet, off-grid)"})

    # ---- phase 2 (dual-version: perfect + humanized)
    perf_path = os.path.join(PROJECT_DIR, "MIDI", f"{PROJECT_NAME}-perfect.mid")
    hum_path = os.path.join(PROJECT_DIR, "MIDI", f"{PROJECT_NAME}-humanized.mid")
    c2 = build_phase2_composer()
    hz_instruments = {VOICE_NAMES[i]: [DOUBLE_BASS, ACCORDION, CLARINET, VIOLIN][i].humanize_dna
                      for i in range(4)}
    hz = export_dual(c2, perf_path, hum_path, style=STYLE, seed=HZ_SEED,
                     bpm=BPM, instruments=hz_instruments)

    assert os.path.getsize(perf_path) > 40, "empty perfect"
    assert os.path.getsize(hum_path) > 40, "empty humanized"
    assert os.path.getsize(p1_path) > 40, "empty phase1"

    for p, phase, gen in [
        (perf_path, "2-perfect", "051-SGLM + musicom rules (grid-locked)"),
        (hum_path, "2-humanized", "051-SGLM + rules + humanize"),
    ]:
        write_provenance(
            p, classification=AI_ASSISTED, generator=gen,
            parameters={"phase": phase, "bpm": BPM, "meter": "7/8", "key": KEY_NAME,
                        "seed": SEED, "humanize_seed": HZ_SEED, "style": STYLE,
                        "voices": 4, "bars": N_BARS,
                        "form": "8 sections x 4 bars = 32 bars",
                        "instruments": INSTR_NAMES},
            notes="Balkan dajcovo 7/8 in G Dorian, rework of 228-balkan-spectral. "
                  "Fiedler vector -> lead, 2nd eigenvector -> violin counter, "
                  "algebraic connectivity -> harmonic tension.")

    # record humanize summary
    hz_summary = {}
    for vname, vstat in hz.items():
        hz_summary[vname] = {
            "seed": vstat.get("seed"), "n_notes": vstat.get("n_notes"),
            "mean_abs_shift_ticks": vstat.get("mean_abs_shift_ticks"),
            "max_abs_shift_ticks": vstat.get("max_abs_shift_ticks"),
            "mean_abs_vel_delta": vstat.get("mean_abs_vel_delta"),
        }

    grid_path = os.path.join(PROJECT_DIR, "Analysis", "grid_visualization.txt")
    write_grid_visualization(c2.matrix, grid_path, ticks_per_character=240, bpm=BPM)

    # ---- audits
    aud_perf = audit_midi(perf_path)
    aud_hum = audit_midi(hum_path)
    spans_hum, ntracks_hum = _zero_drift(hum_path)
    spans_perf, ntracks_perf = _zero_drift(perf_path)

    def _tot(aud):
        t = {"off16": 0, "off8": 0, "out_key": 0, "out_chord": 0, "notes": 0}
        for v in aud.values():
            for k in t:
                t[k] += v[k]
        return t

    tot_perf = _tot(aud_perf)
    tot_hum = _tot(aud_hum)

    # section roots (guard against bar-0 "always tonic" collapse)
    section_roots = [CHORDS[PROGRESSION_PER_SECTION[s][0]]["root"] for s in range(len(SECTION_NAMES))]

    summary = {
        "project": PROJECT_NAME, "genre": GENRE, "source": SOURCE,
        "method": "051 Spectral Graph Laplacian Mapping (SGLM)", "layer": "concrete",
        "rework": "extended (longer + more varied)",
        "key": KEY_NAME, "key_pcs": sorted(KEY_PCS), "bpm": BPM, "meter": "7/8",
        "form": "8 sections x 4 bars = 32 bars", "sections": SECTION_NAMES,
        "section_functions": SECTION_FUNCTION, "section_start_roots": section_roots,
        "spectra": spectra,
        "variation_techniques": [{"section": SECTION_NAMES[i], "technique": SECTION_SPEC[i][7]}
                                 for i in range(len(SECTION_NAMES))],
        "voices": [f"{n}({VOICE_PROGRAMS[i]})" for i, n in enumerate(VOICE_NAMES)],
        "perfect_audit": tot_perf, "humanized_audit": tot_hum,
        "zero_drift": {"perfect_tracks": ntracks_perf, "humanized_tracks": ntracks_hum,
                       "perfect_span": spans_perf, "humanized_span": spans_hum},
        "humanize": {"style": STYLE, "seed": HZ_SEED, "per_voice": hz_summary},
        "seed": SEED,
    }
    with open(os.path.join(PROJECT_DIR, "Analysis", "summary.json"), "w") as f:
        json.dump(summary, f, indent=2, default=str)

    print("=== GRID + HARMONY AUDIT (perfect MIDI) ===")
    for tr in sorted(aud_perf):
        v = aud_perf[tr]
        print(f"  track{tr} notes={v['notes']:3d} off16={v['off16']} off8={v['off8']} "
              f"out_key={v['out_key']} out_chord={v['out_chord']}")
    print(f"  PERFECT  TOTAL notes={tot_perf['notes']} off16={tot_perf['off16']} "
          f"off8={tot_perf['off8']} out_key={tot_perf['out_key']} out_chord={tot_perf['out_chord']}")
    print(f"  HUMANIZED TOTAL notes={tot_hum['notes']} off16={tot_hum['off16']} "
          f"off8={tot_hum['off8']} out_key={tot_hum['out_key']} out_chord={tot_hum['out_chord']}")
    print("  section start roots:", section_roots)
    print("  zero-drift perfect:", ntracks_perf, "tracks len", set(spans_perf))
    print("  zero-drift humanized:", ntracks_hum, "tracks len", set(spans_hum))

    print("\nPHASE1", p1_path, os.path.getsize(p1_path))
    print("PERFECT", perf_path, os.path.getsize(perf_path))
    print("HUMANIZED", hum_path, os.path.getsize(hum_path))
    print("GRID", grid_path)
    print("SUMMARY", os.path.join(PROJECT_DIR, "Analysis", "summary.json"))


if __name__ == "__main__":
    main()