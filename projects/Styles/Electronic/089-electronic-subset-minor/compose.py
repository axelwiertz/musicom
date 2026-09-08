# -*- coding: utf-8 -*-
"""089-electronic-subset-minor — Electronic style / Method ABS-002 Subset
Walker (ABSTRACT layer) + ABS-001 tension-curve steering + method-006 cadence
close (rules layer). LAYER: abstract (weekly abstract-cadence run).

Two-phase architecture:
  Phase 1: raw generative draft — single-voice marimba stream. Each section's
           pitch material is drawn from the CURRENT WALKED SUBSET (chord) pc
           field (octave copies in the lead window), so the subset walk is
           directly audible. Rhythm = euclid-clustered RAW with fractional
           jitter (OFF-GRID fingerprint). No harmony, no bass, no drums.
  Phase 2: musicom rules post-process:
           1. GRID LOCK to 16th grid (120 ticks @ 112 BPM) — 078 rule.
           2. Scale snap to A-natural-minor, then chord-tone quantize per bar
              using GLOBAL bar lookup (s*BARS_PER + local_bar).
           3. Voice-leading leap cap <= 10 toward nearest chord tone.
           4. Texture: marimba lead (euclid groove), clarinet counterline,
              cello pad, dulcimer arp, double-bass roots, drum kit.
           5. Zero-drift landmark + validate() gate on BOTH phases, export
              via engine UnitMatrixComposer.to_midi().

Engine only: structures + workflows.unitmatrix_composer + rules.subset_network
+ rules.voice_leading. mido used READ-ONLY in audit.py for verification.
"""
import json
import os
import random
import sys

import numpy as np

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import (
    UnitMatrixComposer, create_empty_unit,
)

# instrument registry (source of truth — NOT pip-installed)
INSTR_DIR = "/opt/data/repos/musicom/projects/Instruments"
if INSTR_DIR not in sys.path:
    sys.path.insert(0, INSTR_DIR)
from instrument_registry import (          # noqa: E402
    MARIMBA, CLARINET, CELLO, DULCIMER, DOUBLE_BASS, DRUM_KIT,
)
from Percussion.drum_kit.drum_kit import KIT  # noqa: E402

SEED = 20260907
rng = np.random.default_rng(SEED)

# ------------------------------------------------------------------ dirs
PROJ = "/opt/data/projects/Styles/Electronic/089-electronic-subset-minor"
MIDI_DIR = os.path.join(PROJ, "MIDI")
AUDIO_DIR = os.path.join(PROJ, "Audio")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")
for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
    os.makedirs(d, exist_ok=True)

# ------------------------------------------------------------------ concept
BPM = 112
TPB = 480
BEATS = 4
BAR = TPB * BEATS            # 1920
GRID16 = 120                 # 16th-note grid @ 480 TPB
SECTION_TICKS = BAR * 4      # 7680 (4-bar sections)
# A natural minor pitch classes: A B C D E F G
SCALE_PCS = {9, 11, 0, 2, 4, 5, 7}
LEAD_LO, LEAD_HI = 60, 96     # marimba register (sweet 60-84)

NAMES = ["Intro", "Verse", "Chorus", "Break", "Verse2", "Outro"]
BARS_PER = 4
N_SECTIONS = len(NAMES)
N_BARS = N_SECTIONS * BARS_PER            # 24 bars

# ------------------------------------------------------------------ harmony
# The whole harmony comes from the ABSTRACT layer: a walk over the 12TET
# subset network (rules.subset_network.PatternNetwork) steered by a per-bar
# tension curve (ABS-001). 22 bars walked, then a rules-layer cadence close
# (method 006): bar 22 = V7 (dom77 = G7), bar 23 = i (min9 = Am).
from rules.subset_network import (         # noqa: E402
    PatternNetwork, standard_patterns,
)

_WALK_POOL = ['min9', 'dim11', 'maj0', 'min2', 'min4', 'maj5', 'maj7',
              'min79', 'min72', 'min74', 'maj75', 'maj70', 'dom77']
_lib = {p.id: p for p in standard_patterns() if p.id in _WALK_POOL}
_net = PatternNetwork(list(_lib.values()))
_WALK_SEED = 2371
_CURVE22 = [2.0] * 6 + [7.0] * 6 + [2.0] * 10
_walk = _net.walk('min9', 22, rng=random.Random(_WALK_SEED),
                  tension_curve=_CURVE22, home='min9')
assert len(_walk) == 22
PROG = _walk + ['dom77', 'min9']          # 24 bars: ... G7 Am cadence
PROG_NAME = {'min9': 'Am', 'dim11': 'Bdim', 'maj0': 'C', 'min2': 'Dm',
             'min4': 'Em', 'maj5': 'F', 'maj7': 'G', 'min79': 'Am7',
             'min72': 'Dm7', 'min74': 'Em7', 'maj75': 'Fmaj7',
             'maj70': 'Cmaj7', 'dom77': 'G7'}
PROG_DEG = {'min9': 'i', 'dim11': 'ii°', 'maj0': 'III', 'min2': 'iv',
            'min4': 'v', 'maj5': 'VI', 'maj7': 'VII', 'min79': 'i7',
            'min72': 'iv7', 'min74': 'v7', 'maj75': 'VImaj7',
            'maj70': 'IIImaj7', 'dom77': 'V7'}
ROOT_PC = {'min9': 9, 'dim11': 11, 'maj0': 0, 'min2': 2, 'min4': 4,
           'maj5': 5, 'maj7': 7, 'min79': 9, 'min72': 2, 'min74': 4,
           'maj75': 5, 'maj70': 0, 'dom77': 7}
assert len(PROG) == N_BARS

# chord-tone SET per pattern id (pc space; absolute built per instrument reg)
CHORD_PCS = {pid: frozenset(_lib[pid].subset) for pid in PROG_NAME}


def chord_tones_for(pid, lo=48, hi=96):
    """All absolute chord tones of pattern `pid` between lo..hi (octave
    copies). Root anchored so the lowest copy starts at the pattern root.
    Octave-shift range computed dynamically to guarantee coverage of [lo,hi]
    (fixed 2026-09-08: static range(-2,4) returned EMPTY sets for high roots
    like A (root 9) in the 60-96 window — e.g. min9 only reached base 45)."""
    pcs = sorted(CHORD_PCS[pid])
    root = ROOT_PC[pid]
    # sort pcs from the root upwards: (pc - root) % 12 order
    pcs_sorted = sorted(pcs, key=lambda pc: (pc - root) % 12)
    # lowest/highest octave shifts needed to cover lo..hi
    oct_lo = (lo - root) // 12 - 1
    oct_hi = (hi - root) // 12 + 1
    out = set()
    for oct_shift in range(oct_lo, oct_hi + 1):
        base = root + 12 * oct_shift
        for pc in pcs_sorted:
            p = base + (pc - root) % 12
            if lo <= p <= hi:
                out.add(p)
    return sorted(out)


def quantize_to_chord(pitch, tones):
    return min(tones, key=lambda c: (abs(c - pitch), c))


def scale_pcs_of(pitch):
    return pitch % 12 in SCALE_PCS


# ================================================================== PHASE 1
# Raw abstract-layer draft: single marimba voice. Each bar's pitches are
# sampled from the CURRENT WALKED SUBSET pc field (octave copies in the lead
# window) — the walk is audible as raw material. Rhythm = euclid(5,16) onset
# slots scaled by a jittered factor => fractional OFF-GRID ticks (the raw
# fingerprint preserved for phase 1).
def bjorklund_gaps(onsets, steps):
    """Euclidean rhythm as gap list between onsets (incl. wrap)."""
    # build the euclidean string
    if onsets == 0:
        return [steps]
    if onsets == steps:
        return [1] * steps
    groups = [[1] for _ in range(onsets)]
    rem = steps - onsets
    while rem >= onsets:
        for g in groups:
            g.append(0)
        rem -= onsets
    if rem > 0:
        big = groups[:rem]
        small = groups[rem:]
        for g in big:
            g.append(0)
        merged = []
        for i in range(max(len(big), len(small))):
            if i < len(big):
                merged.append(big[i])
            if i < len(small):
                merged.append(small[i])
        groups = merged
    flat = []
    for g in groups:
        flat.extend(g)
    ones = [i for i, v in enumerate(flat) if v == 1]
    gaps = []
    for i in range(len(ones)):
        gaps.append((ones[(i + 1) % len(ones)] - ones[i]) % steps)
    return gaps


def raw_subset_melody(seed, duration_ticks, n_events, bar_chords, slot_step):
    """Off-grid raw stream over `bar_chords` (one pattern id per bar)."""
    r = np.random.default_rng(seed)
    events = []
    tick = 0.0
    bar_idx = 0
    for i in range(n_events):
        # which bar are we in?
        bi = min(int(tick // BAR), len(bar_chords) - 1)
        pid = bar_chords[bi]
        tones = chord_tones_for(pid, lo=LEAD_LO, hi=LEAD_HI)
        # pitch drawn from the walked-subset field with a little contour bias
        prev = events[-1].pitch if events else 69
        near = min(tones, key=lambda c: (abs(c - prev), c))
        if r.random() < 0.62:
            pitch = near
        else:
            pitch = int(r.choice(tones))
        # fractional sojourn: euclid-ish slot * jitter => OFF-GRID
        tau = slot_step * (0.6 + 0.9 * r.random())
        st = int(round(tick))
        dur = max(60, int(tau * (0.5 + 0.5 * r.random())))
        en = st + dur
        if en > duration_ticks:
            en = duration_ticks
        if en > st:
            vel = int(np.clip(58 + 36 * r.random(), 48, 108))
            events.append(MusicEvent(pitch=pitch, volume=vel,
                                     start_tick=st, end_tick=en))
        tick += tau
        bar_idx = bi
    return events


phase1 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
phase1.create_matrix(num_voices=1, num_sections=N_SECTIONS)
phase1.add_voice("LeadRaw", program=MARIMBA.midi_program, channel=0)

DENSITY = {0: 30, 1: 44, 2: 60, 3: 22, 4: 44, 5: 26}
# mean slot step per section in ticks (larger = sparser)
SLOT = {0: 256, 1: 176, 2: 128, 3: 348, 4: 176, 5: 296}
for s, name in enumerate(NAMES):
    phase1.add_section(name, bars=BARS_PER)
    bar_chords = PROG[s * BARS_PER:(s + 1) * BARS_PER]
    evs = raw_subset_melody(SEED + s, SECTION_TICKS, DENSITY[s],
                            bar_chords, SLOT[s])
    phase1.set_unit(0, s, MusicUnit(events=evs))

# zero-drift landmark padding for phase 1 (exact section boundary)
for s in range(N_SECTIONS):
    u = phase1.matrix.get_unit((0, s))
    evs = list(u.events)
    has_landmark = any(e.pitch == 0 and e.end_tick == SECTION_TICKS
                       for e in evs)
    if not has_landmark:
        evs.append(MusicEvent(pitch=0, volume=0,
                              start_tick=SECTION_TICKS - 1,
                              end_tick=SECTION_TICKS))
    phase1.set_unit(0, s, MusicUnit(events=evs))

ok1, msg1 = phase1.validate()
print("PHASE1 validate:", msg1)
P1_MIDI = os.path.join(MIDI_DIR, "089-electronic-subset-minor-phase1.mid")
phase1.to_midi(P1_MIDI)
print("phase1 written", P1_MIDI)


# ================================================================== PHASE 2
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


phase2 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
VOICES = [
    ("Lead",    MARIMBA.midi_program, 0),     # Marimba (subset-walk lead)
    ("Clarinet", CLARINET.midi_program, 1),   # Clarinet (counterline)
    ("Cello",   CELLO.midi_program, 2),       # Cello (sustained pad)
    ("Dulcimer", DULCIMER.midi_program, 3),   # Dulcimer (16th arp)
    ("Bass",    DOUBLE_BASS.midi_program, 4), # Double Bass (roots)
    ("Drums",   0, 9),                        # percussion channel
]
N_V = len(VOICES)
phase2.create_matrix(num_voices=N_V, num_sections=N_SECTIONS)
vnames = [v[0] for v in VOICES]
for name, prog, ch in VOICES:
    phase2.add_voice(name, program=prog, channel=ch)
for n in NAMES:
    phase2.add_section(n, bars=BARS_PER)


def global_bar(s, local_tick):
    return min(s * BARS_PER + local_tick // BAR, N_BARS - 1)


# --- lead: GRID LOCK FIRST, then scale + chord-tone quantize (078 rule)
for s in range(N_SECTIONS):
    raw_unit = phase1.matrix.get_unit((0, s))
    raw_events = quantize_lead_to_grid(list(raw_unit.events), grid=GRID16)
    q_events = []
    for e in raw_events:
        if e.pitch == 0:
            q_events.append(e)
            continue
        if e.pitch % 12 not in SCALE_PCS:
            # snap to nearest scale degree first
            e = MusicEvent(pitch=_snap_scale(e.pitch), volume=e.volume,
                           start_tick=e.start_tick, end_tick=e.end_tick)
        bar = global_bar(s, e.start_tick)
        tones = chord_tones_for(PROG[bar], lo=LEAD_LO - 12, hi=LEAD_HI)
        qp = quantize_to_chord(e.pitch, tones)
        q_events.append(MusicEvent(pitch=qp, volume=e.volume,
                                   start_tick=e.start_tick,
                                   end_tick=e.end_tick))

# --- LEAD: keep in marimba register 60-96 after quantize (pool built down to
#     48 for leap-cap candidates; final pass clamps to instrument range).
    # voice-leading: cap leaps <= 10 toward nearest chord tone
    for i in range(1, len(q_events)):
        e = q_events[i]
        if e.pitch == 0:
            continue
        p_prev = q_events[i - 1].pitch if q_events[i - 1].pitch else LEAD_HI
        if abs(e.pitch - p_prev) > 10:
            bar = global_bar(s, e.start_tick)
            tones = chord_tones_for(PROG[bar], lo=LEAD_LO - 12, hi=LEAD_HI)
            e = MusicEvent(pitch=min(tones, key=lambda c: (abs(c - p_prev), c)),
                           volume=e.volume, start_tick=e.start_tick,
                           end_tick=e.end_tick)
            q_events[i] = e
        # clamp to marimba in-range register
        if e.pitch < MARIMBA.range_min or e.pitch > MARIMBA.range_max:
            bar = global_bar(s, e.start_tick)
            tones = chord_tones_for(PROG[bar], lo=MARIMBA.range_min,
                                    hi=MARIMBA.range_max)
            if tones:
                e = MusicEvent(pitch=min(tones,
                                         key=lambda c: (abs(c - e.pitch), c)),
                               volume=e.volume, start_tick=e.start_tick,
                               end_tick=e.end_tick)
                q_events[i] = e
    phase2.set_unit(0, s, MusicUnit(events=q_events))


def _snap_scale(pitch):
    """Snap to nearest A-natural-minor absolute pitch."""
    best = None
    for oct_shift in range(3, 9):
        for pc in sorted(SCALE_PCS):
            p = pc + 12 * oct_shift
            if 48 <= p <= 108:
                d = abs(p - pitch)
                if best is None or d < best[0]:
                    best = (d, p)
    return best[1]


# --- cello: sustained whole-bar pad. Triads only (drop 7th for pad clarity)
#     on tetrad bars use root+3rd+7th? Simpler: pad = lowest 3 chord tones in
#     cello range 36-72 (root position each bar).
for bar in range(N_BARS):
    s, b = divmod(bar, BARS_PER)
    tones = chord_tones_for(PROG[bar], lo=36, hi=72)
    # keep root position: pick root + next two chord tones above it
    root = ROOT_PC[bar] if False else None
    t0 = b * BAR
    e = []
    # triad shell: tones[0..2] lowest 3 in cello range
    shell = tones[:3] if len(tones) >= 3 else tones
    for k, p in enumerate(shell):
        e.append(MusicEvent(pitch=p, volume=46 + 5 * k,
                            start_tick=t0, end_tick=t0 + BAR - 60))
    unit = phase2.matrix.get_unit((2, s))
    events = list(unit.events) if unit is not None else []
    events.extend(e)
    phase2.set_unit(2, s, MusicUnit(events=events))

# --- dulcimer: 16th arpeggio pattern (on-grid), octave 4/5, chord tones
for bar in range(N_BARS):
    s, b = divmod(bar, BARS_PER)
    tones = chord_tones_for(PROG[bar], lo=60, hi=96)
    if not tones:
        tones = chord_tones_for(PROG[bar], lo=48, hi=96)
    t0 = b * BAR
    e = []
    # arp order: root up 5th up 3rd pattern cycling (pattern length 4 per beat)
    for k in range(0, BAR, GRID16):
        idx = (k // GRID16) % len(tones)
        p = tones[idx]
        e.append(MusicEvent(pitch=p, volume=42,
                            start_tick=t0 + k, end_tick=t0 + k + 100))
    unit = phase2.matrix.get_unit((3, s))
    events = list(unit.events) if unit is not None else []
    events.extend(e)
    phase2.set_unit(3, s, MusicUnit(events=events))

# --- bass: root pulse 8ths (root + 5th alternation), 4/4 root on beats
for bar in range(N_BARS):
    s, b = divmod(bar, BARS_PER)
    pid = PROG[bar]
    root_pc = ROOT_PC[pid]
    # find root in double-bass range 28-74, lowest
    bass_tones = chord_tones_for(pid, lo=28, hi=55)
    root = bass_tones[0]
    fifth = (root + 7) if (root + 7) <= 55 and ((root + 7) % 12) in \
        SCALE_PCS or (root + 7) <= 55 else root
    # fifth chord tone above root if in scale
    fifth_c = min(bass_tones, key=lambda c: (abs(c - (root + 7)), c)) \
        if any(36 <= c <= 55 for c in bass_tones) else root
    if abs(fifth_c - root) > 12:
        fifth_c = root
    t0 = b * BAR
    e = []
    for k in range(0, BAR, 240):
        on_beat = (k // 240) % 2 == 0
        p = root if on_beat else fifth_c
        if p == 0:
            p = root
        e.append(MusicEvent(pitch=p, volume=78 if on_beat else 60,
                            start_tick=t0 + k, end_tick=t0 + k + 200))
    unit = phase2.matrix.get_unit((4, s))
    events = list(unit.events) if unit is not None else []
    events.extend(e)
    phase2.set_unit(4, s, MusicUnit(events=events))

# --- drums: minimal electronic kit. Kick 1&3, snare 2&4, hats 8ths (16ths in
#     chorus), break drops out, outro sparse.
K = KIT
DRUM_PLAN = {
    0: dict(hat=36, kick=70, snare=None, crash=False, hat16=False),
    1: dict(hat=52, kick=84, snare=72, crash=False, hat16=False),
    2: dict(hat=60, kick=96, snare=92, crash=True, hat16=True),
    3: dict(hat=40, kick=66, snare=None, crash=False, hat16=False),
    4: dict(hat=52, kick=84, snare=72, crash=False, hat16=False),
    5: dict(hat=34, kick=64, snare=None, crash=False, hat16=False),
}
for s in range(N_SECTIONS):
    plan = DRUM_PLAN[s]
    evs = []
    for bar in range(BARS_PER):
        t0 = bar * BAR
        hat_step = 120 if plan["hat16"] else 240
        for k in range(0, BAR, hat_step):
            evs.append(MusicEvent(pitch=K["hat_closed"], volume=plan["hat"],
                                  start_tick=t0 + k, end_tick=t0 + k + 60))
        for kb in (0, 960):
            evs.append(MusicEvent(pitch=K["kick"], volume=plan["kick"],
                                  start_tick=t0 + kb, end_tick=t0 + kb + 140))
        if plan["snare"] is not None:
            for sb in (960, 2880):
                evs.append(MusicEvent(pitch=K["snare"], volume=plan["snare"],
                                      start_tick=t0 + sb,
                                      end_tick=t0 + sb + 120))
        if plan["crash"]:
            evs.append(MusicEvent(pitch=K["crash"], volume=64,
                                  start_tick=t0, end_tick=t0 + 600))
    phase2.set_unit(5, s, MusicUnit(events=evs))

# --- clarinet counterline (added after main texture): answers the marimba on
#     beats 2 & 4 with 8th pairs, chord tones in clarinet range 52-96.
for s in range(N_SECTIONS):
    r = np.random.default_rng(SEED + 500 + s)
    evs = []
    for bar in range(BARS_PER):
        pid = PROG[s * BARS_PER + bar]
        tones = chord_tones_for(pid, lo=60, hi=96)
        if not tones:
            tones = chord_tones_for(pid, lo=52, hi=88)
        t0 = bar * BAR
        for beat in (1, 3):
            st = t0 + beat * 480
            p = int(r.choice(tones))
            evs.append(MusicEvent(pitch=p, volume=58,
                                  start_tick=st, end_tick=st + 220))
            st2 = st + 240
            if st2 < t0 + BAR:
                p2 = int(r.choice(tones))
                evs.append(MusicEvent(pitch=p2, volume=50,
                                      start_tick=st2, end_tick=st2 + 220))
    phase2.set_unit(1, s, MusicUnit(events=evs))

# --- voice-leading check (rules.voice_leading): bass + lead per bar pair ---
from rules.voice_leading import VoiceLeadingRules  # noqa: E402

vlc = VoiceLeadingRules(style="classical")
vl_flags = []
for bar in range(N_BARS - 1):
    s, b = divmod(bar, BARS_PER)
    u = phase2.matrix.get_unit((0, s))
    evs = [e for e in u.events if e.pitch > 0
           and b * BAR <= e.start_tick < (b + 1) * BAR]
    evs_next = [e for e in u.events if e.pitch > 0
                and (b + 1) * BAR <= e.start_tick < (b + 2) * BAR]
    if not evs or not evs_next:
        continue
    bass_a = chord_tones_for(PROG[bar], lo=28, hi=55)[0]
    bass_b = chord_tones_for(PROG[bar + 1], lo=28, hi=55)[0]
    lead_a = evs[0].pitch
    lead_b = evs_next[0].pitch
    viol = vlc.check_parallel_motion([bass_a, lead_a], [bass_b, lead_b])
    if viol:
        vl_flags.append((bar, viol))
    hid = vlc.check_hidden_fifths([bass_a, lead_a], [bass_b, lead_b])
    if hid:
        vl_flags.append((bar, hid))
print("VOICE-LEADING flags (bass+lead):", vl_flags[:8], "total",
      len(vl_flags))


def fix_vl(phase2, bar):
    """Nudge the lead's first note of bar+1 off a hidden 5th/8ve with bass."""
    s, b = divmod(bar + 1, BARS_PER)
    if b >= BARS_PER:
        return False
    u = phase2.matrix.get_unit((0, s))
    evs = list(u.events)
    target = None
    for e in evs:
        if e.pitch > 0 and b * BAR <= e.start_tick < (b + 1) * BAR:
            target = e
            break
    if target is None:
        return False
    pid = PROG[bar + 1]
    tones = chord_tones_for(pid, lo=LEAD_LO - 12, hi=LEAD_HI)
    bass = chord_tones_for(pid, lo=28, hi=55)[0]
    cands = [t for t in tones if abs((t - bass) % 12) not in (0, 7)]
    if not cands:
        return False
    target.pitch = min(cands, key=lambda c: (abs(c - target.pitch), c))
    phase2.set_unit(0, s, MusicUnit(events=evs))
    return True


for (bar, _viol) in list(vl_flags):
    if fix_vl(phase2, bar):
        print("VL fix applied at bar", bar)

# re-run voice-leading check after corrections
vl_flags2 = []
for bar in range(N_BARS - 1):
    s, b = divmod(bar, BARS_PER)
    u = phase2.matrix.get_unit((0, s))
    evs = [e for e in u.events if e.pitch > 0
           and b * BAR <= e.start_tick < (b + 1) * BAR]
    evs_next = [e for e in u.events if e.pitch > 0
                and (b + 1) * BAR <= e.start_tick < (b + 2) * BAR]
    if not evs or not evs_next:
        continue
    bass_a = chord_tones_for(PROG[bar], lo=28, hi=55)[0]
    bass_b = chord_tones_for(PROG[bar + 1], lo=28, hi=55)[0]
    lead_a = evs[0].pitch
    lead_b = evs_next[0].pitch
    viol = vlc.check_parallel_motion([bass_a, lead_a], [bass_b, lead_b])
    if viol:
        vl_flags2.append((bar, viol))
    hid = vlc.check_hidden_fifths([bass_a, lead_a], [bass_b, lead_b])
    if hid:
        vl_flags2.append((bar, hid))
print("VOICE-LEADING re-check (after fixes):", vl_flags2[:8], "total",
      len(vl_flags2))
vl_flags = vl_flags2


# --- normalize every cell to exact section boundary (zero-drift invariant) ---
def normalize_cell(unit, total_ticks):
    evs = list(unit.events)
    for e in evs:
        if e.end_tick > total_ticks:
            e.end_tick = total_ticks
    has_landmark = any(e.pitch == 0 and e.end_tick == total_ticks
                       for e in evs)
    if not has_landmark:
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

P2_MIDI = os.path.join(MIDI_DIR, "089-electronic-subset-minor.mid")
phase2.to_midi(P2_MIDI)
print("phase2 written", P2_MIDI)

# ---------------------------------------------------------------- analysis
from visualization.grid import write_grid_visualization  # noqa: E402

grid_path = os.path.join(ANALYSIS_DIR, "grid_visualization.txt")
write_grid_visualization(phase2.matrix, grid_path, ticks_per_character=120,
                         voice_names=vnames, bpm=BPM,
                         mode="A minor / ABS-002 subset walk + electronic texture")
print("grid written", grid_path)

# provenance
from workflows.provenance import write_provenance, AI_GENERATED  # noqa: E402

for mid, phase, note in (
        (P1_MIDI, "1",
         "raw abstract-layer subset-walk draft: single marimba voice, pitches "
         "sampled from the CURRENT WALKED SUBSET pc field, euclid-clustered "
         "rhythm with fractional jitter (off-grid ticks), no harmony/bass/drums"),
        (P2_MIDI, "2",
         "16th-grid locked, A-natural-minor + chord-tone quantized to the "
         "subset-walk progression, marimba/clarinet/cello/dulcimer/double-bass/"
         "drums texture, voice-leading check, full arrangement")):
    write_provenance(
        mid, AI_GENERATED, "ABS-002 Subset Walker + ABS-001 tension curve "
        "(ABSTRACT layer)",
        parameters={"bpm": BPM, "key": "A natural minor (aeolian)",
                    "sections": N_SECTIONS, "bars": N_BARS, "phase": phase,
                    "progression": [PROG_NAME[p] for p in PROG],
                    "walk_seed": _WALK_SEED, "grid16": GRID16,
                    "layer": "abstract"},
        notes=note)
    print("provenance for phase", phase)

# voice-leading audit + summary
with open(os.path.join(ANALYSIS_DIR, "vl_audit.json"), "w") as f:
    json.dump({
        "voice_leading_flags": [str(x) for x in vl_flags],
        "voice_leading_flag_count": len(vl_flags),
        "phase1_validate": msg1,
        "phase2_validate": msg2,
    }, f, indent=2)

with open(os.path.join(ANALYSIS_DIR, "summary.json"), "w") as f:
    json.dump({
        "project": "089-electronic-subset-minor",
        "style": "Electronic",
        "method": "ABS-002 Subset Walker + ABS-001 tension curve + method-006 cadence close",
        "layer": "abstract",
        "bpm": BPM, "key": "A natural minor", "tempo": BPM,
        "bars": N_BARS,
        "sections": {n: BARS_PER for n in NAMES},
        "progression": [PROG_NAME[p] for p in PROG],
        "progression_degrees": [PROG_DEG[p] for p in PROG],
        "voices": vnames,
        "phase1": os.path.basename(P1_MIDI),
        "phase2": os.path.basename(P2_MIDI),
        "grid": os.path.basename(grid_path),
        "seed": SEED, "walk_seed": _WALK_SEED,
    }, f, indent=2)

for p in (P1_MIDI, P2_MIDI, grid_path,
          os.path.join(ANALYSIS_DIR, "summary.json"),
          os.path.join(ANALYSIS_DIR, "vl_audit.json")):
    assert os.path.getsize(p) > 40, "too small: %s" % p
print("ALL SIZE ASSERTS PASSED")
print("PROGRESSION:", [PROG_NAME[p] for p in PROG])
