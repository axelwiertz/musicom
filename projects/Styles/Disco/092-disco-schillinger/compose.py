# -*- coding: utf-8 -*-
"""092-disco-schillinger - Disco style / CONCRETE layer:
Method 018 Schillinger System of Musical Design (resultant interference of two
periodic generators + coordinate-axis pitch projection).

Phase 1: raw Schillinger draft (single voice).
  Rhythm = interference resultant durations of generators a=7, b=4 scaled to
  FRACTIONAL tick spacings (deliberately OFF the 16th grid -> raw fingerprint).
  Pitch  = coordinate-axis sine projection with seeded register drift.
  No harmony, no chord tones, no bass/drums.

Phase 2: musicom rules post-process:
  16th-grid lock (078 mandatory rule) -> Eb-major scale snap -> chord-tone
  quantize per bar (diatonic degree progression, canonical helper
  Scale7ChordDegree.get_diatonic_note) -> voice-leading check/correction
  (rules.voice_leading) -> full 7-voice disco texture (trumpet lead, sax
  counterline, piano comp, organ pad, guitar chank, octave bass, drum kit).

Engine only: structures + workflows.unitmatrix_composer + generators.schillinger
+ rules.voice_leading + rules.progression. mido READ-ONLY in audit scripts.
"""
import os
import json
import sys
import math

import numpy as np

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import (
    UnitMatrixComposer, create_empty_unit,
)
from generators.schillinger import SchillingerGenerator
from rules.progression import Scale7ChordDegree
from rules.voice_leading import VoiceLeadingRules

# instrument registry (source of truth - NOT pip-installed)
INSTR_DIR = "/opt/data/repos/musicom/projects/Instruments"
if INSTR_DIR not in sys.path:
    sys.path.insert(0, INSTR_DIR)
from instrument_registry import (  # noqa: E402
    TRUMPET, SAXOPHONE, PIANO, ORGAN, ACOUSTIC_GUITAR, DOUBLE_BASS, DRUM_KIT,
)

SEED = 20260910
rng = np.random.default_rng(SEED)

# ---------------------------------------------------------------- project dirs
PROJ = ("/opt/data/repos/musicom/projects/Styles/Disco/"
        "092-disco-schillinger")
MIDI_DIR = os.path.join(PROJ, "MIDI")
AUDIO_DIR = os.path.join(PROJ, "Audio")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")
for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
    os.makedirs(d, exist_ok=True)

# ---------------------------------------------------------------- concept
BPM = 118
TPB = 480
BEATS = 4
BAR = TPB * BEATS            # 1920
GRID16 = 120                 # 16th grid @ 480 TPB
GRID8 = 240
SECTION_TICKS = BAR * 4      # 7680 (4 bars per section)
NAMES = ["Intro", "Verse", "Chorus", "Break", "Chorus2", "Outro"]
BARS_PER = 4
N_SECTIONS = len(NAMES)
N_BARS = N_SECTIONS * BARS_PER      # 24

# Eb major: key root = Eb4 (MIDI 63)
KEY_ROOT = 63
MAJOR = [0, 2, 4, 5, 7, 9, 11]
SCALE_PCS = {(KEY_ROOT + i) % 12 for i in MAJOR}     # Eb F G Ab Bb C D
SCALE_PITCHES = [p for p in range(36, 96) if p % 12 in SCALE_PCS]

# diatonic degree roots via the CANONICAL framework helper (no % 7 wrappers)
def degree_pc(d):
    return Scale7ChordDegree.get_diatonic_note(KEY_ROOT, MAJOR, d) % 12


def degree_triad_pcs(d):
    return {Scale7ChordDegree.get_diatonic_note(KEY_ROOT, MAJOR, d + k) % 12
            for k in (0, 2, 4)}


# 24-bar disco progression as 0-based scale degrees (all diatonic in Eb major)
#   Intro   I  vi ii V   | Verse  I  V  vi IV  | Chorus IV V  I  vi
#   Break   ii V  I  vi  | Chorus2 IV V I  vi  | Outro  ii V  I  I
PROG_DEG = ([0, 5, 1, 4] + [0, 4, 5, 3] + [3, 4, 0, 5] +
            [1, 4, 0, 5] + [3, 4, 0, 5] + [1, 4, 0, 0])
assert len(PROG_DEG) == N_BARS, (len(PROG_DEG), N_BARS)
DEG_NAME = {0: "I", 1: "ii", 2: "iii", 3: "IV", 4: "V", 5: "vi", 6: "vii"}
PC_NAME = {3: "Eb", 5: "F", 7: "G", 8: "Ab", 10: "Bb", 0: "C", 2: "D"}
BAR_LABELS = [PC_NAME[degree_pc(d)] + DEG_NAME[d] for d in PROG_DEG]


def chord_tones(deg, lo, hi):
    """Chord tones (diatonic triad) of degree `deg` inside [lo, hi]."""
    pcs = degree_triad_pcs(deg)
    return sorted(p for p in range(lo, hi + 1) if p % 12 in pcs)


def nearest_pc_pitch(pc, lo, hi, anchor=None):
    cands = [p for p in range(lo, hi + 1) if p % 12 == pc]
    if not cands:
        return None
    if anchor is None:
        return min(cands, key=lambda p: (abs(p - (lo + hi) // 2), p))
    return min(cands, key=lambda p: (abs(p - anchor), p))


# ---------------------------------------------------------------- phase 1
SCH_A, SCH_B = 7, 4
sch = SchillingerGenerator(generator_a=SCH_A, generator_b=SCH_B)
SCH_DURS = sch.generate_resultant()
print("Schillinger resultant a=%d b=%d: %s (pulses=%d, onsets=%d)"
      % (SCH_A, SCH_B, SCH_DURS, sum(SCH_DURS), len(SCH_DURS)))

LEAD_LO, LEAD_HI = 60, 84      # trumpet solo range


def raw_schillinger_melody(seed, section_ticks, n_events, center0):
    """Raw Schillinger walk: resultant-scaled fractional onsets + axis pitch."""
    r = np.random.default_rng(seed)
    events = []
    tick = 0
    center = center0
    avg_pulse = sum(SCH_DURS) / float(len(SCH_DURS))
    for i in range(n_events):
        d_pulses = SCH_DURS[i % len(SCH_DURS)]
        scale = (section_ticks / float(n_events)) / avg_pulse
        scale *= (0.88 + 0.28 * r.random())     # jitter -> OFF-GRID onsets
        dur = int(d_pulses * scale)
        dur = max(80, min(dur, section_ticks - tick))
        # coordinate-axis projection (diagonal/sine trajectory) + drift
        p = center + 4.5 * math.sin(i * 0.55) + r.normal(0.0, 1.2)
        p = max(LEAD_LO, min(LEAD_HI, p))
        vel = int(np.clip(64 + 26 * abs(math.sin(i * 1.21)), 48, 108))
        if tick + dur > section_ticks:
            dur = section_ticks - tick
        if dur > 0:
            events.append(MusicEvent(pitch=int(round(p)), volume=vel,
                                     start_tick=tick, end_tick=tick + dur))
        tick += dur
        center += r.normal(0.0, 0.8)
    return events


phase1 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
phase1.create_matrix(num_voices=1, num_sections=N_SECTIONS)
phase1.add_voice("LeadRaw", program=TRUMPET.midi_program, channel=0)

P1_N = {0: 24, 1: 32, 2: 40, 3: 32, 4: 40, 5: 24}
P1_C = {0: 70.0, 1: 72.0, 2: 74.0, 3: 73.0, 4: 74.0, 5: 70.0}
for s, name in enumerate(NAMES):
    phase1.add_section(name, bars=BARS_PER)
    evs = raw_schillinger_melody(SEED + s, SECTION_TICKS, P1_N[s], P1_C[s])
    if not evs or evs[-1].end_tick < SECTION_TICKS:
        evs.append(MusicEvent(pitch=0, volume=0,
                              start_tick=SECTION_TICKS - 1,
                              end_tick=SECTION_TICKS))
    phase1.set_unit(0, s, MusicUnit(events=evs))

ok1, msg1 = phase1.validate()
print("PHASE1 validate:", ok1, msg1)
assert ok1, msg1
P1_MIDI = os.path.join(MIDI_DIR, "092-disco-schillinger-phase1.mid")
phase1.to_midi(P1_MIDI)
print("phase1 written", P1_MIDI, os.path.getsize(P1_MIDI), "bytes")

# ---------------------------------------------------------------- phase 2
def quantize_to_grid(events, grid=GRID16, limit=SECTION_TICKS):
    q = []
    for e in events:
        if e.pitch == 0:
            continue
        st = int(round(e.start_tick / grid) * grid)
        if st >= limit:
            st = limit - grid
        en = max(st + 1, min(e.end_tick, limit))
        q.append(MusicEvent(pitch=e.pitch, volume=e.volume,
                            start_tick=st, end_tick=en))
    q.sort(key=lambda e: (e.start_tick, e.pitch))
    return q


phase2 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
VOICES = [
    ("Lead",   TRUMPET.midi_program, 0),          # Trumpet (disco hook)
    ("Sax",    SAXOPHONE.midi_program, 1),        # Sax (answering line)
    ("Piano",  PIANO.midi_program, 2),            # Piano (stab comp)
    ("Organ",  ORGAN.midi_program, 3),            # Organ (sustained pad)
    ("Guitar", ACOUSTIC_GUITAR.midi_program, 4),  # Acoustic guitar (chank)
    ("Bass",   DOUBLE_BASS.midi_program, 5),      # Double bass (octave pulse)
    ("Drums",  DRUM_KIT.midi_program, 9),         # GM drum kit (channel 9)
]
N_V = len(VOICES)
phase2.create_matrix(num_voices=N_V, num_sections=N_SECTIONS)
for name, prog, ch in VOICES:
    phase2.add_voice(name, program=prog, channel=ch)
for n in NAMES:
    phase2.add_section(n, bars=BARS_PER)

# --- row 0 LEAD: grid lock -> scale snap -> chord-tone quantize -> leap cap
for s in range(N_SECTIONS):
    raw_unit = phase1.matrix.get_unit((0, s))
    evs = quantize_to_grid(list(raw_unit.events), GRID16)
    q = []
    for e in evs:
        bar = s * BARS_PER + min(e.start_tick // BAR, BARS_PER - 1)
        deg = PROG_DEG[bar]
        tones = chord_tones(deg, LEAD_LO, LEAD_HI)
        sc = min(SCALE_PITCHES, key=lambda c: (abs(c - e.pitch), c))
        qp = min(tones, key=lambda c: (abs(c - sc), c))
        q.append(MusicEvent(pitch=qp, volume=e.volume,
                            start_tick=e.start_tick, end_tick=e.end_tick))
    # monophonic: drop duplicate onsets (trumpet cannot sound two notes)
    ded = []
    for e in q:
        if ded and e.start_tick == ded[-1].start_tick:
            continue
        ded.append(e)
    # voice leading: cap leaps > 10 semitones toward nearest chord tone
    for i in range(1, len(ded)):
        if abs(ded[i].pitch - ded[i - 1].pitch) > 10:
            bar = s * BARS_PER + min(ded[i].start_tick // BAR, BARS_PER - 1)
            tones = chord_tones(PROG_DEG[bar], LEAD_LO, LEAD_HI)
            ded[i].pitch = min(tones, key=lambda c: (abs(c - ded[i - 1].pitch), c))
    # monophonic legato: cap each note at the next onset (no overlapping
    # retriggers of the same pitch -> clean MIDI note accounting)
    for i in range(len(ded) - 1):
        if ded[i].end_tick > ded[i + 1].start_tick:
            ded[i].end_tick = ded[i + 1].start_tick
    phase2.set_unit(0, s, MusicUnit(events=ded))

# --- row 1 SAX: 8th-note answering counterline (chord tones, sweet spot)
for s in range(N_SECTIONS):
    r = np.random.default_rng(SEED + 100 + s)
    evs = []
    for b in range(BARS_PER):
        t0 = b * BAR
        deg = PROG_DEG[s * BARS_PER + b]
        tones = chord_tones(deg, 61, 79) or chord_tones(deg, 55, 79) or [67]
        for beat in (1, 3):                    # answers on beats 2 & 4
            st = t0 + beat * 480
            evs.append(MusicEvent(pitch=int(r.choice(tones)), volume=70,
                                  start_tick=st, end_tick=st + 240))
            st2 = st + 240
            evs.append(MusicEvent(pitch=int(r.choice(tones)), volume=62,
                                  start_tick=st2, end_tick=st2 + 240))
    phase2.set_unit(1, s, MusicUnit(events=evs))

# --- row 2 PIANO: offbeat 8th stabs (chord tones, octave 4/5)
for s in range(N_SECTIONS):
    evs = []
    for b in range(BARS_PER):
        t0 = b * BAR
        deg = PROG_DEG[s * BARS_PER + b]
        tones = chord_tones(deg, 60, 84) or [63]
        for beat in range(BEATS):
            st = t0 + beat * 480 + 240        # the "and" of every beat
            p = tones[(beat + b) % len(tones)]
            evs.append(MusicEvent(pitch=p, volume=58,
                                  start_tick=st, end_tick=st + 120))
        st = t0 + 1560                       # 16th pickup into next bar
        evs.append(MusicEvent(pitch=tones[0], volume=52,
                              start_tick=st, end_tick=st + 120))
    phase2.set_unit(2, s, MusicUnit(events=evs))

# --- row 3 ORGAN: sustained whole-bar triad pad (chord tones 55-79)
for s in range(N_SECTIONS):
    evs = []
    for b in range(BARS_PER):
        t0 = b * BAR
        deg = PROG_DEG[s * BARS_PER + b]
        tones = chord_tones(deg, 55, 79)
        if not tones:
            tones = [63]
        pad = tones[:3] if len(tones) >= 3 else tones
        for k, p in enumerate(pad):
            evs.append(MusicEvent(pitch=p, volume=44 + 4 * k,
                                  start_tick=t0, end_tick=t0 + BAR - 60))
    phase2.set_unit(3, s, MusicUnit(events=evs))

# --- row 4 GUITAR: 16th "chank" offbeats (single-note funk/disco scratches)
for s in range(N_SECTIONS):
    evs = []
    for b in range(BARS_PER):
        t0 = b * BAR
        deg = PROG_DEG[s * BARS_PER + b]
        tones = chord_tones(deg, 52, 76) or [63]
        for k, off in enumerate((120, 360, 600, 840, 1080, 1320, 1560, 1800)):
            p = tones[(k + b) % len(tones)]
            evs.append(MusicEvent(pitch=p, volume=48 if off % 480 else 56,
                                  start_tick=t0 + off, end_tick=t0 + off + 110))
    phase2.set_unit(4, s, MusicUnit(events=evs))

# --- row 5 BASS: octave disco pulse (root / root+12 on 8ths)
for s in range(N_SECTIONS):
    evs = []
    for b in range(BARS_PER):
        t0 = b * BAR
        deg = PROG_DEG[s * BARS_PER + b]
        root = nearest_pc_pitch(degree_pc(deg), 33, 48, anchor=39) or 39
        for k in range(0, BAR, GRID8):
            p = root if (k // GRID8) % 2 == 0 else root + 12
            if p > 60:
                p = root
            evs.append(MusicEvent(pitch=p,
                                  volume=86 if k % 480 == 0 else 72,
                                  start_tick=t0 + k, end_tick=t0 + k + 200))
    phase2.set_unit(5, s, MusicUnit(events=evs))

# --- row 6 DRUMS: four-on-the-floor disco kit (channel 9)
from Percussion.drum_kit.drum_kit import KIT  # noqa: E402
K = KIT
DRUM_PLAN = {
    0: dict(kick=104, snare=None, clap=None, hat=56, ride=False, crash=True),
    1: dict(kick=110, snare=88, clap=84, hat=64, ride=False, crash=False),
    2: dict(kick=116, snare=94, clap=92, hat=70, ride=True, crash=True),
    3: dict(kick=108, snare=86, clap=None, hat=60, ride=False, crash=True),
    4: dict(kick=116, snare=94, clap=92, hat=70, ride=True, crash=False),
    5: dict(kick=104, snare=None, clap=None, hat=54, ride=False, crash=True),
}
for s in range(N_SECTIONS):
    plan = DRUM_PLAN[s]
    evs = []
    for b in range(BARS_PER):
        t0 = b * BAR
        for k in range(0, BAR, 480):                      # four-on-the-floor
            evs.append(MusicEvent(pitch=K["kick"], volume=plan["kick"],
                                  start_tick=t0 + k, end_tick=t0 + k + 120))
        for k in range(0, BAR, GRID8):                    # closed hats 8ths
            evs.append(MusicEvent(pitch=K["hat_closed"], volume=plan["hat"],
                                  start_tick=t0 + k, end_tick=t0 + k + 60))
        if plan["ride"]:                                  # ride on choruses
            for k in range(0, BAR, 480):
                evs.append(MusicEvent(pitch=K["ride"], volume=68,
                                      start_tick=t0 + k + 240,
                                      end_tick=t0 + k + 300))
        if plan["snare"] is not None:
            for off in (480, 1440):                       # beats 2 & 4
                evs.append(MusicEvent(pitch=K["snare"], volume=plan["snare"],
                                      start_tick=t0 + off,
                                      end_tick=t0 + off + 120))
        if plan["clap"] is not None:
            for off in (480, 1440):
                evs.append(MusicEvent(pitch=K["clap"], volume=plan["clap"],
                                      start_tick=t0 + off,
                                      end_tick=t0 + off + 120))
        if plan["crash"] and b == 0:
            evs.append(MusicEvent(pitch=K["crash"], volume=96,
                                  start_tick=t0, end_tick=t0 + 240))
    phase2.set_unit(6, s, MusicUnit(events=evs))

# --- voice-leading check (bass + lead outer voices, classical strictness)
vlc = VoiceLeadingRules(style="classical")
vl_flags = []
for bar in range(N_BARS - 1):
    s, b = divmod(bar, BARS_PER)
    deg_a, deg_b = PROG_DEG[bar], PROG_DEG[bar + 1]
    bass_a = nearest_pc_pitch(degree_pc(deg_a), 33, 48, anchor=39) or 39
    bass_b = nearest_pc_pitch(degree_pc(deg_b), 33, 48, anchor=39) or 39
    u = phase2.matrix.get_unit((0, s))
    evs = [e for e in u.events
           if e.pitch > 0 and b * BAR <= e.start_tick < (b + 1) * BAR]
    s2, b2 = (s, b + 1) if b + 1 < BARS_PER else (s + 1, 0)
    if s2 >= N_SECTIONS:
        continue
    u2 = phase2.matrix.get_unit((0, s2))
    evs_next = [e for e in u2.events
                if e.pitch > 0 and b2 * BAR <= e.start_tick < (b2 + 1) * BAR]
    if evs and evs_next:
        viol = vlc.check_parallel_motion([bass_a, evs[0].pitch],
                                         [bass_b, evs_next[0].pitch])
        if viol:
            vl_flags.append((bar, "parallel", viol))
        hid = vlc.check_hidden_fifths([bass_a, evs[0].pitch],
                                      [bass_b, evs_next[0].pitch])
        if hid:
            vl_flags.append((bar, "hidden", hid))
print("VL flags (bass+lead, classical):", len(vl_flags))


def fix_outer_voice(bar_target):
    """Nudge lead's first note of bar_target off a 5th/8ve with the bass."""
    s, b = divmod(bar_target, BARS_PER)
    u = phase2.matrix.get_unit((0, s))
    evs = list(u.events)
    target = None
    for e in evs:
        if e.pitch > 0 and b * BAR <= e.start_tick < (b + 1) * BAR:
            target = e
            break
    if target is None:
        return False
    tones = chord_tones(PROG_DEG[bar_target], LEAD_LO, LEAD_HI)
    bass = nearest_pc_pitch(degree_pc(PROG_DEG[bar_target]), 33, 48,
                            anchor=39) or 39
    cands = [t for t in tones if abs((t - bass) % 12) not in (0, 7)]
    cands = [t for t in cands if abs(t - target.pitch) <= 10]
    if not cands:
        return False
    target.pitch = min(cands, key=lambda c: (abs(c - target.pitch), c))
    phase2.set_unit(0, s, MusicUnit(events=evs))
    return True


n_fixed = 0
for (bar, _kind, _v) in list(vl_flags):
    if fix_outer_voice(bar + 1):
        n_fixed += 1
print("VL fixes applied:", n_fixed)


# --- normalize every cell to the exact section boundary (zero-drift invariant)
def normalize_cell(unit, total_ticks):
    evs = list(unit.events)
    for e in evs:
        if e.end_tick > total_ticks:
            e.end_tick = total_ticks
        if e.start_tick >= total_ticks:
            e.start_tick = total_ticks - 10
        if e.start_tick < 0:
            e.start_tick = 0
        if e.end_tick <= e.start_tick:
            e.end_tick = min(total_ticks, e.start_tick + 60)
    if not evs or evs[-1].end_tick < total_ticks:
        evs.append(MusicEvent(pitch=0, volume=0, start_tick=total_ticks - 1,
                              end_tick=total_ticks))
    return MusicUnit(events=sorted(evs, key=lambda e: (e.start_tick, e.pitch)))


for s in range(N_SECTIONS):
    for v in range(N_V):
        u = phase2.matrix.get_unit((v, s))
        if u is None:
            phase2.set_unit(v, s, create_empty_unit(SECTION_TICKS))
            continue
        phase2.set_unit(v, s, normalize_cell(u, SECTION_TICKS))

ok2, msg2 = phase2.validate()
print("PHASE2 validate:", ok2, msg2)
assert ok2, msg2
P2_MIDI = os.path.join(MIDI_DIR, "092-disco-schillinger.mid")
phase2.to_midi(P2_MIDI)
print("phase2 written", P2_MIDI, os.path.getsize(P2_MIDI), "bytes")

# --- provenance sidecars
from workflows.provenance import write_provenance, AI_ASSISTED  # noqa: E402
write_provenance(P1_MIDI, classification=AI_ASSISTED,
                 generator="SchillingerGenerator(method 018)",
                 parameters={"phase": 1, "seed": SEED,
                             "generators": f"a={SCH_A}, b={SCH_B}",
                             "resultant_pulses": SCH_DURS,
                             "method": "018 Schillinger System of Musical Design"},
                 notes="Raw Schillinger draft: fractional (off-grid) onsets, "
                       "coordinate-axis pitch projection, no harmony.")
write_provenance(P2_MIDI, classification=AI_ASSISTED,
                 generator="SchillingerGenerator(method 018) + rules layer",
                 parameters={"phase": 2, "seed": SEED,
                             "grid": "16th (120 @ 480 TPB)",
                             "key": "Eb major",
                             "progression": BAR_LABELS,
                             "method": "018 + musicom rules layer"})
print("DONE")

# --- canonical high-contrast UnitMatrix grid render (visualization.grid)
from visualization.grid import write_grid_visualization  # noqa: E402
write_grid_visualization(phase2.matrix,
                         os.path.join(ANALYSIS_DIR, "matrix_grid.txt"),
                         ticks_per_character=120, bpm=BPM, mode="disco")
print("matrix_grid.txt written")

# --- machine-readable concept record for the REPORT
with open(os.path.join(ANALYSIS_DIR, "concept.json"), "w") as f:
    json.dump({"project": "092-disco-schillinger", "genre": "Disco",
               "method": "018 Schillinger System of Musical Design",
               "layer": "concrete", "seed": SEED, "bpm": BPM,
               "key": "Eb major", "grid_16th": GRID16,
               "schillinger": {"a": SCH_A, "b": SCH_B,
                               "resultant": SCH_DURS},
               "progression": BAR_LABELS,
               "sections": NAMES,
               "voices": [v[0] for v in VOICES],
               "vl_flags": len(vl_flags), "vl_fixes": n_fixed}, f, indent=2)
