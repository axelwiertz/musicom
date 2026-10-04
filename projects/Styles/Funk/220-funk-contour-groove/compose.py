# -*- coding: utf-8 -*-
"""220-funk-contour-groove - Funk style / ABSTRACT layer: Method 095 Contour
Theory Composition (CTC).

Autonomous nightly composition job (date: 2026-10-03, job 1fc3fd65d359).

Contour Theory (Friedmann 1985; Marvin & Laprade 1987; Morris 1993) treats the
SHAPE of a melodic line as the primary compositional parameter, independent of
exact pitch-class content. The abstract layer designs pure contour prototypes
(CSeg = Contour Segment, a normalized rank sequence; CAS = Contour Adjacency
Series, the up/down/same direction string) and transforms them via the dihedral
group {I, R, RI}. The concrete layer maps ranks -> scale degrees -> pitches.

Two-phase architecture:
  Phase 1 (raw abstract draft): single Trumpet voice. Contour ranks realized as
    a raw whole-tone pitch stream (rank r -> base + 2*r), placed on FRACTIONAL
    off-grid ticks. No scale/chord snapping. Exported as -phase1.mid.
  Phase 2 (musicom rules): 16th-grid lock -> E-minor-pentatonic snap -> per-bar
    palette (chord-tone) quantize -> full 5-voice funk texture (trumpet lead,
    tenor-sax horn stabs, clavinet comp, contrabass funk bass, drum kit).
    Exported as .mid.

Key: E minor pentatonic (E G A B D) = pc {4,7,9,11,2}.
Form: Intro | Theme | Variation | Development | Climax | Outro (6 x 4 = 24 bars).
BPM 100, 4/4, 480 TPB (BAR = 1920, 16th = 120, 8th = 240).

Engine only: structures + workflows.unitmatrix_composer + rules.voice_leading.
mido used READ-ONLY in the separate audit script.
"""

import os
import sys
import json

import numpy as np

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer
from workflows.provenance import write_provenance, AI_ASSISTED
from visualization.grid import write_grid_visualization

# Instrument registry (source of truth - NOT pip-installed)
INSTR_DIR = "/opt/data/repos/musicom/projects/Instruments"
if INSTR_DIR not in sys.path:
    sys.path.insert(0, INSTR_DIR)
from instrument_registry import (  # noqa: E402
    TRUMPET, TENOR_SAX, CLAVI, DOUBLE_BASS,
)
from Percussion.drum_kit.drum_kit import KIT  # noqa: E402

SEED = 20261003
rng = np.random.default_rng(SEED)

# ---------------------------------------------------------------- project dirs
PROJ = "/opt/data/repos/musicom/projects/Styles/Funk/220-funk-contour-groove"
MIDI_DIR = os.path.join(PROJ, "MIDI")
AUDIO_DIR = os.path.join(PROJ, "Audio")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")
for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
    os.makedirs(d, exist_ok=True)

# ---------------------------------------------------------------- grid & timing
BPM = 100
TPB = 480
BEATS_PER_BAR = 4
GRID16 = 120
GRID8 = 240
BAR_TICKS = TPB * BEATS_PER_BAR          # 1920
SECTIONS = ["Intro", "Theme", "Variation", "Development", "Climax", "Outro"]
BARS_PER_SECTION = 4
N_SECTIONS = len(SECTIONS)
N_BARS = N_SECTIONS * BARS_PER_SECTION  # 24
SECTION_TICKS = BAR_TICKS * BARS_PER_SECTION   # 7680
TOTAL_TICKS = SECTION_TICKS * N_SECTIONS       # 46080

# ---------------------------------------------------------------- harmony
# E minor pentatonic: E(4) G(7) A(9) B(11) D(2)
SCALE_PCS = {4, 7, 9, 11, 2}
# pentatonic rank (0..4) -> semitone offset above the tonic (E)
PENT = [0, 3, 5, 7, 10]

# 4-note palettes (subsets of the pentatonic, each drops ONE scale tone).
PALETTES = {
    "Em": {4, 7, 11, 2},    # E G B D   (drop A)
    "G":  {7, 9, 11, 2},    # G A B D   (drop E)
    "A":  {9, 4, 11, 2},    # A E B D   (drop G)
    "D":  {2, 7, 9, 4},     # D G A E   (drop B)
}
PALETTE_ROOT = {"Em": 4, "G": 7, "A": 9, "D": 2}

# Progression per section (4 bars each) - funk minor/dorian arc:
SECTION_PALETTES = {
    0: ["Em", "Em", "G", "Em"],    # Intro     - sparse tonic call, on the one
    1: ["Em", "A", "Em", "G"],     # Theme     - arch statement
    2: ["A", "G", "D", "G"],       # Variation - valley answer
    3: ["D", "G", "A", "D"],       # Development - jagged, tension
    4: ["G", "Em", "D", "Em"],     # Climax    - rising peak
    5: ["Em", "G", "Em", "Em"],    # Outro     - falling resolve
}


def get_bar_palette(bar_idx):
    sec_idx = bar_idx // BARS_PER_SECTION
    bar_in_sec = bar_idx % BARS_PER_SECTION
    return SECTION_PALETTES[sec_idx][bar_in_sec]


def quantize_to_chord(pitch, chord_pcs, min_pitch=None, max_pitch=None):
    """Nearest pitch whose pitch-class is in chord_pcs, optionally bounded."""
    candidates = []
    for octv in range(1, 9):
        for pc in chord_pcs:
            p = octv * 12 + pc
            if min_pitch is not None and p < min_pitch:
                continue
            if max_pitch is not None and p > max_pitch:
                continue
            candidates.append(p)
    if not candidates:
        for octv in range(1, 9):
            for pc in chord_pcs:
                candidates.append(octv * 12 + pc)
    return min(candidates, key=lambda c: (abs(c - pitch), c))


# ================================================================
# ABSTRACT LAYER - Method 095 Contour Theory Composition (CTC)
# ================================================================
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


def contour_tension(cseg):
    cas = cseg.cas()
    changes = sum(1 for i in range(1, len(cas)) if cas[i] != cas[i - 1])
    max_run = 1
    run = 1
    for i in range(1, len(cas)):
        run = run + 1 if cas[i] == cas[i - 1] else 1
        max_run = max(max_run, run)
    from collections import Counter
    counts = Counter(cas)
    probs = [c / len(cas) for c in counts.values()]
    entropy = -sum(p * np.log2(p) for p in probs) if probs else 0.0
    return {
        "direction_changes": changes,
        "max_run_length": max_run,
        "entropy": round(float(entropy), 3),
        "tension_score": round(float(changes + max_run + entropy), 3),
    }


# Length-4 contour vocabulary, keyed by section CAS template.
VOCAB4 = {
    "arch":      CSeg([0, 2, 3, 1]),   # + + -
    "valley":    CSeg([2, 1, 0, 3]),   # - - +
    "oscillate": CSeg([0, 3, 1, 2]),   # + - +
    "rising":    CSeg([0, 1, 2, 3]),   # + + +
    "falling":   CSeg([3, 2, 1, 0]),   # - - -
    "chaos":     CSeg([1, 3, 0, 2]),   # + - + (jagged)
}

SECTION_TEMPLATES = ["oscillate", "arch", "valley", "chaos", "rising", "falling"]

DENSITY = {0: 1, 1: 2, 2: 2, 3: 2, 4: 2, 5: 1}

# Funk 16th-note syncopation grids (all multiples of GRID16 -> on-grid).
FULL_GRID = [0, 6, 10, 14]                       # on the one + offbeat hits
HALF_GRIDS = ([0, 3, 5, 7], [8, 11, 13, 15])     # two half-bar dense grids

TRANSFORMS = ["id", "I", "R", "RI"]

# register base = octave of E (keeps base + PENT inside E-minor-pentatonic)
REGISTER_BASE = {0: 64, 1: 64, 2: 64, 3: 76, 4: 76, 5: 52}


def lead_motifs(s_idx, bar_in_sec):
    ptype = SECTION_TEMPLATES[s_idx]
    seed = VOCAB4[ptype]
    n_motifs = DENSITY[s_idx]
    out = []
    for m in range(n_motifs):
        tf_idx = (s_idx + bar_in_sec * 2 + m) % 4
        tf = TRANSFORMS[tf_idx]
        out.append((seed.transform(tf), tf))
    return out


def motif_onsets(bar_in_sec, motif_idx, n_motifs):
    if n_motifs == 1:
        return FULL_GRID
    return HALF_GRIDS[motif_idx]


def cseg_pitches(cseg, base):
    return [base + PENT[r] for r in cseg.ranks]


# ================================================================
# PHASE 1: Raw abstract draft (single Trumpet voice, whole-tone,
#          off-grid fractional timing, no scale/chord snapping)
# ================================================================
def generate_phase1_raw():
    composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB,
                                  beats_per_bar=BEATS_PER_BAR)
    composer.create_matrix(num_voices=1, num_sections=N_SECTIONS)
    composer.add_voice("RawTrumpet", program=TRUMPET.midi_program, channel=0)

    rng1 = np.random.default_rng(SEED + 1)

    for s_idx, s_name in enumerate(SECTIONS):
        composer.add_section(s_name, bars=BARS_PER_SECTION)
        events = []
        base = REGISTER_BASE[s_idx]
        for bar_in_sec in range(BARS_PER_SECTION):
            bar_start = bar_in_sec * BAR_TICKS
            motifs = lead_motifs(s_idx, bar_in_sec)
            for m_idx, (cseg, tf) in enumerate(motifs):
                onsets = motif_onsets(bar_in_sec, m_idx, len(motifs))
                for i, r in enumerate(cseg.ranks):
                    raw_pitch = base + 2 * r          # whole-tone realization
                    jitter = int(rng1.integers(-30, 31))
                    t_onset = bar_start + onsets[i] * GRID16 + jitter
                    t_onset = max(1, min(t_onset, SECTION_TICKS - 2))
                    dur = int(rng1.integers(150, 260))
                    end_t = min(t_onset + dur, SECTION_TICKS - 1)
                    vel = int(70 + 6 * r)
                    events.append(MusicEvent(
                        pitch=raw_pitch, volume=vel,
                        start_tick=t_onset, end_tick=end_t
                    ))
        events.sort(key=lambda e: (e.start_tick, e.end_tick))
        events.append(MusicEvent(
            pitch=0, volume=0,
            start_tick=SECTION_TICKS - 1, end_tick=SECTION_TICKS
        ))
        composer.fill_voice_section("RawTrumpet", s_name, MusicUnit(events=events))

    ok, msg = composer.validate()
    assert ok, f"Phase 1 validate failed: {msg}"

    p1_path = os.path.join(MIDI_DIR, "220-funk-contour-groove-phase1.mid")
    composer.to_midi(p1_path)
    assert os.path.getsize(p1_path) > 40, "Phase 1 MIDI empty"

    write_provenance(
        p1_path,
        classification=AI_ASSISTED,
        generator="musicom.workflows.unitmatrix_composer",
        parameters={
            "project": "220-funk-contour-groove",
            "phase": 1,
            "style": "Funk",
            "method": "095 Contour Theory Composition (CTC)",
            "layer": "abstract",
            "contour_vocabulary": sorted(VOCAB4.keys()),
            "raw_realization": "whole-tone (rank -> base + 2*rank)",
            "raw_timing": "off-grid (16th +-30 tick jitter)",
            "key": "E minor pentatonic",
            "bpm": BPM,
            "seed": SEED,
        }
    )
    print(f"Phase 1 MIDI: {p1_path} ({os.path.getsize(p1_path)} bytes)")
    return p1_path


# ================================================================
# PHASE 2: Musicom rules post-process + full funk texture
# ================================================================
def generate_phase2_composition():
    composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB,
                                  beats_per_bar=BEATS_PER_BAR)
    composer.create_matrix(num_voices=5, num_sections=N_SECTIONS)

    composer.add_voice("Trumpet", program=TRUMPET.midi_program, channel=0)
    composer.add_voice("Sax", program=TENOR_SAX.midi_program, channel=1)
    composer.add_voice("Clav", program=CLAVI.midi_program, channel=2)
    composer.add_voice("Bass", program=DOUBLE_BASS.midi_program, channel=3)
    composer.add_voice("Drums", program=0, channel=9)

    for s_idx, s_name in enumerate(SECTIONS):
        composer.add_section(s_name, bars=BARS_PER_SECTION)

        trumpet_events = []
        sax_events = []
        clav_events = []
        bass_events = []
        drum_events = []

        base = REGISTER_BASE[s_idx]

        for bar_in_sec in range(BARS_PER_SECTION):
            bar_start = bar_in_sec * BAR_TICKS
            pal_name = SECTION_PALETTES[s_idx][bar_in_sec]
            pal_pcs = PALETTES[pal_name]
            motifs = lead_motifs(s_idx, bar_in_sec)

            # ---- 1. Trumpet lead (contour melody, pentatonic + palette) ----
            for m_idx, (cseg, tf) in enumerate(motifs):
                onsets = motif_onsets(bar_in_sec, m_idx, len(motifs))
                for i, r in enumerate(cseg.ranks):
                    t_onset = bar_start + onsets[i] * GRID16
                    raw = base + PENT[r]
                    p = quantize_to_chord(raw, pal_pcs, min_pitch=52, max_pitch=88)
                    vel = 70 + 6 * r
                    trumpet_events.append(MusicEvent(
                        pitch=p, volume=vel,
                        start_tick=t_onset, end_tick=t_onset + 200
                    ))

            # ---- 2. Tenor sax horn stabs (offbeat punches, beats 2.5 / 4.5) ----
            cseg = motifs[0][0]
            inv = cseg.invert()
            sr = sorted(inv.ranks)
            order = [sr[-1], sr[len(sr) // 2], sr[0]]   # hi -> mid -> lo stab
            base_hi = max(60, min(72, base + 12))
            for i, r in enumerate(order):
                t_onset = bar_start + [6, 10, 14][i] * GRID16
                p = quantize_to_chord(base_hi + PENT[r], pal_pcs,
                                      min_pitch=58, max_pitch=84)
                sax_events.append(MusicEvent(
                    pitch=p, volume=88 - i * 6,
                    start_tick=t_onset, end_tick=t_onset + 160
                ))

            # ---- 3. Clavinet comp (staccato 16th offbeat "chicken scratch") ----
            scratch = [2, 4, 7, 10, 12, 15]
            pal_sorted = sorted(pal_pcs)
            low = quantize_to_chord(base - 12, pal_pcs, min_pitch=48, max_pitch=72)
            high = quantize_to_chord(base, pal_pcs, min_pitch=48, max_pitch=76)
            for i, pos in enumerate(scratch):
                t_onset = bar_start + pos * GRID16
                p = low if i % 2 == 0 else high
                clav_events.append(MusicEvent(
                    pitch=p, volume=66 if i % 2 == 0 else 58,
                    start_tick=t_onset, end_tick=t_onset + 70
                ))

            # ---- 4. Funk bass (root/octave/fifth syncopation, on the one) ----
            root_pc = PALETTE_ROOT[pal_name]
            root = min(range(33, 53), key=lambda c: (0 if c % 12 == root_pc else 1,
                                                     abs(c - 40)))
            fifth = root + 7
            octave = root + 12
            bass_pat = [(0, root), (6, octave), (8, root), (11, fifth), (14, octave)]
            for pos, note in bass_pat:
                t_onset = bar_start + pos * GRID16
                dur = 300 if pos == 0 else 160
                bass_events.append(MusicEvent(
                    pitch=note, volume=96 if pos == 0 else 84,
                    start_tick=t_onset, end_tick=min(t_onset + dur, SECTION_TICKS)
                ))

            # ---- 5. Funk drum kit (backbeat + 16th hats + sync kick + clap) ----
            for pos in (0, 8):
                drum_events.append(MusicEvent(
                    pitch=KIT["kick"], volume=100,
                    start_tick=bar_start + pos * GRID16,
                    end_tick=bar_start + pos * GRID16 + 120
                ))
            drum_events.append(MusicEvent(
                pitch=KIT["kick"], volume=64,
                start_tick=bar_start + 14 * GRID16,
                end_tick=bar_start + 14 * GRID16 + 60
            ))
            for pos in (4, 12):
                drum_events.append(MusicEvent(
                    pitch=KIT["snare"], volume=88,
                    start_tick=bar_start + pos * GRID16,
                    end_tick=bar_start + pos * GRID16 + 100
                ))
            for pos in range(16):
                acc = 70 if pos % 4 == 0 else 48
                drum_events.append(MusicEvent(
                    pitch=KIT["hat_closed"], volume=acc,
                    start_tick=bar_start + pos * GRID16,
                    end_tick=bar_start + pos * GRID16 + 40
                ))
            for pos in (4, 12):
                drum_events.append(MusicEvent(
                    pitch=KIT["clap"], volume=70,
                    start_tick=bar_start + pos * GRID16,
                    end_tick=bar_start + pos * GRID16 + 60
                ))

        def seal(ev_list):
            clamped = []
            for e in ev_list:
                st = min(e.start_tick, SECTION_TICKS - 1)
                en = min(max(e.end_tick, st + 1), SECTION_TICKS)
                clamped.append(MusicEvent(
                    pitch=e.pitch, volume=e.volume,
                    start_tick=st, end_tick=en
                ))
            clamped.sort(key=lambda e: (e.start_tick, e.end_tick))
            clamped.append(MusicEvent(
                pitch=0, volume=0,
                start_tick=SECTION_TICKS - 1, end_tick=SECTION_TICKS
            ))
            return MusicUnit(events=clamped)

        composer.fill_voice_section("Trumpet", s_name, seal(trumpet_events))
        composer.fill_voice_section("Sax", s_name, seal(sax_events))
        composer.fill_voice_section("Clav", s_name, seal(clav_events))
        composer.fill_voice_section("Bass", s_name, seal(bass_events))
        composer.fill_voice_section("Drums", s_name, seal(drum_events))

    ok, msg = composer.validate()
    assert ok, f"Phase 2 validate failed: {msg}"

    p2_path = os.path.join(MIDI_DIR, "220-funk-contour-groove.mid")
    composer.to_midi(p2_path)
    assert os.path.getsize(p2_path) > 40, "Phase 2 MIDI empty"

    grid_path = os.path.join(ANALYSIS_DIR, "grid_visualization.txt")
    write_grid_visualization(
        composer.matrix, grid_path,
        ticks_per_character=240,
        voice_names=["Trumpet", "Sax", "Clav", "Bass", "Drums"],
        bpm=BPM
    )

    write_provenance(
        p2_path,
        classification=AI_ASSISTED,
        generator="musicom.workflows.unitmatrix_composer",
        parameters={
            "project": "220-funk-contour-groove",
            "phase": 2,
            "style": "Funk",
            "method": "095 Contour Theory Composition (CTC)",
            "layer": "abstract",
            "quantization": "16th grid (120 ticks) + E-minor-pentatonic + per-bar palette",
            "key": "E minor pentatonic",
            "bpm": BPM,
            "seed": SEED,
        }
    )
    print(f"Phase 2 MIDI: {p2_path} ({os.path.getsize(p2_path)} bytes)")
    return p2_path


# ================================================================
# Abstract-layer report + summary
# ================================================================
def write_contour_report():
    lines = []
    lines.append("CONTOUR PROGRESSION (abstract layer, Method 095 CTC)")
    lines.append("=" * 70)
    for s_idx, s_name in enumerate(SECTIONS):
        ptype = SECTION_TEMPLATES[s_idx]
        seed = VOCAB4[ptype]
        t = contour_tension(seed)
        lines.append(f"\n[{s_name}] template={ptype}  seed CSeg={seed.ranks} "
                     f"CAS={''.join(seed.cas())}")
        lines.append(f"    tension: changes={t['direction_changes']} "
                     f"max_run={t['max_run_length']} entropy={t['entropy']} "
                     f"score={t['tension_score']}")
        for bar_in_sec in range(BARS_PER_SECTION):
            motifs = lead_motifs(s_idx, bar_in_sec)
            desc = ", ".join(f"{tf}:{c.ranks}" for c, tf in motifs)
            lines.append(f"    bar {bar_in_sec}: {desc}")
    return "\n".join(lines) + "\n"


def write_summary():
    tension_curve = []
    for s_idx, s_name in enumerate(SECTIONS):
        seed = VOCAB4[SECTION_TEMPLATES[s_idx]]
        t = contour_tension(seed)
        tension_curve.append({
            "section": s_name,
            "template": SECTION_TEMPLATES[s_idx],
            "seed_cseg": seed.ranks,
            "cas": "".join(seed.cas()),
            **t,
        })
    summary = {
        "project": "220-funk-contour-groove",
        "style": "Funk",
        "method": "095 Contour Theory Composition (CTC)",
        "layer": "abstract",
        "key": "E minor pentatonic",
        "scale_pcs": sorted(SCALE_PCS),
        "bpm": BPM,
        "tpb": TPB,
        "sections": SECTIONS,
        "bars": N_BARS,
        "total_ticks": TOTAL_TICKS,
        "voices": [
            {"name": "Trumpet", "program": TRUMPET.midi_program, "channel": 0},
            {"name": "Sax", "program": TENOR_SAX.midi_program, "channel": 1},
            {"name": "Clav", "program": CLAVI.midi_program, "channel": 2},
            {"name": "Bass", "program": DOUBLE_BASS.midi_program, "channel": 3},
            {"name": "Drums", "program": 0, "channel": 9},
        ],
        "palettes": {k: sorted(v) for k, v in PALETTES.items()},
        "progression": SECTION_PALETTES,
        "tension_curve": tension_curve,
        "seed": SEED,
    }
    with open(os.path.join(ANALYSIS_DIR, "summary.json"), "w") as f:
        json.dump(summary, f, indent=2)
    return summary


if __name__ == "__main__":
    print("=== Method 095 Contour Theory Composition (abstract layer) ===")
    print("Contour report:")
    print(write_contour_report())
    write_summary()

    print("=== Phase 1: raw abstract draft ===")
    generate_phase1_raw()
    print("=== Phase 2: rules composition ===")
    generate_phase2_composition()
    print("Done!")
