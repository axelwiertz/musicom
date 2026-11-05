# -*- coding: utf-8 -*-
"""287-celtic-tonality-diamond -- Celtic composition via Method 131 TDRPC.

Two-phase architecture, nightly composition job.

  Abstract layer (TDRPC, Harry Partch tonality diamond):
    - build D(7): the 7-limit odd tonality diamond (13 just ratios), each with
      Tenney height H(a/b)=log2(a*b) and cents.
    - hexad vocabulary: Otonality/Utonality sets over identities {1,3,5,7}.
    - identity lattice: common-tone matrix between hexads.
    - height curve: per-section tension target (H) driving register + density.
  Concrete layer (musicom rules post-process):
    - project the diamond's low-height otonality tones to D Mixolydian
      (the 7/4 harmonic seventh = the Mixolydian b7, the diamond's signature).
    - tiered pitch discipline: strong beats snap scale+chord, weak snap scale.
    - grid-lock to 16th, voice-leading cap, dedup, zero-drift, dual export.

Engine only: structures + workflows.unitmatrix_composer + sound.synthesis.scale_quantizer
+ workflows.pitch_audit + workflows.humanize. mido used READ-ONLY for verification.
"""
import os
import json
import sys
from fractions import Fraction
from math import log2

import numpy as np

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer, create_empty_unit
from sound.synthesis.scale_quantizer import ScaleQuantizer, classify_weight, STRONG_GRID
from workflows.pitch_audit import audit_voice

sys.path.insert(0, "/opt/data/projects/Instruments")
from instrument_registry import by_name  # noqa: E402

SEED = 20261105
STYLE = "celtic"
METHOD_ID = "131"
METHOD_NAME = "Tonality Diamond Ratio-Pool Composition (TDRPC)"
LAYER = "abstract"
FORM = "intro-verse-chorus-verse-chorus-outro"
KEY = "D Mixolydian (harmonic 7th via Partch 7/4)"

PROJ = "/opt/data/projects/Styles/Celtic/287-celtic-tonality-diamond"
MIDI_DIR = os.path.join(PROJ, "MIDI")
AUDIO_DIR = os.path.join(PROJ, "Audio")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")
for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
    os.makedirs(d, exist_ok=True)

BPM = 112
TPB = 480
BEATS = 4
BAR = TPB * BEATS            # 1920 ticks
GRID = 120                   # 16th note
EIGHTH = 240

# D Mixolydian: D E F# G A B C -> pitch classes {2,4,6,7,9,11,0}
SCALE_PCS = {2, 4, 6, 7, 9, 11, 0}
SCALE_NAME = "mixolydian"
SCALE_ROOT = 50              # D3
sq = ScaleQuantizer(root=SCALE_ROOT, scale=SCALE_NAME)
STRONG_GRID_44 = tuple(STRONG_GRID["4/4"])   # (0, 960) = beats 1 & 3

# ---------------------------------------------------------------------------
# ABSTRACT LAYER (TDRPC) -- Partch tonality diamond, hexads, identity lattice
# ---------------------------------------------------------------------------
def oddpart(x):
    while x % 2 == 0:
        x //= 2
    return x


def oct2(f):
    f = Fraction(f)
    while f < 1:
        f *= 2
    while f >= 2:
        f /= 2
    return f


def tenney_height(r):
    r = Fraction(r)
    return log2(r.numerator * r.denominator)


def cents(r):
    return 1200.0 * log2(float(r))


LIMIT = 7  # 7-limit odd tonality diamond -> 13 ratios


def build_diamond(n):
    out = set()
    for oa in range(1, n + 1, 2):
        for ob in range(1, n + 1, 2):
            base = Fraction(oa, ob)
            for i in range(-4, 5):
                r = oct2(base * Fraction(2) ** i)
                if oddpart(r.numerator) <= n and oddpart(r.denominator) <= n:
                    out.add(r)
    return sorted(out)


DIAMOND = build_diamond(LIMIT)
DIAMOND_INFO = [{"ratio": str(r), "cents": round(cents(r), 2),
                 "height": round(tenney_height(r), 3),
                 "nearest_semi_from_tonic": int(round(cents(r) / 100.0))}
                for r in DIAMOND]
# nearest-TET semitone offset from tonic D, per ratio
SEMI = {r: int(round(cents(r) / 100.0)) for r in DIAMOND}
HEIGHT = {r: tenney_height(r) for r in DIAMOND}
# height-ordered index table for the walk
ORDER = sorted(range(len(DIAMOND)), key=lambda i: HEIGHT[DIAMOND[i]])


def hexad(identity, polarity, n=LIMIT):
    """Otonality (shared numerator m) / Utonality (shared denominator m)."""
    tones = set()
    for k in range(1, n + 1, 2):
        f = oct2(Fraction(k, identity)) if polarity == "uto" else oct2(Fraction(identity, k))
        tones.add(f)
    return sorted(tones)


IDENTITIES = list(range(1, LIMIT + 1, 2))          # [1,3,5,7]
HEXADS = {m: {p: hexad(m, p) for p in ("oto", "uto")} for m in IDENTITIES}
# identity lattice: common-tone counts between consecutive identities
LATTICE = {}
for a, b in zip(IDENTITIES, IDENTITIES[1:]):
    LATTICE[f"{a}-{b}"] = {
        "oto-oto": len(set(HEXADS[a]["oto"]) & set(HEXADS[b]["oto"])),
        "oto-uto": len(set(HEXADS[a]["oto"]) & set(HEXADS[b]["uto"])),
    }

print("=== ABSTRACT LAYER: D(7) tonality diamond ===")
print(f"|D({LIMIT})| = {len(DIAMOND)} ratios")
for info in DIAMOND_INFO:
    print(f"  {info['ratio']:>6}  cents={info['cents']:7.2f}  H={info['height']:6.3f}  "
          f"semi={info['nearest_semi_from_tonic']}")
print("\nOto(1):", [str(r) for r in HEXADS[1]["oto"]])
print("Uto(1):", [str(r) for r in HEXADS[1]["uto"]])
print("Oto(3):", [str(r) for r in HEXADS[3]["oto"]])
print("Uto(3):", [str(r) for r in HEXADS[3]["uto"]])
print("identity lattice common-tone counts:", LATTICE)

# --- concrete chord map: identity walk -> D Mixolydian triads ---------------
# Root ratio (relative to D), Tenney height, and role (Partch identity).
CHORDS = {
    "D":  {"pcs": {2, 6, 9},   "bass": 38, "triad": [50, 54, 57],
           "ratio": "1/1", "height": 0.0,   "role": "identity 1 nexus (HOME)"},
    "Am": {"pcs": {9, 0, 4},   "bass": 45, "triad": [57, 60, 64],
           "ratio": "3/2", "height": 2.585, "role": "identity 3 dominant fifth"},
    "G":  {"pcs": {7, 11, 2},  "bass": 43, "triad": [55, 59, 62],
           "ratio": "4/3", "height": 3.585, "role": "subdominant (utonality)"},
    "C":  {"pcs": {0, 4, 7},   "bass": 36, "triad": [48, 52, 55],
           "ratio": "7/4", "height": 4.807, "role": "identity 7 harmonic seventh (TENSE)"},
}
CHORD_KEYS = list(CHORDS.keys())

# form layout: 6 sections, 40 bars
NAMES = ["Intro", "Verse", "Chorus", "Verse", "Chorus", "Outro"]
BARS = [4, 8, 8, 8, 8, 4]
N_SECTIONS = len(NAMES)
N_BARS = sum(BARS)            # 40
SECTION_TICKS = [b * BAR for b in BARS]

# per-section chord rotation: identity walk with common-tone retention
SECTION_ROT = {
    0: ["D", "D", "G", "D"],      # Intro   HOME (H 0)
    1: ["D", "G", "C", "G"],      # Verse   build toward harmonic-7th C
    2: ["C", "G", "D", "C"],      # Chorus  bVII peak (TENSE)
    3: ["D", "Am", "G", "D"],     # Verse2  moderate (identity 3)
    4: ["C", "G", "D", "G"],      # Chorus2 lift
    5: ["G", "D", "G", "D"],      # Outro   cadence -> 1/1 nexus (D)
}

# voices: (voice name, registry instrument, GM program, channel)
VOICES = [
    ("Fiddle", "violin",        40, 0),
    ("Flute",  "flute",         73, 1),
    ("Guitar", "steel_acoustic", 25, 2),
    ("Bass",   "acoustic_bass", 32, 3),
    ("Drums",  "drum_kit",       0, 9),
]
N_V = len(VOICES)
vnames = [v[0] for v in VOICES]


def bar_to_section(bar):
    cum = 0
    for s in range(N_SECTIONS):
        if bar < cum + BARS[s]:
            return s, bar - cum
        cum += BARS[s]
    return N_SECTIONS - 1, BARS[-1] - 1


def chord_key_for_bar(bar):
    s, lb = bar_to_section(bar)
    return SECTION_ROT[s][lb % 4]


def chord_tones_for(ck):
    triad = CHORDS[ck]["triad"]
    return sorted({t + 12 * o for t in triad for o in range(-3, 5)})


# ---------------------------------------------------------------------------
# Phase 1: raw diamond walk -> single-voice unquantized melody (off-grid)
# ---------------------------------------------------------------------------
def diamond_walk(seed, dur_ticks, center, n_events, target_h):
    """Walk the height-ordered diamond pool, drifting toward the section's
    Tenney-height target. Onsets + durations jittered (off-grid); pitch =
    nearest-TET projection of the ratio (cents deviation recorded separately)."""
    r = np.random.default_rng(seed)
    idx = 0                     # start at 1/1 (lowest height, HOME)
    step = dur_ticks / n_events
    events = []
    cents_dev = []
    for k in range(n_events):
        onset = int(k * step + r.normal(0.0, 55.0))
        onset = max(0, min(onset, dur_ticks - 60))
        dur = min(dur_ticks - onset, int(max(120.0, step * r.uniform(0.6, 1.05))))
        cur_h = HEIGHT[DIAMOND[ORDER[idx]]]
        if cur_h < target_h - 0.5:
            idx += 1
        elif cur_h > target_h + 0.5:
            idx -= 1
        else:
            idx += int(r.integers(-1, 2))
        idx = int(np.clip(idx, 0, len(ORDER) - 1))
        ratio = DIAMOND[ORDER[idx]]
        pitch = center + SEMI[ratio]
        cents_dev.append(round(cents(ratio) - SEMI[ratio] * 100.0, 2))
        velo = int(np.clip(70 + 25 * r.standard_normal(), 55, 110))
        events.append(MusicEvent(pitch=int(round(pitch)), volume=velo,
                                 start_tick=onset, end_tick=onset + dur))
    return events, cents_dev


# per-section generative params: (center, n_events, target height) follows the
# Tenney height tension arc (register rises with tension, cadence returns HOME)
LEAD_PARAMS = {
    0: dict(center=67, n_events=16, target_h=0.0),    # Intro   HOME, low register
    1: dict(center=72, n_events=40, target_h=3.0),    # Verse   rise
    2: dict(center=79, n_events=56, target_h=4.8),    # Chorus  TENSE peak
    3: dict(center=74, n_events=40, target_h=2.6),    # Verse2  moderate
    4: dict(center=79, n_events=56, target_h=4.8),    # Chorus2 lift
    5: dict(center=67, n_events=20, target_h=0.0),    # Outro   cadence HOME
}

phase1 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
phase1.create_matrix(num_voices=1, num_sections=N_SECTIONS)
phase1.add_voice("DiamondRaw", program=40, channel=0)
cents_log = {}
for s, name in enumerate(NAMES):
    phase1.add_section(name, bars=BARS[s])
    st = SECTION_TICKS[s]
    evs, devs = diamond_walk(SEED + s, st, **LEAD_PARAMS[s])
    cents_log[s] = devs
    evs.append(MusicEvent(pitch=0, volume=0, start_tick=st - 1, end_tick=st))
    phase1.set_unit(0, s, MusicUnit(events=evs))
ok1, msg1 = phase1.validate()
print("\nPHASE1 validate:", msg1)
P1_MIDI = os.path.join(MIDI_DIR, "287-celtic-tonality-diamond-phase1.mid")
phase1.to_midi(P1_MIDI)
print("phase1 written:", P1_MIDI)


# ---------------------------------------------------------------------------
# Phase 2: tiered rules post-process + full 5-voice Celtic texture
# ---------------------------------------------------------------------------
def process_lead(raw_events, s):
    """grid-lock -> tiered snap (strong=scale+chord, weak=scale) -> voice-leading
    cap (leap<=9) -> register clamp -> dedup."""
    pitched = [e for e in raw_events if int(e.pitch) != 0]
    g = []
    for e in pitched:
        st = int(round(int(e.start_tick) / GRID) * GRID)
        st = min(st, SECTION_TICKS[s] - GRID)
        g.append(MusicEvent(pitch=int(e.pitch), volume=int(e.volume),
                            start_tick=st, end_tick=max(st + GRID, int(e.end_tick))))
    q = []
    for e in g:
        st = int(e.start_tick)
        lb = min(st // BAR, BARS[s] - 1)
        ck = SECTION_ROT[s][lb % 4]
        ct = chord_tones_for(ck)
        raw = max(SCALE_ROOT, min(SCALE_ROOT + 36, float(int(e.pitch))))
        w = classify_weight(st % BAR, STRONG_GRID_44, bar_ticks=BAR)
        p = sq.tiered_quantize(raw, weight=w, chord_tones=ct)
        q.append(MusicEvent(pitch=p, volume=int(e.volume),
                            start_tick=st, end_tick=int(e.end_tick)))
    # voice-leading cap
    for i in range(1, len(q)):
        if abs(int(q[i].pitch) - int(q[i - 1].pitch)) > 9:
            lb = min(int(q[i].start_tick) // BAR, BARS[s] - 1)
            ck = SECTION_ROT[s][lb % 4]
            ct = chord_tones_for(ck)
            q[i] = MusicEvent(
                pitch=min(ct, key=lambda c: abs(c - int(q[i - 1].pitch))),
                volume=int(q[i].volume),
                start_tick=int(q[i].start_tick), end_tick=int(q[i].end_tick))
    # dedup (start_tick, pitch) keep longest
    best = {}
    for e in q:
        key = (int(e.start_tick), int(e.pitch))
        if key not in best or int(e.end_tick) > int(best[key].end_tick):
            best[key] = e
    return sorted(best.values(), key=lambda e: (int(e.start_tick), int(e.pitch)))


phase2 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
phase2.create_matrix(num_voices=N_V, num_sections=N_SECTIONS)
for name, rn, prog, ch in VOICES:
    phase2.add_voice(name, program=prog, channel=ch)
for s, n in enumerate(NAMES):
    phase2.add_section(n, bars=BARS[s])

# lead (row 0): tiered-quantize phase-1 raw draft per section
for s in range(N_SECTIONS):
    raw_events = list(phase1.matrix.get_unit((0, s)).events)
    phase2.set_unit(0, s, MusicUnit(events=process_lead(raw_events, s)))

acc = {(r, s): [] for r in range(1, 5) for s in range(N_SECTIONS)}

# --- Guitar (row 2): boom-chick strum (root on 1&3, triad strum on 2&4)
for bar in range(N_BARS):
    s, lb = bar_to_section(bar)
    ck = chord_key_for_bar(bar)
    triad = CHORDS[ck]["triad"]
    t0 = lb * BAR
    acc[(2, s)].append(MusicEvent(pitch=triad[0], volume=76,
                                  start_tick=t0, end_tick=t0 + 400))
    for tone in triad:
        acc[(2, s)].append(MusicEvent(pitch=tone + 12, volume=60,
                                      start_tick=t0 + 480, end_tick=t0 + 760))
    acc[(2, s)].append(MusicEvent(pitch=triad[2], volume=72,
                                  start_tick=t0 + 960, end_tick=t0 + 1320))
    for tone in triad:
        acc[(2, s)].append(MusicEvent(pitch=tone + 12, volume=58,
                                      start_tick=t0 + 1440, end_tick=t0 + 1720))

# --- Bass (row 3): walking (root, fifth, root, octave per bar)
for bar in range(N_BARS):
    s, lb = bar_to_section(bar)
    ck = chord_key_for_bar(bar)
    root = CHORDS[ck]["bass"]
    t0 = lb * BAR
    for beat in range(4):
        bt = t0 + beat * 480
        if beat == 0:
            p, v = root, 104
        elif beat == 1:
            p, v = root + 7, 84
        elif beat == 2:
            p, v = root, 96
        else:
            p, v = root + 12, 88
        acc[(3, s)].append(MusicEvent(pitch=p, volume=v, start_tick=bt, end_tick=bt + 380))

# --- Flute (row 1): counterline (sustained chord third/fifth above the fiddle)
for bar in range(N_BARS):
    s, lb = bar_to_section(bar)
    ck = chord_key_for_bar(bar)
    triad = CHORDS[ck]["triad"]
    t0 = lb * BAR
    if s in (2, 4):          # choruses: full counterline
        acc[(1, s)].append(MusicEvent(pitch=triad[1] + 12, volume=64,
                                      start_tick=t0, end_tick=t0 + 900))
        acc[(1, s)].append(MusicEvent(pitch=triad[2] + 12, volume=58,
                                      start_tick=t0 + 960, end_tick=t0 + 1800))
    elif s in (1, 3):        # verses: light counter
        acc[(1, s)].append(MusicEvent(pitch=triad[2] + 12, volume=52,
                                      start_tick=t0, end_tick=t0 + 1680))
    elif s == 5:             # outro: resolve to root
        acc[(1, s)].append(MusicEvent(pitch=triad[0] + 12, volume=56,
                                      start_tick=t0, end_tick=t0 + BAR - 60))

for (r, s), evs in acc.items():
    phase2.set_unit(r, s, MusicUnit(events=evs))

# --- Drums (row 4, channel 9): reel backbeat (kick 1&3, snare 2&4, hats)
KICK, SNARE, HHAT, CRASH = 36, 38, 42, 49
DRUM_DENS = {0: 0.5, 1: 0.8, 2: 1.0, 3: 0.8, 4: 1.0, 5: 0.9}
for s in range(N_SECTIONS):
    dens = DRUM_DENS[s]
    evs = []
    for lb in range(BARS[s]):
        t0 = lb * BAR
        evs.append(MusicEvent(pitch=KICK, volume=104, start_tick=t0, end_tick=t0 + 140))
        evs.append(MusicEvent(pitch=KICK, volume=100, start_tick=t0 + 960, end_tick=t0 + 1100))
        if dens >= 0.7:
            evs.append(MusicEvent(pitch=SNARE, volume=100, start_tick=t0 + 480, end_tick=t0 + 600))
            evs.append(MusicEvent(pitch=SNARE, volume=102, start_tick=t0 + 1440, end_tick=t0 + 1560))
        if dens >= 0.8:
            for k in (240, 720, 1200, 1680):
                evs.append(MusicEvent(pitch=HHAT, volume=54, start_tick=t0 + k, end_tick=t0 + k + 60))
        if dens >= 1.0:
            for k in (120, 600, 1080, 1560):
                evs.append(MusicEvent(pitch=HHAT, volume=40, start_tick=t0 + k, end_tick=t0 + k + 40))
    if s == N_SECTIONS - 1:
        t0 = (BARS[s] - 1) * BAR
        evs.append(MusicEvent(pitch=CRASH, volume=90, start_tick=t0 + 1680, end_tick=t0 + 1800))
    phase2.set_unit(4, s, MusicUnit(events=evs))


# --- normalize every cell to exact section boundary (zero-drift invariant)
def normalize_cell(unit, total_ticks):
    out = []
    for e in list(unit.events):
        p, v = int(e.pitch), int(e.volume)
        st, et = int(e.start_tick), int(e.end_tick)
        if et > total_ticks:
            et = total_ticks
        if st >= total_ticks:
            st = total_ticks - 1
        out.append(MusicEvent(pitch=p, volume=v, start_tick=st, end_tick=et))
    if not any(int(e.pitch) == 0 and int(e.end_tick) == total_ticks for e in out):
        out.append(MusicEvent(pitch=0, volume=0, start_tick=total_ticks - 1,
                              end_tick=total_ticks))
    out.sort(key=lambda e: (int(e.start_tick), int(e.pitch)))
    return MusicUnit(events=out)


for v in range(N_V):
    for s in range(N_SECTIONS):
        u = phase2.matrix.get_unit((v, s))
        st = SECTION_TICKS[s]
        if u is None or len(u.events) == 0:
            phase2.set_unit(v, s, create_empty_unit(st))
        else:
            phase2.set_unit(v, s, normalize_cell(u, st))

ok2, msg2 = phase2.validate()
print("\nPHASE2 validate:", msg2)
assert ok1 and ok2, (msg1, msg2)


# ---------------------------------------------------------------------------
# Audits (pre-humanization = "perfect" layer)
# ---------------------------------------------------------------------------
def grid_audit(composer):
    results = {}
    for v in range(N_V):
        onsets = []
        for s in range(N_SECTIONS):
            u = composer.matrix.get_unit((v, s))
            if u is None:
                continue
            for e in u.events:
                if int(e.pitch) != 0:
                    onsets.append(int(e.start_tick))
        off16 = [o for o in onsets if o % 120 != 0]
        off8 = [o for o in onsets if o % 240 != 0]
        results[vnames[v]] = {"onsets": len(onsets),
                              "off_16th": len(off16), "off_8th": len(off8)}
    return results


def harmony_audit(composer):
    results = {}
    for v in range(4):  # pitched voices only (drums ch9 excluded)
        agg = {"total": 0, "untagged_out_of_scale": 0, "tagged_non_resolving": 0,
               "strong_violations": 0, "tagged_resolving": 0,
               "weak_in_scale": 0, "strong_ok": 0}
        for s in range(N_SECTIONS):
            u = composer.matrix.get_unit((v, s))
            if u is None:
                continue
            notes = [e for e in u.events if int(e.pitch) != 0]
            cpb = {b: CHORDS[SECTION_ROT[s][b % 4]]["pcs"] for b in range(BARS[s])}
            r = audit_voice(notes, sorted(SCALE_PCS), chord_pcs_by_bar=cpb,
                            strong_grid=STRONG_GRID_44, bar_ticks=BAR, grid=EIGHTH)
            for k in ("total", "untagged_out_of_scale", "tagged_non_resolving",
                      "strong_violations", "tagged_resolving", "weak_in_scale",
                      "strong_ok"):
                agg[k] += int(getattr(r, k, 0))
        results[vnames[v]] = agg
    return results


perfect_grid = grid_audit(phase2)
perfect_harmony = harmony_audit(phase2)
print("\nGRID AUDIT (perfect):", json.dumps(perfect_grid, indent=2))
print("\nHARMONY AUDIT (perfect):", json.dumps(perfect_harmony, indent=2))

harmony_pass = all(
    perfect_harmony[v]["untagged_out_of_scale"] == 0
    and perfect_harmony[v]["tagged_non_resolving"] == 0
    and perfect_harmony[v]["strong_violations"] == 0
    for v in vnames[:4]
)
grid_pass = all(perfect_grid[v]["off_16th"] == 0 for v in vnames)
print("\nHARMONY PASS:", harmony_pass, "| GRID PASS:", grid_pass)
assert harmony_pass, "harmony audit failed"
assert grid_pass, "grid audit failed (perfect must be 0 off-16th)"

from visualization.grid import write_grid_visualization  # noqa: E402
grid_path = os.path.join(ANALYSIS_DIR, "grid_visualization.txt")
write_grid_visualization(phase2.matrix, grid_path, ticks_per_character=120,
                         voice_names=vnames, bpm=BPM,
                         mode="D Mixolydian / TDRPC tonality diamond + bVII cadence")


# ---------------------------------------------------------------------------
# Dual-version export (perfect + humanized) via canonical export_dual
# ---------------------------------------------------------------------------
from workflows.humanize import export_dual  # noqa: E402
hz_instruments = {v[0]: by_name(v[1]).humanize_dna for v in VOICES}
hz_seed = SEED
PERF_MIDI = os.path.join(MIDI_DIR, "287-celtic-tonality-diamond-perfect.mid")
HUM_MIDI = os.path.join(MIDI_DIR, "287-celtic-tonality-diamond-humanized.mid")
hz = export_dual(phase2, PERF_MIDI, HUM_MIDI, style=STYLE, seed=hz_seed,
                 bpm=BPM, instruments=hz_instruments)
print("\ndual-version exported")
print("humanize summary:", json.dumps(hz, indent=2))

humanized_grid = grid_audit(phase2)
print("\nGRID AUDIT (humanized):", json.dumps(humanized_grid, indent=2))
hz_off = sum(humanized_grid[v]["off_16th"] for v in vnames)
print("humanized total off-16th:", hz_off)


# ---------------------------------------------------------------------------
# READ-ONLY mido verification: zero-drift readback + off-grid counts
# ---------------------------------------------------------------------------
import mido  # noqa: E402


def readback(path):
    mid = mido.MidiFile(path)

    def track_total(tr):
        t = 0
        for m in tr:
            if not m.is_meta:
                t += m.time
        return t
    totals = [track_total(t) for t in mid.tracks]
    voice_tots = totals[1:]
    zero_drift = len(set(voice_tots)) == 1
    return {"tracks": totals, "voice_tots": voice_tots,
            "zero_drift": zero_drift, "length": voice_tots[0] if voice_tots else 0}


rb_perfect = readback(PERF_MIDI)
rb_humanized = readback(HUM_MIDI)
rb_phase1 = readback(P1_MIDI)
print("\nZERO-DRIFT perfect:", rb_perfect["zero_drift"], rb_perfect["length"])
print("ZERO-DRIFT humanized:", rb_humanized["zero_drift"], rb_humanized["length"])
print("ZERO-DRIFT phase1:", rb_phase1["zero_drift"], rb_phase1["length"])
assert rb_perfect["zero_drift"] and rb_humanized["zero_drift"] and rb_phase1["zero_drift"]

for p in (P1_MIDI, PERF_MIDI, HUM_MIDI):
    sz = os.path.getsize(p)
    print("size", os.path.basename(p), sz)
    assert sz > 40, p


# ---------------------------------------------------------------------------
# provenance + summary
# ---------------------------------------------------------------------------
from workflows.provenance import write_provenance, AI_ASSISTED  # noqa: E402

section_roots = [SECTION_ROT[s][1 % 4] for s in range(N_SECTIONS)]
prog_per_section = {NAMES[s]: SECTION_ROT[s] for s in range(N_SECTIONS)}

provenance_meta = {
    "bpm": BPM, "key": KEY, "scale": SCALE_NAME,
    "scale_pcs": sorted(SCALE_PCS),
    "style": STYLE, "method_id": METHOD_ID, "method": METHOD_NAME,
    "layer": LAYER, "form": FORM,
    "diamond_limit": LIMIT, "diamond_size": len(DIAMOND),
    "diamond": DIAMOND_INFO,
    "hexads": {str(m): {p: [str(r) for r in HEXADS[m][p]] for p in ("oto", "uto")}
               for m in IDENTITIES},
    "identity_lattice": LATTICE,
    "sections": N_SECTIONS, "bars": N_BARS,
    "progression_per_section": prog_per_section,
    "section_roots_midpoint": section_roots,
    "chord_ratio_map": {k: {"ratio": CHORDS[k]["ratio"], "height": CHORDS[k]["height"],
                            "role": CHORDS[k]["role"]} for k in CHORD_KEYS},
    "seed": SEED, "humanize_seed": hz_seed,
    "voices": [{"name": v[0], "instrument": v[1], "program": v[2], "channel": v[3]}
               for v in VOICES],
}

write_provenance(P1_MIDI, AI_ASSISTED,
                 "TDRPC tonality diamond walk + musicom rules",
                 parameters=dict(provenance_meta, phase="1"),
                 notes="raw single-voice height-directed walk over the D(7) just-ratio "
                       "diamond, nearest-TET projection, jittered off-grid rhythm, no harmony")
write_provenance(PERF_MIDI, AI_ASSISTED,
                 "TDRPC tonality diamond walk + musicom rules",
                 parameters=dict(provenance_meta, phase="2-perfect", humanize=None),
                 notes="grid-locked perfect layer: tiered scale+chord snap per bar, "
                       "voice-leading checked, zero humanization")
write_provenance(HUM_MIDI, AI_ASSISTED,
                 "TDRPC tonality diamond walk + musicom rules",
                 parameters=dict(provenance_meta, phase="2-humanized",
                                 humanize_seed=hz_seed, humanize_profiles=hz),
                 notes="humanized layer: celtic style profile + per-instrument DNA")

with open(os.path.join(PROJ, "provenance.json"), "w") as f:
    json.dump(provenance_meta, f, indent=2)

summary = {
    "perfect_grid": perfect_grid,
    "humanized_grid": humanized_grid,
    "harmony": perfect_harmony,
    "humanize": hz,
    "zero_drift": {"perfect": rb_perfect["zero_drift"],
                   "humanized": rb_humanized["zero_drift"],
                   "phase1": rb_phase1["zero_drift"],
                   "length_ticks": rb_perfect["length"]},
}
with open(os.path.join(ANALYSIS_DIR, "summary.json"), "w") as f:
    json.dump(summary, f, indent=2)

print("\nPROGRESSION (per section):")
for s in range(N_SECTIONS):
    print("  ", NAMES[s], SECTION_ROT[s],
          "midpoint:", SECTION_ROT[s][1 % 4],
          "H=", CHORDS[SECTION_ROT[s][1 % 4]]["height"])

print("\nDONE compose.")
