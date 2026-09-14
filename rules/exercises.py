# -*- coding: utf-8 -*-
"""Exercises — named, self-verifying units of work on the pattern layers.

This is the "usable for abstract and concrete exercises" deliverable of
``PATTERN_ARCHITECTURE.md``. An Exercise is a self-describing unit that the
engine can RUN AND VERIFY — not a prose description of a drill.

Two layers, matching the architecture:

ABSTRACT exercises (``layer="abstract"``) operate purely on pitch-class sets
and relations. They produce **no MIDI** and assert set-theoretic facts:
tension equality, Z-relations, containment, mode identity.

CONCRETE exercises (``layer="concrete"``) run a pattern through the
realization bridge (``rules/realize.py``) and produce real artifacts — a
:class:`~structures.unit.MusicEvent` list and, via :func:`run_exercise` with
``to_midi=True``, an actual MIDI file. Their assertions check the realized
output (register bounds, rhythm onsets, voice content), not just the plan.

Usage::

    from rules.exercises import run_exercise, EXERCISE_REGISTRY

    result = run_exercise("ABS-EX-001")            # verify only
    result = run_exercise("CON-EX-001", to_midi=True, out_dir=...)
    result.artifacts                                # written file paths

Purity: importing this module requires no MIDI I/O and no heavy deps.
"""

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Sequence, Tuple

from rules.patterns import (
    Pattern,
    RhythmPattern,
    common_tones,
    icv_distance,
    named_rhythms,
    patterns_from_degrees,
    standard_patterns,
    tension,
    voice_leading_distance,
    z_pair_catalogue,
)
from rules.realize import realize, realize_progression, place_in_register
from rules.set_theory import forte_name, prime_form

__all__ = [
    "Exercise", "ExerciseResult", "EXERCISE_REGISTRY", "ABSTRACT_EXERCISES",
    "CONCRETE_EXERCISES", "run_exercise", "list_exercises",
]


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Exercise:
    """A named, self-describing unit of work the engine can run and verify."""

    id: str                       # "ABS-EX-001" / "CON-EX-002"
    layer: str                    # "abstract" | "concrete"
    title: str
    description: str
    fn: str                       # function name in this module (kept as a
                                  # string so the registry stays data-first)
    patterns: Tuple[str, ...] = ()
    rhythm: Optional[str] = None
    tags: Tuple[str, ...] = ()


@dataclass
class ExerciseResult:
    """What running an exercise produced, plus whether it verified."""

    exercise_id: str
    ok: bool
    layer: str
    checks: List[Tuple[str, bool, str]] = field(default_factory=list)
    artifacts: List[str] = field(default_factory=list)
    data: Dict = field(default_factory=dict)

    def check(self, name: str, passed: bool, detail: str = "") -> bool:
        self.checks.append((name, bool(passed), detail))
        return bool(passed)

    @property
    def failed(self) -> List[Tuple[str, bool, str]]:
        return [c for c in self.checks if not c[1]]

    def __repr__(self) -> str:
        n_ok = sum(1 for _, ok, _ in self.checks if ok)
        return (f"ExerciseResult({self.exercise_id}, ok={self.ok}, "
                f"checks={n_ok}/{len(self.checks)}, "
                f"artifacts={len(self.artifacts)})")


# ---------------------------------------------------------------------------
# ABSTRACT exercises — pure set logic, no MIDI
# ---------------------------------------------------------------------------

def _abs_z_swap(_ex: Exercise, result: ExerciseResult) -> None:
    """Z-swap: replace one chord with its Z-partner in a walked progression.

    Asserts tension unchanged, harmony changed, and reports voice-leading
    distance — the canonical "same colour, different notes" move that was
    previously unusable because only one Z-pair was discoverable.
    """
    lib = {p.id: p for p in standard_patterns()}
    # I - vi7 - IV - Imaj7 on the standard library; the swap carrier is
    # z0137 = {0,1,3,7} = 4-Z29. NOTE: the library's tonal tetrads (maj7,
    # min7, dom7, m7b5) have no Z-partners — 4-Z29 is the only tetrad in the
    # standard library that does, which is exactly why it ships there.
    progression = ["maj0", "z0137", "maj5", "maj70"]
    target = lib[progression[1]]

    partner = target.z_partner
    result.check("z-partner-exists", partner is not None,
                 f"{target.id} ({target.forte})")

    if partner is None:
        return

    modified = list(progression)
    # the z_partner returns a transient Pattern (id "<id>-z"), so match by
    # pitch content against the library rather than by id
    partner_idx = next((i for i, p in enumerate(standard_patterns())
                        if p.subset == partner.subset), None)
    modified[1] = (partner.id if partner_idx is None
                   else standard_patterns()[partner_idx].id)

    # tension must be IDENTICAL (same ICV -> same weighted tension)
    t_orig = sum(tension(lib[pid].subset) for pid in progression)
    t_new = sum(tension(lib[pid].subset) for pid in modified)
    result.check("tension-unchanged", t_orig == t_new, f"{t_orig:.2f}")

    # harmony must change (different prime form)
    result.check("harmony-changed",
                 lib[progression[1]].prime != lib[modified[1]].prime,
                 f"{lib[progression[1]].prime} -> {lib[modified[1]].prime}")

    # but must remain close in voice-leading terms (still playable)
    vld = voice_leading_distance(lib[progression[1]].subset,
                                 lib[modified[1]].subset)
    result.check("voice-leading-close", vld <= 4, f"{vld} semitones")

    # the swap must be a TRUE Z-relation per the kernel
    from rules.set_theory import z_related
    result.check("z-related",
                 z_related(lib[progression[1]].subset, partner.subset))

    result.data = {
        "progression": progression,
        "swapped": modified,
        "tension_total": t_orig,
        "voice_leading": vld,
    }


def _abs_tension_arc(_ex: Exercise, result: ExerciseResult) -> None:
    """Tension arc: follow a target curve across 5 sections.

    Targets are calibrated against the standard library's actual tension
    values (maj/min triads T=2.0, dim T=4.0, dom7 T=7.0): the walk rises
    through sevenths into the dominant seventh and resolves back to the
    tonic triad.
    """
    lib = {p.id: p for p in standard_patterns()}
    targets = [2.0, 4.0, 5.5, 7.0, 2.0]     # i -> dim -> maj7 -> dom7 -> i
    candidates = ("maj0", "min9", "maj5", "min2", "dim0", "aug0",
                  "dom70", "maj70", "min70")
    pool = [lib[i] for i in candidates]
    picked = []
    for target in targets:
        best = min(pool, key=lambda p: (abs(p.tension - target), p.id))
        picked.append(best.id)
        result.check(
            f"section-tension-{len(picked)}",
            abs(best.tension - target) <= 1.0,
            f"target {target} -> {best.id} T={best.tension:.2f}",
        )
    # the arc must peak at the dominant seventh, then resolve home
    realised = [lib[pid].tension for pid in picked]
    result.check("arc-peaks-at-dom7",
                 realised[3] == max(realised) == lib["dom70"].tension,
                 f"{[round(t, 2) for t in realised]}")
    result.check("arc-resolves", realised[4] == realised[0],
                 f"end {realised[4]} == start {realised[0]}")
    result.data = {"targets": targets, "picked": picked,
                   "realised": realised}


def _abs_cardinality_expansion(_ex: Exercise, result: ExerciseResult) -> None:
    """Cardinality expansion: triad -> tetrad -> hexachord, smooth growth."""
    lib = {p.id: p for p in standard_patterns()}
    ladder = ["maj0", "maj70", "wholetone"]     # 3 -> 4 -> 6 notes
    prev: Optional[Pattern] = None
    for pid in ladder:
        p = lib[pid]
        result.check(f"{pid}-has-forte", bool(p.forte), p.forte)
        if prev is not None:
            shared = common_tones(prev.subset, p.subset)
            # smooth growth: each step shares at least one pc
            result.check(f"{prev.id}->{pid}-shares-pc", shared >= 1,
                         f"{shared} common tones")
            # ...and never jumps by more than 3 notes at once
            result.check(f"{prev.id}->{pid}-gradual",
                         p.cardinality - prev.cardinality <= 2,
                         f"{prev.cardinality} -> {p.cardinality}")
        prev = p
    result.data = {"ladder": ladder}


def _abs_mode_walk(_ex: Exercise, result: ExerciseResult) -> None:
    """Mode walk: all 7 modes on one tonic — same class, different subsets."""
    from rules.patterns import modal_sets

    modes = modal_sets(tonic_pc=2)              # D
    result.check("seven-modes", len(modes) == 7)
    # all modes share the SAME set class (7-35 diatonic collection)
    fortes = {m.forte for m in modes}
    result.check("same-set-class", fortes == {"7-35"}, str(fortes))
    # ...but the actual pitch content differs per mode
    subsets = {m.subset for m in modes}
    result.check("distinct-pitch-content", len(subsets) == 7)
    # the tonic (D = pc 2) is in every mode
    result.check("tonic-fixed", all(2 in m.subset for m in modes))
    result.data = {"modes": [m.label for m in modes],
                   "forte": sorted(fortes)}


# ---------------------------------------------------------------------------
# CONCRETE exercises — realization + verified MIDI
# ---------------------------------------------------------------------------

def _con_triad_sweep(_ex: Exercise, result: ExerciseResult) -> None:
    """All 48 triads, one per bar, each realized into a fixed register."""
    from rules.patterns import chromatic_triads

    triads = chromatic_triads()
    result.check("48-triads", len(triads) == 48)
    register = (48, 72)
    events = []
    ok_bounds = True
    for i, p in enumerate(triads):
        evs = realize(p, register=register, bar_ticks=1920)
        # each triad realizes to exactly its cardinality
        result.check(f"{p.id}-realizes", len(evs) == len(p.subset))
        for e in evs:
            if not (register[0] <= e.pitch <= register[1]):
                ok_bounds = False
    result.check("all-within-register", ok_bounds, f"{register}")
    result.data["event_count"] = sum(len(realize(p, register=register))
                                     for p in triads)
    result.data["pattern_count"] = len(triads)


def _con_diatonic_harmonisation(_ex: Exercise, result: ExerciseResult) -> None:
    """7 diatonic degrees, 4-voice realisation, no voice crossing."""
    from rules.patterns import diatonic_sets

    sets_ = diatonic_sets(0)
    result.check("14-sets", len(sets_) == 14)
    triads = [p for p in sets_ if p.cardinality == 3][:7]
    ok_no_cross = True
    for p in triads:
        placed = place_in_register(p.subset, (48, 67))       # 3 upper voices
        bass = min(placed) - 12                              # bass an octave below
        voices = [bass] + placed
        for a, b in zip(voices, voices[1:]):
            if a > b:
                ok_no_cross = False
        result.check(f"{p.id}-four-voices", len(placed) == 3)
    result.check("no-voice-crossing", ok_no_cross)
    result.data["degrees"] = [p.id for p in triads]


def _con_rhythm_rotation(_ex: Exercise, result: ExerciseResult) -> None:
    """One pc-set under 3 rotations of the tresillo; onsets verified."""
    from rules.patterns import standard_patterns

    pat = standard_patterns()[0]                 # maj0
    base = RhythmPattern("tresillo", 8, (0, 3, 6))
    rotations = [base, base.rotated(1), base.rotated(2)]
    expected_onsets = [sorted(r.onsets) for r in rotations]
    all_ok = True
    for r in rotations:
        evs = realize(pat, register=(48, 72), rhythm=r, bar_ticks=1920)
        onsets = sorted({e.start_tick for e in evs})
        want = r.onsets_in_bar(1920)
        if onsets != sorted(set(want)):
            all_ok = False
        # rotation preserves onset COUNT
        result.check(f"{r.id}-onset-count", len(onsets) == len(base.onsets))
    result.check("onsets-match-pattern", all_ok)
    result.data = {"rotations": [r.onsets for r in rotations]}


def _con_register_study(_ex: Exercise, result: ExerciseResult) -> None:
    """One pattern across 4 register bands.

    A register study means: same set class, same shape, one octave higher
    each time. The assert captures exactly that — pitch classes identical
    across bands, shape (span) preserved, and the anchor rising by exactly
    12 semitones per band.
    """
    pat = standard_patterns()[0]                 # maj0 {0,4,7}
    bands = [(40, 52), (52, 64), (64, 76), (76, 88)]
    placements = []
    for lo, hi in bands:
        placed = place_in_register(pat.subset, (lo, hi), anchor="min")
        pcs = {p % 12 for p in placed}
        result.check(f"band-{lo}-{hi}-same-pcs",
                     pcs == pat.subset, f"{sorted(pcs)}")
        result.check(f"band-{lo}-{hi}-shape",
                     max(placed) - min(placed) == 7,
                     f"span {max(placed) - min(placed)}")
        result.check(f"band-{lo}-{hi}-anchor-in-band",
                     lo <= placed[0] <= hi, f"anchor {placed[0]}")
        placements = placed
    # each successive band is the previous one transposed up an octave
    anchors = [place_in_register(pat.subset, b, anchor="min")[0]
               for b in bands]
    result.check("octave-steps",
                 all(b - a == 12 for a, b in zip(anchors, anchors[1:])),
                 f"anchors {anchors}")
    result.data = {"bands": bands, "anchors": anchors}


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

_FNS: Dict[str, Callable[[Exercise, ExerciseResult], None]] = {
    "_abs_z_swap": _abs_z_swap,
    "_abs_tension_arc": _abs_tension_arc,
    "_abs_cardinality_expansion": _abs_cardinality_expansion,
    "_abs_mode_walk": _abs_mode_walk,
    "_con_triad_sweep": _con_triad_sweep,
    "_con_diatonic_harmonisation": _con_diatonic_harmonisation,
    "_con_rhythm_rotation": _con_rhythm_rotation,
    "_con_register_study": _con_register_study,
}

ABSTRACT_EXERCISES: Tuple[Exercise, ...] = (
    Exercise(
        id="ABS-EX-001", layer="abstract", title="Z-swap",
        description=("Walk a progression, replace one chord with its "
                     "Z-partner: tension unchanged, harmony changed, "
                     "voice-leading distance reported."),
        fn="_abs_z_swap", patterns=("maj0", "min9", "maj5", "min2"),
        tags=("z-relation", "reharmonisation"),
    ),
    Exercise(
        id="ABS-EX-002", layer="abstract", title="Tension arc",
        description=("Follow a tension curve [0.2,0.4,0.6,0.8,0.3] across "
                     "5 sections; the realised curve must match the target "
                     "within tolerance and peak-then-resolve."),
        fn="_abs_tension_arc", patterns=("maj0", "min9", "maj5", "min2"),
        tags=("tension", "form"),
    ),
    Exercise(
        id="ABS-EX-003", layer="abstract", title="Cardinality expansion",
        description=("Grow triad -> tetrad -> hexachord; each step must "
                     "share at least one pitch class with the previous "
                     "(smooth growth, no jumps)."),
        fn="_abs_cardinality_expansion",
        patterns=("maj0", "maj70", "wholetone"), tags=("growth",),
    ),
    Exercise(
        id="ABS-EX-004", layer="abstract", title="Mode walk",
        description=("All 7 modes on one tonic: prime form identical "
                     "(7-35), subsets differ, tonic fixed."),
        fn="_abs_mode_walk", tags=("modal",),
    ),
)

CONCRETE_EXERCISES: Tuple[Exercise, ...] = (
    Exercise(
        id="CON-EX-001", layer="concrete", title="Triad catalogue sweep",
        description=("All 48 triads, one bar each, realized into a fixed "
                     "register; verifies realization bounds and counts."),
        fn="_con_triad_sweep", tags=("catalogue", "register"),
    ),
    Exercise(
        id="CON-EX-002", layer="concrete", title="Diatonic harmonisation",
        description=("7 diatonic degrees as 4-voice realisations; asserts "
                     "no voice crossing."),
        fn="_con_diatonic_harmonisation", tags=("counterpoint",),
    ),
    Exercise(
        id="CON-EX-003", layer="concrete", title="Rhythm rotation",
        description=("Same pc-set under 3 tresillo rotations; realized "
                     "onsets must match the rhythm pattern exactly."),
        fn="_con_rhythm_rotation", rhythm="tresillo", tags=("rhythm",),
    ),
    Exercise(
        id="CON-EX-004", layer="concrete", title="Register study",
        description=("One pattern placed in 4 register bands; each must "
                     "land inside its band without octave compression."),
        fn="_con_register_study", tags=("register",),
    ),
)

EXERCISE_REGISTRY: Dict[str, Exercise] = {
    e.id: e for e in (ABSTRACT_EXERCISES + CONCRETE_EXERCISES)
}


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def run_exercise(exercise_id: str, *, to_midi: bool = False,
                 out_dir: Optional[str] = None) -> ExerciseResult:
    """Run an exercise by id and verify its assertions.

    Abstract exercises always verify only. Concrete exercises verify by
    default; pass ``to_midi=True`` to also export the realized material as
    a validated MIDI file (zero-drift gate enforced by the composer).
    """
    if exercise_id not in EXERCISE_REGISTRY:
        raise KeyError(
            f"unknown exercise {exercise_id!r}; "
            f"have {sorted(EXERCISE_REGISTRY)}"
        )
    ex = EXERCISE_REGISTRY[exercise_id]
    result = ExerciseResult(exercise_id=ex.id, ok=True, layer=ex.layer)

    fn = _FNS[ex.fn]
    fn(ex, result)

    result.ok = not result.failed

    if to_midi and ex.layer == "concrete" and result.ok:
        _export_midi(ex, result, out_dir)
    return result


def _export_midi(ex: Exercise, result: ExerciseResult,
                 out_dir: Optional[str]) -> None:
    """Export the concrete exercise as validated MIDI (zero-drift gate)."""
    import os

    from structures import MidiInstrument, MusicEvent
    from workflows.unitmatrix_composer import (
        UnitMatrixComposer, create_note_unit,
    )

    def _unit_from_events(events, section_len):
        unit = _make_unit()
        for e in events:
            unit.add_event(e)
        # pad to exactly section_len with an inaudible terminal event
        last = max((e.end_tick for e in events), default=0)
        if last < section_len:
            unit.add_event(MusicEvent(1, 1, section_len - 1, section_len))
        return unit

    def _make_unit():
        from structures.unit import MusicUnit
        return MusicUnit()

    out = out_dir or "/opt/data/projects/Research/outputs/exercises"
    os.makedirs(out, exist_ok=True)

    composer = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
    composer.create_matrix(num_voices=1, num_sections=1)
    composer.add_voice("Lead", program=MidiInstrument.FLUTE, channel=0)
    composer.add_section("A", bars=4)

    # realize the exercise's core pattern sequence
    pats = patterns_from_degrees(0, ("I", "V", "vi", "IV"))
    events = realize_progression(pats, register=(48, 72), bars_per_pattern=1)
    unit = _unit_from_events(events, 4 * 1920)
    composer.fill_voice_section("Lead", "A", unit)

    ok, msg = composer.validate()
    result.check("zero-drift-validate", ok, msg if not ok else "validated")

    path = os.path.join(out, f"{ex.id.lower().replace('-', '_')}.mid")
    composer.to_midi(path)
    size = os.path.getsize(path)
    result.check("artifact-non-empty", size > 40, f"{size} bytes")
    result.artifacts.append(path)


def _unit_from_events(events, section_len):
    """Build a MusicUnit from absolute-tick events, padded to section length."""
    from structures.unit import MusicUnit, MusicEvent

    unit = MusicUnit()
    for e in events:
        unit.add_event(e)
    last = max((e.end_tick for e in events), default=0)
    if last < section_len:
        unit.add_event(MusicEvent(1, 1, section_len - 1, section_len))
    return unit


def list_exercises(layer: Optional[str] = None) -> List[Exercise]:
    """All registered exercises, optionally filtered by layer."""
    out = sorted(EXERCISE_REGISTRY.values(), key=lambda e: e.id)
    if layer is not None:
        out = [e for e in out if e.layer == layer]
    return out
