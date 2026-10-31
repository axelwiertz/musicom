# -*- coding: utf-8 -*-
"""276-african-contour-suite - extension of 105-african-contour (African /
Method 095 Contour Theory Composition, abstract layer).

Source audit (2026-10-31): ALL 6 standards PASS -> EXTENSION (identity kept,
existing material used as DNA seed). No redesign required.

Identity preserved (from source 105-african-contour):
  genre African, Method 095 CTC (abstract layer),
  key C major pentatonic {0,2,4,7,9}, 112 BPM 4/4 (bar 1920, 16th 120, 8th 240),
  contour vocabulary (CSeg rank seqs + CAS), dihedral transforms {id,I,R,RI},
  5 core voices (Kalimba 108, Flute 73, Marimba 12, DoubleBass 43, Drums ch9)
  + a NEW Counter voice (Pan Flute 75) in Bridge/Climax only.

New form (LONGER + more varied): 32 bars / 8 sections (source was 24 bars /
6 sections). Per-section harmonic regions + per-section variation technique.

Variation techniques (7 distinct):
  1. Retrograde (R)            -> Variation (valley contour reversed)
  2. Inversion (I)             -> Development (chaos contour inverted)
  3. Register shift (+12)      -> Development + Climax (base 60 -> 72)
  4. Rhythmic augmentation     -> Bridge + Coda (quarter-note grid, motif slowed)
  5. Rhythmic diminution       -> Climax (8th-note grid = double-time density)
  6. Counterline (Pan Flute)   -> Bridge + Climax (new 6th voice)
  7. Density rise + thinning   -> Climax (all 6 voices) vs Coda (3 voices)
"""

import os
import sys
import json
import hashlib

import numpy as np

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer
from workflows.humanize import export_dual
from workflows.provenance import write_provenance, AI_ASSISTED
from visualization.grid import write_grid_visualization

# ------------------------------------------------------------------ paths
PROJ = "/opt/data/projects/Styles/African/276-african-contour-suite"
MIDI_DIR = os.path.join(PROJ, "MIDI")
AUDIO_DIR = os.path.join(PROJ, "Audio")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")
for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
    os.makedirs(d, exist_ok=True)

PID = "276"
NAME = "african-contour-suite"
BASE = f"{PID}-{NAME}"
STYLE = "african"
GENRE = "African"
SOURCE = "/opt/data/projects/Styles/African/105-african-contour"
SOURCE_MIDI = SOURCE + "/MIDI/105-african-contour.mid"

# ------------------------------------------------------------------ identity
BPM = 112
TPB = 480
BEATS = 4
BAR = TPB * BEATS                 # 1920
SIXTEENTH = 120
EIGHTH = 240
QUARTER = 480

KEY_NAME = "C major pentatonic"
KEY_ROOT_PC = 0
KEY_PCS = {0, 2, 4, 7, 9}         # C D E G A
PENT = [0, 2, 4, 7, 9]            # rank 0..4 -> semitone offset above C

# 4-note palettes (subsets of the pentatonic, each drops ONE scale tone).
PALETTES = {
    "C":  {0, 4, 7, 9},           # C E G A   (drop D)
    "D":  {2, 4, 7, 9},           # D E G A   (drop C)
    "Am": {9, 0, 2, 4},           # A C D E   (drop G)
    "G":  {7, 9, 0, 2},           # G A C D   (drop E)
}
PALETTE_ROOT = {"C": 0, "D": 2, "Am": 9, "G": 7}

# ------------------------------------------------------------------ contour
class CSeg:
    """Contour Segment: normalized rank sequence (0 = lowest, n-1 = highest)."""

    def __init__(self, ranks):
        self.ranks = list(ranks)
        self.n = len(self.ranks)
        assert sorted(self.ranks) == list(range(self.n)), self.ranks

    def cas(self):
        out = []
        for a, b in zip(self.ranks, self.ranks[1:]):
            out.append("+" if b > a else ("-" if b < a else "0"))
        return out

    def invert(self):
        return CSeg([self.n - 1 - r for r in self.ranks])

    def retrograde(self):
        return CSeg(list(reversed(self.ranks)))

    def retrograde_invert(self):
        return self.retrograde().invert()

    def transform(self, t):
        return {"I": self.invert, "R": self.retrograde,
                "RI": self.retrograde_invert, "id": lambda: self}[t]()


VOCAB4 = {
    "arch":      CSeg([0, 2, 3, 1]),   # + + -
    "valley":    CSeg([2, 1, 0, 3]),   # - - +
    "oscillate": CSeg([0, 3, 1, 2]),   # + - +
    "rising":    CSeg([0, 1, 2, 3]),   # + + +
    "falling":   CSeg([3, 2, 1, 0]),   # - - -
    "chaos":     CSeg([1, 3, 0, 2]),   # + - +
}

TRANSFORMS = ["id", "I", "R", "RI"]

# ------------------------------------------------------------------ form
# (name, template, section_transform, register_base, density, rhythm_mode)
SECTIONS = [
    ("Intro",       "oscillate", "id", 60, 1, "sync"),
    ("Theme",       "arch",      "id", 60, 2, "sync"),
    ("Variation",   "valley",    "R",  60, 2, "sync"),
    ("Development", "chaos",     "I",  72, 2, "sync"),
    ("Bridge",      "arch",      "id", 48, 1, "aug"),
    ("Climax",      "rising",    "RI", 72, 3, "dense"),
    ("Outro",       "falling",   "id", 48, 2, "sync"),
    ("Coda",        "oscillate", "R",  48, 1, "aug"),
]
BARS_PER_SECTION = 4
N_SECTIONS = len(SECTIONS)
TOTAL_BARS = N_SECTIONS * BARS_PER_SECTION          # 32
TOTAL_TICKS = TOTAL_BARS * BAR                       # 61440

SECTION_PALETTES = {
    0: ["C", "G", "C", "C"],
    1: ["C", "Am", "C", "G"],
    2: ["Am", "G", "D", "G"],
    3: ["D", "G", "Am", "D"],
    4: ["Am", "D", "G", "Am"],
    5: ["G", "C", "D", "C"],
    6: ["C", "G", "Am", "C"],
    7: ["C", "G", "C", "C"],
}
SECTION_MIDPOINT = {s[0]: SECTION_PALETTES[i][1] for i, s in enumerate(SECTIONS)}

ACTIVE = {
    "Intro":       ["Kalimba", "Bass", "Drums"],
    "Theme":       ["Kalimba", "Flute", "Marimba", "Bass", "Drums"],
    "Variation":   ["Kalimba", "Flute", "Marimba", "Bass", "Drums"],
    "Development": ["Kalimba", "Flute", "Marimba", "Bass", "Drums"],
    "Bridge":      ["Kalimba", "Bass", "Counter", "Drums"],
    "Climax":      ["Kalimba", "Flute", "Marimba", "Bass", "Counter", "Drums"],
    "Outro":       ["Kalimba", "Flute", "Bass", "Drums"],
    "Coda":        ["Kalimba", "Bass", "Drums"],
}

SECTION_START = {}
_acc = 0
for name, _t, _tf, _base, _dens, _mode in SECTIONS:
    SECTION_START[name] = _acc
    _acc += BARS_PER_SECTION
assert _acc == TOTAL_BARS

BAR_PALETTE = []                                    # global bar -> palette name
for s_idx, (name, _t, _tf, _base, _dens, _mode) in enumerate(SECTIONS):
    BAR_PALETTE.extend(SECTION_PALETTES[s_idx])
assert len(BAR_PALETTE) == TOTAL_BARS


def bar_of(tick):
    return min(TOTAL_BARS - 1, tick // BAR)


def palette_pcs(bar_idx):
    return PALETTES[BAR_PALETTE[bar_idx]]


def nearest_in_pcs(pitch, pcs, lo=0, hi=127):
    """Nearest note within [lo, hi] whose pitch-class is in pcs. Range-restricted
    so the result never needs a post-clamp (a post-clamp would change the
    pitch-class, breaking chord/scale compliance)."""
    best = None
    for n in range(max(lo, pitch - 12), min(hi, pitch + 12) + 1):
        if n % 12 in pcs:
            if best is None or abs(n - pitch) < abs(best - pitch):
                best = n
    return best


def quantize_to_chord(pitch, chord_pcs, lo, hi):
    return nearest_in_pcs(pitch, chord_pcs, lo, hi)


# ------------------------------------------------------------------ rhythm
FULL_GRID = [0, 4, 10, 14]                          # syncopated 16th, 4 onsets
HALF_GRIDS = ([0, 3, 5, 7], [8, 11, 13, 15])        # two half-bar 4-onset grids
AUG_GRID = [0, 4, 8, 12]                            # quarter notes (augmentation)
DENSE_GRID = [0, 2, 4, 6, 8, 10, 12, 14]            # 8th notes (diminution)
BELL = [0, 3, 6, 8, 11, 14]                         # African 3-3-2 bell (16th units)


def section_motifs(s_idx, bar_in_sec):
    """List of (CSeg, transform) motifs for one bar."""
    name, template, tf, base, density, mode = SECTIONS[s_idx]
    seed = VOCAB4[template].transform(tf)
    if density == 1 or mode in ("aug", "dense"):
        return [(seed, tf)]
    return [(seed, tf), (seed.invert(), "I")]


def motif_onsets(mode, motif_idx, n_motifs):
    if mode == "aug":
        return AUG_GRID
    if mode == "dense":
        return DENSE_GRID
    if n_motifs == 1:
        return FULL_GRID
    return HALF_GRIDS[motif_idx]


def motif_dur(mode):
    return {"aug": 700, "dense": 220, "sync": 200}[mode]


# ------------------------------------------------------------------ phase 1
def generate_phase1_raw():
    """Single Kalimba voice: whole-tone contour (rank -> base + 2*rank), off-grid
    fractional timing, no scale/chord snapping. Pre-rules raw draft."""
    comp = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
    comp.create_matrix(num_voices=1, num_sections=N_SECTIONS)
    comp.add_voice("RawKalimba", program=108, channel=0)
    rng1 = np.random.default_rng(20261031)

    for s_idx, (name, template, tf, base, density, mode) in enumerate(SECTIONS):
        comp.add_section(name, bars=BARS_PER_SECTION)
        events = []
        for bar_in_sec in range(BARS_PER_SECTION):
            bar_start = bar_in_sec * BAR
            motifs = section_motifs(s_idx, bar_in_sec)
            for m_idx, (cseg, tfn) in enumerate(motifs):
                onsets = motif_onsets(mode, m_idx, len(motifs))
                for i, pos in enumerate(onsets):
                    r = cseg.ranks[i % cseg.n]
                    raw_pitch = base + 2 * r
                    jitter = int(rng1.integers(-30, 31))
                    t_onset = bar_start + pos * SIXTEENTH + jitter
                    t_onset = max(1, min(t_onset, BARS_PER_SECTION * BAR - 2))
                    dur = int(rng1.integers(150, 260))
                    end_t = min(t_onset + dur, BARS_PER_SECTION * BAR - 1)
                    events.append(MusicEvent(
                        pitch=raw_pitch, volume=int(70 + 6 * r),
                        start_tick=t_onset, end_tick=end_t))
        events.sort(key=lambda e: (e.start_tick, e.end_tick))
        events.append(MusicEvent(pitch=0, volume=0,
                                 start_tick=BARS_PER_SECTION * BAR - 1,
                                 end_tick=BARS_PER_SECTION * BAR))
        comp.fill_voice_section("RawKalimba", name, MusicUnit(events=events))

    ok, msg = comp.validate()
    if not ok:
        raise RuntimeError(f"phase1 validate failed: {msg}")
    return comp


# ------------------------------------------------------------------ phase 2
def rel_events(abs_events, s_start, s_len):
    out = []
    for e in abs_events:
        s = e.start_tick - s_start
        en = e.end_tick - s_start
        if en <= 0 or s >= s_len:
            continue
        s = max(0, s)
        en = min(s_len, en)
        if en <= s:
            en = min(s_len, s + SIXTEENTH)
        out.append(MusicEvent(pitch=e.pitch, volume=e.volume,
                              start_tick=s, end_tick=en))
    out.sort(key=lambda e: (e.start_tick, e.end_tick, e.pitch))
    out.append(MusicEvent(pitch=0, volume=0,
                          start_tick=max(0, s_len - 10), end_tick=s_len))
    return out


def snap(t):
    return int(round(t / float(SIXTEENTH)) * SIXTEENTH)


def process_lead(raw_events):
    """Grid snap -> scale quantize -> per-bar palette quantize -> range enforce
    -> dedup -> voice-leading. Grid-locked perfect layer (off-grid == 0)."""
    LO, HI = 52, 88
    events = []
    for e in raw_events:
        st = snap(e.start_tick)
        st = max(0, min(TOTAL_TICKS - SIXTEENTH, st))
        bar = bar_of(st)
        pcs = palette_pcs(bar)
        sc = nearest_in_pcs(e.pitch, KEY_PCS, LO, HI)
        ct = quantize_to_chord(sc, pcs, LO, HI)
        events.append(MusicEvent(pitch=ct, volume=e.volume,
                                 start_tick=st, end_tick=st + EIGHTH))
    # dedup collided (start_tick, pitch) keep longest
    best = {}
    for e in events:
        k = (e.start_tick, e.pitch)
        if k not in best or e.end_tick > best[k].end_tick:
            best[k] = e
    events = sorted(best.values(), key=lambda e: (e.start_tick, e.pitch))
    # voice-leading: cap adjacent leap <= 9 semitones (range-restricted)
    fixed = []
    for e in events:
        if fixed:
            prev = fixed[-1]
            if abs(e.pitch - prev.pitch) > 9:
                pcs = palette_pcs(bar_of(e.start_tick))
                cand = nearest_in_pcs((prev.pitch + e.pitch) // 2, pcs, LO, HI)
                if cand is not None:
                    e.pitch = cand
        fixed.append(e)
    return fixed


def build_flute():
    """Call/response: inverted contour answer on beats 3-4, upper register.
    Active in Theme/Variation/Development/Climax/Outro."""
    evs = []
    for s_idx, (name, template, tf, base, density, mode) in enumerate(SECTIONS):
        if name not in ("Theme", "Variation", "Development", "Climax", "Outro"):
            continue
        for bar_in_sec in range(BARS_PER_SECTION):
            bar_global = s_idx * BARS_PER_SECTION + bar_in_sec
            bar_start = bar_global * BAR
            pcs = palette_pcs(bar_global)
            seed = VOCAB4[template].transform(tf)
            inv = seed.invert()
            sr = sorted(inv.ranks)
            order = [sr[-1], sr[len(sr) // 2], sr[0]]   # hi -> mid -> lo
            base_hi = max(72, min(84, base + 24))
            for i, r in enumerate(order):
                t_onset = bar_start + [8, 11, 14][i] * SIXTEENTH
                p = quantize_to_chord(base_hi + PENT[r], pcs, 72, 96)
                evs.append(MusicEvent(pitch=p, volume=82 - i * 6,
                                      start_tick=t_onset, end_tick=t_onset + 360))
    return evs


def build_marimba():
    """African 3-3-2 bell interlock ostinato. Active in Theme/Variation/
    Development/Climax."""
    evs = []
    for s_idx, (name, template, tf, base, density, mode) in enumerate(SECTIONS):
        if name not in ("Theme", "Variation", "Development", "Climax"):
            continue
        for bar_in_sec in range(BARS_PER_SECTION):
            bar_global = s_idx * BARS_PER_SECTION + bar_in_sec
            bar_start = bar_global * BAR
            pcs = palette_pcs(bar_global)
            low = quantize_to_chord(base, pcs, 55, 76)
            high = quantize_to_chord(base + 12, pcs, 55, 88)
            for i, pos in enumerate(BELL):
                t_onset = bar_start + pos * SIXTEENTH
                p = low if i % 2 == 0 else high
                evs.append(MusicEvent(pitch=p, volume=90 if i % 2 == 0 else 74,
                                      start_tick=t_onset, end_tick=t_onset + 140))
    return evs


def build_bass():
    """Double bass foundation: root + fifth per bar's palette root. Every bar."""
    evs = []
    for bar in range(TOTAL_BARS):
        pname = BAR_PALETTE[bar]
        root_pc = PALETTE_ROOT[pname]
        root = min(range(33, 53), key=lambda c: (0 if c % 12 == root_pc else 1,
                                                 abs(c - 40)))
        fifth = root + 7
        t0 = bar * BAR
        evs.append(MusicEvent(pitch=root, volume=96, start_tick=t0,
                              end_tick=t0 + 900))
        evs.append(MusicEvent(pitch=fifth, volume=84, start_tick=t0 + 960,
                              end_tick=t0 + 960 + 900))
    return evs


def build_counter():
    """Pan Flute counterline (new 6th voice), Bridge + Climax only. Descends in
    stepwise pentatonic pairs against the lead."""
    evs = []
    for s_idx, (name, template, tf, base, density, mode) in enumerate(SECTIONS):
        if name not in ("Bridge", "Climax"):
            continue
        for bar_in_sec in range(BARS_PER_SECTION):
            bar_global = s_idx * BARS_PER_SECTION + bar_in_sec
            bar_start = bar_global * BAR
            pcs = palette_pcs(bar_global)
            seed = VOCAB4[template].transform(tf)
            hi = max(74, min(88, base + 20))
            line = [hi, hi + 2, hi, hi - 2]          # stepwise call
            for i, p in enumerate(line):
                p = quantize_to_chord(p, pcs, 72, 96)
                t_onset = bar_start + [2, 6, 10, 14][i] * SIXTEENTH
                evs.append(MusicEvent(pitch=p, volume=74,
                                      start_tick=t_onset,
                                      end_tick=t_onset + 3 * SIXTEENTH))
    return evs


def build_drums():
    """Djembe kit: cowbell bell + kick + snare(slap) + shaker. Density follows
    section (full / sparse / bridge)."""
    KICK, SNARE, SHAKER, COWBELL, CRASH, OPENHH = 36, 38, 70, 56, 49, 46
    evs = []
    for s_idx, (name, template, tf, base, density, mode) in enumerate(SECTIONS):
        for bar_in_sec in range(BARS_PER_SECTION):
            bar_global = s_idx * BARS_PER_SECTION + bar_in_sec
            t0 = bar_global * BAR
            # shaker: 8ths (all sections)
            for k in range(0, BAR, EIGHTH):
                evs.append(MusicEvent(pitch=SHAKER, volume=56,
                                      start_tick=t0 + k, end_tick=t0 + k + 40))
            # kick on beats 1 and 3 (positions 0 and 8 sixteenths)
            for pos in (0, 8):
                evs.append(MusicEvent(pitch=KICK, volume=100,
                                      start_tick=t0 + pos * SIXTEENTH,
                                      end_tick=t0 + pos * SIXTEENTH + 120))
            if name in ("Theme", "Variation", "Development", "Climax", "Outro"):
                # snare slap on beats 2 and 4
                for pos in (4, 12):
                    evs.append(MusicEvent(pitch=SNARE, volume=78,
                                          start_tick=t0 + pos * SIXTEENTH,
                                          end_tick=t0 + pos * SIXTEENTH + 120))
            if name in ("Theme", "Variation", "Development", "Climax"):
                # cowbell bell (African 3-3-2)
                for pos in BELL:
                    evs.append(MusicEvent(pitch=COWBELL, volume=88,
                                          start_tick=t0 + pos * SIXTEENTH,
                                          end_tick=t0 + pos * SIXTEENTH + 60))
            if name == "Climax":
                evs.append(MusicEvent(pitch=CRASH, volume=90,
                                      start_tick=t0, end_tick=t0 + 240))
                evs.append(MusicEvent(pitch=OPENHH, volume=70,
                                      start_tick=t0 + 14 * SIXTEENTH,
                                      end_tick=t0 + 15 * SIXTEENTH))
            elif name in ("Intro", "Coda"):
                # sparse: single snare on beat 2
                evs.append(MusicEvent(pitch=SNARE, volume=72,
                                      start_tick=t0 + 4 * SIXTEENTH,
                                      end_tick=t0 + 4 * SIXTEENTH + 100))
    return evs


VOICES = [
    ("Kalimba", 108, 0),
    ("Flute", 73, 1),
    ("Marimba", 12, 2),
    ("Bass", 43, 3),
    ("Counter", 75, 4),
    ("Drums", 0, 9),
]


def build_phase2(lead_ev, flute_ev, marimba_ev, bass_ev, counter_ev, drums_ev):
    comp = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
    comp.create_matrix(num_voices=len(VOICES), num_sections=N_SECTIONS)
    for vname, prog, ch in VOICES:
        comp.add_voice(vname, program=prog, channel=ch)
    for name, _t, _tf, _base, _dens, _mode in SECTIONS:
        comp.add_section(name, bars=BARS_PER_SECTION)
    vmap = {"Kalimba": lead_ev, "Flute": flute_ev, "Marimba": marimba_ev,
            "Bass": bass_ev, "Counter": counter_ev, "Drums": drums_ev}
    for s_idx, (name, _t, _tf, _base, _dens, _mode) in enumerate(SECTIONS):
        s_off = SECTION_START[name] * BAR
        sec_ticks = BARS_PER_SECTION * BAR
        for vname, all_ev in vmap.items():
            seg = [e for e in all_ev if s_off <= e.start_tick < s_off + sec_ticks]
            comp.fill_voice_section(vname, name, MusicUnit(events=rel_events(seg, s_off, sec_ticks)))
    ok, msg = comp.validate()
    if not ok:
        raise RuntimeError(f"phase2 validate failed: {msg}")
    return comp


# ------------------------------------------------------------------ raw events
def raw_events_all():
    """Raw whole-tone contour walk (single voice), absolute ticks, off-grid."""
    rng = np.random.default_rng(20261032)
    out = []
    for s_idx, (name, template, tf, base, density, mode) in enumerate(SECTIONS):
        s_off = SECTION_START[name] * BAR
        for bar_in_sec in range(BARS_PER_SECTION):
            bar_start = bar_in_sec * BAR
            motifs = section_motifs(s_idx, bar_in_sec)
            for m_idx, (cseg, tfn) in enumerate(motifs):
                onsets = motif_onsets(mode, m_idx, len(motifs))
                for i, pos in enumerate(onsets):
                    r = cseg.ranks[i % cseg.n]
                    raw_pitch = base + 2 * r
                    jitter = int(rng.integers(-30, 31))
                    t_onset = s_off + bar_start + pos * SIXTEENTH + jitter
                    t_onset = max(1, min(t_onset, TOTAL_TICKS - 2))
                    out.append(MusicEvent(pitch=raw_pitch, volume=int(70 + 6 * r),
                                          start_tick=t_onset, end_tick=t_onset + 200))
    out.sort(key=lambda e: (e.start_tick, e.end_tick))
    return out


def main():
    # ---- phase 1 ----
    phase1 = generate_phase1_raw()
    phase1_mid = os.path.join(MIDI_DIR, BASE + "-phase1.mid")
    phase1.to_midi(phase1_mid)
    write_provenance(
        phase1_mid, AI_ASSISTED,
        "musicom two-phase rework (phase=1 raw whole-tone contour, Method 095 CTC)",
        sources=[SOURCE_MIDI],
        parameters={"bpm": BPM, "key": KEY_NAME, "phase": 1, "quantized": False,
                    "bars": TOTAL_BARS, "style": STYLE, "genre": GENRE,
                    "seed": 20261031, "realization": "whole-tone (rank -> base + 2*rank)",
                    "timing": "off-grid (16th +-30 tick jitter)"},
        notes="Raw contour walk, single Kalimba voice, off-grid, pre-rules.")
    write_grid_visualization(phase1.matrix,
                             os.path.join(ANALYSIS_DIR, "grid_visualization_phase1.txt"),
                             ticks_per_character=120, voice_names=["RawKalimba"], bpm=BPM)

    # ---- phase 2 rules ----
    raw = raw_events_all()
    lead_ev = process_lead(raw)
    flute_ev = build_flute()
    marimba_ev = build_marimba()
    bass_ev = build_bass()
    counter_ev = build_counter()
    drums_ev = build_drums()
    phase2 = build_phase2(lead_ev, flute_ev, marimba_ev, bass_ev, counter_ev, drums_ev)

    # ---- dual-version export (perfect + humanized) ----
    sys.path.insert(0, "/opt/data/repos/musicom/projects/Instruments")
    from instrument_registry import by_name
    inst_map = {"Kalimba": "kalimba", "Flute": "flute", "Marimba": "marimba",
                "Bass": "double_bass", "Counter": "pan_flute"}
    hz_instruments = {v: by_name(inst_map[v]).humanize_dna for v in inst_map}
    hz_instruments["Drums"] = (2.0, 4.0, 0.0, 0.008)

    hz_seed = int(hashlib.md5(BASE.encode()).hexdigest()[:8], 16) % 100000
    perfect_path = os.path.join(MIDI_DIR, BASE + "-perfect.mid")
    humanized_path = os.path.join(MIDI_DIR, BASE + "-humanized.mid")
    hz = export_dual(phase2, perfect_path, humanized_path,
                     style=STYLE, seed=hz_seed, bpm=BPM,
                     instruments=hz_instruments)

    # ---- provenance sidecars ----
    provenance_params = {
        "bpm": BPM, "key": KEY_NAME, "key_pcs": sorted(KEY_PCS),
        "style": STYLE, "genre": GENRE,
        "form": "32 bars / 8 sections", "bars": TOTAL_BARS,
        "sections": [{"name": s[0], "bars": BARS_PER_SECTION,
                      "palette": SECTION_PALETTES[i],
                      "midpoint_chord": SECTION_MIDPOINT[s[0]],
                      "template": s[1], "transform": s[2],
                      "register_base": s[3], "density": s[4], "mode": s[5]}
                     for i, s in enumerate(SECTIONS)],
        "method": "095 Contour Theory Composition (CTC)",
        "extension_source": "105-african-contour",
        "audit_result": "all pass (extension)",
        "seed": 20261031, "humanize_seed": hz_seed,
        "voices": [[v[0], v[1], v[2]] for v in VOICES],
        "humanize_profiles": {k: v.get("profile") for k, v in hz.items()},
        "variation_techniques": [
            "retrograde (Variation)", "inversion (Development)",
            "register shift +12 (Development/Climax)",
            "rhythmic augmentation (Bridge/Coda)",
            "rhythmic diminution (Climax)",
            "counterline Pan Flute (Bridge/Climax)",
            "density rise + thinning (Climax/Coda)"],
    }
    write_provenance(
        perfect_path, AI_ASSISTED,
        "musicom two-phase rework (phase=2 rules: grid snap + scale/palette "
        "quantize + voice-leading + range) (Method 095 CTC)",
        sources=[phase1_mid, SOURCE_MIDI],
        parameters=dict(provenance_params, phase=2, version="perfect", off_grid=0),
        notes="Grid-locked perfect layer (32 bars / 8 sections).")
    write_provenance(
        humanized_path, AI_ASSISTED,
        "musicom two-phase rework (phase=2 + humanization) (Method 095 CTC)",
        sources=[perfect_path],
        parameters=dict(provenance_params, phase=2, version="humanized",
                        humanize_seed=hz_seed,
                        humanize_stats={k: {kk: (float(vv) if isinstance(vv, float) else vv)
                                            for kk, vv in v.items() if kk != "profile"}
                                        for k, v in hz.items()}),
        notes="Humanized layer (style african + per-instrument DNA).")

    # ---- grid visualization ----
    write_grid_visualization(phase2.matrix,
                             os.path.join(ANALYSIS_DIR, "grid_visualization.txt"),
                             ticks_per_character=120,
                             voice_names=[v[0] for v in VOICES], bpm=BPM)

    # ---- size asserts ----
    for p in (phase1_mid, perfect_path, humanized_path):
        assert os.path.getsize(p) > 40, f"empty/corrupt: {p}"

    # ---- summary ----
    summary = {
        "project": BASE, "pid": PID, "genre": GENRE, "style": STYLE,
        "key": KEY_NAME, "key_pcs": sorted(KEY_PCS), "bpm": BPM,
        "bars": TOTAL_BARS, "total_ticks": TOTAL_TICKS,
        "sections": [{"name": s[0], "template": s[1], "transform": s[2],
                      "register_base": s[3], "density": s[4], "mode": s[5],
                      "midpoint_chord": SECTION_MIDPOINT[s[0]]}
                     for s in SECTIONS],
        "phase1_path": phase1_mid, "perfect_path": perfect_path,
        "humanized_path": humanized_path, "hz_seed": hz_seed,
        "hz": {k: {kk: vv for kk, vv in v.items() if kk != "profile"}
               for k, v in hz.items()},
        "event_counts": {"lead": len(lead_ev), "flute": len(flute_ev),
                         "marimba": len(marimba_ev), "bass": len(bass_ev),
                         "counter": len(counter_ev), "drums": len(drums_ev)},
    }
    with open(os.path.join(PROJ, "composition_meta.json"), "w") as f:
        json.dump(summary, f, indent=2, default=str)
    print("COMPOSE_OK")
    print(json.dumps(summary, indent=2, default=str))
    return summary


if __name__ == "__main__":
    main()
