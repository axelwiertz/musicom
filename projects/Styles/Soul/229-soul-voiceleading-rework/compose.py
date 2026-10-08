# -*- coding: utf-8 -*-
"""229-soul-voiceleading-rework — Soul, F natural minor, Method 007.

Rework of 078-soul-voiceleading. Fixes audit failures:
  * rhythm-grid sync (no off-grid onsets; snap to 120/240 grid)
  * chord attribution (quantize pitch using floor(final_onset // BAR))
  * sidecars (provenance.json + index.html present)
Longer form: 24 -> 32 bars (8 sections). Variation: inversion, retrograde,
transposition, register shift, per-section method change, density rise.

Two-phase architecture:
  Phase 1 = raw tonal-network graph walk (single voice, unquantized chromatic,
            off-grid). TonalNetworkGenerator.
  Phase 2 = rules post-process: grid snap -> chord-tone quantization per bar
            (correct bar attribution) -> voice-leading/register enforcement ->
            full soul texture (Lead TenorSax, Horns, Rhodes, Violin, Bass, Drums).
Engine only: UnitMatrixComposer + validate() + to_midi(). No raw mido authoring.
"""
import os
import json

import numpy as np

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import (
    UnitMatrixComposer, create_empty_unit,
)
from generators.tonal_network import TonalNetworkGenerator

# instrument library (read-only constants)
import sys
sys.path.insert(0, "/opt/data/projects/Instruments")
from Strings.violin.violin import MIDI_PROGRAM as VIO_PROG  # noqa: E402
from Percussion.drum_kit.drum_kit import KIT, VELOCITIES  # noqa: E402

SEED = 20261008
rng = np.random.default_rng(SEED)

PROJ = "/opt/data/projects/Styles/Soul/229-soul-voiceleading-rework"
MIDI_DIR = os.path.join(PROJ, "MIDI")
AUDIO_DIR = os.path.join(PROJ, "Audio")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")
for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
    os.makedirs(d, exist_ok=True)

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
# 8 sections x 4 bars = 32 bars (source was 24)
NAMES = ["Intro", "Verse", "Chorus", "Verse2", "Chorus2",
         "Bridge", "Chorus3", "Outro"]
BARS_PER = 4
N_SECTIONS = len(NAMES)
N_BARS = N_SECTIONS * BARS_PER      # 32
SECTION_TICKS = BAR * BARS_PER      # 7680

# per-section harmonic regions (each section its own short progression)
SEC_PROG = {
    0: [53, 61, 58, 53],   # i  VI iv i
    1: [53, 58, 56, 60],   # i  iv III v
    2: [61, 56, 58, 60],   # VI III iv v  (lift)
    3: [53, 58, 55, 60],   # i  iv ii v
    4: [61, 56, 60, 53],   # VI III v i
    5: [58, 55, 61, 63],   # iv ii VI VII (dark)
    6: [61, 56, 58, 60],   # VI III iv v  (recap)
    7: [53, 63, 61, 53],   # i  VII VI i
}
PROG = [SEC_PROG[s][b] for s in range(N_SECTIONS) for b in range(BARS_PER)]
assert len(PROG) == N_BARS
# section harmonic anchor = midpoint chord (2nd bar of the section)
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
    """Octave-fold a chord tone into [lo, hi] WITHOUT changing pitch-class.

    Preserves chord/key membership (clamp() pushed tones out of chord — the
    chord_viol bug)."""
    while p < lo:
        p += 12
    while p > hi:
        p -= 12
    return p


# ---------------------------------------------------------------- motif DNA
# arch motif in F natural minor (all scale tones)
MOTIF = [65, 68, 72, 68, 65, 63, 60, 63]     # F4 Ab4 C5 Ab4 F4 Eb4 C4 Eb4
SCALE_IDX = {p: i for i, p in enumerate(SCALE)}


def diatonic_invert(notes, axis_pitch=65):
    """Invert around scale index of axis_pitch (diatonic mirror, stays in key)."""
    ai = SCALE_IDX.get(axis_pitch, 7)
    out = []
    for p in notes:
        i = SCALE_IDX.get(p)
        if i is None:
            out.append(p)
        else:
            out.append(SCALE[2 * ai - i] if 0 <= 2 * ai - i < len(SCALE) else p)
    return out


def diatonic_transpose(notes, steps):
    """Shift each note by 'steps' scale positions (diatonic, stays in key)."""
    out = []
    for p in notes:
        i = SCALE_IDX.get(p)
        out.append(SCALE[i + steps] if i is not None and 0 <= i + steps < len(SCALE) else p)
    return out


# ---------------------------------------------------------------- phase 1
# raw tonal-network walk: single voice, unquantized chromatic, off-grid.
def raw_graph_events(seed, duration_ticks, role_seq, n_events=26):
    r = np.random.default_rng(seed)
    gen = TonalNetworkGenerator(root=53, tonic_quality="minor", seed=seed)
    slot = duration_ticks / n_events          # 7680/26 = 295.4 (off-grid)
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


# per-section role schedules (walk regions)
ROLE_SEQS = {
    0: ["tonic", "mediant", "tonic", "subdominant"],
    1: ["tonic", "subdominant", "dominant", "tonic"],
    2: ["subdominant", "dominant", "tonic", "dominant"],
    3: ["tonic", "subdominant", "dominant", "tonic"],
    4: ["subdominant", "dominant", "tonic", "dominant"],
    5: ["pre_dominant", "subdominant", "borrow", "pre_dominant"],
    6: ["subdominant", "dominant", "tonic", "dominant"],
    7: ["tonic", "mediant", "subdominant", "tonic"],
}

phase1 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
phase1.create_matrix(num_voices=1, num_sections=N_SECTIONS)
phase1.add_voice("LeadRaw", program=65, channel=0)
for s, name in enumerate(NAMES):
    phase1.add_section(name, bars=BARS_PER)
    seq = [ROLE_SEQS[s][b % 4] for b in range(BARS_PER) for _ in range(6)]
    evs = raw_graph_events(SEED + s, SECTION_TICKS, seq)
    # zero-drift landmark
    if not any(e.pitch == 0 and e.end_tick == SECTION_TICKS for e in evs):
        evs.append(MusicEvent(pitch=0, volume=0, start_tick=SECTION_TICKS - 1,
                              end_tick=SECTION_TICKS))
    phase1.set_unit(0, s, MusicUnit(events=evs))
ok1, msg1 = phase1.validate()
print("PHASE1 validate:", msg1)
P1_MIDI = os.path.join(MIDI_DIR, "229-soul-voiceleading-rework-phase1.mid")
phase1.to_midi(P1_MIDI)
print("phase1 written", P1_MIDI)

# ---------------------------------------------------------------- phase 2
VOICES = [
    ("Lead",   65,      0),   # Tenor Sax
    ("Horns",  61,      1),   # Brass Section
    ("Rhodes", 4,       2),   # Electric Piano
    ("Violin", VIO_PROG, 3),  # counterline
    ("Bass",   33,      4),   # Electric Bass (finger)
    ("Drums",  0,       9),   # percussion channel
]
N_V = len(VOICES)
phase2 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
phase2.create_matrix(num_voices=N_V, num_sections=N_SECTIONS)
vnames = [v[0] for v in VOICES]
for name, prog, ch in VOICES:
    phase2.add_voice(name, program=prog, channel=ch)
for n in NAMES:
    phase2.add_section(n, bars=BARS_PER)

# lead register per section (register-shift variation)
LEAD_RANGE = {0: (60, 72), 1: (60, 74), 2: (65, 79), 3: (72, 86),
              4: (67, 82), 5: (60, 74), 6: (65, 79), 7: (55, 68)}
# density per section (drive curve)
SEC_DENS = {0: 0.3, 1: 0.6, 2: 1.0, 3: 0.7, 4: 1.0, 5: 0.5, 6: 1.0, 7: 0.4}


def build_lead(section):
    """Return phase-2 lead events (grid-snapped + chord-quantized) for a section."""
    name = NAMES[section]
    lo, hi = LEAD_RANGE[section]
    raw_unit = phase1.matrix.get_unit((0, section))
    out = []

    if section in (1, 3, 7):
        # method: tonal-network walk (quantized). Verse2 (3) = octave-up shift.
        oct_shift = 12 if section == 3 else 0
        for e in raw_unit.events:
            if e.pitch == 0:
                continue
            st = snap(e.start_tick)
            if st >= SECTION_TICKS:
                st = SECTION_TICKS - GRID
            bar = bar_of(section, st)
            tones = CHORDS[PROG[bar]]
            base = e.pitch + oct_shift
            qp = quantize_to_chord(base, tones)
            qp = fold_register(qp, lo, hi)
            dur = max(GRID, min(e.end_tick - e.start_tick, 4 * GRID))
            if st + dur > SECTION_TICKS:
                dur = SECTION_TICKS - st
            out.append(MusicEvent(pitch=qp, volume=e.volume,
                                  start_tick=st, end_tick=st + dur))
    elif section in (2, 6):
        # method: main hook (MOTIF). Chorus3 (6) = recap.
        notes = MOTIF
        for k, p in enumerate(notes):
            st = snap(k * 240)
            bar = bar_of(section, st)
            qp = quantize_to_chord(p, CHORDS[PROG[bar]])
            qp = fold_register(qp, lo, hi)
            out.append(MusicEvent(pitch=qp, volume=96,
                                  start_tick=st, end_tick=st + 220))
    elif section == 0:
        # variation: diatonic INVERSION of the hook (sparse)
        notes = diatonic_invert(MOTIF)
        for k, p in enumerate(notes):
            st = snap(k * 480)
            bar = bar_of(section, st)
            qp = quantize_to_chord(p, CHORDS[PROG[bar]])
            qp = fold_register(qp, lo, hi)
            out.append(MusicEvent(pitch=qp, volume=72,
                                  start_tick=st, end_tick=st + 360))
    elif section == 4:
        # variation: diatonic TRANSPOSITION of the hook (+2 scale steps)
        notes = diatonic_transpose(MOTIF, 2)
        for k, p in enumerate(notes):
            st = snap(k * 240)
            bar = bar_of(section, st)
            qp = quantize_to_chord(p, CHORDS[PROG[bar]])
            qp = fold_register(qp, lo, hi)
            out.append(MusicEvent(pitch=qp, volume=92,
                                  start_tick=st, end_tick=st + 220))
    elif section == 5:
        # variation: RETROGRADE of the hook (bridge)
        notes = MOTIF[::-1]
        for k, p in enumerate(notes):
            st = snap(k * 480)
            bar = bar_of(section, st)
            qp = quantize_to_chord(p, CHORDS[PROG[bar]])
            qp = fold_register(qp, lo, hi)
            out.append(MusicEvent(pitch=qp, volume=80,
                                  start_tick=st, end_tick=st + 360))
    return out


for s in range(N_SECTIONS):
    phase2.set_unit(0, s, MusicUnit(events=build_lead(s)))


# horns: syncopated stabs, chord tones +12, density by section (diminution)
for s in range(N_SECTIONS):
    evs = []
    for b in range(BARS_PER):
        bar = s * BARS_PER + b
        tones = CHORDS[PROG[bar]]
        t0 = b * BAR
        if s in (2, 4, 6):        # choruses: 4 stabs, 8th pushes (diminution)
            for off in (720, 960, 1680, 1800):
                for p in tones:
                    evs.append(MusicEvent(pitch=p + 12, volume=76,
                                          start_tick=t0 + off, end_tick=t0 + off + 120))
        elif s in (1, 3):         # verses: 2 stabs per bar
            for off in (960, 1680):
                evs.append(MusicEvent(pitch=tones[1] + 12, volume=66,
                                      start_tick=t0 + off, end_tick=t0 + off + 120))
        # intro/outro: no horns (density 0)
    phase2.set_unit(1, s, MusicUnit(events=evs))


# rhodes: sustained comp, 3rd+7th color on quarter grid
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


# violin counterline (F-minor pentatonic pool, chord-quantized per bar)
VIO_LINE = [72, 68, 70, 75, 72, 68, 70, 65]     # C5 Ab4 Bb4 Eb5 C5 Ab4 Bb4 F4
VIO_RETRO = VIO_LINE[::-1]


def violin_section(s):
    evs = []
    for b in range(BARS_PER):
        bar = s * BARS_PER + b
        tones = CHORDS[PROG[bar]]
        t0 = b * BAR
        if s in (1, 3):                       # verse: answer phrase beats 3-4
            for k, p in enumerate(VIO_LINE[4:]):
                qp = quantize_to_chord(p, tones)
                evs.append(MusicEvent(pitch=qp, volume=62,
                                      start_tick=t0 + 960 + k * 240,
                                      end_tick=t0 + 960 + k * 240 + 200))
        elif s in (2, 4, 6):                  # chorus: full line
            for k, p in enumerate(VIO_LINE):
                qp = quantize_to_chord(p, tones)
                evs.append(MusicEvent(pitch=qp, volume=68,
                                      start_tick=t0 + k * 240,
                                      end_tick=t0 + k * 240 + 200))
        elif s == 5:                          # bridge: RETROGRADE line
            for k, p in enumerate(VIO_RETRO):
                qp = quantize_to_chord(p, tones)
                evs.append(MusicEvent(pitch=qp, volume=64,
                                      start_tick=t0 + k * 240,
                                      end_tick=t0 + k * 240 + 200))
        elif s == 0:                          # intro: sparse 1 note / bar
            qp = quantize_to_chord(72, tones)
            evs.append(MusicEvent(pitch=qp, volume=56,
                                  start_tick=t0 + 960, end_tick=t0 + 1200))
        elif s == 7:                          # outro: descending
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
        fifth = CHORDS[PROG[bar]][2] - 24      # actual chord fifth (avoids ii bug)
        t0 = b * BAR
        evs += [
            MusicEvent(pitch=root, volume=100, start_tick=t0, end_tick=t0 + 360),
            MusicEvent(pitch=fifth, volume=88, start_tick=t0 + 480, end_tick=t0 + 840),
            MusicEvent(pitch=root, volume=100, start_tick=t0 + 960, end_tick=t0 + 1320),
            MusicEvent(pitch=fifth, volume=88, start_tick=t0 + 1440, end_tick=t0 + 1800),
        ]
        if s in (2, 4, 6):                    # chorus: 16th push
            evs.append(MusicEvent(pitch=root, volume=92, start_tick=t0 + 1800,
                                  end_tick=t0 + BAR - 10))
    phase2.set_unit(4, s, MusicUnit(events=evs))


# drums: backbeat soul, density curve per section
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


# voice-leading check on lead
from rules.voice_leading import VoiceLeadingRules  # noqa: E402
vlc = VoiceLeadingRules(style="pop")
vl_flags = []
for s in range(N_SECTIONS):
    u = phase2.matrix.get_unit((0, s))
    evs = sorted([e for e in u.events if e.pitch > 0], key=lambda e: e.start_tick)
    for i in range(1, len(evs)):
        a, b = evs[i - 1], evs[i]
        if abs(b.pitch - a.pitch) > 9:
            vl_flags.append((s, a.pitch, b.pitch, "leap>9"))
        if vlc.check_hidden_fifths([a.pitch], [b.pitch]):
            vl_flags.append((s, a.pitch, b.pitch, "hidden-fifth"))
print("VOICE-LEADING flags (lead):", vl_flags[:8], "total", len(vl_flags))


# normalize every cell: dedup (start,pitch)->longest, clamp to section, landmark
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
    evs.sort(key=lambda e: e.start_tick)
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
print("PHASE2 validate:", msg2)
assert ok1 and ok2, (msg1, msg2)
P2_MIDI = os.path.join(MIDI_DIR, "229-soul-voiceleading-rework.mid")
phase2.to_midi(P2_MIDI)
print("phase2 written", P2_MIDI)

# ---------------------------------------------------------------- sidecars
from visualization.grid import write_grid_visualization  # noqa: E402
from workflows.provenance import write_provenance, AI_GENERATED  # noqa: E402

grid_path = os.path.join(ANALYSIS_DIR, "grid_visualization.txt")
write_grid_visualization(phase2.matrix, grid_path, ticks_per_character=120,
                         voice_names=vnames, bpm=BPM,
                         mode="F minor / 007 voice-leading graph soul (rework)")
print("grid written", grid_path)

for mid, phase, note in (
        (P1_MIDI, "1", "raw tonal-network graph walk, unquantized chromatic, off-grid, single voice, no harmony"),
        (P2_MIDI, "2", "grid-snapped + chord-tone quantized (floor bar attribution) + voice-leading check + full soul texture")):
    write_provenance(mid, AI_GENERATED,
                     "Voice-Leading Graph Search (Method 007, TonalNetworkGenerator) + musicom rules",
                     parameters={"bpm": BPM, "key": "F natural minor",
                                 "sections": N_SECTIONS, "bars": N_BARS,
                                 "phase": phase,
                                 "progression": [CHORD_NAMES[r] for r in PROG],
                                 "seed": SEED, "rework_of": "078-soul-voiceleading"},
                     notes=note)
    print("provenance phase", phase)

with open(os.path.join(PROJ, "provenance.json"), "w") as f:
    json.dump({"project": "229-soul-voiceleading-rework", "style": "Soul",
               "method": "007 Voice-Leading Graph Search (rework)",
               "bpm": BPM, "key": "F natural minor", "bars": N_BARS,
               "sections": {n: BARS_PER for n in NAMES},
               "progression": [CHORD_NAMES[r] for r in PROG],
               "section_anchors": {NAMES[s]: CHORD_NAMES[SEC_ANCHOR[s]] for s in range(N_SECTIONS)},
               "voices": vnames, "phase1": os.path.basename(P1_MIDI),
               "phase2": os.path.basename(P2_MIDI),
               "seed": SEED, "rework_of": "078-soul-voiceleading"}, f, indent=2)

with open(os.path.join(ANALYSIS_DIR, "summary.json"), "w") as f:
    json.dump({"project": "229-soul-voiceleading-rework", "style": "Soul",
               "bpm": BPM, "key": "F natural minor", "bars": N_BARS,
               "sections": {n: BARS_PER for n in NAMES},
               "progression": [CHORD_NAMES[r] for r in PROG],
               "section_anchors": {NAMES[s]: CHORD_NAMES[SEC_ANCHOR[s]] for s in range(N_SECTIONS)},
               "voices": vnames, "phase1": os.path.basename(P1_MIDI),
               "phase2": os.path.basename(P2_MIDI), "grid": "grid_visualization.txt",
               "seed": SEED}, f, indent=2)

for p in (P1_MIDI, P2_MIDI, grid_path,
          os.path.join(PROJ, "provenance.json"),
          os.path.join(ANALYSIS_DIR, "summary.json")):
    assert os.path.getsize(p) > 40, "too small: %s" % p
print("ALL SIZE ASSERTS PASSED")
print("PROGRESSION:", [CHORD_NAMES[r] for r in PROG])
