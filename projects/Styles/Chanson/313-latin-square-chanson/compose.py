# -*- coding: utf-8 -*-
"""313-latin-square-chanson -- Chanson via Latin Square & Orthogonal-Array (ABS-139).

Nightly composition job (2026-11-19). Selection: style=Chanson, method=ABS-139
Latin Square & Orthogonal-Array Composition (LSAC, ABSTRACT layer), form=
verse-chorus (pick_form("chanson") -> Intro/Verse/Chorus/Verse2/Chorus2/Outro,
bars [4,8,8,8,8,4] = 40 bars).

MUSICAL DNA
  - Key G major (ionian) = pc {7,9,11,0,2,4,6}; tonic G.
  - 112 BPM, 4/4, 480 TPB, BAR=1920, 8th=240, 16th=120.
  - Method ABS-139 LSAC (abstract layer): lay the piece out as a Latin square
    over the UnitMatrix -- rows = voice/register layers, columns = time-slot
    classes, symbols = the 7 diatonic scale degrees. Two mutually-orthogonal
    order-7 squares (cyclic):
        L[i][j] = (i + j) mod 7      -> pitch-degree square
        M[i][j] = (i + 2j) mod 7     -> duration-class square (orthogonal mate)
    Every row and column of L is a complete aggregate (permutation of the 7
    degrees); orthogonality means every (degree, duration-class) ordered pair
    occurs exactly once across the 7x7 design -- a complete factorial design.
    The lead melody walks L row-major (bar b -> cell (b//7, b%7)); its onset
    anchor degree = L[row][col], its duration class = M[row][col]. The odd
    order 7 guarantees a transversal (through-line) -- the main diagonal
    L[i][i] = (2i)%7 = [0,2,4,6,1,3,5] is one (Ryser 1967).
  - The duration class directly drives melodic density: long cells (whole /
    dotted-half / half) -> a single held anchor note; short cells -> a 4-note
    figure (anchor + chord-tone response + two in-scale passing notes).
  - 5-voice Chanson texture: Trumpet lead (Latin-square melody), Accordion
    musette comp (voice-led triads), steel-string Guitar strum (8th chords),
    Double Bass (root/fifth), Drum Kit (march-like 4/4).

TWO-PHASE
  Phase 1 (raw): single trumpet voice, the raw Latin-square anchor stream --
    jittered pitch (scale-degree note + sigma=0.35) + off-grid onsets + the
    orthogonal duration class; own composer + validate().
  Phase 2 (rules): tiered quantize (strong -> scale THEN chord tone, weak ->
    scale only via ScaleQuantizer.tiered_quantize), 8th-grid snap, voice-led
    comp triads, register enforcement, 5-voice Chanson texture.
  Dual-version: export_dual -> -perfect.mid (grid-locked) + -humanized.mid.
"""
import json
import os
import sys
import hashlib

import numpy as np

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer
from workflows.humanize import export_dual
from workflows.provenance import write_provenance, AI_ASSISTED
from visualization.grid import write_grid_visualization
from rules.progression import Scale7ChordDegree
from rules.voice_leading import VoiceLeadingRules
from sound.synthesis.scale_quantizer import ScaleQuantizer, STRONG_GRID, classify_weight

_INSTR_DIR = "/opt/data/repos/musicom/projects/Instruments"
if _INSTR_DIR not in sys.path:
    sys.path.insert(0, _INSTR_DIR)
from instrument_registry import (  # noqa: E402
    TRUMPET, ACCORDION, STEEL_ACOUSTIC, DOUBLE_BASS, DRUM_KIT)

# ---------------------------------------------------------------------------
# Project layout / identity
# ---------------------------------------------------------------------------
GENRE = "Chanson"
STYLE = "chanson"
PROJECT = "313-latin-square-chanson"
BASE = os.path.join("/opt/data/projects/Styles", GENRE, PROJECT)
MIDI_DIR = os.path.join(BASE, "MIDI")
AUDIO_DIR = os.path.join(BASE, "Audio")
ANALYSIS_DIR = os.path.join(BASE, "Analysis")
for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
    os.makedirs(d, exist_ok=True)

BPM = 112
TPB = 480
BPB = 4
BAR = TPB * BPB                     # 1920
GRID = 240                          # 8th (snap target)
EIGHTH = 240
SIXTEENTH = 120
QUARTER = 480
TOTAL_BARS = 40
TOTAL_TICKS = TOTAL_BARS * BAR

KEY_NAME = "G major"
TONIC_PC = 7                        # G
INTERVALS = [0, 2, 4, 5, 7, 9, 11]  # ionian/major step pattern
KEY_PCS = sorted({(TONIC_PC + iv) % 12 for iv in INTERVALS})  # {0,2,4,5,7,9,11}
TONIC_BASE = 55                     # G3 (triad/pad reference)

# Latin-square lead register (trumpet). Row = one octave of G major, G4..G5.
LEAD_BASE = 67                      # G4
LEAD_OFFSETS = [0, 2, 4, 5, 7, 9, 11, 12]


def lead_scale_note(deg):
    """Diatonic scale note (MIDI) for degree 0..6 in the lead register."""
    return Scale7ChordDegree.get_diatonic_note(LEAD_BASE, INTERVALS, deg % 7)


# 0-based degree -> triad quality intervals (G major diatonic)
# 0=G, 1=Am, 2=Bm, 3=C, 4=D, 5=Em, 6=F#dim
QUALITY = {0: (0, 4, 7), 1: (0, 3, 7), 2: (0, 3, 7), 3: (0, 4, 7),
           4: (0, 4, 7), 5: (0, 3, 7), 6: (0, 3, 6)}
DEGREE_NAMES = {0: "G", 1: "Am", 2: "Bm", 3: "C",
                4: "D", 5: "Em", 6: "F#dim"}

# deterministic seeds
hz_seed = int(hashlib.md5(
    (STYLE + KEY_NAME + str(BPM) + str(TOTAL_BARS) + PROJECT).encode()
).hexdigest()[:8], 16) % 100000
raw_seed = 20261119

# ---------------------------------------------------------------------------
# Form (verse-chorus: Intro4 Verse8 Chorus8 Verse2 8 Chorus2 8 Outro4 = 40)
# Chanson-flavoured progressions (I vi IV V / I IV V I turnarounds).
# ---------------------------------------------------------------------------
SECTIONS = [
    ("Intro",   4, [0, 3, 4, 0]),                        # G C D G
    ("Verse",   8, [0, 5, 3, 4, 0, 5, 1, 4]),            # G Em C D G Em Am D
    ("Chorus",  8, [0, 3, 4, 0, 5, 1, 4, 0]),            # G C D G Em Am D G
    ("Verse2",  8, [0, 5, 3, 4, 0, 5, 1, 4]),
    ("Chorus2", 8, [0, 3, 4, 0, 5, 1, 4, 0]),
    ("Outro",   4, [0, 3, 4, 0]),                        # G C D G
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

BAR_TO_SECTION = {}
for name, bars, prog in SECTIONS:
    s0 = SECTION_START[name]
    for b in range(bars):
        BAR_TO_SECTION[s0 + b] = name

VOICES = ["Lead", "Accordion", "Guitar", "Bass", "Drums"]
VOICE_PROGRAMS = [TRUMPET.midi_program, ACCORDION.midi_program,
                  STEEL_ACOUSTIC.midi_program, DOUBLE_BASS.midi_program, 0]
VOICE_CHANNELS = [0, 1, 2, 3, 9]

LEAD_LO, LEAD_HI = 57, 83          # trumpet (range 54-86)
ACCORDION_LO, ACCORDION_HI = 48, 84
GUITAR_LO, GUITAR_HI = 45, 79
BASS_LO, BASS_HI = 40, 55          # double bass sweet spot


# ---------------------------------------------------------------------------
# Method ABS-139: Latin squares (order 7) + orthogonality
# ---------------------------------------------------------------------------
N = 7                               # 7 diatonic degrees

# Latin square L (degree) and its orthogonal mate M (duration class).
# cyclic square L(i,j)=(a*i+b*j)%n is Latin iff gcd(a,n)=gcd(b,n)=1;
# L and M are orthogonal (MOLS pair) because n is prime and gcd(2,7)=1.
L_SQ = [[(i + j) % N for j in range(N)] for i in range(N)]
M_SQ = [[(i + 2 * j) % N for j in range(N)] for i in range(N)]


def _is_latin(M):
    return all(sorted(r) == list(range(N)) for r in M) and \
           all(sorted(M[i][c] for i in range(N)) == list(range(N))
               for c in range(N))


def _orthogonal(A, B):
    return len({(A[i][j], B[i][j]) for i in range(N) for j in range(N)}) == N * N


assert _is_latin(L_SQ) and _is_latin(M_SQ), "Latin-square construction failed"
assert _orthogonal(L_SQ, M_SQ), "L/M are not orthogonal (MOLS pair)"
# odd order 7 -> transversal exists (Ryser): main diagonal L[i][i]=(2i)%7
TRANSVERSAL = [L_SQ[i][i] for i in range(N)]
assert sorted(TRANSVERSAL) == list(range(N)), "diagonal not a transversal"


def cell_for_bar(b):
    """bar b -> (row, col) in the 7x7 design (row-major walk)."""
    return (b // N) % N, b % N


# duration class -> note duration in ticks (orthogonal square = rhythm dim)
DUR_TICKS = {
    0: 4 * QUARTER,                 # whole
    1: 3 * QUARTER,                 # dotted half
    2: 2 * QUARTER,                 # half
    3: QUARTER + EIGHTH,            # dotted quarter
    4: QUARTER,                     # quarter
    5: EIGHTH,                      # 8th
    6: EIGHTH + SIXTEENTH,          # 8th + 16th
}
LONG_CELLS = (0, 1, 2)              # whole / dotted-half / half -> held anchor


def simulate_latin(rng):
    """Walk the design bar-by-bar -> raw (bar, degree, durclass) records."""
    records = []
    for b in range(TOTAL_BARS):
        row, col = cell_for_bar(b)
        deg = L_SQ[row][col]
        dc = M_SQ[row][col]
        jit = int(rng.integers(-25, 26))
        tick_abs = max(0, min(TOTAL_TICKS - 30, b * BAR + jit))
        p = float(lead_scale_note(deg)) + float(rng.normal(0.0, 0.35))
        vel = int(rng.integers(72, 100))
        records.append({"tick_abs": tick_abs, "pitch": p, "dur": DUR_TICKS[dc],
                        "vel": vel, "bar": b, "degree": deg, "durclass": dc,
                        "row": row, "col": col,
                        "chord_degree": BAR_DEGREES[b]})
    return records


# ---------------------------------------------------------------------------
# Diatonic helpers
# ---------------------------------------------------------------------------
def diatonic(deg_index, base=TONIC_BASE):
    return Scale7ChordDegree.get_diatonic_note(base, INTERVALS, deg_index)


def chord_pcs(d):
    root_pc = (TONIC_PC + INTERVALS[d]) % 12
    return sorted({(root_pc + iv) % 12 for iv in QUALITY[d]})


def chord_tones(d, lo=34, hi=91):
    root_pc = (TONIC_PC + INTERVALS[d]) % 12
    out = set()
    for octv in range(0, 9):
        for iv in QUALITY[d]:
            n = root_pc + 12 * octv + iv
            if lo <= n <= hi:
                out.add(n)
    return sorted(out)


def triad(d, base=TONIC_BASE):
    return sorted([diatonic(d, base), diatonic(d + 2, base),
                   diatonic(d + 4, base)])


# ---------------------------------------------------------------------------
# Phase 1 raw draft (single voice, unquantized)
# ---------------------------------------------------------------------------
def build_phase1(records):
    p1 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BPB)
    p1.create_matrix(num_voices=1, num_sections=len(SECTIONS))
    p1.add_voice("RawSquare", program=TRUMPET.midi_program, channel=0)
    for name, bars, prog in SECTIONS:
        p1.add_section(name, bars=bars)

    per_section = {name: [] for name, bars, prog in SECTIONS}
    for r in records:
        per_section[BAR_TO_SECTION[r["bar"]]].append(r)

    for name, bars, prog in SECTIONS:
        s_ticks = bars * BAR
        s0 = SECTION_START[name] * BAR
        cell = []
        for r in per_section[name]:
            st = r["tick_abs"] - s0
            if st < 0:
                st = 0
            if st >= s_ticks:
                continue
            en = min(s_ticks, st + r["dur"])
            if en <= st:
                en = st + 30
            cell.append(MusicEvent(pitch=int(round(r["pitch"])), volume=r["vel"],
                                   start_tick=st, end_tick=en))
        cell.sort(key=lambda e: (e.start_tick, e.end_tick))
        if not cell or cell[-1].end_tick < s_ticks:
            last_end = cell[-1].end_tick if cell else 0
            cell.append(MusicEvent(pitch=0, volume=0, start_tick=last_end,
                                   end_tick=s_ticks))
        p1.fill_voice_section("RawSquare", name, MusicUnit(events=cell))
    ok, msg = p1.validate()
    if not ok:
        raise RuntimeError(f"phase1 validate failed: {msg}")
    return p1


# ---------------------------------------------------------------------------
# Phase 2 helpers
# ---------------------------------------------------------------------------
def snap_grid(t, grid=GRID):
    return int(round(t / float(grid)) * grid)


def to_register(pitch, lo, hi):
    p = int(pitch)
    while p < lo:
        p += 12
    while p > hi:
        p -= 12
    return p


def weight_of(onset):
    return classify_weight(onset, STRONG_GRID["4/4"], bar_ticks=BAR)


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
            n_viol = len(vl.check_parallel_motion(prev, cand)) + \
                     len(vl.check_hidden_fifths(prev, cand))
            dist = vl.calculate_voice_leading_distance(prev, cand)
            score = (n_viol, dist)
            if best_score is None or score < best_score:
                best_score, best = score, cand
        if best_score[0] > 0:
            fixed += 1
        corrected.append(sorted(best))
    return corrected, fixed


def _dedup_sort(ev):
    best = {}
    for e in ev:
        key = (e.start_tick, e.pitch)
        if key not in best or (e.end_tick - e.start_tick) > \
                (best[key].end_tick - best[key].start_tick):
            best[key] = e
    return sorted(best.values(), key=lambda e: (e.start_tick, e.pitch))


def build_lead_section(name, records, sq):
    """Latin-square lead: anchor (chord tone, strong) + density from the
    orthogonal duration class. Long cells -> held anchor only; short cells ->
    anchor + chord-tone response (beat 3) + two in-scale passing (beats 2/4)."""
    nbars = SECTION_BARS[name]
    s_ticks = nbars * BAR
    s0 = SECTION_START[name] * BAR
    ev = []
    for r in records:
        if not (s0 <= r["tick_abs"] < s0 + s_ticks):
            continue
        bar = r["bar"]
        d = BAR_DEGREES[bar]
        bs = (bar - SECTION_START[name]) * BAR          # bar start, section-rel
        ct = chord_tones(d, LEAD_LO, LEAD_HI)
        # anchor (strong, beat 1): chord-tone snap of the Latin-square degree
        anchor = sq.tiered_quantize(r["pitch"], weight="strong", chord_tones=ct)
        anchor = max(LEAD_LO, min(LEAD_HI, anchor))
        if r["durclass"] in LONG_CELLS:
            dur = min(DUR_TICKS[r["durclass"]], s_ticks - bs - 20)
            ev.append(MusicEvent(pitch=anchor, volume=r["vel"], start_tick=bs,
                                 end_tick=bs + dur))
            continue
        # short cell -> 4-note figure
        dur = EIGHTH
        ev.append(MusicEvent(pitch=anchor, volume=r["vel"], start_tick=bs,
                             end_tick=bs + dur))
        # beat 2 (weak): in-scale passing (step down)
        p2 = sq.quantize(anchor - 2)
        p2 = max(LEAD_LO, min(LEAD_HI, p2))
        ev.append(MusicEvent(pitch=p2, volume=min(r["vel"] - 8, 92),
                             start_tick=bs + 480, end_tick=bs + 480 + dur))
        # beat 3 (strong): chord-tone response (3rd/5th above the anchor)
        resp = min((c for c in ct if c != anchor),
                   key=lambda c: abs(c - (anchor + 3)))
        ev.append(MusicEvent(pitch=resp, volume=r["vel"] - 4,
                             start_tick=bs + 960, end_tick=bs + 960 + dur))
        # beat 4 (weak): in-scale passing (step up)
        p4 = sq.quantize(anchor + 2)
        p4 = max(LEAD_LO, min(LEAD_HI, p4))
        ev.append(MusicEvent(pitch=p4, volume=min(r["vel"] - 8, 92),
                             start_tick=bs + 1440, end_tick=bs + 1440 + dur))
    return _dedup_sort(ev)


def build_accordion_section(name, corr_triads):
    """Musette accordion comp: sustained voice-led triad per bar (bellows pad)."""
    nbars = SECTION_BARS[name]
    s_ticks = nbars * BAR
    ev = []
    for bi in range(nbars):
        bar = SECTION_START[name] + bi
        r, th, f = corr_triads[bar]
        bs = bi * BAR
        end = min(bs + BAR - 40, s_ticks - 40)
        for p in (r, th, f):
            p = to_register(p, ACCORDION_LO, ACCORDION_HI)
            ev.append(MusicEvent(pitch=p, volume=56, start_tick=bs, end_tick=end))
    return ev


def build_guitar_section(name, corr_triads):
    """Steel-string strum: 8th-note triads, down/up velocity accents."""
    nbars = SECTION_BARS[name]
    s_ticks = nbars * BAR
    ev = []
    for bi in range(nbars):
        bar = SECTION_START[name] + bi
        r, th, f = corr_triads[bar]
        bs = bi * BAR
        for k in range(8):
            off = k * EIGHTH
            rr = to_register(r, GUITAR_LO, GUITAR_HI)
            tt = to_register(th, GUITAR_LO, GUITAR_HI)
            ff = to_register(f, GUITAR_LO, GUITAR_HI)
            if k % 2 == 0:               # downstroke (beat) -> fuller
                vel = 72
                notes = (rr, tt, ff)
            else:                        # upstroke (offbeat) -> lighter dyad
                vel = 58
                notes = (rr, ff)
            for p in notes:
                ev.append(MusicEvent(pitch=p, volume=vel,
                                     start_tick=bs + off,
                                     end_tick=bs + off + EIGHTH - 20))
    ev.sort(key=lambda e: (e.start_tick, e.pitch))
    return ev


def build_bass_section(name, corr_triads):
    """Double bass: root (beat 1) + fifth (beat 3), chanson root-fifth pulse."""
    nbars = SECTION_BARS[name]
    s_ticks = nbars * BAR
    ev = []
    for bi in range(nbars):
        bar = SECTION_START[name] + bi
        r, th, f = corr_triads[bar]
        bs = bi * BAR
        root = to_register(r - 12, BASS_LO, BASS_HI)
        fifth = to_register(f - 12, BASS_LO, BASS_HI)
        ev.append(MusicEvent(pitch=root, volume=82,
                             start_tick=bs, end_tick=bs + BAR - 60))
        ev.append(MusicEvent(pitch=fifth, volume=66,
                             start_tick=bs + 960, end_tick=bs + 960 + 400))
    return ev


def build_drums_section(name):
    """March-like 4/4: kick 1&3, snare 2&4, closed hats on 8ths."""
    nbars = SECTION_BARS[name]
    ev = []
    for bi in range(nbars):
        bs = bi * BAR
        ev.append(MusicEvent(pitch=36, volume=96, start_tick=bs, end_tick=bs + 70))
        ev.append(MusicEvent(pitch=36, volume=86, start_tick=bs + 960,
                             end_tick=bs + 1030))
        ev.append(MusicEvent(pitch=38, volume=84, start_tick=bs + 480,
                             end_tick=bs + 550))
        ev.append(MusicEvent(pitch=38, volume=84, start_tick=bs + 1440,
                             end_tick=bs + 1510))
        for off in range(0, 1920, 240):
            hat = 46 if (off // 240) % 4 == 3 else 42
            ev.append(MusicEvent(pitch=hat, volume=62, start_tick=bs + off,
                                 end_tick=bs + off + 40))
    ev.sort(key=lambda e: (e.start_tick, e.pitch))
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
        out.append(MusicEvent(pitch=0, volume=0, start_tick=last_end,
                              end_tick=sec_ticks))
    return MusicUnit(events=out)


def build_phase2(records, corr_triads, sq):
    comp = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BPB)
    comp.create_matrix(num_voices=len(VOICES), num_sections=len(SECTIONS))
    for name, prog, ch in zip(VOICES, VOICE_PROGRAMS, VOICE_CHANNELS):
        comp.add_voice(name, program=prog, channel=ch)
    for name, bars, prog in SECTIONS:
        comp.add_section(name, bars=bars)

    for name, bars, prog in SECTIONS:
        s_ticks = bars * BAR
        comp.fill_voice_section("Lead", name,
                                seal(build_lead_section(name, records, sq), s_ticks))
        comp.fill_voice_section("Accordion", name,
                                seal(build_accordion_section(name, corr_triads), s_ticks))
        comp.fill_voice_section("Guitar", name,
                                seal(build_guitar_section(name, corr_triads), s_ticks))
        comp.fill_voice_section("Bass", name,
                                seal(build_bass_section(name, corr_triads), s_ticks))
        comp.fill_voice_section("Drums", name,
                                seal(build_drums_section(name), s_ticks))
    ok, msg = comp.validate()
    if not ok:
        raise RuntimeError(f"phase2 validate failed: {msg}")
    return comp


def count_offgrid(events, grid=SIXTEENTH):
    off = sum(1 for e in events if e.pitch > 0 and e.start_tick % grid != 0)
    tot = sum(1 for e in events if e.pitch > 0)
    return off, tot


def main():
    rng = np.random.default_rng(raw_seed)
    records = simulate_latin(rng)
    print("LSAC design: L latin=", _is_latin(L_SQ), " M latin=", _is_latin(M_SQ),
          " orthogonal=", _orthogonal(L_SQ, M_SQ))
    print("transversal (diagonal):", TRANSVERSAL)
    print("LATIN raw notes =", len(records))
    long_n = sum(1 for r in records if r["durclass"] in LONG_CELLS)
    print(f"  long cells (held): {long_n} / short cells (run): {len(records) - long_n}")
    # confirm the complete factorial design over the first 40 cells is distinct
    pairs = [(r["degree"], r["durclass"]) for r in records]
    print("  distinct (degree,durclass) pairs:", len(set(pairs)), "of", len(pairs))

    # ---- Phase 1 raw draft -------------------------------------------------
    phase1 = build_phase1(records)
    phase1_mid = os.path.join(MIDI_DIR, PROJECT + "-phase1.mid")
    phase1.to_midi(phase1_mid)
    write_provenance(
        phase1_mid, AI_ASSISTED,
        "musicom.latin_square_phase1",
        parameters={"bpm": BPM, "bars": TOTAL_BARS, "seed": raw_seed,
                    "phase": 1, "quantized": False, "key": KEY_NAME,
                    "form": "verse-chorus", "style": STYLE,
                    "method": "ABS-139 Latin Square & Orthogonal-Array (LSAC)",
                    "layer": "abstract", "paradigm": "Rules-Based",
                    "order": N,
                    "latin_square": L_SQ, "orthogonal_mate": M_SQ,
                    "transversal": TRANSVERSAL,
                    "notes": len(records),
                    "rules_applied": "NONE (pre-rules)"},
        notes="Raw Latin-square anchor stream: single trumpet voice, jittered "
              "pitch (scale-degree note + jitter) + off-grid onsets + "
              "orthogonal duration class, 40 bars, pre-rules. ABS-139 abstract.")
    write_grid_visualization(phase1.matrix,
                             os.path.join(ANALYSIS_DIR,
                                          "grid_visualization_phase1.txt"),
                             voice_names=["RawSquare"], bpm=BPM)
    print("PHASE1_OK", "raw_notes=", len(records))

    # ---- Phase 2 rules + texture -------------------------------------------
    bar_triads = [triad(d, base=TONIC_BASE) for d in BAR_DEGREES]
    vl = VoiceLeadingRules(style="classical")
    opt_triads = vl.optimize_voice_leading(bar_triads)
    corr_triads, fixed = correct_voice_leading(opt_triads)
    print(f"[voicing] corrected {fixed} chord(s)")

    sq = ScaleQuantizer(root=TONIC_BASE, scale="major")
    phase2 = build_phase2(records, corr_triads, sq)

    # grid audit on perfect layer (pre-humanization)
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
    print(f"[grid] perfect-layer off-grid (16th): {off}/{tot}")
    assert off == 0, f"perfect layer has {off} off-grid onsets"

    # ---- dual-version export -----------------------------------------------
    hz_instruments = {
        "Lead": TRUMPET.humanize_dna,
        "Accordion": ACCORDION.humanize_dna,
        "Guitar": STEEL_ACOUSTIC.humanize_dna,
        "Bass": DOUBLE_BASS.humanize_dna,
        "Drums": DRUM_KIT.humanize_dna,
    }
    perfect_path = os.path.join(MIDI_DIR, PROJECT + "-perfect.mid")
    humanized_path = os.path.join(MIDI_DIR, PROJECT + "-humanized.mid")
    hz = export_dual(phase2, perfect_path, humanized_path,
                     style=STYLE, seed=hz_seed, bpm=BPM, instruments=hz_instruments)

    # ---- provenance sidecars ----------------------------------------------
    prov = {
        "bpm": BPM, "key": "G", "mode": "major", "style": STYLE,
        "form": "verse-chorus", "bars": TOTAL_BARS,
        "sections": [s[0] for s in SECTIONS],
        "section_bars": {s[0]: s[1] for s in SECTIONS},
        "bar_degrees": BAR_DEGREES,
        "degree_names": {str(k): v for k, v in DEGREE_NAMES.items()},
        "method": "ABS-139 Latin Square & Orthogonal-Array (LSAC)",
        "layer": "abstract", "paradigm": "Rules-Based",
        "order": N, "latin_square": L_SQ, "orthogonal_mate": M_SQ,
        "transversal": TRANSVERSAL,
        "long_cells": list(LONG_CELLS),
        "voices": [[v, p, ch] for v, p, ch in
                   zip(VOICES, VOICE_PROGRAMS, VOICE_CHANNELS)],
        "voice_leading_corrections": fixed,
        "humanize_seed": hz_seed, "raw_seed": raw_seed,
        "humanize_profiles": {k: v["profile"] for k, v in hz.items()},
    }
    write_provenance(
        perfect_path, AI_ASSISTED,
        "musicom two-phase (phase=2 rules: tiered chord-tone quantization + "
        "8th grid snap + dedup + voice-leading + 5-voice Chanson texture) "
        "(ABS-139 Latin Square & Orthogonal-Array)",
        sources=[phase1_mid],
        parameters=dict(prov, phase=2, version="perfect", off_grid=0),
        notes="Grid-locked perfect layer (verse-chorus, 40 bars). "
              "ABS-139 Latin Square (abstract).")
    write_provenance(
        humanized_path, AI_ASSISTED,
        "musicom two-phase (phase=2 + humanization) (ABS-139 LSAC)",
        sources=[perfect_path],
        parameters=dict(prov, phase=2, version="humanized",
                        humanize_seed=hz_seed,
                        humanize_stats={k: {kk: (float(vv) if isinstance(vv, float) else vv)
                                            for kk, vv in v.items() if kk != "profile"}
                                        for k, v in hz.items()}),
        notes="Humanized layer (style chanson + per-instrument DNA).")

    # ---- grid visualization ------------------------------------------------
    write_grid_visualization(phase2.matrix,
                             os.path.join(ANALYSIS_DIR, "grid_visualization.txt"),
                             voice_names=VOICES, bpm=BPM)

    # ---- size asserts ------------------------------------------------------
    for p in (phase1_mid, perfect_path, humanized_path):
        assert os.path.getsize(p) > 40, f"empty/corrupt: {p}"

    summary = {
        "style": STYLE, "genre": GENRE,
        "method": "ABS-139 Latin Square & Orthogonal-Array (LSAC)",
        "layer": "abstract", "paradigm": "Rules-Based",
        "form": "verse-chorus", "key": KEY_NAME, "bpm": BPM,
        "bars": TOTAL_BARS, "sections": [s[0] for s in SECTIONS],
        "section_bars": [s[1] for s in SECTIONS],
        "order": N, "latin_square": L_SQ, "orthogonal_mate": M_SQ,
        "transversal": TRANSVERSAL,
        "raw_notes": len(records),
        "long_cells": long_n,
        "distinct_pairs": len(set(pairs)),
        "voice_leading_corrections": fixed,
        "phase1_path": phase1_mid, "perfect_path": perfect_path,
        "humanized_path": humanized_path,
        "hz_seed": hz_seed,
        "hz": {k: {kk: vv for kk, vv in v.items() if kk != "profile"}
               for k, v in hz.items()},
        "progression": {s[0]: [DEGREE_NAMES[d] for d in s[2]] for s in SECTIONS},
    }
    with open(os.path.join(ANALYSIS_DIR, "compose_summary.json"), "w") as f:
        json.dump(summary, f, indent=2, default=str)
    print("COMPOSE_OK")
    print(json.dumps(summary, indent=2, default=str))


if __name__ == "__main__":
    main()
