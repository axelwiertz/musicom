#!/opt/data/micromamba/envs/musicom/bin/python
# -*- coding: utf-8 -*-
"""254-celtic-reel-variations — identity-preserving EXTENSION of 085-celtic-subset-walk.

Nightly rework agent. Source 085 passed all 5 musical/engine standards
(UnitMatrixComposer, zero-drift 7x46080, off-grid 0, scale-viol 0, two-phase
present); only index.html was missing (doc gap). Decision: EXTENSION — keep the
clean material as DNA seed, compose a NEW LONGER (8 sections x 4 bars = 32 bars,
vs 24) and MORE VARIED version.

METHOD (preserved identity): ABS-002 Subset Walker (rules.subset_network.
PatternNetwork.walk) steered by an ABS-001 tension curve + method-006 cadence
close, realized in Ab major as root-position diatonic chords.

VARIATION TECHNIQUES (6 distinct, one per section change):
  Intro    sparse (low lead density, drums tacet)
  ReelA    baseline full texture (8th lead)
  ReelB    counterline prominence (violin full 8th line)
  Lift     DIMINUTION (16th subdivision, dense)
  ReelA2   TRANSPOSITION (diatonic sequence +2 scale degrees)
  Bridge   INVERSION + RETROGRADE (palindromic contour)
  Climax   REGISTER SHIFT (+12) + octave doubling + density rise
  Outro    AUGMENTATION (sustain x2) fade to tonic

TWO-PHASE: phase1 = raw off-grid single-voice draft; phase2 = rules (per-bar
chord-tone quantize, 8th/16th grid lock, voice-leading cap) + DUAL-VERSION
export (perfect grid-locked + humanized) via workflows.humanize.export_dual.

Engine only: structures + workflows.unitmatrix_composer + generators.* +
rules.subset_network + rules.voice_leading. validate() gate + to_midi().
mido is used READ-ONLY for the independent readback audit.
"""
import os
import json

import numpy as np

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import (
    UnitMatrixComposer, create_empty_unit,
)
from rules.subset_network import standard_patterns, PatternNetwork
from rules.voice_leading import VoiceLeadingRules
from workflows.humanize import export_dual
from visualization.grid import write_grid_visualization
from workflows.provenance import write_provenance, AI_ASSISTED

# instrument registry (source of truth) — flat module, not pip-installed
import sys as _sys
_INSTR_DIR = "/opt/data/projects/Instruments"
if _INSTR_DIR not in _sys.path:
    _sys.path.insert(0, _INSTR_DIR)
from instrument_registry import (  # noqa: E402
    MARIMBA, FRENCH_HORN, CELLO, VIOLIN, BASSOON, DOUBLE_BASS, DRUM_KIT,
)
from Percussion.drum_kit.drum_kit import KIT, VELOCITIES  # noqa: E402
del _sys

# ------------------------------------------------------------------ config --
GENRE = "Celtic"
PROJECT_ID = 254
PROJECT_NAME = "254-celtic-reel-variations"
PROJECT_DIR = f"/opt/data/projects/Styles/{GENRE}/{PROJECT_NAME}"
SOURCE = "085-celtic-subset-walk"

BPM = 96
TPB = 480
BEATS = 4
BAR = TPB * BEATS                       # 1920
GRID16 = 120
GRID8 = 240
SECTION_TICKS = BAR * 4                 # 7680 (4 bars / section)

SEED = 20261021
WALK_SEED = 7                           # fresh subset-network walk (new vs 085's 3)
HZ_SEED = SEED + PROJECT_ID * 1000      # deterministic humanize seed
STYLE = "folk"                          # celtic -> folk-family (loose organic profile)

KEY_PCS = {8, 10, 0, 1, 3, 5, 7}       # Ab Bb C Db Eb F G
KEY_NAME = "Ab major"
SCALE_LADDER = [8, 10, 0, 1, 3, 5, 7]   # ascending pcs from Ab

for sub in ("MIDI", "Audio", "Analysis", "Scripts"):
    os.makedirs(os.path.join(PROJECT_DIR, sub), exist_ok=True)

# ------------------------------------------------------------------ form ----
SECTION_NAMES = ["Intro", "ReelA", "ReelB", "Lift", "ReelA2", "Bridge",
                 "Climax", "Outro"]
N_SECTIONS = len(SECTION_NAMES)         # 8
N_BARS = N_SECTIONS * 4                 # 32

# ABS-001 tension curve, 32 bars: intro sway -> reel rise -> lean -> lift peak
# -> dance return -> bridge re-tension -> climax peak 2 -> cadence down.
BAR_TENSION = [
    2.0, 2.0, 2.0, 2.0,                # Intro sway
    2.5, 2.5, 3.0, 3.0,                # ReelA rise
    3.5, 3.5, 4.0, 4.0,                # ReelB lean
    4.5, 5.0, 5.5, 4.5,                # Lift peak (V7)
    3.0, 2.5, 2.0, 2.0,                # ReelA2 dance return
    3.5, 4.0, 4.5, 4.0,                # Bridge re-tension
    5.0, 5.5, 5.5, 5.0,                # Climax peak 2 (I7/V7)
    1.5, 1.3, 1.1, 1.0,                # Outro cadence
]
assert len(BAR_TENSION) == N_BARS

# variation table: (register, reverse, invert, diashift, subdiv, sustain,
#                   oct_double, lead_density, method, label)
#   subdiv 8 = 8th lead, 16 = 16th lead (diminution)
#   method: "subset" (walked-subset field), "step" (scale ladder), "penta"
SECTION_SPEC = [
    (0,  False, False, 0, 8,  1, False, 8,  "subset", "sparse intro (drums tacet)"),
    (0,  False, False, 0, 8,  1, False, 14, "subset", "baseline full texture (8th lead)"),
    (0,  False, False, 0, 8,  1, False, 12, "subset", "counterline prominence (violin full line)"),
    (0,  False, False, 0, 16, 1, False, 16, "subset", "diminution (16th subdivision, dense)"),
    (0,  False, False, 2, 8,  1, False, 12, "subset", "transposition (diatonic sequence +2 degrees)"),
    (0,  True,  True,  0, 8,  1, False, 10, "step",   "inversion + retrograde (palindromic bridge)"),
    (12, False, False, 0, 8,  1, True,  14, "penta",  "register shift (+12) + octave doubling"),
    (0,  False, False, 0, 8,  2, False, 6,  "subset", "augmentation (sustain x2) fade to tonic"),
]
assert len(SECTION_SPEC) == N_SECTIONS

# per-section drum density (density-rise variation)
SEC_DENS = [0.0, 0.85, 1.0, 0.7, 0.9, 0.6, 1.0, 0.4]

# ------------------------------------------------------------------ harmony --
TONIC_OFF = 8
_ANCHOR_IDS = ["maj0", "min2", "min4", "maj5", "maj7", "min9",
               "maj70", "dom77", "min72"]
_lib = PatternNetwork(standard_patterns())
_anchors = [_lib.patterns[i] for i in _ANCHOR_IDS]
for _a in _anchors:
    _t = set((pc + TONIC_OFF) % 12 for pc in _a.subset)
    assert _t <= set(KEY_PCS), (_a.id, sorted(_t))
_NET = PatternNetwork(_anchors)
_rng = np.random.default_rng(WALK_SEED)
_WALK = _NET.walk("maj0", N_BARS, rng=_rng,
                  tension_curve=BAR_TENSION, home="maj0")
_WALK[-1] = "maj0"                       # hard cadence home on final bar
# method-006 cadence close: bar 30 -> V7 (dom77), bar 31 -> I (already maj0)
if _WALK[30] not in ("dom77", "maj7"):
    _WALK[30] = "dom77"
WALK_IDS = _WALK


def _root_pc_ab(pid):
    return (int(pid[-1]) + TONIC_OFF) % 12


def _diffs(pid):
    subset = _lib.patterns[pid].subset
    root_c = int(pid[-1])
    return sorted((pc - root_c) % 12 for pc in subset)


def _degree_of(pid):
    tri = {0: "I", 2: "ii", 4: "iii", 5: "IV", 7: "V", 9: "vi"}
    if pid == "maj70":
        return "I7"
    if pid == "dom77":
        return "V7"
    if pid == "min72":
        return "ii7"
    return tri[int(pid[-1])]


def chord_tones_bar(bar, anchor=48):
    pid = WALK_IDS[bar]
    root_midi = anchor + _root_pc_ab(pid)
    return [root_midi + d for d in _diffs(pid)]


def chord_pool(pitch, tones, lo=48, hi=96):
    pool = []
    for t in tones:
        m = t
        while m < lo:
            m += 12
        while m <= hi:
            pool.append(m)
            m += 12
    if not pool:
        pool = [int(t) for t in tones]
    return pool


def quantize_to_chord(pitch, tones, lo=48, hi=96):
    pool = chord_pool(pitch, tones, lo=lo, hi=hi)
    return int(min(pool, key=lambda c: (abs(c - pitch), c)))


def quantize_to_grid(events, grid=GRID8):
    q = []
    for e in events:
        if e.pitch == 0:
            q.append(e)
            continue
        st = int(round(e.start_tick / grid) * grid)
        q.append(MusicEvent(pitch=int(e.pitch), volume=int(e.volume),
                            start_tick=st, end_tick=max(st + 1, int(e.end_tick))))
    return q


def dedup_events(events):
    best = {}
    for e in events:
        if e.pitch == 0:
            continue
        k = (e.start_tick, e.pitch)
        d = e.end_tick - e.start_tick
        if k not in best or d > (best[k].end_tick - best[k].start_tick):
            best[k] = e
    return list(best.values())


def scale_shift(pitch, steps):
    """Diatonic transposition by `steps` scale degrees (stays in Ab major)."""
    pc = int(pitch) % 12
    idx = SCALE_LADDER.index(pc)
    new_pc = SCALE_LADDER[(idx + steps) % 7]
    oct_shift = (idx + steps) // 7
    return int(pitch) + (new_pc - pc) + 12 * oct_shift


def invert_contour(evs):
    """Negate consecutive intervals (contour inversion), rhythm preserved."""
    if len(evs) < 2:
        return evs
    out = [evs[0]]
    for i in range(1, len(evs)):
        prev_p = out[-1].pitch
        orig_int = evs[i].pitch - evs[i - 1].pitch
        new_p = prev_p - orig_int
        out.append(MusicEvent(pitch=int(new_p), volume=int(evs[i].volume),
                              start_tick=int(evs[i].start_tick),
                              end_tick=int(evs[i].end_tick)))
    return out


# ------------------------------------------------------------------ lead raw --
BASE_LO, BASE_HI = 67, 91


def _field_pool(pid, lo, hi):
    field_pcs = set((pc + TONIC_OFF) % 12 for pc in _lib.patterns[pid].subset)
    pool = []
    for pc in field_pcs:
        m = pc + 60
        while m <= hi:
            if lo <= m <= hi:
                pool.append(m)
            m += 12
    if not pool:
        pool = [lo + 5]
    return pool


def _penta_pool(lo, hi):
    pcs = [8, 10, 0, 3, 5]             # Ab major pentatonic
    pool = []
    for pc in pcs:
        m = pc + 60
        while m <= hi:
            if lo <= m <= hi:
                pool.append(m)
            m += 12
    return pool


def _ladder_pool(lo, hi):
    pool = []
    for pc in SCALE_LADDER:
        m = pc + 60
        while m <= hi:
            if lo <= m <= hi:
                pool.append(m)
            m += 12
    return pool


def raw_bar_events(rng, bar, n_events, lo, hi, method):
    pid = WALK_IDS[bar]
    if method == "penta":
        pool = _penta_pool(lo, hi)
    elif method == "step":
        pool = _ladder_pool(lo, hi)
    else:
        pool = _field_pool(pid, lo, hi)
    evs = []
    tick = 0.0
    n = 0
    while n < n_events and tick < BAR:
        p = int(rng.choice(pool))
        step = BAR / n_events
        st = int(round(tick))
        dur = max(60, int(step * 0.62))
        if st + dur > BAR:
            dur = BAR - st
        vel = int(np.clip(76 + 20 * abs(np.sin(tick / 300.0)), 56, 108))
        if dur > 0:
            evs.append(MusicEvent(pitch=p, volume=vel,
                                  start_tick=st, end_tick=st + dur))
        tick += step * (1.0 + 0.06 * rng.standard_normal())
        n += 1
    return evs


# ------------------------------------------------------------------ phase 1 --
def phase1_raw_events(total_ticks):
    rng = np.random.default_rng(SEED)
    evs = []
    for bar in range(N_BARS):
        evs += raw_bar_events(rng, bar, 12, BASE_LO, BASE_HI, "subset")
    # clamp to total span + terminal landmark
    for e in evs:
        if e.end_tick > total_ticks:
            e.end_tick = total_ticks
        if e.start_tick >= total_ticks:
            e.start_tick = total_ticks - 1
    evs.append(MusicEvent(pitch=0, volume=0,
                          start_tick=total_ticks - 1, end_tick=total_ticks))
    return evs


def export_phase1(path):
    c = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=4)
    c.create_matrix(num_voices=1, num_sections=1)
    c.add_voice("LeadRaw", program=MARIMBA.midi_program, channel=0)
    c.add_section("Raw", bars=N_BARS)
    c.set_unit(0, 0, MusicUnit(events=phase1_raw_events(N_BARS * BAR)))
    ok, msg = c.validate()
    if not ok:
        raise RuntimeError(f"phase1 validate failed: {msg}")
    c.to_midi(path)
    return c


# ------------------------------------------------------------------ phase 2 --
VOICES = [
    ("Marimba", MARIMBA.midi_program, 0),       # lead
    ("Horns",   FRENCH_HORN.midi_program, 1),   # pad harmony
    ("Cello",   CELLO.midi_program, 2),         # cello pad
    ("Violin",  VIOLIN.midi_program, 3),        # counterline
    ("Bassoon", BASSOON.midi_program, 4),       # root counter
    ("Bass",    DOUBLE_BASS.midi_program, 5),   # double bass roots
    ("Drums",   0, 9),                          # drum kit (ch9)
]
N_V = len(VOICES)
VNAMES = [v[0] for v in VOICES]
INSTR_NAMES = ["Marimba", "French Horn", "Cello", "Violin", "Bassoon",
               "Double Bass", "Drum Kit"]

# violin celtic answer line (identity motif, chord-quantized per bar)
VIO_LINE = [74, 72, 70, 77, 74, 72, 70, 67]


def lead_section(s):
    """Realized (rules-processed) lead for one section, variation applied."""
    (reg, rev, inv, diashift, subdiv, sustain, octd, density, method, _lab) = \
        SECTION_SPEC[s]
    lo, hi = BASE_LO + reg, BASE_HI + reg
    rng = np.random.default_rng(SEED + 1000 * s + 7)
    out = []
    for b in range(4):
        bar = s * 4 + b
        raw = raw_bar_events(rng, bar, density, lo, hi, method)
        if diashift:
            raw = [MusicEvent(pitch=scale_shift(e.pitch, diashift),
                              volume=e.volume, start_tick=e.start_tick,
                              end_tick=e.end_tick) for e in raw]
        if inv:
            raw = invert_contour(raw)
        if rev:
            raw = raw[::-1]            # retrograde the pitch/onset order
        # sustain (augmentation): multiply duration
        if sustain != 1:
            raw = [MusicEvent(pitch=e.pitch, volume=e.volume,
                              start_tick=e.start_tick,
                              end_tick=min(BAR, e.start_tick + (e.end_tick - e.start_tick) * sustain))
                   for e in raw]
        snapped = quantize_to_grid([e for e in raw if e.pitch > 0],
                                   grid=GRID16 if subdiv == 16 else GRID8)
        for e in snapped:
            if e.start_tick >= SECTION_TICKS:
                continue
            bar_abs = s * 4 + (e.start_tick // BAR)
            tones = chord_tones_bar(bar_abs if bar_abs < N_BARS else N_BARS - 1)
            qp = quantize_to_chord(e.pitch, tones, lo=lo, hi=hi)
            out.append(MusicEvent(pitch=qp, volume=e.volume,
                                  start_tick=e.start_tick, end_tick=e.end_tick))
            if octd:                   # octave doubling
                up = qp + 12
                if up <= 108:
                    out.append(MusicEvent(pitch=up, volume=max(0, e.volume - 8),
                                          start_tick=e.start_tick,
                                          end_tick=e.end_tick))
    out = dedup_events(out)
    out.sort(key=lambda e: (e.start_tick, e.pitch))
    # voice-leading cap (adjacent leaps > 10 snapped to chord)
    for i in range(1, len(out)):
        e = out[i]
        prev = out[i - 1]
        if abs(e.pitch - prev.pitch) > 10:
            bar_abs = s * 4 + (e.start_tick // BAR)
            tones = chord_tones_bar(bar_abs if bar_abs < N_BARS else N_BARS - 1)
            e.pitch = quantize_to_chord(prev.pitch, tones, lo=lo, hi=hi)
    return out


def horns_section(s):
    evs = []
    for b in range(4):
        bar = s * 4 + b
        tones = chord_tones_bar(bar, anchor=48)
        t0 = b * BAR
        notes = [t for t in tones if 52 <= t <= 84] or [tones[0]]
        if s in (0, 7):                # intro/outro whole-bar
            for p in notes:
                evs.append(MusicEvent(pitch=int(p), volume=56,
                                      start_tick=t0, end_tick=t0 + BAR))
        else:
            for half, off in ((0, 0), (1, 960)):
                for p in notes:
                    evs.append(MusicEvent(pitch=int(p), volume=54,
                                          start_tick=t0 + off,
                                          end_tick=t0 + off + 840))
    return evs


def cello_section(s):
    evs = []
    for b in range(4):
        bar = s * 4 + b
        tones = chord_tones_bar(bar, anchor=36)
        t0 = b * BAR
        r = tones[0]
        for p in (r, r + 7):
            if 40 <= p <= 72:
                evs.append(MusicEvent(pitch=int(p), volume=48,
                                      start_tick=t0, end_tick=t0 + BAR))
    return evs


def violin_section(s):
    evs = []
    for b in range(4):
        bar = s * 4 + b
        tones = chord_tones_bar(bar, anchor=48)
        t0 = b * BAR
        line = VIO_LINE
        if s == 5:                     # bridge: retrograde the answer line
            line = line[::-1]
        if s in (2, 5, 6):             # full 8-note line on 8ths
            for k, p in enumerate(line):
                off = k * 240
                qp = quantize_to_chord(p, tones, lo=60, hi=96)
                evs.append(MusicEvent(pitch=qp, volume=64,
                                      start_tick=t0 + off, end_tick=t0 + off + 200))
        elif s in (1, 3, 4):           # 4-note tail answer (beats 3-4)
            for k, p in enumerate(line[4:]):
                off = 960 + k * 240
                qp = quantize_to_chord(p, tones, lo=60, hi=96)
                evs.append(MusicEvent(pitch=qp, volume=60,
                                      start_tick=t0 + off, end_tick=t0 + off + 200))
    return evs


def bassoon_section(s):
    evs = []
    for b in range(4):
        bar = s * 4 + b
        tones = chord_tones_bar(bar, anchor=36)
        root = tones[0]
        t0 = b * BAR
        if s in (2, 4, 6):             # 8th drive
            for k in range(8):
                evs.append(MusicEvent(pitch=root + 12, volume=62,
                                      start_tick=t0 + k * 240,
                                      end_tick=t0 + k * 240 + 180))
        elif s in (1, 3, 5):           # quarter lift
            for k in (0, 2, 4, 6):
                evs.append(MusicEvent(pitch=root + 12, volume=58,
                                      start_tick=t0 + k * 240,
                                      end_tick=t0 + k * 240 + 200))
        else:                          # intro/outro whole-bar
            evs.append(MusicEvent(pitch=root + 12, volume=52,
                                  start_tick=t0, end_tick=t0 + BAR - 60))
    return evs


def bass_section(s):
    def bass_register(root_midi):
        while root_midi < 28:
            root_midi += 12
        while root_midi > 52:
            root_midi -= 12
        return root_midi

    evs = []
    for b in range(4):
        bar = s * 4 + b
        tones = chord_tones_bar(bar, anchor=24)
        broot = bass_register(tones[0])
        t0 = b * BAR
        for k in range(4):             # quarter pulse
            evs.append(MusicEvent(pitch=broot, volume=95,
                                  start_tick=t0 + k * 480,
                                  end_tick=t0 + k * 480 + 320))
        if s in (2, 4, 6):             # 16th push into downbeats
            evs.append(MusicEvent(pitch=broot, volume=88,
                                  start_tick=t0 + 1800, end_tick=t0 + 1900))
    return evs


def drums_section(s):
    K, V = KIT, VELOCITIES
    dens = SEC_DENS[s]
    if dens <= 0.0:
        return create_empty_unit(SECTION_TICKS).events
    evs = []
    for bar in range(4):
        t0 = bar * BAR
        for k in range(0, BAR, 240):   # hat 8ths
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
        if dens >= 0.6:
            evs.append(MusicEvent(pitch=K["woodblock"], volume=V["woodblock"] - 5,
                                  start_tick=t0 + 720, end_tick=t0 + 800))
    return evs


def normalize_cell(unit, total_ticks):
    evs = list(unit.events)
    for e in evs:
        if e.end_tick > total_ticks:
            e.end_tick = total_ticks
        if e.start_tick >= total_ticks:
            e.start_tick = total_ticks - 1
    if not any(e.pitch == 0 and e.end_tick == total_ticks for e in evs):
        evs.append(MusicEvent(pitch=0, volume=0,
                              start_tick=total_ticks - 1, end_tick=total_ticks))
    return MusicUnit(events=evs)


def build_phase2_composer():
    c = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
    c.create_matrix(num_voices=N_V, num_sections=N_SECTIONS)
    for name, prog, ch in VOICES:
        c.add_voice(name, program=prog, channel=ch)
    for n in SECTION_NAMES:
        c.add_section(n, bars=4)

    builders = {
        0: lead_section, 1: horns_section, 2: cello_section, 3: violin_section,
        4: bassoon_section, 5: bass_section, 6: drums_section,
    }
    for s in range(N_SECTIONS):
        for v in range(N_V):
            evs = builders[v](s)
            # chronological sort (start_tick, then pitch) so the humanizer's
            # forward-clamp "no backtrack" invariant holds (unsorted input
            # cascades ns=max(prev_start, ...) and scrambles the groove).
            evs = sorted(evs, key=lambda e: (int(e.start_tick), int(e.pitch)))
            unit = normalize_cell(MusicUnit(events=evs), SECTION_TICKS)
            c.set_unit(v, s, unit)

    # voice-leading sanity on the two melody voices (leaps > 12 flag only)
    vlc = VoiceLeadingRules(style="pop")
    vl_flags = []
    for voice_idx in (0, 3):
        for s in range(N_SECTIONS):
            u = c.matrix.get_unit((voice_idx, s))
            evs = sorted([e for e in u.events if e.pitch > 0],
                         key=lambda e: (e.start_tick, e.pitch))
            for i in range(1, len(evs)):
                a, b = evs[i - 1], evs[i]
                if b.start_tick - a.start_tick > 480:
                    continue
                if abs(int(b.pitch) - int(a.pitch)) > 12:
                    vl_flags.append((voice_idx, s, a.pitch, b.pitch, "leap>12"))
    print("VOICE-LEADING leaps>12 flags:", len(vl_flags))

    ok, msg = c.validate()
    if not ok:
        raise RuntimeError(f"phase2 validate failed: {msg}")
    return c


# ------------------------------------------------------------------ audits ---
def audit_midi(midi_path):
    import mido  # READING ONLY (analysis)
    mf = mido.MidiFile(midi_path)
    bar_pcs = [set(p % 12 for p in chord_tones_bar(b)) for b in range(N_BARS)]
    per_track = {}
    for tr_idx, track in enumerate(mf.tracks):
        t = 0
        notes = []
        ch = None
        for msg in track:
            t += msg.time
            if msg.type == "program_change":
                ch = msg.channel
            if msg.type == "note_on" and msg.velocity > 0 and msg.note > 0:
                notes.append((int(msg.note), t, int(msg.velocity), ch))
        if notes:
            per_track[tr_idx] = notes
    report = {}
    for tr_idx, notes in per_track.items():
        ch = notes[0][3]
        off16 = sum(1 for (p, t, v, _c) in notes if t % GRID16 != 0)
        off8 = sum(1 for (p, t, v, _c) in notes if t % GRID8 != 0)
        out_key = sum(1 for (p, t, v, _c) in notes
                      if ch != 9 and p % 12 not in KEY_PCS)
        out_chord = 0
        for (p, t, v, _c) in notes:
            if ch == 9:
                continue
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


# ------------------------------------------------------------------ main -----
def main():
    # ---- phase 1
    p1_path = os.path.join(PROJECT_DIR, "MIDI", f"{PROJECT_NAME}-phase1.mid")
    export_phase1(p1_path)
    write_provenance(
        p1_path, classification=AI_ASSISTED,
        generator="ABS-002 Subset Walker (raw subset-field draft)",
        parameters={"phase": 1, "bpm": BPM, "meter": "4/4", "key": KEY_NAME,
                    "seed": SEED, "voices": 1, "bars": N_BARS,
                    "note": "raw generative draft (single marimba, off-grid)"})

    # ---- phase 2 (dual-version: perfect + humanized)
    perf_path = os.path.join(PROJECT_DIR, "MIDI", f"{PROJECT_NAME}-perfect.mid")
    hum_path = os.path.join(PROJECT_DIR, "MIDI", f"{PROJECT_NAME}-humanized.mid")
    c2 = build_phase2_composer()

    grid_path = os.path.join(PROJECT_DIR, "Analysis", "grid_visualization.txt")
    write_grid_visualization(c2.matrix, grid_path, ticks_per_character=GRID16,
                             voice_names=VNAMES, bpm=BPM,
                             mode="Ab major / ABS-002 subset walk (Celtic)")

    hz_instruments = {
        "Marimba": MARIMBA.humanize_dna,
        "Horns": FRENCH_HORN.humanize_dna,
        "Cello": CELLO.humanize_dna,
        "Violin": VIOLIN.humanize_dna,
        "Bassoon": BASSOON.humanize_dna,
        "Bass": DOUBLE_BASS.humanize_dna,
        "Drums": DRUM_KIT.humanize_dna,
    }
    hz = export_dual(c2, perf_path, hum_path, style=STYLE, seed=HZ_SEED,
                     bpm=BPM, instruments=hz_instruments)

    assert os.path.getsize(perf_path) > 40, "empty perfect"
    assert os.path.getsize(hum_path) > 40, "empty humanized"
    assert os.path.getsize(p1_path) > 40, "empty phase1"

    for p, phase, gen in [
        (perf_path, "2-perfect", "ABS-002 + musicom rules (grid-locked)"),
        (hum_path, "2-humanized", "ABS-002 + rules + humanize"),
    ]:
        write_provenance(
            p, classification=AI_ASSISTED, generator=gen,
            parameters={"phase": phase, "bpm": BPM, "meter": "4/4",
                        "key": KEY_NAME, "seed": SEED,
                        "humanize_seed": HZ_SEED, "style": STYLE,
                        "voices": N_V, "bars": N_BARS,
                        "form": "8 sections x 4 bars = 32 bars",
                        "instruments": INSTR_NAMES,
                        "walk_seed": WALK_SEED,
                        "subset_walk": WALK_IDS,
                        "progression": [_degree_of(w) for w in WALK_IDS]},
            notes="Celtic reel in Ab major, identity-preserving extension of "
                  "085-celtic-subset-walk (24 -> 32 bars). Six variation "
                  "techniques: transposition (diatonic sequence), inversion, "
                  "retrograde, diminution, augmentation, register shift + "
                  "octave doubling, density rise, counterline prominence.")

    hz_summary = {}
    for vname, vstat in hz.items():
        hz_summary[vname] = {
            "seed": vstat.get("seed"), "n_notes": vstat.get("n_notes"),
            "mean_abs_shift_ticks": vstat.get("mean_abs_shift_ticks"),
            "max_abs_shift_ticks": vstat.get("max_abs_shift_ticks"),
            "mean_abs_vel_delta": vstat.get("mean_abs_vel_delta"),
        }

    # ---- audits (readback)
    aud_perf = audit_midi(perf_path)
    aud_hum = audit_midi(hum_path)
    spans_perf, ntracks_perf = _zero_drift(perf_path)
    spans_hum, ntracks_hum = _zero_drift(hum_path)

    def _tot(aud):
        t = {"off16": 0, "off8": 0, "out_key": 0, "out_chord": 0, "notes": 0}
        for v in aud.values():
            for k in t:
                t[k] += v[k]
        return t

    tot_perf = _tot(aud_perf)
    tot_hum = _tot(aud_hum)

    # section roots from MIDPOINT chord (bar offset 1 = 2nd bar of each section)
    section_roots = []
    for s in range(N_SECTIONS):
        mid_bar = s * 4 + 1
        pid = WALK_IDS[mid_bar]
        section_roots.append({"section": SECTION_NAMES[s], "mid_bar": mid_bar,
                              "pid": pid, "degree": _degree_of(pid),
                              "root_pc": _root_pc_ab(pid)})

    variation = [{"section": SECTION_NAMES[i], "technique": SECTION_SPEC[i][9]}
                 for i in range(N_SECTIONS)]

    summary = {
        "project": PROJECT_NAME, "genre": GENRE, "source": SOURCE,
        "method": "ABS-002 Subset Walker + ABS-001 tension + method-006 close",
        "layer": "abstract -> concrete", "rework": "extended (longer + more varied)",
        "decision": "identity-preserving extension",
        "key": KEY_NAME, "key_pcs": sorted(KEY_PCS), "bpm": BPM, "meter": "4/4",
        "form": "8 sections x 4 bars = 32 bars", "sections": SECTION_NAMES,
        "section_roots": section_roots, "variation_techniques": variation,
        "subset_walk": WALK_IDS, "progression": [_degree_of(w) for w in WALK_IDS],
        "voices": [f"{n}({p})" for n, p, _c in VOICES],
        "perfect_audit": tot_perf, "humanized_audit": tot_hum,
        "zero_drift": {"perfect_tracks": ntracks_perf,
                       "humanized_tracks": ntracks_hum,
                       "perfect_span": spans_perf, "humanized_span": spans_hum},
        "humanize": {"style": STYLE, "seed": HZ_SEED, "per_voice": hz_summary},
        "seed": SEED, "walk_seed": WALK_SEED,
    }
    with open(os.path.join(PROJECT_DIR, "Analysis", "summary.json"), "w") as f:
        json.dump(summary, f, indent=2, default=str)

    print("=== GRID + HARMONY AUDIT (perfect MIDI) ===")
    for tr in sorted(aud_perf):
        v = aud_perf[tr]
        print(f"  track{tr} notes={v['notes']:3d} off16={v['off16']} "
              f"off8={v['off8']} out_key={v['out_key']} out_chord={v['out_chord']}")
    print(f"  PERFECT  TOTAL notes={tot_perf['notes']} off16={tot_perf['off16']} "
          f"off8={tot_perf['off8']} out_key={tot_perf['out_key']} "
          f"out_chord={tot_perf['out_chord']}")
    print(f"  HUMANIZED TOTAL notes={tot_hum['notes']} off16={tot_hum['off16']} "
          f"off8={tot_hum['off8']} out_key={tot_hum['out_key']} "
          f"out_chord={tot_hum['out_chord']}")
    print("  section roots:", [(r["section"], r["degree"], r["root_pc"])
                               for r in section_roots])
    print("  zero-drift perfect:", ntracks_perf, "tracks len", set(spans_perf))
    print("  zero-drift humanized:", ntracks_hum, "tracks len", set(spans_hum))

    print("\nPHASE1", p1_path, os.path.getsize(p1_path))
    print("PERFECT", perf_path, os.path.getsize(perf_path))
    print("HUMANIZED", hum_path, os.path.getsize(hum_path))
    print("GRID", grid_path)
    print("SUMMARY", os.path.join(PROJECT_DIR, "Analysis", "summary.json"))


if __name__ == "__main__":
    main()
