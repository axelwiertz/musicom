# -*- coding: utf-8 -*-
"""097-jazz-bebop-changes - Jazz style / ABSTRACT layer:
ABS-002 Subset Walker + ABS-001 tension-curve steering + method-006 cadence
close (ii-V-I into final bar). Bebop head over walked ii-V-I rhythm changes.

KEY DESIGN (089-lesson): anchor pool holds SEVENTH chords (7-note color);
sub-theme triads sampled per section from the anchor's own pc-set.
Harmony universe = tetrad tones + diatonic pass + chromatic approach = all
audited IN-SCALE by construction.

Phase 1: raw generative draft (single trumpet voice). Pitch = sampled from
CURRENT WALKED ANCHOR tetrad pcs (+chromatic approach 30%), placed in trumpet
register via nearest-pc; rhythm = swing-8th grid with FRACTIONAL jitter
(off-grid fingerprint). No harmony/bass/drums.
Phase 2: musicom rules post-process: 16th-grid lock (078 rule) -> subset
realization (tetrad/diatonic/chromatic) -> chord-tone quantize per global
bar -> voice-leading check/correction -> full 6-voice bebop texture
(trumpet lead, trombone counterline, piano comp, upright bass walk, drums).

Engine only: structures + workflows.unitmatrix_composer + rules.voice_leading
+ rules.patterns (abstract layer). mido READ-ONLY in audit.
"""
import os
import sys
import json

import numpy as np

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer
from rules.patterns import standard_patterns
from rules.subset_network import PatternNetwork
 

# instrument registry (source of truth - NOT pip-installed)
INSTR_DIR = "/opt/data/repos/musicom/projects/Instruments"
if INSTR_DIR not in sys.path:
    sys.path.insert(0, INSTR_DIR)
from instrument_registry import (  # noqa: E402
    TRUMPET, TROMBONE, PIANO, DOUBLE_BASS, DRUM_KIT,
)
from Percussion.drum_kit.drum_kit import KIT  # noqa: E402

SEED = 20260917
rng = np.random.default_rng(SEED)

# ---------------------------------------------------------------- project dirs
PROJ = "/opt/data/repos/musicom/projects/Styles/Jazz/097-jazz-bebop-changes"
MIDI_DIR = os.path.join(PROJ, "MIDI")
AUDIO_DIR = os.path.join(PROJ, "Audio")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")
for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
    os.makedirs(d, exist_ok=True)

# ---------------------------------------------------------------- concept
BPM = 132
TPB = 480
BEATS = 4
BAR = TPB * BEATS            # 1920
GRID16 = 120                 # 16th-note grid @ 480 TPB
GRID8 = 240                  # 8th-note grid
SECTION_TICKS = BAR * 4      # 7680 (4 bars per section)

# G ionian (G major) pitch universe: diatonic pitch classes.
G_PCS = {7, 9, 11, 0, 2, 4, 6}          # G A B C D E F#
AUDIT_SCALE_PCS = set(G_PCS)            # strict: lead/trombone/piano all chord-quantized
SCALE_SORTED = sorted(G_PCS)

def snap_diatonic(pitch):
    """Nearest G-major diatonic pitch (octave-aware)."""
    return min(range(pitch - 6, pitch + 7),
               key=lambda c: (0 if c % 12 in G_PCS else 1, abs(c - pitch), c))

# ---------------------------------------------------------------- harmony
# Abstract layer: 12TET subset walk over G-major diatonic seventh anchors.
# ids use CURRENT standard_patterns() naming (maj7 = G triad, min9 = Am ...).
lib = {p.id: p for p in standard_patterns()}
POOL_IDS = [
    "maj7",    # G     I
    "min9",    # Am    ii
    "min11",   # Bm    iii
    "maj0",    # C     IV
    "maj2",    # D     V
    "min4",    # Em    vi
    "min79",   # Am7   ii7
    "min711",  # Bm7   iii7
    "maj70",   # Cmaj7 IV7
    "dom72",   # D7    V7  (T=7.0 tension peak)
    "min74",   # Em7   vi7
    "maj77",   # Gmaj7 I7
]
POOL = [lib[i] for i in POOL_IDS]
NET = PatternNetwork(POOL)
# tension curve across 24 bars: head sway -> solo rise -> bridge lean ->
# shout peak (V7/I7 tetrads) -> head return -> outro tag resolve.
# 22 bars walked + 2 forced cadence bars (method-006).
TENSION_CURVE = [2.0] * 6 + [3.0] * 6 + [5.0] * 6 + [5.5] * 3 + [2.0] * 1
import random as _random
_walk_rng = _random.Random(SEED)
WALK = NET.walk("maj7", 22, rng=_walk_rng, tension_curve=TENSION_CURVE,
                home="maj7") + ["dom72", "maj7"]   # forced V7 -> I cadence
assert len(WALK) == 24, WALK

# pattern id -> bebop functional label (G-major reading)
PAT_LABEL = {
    "maj7": "I", "min9": "ii", "min11": "iii", "maj0": "IV",
    "maj2": "V", "min4": "vi",
    "min79": "ii7", "min711": "iii7", "maj70": "IV7",
    "dom72": "V7", "min74": "vi7", "maj77": "I7",
}
CHORD_LABELS = [PAT_LABEL[pid] for pid in WALK]

# concrete chord realization: root MIDI pitch + quality intervals
# (roots in octave 3; V7 = D7 dominant for the bebop turnaround pull)
CHORD_DEF = {
    "maj7":   (55, "M"),    # G     I
    "min9":   (57, "m"),    # Am    ii
    "min11":  (59, "m"),    # Bm    iii
    "maj0":   (48, "M"),    # C     IV
    "maj2":   (50, "M"),    # D     V
    "min4":   (52, "m"),    # Em    vi
    "min79":  (57, "m7"),   # Am7   ii7
    "min711": (59, "m7"),   # Bm7   iii7
    "maj70":  (48, "M7"),   # Cmaj7 IV7
    "dom72":  (50, "7"),    # D7    V7
    "min74":  (52, "m7"),   # Em7   vi7
    "maj77":  (55, "M7"),   # Gmaj7 I7
}
IV = {"M": (0, 4, 7), "m": (0, 3, 7), "d": (0, 3, 6), "7": (0, 4, 7, 10),
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
    """Nearest pitch in [lo, hi] with pitch class `pc`."""
    cands = [p for p in range(lo, hi + 1) if p % 12 == pc]
    if not cands:
        return None
    if anchor is None:
        return min(cands, key=lambda p: (abs(p - (lo + hi) // 2), p))
    return min(cands, key=lambda p: (abs(p - anchor), p))


# sanity: every anchor pc-set must equal its chord-def pc-set
for pid in POOL_IDS:
    assert set(lib[pid].subset) == chord_pcs_of(pid), (pid, sorted(lib[pid].subset))

NAMES = ["Intro", "Head", "Solo", "Bridge", "Head2", "Outro"]
BARS_PER = 4
N_SECTIONS = len(NAMES)
N_BARS = N_SECTIONS * BARS_PER            # 24

# ---------------------------------------------------------------- TexturePlan
# Bebop behavior deliberately mirrors the 076-reggae-lsystem plan shape
# (sub-theme sampling per section from the 7-pc abstract color => the
# texture voices and the abstract-pool colors LISTEN to each other).
TEXTURE_PLAN = {
    0: dict(sub="triad",  head="half",    snare="brush",  hat=False, lead=0.70),
    1: dict(sub="seventh", head="swing",  snare="back",   hat=True,  lead=0.85),
    2: dict(sub="seventh", head="swing",  snare="back",   hat=True,  lead=0.90),
    3: dict(sub="seventh", head="double", snare="press",  hat=True,  lead=1.00),
    4: dict(sub="triad",  head="swing",  snare="back",    hat=True,  lead=0.90),
    5: dict(sub="triad",  head="half",   snare="brush",   hat=False, lead=0.60),
}
# sub-theme sampling: triad sections reuse the anchor's first 3 pitch
# classes; seventh sections use the full walked tetrad pc-set.
ANCHOR_SUB = {}
for pid in POOL_IDS:
    pcs = sorted(lib[pid].subset)
    ANCHOR_SUB[(pid, "triad")] = pcs[:3]
    ANCHOR_SUB[(pid, "seventh")] = pcs

# ---------------------------------------------------------------- phase 1
# Raw abstract-layer draft: single trumpet voice. For each swing-8th slot
# (on-grid 240 + fractional jitter -40..+40 = off-grid fingerprint), with
# probability = section lead density, emit a note whose pitch class is
# sampled from the CURRENT WALKED ANCHOR tetrad pcs (+30% chromatic approach
# neighbor of a chord tone: bebop enclosure color, still in-scale audit).
P_ONSET = {s: TEXTURE_PLAN[s]["lead"] for s in range(N_SECTIONS)}
CENTERS = {0: 67.0, 1: 71.0, 2: 72.0, 3: 74.0, 4: 71.0, 5: 67.0}
rng1 = np.random.default_rng(SEED + 1)

phase1 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
phase1.create_matrix(num_voices=1, num_sections=N_SECTIONS)
phase1.add_voice("LeadRaw", program=TRUMPET.midi_program, channel=0)

SWING = {0: 0, 1: 28}   # long-short swing pair offsets inside each quarter

for s, name in enumerate(NAMES):
    evs = []
    prev_end = 0.0
    bar_offset = s * BARS_PER
    n_slots = SECTION_TICKS // GRID8
    for slot in range(n_slots):
        bar = bar_offset + (slot * GRID8) // BAR
        pid = WALK[bar]
        pcs = sorted(lib[pid].subset)
        if rng1.random() < P_ONSET[s]:
            # 70% anchor tetrad tone / 30% chromatic approach (bebop color)
            if rng1.random() < 0.30:
                anchor_pc = int(rng1.choice(pcs))
                pc = (anchor_pc + int(rng1.choice([-1, 1]))) % 12
            else:
                pc = int(rng1.choice(pcs))
            # swing-8th slot base + fractional jitter (off-grid fingerprint)
            base = slot * GRID8 + SWING[slot % 2]
            st = base + int(rng1.integers(-40, 41))
            st = max(0, min(st, SECTION_TICKS - 1))
            anchor = CENTERS[s] + rng1.normal(0, 4)
            p = nearest_pc_pitch(pc, 58, 82, anchor=int(anchor))
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
P1_MIDI = os.path.join(MIDI_DIR, "097-jazz-bebop-changes-phase1.mid")
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
    ("Lead",     TRUMPET.midi_program, 0),      # Trumpet (bebop head)
    ("Trombone", TROMBONE.midi_program, 1),     # Trombone (counterline)
    ("Piano",    PIANO.midi_program, 2),        # Piano (comping)
    ("Bass",     DOUBLE_BASS.midi_program, 3),  # Double Bass (walking)
    ("Drums",    DRUM_KIT.midi_program, 9),     # percussion channel
]
N_V = len(VOICES)
phase2.create_matrix(num_voices=N_V, num_sections=N_SECTIONS)
vnames = [v[0] for v in VOICES]
for name, prog, ch in VOICES:
    phase2.add_voice(name, program=prog, channel=ch)
for n in NAMES:
    phase2.add_section(n, bars=BARS_PER)

# --- lead: GRID LOCK FIRST, then subset realization (tetrad/diatonic/
#     chromatic-approach) + chord-tone quantize per global bar (078 rule)
for s, name in enumerate(NAMES):
    raw_unit = phase1.matrix.get_unit((0, s))
    raw_events = quantize_to_grid(list(raw_unit.events), grid=GRID16)
    q_events = []
    for e in raw_events:
        if e.pitch == 0:
            q_events.append(e)
            continue
        local_bar = e.start_tick // BAR
        bar = s * BARS_PER + local_bar
        if bar >= N_BARS:
            bar = N_BARS - 1
        pid = WALK[bar]
        tones = chord_tones(pid, lo=58, hi=82)   # trumpet lead register
        pc = e.pitch % 12
        if pc in chord_pcs_of(pid):
            qp = quantize_to_chord(e.pitch, tones)          # tetrad tone
        elif pc in G_PCS:
            qp = quantize_to_chord(snap_diatonic(e.pitch), tones)  # diatonic pass
        else:
            # chromatic approach (phase-1 bebop color) resolves to nearest
            # chord tone in phase 2 per two-phase rules (078 lock)
            qp = quantize_to_chord(e.pitch, tones)
        q_events.append(MusicEvent(pitch=qp, volume=e.volume,
                                   start_tick=e.start_tick,
                                   end_tick=e.end_tick))
    # voice-leading: cap leaps <= 10 toward nearest chord tone of next event
    for i in range(1, len(q_events)):
        e = q_events[i]
        if e.pitch == 0:
            continue
        p_prev = q_events[i - 1].pitch if q_events[i - 1].pitch else 71
        if abs(e.pitch - p_prev) > 10:
            local_bar = e.start_tick // BAR
            bar = s * BARS_PER + local_bar
            if bar >= N_BARS:
                bar = N_BARS - 1
            tones = chord_tones(WALK[bar], lo=58, hi=82)
            e.pitch = min(tones, key=lambda c: (abs(c - p_prev), c))
    phase2.set_unit(0, s, MusicUnit(events=q_events))

# --- trombone: counterline. Chord tones sampled from the section sub-theme
#     (triad/seventh per TEXTURE_PLAN) +12-style window; answers on beats
#     2 & 4 with 8th pickups. All on-grid.
for s in range(N_SECTIONS):
    r = np.random.default_rng(SEED + 300 + s)
    sub = TEXTURE_PLAN[s]["sub"]
    evs = []
    for bar in range(BARS_PER):
        t0 = bar * BAR
        pid = WALK[s * BARS_PER + bar]
        sub_pcs = set(ANCHOR_SUB[(pid, sub)])
        tones = sorted(p for p in chord_tones(pid, lo=52, hi=72)
                       if p % 12 in sub_pcs)
        if not tones:
            tones = chord_tones(pid, lo=52, hi=72)
        for beat in (1, 3):
            st = t0 + beat * 480
            pitch = int(r.choice(tones))
            evs.append(MusicEvent(pitch=pitch, volume=64,
                                  start_tick=st, end_tick=st + 240))
            st2 = st + 240
            if st2 < t0 + BAR:
                pitch2 = int(r.choice(tones))
                evs.append(MusicEvent(pitch=pitch2, volume=58,
                                      start_tick=st2, end_tick=st2 + 240))
    phase2.set_unit(1, s, MusicUnit(events=evs))

# --- piano: bebop comping. Charleston + red-garland block hits from the
#     section sub-theme window; all on-grid, staccato stabs.
for bar in range(N_BARS):
    s, b = divmod(bar, BARS_PER)
    sub = TEXTURE_PLAN[s]["sub"]
    pid = WALK[bar]
    sub_pcs = set(ANCHOR_SUB[(pid, sub)])
    tones = sorted(p for p in chord_tones(pid, lo=60, hi=79)
                   if p % 12 in sub_pcs)
    if len(tones) < 2:
        tones = chord_tones(pid, lo=60, hi=79)
    t0 = b * BAR
    gg = np.random.default_rng(SEED + 500 + bar)
    # charleston core: beat 1 + offbeat-and-of-2; bridge adds beat-4 stab
    hits = [0, 720]
    if TEXTURE_PLAN[s]["head"] == "double":
        hits.append(1440)
    if s in (1, 2) and gg.random() < 0.5:
        hits.append(1680)   # and-of-4 pickup (must stay < BAR=1920)
    e = []
    for h in hits:
        root, _kind = CHORD_DEF[pid]
        shell = [t for t in tones if t % 12 in (root % 12, (root + 7) % 12)]
        pick = shell if shell and gg.random() < 0.6 else tones
        k = min(3, len(pick))
        chord = sorted(gg.choice(pick, size=k, replace=False).tolist())
        for p in chord:
            e.append(MusicEvent(pitch=int(p), volume=56,
                                start_tick=t0 + h, end_tick=t0 + h + 160))
    unit = phase2.matrix.get_unit((2, s))
    events = list(unit.events) if unit is not None else []
    events.extend(e)
    phase2.set_unit(2, s, MusicUnit(events=events))

# --- bass: walking quarters, scalar approach on beat 4 (diatonic lane).
#     Roots voice-led (nearest octave), beat-4 = diatonic step toward next
#     root. All on-grid.
for bar in range(N_BARS):
    s, b = divmod(bar, BARS_PER)
    root, _kind = CHORD_DEF[WALK[bar]]
    nxt_root, _ = CHORD_DEF[WALK[bar + 1]] if bar + 1 < N_BARS else CHORD_DEF[WALK[bar]]
    bass = nearest_pc_pitch(root % 12, 33, 52, anchor=41)
    if bass is None:
        bass = 41
    nxt = nearest_pc_pitch(nxt_root % 12, 33, 52, anchor=bass)
    if nxt is None:
        nxt = bass
    t0 = b * BAR
    e = []
    # beats 1-3: root, fifth-or-third, fifth-or-third (chord tones)
    thirds = [bass + 3 if CHORD_DEF[WALK[bar]][1] in ("m", "m7") else bass + 4]
    fifth = bass + 7
    line = [bass, fifth if (bar % 2 == 0) else thirds[0], fifth]
    for k, p in enumerate(line):
        p = max(28, min(58, p))
        e.append(MusicEvent(pitch=p, volume=80 if k == 0 else 68,
                            start_tick=t0 + k * 480,
                            end_tick=t0 + k * 480 + 440))
    # beat 4: diatonic scalar approach toward next root. Candidate steps
    # from the CURRENT bass note toward next root, snapped diatonic; if the
    # snap lands off the destination chord, fall back to chord tone nearest
    # next root (keeps 0 out-of-chord by construction).
    step_dir = 1 if nxt >= bass else -1
    cand = snap_diatonic(bass + step_dir * 2)
    cand = max(28, min(58, cand))
    dest_tones = chord_tones(WALK[bar], lo=28, hi=58)
    if cand % 12 not in chord_pcs_of(WALK[bar]):
        cand = min(dest_tones, key=lambda c: (abs(c - nxt), abs(c - cand)))
    e.append(MusicEvent(pitch=cand, volume=70,
                        start_tick=t0 + 1440, end_tick=t0 + 1440 + 440))
    unit = phase2.matrix.get_unit((3, s))
    events = list(unit.events) if unit is not None else []
    events.extend(e)
    phase2.set_unit(3, s, MusicUnit(events=events))

# --- drums: bebop ride-driven kit. Intro brushes, Head/Solo backbeat ride,
#     Bridge press-roll + crash, Outro brushes. All on-grid (multiples of 120).
K = KIT
DRUM_PLAN = {
    0: dict(ride=52, kick=60, snare=58, hat=None, crash=False, ride_pat="swung"),
    1: dict(ride=66, kick=78, snare=72, hat=56,  crash=False, ride_pat="spang"),
    2: dict(ride=66, kick=82, snare=76, hat=56,  crash=False, ride_pat="spang"),
    3: dict(ride=74, kick=90, snare=86, hat=62,  crash=True,  ride_pat="spang"),
    4: dict(ride=66, kick=82, snare=76, hat=56,  crash=False, ride_pat="spang"),
    5: dict(ride=52, kick=60, snare=58, hat=None, crash=False, ride_pat="swung"),
}
SPANG = [0, 720, 960, 1680]   # spang-a-lang skeleton per bar (all %120==0)
SWUNG = [0, 720, 1440]
for s in range(N_SECTIONS):
    plan = DRUM_PLAN[s]
    evs = []
    for bar in range(BARS_PER):
        t0 = bar * BAR
        ride_hits = SPANG if plan["ride_pat"] == "spang" else SWUNG
        for h in ride_hits:
            evs.append(MusicEvent(pitch=K["ride"], volume=plan["ride"],
                                  start_tick=t0 + h, end_tick=t0 + h + 60))
        if plan["hat"] is not None:
            for h in (480, 1440):
                evs.append(MusicEvent(pitch=K["hat_closed"], volume=plan["hat"],
                                      start_tick=t0 + h, end_tick=t0 + h + 60))
        # kick: feathered 1 & 3 (+ bridge "&" ghosts)
        kick_beats = [0, 960]
        if s == 3:
            kick_beats += [240, 1440]
        for kb in kick_beats:
            evs.append(MusicEvent(pitch=K["kick"], volume=plan["kick"],
                                  start_tick=t0 + kb, end_tick=t0 + kb + 120))
        # snare: backbeat 2 & 4 (brushes = lighter, on 2 & 4 too)
        for sb in (480, 1440):
            evs.append(MusicEvent(pitch=K["snare"], volume=plan["snare"],
                                  start_tick=t0 + sb, end_tick=t0 + sb + 120))
        if plan["crash"]:
            evs.append(MusicEvent(pitch=K["crash"], volume=70,
                                  start_tick=t0, end_tick=t0 + 500))
    phase2.set_unit(4, s, MusicUnit(events=evs))

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


def fix_hidden_fifth(phase2c, bar):
    """Nudge lead's first note of bar+1 off a hidden 5th/8ve with the bass."""
    s, b = divmod(bar + 1, BARS_PER)
    if b >= BARS_PER:
        return False
    u = phase2c.matrix.get_unit((0, s))
    evs = list(u.events)
    target = None
    for e in evs:
        if e.pitch > 0 and b * BAR <= e.start_tick < (b + 1) * BAR:
            target = e
            break
    if target is None:
        return False
    tones = chord_tones(WALK[bar + 1], lo=58, hi=82)
    bass = nearest_pc_pitch(CHORD_DEF[WALK[bar + 1]][0] % 12, 33, 52,
                            anchor=41) or 41
    cands = [t for t in tones if abs((t - bass) % 12) not in (0, 7)]
    if not cands:
        return False
    target.pitch = min(cands, key=lambda c: (abs(c - target.pitch), c))
    phase2c.set_unit(0, s, MusicUnit(events=evs))
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
            from workflows.unitmatrix_composer import create_empty_unit
            phase2.set_unit(v, s, create_empty_unit(SECTION_TICKS))
        else:
            phase2.set_unit(v, s, normalize_cell(u, SECTION_TICKS))

ok2, msg2 = phase2.validate()
print("PHASE2 validate:", msg2)
assert ok1 and ok2, (msg1, msg2)

P2_MIDI = os.path.join(MIDI_DIR, "097-jazz-bebop-changes.mid")
phase2.to_midi(P2_MIDI)
print("phase2 written", P2_MIDI)

# ---------------------------------------------------------------- analysis
from visualization.grid import write_grid_visualization  # noqa: E402

grid_path = os.path.join(ANALYSIS_DIR, "grid_visualization.txt")
write_grid_visualization(phase2.matrix, grid_path, ticks_per_character=120,
                         voice_names=vnames, bpm=BPM,
                         mode="G major / ABS-002 Subset Walk + bebop texture")
print("grid written", grid_path)

# provenance
from workflows.provenance import write_provenance, AI_GENERATED  # noqa: E402

for mid, phase, note in (
        (P1_MIDI, "1",
         "raw abstract-layer draft: single trumpet voice, pitch classes "
         "sampled from the CURRENT WALKED ANCHOR tetrad pcs (+30% chromatic "
         "approach color), swing-8th rhythm with fractional jitter (off-grid "
         "fingerprint), no harmony/bass/drums"),
        (P2_MIDI, "2",
         "16th-grid locked, subset realization (tetrad/diatonic/chromatic) + "
         "chord-tone quantize per global bar (walked-anchor realization), "
         "trumpet/trombone/piano/bass/drums bebop texture, voice-leading "
         "check, full arrangement")):
    write_provenance(
        mid, AI_GENERATED,
        "ABS-002 Subset Walker + ABS-001 tension-curve steering + "
        "method-006 cadence close (abstract layer)",
        parameters={"bpm": BPM, "key": "G major (ionian)",
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
        "project": "097-jazz-bebop-changes",
        "style": "Jazz",
        "method": "ABS-002 Subset Walker + ABS-001 tension-curve steering + "
                  "method-006 cadence close",
        "layer": "abstract (weekly abstract-cadence run)",
        "bpm": BPM, "key": "G major (ionian)", "tempo": BPM,
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
