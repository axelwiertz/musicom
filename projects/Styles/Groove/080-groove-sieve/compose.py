# -*- coding: utf-8 -*-
"""080-groove-sieve - Groove style / Method 025 Xenakis Sieve Theory.

Two-phase composition:
  Phase 1: raw sieve walk - a single-voice melodic draft whose pitches come
           from a Xenakis sieve (union/intersection of arithmetic
           progressions) realized as a sequence of sieve-selected pitch-class
           offsets from a center, unquantized (raw floats rounded, onsets at
           non-grid-fractional ticks), no chord-tone quantization, no harmony.
           The sieve's residual structure (periodic selection, modular
           filtering) is the "generative method" voice.
  Phase 2: musicom rules post-process - rhythm locked to the 8th grid
           (240 ticks @ 110 BPM), chord-tone quantization per bar to a
           G-minor groove progression (i III iv V / i iv V i ...), voice
           leading checks via rules.voice_leading, full groove texture:
           lead (soprano sax) + horns (sieve-stab accents) + Rhodes comp
           + electric bass (octave pulse + 16th push) + drums (kick 1&3,
           snare 2&4, hats 8ths, chorus claps + ride).

Engine only: structures + workflows.unitmatrix_composer + rules.voice_leading.
validate() gate + to_midi(). No raw mido authoring.
"""
import os
import json
import sys

import numpy as np

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import (
    UnitMatrixComposer, create_empty_unit,
)

# instrument library constants (read-only)
sys.path.insert(0, "/opt/data/projects/Instruments")
from Brass.trumpet.trumpet import MIDI_PROGRAM as TRUMPET_PROG  # noqa: E402
from Percussion.drum_kit.drum_kit import KIT, VELOCITIES  # noqa: E402

SEED = 20260828
rng = np.random.default_rng(SEED)

# ---------------------------------------------------------------- project dirs
PROJ = "/opt/data/projects/Styles/Groove/080-groove-sieve"
MIDI_DIR = os.path.join(PROJ, "MIDI")
AUDIO_DIR = os.path.join(PROJ, "Audio")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")
for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
    os.makedirs(d, exist_ok=True)

# ---------------------------------------------------------------- concept
BPM = 110
TPB = 480
BEATS = 4
BAR = TPB * BEATS            # 1920
# G natural minor (groove tonal palette), 8th grid = 240 @ 110 BPM
SCALE = [55, 57, 58, 60, 62, 63, 65, 67, 69, 70, 72, 74, 75, 77, 79, 81]
LEAD_LO, LEAD_HI = 57, 84

# diatonic triads in G natural minor, keyed by root MIDI
CHORDS = {
    55: [55, 58, 62],   # Gm  i
    58: [58, 62, 65],   # Bb  III
    60: [60, 63, 67],   # Cm  iv
    62: [62, 65, 69],   # D   V (major - harmonic lift)
    63: [63, 67, 70],   # Eb  VI
}
ROOTS = [55, 58, 60, 62, 63]
BASS = {55: 31, 58: 34, 60: 36, 62: 38, 63: 39}   # octave 2 (G1-Bb1-C2-D2-Eb2)

# ---------------------------------------------------------------- sections
NAMES = ["Intro", "Verse", "Chorus", "Verse2", "Chorus2", "Outro"]
BARS_PER = 4
N_SECTIONS = len(NAMES)
N_BARS = N_SECTIONS * BARS_PER            # 24 bars
SECTION_TICKS = BAR * BARS_PER            # 7680

# 24-bar groove progression (G minor): i III iv V | i III iv V |
#   i iv V i | i V i VI | i III iv V | i V iv i
PROG = ([55, 58, 60, 62] * 2) + [55, 60, 62, 55] + [55, 62, 55, 63] + \
       [55, 58, 60, 62] + [55, 62, 60, 55]
assert len(PROG) == N_BARS, (len(PROG), N_BARS)
CHORD_NAMES = {55: "i", 58: "III", 60: "iv", 62: "V", 63: "VI"}


def chord_for_bar(bar):
    return CHORDS[PROG[bar]]


def quantize_to_chord(pitch, chord_tones):
    """Snap a pitch to nearest chord tone, resolving ties toward lower."""
    return min(chord_tones, key=lambda c: (abs(c - pitch), c))


# ---------------------------------------------------------------- sieve core
# Xenakis sieve: logical combination of arithmetic progressions (residual
# classes modulo a modulus). A sieve S = { n : (n mod m) in R } for some
# modulus m and allowed-residue set R. Union/intersection of several such
# progressions yields periodic "filtered" pitch-class universes.
#
# We build two nested sieves and intersect them:
#   A: modulus 8, residues {0,2,5}  (diatonic-ish skeleton: 3 of 8)
#   B: modulus 7, residues {0,1,4}  (asymmetry -> groove syncopation)
# C = A ∩ B is periodic with period lcm(8,7)=56; its members are the raw
# pitch-class offsets (in semitones) admitted by the sieve. This is the
# "tone row" of the method: strictly periodic, modularly filtered, exactly
# reproducible, and NOT a scale pattern (it contains chromatic gaps and
# repeated classes at octave displacement).

SIEVE_A_MOD, SIEVE_A_RES = 8, (0, 2, 5)
SIEVE_B_MOD, SIEVE_B_RES = 7, (0, 1, 4)


def sieve_offsets(lo=0, hi=56):
    """All n in [lo, hi) admitted by sieve C = A ∩ B (raw semitone offsets)."""
    out = []
    for n in range(lo, hi):
        if (n % SIEVE_A_MOD) in SIEVE_A_RES and (n % SIEVE_B_MOD) in SIEVE_B_RES:
            out.append(n)
    return out


SIEVE_OFFSETS = sieve_offsets(0, 56)          # one full period (lcm 8,7 = 56)
print("sieve C offsets (period 56):", SIEVE_OFFSETS)


def sieve_pitch(i, center):
    """i-th sieve offset, wrapped over the period, + center + drift."""
    return center + SIEVE_OFFSETS[i % len(SIEVE_OFFSETS)]


# ---------------------------------------------------------------- phase 1
# raw sieve walk: single-voice draft. Onsets at sieve-period-scaled
# fractional ticks (raw, unquantized), pitches = sieve offsets around a
# drifting center, NO chord quantization, NO harmony.
SEC_DENS = [0.5, 0.8, 1.0, 0.8, 1.0, 0.55]     # event density per section


def raw_sieve_melody(seed, duration_ticks, n_events, center0):
    """Single-voice raw sieve walk (unquantized rhythm + raw pitches)."""
    r = np.random.default_rng(seed)
    events = []
    tick = 0
    center = center0
    for i in range(n_events):
        p = sieve_pitch(i, center)
        # raw: continuous chromatic wander around the sieve pitch (unquantized)
        p = p + r.normal(0.0, 1.1)
        p = max(LEAD_LO, min(LEAD_HI, p))
        midi = int(round(p))
        # rhythm: sieve-period proportion + jitter -> NON-grid multiples
        dur = int(SECTION_TICKS / n_events * (0.8 + 0.4 * r.random()))
        dur = max(120, min(dur, duration_ticks - tick))
        vel = int(np.clip(60 + 26 * abs(np.sin(i * 1.31)), 44, 104))
        if tick + dur > duration_ticks:
            dur = duration_ticks - tick
        if dur > 0:
            events.append(MusicEvent(pitch=midi, volume=vel,
                                     start_tick=tick, end_tick=tick + dur))
        tick += dur
        # register drift keeps the walk organic (macro-form arc)
        center += r.normal(0.0, 0.9)
    return events


phase1 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
phase1.create_matrix(num_voices=1, num_sections=N_SECTIONS)
phase1.add_voice("LeadRaw", program=65, channel=0)  # Soprano Sax (raw draft)

# per-section density: intro sparse, choruses dense, outro thins
for s, name in enumerate(NAMES):
    phase1.add_section(name, bars=BARS_PER)
    n_events = {0: 26, 1: 34, 2: 40, 3: 34, 4: 40, 5: 26}[s]
    center0 = {0: 67.0, 1: 69.0, 2: 71.0, 3: 69.0, 4: 71.0, 5: 67.0}[s]
    evs = raw_sieve_melody(SEED + s, SECTION_TICKS, n_events, center0)
    phase1.set_unit(0, s, MusicUnit(events=evs))

# zero-drift landmark padding for phase 1 (exact section boundary)
for s in range(N_SECTIONS):
    u = phase1.matrix.get_unit((0, s))
    evs = list(u.events)
    has_landmark = any(e.pitch == 0 and e.end_tick == SECTION_TICKS for e in evs)
    if not has_landmark:
        evs.append(MusicEvent(pitch=0, volume=0, start_tick=SECTION_TICKS - 1,
                              end_tick=SECTION_TICKS))
    phase1.set_unit(0, s, MusicUnit(events=evs))

ok1, msg1 = phase1.validate()
print("PHASE1 validate:", msg1)
P1_MIDI = os.path.join(MIDI_DIR, "080-groove-sieve-phase1.mid")
phase1.to_midi(P1_MIDI)
print("phase1 written", P1_MIDI)


# ---------------------------------------------------------------- phase 2
# rules post-process: grid lock -> chord-tone quantization -> voice-leading
def quantize_lead_to_grid(events, grid=240):
    """Phase-2 rhythm lock: snap every onset to nearest 8th (240 @ 110 BPM)."""
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
    ("Lead",     65, 0),   # Soprano Sax (sieve lead)
    ("Horns",    61, 1),   # Brass Section (sieve-stab accents)
    ("Rhodes",   4,  2),   # Electric Piano (comp)
    ("Bass",     33, 3),   # Electric Bass (finger)
    ("Drums",     0, 9),   # percussion channel
]
N_V = len(VOICES)
phase2.create_matrix(num_voices=N_V, num_sections=N_SECTIONS)
vnames = [v[0] for v in VOICES]
for name, prog, ch in VOICES:
    phase2.add_voice(name, program=prog, channel=ch)
for n in NAMES:
    phase2.add_section(n, bars=BARS_PER)

# --- lead: GRID LOCK FIRST, then chord-tone quantize per bar (078/079 rule) ---
for s, name in enumerate(NAMES):
    raw_unit = phase1.matrix.get_unit((0, s))
    raw_events = list(raw_unit.events)
    # step 1: RHYTHM LOCK to the 8th grid (240 ticks @ 110 BPM)
    raw_events = quantize_lead_to_grid(raw_events, grid=240)
    q_events = []
    for e in raw_events:
        if e.pitch == 0:
            q_events.append(e)
            continue
        # Phase 2a: nearest scale degree first (sieve skeleton -> mode)
        sc = min(SCALE, key=lambda c: (abs(c - e.pitch), c))
        # Phase 2b: chord-tone quantization per bar using GRID-LOCKED tick
        # (078 bugfix: phase-1 events are SECTION-RELATIVE ticks, so the
        # global bar = s*BARS_PER + (local tick // BAR))
        local_bar = e.start_tick // BAR
        bar = s * BARS_PER + local_bar
        tones = chord_for_bar(bar if bar < N_BARS else N_BARS - 1)
        qp = quantize_to_chord(sc, tones)
        q_events.append(MusicEvent(pitch=qp, volume=e.volume,
                                   start_tick=e.start_tick, end_tick=e.end_tick))
    # voice-leading: cap leaps to <= 9 semitones, drift toward nearest chord tone
    for i in range(1, len(q_events)):
        e = q_events[i]
        if e.pitch == 0:
            continue
        p_prev = q_events[i - 1].pitch if q_events[i - 1].pitch else LEAD_HI
        if abs(e.pitch - p_prev) > 9:
            local_bar = e.start_tick // BAR
            bar = s * BARS_PER + local_bar
            tones = chord_for_bar(bar if bar < N_BARS else N_BARS - 1)
            e.pitch = min(tones, key=lambda c: (abs(c - p_prev), c))
    phase2.set_unit(0, s, MusicUnit(events=q_events))

# --- horns: sieve-stab accents. The sieve C's residues select which offbeats
#     get stabbed: pattern [0,2,5] mod 8 over the bar -> 8ths 0, 2, 5
#     (beat 1, 2&, 3&), plus 7 (4& push) in choruses. Every stab plays the
#     bar's chord tones (in-chord invariant). ---
HORN_STRONG = {2, 4}   # chorus sections
for bar in range(N_BARS):
    s, b = divmod(bar, BARS_PER)
    tones = chord_for_bar(bar)
    t0 = b * BAR
    e = []
    stab_offs = [0, 720, 1200]          # sieve residues 0,2,5 -> 8ths 0,2,5
    if s in HORN_STRONG:
        stab_offs = [0, 720, 1200, 1680]  # + 4& push (sieve residue 7)
    for off in stab_offs:
        # alternate root/third/fifth across stabs (sieve rotation)
        p = tones[(off // 240) % len(tones)] + 12
        e.append(MusicEvent(pitch=p, volume=76,
                            start_tick=t0 + off, end_tick=t0 + off + 120))
    unit = phase2.matrix.get_unit((1, s))
    events = list(unit.events) if unit is not None else []
    events.extend(e)
    phase2.set_unit(1, s, MusicUnit(events=events))

# --- rhodes: sustained comp per bar, 3rd+7th color, light 8th rhythm ---
for bar in range(N_BARS):
    s, b = divmod(bar, BARS_PER)
    tones = chord_for_bar(bar)
    t0 = b * BAR
    third = tones[1] + 12
    seventh = tones[2] + 12
    e = []
    for k in range(0, BAR, 480):
        if k % 960 == 0:
            e.append(MusicEvent(pitch=third, volume=58,
                                start_tick=t0 + k, end_tick=t0 + k + 420))
        else:
            e.append(MusicEvent(pitch=seventh, volume=52,
                                start_tick=t0 + k, end_tick=t0 + k + 380))
    unit = phase2.matrix.get_unit((2, s))
    events = list(unit.events) if unit is not None else []
    events.extend(e)
    phase2.set_unit(2, s, MusicUnit(events=events))

# --- bass: groove octave pulse, root on 1&3, fifth on 2&4, 16th push in
#     choruses (sieve residue 7 = the "push" 16th before the next bar) ---
for bar in range(N_BARS):
    s, b = divmod(bar, BARS_PER)
    root = BASS[PROG[bar]]
    fifth = root + 7
    t0 = b * BAR
    e = [
        MusicEvent(pitch=root, volume=102, start_tick=t0, end_tick=t0 + 360),
        MusicEvent(pitch=fifth, volume=88, start_tick=t0 + 480, end_tick=t0 + 840),
        MusicEvent(pitch=root, volume=102, start_tick=t0 + 960, end_tick=t0 + 1320),
        MusicEvent(pitch=fifth, volume=88, start_tick=t0 + 1440, end_tick=t0 + 1800),
    ]
    if s in (2, 4):   # chorus: 16th push into next bar
        e.append(MusicEvent(pitch=root, volume=92, start_tick=t0 + 1800,
                            end_tick=t0 + 1920 - 10))
    unit = phase2.matrix.get_unit((3, s))
    events = list(unit.events) if unit is not None else []
    events.extend(e)
    phase2.set_unit(3, s, MusicUnit(events=events))

# --- drums: backbeat groove (KIT constants). Kick 1&3, snare 2&4,
#     closed hat 8ths, chorus adds claps + ride. ---
K = KIT
V = VELOCITIES
DRUM_DENS = [0.5, 0.8, 1.0, 0.8, 1.0, 0.55]
for s in range(N_SECTIONS):
    dens = DRUM_DENS[s]
    evs = []
    if dens <= 0:
        phase2.set_unit(4, s, create_empty_unit(SECTION_TICKS))
        continue
    for bar in range(BARS_PER):
        t0 = bar * BAR
        # closed hat 8ths (always)
        for k in range(0, BAR, 240):
            evs.append(MusicEvent(pitch=K["hat_closed"], volume=int(V["hat_closed"] * 0.8),
                                  start_tick=t0 + k, end_tick=t0 + k + 90))
        # kick on 1 and 3
        evs.append(MusicEvent(pitch=K["kick"], volume=int(V["kick"] * 1.05),
                              start_tick=t0, end_tick=t0 + 160))
        evs.append(MusicEvent(pitch=K["kick"], volume=int(V["kick"] * 1.0),
                              start_tick=t0 + 960, end_tick=t0 + 1120))
        if dens >= 0.8:
            # snare backbeat on 2 and 4
            evs.append(MusicEvent(pitch=K["snare"], volume=int(V["snare"] * 1.1),
                                  start_tick=t0 + 480, end_tick=t0 + 620))
            evs.append(MusicEvent(pitch=K["snare"], volume=int(V["snare"] * 1.15),
                                  start_tick=t0 + 1440, end_tick=t0 + 1580))
            if dens >= 1.0:
                # clap doubles snare + ride cymbal on beat 1
                evs.append(MusicEvent(pitch=K["clap"], volume=int(V["clap"] * 0.95),
                                      start_tick=t0 + 480, end_tick=t0 + 600))
                evs.append(MusicEvent(pitch=K["clap"], volume=int(V["clap"] * 1.0),
                                      start_tick=t0 + 1440, end_tick=t0 + 1560))
                evs.append(MusicEvent(pitch=K["ride"], volume=int(V["ride"] * 1.0),
                                      start_tick=t0, end_tick=t0 + 600))
    phase2.set_unit(4, s, MusicUnit(events=evs))

# --- voice-leading check on lead (rules.voice_leading) ---
from rules.voice_leading import VoiceLeadingRules  # noqa: E402

vlc = VoiceLeadingRules(style="classical")   # strict: hidden 5ths flagged
vl_flags = []
for s in range(N_SECTIONS):
    u = phase2.matrix.get_unit((0, s))
    evs = [e for e in u.events if e.pitch > 0]
    if len(evs) < 2:
        continue
    for i in range(1, len(evs)):
        a, b = evs[i - 1], evs[i]
        if vlc.check_hidden_fifths([a.pitch], [b.pitch]):
            vl_flags.append((s, a.pitch, b.pitch, "hidden-fifth"))
print("VOICE-LEADING flags (lead, classical):", vl_flags[:8], "total", len(vl_flags))


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

P2_MIDI = os.path.join(MIDI_DIR, "080-groove-sieve.mid")
phase2.to_midi(P2_MIDI)
print("phase2 written", P2_MIDI)

# ---------------------------------------------------------------- analysis
from visualization.grid import write_grid_visualization  # noqa: E402

grid_path = os.path.join(ANALYSIS_DIR, "grid_visualization.txt")
write_grid_visualization(phase2.matrix, grid_path, ticks_per_character=120,
                         voice_names=vnames, bpm=BPM,
                         mode="G minor / Method 025 Xenakis sieve + groove")
print("grid written", grid_path)

# provenance
from workflows.provenance import write_provenance, AI_GENERATED  # noqa: E402

for mid, phase, note in (
        (P1_MIDI, "1", "raw Xenakis sieve walk (sieve A mod 8 res {0,2,5} ∩ B mod 7 res {0,1,4}), unquantized, single voice, no harmony"),
        (P2_MIDI, "2", "8th-grid locked, chord-tone quantized to G-minor groove progression, sieve-stab horns, voice-leading check, full texture")):
    write_provenance(
        mid, AI_GENERATED, "Xenakis Sieve Theory (Method 025, sieve C = A ∩ B, lcm 56)",
        parameters={"bpm": BPM, "key": "G natural minor", "sections": N_SECTIONS,
                    "bars": N_BARS, "phase": phase,
                    "progression": [CHORD_NAMES[r] for r in PROG], "seed": SEED,
                    "sieve_A": {"mod": SIEVE_A_MOD, "res": list(SIEVE_A_RES)},
                    "sieve_B": {"mod": SIEVE_B_MOD, "res": list(SIEVE_B_RES)}},
        notes=note)
    print("provenance for phase", phase)

# summary.json
with open(os.path.join(ANALYSIS_DIR, "summary.json"), "w") as f:
    json.dump({
        "project": "080-groove-sieve",
        "style": "Groove",
        "method": "025 Xenakis Sieve Theory (sieve C = A ∩ B, lcm 56)",
        "bpm": BPM, "key": "G natural minor", "tempo": BPM,
        "bars": N_BARS,
        "sections": {n: BARS_PER for n in NAMES},
        "progression": [CHORD_NAMES[r] for r in PROG],
        "voices": vnames,
        "phase1": os.path.basename(P1_MIDI),
        "phase2": os.path.basename(P2_MIDI),
        "grid": os.path.basename(grid_path),
        "seed": SEED,
        "sieve_A": {"mod": SIEVE_A_MOD, "res": list(SIEVE_A_RES)},
        "sieve_B": {"mod": SIEVE_B_MOD, "res": list(SIEVE_B_RES)},
    }, f, indent=2)
print("summary.json written")

# ---------------------------------------------------------------- size asserts
for p in (P1_MIDI, P2_MIDI, grid_path,
          os.path.join(ANALYSIS_DIR, "summary.json")):
    assert os.path.getsize(p) > 40, "too small: %s" % p
print("ALL SIZE ASSERTS PASSED")
print("PROGRESSION:", [CHORD_NAMES[r] for r in PROG])
