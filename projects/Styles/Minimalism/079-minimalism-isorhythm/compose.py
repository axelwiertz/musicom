# -*- coding: utf-8 -*-
"""079-minimalism-isorhythm - Minimalism style / Method 032 Isorhythmic Talea-Color Mapping.

Two-phase composition:
  Phase 1: raw isorhythmic talea-color walk - a single-voice melodic draft
           whose pitches come from a Pärt-style color pattern (semitone offsets
           from tonic, cycled) and whose rhythm comes from a talea duration
           pattern (cycled), WITHOUT chord-tone quantization and without full
           harmony. Raw walk emits unquantized chromatic wander, no bass, no
           drums. Pure isorhythmic melodic draft.
  Phase 2: musicom rules post-process - M-voice snapped to E-natural-minor
           mode degrees (conjunct), T-voice = tintinnabuli triad shadow
           (E-G-B), chord-tone quantization per bar (diatonic E-minor
           minimalist progression i VI III iv), voice-leading checks via
           rules.voice_leading.VoiceLeadingRules, rhythm locked to the 16th
           grid (120 ticks @ 92 BPM), full texture:
           M-voice (Viola) + T-voice (Cello) + sustained strings pad (Violin)
           + double-bass drones + bell (glockenspiel) + minimal percussion.

Engine only: structures + workflows.unitmatrix_composer + generators.tintinnabuli
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
from generators.tintinnabuli import TintinnabuliGenerator, isorhythmize

# instrument library constants (read-only)
sys.path.insert(0, "/opt/data/projects/Instruments")
from Strings.violin.violin import MIDI_PROGRAM as VIO_PROG  # noqa: E402
from Strings.viola.viola import MIDI_PROGRAM as VLA_PROG  # noqa: E402
from Strings.cello.cello import MIDI_PROGRAM as CEL_PROG  # noqa: E402
from Strings.double_bass.double_bass import MIDI_PROGRAM as DB_PROG  # noqa: E402
from Percussion.drum_kit.drum_kit import KIT, VELOCITIES  # noqa: E402

SEED = 20260827
rng = np.random.default_rng(SEED)

# ---------------------------------------------------------------- project dirs
PROJ = "/opt/data/projects/Styles/Minimalism/079-minimalism-isorhythm"
MIDI_DIR = os.path.join(PROJ, "MIDI")
AUDIO_DIR = os.path.join(PROJ, "Audio")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")
for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
    os.makedirs(d, exist_ok=True)

# ---------------------------------------------------------------- concept
BPM = 92
TPB = 480
BEATS = 4
BAR = TPB * BEATS            # 1920
# E natural minor (Pärt holy-minimalism tonal palette):
# E F# G A B C D (across two octaves, 16th grid = 120)
SCALE = [52, 54, 55, 57, 59, 60, 62, 64, 66, 67, 69, 71, 72, 74, 76]
LEAD_LO, LEAD_HI = 55, 84

# diatonic triads in E natural minor, keyed by root MIDI
CHORDS = {
    52: [52, 55, 59],   # Em  i
    55: [55, 59, 62],   # G   III
    57: [57, 60, 64],   # Am  iv
    59: [59, 62, 66],   # B   V (major - harmonic lift)
    60: [60, 64, 67],   # C   VI
}
ROOTS = [52, 55, 57, 59, 60]
BASS = {52: 28, 55: 31, 57: 33, 59: 35, 60: 36}   # octave 2 (E1-G1-A1-B1-C2)

# ---------------------------------------------------------------- sections
NAMES = ["Intro", "Mvt1", "Mvt2", "Mvt3", "Mvt4", "Outro"]
BARS_PER = 4
N_SECTIONS = len(NAMES)
N_BARS = N_SECTIONS * BARS_PER            # 24 bars
SECTION_TICKS = BAR * BARS_PER            # 7680

# chord roots, one per bar: i VI III iv | i VI iii V | i VI IV V | ...
PROG = [52, 60, 55, 57] * 2 + [52, 60, 55, 59] + [52, 60, 57, 59] + \
       [52, 60, 55, 57] + [52, 55, 57, 52]
assert len(PROG) == N_BARS, (len(PROG), N_BARS)
CHORD_NAMES = {52: "i", 55: "III", 57: "iv", 59: "V", 60: "VI"}


def chord_for_bar(bar):
    return CHORDS[PROG[bar]]


def quantize_to_chord(pitch, chord_tones):
    """Snap a pitch to nearest chord tone, resolving ties toward lower."""
    return min(chord_tones, key=lambda c: (abs(c - pitch), c))


# ---------------------------------------------------------------- phase 1
# raw isorhythmic talea-color walk: melodic draft from Pärt-style color/talea
# patterns, NO chord quantization, NO harmony context.
# color (semitone offsets from tonic E4=64), talea (durations in beats):
COLOR = [0, 2, 4, 7, 5, 7, 4, 2, 0, -1, -3, -5]
TALEA = [1.0, 0.5, 0.5, 1.0, 0.5, 1.5, 0.5, 1.0, 2.0, 0.5, 1.0, 0.5]


def raw_isorhythm_melody(seed, duration_ticks, n_events=32):
    """Single-voice raw melody: isorhythmic color/talea cycling, unquantized.

    The color and talea cycles have coprime lengths (12 vs 12 -> period 12,
    but we add drift via a seeded register wander) so pitch and rhythm never
    lock into a static pattern. Onsets are placed at non-grid-fractional
    intervals (the raw draft keeps this character; phase-2 quantizes).
    """
    r = np.random.default_rng(seed)
    events = []
    tick = 0
    center = 67.0
    for i in range(n_events):
        c = COLOR[i % len(COLOR)]
        base = center + c
        # raw: continuous chromatic wander around the color pitch (unquantized)
        p = base + r.normal(0.0, 1.2)
        p = max(LEAD_LO, min(LEAD_HI, p))
        midi = int(round(p))
        dur_beats = TALEA[i % len(TALEA)]
        dur = int(dur_beats * TPB)
        dur = max(60, dur)   # min 16th
        vel = int(np.clip(62 + 22 * abs(np.sin(i * 1.7)), 44, 100))
        if tick + dur > duration_ticks:
            dur = duration_ticks - tick
        if dur > 0:
            events.append(MusicEvent(pitch=midi, volume=vel,
                                     start_tick=tick, end_tick=tick + dur))
        tick += dur
        # register drift keeps the walk organic
        center += r.normal(0.0, 0.8)
    return events


def quantize_lead_to_grid(events, grid=120):
    """Phase-2 rhythm lock: snap every onset to the nearest grid tick.

    Phase-1 raw walk emits onsets at talea-derived fractional offsets that
    are NOT multiples of the 16th grid. For the final arrangement every
    melodic/harmonic voice MUST lock to the same grid as percussion
    (16th = 120 ticks at 92 BPM). Snap start_tick to nearest grid multiple,
    clamp end_tick to section end, keep pitch contour.
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
phase1.add_voice("LeadRaw", program=75, channel=0)  # Pan Flute (soft, breathy)

# per-section talea/color rotation: intro sparse, movements densify, outro thins
for s, name in enumerate(NAMES):
    phase1.add_section(name, bars=BARS_PER)
    n_events = {0: 24, 1: 32, 2: 36, 3: 32, 4: 36, 5: 24}[s]
    evs = raw_isorhythm_melody(SEED + s, SECTION_TICKS, n_events)
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
P1_MIDI = os.path.join(MIDI_DIR, "079-minimalism-isorhythm-phase1.mid")
phase1.to_midi(P1_MIDI)
print("phase1 written", P1_MIDI)

# ---------------------------------------------------------------- phase 2
# rules post-process: mode/triad quantization + voice-leading check +
# full minimalist texture
phase2 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
VOICES = [
    ("M-Voice",   VLA_PROG, 0),   # Viola (melodic voice, Pärt M-voice)
    ("T-Voice",   CEL_PROG, 1),   # Cello (tintinnabuli triad shadow)
    ("Violin",    VIO_PROG, 2),   # sustained string pad (drone harmony)
    ("DblBass",   DB_PROG, 3),    # double-bass root drones
    ("Bells",     9, 4),          # Music Box / glockenspiel (color accents)
    ("Drums",     0, 9),          # percussion channel
]
N_V = len(VOICES)
phase2.create_matrix(num_voices=N_V, num_sections=N_SECTIONS)
vnames = [v[0] for v in VOICES]
for name, prog, ch in VOICES:
    phase2.add_voice(name, program=prog, channel=ch)
for n in NAMES:
    phase2.add_section(n, bars=BARS_PER)

# --- M-voice: grid-lock, then mode/chord-tone quantize phase-1 raw events ---
# ORDER MATTERS (079 bugfix): grid-lock FIRST, THEN chord-quantize using the
# grid-locked tick for bar lookup. Quantizing first then snapping the onset
# can push a note across a bar boundary into a bar whose chord it doesn't fit.
tint = TintinnabuliGenerator(tonic=52, mode='natural minor', t_register=40)
for s, name in enumerate(NAMES):
    raw_unit = phase1.matrix.get_unit((0, s))
    raw_events = list(raw_unit.events)
    # step 1: RHYTHM LOCK to the 16th grid (120 ticks @ 92 BPM)
    raw_events = quantize_lead_to_grid(raw_events, grid=120)
    q_events = []
    for e in raw_events:
        if e.pitch == 0:
            q_events.append(e)
            continue
        # Phase 2a: snap to mode degrees (M-voice conjunct tendency)
        m = tint.m_voice([e.pitch], volume=e.volume)
        snapped = m.pitches[0]
        # Phase 2b: chord-tone quantization per bar (nearest chord tone),
        # using the GRID-LOCKED tick for GLOBAL bar lookup.
        # NOTE (079 bugfix): phase-1 events are SECTION-RELATIVE ticks, so the
        # global bar = s*BARS_PER + (local tick // BAR). Using only the local
        # bar index silently quantized to the wrong chord whenever a section's
        # 4-bar pattern differed from the global progression (e.g. section 2
        # bar 3 = V, not iv).
        local_bar = e.start_tick // BAR
        bar = s * BARS_PER + local_bar
        tones = chord_for_bar(bar if bar < N_BARS else N_BARS - 1)
        qp = quantize_to_chord(snapped, tones)
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

# --- T-voice: tintinnabuli triad shadow below the M-voice ---
# The tintinnabuli T-voice draws ONLY from the E-minor tonic triad (E-G-B).
# To keep the strict harmony invariant (every pitched note in the bar's
# chord), the per-note pool is TRIAD_TONES ∩ bar-chord tones. Since the tonic
# triad shares at least one pitch-class with every diatonic chord of E minor,
# the pool is never empty and the shadow stays consonant + in-chord while
# retaining the tintinnabuli character on tonic bars (full triad).
TRIAD_TONES = [52, 55, 59, 64, 67, 71, 76]   # E-G-B (E-minor tintinnabuli triad), C3-E5
for s in range(N_SECTIONS):
    m_unit = phase2.matrix.get_unit((0, s))
    m_evs = [e for e in m_unit.events if e.pitch > 0]
    evs = []
    # one T note per M-event, nearest in-chord triad tone BELOW the M-pitch
    for e in m_evs:
        # GLOBAL bar lookup (M events are section-relative ticks)
        local_bar = e.start_tick // BAR
        bar = s * BARS_PER + local_bar
        tones = chord_for_bar(bar if bar < N_BARS else N_BARS - 1)
        chord_pcs = {t % 12 for t in tones}
        pool = [t for t in TRIAD_TONES if (t % 12) in chord_pcs and t < e.pitch]
        if not pool:
            pool = [t for t in TRIAD_TONES if (t % 12) in chord_pcs]
        if not pool:
            pool = TRIAD_TONES
        tp = min(pool, key=lambda t: abs(t - e.pitch))
        evs.append(MusicEvent(pitch=tp, volume=max(40, e.volume - 14),
                              start_tick=e.start_tick, end_tick=e.end_tick))
    # grid-lock the T-voice onsets too (already on grid from M, keep clean)
    evs = quantize_lead_to_grid(evs, grid=120)
    phase2.set_unit(1, s, MusicUnit(events=evs))

# --- violin: sustained organum pad following the bar's chord (root + fifth) ---
for bar in range(N_BARS):
    s, b = divmod(bar, BARS_PER)
    tones = chord_for_bar(bar)
    root = tones[0]
    fifth = min(tones, key=lambda t: abs(t - (root + 7)))
    b0 = b * BAR
    evs = [
        MusicEvent(pitch=root + 24, volume=48, start_tick=b0, end_tick=b0 + BAR - 60),
        MusicEvent(pitch=fifth + 24, volume=44, start_tick=b0 + 480, end_tick=b0 + BAR - 60),
    ]
    unit = phase2.matrix.get_unit((2, s))
    events = list(unit.events) if unit is not None else []
    events.extend(evs)
    phase2.set_unit(2, s, MusicUnit(events=events))

# --- double bass: root drone, half notes, sustained ---
for bar in range(N_BARS):
    s, b = divmod(bar, BARS_PER)
    root = BASS[PROG[bar]]
    t0 = b * BAR
    evs = [
        MusicEvent(pitch=root, volume=82, start_tick=t0, end_tick=t0 + BAR - 30),
    ]
    unit = phase2.matrix.get_unit((3, s))
    events = list(unit.events) if unit is not None else []
    events.extend(evs)
    phase2.set_unit(3, s, MusicUnit(events=events))

# --- bells: chord-tone arpeggio accents (color), 8th/16th grid ---
# bells play the bar's chord tones (octave-shifted up) so every pitched note
# stays in the bar's harmony while keeping a bright minimalist color accent.
for s in range(N_SECTIONS):
    evs = []
    for bar_local in range(BARS_PER):
        b0 = bar_local * BAR
        # GLOBAL bar lookup (section-relative cell ticks)
        bar = s * BARS_PER + bar_local
        tones = chord_for_bar(bar)
        bells = [t + 24 for t in tones]
        # 4 hits per bar on 1, 2&, 3, 4& cycling through chord tones
        for k, off in enumerate((0, 720, 960, 1680)):
            tone = bells[(k + s) % len(bells)]
            evs.append(MusicEvent(pitch=tone, volume=70,
                                  start_tick=b0 + off, end_tick=b0 + off + 120))
    phase2.set_unit(4, s, MusicUnit(events=evs))

# --- drums: minimal tintinnabuli pulse (bowed-metal / hand-drum vibe) ---
# soft, sparse: kick on 1, hat on 8ths, snare on 2&4 in movements only
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
        # closed hat 8ths (always, soft)
        for k in range(0, BAR, 240):
            evs.append(MusicEvent(pitch=K["hat_closed"], volume=int(V["hat_closed"] * 0.7),
                                  start_tick=t0 + k, end_tick=t0 + k + 90))
        # kick on 1 (soft)
        evs.append(MusicEvent(pitch=K["kick"], volume=int(V["kick"] * 0.8),
                              start_tick=t0, end_tick=t0 + 160))
        if dens >= 0.8:
            # snare on 2 and 4 (backbeat), soft
            evs.append(MusicEvent(pitch=K["snare"], volume=int(V["snare"] * 0.7),
                                  start_tick=t0 + 480, end_tick=t0 + 620))
            evs.append(MusicEvent(pitch=K["snare"], volume=int(V["snare"] * 0.7),
                                  start_tick=t0 + 1440, end_tick=t0 + 1580))
            if dens >= 1.0:
                # ride cymbal on beat 1
                evs.append(MusicEvent(pitch=K["ride"], volume=int(V["ride"] * 0.8),
                                      start_tick=t0, end_tick=t0 + 600))
    phase2.set_unit(5, s, MusicUnit(events=evs))

# --- voice-leading check on M-voice (rules.voice_leading) ---
from rules.voice_leading import VoiceLeadingRules  # noqa: E402

vlc = VoiceLeadingRules(style="classical")   # strict: parallel 5ths/8ves flagged
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
        if vlc.check_parallel_motion([a.pitch], [b.pitch]):
            pass  # single-voice melodic check only; parallel requires 2+ voices
print("VOICE-LEADING flags (M-voice, classical):", vl_flags[:8], "total", len(vl_flags))

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

P2_MIDI = os.path.join(MIDI_DIR, "079-minimalism-isorhythm.mid")
phase2.to_midi(P2_MIDI)
print("phase2 written", P2_MIDI)

# ---------------------------------------------------------------- analysis
from visualization.grid import write_grid_visualization  # noqa: E402

grid_path = os.path.join(ANALYSIS_DIR, "grid_visualization.txt")
write_grid_visualization(phase2.matrix, grid_path, ticks_per_character=120,
                         voice_names=vnames, bpm=BPM,
                         mode="E natural minor / Method 032 isorhythm + tintinnabuli")
print("grid written", grid_path)

# provenance
from workflows.provenance import write_provenance, AI_GENERATED  # noqa: E402

for mid, phase, note in (
        (P1_MIDI, "1", "raw isorhythmic talea-color walk, unquantized, single voice, no harmony"),
        (P2_MIDI, "2", "mode/triad quantized to E-minor progression, tintinnabuli T-voice, voice-leading check, full texture")):
    write_provenance(
        mid, AI_GENERATED, "Isorhythmic Talea-Color Mapping (Method 032, generators.tintinnabuli)",
        parameters={"bpm": BPM, "key": "E natural minor", "sections": N_SECTIONS,
                    "bars": N_BARS, "phase": phase,
                    "progression": [CHORD_NAMES[r] for r in PROG], "seed": SEED},
        notes=note)
    print("provenance for phase", phase)

# summary.json
with open(os.path.join(ANALYSIS_DIR, "summary.json"), "w") as f:
    json.dump({
        "project": "079-minimalism-isorhythm",
        "style": "Minimalism",
        "method": "032 Isorhythmic Talea-Color Mapping (TintinnabuliGenerator)",
        "bpm": BPM, "key": "E natural minor", "tempo": BPM,
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
