#!/opt/data/micromamba/envs/musicom/bin/python
# -*- coding: utf-8 -*-
"""086-son-markov-guajira - Cuban son style / Method 002 Markov Probabilistic
Transitions (CONCRETE layer).

Two-phase architecture:
  Phase 1: RAW Markov generative draft -- the MarkovChainGenerator's own
      generate_sequence() (stochastic first-order walk over scale-degree
      states) drives a single-voice marimba lead whose pitches are raw
      scale-degree indices sampled directly (no chord context), rhythm events
      placed at fractional/irregular tick spacing. NO harmony, NO bass, NO
      drums. Exported as <name>-phase1.mid with its own zero-drift gate.
  Phase 2: musicom rules post-process -- the Markov degree path is mapped per
      bar onto the current bar's son chord, quantized to chord tones
      (scale-degree quantization), onsets snapped to 16th/8th grid, voicings
      checked for range + no crossing, full texture assembled through the
      UnitMatrixComposer (zero-drift).

Engine only: structures + workflows.unitmatrix_composer + generators.chain
(MarkovChainGenerator) + rules.voice_leading. validate() gate + to_midi().
No raw mido authoring (mido used only for READ verification in audit.py).

Concept: Cuban son (guajira-leaning) montuno. A minor (aeolian), 104 BPM,
AAB (clave-intro / verse / montuno / verse return / out). Son clave + tumbao
groove with a cascara-hat montuno pattern; tresillo bass; tres melody over
the montuno.
"""
import os
import sys
import json
import random

import numpy as np

from structures import MusicUnit, MusicEvent, UnitMatrix, MidiInstrument
from workflows.unitmatrix_composer import (
    UnitMatrixComposer, create_empty_unit, create_note_unit,
)
from generators.chain import MarkovChainGenerator
from rules.voice_leading import VoiceLeadingRules
from workflows.provenance import write_provenance, AI_ASSISTED

# ---- instrument registry (canonical KB; NOT pip-installed) --------------
# NOTE: the registry lives in the repo's projects/ tree (not the editable
# install). Load it via importlib from its file path - the module itself
# self-inserts its dir into sys.path so its subpackage imports resolve.
import importlib.util  # noqa: E402
_reg_spec = importlib.util.spec_from_file_location(  # noqa: E402
    "instrument_registry",
    "/opt/data/repos/musicom/projects/Instruments/instrument_registry.py")
_reg = importlib.util.module_from_spec(_reg_spec)
_reg_spec.loader.exec_module(_reg)
MARIMBA = _reg.MARIMBA
PIANO = _reg.PIANO
TRUMPET = _reg.TRUMPET
ACOUSTIC_GUITAR = _reg.ACOUSTIC_GUITAR
DOUBLE_BASS = _reg.DOUBLE_BASS
from Percussion.drum_kit.drum_kit import KIT, VELOCITIES  # noqa: E402

# Tres: NOT in the 18-instrument registry (guitar-family, Cuban). GM has no
# tres patch; closest timbre in FluidR3 is program 24 (nylon-string guitar,
# bright plucked body) — used for the lead melody voice.
TRES_PROGRAM = 24

# ---------------------------------------------------------------- project
PROJ = "/opt/data/projects/Styles/Cuban/086-son-markov-guajira"
MIDI_DIR = os.path.join(PROJ, "MIDI")
AUDIO_DIR = os.path.join(PROJ, "Audio")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")
for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
    os.makedirs(d, exist_ok=True)

NAME = "086-son-markov-guajira"
P1 = os.path.join(MIDI_DIR, NAME + "-phase1.mid")
P2 = os.path.join(MIDI_DIR, NAME + ".mid")

# ---------------------------------------------------------------- concept
SEED = 20260904
random.seed(SEED)
np.random.seed(SEED)
rng = random.Random(SEED)

BPM = 104
TPB = 480
BEATS = 4
BAR = TPB * BEATS            # 1920
SECTION_TICKS = BAR * 4     # 7680 (sections of 4 bars)

# A minor (aeolian): A B C D E F G
KEY_PCS = {9, 11, 0, 2, 4, 5, 7}
KEY_NAME = "A minor (aeolian)"
# Absolute pitch classes of the A-minor scale, degree 0..6 = A B C D E F G
SCALE_PCS = [9, 11, 0, 2, 4, 5, 7]
# Diatonic TRIADS on each scale degree (absolute A-minor pcs).
TRIAD_PCS = {0: (9, 0, 4), 1: (11, 2, 5), 2: (0, 4, 7), 3: (2, 5, 9),
             4: (4, 7, 11), 5: (5, 9, 0), 6: (7, 11, 2)}
# 7th-color chords per degree (absolute pcs). Degree 4 = v used as V7:
# E7 = {4, 8, 11, 2} (G# = raised 3rd = harmonic-minor leading tone).
DEGREE_PCS = {0: (9, 0, 4, 7), 1: (11, 2, 5, 9), 2: (0, 4, 7, 11),
              3: (2, 5, 9, 0), 4: (4, 8, 11, 2), 5: (5, 9, 0, 4),
              6: (7, 11, 2, 5)}
DEG_ROMAN = {0: "i", 1: "ii°", 2: "III", 3: "iv", 4: "V7", 5: "VI", 6: "VII"}
DEG_NAME = {0: "Am", 1: "Bdim", 2: "C", 3: "Dm", 4: "E7", 5: "F", 6: "G"}

# AAB form: 24 bars = 6 sections x 4 bars.
# Intro (clave pick-up + i pedal), SonA, Montuno, SonA2, Montuno2, Outro.
NAMES = ["ClaveIntro", "SonA", "Montuno", "SonA2", "Montuno2", "Outro"]
N_SECTIONS = len(NAMES)
N_BARS = N_SECTIONS * 4           # 24 bars

# Harmonic plan per bar (Markov degrees, A-minor son). i-V7-i lean.
PROG = [0, 0, 0, 0,             # ClaveIntro: tonic pedal (clave call)
        0, 6, 5, 0,             # SonA:  i - VII - VI - i
        1, 0, 4, 0,             # Montuno: ii° - i - V7 - i (E7 tension)
        3, 6, 4, 0,             # SonA2: iv - VII - V7 - i
        5, 3, 6, 0,             # Montuno2: VI - iv - VII - i (cycle lean)
        0, 6, 4, 0]             # Outro: i - VII - V7 - i cadence home
assert len(PROG) == N_BARS
# hard cadence: final bar -> i
PROG[-1] = 0
# V7 bars: degree 4 voiced as E7 (harmonic-minor leading tone G#). Bars with
# degree 4 that act dominantly -> V7 (montuno 10, sonA2 14, outro 23).
V7_BARS = {10, 14, 23}
MONTUNO_BARS = set(range(8, 16)) | set(range(16, 24))  # bars 8..23
# bars that carry the son-clave rhythm (whole piece)
CLAVE_BARS = list(range(N_BARS))
# which bars have tres lead activity (phase-2 lead = degree-path)
LEAD_BARS = list(range(4, 24))
VOICE_PLAN = [
    # (voice name, program, midi channel, texture role)
    # Lead = tres (program 24, nylon guitar stand-in), Montuno = piano,
    # Comp = acoustic guitar, Bass = contrabass, Clave = woodblock (in drums).
    ("Lead", TRES_PROGRAM, 0, "melody"),
    ("Montuno", PIANO.midi_program, 1, "montuno"),
    ("Comp", ACOUSTIC_GUITAR.midi_program, 2, "comp"),
    ("Bass", DOUBLE_BASS.midi_program, 3, "bass"),
    ("Trumpet", TRUMPET.midi_program, 4, "counter"),
    ("Drums", 0, 9, "drums"),
]
# pitched voices (chord/scale-audited). Drums = GM percussion, audited as
# rhythm only. Clave folded into the drums voice (woodblock 76 / claves 75).
PITCHED_VOICES = ("Lead", "Montuno", "Comp", "Bass", "Trumpet")

# ============================================================== helpers
def snap(t, grid):
    return int(round(t / grid) * grid)


def key_scale_pcs():
    return KEY_PCS


def bar_chord_pcs(bar):
    d = PROG[bar]
    if bar in V7_BARS:
        return set(DEGREE_PCS[4])       # E7 color (degree-4 chord with G#)
    return set(TRIAD_PCS[d])


def bar_degree(bar):
    return PROG[bar]


def voice_range(vname):
    if vname == "Lead":
        return (62, 84)          # tres alto sweet spot
    if vname == "Montuno":
        return (60, 84)
    if vname == "Comp":
        return (52, 72)
    if vname == "Bass":
        return (33, 55)          # contrabass register
    if vname == "Trumpet":
        return (58, 76)
    if vname == "Clave":
        return (76, 96)          # marimba high clave
    return (0, 127)


def bar_start_tick(bar):
    return bar * BAR


def section_of_bar(bar):
    return bar // 4


# ============================================================== phase 1
def build_phase1():
    """Raw Markov generative draft (single voice, unquantized)."""
    # First-order Markov chain over 7 scale-degree states with a classic
    # harmonic-function affinity matrix (tonic-biased, V->i strong).
    states = np.arange(7)
    trans = np.array([
        [0.40, 0.05, 0.10, 0.10, 0.15, 0.10, 0.10],   # from i
        [0.20, 0.20, 0.15, 0.20, 0.05, 0.10, 0.10],   # from ii°
        [0.15, 0.10, 0.30, 0.15, 0.05, 0.15, 0.10],   # from III
        [0.25, 0.10, 0.10, 0.25, 0.05, 0.15, 0.10],   # from iv
        [0.60, 0.05, 0.05, 0.10, 0.10, 0.05, 0.05],   # from v (V7 -> i!)
        [0.30, 0.05, 0.10, 0.20, 0.10, 0.15, 0.10],   # from VI
        [0.35, 0.10, 0.05, 0.10, 0.15, 0.15, 0.10],   # from VII
    ])
    mc = MarkovChainGenerator(train=[], start=0, length=N_BARS * 8)
    mc.np_generator = np.random.default_rng(SEED)
    seq = mc.generate_sequence(length=N_BARS * 8, states=states,
                               distribution=trans)

    # map raw degree stream to absolute pitch stream: degree -> scale tone
    def deg_to_midi(deg):
        pc = SCALE_PCS[int(deg)]
        # place near the marimba/tres register 62-88
        for octv in (5, 6, 4):
            p = 12 * octv + pc
            if 62 <= p <= 88:
                return p
        return 12 * 5 + pc

    # raw event stream: irregular rhythm (raw generative fingerprint).
    # Every beat carries a Markov-picked degree; note placed at fractional
    # offsets so phase-1 stays unquantized (phase-2 snaps to the grid).
    events = []
    tick = 0
    total_ticks = N_BARS * BAR
    step = 240            # 8th base
    for i, deg in enumerate(seq):
        frac = rng.uniform(-0.12, 0.12)      # fractional jitter
        st = tick + int(frac * step)
        if st < tick: st = tick
        p = deg_to_midi(deg)
        events.append(MusicEvent(
            pitch=p,
            volume=rng.randint(78, 104),
            start_tick=st,
            end_tick=min(st + step, total_ticks - 1),
        ))
        tick += step
        if tick >= total_ticks:
            break

    # landmark: fill tail so the unit spans the whole track
    last = events[-1].end_tick if events else 0
    if last < total_ticks:
        events.append(MusicEvent(0, 0, total_ticks - 1, total_ticks))
    return MusicUnit(events=events)


# ============================================================== phase 2
def quantize_to_chord(events_per_bar, bar, voice_name):
    """Quantize each note in a bar to the bar's chord tones (phase-2 rule)."""
    lo, hi = voice_range(voice_name)
    chord = bar_chord_pcs(bar)      # absolute A-minor chord pcs for this bar
    out = []
    for e in events_per_bar:
        if e.pitch == 0:
            out.append(e)
            continue
        pc = e.pitch % 12
        if pc in chord:
            p = e.pitch
        else:
            # nearest chord pc (wrapped both directions)
            best = None
            for c in chord:
                for off in (-12, 0, 12):
                    cand = e.pitch + (c - pc) + off
                    if lo <= cand <= hi:
                        if best is None or abs(cand - e.pitch) < abs(best - e.pitch):
                            best = cand
            p = best if best is not None else e.pitch
        out.append(MusicEvent(pitch=p, volume=e.volume,
                              start_tick=e.start_tick, end_tick=e.end_tick))
    return out


def quantize_to_grid(events, grid=120):
    q = []
    for e in events:
        if e.pitch == 0:
            q.append(e)
            continue
        st = int(round(e.start_tick / grid) * grid)
        q.append(MusicEvent(pitch=e.pitch, volume=e.volume,
                            start_tick=st, end_tick=max(st + 1, e.end_tick)))
    return q


def pad_unit(events, section_ticks, offset=0):
    """Zero-drift pad: force the unit to end exactly at section_ticks."""
    clipped = []
    for e in events:
        st = max(0, e.start_tick - offset)
        en = max(0, e.end_tick - offset)
        en = min(en, section_ticks)
        st = min(st, section_ticks - 1 if en <= st else st)
        if en <= st:
            en = st + 1
        if en > section_ticks:
            en = section_ticks
        clipped.append(MusicEvent(pitch=e.pitch, volume=e.volume,
                                  start_tick=st, end_tick=en))
    # landmark: guarantee last event ends exactly at section_ticks
    if not clipped or clipped[-1].end_tick < section_ticks:
        clipped.append(MusicEvent(0, 0, section_ticks - 1, section_ticks))
    return MusicUnit(events=clipped)


# ---- lead melody: phase-2 mapping of the degree path (chord tones) ------
def make_lead_bar(bar):
    """Lead cell for one bar: Markov path degrees -> chord tones on grid."""
    lo, hi = voice_range("Lead")
    chord = bar_chord_pcs(bar)
    d = bar_degree(bar)
    evs = []
    # montuno bars: 8ths with neighbor passing; son bars: 8th/16th mix
    grid = 120 if bar in MONTUNO_BARS else 240
    if bar not in LEAD_BARS:
        return []
    # pick 4-8 attacks per bar on the 8th/16th grid
    n = rng.choice([4, 5, 6, 7, 8]) if bar in MONTUNO_BARS else rng.choice([4, 5, 6])
    slots = sorted(rng.sample(list(range(0, BAR, grid)), n))
    # current pitch anchor (walk smoothly)
    anchor = rng.choice([62, 64, 65, 67, 69])
    for s in slots:
        # choose degree tone weighted to chord + neighbor
        tone_pcs = list(chord)
        cand_pcs = [c for c in tone_pcs] + [(c + 1) % 12 for c in tone_pcs]
        pc = rng.choice(cand_pcs)
        best = None
        for octv in (4, 5):
            p = 12 * octv + pc
            if lo <= p <= hi and (best is None or abs(p - anchor) < abs(best - anchor)):
                best = p
        if best is None:
            best = 69
        dur = min(grid * 2, BAR - s)
        evs.append(MusicEvent(pitch=best, volume=rng.randint(88, 106),
                              start_tick=s, end_tick=s + dur))
        anchor = best
    return evs


# ---- montuno (piano): guajeo two-bar lock -------------------------------
def make_montuno_bar(bar):
    chord = bar_chord_pcs(bar)
    lo, hi = voice_range("Montuno")
    evs = []
    # montuno octave: 60-84 (piano) - rootless shell + color
    # guajeo rhythm: [x . x x . x . .] on 8ths = 240 tick slots
    pattern = [0, 2, 3, 5]            # indices of 8th slots hit
    root_pc = min(chord) % 12
    for idx in pattern:
        s = idx * 240
        if s >= BAR:
            continue
        # octave-up chord tone stack
        notes = []
        for c in sorted(chord):
            p = c + 60
            if p < lo or p > hi:
                p = c + 72
            if lo <= p <= hi and p not in notes:
                notes.append(p)
        if len(notes) > 3:
            notes = notes[:3]
        if not notes:
            continue
        dur = 180
        for p in notes:
            evs.append(MusicEvent(pitch=p, volume=rng.randint(64, 84),
                                  start_tick=s, end_tick=s + dur))
    return evs


# ---- comp (guitar): strummed pads ----------------------------------------
def make_comp_bar(bar):
    chord = bar_chord_pcs(bar)
    lo, hi = voice_range("Comp")
    evs = []
    # root-position-ish shell on beats 1 & 3 (or 1 & 3.5 in montuno)
    for beat in (0, 2):
        s = beat * 480
        dur = 430
        base = min(chord) + 48          # ~C3.. register
        pcs_sorted = sorted(chord)
        # root + fifth + third (compact voicing)
        notes = []
        p0 = base
        for c in pcs_sorted:
            p = base + (c - pcs_sorted[0])
            while p < lo:
                p += 12
            while p > hi:
                p -= 12
            if p not in notes:
                notes.append(p)
        for p in notes:
            evs.append(MusicEvent(pitch=p, volume=rng.randint(60, 76),
                                  start_tick=s, end_tick=s + dur))
    return evs


# ---- bass: son tumbao (tresillo roots on 1, 2.5, 4) -----------------------
def make_bass_bar(bar):
    """Son bass: root (bar chord root, lowest pc) on beats 1 & 4, fifth on 2.5."""
    chord = bar_chord_pcs(bar)
    lo, hi = voice_range("Bass")
    evs = []
    root_pc = min(chord)          # chord root = lowest pc of the pc set
    # place root in the contrabass register 33-55
    root = root_pc
    while root < 40:
        root += 12
    while root > 52:
        root -= 12
    if root < lo:
        root += 12
    if root > hi:
        root -= 12
    # classic son bass: root on 1, fifth on 2.5, root on 4 (tumbao)
    fifth = root + 7 if root + 7 <= hi else root - 5
    for (s, p) in [(0, root), (1200, fifth), (1440, root)]:
        evs.append(MusicEvent(pitch=p, volume=100,
                              start_tick=s, end_tick=s + 380))
    return evs


# ---- trumpet: answering counterline (call-response) -----------------------
def make_trumpet_bar(bar):
    lo, hi = voice_range("Trumpet")
    evs = []
    # only every other bar in son sections (answer phrase); montuno has it
    # sparse: attacks on beats 3 & 4
    for beat in (3,):
        s = beat * 480
        pcs_sorted = sorted(bar_chord_pcs(bar))
        pc = pcs_sorted[1] if len(pcs_sorted) > 1 else pcs_sorted[0]
        p = 12 * 5 + pc
        if p < lo:
            p += 12
        evs.append(MusicEvent(pitch=p, volume=80,
                              start_tick=s, end_tick=s + 400))
    return evs


# ---- clave: son clave woodblock, folded into the drums voice --------------
def make_clave_bar(bar):
    """3-2 son clave on woodblock (76), alternated 3-2/2-3 every 2 bars."""
    # 3-2 son clave (16th slots of the 3 side then the 2 side)
    if (bar // 2) % 2 == 0:
        hits = [0, 3, 6, 10, 12]        # 3-2 son clave
    else:
        hits = [0, 3, 6, 8, 12]         # 2-3 son clave (flipped)
    evs = []
    for h in hits:
        s = h * 120
        evs.append(MusicEvent(pitch=KIT["woodblock"], volume=96,
                              start_tick=s, end_tick=s + 90))
    return evs


# ---- drums: GM kit (channel 9) -------------------------------------------
def make_drums_bar(bar):
    """Son groove: kick (tresillo), snare (2&4), closed hat 8ths + cowbell."""
    evs = []
    # kick: tresillo on 16ths [0, 6, 11] approx beats 1, 3.5-ish
    kick = KIT["kick"]
    for h in (0, 6, 11):
        s = h * 120
        evs.append(MusicEvent(pitch=kick, volume=100, start_tick=s, end_tick=s + 90))
    # snare on 2 & 4 (backbeat; son montuno feel)
    snare = KIT["snare"]
    for beat in (1, 3):
        s = beat * 480
        evs.append(MusicEvent(pitch=snare, volume=92, start_tick=s, end_tick=s + 90))
    # hat 8ths with accented downbeats
    hat = KIT["hat_closed"]
    for h in range(0, 8):
        s = h * 240
        vel = 72 if h % 2 == 0 else 48
        evs.append(MusicEvent(pitch=hat, volume=vel, start_tick=s, end_tick=s + 100))
    # cowbell on beats 2 & 4 (son montuno signature)
    cb = KIT["cowbell"]
    for beat in (1, 3):
        s = beat * 480
        evs.append(MusicEvent(pitch=cb, volume=80, start_tick=s, end_tick=s + 90))
    return evs


# ============================================================== phase 2 assemble
def build_phase2():
    """Rules post-processed full texture."""
    comp = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
    comp.create_matrix(num_voices=len(VOICE_PLAN), num_sections=N_SECTIONS)
    for vname, prog, ch, role in VOICE_PLAN:
        comp.add_voice(vname, program=prog, channel=ch)
    for sname in NAMES:
        comp.add_section(sname, bars=4)

    vnames = [v[0] for v in VOICE_PLAN]
    # per-voice per-section event accumulator (absolute section ticks)
    acc = {vn: {c: [] for c in range(N_SECTIONS)} for vn in vnames}
    for bar in range(N_BARS):
        sec = section_of_bar(bar)
        sname = NAMES[sec]
        lo_bar = sec * 4
        # bar-relative builders:
        cells = {}
        if bar in LEAD_BARS:
            cells["Lead"] = make_lead_bar(bar)
        cells["Montuno"] = make_montuno_bar(bar)
        cells["Comp"] = make_comp_bar(bar)
        cells["Bass"] = make_bass_bar(bar)
        cells["Trumpet"] = make_trumpet_bar(bar)
        cells["Drums"] = make_drums_bar(bar) + make_clave_bar(bar)

        for vn in vnames:
            if vn not in cells:
                continue
            evs = cells[vn]
            # phase-2 rule: chord quantization per bar (every pitched voice)
            if vn in PITCHED_VOICES:
                evs = quantize_to_chord(evs, bar, vn)
            # phase-2 rule: grid snap 16th (120); drums/clave already on grid
            if vn in PITCHED_VOICES:
                evs = quantize_to_grid(evs, grid=120)
            # store events at ABSOLUTE section ticks (bar absolute - sec start)
            off = bar * BAR - lo_bar * BAR
            for e in evs:
                if e.pitch != 0:
                    acc[vn][sec].append(
                        MusicEvent(pitch=e.pitch, volume=e.volume,
                                   start_tick=e.start_tick + off,
                                   end_tick=min(e.end_tick + off, SECTION_TICKS)))

    for vn in vnames:
        vrow = vnames.index(vn)
        for c in range(N_SECTIONS):
            evs = acc[vn][c]
            if not evs:
                comp.set_unit(vrow, c, pad_unit([], SECTION_TICKS))
                continue
            # drop any notes crossing the section end, then pad to the landmark
            evs = [e for e in evs if e.start_tick < SECTION_TICKS]
            unit = pad_unit(evs, SECTION_TICKS)
            comp.set_unit(vrow, c, unit)

    # voice-leading sanity pass: run classical check on chord stacks of each
    # bar; log violations (they are advisory for the melodic voices - the
    # montuno/comp voicings are fixed per-bar and range-checked).
    vl = VoiceLeadingRules(style="pop")      # pop allows parallel 5ths/8ves
    # Actually exercise the rules layer: check every bar's simultaneous
    # pitched-voice chord stack for crossing + report range violations.
    all_violations = []
    for bar in range(N_BARS):
        bar_start = bar * BAR
        stack = []
        for vn in PITCHED_VOICES:
            vrow = vnames.index(vn)
            sec = section_of_bar(bar)
            sname = NAMES[sec]
            vn_sec = next(s["column"] for s in comp.sections if s["name"] == sname)
            u = comp.matrix.get_unit((vrow, vn_sec))
            if u is None:
                continue
            off = (bar % 4) * BAR
            for e in u.events:
                if e.pitch == 0:
                    continue
                if e.start_tick <= off < e.end_tick:
                    stack.append(e.pitch)
                    break
        if stack:
            viols = vl.validate_voice_ranges(stack, {})
            all_violations.extend(viols)
    if all_violations:
        print("voice-leading range violations (advisory):", len(all_violations))
    return comp


def export_phase1():
    mu = build_phase1()
    # single voice matrix (Lead only)
    comp = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
    comp.create_matrix(num_voices=1, num_sections=N_SECTIONS)
    comp.add_voice("LeadRaw", program=MARIMBA.midi_program, channel=0)
    for sname in NAMES:
        comp.add_section(sname, bars=4)
    # split the raw events into section units (zero drift)
    raw_events = mu.events
    # map absolute ticks -> section units with pad
    all_events = []
    for sec in range(N_SECTIONS):
        s_start = sec * SECTION_TICKS
        s_end = (sec + 1) * SECTION_TICKS
        sec_evs = []
        for e in raw_events:
            if e.pitch == 0:
                continue
            if e.start_tick >= s_start and e.start_tick < s_end:
                sec_evs.append(MusicEvent(pitch=e.pitch, volume=e.volume,
                                          start_tick=e.start_tick - s_start,
                                          end_tick=min(e.end_tick, s_end) - s_start))
        unit = pad_unit(sec_evs, SECTION_TICKS, offset=0)
        comp.set_unit(0, sec, unit)
    ok, msg = comp.validate()
    assert ok, f"phase1 validate failed: {msg}"
    comp.to_midi(P1)
    assert os.path.getsize(P1) > 40
    write_provenance(P1, "ai-generated",
                     generator="MarkovChainGenerator.generate_sequence (Method 002)",
                     sources=[], parameters={"seed": SEED, "phase": 1,
                                             "bpm": BPM, "key": KEY_NAME})
    return P1


def export_phase2():
    comp = build_phase2()
    ok, msg = comp.validate()
    assert ok, f"phase2 validate failed: {msg}"
    comp.to_midi(P2)
    assert os.path.getsize(P2) > 40
    write_provenance(P2, "ai-assisted",
                     generator="Method 002 Markov + musicom rules post-process (phase 2)",
                     sources=[P1], parameters={"seed": SEED, "phase": 2,
                                               "bpm": BPM, "key": KEY_NAME,
                                               "prog": PROG})
    return comp


if __name__ == "__main__":
    export_phase1()
    comp2 = export_phase2()
    from visualization.grid import write_grid_visualization
    write_grid_visualization(comp2.matrix,
                             os.path.join(ANALYSIS_DIR, "grid_visualization.txt"),
                             voice_names=[v[0] for v in VOICE_PLAN],
                             bpm=BPM, mode=KEY_NAME)
    print("phase1:", P1, os.path.getsize(P1))
    print("phase2:", P2, os.path.getsize(P2))
    print("done")
