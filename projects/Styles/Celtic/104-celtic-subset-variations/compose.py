#!/opt/data/micromamba/envs/musicom/bin/python
# -*- coding: utf-8 -*-
"""104-celtic-subset-variations - Celtic rework of 085-celtic-subset-walk.

Rework decision: source 085 audited 5/6 standards pass; FAILED std6 (index.html
missing). Redesign required -> rebuilt through the canonical UnitMatrixComposer
workflow, preserving identity (Celtic / Ab major / 96 BPM / ABS-002 subset walk
+ ABS-001 tension curve + method-006 cadence close / marimba+french-horn+cello+
violin+bassoon+double-bass+drums) and EXTENDED to a longer, more varied form.

Form: 8 sections x 4 bars = 32 bars (source had 6 sections / 24 bars).
  Intro | ReelA | ReelB | Lift | Bridge | ReelA2 | ReelC | Outro

Variation techniques (>=3 required, 7 applied):
  V1 retrograde   - Bridge lead: raw subset pitch stream reversed per bar.
  V2 inversion    - Bridge violin: answer phrase inverted around pivot 74.
  V3 register     - Bridge lead low window (60-76); ReelC lead +12 (octave up).
  V4 transposition- ReelC violin: answer phrase transposed +7 (perfect fifth).
  V5 augmentation - Outro bassoon: root counter 8ths -> whole-bar.
  V6 diminution   - ReelC bassoon: root counter 8ths -> 16ths.
  V7 density/method - drum density curve over 8 sections (0.35..1.0).

Two-phase architecture (mandatory):
  Phase 1 = raw generative draft (subset field pitch stream, fractional off-grid
            rhythm, single marimba voice, no harmony). Own validate() gate.
  Phase 2 = musicom rules post-process: per-bar chord-tone quantization to the
            root-position Ab realization of the walked subset, 8th/16th grid
            snap (120/240), dedup, voice-leading cap, full texture.

Engine only: structures + workflows.unitmatrix_composer + rules.subset_network
+ rules.voice_leading. mido used ONLY for read verification in a separate audit
script. No raw mido authoring, no sys.path hacks.
"""
import os
import json
import random

import numpy as np

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import (
    UnitMatrixComposer, create_empty_unit,
)
from rules.subset_network import PatternNetwork, standard_patterns
from rules.voice_leading import VoiceLeadingRules

# ------------------------------------------------------------------ constants
SEED = 20260924
WALK_SEED = 7       # probed: 9 distinct degrees, V7 peak @ bar 14, V7->I outro

PROJ = "/opt/data/projects/Styles/Celtic/104-celtic-subset-variations"
MIDI_DIR = os.path.join(PROJ, "MIDI")
AUDIO_DIR = os.path.join(PROJ, "Audio")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")
for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
    os.makedirs(d, exist_ok=True)

BPM = 96
TPB = 480
BEATS = 4
BAR = TPB * BEATS            # 1920
SECTION_TICKS = BAR * 4      # 7680
KEY_PCS = {8, 10, 0, 1, 3, 5, 7}      # Ab Bb C Db Eb F G
KEY_NAME = "Ab major"
LEAD_LO, LEAD_HI = 70, 90

NAMES = ["Intro", "ReelA", "ReelB", "Lift", "Bridge", "ReelA2", "ReelC", "Outro"]
N_SECTIONS = len(NAMES)
N_BARS = N_SECTIONS * 4      # 32 bars

# 32-bar tension curve (ABS-001). Arc: intro sway -> reel rise -> lean -> Lift
# peak (V7) -> Bridge contrast dip -> dance return -> ReelC second peak -> outro.
BAR_TENSION = [
    2.0, 2.0, 2.0, 2.0,   # Intro
    2.5, 2.5, 3.0, 3.0,   # ReelA
    3.5, 3.5, 4.0, 4.0,   # ReelB
    4.5, 5.0, 5.5, 4.5,   # Lift
    3.5, 3.0, 3.0, 3.5,   # Bridge
    3.0, 2.5, 2.0, 2.0,   # ReelA2
    3.5, 4.0, 4.0, 3.5,   # ReelC
    2.0, 1.5, 1.2, 1.0,   # Outro
]

# ------------------------------------------------------------------ abstract
TONIC_OFF = 8
_ANCHOR_IDS = ["maj0", "min2", "min4", "maj5", "maj7", "min9",
               "maj70", "dom77", "min72"]
_lib = PatternNetwork(standard_patterns())
_anchors = [_lib.patterns[i] for i in _ANCHOR_IDS]
for _a in _anchors:
    _t = set((pc + TONIC_OFF) % 12 for pc in _a.subset)
    assert _t <= KEY_PCS, (_a.id, sorted(_t))
_NET = PatternNetwork(_anchors)
_rng = random.Random(WALK_SEED)
_WALK = _NET.walk("maj0", N_BARS, rng=_rng,
                  tension_curve=BAR_TENSION, home="maj0")
_WALK[-1] = "maj0"                 # hard cadence home
if _WALK[30] not in ("dom77", "maj7"):
    _WALK[30] = "dom77"            # authentic close V7 -> I
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


def _quality_of(pid):
    d = _degree_of(pid)
    if "7" in d:
        return "dom7" if d == "V7" else "maj7" if d == "I7" else "min7"
    if d[0].isupper() and d != "IV":
        return "major"
    return "major" if d in ("I", "IV", "V") else "minor"


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
        pool = tones
    return pool


def quantize_to_chord(pitch, tones, lo=48, hi=96):
    pool = chord_pool(pitch, tones, lo=lo, hi=hi)
    return min(pool, key=lambda c: (abs(c - pitch), c))


def quantize_to_grid(events, grid=240):
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
    best = {}
    for e in events:
        if e.pitch == 0:
            continue
        k = (e.start_tick, e.pitch)
        d = e.end_tick - e.start_tick
        if k not in best or d > (best[k].end_tick - best[k].start_tick):
            best[k] = e
    return list(best.values())


# ------------------------------------------------------------------ phase 1
def raw_subset_melody(seed, bar, n_events=14):
    """Raw single-bar events: pc from walked subset field, fractional ticks."""
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
phase1.add_voice("LeadRaw", program=12, channel=0)   # marimba GM 12
for s, name in enumerate(NAMES):
    phase1.add_section(name, bars=4)
    evs = []
    for b in range(4):
        bar = s * 4 + b
        bar_evs = raw_subset_melody(SEED + bar, bar, n_events=12 + (s % 3))
        for e in bar_evs:               # offset each bar within the section
            e.start_tick += b * BAR
            e.end_tick += b * BAR
        evs += bar_evs
    phase1.set_unit(0, s, MusicUnit(events=evs))
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
P1_MIDI = os.path.join(MIDI_DIR, "104-celtic-subset-variations-phase1.mid")
phase1.to_midi(P1_MIDI)
print("phase1 written", P1_MIDI, os.path.getsize(P1_MIDI), "bytes")

# ------------------------------------------------------------------ phase 2
VOICES = [
    ("Marimba", 12, 0),   # lead
    ("Horns",   60, 1),   # french horn pad
    ("Cello",   42, 2),   # cello pad
    ("Violin",  40, 3),   # counterline
    ("Bassoon", 70, 4),   # root counter
    ("Bass",    43, 5),   # double bass
    ("Drums",    0, 9),   # drum kit ch9
]
N_V = len(VOICES)
KIT = {"kick": 36, "snare": 38, "clap": 39, "hat_closed": 42,
       "ride": 51, "woodblock": 76}
VEL = {"kick": 100, "snare": 90, "clap": 90, "hat_closed": 65,
       "ride": 70, "woodblock": 80}

phase2 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
phase2.create_matrix(num_voices=N_V, num_sections=N_SECTIONS)
vnames = [v[0] for v in VOICES]
for name, prog, ch in VOICES:
    phase2.add_voice(name, program=prog, channel=ch)
for n in NAMES:
    phase2.add_section(n, bars=4)

# --- Marimba lead: derive from phase-1 raw, apply per-section variation,
#     snap to 16th grid, chord-tone quantize per bar, dedup + VL cap.
for s in range(N_SECTIONS):
    raw = phase1.matrix.get_unit((0, s))
    out_evs = []
    for b in range(4):
        bar = s * 4 + b
        bar_evs = [e for e in raw.events
                   if e.pitch > 0 and (e.start_tick // BAR) == b]
        bar_evs.sort(key=lambda e: e.start_tick)
        if s == 4:                       # V1 retrograde (Bridge)
            bar_evs = list(reversed(bar_evs))
        lo, hi = (60, 76) if s == 4 else (48, 96)   # V3 register shift
        for i, e in enumerate(bar_evs):
            st = b * BAR + i * 120        # bar offset + 16th grid
            if st >= (b + 1) * BAR:
                break
            p = int(e.pitch)
            if s == 6:                    # V3 register shift up (ReelC)
                p += 12
            tones = chord_tones_bar(bar)
            out_evs.append(MusicEvent(
                pitch=quantize_to_chord(p, tones, lo=lo, hi=hi),
                volume=e.volume, start_tick=st, end_tick=st + 100))
    out_evs = dedup_events(out_evs)
    out_evs.sort(key=lambda e: (e.start_tick, e.pitch))
    for i in range(1, len(out_evs)):     # voice-leading cap (max leap 10)
        e = out_evs[i]
        prev = out_evs[i - 1]
        if abs(int(e.pitch) - int(prev.pitch)) > 10:
            tones = chord_tones_bar(s * 4 + (e.start_tick // BAR))
            e.pitch = quantize_to_chord(prev.pitch, tones, lo=48, hi=96)
    phase2.set_unit(0, s, MusicUnit(events=out_evs))

# --- Horns (french horn pad): root-position, whole-bar on sparse sections,
#     half-bar on dance sections.
for bar in range(N_BARS):
    s, b = divmod(bar, 4)
    tones = chord_tones_bar(bar, anchor=48)
    t0 = b * BAR
    e = []
    notes = [t for t in tones if 52 <= t <= 84]
    if not notes:
        notes = [tones[0]]
    if s in (0, 4, 7):                    # Intro/Bridge/Outro: whole-bar
        for p in notes:
            e.append(MusicEvent(pitch=p, volume=56,
                                start_tick=t0, end_tick=t0 + BAR))
    else:                                 # dance: half-bar
        for half, off in ((0, 0), (1, 960)):
            for p in notes:
                e.append(MusicEvent(pitch=p, volume=54,
                                    start_tick=t0 + off,
                                    end_tick=t0 + off + 840))
    unit = phase2.matrix.get_unit((1, s))
    events = list(unit.events) if unit is not None else []
    events.extend(e)
    phase2.set_unit(1, s, MusicUnit(events=events))

# --- Cello pad: root + fifth open harmony, whole bar.
for bar in range(N_BARS):
    s, b = divmod(bar, 4)
    tones = chord_tones_bar(bar, anchor=36)
    t0 = b * BAR
    r = tones[0]
    e = []
    for p in (r, r + 7):
        if 40 <= p <= 72:
            e.append(MusicEvent(pitch=p, volume=48,
                                start_tick=t0, end_tick=t0 + BAR))
    unit = phase2.matrix.get_unit((2, s))
    events = list(unit.events) if unit is not None else []
    events.extend(e)
    phase2.set_unit(2, s, MusicUnit(events=events))

# --- Violin counterline: Ab-pentatonic answer, with inversion (Bridge) and
#     transposition (ReelC) variations. Chord-quantized per bar, 8th grid.
VIO_LINE = [74, 72, 70, 77, 74, 72, 70, 67]     # Db5 C5 Bb4 F5 Db5 C5 Bb4 G4
VIO_INV = [148 - p for p in VIO_LINE]           # V2 inversion around pivot 74
VIO_TR = [p + 7 for p in VIO_LINE]              # V4 transposition up a fifth


def vio_line_for(s):
    if s == 4:
        return VIO_INV
    if s == 6:
        return VIO_TR
    return VIO_LINE


for bar in range(N_BARS):
    s, b = divmod(bar, 4)
    tones = chord_tones_bar(bar, anchor=48)
    t0 = b * BAR
    e = []
    if s in (1, 2, 4, 5, 6):       # active sections: full 8-note line on 8ths
        line = vio_line_for(s)
        for k, p in enumerate(line):
            off = k * 240
            qp = quantize_to_chord(p, tones, lo=60, hi=96)
            e.append(MusicEvent(pitch=qp, volume=64,
                                start_tick=t0 + off, end_tick=t0 + off + 200))
    elif s == 3:                    # Lift: 4-note tail answer (beats 3-4)
        for k, p in enumerate(VIO_LINE[4:]):
            off = 960 + k * 240
            qp = quantize_to_chord(p, tones, lo=60, hi=96)
            e.append(MusicEvent(pitch=qp, volume=60,
                                start_tick=t0 + off, end_tick=t0 + off + 200))
    unit = phase2.matrix.get_unit((3, s))
    events = list(unit.events) if unit is not None else []
    events.extend(e)
    phase2.set_unit(3, s, MusicUnit(events=events))

# --- Bassoon root counter: 8ths on dance, 16ths on ReelC (diminution),
#     quarters on rise/lift/bridge, whole-bar on intro/outro (augmentation).
for bar in range(N_BARS):
    s, b = divmod(bar, 4)
    tones = chord_tones_bar(bar, anchor=36)
    root = tones[0] + 12
    t0 = b * BAR
    e = []
    if s in (2, 5):                 # 8ths
        for k in range(8):
            e.append(MusicEvent(pitch=root, volume=62,
                                start_tick=t0 + k * 240,
                                end_tick=t0 + k * 240 + 180))
    elif s == 6:                    # V6 diminution: 16ths
        for k in range(16):
            e.append(MusicEvent(pitch=root, volume=60,
                                start_tick=t0 + k * 120,
                                end_tick=t0 + k * 120 + 90))
    elif s in (1, 3, 4):            # quarters
        for k in (0, 2, 4, 6):
            e.append(MusicEvent(pitch=root, volume=58,
                                start_tick=t0 + k * 240,
                                end_tick=t0 + k * 240 + 200))
    else:                           # V5 augmentation: whole-bar
        e.append(MusicEvent(pitch=root, volume=52,
                            start_tick=t0, end_tick=t0 + BAR - 60))
    unit = phase2.matrix.get_unit((4, s))
    events = list(unit.events) if unit is not None else []
    events.extend(e)
    phase2.set_unit(4, s, MusicUnit(events=events))


def bass_register(root_midi):
    while root_midi < 28:
        root_midi += 12
    while root_midi > 52:
        root_midi -= 12
    return root_midi


# --- Double bass roots: quarter pulse + 16th push on dance sections.
for bar in range(N_BARS):
    s, b = divmod(bar, 4)
    tones = chord_tones_bar(bar, anchor=24)
    bass_root = bass_register(tones[0])
    t0 = b * BAR
    e = []
    for k in range(4):
        e.append(MusicEvent(pitch=bass_root, volume=95,
                            start_tick=t0 + k * 480,
                            end_tick=t0 + k * 480 + 320))
    if s in (2, 5, 6):
        e.append(MusicEvent(pitch=bass_root, volume=88,
                            start_tick=t0 + 1800, end_tick=t0 + 1900))
    unit = phase2.matrix.get_unit((5, s))
    events = list(unit.events) if unit is not None else []
    events.extend(e)
    phase2.set_unit(5, s, MusicUnit(events=events))

# --- Drums: celtic 4/4 reel (kick 1&3, snare 2&4, hat 8ths) with density curve.
SEC_DENS = [0.35, 0.85, 1.0, 0.7, 0.55, 1.0, 1.0, 0.4]
for s in range(N_SECTIONS):
    dens = SEC_DENS[s]
    if dens <= 0.3:
        phase2.set_unit(6, s, create_empty_unit(SECTION_TICKS))
        continue
    evs = []
    for bar in range(4):
        t0 = bar * BAR
        for k in range(0, BAR, 240):
            evs.append(MusicEvent(pitch=KIT["hat_closed"], volume=VEL["hat_closed"],
                                  start_tick=t0 + k, end_tick=t0 + k + 90))
        evs.append(MusicEvent(pitch=KIT["kick"], volume=VEL["kick"],
                              start_tick=t0, end_tick=t0 + 160))
        evs.append(MusicEvent(pitch=KIT["kick"], volume=VEL["kick"] - 6,
                              start_tick=t0 + 960, end_tick=t0 + 1120))
        evs.append(MusicEvent(pitch=KIT["snare"], volume=VEL["snare"],
                              start_tick=t0 + 480, end_tick=t0 + 620))
        evs.append(MusicEvent(pitch=KIT["snare"], volume=VEL["snare"] + 4,
                              start_tick=t0 + 1440, end_tick=t0 + 1580))
        evs.append(MusicEvent(pitch=KIT["ride"], volume=VEL["ride"],
                              start_tick=t0, end_tick=t0 + 520))
        if dens >= 0.85:
            evs.append(MusicEvent(pitch=KIT["clap"], volume=VEL["clap"],
                                  start_tick=t0 + 480, end_tick=t0 + 590))
            evs.append(MusicEvent(pitch=KIT["clap"], volume=VEL["clap"] + 4,
                                  start_tick=t0 + 1440, end_tick=t0 + 1550))
        if dens >= 0.6:
            evs.append(MusicEvent(pitch=KIT["woodblock"], volume=VEL["woodblock"] - 5,
                                  start_tick=t0 + 720, end_tick=t0 + 800))
    phase2.set_unit(6, s, MusicUnit(events=evs))

# --- voice-leading sanity pass on the two melody voices (lead + violin)
vlc = VoiceLeadingRules(style="pop")
vl_flags = []
for voice_idx in (0, 3):
    for s in range(N_SECTIONS):
        u = phase2.matrix.get_unit((voice_idx, s))
        evs = [e for e in u.events if e.pitch > 0]
        evs.sort(key=lambda e: (e.start_tick, e.pitch))
        for i in range(1, len(evs)):
            a, b = evs[i - 1], evs[i]
            if b.start_tick - a.start_tick > 480:
                continue
            if abs(int(b.pitch) - int(a.pitch)) > 12:
                vl_flags.append((voice_idx, s, a.pitch, b.pitch, "leap>12"))
print("VOICE-LEADING leaps>12 flags:", len(vl_flags))


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
P2_MIDI = os.path.join(MIDI_DIR, "104-celtic-subset-variations.mid")
phase2.to_midi(P2_MIDI)
print("phase2 written", P2_MIDI, os.path.getsize(P2_MIDI), "bytes")

# ------------------------------------------------------------------ sidecars
from visualization.grid import write_grid_visualization  # noqa: E402

grid_path = os.path.join(ANALYSIS_DIR, "grid_visualization.txt")
write_grid_visualization(phase2.matrix, grid_path, ticks_per_character=120,
                         voice_names=vnames, bpm=BPM,
                         mode="Ab major / ABS-002 subset walk (Celtic rework)")
print("grid written", grid_path)

from workflows.provenance import write_provenance, AI_GENERATED  # noqa: E402

_prog = [_degree_of(w) for w in WALK_IDS]
for mid, phase, note in (
        (P1_MIDI, "1",
         "raw ABS-002 subset-walk draft (32-bar): pitch stream from walked "
         "subset pitch-class field, fractional off-grid rhythm, single marimba "
         "voice, no harmony/bass/drums. Redesign of 085 (std6 index.html fail)."),
        (P2_MIDI, "2",
         "abstract walk realized in Ab major over 8 sections: per-bar "
         "chord-tone quantization to root-position walked subset, 8th/16th grid "
         "lock, voice-leading cap, full celtic texture (marimba, french horn, "
         "cello, violin, bassoon, double bass, drums). 7 variation techniques: "
         "retrograde, inversion, register shift, transposition, augmentation, "
         "diminution, density/method change. Redesign of 085.")):
    write_provenance(
        mid, AI_GENERATED,
        "ABS-002 Subset Walker (rules.subset_network.PatternNetwork.walk) "
        "+ ABS-001 tension-curve steering + method-006 cadence close "
        "+ musicom rules (chord-tone quantize, grid snap, voice-leading)",
        parameters={"bpm": BPM, "key": KEY_NAME, "sections": N_SECTIONS,
                    "bars": N_BARS, "phase": phase, "seed": SEED,
                    "walk_seed": WALK_SEED, "subset_walk": WALK_IDS,
                    "bar_tension": BAR_TENSION, "progression": _prog,
                    "rework_of": "085-celtic-subset-walk",
                    "decision": "redesign (std6 index.html missing) + extend",
                    "layer": "abstract (ABS-002) -> concrete realization"},
        notes=note)
    print("provenance phase", phase)

# section midpoint chord (root + quality) — per-section harmonic regions
section_mid = {}
for s, name in enumerate(NAMES):
    mid_bar = s * 4 + 2
    pid = WALK_IDS[mid_bar]
    root_pc = _root_pc_ab(pid)
    section_mid[name] = {
        "midpoint_bar": mid_bar,
        "subset": pid,
        "degree": _degree_of(pid),
        "quality": _quality_of(pid),
        "root_pc": root_pc,
        "bars": [_degree_of(WALK_IDS[s * 4 + b]) for b in range(4)],
    }

with open(os.path.join(ANALYSIS_DIR, "summary.json"), "w") as f:
    json.dump({
        "project": "104-celtic-subset-variations",
        "style": "Celtic", "method": "ABS-002 Subset Walker",
        "layer": "abstract", "bpm": BPM, "key": KEY_NAME,
        "bars": N_BARS, "seed": SEED, "walk_seed": WALK_SEED,
        "sections": {n: 4 for n in NAMES},
        "subset_walk": WALK_IDS,
        "progression": _prog,
        "section_midpoint": section_mid,
        "voices": vnames,
        "variation_techniques": [
            "V1 retrograde (Bridge lead)",
            "V2 inversion (Bridge violin, pivot 74)",
            "V3 register shift (Bridge lead low 60-76 / ReelC lead +12)",
            "V4 transposition (ReelC violin +7)",
            "V5 augmentation (Outro bassoon 8th->whole)",
            "V6 diminution (ReelC bassoon 8th->16th)",
            "V7 density/method change (drum curve 0.35..1.0)",
        ],
        "rework_of": "085-celtic-subset-walk",
        "phase1": os.path.basename(P1_MIDI),
        "phase2": os.path.basename(P2_MIDI),
        "grid": os.path.basename(grid_path),
    }, f, indent=2)
print("summary.json written")

for p in (P1_MIDI, P2_MIDI, grid_path,
          os.path.join(ANALYSIS_DIR, "summary.json")):
    assert os.path.getsize(p) > 40, "too small: %s" % p
print("ALL SIZE ASSERTS PASSED")
print("WALK:", _prog)
