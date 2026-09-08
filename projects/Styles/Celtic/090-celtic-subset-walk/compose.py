# -*- coding: utf-8 -*-
"""090-celtic-subset-walk - Celtic style / ABSTRACT layer:
ABS-002 Subset Walker + ABS-001 tension-curve steering + rules-layer
method-006 cadence close (forced A7 -> Dm on the final two bars).

Phase 1: raw generative draft (single bagpipe voice). Pitch = raw pc from the
CURRENT WALKED SUBSET (walk directly audible), placed in the bagpipe register
by choosing the nearest pitch of that pc in range; rhythm = 8th-note grid with
FRACTIONAL jitter (off-grid fingerprint). No harmony, no bass, no drums.
Phase 2: musicom rules post-process: 16th-grid lock (078 rule) -> D-minor
scale snap -> chord-tone quantize per global bar -> voice-leading check and
correction -> full 6-voice Celtic texture (violin lead, flute counterline,
cello pad, piano harp-rolls, double-bass roots, drum kit).

Engine only: structures + workflows.unitmatrix_composer + rules.voice_leading +
rules.subset_network (abstract layer). mido used READ-ONLY in audit.py.
"""
import os
import sys
import json

import numpy as np

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import (
    UnitMatrixComposer, create_empty_unit,
)
from rules.subset_network import standard_patterns, PatternNetwork

# instrument registry (source of truth - NOT pip-installed)
INSTR_DIR = "/opt/data/repos/musicom/projects/Instruments"
if INSTR_DIR not in sys.path:
    sys.path.insert(0, INSTR_DIR)
from instrument_registry import (  # noqa: E402
    VIOLIN, FLUTE, CELLO, PIANO, DOUBLE_BASS, DRUM_KIT, BAGPIPE,
)
from Percussion.drum_kit.drum_kit import KIT  # noqa: E402

SEED = 20260908
rng = np.random.default_rng(SEED)

# ---------------------------------------------------------------- project dirs
PROJ = "/opt/data/projects/Styles/Celtic/090-celtic-subset-walk"
MIDI_DIR = os.path.join(PROJ, "MIDI")
AUDIO_DIR = os.path.join(PROJ, "Audio")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")
for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
    os.makedirs(d, exist_ok=True)

# ---------------------------------------------------------------- concept
BPM = 108
TPB = 480
BEATS = 4
BAR = TPB * BEATS            # 1920
GRID16 = 120                 # 16th-note grid @ 480 TPB
GRID8 = 240                  # 8th-note grid
SECTION_TICKS = BAR * 4      # 7680 (4 bars per section)

# D aeolian (natural minor) scale pitches in bagpipe/violin registers
SCALE = [38, 40, 41, 43, 45, 46, 48, 50, 52, 53, 55, 57, 58, 60, 62, 64, 65,
         67, 69, 70, 72, 74, 76, 77, 79, 81, 83, 84]
SCALE_PCS = {2, 4, 5, 7, 9, 11, 0}   # D E F G A Bb C

# ---------------------------------------------------------------- harmony
# Abstract layer: 12TET subset walk over D-minor diatonic anchors.
lib = {p.id: p for p in standard_patterns()}
POOL_IDS = ["min2", "maj5", "min9", "maj0", "maj10", "min7",
            "dom79", "dim1", "min70", "dom77", "maj75", "min4"]
POOL = [lib[i] for i in POOL_IDS]
NET = PatternNetwork(POOL)
# tension curve across 24 bars: intro low -> verse rise -> chorus peak ->
# break settle -> outro resolve (22 bars walked, 2 forced cadence bars)
TENSION_CURVE = [2.0] * 6 + [6.0] * 6 + [8.5] * 6 + [4.0] * 3 + [2.0] * 1
import random as _random
_walk_rng = _random.Random(SEED)
WALK = NET.walk("min2", 22, rng=_walk_rng, tension_curve=TENSION_CURVE,
                home="min2") + ["dom79", "min2"]   # forced A7 -> Dm cadence
assert len(WALK) == 24

# pattern id -> chord label (D-minor functional reading)
PAT_LABEL = {
    "min2": "i", "maj5": "III", "min9": "v", "maj0": "VII",
    "maj10": "VI", "min7": "iv", "dom79": "V7", "dim1": "vii*",
    "min70": "i7", "dom77": "bVII7", "maj75": "IIImaj7", "min4": "ii",
}
CHORD_LABELS = [PAT_LABEL[pid] for pid in WALK]

# concrete chord realization: root MIDI pitch + chord tone intervals
# (roots in octave 3; intervals relative to root, minor/major/dim/dom7)
CHORD_DEF = {
    "min2":   (50, "m"),    # Dm   i
    "maj5":   (53, "M"),    # F    III
    "min9":   (57, "m"),    # Am   v
    "maj0":   (48, "M"),    # C    VII
    "maj10":  (46, "M"),    # Bb   VI
    "min7":   (55, "m"),    # Gm   iv
    "dom79":  (57, "7"),    # A7   V7
    "dim1":   (49, "d"),    # C#dim vii*
    "min70":  (50, "m7"),   # Dm7  i7
    "dom77":  (55, "7"),    # G7   bVII7
    "maj75":  (53, "M7"),   # Fmaj7 IIImaj7
    "min4":   (52, "m"),    # Em   ii
}
IV = {"m": (0, 3, 7), "M": (0, 4, 7), "d": (0, 3, 6), "7": (0, 4, 7, 10),
      "m7": (0, 3, 7, 10), "M7": (0, 4, 7, 11)}


def chord_pcs_of(pid):
    root, kind = CHORD_DEF[pid]
    return set((root + i) % 12 for i in IV[kind])


def chord_tones(pid, lo, hi):
    root, kind = CHORD_DEF[pid]
    tones = set()
    for oct_shift in range(-2, 5):
        for i in IV[kind]:
            p = root + i + oct_shift * 12
            if lo <= p <= hi:
                tones.add(p)
    return sorted(tones)


def quantize_to_chord(pitch, tones):
    return min(tones, key=lambda c: (abs(c - pitch), c))


def nearest_pc_pitch(pc, lo, hi, anchor=None):
    """Nearest pitch in [lo, hi] with pitch class `pc`. If anchor given,
    prefer the closest to anchor (voice-leading)."""
    cands = [p for p in range(lo, hi + 1) if p % 12 == pc]
    if not cands:
        return None
    if anchor is None:
        return min(cands, key=lambda p: (abs(p - (lo + hi) // 2), p))
    return min(cands, key=lambda p: (abs(p - anchor), p))


NAMES = ["Intro", "Verse", "Chorus", "Break", "Chorus2", "Outro"]
BARS_PER = 4
N_SECTIONS = len(NAMES)
N_BARS = N_SECTIONS * BARS_PER            # 24

# ---------------------------------------------------------------- phase 1
# Raw abstract-layer draft: single bagpipe voice. For each 8th slot, with
# probability p_onset (section density), emit a note whose pitch class is
# sampled from the CURRENT WALKED SUBSET pcs (the walk is directly audible as
# the harmony colour). Rhythm = 8th grid + fractional jitter (off-grid raw
# fingerprint). Durations = fractional legato-ish until next onset.
P_ONSET = {0: 0.55, 1: 0.70, 2: 0.85, 3: 0.60, 4: 0.85, 5: 0.50}
CENTERS = {0: 67.0, 1: 69.0, 2: 74.0, 3: 67.0, 4: 74.0, 5: 62.0}
rng1 = np.random.default_rng(SEED + 1)

phase1 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
phase1.create_matrix(num_voices=1, num_sections=N_SECTIONS)
phase1.add_voice("LeadRaw", program=BAGPIPE.midi_program, channel=0)

for s, name in enumerate(NAMES):
    evs = []
    tick = 0.0
    prev_end = 0.0
    bar_offset = s * BARS_PER
    for slot in range(SECTION_TICKS // GRID8):
        bar = bar_offset + (slot * GRID8) // BAR
        pid = WALK[bar]
        pcs = sorted(lib[pid].pcs)
        if rng1.random() < P_ONSET[s]:
            pc = int(rng1.choice(pcs))
            # fractional jitter: -40..+40 ticks off the 8th grid
            st = slot * GRID8 + int(rng1.integers(-40, 41))
            st = max(0, min(st, SECTION_TICKS - 1))
            # register: bagpipe sweet band, biased to section center
            anchor = CENTERS[s] + rng1.normal(0, 4)
            p = nearest_pc_pitch(pc, 60, 88, anchor=int(anchor))
            if p is None:
                continue
            if st < prev_end - 10:
                st = int(prev_end) + 10
            dur = GRID8 * (0.85 + 0.4 * rng1.random())
            en = st + int(dur)
            if en > SECTION_TICKS:
                en = SECTION_TICKS
            if en > st:
                vel = int(np.clip(58 + 30 * rng1.random(), 52, 100))
                evs.append(MusicEvent(pitch=p, volume=vel,
                                      start_tick=st, end_tick=en))
                prev_end = float(en)
        tick += GRID8
    phase1.add_section(name, bars=BARS_PER)
    phase1.set_unit(0, s, MusicUnit(events=evs))

# zero-drift landmark padding for phase 1 (exact section boundary)
for s in range(N_SECTIONS):
    u = phase1.matrix.get_unit((0, s))
    evs = list(u.events)
    has_landmark = any(e.pitch == 0 and e.end_tick == SECTION_TICKS
                       for e in evs)
    if not has_landmark:
        evs.append(MusicEvent(pitch=0, volume=0, start_tick=SECTION_TICKS - 1,
                              end_tick=SECTION_TICKS))
    phase1.set_unit(0, s, MusicUnit(events=evs))

ok1, msg1 = phase1.validate()
print("PHASE1 validate:", msg1)
P1_MIDI = os.path.join(MIDI_DIR, "090-celtic-subset-walk-phase1.mid")
phase1.to_midi(P1_MIDI)
print("phase1 written", P1_MIDI)

# ---------------------------------------------------------------- phase 2
def quantize_to_grid(events, grid=GRID16):
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
    ("Lead",    VIOLIN.midi_program, 0),      # Violin (subset-walk lead)
    ("Flute",   FLUTE.midi_program, 1),       # Flute (counterline)
    ("Cello",   CELLO.midi_program, 2),       # Cello (sustained pad)
    ("Piano",   PIANO.midi_program, 3),       # Piano (harp-roll arpeggio)
    ("Bass",    DOUBLE_BASS.midi_program, 4), # Double Bass (root pulse)
    ("Drums",   DRUM_KIT.midi_program, 9),    # percussion channel
]
N_V = len(VOICES)
phase2.create_matrix(num_voices=N_V, num_sections=N_SECTIONS)
vnames = [v[0] for v in VOICES]
for name, prog, ch in VOICES:
    phase2.add_voice(name, program=prog, channel=ch)
for n in NAMES:
    phase2.add_section(n, bars=BARS_PER)

# --- lead: GRID LOCK FIRST, then scale snap + chord-tone quantize (078 rule)
for s, name in enumerate(NAMES):
    raw_unit = phase1.matrix.get_unit((0, s))
    raw_events = quantize_to_grid(list(raw_unit.events), grid=GRID16)
    q_events = []
    for e in raw_events:
        if e.pitch == 0:
            q_events.append(e)
            continue
        # scale snap (D aeolian)
        sc = min(SCALE, key=lambda c: (abs(c - e.pitch), c))
        local_bar = e.start_tick // BAR
        bar = s * BARS_PER + local_bar
        if bar >= N_BARS:
            bar = N_BARS - 1
        pid = WALK[bar]
        tones = chord_tones(pid, lo=60, hi=88)   # violin lead register
        qp = quantize_to_chord(sc, tones)
        q_events.append(MusicEvent(pitch=qp, volume=e.volume,
                                   start_tick=e.start_tick,
                                   end_tick=e.end_tick))
    # voice-leading: cap leaps <= 10 toward nearest chord tone of next event
    for i in range(1, len(q_events)):
        e = q_events[i]
        if e.pitch == 0:
            continue
        p_prev = q_events[i - 1].pitch if q_events[i - 1].pitch else 74
        if abs(e.pitch - p_prev) > 10:
            local_bar = e.start_tick // BAR
            bar = s * BARS_PER + local_bar
            if bar >= N_BARS:
                bar = N_BARS - 1
            tones = chord_tones(WALK[bar], lo=60, hi=88)
            e.pitch = min(tones, key=lambda c: (abs(c - p_prev), c))
    phase2.set_unit(0, s, MusicUnit(events=q_events))

# --- cello: sustained whole-bar pad (root-position triad shell, octave 3/4)
for bar in range(N_BARS):
    s, b = divmod(bar, BARS_PER)
    pid = WALK[bar]
    root, kind = CHORD_DEF[pid]
    tones = [root - 12, root - 12 + IV[kind][1], root - 12 + IV[kind][2]]
    tones = sorted(set(p for p in tones if 36 <= p <= 62))
    t0 = b * BAR
    e = []
    for k, p in enumerate(tones):
        e.append(MusicEvent(pitch=p, volume=46 + 4 * k,
                            start_tick=t0, end_tick=t0 + BAR - 60))
    unit = phase2.matrix.get_unit((2, s))
    events = list(unit.events) if unit is not None else []
    events.extend(e)
    phase2.set_unit(2, s, MusicUnit(events=events))

# --- flute: 8th-note answering counterline (chord tones +12 window)
for s in range(N_SECTIONS):
    r = np.random.default_rng(SEED + 300 + s)
    evs = []
    for bar in range(BARS_PER):
        t0 = bar * BAR
        pid = WALK[s * BARS_PER + bar]
        tones = [t for t in chord_tones(pid, lo=72, hi=88)]
        if not tones:
            tones = chord_tones(pid, lo=60, hi=76)
        # answers on beats 2 & 4 with 8th pickup into next beat
        for beat in (1, 3):
            st = t0 + beat * 480
            pitch = int(r.choice(tones))
            evs.append(MusicEvent(pitch=pitch, volume=62,
                                  start_tick=st, end_tick=st + 240))
            st2 = st + 240
            if st2 < t0 + BAR:
                pitch2 = int(r.choice(tones))
                evs.append(MusicEvent(pitch=pitch2, volume=56,
                                      start_tick=st2, end_tick=st2 + 240))
    phase2.set_unit(1, s, MusicUnit(events=evs))

# --- piano: harp-style 16th arpeggio rolls (chord tones, octave 4/5)
for bar in range(N_BARS):
    s, b = divmod(bar, BARS_PER)
    pid = WALK[bar]
    tones = chord_tones(pid, lo=60, hi=84)
    t0 = b * BAR
    e = []
    n = len(tones)
    for k in range(0, BAR, 120):
        idx = (k // 120) % n
        p = tones[idx]
        e.append(MusicEvent(pitch=p, volume=54,
                            start_tick=t0 + k, end_tick=t0 + k + 80))
    unit = phase2.matrix.get_unit((3, s))
    events = list(unit.events) if unit is not None else []
    events.extend(e)
    phase2.set_unit(3, s, MusicUnit(events=events))

# --- bass: root pulse. quarter-note roots; 8th push into next bar in
#     Chorus/Break; octave pops in choruses. All on-grid.
BASS_8TH = {2, 4}          # sections with 8th-note pulse
BASS_PUSH = {2, 3, 4}      # sections with 16th end-push
BASS_OCT = {2, 4}          # octave pops in choruses
for bar in range(N_BARS):
    s, b = divmod(bar, BARS_PER)
    root, _kind = CHORD_DEF[WALK[bar]]
    root_pc = root % 12
    # double-bass register 28..58; nearest pitch of root pc around octave 2
    bass = nearest_pc_pitch(root_pc, 33, 52, anchor=41)
    if bass is None:
        bass = 41
    octv = bass + 12 if bass + 12 <= 58 else bass
    t0 = b * BAR
    e = []
    step = 240 if s in BASS_8TH else 480
    for k in range(0, BAR, step):
        on_beat = (k // step) % 2 == 0
        pitch = bass if on_beat else (octv if s in BASS_OCT else bass)
        e.append(MusicEvent(pitch=pitch, volume=80 if on_beat else 64,
                            start_tick=t0 + k, end_tick=t0 + k + step - 40))
    if s in BASS_PUSH and b != BARS_PER - 1:
        e.append(MusicEvent(pitch=bass, volume=70,
                            start_tick=t0 + BAR - 120, end_tick=t0 + BAR - 20))
    unit = phase2.matrix.get_unit((4, s))
    events = list(unit.events) if unit is not None else []
    events.extend(e)
    phase2.set_unit(4, s, MusicUnit(events=events))

# --- drums: Celtic-ish body. Intro sparse, Verse groove, Chorus full (16th
#     hats, claps), Break half-time feel (low tom on 3), Outro sparse.
K = KIT
DRUM_PLAN = {
    0: dict(hat=38, kick=58, snare=None, clap=None, crash=False, hat16=False,
            tom=None),
    1: dict(hat=50, kick=76, snare=68, clap=None, crash=False, hat16=False,
            tom=None),
    2: dict(hat=56, kick=92, snare=88, clap=82, crash=True, hat16=True,
            tom=None),
    3: dict(hat=40, kick=66, snare=62, clap=None, crash=False, hat16=False,
            tom="mid"),
    4: dict(hat=56, kick=92, snare=88, clap=82, crash=True, hat16=True,
            tom=None),
    5: dict(hat=34, kick=60, snare=None, clap=None, crash=False, hat16=False,
            tom=None),
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
        # kick: 1 & 3 (with "&" ghosts in choruses)
        kick_beats = [0, 960]
        if s in (2, 4):
            kick_beats += [240, 1440]
        for kb in kick_beats:
            evs.append(MusicEvent(pitch=K["kick"], volume=plan["kick"],
                                  start_tick=t0 + kb, end_tick=t0 + kb + 120))
        if plan["snare"] is not None:
            for sb in (960, 2880):
                evs.append(MusicEvent(pitch=K["snare"], volume=plan["snare"],
                                      start_tick=t0 + sb, end_tick=t0 + sb + 120))
        if plan["clap"] is not None:
            for sb in (960, 2880):
                evs.append(MusicEvent(pitch=K["clap"], volume=plan["clap"],
                                      start_tick=t0 + sb, end_tick=t0 + sb + 120))
        if plan["crash"]:
            evs.append(MusicEvent(pitch=K["crash"], volume=68,
                                  start_tick=t0, end_tick=t0 + 500))
        if plan["tom"] == "mid":
            evs.append(MusicEvent(pitch=K["tom_mid"], volume=72,
                                  start_tick=t0 + 1920, end_tick=t0 + 1920 + 240))
    phase2.set_unit(5, s, MusicUnit(events=evs))

# --- voice-leading check (rules.voice_leading): bass + lead per bar pair ---
from rules.voice_leading import VoiceLeadingRules  # noqa: E402

vlc = VoiceLeadingRules(style="classical")
vl_flags = []
for bar in range(N_BARS - 1):
    s, b = divmod(bar, BARS_PER)
    root_a, _ = CHORD_DEF[WALK[bar]]
    root_b, _ = CHORD_DEF[WALK[bar + 1]]
    bass_a = nearest_pc_pitch(root_a % 12, 33, 52, anchor=41) or 41
    bass_b = nearest_pc_pitch(root_b % 12, 33, 52, anchor=41) or 41
    u = phase2.matrix.get_unit((0, s))
    evs = [e for e in u.events
           if e.pitch > 0 and b * BAR <= e.start_tick < (b + 1) * BAR]
    evs_next = [e for e in u.events
                if e.pitch > 0 and (b + 1) * BAR <= e.start_tick < (b + 2) * BAR]
    if evs and evs_next:
        lead_a = evs[0].pitch
        lead_b = evs_next[0].pitch
        viol = vlc.check_parallel_motion([bass_a, lead_a], [bass_b, lead_b])
        if viol:
            vl_flags.append((bar, viol))
        hid = vlc.check_hidden_fifths([bass_a, lead_a], [bass_b, lead_b])
        if hid:
            vl_flags.append((bar, hid))
print("VOICE-LEADING flags (bass+lead, classical):", vl_flags[:8], "total",
      len(vl_flags))


def fix_hidden_fifth(phase2, bar):
    """Nudge lead's first note of bar+1 off a hidden 5th/8ve with the bass."""
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
    tones = chord_tones(WALK[bar + 1], lo=60, hi=88)
    bass = nearest_pc_pitch(CHORD_DEF[WALK[bar + 1]][0] % 12, 33, 52,
                            anchor=41) or 41
    cands = [t for t in tones if abs((t - bass) % 12) not in (0, 7)]
    if not cands:
        return False
    target.pitch = min(cands, key=lambda c: (abs(c - target.pitch), c))
    phase2.set_unit(0, s, MusicUnit(events=evs))
    return True


for (bar, _viol) in list(vl_flags):
    if fix_hidden_fifth(phase2, bar):
        print("VL fix applied at bar", bar)

# re-run voice-leading check after corrections
vl_flags2 = []
for bar in range(N_BARS - 1):
    s, b = divmod(bar, BARS_PER)
    root_a, _ = CHORD_DEF[WALK[bar]]
    root_b, _ = CHORD_DEF[WALK[bar + 1]]
    bass_a = nearest_pc_pitch(root_a % 12, 33, 52, anchor=41) or 41
    bass_b = nearest_pc_pitch(root_b % 12, 33, 52, anchor=41) or 41
    u = phase2.matrix.get_unit((0, s))
    evs = [e for e in u.events
           if e.pitch > 0 and b * BAR <= e.start_tick < (b + 1) * BAR]
    evs_next = [e for e in u.events
                if e.pitch > 0 and (b + 1) * BAR <= e.start_tick < (b + 2) * BAR]
    if evs and evs_next:
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
    has_landmark = any(e.pitch == 0 and e.end_tick == total_ticks for e in evs)
    if not has_landmark:
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

P2_MIDI = os.path.join(MIDI_DIR, "090-celtic-subset-walk.mid")
phase2.to_midi(P2_MIDI)
print("phase2 written", P2_MIDI)

# ---------------------------------------------------------------- analysis
from visualization.grid import write_grid_visualization  # noqa: E402

grid_path = os.path.join(ANALYSIS_DIR, "grid_visualization.txt")
write_grid_visualization(phase2.matrix, grid_path, ticks_per_character=120,
                         voice_names=vnames, bpm=BPM,
                         mode="D minor / ABS-002 Subset Walk + Celtic texture")
print("grid written", grid_path)

# provenance
from workflows.provenance import write_provenance, AI_GENERATED  # noqa: E402

for mid, phase, note in (
        (P1_MIDI, "1",
         "raw abstract-layer draft: single bagpipe voice, pitch classes "
         "sampled from the CURRENT WALKED SUBSET pc field (walk directly "
         "audible), 8th-grid rhythm with fractional jitter (off-grid "
         "fingerprint), no harmony/bass/drums"),
        (P2_MIDI, "2",
         "16th-grid locked, D-aeolian scale snap + chord-tone quantize per "
         "global bar (subset walk realization), violin/flute/cello/piano/"
         "double-bass/drums Celtic texture, voice-leading check, full "
         "arrangement")):
    write_provenance(
        mid, AI_GENERATED,
        "ABS-002 Subset Walker + ABS-001 tension-curve steering + "
        "method-006 cadence close (abstract layer)",
        parameters={"bpm": BPM, "key": "D minor (aeolian)",
                    "sections": N_SECTIONS, "bars": N_BARS, "phase": phase,
                    "progression": CHORD_LABELS,
                    "walk": WALK, "seed": SEED,
                    "tension_curve": TENSION_CURVE + [7.0, 2.0],
                    "grid16": GRID16},
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
        "project": "090-celtic-subset-walk",
        "style": "Celtic",
        "method": "ABS-002 Subset Walker + ABS-001 tension-curve steering + "
                  "method-006 cadence close",
        "layer": "abstract (weekly abstract-cadence run)",
        "bpm": BPM, "key": "D minor (aeolian)", "tempo": BPM,
        "bars": N_BARS,
        "sections": {n: BARS_PER for n in NAMES},
        "progression": CHORD_LABELS,
        "walk": WALK,
        "voices": vnames,
        "phase1": os.path.basename(P1_MIDI),
        "phase2": os.path.basename(P2_MIDI),
        "grid": os.path.basename(grid_path),
        "seed": SEED,
    }, f, indent=2)

for p in (P1_MIDI, P2_MIDI, grid_path,
          os.path.join(ANALYSIS_DIR, "summary.json"),
          os.path.join(ANALYSIS_DIR, "vl_audit.json")):
    assert os.path.getsize(p) > 40, "too small: %s" % p
print("ALL SIZE ASSERTS PASSED")
print("PROGRESSION:", CHORD_LABELS)
print("WALK:", WALK)
