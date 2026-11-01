# -*- coding: utf-8 -*-
"""278-funk-contour-groove-suite - EXTENSION of 220-funk-contour-groove.

Rework job (2026-11-01): audit source 220, found engine-compliant, EXTEND to a
longer (32-bar, 8-section) suite with more variation. Preserves identity:
Funk, E minor pentatonic, 100 BPM, Contour Theory (CTC) method, and the
5-voice texture (trumpet lead / tenor-sax stabs / clavinet comp / contrabass
funk bass / backbeat kit).

Method 095 Contour Theory Composition (abstract layer): melodic DNA = shape.
Length-4 CSeg (normalized rank sequence) + CAS (up/down direction string),
transformed under the dihedral group {I, R, RI}, concretized into the
E-minor-pentatonic then quantized to per-bar chord-tone palettes.

Two-phase architecture:
  Phase 1 (raw abstract draft): single Trumpet voice, whole-tone realization
    (rank -> base + 2*rank), fractional off-grid ticks, no scale/chord snap.
  Phase 2 (musicom rules): 16th-grid lock -> pentatonic snap -> per-bar palette
    quantize -> 5-voice funk texture -> humanize (dual -perfect/-humanized).

Variation techniques added on top of the source (each mapped to a section):
  1. Inversion  (I)    - ThemeB is the arch contour inverted (valley).
  2. Retrograde (R)    - Variation is the arch contour reversed.
  3. Augmentation      - Climax plays half-time (8th onsets, ~2x durations).
  4. Diminution        - Development runs 3 motifs/bar (denser 16th grid).
  5. Register shift    - E4 -> E5 (Development/Climax), E3 (Bridge/Outro).
  6. Counterline       - Climax sax sustains a rising counter-melody; Bridge
                         bass holds a root pedal.
  7. Palette/mode color- Bridge leans on a D-palette pedal (dominant-ish pull).

Key: E minor pentatonic (E G A B D) = pc {4,7,9,11,2}.
Form: Intro|ThemeA|ThemeB|Variation|Development|Bridge|Climax|Outro (8 x 4 = 32).
BPM 100, 4/4, 480 TPB (BAR = 1920, 16th = 120, 8th = 240).

Engine only: structures + workflows.unitmatrix_composer + workflows.humanize.
mido used READ-ONLY in the separate verify.py.
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

# Instrument registry (source of truth - NOT pip-installed)
INSTR_DIR = "/opt/data/repos/musicom/projects/Instruments"
if INSTR_DIR not in sys.path:
    sys.path.insert(0, INSTR_DIR)
import instrument_registry as IR  # noqa: E402
from Percussion.drum_kit.drum_kit import KIT  # noqa: E402

PROJ_NAME = "278-funk-contour-groove-suite"
SEED = 20261101
rng = np.random.default_rng(SEED)

PROJ = "/opt/data/projects/Styles/Funk/" + PROJ_NAME
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
SECTIONS = ["Intro", "ThemeA", "ThemeB", "Variation",
            "Development", "Bridge", "Climax", "Outro"]
BARS_PER_SECTION = 4
N_SECTIONS = len(SECTIONS)               # 8
N_BARS = N_SECTIONS * BARS_PER_SECTION   # 32
SECTION_TICKS = BAR_TICKS * BARS_PER_SECTION   # 7680
TOTAL_TICKS = SECTION_TICKS * N_SECTIONS       # 61440

STYLE = "funk"

# ---------------------------------------------------------------- harmony
# E minor pentatonic: E(4) G(7) A(9) B(11) D(2)
SCALE_PCS = {4, 7, 9, 11, 2}
PENT = [0, 3, 5, 7, 10]                  # pentatonic rank -> semitone above E

# 4-note palettes (subsets of the pentatonic; each drops ONE scale tone).
PALETTES = {
    "Em": {4, 7, 11, 2},     # E G B D
    "G":  {7, 9, 11, 2},     # G A B D
    "A":  {9, 4, 11, 2},     # A E B D
    "D":  {2, 7, 9, 4},      # D G A E
}
PALETTE_ROOT = {"Em": 4, "G": 7, "A": 9, "D": 2}

# Per-section 4-bar progression (each section its own short arc). Midpoint bar
# (index 1) gives the section's harmonic root -> midpoints are E,A,G,G,E,A,D,G:
# diverse (NOT all tonic). This defeats the bar-0 tonic bug.
SECTION_PALETTES = {
    0: ["Em", "Em", "G", "Em"],     # Intro       - sparse call, midpoint Em
    1: ["Em", "A", "Em", "G"],      # ThemeA      - statement, midpoint A
    2: ["A", "G", "D", "G"],        # ThemeB      - inversion answer, mid G
    3: ["D", "G", "A", "D"],        # Variation   - retrograde, mid G
    4: ["G", "Em", "D", "Em"],      # Development - jagged, mid Em
    5: ["D", "A", "G", "D"],        # Bridge      - D pedal pull, mid A
    6: ["A", "D", "G", "D"],        # Climax      - rising peak, mid D
    7: ["Em", "G", "Em", "Em"],     # Outro       - falling resolve, mid G
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


# Core vocabulary. ThemeA = arch; ThemeB = invert(arch); Variation =
# retrograde(arch). Explicitly derived so the technique is real, not coincidence.
_ARCH = CSeg([0, 2, 3, 1])          # + + -
VOCAB = {
    "oscillate": CSeg([0, 3, 1, 2]),    # + - +
    "arch":      _ARCH,                 # + + -
    "valley":    _ARCH.invert(),        # - - +   (INVERSION of arch)
    "retro_arch": _ARCH.retrograde(),   # + - -   (RETROGRADE of arch)
    "chaos":     CSeg([1, 3, 0, 2]),    # + - +
    "rising":    CSeg([0, 1, 2, 3]),    # + + +
    "falling":   CSeg([3, 2, 1, 0]),    # - - -
}

SECTION_TEMPLATES = ["oscillate", "arch", "valley", "retro_arch",
                     "chaos", "valley", "rising", "falling"]

# motifs per bar (density curve): Dev=3 (diminution), most=2, sparse ends=1.
DENSITY = {0: 1, 1: 2, 2: 2, 3: 2, 4: 3, 5: 1, 6: 2, 7: 1}

# register base (octave of E). Register-shift variation: E4 -> E5 (dev/climax),
# E3 (bridge/outro).
REGISTER_BASE = {0: 64, 1: 64, 2: 64, 3: 64, 4: 76, 5: 52, 6: 76, 7: 52}

# Augmentation only in Climax (section 6): half-time onset grid + ~2x duration.
AUGMENT = {6: True}

TRANSFORMS = ["id", "I", "R", "RI"]

# 16th-note syncopation grids (multiples of GRID16 -> on-grid by construction).
FULL_GRID = [0, 6, 10, 14]
HALF_GRIDS = ([0, 3, 5, 7], [8, 11, 13, 15])
THIRD_GRIDS = ([0, 2, 4, 6], [5, 7, 9, 11], [10, 12, 14, 15])
# half-time grid for augmentation (8th positions -> slower feel)
HALF_GRID_8 = [0, 3, 5, 7]


def lead_motifs(s_idx, bar_in_sec):
    ptype = SECTION_TEMPLATES[s_idx]
    seed = VOCAB[ptype]
    n_motifs = DENSITY[s_idx]
    out = []
    for m in range(n_motifs):
        tf_idx = (s_idx + bar_in_sec * 2 + m) % 4
        tf = TRANSFORMS[tf_idx]
        out.append((seed.transform(tf), tf))
    return out


def motif_onsets(s_idx, bar_in_sec, motif_idx, n_motifs):
    if AUGMENT.get(s_idx):
        return HALF_GRID_8 if motif_idx == 0 else HALF_GRID_8
    if n_motifs == 1:
        return FULL_GRID
    if n_motifs == 2:
        return HALF_GRIDS[motif_idx]
    return THIRD_GRIDS[motif_idx]


def onset_step(s_idx):
    return GRID8 if AUGMENT.get(s_idx) else GRID16


def note_dur(s_idx):
    return 430 if AUGMENT.get(s_idx) else 200


# ================================================================
# PHASE 1: raw abstract draft (single Trumpet voice, whole-tone,
#          off-grid fractional timing, no scale/chord snapping)
# ================================================================
def generate_phase1_raw():
    composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB,
                                  beats_per_bar=BEATS_PER_BAR)
    composer.create_matrix(num_voices=1, num_sections=N_SECTIONS)
    composer.add_voice("RawTrumpet", program=IR.TRUMPET.midi_program, channel=0)

    rng1 = np.random.default_rng(SEED + 1)

    for s_idx, s_name in enumerate(SECTIONS):
        composer.add_section(s_name, bars=BARS_PER_SECTION)
        events = []
        base = REGISTER_BASE[s_idx]
        for bar_in_sec in range(BARS_PER_SECTION):
            bar_start = bar_in_sec * BAR_TICKS
            motifs = lead_motifs(s_idx, bar_in_sec)
            for m_idx, (cseg, tf) in enumerate(motifs):
                onsets = motif_onsets(s_idx, bar_in_sec, m_idx, len(motifs))
                step = onset_step(s_idx)
                for i, r in enumerate(cseg.ranks):
                    raw_pitch = base + 2 * r          # whole-tone realization
                    jitter = int(rng1.integers(-30, 31))
                    on = bar_start + onsets[i] * step
                    t_onset = max(1, min(on + jitter, SECTION_TICKS - 2))
                    dur = int(rng1.integers(150, 260))
                    end_t = min(t_onset + dur, SECTION_TICKS - 1)
                    events.append(MusicEvent(
                        pitch=raw_pitch, volume=70 + 6 * r,
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

    p1_path = os.path.join(MIDI_DIR, PROJ_NAME + "-phase1.mid")
    composer.to_midi(p1_path)
    assert os.path.getsize(p1_path) > 40, "Phase 1 MIDI empty"

    write_provenance(
        p1_path,
        classification=AI_ASSISTED,
        generator="musicom.workflows.unitmatrix_composer",
        parameters={
            "project": PROJ_NAME,
            "phase": 1,
            "style": "Funk",
            "method": "095 Contour Theory Composition (CTC)",
            "layer": "abstract",
            "source": "extension of 220-funk-contour-groove",
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
# PHASE 2: musicom rules post-process + full funk texture
# ================================================================
def generate_phase2_composition():
    composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB,
                                  beats_per_bar=BEATS_PER_BAR)
    composer.create_matrix(num_voices=5, num_sections=N_SECTIONS)

    composer.add_voice("Trumpet", program=IR.TRUMPET.midi_program, channel=0)
    composer.add_voice("Sax", program=IR.TENOR_SAX.midi_program, channel=1)
    composer.add_voice("Clav", program=IR.CLAVI.midi_program, channel=2)
    composer.add_voice("Bass", program=IR.DOUBLE_BASS.midi_program, channel=3)
    composer.add_voice("Drums", program=0, channel=9)

    for s_idx, s_name in enumerate(SECTIONS):
        composer.add_section(s_name, bars=BARS_PER_SECTION)

        trumpet_events, sax_events, clav_events = [], [], []
        bass_events, drum_events = [], []

        base = REGISTER_BASE[s_idx]
        augmented = AUGMENT.get(s_idx, False)

        for bar_in_sec in range(BARS_PER_SECTION):
            bar_start = bar_in_sec * BAR_TICKS
            pal_name = SECTION_PALETTES[s_idx][bar_in_sec]
            pal_pcs = PALETTES[pal_name]
            motifs = lead_motifs(s_idx, bar_in_sec)
            n_motifs = len(motifs)
            step = onset_step(s_idx)

            # ---- 1. Trumpet lead (contour melody, pentatonic + palette) ----
            for m_idx, (cseg, tf) in enumerate(motifs):
                onsets = motif_onsets(s_idx, bar_in_sec, m_idx, n_motifs)
                for i, r in enumerate(cseg.ranks):
                    t_onset = bar_start + onsets[i] * step
                    raw = base + PENT[r]
                    p = quantize_to_chord(raw, pal_pcs, min_pitch=52, max_pitch=88)
                    end = min(t_onset + note_dur(s_idx), SECTION_TICKS)
                    trumpet_events.append(MusicEvent(
                        pitch=p, volume=70 + 6 * r,
                        start_tick=t_onset, end_tick=end
                    ))

            # ---- 2. Tenor sax (stabs; counterline in Climax/Bridge) ----
            cseg = motifs[0][0]
            if s_idx == 6:   # Climax: sustained rising counter-melody (inversion)
                inv = cseg.invert()
                base_hi = max(60, min(72, base + 12))
                for i, r in enumerate(inv.ranks):
                    t_onset = bar_start + [0, 3, 5, 7][i] * GRID8
                    p = quantize_to_chord(base_hi + PENT[r], pal_pcs,
                                          min_pitch=58, max_pitch=84)
                    sax_events.append(MusicEvent(
                        pitch=p, volume=84, start_tick=t_onset,
                        end_tick=min(t_onset + 420, SECTION_TICKS)
                    ))
            elif s_idx == 5:  # Bridge: sparse sustained color tone
                root_pc = PALETTE_ROOT[pal_name]
                p = quantize_to_chord(base + 12, pal_pcs, min_pitch=58, max_pitch=84)
                p = min([c for c in range(58, 85) if c % 12 == root_pc],
                        key=lambda c: abs(c - (base + 12)))
                sax_events.append(MusicEvent(
                    pitch=p, volume=72, start_tick=bar_start,
                    end_tick=min(bar_start + 900, SECTION_TICKS)
                ))
            else:            # normal offbeat horn stabs
                inv = cseg.invert()
                sr = sorted(inv.ranks)
                order = [sr[-1], sr[len(sr) // 2], sr[0]]
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
            low = quantize_to_chord(base - 12, pal_pcs, min_pitch=48, max_pitch=72)
            high = quantize_to_chord(base, pal_pcs, min_pitch=48, max_pitch=76)
            for i, pos in enumerate(scratch):
                t_onset = bar_start + pos * GRID16
                p = low if i % 2 == 0 else high
                clav_events.append(MusicEvent(
                    pitch=p, volume=66 if i % 2 == 0 else 58,
                    start_tick=t_onset, end_tick=t_onset + 70
                ))

            # ---- 4. Funk bass (root/octave/fifth syncopation; Bridge = pedal) ----
            root_pc = PALETTE_ROOT[pal_name]
            root = min(range(33, 53),
                       key=lambda c: (0 if c % 12 == root_pc else 1, abs(c - 40)))
            fifth = root + 7
            octave = root + 12
            if s_idx == 5:   # Bridge: root pedal (counterline contrast)
                bass_pat = [(0, root)]
                for pos, note in bass_pat:
                    t_onset = bar_start + pos * GRID16
                    bass_events.append(MusicEvent(
                        pitch=note, volume=96, start_tick=t_onset,
                        end_tick=min(bar_start + BAR_TICKS - 120, SECTION_TICKS)
                    ))
                bass_events.append(MusicEvent(
                    pitch=octave, volume=80,
                    start_tick=bar_start + 8 * GRID16,
                    end_tick=bar_start + 8 * GRID16 + 200
                ))
            else:
                bass_pat = [(0, root), (6, octave), (8, root), (11, fifth), (14, octave)]
                for pos, note in bass_pat:
                    t_onset = bar_start + pos * GRID16
                    dur = 300 if pos == 0 else 160
                    bass_events.append(MusicEvent(
                        pitch=note, volume=96 if pos == 0 else 84,
                        start_tick=t_onset,
                        end_tick=min(t_onset + dur, SECTION_TICKS)
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

    # ---- dual-version export: perfect (grid-locked) + humanized ----
    hz_seed = int(hashlib.md5((PROJ_NAME + "funk").encode()).hexdigest()[:8], 16)
    hz_instruments = {
        "Trumpet": IR.by_name("Trumpet").humanize_dna,
        "Sax": IR.by_name("Tenor Sax").humanize_dna,
        "Clav": IR.by_name("Clavi").humanize_dna,
        "Bass": IR.by_name("Double Bass").humanize_dna,
        "Drums": IR.by_name("Drum Kit").humanize_dna,
    }

    perfect_path = os.path.join(MIDI_DIR, PROJ_NAME + "-perfect.mid")
    humanized_path = os.path.join(MIDI_DIR, PROJ_NAME + "-humanized.mid")

    hz = export_dual(composer, perfect_path, humanized_path,
                     style=STYLE, seed=hz_seed, bpm=BPM, instruments=hz_instruments)

    assert os.path.getsize(perfect_path) > 40, "perfect MIDI empty"
    assert os.path.getsize(humanized_path) > 40, "humanized MIDI empty"

    with open(os.path.join(ANALYSIS_DIR, "humanize.json"), "w") as f:
        json.dump({"seed": hz_seed, "style": STYLE, "per_voice": hz}, f, indent=2)
    print("humanize stats:", json.dumps(hz, indent=1))

    grid_path = os.path.join(ANALYSIS_DIR, "grid_visualization.txt")
    # grid image is drawn from the (now humanized) matrix; acceptable since
    # it shows onset density/voice roles at 8th-note resolution.
    write_grid_visualization(
        composer.matrix, grid_path, ticks_per_character=240,
        voice_names=["Trumpet", "Sax", "Clav", "Bass", "Drums"], bpm=BPM
    )

    for path, phase in ((perfect_path, "phase2-perfect"),
                        (humanized_path, "phase2-humanized")):
        write_provenance(
            path,
            classification=AI_ASSISTED,
            generator="musicom.workflows.unitmatrix_composer + workflows.humanize",
            parameters={
                "project": PROJ_NAME,
                "phase": phase,
                "style": "Funk",
                "method": "095 Contour Theory Composition (CTC)",
                "layer": "abstract",
                "source": "extension of 220-funk-contour-groove",
                "decision": "extension (audit: standards 1-5 pass; index.html gap)",
                "quantization": "16th grid (120) + E-minor-pentatonic + per-bar palette",
                "humanize_seed": hz_seed,
                "humanize_style": STYLE,
                "key": "E minor pentatonic",
                "bpm": BPM,
                "seed": SEED,
            }
        )

    print(f"Perfect MIDI: {perfect_path} ({os.path.getsize(perfect_path)} bytes)")
    print(f"Humanized MIDI: {humanized_path} ({os.path.getsize(humanized_path)} bytes)")
    return perfect_path, humanized_path, hz, hz_seed


def write_summary():
    section_roots = [PALETTE_ROOT[SECTION_PALETTES[s][1]] for s in range(N_SECTIONS)]
    summary = {
        "project": PROJ_NAME,
        "style": "Funk",
        "method": "095 Contour Theory Composition (CTC)",
        "layer": "abstract",
        "decision": "extension of 220-funk-contour-groove",
        "key": "E minor pentatonic",
        "scale_pcs": sorted(SCALE_PCS),
        "bpm": BPM,
        "tpb": TPB,
        "sections": SECTIONS,
        "bars": N_BARS,
        "total_ticks": TOTAL_TICKS,
        "variation_techniques": {
            "Inversion": "ThemeB = invert(arch)",
            "Retrograde": "Variation = retrograde(arch)",
            "Augmentation": "Climax = half-time 8th onsets, ~2x durations",
            "Diminution": "Development = 3 motifs/bar dense 16th",
            "Register shift": "E4->E5 (Dev/Climax), E3 (Bridge/Outro)",
            "Counterline": "Climax sax rises + Bridge bass pedal",
            "Palette color": "Bridge D-pedal (dominant-ish pull)",
        },
        "section_roots_midpoint_pcs": section_roots,
        "progression": SECTION_PALETTES,
        "seed": SEED,
    }
    with open(os.path.join(ANALYSIS_DIR, "summary.json"), "w") as f:
        json.dump(summary, f, indent=2)
    return summary


if __name__ == "__main__":
    print(f"=== {PROJ_NAME} (extension of 220-funk-contour-groove) ===")
    write_summary()
    print("=== Phase 1: raw abstract draft ===")
    generate_phase1_raw()
    print("=== Phase 2: rules composition (dual-version) ===")
    generate_phase2_composition()
    print("Done!")