# -*- coding: utf-8 -*-
"""216-lsystem-fractal — Electronic / Method 019 L-System Algorithmic Composition.

Two-phase architecture:
  Phase 1 = raw L-system interval walk (single voice, square lead, unquantized
            chromatic wander, NO harmony). Exported as -phase1.mid.
  Phase 2 = musicom rules: grid-lock (8th=240, 16th=120), chord-tone
            quantization per bar (A natural minor diatonic triads), full
            electronic texture (lead/pad/bass/arp/sparkle/drums), voice-leading
            checks, zero-drift normalize.

Engine only: structures + workflows.unitmatrix_composer + generators.interval_lsystem
+ rules.voice_leading. validate() gate + to_midi(). NO raw mido authoring
(mido used only for READ/verify in render_audio.py).
"""
import os
import json

import numpy as np

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import (
    UnitMatrixComposer, create_empty_unit,
)
from generators.interval_lsystem import IntervalLSystem

# instrument programs (registry source of truth where available; raw GM for
# synth-only voices not present in the 18-instrument registry)
LEAD_PROG = 80   # Lead 1 (square) — L-system fractal melody (raw GM, no registry synth-lead)
PAD_PROG = 90    # Pad 2 (warm) — sustained harmony (raw GM)
BASS_PROG = 38   # Synth Bass 1 — root pulses (raw GM)
ARP_PROG = 7     # Clavi (registry: CLAVI.midi_program = 7)
SPARK_PROG = 8   # Celesta (registry: CELESTA.midi_program = 8)
KIT = {"kick": 36, "snare": 38, "hat_closed": 42, "hat_open": 46}
VEL = {"kick": 100, "snare": 90, "hat_closed": 60, "hat_open": 55}

SEED = 20261001
rng = np.random.default_rng(SEED)

# ---------------------------------------------------------------- project dirs
PROJ = "/opt/data/projects/Styles/Electronic/216-lsystem-fractal"
MIDI_DIR = os.path.join(PROJ, "MIDI")
AUDIO_DIR = os.path.join(PROJ, "Audio")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")
for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
    os.makedirs(d, exist_ok=True)

# ---------------------------------------------------------------- concept
BPM = 120
TPB = 480
BEATS = 4
BAR = TPB * BEATS            # 1920
GRID16 = 120                 # 16th note
GRID8 = 240                  # 8th note
# A natural minor pcs: A B C D E F G = {9,11,0,2,4,5,7}
KEY_PCS = {9, 11, 0, 2, 4, 5, 7}
LEAD_LO, LEAD_HI = 48, 88

# ---------------------------------------------------------------- L-system DNA (method 019)
LSAXIOM = "A"
LSRULES = {"A": "A+B-A-B+A", "B": "A-B+A+B-A"}
LSSYMBOLS = {"+": 2, "-": 1}   # + = +2 semitones (whole), - = +1 semitone
lsys = IntervalLSystem(axiom=LSAXIOM, rules=LSRULES, symbols=LSSYMBOLS)
DELTAS = lsys.generate_deltas(iterations=3)   # 124 self-similar stepwise deltas

# ---------------------------------------------------------------- diatonic chords (A natural minor)
# notes: ascending chord-tone pool used for quantization + voicing
CHORD_TONES = {
    "Am":    {"pcs": {9, 0, 4},    "notes": [45, 48, 52, 57, 60, 64, 69, 72, 76], "bass": 33},
    "Bdim":  {"pcs": {11, 2, 5},   "notes": [47, 50, 53, 59, 62, 65, 71, 74],      "bass": 35},
    "C":     {"pcs": {0, 4, 7},    "notes": [48, 52, 55, 60, 64, 67, 72, 76],      "bass": 36},
    "Dm":    {"pcs": {2, 5, 9},    "notes": [50, 53, 57, 62, 65, 69, 74],          "bass": 38},
    "Em":    {"pcs": {4, 7, 11},   "notes": [52, 55, 59, 64, 67, 71, 76],          "bass": 40},
    "F":     {"pcs": {5, 9, 0},    "notes": [53, 57, 60, 65, 69, 72, 77],          "bass": 41},
    "G":     {"pcs": {7, 11, 2},   "notes": [55, 59, 62, 67, 71, 74, 79],          "bass": 43},
}

# ---------------------------------------------------------------- sections (8 x 4 bars = 32)
# per-section 4-bar progression; each section its OWN harmonic region, varied
# start degrees (never all tonic). variation technique documented per section.
SECTIONS = [
    # name       prog (4 chords)             variation technique              density(perc)
    ("Intro",    ["Am", "Am", "Am", "Am"],  "sparse drone, no drums",         0.0),
    ("VerseA",   ["Am", "F", "C", "G"],     "baseline L-system deltas",       0.5),
    ("VerseB",   ["F", "Am", "G", "C"],     "retrograde deltas",              0.6),
    ("Chorus",   ["F", "C", "G", "Am"],     "full texture",                   0.9),
    ("Drop",     ["Am", "Em", "F", "G"],    "augmentation (durations x2)",    0.8),
    ("Bridge",   ["F", "G", "Am", "Em"],    "inversion (negate deltas)",      0.6),
    ("Climax",   ["Am", "F", "C", "G"],     "register shift +12, full drums", 1.0),
    ("Outro",    ["Am", "Am", "Am", "Am"],  "diminution (durations x0.5)",    0.3),
]
N_SECTIONS = len(SECTIONS)
BARS_PER = 4
N_BARS = N_SECTIONS * BARS_PER               # 32
SECTION_TICKS = BAR * BARS_PER               # 7680

PROG = []
for _name, progs, _v, _d in SECTIONS:
    PROG.extend(progs)
assert len(PROG) == N_BARS, (len(PROG), N_BARS)


def chord_for_bar(bar):
    return CHORD_TONES[PROG[min(bar, N_BARS - 1)]]


def quantize_to_chord(pitch, chord):
    return min(chord["notes"], key=lambda c: (abs(c - pitch), c))


def section_midpoint_name(s):
    mid_bar = s * BARS_PER + 2
    return PROG[mid_bar]


# ---------------------------------------------------------------- L-system per-section deltas
def retrograde(deltas):
    return list(reversed(deltas))


def invert(deltas):
    return [-d for d in deltas]


SEC_DELTAS = {
    0: DELTAS, 1: DELTAS, 2: retrograde(DELTAS), 3: DELTAS,
    4: DELTAS, 5: invert(DELTAS), 6: DELTAS, 7: DELTAS,
}
SEC_STEP = {0: 240, 1: 240, 2: 240, 3: 240, 4: 480, 5: 240, 6: 240, 7: 120}
SEC_SHIFT = {6: 12}  # register shift +12 in Climax


# ---------------------------------------------------------------- phase 1: raw walk
def raw_lsystem_walk(seed, duration_ticks, deltas, step_dur=240, jitter=True):
    """Single-voice raw L-system interval walk, unquantized + chromatic wander."""
    r = np.random.default_rng(seed)
    events = []
    tick = 0
    center = 69.0
    i = 0
    while tick < duration_ticks - 120:
        d = deltas[i % len(deltas)]
        p = center + d
        if jitter:
            p += r.normal(0.0, 0.9)
        p = max(LEAD_LO, min(LEAD_HI, p))
        midi = int(round(p))
        dur = step_dur + (int(r.normal(0, 18)) if jitter else 0)
        dur = max(60, dur)
        onset = tick + (int(r.normal(0, 18)) if jitter else 0)
        onset = max(0, onset)
        end = onset + dur
        if end > duration_ticks:
            end = duration_ticks
        if end > onset:
            events.append(MusicEvent(pitch=midi, volume=90,
                                     start_tick=onset, end_tick=end))
        tick += dur
        center = p
        i += 1
        if i > 2000:
            break
    return events


def quantize_lead_to_grid(events, grid=GRID16):
    q = []
    for e in events:
        if e.pitch == 0:
            q.append(e)
            continue
        st = int(round(e.start_tick / grid) * grid)
        q.append(MusicEvent(pitch=e.pitch, volume=e.volume,
                            start_tick=st, end_tick=max(st + 1, e.end_tick)))
    return q


phase1 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
phase1.create_matrix(num_voices=1, num_sections=N_SECTIONS)
phase1.add_voice("LeadRaw", program=LEAD_PROG, channel=0)

for s, (name, _p, _v, _d) in enumerate(SECTIONS):
    phase1.add_section(name, bars=BARS_PER)
    evs = raw_lsystem_walk(SEED + s, SECTION_TICKS, SEC_DELTAS[s],
                           step_dur=SEC_STEP[s], jitter=True)
    phase1.set_unit(0, s, MusicUnit(events=evs))

for s in range(N_SECTIONS):
    u = phase1.matrix.get_unit((0, s))
    evs = list(u.events)
    if not any(e.pitch == 0 and e.end_tick == SECTION_TICKS for e in evs):
        evs.append(MusicEvent(pitch=0, volume=0, start_tick=SECTION_TICKS - 1,
                              end_tick=SECTION_TICKS))
    phase1.set_unit(0, s, MusicUnit(events=evs))

ok1, msg1 = phase1.validate()
print("PHASE1 validate:", msg1)
P1_MIDI = os.path.join(MIDI_DIR, "216-lsystem-fractal-phase1.mid")
phase1.to_midi(P1_MIDI)
print("phase1 written", P1_MIDI)

# ---------------------------------------------------------------- phase 2: rules
phase2 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
VOICES = [
    ("Lead",    LEAD_PROG,  0),   # L-system fractal lead (square synth)
    ("Pad",     PAD_PROG,   1),   # sustained harmony (warm pad)
    ("Bass",    BASS_PROG,  2),   # synth bass root pulses
    ("Arp",     ARP_PROG,   3),   # clavi 16th arpeggio
    ("Sparkle", SPARK_PROG, 4),   # celesta high accents
    ("Drums",   0,          9),   # percussion
]
N_V = len(VOICES)
phase2.create_matrix(num_voices=N_V, num_sections=N_SECTIONS)
vnames = [v[0] for v in VOICES]
for name, prog, ch in VOICES:
    phase2.add_voice(name, program=prog, channel=ch)
for name, _p, _v, _d in SECTIONS:
    phase2.add_section(name, bars=BARS_PER)


def build_lead(s):
    """Regenerate the raw L-system walk (same seed, NO jitter), grid-lock,
    then chord-quantize to each event's bar chord. Apply section register shift."""
    evs = raw_lsystem_walk(SEED + s, SECTION_TICKS, SEC_DELTAS[s],
                           step_dur=SEC_STEP[s], jitter=False)
    evs = quantize_lead_to_grid(evs, grid=GRID16)
    shift = SEC_SHIFT.get(s, 0)
    q = []
    for e in evs:
        if e.pitch == 0:
            q.append(e)
            continue
        bar = s * BARS_PER + (e.start_tick // BAR)
        chord = chord_for_bar(bar)
        qp = quantize_to_chord(e.pitch + shift, chord)
        q.append(MusicEvent(pitch=qp, volume=e.volume,
                            start_tick=e.start_tick, end_tick=min(e.start_tick + SEC_STEP[s], SECTION_TICKS)))
    # voice-leading: cap consecutive leaps to <= 9 semitones
    for i in range(1, len(q)):
        e = q[i]
        if e.pitch == 0:
            continue
        p_prev = q[i - 1].pitch if q[i - 1].pitch else LEAD_HI
        if abs(e.pitch - p_prev) > 9:
            bar = s * BARS_PER + (e.start_tick // BAR)
            chord = chord_for_bar(bar)
            e.pitch = min(chord["notes"], key=lambda c: (abs(c - p_prev), c))
    return q


for s in range(N_SECTIONS):
    phase2.set_unit(0, s, MusicUnit(events=build_lead(s)))

# --- Pad: sustained chord (root+3rd+5th) per bar
for bar in range(N_BARS):
    s, b = divmod(bar, BARS_PER)
    chord = chord_for_bar(bar)
    notes = chord["notes"]
    root = notes[3] if len(notes) > 3 else notes[0]
    third = min(notes, key=lambda n: abs(n - (root + 3)))
    fifth = min(notes, key=lambda n: abs(n - (root + 7)))
    b0 = b * BAR
    evs = [
        MusicEvent(pitch=root, volume=52, start_tick=b0, end_tick=b0 + BAR - 60),
        MusicEvent(pitch=third, volume=48, start_tick=b0, end_tick=b0 + BAR - 60),
        MusicEvent(pitch=fifth, volume=48, start_tick=b0, end_tick=b0 + BAR - 60),
    ]
    unit = phase2.matrix.get_unit((1, s))
    events = list(unit.events) if unit is not None else []
    events.extend(evs)
    phase2.set_unit(1, s, MusicUnit(events=events))

# --- Bass: 8th-note root pulses with octave bounce
for bar in range(N_BARS):
    s, b = divmod(bar, BARS_PER)
    chord = chord_for_bar(bar)
    bass = chord["bass"]
    t0 = b * BAR
    evs = []
    for k in range(0, BAR, GRID8):
        pitch = bass if (k // GRID8) % 4 != 3 else bass + 12  # octave up on the "and of 4"
        evs.append(MusicEvent(pitch=pitch, volume=86,
                              start_tick=t0 + k, end_tick=t0 + k + GRID8 - 40))
    unit = phase2.matrix.get_unit((2, s))
    events = list(unit.events) if unit is not None else []
    events.extend(evs)
    phase2.set_unit(2, s, MusicUnit(events=events))

# --- Arp: clavi 16th-note arpeggio cycling chord tones (root-3rd-5th-octave)
for s in range(N_SECTIONS):
    evs = []
    for bar_local in range(BARS_PER):
        b0 = bar_local * BAR
        bar = s * BARS_PER + bar_local
        chord = chord_for_bar(bar)
        notes = chord["notes"]
        root = notes[3] if len(notes) > 3 else notes[0]
        third = min(notes, key=lambda n: abs(n - (root + 3)))
        fifth = min(notes, key=lambda n: abs(n - (root + 7)))
        octv = min(notes, key=lambda n: abs(n - (root + 12)))
        pat = [root, third, fifth, octv, fifth, third, root, third]
        for k in range(0, BAR, GRID16):
            tone = pat[(k // GRID16) % len(pat)]
            evs.append(MusicEvent(pitch=tone, volume=70,
                                  start_tick=b0 + k, end_tick=b0 + k + GRID16 - 20))
    phase2.set_unit(3, s, MusicUnit(events=evs))

# --- Sparkle: celesta off-beat high chord-tone accents
for s in range(N_SECTIONS):
    evs = []
    for bar_local in range(BARS_PER):
        b0 = bar_local * BAR
        bar = s * BARS_PER + bar_local
        chord = chord_for_bar(bar)
        high = [n for n in chord["notes"] if n >= 72]
        if not high:
            high = [chord["notes"][-1] + 12]
        for k, off in enumerate((GRID8, GRID8 + GRID16 * 3)):
            tone = high[(k + s) % len(high)]
            evs.append(MusicEvent(pitch=tone, volume=66,
                                  start_tick=b0 + off, end_tick=b0 + off + GRID16))
    phase2.set_unit(4, s, MusicUnit(events=evs))

# --- Drums: four-on-floor kick, snare 2&4, 8th hats, open hat on "and of 4"
for s, (_n, _p, _v, dens) in enumerate(SECTIONS):
    evs = []
    if dens <= 0:
        phase2.set_unit(5, s, create_empty_unit(SECTION_TICKS))
        continue
    for bar in range(BARS_PER):
        t0 = bar * BAR
        for k in range(0, BAR, GRID8):  # closed hat 8ths
            if k % 2 == 1 or dens < 0.9:  # offbeat hats when not full
                evs.append(MusicEvent(pitch=KIT["hat_closed"],
                                      volume=int(VEL["hat_closed"] * (0.6 if k % 2 else 1.0)),
                                      start_tick=t0 + k, end_tick=t0 + k + 70))
        for beat in (0, GRID8 * 2, GRID8 * 4, GRID8 * 6):  # kick every beat
            evs.append(MusicEvent(pitch=KIT["kick"], volume=int(VEL["kick"] * 0.9),
                                  start_tick=t0 + beat, end_tick=t0 + beat + 140))
        if dens >= 0.6:  # snare on 2 & 4
            evs.append(MusicEvent(pitch=KIT["snare"], volume=int(VEL["snare"] * 0.75),
                                  start_tick=t0 + GRID8 * 2, end_tick=t0 + GRID8 * 2 + 140))
            evs.append(MusicEvent(pitch=KIT["snare"], volume=int(VEL["snare"] * 0.75),
                                  start_tick=t0 + GRID8 * 6, end_tick=t0 + GRID8 * 6 + 140))
        if dens >= 1.0:
            evs.append(MusicEvent(pitch=KIT["hat_open"], volume=int(VEL["hat_open"] * 0.8),
                                  start_tick=t0 + GRID8 * 7, end_tick=t0 + GRID8 * 7 + 200))
    phase2.set_unit(5, s, MusicUnit(events=evs))

# --- voice-leading check on Lead
from rules.voice_leading import VoiceLeadingRules  # noqa: E402

vlc = VoiceLeadingRules(style="pop")
vl_flags = []
for s in range(N_SECTIONS):
    u = phase2.matrix.get_unit((0, s))
    evs = [e for e in u.events if e.pitch > 0]
    for i in range(1, len(evs)):
        a, b = evs[i - 1], evs[i]
        if vlc.check_hidden_fifths([a.pitch], [b.pitch]):
            vl_flags.append((s, a.pitch, b.pitch))
print("VOICE-LEADING flags (Lead):", vl_flags[:6], "total", len(vl_flags))

# --- normalize every cell to exact section boundary (zero-drift)
def normalize_cell(unit, total_ticks):
    evs = list(unit.events)
    for e in evs:
        if e.end_tick > total_ticks:
            e.end_tick = total_ticks
    if not any(e.pitch == 0 and e.end_tick == total_ticks for e in evs):
        evs.append(MusicEvent(pitch=0, volume=0, start_tick=total_ticks - 1,
                              end_tick=total_ticks))
    return MusicUnit(events=evs)


for v in range(N_V):
    for s in range(N_SECTIONS):
        u = phase2.matrix.get_unit((v, s))
        if u is None or len(u.events) == 0:
            phase2.set_unit(v, s, create_empty_unit(SECTION_TICKS))
        else:
            phase2.set_unit(v, s, normalize_cell(u, SECTION_TICKS))

ok2, msg2 = phase2.validate()
print("PHASE2 validate:", msg2)
assert ok1 and ok2, (msg1, msg2)

P2_MIDI = os.path.join(MIDI_DIR, "216-lsystem-fractal.mid")
phase2.to_midi(P2_MIDI)
print("phase2 written", P2_MIDI)

# ---------------------------------------------------------------- grid visualization
from visualization.grid import write_grid_visualization  # noqa: E402

grid_path = os.path.join(ANALYSIS_DIR, "grid_visualization.txt")
write_grid_visualization(phase2.matrix, grid_path, ticks_per_character=120,
                         voice_names=vnames, bpm=BPM,
                         mode="A natural minor / Method 019 L-System (fractal)")
print("grid written", grid_path)

# ---------------------------------------------------------------- provenance
from workflows.provenance import write_provenance, AI_GENERATED  # noqa: E402

section_mid = [section_midpoint_name(s) for s in range(N_SECTIONS)]
print("SECTION MIDPOINT CHORDS:", section_mid)
print("SECTION START DEGREES:", [SECTIONS[s][1][0] for s in range(N_SECTIONS)])

for mid, phase, note in (
        (P1_MIDI, "1", "raw L-system interval walk, unquantized chromatic, single voice, no harmony"),
        (P2_MIDI, "2", "grid-locked + chord-quantized A-natural-minor, full 6-voice electronic texture, voice-leading, 8 sections")) :
    write_provenance(
        mid, AI_GENERATED,
        "L-System Algorithmic Composition (Method 019, generators.interval_lsystem) + musicom rules",
        parameters={"bpm": BPM, "key": "A natural minor", "sections": N_SECTIONS,
                    "bars": N_BARS, "phase": phase,
                    "lsystem": {"axiom": LSAXIOM, "rules": LSRULES, "symbols": LSSYMBOLS,
                                "iterations": 3, "n_deltas": len(DELTAS)},
                    "progression": PROG,
                    "section_midpoint_chords": section_mid,
                    "variations": [SECTIONS[s][2] for s in range(N_SECTIONS)],
                    "seed": SEED},
        notes=note)
    print("provenance for phase", phase)

# ---------------------------------------------------------------- summary
summary = {
    "project": "216-lsystem-fractal",
    "style": "Electronic",
    "method": "019 L-System Algorithmic Composition (IntervalLSystem)",
    "bpm": BPM, "key": "A natural minor", "pcs": sorted(KEY_PCS),
    "bars": N_BARS, "sections": N_SECTIONS,
    "section_names": [SECTIONS[s][0] for s in range(N_SECTIONS)],
    "section_progressions": [SECTIONS[s][1] for s in range(N_SECTIONS)],
    "section_variations": [SECTIONS[s][2] for s in range(N_SECTIONS)],
    "section_midpoint_chords": section_mid,
    "progression": PROG,
    "voices": vnames,
    "lsystem_deltas_sample": DELTAS[:24],
    "phase1": os.path.basename(P1_MIDI),
    "phase2": os.path.basename(P2_MIDI),
    "grid": os.path.basename(grid_path),
    "seed": SEED,
}
with open(os.path.join(ANALYSIS_DIR, "summary.json"), "w") as f:
    json.dump(summary, f, indent=2)

for p in (P1_MIDI, P2_MIDI, grid_path, os.path.join(ANALYSIS_DIR, "summary.json")):
    assert os.path.getsize(p) > 40, "too small: %s" % p
print("ALL SIZE ASSERTS PASSED")
print("PROGRESSION:", PROG)
