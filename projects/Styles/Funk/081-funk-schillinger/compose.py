# -*- coding: utf-8 -*-
"""081-funk-schillinger - Funk style / Method 018 Schillinger System of Musical Design.

Two-phase composition:
  Phase 1: raw Schillinger resultant walk - a single-voice melodic draft whose
           rhythm comes from the Schillinger interference resultant of two
           periodic generators (a=5, b=3 -> durations in pulses) scaled to
           fractional (non-grid) tick durations, and whose pitches come from a
           coordinate-axis projection (sine curve over the scale) with seeded
           register drift. No chord-tone quantization, no harmony, no bass, no
           drums. Pure Schillinger rhythmic draft with raw pitch projection.
  Phase 2: musicom rules post-process - rhythm locked to the 16th grid
           (120 ticks @ 100 BPM), chord-tone quantization per bar to a
           Bb-major funk progression (I vi ii V / I IV V I ...), voice
           leading checks via rules.voice_leading (parallel motion between
           bass + lead), full funk texture: lead (trumpet) + Rhodes comp
           + wah-ish guitar stabs (electric guitar 27) + bass (octave
           pulse + 16th push) + drums (kick 1&3, snare 2&4, hats 8ths +
           claps in choruses) + clavinet horn-stabs in choruses.

Engine only: structures + workflows.unitmatrix_composer + generators.schillinger
+ rules.voice_leading. validate() gate + to_midi(). No raw mido authoring.
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

# instrument library constants (read-only)
sys.path.insert(0, "/opt/data/projects/Instruments")
from Brass.trumpet.trumpet import MIDI_PROGRAM as TRUMPET_PROG  # noqa: E402
from Percussion.drum_kit.drum_kit import KIT, VELOCITIES  # noqa: E402

SEED = 20260829
rng = np.random.default_rng(SEED)

# ---------------------------------------------------------------- project dirs
PROJ = "/opt/data/projects/Styles/Funk/081-funk-schillinger"
MIDI_DIR = os.path.join(PROJ, "MIDI")
AUDIO_DIR = os.path.join(PROJ, "Audio")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")
for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
    os.makedirs(d, exist_ok=True)

# ---------------------------------------------------------------- concept
BPM = 100
TPB = 480
BEATS = 4
BAR = TPB * BEATS            # 1920
# Bb major (funk tonal palette), 16th grid = 120 @ 100 BPM
SCALE = [58, 60, 62, 63, 65, 67, 69, 70, 72, 74, 76, 77, 79, 81]
LEAD_LO, LEAD_HI = 60, 88

# diatonic triads in Bb major, keyed by root MIDI
CHORDS = {
    58: [58, 62, 65],   # Bb  I
    60: [60, 63, 67],   # Cm  ii
    62: [62, 65, 69],   # Dm  iii
    63: [63, 67, 70],   # Eb  IV
    65: [65, 69, 72],   # F   V
}
ROOTS = [58, 60, 62, 63, 65]
BASS = {58: 34, 60: 36, 62: 38, 63: 39, 65: 41}   # octave 2 (Bb1-C2-D2-Eb2-F2)

# ---------------------------------------------------------------- sections
NAMES = ["Intro", "Verse", "Chorus", "Verse2", "Chorus2", "Outro"]
BARS_PER = 4
N_SECTIONS = len(NAMES)
N_BARS = N_SECTIONS * BARS_PER            # 24 bars
SECTION_TICKS = BAR * BARS_PER            # 7680

# 24-bar funk progression (Bb major): I vi ii V | I vi ii V |
#   I IV V I | I V I ii | I vi ii V | I IV ii I
PROG = ([58, 60, 62, 65] * 2) + [58, 63, 65, 58] + [58, 65, 58, 60] + \
       [58, 60, 62, 65] + [58, 63, 60, 58]
assert len(PROG) == N_BARS, (len(PROG), N_BARS)
CHORD_NAMES = {58: "I", 60: "ii", 62: "iii", 63: "IV", 65: "V"}


def chord_for_bar(bar):
    return CHORDS[PROG[bar]]


def quantize_to_chord(pitch, chord_tones):
    """Snap a pitch to nearest chord tone, resolving ties toward lower."""
    return min(chord_tones, key=lambda c: (abs(c - pitch), c))


# ---------------------------------------------------------------- phase 1
# raw Schillinger resultant walk: durations from generator interference.
#   resultant of a=5, b=3 (pulses): durations in pulse units; scaled to ticks
#   with a fractional multiplier (e.g. x 210) so onsets are NON-grid multiples
#   (raw draft keeps this character; phase 2 quantizes).
SCH_A, SCH_B = 5, 3
sch = SchillingerGenerator(generator_a=SCH_A, generator_b=SCH_B)
SCH_DURS = sch.generate_resultant()          # e.g. [1,1,1,1,2,2,3,1,1,2,2,1,1,2] sum 21
print("Schillinger resultant a=%d,b=%d:" % (SCH_A, SCH_B), SCH_DURS)


def raw_schillinger_melody(seed, duration_ticks, n_events, center0):
    """Single-voice raw Schillinger walk (unquantized rhythm + raw pitches)."""
    r = np.random.default_rng(seed)
    events = []
    tick = 0
    center = center0
    cycle = SCH_DURS
    total_pulses = float(sum(cycle))
    for i in range(n_events):
        # rhythm: Schillinger resultant duration, scaled to fractional ticks
        d_pulses = cycle[i % len(cycle)]
        # scale factor ~ (SECTION_TICKS / n_events) / (avg pulse) with jitter
        scale = (duration_ticks / n_events) / (total_pulses / len(cycle))
        scale *= (0.9 + 0.25 * r.random())      # raw: jittered, off-grid
        dur = int(d_pulses * scale)
        dur = max(90, min(dur, duration_ticks - tick))
        # pitch: coordinate-axis projection (sine) + register drift
        p = center + 4.0 * math.sin(i * 0.55)
        p = p + r.normal(0.0, 1.1)
        p = max(LEAD_LO, min(LEAD_HI, p))
        midi = int(round(p))
        vel = int(np.clip(62 + 24 * abs(math.sin(i * 1.23)), 46, 106))
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
phase1.add_voice("LeadRaw", program=56, channel=0)  # Trumpet (raw draft)

# per-section density: intro sparse, choruses dense, outro thins
for s, name in enumerate(NAMES):
    phase1.add_section(name, bars=BARS_PER)
    n_events = {0: 26, 1: 34, 2: 42, 3: 34, 4: 42, 5: 26}[s]
    center0 = {0: 70.0, 1: 72.0, 2: 74.0, 3: 72.0, 4: 74.0, 5: 70.0}[s]
    evs = raw_schillinger_melody(SEED + s, SECTION_TICKS, n_events, center0)
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
P1_MIDI = os.path.join(MIDI_DIR, "081-funk-schillinger-phase1.mid")
phase1.to_midi(P1_MIDI)
print("phase1 written", P1_MIDI)


# ---------------------------------------------------------------- phase 2
# rules post-process: grid lock -> chord-tone quantization -> voice-leading
def quantize_lead_to_grid(events, grid=120):
    """Phase-2 rhythm lock: snap every onset to nearest 16th (120 @ 100 BPM)."""
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
    ("Lead",     TRUMPET_PROG, 0),   # Trumpet (Schillinger lead)
    ("Rhodes",   4,  1),             # Electric Piano (comp)
    ("Guitar",   27, 2),             # Electric Guitar (clean, wah stabs)
    ("Bass",     33, 3),             # Electric Bass (finger)
    ("Clav",     7,  4),             # Clavinet (horn stabs in choruses)
    ("Drums",     0, 9),             # percussion channel
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
    # step 1: RHYTHM LOCK to the 16th grid (120 ticks @ 100 BPM)
    raw_events = quantize_lead_to_grid(raw_events, grid=120)
    q_events = []
    for e in raw_events:
        if e.pitch == 0:
            q_events.append(e)
            continue
        # Phase 2a: nearest scale degree first (raw projection -> mode)
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

# --- rhodes: sustained comp per bar, 3rd+5th color, 8th rhythm ---
for bar in range(N_BARS):
    s, b = divmod(bar, BARS_PER)
    tones = chord_for_bar(bar)
    t0 = b * BAR
    third = tones[1] + 12
    fifth = tones[2] + 12
    e = []
    for k in range(0, BAR, 480):
        if k % 960 == 0:
            e.append(MusicEvent(pitch=third, volume=56,
                                start_tick=t0 + k, end_tick=t0 + k + 420))
        else:
            e.append(MusicEvent(pitch=fifth, volume=50,
                                start_tick=t0 + k, end_tick=t0 + k + 380))
    unit = phase2.matrix.get_unit((1, s))
    events = list(unit.events) if unit is not None else []
    events.extend(e)
    phase2.set_unit(1, s, MusicUnit(events=events))

# --- guitar: wah-ish offbeat stabs (16th push feel), chord tones +12 ---
for bar in range(N_BARS):
    s, b = divmod(bar, BARS_PER)
    tones = chord_for_bar(bar)
    t0 = b * BAR
    e = []
    # stabs on 2&, 3&, 4& (offbeats) - classic funk rhythm guitar
    for off in (720, 1200, 1680):
        p = tones[(off // 240) % len(tones)] + 12
        e.append(MusicEvent(pitch=p, volume=62,
                            start_tick=t0 + off, end_tick=t0 + off + 100))
    if s in (2, 4):   # choruses: add 1& push into the bar
        e.append(MusicEvent(pitch=tones[0] + 12, volume=66,
                            start_tick=t0 + 120, end_tick=t0 + 200))
    unit = phase2.matrix.get_unit((2, s))
    events = list(unit.events) if unit is not None else []
    events.extend(e)
    phase2.set_unit(2, s, MusicUnit(events=events))

# --- bass: funk octave pulse, root on 1&3, fifth on 2&4, 16th push in
#     choruses ---
for bar in range(N_BARS):
    s, b = divmod(bar, BARS_PER)
    root = BASS[PROG[bar]]
    fifth = root + 7
    t0 = b * BAR
    e = [
        MusicEvent(pitch=root, volume=104, start_tick=t0, end_tick=t0 + 340),
        MusicEvent(pitch=fifth, volume=88, start_tick=t0 + 480, end_tick=t0 + 820),
        MusicEvent(pitch=root, volume=104, start_tick=t0 + 960, end_tick=t0 + 1300),
        MusicEvent(pitch=fifth, volume=88, start_tick=t0 + 1440, end_tick=t0 + 1780),
    ]
    if s in (2, 4):   # chorus: 16th push into next bar (funk anticipation)
        e.append(MusicEvent(pitch=root, volume=94, start_tick=t0 + 1800,
                            end_tick=t0 + 1910))
    unit = phase2.matrix.get_unit((3, s))
    events = list(unit.events) if unit is not None else []
    events.extend(e)
    phase2.set_unit(3, s, MusicUnit(events=events))

# --- clav: horn-stab accents in choruses (chord tones, 8th offbeats) ---
for bar in range(N_BARS):
    s, b = divmod(bar, BARS_PER)
    if s not in (2, 4):
        continue
    tones = chord_for_bar(bar)
    t0 = b * BAR
    e = []
    for off in (0, 720, 1200, 1680):
        p = tones[(off // 240) % len(tones)] + 24
        e.append(MusicEvent(pitch=p, volume=70,
                            start_tick=t0 + off, end_tick=t0 + off + 110))
    unit = phase2.matrix.get_unit((4, s))
    events = list(unit.events) if unit is not None else []
    events.extend(e)
    phase2.set_unit(4, s, MusicUnit(events=events))

# --- drums: backbeat funk groove (KIT constants). Kick 1&3, snare 2&4,
#     closed hat 8ths, chorus adds claps + ride. ---
K = KIT
V = VELOCITIES
DRUM_DENS = [0.5, 0.8, 1.0, 0.8, 1.0, 0.55]
for s in range(N_SECTIONS):
    dens = DRUM_DENS[s]
    evs = []
    if dens <= 0:
        phase2.set_unit(5, s, create_empty_unit(SECTION_TICKS))
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
    phase2.set_unit(5, s, MusicUnit(events=evs))

# --- voice-leading check (rules.voice_leading): parallel motion between
#     bass (root pulses) and lead (chord tones) per bar-pair ---
from rules.voice_leading import VoiceLeadingRules  # noqa: E402

vlc = VoiceLeadingRules(style="classical")   # strict: parallel 5ths/8ves flagged
vl_flags = []
for bar in range(N_BARS - 1):
    s, b = divmod(bar, BARS_PER)
    bass_a = BASS[PROG[bar]]
    bass_b = BASS[PROG[bar + 1]]
    # lead: first pitched event of each bar (grid-locked)
    u = phase2.matrix.get_unit((0, s))
    evs = [e for e in u.events if e.pitch > 0 and b * BAR <= e.start_tick < (b + 1) * BAR]
    evs_next = [e for e in u.events if e.pitch > 0 and (b + 1) * BAR <= e.start_tick < (b + 2) * BAR]
    if evs and evs_next:
        lead_a = evs[0].pitch
        lead_b = evs_next[0].pitch
        viol = vlc.check_parallel_motion([bass_a, lead_a], [bass_b, lead_b])
        if viol:
            vl_flags.append((bar, viol))
        hid = vlc.check_hidden_fifths([bass_a, lead_a], [bass_b, lead_b])
        if hid:
            vl_flags.append((bar, hid))
print("VOICE-LEADING flags (bass+lead, classical):", vl_flags[:8], "total", len(vl_flags))


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

P2_MIDI = os.path.join(MIDI_DIR, "081-funk-schillinger.mid")
phase2.to_midi(P2_MIDI)
print("phase2 written", P2_MIDI)

# ---------------------------------------------------------------- analysis
from visualization.grid import write_grid_visualization  # noqa: E402

grid_path = os.path.join(ANALYSIS_DIR, "grid_visualization.txt")
write_grid_visualization(phase2.matrix, grid_path, ticks_per_character=120,
                         voice_names=vnames, bpm=BPM,
                         mode="Bb major / Method 018 Schillinger resultant + funk")
print("grid written", grid_path)

# provenance
from workflows.provenance import write_provenance, AI_GENERATED  # noqa: E402

for mid, phase, note in (
        (P1_MIDI, "1", "raw Schillinger resultant walk (a=5,b=3 interference), fractional tick durations, single voice, no harmony"),
        (P2_MIDI, "2", "16th-grid locked, chord-tone quantized to Bb-major funk progression, Rhodes/guitar/bass/clav texture, voice-leading check, full arrangement")):
    write_provenance(
        mid, AI_GENERATED, "Schillinger System of Musical Design (Method 018, generators.schillinger)",
        parameters={"bpm": BPM, "key": "Bb major", "sections": N_SECTIONS,
                    "bars": N_BARS, "phase": phase,
                    "progression": [CHORD_NAMES[r] for r in PROG], "seed": SEED,
                    "schillinger_a": SCH_A, "schillinger_b": SCH_B,
                    "resultant": SCH_DURS},
        notes=note)
    print("provenance for phase", phase)

# summary.json
with open(os.path.join(ANALYSIS_DIR, "summary.json"), "w") as f:
    json.dump({
        "project": "081-funk-schillinger",
        "style": "Funk",
        "method": "018 Schillinger System of Musical Design (resultant a=5,b=3)",
        "bpm": BPM, "key": "Bb major", "tempo": BPM,
        "bars": N_BARS,
        "sections": {n: BARS_PER for n in NAMES},
        "progression": [CHORD_NAMES[r] for r in PROG],
        "voices": vnames,
        "phase1": os.path.basename(P1_MIDI),
        "phase2": os.path.basename(P2_MIDI),
        "grid": os.path.basename(grid_path),
        "seed": SEED,
        "schillinger_a": SCH_A, "schillinger_b": SCH_B,
        "resultant": SCH_DURS,
    }, f, indent=2)
print("summary.json written")

# ---------------------------------------------------------------- size asserts
for p in (P1_MIDI, P2_MIDI, grid_path,
          os.path.join(ANALYSIS_DIR, "summary.json")):
    assert os.path.getsize(p) > 40, "too small: %s" % p
print("ALL SIZE ASSERTS PASSED")
print("PROGRESSION:", [CHORD_NAMES[r] for r in PROG])
