# -*- coding: utf-8 -*-
"""105-african-contour - African style / ABSTRACT layer: Method 095 Contour
Theory Composition (CTC).

Autonomous nightly composition job (date: 2026-09-24).

Contour Theory (Friedmann 1985; Marvin & Laprade 1987; Morris 1993) treats the
SHAPE of a melodic line as the primary compositional parameter, independent of
exact pitch-class content. The abstract layer designs pure contour prototypes
(CSeg = Contour Segment, a normalized rank sequence; CAS = Contour Adjacency
Series, the up/down/same direction string) and transforms them via the dihedral
group {I, R, RI}. The concrete layer maps ranks -> scale degrees -> pitches.

Two-phase architecture:
  Phase 1 (raw abstract draft): single Kalimba voice. Contour ranks realized as
    a raw whole-tone pitch stream (rank r -> base + 2*r), placed on FRACTIONAL
    off-grid ticks. No scale/chord snapping. Exported as -phase1.mid.
  Phase 2 (musicom rules): 16th-grid lock -> C-pentatonic scale snap -> per-bar
    palette (chord-tone) quantize -> voice-leading -> full 5-voice African
    texture (kalimba lead, flute call/response, marimba interlock, double-bass
    foundation, djembe kit). Exported as .mid.

Key: C major pentatonic (C D E G A) = pc {0,2,4,7,9}.
Form: Intro | Theme | Variation | Development | Climax | Outro (6 x 4 = 24 bars).
BPM 112, 4/4, 480 TPB (BAR = 1920, 16th = 120, 8th = 240).

Engine only: structures + workflows.unitmatrix_composer + rules.voice_leading.
mido used READ-ONLY in the separate audit script.
"""

import os
import sys
import json
import random as _random

import numpy as np

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer
from workflows.provenance import write_provenance, AI_ASSISTED
from visualization.grid import write_grid_visualization
from rules.voice_leading import VoiceLeadingRules

# Instrument registry (source of truth - NOT pip-installed)
INSTR_DIR = "/opt/data/repos/musicom/projects/Instruments"
if INSTR_DIR not in sys.path:
    sys.path.insert(0, INSTR_DIR)
from instrument_registry import (  # noqa: E402
    KALIMBA, FLUTE, MARIMBA, DOUBLE_BASS,
)
from Percussion.drum_kit.drum_kit import KIT  # noqa: E402

SEED = 20260924
rng = np.random.default_rng(SEED)

# ---------------------------------------------------------------- project dirs
PROJ = "/opt/data/repos/musicom/projects/Styles/African/105-african-contour"
MIDI_DIR = os.path.join(PROJ, "MIDI")
AUDIO_DIR = os.path.join(PROJ, "Audio")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")
for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
    os.makedirs(d, exist_ok=True)

# ---------------------------------------------------------------- grid & timing
BPM = 112
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
# C major pentatonic: C(0) D(2) E(4) G(7) A(9)
SCALE_PCS = {0, 2, 4, 7, 9}
# pentatonic rank (0..4) -> semitone offset above the tonic (C)
PENT = [0, 2, 4, 7, 9]

# 4-note palettes (subsets of the pentatonic, each drops ONE scale tone).
# The dropped tone is the out-of-chord note -> the harmony audit has teeth.
PALETTES = {
    "C":  {0, 4, 7, 9},   # C E G A   (drop D)
    "D":  {2, 4, 7, 9},   # D E G A   (drop C)
    "Am": {9, 0, 2, 4},   # A C D E   (drop G)
    "G":  {7, 9, 0, 2},   # G A C D   (drop E)
}
PALETTE_ROOT = {"C": 0, "D": 2, "Am": 9, "G": 7}

# Progression per section (4 bars each), modal arc:
SECTION_PALETTES = {
    0: ["C", "C", "G", "C"],       # Intro     - sparse tonic call
    1: ["C", "Am", "C", "G"],      # Theme     - arch statement
    2: ["Am", "G", "D", "G"],      # Variation - valley answer
    3: ["D", "G", "Am", "D"],      # Development - jagged, tension
    4: ["G", "C", "D", "C"],       # Climax    - rising peak
    5: ["C", "G", "C", "C"],       # Outro     - falling resolve
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
        """Contour Adjacency Series: up/down/same between adjacent points."""
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

# density: motifs per bar (arc). 1 motif = 4 notes on full-bar syncopated grid;
# 2 motifs = 4+4 notes on two half-bar grids.
DENSITY = {0: 1, 1: 2, 2: 2, 3: 2, 4: 2, 5: 1}

FULL_GRID = [0, 4, 10, 14]                       # full-bar, 4 onsets (syncopated)
HALF_GRIDS = ([0, 3, 5, 7], [8, 11, 13, 15])    # two half-bar 4-onset grids

TRANSFORMS = ["id", "I", "R", "RI"]

# register base = octave of C (keeps base + PENT inside C-pentatonic)
REGISTER_BASE = {0: 60, 1: 60, 2: 60, 3: 72, 4: 72, 5: 48}


def lead_motifs(s_idx, bar_in_sec):
    """Return list of (CSeg, transform) motifs for this bar."""
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
    """16th-grid onset positions (multiples of GRID16) for one motif."""
    if n_motifs == 1:
        return FULL_GRID
    return HALF_GRIDS[motif_idx]


def cseg_pitches(cseg, base):
    """Rank -> pentatonic degree -> absolute pitch (C-pentatonic at `base`)."""
    return [base + PENT[r] for r in cseg.ranks]


# ================================================================
# PHASE 1: Raw abstract draft (single Kalimba voice, whole-tone,
#          off-grid fractional timing, no scale/chord snapping)
# ================================================================
def generate_phase1_raw():
    composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB,
                                  beats_per_bar=BEATS_PER_BAR)
    composer.create_matrix(num_voices=1, num_sections=N_SECTIONS)
    composer.add_voice("RawKalimba", program=KALIMBA.midi_program, channel=0)

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
                    # raw whole-tone realization: rank -> base + 2*rank
                    raw_pitch = base + 2 * r
                    # off-grid jitter (raw fingerprint)
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
        # terminal landmark (zero-drift)
        events.sort(key=lambda e: (e.start_tick, e.end_tick))
        events.append(MusicEvent(
            pitch=0, volume=0,
            start_tick=SECTION_TICKS - 1, end_tick=SECTION_TICKS
        ))
        composer.fill_voice_section("RawKalimba", s_name, MusicUnit(events=events))

    ok, msg = composer.validate()
    assert ok, f"Phase 1 validate failed: {msg}"

    p1_path = os.path.join(MIDI_DIR, "105-african-contour-phase1.mid")
    composer.to_midi(p1_path)
    assert os.path.getsize(p1_path) > 40, "Phase 1 MIDI empty"

    write_provenance(
        p1_path,
        classification=AI_ASSISTED,
        generator="musicom.workflows.unitmatrix_composer",
        parameters={
            "project": "105-african-contour",
            "phase": 1,
            "style": "African",
            "method": "095 Contour Theory Composition (CTC)",
            "layer": "abstract",
            "contour_vocabulary": sorted(VOCAB4.keys()),
            "raw_realization": "whole-tone (rank -> base + 2*rank)",
            "raw_timing": "off-grid (16th +-30 tick jitter)",
            "key": "C major pentatonic",
            "bpm": BPM,
            "seed": SEED,
        }
    )
    print(f"Phase 1 MIDI: {p1_path} ({os.path.getsize(p1_path)} bytes)")
    return p1_path


# ================================================================
# PHASE 2: Musicom rules post-process + full African texture
# ================================================================
def generate_phase2_composition():
    composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB,
                                  beats_per_bar=BEATS_PER_BAR)
    composer.create_matrix(num_voices=5, num_sections=N_SECTIONS)

    composer.add_voice("Kalimba", program=KALIMBA.midi_program, channel=0)
    composer.add_voice("Flute", program=FLUTE.midi_program, channel=1)
    composer.add_voice("Marimba", program=MARIMBA.midi_program, channel=2)
    composer.add_voice("Bass", program=DOUBLE_BASS.midi_program, channel=3)
    composer.add_voice("Drums", program=0, channel=9)

    for s_idx, s_name in enumerate(SECTIONS):
        composer.add_section(s_name, bars=BARS_PER_SECTION)

        kalimba_events = []
        flute_events = []
        marimba_events = []
        bass_events = []
        drum_events = []

        base = REGISTER_BASE[s_idx]

        for bar_in_sec in range(BARS_PER_SECTION):
            bar_start = bar_in_sec * BAR_TICKS
            pal_name = SECTION_PALETTES[s_idx][bar_in_sec]
            pal_pcs = PALETTES[pal_name]
            motifs = lead_motifs(s_idx, bar_in_sec)

            # ---- 1. Kalimba lead (contour melody, pentatonic + palette) ----
            for m_idx, (cseg, tf) in enumerate(motifs):
                onsets = motif_onsets(bar_in_sec, m_idx, len(motifs))
                for i, r in enumerate(cseg.ranks):
                    t_onset = bar_start + onsets[i] * GRID16
                    raw = base + PENT[r]
                    p = quantize_to_chord(raw, pal_pcs, min_pitch=52, max_pitch=88)
                    vel = 70 + 6 * r
                    kalimba_events.append(MusicEvent(
                        pitch=p, volume=vel,
                        start_tick=t_onset, end_tick=t_onset + 200
                    ))

            # ---- 2. Flute call/response (inverted contour, upper register,
            #         answered on beats 3-4 = half-bar offset) ----
            cseg = motifs[0][0]
            inv = cseg.invert()
            sr = sorted(inv.ranks)
            order = [sr[-1], sr[len(sr) // 2], sr[0]]   # hi -> mid -> lo answer
            base_hi = max(72, min(84, base + 24))
            for i, r in enumerate(order):
                t_onset = bar_start + [8, 11, 14][i] * GRID16
                p = quantize_to_chord(base_hi + PENT[r], pal_pcs,
                                      min_pitch=72, max_pitch=96)
                flute_events.append(MusicEvent(
                    pitch=p, volume=82 - i * 6,
                    start_tick=t_onset, end_tick=t_onset + 360
                ))

            # ---- 3. Marimba interlock (African 3-3-2 bell pattern ostinato) ----
            bell = [0, 3, 6, 8, 11, 14]
            pal_sorted = sorted(pal_pcs)
            low = quantize_to_chord(base, pal_pcs, min_pitch=55, max_pitch=76)
            high = quantize_to_chord(base + 12, pal_pcs, min_pitch=55, max_pitch=88)
            for i, pos in enumerate(bell):
                t_onset = bar_start + pos * GRID16
                p = low if i % 2 == 0 else high
                marimba_events.append(MusicEvent(
                    pitch=p, volume=90 if i % 2 == 0 else 74,
                    start_tick=t_onset, end_tick=t_onset + 140
                ))

            # ---- 4. Double bass foundation (root + fifth, low) ----
            root_pc = PALETTE_ROOT[pal_name]
            root = min(range(33, 53), key=lambda c: (0 if c % 12 == root_pc else 1,
                                                     abs(c - 40)))
            fifth = root + 7
            bass_events.append(MusicEvent(
                pitch=root, volume=96, start_tick=bar_start,
                end_tick=bar_start + 900
            ))
            bass_events.append(MusicEvent(
                pitch=fifth, volume=84, start_tick=bar_start + 960,
                end_tick=bar_start + 960 + 900
            ))

            # ---- 5. Djembe kit (cowbell bell pattern + kick/slap/shaker) ----
            for pos in bell:
                drum_events.append(MusicEvent(
                    pitch=KIT["cowbell"], volume=88,
                    start_tick=bar_start + pos * GRID16,
                    end_tick=bar_start + pos * GRID16 + 60
                ))
            for pos in (0, 8):
                drum_events.append(MusicEvent(
                    pitch=KIT["kick"], volume=100,
                    start_tick=bar_start + pos * GRID16,
                    end_tick=bar_start + pos * GRID16 + 120
                ))
            for pos in (4, 12):
                drum_events.append(MusicEvent(
                    pitch=KIT["snare"], volume=78,
                    start_tick=bar_start + pos * GRID16,
                    end_tick=bar_start + pos * GRID16 + 120
                ))
            for pos in range(0, 16, 2):
                drum_events.append(MusicEvent(
                    pitch=KIT["maracas"], volume=56,
                    start_tick=bar_start + pos * GRID16,
                    end_tick=bar_start + pos * GRID16 + 40
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

        composer.fill_voice_section("Kalimba", s_name, seal(kalimba_events))
        composer.fill_voice_section("Flute", s_name, seal(flute_events))
        composer.fill_voice_section("Marimba", s_name, seal(marimba_events))
        composer.fill_voice_section("Bass", s_name, seal(bass_events))
        composer.fill_voice_section("Drums", s_name, seal(drum_events))

    ok, msg = composer.validate()
    assert ok, f"Phase 2 validate failed: {msg}"

    p2_path = os.path.join(MIDI_DIR, "105-african-contour.mid")
    composer.to_midi(p2_path)
    assert os.path.getsize(p2_path) > 40, "Phase 2 MIDI empty"

    grid_path = os.path.join(ANALYSIS_DIR, "grid_visualization.txt")
    write_grid_visualization(
        composer.matrix, grid_path,
        ticks_per_character=240,
        voice_names=["Kalimba", "Flute", "Marimba", "Bass", "Drums"],
        bpm=BPM
    )

    write_provenance(
        p2_path,
        classification=AI_ASSISTED,
        generator="musicom.workflows.unitmatrix_composer",
        parameters={
            "project": "105-african-contour",
            "phase": 2,
            "style": "African",
            "method": "095 Contour Theory Composition (CTC)",
            "layer": "abstract",
            "quantization": "16th grid (120 ticks) + pentatonic + per-bar palette",
            "key": "C major pentatonic",
            "bpm": BPM,
            "seed": SEED,
        }
    )
    print(f"Phase 2 MIDI: {p2_path} ({os.path.getsize(p2_path)} bytes)")
    return p2_path


# ================================================================
# Abstract-layer report (contour progression + tension curve)
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
        "project": "105-african-contour",
        "style": "African",
        "method": "095 Contour Theory Composition (CTC)",
        "layer": "abstract",
        "key": "C major pentatonic",
        "scale_pcs": sorted(SCALE_PCS),
        "bpm": BPM,
        "tpb": TPB,
        "sections": SECTIONS,
        "bars": N_BARS,
        "total_ticks": TOTAL_TICKS,
        "voices": [
            {"name": "Kalimba", "program": KALIMBA.midi_program, "channel": 0},
            {"name": "Flute", "program": FLUTE.midi_program, "channel": 1},
            {"name": "Marimba", "program": MARIMBA.midi_program, "channel": 2},
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
