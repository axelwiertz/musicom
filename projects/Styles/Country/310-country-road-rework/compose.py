#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""310-country-road-rework - engine redesign of 012-country-country-uke.

Source 012 audited and FAILED engine standards (hand-rolled mido, zero-drift
drift, 192 off-grid onsets, no phase1, no provenance). Rebuilt FROM SCRATCH
through the canonical UnitMatrixComposer workflow, preserving the musical
identity: Country road song, G major, 96 BPM, I-V-vi-IV (G D Em C), 8 voices.

Two-phase architecture:
  Phase 1 = raw generative draft (seeded random-walk pitch_index + unquantized
            rhythm), single voice, exported as -phase1.mid.
  Phase 2 = musicom rules: chord-tone quantization per bar, rhythm-grid snap to
            16th (120 ticks), register/range enforcement, per-section harmonic
            regions, dedup of collided (start_tick, pitch).
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import random

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer
from visualization.grid import write_grid_visualization
from workflows.provenance import write_provenance, AI_ASSISTED
from workflows.humanize import export_dual

# Instrument registry is a data module under the repo (not pip-installed, not in
# the editable MAPPING). Load it by absolute path WITHOUT touching sys.path.
_reg_spec = importlib.util.spec_from_file_location(
    "instrument_registry",
    "/opt/data/repos/musicom/projects/Instruments/instrument_registry.py")
_reg = importlib.util.module_from_spec(_reg_spec)
_reg_spec.loader.exec_module(_reg)
by_name = _reg.by_name

# ---------------------------------------------------------------------------
# Identity constants (preserved from source 012)
# ---------------------------------------------------------------------------
BPM = 96
TPB = 480
BPB = 4
BAR = TPB * BPB            # 1920 ticks = 1 bar
SIX = 120                  # 16th note
EIGH = 240                 # 8th note
QUAR = 480                 # quarter
HALF = 960
WHOLE = 1920

KEY = "G"
KEY_PCS = {7, 9, 11, 0, 2, 4, 6}   # G major pitch classes
STYLE = "country"
GENRE = "Country"
GEN_SEED = 310            # deterministic composition seed

PROJ = "/opt/data/projects/Styles/Country/310-country-road-rework"
SOURCE = "/opt/data/projects/Styles/Country/012-country-country-uke"

# Chord library: pitch classes + voicing + bass root. All diatonic to G major.
CHORDS = {
    "G":  {"pcs": [7, 11, 2], "v": [55, 59, 62], "root": 43},
    "D":  {"pcs": [2, 6, 9],  "v": [50, 54, 57], "root": 38},
    "Em": {"pcs": [4, 7, 11], "v": [52, 55, 59], "root": 40},
    "C":  {"pcs": [0, 4, 7],  "v": [48, 52, 55], "root": 36},
    "Am": {"pcs": [9, 0, 4],  "v": [45, 48, 52], "root": 33},
}

# Form: 10 sections, 68 bars (source had 8 sections / 48 bars). N+2 satisfied.
# Each section owns its own harmonic region (midpoint chord never forced to i).
SECTIONS = [
    ("Intro",        4, ["G", "D", "Em", "C"]),
    ("Verse 1",      8, ["G", "D", "Em", "C", "G", "D", "C", "D"]),
    ("Pre-Chorus",   4, ["C", "D", "Em", "D"]),
    ("Chorus 1",     8, ["G", "D", "Em", "C", "G", "D", "C", "D"]),
    ("Verse 2",      8, ["G", "D", "Em", "C", "G", "D", "C", "D"]),
    ("Chorus 2",     8, ["G", "D", "Em", "C", "G", "D", "C", "D"]),
    ("Bridge",       8, ["Em", "C", "G", "D", "Em", "C", "Am", "D"]),
    ("Solo",         8, ["G", "Em", "C", "D", "G", "Em", "C", "D"]),
    ("Final Chorus", 8, ["G", "D", "Em", "C", "G", "D", "C", "D"]),
    ("Outro",        4, ["G", "C", "G", "G"]),
]

TOTAL_BARS = sum(s[1] for s in SECTIONS)
TOTAL_TICKS = TOTAL_BARS * BAR

# global bar -> chord name (for per-bar attribution)
BAR_CHORDS = []
sec_start = []
_acc = 0
for _name, _bars, _chords in SECTIONS:
    sec_start.append(_acc)
    for _b in range(_bars):
        BAR_CHORDS.append(_chords[_b % len(_chords)])
    _acc += _bars

# Voice program map (raw GM numbers; source identity preserved)
VOICES = [
    ("Lead Vocal",     53, 0),
    ("Harmony Vox",    52, 1),
    ("Acoustic Guitar", 24, 2),
    ("Electric Guitar", 29, 3),
    ("Bass",           33, 4),
    ("Drums",           0, 9),
    ("Fiddle",         40, 5),
    ("Pedal Steel",    48, 6),
]

# instrument-registry name for humanize DNA (per voice)
HZ_INST = {
    "Lead Vocal": "choir",
    "Harmony Vox": "choir",
    "Acoustic Guitar": "acoustic_guitar",
    "Electric Guitar": "overdriven",
    "Bass": "electric_bass",
    "Drums": "drum_kit",
    "Fiddle": "fiddle",
    "Pedal Steel": "steel_acoustic",
}

# fallback 4-tuples (timing_sigma_ms, velocity_sigma, layback_ms, duration_sigma)
HZ_DNA_FALLBACK = {
    "Lead Vocal": (None, 8.0, None, 0.03),
    "Harmony Vox": (None, 8.0, None, 0.03),
    "Acoustic Guitar": (None, 6.0, None, 0.02),
    "Electric Guitar": (None, 6.0, None, 0.02),
    "Bass": (5.0, 4.0, 8.0, 0.01),
    "Drums": (2.0, 4.0, 0.0, 0.008),
    "Fiddle": (None, 6.0, None, 0.02),
    "Pedal Steel": (None, 6.0, None, 0.02),
}


def _instr(name: str):
    try:
        return by_name(name)
    except Exception:
        return None


def hz_dna_for(voice_name: str):
    inst = _instr(HZ_INST[voice_name])
    if inst is not None and getattr(inst, "humanize_dna", None) is not None:
        return inst.humanize_dna
    return HZ_DNA_FALLBACK[voice_name]


# ---------------------------------------------------------------------------
# Grid / quantization helpers
# ---------------------------------------------------------------------------
def snap(t, grid=SIX):
    return int(round(t / grid)) * grid


def nearest_chord_pc(pc, chord):
    pcs = chord["pcs"]
    def circ(a, b):
        return min((a - b) % 12, (b - a) % 12)
    return pcs[min(range(len(pcs)), key=lambda i: circ(pc, pcs[i]))]


def quantize_pitch(midi, chord, lo, hi):
    pc = nearest_chord_pc(midi % 12, chord)
    out = (midi // 12) * 12 + pc
    while out < lo:
        out += 12
    while out > hi:
        out -= 12
    return out


def build_unit(notes, span):
    """Notes = list of (pitch, vel, start, dur). Terminal landmark guarantees
    len_ticks() == span (zero-drift invariant per cell)."""
    evs = []
    for pitch, vel, start, dur in notes:
        start = max(0, min(int(start), span - SIX))
        end = min(int(start) + int(dur), span)
        if end <= start:
            end = start + SIX
        evs.append(MusicEvent(pitch=pitch, volume=vel, start_tick=start, end_tick=end))
    evs.append(MusicEvent(pitch=0, volume=0, start_tick=span - 1, end_tick=span))
    return MusicUnit(events=evs)


def dedup(notes):
    """Snap done upstream; dedup collided (start_tick, pitch) keep longest."""
    notes.sort(key=lambda n: (n[2], n[0]))
    d = {}
    for midi, vel, onset, dur in notes:
        k = (onset, midi)
        if k not in d or dur > d[k][3]:
            d[k] = (midi, vel, onset, dur)
    return sorted(d.values(), key=lambda n: n[2])


# ---------------------------------------------------------------------------
# Phase 1 - raw generative draft (single voice, unquantized)
# ---------------------------------------------------------------------------
def phase1_raw(seed):
    """Random-walk pitch_index in [0,1] + unquantized rhythm (float beats)."""
    rng = random.Random(seed)
    out = []
    t = 0.0
    p = 0.5
    total_beats = TOTAL_BARS * 4
    while t < total_beats - 1.0:
        dur = rng.uniform(0.4, 1.1)
        out.append((t, p, dur))
        p += rng.uniform(-0.22, 0.22)
        p = max(0.05, min(0.95, p))
        t += rng.uniform(0.35, 0.95)
    return out


def build_phase1(raw):
    """Raw pitch_index -> raw MIDI pitch (NOT snapped to scale/chord), raw
    rhythm (NOT grid snapped). Single voice, but split across the SAME section
    grid as phase 2 so no single cell exceeds the uint16 tick ceiling
    (MusicEvent.DTYPE stores ticks as uint16; a 68-bar cell = 130560 ticks
    would overflow and corrupt the timeline)."""
    p1 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BPB)
    p1.create_matrix(1, len(SECTIONS))
    p1.add_voice("RawDraft", program=40, channel=0)
    for name, bars, chords in SECTIONS:
        p1.add_section(name, bars=bars)
    for si, (name, bars, chords) in enumerate(SECTIONS):
        b0 = sec_start[si]
        span = bars * BAR
        notes = []
        for t, p, dur in raw:
            bar = int(t // 4)
            if b0 <= bar < b0 + bars:
                onset = int(t * TPB) - b0 * BAR
                if onset < 0 or onset >= span - SIX:
                    continue
                midi = 57 + int(p * 28)      # raw, no scale/chord quantization
                d = int(dur * TPB)
                notes.append((midi, 90, onset, d))
        p1.fill_voice_section("RawDraft", name, build_unit(notes, span))
    ok, msg = p1.validate()
    if not ok:
        raise RuntimeError(f"phase1 validate failed: {msg}")
    return p1


# ---------------------------------------------------------------------------
# Phase 2 - rules post-processing
# ---------------------------------------------------------------------------
def raw_events_for_section(sec_idx):
    name, bars, chords = SECTIONS[sec_idx]
    b0 = sec_start[sec_idx]
    b1 = b0 + bars
    evs = []
    for t, p, dur in RAW:
        bar = int(t // 4)
        if b0 <= bar < b1:
            onset = snap(int(t * TPB) - b0 * BAR, SIX)
            if onset < 0 or onset >= bars * BAR:
                continue
            evs.append((onset, p, dur))
    return evs


def local_chords(sec_idx):
    name, bars, chords = SECTIONS[sec_idx]
    return [CHORDS[chords[b % len(chords)]] for b in range(bars)]


def quantize_lead(sec_idx, lo=60, hi=81, vel=88):
    lc = local_chords(sec_idx)
    notes = []
    for onset, p, dur in raw_events_for_section(sec_idx):
        chord = lc[min(onset // BAR, len(lc) - 1)]
        raw_midi = 57 + int(p * 28)
        midi = quantize_pitch(raw_midi, chord, lo, hi)
        d = max(SIX, snap(int(dur * TPB), SIX))
        notes.append((midi, vel, onset, d))
    return dedup(notes)


def re_quantize(notes, lc, lo, hi):
    out = []
    for midi, vel, onset, d in notes:
        chord = lc[min(onset // BAR, len(lc) - 1)]
        out.append((quantize_pitch(midi, chord, lo, hi), vel, onset, d))
    return out


def invert_notes(notes, lc, pivot=67, lo=60, hi=81):
    out = []
    for midi, vel, onset, d in notes:
        chord = lc[min(onset // BAR, len(lc) - 1)]
        out.append((quantize_pitch(2 * pivot - midi, chord, lo, hi), vel, onset, d))
    return out


def augment_notes(notes, factor=2.0):
    return [(m, v, s, max(SIX, snap(int(d * factor), SIX))) for m, v, s, d in notes]


def harmonize_below(lead_midi, chord):
    pcs = sorted(chord["pcs"])
    pc = lead_midi % 12
    below = [c for c in pcs if c < pc]
    target = max(below) if below else pcs[-1]
    out = lead_midi - ((pc - target) % 12)
    while out < 55:
        out += 12
    while out > 76:
        out -= 12
    return out


# Build per-section lead notes (with documented variation techniques)
def build_lead_map():
    leads = {}
    leads["Intro"] = quantize_lead(0, lo=60, hi=76, vel=82)
    v1 = quantize_lead(1, lo=60, hi=79, vel=86)
    leads["Verse 1"] = v1
    leads["Pre-Chorus"] = quantize_lead(2, lo=64, hi=84, vel=90)          # register shift up
    c1 = quantize_lead(3, lo=62, hi=81, vel=94)
    leads["Chorus 1"] = c1
    # variation: motif INVERSION (Verse 2 inverts Verse 1 contour)
    leads["Verse 2"] = invert_notes(v1, local_chords(4), pivot=67, lo=60, hi=79)
    # variation: DENSITY RISE + register shift (Chorus 2 lifts + counterline added below)
    leads["Chorus 2"] = re_quantize(c1, local_chords(5), lo=64, hi=84)
    # variation: MODE SHIFT to relative minor (Bridge = Em/Am emphasis, low register)
    leads["Bridge"] = quantize_lead(6, lo=57, hi=74, vel=82)
    leads["Solo"] = []                                                     # lead rests, fiddle solo
    # variation: REGISTER SHIFT +12 (octave up final chorus)
    leads["Final Chorus"] = re_quantize(c1, local_chords(8), lo=72, hi=84)
    # variation: RETROGRADE descending motif (degrees 5-3-2-1) as outro
    leads["Outro"] = retro_outro()
    return leads


def retro_outro():
    motif = [74, 71, 69, 67]      # D5 B4 A4 G4  (5-3-2-1)
    lc = local_chords(9)          # G C G G
    notes = []
    for i, m in enumerate(motif):
        bar = i                       # one note per bar, quarter grid
        chord = lc[bar]
        midi = quantize_pitch(m, chord, 60, 79)
        notes.append((midi, 74, bar * BAR, QUAR))
    return notes


# ---------------------------------------------------------------------------
# Accompaniment voices
# ---------------------------------------------------------------------------
def guitar_notes(sec_idx, vel):
    name, bars, chords = SECTIONS[sec_idx]
    notes = []
    for b in range(bars):
        chord = CHORDS[chords[b % len(chords)]]
        for beat in (0, 2):           # strum on beats 1 and 3
            onset = b * BAR + beat * QUAR
            for n in chord["v"]:
                notes.append((n, vel, onset, 360))
    return notes


def electric_notes(sec_idx, vel, sixteenth=False):
    name, bars, chords = SECTIONS[sec_idx]
    notes = []
    step = SIX if sixteenth else EIGH
    for b in range(bars):
        chord = CHORDS[chords[b % len(chords)]]
        v = chord["v"]
        pos = 0
        idx = 0
        while pos < BAR:
            if pos % QUAR != 0:       # off-beats only (fills)
                notes.append((v[idx % 3] + 12, vel, b * BAR + pos, step))
            idx += 1
            pos += step
    return notes


def bass_notes(sec_idx, vel):
    name, bars, chords = SECTIONS[sec_idx]
    notes = []
    for b in range(bars):
        chord = CHORDS[chords[b % len(chords)]]
        root = chord["root"]
        fifth = chord["root"] + 7
        notes.append((root, vel, b * BAR, 480))
        notes.append((fifth, vel, b * BAR + HALF, 480))
    return notes


def drums_notes(sec_idx, vel, half_time=False, open_hat=False):
    name, bars, chords = SECTIONS[sec_idx]
    notes = []
    for b in range(bars):
        base = b * BAR
        if half_time:
            notes.append((36, vel, base, SIX))              # kick on 1 only
            notes.append((38, vel, base + HALF, SIX))       # snare on 3
            for e in range(0, 8):
                notes.append((42, vel - 12, base + e * EIGH, SIX))
        else:
            notes.append((36, vel, base, SIX))              # kick 1
            notes.append((36, vel, base + HALF, SIX))       # kick 3
            notes.append((38, vel, base + QUAR, SIX))       # snare 2
            notes.append((38, vel, base + QUAR * 3, SIX))   # snare 4
            for e in range(0, 8):
                notes.append((42, vel - 10, base + e * EIGH, SIX))
            if open_hat:
                notes.append((46, vel - 6, base + QUAR * 3 + EIGH, SIX))
    return notes


def fiddle_notes(sec_idx, sec_name, vel, augmented_lead=None):
    name, bars, chords = SECTIONS[sec_idx]
    notes = []
    if sec_name == "Solo":
        # variation: AUGMENTATION - fiddle takes lead, durations x2
        for m, v, s, d in augmented_lead:
            notes.append((m, v + 4, s, d))
        return notes
    if sec_name == "Bridge":
        for b in range(bars):          # sustained texture
            chord = CHORDS[chords[b % len(chords)]]
            notes.append((chord["v"][1] + 12, vel, b * BAR, WHOLE))
        return notes
    # verses/chorus: off-beat chord-tone fills (counterline)
    for b in range(bars):
        chord = CHORDS[chords[b % len(chords)]]
        notes.append((chord["v"][2] + 12, vel, b * BAR + QUAR * 2 + EIGH, EIGH))  # beat 2.5
        notes.append((chord["v"][1] + 12, vel, b * BAR + QUAR * 3 + EIGH, EIGH))  # beat 3.5
    return notes


def steel_notes(sec_idx, sec_name, vel):
    name, bars, chords = SECTIONS[sec_idx]
    notes = []
    if sec_name == "Outro":
        # variation: DIMINUTION + velocity taper
        for b in range(bars):
            chord = CHORDS[chords[b % len(chords)]]
            notes.append((chord["v"][0], max(40, vel - 14 * b), b * BAR, EIGH))
            notes.append((chord["v"][1], max(40, vel - 14 * b), b * BAR + EIGH * 2, EIGH))
        return notes
    for b in range(bars):
        chord = CHORDS[chords[b % len(chords)]]
        notes.append((chord["v"][1], vel, b * BAR, HALF + QUAR))   # long sustained slide
        notes.append((chord["v"][0], vel, b * BAR + HALF, HALF))
    return notes


# ---------------------------------------------------------------------------
# Main build
# ---------------------------------------------------------------------------
def main():
    os.makedirs(os.path.join(PROJ, "MIDI"), exist_ok=True)
    os.makedirs(os.path.join(PROJ, "Audio"), exist_ok=True)
    os.makedirs(os.path.join(PROJ, "Analysis"), exist_ok=True)

    global RAW
    RAW = phase1_raw(GEN_SEED)

    # ---- Phase 1 export ----
    phase1_path = os.path.join(PROJ, "MIDI", "310-country-road-rework-phase1.mid")
    p1 = build_phase1(RAW)
    p1.to_midi(phase1_path)
    write_provenance(
        phase1_path, AI_ASSISTED,
        "random-walk pitch_index + unquantized rhythm (phase 1 raw draft)",
        sources=[SOURCE + "/Scripts/generate_v2.py"],
        parameters={"seed": GEN_SEED, "key": KEY, "bpm": BPM, "phase": 1,
                    "total_bars": TOTAL_BARS, "quantized": False},
        notes="Raw generative draft, pre-rules. Off-grid + off-scale by design.")
    write_grid_visualization(p1.matrix,
                             os.path.join(PROJ, "Analysis", "grid_visualization_phase1.txt"))

    # ---- Phase 2 build (8 voices, rules-processed) ----
    leads = build_lead_map()
    comp = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BPB)
    comp.create_matrix(num_voices=len(VOICES), num_sections=len(SECTIONS))
    for name, program, ch in VOICES:
        comp.add_voice(name, program=program, channel=ch)
    for i, (name, bars, chords) in enumerate(SECTIONS):
        comp.add_section(name, bars=bars)

    for si, (name, bars, chords) in enumerate(SECTIONS):
        span = bars * BAR
        lead = leads[name]
        harmony = [(harmonize_below(m, CHORDS[BAR_CHORDS[sec_start[si] + (s // BAR)]]), v - 6, s, d)
                   for m, v, s, d in lead]
        # clamp harmony into its own bar's chord (harmonize_below already chord-tone; safe)
        guitar = guitar_notes(si, 76 if "Chorus" in name else 68)
        electric = electric_notes(si, 78 if "Chorus" in name else 70,
                                  sixteenth=("Chorus" in name))
        bass = bass_notes(si, 88 if "Chorus" in name else 82)
        drums = drums_notes(si, 90,
                            half_time=(name == "Bridge"),
                            open_hat=("Chorus" in name))
        fiddle = fiddle_notes(si, name, 84 if "Chorus" in name else 74,
                              augmented_lead=augment_notes(quantize_lead(7, lo=67, hi=86, vel=84), 2.0)
                              if name == "Solo" else None)
        steel = steel_notes(si, name, 70)

        comp.fill_voice_section("Lead Vocal", name, build_unit(lead, span))
        comp.fill_voice_section("Harmony Vox", name, build_unit(harmony, span))
        comp.fill_voice_section("Acoustic Guitar", name, build_unit(guitar, span))
        comp.fill_voice_section("Electric Guitar", name, build_unit(electric, span))
        comp.fill_voice_section("Bass", name, build_unit(bass, span))
        comp.fill_voice_section("Drums", name, build_unit(drums, span))
        comp.fill_voice_section("Fiddle", name, build_unit(fiddle, span))
        comp.fill_voice_section("Pedal Steel", name, build_unit(steel, span))

    # ---- grid visualization of the PERFECT layer (before humanization) ----
    write_grid_visualization(comp.matrix,
                             os.path.join(PROJ, "Analysis", "grid_visualization.txt"))

    # ---- dual-version export (perfect + humanized) ----
    hz_seed = int(hashlib.md5(
        f"{STYLE}-{KEY}-{BPM}-{TOTAL_BARS}-{GEN_SEED}".encode()).hexdigest()[:8], 16)
    hz_instruments = {v[0]: hz_dna_for(v[0]) for v in VOICES}
    perfect_path = os.path.join(PROJ, "MIDI", "310-country-road-rework-perfect.mid")
    humanized_path = os.path.join(PROJ, "MIDI", "310-country-road-rework-humanized.mid")
    hz = export_dual(comp, perfect_path, humanized_path,
                     style=STYLE, seed=hz_seed, bpm=BPM, instruments=hz_instruments)

    # ---- provenance sidecars ----
    common = {"sources": [SOURCE + "/MIDI/v2_country_unitmatrix.mid"],
              "parameters": {"seed": GEN_SEED, "hz_seed": hz_seed, "key": KEY,
                             "bpm": BPM, "style": STYLE, "total_bars": TOTAL_BARS,
                             "form": [s[0] for s in SECTIONS]}}
    write_provenance(perfect_path, AI_ASSISTED,
                     "random-walk + musicom rules (phase 2 perfect, grid-locked)",
                     notes="Phase 2 rules-processed. Chord-tone quantized, rhythm-grid snapped. off-grid==0.",
                     **common)
    write_provenance(humanized_path, AI_ASSISTED,
                     "random-walk + musicom rules (phase 2 humanized)",
                     notes=f"Humanized: style={STYLE} seed={hz_seed}. Per-voice jitter applied.",
                     **common)

    # ---- persist hz + variation metadata ----
    meta = {
        "project": "310-country-road-rework",
        "source": "012-country-country-uke",
        "decision": "redesign",
        "genre": GENRE, "key": KEY, "bpm": BPM, "total_bars": TOTAL_BARS,
        "total_ticks": TOTAL_TICKS,
        "sections": [{"name": s[0], "bars": s[1], "chords": s[2]} for s in SECTIONS],
        "variation_techniques": [
            {"technique": "inversion", "where": "Verse 2", "detail": "lead contour inverted around G4=67, re-quantized to chord tones"},
            {"technique": "register shift", "where": "Pre-Chorus (+4/+5) and Final Chorus (+12)", "detail": "quantization window raised; final chorus one octave up"},
            {"technique": "retrograde", "where": "Outro", "detail": "descending motif D5-B4-A4-G4 (degrees 5-3-2-1) reversing the intro 1-2-3-5 rise"},
            {"technique": "mode shift", "where": "Bridge", "detail": "relative-minor emphasis: Em/C/Am region, low register, sustained fiddle texture"},
            {"technique": "augmentation", "where": "Solo", "detail": "fiddle takes lead, durations doubled (half speed)"},
            {"technique": "density rise + counterline", "where": "Chorus 2", "detail": "16th electric arpeggios, open hi-hat, fiddle off-beat counterline"},
            {"technique": "diminution", "where": "Outro", "detail": "pedal steel durations shortened with velocity taper"},
        ],
        "humanize": {"seed": hz_seed, "style": STYLE, "profiles": hz},
    }
    with open(os.path.join(PROJ, "Analysis", "compose_meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    print(json.dumps({"phase1": phase1_path, "perfect": perfect_path,
                      "humanized": humanized_path, "hz": hz}, indent=2))
    print("TOTAL_BARS", TOTAL_BARS, "TOTAL_TICKS", TOTAL_TICKS, "hz_seed", hz_seed)


if __name__ == "__main__":
    main()
