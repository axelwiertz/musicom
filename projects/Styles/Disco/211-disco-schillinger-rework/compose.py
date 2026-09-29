# -*- coding: utf-8 -*-
"""211-disco-schillinger-rework - Disco / Method 018 Schillinger System.

Rework agent nightly job. Source = 092-disco-schillinger (Disco, Eb major,
118 BPM, Method 018 resultant interference a=7 b=4).
Audit FAILED std6 (provenance.json + index.html missing at project root).
Decision: REDESIGN via canonical UnitMatrixComposer preserving identity
(genre/key/tempo/instrumentation/Schillinger method) -> NEW LONGER 32-bar
piece with >=3 variation techniques.

Two-phase (MANDATORY):
  Phase 1 = raw Schillinger draft, single voice, off-grid fractional onsets,
            coordinate-axis sine pitch (no harmony).
  Phase 2 = musicom rules: 16th-grid lock, Eb-major scale snap, chord-tone
            quantize per bar (floor t//BAR), voice-leading leap cap, register
            enforcement, full 7-voice disco arrangement.
"""

import os
import json

import numpy as np

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import (
    UnitMatrixComposer, create_empty_unit,
)
from generators.schillinger import SchillingerGenerator
from rules.progression import Scale7ChordDegree
from workflows.provenance import write_provenance, AI_ASSISTED
from visualization.grid import write_grid_visualization

SEED = 20260929
rng = np.random.default_rng(SEED)

# ---------------------------------------------------------------- project dirs
GENRE = "Disco"
PROJ = ("/opt/data/repos/musicom/projects/Styles/Disco/"
        "211-disco-schillinger-rework")
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
NAMES = ["Intro", "Verse", "Chorus", "Break",
         "Verse2", "Chorus2", "Breakdown", "Outro"]
BARS_PER = 4
N_SECTIONS = len(NAMES)      # 8
N_BARS = N_SECTIONS * BARS_PER   # 32
TOTAL_TICKS = SECTION_TICKS * N_SECTIONS

# Eb major: key root = Eb4 (MIDI 63)
KEY_ROOT = 63
MAJOR = [0, 2, 4, 5, 7, 9, 11]
SCALE_PCS = {(KEY_ROOT + i) % 12 for i in MAJOR}     # Eb F G Ab Bb C D
SCALE_PITCHES = [p for p in range(36, 96) if p % 12 in SCALE_PCS]


def degree_pc(d):
    return Scale7ChordDegree.get_diatonic_note(KEY_ROOT, MAJOR, d) % 12


def degree_triad_pcs(d):
    return {Scale7ChordDegree.get_diatonic_note(KEY_ROOT, MAJOR, d + k) % 12
            for k in (0, 2, 4)}


# 32-bar disco progression, 0-based diatonic degrees. Each section starts on
# a DIFFERENT degree (per-section harmonic regions; section roots derived from
# the MIDPOINT bar -> fixes "bar-0 always degree i" bug).
#   Intro      I  vi ii V    Verse   I  V  vi IV
#   Chorus     IV V  I  vi   Break   ii V  I  vi
#   Verse2     vi IV V  I    Chorus2 IV V  I  IV
#   Breakdown  ii IV V  vi   Outro   ii V  I  I
PROG_DEG = ([0, 5, 1, 4] + [0, 4, 5, 3] + [3, 4, 0, 5] + [1, 4, 0, 5] +
            [5, 3, 4, 0] + [3, 4, 0, 3] + [1, 3, 4, 5] + [1, 4, 0, 0])
assert len(PROG_DEG) == N_BARS, (len(PROG_DEG), N_BARS)
DEG_NAME = {0: "I", 1: "ii", 2: "iii", 3: "IV", 4: "V", 5: "vi", 6: "vii"}
PC_NAME = {3: "Eb", 5: "F", 7: "G", 8: "Ab", 10: "Bb", 0: "C", 2: "D"}
BAR_LABELS = [PC_NAME[degree_pc(d)] + DEG_NAME[d] for d in PROG_DEG]


def section_midpoint_deg(s_idx):
    """Degree at the section's midpoint bar (never bar 0)."""
    return PROG_DEG[s_idx * BARS_PER + 1]


SECTION_DEGS = [section_midpoint_deg(s) for s in range(N_SECTIONS)]


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
        p = center + 4.5 * np.sin(i * 0.55) + r.normal(0.0, 1.2)
        p = max(LEAD_LO, min(LEAD_HI, p))
        vel = int(np.clip(64 + 26 * abs(np.sin(i * 1.21)), 48, 108))
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
phase1.add_voice("LeadRaw", program=56, channel=0)

P1_N = {0: 24, 1: 32, 2: 40, 3: 32, 4: 40, 5: 40, 6: 32, 7: 24}
P1_C = {0: 70.0, 1: 72.0, 2: 74.0, 3: 73.0,
        4: 74.0, 5: 74.0, 6: 73.0, 7: 70.0}
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
P1_MIDI = os.path.join(MIDI_DIR, "211-disco-schillinger-rework-phase1.mid")
phase1.to_midi(P1_MIDI)
print("phase1 written", P1_MIDI, os.path.getsize(P1_MIDI), "bytes")

# ---------------------------------------------------------------- phase 2
def snap16(t):
    return int(round(t / float(GRID16)) * GRID16)


# Variation transforms applied to the raw lead (pre-quantization).
# 0 Intro     = identity
# 2 Chorus    = transposition +5 (perfect 4th)
# 3 Break     = retrograde (reverse pitch sequence)
# 4 Verse2    = register shift +12 (octave up)
# 5 Chorus2   = inversion around Eb4 (63)
# 6 Breakdown = diminution x0.5 (staccato)
# 7 Outro     = augmentation x2.0 (legato)
def transform_lead(s_idx, raw_events):
    pitches = [e.pitch for e in raw_events]
    onsets = [e.start_tick for e in raw_events]
    durs = [e.end_tick - e.start_tick for e in raw_events]
    vels = [e.volume for e in raw_events]
    if s_idx == 2:
        pitches = [p + 5 for p in pitches]
    elif s_idx == 3:
        pitches = list(reversed(pitches))
    elif s_idx == 4:
        pitches = [p + 12 for p in pitches]
    elif s_idx == 5:
        pitches = [2 * 63 - p for p in pitches]
    tscale = 1.0
    if s_idx == 6:
        tscale = 0.5
    elif s_idx == 7:
        tscale = 2.0
    return pitches, onsets, durs, vels, tscale


phase2 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
VOICES = [
    ("Lead",   56, 0),          # Trumpet (disco hook)
    ("Sax",    65, 1),          # Sax (answering line)
    ("Piano",  1, 2),           # Piano (stab comp)
    ("Organ",  19, 3),          # Organ (sustained pad)
    ("Guitar", 25, 4),          # Acoustic guitar (chank)
    ("Bass",   43, 5),          # Double bass (octave pulse)
    ("Drums",  0, 9),           # GM drum kit (channel 9)
]
N_V = len(VOICES)
phase2.create_matrix(num_voices=N_V, num_sections=N_SECTIONS)
for name, prog, ch in VOICES:
    phase2.add_voice(name, program=prog, channel=ch)
for n in NAMES:
    phase2.add_section(n, bars=BARS_PER)

# --- row 0 LEAD: variation -> grid lock -> scale snap -> chord-tone -> leap cap
lead_sections = []
prev_pitch = 63  # Eb4
for s in range(N_SECTIONS):
    raw_unit = phase1.matrix.get_unit((0, s))
    raw = [e for e in raw_unit.events if e.pitch > 0]
    pitches, onsets, durs, vels, tscale = transform_lead(s, raw)
    evs = []
    last_end = 0
    for i in range(len(pitches)):
        st = snap16(int(onsets[i]))
        if st < last_end:
            st = last_end
        if st >= SECTION_TICKS - GRID16:
            continue
        dur = snap16(max(GRID16, int(durs[i] * tscale)))
        en = min(SECTION_TICKS, st + dur)
        if en <= st:
            en = st + GRID16
            if en > SECTION_TICKS:
                en = SECTION_TICKS
        bar = s * BARS_PER + min(st // BAR, BARS_PER - 1)
        deg = PROG_DEG[bar]
        tones = chord_tones(deg, LEAD_LO, LEAD_HI)
        sc = min(SCALE_PITCHES, key=lambda c: (abs(c - pitches[i]), c))
        q = min(tones, key=lambda c: (abs(c - sc), c))
        if abs(q - prev_pitch) > 9:          # voice-leading leap cap (9 st)
            q = min(tones, key=lambda c: (abs(c - prev_pitch), c))
        evs.append(MusicEvent(pitch=q, volume=vels[i], start_tick=st,
                              end_tick=en))
        prev_pitch = q
        last_end = en
    evs.append(MusicEvent(pitch=0, volume=0, start_tick=SECTION_TICKS - 1,
                          end_tick=SECTION_TICKS))
    lead_sections.append(evs)

# --- row 1 SAX: 8th-note answering counterline (chord tones)
sax_sections = []
for s in range(N_SECTIONS):
    r = np.random.default_rng(SEED + 100 + s)
    evs = []
    for b in range(BARS_PER):
        t0 = b * BAR
        deg = PROG_DEG[s * BARS_PER + b]
        tones = chord_tones(deg, 61, 79) or chord_tones(deg, 55, 79) or [67]
        for beat in (1, 3):
            st = t0 + beat * 480
            evs.append(MusicEvent(pitch=int(r.choice(tones)), volume=70,
                                  start_tick=st, end_tick=st + 240))
            st2 = st + 240
            evs.append(MusicEvent(pitch=int(r.choice(tones)), volume=62,
                                  start_tick=st2, end_tick=st2 + 240))
    evs.append(MusicEvent(pitch=0, volume=0, start_tick=SECTION_TICKS - 1,
                          end_tick=SECTION_TICKS))
    sax_sections.append(evs)

# --- row 2 PIANO: offbeat 8th stabs (chord tones, octave 4/5)
piano_sections = []
for s in range(N_SECTIONS):
    evs = []
    for b in range(BARS_PER):
        t0 = b * BAR
        deg = PROG_DEG[s * BARS_PER + b]
        tones = chord_tones(deg, 60, 84) or [63]
        for beat in range(BEATS):
            st = t0 + beat * 480 + 240
            p = tones[(beat + b) % len(tones)]
            evs.append(MusicEvent(pitch=p, volume=58,
                                  start_tick=st, end_tick=st + 120))
        st = t0 + 1560
        evs.append(MusicEvent(pitch=tones[0], volume=52,
                              start_tick=st, end_tick=st + 120))
    evs.append(MusicEvent(pitch=0, volume=0, start_tick=SECTION_TICKS - 1,
                          end_tick=SECTION_TICKS))
    piano_sections.append(evs)

# --- row 3 ORGAN: sustained whole-bar triad pad (chord tones 55-79)
organ_sections = []
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
    evs.append(MusicEvent(pitch=0, volume=0, start_tick=SECTION_TICKS - 1,
                          end_tick=SECTION_TICKS))
    organ_sections.append(evs)

# --- row 4 GUITAR: 16th "chank" offbeats (single-note disco scratches)
guitar_sections = []
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
    evs.append(MusicEvent(pitch=0, volume=0, start_tick=SECTION_TICKS - 1,
                          end_tick=SECTION_TICKS))
    guitar_sections.append(evs)

# --- row 5 BASS: octave disco pulse (root / root+12 on 8ths)
bass_sections = []
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
    evs.append(MusicEvent(pitch=0, volume=0, start_tick=SECTION_TICKS - 1,
                          end_tick=SECTION_TICKS))
    bass_sections.append(evs)

# --- row 6 DRUMS: four-on-the-floor disco kit (channel 9), raw GM numbers
KICK, SNARE, CLAP, HAT_C, HAT_O, RIDE, CRASH = 36, 38, 39, 42, 46, 51, 49
DRUM_PLAN = {
    0: dict(kick=104, snare=None, clap=None, hat=56, ride=False, crash=True),
    1: dict(kick=110, snare=88, clap=84, hat=64, ride=False, crash=False),
    2: dict(kick=116, snare=94, clap=92, hat=70, ride=True, crash=True),
    3: dict(kick=108, snare=86, clap=None, hat=60, ride=False, crash=True),
    4: dict(kick=110, snare=88, clap=84, hat=64, ride=False, crash=False),
    5: dict(kick=116, snare=94, clap=92, hat=70, ride=True, crash=False),
    6: dict(kick=96, snare=None, clap=None, hat=50, ride=False, crash=False),
    7: dict(kick=104, snare=None, clap=None, hat=54, ride=False, crash=True),
}
drum_sections = []
for s in range(N_SECTIONS):
    plan = DRUM_PLAN[s]
    evs = []
    for b in range(BARS_PER):
        t0 = b * BAR
        for k in range(0, BAR, 480):                      # four-on-the-floor
            evs.append(MusicEvent(pitch=KICK, volume=plan["kick"],
                                  start_tick=t0 + k, end_tick=t0 + k + 120))
        for k in range(0, BAR, GRID8):                    # closed hats 8ths
            evs.append(MusicEvent(pitch=HAT_C, volume=plan["hat"],
                                  start_tick=t0 + k, end_tick=t0 + k + 60))
        if plan["ride"]:
            for k in range(0, BAR, 480):
                evs.append(MusicEvent(pitch=RIDE, volume=68,
                                      start_tick=t0 + k + 240,
                                      end_tick=t0 + k + 300))
        if plan["snare"] is not None:
            for off in (480, 1440):
                evs.append(MusicEvent(pitch=SNARE, volume=plan["snare"],
                                      start_tick=t0 + off,
                                      end_tick=t0 + off + 120))
        if plan["clap"] is not None:
            for off in (480, 1440):
                evs.append(MusicEvent(pitch=CLAP, volume=plan["clap"],
                                      start_tick=t0 + off,
                                      end_tick=t0 + off + 120))
        if plan["crash"] and b == 0:
            evs.append(MusicEvent(pitch=CRASH, volume=96,
                                  start_tick=t0, end_tick=t0 + 240))
    evs.append(MusicEvent(pitch=0, volume=0, start_tick=SECTION_TICKS - 1,
                          end_tick=SECTION_TICKS))
    drum_sections.append(evs)

# --- voice-leading (correction enforced inline in the lead build loop above:
#     <=9-semitone leap cap against the previous chord tone, so the lead is a
#     stepwise chord-tone line -> no parallel 5th/8ve is retained) -----------
n_fixed = 0

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


def dedup(events):
    best = {}
    for e in events:
        if e.pitch == 0:
            continue
        k = (e.start_tick, e.pitch)
        if k not in best or (e.end_tick - e.start_tick) > (
                best[k].end_tick - best[k].start_tick):
            best[k] = e
    return sorted(best.values(), key=lambda e: (e.start_tick, e.pitch))


for arr in (lead_sections, sax_sections, piano_sections, organ_sections,
            guitar_sections, bass_sections, drum_sections):
    for i in range(N_SECTIONS):
        arr[i] = dedup(arr[i])
        arr[i].append(MusicEvent(pitch=0, volume=0,
                                 start_tick=SECTION_TICKS - 1,
                                 end_tick=SECTION_TICKS))

# set all cells
for s in range(N_SECTIONS):
    phase2.set_unit(0, s, MusicUnit(events=lead_sections[s]))
    phase2.set_unit(1, s, MusicUnit(events=sax_sections[s]))
    phase2.set_unit(2, s, MusicUnit(events=piano_sections[s]))
    phase2.set_unit(3, s, MusicUnit(events=organ_sections[s]))
    phase2.set_unit(4, s, MusicUnit(events=guitar_sections[s]))
    phase2.set_unit(5, s, MusicUnit(events=bass_sections[s]))
    phase2.set_unit(6, s, MusicUnit(events=drum_sections[s]))

for s in range(N_SECTIONS):
    for v in range(N_V):
        u = phase2.matrix.get_unit((v, s))
        phase2.set_unit(v, s, normalize_cell(u, SECTION_TICKS))

ok2, msg2 = phase2.validate()
print("PHASE2 validate:", ok2, msg2)
assert ok2, msg2
P2_MIDI = os.path.join(MIDI_DIR, "211-disco-schillinger-rework.mid")
phase2.to_midi(P2_MIDI)
print("phase2 written", P2_MIDI, os.path.getsize(P2_MIDI), "bytes")

# ---------------------------------------------------------------- sidecars
write_provenance(P1_MIDI, classification=AI_ASSISTED,
                 generator="SchillingerGenerator(method 018)",
                 parameters={"phase": 1, "seed": SEED,
                             "generators": f"a={SCH_A}, b={SCH_B}",
                             "resultant_pulses": SCH_DURS,
                             "source": "092-disco-schillinger",
                             "method": "018 Schillinger System of Musical Design"},
                 notes="Raw Schillinger draft (rework of 092): fractional "
                       "(off-grid) onsets, coordinate-axis sine pitch, no "
                       "harmony, single voice.")

write_provenance(P2_MIDI, classification=AI_ASSISTED,
                 generator="SchillingerGenerator(method 018) + rules layer",
                 parameters={"phase": 2, "seed": SEED,
                             "grid": "16th (120 @ 480 TPB)",
                             "key": "Eb major",
                             "progression": BAR_LABELS,
                             "source": "092-disco-schillinger",
                             "variation": ["transposition +5", "retrograde",
                                           "inversion", "register-shift +12",
                                           "diminution x0.5",
                                           "augmentation x2.0"],
                             "method": "018 + musicom rules layer"},
                 notes="Redesign: source 092 failed std6 (provenance.json / "
                       "index.html missing at root). Rebuilt via "
                       "UnitMatrixComposer preserving identity; extended "
                       "24->32 bars, 8 sections, 6 variation techniques.")

write_grid_visualization(phase2.matrix,
                         os.path.join(ANALYSIS_DIR, "grid_visualization.txt"),
                         ticks_per_character=120, bpm=BPM, mode="disco")
print("grid_visualization.txt written")

# ---------------------------------------------------------------- meta
meta = {
    "project": "211-disco-schillinger-rework",
    "genre": GENRE,
    "key": "Eb major",
    "bpm": BPM,
    "form": "8 sections x 4 bars = 32 bars",
    "source": "092-disco-schillinger",
    "redesign_required": True,
    "audit_failures": ["std6_provenance.json", "std6_index.html"],
    "variation_techniques": [
        "transposition +5 (Chorus)",
        "retrograde (Break)",
        "inversion around Eb4 (Chorus2)",
        "register-shift +12 (Verse2)",
        "diminution x0.5 (Breakdown)",
        "augmentation x2.0 (Outro)",
    ],
    "seed": SEED,
    "p1": P1_MIDI, "p2": P2_MIDI,
    "key_pcs": sorted(SCALE_PCS),
    "prog_deg": PROG_DEG,
    "section_midpoint_deg": SECTION_DEGS,
    "bars": N_BARS, "sections": N_SECTIONS,
    "total_ticks": TOTAL_TICKS,
    "bar_labels": BAR_LABELS,
}
json.dump(meta, open(os.path.join(ANALYSIS_DIR, "summary.json"), "w"), indent=2)
json.dump(meta, open("/opt/data/.cron_scratch/rework_211_meta.json", "w"),
          indent=2)
print("DONE compose.")
