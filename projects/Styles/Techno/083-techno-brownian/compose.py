# -*- coding: utf-8 -*-
"""083-techno-brownian - Techno style / Method 048 Reflected Brownian Motion
Pitch Diffusion (RBMPD).

Two-phase architecture:
  Phase 1: raw generative draft - single-voice Reflected Brownian motion walk.
           Each particle step = Gaussian innovation, drift-biased toward the
           nearest tonic octave; reflecting barriers at [LEAD_LO, LEAD_HI]
           generate the motif repeats and neighbor-tone turns (RBMPD signature).
           Rhythm = random-walk inter-onset spacings (FRACTIONAL ticks,
           OFF-GRID - this is the point of phase 1). Pitches raw (unquantized,
           no scale/chord constraint). No harmony, no bass, no drums.
  Phase 2: musicom rules post-process:
           1. GRID LOCK first: every pitched onset snapped to the 16th grid
              (120 ticks @ 128 BPM) - mandatory rhythm-grid sync (078/079 rule).
           2. Scale snap: raw pitch -> nearest F-natural-minor scale degree.
           3. CHORD-TONE quantization per bar via GLOBAL bar lookup
              (bar = s*BARS_PER + local_bar).
           4. Voice-leading: leap cap <= 9 semitones toward nearest chord tone;
              rules.voice_leading.VoiceLeadingRules(style="classical") check
              on bass+lead per bar-pair.
           5. Texture: organ lead + cello pad + piano offbeat stabs +
              violin counterline + double-bass root pulse + four-on-floor drums.
           6. Zero-drift: every cell normalized to exact section boundary,
              landmark events appended, validate() gate, to_midi().

Engine only: structures + workflows.unitmatrix_composer + rules.voice_leading.
mido used READ-ONLY in audit.py for verification. No raw MIDI authoring.
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
from Keys.organ.organ import MIDI_PROGRAM as ORGAN_PROG  # noqa: E402
from Keys.piano.piano import MIDI_PROGRAM as PIANO_PROG  # noqa: E402
from Strings.cello.cello import MIDI_PROGRAM as CELLO_PROG  # noqa: E402
from Strings.violin.violin import MIDI_PROGRAM as VIOLIN_PROG  # noqa: E402
from Strings.double_bass.double_bass import MIDI_PROGRAM as DBASS_PROG  # noqa: E402
from Percussion.drum_kit.drum_kit import KIT, VELOCITIES  # noqa: E402

SEED = 20260831
rng = np.random.default_rng(SEED)

# ---------------------------------------------------------------- project dirs
PROJ = "/opt/data/projects/Styles/Techno/083-techno-brownian"
MIDI_DIR = os.path.join(PROJ, "MIDI")
AUDIO_DIR = os.path.join(PROJ, "Audio")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")
for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
    os.makedirs(d, exist_ok=True)

# ---------------------------------------------------------------- concept
BPM = 128
TPB = 480
BEATS = 4
BAR = TPB * BEATS            # 1920
GRID16 = 120                 # 16th-note grid @ 480 TPB
# F natural minor (aeolian) pitch set, MIDI 41..89
SCALE = [41, 43, 44, 46, 48, 49, 51, 53, 55, 56, 58, 60, 61, 63, 65, 67,
         68, 70, 72, 73, 75, 77, 79, 80, 82, 84, 85, 87, 89]
SCALE_PCS = set(p % 12 for p in SCALE)      # {0,1,3,5,7,8,10} = F G Ab Bb C Db Eb
LEAD_LO, LEAD_HI = 53, 84                    # organ sweet spot region G3-G5+

# ---------------------------------------------------------------- harmony
# diatonic triads in F natural minor, keyed by root MIDI (octave 3/4)
ROOT_QUAL = {53: "m", 49: "M", 44: "M", 51: "M", 46: "m", 48: "m"}
CHORD_NAMES = {53: "i", 49: "VI", 44: "III", 51: "VII", 46: "iv", 48: "v"}
# bass roots (octave 2/3, all within double-bass range 28..74)
BASS = {53: 41, 49: 37, 44: 32, 51: 39, 46: 34, 48: 36}   # F2 Db2 Ab2 Eb3 Bb2 C2
# cello pad whole-bar triads (octave 3/4)
CELLO_V = {
    53: [53, 56, 60],   # Fm   i   (F3 Ab3 C4)
    49: [49, 53, 56],   # Db   VI  (Db3 F3 Ab3)
    44: [44, 48, 51],   # Ab   III (Ab3 C4 Eb4)
    51: [51, 55, 58],   # Eb   VII (Eb4 G4 Bb4)
    46: [46, 49, 53],   # Bbm  iv  (Bb3 Db4 F4)
    48: [48, 51, 55],   # Cm   v   (C4 Eb4 G4)
}


def chord_intervals(root):
    """Triad intervals (semitones above root): minor (0,3,7), major (0,4,7)."""
    return (0, 3, 7) if ROOT_QUAL[root] == "m" else (0, 4, 7)


def chord_tones(root, lo=48, hi=88):
    """All chord tones spanning octaves within [lo, hi]."""
    tones = set()
    for oct_shift in (-12, 0, 12, 24):
        for i in chord_intervals(root):
            p = root + i + oct_shift
            if lo <= p <= hi:
                tones.add(p)
    return sorted(tones)


def chord_pcs(root):
    return set((root + i) % 12 for i in chord_intervals(root))


def quantize_to_chord(pitch, tones):
    """Snap a pitch to nearest chord tone, resolving ties toward lower."""
    return min(tones, key=lambda c: (abs(c - pitch), c))


# ---------------------------------------------------------------- sections
NAMES = ["Intro", "Build", "Drop", "Break", "Drop2", "Outro"]
BARS_PER = 4
N_SECTIONS = len(NAMES)
N_BARS = N_SECTIONS * BARS_PER            # 24 bars
SECTION_TICKS = BAR * BARS_PER            # 7680

# 24-bar F-minor techno progression: i VI III VII | i iv v i |
#   VI III VII i | i VI III VII | i iv v i | VI III i i
PROG = ([53, 49, 44, 51] + [53, 46, 48, 53] + [49, 44, 51, 53] +
        [53, 49, 44, 51] + [53, 46, 48, 53] + [49, 44, 53, 53])
assert len(PROG) == N_BARS, (len(PROG), N_BARS)


def chord_for_bar(bar):
    return chord_tones(PROG[bar])


# ---------------------------------------------------------------- phase 1
# raw Reflected Brownian motion walk: unquantized rhythm (random-walk
# spacings) + raw unquantized pitch walk with tonic drift + reflecting
# barriers. Single voice, no harmony.
def raw_brownian_melody(seed, duration_ticks, n_events, center):
    r = np.random.default_rng(seed)
    events = []
    # nearest tonic (F) octave anchor for drift bias: F3=53 or F4=65
    anchor = 53 if abs(center - 53) <= abs(center - 65) else 65
    tick = 0.0
    x = float(center)
    drift = 0.0
    for i in range(n_events):
        step = r.normal(drift, 1.9)          # Gaussian innovation
        x += step
        # reflecting barriers -> motif repeats / neighbor-tone turns
        if x < LEAD_LO:
            x = 2 * LEAD_LO - x
        if x > LEAD_HI:
            x = 2 * LEAD_HI - x
        drift = (anchor - x) * 0.02 + 0.12 * r.normal(0.0, 0.3)
        midi = int(round(x))
        # random-walk inter-onset spacing (fractional, OFF-GRID by design)
        spacing = (duration_ticks / float(n_events)) * (0.5 + 1.0 * r.random())
        dur = spacing * (0.6 + 0.6 * r.random())
        st = int(round(tick))
        en = int(round(tick + dur))
        if en > duration_ticks:
            en = duration_ticks
        if en > st:
            vel = int(np.clip(52 + 42 * r.random(), 44, 102))
            events.append(MusicEvent(pitch=midi, volume=vel,
                                     start_tick=st, end_tick=en))
        tick += spacing
    return events


phase1 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
phase1.create_matrix(num_voices=1, num_sections=N_SECTIONS)
phase1.add_voice("LeadRaw", program=ORGAN_PROG, channel=0)

DENSITY = {0: 22, 1: 30, 2: 40, 3: 24, 4: 40, 5: 20}
CENTER = {0: 62.0, 1: 66.0, 2: 72.0, 3: 64.0, 4: 72.0, 5: 60.0}
for s, name in enumerate(NAMES):
    phase1.add_section(name, bars=BARS_PER)
    evs = raw_brownian_melody(SEED + s, SECTION_TICKS, DENSITY[s], CENTER[s])
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
P1_MIDI = os.path.join(MIDI_DIR, "083-techno-brownian-phase1.mid")
phase1.to_midi(P1_MIDI)
print("phase1 written", P1_MIDI)


# ---------------------------------------------------------------- phase 2
# rules post-process: grid lock -> chord-tone quantization -> voice-leading
def quantize_lead_to_grid(events, grid=GRID16):
    """Phase-2 rhythm lock: snap every onset to nearest 16th (120 @ 128 BPM)."""
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
    ("Lead",    ORGAN_PROG,  0),   # Church Organ (Brownian lead)
    ("Cello",   CELLO_PROG,  1),   # Cello (sustained pad)
    ("Piano",   PIANO_PROG,  2),   # Piano (offbeat stabs)
    ("Violin",  VIOLIN_PROG, 3),   # Violin (counterline)
    ("Bass",    DBASS_PROG,  4),   # Double Bass (root pulse)
    ("Drums",   0,            9),  # percussion channel
]
N_V = len(VOICES)
phase2.create_matrix(num_voices=N_V, num_sections=N_SECTIONS)
vnames = [v[0] for v in VOICES]
for name, prog, ch in VOICES:
    phase2.add_voice(name, program=prog, channel=ch)
for n in NAMES:
    phase2.add_section(n, bars=BARS_PER)

# --- lead: GRID LOCK FIRST, then scale snap + chord-tone quantize (078/079 rule)
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
        if bar >= N_BARS:
            bar = N_BARS - 1
        tones = chord_for_bar(bar)
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
            if bar >= N_BARS:
                bar = N_BARS - 1
            tones = chord_for_bar(bar)
            e.pitch = min(tones, key=lambda c: (abs(c - p_prev), c))
    phase2.set_unit(0, s, MusicUnit(events=q_events))

# --- cello: sustained pad, whole-bar triad (octave 3/4)
for bar in range(N_BARS):
    s, b = divmod(bar, BARS_PER)
    tones = CELLO_V[PROG[bar]]
    t0 = b * BAR
    e = []
    for k, p in enumerate(tones):
        e.append(MusicEvent(pitch=p, volume=52 + 4 * k,
                            start_tick=t0, end_tick=t0 + BAR - 90))
    unit = phase2.matrix.get_unit((1, s))
    events = list(unit.events) if unit is not None else []
    events.extend(e)
    phase2.set_unit(1, s, MusicUnit(events=events))

# --- piano: offbeat 16th stabs (chord tones +12), techno staccato
for bar in range(N_BARS):
    s, b = divmod(bar, BARS_PER)
    tones = [t + 12 for t in chord_tones(PROG[bar], lo=48, hi=76)]
    t0 = b * BAR
    e = []
    # offbeats: the "and" of every 8th (t0+120, +360, ...) - 16th-aligned
    for k in range(0, BAR, 240):
        off = t0 + k + 120
        p = tones[(off // 120) % len(tones)]
        e.append(MusicEvent(pitch=p, volume=58,
                            start_tick=off, end_tick=off + 90))
    unit = phase2.matrix.get_unit((2, s))
    events = list(unit.events) if unit is not None else []
    events.extend(e)
    phase2.set_unit(2, s, MusicUnit(events=events))

# --- violin: 8th-note counterline, chord tones +12, seedy perlin choice
for s in range(N_SECTIONS):
    r = np.random.default_rng(SEED + 200 + s)
    evs = []
    for bar in range(BARS_PER):
        t0 = bar * BAR
        tones = [t + 12 for t in chord_tones(PROG[s * BARS_PER + bar], lo=48, hi=76)]
        for k in range(0, BAR, 240):
            idx = int(r.integers(0, len(tones)))
            p = tones[idx]
            vel = int(np.clip(46 + 20 * abs(np.sin(k * 0.05 + s)), 40, 80))
            evs.append(MusicEvent(pitch=p, volume=vel,
                                  start_tick=t0 + k, end_tick=t0 + k + 170))
    phase2.set_unit(3, s, MusicUnit(events=evs))

# --- bass: root pulse. 8th-note pulse in Drop/Drop2, quarters elsewhere;
#     16th push at bar end in Build/Drop/Drop2. All on-grid.
BASS_8TH = {2, 4}          # sections with 8th pulse
BASS_PUSH = {1, 2, 4}      # sections with 16th end-push
for bar in range(N_BARS):
    s, b = divmod(bar, BARS_PER)
    root = BASS[PROG[bar]]
    t0 = b * BAR
    e = []
    step = 240 if s in BASS_8TH else 480
    for k in range(0, BAR, step):
        e.append(MusicEvent(pitch=root, volume=80,
                            start_tick=t0 + k, end_tick=t0 + k + step - 30))
    if s in BASS_PUSH and bar % BARS_PER != BARS_PER - 1:
        e.append(MusicEvent(pitch=root, volume=72,
                            start_tick=t0 + BAR - 120, end_tick=t0 + BAR - 10))
    unit = phase2.matrix.get_unit((4, s))
    events = list(unit.events) if unit is not None else []
    events.extend(e)
    phase2.set_unit(4, s, MusicUnit(events=events))

# --- drums: techno four-on-floor. Drop/Drop2 full drive; Intro/Break/Outro sparse.
K = KIT
V = VELOCITIES
DRUM_PLAN = {
    0: dict(hat=38, kick=58, snare=None, clap=None, ride=None, crash=False, hat16=False),
    1: dict(hat=48, kick=82, snare=68, clap=None, ride=38, crash=False, hat16=False),
    2: dict(hat=56, kick=94, snare=88, clap=82, ride=None, crash=True, hat16=True),
    3: dict(hat=40, kick=62, snare=None, clap=None, ride=None, crash=False, hat16=False),
    4: dict(hat=56, kick=94, snare=88, clap=82, ride=None, crash=True, hat16=True),
    5: dict(hat=34, kick=70, snare=None, clap=None, ride=None, crash=False, hat16=False),
}
for s in range(N_SECTIONS):
    plan = DRUM_PLAN[s]
    evs = []
    for bar in range(BARS_PER):
        t0 = bar * BAR
        hat_step = 120 if plan["hat16"] else 240
        for k in range(0, BAR, hat_step):
            evs.append(MusicEvent(pitch=K["hat_closed"], volume=plan["hat"],
                                  start_tick=t0 + k, end_tick=t0 + k + 60))
        # kick: four-on-floor in drops (every beat), else 1&3
        kick_beats = (0, 480, 960, 1440) if plan["hat16"] else (0, 960)
        for kb in kick_beats:
            evs.append(MusicEvent(pitch=K["kick"], volume=plan["kick"],
                                  start_tick=t0 + kb, end_tick=t0 + kb + 130))
        if plan["snare"] is not None:
            for sb in (960, 2880):
                evs.append(MusicEvent(pitch=K["snare"], volume=plan["snare"],
                                      start_tick=t0 + sb, end_tick=t0 + sb + 120))
        if plan["clap"] is not None:
            for sb in (960, 2880):
                evs.append(MusicEvent(pitch=K["clap"], volume=plan["clap"],
                                      start_tick=t0 + sb, end_tick=t0 + sb + 120))
        if plan["ride"] is not None:
            evs.append(MusicEvent(pitch=K["ride"], volume=plan["ride"],
                                  start_tick=t0, end_tick=t0 + 480))
        if plan["crash"]:
            evs.append(MusicEvent(pitch=K["crash"], volume=64,
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
    tones = sorted(chord_tones(PROG[bar + 1], lo=48, hi=88))
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

P2_MIDI = os.path.join(MIDI_DIR, "083-techno-brownian.mid")
phase2.to_midi(P2_MIDI)
print("phase2 written", P2_MIDI)

# ---------------------------------------------------------------- analysis
from visualization.grid import write_grid_visualization  # noqa: E402

grid_path = os.path.join(ANALYSIS_DIR, "grid_visualization.txt")
write_grid_visualization(phase2.matrix, grid_path, ticks_per_character=120,
                         voice_names=vnames, bpm=BPM,
                         mode="F minor / Method 048 RBMPD + techno texture")
print("grid written", grid_path)

# provenance
from workflows.provenance import write_provenance, AI_GENERATED  # noqa: E402

for mid, phase, note in (
        (P1_MIDI, "1", "raw Reflected Brownian motion walk: Gaussian innovations, tonic-drift bias, reflecting barriers, random-walk fractional-tick spacings (off-grid rhythm), unquantized pitches, single voice, no harmony"),
        (P2_MIDI, "2", "16th-grid locked, chord-tone quantized to F-minor techno progression, organ/cello/piano/violin/bass/four-on-floor drums texture, voice-leading check, full arrangement")):
    write_provenance(
        mid, AI_GENERATED, "Reflected Brownian Motion Pitch Diffusion (Method 048)",
        parameters={"bpm": BPM, "key": "F minor", "sections": N_SECTIONS,
                    "bars": N_BARS, "phase": phase,
                    "progression": [CHORD_NAMES[r] for r in PROG], "seed": SEED,
                    "grid16": GRID16, "drift_bias": 0.02, "barrier_reflect": True},
        notes=note)
    print("provenance for phase", phase)

# voice-leading audit
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
        "project": "083-techno-brownian",
        "style": "Techno",
        "method": "048 Reflected Brownian Motion Pitch Diffusion (RBMPD)",
        "bpm": BPM, "key": "F minor", "tempo": BPM,
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
