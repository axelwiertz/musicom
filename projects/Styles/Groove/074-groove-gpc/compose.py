# -*- coding: utf-8 -*-
"""074-groove-gpc - Groove style / Method 061 Gaussian Process Composition (GPC).

Two-phase composition:
  Phase 1: raw GP prior sample - a single-voice posterior draw over a latent
           pitch curve (continuous semitone values, unquantized, no harmony).
           Onsets from a separate log-IOI GP + derivative density. Pure
           stochastic generative draft.
  Phase 2: musicom rules post-process - chord-tone quantization per bar,
           voice-leading leap cap, full groove texture:
           lead (synth lead) + horns (stab accents) + Rhodes comp + bass
           (funk octave/syncopated) + drums (kick 1&3, snare 2&4, hats,
           chorus claps + ride).

Engine only: structures + workflows.unitmatrix_composer. validate() gate + to_midi().
"""
import os
import json

import numpy as np

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import (
    UnitMatrixComposer, create_empty_unit,
)

SEED = 20260820
rng = np.random.default_rng(SEED)

# ---------------------------------------------------------------- project dirs
PROJ = "/opt/data/projects/Styles/Groove/074-groove-gpc"
MIDI_DIR = os.path.join(PROJ, "MIDI")
AUDIO_DIR = os.path.join(PROJ, "Audio")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")
for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
    os.makedirs(d, exist_ok=True)

# ---------------------------------------------------------------- concept
BPM = 106
TPB = 480
BEATS = 4
BAR = TPB * BEATS            # 1920
# G minor groove: G A Bb C D Eb F (natural minor) across two octaves
SCALE = [55, 57, 58, 60, 62, 63, 65, 67, 69, 70, 72, 74, 75, 77, 79, 81]
LEAD_LO, LEAD_HI = 60, 84

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

# chord roots, one per bar: i III iv V | i III iv V | i iv V VI | i V i VI | ...
# 24 bars: i III iv V | i III iv V | i iv V i | i V i VI | i III iv V | i V iv i
PROG = ([55, 58, 60, 62] * 2) + [55, 60, 62, 55] + [55, 62, 55, 63] + \
       [55, 58, 60, 62] + [55, 62, 60, 55]
assert len(PROG) == N_BARS, (len(PROG), N_BARS)
CHORD_NAMES = {55: "i", 58: "III", 60: "iv", 62: "V", 63: "VI"}

def chord_for_bar(bar):
    return CHORDS[PROG[bar]]

def quantize_to_chord(pitch, chord_tones):
    """Snap a pitch to nearest chord tone, resolving ties toward lower."""
    return min(chord_tones, key=lambda c: (abs(c - pitch), c))

# ---------------------------------------------------------------- GP core
def rbf_kernel(X1, X2, lengthscale=1.0, variance=1.0):
    sq = (X1[:, None] - X2[None, :]) ** 2
    return variance * np.exp(-0.5 * sq / lengthscale ** 2)

def periodic_kernel(X1, X2, period=1.0, lengthscale=1.0, variance=1.0):
    d = np.sin(np.pi * (X1[:, None] - X2[None, :]) / period)
    return variance * np.exp(-2.0 * d ** 2 / lengthscale ** 2)

class GPComposer:
    def __init__(self, kernel=rbf_kernel, noise=1e-3, mean=0.0):
        self.kernel, self.noise, self.mean = kernel, noise, mean

    def condition(self, X_anchor, y_anchor):
        self.X = np.asarray(X_anchor, dtype=float)
        self.y = np.asarray(y_anchor, dtype=float)
        K = self.kernel(self.X, self.X) + self.noise * np.eye(len(self.X))
        self.L = np.linalg.cholesky(K)
        self.alpha = np.linalg.solve(self.L.T,
                    np.linalg.solve(self.L, self.y - self.mean))

    def predict(self, X_new):
        X_new = np.asarray(X_new, dtype=float)
        Ks = self.kernel(X_new, self.X)
        mean = self.mean + Ks @ self.alpha
        v = np.linalg.solve(self.L, Ks.T)
        kxx_diag = np.diag(self.kernel(X_new, X_new))
        var = kxx_diag - (v ** 2).sum(0)
        return mean, np.clip(var, 0.0, None)

    def sample(self, X_new, n=1, seed=None):
        mean, var = self.predict(X_new)
        rr = np.random.default_rng(seed)
        L = np.linalg.cholesky(np.diag(np.clip(var, 0, None)) + 1e-9 * np.eye(len(var)))
        return mean[:, None] + L @ rr.standard_normal((len(var), n))

# ---------------------------------------------------------------- phase 1
# GP prior over a latent pitch curve in bar-index space. Anchors = tonic
# pull per section (macro-form arc). Kernel = RBF (smooth conjunct contour)
# + periodic (bar-cycle ostinato). Then sample a smooth continuous curve,
# take its derivative to derive onset density, map value -> semitone offset.
#
# Per-section drift targets = macro-form (Intro wander -> Verse tonic ->
# Chorus strong tonic -> Outro settle). This is the GPC "mean + kernel
# horizon" story: long lengthscale = phrase memory, period = bar ostinato.

SEC_MEAN = [0.0, -0.5, -1.5, -0.5, -1.5, -3.0]   # semitone offsets toward tonic
SEC_LS = [1.6, 1.3, 1.0, 1.3, 1.0, 1.8]         # lengthscale = phrase horizon
SEC_VAR = [1.2, 1.5, 1.9, 1.5, 1.9, 0.9]
SEC_DENS = [0.45, 0.8, 1.0, 0.8, 1.0, 0.5]       # onset density multiplier

def gp_lead_section(s, name):
    """Sample raw lead contour for one section (continuous semitones + onsets)."""
    n_bar = BARS_PER
    # latent curve sampled at 16th-note resolution (120 per bar)
    res = 120
    X_all = np.linspace(0.0, n_bar, n_bar * res, endpoint=False)
    # anchors: tonic (0.0) at section start/end + slight arc
    anchors_x = np.array([0.0, n_bar * 0.25, n_bar * 0.5, n_bar * 0.75, n_bar])
    anchors_y = np.array([SEC_MEAN[s], SEC_MEAN[s] * 0.3, SEC_MEAN[s] * 0.8,
                          SEC_MEAN[s] * 0.5, 0.0])
    gp = GPComposer(kernel=rbf_kernel, noise=1e-3, mean=0.0)
    gp.condition(anchors_x, anchors_y)
    curve = gp.sample(X_all, n=1, seed=SEED + s)[:, 0]
    # add small periodic ostinato (bar cycle) on top
    period = periodic_kernel(X_all, X_all, period=1.0,
                             lengthscale=0.8, variance=SEC_VAR[s])
    curve = curve + np.sqrt(np.clip(np.diag(period), 0, None)) * \
        rng.standard_normal(len(X_all)) * 0.4
    # onset density from |derivative| scaled by section density
    d = np.abs(np.gradient(curve, X_all))
    threshold = np.percentile(d, 100 * (1 - SEC_DENS[s]))
    onsets = np.where(d > threshold)[0]
    # velocity from contour energy (soft tanh compressor)
    vels = np.clip(62 + 34 * np.tanh(d[onsets] / 0.15), 45, 116).astype(int)
    # map curve value -> semitone offset centered on 0
    semis = curve[onsets]
    return X_all[onsets], semis, vels

phase1 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
phase1.create_matrix(num_voices=1, num_sections=N_SECTIONS)
phase1.add_voice("LeadRaw", program=80, channel=0)  # Square Lead (raw GP draft)
for n in NAMES:
    phase1.add_section(n, bars=BARS_PER)

for s, name in enumerate(NAMES):
    xs, semis, vels = gp_lead_section(s, name)
    events = []
    for x, sem, v in zip(xs, semis, vels):
        tick = int(round(x / BARS_PER * SECTION_TICKS))
        midi = int(round(72 + sem * 2.0))     # amplify curve -> semitone space
        midi = max(LEAD_LO, min(LEAD_HI, midi))
        dur = 220
        events.append(MusicEvent(pitch=midi, volume=int(v),
                                 start_tick=int(tick), end_tick=int(tick) + dur))
    if events:
        last = events[-1].end_tick
        if last > SECTION_TICKS:
            events[-1].end_tick = SECTION_TICKS
    phase1.set_unit(0, s, MusicUnit(events=events))

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
P1_MIDI = os.path.join(MIDI_DIR, "074-groove-gpc-phase1.mid")
phase1.to_midi(P1_MIDI)
print("phase1 written", P1_MIDI)

# ---------------------------------------------------------------- phase 2
# rules post-process: chord-tone quantization + voice-leading + full groove texture
phase2 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
VOICES = [
    ("Lead",     80, 0),   # Square Lead (groove lead)
    ("Horns",    61, 1),   # Brass Section (stabs)
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

# --- horns: syncopated stab accents on beats 2& / 4& (groove classic) ---
HORN_STRONG = {2, 4}   # chorus sections
for bar in range(N_BARS):
    s, b = divmod(bar, BARS_PER)
    tones = chord_for_bar(bar)
    t0 = b * BAR
    e = []
    if s in HORN_STRONG:
        # 4 stabs per bar: beats 2, 2&, 4, 4& (offbeat pushes)
        for off in (720, 960, 1680, 1920 - 240):
            for p in tones:
                e.append(MusicEvent(pitch=p + 12, volume=78,
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

# --- bass: groove octave pulse, root on 1&3, fifth on 2&4, syncopated 16th push ---
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

# --- drums: backbeat groove. 35 kick 1&3, 38 snare 2&4, 42 closed hat 8ths,
#      chorus adds 51 ride + 39 clap on 2&4 ---
DRUM_DENS = [0.4, 0.8, 1.0, 0.8, 1.0, 0.5]
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
            evs.append(MusicEvent(pitch=42, volume=48,
                                  start_tick=t0 + k, end_tick=t0 + k + 90))
        # kick on 1 and 3
        evs.append(MusicEvent(pitch=35, volume=106, start_tick=t0, end_tick=t0 + 160))
        evs.append(MusicEvent(pitch=35, volume=100, start_tick=t0 + 960, end_tick=t0 + 1120))
        if dens >= 0.8:
            # snare backbeat on 2 and 4
            evs.append(MusicEvent(pitch=38, volume=100, start_tick=t0 + 480, end_tick=t0 + 620))
            evs.append(MusicEvent(pitch=38, volume=106, start_tick=t0 + 1440, end_tick=t0 + 1580))
            if dens >= 1.0:
                # clap doubles snare + ride cymbal on beat 1
                evs.append(MusicEvent(pitch=39, volume=84, start_tick=t0 + 480, end_tick=t0 + 600))
                evs.append(MusicEvent(pitch=39, volume=88, start_tick=t0 + 1440, end_tick=t0 + 1560))
                evs.append(MusicEvent(pitch=51, volume=70, start_tick=t0, end_tick=t0 + 600))
    phase2.set_unit(4, s, MusicUnit(events=evs))

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
        if u is not None and len(u.events) > 0:
            phase2.set_unit(v, s, normalize_cell(u, SECTION_TICKS))

ok2, msg2 = phase2.validate()
print("PHASE2 validate:", msg2)
assert ok1 and ok2, (msg1, msg2)

P2_MIDI = os.path.join(MIDI_DIR, "074-groove-gpc.mid")
phase2.to_midi(P2_MIDI)
print("phase2 written", P2_MIDI)

# ---------------------------------------------------------------- analysis
from visualization.grid import write_grid_visualization
grid_path = os.path.join(ANALYSIS_DIR, "grid_visualization.txt")
write_grid_visualization(phase2.matrix, grid_path, ticks_per_character=120,
                         voice_names=vnames, bpm=BPM, mode="G minor / GP groove")
print("grid written", grid_path)

# provenance
from workflows.provenance import write_provenance, AI_GENERATED
for mid, phase, note in (
        (P1_MIDI, "1", "raw GP posterior sample, unquantized, single voice, no harmony"),
        (P2_MIDI, "2", "chord-tone quantized to G-minor groove progression, full texture")):
    write_provenance(
        mid, AI_GENERATED, "GPC (Method 061 Gaussian Process Composition)",
        parameters={"bpm": BPM, "key": "G natural minor", "sections": N_SECTIONS,
                    "bars": N_BARS, "phase": phase,
                    "progression": [CHORD_NAMES[r] for r in PROG], "seed": SEED},
        notes=note)
    print("provenance for phase", phase)

# summary.json
with open(os.path.join(ANALYSIS_DIR, "summary.json"), "w") as f:
    json.dump({
        "project": "074-groove-gpc",
        "style": "Groove",
        "method": "061 Gaussian Process Composition (GPC)",
        "bpm": BPM, "key": "G natural minor", "tempo": BPM,
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
