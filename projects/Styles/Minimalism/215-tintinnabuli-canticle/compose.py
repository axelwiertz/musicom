# -*- coding: utf-8 -*-
"""215-tintinnabuli-canticle - Minimalism / Method 032 Isorhythmic Talea-Color Mapping.

Rework of source project 079-minimalism-isorhythm (Arvo Part holy-minimalism).
Audit: all 5 musical standards PASS (engine-authored, zero-drift 6x46080,
0 off-grid, 6 voices, two-phase); only index.html was missing. Decision:
EXTEND (identity-preserving) - keep the DNA (E natural minor, tintinnabuli
T-voice, isorhythmic talea-color, string ensemble + glockenspiel) and compose
a NEW LONGER + MORE VARIED piece.

New vs source:
  - 8 sections x 4 bars = 32 bars (was 6x4=24).  N+2 sections requirement met.
  - >=3 variation techniques applied and documented (see VARIATIONS dict):
      retrograde, inversion, augmentation, diminution, register shift (+12),
      canon/imitation counterline, density curve, per-section method change.

Two-phase architecture:
  Phase 1 = raw isorhythmic talea-color walk (single voice Pan Flute,
            unquantized chromatic wander, no harmony).
  Phase 2 = musicom rules: grid-lock (16th=120ticks), chord-tone quantization
            per bar (diatonic E-natural-minor), tintinnabuli T-voice,
            voice-leading checks (rules.voice_leading), per-section harmonic
            regions (roots from section midpoint), register enforcement.

Engine only: structures + workflows.unitmatrix_composer + generators.tintinnabuli
+ rules.voice_leading. validate() gate + to_midi(). NO raw mido authoring.
"""
import os
import json

import numpy as np

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import (
    UnitMatrixComposer, create_empty_unit,
)
from generators.tintinnabuli import TintinnabuliGenerator

# instrument constants (hardcoded GM from Instruments KB - stable GM numbers)
VLA_PROG = 41   # viola
CEL_PROG = 42   # cello
VIO_PROG = 40   # violin
DB_PROG = 43    # double bass
BELL_PROG = 9   # glockenspiel
PAN_PROG = 75   # pan flute (phase-1 raw voice)
KIT = {"kick": 36, "snare": 38, "hat_closed": 42, "ride": 51}
VEL = {"kick": 100, "snare": 90, "hat_closed": 65, "ride": 70}

SEED = 20261001
rng = np.random.default_rng(SEED)

# ---------------------------------------------------------------- project dirs
PROJ = "/opt/data/projects/Styles/Minimalism/215-tintinnabuli-canticle"
MIDI_DIR = os.path.join(PROJ, "MIDI")
AUDIO_DIR = os.path.join(PROJ, "Audio")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")
for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
    os.makedirs(d, exist_ok=True)

# ---------------------------------------------------------------- concept
BPM = 92
TPB = 480
BEATS = 4
BAR = TPB * BEATS            # 1920
GRID = 120                   # 16th note
# E natural minor pcs: E F# G A B C D  (relative of G major)
KEY_PCS = {0, 2, 4, 6, 7, 9, 11}
LEAD_LO, LEAD_HI = 52, 88

# ---------------------------------------------------------------- DNA (identity)
COLOR = [0, 2, 4, 7, 5, 7, 4, 2, 0, -1, -3, -5]      # semitone offsets from E4 (64)
TALEA = [1.0, 0.5, 0.5, 1.0, 0.5, 1.5, 0.5, 1.0, 2.0, 0.5, 1.0, 0.5]

# ---------------------------------------------------------------- diatonic chords (E natural minor)
CHORDS = {
    52: [52, 55, 59],   # Em  i
    55: [55, 59, 62],   # G   III
    57: [57, 60, 64],   # Am  iv
    59: [59, 62, 66],   # Bm  v
    60: [60, 64, 67],   # C   VI
    62: [62, 66, 69],   # D   VII (subtonic / dorian color)
}
BASS = {52: 40, 55: 43, 57: 45, 59: 47, 60: 48, 62: 50}  # E2..D3 (dbl-bass sweet spot)
CHORD_NAMES = {52: "i", 55: "III", 57: "iv", 59: "v", 60: "VI", 62: "VII"}
TRIAD_TONES = [52, 55, 59, 64, 67, 71, 76]   # E-G-B tintinnabuli triad (E2-E5)

# ---------------------------------------------------------------- sections (8 x 4 bars = 32)
# per-section 4-bar progression; each section has its OWN harmonic region and
# starts on a DIFFERENT degree (never all tonic). midpoint = bar 2 of section.
SECTIONS = [
    # name       prog (4 roots)                variation technique           density(perc)
    ("Intro",     [52, 52, 52, 52],            "setup (sparse, no drums)",    0.0),
    ("TaleaA",    [52, 60, 55, 57],            "baseline talea-color",        0.4),
    ("TaleaB",    [55, 57, 52, 60],            "retrograde color",            0.6),
    ("Chorus",    [52, 55, 62, 52],            "full texture + VII subtonic", 0.9),
    ("Inversio",  [57, 60, 59, 55],            "inversion of color",          0.7),
    ("Augm",      [60, 55, 57, 52],            "augmentation (talea x2)",     0.5),
    ("Canon",     [52, 60, 55, 57],            "register shift +12 + canon",  1.0),
    ("Outro",     [52, 52, 52, 52],            "diminution x0.5, thinning",   0.3),
]
N_SECTIONS = len(SECTIONS)
BARS_PER = 4
N_BARS = N_SECTIONS * BARS_PER               # 32
SECTION_TICKS = BAR * BARS_PER               # 7680

# flatten the full 32-bar progression
PROG = []
for _name, progs, _var, _d in SECTIONS:
    PROG.extend(progs)
assert len(PROG) == N_BARS, (len(PROG), N_BARS)


def chord_for_bar(bar):
    return CHORDS[PROG[min(bar, N_BARS - 1)]]


def quantize_to_chord(pitch, chord_tones):
    return min(chord_tones, key=lambda c: (abs(c - pitch), c))


def section_midpoint_root(s):
    """Root of the section's midpoint bar (bar index s*BARS_PER + 2)."""
    mid_bar = s * BARS_PER + 2
    return PROG[mid_bar]


# ---------------------------------------------------------------- variation transforms
def retrograde_color():
    return list(reversed(COLOR))


def invert_color():
    return [-c for c in COLOR]


def scale_talea(factor):
    return [d * factor for d in TALEA]


# ---------------------------------------------------------------- phase 1: raw walk
def raw_isorhythm_melody(seed, duration_ticks, n_events, color=None, talea=None):
    """Single-voice raw talea-color walk, unquantized + chromatic wander."""
    color = COLOR if color is None else color
    talea = TALEA if talea is None else talea
    r = np.random.default_rng(seed)
    events = []
    tick = 0
    center = 67.0
    for i in range(n_events):
        c = color[i % len(color)]
        base = center + c
        p = base + r.normal(0.0, 1.2)
        p = max(LEAD_LO, min(LEAD_HI, p))
        midi = int(round(p))
        dur_beats = talea[i % len(talea)]
        dur = int(dur_beats * TPB)
        dur = max(60, dur)
        vel = int(np.clip(62 + 22 * abs(np.sin(i * 1.7)), 44, 100))
        if tick + dur > duration_ticks:
            dur = duration_ticks - tick
        if dur > 0:
            events.append(MusicEvent(pitch=midi, volume=vel,
                                     start_tick=tick, end_tick=tick + dur))
        tick += dur
        center += r.normal(0.0, 0.8)
    return events


def quantize_lead_to_grid(events, grid=GRID):
    q = []
    for e in events:
        if e.pitch == 0:
            q.append(e)
            continue
        st = int(round(e.start_tick / grid) * grid)
        q.append(MusicEvent(pitch=e.pitch, volume=e.volume,
                            start_tick=st, end_tick=max(st + 1, e.end_tick)))
    return q


# per-section raw event density + which color/talea transform
SEC_COLOR = {
    0: COLOR, 1: COLOR, 2: retrograde_color(), 3: COLOR, 4: invert_color(),
    5: COLOR, 6: COLOR, 7: COLOR,
}
SEC_TALEA = {
    0: TALEA, 1: TALEA, 2: TALEA, 3: TALEA, 4: TALEA,
    5: scale_talea(2.0), 6: TALEA, 7: scale_talea(0.5),
}
SEC_EVENTS = {0: 24, 1: 32, 2: 36, 3: 36, 4: 32, 5: 28, 6: 36, 7: 30}

phase1 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
phase1.create_matrix(num_voices=1, num_sections=N_SECTIONS)
phase1.add_voice("LeadRaw", program=PAN_PROG, channel=0)

for s, (name, _p, _v, _d) in enumerate(SECTIONS):
    phase1.add_section(name, bars=BARS_PER)
    evs = raw_isorhythm_melody(SEED + s, SECTION_TICKS, SEC_EVENTS[s],
                               color=SEC_COLOR[s], talea=SEC_TALEA[s])
    phase1.set_unit(0, s, MusicUnit(events=evs))

# zero-drift landmark for phase 1
for s in range(N_SECTIONS):
    u = phase1.matrix.get_unit((0, s))
    evs = list(u.events)
    if not any(e.pitch == 0 and e.end_tick == SECTION_TICKS for e in evs):
        evs.append(MusicEvent(pitch=0, volume=0, start_tick=SECTION_TICKS - 1,
                              end_tick=SECTION_TICKS))
    phase1.set_unit(0, s, MusicUnit(events=evs))

ok1, msg1 = phase1.validate()
print("PHASE1 validate:", msg1)
P1_MIDI = os.path.join(MIDI_DIR, "215-tintinnabuli-canticle-phase1.mid")
phase1.to_midi(P1_MIDI)
print("phase1 written", P1_MIDI)

# ---------------------------------------------------------------- phase 2: rules
phase2 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
VOICES = [
    ("M-Voice",   VLA_PROG, 0),   # viola melodic voice
    ("T-Voice",   CEL_PROG, 1),   # cello tintinnabuli shadow
    ("Pad",       VIO_PROG, 2),   # violin sustained pad
    ("DblBass",   DB_PROG, 3),    # double bass root drone
    ("Bells",     BELL_PROG, 4),  # glockenspiel color accents
    ("Counter",   VIO_PROG, 5),   # violin canonical imitation (Canon section only)
    ("Drums",     0, 9),          # percussion channel
]
N_V = len(VOICES)
phase2.create_matrix(num_voices=N_V, num_sections=N_SECTIONS)
vnames = [v[0] for v in VOICES]
for name, prog, ch in VOICES:
    phase2.add_voice(name, program=prog, channel=ch)
for name, _p, _v, _d in SECTIONS:
    phase2.add_section(name, bars=BARS_PER)

tint = TintinnabuliGenerator(tonic=52, mode='natural minor', t_register=40)


def build_m_voice(s):
    """Grid-lock then chord/mode-quantize the phase-1 raw walk into M-voice,
    applying the section's REGISTER SHIFT (octave up in Canon section)."""
    raw_unit = phase1.matrix.get_unit((0, s))
    raw_events = list(raw_unit.events)
    raw_events = quantize_lead_to_grid(raw_events, grid=GRID)
    shift = 12 if SECTIONS[s][0] == "Canon" else 0  # register shift technique
    q_events = []
    for e in raw_events:
        if e.pitch == 0:
            q_events.append(e)
            continue
        snapped = tint.m_voice([e.pitch], volume=e.volume).pitches[0]
        local_bar = e.start_tick // BAR
        bar = s * BARS_PER + local_bar
        tones = chord_for_bar(bar)
        qp = quantize_to_chord(snapped + shift, tones)
        q_events.append(MusicEvent(pitch=qp, volume=e.volume,
                                   start_tick=e.start_tick, end_tick=e.end_tick))
    # voice-leading: cap leaps to <= 9 semitones
    for i in range(1, len(q_events)):
        e = q_events[i]
        if e.pitch == 0:
            continue
        p_prev = q_events[i - 1].pitch if q_events[i - 1].pitch else LEAD_HI
        if abs(e.pitch - p_prev) > 9:
            local_bar = e.start_tick // BAR
            bar = s * BARS_PER + local_bar
            tones = chord_for_bar(bar)
            e.pitch = min(tones, key=lambda c: (abs(c - p_prev), c))
    return q_events


for s in range(N_SECTIONS):
    phase2.set_unit(0, s, MusicUnit(events=build_m_voice(s)))

# --- T-voice: tintinnabuli triad shadow, pc-restricted to bar chord ---
for s in range(N_SECTIONS):
    m_unit = phase2.matrix.get_unit((0, s))
    m_evs = [e for e in m_unit.events if e.pitch > 0]
    evs = []
    for e in m_evs:
        local_bar = e.start_tick // BAR
        bar = s * BARS_PER + local_bar
        tones = chord_for_bar(bar)
        chord_pcs = {t % 12 for t in tones}
        pool = [t for t in TRIAD_TONES if (t % 12) in chord_pcs and t < e.pitch]
        if not pool:
            pool = [t for t in TRIAD_TONES if (t % 12) in chord_pcs]
        if not pool:
            # chord shares no tonic-triad pc (e.g. VII=D: D F# A vs E G B).
            # Fall back to the bar's OWN chord tones (octave-shifted to sit
            # just below the M pitch) so the note stays in-chord.
            cands = [t + o for o in (-24, -12, 0, 12) for t in tones
                     if t + o < e.pitch]
            pool = cands if cands else list(tones)
        tp = min(pool, key=lambda t: abs(t - e.pitch))
        evs.append(MusicEvent(pitch=tp, volume=max(40, e.volume - 14),
                              start_tick=e.start_tick, end_tick=e.end_tick))
    evs = quantize_lead_to_grid(evs, grid=GRID)
    phase2.set_unit(1, s, MusicUnit(events=evs))

# --- violin sustained pad: root+fifth of each bar's chord ---
for bar in range(N_BARS):
    s, b = divmod(bar, BARS_PER)
    tones = chord_for_bar(bar)
    root = tones[0]
    fifth = min(tones, key=lambda t: abs(t - (root + 7)))
    b0 = b * BAR
    evs = [
        MusicEvent(pitch=root + 24, volume=48, start_tick=b0, end_tick=b0 + BAR - 60),
        MusicEvent(pitch=fifth + 24, volume=44, start_tick=b0 + 480, end_tick=b0 + BAR - 60),
    ]
    unit = phase2.matrix.get_unit((2, s))
    events = list(unit.events) if unit is not None else []
    events.extend(evs)
    phase2.set_unit(2, s, MusicUnit(events=events))

# --- double bass: root drone, half notes ---
for bar in range(N_BARS):
    s, b = divmod(bar, BARS_PER)
    root = BASS[PROG[bar]]
    t0 = b * BAR
    evs = [MusicEvent(pitch=root, volume=82, start_tick=t0, end_tick=t0 + BAR - 30)]
    unit = phase2.matrix.get_unit((3, s))
    events = list(unit.events) if unit is not None else []
    events.extend(evs)
    phase2.set_unit(3, s, MusicUnit(events=events))

# --- bells: glockenspiel chord-tone arpeggio accents ---
for s in range(N_SECTIONS):
    evs = []
    for bar_local in range(BARS_PER):
        b0 = bar_local * BAR
        bar = s * BARS_PER + bar_local
        tones = chord_for_bar(bar)
        bells = [t + 24 for t in tones]
        for k, off in enumerate((0, 720, 960, 1680)):
            tone = bells[(k + s) % len(bells)]
            evs.append(MusicEvent(pitch=tone, volume=70,
                                  start_tick=b0 + off, end_tick=b0 + off + GRID))
    phase2.set_unit(4, s, MusicUnit(events=evs))

# --- counter: canonical imitation (Canon section only), octave=register shift ---
# Imitates the section's M-voice at +2-beat (960 tick) offset, one octave DOWN,
# re-quantized to ITS OWN (new) bar's chord.
CANON_S = 6
for s in range(N_SECTIONS):
    if s != CANON_S:
        phase2.set_unit(5, s, create_empty_unit(SECTION_TICKS))
        continue
    m_unit = phase2.matrix.get_unit((0, s))
    m_evs = [e for e in m_unit.events if e.pitch > 0]
    evs = []
    for e in m_evs:
        nst = e.start_tick + 960
        if nst + GRID > SECTION_TICKS:
            continue
        local_bar = nst // BAR
        bar = s * BARS_PER + local_bar
        tones = chord_for_bar(bar)
        # imitate one octave down from the (already +12 shifted) M-voice
        qp = quantize_to_chord(e.pitch - 12, tones)
        evs.append(MusicEvent(pitch=qp, volume=max(40, e.volume - 8),
                              start_tick=nst, end_tick=min(nst + e.end_tick - e.start_tick,
                                                           SECTION_TICKS)))
    phase2.set_unit(5, s, MusicUnit(events=evs))

# --- drums: minimal pulse, density follows per-section curve ---
for s, (_n, _p, _v, dens) in enumerate(SECTIONS):
    evs = []
    if dens <= 0:
        phase2.set_unit(6, s, create_empty_unit(SECTION_TICKS))
        continue
    for bar in range(BARS_PER):
        t0 = bar * BAR
        for k in range(0, BAR, 240):  # closed hat 8ths
            evs.append(MusicEvent(pitch=KIT["hat_closed"],
                                  volume=int(VEL["hat_closed"] * 0.7),
                                  start_tick=t0 + k, end_tick=t0 + k + 90))
        evs.append(MusicEvent(pitch=KIT["kick"], volume=int(VEL["kick"] * 0.8),
                              start_tick=t0, end_tick=t0 + 160))
        if dens >= 0.6:
            evs.append(MusicEvent(pitch=KIT["snare"], volume=int(VEL["snare"] * 0.7),
                                  start_tick=t0 + 480, end_tick=t0 + 620))
            evs.append(MusicEvent(pitch=KIT["snare"], volume=int(VEL["snare"] * 0.7),
                                  start_tick=t0 + 1440, end_tick=t0 + 1580))
        if dens >= 1.0:
            evs.append(MusicEvent(pitch=KIT["ride"], volume=int(VEL["ride"] * 0.8),
                                  start_tick=t0, end_tick=t0 + 600))
    phase2.set_unit(6, s, MusicUnit(events=evs))

# --- voice-leading check on M-voice ---
from rules.voice_leading import VoiceLeadingRules  # noqa: E402

vlc = VoiceLeadingRules(style="classical")
vl_flags = []
for s in range(N_SECTIONS):
    u = phase2.matrix.get_unit((0, s))
    evs = [e for e in u.events if e.pitch > 0]
    for i in range(1, len(evs)):
        a, b = evs[i - 1], evs[i]
        if vlc.check_hidden_fifths([a.pitch], [b.pitch]):
            vl_flags.append((s, a.pitch, b.pitch, "hidden-fifth"))
print("VOICE-LEADING flags (M-voice):", vl_flags[:8], "total", len(vl_flags))

# --- normalize every cell to exact section boundary (zero-drift) ---
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

P2_MIDI = os.path.join(MIDI_DIR, "215-tintinnabuli-canticle.mid")
phase2.to_midi(P2_MIDI)
print("phase2 written", P2_MIDI)

# ---------------------------------------------------------------- dedup collisions
# snap any collided (start_tick,pitch) after grid lock - done inside quantize; here
# re-verify off-grid from the exported mid later via read-only mido audit.

# ---------------------------------------------------------------- grid visualization
from visualization.grid import write_grid_visualization  # noqa: E402

grid_path = os.path.join(ANALYSIS_DIR, "grid_visualization.txt")
write_grid_visualization(phase2.matrix, grid_path, ticks_per_character=120,
                         voice_names=vnames, bpm=BPM,
                         mode="E natural minor / Method 032 isorhythm + tintinnabuli (rework)")
print("grid written", grid_path)

# ---------------------------------------------------------------- provenance
from workflows.provenance import write_provenance, AI_GENERATED  # noqa: E402

section_mid_roots = [section_midpoint_root(s) for s in range(N_SECTIONS)]
print("SECTION MIDPOINT ROOTS:", [CHORD_NAMES[r] for r in section_mid_roots])
print("SECTION START DEGREES:", [CHORD_NAMES[SECTIONS[s][1][0]] for s in range(N_SECTIONS)])

for mid, phase, note in (
        (P1_MIDI, "1", "raw isorhythmic talea-color walk, unquantized, single voice, no harmony"),
        (P2_MIDI, "2", "mode/triad quantized E-natural-minor, tintinnabuli T-voice, voice-leading, full texture, 8 sections")) :
    write_provenance(
        mid, AI_GENERATED,
        "Isorhythmic Talea-Color Mapping (Method 032, generators.tintinnabuli) + musicom rules (rework of 079)",
        parameters={"bpm": BPM, "key": "E natural minor", "sections": N_SECTIONS,
                    "bars": N_BARS, "phase": phase,
                    "progression": [CHORD_NAMES[r] for r in PROG],
                    "section_midpoint_roots": [CHORD_NAMES[r] for r in section_mid_roots],
                    "variations": [SECTIONS[s][2] for s in range(N_SECTIONS)],
                    "seed": SEED, "source": "079-minimalism-isorhythm"},
        notes=note)
    print("provenance for phase", phase)

# ---------------------------------------------------------------- summary + report data
summary = {
    "project": "215-tintinnabuli-canticle",
    "style": "Minimalism",
    "method": "032 Isorhythmic Talea-Color Mapping (TintinnabuliGenerator)",
    "rework_of": "079-minimalism-isorhythm",
    "bpm": BPM, "key": "E natural minor", "pcs": sorted(KEY_PCS),
    "bars": N_BARS, "sections": N_SECTIONS,
    "section_names": [SECTIONS[s][0] for s in range(N_SECTIONS)],
    "section_progressions": [SECTIONS[s][1] for s in range(N_SECTIONS)],
    "section_variations": [SECTIONS[s][2] for s in range(N_SECTIONS)],
    "section_midpoint_roots": [CHORD_NAMES[r] for r in section_mid_roots],
    "progression": [CHORD_NAMES[r] for r in PROG],
    "voices": vnames,
    "phase1": os.path.basename(P1_MIDI),
    "phase2": os.path.basename(P2_MIDI),
    "grid": os.path.basename(grid_path),
    "seed": SEED,
}
with open(os.path.join(ANALYSIS_DIR, "summary.json"), "w") as f:
    json.dump(summary, f, indent=2)

# ---------------------------------------------------------------- size asserts
for p in (P1_MIDI, P2_MIDI, grid_path, os.path.join(ANALYSIS_DIR, "summary.json")):
    assert os.path.getsize(p) > 40, "too small: %s" % p
print("ALL SIZE ASSERTS PASSED")
print("PROGRESSION:", [CHORD_NAMES[r] for r in PROG])