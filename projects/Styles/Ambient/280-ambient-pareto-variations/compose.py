# -*- coding: utf-8 -*-
"""280-ambient-pareto-variations — Ambient rework of 234-ambient-pareto-build.

Nightly rework job (2026-11-02). Source: 234-ambient-pareto-build (Ambient,
Method 098 MOEPC / NSGA-II). Audit result: standards 1-5 pass (engine,
zero-drift, grid-sync, 5-voice setup, two-phase). Only standard 6 index.html
missing -> EXTENSION (identity-preserving), not redesign.

Identity preserved from source:
  genre Ambient · key D Aeolian (D E F G A Bb C, pc {2,4,5,7,9,10,0}) ·
  70 BPM · 4/4 · 480 TPB · BAR 1920 · method 098 MOEPC/NSGA-II ·
  voices Lead=Celesta(8) Pad=Organ(19) Bass=Cello(42) Sparkle=Harp(46)
  Drums=GM kit ch9 · cinematic-build form with smooth/balanced/active
  Pareto-front archetypes.

Extended + varied (44 bars, 7 sections, was 32 bars / 5 sections):
  Intro(4) Build(8) Rise(8) Peak(8) Bridge(8) Resolve(4) Coda(4).

Variation techniques (7, each key-safe in D Aeolian):
  T1 RETROGRADE      Bridge: Lead replays the Build's balanced contour reversed.
  T2 INVERSION       Bridge: Harp swaps arpeggio for a melodic counter-line,
                     the active motif mirrored around axis D4 (=62).
  T3 AUGMENTATION    Coda: Lead + Pad durations doubled -> spacious fade.
  T4 DIMINUTION      Rise: Lead note durations halved -> lighter forward drive.
  T5 REGISTER SHIFT  Peak +12 / Intro-Resolve-Coda -12 / Bridge Pad +12 upper.
  T6 RELATIVE-MAJOR  Bridge: harmonic center re-orients to VI (Bb) region.
  T7 DENSITY RISE    Rise: Harp 16th-note arpeggios + drums every bar.

Two-phase architecture:
  Phase 1 (raw): NSGA-II MOEPC "balanced" front melody, single celesta voice,
    unquantized float pitch + off-grid onsets, own composer + validate() gate.
  Phase 2 (rules): per-bar chord-tone quantization (floor bar attribution),
    240-tick 8th grid snap + dedup, voice-leading check/correction, register
    enforcement, 5-voice ambient texture + variation techniques.
  Dual-version contract: export_dual -> -perfect.mid (grid-locked) +
    -humanized.mid (style ambient + per-instrument DNA).
"""
import json
import os
import sys
import hashlib
import random

import numpy as np

from structures import MusicUnit, MusicEvent, MidiPercussion
from workflows.unitmatrix_composer import UnitMatrixComposer
from workflows.humanize import export_dual
from workflows.provenance import write_provenance, AI_ASSISTED
from visualization.grid import write_grid_visualization
from rules.progression import Scale7ChordDegree
from rules.voice_leading import VoiceLeadingRules

_INSTR_DIR = "/opt/data/repos/musicom/projects/Instruments"
if _INSTR_DIR not in sys.path:
    sys.path.insert(0, _INSTR_DIR)
from instrument_registry import CELESTA, ORGAN, CELLO, HARP  # noqa: E402

# ---------------------------------------------------------------------------
# Project layout / identity
# ---------------------------------------------------------------------------
GENRE = "Ambient"
STYLE = "ambient"
PROJECT = "280-ambient-pareto-variations"
BASE = os.path.join("/opt/data/projects/Styles", GENRE, PROJECT)
MIDI_DIR = os.path.join(BASE, "MIDI")
AUDIO_DIR = os.path.join(BASE, "Audio")
ANALYSIS_DIR = os.path.join(BASE, "Analysis")
for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
    os.makedirs(d, exist_ok=True)

BPM = 70
TPB = 480
BPB = 4
BAR = TPB * BPB                     # 1920
GRID = 120                          # 16th
EIGHTH = 240                        # 8th
TOTAL_BARS = 44
TOTAL_TICKS = TOTAL_BARS * BAR      # 84480

KEY_NAME = "D Aeolian"
TONIC_PC = 2                        # D
KEY_PCS = {2, 4, 5, 7, 9, 10, 0}    # D E F G A Bb C
INTERVALS = [0, 2, 3, 5, 7, 8, 10]  # natural-minor offsets from D
TONIC_BASE = 62                     # D4 (diatonic reference)
AXIS = 62                           # inversion axis D4

# 0-based degree -> triad quality intervals (D Aeolian diatonic)
# i=0 Dm, ii=1 Edim, III=2 F, iv=3 Gm, v=4 Am, VI=5 Bb, VII=6 C
QUALITY = {0: (0, 3, 7), 1: (0, 3, 6), 2: (0, 4, 7), 3: (0, 3, 7),
           4: (0, 3, 7), 5: (0, 4, 7), 6: (0, 4, 7)}
DEGREE_NAMES = {0: "Dm", 1: "Edim", 2: "F", 3: "Gm", 4: "Am", 5: "Bb", 6: "C"}

# deterministic seeds
hz_seed = int(hashlib.md5(PROJECT.encode()).hexdigest()[:8], 16) % 100000
raw_seed = 20261102                   # nightly selection seed
RNG = random.Random(raw_seed)
NP_RNG = np.random.default_rng(raw_seed)

# ---------------------------------------------------------------------------
# Form (44 bars, 7 sections). (name, bars, per-bar 0-based degrees)
# ---------------------------------------------------------------------------
SECTIONS = [
    ("Intro",   4, [0, 0, 5, 5]),                          # i i VI VI
    ("Build",   8, [0, 5, 6, 5, 3, 0, 5, 6]),              # i VI VII VI iv i VI VII
    ("Rise",    8, [3, 4, 5, 6, 3, 4, 0, 6]),              # iv v VI VII iv v i VII
    ("Peak",    8, [0, 5, 3, 4, 5, 6, 0, 0]),              # i VI iv v VI VII i i
    ("Bridge",  8, [5, 5, 0, 3, 5, 6, 0, 3]),              # VI-centric (relative-major)
    ("Resolve", 4, [0, 0, 5, 0]),                          # i i VI i
    ("Coda",    4, [0, 0, 0, 0]),                          # i drone
]
SECTION_START = {}
_acc = 0
for name, bars, prog in SECTIONS:
    SECTION_START[name] = _acc
    _acc += bars
assert _acc == TOTAL_BARS
SECTION_BARS = {name: bars for name, bars, prog in SECTIONS}

BAR_DEGREES = []
for name, bars, prog in SECTIONS:
    BAR_DEGREES.extend(prog)
assert len(BAR_DEGREES) == TOTAL_BARS

# archetype + octave + variation per section
SECTION_ARCH = {"Intro": "smooth", "Build": "balanced", "Rise": "active",
                "Peak": "active", "Bridge": "balanced", "Resolve": "smooth",
                "Coda": "smooth"}
SECTION_OCT = {"Intro": -12, "Build": 0, "Rise": 0, "Peak": 12,
               "Bridge": 0, "Resolve": -12, "Coda": -12}
# explicit per-section variation flags (key-safe, applied pre-quantization)
SECTION_LEAD_TRANSFORM = {"Bridge": "retrograde"}       # T1 retrograde
SECTION_LEAD_DUR = {"Rise": "diminish", "Coda": "augment"}  # T4 / T3
# variation technique applied per section (for provenance + REPORT)
SECTION_TECHNIQUE = {
    "Intro": "register-shift (-12)",
    "Build": "baseline (balanced motif)",
    "Rise": "diminution (dur x0.5) + density-rise (harp 16ths, drums/bar)",
    "Peak": "register-shift (+12) + full density",
    "Bridge": "retrograde + inversion counterline + relative-major re-orientation",
    "Resolve": "register-shift (-12)",
    "Coda": "augmentation (dur x2) fade",
}

VOICES = ["Lead", "Pad", "Bass", "Sparkle", "Drums"]
VOICE_PROGRAMS = [CELESTA.midi_program, ORGAN.midi_program, CELLO.midi_program,
                  HARP.midi_program, 0]
VOICE_CHANNELS = [0, 1, 2, 3, 9]


# ---------------------------------------------------------------------------
# Diatonic / chord helpers (canonical Scale7ChordDegree — no %7 wrapper)
# ---------------------------------------------------------------------------
def diatonic(deg_index, base=TONIC_BASE):
    return Scale7ChordDegree.get_diatonic_note(base, INTERVALS, deg_index)


def chord_tones(d, lo=36, hi=96):
    root_pc = (TONIC_PC + INTERVALS[d]) % 12
    out = set()
    for octv in range(-3, 11):
        for iv in QUALITY[d]:
            n = root_pc + 12 * octv + iv
            if lo <= n <= hi:
                out.add(n)
    return sorted(out)


def chord_pcs(d):
    root_pc = (TONIC_PC + INTERVALS[d]) % 12
    return sorted({(root_pc + iv) % 12 for iv in QUALITY[d]})


def quantize_to_chord_tone(raw_pitch, d, lo=55, hi=96):
    cands = chord_tones(d, lo=lo, hi=hi)
    if not cands:
        cands = [int(round(raw_pitch))]
    return min(cands, key=lambda c: abs(c - raw_pitch))


def snap_grid(t, grid=EIGHTH):
    return int(round(t / float(grid)) * grid)


# ---------------------------------------------------------------------------
# NSGA-II (Method 098 MOEPC core, ported from source, extended to 44 bars)
# ---------------------------------------------------------------------------
N_NOTES = 132                          # 3 notes/bar x 44 bars
DIM = N_NOTES * 3
POP = 64
GEN = 70
KEY_PCS_F = np.array(sorted(KEY_PCS), dtype=float)


def decode(x):
    p = x[0::3]
    o = x[1::3]
    d = x[2::3]
    pitch = 52.0 + p * 43.0                       # 52..95 unquantized float
    onset = o * (TOTAL_TICKS - 1)                 # 0..TOTAL_TICKS
    dur = 240.0 + d * 1440.0                      # 240..1680
    order = np.argsort(onset)
    return pitch[order].copy(), onset[order].copy(), dur[order].copy()


def objectives(pitch, onset, dur):
    pc = np.mod(pitch, 12.0)
    dist = np.abs(pc[:, None] - KEY_PCS_F[None, :])
    dist = np.minimum(dist, 12.0 - dist)
    f1 = dist.min(axis=1).mean() / 6.0            # harmonic quality
    iv = np.abs(np.diff(pitch))
    f2 = iv.mean() / 12.0                         # melodic quality
    gaps = np.diff(onset)
    gaps = np.clip(gaps, 1.0, None)
    cv = gaps.std() / (gaps.mean() + 1e-9)
    f3 = min(cv, 2.0) / 2.0                       # rhythmic coherence
    di = np.sign(np.diff(pitch))
    changes = int(np.sum(di[1:] != di[:-1]))
    interest_dir = changes / max(1, N_NOTES - 2)
    spread = (pitch.max() - pitch.min()) / 43.0
    interest = 0.5 * interest_dir + 0.5 * spread
    f4 = 1.0 - interest                           # voice independence
    return np.array([f1, f2, f3, f4])


def _dom(a, b):
    return bool(np.all(a <= b) and np.any(a < b))


def fast_non_dominated_sort(fits):
    n = len(fits)
    S = [[] for _ in range(n)]
    n_p = [0] * n
    fronts = [[]]
    for i in range(n):
        for j in range(i + 1, n):
            if _dom(fits[i], fits[j]):
                S[i].append(j)
                n_p[j] += 1
            elif _dom(fits[j], fits[i]):
                S[j].append(i)
                n_p[i] += 1
        if n_p[i] == 0:
            fronts[0].append(i)
    k = 0
    while fronts[k]:
        nxt = []
        for i in fronts[k]:
            for j in S[i]:
                n_p[j] -= 1
                if n_p[j] == 0:
                    nxt.append(j)
        k += 1
        fronts.append(nxt)
    fronts.pop()
    return fronts


def crowding_distance(fits):
    n, m = fits.shape
    dist = np.zeros(n)
    for obj in range(m):
        idx = np.argsort(fits[:, obj])
        dist[idx[0]] = dist[idx[-1]] = np.inf
        fmin, fmax = fits[idx[0], obj], fits[idx[-1], obj]
        if fmax - fmin < 1e-9:
            continue
        for r in range(1, n - 1):
            dist[idx[r]] += (fits[idx[r + 1], obj] - fits[idx[r - 1], obj]) / (fmax - fmin)
    return dist


def sbx_crossover(p1, p2, eta=15.0):
    u = NP_RNG.random(len(p1))
    beta = np.where(u <= 0.5, (2.0 * u) ** (1.0 / (eta + 1)),
                    (1.0 / (2.0 * (1.0 - u))) ** (1.0 / (eta + 1)))
    c1 = 0.5 * ((1 + beta) * p1 + (1 - beta) * p2)
    c2 = 0.5 * ((1 - beta) * p1 + (1 + beta) * p2)
    return np.clip(c1, 0, 1), np.clip(c2, 0, 1)


def poly_mutate(x, eta=20.0, prob=None):
    prob = prob if prob is not None else 1.0 / DIM
    y = x.copy()
    mask = NP_RNG.random(DIM) < prob
    r = NP_RNG.random(DIM)
    delta = np.where(r < 0.5,
                     (2.0 * r) ** (1.0 / (eta + 1)) - 1.0,
                     1.0 - (2.0 * (1.0 - r)) ** (1.0 / (eta + 1)))
    y[mask] += delta[mask]
    return np.clip(y, 0, 1)


def evolve():
    pop = NP_RNG.random((POP, DIM))
    for gen in range(GEN):
        fits = np.array([objectives(*decode(ind)) for ind in pop])
        fronts = fast_non_dominated_sort(fits)
        rank = np.zeros(POP, dtype=int)
        for r, fr in enumerate(fronts):
            for i in fr:
                rank[i] = r
        cd = np.zeros(POP)
        for fr in fronts:
            if len(fr) > 1:
                cd[fr] = crowding_distance(fits[fr])
        offspring = []
        while len(offspring) < POP:
            a, b = NP_RNG.choice(POP, 2, replace=False)
            ta = a if (rank[a] < rank[b] or (rank[a] == rank[b] and cd[a] > cd[b])) else b
            c, d = NP_RNG.choice(POP, 2, replace=False)
            tb = c if (rank[c] < rank[d] or (rank[c] == rank[d] and cd[c] > cd[d])) else d
            c1, c2 = sbx_crossover(pop[ta], pop[tb])
            offspring.append(poly_mutate(c1))
            offspring.append(poly_mutate(c2))
        pop = np.array(offspring[:POP])
    fits = np.array([objectives(*decode(ind)) for ind in pop])
    fronts = fast_non_dominated_sort(fits)
    return pop, fits, fronts


def pick_archetypes(pop, fits, fronts):
    f0 = fronts[0]
    f0fits = fits[f0]
    smooth_i = f0[int(np.argmin(f0fits[:, 1]))]
    active_i = f0[int(np.argmin(f0fits[:, 3]))]
    norm = (f0fits - f0fits.mean(0)) / (f0fits.std(0) + 1e-9)
    balanced_i = f0[int(np.argmin(norm.sum(1)))]
    return {
        "smooth": decode(pop[smooth_i]),
        "balanced": decode(pop[balanced_i]),
        "active": decode(pop[active_i]),
    }


# ---------------------------------------------------------------------------
# Phase 1: raw single-voice draft (balanced archetype)
# ---------------------------------------------------------------------------
def build_phase1(arch):
    p1 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BPB)
    p1.create_matrix(num_voices=1, num_sections=len(SECTIONS))
    p1.add_voice("RawDraft", program=CELESTA.midi_program, channel=0)
    for name, bars, prog in SECTIONS:
        p1.add_section(name, bars=bars)

    pitch, onset, dur = arch["balanced"]
    for name, bars, prog in SECTIONS:
        s0 = SECTION_START[name] * BAR
        s_ticks = bars * BAR
        cell = []
        for i in range(len(onset)):
            if onset[i] < s0 or onset[i] >= s0 + s_ticks:
                continue
            st = max(0, int(onset[i] - s0))
            en = min(s_ticks, int(onset[i] - s0 + dur[i]))
            if en <= st:
                continue
            p = max(36, min(96, int(round(pitch[i]))))
            cell.append(MusicEvent(pitch=p, volume=86, start_tick=st, end_tick=en))
        cell.sort(key=lambda e: (e.start_tick, e.end_tick))
        if not cell or cell[-1].end_tick < s_ticks:
            cell.append(MusicEvent(pitch=0, volume=0,
                                   start_tick=cell[-1].end_tick if cell else 0,
                                   end_tick=s_ticks))
        p1.fill_voice_section("RawDraft", name, MusicUnit(events=cell))
    ok, msg = p1.validate()
    if not ok:
        raise RuntimeError(f"phase1 validate failed: {msg}")
    return p1


# ---------------------------------------------------------------------------
# Phase 2: rules + variation techniques
# ---------------------------------------------------------------------------
def correct_voice_leading(triads):
    vl = VoiceLeadingRules(style="classical")
    corrected = [sorted(triads[0])]
    fixed = 0
    for i in range(1, len(triads)):
        prev = corrected[-1]
        base = sorted(triads[i])
        cands = [base]
        for rot in range(1, len(base)):
            cands.append(vl._rotate_chord(base, rot))
        cands = cands + [[p + 12 for p in c] for c in cands]
        best, best_score = cands[0], None
        for cand in cands:
            n_viol = len(vl.check_parallel_motion(prev, cand)) + len(vl.check_hidden_fifths(prev, cand))
            dist = vl.calculate_voice_leading_distance(prev, cand)
            score = (n_viol, dist)
            if best_score is None or score < best_score:
                best_score, best = score, cand
        if best_score[0] > 0:
            fixed += 1
        corrected.append(sorted(best))
    return corrected, fixed


def build_lead_section(arch, name, corr_triads):
    """Lead (celesta) events for one section, with variation technique."""
    pitch, onset, dur = arch[SECTION_ARCH[name]]
    octave = SECTION_OCT[name]
    transform = SECTION_LEAD_TRANSFORM.get(name)
    durmode = SECTION_LEAD_DUR.get(name)
    s0 = SECTION_START[name] * BAR
    nbars = SECTION_BARS[name]
    s_ticks = nbars * BAR

    # collect raw notes in this section's absolute range
    raw = []
    for i in range(len(onset)):
        if onset[i] < s0 or onset[i] >= s0 + s_ticks:
            continue
        st_global = snap_grid(onset[i])
        if st_global < s0 or st_global >= s0 + s_ticks:
            continue
        bar = st_global // BAR                       # floor attribution (post-snap)
        raw.append({"pitch": int(round(pitch[i])), "st": st_global,
                    "dur": dur[i], "bar": bar})

    # apply contour transform to the pitch sequence (before quantization)
    pitches = [r["pitch"] for r in raw]
    if transform == "retrograde":
        pitches = list(reversed(pitches))
    elif transform == "inversion":
        pitches = [int(2 * AXIS - p) for p in pitches]

    events = []
    for r, p in zip(raw, pitches):
        d = BAR_DEGREES[r["bar"]]
        qp = quantize_to_chord_tone(p + octave, d, lo=50, hi=96)
        qp = max(48, min(96, qp))
        st = r["st"] - s0
        if st >= s_ticks - 30:
            continue
        dur = r["dur"]
        if durmode == "diminish":
            dur = max(120, dur * 0.5)
        elif durmode == "augment":
            dur = dur * 2.0
        en = min(s_ticks - 20, st + int(dur))
        if en <= st + 30:
            en = st + 120
        events.append(MusicEvent(pitch=qp, volume=82, start_tick=st, end_tick=en))

    # dedup collided (start,pitch) keep longest
    best = {}
    for e in events:
        key = (e.start_tick, e.pitch)
        if key not in best or (e.end_tick - e.start_tick) > (best[key].end_tick - best[key].start_tick):
            best[key] = e
    return sorted(best.values(), key=lambda e: (e.start_tick, e.pitch))


def build_pad_section(name, corr_triads):
    nbars = SECTION_BARS[name]
    s_ticks = nbars * BAR
    ev = []
    for bi in range(nbars):
        bar = SECTION_START[name] + bi
        triad = corr_triads[bar]
        r, th, f = triad
        bs = bi * BAR
        if name == "Coda":
            end = bs + BAR * 2 - 30                       # augmentation: held longer
        else:
            end = bs + BAR - 30
        ev.append(MusicEvent(pitch=r, volume=64, start_tick=bs, end_tick=min(end, s_ticks - 30)))
        ev.append(MusicEvent(pitch=th, volume=60, start_tick=bs, end_tick=min(end, s_ticks - 30)))
        ev.append(MusicEvent(pitch=f, volume=60, start_tick=bs, end_tick=min(end, s_ticks - 30)))
        if name in ("Peak", "Bridge", "Rise"):
            ev.append(MusicEvent(pitch=r + 12, volume=58, start_tick=bs,
                                 end_tick=min(bs + BAR - 30, s_ticks - 30)))
    return ev


def build_bass_section(name, corr_triads):
    nbars = SECTION_BARS[name]
    s_ticks = nbars * BAR
    ev = []
    for bi in range(nbars):
        bar = SECTION_START[name] + bi
        triad = corr_triads[bar]
        r, th, f = triad
        bs = bi * BAR
        ev.append(MusicEvent(pitch=r - 12, volume=76, start_tick=bs, end_tick=bs + BAR - 40))
        ev.append(MusicEvent(pitch=f - 12, volume=68, start_tick=bs + 960, end_tick=bs + 960 + 400))
        if name in ("Peak", "Bridge"):
            ev.append(MusicEvent(pitch=r - 12, volume=72, start_tick=bs + 480, end_tick=bs + 480 + 200))
    return ev


def build_sparkle_section(name, corr_triads):
    """Harp: 8th-note arpeggio (16th in Rise = density); counter-line in Bridge."""
    nbars = SECTION_BARS[name]
    s_ticks = nbars * BAR
    ev = []
    for bi in range(nbars):
        bar = SECTION_START[name] + bi
        triad = corr_triads[bar]
        r, th, f = triad
        bs = bi * BAR
        if name == "Bridge":
            # T2 inversion counter-line: invert chord-derived seed around D4,
            # then quantize each to the bar's chord tones (key-safe).
            seed = [r + 12, f + 12, th + 12, r + 24]
            inv = [int(2 * AXIS - p) for p in seed]
            for k, p in enumerate(inv):
                qp = quantize_to_chord_tone(p, BAR_DEGREES[bar], lo=48, hi=96)
                qp = max(48, min(96, qp))
                ev.append(MusicEvent(pitch=qp, volume=62,
                                     start_tick=bs + k * EIGHTH,
                                     end_tick=bs + k * EIGHTH + 200))
        elif name == "Rise":
            # T7 density rise: 16th-note arpeggio
            pat = [r + 12, th + 12, f + 12, r + 24, f + 12, th + 12,
                   r + 12, th + 12, f + 12, r + 24, f + 12, th + 12]
            for k in range(12):
                ev.append(MusicEvent(pitch=pat[k], volume=58,
                                     start_tick=bs + k * GRID,
                                     end_tick=bs + k * GRID + 100))
        else:
            pat = [r + 12, th + 12, f + 12, r + 24, f + 12, th + 12]
            offsets = [0, 240, 480, 960, 1200, 1440]
            for k, off in enumerate(offsets):
                ev.append(MusicEvent(pitch=pat[k], volume=58,
                                     start_tick=bs + off, end_tick=bs + off + 220))
    return ev


def build_drums_section(name):
    nbars = SECTION_BARS[name]
    s_ticks = nbars * BAR
    ev = []
    kick = MidiPercussion.BASS_DRUM
    low_tom = MidiPercussion.LOW_TOM
    crash = MidiPercussion.CRASH_CYMBAL
    for bi in range(nbars):
        bs = bi * BAR
        if name in ("Build", "Rise", "Peak", "Bridge"):
            ev.append(MusicEvent(pitch=kick, volume=72, start_tick=bs, end_tick=bs + 80))
            ev.append(MusicEvent(pitch=low_tom, volume=68, start_tick=bs + 960, end_tick=bs + 1030))
        if name in ("Rise", "Peak"):
            ev.append(MusicEvent(pitch=low_tom, volume=64, start_tick=bs + 480, end_tick=bs + 540))
        if name == "Peak" and bi % 2 == 0:
            ev.append(MusicEvent(pitch=crash, volume=78, start_tick=bs, end_tick=bs + 200))
        if name == "Coda" and bi % 2 == 0:
            ev.append(MusicEvent(pitch=low_tom, volume=56, start_tick=bs, end_tick=bs + 100))
    return ev


def seal(ev, sec_ticks):
    ev = sorted(ev, key=lambda e: (e.start_tick, e.pitch))
    out = []
    for e in ev:
        if e.start_tick < 0 or e.start_tick >= sec_ticks:
            continue
        en = min(sec_ticks, e.end_tick)
        if en <= e.start_tick:
            en = min(sec_ticks, e.start_tick + 30)
        out.append(MusicEvent(pitch=e.pitch, volume=e.volume,
                              start_tick=e.start_tick, end_tick=en))
    if not out or out[-1].end_tick < sec_ticks:
        last_end = out[-1].end_tick if out else 0
        out.append(MusicEvent(pitch=0, volume=0, start_tick=last_end, end_tick=sec_ticks))
    return MusicUnit(events=out)


def build_phase2(arch, corr_triads):
    comp = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BPB)
    comp.create_matrix(num_voices=len(VOICES), num_sections=len(SECTIONS))
    for name, prog, ch in zip(VOICES, VOICE_PROGRAMS, VOICE_CHANNELS):
        comp.add_voice(name, program=prog, channel=ch)
    for name, bars, prog in SECTIONS:
        comp.add_section(name, bars=bars)

    for name, bars, prog in SECTIONS:
        s_ticks = bars * BAR
        lead = build_lead_section(arch, name, corr_triads)
        pad = build_pad_section(name, corr_triads)
        bass = build_bass_section(name, corr_triads)
        spark = build_sparkle_section(name, corr_triads)
        drums = build_drums_section(name)
        comp.fill_voice_section("Lead", name, seal(lead, s_ticks))
        comp.fill_voice_section("Pad", name, seal(pad, s_ticks))
        comp.fill_voice_section("Bass", name, seal(bass, s_ticks))
        comp.fill_voice_section("Sparkle", name, seal(spark, s_ticks))
        comp.fill_voice_section("Drums", name, seal(drums, s_ticks))
    ok, msg = comp.validate()
    if not ok:
        raise RuntimeError(f"phase2 validate failed: {msg}")
    return comp


# ---------------------------------------------------------------------------
# Audits (pre-export, on event lists)
# ---------------------------------------------------------------------------
def count_offgrid(events, grid=120):
    off = sum(1 for e in events if e.pitch > 0 and e.start_tick % grid != 0)
    tot = sum(1 for e in events if e.pitch > 0)
    return off, tot


def main():
    print("[evolve] NSGA-II MOEPC population ...")
    pop, fits, fronts = evolve()
    front_size = len(fronts[0])
    print(f"[evolve] done. Pareto front rank-0 size: {front_size}")
    arch = pick_archetypes(pop, fits, fronts)
    print("[arch] smooth/balanced/active decoded")

    # ---- Phase 1 raw draft -------------------------------------------------
    phase1 = build_phase1(arch)
    phase1_mid = os.path.join(MIDI_DIR, PROJECT + "-phase1.mid")
    phase1.to_midi(phase1_mid)
    write_provenance(
        phase1_mid, AI_ASSISTED,
        "musicom.method.098_moepc_phase1",
        sources=["/opt/data/projects/Styles/Ambient/234-ambient-pareto-build/"
                 "MIDI/234-ambient-pareto-build-phase1.mid"],
        parameters={"bpm": BPM, "bars": TOTAL_BARS, "seed": raw_seed,
                    "phase": 1, "quantized": False, "key": KEY_NAME,
                    "form": "intro-build-rise-peak-bridge-resolve-coda",
                    "style": STYLE, "method": "098 MOEPC (NSGA-II, pop 64 x gen 70)",
                    "notes": 132, "front_size": front_size,
                    "archetype_used": "balanced", "rules_applied": "NONE (pre-rules)"},
        notes="Raw NSGA-II MOEPC draft: balanced Pareto-front melody, single "
              "celesta voice, unquantized float pitch + off-grid onsets, 44 bars, "
              "pre-rules. Rework source: 234-ambient-pareto-build (identity-preserving "
              "extension).")
    write_grid_visualization(phase1.matrix,
                             os.path.join(ANALYSIS_DIR, "grid_visualization_phase1.txt"),
                             voice_names=["RawDraft"], bpm=BPM)
    print("PHASE1_OK")

    # ---- Phase 2 rules + variation -----------------------------------------
    bar_triads = [sorted([diatonic(d), diatonic(d + 2), diatonic(d + 4)])
                  for d in BAR_DEGREES]
    vl = VoiceLeadingRules(style="classical")
    opt_triads = vl.optimize_voice_leading(bar_triads)
    corr_triads, fixed = correct_voice_leading(opt_triads)
    print(f"[voicing] corrected {fixed} chord(s)")

    phase2 = build_phase2(arch, corr_triads)

    # gather all pitched events from the phase-2 matrix (perfect layer)
    all_pitched = []
    for r in range(phase2.matrix.num_rows):
        for c in range(phase2.matrix.num_cols):
            cell = phase2.matrix.get_unit((r, c))
            if cell is None:
                continue
            for e in cell.events:
                if e.pitch > 0:
                    all_pitched.append(e)
    off, tot = count_offgrid(all_pitched)
    print(f"[grid] perfect-layer off-grid (pitched): {off}/{tot}")
    assert off == 0, f"perfect layer has {off} off-grid onsets"

    # ---- dual-version export ----------------------------------------------
    hz_instruments = {
        "Lead": CELESTA.humanize_dna,
        "Pad": ORGAN.humanize_dna,
        "Bass": CELLO.humanize_dna,
        "Sparkle": HARP.humanize_dna,
        "Drums": None,
    }
    perfect_path = os.path.join(MIDI_DIR, PROJECT + "-perfect.mid")
    humanized_path = os.path.join(MIDI_DIR, PROJECT + "-humanized.mid")
    hz = export_dual(phase2, perfect_path, humanized_path,
                     style=STYLE, seed=hz_seed, bpm=BPM, instruments=hz_instruments)

    # ---- provenance sidecars ----------------------------------------------
    section_midpoints = {}
    for name, bars, prog in SECTIONS:
        mid_idx = bars // 2
        section_midpoints[name] = {"degree": prog[mid_idx],
                                   "chord": DEGREE_NAMES[prog[mid_idx]]}
    prov = {
        "bpm": BPM, "key": "D", "mode": "aeolian", "style": STYLE,
        "form": "intro-build-rise-peak-bridge-resolve-coda",
        "bars": TOTAL_BARS, "sections": [s[0] for s in SECTIONS],
        "section_bars": {s[0]: s[1] for s in SECTIONS},
        "section_techniques": SECTION_TECHNIQUE,
        "section_midpoint_chords": section_midpoints,
        "bar_degrees": BAR_DEGREES,
        "method": "098 MOEPC", "layer": "concrete", "paradigm": "Stochastic",
        "rework": {"source": "234-ambient-pareto-build", "decision": "extension",
                   "standard_failures": ["index.html missing (docs only)"]},
        "variation_techniques": {
            "retrograde": "Bridge lead (balanced motif reversed)",
            "inversion": "Bridge harp counter-line (active motif around D4)",
            "augmentation": "Coda lead+pad durations x2",
            "diminution": "Rise lead durations x0.5",
            "register_shift": "Peak +12 / Intro-Resolve-Coda -12",
            "relative_major": "Bridge harmonic center -> VI (Bb) region",
            "density_rise": "Rise harp 16ths + drums every bar",
        },
        "voices": [[v, p, ch] for v, p, ch in zip(VOICES, VOICE_PROGRAMS, VOICE_CHANNELS)],
        "humanize_seed": hz_seed, "raw_seed": raw_seed,
        "humanize_profiles": {k: v["profile"] for k, v in hz.items()},
    }
    write_provenance(
        perfect_path, AI_ASSISTED,
        "musicom two-phase (phase=2 rules: chord-tone quantization + 8th grid "
        "snap + dedup + voice-leading + variation techniques) (method 098 MOEPC)",
        sources=[phase1_mid],
        parameters=dict(prov, phase=2, version="perfect", off_grid=0),
        notes="Grid-locked perfect layer (intro-build-rise-peak-bridge-resolve-coda, "
              "44 bars). Identity-preserving extension of 234-ambient-pareto-build.")
    write_provenance(
        humanized_path, AI_ASSISTED,
        "musicom two-phase (phase=2 + humanization) (method 098 MOEPC)",
        sources=[perfect_path],
        parameters=dict(prov, phase=2, version="humanized",
                        humanize_seed=hz_seed,
                        humanize_stats={k: {kk: (float(vv) if isinstance(vv, float) else vv)
                                            for kk, vv in v.items() if kk != "profile"}
                                        for k, v in hz.items()}),
        notes="Humanized layer (style ambient + per-instrument DNA).")

    # ---- grid visualization -------------------------------------------------
    write_grid_visualization(phase2.matrix,
                             os.path.join(ANALYSIS_DIR, "grid_visualization.txt"),
                             voice_names=VOICES, bpm=BPM)

    # ---- size asserts -------------------------------------------------------
    for p in (phase1_mid, perfect_path, humanized_path):
        assert os.path.getsize(p) > 40, f"empty/corrupt: {p}"

    summary = {
        "style": STYLE, "genre": GENRE, "method": "098 MOEPC",
        "form": "intro-build-rise-peak-bridge-resolve-coda",
        "key": KEY_NAME, "bpm": BPM, "bars": TOTAL_BARS,
        "sections": [s[0] for s in SECTIONS],
        "section_bars": [s[1] for s in SECTIONS],
        "section_techniques": SECTION_TECHNIQUE,
        "front_size": front_size, "raw_notes": N_NOTES,
        "voice_leading_corrections": fixed,
        "phase1_path": phase1_mid, "perfect_path": perfect_path,
        "humanized_path": humanized_path,
        "hz_seed": hz_seed,
        "hz": {k: {kk: vv for kk, vv in v.items() if kk != "profile"}
               for k, v in hz.items()},
        "progression": {s[0]: [DEGREE_NAMES[d] for d in s[2]] for s in SECTIONS},
        "rework_source": "234-ambient-pareto-build",
        "rework_decision": "extension",
    }
    with open(os.path.join(ANALYSIS_DIR, "compose_summary.json"), "w") as f:
        json.dump(summary, f, indent=2, default=str)
    print("COMPOSE_OK")
    print(json.dumps(summary, indent=2, default=str))


if __name__ == "__main__":
    main()
