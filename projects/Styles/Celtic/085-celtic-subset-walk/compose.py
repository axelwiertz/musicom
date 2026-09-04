#!/opt/data/micromamba/envs/musicom/bin/python
# -*- coding: utf-8 -*-
"""085-celtic-subset-walk - Celtic style / Method ABS-002 Subset Walker (ABSTRACT layer).

Abstract -> concrete end-to-end exercise (weekly abstract cadence, 1-in-7).

LAYERS
  Abstract (ABS-002): a walk over the 12TET subset network
      (rules.subset_network.PatternNetwork) steered by a per-bar tension
      curve (ABS-001 style target) produces the 24-bar chord/section design
      -- transposition-invariant subset ids (maj/min/dom7 anchors).
  Concrete (Phase 2): subset ids realized as diatonic Ab-major chords in
      root position (root pc parsed from the subset id, e.g. dom77 = Eb7),
      per-voice register assignment (marimba lead, French-horn pad,
      cello pad, violin counterline, bassoon root counter, double-bass
      roots, drum kit), chord-tone quantization + 8th/16th grid locking.
  Absolute: SP-001 FluidSynth render (workflows.musicom_workflow.produce).

Two-phase artifacts:
  Phase 1: RAW generative draft from the abstract layer itself -- the subset
      walk's tension curve drives a single-voice lead whose raw pitch stream
      samples the CURRENT WALKED SUBSET's pitch-class field (chromatic
      register wander inside the subset field), rhythm events placed at
      fractional (off-grid) ticks. Single voice (marimba program 12), NO
      harmony/bass/drums. The abstract fingerprint before realization.
  Phase 2: musicom rules post-process -- every pitched voice chord-quantized
      per bar to the root-position Ab-major realization of the walked subset,
      onsets snapped to the 8th (240) / 16th (120) grid, voice-leading cap,
      full texture.

Engine only: structures + workflows.unitmatrix_composer + generators.*
+ rules.subset_network + rules.voice_leading. validate() gate + to_midi().
No raw mido authoring (mido only for READ verification).
"""
import os
import json
import random

import numpy as np

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import (
    UnitMatrixComposer, create_empty_unit,
)
from rules.subset_network import (
    standard_patterns, PatternNetwork,
)
from rules.voice_leading import VoiceLeadingRules

# instrument library path (canonical per prior nightly projects 078/080/081/
# 082/083/084: the Instruments KB lives outside the editable install)
import sys  # noqa: E402
sys.path.insert(0, "/opt/data/projects/Instruments")  # noqa: E402
from instrument_registry import (  # noqa: E402
    MARIMBA, FRENCH_HORN, CELLO, VIOLIN, BASSOON, DOUBLE_BASS,
)
from Percussion.drum_kit.drum_kit import KIT, VELOCITIES  # noqa: E402

SEED = 20260903
WALK_SEED = 3   # subset-network walk seed (probed: balanced dominant placement)

# ---------------------------------------------------------------- project dirs
PROJ = "/opt/data/projects/Styles/Celtic/085-celtic-subset-walk"
MIDI_DIR = os.path.join(PROJ, "MIDI")
AUDIO_DIR = os.path.join(PROJ, "Audio")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")
for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
    os.makedirs(d, exist_ok=True)

# ---------------------------------------------------------------- concept
BPM = 96
TPB = 480
BEATS = 4
BAR = TPB * BEATS            # 1920
SECTION_TICKS = BAR * 4     # 7680 (sections of 4 bars)
# Celtic tonal palette: Ab major (ionian), bright pipe-friendly lift.
KEY_PCS = {8, 10, 0, 1, 3, 5, 7}      # Ab Bb C Db Eb F G
KEY_NAME = "Ab major"
# lead register 70-90 (marimba bright celtic lead)
LEAD_LO, LEAD_HI = 70, 90

# ---------------------------------------------------------------- sections
NAMES = ["Intro", "ReelA", "ReelB", "Lift", "ReelA2", "Outro"]
N_SECTIONS = len(NAMES)
N_BARS = N_SECTIONS * 4          # 24 bars
# Tension targets per bar (ABS-001 tension-curve shaping). Triad anchors all
# carry T=2.0 and 7th anchors T=5.0-7.0, so peaks >=4.5 pull V7/I7 into the
# walk. Arc: Intro sway -> ReelA rise -> ReelB lean -> Lift peak (V7) ->
# ReelA2 dance return -> Outro resolve.
BAR_TENSION = [2.0, 2.0, 2.0, 2.0,   # Intro: tonic-sway
               2.5, 2.5, 3.0, 3.0,   # ReelA: rise
               3.5, 3.5, 4.0, 4.0,   # ReelB: dominant-lean
               4.5, 5.0, 5.5, 4.5,   # Lift: peak (V7 region)
               3.0, 2.5, 2.0, 2.0,   # ReelA2: dance return
               1.5, 1.3, 1.1, 1.0]   # Outro: cadence down

# ---------------------------------------------------------------------------
# ABSTRACT LAYER: subset-network design (the generative method itself)
# ---------------------------------------------------------------------------
# Fully diatonic-in-Ab anchors (C-library subset +8 semitones = Ab space):
#   maj0 -> Ab I    min2 -> Bb-ii   min4 -> C-iii   maj5 -> Db-IV
#   maj7 -> Eb V    min9 -> F-vi    maj70 -> Abmaj7 (I7 color)
#   dom77 -> Eb7 (V7, lift peak)    min72 -> Bbm7 (ii7)
TONIC_OFF = 8
_ANCHOR_IDS = ["maj0", "min2", "min4", "maj5", "maj7", "min9",
               "maj70", "dom77", "min72"]
_lib = PatternNetwork(standard_patterns())
_anchors = [_lib.patterns[i] for i in _ANCHOR_IDS]
for _a in _anchors:
    _t = set((pc + TONIC_OFF) % 12 for pc in _a.subset)
    assert _t <= set(KEY_PCS), (_a.id, sorted(_t))
_NET = PatternNetwork(_anchors)
_rng = random.Random(WALK_SEED)
_WALK = _NET.walk("maj0", N_BARS, rng=_rng,
                  tension_curve=BAR_TENSION, home="maj0")
_WALK[-1] = "maj0"          # hard cadence home on the final bar
# Cadence-and-closure post-rule (rules layer, cf. method 006): the walk's
# outro must close authentically. Force bar 22 -> V7 (dom77) unless the walk
# already placed a dominant there, and bar 23 -> I (already forced).
if _WALK[22] not in ("dom77", "maj7"):
    _WALK[22] = "dom77"
WALK_IDS = _WALK

# pattern id -> (degree name, root pc in Ab space). Root pc is encoded in the
# subset id itself: maj{pc} / min{pc} / maj7{pc} / dom7{pc}.
def _root_pc_ab(pid):
    root_c = int(pid[-1])
    return (root_c + TONIC_OFF) % 12


def _diffs(pid):
    """Root-normalized semitone offsets of the pattern's subset."""
    subset = _lib.patterns[pid].subset
    root_c = int(pid[-1])
    return sorted((pc - root_c) % 12 for pc in subset)


def _degree_of(pid):
    tri = {0: "I", 2: "ii", 4: "iii", 5: "IV", 7: "V", 9: "vi"}
    if pid in ("maj70",):
        return "I7"
    if pid in ("dom77",):
        return "V7"
    if pid in ("min72",):
        return "ii7"
    return tri[int(pid[-1])]


def chord_tones_bar(bar, anchor=48):
    """Root-position diatonic realization of the walked subset at `anchor`
    register: root_midi = anchor + root-pc offset, then root + diffs."""
    pid = WALK_IDS[bar]
    root_midi = anchor + _root_pc_ab(pid)
    return [root_midi + d for d in _diffs(pid)]


def chord_pool(pitch, tones, lo=48, hi=96):
    """Octave-expanded chord-tone pool around `pitch` (nearest-copy search)."""
    pool = []
    for t in tones:
        m = t
        while m < lo:
            m += 12
        while m <= hi:
            pool.append(m)
            m += 12
    if not pool:
        pool = tones
    return pool


def quantize_to_chord(pitch, tones, lo=48, hi=96):
    """Snap a pitch to the nearest chord tone (ties -> lower), searching
    octave copies of the root-position voicing so register is preserved."""
    pool = chord_pool(pitch, tones, lo=lo, hi=hi)
    return min(pool, key=lambda c: (abs(c - pitch), c))


def quantize_to_grid(events, grid=240):
    """Snap onsets to the rhythmic grid (8th=240 / 16th=120 @ 96 BPM)."""
    q = []
    for e in events:
        if e.pitch == 0:
            q.append(e)
            continue
        st = int(round(e.start_tick / grid) * grid)
        q.append(MusicEvent(pitch=e.pitch, volume=e.volume,
                            start_tick=st, end_tick=max(st + 1, e.end_tick)))
    return q


def dedup_events(events):
    """Collapse events sharing (start_tick, pitch): keep the longest."""
    best = {}
    for e in events:
        if e.pitch == 0:
            continue
        k = (e.start_tick, e.pitch)
        d = e.end_tick - e.start_tick
        if k not in best or d > (best[k].end_tick - best[k].start_tick):
            best[k] = e
    return list(best.values())


# ---------------------------------------------------------------- PHASE 1
# RAW ABSTRACT-LAYER DRAFT: the subset walk is the melody source. Each bar's
# lead events sample the CURRENT WALKED SUBSET's pitch-class field (octave
# copies across the lead window), with off-grid fractional onset slots -- the
# abstract fingerprint BEFORE concrete chord-tone/grid realization. One voice,
# no harmony. Events are clamped to their bar so the raw draft stays inside
# its section (zero-drift).
def raw_subset_melody(seed, bar, n_events=14):
    """Raw single-bar events: pitch class from walked subset, off-grid ticks."""
    r = np.random.default_rng(seed)
    pid = WALK_IDS[bar]
    field_pcs = set((pc + TONIC_OFF) % 12 for pc in _lib.patterns[pid].subset)
    pool = []
    for pc in field_pcs:
        m = pc + 60
        while m <= LEAD_HI + 12:
            if LEAD_LO <= m <= LEAD_HI + 12:
                pool.append(m)
            m += 12
    if not pool:
        pool = [72]
    evs = []
    tick = 0.0
    n = 0
    while n < n_events and tick < BAR:
        p = int(r.choice(pool))
        if p > LEAD_HI:
            p -= 12
        step = BAR / n_events
        st = int(round(tick))
        dur = max(60, int(step * 0.62))
        if st + dur > BAR:
            dur = BAR - st
        vel = int(np.clip(76 + 20 * abs(np.sin(tick / 300.0)), 56, 108))
        if dur > 0:
            evs.append(MusicEvent(pitch=p, volume=vel,
                                  start_tick=st, end_tick=st + dur))
        tick += step * (1.0 + 0.06 * r.standard_normal())
        n += 1
    return evs


phase1 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
phase1.create_matrix(num_voices=1, num_sections=N_SECTIONS)
phase1.add_voice("LeadRaw", program=MARIMBA.midi_program, channel=0)
for s, name in enumerate(NAMES):
    phase1.add_section(name, bars=4)
    evs = []
    for b in range(4):
        bar = s * 4 + b
        evs += raw_subset_melody(SEED + bar, bar, n_events=12 + (s % 3))
    phase1.set_unit(0, s, MusicUnit(events=evs))
# zero-drift landmark: exact section boundary
for s in range(N_SECTIONS):
    u = phase1.matrix.get_unit((0, s))
    evs = list(u.events)
    if not any(e.pitch == 0 and e.end_tick == SECTION_TICKS for e in evs):
        evs.append(MusicEvent(pitch=0, volume=0,
                              start_tick=SECTION_TICKS - 1,
                              end_tick=SECTION_TICKS))
    phase1.set_unit(0, s, MusicUnit(events=evs))

ok1, msg1 = phase1.validate()
print("PHASE1 validate:", msg1)
assert ok1, msg1
P1_MIDI = os.path.join(MIDI_DIR, "085-celtic-subset-walk-phase1.mid")
phase1.to_midi(P1_MIDI)
print("phase1 written", P1_MIDI, os.path.getsize(P1_MIDI), "bytes")

# ---------------------------------------------------------------- PHASE 2
VOICES = [
    ("Marimba",   MARIMBA.midi_program,       0),   # lead (registry)
    ("Horns",     FRENCH_HORN.midi_program,   1),   # pad harmony (registry)
    ("Cello",     CELLO.midi_program,         2),   # cello pad (registry)
    ("Violin",    VIOLIN.midi_program,        3),   # counterline (registry)
    ("Bassoon",   BASSOON.midi_program,       4),   # root counter (registry)
    ("Bass",      DOUBLE_BASS.midi_program,   5),   # double bass (registry)
    ("Drums",     0,                          9),   # drum kit (ch9)
]
N_V = len(VOICES)

phase2 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
phase2.create_matrix(num_voices=N_V, num_sections=N_SECTIONS)
vnames = [v[0] for v in VOICES]
for name, prog, ch in VOICES:
    phase2.add_voice(name, program=prog, channel=ch)
for n in NAMES:
    phase2.add_section(n, bars=4)

# --- Marimba lead: phase-1 raw events -> 16th-grid lock FIRST, then
#     chord-tone quantize per the bar where the SNAPPED onset lands (a raw
#     onset in the last 120 ticks of bar N snaps into bar N+1 and must take
#     bar N+1's chord), dedup + voice-leading cap.
#     NOTE: cell ticks are SECTION-RELATIVE -> absolute bar = s*4 + (t//BAR).
for s in range(N_SECTIONS):
    raw = phase1.matrix.get_unit((0, s))
    snapped = quantize_to_grid([e for e in raw.events if e.pitch > 0], grid=120)
    out_evs = []
    for e in snapped:
        if e.start_tick >= SECTION_TICKS:
            continue
        bar = s * 4 + (e.start_tick // BAR)
        tones = chord_tones_bar(bar if bar < N_BARS else N_BARS - 1)
        out_evs.append(MusicEvent(
            pitch=quantize_to_chord(e.pitch, tones, lo=48, hi=96),
            volume=e.volume, start_tick=e.start_tick, end_tick=e.end_tick))
    out_evs = dedup_events(out_evs)
    out_evs.sort(key=lambda e: (e.start_tick, e.pitch))
    for i in range(1, len(out_evs)):
        e = out_evs[i]
        prev = out_evs[i - 1]
        if e.pitch == 0 or prev.pitch == 0:
            continue
        if abs(e.pitch - prev.pitch) > 10:
            bar = s * 4 + (e.start_tick // BAR)
            tones = chord_tones_bar(bar if bar < N_BARS else N_BARS - 1)
            e.pitch = quantize_to_chord(prev.pitch, tones, lo=48, hi=96)
    phase2.set_unit(0, s, MusicUnit(events=out_evs))

# --- Horns (French Horn, registry sweet 55-72): root-position pad.
#     Whole-bar on Intro/Outro; half-bar splits on dance sections. Triads
#     closed [r,3rd,5th]; 7ths [r,3rd,5th,7th] in the 48-84 register.
for bar in range(N_BARS):
    s, b = divmod(bar, 4)
    tones = chord_tones_bar(bar, anchor=48)
    t0 = b * BAR
    e = []
    notes = [t for t in tones if 52 <= t <= 84]
    if not notes:
        notes = [tones[0]]
    if s in (0, 5):
        for p in notes:
            e.append(MusicEvent(pitch=p, volume=56,
                                start_tick=t0, end_tick=t0 + BAR))
    else:
        for half, off in ((0, 0), (1, 960)):
            for p in notes:
                e.append(MusicEvent(pitch=p, volume=54,
                                    start_tick=t0 + off,
                                    end_tick=t0 + off + 840))
    unit = phase2.matrix.get_unit((1, s))
    events = list(unit.events) if unit is not None else []
    events.extend(e)
    phase2.set_unit(1, s, MusicUnit(events=events))

# --- Cello pad (registry sweet 48-67): root+fifth open harmony, whole bar.
for bar in range(N_BARS):
    s, b = divmod(bar, 4)
    tones = chord_tones_bar(bar, anchor=36)
    t0 = b * BAR
    e = []
    r = tones[0]
    fifth = r + 7 if (r + 7) - tones[0] < 12 else tones[-1]
    for p in (r, r + 7):
        if 40 <= p <= 72:
            e.append(MusicEvent(pitch=p, volume=48,
                                start_tick=t0, end_tick=t0 + BAR))
    unit = phase2.matrix.get_unit((2, s))
    events = list(unit.events) if unit is not None else []
    events.extend(e)
    phase2.set_unit(2, s, MusicUnit(events=events))

# --- Violin counterline (registry sweet 67-96): celtic answer phrase built
#     from Ab-major pentatonic (Db C Bb F / G), chord-quantized per bar to
#     the walked subset. Onsets locked to the 8th grid.
VIO_LINE = [74, 72, 70, 77, 74, 72, 70, 67]   # Db5 C5 Bb4 F5 Db5 C5 Bb4 G4
for bar in range(N_BARS):
    s, b = divmod(bar, 4)
    tones = chord_tones_bar(bar, anchor=48)
    t0 = b * BAR
    e = []
    if s in (2, 4):      # ReelB / ReelA2: full 8-note answering line on 8ths
        for k, p in enumerate(VIO_LINE):
            off = k * 240
            qp = quantize_to_chord(p, tones, lo=60, hi=96)
            e.append(MusicEvent(pitch=qp, volume=64,
                                start_tick=t0 + off, end_tick=t0 + off + 200))
    elif s in (1, 3):    # ReelA / Lift: 4-note tail answer (beats 3-4)
        for k, p in enumerate(VIO_LINE[4:]):
            off = 960 + k * 240
            qp = quantize_to_chord(p, tones, lo=60, hi=96)
            e.append(MusicEvent(pitch=qp, volume=60,
                                start_tick=t0 + off, end_tick=t0 + off + 200))
    unit = phase2.matrix.get_unit((3, s))
    events = list(unit.events) if unit is not None else []
    events.extend(e)
    phase2.set_unit(3, s, MusicUnit(events=events))

# --- Bassoon root counter (registry sweet 48-72): roots at +1 octave, 8th
#     drive on dance sections, quarter lift elsewhere. On-grid.
for bar in range(N_BARS):
    s, b = divmod(bar, 4)
    tones = chord_tones_bar(bar, anchor=36)
    root = tones[0]
    t0 = b * BAR
    e = []
    if s in (2, 4):
        for k in range(8):
            e.append(MusicEvent(pitch=root + 12, volume=62,
                                start_tick=t0 + k * 240,
                                end_tick=t0 + k * 240 + 180))
    elif s in (1, 3):
        for k in (0, 2, 4, 6):
            e.append(MusicEvent(pitch=root + 12, volume=58,
                                start_tick=t0 + k * 240,
                                end_tick=t0 + k * 240 + 200))
    else:                # Intro/Outro: whole-bar root (bassoon color)
        e.append(MusicEvent(pitch=root + 12, volume=52,
                            start_tick=t0, end_tick=t0 + BAR - 60))
    unit = phase2.matrix.get_unit((4, s))
    events = list(unit.events) if unit is not None else []
    events.extend(e)
    phase2.set_unit(4, s, MusicUnit(events=events))

# --- Double-bass roots (registry sweet 40-55): celtic 4/4 pulse, root 8ths
#     with a 16th push into chorus downbeats (s=2,4) -- dance lock.
def bass_register(root_midi):
    while root_midi < 28:
        root_midi += 12
    while root_midi > 52:
        root_midi -= 12
    return root_midi


for bar in range(N_BARS):
    s, b = divmod(bar, 4)
    tones = chord_tones_bar(bar, anchor=24)
    bass_root = bass_register(tones[0])
    t0 = b * BAR
    e = []
    for k in range(4):        # quarter pulse
        e.append(MusicEvent(pitch=bass_root, volume=95,
                            start_tick=t0 + k * 480,
                            end_tick=t0 + k * 480 + 320))
    if s in (2, 4):           # dance sections: root push at 16th 15
        e.append(MusicEvent(pitch=bass_root, volume=88,
                            start_tick=t0 + 1800, end_tick=t0 + 1900))
    unit = phase2.matrix.get_unit((5, s))
    events = list(unit.events) if unit is not None else []
    events.extend(e)
    phase2.set_unit(5, s, MusicUnit(events=events))

# --- Drums: celtic-tinged 4/4 -- kick 1&3, snare 2&4 (reel backbeat),
#     closed hat 8ths, ride on downbeats, claps doubling snare on full-dance
#     sections, woodblock 2& tick.
K, V = KIT, VELOCITIES
SEC_DENS = [0.35, 0.85, 1.0, 0.7, 1.0, 0.4]
for s in range(N_SECTIONS):
    dens = SEC_DENS[s]
    evs = []
    if dens <= 0.3:
        phase2.set_unit(6, s, create_empty_unit(SECTION_TICKS))
        continue
    for bar in range(4):
        t0 = bar * BAR
        for k in range(0, BAR, 240):            # hat 8ths
            evs.append(MusicEvent(pitch=K["hat_closed"], volume=V["hat_closed"],
                                  start_tick=t0 + k, end_tick=t0 + k + 90))
        evs.append(MusicEvent(pitch=K["kick"], volume=V["kick"],
                              start_tick=t0, end_tick=t0 + 160))
        evs.append(MusicEvent(pitch=K["kick"], volume=V["kick"] - 6,
                              start_tick=t0 + 960, end_tick=t0 + 1120))
        evs.append(MusicEvent(pitch=K["snare"], volume=V["snare"],
                              start_tick=t0 + 480, end_tick=t0 + 620))
        evs.append(MusicEvent(pitch=K["snare"], volume=V["snare"] + 4,
                              start_tick=t0 + 1440, end_tick=t0 + 1580))
        evs.append(MusicEvent(pitch=K["ride"], volume=V["ride"],
                              start_tick=t0, end_tick=t0 + 520))
        if dens >= 0.85:
            evs.append(MusicEvent(pitch=K["clap"], volume=V["clap"],
                                  start_tick=t0 + 480, end_tick=t0 + 590))
            evs.append(MusicEvent(pitch=K["clap"], volume=V["clap"] + 4,
                                  start_tick=t0 + 1440, end_tick=t0 + 1550))
        if dens >= 0.6:     # woodblock 2& (celtic dance tick)
            evs.append(MusicEvent(pitch=K["woodblock"], volume=V["woodblock"] - 5,
                                  start_tick=t0 + 720, end_tick=t0 + 800))
    phase2.set_unit(6, s, MusicUnit(events=evs))

# --- voice-leading sanity pass on the two melody voices (lead + violin)
vlc = VoiceLeadingRules(style="pop")     # pop: parallel 5th/8ve allowed
vl_flags = []
for voice_idx in (0, 3):
    for s in range(N_SECTIONS):
        u = phase2.matrix.get_unit((voice_idx, s))
        evs = [e for e in u.events if e.pitch > 0]
        evs.sort(key=lambda e: (e.start_tick, e.pitch))
        for i in range(1, len(evs)):
            a, b = evs[i - 1], evs[i]
            # only adjacent-in-time events (<= 1 beat apart) are VL neighbors
            if b.start_tick - a.start_tick > 480:
                continue
            if abs(int(b.pitch) - int(a.pitch)) > 12:
                vl_flags.append((voice_idx, s, a.pitch, b.pitch, "leap>12"))
print("VOICE-LEADING leaps>12 flags:", len(vl_flags))

# --- normalize every cell to exact section boundary (zero-drift invariant)
def normalize_cell(unit, total_ticks):
    evs = list(unit.events)
    for e in evs:
        if e.end_tick > total_ticks:
            e.end_tick = total_ticks
    if not any(e.pitch == 0 and e.end_tick == total_ticks for e in evs):
        evs.append(MusicEvent(pitch=0, volume=0,
                              start_tick=total_ticks - 1,
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
P2_MIDI = os.path.join(MIDI_DIR, "085-celtic-subset-walk.mid")
phase2.to_midi(P2_MIDI)
print("phase2 written", P2_MIDI, os.path.getsize(P2_MIDI), "bytes")

# ---------------------------------------------------------------- analysis
from visualization.grid import write_grid_visualization  # noqa: E402

grid_path = os.path.join(ANALYSIS_DIR, "grid_visualization.txt")
write_grid_visualization(phase2.matrix, grid_path, ticks_per_character=120,
                         voice_names=vnames, bpm=BPM,
                         mode="Ab major / Method ABS-002 subset walk (Celtic)")
print("grid written", grid_path)

from workflows.provenance import write_provenance, AI_GENERATED  # noqa: E402

for mid, phase, note in (
        (P1_MIDI, "1",
         "raw ABS-002 subset-walk draft: pitch stream from walked subset "
         "pitch-class field, off-grid fractional rhythm, single marimba voice, "
         "no harmony/bass/drums"),
        (P2_MIDI, "2",
         "abstract walk realized in Ab major: per-bar chord-tone quantization "
         "to root-position walked subset, 8th/16th grid lock, voice-leading "
         "cap, full celtic texture (marimba, horns, cello, violin, bassoon, "
         "bass, drums)")):
    write_provenance(
        mid, AI_GENERATED,
        "ABS-002 Subset Walker (rules.subset_network.PatternNetwork.walk) "
        "+ ABS-001 tension-curve steering + method-006 cadence close",
        parameters={"bpm": BPM, "key": KEY_NAME, "sections": N_SECTIONS,
                    "bars": N_BARS, "phase": phase, "seed": SEED,
                    "walk_seed": WALK_SEED,
                    "subset_walk": WALK_IDS,
                    "bar_tension": BAR_TENSION,
                    "progression": [_degree_of(w) for w in WALK_IDS],
                    "layer": "abstract (ABS-002) -> concrete realization"},
        notes=note)
    print("provenance phase", phase)

with open(os.path.join(ANALYSIS_DIR, "summary.json"), "w") as f:
    json.dump({
        "project": "085-celtic-subset-walk",
        "style": "Celtic", "method": "ABS-002 Subset Walker",
        "layer": "abstract", "bpm": BPM, "key": KEY_NAME,
        "bars": N_BARS, "seed": SEED, "walk_seed": WALK_SEED,
        "sections": {n: 4 for n in NAMES},
        "subset_walk": WALK_IDS,
        "progression": [_degree_of(w) for w in WALK_IDS],
        "voices": vnames,
        "phase1": os.path.basename(P1_MIDI),
        "phase2": os.path.basename(P2_MIDI),
        "grid": os.path.basename(grid_path),
    }, f, indent=2)
print("summary.json written")

for p in (P1_MIDI, P2_MIDI, grid_path,
          os.path.join(ANALYSIS_DIR, "summary.json")):
    assert os.path.getsize(p) > 40, "too small: %s" % p
print("ALL SIZE ASSERTS PASSED")
print("WALK:", [_degree_of(w) for w in WALK_IDS])
