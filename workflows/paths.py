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
    "HC-003": ("L2", False),  # Makam Seyir
    "HC-010": ("L2", False),  # Fanfare
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

# Diatonic chord shapes: degree -> (root_interval, quality)
CHORD_SHAPES = {
    "I": (0, "maj"), "ii": (2, "min"), "iii": (4, "min"),
    "IV": (5, "maj"), "V": (7, "maj"), "vi": (9, "min"), "vii": (11, "dim"),
}
# Major scale pitch-class offsets (for a C root, offset list per degree)
MAJOR_DEGREES = ["I", "ii", "iii", "IV", "V", "vi", "vii"]

KEY_OFFSET = {
    "C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4,
    "F": 5, "F#": 6, "Gb": 6, "G": 7, "G#": 8, "Ab": 8, "A": 9,
    "A#": 10, "Bb": 10, "B": 11,
    # relative minor keys
    "Cm": -3, "C#m": -2, "Dm": -1, "D#m": 0, "Em": 1, "Fm": 2,
    "F#m": 3, "Gm": 4, "G#m": 5, "Am": 6, "A#m": 7, "Bm": 8,
}

# Common progressions by style flavor (degree lists)
PROGRESSIONS = {
    "pop": ["I", "V", "vi", "IV"],
    "pop-ballad": ["I", "vi", "IV", "V"],
    "andalucian": ["i", "VII", "VI", "V"],  # flamenco flavor
    "doo-wop": ["I", "vi", "IV", "V"],
    "minor-aeolian": ["i", "VI", "III", "VII"],
    "major-asc": ["I", "III", "IV", "V"],
    "blues-rock": ["I", "IV", "I", "V"],
}

# Chord quality -> semitone offsets from root
QUALITY_INTERVALS = {
    "maj": (0, 4, 7),
    "min": (0, 3, 7),
    "dim": (0, 3, 6),
}


def _chord_tones(degree: str, root_midi: int) -> List[int]:
    """Pitch classes of a chord built on `root_midi` for a scale degree.

    Handles both "I"/"vi" (major scale spelling) and "i"/"VII" (natural
    minor spelling, flamenco-style) by case: uppercase roots follow the
    major scale offsets, lowercase follow the natural minor scale.
    """
    qual = "maj" if degree == degree.upper() else "min"
    # map the degree letter to a scale offset
    letter = degree.upper()
    if letter in ("I", "II", "III", "IV", "V", "VI", "VII"):
        idx = MAJOR_DEGREES.index(letter)
        # natural-minor spelling: b3, b6, b7 vs major
        minor_offsets = [0, 2, 3, 5, 7, 8, 10]
        if degree != degree.upper():
            scale_off = minor_offsets[idx]
        else:
            scale_off = [0, 2, 4, 5, 7, 9, 11][idx]
    else:
        scale_off = 0
    root = root_midi + scale_off
    intervals = QUALITY_INTERVALS[qual]
    return [root + i for i in intervals]


def _euclidean_positions(onsets: int, steps: int) -> List[int]:
    """Bjorklund-style even spacing: list of step indexes that carry onsets."""
    if onsets <= 0 or steps <= 0 or onsets > steps:
        raise ValueError(f"bad euclidean ({onsets}/{steps})")
    return [i * steps // onsets for i in range(onsets)]


def build_framework(style="pop", key="C", bpm=120, form=None, num_bars=None,
                    seed=None) -> UnitMatrixComposer:
    """Build the middle-out framework (Path C, steps 1–2 of the chain).

    Creates the UnitMatrixComposer with pop form sections (L4 skeleton)
    and the standard pop voice stack, ready for cell filling. The
    framework is deterministic given (style, key, bpm) — the L3 anchor
    (groove) and L2/L1 material are added in later chain steps.
    """
    import random
    rng = random.Random(seed)

    form = form or POP_FORM
    composer = UnitMatrixComposer(bpm=bpm, ticks_per_beat=480, beats_per_bar=4)

    # --- voices (pop default stack) ---
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
    off = KEY_OFFSET.get(key, 0)
    # per-bar root sequence
    total_bars = sum(bars_per)
    deg_seq = [progression[i % len(progression)] for i in range(total_bars)]
    # map each degree to a midi root (bass octave 36 + key offset + degree offset)
    roots_per_bar = []
    for deg in deg_seq:
        letter = deg.upper()
        idx = MAJOR_DEGREES.index(letter) if letter in MAJOR_DEGREES else 0
        major_offsets = [0, 2, 4, 5, 7, 9, 11]
        scale_off = major_offsets[idx]
        if deg != deg.upper():
            # natural-minor spelling: b3, b6, b7
            minor_offsets = [0, 2, 3, 5, 7, 8, 10]
            scale_off = minor_offsets[idx]
        roots_per_bar.append(36 + off + scale_off)
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
    out_dir = Path(out_dir or f"/opt/data/projects/Styles/{style.title()}/path-C")
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
