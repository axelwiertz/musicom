# -*- coding: utf-8 -*-
"""267-blues-interval-exchange -- Method 121 IETC (Interval Exchange Transformation).

Two-phase architecture, engine-only (structures + unitmatrix_composer +
scale_quantizer tiered snap + workflows.humanize.export_dual + pitch_audit).

METHOD (concrete, Rules-Based): a 7-block Interval Exchange Transformation
partitions the unit circle into 7 blocks, one per scale degree of Ab natural
minor, whose widths encode TONAL GRAVITY (tonic widest, then 5th, 4th, b3,
b7, b6, 2nd). Iterating the IET from one seed point yields the melodic degree
stream. Unique ergodicity (irrational rotation number alpha = 1/phi^2) forces
the visit frequency of each block to EQUAL its width -- "width IS tonal
gravity". Verified empirically below (400k iterates, error ~1e-6).

PHASE 1: raw draft -- single harmonica voice, degree pc -> pitch with register
drift, off-grid 8th-slot onsets, NO harmony.
PHASE 2: rules -- grid-lock to 16ths, tiered weight-aware snap (strong -> in
scale AND in chord via ScaleQuantizer.tiered_quantize; weak -> in scale only),
plus blues texture: drawbar-organ comp (sustained m7), double-bass shuffle
(dotted-8th+16th lilt), drum backbeat. Dual export (perfect + humanized).
"""
import json
import math
import random
import sys
from pathlib import Path

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer
from workflows.provenance import write_provenance
from workflows.humanize import export_dual
from sound.synthesis.scale_quantizer import ScaleQuantizer, classify_weight

# ---- instrument registry (source of truth) ---------------------------------
INSTR_DIR = "/opt/data/repos/musicom/projects/Instruments"
if INSTR_DIR not in sys.path:
    sys.path.insert(0, INSTR_DIR)
from instrument_registry import HARMONICA, DRAWBAR_ORGAN, DOUBLE_BASS, DRUM_KIT  # noqa: E402

# ---- concept ---------------------------------------------------------------
GENRE = "Blues"
STYLE = "Blues"
NAME = "267-blues-interval-exchange"
ROOT = Path(f"/opt/data/projects/Styles/{GENRE}/{NAME}")
for sub in ("MIDI", "Audio", "Analysis"):
    (ROOT / sub).mkdir(parents=True, exist_ok=True)

TONIC = 8                       # Ab
KEY_NAME = "Ab natural minor (aeolian)"
NAT = [8, 10, 11, 1, 3, 4, 6]   # Ab Bb Cb Db Eb Fb Gb
SCALE_PCS = set(NAT)
BPM = 100
TPB = 480
BAR = 1920
EIGHTH = 240
SIXTEENTH = 120
BEAT = 480
SEED = 20261025

# ============================================================================
# METHOD 121 IETC -- 7-block Interval Exchange Transformation
# ============================================================================
PHI = (1.0 + math.sqrt(5.0)) / 2.0

# degree index -> pitch class (scale position in Ab natural minor)
DEGREE_PC = [8, 10, 11, 1, 3, 4, 6]   # tonic 2nd b3 4th 5th b6 b7
DEGREE_NAME = ["1 (tonic)", "2", "b3", "4", "5", "b6", "b7"]

# widths = tonal gravity. Group A (deg 0-3) totals 1/phi, group B (deg 4-6)
# totals 1/phi^2, so the rotation number alpha = 1/phi^2 is IRRATIONAL
# (=> aperiodic, uniquely ergodic).
_g0 = [0.28, 0.05, 0.14, 0.15]
_g1 = [0.20, 0.06, 0.12]
_wA = [w * (1.0 / PHI) / sum(_g0) for w in _g0]
_wB = [w * (1.0 / PHI ** 2) / sum(_g1) for w in _g1]
WIDTHS = _wA + _wB
PERM = [(j + 3) % 7 for j in range(7)]        # rotation-type IET (S_{3,4})
ALPHA = sum(WIDTHS[4:])                        # = 1/phi^2, the rotation number

assert abs(sum(WIDTHS) - 1.0) < 1e-12
assert abs(ALPHA - 1.0 / PHI ** 2) < 1e-12, ALPHA

CUM = [0.0] * 8
for i in range(7):
    CUM[i + 1] = CUM[i] + WIDTHS[i]
TPOS = [sum(WIDTHS[i] for i in range(7) if PERM[i] < PERM[j]) for j in range(7)]


def iet_step(x):
    """Return (T(x), block_index) for the 7-block IET."""
    j = 6
    for k in range(7):
        if CUM[k] <= x < CUM[k + 1]:
            j = k
            break
    return TPOS[j] + (x - CUM[j]), j


def degree_stream(x0, n):
    """Yield n scale-degree pitch classes by iterating the IET orbit."""
    x = x0
    for _ in range(n):
        x, j = iet_step(x)
        yield DEGREE_PC[j], j


# ---- verify unique ergodicity (real number) --------------------------------
_x = 0.3141592653589793
_NCHK = 400000
_counts = [0] * 7
for _ in range(_NCHK):
    _x, _j = iet_step(_x)
    _counts[_j] += 1
ERGODIC_MAX_ERR = max(abs(_counts[j] / _NCHK - WIDTHS[j]) for j in range(7))
print(f"IET widths: {[round(w, 6) for w in WIDTHS]}")
print(f"rotation number alpha = {ALPHA:.12f}  (= 1/phi^2, irrational)")
print(f"unique ergodicity: max |freq - width| = {ERGODIC_MAX_ERR:.6e} "
      f"over {_NCHK} iterates")

# ============================================================================
# 12-BAR MINOR BLUES HARMONY (diatonic m7 chords in Ab natural minor)
# ============================================================================
# i7 | i7 | i7 | i7 | iv7 | iv7 | i7 | i7 | v7 | iv7 | i7 | i7
CHORD_ROOT_PC = [8, 8, 8, 8, 1, 1, 8, 8, 3, 1, 8, 8]
CHORD_LABEL = ["i7", "i7", "i7", "i7", "iv7", "iv7",
               "i7", "i7", "v7", "iv7", "i7", "i7"]
# bass roots (MIDI, within Double Bass sweet spot 40-55)
CHORD_ROOT_MIDI = [44, 44, 44, 44, 49, 49, 44, 44, 51, 49, 44, 44]
N_BARS = 12


def chord_pcs(root_pc):
    return {(root_pc + i) % 12 for i in (0, 3, 7, 10)}


CHORD_PCS_BY_BAR = {b: sorted(chord_pcs(CHORD_ROOT_PC[b])) for b in range(N_BARS)}


def chord_tones_midi(root_pc, lo, hi):
    pcs = chord_pcs(root_pc)
    return sorted(p for p in range(lo, hi + 1) if p % 12 in pcs)


def nearest_pc_pitch(pc, lo, hi, anchor=None):
    cands = [p for p in range(lo, hi + 1) if p % 12 == pc]
    if not cands:
        return None
    if anchor is None:
        return min(cands, key=lambda p: (abs(p - (lo + hi) // 2), p))
    return min(cands, key=lambda p: (abs(p - anchor), p))


SECTIONS = ["Blues"]
BARS_PER = [12]
N_SECTIONS = 1
SECTION_TICKS = N_BARS * BAR            # 23040

# ============================================================================
# PHASE 1 -- RAW IET DRAFT (single harmonica, off-grid, no harmony)
# ============================================================================
P_ONSET = 0.55
rng1 = random.Random(SEED + 1)

phase1 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=4)
phase1.create_matrix(num_voices=1, num_sections=N_SECTIONS)
phase1.add_voice("HarmonicaRaw", program=HARMONICA.midi_program, channel=0)
phase1.add_section("Blues", bars=N_BARS)

deg_gen = degree_stream(0.6180339887498948, 2000)   # irrational seed point
raw_events = []
prev_end = 0
for slot in range(N_BARS * 8):                       # 8th-note slots (96)
    pc, deg = next(deg_gen)
    if rng1.random() >= P_ONSET:
        continue
    st = slot * EIGHTH + int(rng1.randint(-40, 41))   # off-grid jitter
    st = max(0, min(st, SECTION_TICKS - 1))
    anchor = 72 + 6.0 * math.sin(slot / 5.0) + rng1.uniform(-3, 3)
    p = nearest_pc_pitch(pc, 64, 79, anchor=int(anchor))
    if p is None:
        continue
    if st < prev_end - 10:
        st = prev_end + 10
    dur = int(EIGHTH * (0.85 + 0.4 * rng1.random()))
    en = min(st + dur, SECTION_TICKS)
    if en > st:
        raw_events.append(MusicEvent(pitch=p, volume=int(72 + 24 * rng1.random()),
                                     start_tick=st, end_tick=en))
        prev_end = en
raw_events.append(MusicEvent(0, 0, SECTION_TICKS - 1, SECTION_TICKS))  # landmark
phase1.set_unit(0, 0, MusicUnit(events=sorted(raw_events,
                                              key=lambda e: e.start_tick)))

ok1, msg1 = phase1.validate()
assert ok1, f"phase1 validate failed: {msg1}"
midi1 = ROOT / "MIDI" / f"{NAME}-phase1.mid"
phase1.to_midi(str(midi1))
write_provenance(str(midi1), "ai-generated", f"musicom {NAME}",
                 sources=["methods_db:121 Interval Exchange Transformation",
                          f"style:{STYLE}", "phase:1 raw draft"],
                 parameters={"phase": 1, "seed": SEED, "key": KEY_NAME,
                             "bpm": BPM, "iet_widths": WIDTHS,
                             "iet_perm": PERM, "alpha": ALPHA,
                             "notes": "IET degree pc -> off-grid raw harmonica"})
print(f"phase1 raw events: {len([e for e in raw_events if e.pitch > 0])} "
      f"notes; midi {midi1.stat().st_size} bytes")

# ============================================================================
# PHASE 2 -- RULES (grid-lock + tiered weight-aware snap + blues texture)
# ============================================================================
sq = ScaleQuantizer(root=68, scale="minor")     # Ab natural minor
STRONG = (0, 960)                                # beats 1 & 3


def quantize_to_grid(events, grid=SIXTEENTH):
    q = []
    for e in events:
        if e.pitch == 0:
            q.append(e)
            continue
        st = int(round(e.start_tick / grid) * grid)
        q.append(MusicEvent(pitch=e.pitch, volume=e.volume,
                            start_tick=st, end_tick=max(st + 1, e.end_tick)))
    return q


VOICES = [
    ("Harmonica", HARMONICA.midi_program, 0),      # lead
    ("Organ", DRAWBAR_ORGAN.midi_program, 1),      # comp
    ("Bass", DOUBLE_BASS.midi_program, 2),         # bass
    ("Drums", 0, 9),                               # percussion
]
N_V = len(VOICES)
phase2 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=4)
phase2.create_matrix(num_voices=N_V, num_sections=N_SECTIONS)
for vname, prog, ch in VOICES:
    phase2.add_voice(vname, program=prog, channel=ch)
phase2.add_section("Blues", bars=N_BARS)

# --- lead (harmonica): grid-lock -> tiered weight-aware snap ----------------
lead_events = []
for e in quantize_to_grid(raw_events):
    if e.pitch == 0:
        lead_events.append(e)
        continue
    bar = min(e.start_tick // BAR, N_BARS - 1)
    root_pc = CHORD_ROOT_PC[bar]
    ctones = chord_tones_midi(root_pc, 64, 79)
    w = classify_weight(e.start_tick, STRONG, BAR)
    if w == "strong":
        p = sq.tiered_quantize(e.pitch, "strong", ctones)
    else:
        p = sq.tiered_quantize(e.pitch, "weak")
    p = max(64, min(79, p))
    lead_events.append(MusicEvent(pitch=p, volume=max(70, min(100, e.volume)),
                                  start_tick=e.start_tick,
                                  end_tick=min(e.start_tick + EIGHTH,
                                               SECTION_TICKS)))
phase2.set_unit(0, 0, MusicUnit(events=lead_events))

# --- organ (comp): sustained root-position m7 per bar -----------------------
organ_events = []
for bar in range(N_BARS):
    root_pc = CHORD_ROOT_PC[bar]
    tones = chord_tones_midi(root_pc, 55, 72)[:4]   # root-position m7
    t0 = bar * BAR
    for k, p in enumerate(tones):
        organ_events.append(MusicEvent(pitch=p, volume=52 + 4 * k,
                                       start_tick=t0, end_tick=t0 + BAR - 60))
phase2.set_unit(1, 0, MusicUnit(events=organ_events))

# --- bass (double bass): shuffle lilt (dotted-8th + 16th, all 16th-aligned) --
bass_events = []
SHUF = [0, 360, 480, 840, 960, 1320, 1440, 1800]
for bar in range(N_BARS):
    r = CHORD_ROOT_MIDI[bar]
    root_pc = CHORD_ROOT_PC[bar]
    fifth = r + 7
    b7 = r + 10
    t0 = bar * BAR
    plan = [(0, r, 92), (360, r, 70), (480, fifth, 74), (840, r, 70),
            (960, r, 90), (1320, b7, 70), (1440, fifth, 74), (1800, b7, 72)]
    for off, pitch, vel in plan:
        bass_events.append(MusicEvent(pitch=pitch, volume=vel,
                                      start_tick=t0 + off,
                                      end_tick=t0 + off + EIGHTH - 30))
phase2.set_unit(2, 0, MusicUnit(events=bass_events))

# --- drums: blues shuffle backbeat ------------------------------------------
KICK, SNARE, CLHAT, OPENHAT = 36, 38, 42, 46
drum_events = []
for bar in range(N_BARS):
    t0 = bar * BAR
    for off in SHUF:                                   # swung 8ths (16th grid)
        drum_events.append(MusicEvent(pitch=CLHAT, volume=42,
                                      start_tick=t0 + off,
                                      end_tick=t0 + off + 60))
    for kb in (0, 960):                                # kick 1 & 3
        drum_events.append(MusicEvent(pitch=KICK, volume=96,
                                      start_tick=t0 + kb,
                                      end_tick=t0 + kb + 120))
    for sb in (480, 1440):                             # snare 2 & 4
        drum_events.append(MusicEvent(pitch=SNARE, volume=88,
                                      start_tick=t0 + sb,
                                      end_tick=t0 + sb + 120))
    if bar in (7, 11):                                 # turnaround pickup
        drum_events.append(MusicEvent(pitch=OPENHAT, volume=60,
                                      start_tick=t0 + 1800,
                                      end_tick=t0 + 1800 + 60))
phase2.set_unit(3, 0, MusicUnit(events=drum_events))

# ---- normalize every cell to exact section boundary (zero-drift) -----------
def normalize_cell(unit, total_ticks):
    evs = list(unit.events)
    out = []
    for e in evs:
        if e.end_tick > total_ticks:
            e.end_tick = total_ticks
        if e.start_tick >= total_ticks:
            e.start_tick = total_ticks - 1
        if e.end_tick > e.start_tick:
            out.append(e)
    has_landmark = any(e.pitch == 0 and e.end_tick == total_ticks for e in out)
    if not has_landmark:
        out.append(MusicEvent(0, 0, total_ticks - 1, total_ticks))
    return MusicUnit(events=sorted(out, key=lambda e: (e.start_tick, e.pitch)))


for r in range(N_V):
    u = phase2.matrix.get_unit((r, 0))
    phase2.set_unit(r, 0, normalize_cell(u, SECTION_TICKS))

ok2, msg2 = phase2.validate()
assert ok2, f"phase2 validate failed: {msg2}"

# ---- dual-version export (perfect then humanized) --------------------------
hz_seed = SEED + 1
hz_instruments = {
    "Harmonica": HARMONICA.humanize_dna,
    "Organ": DRAWBAR_ORGAN.humanize_dna,
    "Bass": DOUBLE_BASS.humanize_dna,
    "Drums": DRUM_KIT.humanize_dna,
}
perfect_path = ROOT / "MIDI" / f"{NAME}-perfect.mid"
humanized_path = ROOT / "MIDI" / f"{NAME}-humanized.mid"
hz = export_dual(phase2, str(perfect_path), str(humanized_path),
                 style=STYLE, seed=hz_seed, bpm=BPM, instruments=hz_instruments)

for path, phase, note in ((perfect_path, "2-perfect", "grid-locked"),
                          (humanized_path, "2-humanized", "blues humanized")):
    write_provenance(str(path), "ai-generated", f"musicom {NAME}",
                     sources=["methods_db:121 Interval Exchange Transformation",
                              f"style:{STYLE}", "phase:2 rules"],
                     parameters={"phase": phase, "seed": SEED, "key": KEY_NAME,
                                 "bpm": BPM, "iet_widths": WIDTHS,
                                 "alpha": ALPHA, "humanize": hz, "note": note})
print("perfect midi:", perfect_path, perfect_path.stat().st_size, "bytes")
print("humanized midi:", humanized_path, humanized_path.stat().st_size, "bytes")

# ---- summary ---------------------------------------------------------------
summary = {
    "project": NAME, "genre": GENRE, "style_key": STYLE,
    "method": "121 Interval Exchange Transformation Composition (IETC)",
    "layer": "concrete", "paradigm": "Rules-Based (ergodic/deterministic)",
    "key": KEY_NAME, "tonic_pc": TONIC, "scale_pcs": NAT, "bpm": BPM,
    "form": "blues-12", "sections": SECTIONS, "bars": N_BARS,
    "iet": {
        "widths": WIDTHS, "perm": PERM, "alpha": ALPHA,
        "alpha_is_irrational": True, "degree_pc": DEGREE_PC,
        "degree_name": DEGREE_NAME,
        "ergodic_max_err": ERGODIC_MAX_ERR, "ergodic_n_iterates": _NCHK,
        "note": "width = tonal gravity; unique ergodicity forces "
                "visit-frequency == width",
    },
    "chords": {"roots_pc": CHORD_ROOT_PC, "labels": CHORD_LABEL,
               "roots_midi": CHORD_ROOT_MIDI,
               "pcs_by_bar": CHORD_PCS_BY_BAR},
    "voices": [v for v, _, _ in VOICES],
    "instruments": [HARMONICA.name, DRAWBAR_ORGAN.name,
                    DOUBLE_BASS.name, DRUM_KIT.name],
    "humanize_seed": hz_seed,
    "humanize_stats": hz,
}
with open(ROOT / "Analysis" / "summary.json", "w") as f:
    json.dump(summary, f, indent=2)
print("chords:", " ".join(CHORD_LABEL))
print("DONE compose")
