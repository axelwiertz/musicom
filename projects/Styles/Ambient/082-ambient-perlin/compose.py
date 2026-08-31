# -*- coding: utf-8 -*-
"""082-ambient-perlin - Ambient style / Method 040 Perlin Noise Composition.

Two-phase composition:
  Phase 1: raw Perlin fBm walk - single-voice melodic draft whose rhythm comes
           from Perlin-modulated event spacings (fractional, OFF-GRID ticks)
           and whose pitches come from fractal Brownian motion contours
           (unquantized, no scale/chord constraint). Raw generative character.
  Phase 2: musicom rules post-process - rhythm locked to the 16th grid
           (120 ticks @ 72 BPM), chord-tone quantization per bar to a
           D-minor ambient progression (i VI III VII / i iv v i ...),
           voice-leading checks via rules.voice_leading (bass + lead),
           full ambient texture: flute lead + cello pad + violin counterline
           + piano arpeggio comp + double-bass root + soft pulse drums.

Engine only: structures + workflows.unitmatrix_composer + rules.voice_leading.
validate() gate + to_midi(). No raw mido authoring (mido read-only for audit).
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

# instrument library constants (read-only)
sys.path.insert(0, "/opt/data/projects/Instruments")
from Woodwind.flute.flute import MIDI_PROGRAM as FLUTE_PROG  # noqa: E402
from Strings.cello.cello import MIDI_PROGRAM as CELLO_PROG  # noqa: E402
from Strings.violin.violin import MIDI_PROGRAM as VIOLIN_PROG  # noqa: E402
from Strings.double_bass.double_bass import MIDI_PROGRAM as DBASS_PROG  # noqa: E402
from Keys.piano.piano import MIDI_PROGRAM as PIANO_PROG  # noqa: E402
from Percussion.drum_kit.drum_kit import KIT, VELOCITIES  # noqa: E402

SEED = 20260830
rng = np.random.default_rng(SEED)

# ---------------------------------------------------------------- project dirs
PROJ = "/opt/data/projects/Styles/Ambient/082-ambient-perlin"
MIDI_DIR = os.path.join(PROJ, "MIDI")
AUDIO_DIR = os.path.join(PROJ, "Audio")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")
for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
    os.makedirs(d, exist_ok=True)

# ---------------------------------------------------------------- concept
BPM = 72
TPB = 480
BEATS = 4
BAR = TPB * BEATS            # 1920
GRID16 = 120                 # 16th-note grid @ 480 TPB
# D natural minor (aeolian) pitch set, MIDI 36..96
SCALE = [38, 40, 41, 43, 45, 46, 48, 50, 52, 53, 55, 57, 58, 60,
         62, 64, 65, 67, 69, 70, 72, 74, 76, 77, 79, 81, 82, 84]
LEAD_LO, LEAD_HI = 62, 88

# diatonic triads in D minor, keyed by root MIDI
CHORDS = {
    62: [62, 65, 69],   # Dm   i
    70: [70, 74, 77],   # Bb   VI
    65: [65, 69, 72],   # F    III
    72: [72, 76, 79],   # C    VII
    67: [67, 70, 74],   # Gm   iv
    69: [69, 72, 76],   # Am   v
}
ROOTS = [62, 70, 65, 72, 67, 69]
BASS = {62: 38, 70: 46, 65: 41, 72: 36, 67: 43, 69: 45}   # octave 2
CELLO_V = {62: [50, 53, 57], 70: [58, 62, 65], 65: [53, 57, 60],
           72: [60, 64, 67], 67: [55, 58, 62], 69: [57, 60, 64]}  # octave 3

# ---------------------------------------------------------------- sections
NAMES = ["Intro", "DriftA", "Rise", "DriftB", "Pulse", "Outro"]
BARS_PER = 4
N_SECTIONS = len(NAMES)
N_BARS = N_SECTIONS * BARS_PER            # 24 bars
SECTION_TICKS = BAR * BARS_PER            # 7680

# 24-bar D-minor ambient progression: i VI III VII | i iv v i |
#   VI III VII i | i VI III VII | i iv v i | VI III i i
PROG = ([62, 70, 65, 72] + [62, 67, 69, 62] + [70, 65, 72, 62] +
        [62, 70, 65, 72] + [62, 67, 69, 62] + [70, 65, 62, 62])
assert len(PROG) == N_BARS, (len(PROG), N_BARS)
CHORD_NAMES = {62: "i", 70: "VI", 65: "III", 72: "VII", 67: "iv", 69: "v"}


def chord_for_bar(bar):
    return CHORDS[PROG[bar]]


def quantize_to_chord(pitch, chord_tones):
    """Snap a pitch to nearest chord tone, resolving ties toward lower."""
    return min(chord_tones, key=lambda c: (abs(c - pitch), c))


# ---------------------------------------------------------------- perlin noise
def perlin1d(x, seed):
    """1D Perlin gradient noise, seeded, output ~[-1, 1]."""
    x = np.asarray(x, dtype=np.float64)
    i = np.floor(x).astype(np.int64)
    frac = x - i
    u = frac * frac * (3.0 - 2.0 * frac)      # smoothstep

    def grad(n):
        h = (n * 374761393 + seed * 668265263) & 0xFFFFFFFF
        h = (h ^ (h >> 13)) * 1274126177 & 0xFFFFFFFF
        return (h & 0x7FFFFFFF) / float(0x7FFFFFFF) * 2.0 - 1.0

    g0 = grad(i)
    g1 = grad(i + 1)
    return g0 * (1.0 - u) + g1 * u


def fbm(x, seed, octaves=4, lacunarity=2.0, gain=0.5):
    """Fractal Brownian motion: sum of Perlin octaves, output ~[-1, 1]."""
    total = np.zeros_like(np.asarray(x, dtype=np.float64))
    amp = 1.0
    freq = 1.0
    for o in range(octaves):
        total += amp * perlin1d(np.asarray(x) * freq, seed + o * 101)
        amp *= gain
        freq *= lacunarity
    return total


# ---------------------------------------------------------------- phase 1
# raw Perlin fBm walk: unquantized rhythm (Perlin-modulated spacings) +
# raw fBm pitch contour, single voice, no harmony.
def raw_perlin_melody(seed, duration_ticks, n_events, center0):
    """Single-voice raw Perlin walk (off-grid rhythm + raw pitches)."""
    r = np.random.default_rng(seed)
    events = []
    t_idx = np.arange(n_events, dtype=np.float64)
    # Perlin density field -> event spacings (fractional, off-grid)
    dens = 0.5 + 0.5 * fbm(t_idx * 0.45 + seed % 13, seed + 7, octaves=3)
    base = duration_ticks / float(n_events)
    tick = 0.0
    center = center0
    for i in range(n_events):
        spacing = base * (0.55 + 0.95 * dens[i])
        spacing *= (0.9 + 0.3 * r.random())
        dur = spacing * (0.8 + 0.4 * r.random())
        # pitch: fBm contour + slow macro layer + register drift
        p = center + 6.0 * fbm(np.array([i * 0.35]), seed)[0]
        p += 3.0 * fbm(np.array([i * 0.11]), seed + 3)[0]
        p = max(LEAD_LO, min(LEAD_HI, p))
        midi = int(round(p))
        vel = int(np.clip(55 + 40 * abs(math.sin(i * 1.7)), 42, 108))
        st = int(round(tick))
        en = int(round(tick + dur))
        if en > duration_ticks:
            en = duration_ticks
        if en > st:
            events.append(MusicEvent(pitch=midi, volume=vel,
                                     start_tick=st, end_tick=en))
        tick += spacing
        center += r.normal(0.0, 0.55)
    return events


phase1 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
phase1.create_matrix(num_voices=1, num_sections=N_SECTIONS)
phase1.add_voice("LeadRaw", program=FLUTE_PROG, channel=0)

DENSITY = {0: 18, 1: 26, 2: 34, 3: 26, 4: 30, 5: 16}
CENTER = {0: 70.0, 1: 73.0, 2: 76.0, 3: 73.0, 4: 74.0, 5: 69.0}
for s, name in enumerate(NAMES):
    phase1.add_section(name, bars=BARS_PER)
    evs = raw_perlin_melody(SEED + s, SECTION_TICKS, DENSITY[s], CENTER[s])
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
P1_MIDI = os.path.join(MIDI_DIR, "082-ambient-perlin-phase1.mid")
phase1.to_midi(P1_MIDI)
print("phase1 written", P1_MIDI)


# ---------------------------------------------------------------- phase 2
# rules post-process: grid lock -> chord-tone quantization -> voice-leading
def quantize_lead_to_grid(events, grid=GRID16):
    """Phase-2 rhythm lock: snap every onset to nearest 16th (120 @ 72 BPM)."""
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
    ("Lead",    FLUTE_PROG,  0),   # Flute (Perlin lead)
    ("Cello",   CELLO_PROG,  1),   # Cello (sustained pad)
    ("Violin",  VIOLIN_PROG, 2),   # Violin (counterline)
    ("Piano",   PIANO_PROG,  3),   # Piano (arpeggio comp)
    ("Bass",    DBASS_PROG,  4),   # Double Bass (root)
    ("Drums",   0,            9),  # percussion channel
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
    raw_events = quantize_lead_to_grid(raw_events, grid=GRID16)
    q_events = []
    for e in raw_events:
        if e.pitch == 0:
            q_events.append(e)
            continue
        sc = min(SCALE, key=lambda c: (abs(c - e.pitch), c))
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

# --- cello: sustained pad, whole-bar chord tones (octave 3) ---
for bar in range(N_BARS):
    s, b = divmod(bar, BARS_PER)
    tones = CELLO_V[PROG[bar]]
    t0 = b * BAR
    e = []
    for k, p in enumerate(tones):
        e.append(MusicEvent(pitch=p, volume=58 + 4 * k,
                            start_tick=t0, end_tick=t0 + BAR - 90))
    unit = phase2.matrix.get_unit((1, s))
    events = list(unit.events) if unit is not None else []
    events.extend(e)
    phase2.set_unit(1, s, MusicUnit(events=events))

# --- violin: counterline on 8th grid (240), chord tones +12, perlin-chosen ---
for s in range(N_SECTIONS):
    r = np.random.default_rng(SEED + 100 + s)
    evs = []
    for bar in range(BARS_PER):
        t0 = bar * BAR
        tones = [t + 12 for t in CHORDS[PROG[s * BARS_PER + bar]]]
        for k in range(0, BAR, 240):
            idx = int(r.integers(0, len(tones)))
            p = tones[idx]
            vel = int(np.clip(50 + 22 * abs(math.sin(k * 0.05 + s)), 40, 84))
            evs.append(MusicEvent(pitch=p, volume=vel,
                                  start_tick=t0 + k, end_tick=t0 + k + 190))
    phase2.set_unit(2, s, MusicUnit(events=evs))

# --- piano: soft 8th-note arpeggio comp (root-5th-3rd-5th), octave 4 ---
for bar in range(N_BARS):
    s, b = divmod(bar, BARS_PER)
    tones = [t + 12 for t in CHORDS[PROG[bar]]]
    root, third, fifth = tones[0], tones[1], tones[2]
    t0 = b * BAR
    e = []
    seq = [root, fifth, third, fifth]
    for k in range(0, BAR, 240):
        p = seq[(k // 240) % 4]
        e.append(MusicEvent(pitch=p, volume=46,
                            start_tick=t0 + k, end_tick=t0 + k + 170))
    unit = phase2.matrix.get_unit((3, s))
    events = list(unit.events) if unit is not None else []
    events.extend(e)
    phase2.set_unit(3, s, MusicUnit(events=events))

# --- bass: whole-bar root (double bass octave 2), gentle pulse ---
for bar in range(N_BARS):
    s, b = divmod(bar, BARS_PER)
    root = BASS[PROG[bar]]
    t0 = b * BAR
    e = [MusicEvent(pitch=root, volume=74,
                    start_tick=t0, end_tick=t0 + BAR - 90)]
    unit = phase2.matrix.get_unit((4, s))
    events = list(unit.events) if unit is not None else []
    events.extend(e)
    phase2.set_unit(4, s, MusicUnit(events=events))

# --- drums: soft ambient pulse. hat 8ths always; kick 1&3 + ride 1 in
#     Rise/Pulse; ride 1 only in DriftA/DriftB; Intro/Outro hat shimmer. ---
K = KIT
V = VELOCITIES
DRUM_PLAN = {
    0: dict(hat=30, kick=None, ride=None),
    1: dict(hat=34, kick=40, ride=38),
    2: dict(hat=42, kick=50, ride=44),
    3: dict(hat=34, kick=40, ride=38),
    4: dict(hat=46, kick=54, ride=48),
    5: dict(hat=26, kick=None, ride=None),
}
for s in range(N_SECTIONS):
    plan = DRUM_PLAN[s]
    evs = []
    for bar in range(BARS_PER):
        t0 = bar * BAR
        for k in range(0, BAR, 240):
            evs.append(MusicEvent(pitch=K["hat_closed"], volume=plan["hat"],
                                  start_tick=t0 + k, end_tick=t0 + k + 80))
        if plan["kick"] is not None:
            evs.append(MusicEvent(pitch=K["kick"], volume=plan["kick"],
                                  start_tick=t0, end_tick=t0 + 140))
            evs.append(MusicEvent(pitch=K["kick"], volume=int(plan["kick"] * 0.85),
                                  start_tick=t0 + 960, end_tick=t0 + 1100))
        if plan["ride"] is not None:
            evs.append(MusicEvent(pitch=K["ride"], volume=plan["ride"],
                                  start_tick=t0, end_tick=t0 + 540))
    phase2.set_unit(5, s, MusicUnit(events=evs))

# --- voice-leading check (rules.voice_leading): bass + lead per bar-pair ---
from rules.voice_leading import VoiceLeadingRules  # noqa: E402

vlc = VoiceLeadingRules(style="classical")
vl_flags = []
for bar in range(N_BARS - 1):
    s, b = divmod(bar, BARS_PER)
    bass_a = BASS[PROG[bar]]
    bass_b = BASS[PROG[bar + 1]]
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


def fix_hidden_fifth(phase2, bar):
    """Nudge lead's first note of bar+1 off the hidden-fifth relation with the
    bass: pick a chord tone of bar+1 that is not a 5th/8ve above the bass."""
    s, b = divmod(bar + 1, BARS_PER)
    if b >= BARS_PER:
        return False
    u = phase2.matrix.get_unit((0, s))
    evs = list(u.events)
    target = None
    for e in evs:
        if e.pitch > 0 and b * BAR <= e.start_tick < (b + 1) * BAR:
            target = e
            break
    if target is None:
        return False
    tones = sorted(CHORDS[PROG[bar + 1]])
    bass = BASS[PROG[bar + 1]]
    cands = [t for t in tones if abs((t - bass) % 12) not in (0, 7)]
    if not cands:
        return False
    target.pitch = min(cands, key=lambda c: (abs(c - target.pitch), c))
    phase2.set_unit(0, s, MusicUnit(events=evs))
    return True


for (bar, _viol) in list(vl_flags):
    if fix_hidden_fifth(phase2, bar):
        print("VL fix applied at bar", bar)

# re-run voice-leading check after corrections
vl_flags2 = []
for bar in range(N_BARS - 1):
    s, b = divmod(bar, BARS_PER)
    bass_a = BASS[PROG[bar]]
    bass_b = BASS[PROG[bar + 1]]
    u = phase2.matrix.get_unit((0, s))
    evs = [e for e in u.events if e.pitch > 0 and b * BAR <= e.start_tick < (b + 1) * BAR]
    evs_next = [e for e in u.events if e.pitch > 0 and (b + 1) * BAR <= e.start_tick < (b + 2) * BAR]
    if evs and evs_next:
        lead_a = evs[0].pitch
        lead_b = evs_next[0].pitch
        viol = vlc.check_parallel_motion([bass_a, lead_a], [bass_b, lead_b])
        if viol:
            vl_flags2.append((bar, viol))
        hid = vlc.check_hidden_fifths([bass_a, lead_a], [bass_b, lead_b])
        if hid:
            vl_flags2.append((bar, hid))
print("VOICE-LEADING re-check (after fixes):", vl_flags2[:8], "total", len(vl_flags2))
vl_flags = vl_flags2


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

P2_MIDI = os.path.join(MIDI_DIR, "082-ambient-perlin.mid")
phase2.to_midi(P2_MIDI)
print("phase2 written", P2_MIDI)

# ---------------------------------------------------------------- analysis
from visualization.grid import write_grid_visualization  # noqa: E402

grid_path = os.path.join(ANALYSIS_DIR, "grid_visualization.txt")
write_grid_visualization(phase2.matrix, grid_path, ticks_per_character=120,
                         voice_names=vnames, bpm=BPM,
                         mode="D minor / Method 040 Perlin fBm + ambient texture")
print("grid written", grid_path)

# provenance
from workflows.provenance import write_provenance, AI_GENERATED  # noqa: E402

for mid, phase, note in (
        (P1_MIDI, "1", "raw Perlin fBm walk: Perlin-modulated fractional-tick spacings (off-grid rhythm), fBm pitch contour, single voice, no harmony"),
        (P2_MIDI, "2", "16th-grid locked, chord-tone quantized to D-minor ambient progression, cello/violin/piano/bass/drums texture, voice-leading check, full arrangement")):
    write_provenance(
        mid, AI_GENERATED, "Perlin Noise Composition (Method 040, fBm gradient noise)",
        parameters={"bpm": BPM, "key": "D minor", "sections": N_SECTIONS,
                    "bars": N_BARS, "phase": phase,
                    "progression": [CHORD_NAMES[r] for r in PROG], "seed": SEED,
                    "grid16": GRID16, "octaves": 4},
        notes=note)
    print("provenance for phase", phase)

# ---------------------------------------------------------------- audits
# NOTE: mido-based read-only grid/harmony audits live in audit.py (separate
# file, like 081) so compose.py stays engine-only and preflight-clean.
# compose.py writes the voice-leading audit here; audit.py merges it with the
# grid/harmony audits and writes Analysis/audit.json.
with open(os.path.join(ANALYSIS_DIR, "vl_audit.json"), "w") as f:
    json.dump({
        "voice_leading_flags": [str(x) for x in vl_flags],
        "voice_leading_flag_count": len(vl_flags),
        "phase1_validate": msg1,
        "phase2_validate": msg2,
    }, f, indent=2)
print("vl_audit.json written")

# summary.json
with open(os.path.join(ANALYSIS_DIR, "summary.json"), "w") as f:
    json.dump({
        "project": "082-ambient-perlin",
        "style": "Ambient",
        "method": "040 Perlin Noise Composition (fBm gradient noise)",
        "bpm": BPM, "key": "D minor", "tempo": BPM,
        "bars": N_BARS,
        "sections": {n: BARS_PER for n in NAMES},
        "progression": [CHORD_NAMES[r] for r in PROG],
        "voices": vnames,
        "phase1": os.path.basename(P1_MIDI),
        "phase2": os.path.basename(P2_MIDI),
        "grid": os.path.basename(grid_path),
        "seed": SEED,
        "octaves": 4,
    }, f, indent=2)
print("summary.json written")

# ---------------------------------------------------------------- size asserts
for p in (P1_MIDI, P2_MIDI, grid_path,
          os.path.join(ANALYSIS_DIR, "summary.json"),
          os.path.join(ANALYSIS_DIR, "audit.json")):
    assert os.path.getsize(p) > 40, "too small: %s" % p
print("ALL SIZE ASSERTS PASSED")
print("PROGRESSION:", [CHORD_NAMES[r] for r in PROG])
