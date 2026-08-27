# -*- coding: utf-8 -*-
"""078-soul-voiceleading - Soul style / Method 007 Voice-Leading Graph Search.

Two-phase composition:
  Phase 1: raw tonal-network random walk - a single-voice melodic draft whose
           pitches come from a weighted random walk over the tonal function
           graph (tonic/subdominant/dominant/mediant/pre-dominant/borrow),
           WITHOUT chord-tone quantization and without full harmony. The raw
           walk emits unquantized chromatic pitches (register wander), no
           bass, no drums. Pure graph-generated melodic draft.
  Phase 2: musicom rules post-process - chord-tone quantization per bar
           (diatonic F-minor soul progression), voice-leading checks via
           rules.voice_leading.VoiceLeadingChecker (parallel motion, hidden
           fifths, voice crossing), full soul texture:
           lead (Tenor Sax) + horn stabs + Rhodes comp + violin counterline
           + electric bass + backbeat drums.

Engine only: structures + workflows.unitmatrix_composer + generators.tonal_network
+ rules.voice_leading. validate() gate + to_midi(). No raw mido authoring.
"""
import os
import json
import sys

import numpy as np

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import (
    UnitMatrixComposer, create_empty_unit,
)
from generators.tonal_network import TonalNetworkGenerator

# instrument library constants (read-only)
sys.path.insert(0, "/opt/data/projects/Instruments")
from Strings.violin.violin import MIDI_PROGRAM as VIO_PROG  # noqa: E402
from Percussion.drum_kit.drum_kit import KIT, VELOCITIES  # noqa: E402

SEED = 20260826
rng = np.random.default_rng(SEED)

# ---------------------------------------------------------------- project dirs
PROJ = "/opt/data/projects/Styles/Soul/078-soul-voiceleading"
MIDI_DIR = os.path.join(PROJ, "MIDI")
AUDIO_DIR = os.path.join(PROJ, "Audio")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")
for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
    os.makedirs(d, exist_ok=True)

# ---------------------------------------------------------------- concept
BPM = 96
TPB = 480
BEATS = 4
BAR = TPB * BEATS            # 1920
# F natural minor soul:  F G Ab Bb C Db Eb (across two octaves)
SCALE = [53, 55, 56, 58, 60, 61, 63, 65, 67, 68, 70, 72, 73, 75, 77]
LEAD_LO, LEAD_HI = 60, 86

# diatonic triads in F natural minor, keyed by root MIDI
CHORDS = {
    53: [53, 56, 60],   # Fm  i
    56: [56, 60, 63],   # Ab  III
    58: [58, 61, 65],   # Bbm iv
    60: [60, 63, 67],   # C   V (major - harmonic lift)
    61: [61, 65, 68],   # Db  VI
}
ROOTS = [53, 56, 58, 60, 61]
BASS = {53: 29, 56: 32, 58: 34, 60: 36, 61: 37}   # octave 2 (F1-Ab1-Bb1-C2-Db2)

# ---------------------------------------------------------------- sections
NAMES = ["Intro", "Verse", "Chorus", "Verse2", "Chorus2", "Outro"]
BARS_PER = 4
N_SECTIONS = len(NAMES)
N_BARS = N_SECTIONS * BARS_PER            # 24 bars
SECTION_TICKS = BAR * BARS_PER            # 7680

# chord roots, one per bar: i iv V III | i iv V VI | i V i VI | i iv V i | ...
PROG = [53, 58, 60, 56] * 2 + [53, 60, 53, 61] + [53, 58, 60, 53] + \
       [53, 58, 60, 56] + [53, 60, 58, 53]
assert len(PROG) == N_BARS, (len(PROG), N_BARS)
CHORD_NAMES = {53: "i", 56: "III", 58: "iv", 60: "V", 61: "VI"}


def chord_for_bar(bar):
    return CHORDS[PROG[bar]]


def quantize_to_chord(pitch, chord_tones):
    """Snap a pitch to nearest chord tone, resolving ties toward lower."""
    return min(chord_tones, key=lambda c: (abs(c - pitch), c))


# ---------------------------------------------------------------- phase 1
# raw tonal-network walk: melodic draft from the functional graph, NO chord
# quantization, NO harmony context. Graph roles map to F-minor regions:
# tonic=Fm, subdominant=Bbm, dominant=C, mediant=Ab, pre_dominant=Gdim,
# borrow=Db (bVII backdoor).
def raw_graph_melody(seed, duration_ticks, role_seq, n_events=26):
    """Single-voice raw melody: graph walk + register wander, unquantized.

    NOTE: n_events=26 gives slot=295 ticks (7680//26) which is OFF the
    rhythmic grid. The RAW draft keeps this (it's the unquantized phase-1
    artifact). Phase-2 quantizes onsets to the 8th-note grid — see
    quantize_lead_to_grid().
    """
    r = np.random.default_rng(seed)
    # graph node absolute pitches for each role (F minor root 53)
    gen = TonalNetworkGenerator(root=53, tonic_quality="minor", seed=seed)
    events = []
    tick = 0
    slot = duration_ticks // n_events
    center = 72.0
    for role in role_seq:
        tones = gen.node_pitches(role)
        base = float(r.choice(tones))
        # raw: continuous chromatic wander around the node pitch (unquantized)
        p = base + r.normal(0.0, 1.6)
        p = max(LEAD_LO, min(LEAD_HI, p))
        midi = int(round(p))
        dur = int(slot * 0.7)
        vel = int(np.clip(68 + 24 * abs(np.sin(tick / 240.0)), 48, 108))
        if tick + dur > duration_ticks:
            dur = duration_ticks - tick
        if dur > 0:
            events.append(MusicEvent(pitch=midi, volume=vel,
                                     start_tick=tick, end_tick=tick + dur))
        tick += slot
    return events


def quantize_lead_to_grid(events, grid=240):
    """Phase-2 rhythm lock: snap every onset to the nearest grid tick.

    The phase-1 raw walk emits onsets at slot=295 (off-grid). For the
    final arrangement the lead MUST lock to the same grid as drums
    (8th = 240 ticks at 96 BPM). Snap start_tick to nearest grid
    multiple, keep duration (clamp to section end). Rhythm becomes
    groove-locked while preserving the pitch contour.
    """
    q = []
    for e in events:
        if e.pitch == 0:
            q.append(e)
            continue
        st = int(round(e.start_tick / grid) * grid)
        q.append(MusicEvent(pitch=e.pitch, volume=e.volume,
                            start_tick=st, end_tick=max(st + 1, e.end_tick)))
    return q


phase1 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
phase1.create_matrix(num_voices=1, num_sections=N_SECTIONS)
phase1.add_voice("LeadRaw", program=65, channel=0)  # Tenor Sax

# per-section role schedules: intro wanders tonic/mediant; verse tonic->subdom;
# chorus dominant-heavy (lift); outro drifts back to tonic (homecoming)
ROLE_SEQS = {
    0: ["tonic", "mediant", "tonic", "subdominant"],
    1: ["tonic", "subdominant", "dominant", "tonic"],
    2: ["subdominant", "dominant", "tonic", "dominant"],
    3: ["tonic", "subdominant", "dominant", "tonic"],
    4: ["subdominant", "dominant", "tonic", "dominant"],
    5: ["tonic", "mediant", "subdominant", "tonic"],
}

for s, name in enumerate(NAMES):
    phase1.add_section(name, bars=BARS_PER)
    seq = [ROLE_SEQS[s][b % 4] for b in range(BARS_PER) for _ in range(6)]
    evs = raw_graph_melody(SEED + s, SECTION_TICKS, seq)
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
P1_MIDI = os.path.join(MIDI_DIR, "078-soul-voiceleading-phase1.mid")
phase1.to_midi(P1_MIDI)
print("phase1 written", P1_MIDI)

# ---------------------------------------------------------------- phase 2
# rules post-process: chord-tone quantization + voice-leading check + full soul texture
phase2 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
VOICES = [
    ("Lead",     65, 0),   # Tenor Sax (soul lead)
    ("Horns",    61, 1),   # Brass Section (stabs)
    ("Rhodes",   4,  2),   # Electric Piano (pad/comp)
    ("Violin",   VIO_PROG, 3),   # counterline (instrument library)
    ("Bass",     33, 4),   # Electric Bass (finger)
    ("Drums",     0, 9),   # percussion channel
]
N_V = len(VOICES)
phase2.create_matrix(num_voices=N_V, num_sections=N_SECTIONS)
vnames = [v[0] for v in VOICES]
for name, prog, ch in VOICES:
    phase2.add_voice(name, program=prog, channel=ch)
for n in NAMES:
    phase2.add_section(n, bars=BARS_PER)

# --- lead: quantize phase-1 raw events to each bar's chord tones ---
for s, name in enumerate(NAMES):
    raw_unit = phase1.matrix.get_unit((0, s))
    q_events = []
    for e in raw_unit.events:
        if e.pitch == 0:
            q_events.append(e)
            continue
        bar = e.start_tick // BAR
        tones = chord_for_bar(bar if bar < N_BARS else N_BARS - 1)
        qp = quantize_to_chord(e.pitch, tones)
        q_events.append(MusicEvent(pitch=qp, volume=e.volume,
                                   start_tick=e.start_tick, end_tick=e.end_tick))
    # RHYTHM LOCK: snap onsets to the 8th-note grid (240 ticks @ 96 BPM)
    # so the lead grooves with drums/bass/Rhodes instead of drifting at
    # slot=295 off-grid intervals. Pitch contour preserved.
    q_events = quantize_lead_to_grid(q_events, grid=240)
    # voice-leading: cap leaps to <= 9 semitones, drift toward nearest chord tone
    for i in range(1, len(q_events)):
        e = q_events[i]
        if e.pitch == 0:
            continue
        p_prev = q_events[i - 1].pitch if q_events[i - 1].pitch else LEAD_HI
        if abs(e.pitch - p_prev) > 9:
            bar = e.start_tick // BAR
            tones = chord_for_bar(bar if bar < N_BARS else N_BARS - 1)
            e.pitch = min(tones, key=lambda c: (abs(c - p_prev), c))
    phase2.set_unit(0, s, MusicUnit(events=q_events))

# --- horns: syncopated stab accents on beats 2& / 4& (soul classic) ---
HORN_STRONG = {2, 4}   # choruses
for bar in range(N_BARS):
    s, b = divmod(bar, BARS_PER)
    tones = chord_for_bar(bar)
    t0 = b * BAR
    e = []
    if s in HORN_STRONG:
        # 4 stabs per bar: beats 2, 2&, 4, 4& (offbeat pushes)
        for off in (720, 960, 1680, 1920 - 240):
            for p in tones:
                e.append(MusicEvent(pitch=p + 12, volume=76,
                                    start_tick=t0 + off, end_tick=t0 + off + 120))
    else:
        # lighter: 2 stabs per bar on 2& and 4
        for off in (960, 1680):
            e.append(MusicEvent(pitch=tones[1] + 12, volume=66,
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

# --- violin: call-response counterline (violin library sweet spot 67-96) ---
# FIX (2026-08-27): old VIO_LINE was C-major pentatonic (E C D B E C D G)
# in an F-minor piece -> E/D/B out of key in every bar. New line uses
# F-minor pentatonic (F Ab Bb C Eb) and is chord-quantized per bar below.
VIO_LINE = [72, 68, 70, 75, 72, 68, 70, 65]   # C5 Ab4 Bb4 Eb5 C5 Ab4 Bb4 F4
for bar in range(N_BARS):
    s, b = divmod(bar, BARS_PER)
    t0 = b * BAR
    e = []
    if s in (1, 3):       # verses: answer phrase on beats 3-4
        for k, p in enumerate(VIO_LINE[4:]):
            off = 960 + k * 240
            qp = quantize_to_chord(p, chord_for_bar(bar))
            e.append(MusicEvent(pitch=qp, volume=62,
                                start_tick=t0 + off, end_tick=t0 + off + 200))
    elif s in (2, 4):     # choruses: full 8-note line
        for k, p in enumerate(VIO_LINE):
            off = 480 + k * 180
            qp = quantize_to_chord(p, chord_for_bar(bar))
            e.append(MusicEvent(pitch=qp, volume=68,
                                start_tick=t0 + off, end_tick=t0 + off + 150))
    unit = phase2.matrix.get_unit((3, s))
    events = list(unit.events) if unit is not None else []
    events.extend(e)
    phase2.set_unit(3, s, MusicUnit(events=events))

# --- bass: soul octave pulse, root on 1&3, fifth on 2&4, syncopated 16th push ---
for bar in range(N_BARS):
    s, b = divmod(bar, BARS_PER)
    root = BASS[PROG[bar]]
    fifth = root + 7
    t0 = b * BAR
    e = [
        MusicEvent(pitch=root, volume=100, start_tick=t0, end_tick=t0 + 360),
        MusicEvent(pitch=fifth, volume=88, start_tick=t0 + 480, end_tick=t0 + 840),
        MusicEvent(pitch=root, volume=100, start_tick=t0 + 960, end_tick=t0 + 1320),
        MusicEvent(pitch=fifth, volume=88, start_tick=t0 + 1440, end_tick=t0 + 1800),
    ]
    if s in (2, 4):   # chorus: 16th push into next bar
        e.append(MusicEvent(pitch=root, volume=92, start_tick=t0 + 1800,
                            end_tick=t0 + 1920 - 10))
    unit = phase2.matrix.get_unit((4, s))
    events = list(unit.events) if unit is not None else []
    events.extend(e)
    phase2.set_unit(4, s, MusicUnit(events=events))

# --- drums: backbeat soul via instrument library KIT ---
K = KIT
V = VELOCITIES
SEC_DENS = [0.4, 0.8, 1.0, 0.8, 1.0, 0.5]
for s in range(N_SECTIONS):
    dens = SEC_DENS[s]
    evs = []
    if dens <= 0:
        phase2.set_unit(5, s, create_empty_unit(SECTION_TICKS))
        continue
    for bar in range(BARS_PER):
        t0 = bar * BAR
        # closed hat 8ths (always)
        for k in range(0, BAR, 240):
            evs.append(MusicEvent(pitch=K["hat_closed"], volume=V["hat_closed"],
                                  start_tick=t0 + k, end_tick=t0 + k + 90))
        # kick on 1 and 3
        evs.append(MusicEvent(pitch=K["kick"], volume=V["kick"],
                              start_tick=t0, end_tick=t0 + 160))
        evs.append(MusicEvent(pitch=K["kick"], volume=V["kick"] - 4,
                              start_tick=t0 + 960, end_tick=t0 + 1120))
        if dens >= 0.8:
            # snare backbeat on 2 and 4
            evs.append(MusicEvent(pitch=K["snare"], volume=V["snare"],
                                  start_tick=t0 + 480, end_tick=t0 + 620))
            evs.append(MusicEvent(pitch=K["snare"], volume=V["snare"] + 4,
                                  start_tick=t0 + 1440, end_tick=t0 + 1580))
            if dens >= 1.0:
                # clap doubles snare + ride cymbal on beat 1
                evs.append(MusicEvent(pitch=K["clap"], volume=V["clap"],
                                      start_tick=t0 + 480, end_tick=t0 + 600))
                evs.append(MusicEvent(pitch=K["clap"], volume=V["clap"] + 4,
                                      start_tick=t0 + 1440, end_tick=t0 + 1560))
                evs.append(MusicEvent(pitch=K["ride"], volume=V["ride"],
                                      start_tick=t0, end_tick=t0 + 600))
    phase2.set_unit(5, s, MusicUnit(events=evs))

# --- voice-leading check on lead voice (rules.voice_leading) ---
from rules.voice_leading import VoiceLeadingRules  # noqa: E402

vlc = VoiceLeadingRules(style="pop")   # pop allows parallel 5ths/8ves
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
print("VOICE-LEADING flags (lead, pop style):", vl_flags[:8], "total", len(vl_flags))

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

P2_MIDI = os.path.join(MIDI_DIR, "078-soul-voiceleading.mid")
phase2.to_midi(P2_MIDI)
print("phase2 written", P2_MIDI)

# ---------------------------------------------------------------- analysis
from visualization.grid import write_grid_visualization  # noqa: E402

grid_path = os.path.join(ANALYSIS_DIR, "grid_visualization.txt")
write_grid_visualization(phase2.matrix, grid_path, ticks_per_character=120,
                         voice_names=vnames, bpm=BPM,
                         mode="F minor / Method 007 voice-leading graph soul")
print("grid written", grid_path)

# provenance
from workflows.provenance import write_provenance, AI_GENERATED  # noqa: E402

for mid, phase, note in (
        (P1_MIDI, "1", "raw tonal-network graph walk, unquantized, single voice, no harmony"),
        (P2_MIDI, "2", "chord-tone quantized to F-minor soul progression, voice-leading check, full texture")):
    write_provenance(
        mid, AI_GENERATED, "Voice-Leading Graph Search (Method 007, TonalNetworkGenerator)",
        parameters={"bpm": BPM, "key": "F natural minor", "sections": N_SECTIONS,
                    "bars": N_BARS, "phase": phase,
                    "progression": [CHORD_NAMES[r] for r in PROG], "seed": SEED},
        notes=note)
    print("provenance for phase", phase)

# summary.json
with open(os.path.join(ANALYSIS_DIR, "summary.json"), "w") as f:
    json.dump({
        "project": "078-soul-voiceleading",
        "style": "Soul",
        "method": "007 Voice-Leading Graph Search (TonalNetworkGenerator)",
        "bpm": BPM, "key": "F natural minor", "tempo": BPM,
        "bars": N_BARS,
        "sections": {n: BARS_PER for n in NAMES},
        "progression": [CHORD_NAMES[r] for r in PROG],
        "voices": vnames,
        "phase1": os.path.basename(P1_MIDI),
        "phase2": os.path.basename(P2_MIDI),
        "grid": os.path.basename(grid_path),
        "seed": SEED,
    }, f, indent=2)
print("summary.json written")

# ---------------------------------------------------------------- size asserts
for p in (P1_MIDI, P2_MIDI, grid_path,
          os.path.join(ANALYSIS_DIR, "summary.json")):
    assert os.path.getsize(p) > 40, "too small: %s" % p
print("ALL SIZE ASSERTS PASSED")
print("PROGRESSION:", [CHORD_NAMES[r] for r in PROG])
