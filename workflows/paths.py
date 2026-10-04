# -*- coding: utf-8 -*-
"""Composition Path Layer — SCALE registry + middle-out (Path C) orchestrator.

Build order step 1 of the PATH_LAYER_PLAN (projects/Research/CompositionMethods):

    workflows/paths.py   # SCALE registry (L1–L4 per method) + Path C orchestrator

The abstraction scale comes from the methods DB's Memory Depth column, split
into 4 levels:

    L4 MACRO — form, sections, tonal plans      (output: skeleton)
    L3 MESO  — phrase, motif, loop, groove      (output: cells per section)
    L2 VOICE — one line at a time, contour      (output: melodic lines)
    L1 MICRO — one note -> next note            (output: transitions)

Sequence paths (directions through the scale):

    Path A TOP-DOWN    L4 -> L3 -> L2 -> L1   (skeleton first)
    Path B BOTTOM-UP   L1/L2 -> L3 -> L4      (structure induced)
    Path C MIDDLE-OUT  L3 anchor -> L4 form around it, L2/L1 on top
    Path D RANDOM      candidates + selection (search, wraps A/B/C)

This module implements Path C (middle-out) — the empirically strongest
default for style-faithful work (9/17 human methods are middle-out) and the
first deliverable of the build order. Paths A/B/D come in later steps.

Guarantees:
- Uses ONLY the musicom engine (UnitMatrixComposer + generators/) — no raw
  mido authoring, no ad-hoc numpy event arrays (AGENTS.md hard rule).
- Zero-drift gate: composer.validate() MUST pass before export.
- Seeded throughout: same (style, key, bpm, seed) -> byte-identical MIDI.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# --- engine imports (editable install; no sys.path hacks) -------------------
from structures import MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer
from workflows.provenance import write_provenance

# ============================================================================
# 1. SCALE registry — method ID -> (level, impl status)
# ============================================================================
# Level is the method's PRIMARY abstraction level (plan §1).
# `impl` mirrors generator_registry implementation status so the selector
# (step 2) can filter spec-only methods without touching the DB.

SCALE = {
    # --- Abstract layer (subset network, LAYER_ARCHITECTURE.md) ---
    # Registered at L4/L3: they produce structural plan (subset sequences,
    # tension targets), not note material. Level only matters for selector
    # memory_depth routing; abstract methods are layer-filtered separately.
    "ABS-001": ("L4", True),   # Tension Curve Planner
    "ABS-002": ("L4", True),   # Subset Walker
    "ABS-003": ("L3", True),   # Z-Variation
    "ABS-004": ("L3", True),   # Parsimonious Voice Leading
    "ABS-005": ("L3", True),   # Complement Contrast
    # --- L4 MACRO ---
    "001": ("L4", True),   # Skeleton-First Refinement
    "006": ("L4", False),  # Cadence & Closure Mapping (spec)
    "007": ("L4", False),  # Narrative Arc Register Planning (spec)
    "010": ("L4", True),   # Hierarchical Diffusion (markov base)
    "017": ("L4", False),  # Cascaded Diffusion Hierarchies (spec)
    "034": ("L4", False),  # PCFG Recursion (spec)
    "044": ("L4", False),  # Persistent Homology (spec)
    "049": ("L4", False),  # IFS Fractal Generation (spec)
    "066": ("L4", False),  # GTTM-HC (spec)
    "HC-001": ("L4", False),  # Partimento Schemata
    "HC-006": ("L4", False),  # Big Band Shout Chorus
    "HC-011": ("L4", False),  # Orchestration
    "HC-016": ("L4", False),  # Drumband Showcraft
    # --- L3 MESO ---
    "003": ("L3", True),   # Genetic Genome Selection (evolves motifs/anchors, plan §3.3/Ex D)
    "004": ("L3", False),  # Prosodic Coupling
    "005": ("L3", False),  # Prosodic Syntax
    "008": ("L3", False),  # Call-Response Allocation
    "009": ("L3", False),  # Rhyme Density Control
    "012": ("L3", True),   # Euclidean Groove Locking
    "015": ("L3", False),  # Ostinato Constraint
    "016": ("L3", False),  # Groove-Locked Patterns
    "018": ("L3", True),   # Schillinger Resultants
    "021": ("L3", False),  # Cellular Automata
    "025": ("L3", False),  # Xenakis Sieves
    "026": ("L3", False),  # DPSM — spec only
    "032": ("L3", False),  # Isorhythm Talea-Color
    "033": ("L3", False),  # Wave Function Collapse
    "056": ("L3", False),  # Species Counterpoint
    "064": ("L3", False),  # MRFCC
    "069": ("L3", False),  # Christoffel Words
    "HC-002": ("L3", False),  # Gamelan Kotekan
    "HC-004": ("L3", False),  # Raga-Tala
    "HC-005": ("L3", False),  # Ewe Cross-Rhythm
    "HC-008": ("L3", False),  # Minimalist Process
    "HC-009": ("L3", False),  # Motivic Development
    "HC-012": ("L3", True),   # Flamenco Compas (chord_degrees)
    "HC-013": ("L3", False),  # Georgian Polyphony
    "HC-014": ("L3", False),  # Pygmy Hocket
    "HC-015": ("L3", False),  # Sacred Harp
    "HC-017": ("L3", False),  # Sanjo Jangdan
    # --- L2 VOICE/CONTOUR ---
    "013": ("L2", False),  # Inversion/Retrograde
    "014": ("L2", False),  # Negative Harmony
    "020": ("L2", False),  # Sound-Mass Trajectory
    "023": ("L2", True),   # Tendency Masking
    "029": ("L2", False),  # Continuous Portamento Glide
    "031": ("L2", False),  # Boids Flocking
    "036": ("L2", False),  # Abelian Sandpile
    "037": ("L2", False),  # FitzHugh-Nagumo Spiking
    "038": ("L2", False),  # Kuramoto Phase Sync
    "040": ("L2", True),   # Perlin Noise (pitchpattern)
    "043": ("L2", False),  # Strange Attractors
    "048": ("L2", False),  # Reflected Brownian Motion — spec only
    "051": ("L2", False),  # Spectral Graph Laplacian
    "053": ("L2", False),  # Levy Flight
    "059": ("L2", False),  # ESN Reservoir
    "061": ("L2", False),  # Gaussian Process
    "068": ("L2", False),  # CME-SSA
    "070": ("L2", False),  # Coupled Map Lattice
    "071": ("L4", False),  # Hopfield Associative Memory (HAM-C) (spec)
    "073": ("L4", False),  # Harmony Search Improvisational (HSIC) (spec)
    "074": ("L4", False),  # Restricted Boltzmann Machine (RBM-C) (spec)
    "075": ("L4", False),  # Self-Organizing Map (SOM-C) (spec)
    "072": ("L4", False),  # Normalizing Flow Composition (NFC) (spec)
    "076": ("L3", False),  # Thue-Morse Automatic Sequence (PTM-ASC) (spec)
    "077": ("L3", False),  # De Bruijn Universal Cycle (DBUC) (spec)
    "078": ("L3", False),  # Ising Model Equilibrium (IMEC) (spec)
    # REGISTERED 2026-09-13 (weekly prose->code promotion, reports 079..085)
    "079": ("L3", True),   # Tintinnabuli (TINC) — generators/tintinnabuli.py (IMPLEMENTED)
    "080": ("L3", False),  # Messiaen Modes of Limited Transposition (MMLT) (spec)
    "081": ("L3", False),  # Narmour Implication-Realization Melodic (NIRMC) (spec)
    "082": ("L3", False),  # Random Boolean Network Criticality (RBNCC) (spec)
    "083": ("L4", False),  # Aperiodic Quasicrystal Tiling (QTSC) (spec)
    "084": ("L4", False),  # Zipf-Mandelbrot Rank-Frequency (ZMRC) (spec)
    "085": ("L4", False),  # Non-negative Matrix Factorization (NMF-C) (spec)
    # REGISTERED 2026-09-20 (weekly prose->code promotion, reports 086..091)
    "086": ("L3", False),  # Hidden Markov Model Latent-State Composition (HMM-C) (spec)
    "087": ("L3", False),  # Multiple Viewpoint Systems Composition (MVS-C) (spec)
    "088": ("L4", False),  # Voronoi Tessellation Event Partitioning (VTEP) (spec)
    "089": ("L4", False),  # Change-Ringing Combinatorial Method (CRCM) (spec)
    "090": ("L4", False),  # Golomb Ruler Distinct-Difference Composition (GRDC) (spec)
    "091": ("L4", False),  # Coxeter-Conway Frieze Pattern Composition (CCFPC) (spec)
    "HC-003": ("L2", False),  # Makam Seyir
    "HC-010": ("L2", False),  # Fanfare
    "HC-018": ("L3", False),  # Clave-Guided Montuno (spec)
    "HC-019": ("L3", False),  # Aksak Horo (spec)
    "HC-020": ("L4", False),  # Tension-Release Drop Arrangement (spec)
    "HC-021": ("L3", False),  # Species Counterpoint (spec)
    "HC-022": ("L3", False),  # Twelve-Bar Blues AAB (spec)
    "HC-023": ("L3", False),  # Spectral Listening Orchestration (spec)
    "HC-024": ("L4", False),  # Graphic Score Indeterminate (spec)
    "HC-025": ("L3", False),  # Kora Griot Ostinato-Song (spec)
    "HC-026": ("L3", False),  # Pibroch Theme-Variation (spec)
    "HC-027": ("L3", False),  # Tuvan Overtone Throat Singing (spec)
    # REGISTERED 2026-09-13 (weekly promotion, reports HC-028..HC-034)
    "HC-028": ("L3", False),  # Jazz Chord-Scale Improv & Comping (spec)
    "HC-029": ("L4", False),  # Shakuhachi Honkyoku Breath-Arch (spec)
    "HC-030": ("L4", False),  # Argentine Tango Arrangement Arc (spec)
    "HC-031": ("L4", False),  # Persian Radif Dastgah-Gusheh Ordering (spec)
    "HC-032": ("L4", False),  # Guqin Jianzipu Dapu Arch Reconstruction (spec)
    "HC-033": ("L3", False),  # Inuit Katajjaq Duet Rounds (spec)
    "HC-034": ("L3", False),  # Choro Rondo & Baixaria (spec)
    # REGISTERED 2026-09-20 (weekly promotion, reports HC-035..HC-040)
    "HC-035": ("L3", False),  # Shona Mbira Kushaura/Kutsinhira Interlocking (spec)
    "HC-036": ("L4", False),  # Norwegian Hardanger Fiddle Slått Craft (spec)
    "HC-037": ("L4", False),  # Klezmer Ornament-Led Ensemble Craft (spec)
    "HC-038": ("L4", False),  # Sonata Form Process (spec)
    "HC-039": ("L3", False),  # Irish Traditional Dance Tune Setting & Ornamentation (spec)
    "HC-040": ("L4", False),  # Andalusi Nūbah Suite Architecture & Mīzān Metric Acceleration (spec)
    # REGISTERED 2026-09-27 (weekly prose->code promotion, reports 093..097, HC-041..047)
    "093": ("L3", False),  # Percolation Process Network Criticality (PPNC) (spec)
    "094": ("L3", False),  # Apollonian Circle Packing Composition (ACPC) (spec)
    "ABS-095": ("L3", True),  # Contour Theory Composition (CTC) — rules.subset_network (abstract)
    "096": ("L3", False),  # Dynamic Time Warping Composition (DTWC) (spec)
    "097": ("L4", False),  # Maximum Entropy Composition (MaxEnt-C) (spec)
    "HC-041": ("L4", False),  # Gagaku Kangen Orchestral Stratification & Jo-Ha-Kyū (spec)
    "HC-042": ("L3", False),  # Andean Sikuri Hocket & Communal Tropa Craft (Ira-Arka) (spec)
    "HC-043": ("L3", False),  # Cante Alentejano Choral Stratification & Parallel-Third Descant (spec)
    "HC-044": ("L3", False),  # Zulu Isicathamiya/Mbube A Cappella Choral Craft (spec)
    "HC-045": ("L3", False),  # Qañat Kiñit Modal System — Azmari Wax-and-Gold (spec)
    "HC-046": ("L4", False),  # Javanese Gamelan Gending Composition — Colotomic & Pathet (spec)
    "HC-047": ("L3", False),  # Barbershop Quartet Voicing & Overtone Ring Craft (spec)
    # REGISTERED 2026-10-04 (weekly prose->code promotion, reports 098..104, HC-048..054)
    "098": ("L4", False),   # Multi-Objective Evolutionary Pareto Composition (MOEPC) (spec)
    "ABS-099": ("L4", True),  # Self-Similarity Matrix Composition (SSMC) — rules.subset_network (abstract)
    "100": ("L4", False),   # Active Inference Composition (AIFC) (spec)
    "101": ("L4", False),   # Flow Matching Composition (FMC) (spec)
    "102": ("L4", False),   # Cross-Entropy Method Composition (CEMC) (spec)
    "103": ("L4", False),   # Graph Neural Network Composition (GNNC) (spec)
    "ABS-104": ("L4", True),  # Parsimonious Subset Sequence Composition (PSSC) — rules.subset_network (abstract)
    "HC-048": ("L3", False),  # Cuban Rumba Guaguancó/Yambú/Columbia Drum-Dance-Song (spec)
    "HC-049": ("L4", False),  # Kecak Ramayana Monkey Chant (spec)
    "HC-050": ("L3", False),  # Yoruba Dùndún Talking-Drum Ensemble (spec)
    "HC-051": ("L4", False),  # Ragtime Stride Piano Composition (spec)
    "HC-052": ("L3", False),  # Reggae Riddim Construction (spec)
    "HC-053": ("L3", False),  # Bossa Nova Batida & Fraseado (spec)
    "HC-054": ("L4", False),  # Bluegrass Ensemble Arrangement (spec)
    # --- L1 MICRO ---
    "002": ("L1", True),   # Markov Transitions
    "011": ("L1", False),  # Voice-Leading Graph Search
    "022": ("L1", False),  # Markov-Constraint Wavefront
    "045": ("L1", False),  # Hawkes Self-Exciting
    "050": ("L1", False),  # Optimal Transport Voice Leading
    "052": ("L1", False),  # Quantum Walk
    "065": ("L1", False),  # TTSMC Row Forms
    "067": ("L1", False),  # Factor Oracle
    "HC-007": ("L1", False),  # Lyric-Melody Prosody
}

LEVELS = ("L4", "L3", "L2", "L1")

# Path C uses this chain (plan Example A / recommendation matrix):
#   L3 anchor (groove) -> L4 form around it -> L2 lines on top -> L1 micro-fills
# Each entry: (scale_label, method_id, description)
MIDDLE_OUT_CHAIN = [
    ("L3", "012", "Euclidean Groove Locking — anchor rhythm"),
    ("L3", "018", "Schillinger Resultants — groove variation"),
    ("L4", "001", "Skeleton-First — form around the anchor"),
    ("L2", "023", "Tendency Masking — melodic line above"),
    ("L1", "002", "Markov Transitions — micro-fill transitions"),
]


def methods_by_scale(level: str) -> List[str]:
    """Method IDs at one scale level (plan §1 tables, auto-generated)."""
    return sorted(mid for mid, (lv, _) in SCALE.items() if lv == level)


def scale_of(method_id: str) -> Optional[str]:
    """Primary abstraction level of a method ID, or None if unknown."""
    entry = SCALE.get(method_id)
    return entry[0] if entry else None


def impl_status(method_id: str) -> bool:
    """True if the method has working shared code (registry-aware routing)."""
    entry = SCALE.get(method_id)
    return entry[1] if entry else False


def scale_table() -> str:
    """Markdown table of the SCALE registry (for docs/)."""
    rows = ["| Method ID | Level | Implemented |", "|---|---|---|"]
    for mid in sorted(SCALE):
        lv, impl = SCALE[mid]
        rows.append(f"| {mid} | {lv} | {'yes' if impl else 'spec-only'} |")
    return "\n".join(rows)


# ============================================================================
# Registration helper — one call, three places (LAYER_ARCHITECTURE.md)
# ============================================================================
# A method is registered in: SCALE (level + impl), GENERATOR_REGISTRY (code
# resolution). Editing all three by hand drifts (ABS-* landed in two, missed
# the prose DB). Use register_method() so the machine-readable stores stay in
# sync; the long-form methods_db.md prose stays manual (documented there).

def register_method(method_id: str, level: str, registry_mod_path: str,
                    description: str) -> None:
    """Register a method in SCALE + generator_registry in one call.

    Args:
        method_id: e.g. "ABS-006" or "HC-023".
        level: SCALE level, one of LEVELS ("L1".."L4").
        registry_mod_path: import path for the implementation module (or None
            for spec-only — registers in SCALE only, not routable).
        description: short description for the registry.
    """
    if level not in LEVELS:
        raise ValueError(f"level must be one of {LEVELS}, got {level!r}")
    SCALE[method_id] = (level, registry_mod_path is not None)
    if registry_mod_path is not None:
        from generators.generator_registry import GENERATOR_REGISTRY
        GENERATOR_REGISTRY[method_id] = (registry_mod_path, None, description)


# ============================================================================
# 2. Middle-out framework builder (Path C)
# ============================================================================
# "Fix an invariant mid-level spine; structure grows around it, variation
# grows on top." 9/17 human methods are middle-out (Ewe timeline, compas,
# tala, jangdan, ...). This is the empirically strongest default for
# style-faithful composition (plan §2 Path C).

# Standard pop form (bars per section) — intro/verse/chorus/bridge/outro
POP_FORM = [
    ("Intro", 4),
    ("Verse", 8),
    ("Chorus", 8),
    ("Bridge", 4),
    ("Outro", 4),
]

# --- harmony tables (canonical source: rules/harmony.py) -------------------
from rules.harmony import (  # noqa: E402  (re-exported for backward compat)
    CHORD_SHAPES, MAJOR_DEGREES, KEY_OFFSET, PROGRESSIONS, QUALITY_INTERVALS,
    MODE_OFFSETS, degree_offset, infer_mode, parse_degree, tonic_offset,
    chord_tones as _harmony_chord_tones,
    progression_roots as _harmony_progression_roots,
)


def _chord_tones(degree: str, root_midi: int) -> List[int]:
    """Pitch classes of a chord built on `root_midi` for a scale degree."""
    return _harmony_chord_tones(degree, root_midi)


def progression_roots(progression, total_bars: int, key: str,
                      harmonic_rhythm: int = 1, mode=None,
                      base_octave: int = 36) -> List[int]:
    """Per-bar root MIDI pitches for a progression (mode-aware).

    Single canonical implementation (rules/harmony.progression_roots),
    re-exported here so workflow modules don't re-derive scale offsets.
    """
    return _harmony_progression_roots(
        progression, total_bars, key, harmonic_rhythm=harmonic_rhythm,
        mode=mode, base_octave=base_octave)


def _euclidean_positions(onsets: int, steps: int) -> List[int]:
    """Bjorklund-style even spacing: list of step indexes that carry onsets."""
    if onsets <= 0 or steps <= 0 or onsets > steps:
        raise ValueError(f"bad euclidean ({onsets}/{steps})")
    return [i * steps // onsets for i in range(onsets)]


def build_framework(style="pop", key="C", bpm=120, form=None, num_bars=None,
                    seed=None, voices=None) -> UnitMatrixComposer:
    """Build the middle-out framework (Path C, steps 1–2 of the chain).

    Creates the UnitMatrixComposer with pop form sections (L4 skeleton)
    and a voice stack, ready for cell filling. The framework is
    deterministic given (style, key, bpm) — the L3 anchor (groove) and
    L2/L1 material are added in later chain steps.

    voices: optional list of (voice_name, instrument_name) overrides. When
    omitted, the standard pop stack is used. Instrument names resolve
    through the instrument registry (see workflows.musicom_workflow
    ._resolve_instrument), so style-appropriate palettes can be swapped in
    without forking the framework.
    """
    import random
    rng = random.Random(seed)

    form = form or POP_FORM
    composer = UnitMatrixComposer(bpm=bpm, ticks_per_beat=480, beats_per_bar=4)

    # --- voices (pop default stack, or a caller-supplied palette) ---
    if not voices:
        voices = [
            ("Lead", "Flute"),
            ("Pad", "Piano"),
            ("Bass", "Double Bass"),
            ("Arp", "Clarinet"),
            ("Drums", "Drum Kit"),
        ]
    from workflows.musicom_workflow import _resolve_instrument
    composer.create_matrix(num_voices=len(voices), num_sections=len(form))
    for vname, inst in voices:
        label, prog, ch = _resolve_instrument(vname, inst)
        composer.add_voice(label, program=prog, channel=ch)

    # --- sections (L4: form around the anchor) ---
    for sname, nbars in form:
        composer.add_section(sname, bars=nbars)

    return composer


# ============================================================================
# 3. Cell-filling builders (each returns a MusicUnit for one voice/section)
# ============================================================================

def _unit(events, section_len):
    """Wrap events with a terminal silent landmark at section_len (zero-drift)."""
    from structures import MusicUnit
    unit = MusicUnit()
    for ev in events:
        unit.add_event(ev)
    unit.add_event(MusicEvent(0, 0, section_len, section_len))
    return unit


def fill_anchor(composer, rng, roots_per_bar, section_names, bars_per,
                BAR=1920):
    """L3 anchor: groove-locked bass from the progression roots.

    The anchor is the invariant mid-level spine — the bass plays the
    progression roots in a Euclidean groove pattern (method 012). The
    accent density varies 3/4/4 across bars (Schillinger-style resultant
    variation, method 018). Everything else orbits this.
    """
    bass_evs = []
    bar = 0
    for si, sname in enumerate(section_names):
        nbars = bars_per[si]
        section_len = nbars * BAR
        for b in range(nbars):
            root = roots_per_bar[bar]
            onsets = 3 + (b % 2)  # 3 or 4 accents per bar (even spacing)
            pos = _euclidean_positions(onsets, 4)
            for p in pos:
                start = b * BAR + p * 480
                bass_evs.append(MusicEvent(root, 95, start, start + 400))
            bar += 1
        composer.fill_voice_section("Bass", sname, _unit(bass_evs, section_len))
        bass_evs = []


def fill_pad(composer, roots, section_names, bars_per, BAR=1920):
    """Pad: sustained chord per section from the progression."""
    for si, sname in enumerate(section_names):
        nbars = bars_per[si]
        section_len = nbars * BAR
        root = roots[si * max(1, len(bars_per) // 5)] if roots else 48
        # pad chord: root triad
        tones = [root, root + 4, root + 7]
        pad_evs = [MusicEvent(t, 60, 0, section_len) for t in tones]
        composer.fill_voice_section("Pad", sname, _unit(pad_evs, section_len))


def fill_lead(composer, rng, roots, section_names, bars_per, key="C", BAR=1920):
    """L2 line: tendency-masking bounded melodic contour over the anchor.

    A seeded walk over the chord tones with a tendency toward the nearest
    chord tone (the L2 layer grows on top of the L3 anchor).
    """
    for si, sname in enumerate(section_names):
        nbars = bars_per[si]
        section_len = nbars * BAR
        root = roots[si] if si < len(roots) else 48
        tones = [root + 12, root + 16, root + 19]
        # seed a bounded walk
        cur = tones[0]
        lead_evs = []
        step = 0
        t = 0
        while t < section_len - 480:
            # tendency: pull toward nearest chord tone
            candidates = tones + [tones[0] + 12]
            nearest = min(candidates, key=lambda p: abs(p - cur))
            if rng.random() < 0.6:
                nxt = nearest
            else:
                nxt = cur + rng.choice([-2, -1, 1, 2])
            nxt = max(tones[0] - 5, min(tones[-1] + 12, nxt))
            lead_evs.append(MusicEvent(nxt, 90, t, t + 440))
            cur = nxt
            t += 480
            step += 1
        composer.fill_voice_section("Lead", sname, _unit(lead_evs, section_len))


def fill_arp(composer, rng, roots, section_names, bars_per, BAR=1920):
    """Arp: 16th-note arpeggio of the chord tones (L1 micro texture)."""
    for si, sname in enumerate(section_names):
        nbars = bars_per[si]
        section_len = nbars * BAR
        root = roots[si] if si < len(roots) else 48
        tones = [root + 12, root + 16, root + 19]
        arp_evs = []
        for b in range(nbars * 4):
            note = tones[b % 3]
            arp_evs.append(MusicEvent(note, 70, b * 480, b * 480 + 240))
        composer.fill_voice_section("Arp", sname, _unit(arp_evs, section_len))


def fill_drums(composer, section_names, bars_per, BAR=1920):
    """Drums: backbeat grid — kick 1&3, snare 2&4, hats 8ths (the grid)."""
    for si, sname in enumerate(section_names):
        nbars = bars_per[si]
        section_len = nbars * BAR
        drum_evs = []
        for b in range(nbars):
            bar_start = b * BAR
            drum_evs.append(MusicEvent(36, 100, bar_start, bar_start + 120))
            drum_evs.append(MusicEvent(38, 90, bar_start + 960, bar_start + 1080))
            for h in range(8):
                drum_evs.append(MusicEvent(42, 60, bar_start + h * 240,
                                           bar_start + h * 240 + 120))
        composer.fill_voice_section("Drums", sname, _unit(drum_evs, section_len))


# ============================================================================
# 4. Path C orchestrator — middle-out compose
# ============================================================================

@dataclass
class PathResult:
    """Result of a path composition run."""
    midi_path: str
    provenance_path: str
    path: str                 # "C"
    chain: List[Dict]         # [(scale, method_id, desc, status)]
    seed: int
    bpm: int
    key: str
    style: str


def compose_middle_out(style="pop", key="C", bpm=120, progression=None,
                       form=None, seed=None, out_dir=None, method=None):
    """Path C: middle-out composition (anchor -> form -> lines -> fills).

    Chain (plan §2 Path C, Example A):
      1. L3 anchor:  012 Euclidean Groove Locking (bass) + backbeat grid (drums)
      2. L3 variation: 018 Schillinger resultants (accent density 3/4/5)
      3. L4 form:    001 Skeleton-First (intro/verse/chorus/bridge/outro)
      4. L2 line:    023 Tendency Masking (lead contour over the anchor)
      5. L1 micro:   002 Markov-ish bounded walk (arp 16ths + lead fills)

    The anchor is fixed first (the invariant spine), the form grows around
    it, and the variation grows on top. Deterministic given seed.

    Returns PathResult with validated zero-drift MIDI + provenance.
    """
    import random
    rng = random.Random(seed)
    seed = seed if seed is not None else rng.randint(0, 2**31)

    # ---- L4 form (skeleton) ----
    form = form or POP_FORM
    section_names = [s[0] for s in form]
    bars_per = [s[1] for s in form]

    # ---- L3 anchor: progression = the invariant harmony spine ----
    progression = progression or PROGRESSIONS.get(style, PROGRESSIONS["pop"])
    # per-bar root sequence (mode-aware; canonical helper)
    total_bars = sum(bars_per)
    roots_per_bar = progression_roots(progression, total_bars, key)
    # per-section roots (first bar of the section = section root)
    section_roots = []
    bar_cursor = 0
    for nbars in bars_per:
        section_roots.append(roots_per_bar[bar_cursor])
        bar_cursor += nbars

    # ---- build the composer + fill every cell ----
    composer = build_framework(style=style, key=key, bpm=bpm, form=form, seed=seed)
    fill_drums(composer, section_names, bars_per)
    fill_anchor(composer, rng, roots_per_bar, section_names, bars_per)
    fill_pad(composer, section_roots, section_names, bars_per)
    fill_lead(composer, rng, section_roots, section_names, bars_per, key=key)
    fill_arp(composer, rng, section_roots, section_names, bars_per)

    # ---- zero-drift gate ----
    ok, msg = composer.validate()
    if not ok:
        raise RuntimeError(f"validate() failed: {msg}")

    # ---- export ----
    out_dir = Path(out_dir or f"outputs/{style.title()}/path-C")
    midi_dir = out_dir / "MIDI"
    midi_dir.mkdir(parents=True, exist_ok=True)
    midi_path = midi_dir / f"{style}-C-{seed}.mid"
    composer.to_midi(str(midi_path))

    chain = [
        {"scale": sc, "method": mid, "desc": desc,
         "impl": impl_status(mid)}
        for sc, mid, desc in MIDDLE_OUT_CHAIN
    ]
    prov = write_provenance(
        artifact_path=str(midi_path),
        classification="ai-assisted",
        generator=f"workflows.paths.compose_middle_out(style={style}, seed={seed})",
        sources=[f"style:{style}", f"key:{key}", f"progression:{progression}",
                 "path:C", "chain:012,018,001,023,002"],
        parameters={"seed": seed, "bpm": bpm, "form": form,
                    "progression": progression, "path": "C",
                    "chain": MIDDLE_OUT_CHAIN},
    )
    return PathResult(
        midi_path=str(midi_path),
        provenance_path=str(prov) if prov else "",
        path="C",
        chain=chain,
        seed=seed,
        bpm=bpm,
        key=key,
        style=style,
    )


if __name__ == "__main__":
    print("=== SCALE REGISTRY (methods by level) ===")
    for lv in LEVELS:
        print(f"{lv}: {methods_by_scale(lv)}")
    print()
    print("=== Path C demo ===")
    r = compose_middle_out(style="pop", key="C", bpm=120, seed=42)
    print(f"MIDI: {r.midi_path}")
    print(f"seed: {r.seed}")
    for step in r.chain:
        print(f"  {step['scale']} {step['method']}: {step['desc']} "
              f"({'impl' if step['impl'] else 'spec-only'})")
    print(f"provenance: {r.provenance_path}")
