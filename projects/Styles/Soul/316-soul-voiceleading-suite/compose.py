# -*- coding: utf-8 -*-
"""316-soul-voiceleading-suite — Soul, F natural minor, Method 007 (EXTENSION).

EXTENSION of 229-soul-voiceleading-rework (itself a rework of 078-soul-voiceleading).
Source audit (229): ALL 6 standards PASS -> extension path (no redesign):
  1 Engine UnitMatrixComposer     PASS (compose.py imports UnitMatrixComposer)
  2 Zero-drift                    PASS (6 voice tracks x 61440)
  3 Rhythm-grid sync              PASS (0 off-grid pitched onsets)
  4 Track setup >=4               PASS (6 voice tracks)
  5 Two-phase artifacts           PASS (.mid + -phase1.mid)
  6 provenance.json + index.html  PASS

Identity preserved: Soul, F natural minor, 96 BPM, Method 007 Voice-Leading
Graph Search (TonalNetworkGenerator), arch hook motif, 6-voice texture
(Lead TenorSax / Horns / Rhodes / Violin / Bass / Drums).

Longer form: 32 -> 40 bars (8 -> 10 sections). Two NEW sections:
  PreChorus  (rising build, hook AUGMENTATION = half-time)
  PreChorus2 (rising build, hook DIMINUTION = 16th runs)

Variation techniques (8, > source's 6):
  1 Inversion    - Intro lead = diatonic inversion of hook around F4
  2 Augmentation - PreChorus  hook half-time (480-tick onsets, legato)   [NEW]
  3 Diminution   - PreChorus2 hook 16th runs (120-tick onsets)           [NEW]
  4 Register shift - Verse2 lead = walk +1 octave
  5 Transposition  - Chorus2 hook = diatonic +2 scale steps
  6 Retrograde     - Bridge lead = retrograde hook
  7 Counterline    - rising violin obbligato in PreChorus/PreChorus2      [NEW]
  8 Density curve  - drum/horn density 0.3->1.0->0.3 across 10 sections

Two-phase architecture:
  Phase 1 (-phase1.mid): raw tonal-network graph walk, single voice,
    unquantized chromatic, off-grid onsets, no harmony.
  Phase 2 (dual -perfect/-humanized.mid): rules post-process -> grid snap
    (120/240) -> chord-tone quantization (floor bar attribution) ->
    voice-leading check + octave-fold correction -> full soul texture ->
    humanize (style soul, seeded) via workflows.humanize.export_dual.

Engine only: UnitMatrixComposer + validate() + export_dual()/to_midi().
No raw mido authoring.
"""
import os
import json

import numpy as np

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer, create_empty_unit
from workflows.humanize import export_dual
from workflows.provenance import write_provenance, AI_GENERATED
from visualization.grid import write_grid_visualization
from generators.tonal_network import TonalNetworkGenerator
from rules.voice_leading import VoiceLeadingRules

# instrument registry (not pip-installed -> sanctioned path insert only)
import sys
sys.path.insert(0, "/opt/data/repos/musicom/projects/Instruments")
import instrument_registry as ir  # noqa: E402

SEED = 20261121
HZ_SEED = 316096                 # 316-id + 96-bpm, deterministic
rng = np.random.default_rng(SEED)

PROJ = "/opt/data/projects/Styles/Soul/316-soul-voiceleading-suite"
MIDI_DIR = os.path.join(PROJ, "MIDI")
AUDIO_DIR = os.path.join(PROJ, "Audio")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")
for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
    os.makedirs(d, exist_ok=True)

PROJ_ID = "316-soul-voiceleading-suite"

# ------------------------------------------------------------------ concept
BPM = 96
TPB = 480
BEATS = 4
BAR = TPB * BEATS                    # 1920
GRID = 120                           # 16th-note grid (120); 8th = 240
# F natural minor: F G Ab Bb C Db Eb
KEY_PCS = {5, 7, 8, 10, 0, 1, 3}
SCALE = [53, 55, 56, 58, 60, 61, 63, 65, 67, 68, 70, 72, 73, 75, 77]

# diatonic triads in F natural minor (all pcs in key), keyed by root
CHORDS = {
    53: [53, 56, 60],   # Fm   i
    55: [55, 58, 61],   # Gdim ii (diminished)
    56: [56, 60, 63],   # Ab   III
    58: [58, 61, 65],   # Bbm  iv
    60: [60, 63, 67],   # Cm   v (natural-minor dominant)
    61: [61, 65, 68],   # Db   VI
    63: [63, 67, 70],   # Eb   VII
}
CHORD_NAMES = {53: "i(Fm)", 55: "ii(Gdim)", 56: "III(Ab)", 58: "iv(Bbm)",
               60: "v(Cm)", 61: "VI(Db)", 63: "VII(Eb)"}
BASS = {r: r - 24 for r in CHORDS}   # roots in octave 1-2

# ------------------------------------------------------------------ sections
# 10 sections x 4 bars = 40 bars (source was 8 x 4 = 32)
NAMES = ["Intro", "Verse", "PreChorus", "Chorus", "Verse2",
         "PreChorus2", "Chorus2", "Bridge", "Chorus3", "Outro"]
BARS_PER = 4
N_SECTIONS = len(NAMES)
N_BARS = N_SECTIONS * BARS_PER      # 40
SECTION_TICKS = BAR * BARS_PER      # 7680

# per-section harmonic regions (each section its own short progression)
SEC_PROG = {
    0: [53, 61, 58, 53],   # i  VI iv i
    1: [53, 58, 56, 60],   # i  iv III v
    2: [58, 60, 61, 63],   # iv v  VI VII   (rising lift)
    3: [61, 56, 58, 60],   # VI III iv v    (lift)
    4: [53, 58, 55, 60],   # i  iv ii v
    5: [58, 60, 61, 63],   # iv v  VI VII   (rising lift)
    6: [61, 56, 60, 53],   # VI III v i
    7: [58, 55, 61, 63],   # iv ii VI VII   (dark)
    8: [61, 56, 58, 60],   # VI III iv v    (recap)
    9: [53, 63, 61, 53],   # i  VII VI i    (plagal descent)
}
PROG = [SEC_PROG[s][b] for s in range(N_SECTIONS) for b in range(BARS_PER)]
assert len(PROG) == N_BARS
# section harmonic anchor = midpoint chord (2nd bar) -> avoids bar-0 tonic bug
SEC_ANCHOR = {s: SEC_PROG[s][1] for s in range(N_SECTIONS)}

LEAD_LO, LEAD_HI = 55, 86


def bar_of(section, tick):
    """Absolute bar index from section-relative tick (floor, post-snap)."""
    return section * BARS_PER + (int(tick) // BAR)


def snap(tick, grid=GRID):
    return int(round(tick / grid) * grid)


def quantize_to_chord(pitch, chord_tones):
    """Snap pitch-class to nearest chord tone pc, preserving octave/register."""
    pc = pitch % 12
    cpcs = [c % 12 for c in chord_tones]
    target = min(cpcs, key=lambda c: (min(abs(c - pc), 12 - abs(c - pc)), c))
    octv = pitch // 12
    q = octv * 12 + target
    if abs(q - pitch) > 6:
        q2 = (octv + (1 if target < 6 else -1)) * 12 + target
        if abs(q2 - pitch) < abs(q - pitch):
            q = q2
    return q


def clamp(p, lo, hi):
    return max(lo, min(hi, p))


def fold_register(p, lo, hi):
    """Octave-fold a chord tone into [lo, hi] WITHOUT changing pitch-class."""
    while p < lo:
        p += 12
    while p > hi:
        p -= 12
    return p


# ---------------------------------------------------------------- motif DNA
MOTIF = [65, 68, 72, 68, 65, 63, 60, 63]     # F4 Ab4 C5 Ab4 F4 Eb4 C4 Eb4
SCALE_IDX = {p: i for i, p in enumerate(SCALE)}


def diatonic_invert(notes, axis_pitch=65):
    ai = SCALE_IDX.get(axis_pitch, 7)
    out = []
    for p in notes:
        i = SCALE_IDX.get(p)
        out.append(SCALE[2 * ai - i] if (i is not None and 0 <= 2 * ai - i < len(SCALE)) else p)
    return out


def diatonic_transpose(notes, steps):
    out = []
    for p in notes:
        i = SCALE_IDX.get(p)
        out.append(SCALE[i + steps] if (i is not None and 0 <= i + steps < len(SCALE)) else p)
    return out


# ---------------------------------------------------------------- phase 1
def raw_graph_events(seed, duration_ticks, role_seq, n_events=26):
    r = np.random.default_rng(seed)
    gen = TonalNetworkGenerator(root=53, tonic_quality="minor", seed=seed)
    slot = duration_ticks / n_events          # off-grid by design
    center = 72.0
    events = []
    tick = 0.0
    for role in role_seq:
        tones = gen.node_pitches(role)
        base = float(r.choice(tones))
        p = clamp(base + r.normal(0.0, 1.6), LEAD_LO, LEAD_HI)
        midi = int(round(p))
        dur = int(slot * 0.7)
        vel = int(np.clip(68 + 24 * abs(np.sin(tick / 240.0)), 48, 108))
        st = int(round(tick))
        if st + dur > duration_ticks:
            dur = duration_ticks - st
        if dur > 0:
            events.append(MusicEvent(pitch=midi, volume=vel,
                                     start_tick=st, end_tick=st + dur))
        tick += slot
    return events


ROLE_SEQS = {
    0: ["tonic", "mediant", "tonic", "subdominant"],
    1: ["tonic", "subdominant", "dominant", "tonic"],
    2: ["subdominant", "dominant", "tonic", "dominant"],
    3: ["subdominant", "dominant", "tonic", "dominant"],
    4: ["tonic", "subdominant", "dominant", "tonic"],
    5: ["subdominant", "dominant", "tonic", "dominant"],
    6: ["subdominant", "dominant", "tonic", "dominant"],
    7: ["pre_dominant", "subdominant", "borrow", "pre_dominant"],
    8: ["subdominant", "dominant", "tonic", "dominant"],
    9: ["tonic", "mediant", "subdominant", "tonic"],
}

phase1 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
phase1.create_matrix(num_voices=1, num_sections=N_SECTIONS)
phase1.add_voice("LeadRaw", program=ir.TENOR_SAX.program, channel=0)
for s, name in enumerate(NAMES):
    phase1.add_section(name, bars=BARS_PER)
    seq = [ROLE_SEQS[s][b % 4] for b in range(BARS_PER) for _ in range(6)]
    evs = raw_graph_events(SEED + s, SECTION_TICKS, seq)
    if not any(e.pitch == 0 and e.end_tick == SECTION_TICKS for e in evs):
        evs.append(MusicEvent(pitch=0, volume=0, start_tick=SECTION_TICKS - 1,
                              end_tick=SECTION_TICKS))
    phase1.set_unit(0, s, MusicUnit(events=evs))
ok1, msg1 = phase1.validate()
print("PHASE1 validate:", msg1)
P1_MIDI = os.path.join(MIDI_DIR, PROJ_ID + "-phase1.mid")
phase1.to_midi(P1_MIDI)
print("phase1 written", P1_MIDI)

# ---------------------------------------------------------------- phase 2
VOICES = [
    ("Lead",   ir.TENOR_SAX.program,      0),   # Tenor Sax (66)
    ("Horns",  ir.BRASS_SECTION.program,  1),   # Brass Section (61)
    ("Rhodes", ir.RHODES.program,         2),   # Electric Piano (4)
    ("Violin", ir.VIOLIN.program,         3),   # counterline (40)
    ("Bass",   ir.ELECTRIC_BASS.program,  4),   # Electric Bass (33)
    ("Drums",  ir.DRUM_KIT.program,       9),   # percussion channel
]
N_V = len(VOICES)
phase2 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
phase2.create_matrix(num_voices=N_V, num_sections=N_SECTIONS)
vnames = [v[0] for v in VOICES]
for name, prog, ch in VOICES:
    phase2.add_voice(name, program=prog, channel=ch)
for n in NAMES:
    phase2.add_section(n, bars=BARS_PER)

LEAD_RANGE = {0: (60, 72), 1: (60, 74), 2: (62, 77), 3: (65, 79), 4: (72, 86),
              5: (66, 82), 6: (67, 82), 7: (60, 74), 8: (65, 79), 9: (55, 68)}
SEC_DENS = {0: 0.3, 1: 0.6, 2: 0.75, 3: 1.0, 4: 0.7, 5: 0.85,
            6: 1.0, 7: 0.5, 8: 1.0, 9: 0.3}

CHORUS_SECS = {3, 6, 8}
VERSE_SECS = {1, 4}
PRECHORUS_SECS = {2, 5}


def emit_motif(section, notes, onset_step, dur, vel):
    """Cycle a motif through a section at a fixed onset grid.

    onset_step 480 = augmentation (half-time), 240 = normal, 120 = diminution.
    Every onset is snapped to the 120/240 grid, then chord-quantized per bar.
    """
    lo, hi = LEAD_RANGE[section]
    out = []
    t = 0
    k = 0
    while t < SECTION_TICKS:
        p = notes[k % len(notes)]
        st = snap(t)
        if st >= SECTION_TICKS:
            break
        bar = bar_of(section, st)
        qp = quantize_to_chord(p, CHORDS[PROG[bar]])
        qp = fold_register(qp, lo, hi)
        d = min(dur, SECTION_TICKS - st)
        out.append(MusicEvent(pitch=qp, volume=vel,
                              start_tick=st, end_tick=st + d))
        t += onset_step
        k += 1
    return out


def walk_lead(section, oct_shift=0):
    """Tonal-network walk lead (verse), grid-snapped + chord-quantized."""
    lo, hi = LEAD_RANGE[section]
    raw_unit = phase1.matrix.get_unit((0, section))
    out = []
    for e in raw_unit.events:
        if e.pitch == 0:
            continue
        st = snap(e.start_tick)
        if st >= SECTION_TICKS:
            st = SECTION_TICKS - GRID
        bar = bar_of(section, st)
        tones = CHORDS[PROG[bar]]
        base = int(e.pitch) + oct_shift
        qp = quantize_to_chord(base, tones)
        qp = fold_register(qp, lo, hi)
        dur = max(GRID, min(e.end_tick - e.start_tick, 4 * GRID))
        if st + dur > SECTION_TICKS:
            dur = SECTION_TICKS - st
        out.append(MusicEvent(pitch=qp, volume=e.volume,
                              start_tick=st, end_tick=st + dur))
    return out


def build_lead(section):
    if section in VERSE_SECS:
        return walk_lead(section, oct_shift=12 if section == 4 else 0)
    if section == 0:
        return emit_motif(0, diatonic_invert(MOTIF), 480, 360, 72)   # inversion
    if section == 2:
        return emit_motif(2, MOTIF, 480, 440, 80)                    # augmentation
    if section == 3:
        return emit_motif(3, MOTIF, 240, 220, 96)                    # hook
    if section == 5:
        return emit_motif(5, MOTIF, 120, 100, 88)                    # diminution
    if section == 6:
        return emit_motif(6, diatonic_transpose(MOTIF, 2), 240, 220, 92)  # transposition
    if section == 7:
        return emit_motif(7, MOTIF[::-1], 480, 360, 80)              # retrograde
    if section == 8:
        return emit_motif(8, MOTIF, 240, 220, 96)                    # recap
    if section == 9:
        return emit_motif(9, diatonic_transpose(MOTIF, -2), 240, 200, 72)  # descending
    return []


vlc = VoiceLeadingRules(style="pop")


def correct_voice_leading(events, rng):
    """Octave-fold huge leaps toward the previous note (pc-safe, chord-safe).

    Operates on build-time Python-int events (before the numpy round-trip).
    Also reports the leap>9 flag count."""
    lo, hi = rng
    flags = []
    out = []
    prev = None
    for e in sorted(events, key=lambda x: (x.start_tick, x.pitch)):
        if e.pitch == 0:
            out.append(e)
            continue
        p = int(e.pitch)
        if prev is not None:
            d = p - prev
            if abs(d) > 9:
                flags.append((prev, p, "leap>9"))
            if abs(d) > 12:
                folded = p
                while abs(folded - prev) > 12:
                    folded = folded - 12 if folded > prev else folded + 12
                if lo <= folded <= hi:
                    p = folded
        e.pitch = p
        out.append(e)
        prev = p
    return out, flags


vl_flags = []
for s in range(N_SECTIONS):
    levs, fl = correct_voice_leading(build_lead(s), LEAD_RANGE[s])
    vl_flags.extend((s, a, b, tag) for a, b, tag in fl)
    phase2.set_unit(0, s, MusicUnit(events=levs))
print("VOICE-LEADING flags (lead):", vl_flags[:8], "total", len(vl_flags))

# horns: syncopated stabs, chord tones +12, density by section
for s in range(N_SECTIONS):
    evs = []
    for b in range(BARS_PER):
        bar = s * BARS_PER + b
        tones = CHORDS[PROG[bar]]
        t0 = b * BAR
        if s in CHORUS_SECS:              # 4 stabs, 8th pushes
            for off in (720, 960, 1680, 1800):
                for p in tones:
                    evs.append(MusicEvent(pitch=p + 12, volume=76,
                                          start_tick=t0 + off, end_tick=t0 + off + 120))
        elif s in PRECHORUS_SECS:         # rising build: 3 stabs/bar
            for off in (480, 960, 1440):
                evs.append(MusicEvent(pitch=tones[1] + 12, volume=70,
                                      start_tick=t0 + off, end_tick=t0 + off + 120))
        elif s in VERSE_SECS:             # 2 stabs/bar
            for off in (960, 1680):
                evs.append(MusicEvent(pitch=tones[1] + 12, volume=66,
                                      start_tick=t0 + off, end_tick=t0 + off + 120))
        elif s == 7:                      # bridge: 2 stabs/bar (sparse)
            for off in (960, 1680):
                evs.append(MusicEvent(pitch=tones[2] + 12, volume=60,
                                      start_tick=t0 + off, end_tick=t0 + off + 120))
        # intro/outro: no horns
    phase2.set_unit(1, s, MusicUnit(events=evs))

# rhodes: sustained comp, 3rd + 7th color on quarter grid
for s in range(N_SECTIONS):
    evs = []
    for b in range(BARS_PER):
        bar = s * BARS_PER + b
        tones = CHORDS[PROG[bar]]
        t0 = b * BAR
        third = tones[1] + 12
        seventh = tones[2] + 12
        for k in range(0, BAR, 480):
            if k % 960 == 0:
                evs.append(MusicEvent(pitch=third, volume=58,
                                      start_tick=t0 + k, end_tick=t0 + k + 420))
            else:
                evs.append(MusicEvent(pitch=seventh, volume=52,
                                      start_tick=t0 + k, end_tick=t0 + k + 380))
    phase2.set_unit(2, s, MusicUnit(events=evs))

# violin counterline
VIO_LINE = [72, 68, 70, 75, 72, 68, 70, 65]     # C5 Ab4 Bb4 Eb5 C5 Ab4 Bb4 F4
VIO_RETRO = VIO_LINE[::-1]
VIO_RISE = [65, 68, 70, 72, 75, 77, 80, 77]     # NEW rising obbligato


def violin_section(s):
    evs = []
    for b in range(BARS_PER):
        bar = s * BARS_PER + b
        tones = CHORDS[PROG[bar]]
        t0 = b * BAR
        if s in VERSE_SECS:                    # answer phrase beats 3-4
            for k, p in enumerate(VIO_LINE[4:]):
                qp = quantize_to_chord(p, tones)
                evs.append(MusicEvent(pitch=qp, volume=62,
                                      start_tick=t0 + 960 + k * 240,
                                      end_tick=t0 + 960 + k * 240 + 200))
        elif s in PRECHORUS_SECS:              # NEW rising obbligato
            for k, p in enumerate(VIO_RISE):
                qp = quantize_to_chord(p, tones)
                evs.append(MusicEvent(pitch=qp, volume=64,
                                      start_tick=t0 + k * 240,
                                      end_tick=t0 + k * 240 + 200))
        elif s in CHORUS_SECS:                 # full line
            for k, p in enumerate(VIO_LINE):
                qp = quantize_to_chord(p, tones)
                evs.append(MusicEvent(pitch=qp, volume=68,
                                      start_tick=t0 + k * 240,
                                      end_tick=t0 + k * 240 + 200))
        elif s == 7:                           # retrograde
            for k, p in enumerate(VIO_RETRO):
                qp = quantize_to_chord(p, tones)
                evs.append(MusicEvent(pitch=qp, volume=64,
                                      start_tick=t0 + k * 240,
                                      end_tick=t0 + k * 240 + 200))
        elif s == 0:                           # sparse 1 note/bar
            qp = quantize_to_chord(72, tones)
            evs.append(MusicEvent(pitch=qp, volume=56,
                                  start_tick=t0 + 960, end_tick=t0 + 1200))
        elif s == 9:                           # descending outro
            qp = quantize_to_chord([75, 72, 68, 65][b], tones)
            evs.append(MusicEvent(pitch=qp, volume=56,
                                  start_tick=t0 + 960, end_tick=t0 + 1200))
    return evs


for s in range(N_SECTIONS):
    phase2.set_unit(3, s, MusicUnit(events=violin_section(s)))

# bass: root on 1&3, chord fifth on 2&4, chorus 16th push
for s in range(N_SECTIONS):
    evs = []
    for b in range(BARS_PER):
        bar = s * BARS_PER + b
        root = BASS[PROG[bar]]
        fifth = CHORDS[PROG[bar]][2] - 24
        t0 = b * BAR
        evs += [
            MusicEvent(pitch=root, volume=100, start_tick=t0, end_tick=t0 + 360),
            MusicEvent(pitch=fifth, volume=88, start_tick=t0 + 480, end_tick=t0 + 840),
            MusicEvent(pitch=root, volume=100, start_tick=t0 + 960, end_tick=t0 + 1320),
            MusicEvent(pitch=fifth, volume=88, start_tick=t0 + 1440, end_tick=t0 + 1800),
        ]
        if s in CHORUS_SECS:
            evs.append(MusicEvent(pitch=root, volume=92, start_tick=t0 + 1800,
                                  end_tick=t0 + BAR - 10))
    phase2.set_unit(4, s, MusicUnit(events=evs))

# drums: backbeat soul, density curve per section
from Percussion.drum_kit.drum_kit import KIT, VELOCITIES  # noqa: E402
K, V = KIT, VELOCITIES
for s in range(N_SECTIONS):
    dens = SEC_DENS[s]
    evs = []
    for b in range(BARS_PER):
        t0 = b * BAR
        if dens <= 0.01:
            continue
        for k in range(0, BAR, 240):          # closed hat 8ths
            evs.append(MusicEvent(pitch=K["hat_closed"], volume=V["hat_closed"],
                                  start_tick=t0 + k, end_tick=t0 + k + 90))
        evs.append(MusicEvent(pitch=K["kick"], volume=V["kick"],
                              start_tick=t0, end_tick=t0 + 160))
        evs.append(MusicEvent(pitch=K["kick"], volume=V["kick"] - 4,
                              start_tick=t0 + 960, end_tick=t0 + 1120))
        if dens >= 0.6:
            evs.append(MusicEvent(pitch=K["snare"], volume=V["snare"],
                                  start_tick=t0 + 480, end_tick=t0 + 620))
            evs.append(MusicEvent(pitch=K["snare"], volume=V["snare"] + 4,
                                  start_tick=t0 + 1440, end_tick=t0 + 1580))
        if dens >= 1.0:
            evs.append(MusicEvent(pitch=K["clap"], volume=V["clap"],
                                  start_tick=t0 + 480, end_tick=t0 + 600))
            evs.append(MusicEvent(pitch=K["clap"], volume=V["clap"] + 4,
                                  start_tick=t0 + 1440, end_tick=t0 + 1560))
            evs.append(MusicEvent(pitch=K["ride"], volume=V["ride"],
                                  start_tick=t0, end_tick=t0 + 600))
    phase2.set_unit(5, s, MusicUnit(events=evs))

# (voice-leading check + octave-fold correction now happens at build time above)


# normalize every cell: dedup (start,pitch)->longest, clamp, landmark, sort
def finalize_cell(events, total_ticks):
    d = {}
    for e in events:
        if e.end_tick > total_ticks:
            e.end_tick = total_ticks
        if e.start_tick >= total_ticks:
            e.start_tick = total_ticks - GRID
        if e.start_tick < 0:
            e.start_tick = 0
        if e.end_tick <= e.start_tick:
            e.end_tick = min(total_ticks, e.start_tick + GRID)
        key = (e.start_tick, e.pitch)
        if key not in d or e.end_tick - e.start_tick > d[key].end_tick - d[key].start_tick:
            d[key] = e
    evs = list(d.values())
    evs.sort(key=lambda e: (e.start_tick, e.pitch))
    if not any(e.pitch == 0 and e.end_tick == total_ticks for e in evs):
        evs.append(MusicEvent(pitch=0, volume=0, start_tick=total_ticks - 1,
                              end_tick=total_ticks))
    return MusicUnit(events=evs)


for v in range(N_V):
    for s in range(N_SECTIONS):
        u = phase2.matrix.get_unit((v, s))
        evs = list(u.events) if u is not None else []
        if not evs:
            phase2.set_unit(v, s, create_empty_unit(SECTION_TICKS))
        else:
            phase2.set_unit(v, s, finalize_cell(evs, SECTION_TICKS))

ok2, msg2 = phase2.validate()
print("PHASE2 validate (pre-export):", msg2)
assert ok1 and ok2, (msg1, msg2)

# ---------------------------------------------------------------- dual export
hz_instruments = {
    "Lead":   ir.TENOR_SAX.humanize_dna,      # (None, 7.0, None, 0.02)
    "Horns":  ir.BRASS_SECTION.humanize_dna,  # (None, 8.0, None, 0.02)
    "Rhodes": ir.RHODES.humanize_dna,         # (None, 5.0, None, 0.015)
    "Violin": ir.VIOLIN.humanize_dna,         # (None, 6.0, None, 0.03)
    "Bass":   ir.ELECTRIC_BASS.humanize_dna,  # (5.0, 4.0, 8.0, 0.01)
    "Drums":  ir.DRUM_KIT.humanize_dna,       # (2.0, 4.0, 0.0, 0.008)
}
P_PERFECT = os.path.join(MIDI_DIR, PROJ_ID + "-perfect.mid")
P_HUMAN = os.path.join(MIDI_DIR, PROJ_ID + "-humanized.mid")
hz = export_dual(phase2, P_PERFECT, P_HUMAN,
                 style="soul", seed=HZ_SEED, bpm=BPM, instruments=hz_instruments)
print("dual export done. humanize summary:", json.dumps(hz, default=str)[:400])

# ---------------------------------------------------------------- sidecars
grid_path = os.path.join(ANALYSIS_DIR, "grid_visualization.txt")
write_grid_visualization(phase2.matrix, grid_path, ticks_per_character=120,
                         voice_names=vnames, bpm=BPM,
                         mode="F minor / 007 voice-leading graph soul (extension)")
print("grid written", grid_path)

for mid, phase, note in (
        (P1_MIDI, "1", "raw tonal-network graph walk, unquantized chromatic, off-grid, single voice, no harmony"),
        (P_PERFECT, "2", "grid-snapped + chord-tone quantized (floor bar attribution) + voice-leading check + full soul texture (PERFECT, no humanization)"),
        (P_HUMAN, "2-humanized", "phase-2 concrete layer humanized via workflows.humanize (style=soul, seeded)")):
    write_provenance(mid, AI_GENERATED,
                     "Voice-Leading Graph Search (Method 007, TonalNetworkGenerator) + musicom rules + humanize",
                     parameters={"bpm": BPM, "key": "F natural minor",
                                 "sections": N_SECTIONS, "bars": N_BARS,
                                 "phase": phase,
                                 "progression": [CHORD_NAMES[r] for r in PROG],
                                 "seed": SEED, "humanize_seed": HZ_SEED,
                                 "humanize_style": "soul",
                                 "extension_of": "229-soul-voiceleading-rework",
                                 "rework_of": "078-soul-voiceleading"},
                     notes=note)
    print("provenance phase", phase)

with open(os.path.join(PROJ, "provenance.json"), "w") as f:
    json.dump({"project": PROJ_ID, "style": "Soul",
               "method": "007 Voice-Leading Graph Search (extension)",
               "bpm": BPM, "key": "F natural minor", "bars": N_BARS,
               "sections": {n: BARS_PER for n in NAMES},
               "progression": [CHORD_NAMES[r] for r in PROG],
               "section_anchors": {NAMES[s]: CHORD_NAMES[SEC_ANCHOR[s]] for s in range(N_SECTIONS)},
               "voices": vnames,
               "phase1": os.path.basename(P1_MIDI),
               "phase2_perfect": os.path.basename(P_PERFECT),
               "phase2_humanized": os.path.basename(P_HUMAN),
               "seed": SEED, "humanize_seed": HZ_SEED,
               "humanize_summary": hz,
               "variation_techniques": [
                   "inversion", "augmentation", "diminution", "register-shift",
                   "transposition", "retrograde", "counterline", "density-curve"],
               "extension_of": "229-soul-voiceleading-rework",
               "rework_of": "078-soul-voiceleading"}, f, indent=2, default=str)

with open(os.path.join(ANALYSIS_DIR, "summary.json"), "w") as f:
    json.dump({"project": PROJ_ID, "style": "Soul",
               "bpm": BPM, "key": "F natural minor", "bars": N_BARS,
               "sections": {n: BARS_PER for n in NAMES},
               "progression": [CHORD_NAMES[r] for r in PROG],
               "section_anchors": {NAMES[s]: CHORD_NAMES[SEC_ANCHOR[s]] for s in range(N_SECTIONS)},
               "voices": vnames,
               "phase1": os.path.basename(P1_MIDI),
               "phase2_perfect": os.path.basename(P_PERFECT),
               "phase2_humanized": os.path.basename(P_HUMAN),
               "humanize_seed": HZ_SEED, "humanize_summary": hz,
               "grid": "grid_visualization.txt", "seed": SEED}, f, indent=2, default=str)

for p in (P1_MIDI, P_PERFECT, P_HUMAN, grid_path,
          os.path.join(PROJ, "provenance.json"),
          os.path.join(ANALYSIS_DIR, "summary.json")):
    assert os.path.getsize(p) > 40, "too small: %s" % p
print("ALL SIZE ASSERTS PASSED")
print("PROGRESSION:", [CHORD_NAMES[r] for r in PROG])
print("ANCHORS:", [CHORD_NAMES[SEC_ANCHOR[s]] for s in range(N_SECTIONS)])
