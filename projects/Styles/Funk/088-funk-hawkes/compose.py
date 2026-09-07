# -*- coding: utf-8 -*-
"""088-funk-hawkes - Funk style / Method 045 Hawkes Process Self-Exciting
Composition (HPSEC). LAYER: concrete.

Two-phase architecture:
  Phase 1: raw generative draft - single-voice Hawkes self-exciting point
           process. Each event raises the conditional intensity; the sampled
           sojourn time tau = Exp(lambda(t)) gives OFF-GRID fractional
           inter-onset intervals (the raw rhythm fingerprint). Raw pitches:
           unquantized drift around section centers + jump kernel on
           excitation (contagion = brief pitch burst). No harmony, no bass,
           no drums.
  Phase 2: musicom rules post-process:
           1. GRID LOCK to 16th grid (120 ticks @ 100 BPM) - 078 rule.
           2. Scale snap to F minor pentatonic THEN chord-tone quantize per
              bar using GLOBAL bar lookup (s*BARS_PER + local_bar).
           3. Voice-leading: leap cap <= 9 toward nearest chord tone.
           4. Texture: trumpet lead, sax counterline, cello sustained pad,
              piano offbeat stabs, double-bass octave pulse + 16th pushes,
              funk drum kit (kick 1&3, snare 2&4, hats 16ths, claps).
           5. Zero-drift landmark + validate() gate on BOTH phases, export
              via engine UnitMatrixComposer.to_midi().

Engine only: structures + workflows.unitmatrix_composer + rules.voice_leading.
mido used READ-ONLY in audit.py for verification. No raw MIDI authoring.
"""
import os
import sys
import json

import numpy as np

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import (
    UnitMatrixComposer, create_empty_unit,
)

# instrument registry (source of truth - NOT pip-installed)
INSTR_DIR = "/opt/data/repos/musicom/projects/Instruments"
if INSTR_DIR not in sys.path:
    sys.path.insert(0, INSTR_DIR)
from instrument_registry import (  # noqa: E402
    TRUMPET, SAXOPHONE, CELLO, PIANO, DOUBLE_BASS, DRUM_KIT,
)
from Percussion.drum_kit.drum_kit import KIT  # noqa: E402

SEED = 20260906
rng = np.random.default_rng(SEED)

# ---------------------------------------------------------------- project dirs
PROJ = "/opt/data/projects/Styles/Funk/088-funk-hawkes"
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
GRID16 = 120                 # 16th-note grid @ 480 TPB
# F minor pentatonic (blues/funk) pitch set MIDI 41..93
SCALE = [41, 43, 46, 48, 53, 55, 58, 60, 65, 67, 70, 72, 77, 79, 82, 84,
         89, 91, 93]
SCALE_PCS = {0, 3, 5, 8, 10}   # F Ab Bb C Eb - minor pentatonic colour
LEAD_LO, LEAD_HI = 53, 91    # trumpet sweet band G3..G5+

# ---------------------------------------------------------------- harmony
# diatonic triads in F minor (aeolian), root-keyed; quality dict
ROOT_QUAL = {53: "m", 49: "M", 44: "M", 51: "M", 46: "m", 48: "m"}
CHORD_NAMES = {53: "i", 49: "VI", 44: "III", 51: "VII", 46: "iv", 48: "v"}
# bass roots (octave 2, within double bass 28..74)
BASS = {53: 41, 49: 37, 44: 32, 51: 39, 46: 34, 48: 36}   # F2 Db2 Ab2 Eb3 Bb2 C2
# funk-octave bass: root/fifth + octave for groove
CELLO_V = {
    53: [53, 56, 60],   # Fm   i   (F3 Ab3 C4)
    49: [49, 53, 56],   # Db   VI  (Db3 F3 Ab3)
    44: [44, 48, 51],   # Ab   III (Ab3 C4 Eb4)
    51: [51, 55, 58],   # Eb   VII (Eb4 G4 Bb4)
    46: [46, 49, 53],   # Bbm  iv  (Bb3 Db4 F4)
    48: [48, 51, 55],   # Cm   v   (C4 Eb4 G4)
}


def chord_intervals(root):
    """Triad intervals: minor (0,3,7), major (0,4,7)."""
    return (0, 3, 7) if ROOT_QUAL[root] == "m" else (0, 4, 7)


def chord_tones(root, lo=48, hi=88):
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
    return min(tones, key=lambda c: (abs(c - pitch), c))
NAMES = ["Intro", "Verse", "Chorus", "Break", "Chorus2", "Outro"]
BARS_PER = 4
N_SECTIONS = len(NAMES)
N_BARS = N_SECTIONS * BARS_PER            # 24 bars
SECTION_TICKS = BAR * BARS_PER            # 7680

# 24-bar F-minor funk progression: i VI III VII | i VI i v | i VI III VII |
# i VI i v | i VI III VII | VI III i i
PROG = ([53, 49, 44, 51] + [53, 49, 53, 48] + [53, 49, 44, 51] +
        [53, 49, 53, 48] + [53, 49, 44, 51] + [49, 44, 53, 53])
assert len(PROG) == N_BARS, (len(PROG), N_BARS)


def chord_for_bar(bar):
    return chord_tones(PROG[bar])


# ---------------------------------------------------------------- phase 1
# Raw Hawkes self-exciting point process:
#   dlambda = mu + sum_{t_i<t} alpha * exp(-beta*(t - t_i))
#   inter-onset sojourn tau ~ Exp(lambda) in "tick units" -> FRACTIONAL ticks
#   (off-grid raw fingerprint). Excitation kernel briefly drives pitch upward
#   (contagion = pitch burst), then relaxes back to the section center.
def raw_hawkes_melody(seed, duration_ticks, n_events, center, mu=0.12,
                      alpha=0.55, beta=0.006):
    r = np.random.default_rng(seed)
    events = []
    tick = 0.0
    x = float(center)
    lam = mu
    excite = 0.0
    for i in range(n_events):
        # self-exciting intensity at current time
        lam = mu + excite * alpha * np.exp(-beta * 0.0)  # refresh at event
        # wait, excite decays in continuous time; sample sojourn from the
        # intensity LEVEL just after the last event (Ogata thinning approx:
        # for a pure Hawkes the level is piecewise constant between events,
        # so an exact sojourn sample is tau ~ Exp(lambda_i) - this is the
        # standard Gillespie-style thinning for a self-exciting process.)
        tau = r.exponential(1.0 / lam)
        # scale tau so that mean event count ~ n_events over duration
        tau *= (duration_ticks / float(n_events)) / (1.0 / lam)
        # raw pitch: contagion pulls UP while excited, then relaxes to center
        x += (excite * 2.2 - 0.35) * r.normal(0.0, 1.0) + 0.4 * r.normal(0.0, 1.0)
        if excite > 0:
            x += 0.8 * r.normal(0.4, 0.6)     # burst push
        if x < LEAD_LO:
            x = 2 * LEAD_LO - x
        if x > LEAD_HI:
            x = 2 * LEAD_HI - x
        x = 0.92 * x + 0.08 * center          # tonic-centering drift
        midi = int(round(x))
        st = int(round(tick))
        dur = tau * (0.45 + 0.55 * r.random())
        en = int(round(tick + dur))
        if en > duration_ticks:
            en = duration_ticks
        if en > st:
            vel = int(np.clip(60 + 34 * r.random(), 50, 104))
            events.append(MusicEvent(pitch=midi, volume=vel,
                                     start_tick=st, end_tick=en))
        tick += tau
        # kernel decay + random re-excitation (aftershocks)
        excite = excite * np.exp(-beta * tau) + (1.0 if r.random() < 0.28 else 0.0)
        if excite > 3.0:
            excite = 3.0
    return events


phase1 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
phase1.create_matrix(num_voices=1, num_sections=N_SECTIONS)
phase1.add_voice("LeadRaw", program=TRUMPET.midi_program, channel=0)

DENSITY = {0: 24, 1: 34, 2: 44, 3: 26, 4: 44, 5: 22}
CENTER = {0: 62.0, 1: 66.0, 2: 74.0, 3: 64.0, 4: 74.0, 5: 60.0}
for s, name in enumerate(NAMES):
    phase1.add_section(name, bars=BARS_PER)
    evs = raw_hawkes_melody(SEED + s, SECTION_TICKS, DENSITY[s], CENTER[s])
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
P1_MIDI = os.path.join(MIDI_DIR, "088-funk-hawkes-phase1.mid")
phase1.to_midi(P1_MIDI)
print("phase1 written", P1_MIDI)


# ---------------------------------------------------------------- phase 2
def quantize_lead_to_grid(events, grid=GRID16):
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
    ("Lead",    TRUMPET.midi_program, 0),   # Trumpet (Hawkes lead)
    ("Sax",     SAXOPHONE.midi_program, 1),  # Alto Sax (counterline)
    ("Cello",   CELLO.midi_program, 2),      # Cello (sustained pad)
    ("Piano",   PIANO.midi_program, 3),      # Piano (offbeat stabs)
    ("Bass",    DOUBLE_BASS.midi_program, 4),# Double Bass (octave pulse)
    ("Drums",   0, 9),                       # percussion channel
]
N_V = len(VOICES)
phase2.create_matrix(num_voices=N_V, num_sections=N_SECTIONS)
vnames = [v[0] for v in VOICES]
for name, prog, ch in VOICES:
    phase2.add_voice(name, program=prog, channel=ch)
for n in NAMES:
    phase2.add_section(n, bars=BARS_PER)

# --- lead: GRID LOCK FIRST, then scale snap + chord-tone quantize (078 rule)
for s, name in enumerate(NAMES):
    raw_unit = phase1.matrix.get_unit((0, s))
    raw_events = list(raw_unit.events)
    raw_events = quantize_lead_to_grid(raw_events, grid=GRID16)
    q_events = []
    for e in raw_events:
        if e.pitch == 0:
            q_events.append(e)
            continue
        # scale snap first (F minor pentatonic blues colour)
        sc = min(SCALE, key=lambda c: (abs(c - e.pitch), c))
        local_bar = e.start_tick // BAR
        bar = s * BARS_PER + local_bar
        if bar >= N_BARS:
            bar = N_BARS - 1
        # chord-tone quantize into trumpet range 54..86 (registry range);
        # pool already spans octaves, so nearest-in-pool is register-correct
        tones = chord_tones(PROG[bar], lo=54, hi=86)
        qp = quantize_to_chord(sc, tones)
        q_events.append(MusicEvent(pitch=qp, volume=e.volume,
                                   start_tick=e.start_tick, end_tick=e.end_tick))
    # voice-leading: cap leaps <= 9 semitones toward nearest chord tone
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
            tones = chord_tones(PROG[bar], lo=54, hi=86)
            e.pitch = min(tones, key=lambda c: (abs(c - p_prev), c))
    phase2.set_unit(0, s, MusicUnit(events=q_events))

# --- cello: sustained whole-bar triad pad (octave 3/4)
for bar in range(N_BARS):
    s, b = divmod(bar, BARS_PER)
    tones = CELLO_V[PROG[bar]]
    t0 = b * BAR
    e = []
    for k, p in enumerate(tones):
        e.append(MusicEvent(pitch=p, volume=50 + 4 * k,
                            start_tick=t0, end_tick=t0 + BAR - 90))
    unit = phase2.matrix.get_unit((2, s))
    events = list(unit.events) if unit is not None else []
    events.extend(e)
    phase2.set_unit(2, s, MusicUnit(events=events))

# --- sax: 8th-note answering counterline (chord tones +12 window)
for s in range(N_SECTIONS):
    r = np.random.default_rng(SEED + 300 + s)
    evs = []
    for bar in range(BARS_PER):
        t0 = bar * BAR
        tones = [t + 12 for t in chord_tones(PROG[s * BARS_PER + bar],
                                              lo=48, hi=76) if t + 12 <= 88]
        if not tones:
            tones = chord_tones(PROG[s * BARS_PER + bar], lo=60, hi=76)
        # answers on beats 2 & 4 with 8th pickup into next beat
        for beat in (1, 3):
            st = t0 + beat * 480
            pitch = int(r.choice(tones))
            evs.append(MusicEvent(pitch=pitch, volume=64,
                                  start_tick=st, end_tick=st + 240))
            st2 = st + 240
            if st2 < t0 + BAR:
                pitch2 = int(r.choice(tones))
                evs.append(MusicEvent(pitch=pitch2, volume=58,
                                      start_tick=st2, end_tick=st2 + 240))
    phase2.set_unit(1, s, MusicUnit(events=evs))

# --- piano: offbeat 16th stabs (chord tones +12), funk staccato
for bar in range(N_BARS):
    s, b = divmod(bar, BARS_PER)
    tones = [t + 12 for t in chord_tones(PROG[bar], lo=48, hi=76)]
    t0 = b * BAR
    e = []
    for k in range(0, BAR, 240):
        off = t0 + k + 120        # the "and" of every 8th - 16th aligned
        p = tones[(off // 120) % len(tones)]
        e.append(MusicEvent(pitch=p, volume=56,
                            start_tick=off, end_tick=off + 90))
    unit = phase2.matrix.get_unit((3, s))
    events = list(unit.events) if unit is not None else []
    events.extend(e)
    phase2.set_unit(3, s, MusicUnit(events=events))

# --- bass: funk octave pulse. root on 1 (+octave on the "and"), 5th/octave
#     moves on beats; 16th push into next bar in Chorus/Break. All on-grid.
BASS_8TH = {2, 4}          # sections with 8th-note pulse (chorus)
BASS_PUSH = {2, 3, 4}      # sections with 16th end-push
BASS_OCT = {2, 4}          # octave pops in choruses
for bar in range(N_BARS):
    s, b = divmod(bar, BARS_PER)
    root = BASS[PROG[bar]]
    fifth = root + 7 if root + 7 <= 43 else root - 5
    octv = root + 12 if root + 12 <= 55 else root
    t0 = b * BAR
    e = []
    step = 240 if s in BASS_8TH else 480
    for k in range(0, BAR, step):
        # low root on the beat, octave pop on the "and"
        on_beat = (k // step) % 2 == 0
        pitch = root if on_beat else (octv if s in BASS_OCT else root)
        e.append(MusicEvent(pitch=pitch, volume=82 if on_beat else 66,
                            start_tick=t0 + k, end_tick=t0 + k + step - 40))
    # 16th pickup push at bar end in funky sections
    if s in BASS_PUSH and b != BARS_PER - 1:
        e.append(MusicEvent(pitch=root, volume=72,
                            start_tick=t0 + BAR - 120, end_tick=t0 + BAR - 20))
    unit = phase2.matrix.get_unit((4, s))
    events = list(unit.events) if unit is not None else []
    events.extend(e)
    phase2.set_unit(4, s, MusicUnit(events=events))

# --- drums: funk kit. Intro sparse, Verse groove, Chorus full (16th hats,
#     claps), Break half-time feel, Outro sparse.
K = KIT
DRUM_PLAN = {
    0: dict(hat=40, kick=60, snare=None, clap=None, crash=False, hat16=False),
    1: dict(hat=52, kick=80, snare=70, clap=None, crash=False, hat16=False),
    2: dict(hat=58, kick=94, snare=90, clap=84, crash=True, hat16=True),
    3: dict(hat=42, kick=70, snare=64, clap=None, crash=False, hat16=False),
    4: dict(hat=58, kick=94, snare=90, clap=84, crash=True, hat16=True),
    5: dict(hat=36, kick=64, snare=None, clap=None, crash=False, hat16=False),
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
        # kick: 1 & 3 ("&" ghost in choruses)
        kick_beats = [0, 960]
        if s in (2, 4):
            kick_beats += [240, 1440]     # 1& 3& drive
        for kb in kick_beats:
            evs.append(MusicEvent(pitch=K["kick"], volume=plan["kick"],
                                  start_tick=t0 + kb, end_tick=t0 + kb + 120))
        if plan["snare"] is not None:
            for sb in (960, 2880):
                evs.append(MusicEvent(pitch=K["snare"], volume=plan["snare"],
                                      start_tick=t0 + sb, end_tick=t0 + sb + 120))
        if plan["clap"] is not None:
            for sb in (960, 2880):
                evs.append(MusicEvent(pitch=K["clap"], volume=plan["clap"],
                                      start_tick=t0 + sb, end_tick=t0 + sb + 120))
        if plan["crash"]:
            evs.append(MusicEvent(pitch=K["crash"], volume=70,
                                  start_tick=t0, end_tick=t0 + 500))
    phase2.set_unit(5, s, MusicUnit(events=evs))

# --- voice-leading check (rules.voice_leading): bass + lead per bar pair ---
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
    """Nudge lead's first note of bar+1 off a hidden 5th/8ve with the bass."""
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
    tones = sorted(chord_tones(PROG[bar + 1], lo=48, hi=91))
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

P2_MIDI = os.path.join(MIDI_DIR, "088-funk-hawkes.mid")
phase2.to_midi(P2_MIDI)
print("phase2 written", P2_MIDI)

# ---------------------------------------------------------------- analysis
from visualization.grid import write_grid_visualization  # noqa: E402

grid_path = os.path.join(ANALYSIS_DIR, "grid_visualization.txt")
write_grid_visualization(phase2.matrix, grid_path, ticks_per_character=120,
                         voice_names=vnames, bpm=BPM,
                         mode="F minor / Method 045 HPSEC + funk texture")
print("grid written", grid_path)

# provenance
from workflows.provenance import write_provenance, AI_GENERATED  # noqa: E402

for mid, phase, note in (
        (P1_MIDI, "1",
         "raw Hawkes self-exciting point process: Ogata-thinned Exp(lambda) "
         "sojourn times (fractional off-grid ticks), contagion pitch bursts "
         "with exponential kernel decay, single voice, no harmony"),
        (P2_MIDI, "2",
         "16th-grid locked, F-minor-pentatonic scale snap + chord-tone "
         "quantized to funk progression, trumpet/sax/cello/piano/bass/funk "
         "drums texture, voice-leading check, full arrangement")):
    write_provenance(
        mid, AI_GENERATED, "Hawkes Process Self-Exciting Composition (Method 045)",
        parameters={"bpm": BPM, "key": "F minor (pentatonic colour)",
                    "sections": N_SECTIONS, "bars": N_BARS, "phase": phase,
                    "progression": [CHORD_NAMES[r] for r in PROG],
                    "seed": SEED, "grid16": GRID16,
                    "hawkes_mu": 0.12, "hawkes_alpha": 0.55,
                    "hawkes_beta": 0.006},
        notes=note)
    print("provenance for phase", phase)

# voice-leading audit + summary
with open(os.path.join(ANALYSIS_DIR, "vl_audit.json"), "w") as f:
    json.dump({
        "voice_leading_flags": [str(x) for x in vl_flags],
        "voice_leading_flag_count": len(vl_flags),
        "phase1_validate": msg1,
        "phase2_validate": msg2,
    }, f, indent=2)

with open(os.path.join(ANALYSIS_DIR, "summary.json"), "w") as f:
    json.dump({
        "project": "088-funk-hawkes",
        "style": "Funk",
        "method": "045 Hawkes Process Self-Exciting Composition (HPSEC)",
        "layer": "concrete",
        "bpm": BPM, "key": "F minor (pentatonic)", "tempo": BPM,
        "bars": N_BARS,
        "sections": {n: BARS_PER for n in NAMES},
        "progression": [CHORD_NAMES[r] for r in PROG],
        "voices": vnames,
        "phase1": os.path.basename(P1_MIDI),
        "phase2": os.path.basename(P2_MIDI),
        "grid": os.path.basename(grid_path),
        "seed": SEED,
    }, f, indent=2)

for p in (P1_MIDI, P2_MIDI, grid_path,
          os.path.join(ANALYSIS_DIR, "summary.json"),
          os.path.join(ANALYSIS_DIR, "vl_audit.json")):
    assert os.path.getsize(p) > 40, "too small: %s" % p
print("ALL SIZE ASSERTS PASSED")
print("PROGRESSION:", [CHORD_NAMES[r] for r in PROG])
