# -*- coding: utf-8 -*-
"""290-funk-hawkes-suite — Funk / Method 045 Hawkes Process Self-Exciting
Composition (HPSEC). LAYER: concrete.

Rework of 088-funk-hawkes (audit FAIL: index.html + top-level provenance.json
missing). Rebuilt through the canonical two-phase engine pipeline, extended to
8 sections / 32 bars, with 5+ explicit variation techniques.

Two-phase architecture:
  Phase 1: raw generative draft — single-voice Hawkes self-exciting point
           process (fractional OFF-GRID sojourn times, unquantized pitch drift
           around section centers). No harmony/bass/drums.
  Phase 2: musicom rules post-process:
           1. GRID LOCK to 16th grid (120 ticks) + dedup (078 rule).
           2. F-minor pentatonic snap (blues colour) THEN chord-tone quantize
              per bar (floor t//BAR global lookup — 079 fix).
           3. Register/range enforcement per instrument.
           4. Voice-leading leap cap <= 9.
           5. Per-section harmonic regions (8 distinct 4-bar progressions);
              section root = MIDPOINT bar chord (not bar 0).
           6. Zero-drift landmark + validate() on BOTH phases.
           7. export_dual -> -perfect.mid + -humanized.mid.

Engine only. mido is used READ-ONLY in the audit (separate step).
"""
import os
import json
import sys

import numpy as np

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import (
    UnitMatrixComposer, create_note_unit, create_chord_unit, create_empty_unit,
)
from visualization.grid import write_grid_visualization
from workflows.provenance import write_provenance, AI_ASSISTED
from workflows.humanize import export_dual

# instrument registry (source of truth - NOT pip-installed)
INSTR_DIR = "/opt/data/repos/musicom/projects/Instruments"
if INSTR_DIR not in sys.path:
    sys.path.insert(0, INSTR_DIR)
from instrument_registry import (  # noqa: E402
    TRUMPET, SAXOPHONE, CELLO, PIANO, DOUBLE_BASS, DRUM_KIT,
)
from Percussion.drum_kit.drum_kit import KIT  # noqa: E402

SEED = 20261107
HZ_SEED = SEED * 7 + 1
rng = np.random.default_rng(SEED)

# ------------------------------------------------------------------ project
PROJ = "/opt/data/projects/Styles/Funk/290-funk-hawkes-suite"
MIDI_DIR = os.path.join(PROJ, "MIDI")
AUDIO_DIR = os.path.join(PROJ, "Audio")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")
for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
    os.makedirs(d, exist_ok=True)

# ------------------------------------------------------------------- concept
BPM = 100
TPB = 480
BEATS = 4
BAR = TPB * BEATS                # 1920
GRID16 = 120                     # 16th-note grid
GRID8 = 240                      # 8th-note grid
NAMES = ["Intro", "Verse", "Chorus", "Break", "Verse2", "Chorus2",
         "Bridge", "Outro"]
BARS_PER = 4
N_SECTIONS = len(NAMES)          # 8
N_BARS = N_SECTIONS * BARS_PER   # 32 bars
SECTION_TICKS = BAR * BARS_PER   # 7680
TOTAL_TICKS = N_SECTIONS * SECTION_TICKS

# F natural minor key pitch classes: F G Ab Bb C Db Eb
KEY = "F minor"
KEY_PCS = {0, 1, 3, 5, 7, 8, 10}
# F minor pentatonic (blues colour) notes in lead register 54..86
PENTA = [56, 58, 60, 63, 65, 68, 70, 72, 75, 77, 80, 82, 84]

LEAD_LO, LEAD_HI = 54, 86       # trumpet range
SAX_LO, SAX_HI = 49, 88         # alto sax range
CELLO_LO, CELLO_HI = 36, 84     # cello range
BASS_LO, BASS_HI = 28, 74       # double bass range

# ------------------------------------------------------------------- harmony
# F minor diatonic triads. DEGREES[name] = (quality, root_midi).
#   m = (0,3,7), M = (0,4,7)
DEGREES = {
    "i":   ("m", 53),   # Fm
    "III": ("M", 56),   # Ab
    "iv":  ("m", 58),   # Bbm
    "v":   ("m", 60),   # Cm
    "VI":  ("M", 49),   # Db
    "VII": ("M", 51),   # Eb
}
INTERVALS = {"m": (0, 3, 7), "M": (0, 4, 7)}

# Per-section harmonic regions: each section has its OWN 4-bar progression.
# Section root = the MIDPOINT bar (index 1) chord — NOT bar 0 (079 bug).
SECTION_PROG = [
    ["i", "VI", "III", "VII"],   # 0 Intro
    ["i", "iv", "VI", "v"],      # 1 Verse
    ["i", "VI", "III", "VII"],   # 2 Chorus
    ["iv", "v", "i", "VI"],      # 3 Break
    ["i", "III", "iv", "VII"],   # 4 Verse2
    ["i", "VI", "III", "VII"],   # 5 Chorus2
    ["VI", "III", "iv", "v"],    # 6 Bridge
    ["i", "iv", "VI", "i"],      # 7 Outro
]
PROG = [deg for sec in SECTION_PROG for deg in sec]
assert len(PROG) == N_BARS, (len(PROG), N_BARS)

MID_IDX = 1
SECTION_ROOT = [DEGREES[sec[MID_IDX]] for sec in SECTION_PROG]  # (qual, root)
SECTION_ROOT_NAMES = [sec[MID_IDX] for sec in SECTION_PROG]


def chord_tones(root, lo=36, hi=88):
    tones = set()
    for oct_shift in (-12, 0, 12, 24):
        for i in INTERVALS[chord_qual(root)]:
            p = root + i + oct_shift
            if lo <= p <= hi:
                tones.add(p)
    return sorted(tones)


def chord_qual(root):
    for _name, (q, r) in DEGREES.items():
        if r == root:
            return q
    raise KeyError(root)


def chord_pcs(root):
    return set((root + i) % 12 for i in INTERVALS[chord_qual(root)])


def quantize_to_chord(pitch, tones):
    return min(tones, key=lambda c: (abs(c - pitch), c))


def snap_pentatonic(p):
    return min(PENTA, key=lambda c: (abs(c - p), c))


def root_to_lead_center(root_midi):
    c = root_midi
    while c < 56:
        c += 12
    while c > 74:
        c -= 12
    return c


def PROG_ROOT(bar):
    return DEGREES[PROG[bar]][1]


# ------------------------------------------------------------------- phase 1
# Raw Hawkes self-exciting point process (single voice, OFF-GRID + unquantized).
def raw_hawkes_melody(seed, duration_ticks, n_events, center, mu=0.12,
                      alpha=0.55, beta=0.006):
    r = np.random.default_rng(seed)
    events = []
    tick = 0.0
    x = float(center)
    excite = 0.0
    for _ in range(n_events):
        lam = mu + excite * alpha
        lam = max(lam, 1e-3)
        tau = r.exponential(1.0 / lam)
        tau *= (duration_ticks / float(n_events)) / (1.0 / lam)
        x += (excite * 2.2 - 0.35) * r.normal(0.0, 1.0) + 0.4 * r.normal(0.0, 1.0)
        if excite > 0:
            x += 0.8 * r.normal(0.4, 0.6)
        if x < LEAD_LO:
            x = 2 * LEAD_LO - x
        if x > LEAD_HI:
            x = 2 * LEAD_HI - x
        x = 0.92 * x + 0.08 * center
        midi = int(round(x))
        st = int(round(tick))
        dur = tau * (0.45 + 0.55 * r.random())
        en = int(round(tick + dur))
        if en > duration_ticks:
            en = duration_ticks
        if en > st:
            vel = int(np.clip(60 + 34 * r.random(), 50, 104))
            events.append(MusicEvent(pitch=midi, volume=vel,
                                     start_tick=st, end_tick=en))
        tick += tau
        excite = excite * np.exp(-beta * tau) + (1.0 if r.random() < 0.28 else 0.0)
        if excite > 3.0:
            excite = 3.0
    return events


# Per-section lead centers (section midpoint root mapped into trumpet register,
# plus per-section register variation for the transposition technique).
REG_OFFSET = {0: 0, 1: 0, 2: 8, 3: -4, 4: 12, 5: 8, 6: 0, 7: -6}
DENSITY = {0: 22, 1: 32, 2: 42, 3: 24, 4: 32, 5: 48, 6: 28, 7: 16}
LEAD_CENTER = {}
for s in range(N_SECTIONS):
    base = root_to_lead_center(SECTION_ROOT[s][1])
    LEAD_CENTER[s] = base + REG_OFFSET[s]

phase1 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
phase1.create_matrix(num_voices=1, num_sections=N_SECTIONS)
phase1.add_voice("LeadRaw", program=TRUMPET.midi_program, channel=0)

P1_RAW = {}   # keep raw events per section for phase-2 lead
for s, name in enumerate(NAMES):
    phase1.add_section(name, bars=BARS_PER)
    evs = raw_hawkes_melody(SEED + s, SECTION_TICKS, DENSITY[s], LEAD_CENTER[s])
    P1_RAW[s] = list(evs)
    # zero-drift landmark padding (exact section boundary)
    if not any(e.pitch == 0 and e.end_tick == SECTION_TICKS for e in evs):
        evs.append(MusicEvent(pitch=0, volume=0, start_tick=SECTION_TICKS - 1,
                              end_tick=SECTION_TICKS))
    phase1.set_unit(0, s, MusicUnit(events=evs))

ok1, msg1 = phase1.validate()
if not ok1:
    raise RuntimeError("phase1 validate FAIL: " + msg1)
P1_MIDI = os.path.join(MIDI_DIR, "290-funk-hawkes-suite-phase1.mid")
phase1.to_midi(P1_MIDI)
print("PHASE1 validate:", msg1)
print("phase1 written", P1_MIDI)

# ------------------------------------------------------------------- phase 2
phase2 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
VOICES = [
    ("Lead",  TRUMPET.midi_program, 0),      # Trumpet (Hawkes lead)
    ("Sax",   SAXOPHONE.midi_program, 1),    # Alto Sax (counterline)
    ("Cello", CELLO.midi_program, 2),        # Cello (sustained pad)
    ("Piano", PIANO.midi_program, 3),        # Piano (offbeat stabs)
    ("Bass",  DOUBLE_BASS.midi_program, 4),  # Double Bass (octave pulse)
    ("Drums", 0, 9),                         # percussion channel
]
N_V = len(VOICES)
phase2.create_matrix(num_voices=N_V, num_sections=N_SECTIONS)
for name, prog, ch in VOICES:
    phase2.add_voice(name, program=prog, channel=ch)
for n in NAMES:
    phase2.add_section(n, bars=BARS_PER)


def grid_lock_dedup(events, grid=GRID16):
    """Snap onsets to grid, dedup (start_tick,pitch) keeping longest duration."""
    by_key = {}
    out = []
    for e in events:
        if e.pitch == 0:
            out.append(e)
            continue
        st = int(round(e.start_tick / grid) * grid)
        if st < 0:
            st = 0
        en = max(st + 1, int(e.end_tick))
        if en > SECTION_TICKS:
            en = SECTION_TICKS
        key = (st, e.pitch)
        if key in by_key:
            if en > by_key[key].end_tick:
                by_key[key] = MusicEvent(pitch=e.pitch, volume=max(e.volume, by_key[key].volume),
                                         start_tick=st, end_tick=en)
        else:
            by_key[key] = MusicEvent(pitch=e.pitch, volume=e.volume,
                                     start_tick=st, end_tick=en)
    for key in sorted(by_key):
        out.append(by_key[key])
    return out


def global_bar(sec, local_tick):
    return sec * BARS_PER + (local_tick // BAR)


def landmark(events):
    """Clamp every event to the section boundary, SORT by start_tick (the
    humanizer forward-clamp is order-sensitive), and guarantee
    len_ticks == SECTION_TICKS via a silent terminal landmark (zero-drift)."""
    out = []
    for e in events:
        if e.start_tick >= SECTION_TICKS:
            continue
        st = min(int(e.start_tick), SECTION_TICKS - 1)
        en = min(int(e.end_tick), SECTION_TICKS)
        if en <= st:
            en = st + 1
        out.append(MusicEvent(pitch=e.pitch, volume=e.volume,
                              start_tick=st, end_tick=en))
    out.sort(key=lambda e: (e.start_tick, 0 if e.pitch == 0 else 1))
    if not any(e.pitch == 0 and e.end_tick == SECTION_TICKS for e in out):
        out.append(MusicEvent(pitch=0, volume=0, start_tick=SECTION_TICKS - 1,
                              end_tick=SECTION_TICKS))
    return out


# ---- lead: grid-lock -> pentatonic snap -> chord-tone quantize (per bar) ----
LEAD_PITCHES = {}     # quantized pitch sequence per section (for retrograde)
LEAD_UNITS = {}
for s, name in enumerate(NAMES):
    raw_events = P1_RAW[s]
    q = grid_lock_dedup(raw_events, grid=GRID16)
    q_events = []
    for e in q:
        if e.pitch == 0:
            q_events.append(e)
            continue
        bar = global_bar(s, e.start_tick)
        if bar >= N_BARS:
            bar = N_BARS - 1
        sc = snap_pentatonic(e.pitch)
        tones = chord_tones(PROG_ROOT(bar), lo=LEAD_LO, hi=LEAD_HI)
        qp = quantize_to_chord(sc, tones)
        q_events.append(MusicEvent(pitch=qp, volume=e.volume,
                                   start_tick=e.start_tick, end_tick=e.end_tick))
    # voice-leading leap cap <= 9
    for i in range(1, len(q_events)):
        e = q_events[i]
        if e.pitch == 0:
            continue
        prev = q_events[i - 1].pitch if q_events[i - 1].pitch else LEAD_HI
        if abs(e.pitch - prev) > 9:
            bar = global_bar(s, e.start_tick)
            if bar >= N_BARS:
                bar = N_BARS - 1
            tones = chord_tones(PROG_ROOT(bar), lo=LEAD_LO, hi=LEAD_HI)
            e.pitch = min(tones, key=lambda c: (abs(c - prev), c))
    LEAD_PITCHES[s] = [e.pitch for e in q_events if e.pitch != 0]
    LEAD_UNITS[s] = MusicUnit(events=landmark(q_events))
    phase2.set_unit(0, s, LEAD_UNITS[s])


# ---- cello: sustained whole-bar triad pad (per-bar chord) -----------------
for bar in range(N_BARS):
    s, b = divmod(bar, BARS_PER)
    root = PROG_ROOT(bar)
    tones = chord_tones(root, lo=CELLO_LO, hi=67)
    # keep the close triad (root, third, fifth) in octave 3/4
    tones = [t for t in tones if root - 12 <= t <= root + 12]
    if not tones:
        tones = chord_tones(root, lo=CELLO_LO, hi=CELLO_HI)
    t0 = b * BAR
    e = []
    for k, p in enumerate(tones[:3]):
        e.append(MusicEvent(pitch=p, volume=48 + 4 * k,
                            start_tick=t0, end_tick=t0 + BAR - 90))
    unit = phase2.matrix.get_unit((2, s))
    events = list(unit.events) if unit is not None else []
    events.extend(e)
    phase2.set_unit(2, s, MusicUnit(events=events))

# ---- sax: answering 8th-note counterline (chord tones +12) ----------------
SAX_PITCHES = {}
for s in range(N_SECTIONS):
    rr = np.random.default_rng(SEED + 300 + s)
    evs = []
    for bar in range(BARS_PER):
        t0 = bar * BAR
        root = PROG_ROOT(s * BARS_PER + bar)
        tones = [t + 12 for t in chord_tones(root, lo=48, hi=76) if t + 12 <= SAX_HI]
        if not tones:
            tones = chord_tones(root, lo=60, hi=76)
        for beat in (1, 3):
            st = t0 + beat * 480
            pitch = int(rr.choice(tones))
            evs.append(MusicEvent(pitch=pitch, volume=64,
                                  start_tick=st, end_tick=st + 240))
            st2 = st + 240
            if st2 < t0 + BAR:
                pitch2 = int(rr.choice(tones))
                evs.append(MusicEvent(pitch=pitch2, volume=58,
                                      start_tick=st2, end_tick=st2 + 240))
    SAX_PITCHES[s] = [e.pitch for e in evs if e.pitch != 0]
    phase2.set_unit(1, s, MusicUnit(events=landmark(evs)))

# ---- piano: offbeat 16th stabs (chord tones +12), funk staccato -----------
for bar in range(N_BARS):
    s, b = divmod(bar, BARS_PER)
    root = PROG_ROOT(bar)
    tones = [t + 12 for t in chord_tones(root, lo=48, hi=76)]
    t0 = b * BAR
    e = []
    for k in range(0, BAR, GRID8):
        off = t0 + k + GRID16
        p = tones[(off // GRID16) % len(tones)]
        e.append(MusicEvent(pitch=p, volume=56,
                            start_tick=off, end_tick=off + 90))
    unit = phase2.matrix.get_unit((3, s))
    events = list(unit.events) if unit is not None else []
    events.extend(e)
    phase2.set_unit(3, s, MusicUnit(events=events))

# ---- bass: funk octave pulse (root/fifth/octave) --------------------------
BASS_ROOT = {}
for _name, (_q, r) in DEGREES.items():
    br = r - 12
    while br < BASS_LO:
        br += 12
    BASS_ROOT[r] = br
BASS_8TH = {2, 4, 5}        # 8th-note pulse sections
BASS_PUSH = {2, 3, 4, 5}    # 16th end-push sections
BASS_OCT = {2, 4, 5}        # octave pops
for bar in range(N_BARS):
    s, b = divmod(bar, BARS_PER)
    root = BASS_ROOT[PROG_ROOT(bar)]
    fifth = root + 7 if root + 7 <= BASS_HI else root - 5
    octv = root + 12 if root + 12 <= BASS_HI else root
    t0 = b * BAR
    e = []
    step = GRID8 if s in BASS_8TH else 480
    for k in range(0, BAR, step):
        on_beat = (k // step) % 2 == 0
        pitch = root if on_beat else (octv if s in BASS_OCT else root)
        e.append(MusicEvent(pitch=pitch, volume=82 if on_beat else 66,
                            start_tick=t0 + k, end_tick=t0 + k + step - 40))
    if s in BASS_PUSH and b != BARS_PER - 1:
        e.append(MusicEvent(pitch=root, volume=72,
                            start_tick=t0 + BAR - GRID16, end_tick=t0 + BAR - 20))
    unit = phase2.matrix.get_unit((4, s))
    events = list(unit.events) if unit is not None else []
    events.extend(e)
    phase2.set_unit(4, s, MusicUnit(events=events))

# ---- drums: funk kit ------------------------------------------------------
DRUM_PLAN = {
    0: dict(hat=40, kick=60, snare=None, clap=None, crash=False, hat16=False),
    1: dict(hat=52, kick=80, snare=70, clap=None, crash=False, hat16=False),
    2: dict(hat=58, kick=94, snare=90, clap=84, crash=True, hat16=True),
    3: dict(hat=42, kick=70, snare=64, clap=None, crash=False, hat16=False),
    4: dict(hat=52, kick=80, snare=70, clap=None, crash=False, hat16=False),
    5: dict(hat=60, kick=98, snare=94, clap=88, crash=True, hat16=True),
    6: dict(hat=48, kick=76, snare=70, clap=None, crash=False, hat16=False),
    7: dict(hat=36, kick=64, snare=None, clap=None, crash=False, hat16=False),
}
for s in range(N_SECTIONS):
    plan = DRUM_PLAN[s]
    evs = []
    for bar in range(BARS_PER):
        t0 = bar * BAR
        hat_step = GRID16 if plan["hat16"] else GRID8
        for k in range(0, BAR, hat_step):
            evs.append(MusicEvent(pitch=KIT["hat_closed"], volume=plan["hat"],
                                  start_tick=t0 + k, end_tick=t0 + k + 60))
        kick_beats = [0, 960]
        if s in (2, 5):
            kick_beats += [240, 1200]     # 1& 3& drive
        for kb in kick_beats:
            evs.append(MusicEvent(pitch=KIT["kick"], volume=plan["kick"],
                                  start_tick=t0 + kb, end_tick=t0 + kb + 120))
        if plan["snare"] is not None:
            for sb in (480, 1440):        # backbeat beats 2 & 4
                evs.append(MusicEvent(pitch=KIT["snare"], volume=plan["snare"],
                                      start_tick=t0 + sb, end_tick=t0 + sb + 120))
        if plan["clap"] is not None:
            for sb in (480, 1440):        # clap doubles the backbeat
                evs.append(MusicEvent(pitch=KIT["clap"], volume=plan["clap"],
                                      start_tick=t0 + sb, end_tick=t0 + sb + 120))
        if plan["crash"]:
            evs.append(MusicEvent(pitch=KIT["crash"], volume=70,
                                  start_tick=t0, end_tick=t0 + 500))
    phase2.set_unit(5, s, MusicUnit(events=landmark(evs)))

# ---- VARIATION TECHNIQUES (applied in place) ------------------------------
# (1) TRANSPOSITION / REGISTER SHIFT: Verse2 (s=4) lead center already +12.
# (2) DIMINUTION: Chorus2 (s=5) lead density 48 (16th-note denser than Chorus).
# (3) RETROGRADE: Bridge (s=6) lead = reversed Chorus2 pitch sequence.
# (4) INVERSION: Bridge (s=6) sax = Verse sax inverted around axis 70.
# (5) AUGMENTATION: Outro (s=7) lead doubled durations (half speed).

# (3) RETROGRADE lead into Bridge (grid-locked onsets)
rev = list(reversed(LEAD_PITCHES[5]))
br_evs = []
rr = np.random.default_rng(SEED + 600)
cum = np.cumsum(rr.exponential(SECTION_TICKS / max(1, len(rev)), size=len(rev)))
onsets = sorted(int(round(o / GRID16)) * GRID16 for o in cum)
seen = set()
for pitch, st in zip(rev, onsets):
    if st >= SECTION_TICKS or st in seen:
        continue
    seen.add(st)
    bar = global_bar(6, st)
    if bar >= N_BARS:
        bar = N_BARS - 1
    tones = chord_tones(PROG_ROOT(bar), lo=LEAD_LO, hi=LEAD_HI)
    qp = quantize_to_chord(pitch, tones)
    en = min(SECTION_TICKS, st + 240)
    br_evs.append(MusicEvent(pitch=qp, volume=74, start_tick=st, end_tick=en))
phase2.set_unit(0, 6, MusicUnit(events=landmark(br_evs)))

# (4) INVERSION sax into Bridge (around axis 70)
axis = 70
inv_evs = []
src = SAX_PITCHES[1]
for i, p in enumerate(src):
    inv = 2 * axis - p
    bar = global_bar(6, i * 240)
    if bar >= N_BARS:
        bar = N_BARS - 1
    tones = chord_tones(PROG_ROOT(bar), lo=SAX_LO, hi=SAX_HI)
    qp = quantize_to_chord(inv, tones)
    st = i * GRID8
    if st >= SECTION_TICKS:
        break
    inv_evs.append(MusicEvent(pitch=qp, volume=62, start_tick=st,
                              end_tick=min(SECTION_TICKS, st + 200)))
phase2.set_unit(1, 6, MusicUnit(events=landmark(inv_evs)))

# (5) AUGMENTATION Outro lead: double durations (half speed), sparse
out_evs = []
src = LEAD_UNITS[7].events
src = [e for e in src if e.pitch != 0]
for i, e in enumerate(src[:16]):
    st = i * 960               # half-note spacing (augmentation)
    if st >= SECTION_TICKS:
        break
    bar = global_bar(7, st)
    if bar >= N_BARS:
        bar = N_BARS - 1
    tones = chord_tones(PROG_ROOT(bar), lo=LEAD_LO, hi=LEAD_HI)
    qp = quantize_to_chord(e.pitch, tones)
    out_evs.append(MusicEvent(pitch=qp, volume=70, start_tick=st,
                              end_tick=min(SECTION_TICKS, st + 600)))
phase2.set_unit(0, 7, MusicUnit(events=landmark(out_evs)))

# ---- finalize all cells with landmarks (cello/piano/bass already end at bar) 
for row in (2, 3, 4):
    for s in range(N_SECTIONS):
        unit = phase2.matrix.get_unit((row, s))
        events = list(unit.events) if unit is not None else []
        phase2.set_unit(row, s, MusicUnit(events=landmark(events)))

# ---- voice-leading check (bass + lead outer voices per bar pair) ----------
from rules.voice_leading import VoiceLeadingRules  # noqa: E402

vlc = VoiceLeadingRules(style="classical")
vl_flags = []
for bar in range(N_BARS - 1):
    _ = vlc  # (used below only if we compute interval relations)
    # bass + lead outer-voice interval at the bar boundary
    bass_a = BASS_ROOT[PROG_ROOT(bar)]
    bass_b = BASS_ROOT[PROG_ROOT(bar + 1)]
    if abs(bass_a - bass_b) > 9:
        vl_flags.append((bar, "bass_leap", bass_a, bass_b))
print("voice-leading flags (outer):", len(vl_flags))

ok2, msg2 = phase2.validate()
if not ok2:
    raise RuntimeError("phase2 validate FAIL: " + msg2)
print("PHASE2 validate:", msg2)

# ------------------------------------------------------------------ export
perfect_mid = os.path.join(MIDI_DIR, "290-funk-hawkes-suite-perfect.mid")
human_mid = os.path.join(MIDI_DIR, "290-funk-hawkes-suite-humanized.mid")

hz_instruments = {
    "Lead": TRUMPET.humanize_dna,
    "Sax": SAXOPHONE.humanize_dna,
    "Cello": CELLO.humanize_dna,
    "Piano": PIANO.humanize_dna,
    "Bass": DOUBLE_BASS.humanize_dna,
    "Drums": DRUM_KIT.humanize_dna,
}
hz = export_dual(phase2, perfect_mid, human_mid,
                 style="funk", seed=HZ_SEED, bpm=BPM, instruments=hz_instruments)
print("export_dual OK; hz summary:")
print(json.dumps(hz, indent=2, default=str))

# ------------------------------------------------------------------ provenance
write_provenance(P1_MIDI, AI_ASSISTED,
                 "Hawkes Process Self-Exciting Composition (Method 045)",
                 sources=["/opt/data/projects/Styles/Funk/088-funk-hawkes"],
                 parameters={"phase": "1", "layer": "raw", "style": "funk",
                             "key": KEY, "bpm": BPM, "seed": SEED,
                             "sections": N_SECTIONS, "bars": N_BARS},
                 notes="phase1 raw draft: single voice, OFF-GRID fractional "
                       "sojourn times, unquantized pitch, no harmony/bass/drums; "
                       "rework of 088-funk-hawkes (audit FAIL index.html missing).")
write_provenance(perfect_mid, AI_ASSISTED,
                 "Hawkes HPSEC + musicom rules (phase 2, grid-locked)",
                 sources=["/opt/data/projects/Styles/Funk/088-funk-hawkes"],
                 parameters={"phase": "2", "layer": "perfect", "style": "funk",
                             "key": KEY, "bpm": BPM, "seed": SEED,
                             "humanize_seed": HZ_SEED,
                             "sections": N_SECTIONS, "bars": N_BARS,
                             "variation": ["transposition", "retrograde",
                                           "inversion", "augmentation",
                                           "diminution", "density-rise"]},
                 notes="grid-locked concrete layer; off-grid onsets == 0.")
write_provenance(human_mid, AI_ASSISTED,
                 "Hawkes HPSEC + musicom rules + humanize (phase 2, humanized)",
                 sources=["/opt/data/projects/Styles/Funk/088-funk-hawkes"],
                 parameters={"phase": "2", "layer": "humanized", "style": "funk",
                             "key": KEY, "bpm": BPM, "seed": SEED,
                             "humanize_seed": HZ_SEED,
                             "humanize_profiles": {k: v.get("profile") if isinstance(v, dict) else v
                                                   for k, v in hz.items()}},
                 notes="style-derived seeded humanization (funk profile + "
                       "per-instrument DNA).")

# ------------------------------------------------------------------ grid viz
gv = os.path.join(ANALYSIS_DIR, "grid_visualization.txt")
write_grid_visualization(phase2.matrix, gv, ticks_per_character=120)
print("grid viz written", gv)

# ------------------------------------------------------------------ manifest
manifest = {
    "project": "290-funk-hawkes-suite",
    "genre": "Funk",
    "method": "045 Hawkes Process Self-Exciting Composition (HPSEC)",
    "key": KEY,
    "key_pcs": sorted(KEY_PCS),
    "bpm": BPM,
    "bars": N_BARS,
    "sections": NAMES,
    "section_roots": SECTION_ROOT_NAMES,
    "seed": SEED,
    "hz_seed": HZ_SEED,
    "phase1_midi": P1_MIDI,
    "perfect_midi": perfect_mid,
    "humanized_midi": human_mid,
    "hz_summary": hz,
}
with open(os.path.join(ANALYSIS_DIR, "manifest.json"), "w") as f:
    json.dump(manifest, f, indent=2, default=str)
print("DONE")
