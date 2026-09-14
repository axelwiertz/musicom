# Patterns & Pitch-Class Sets — engine guide

How the pattern layer works after the P0–P6 reorganization
(`PATTERN_ARCHITECTURE.md` in `projects/Research/CompositionMethods/` is the
design doc with the full findings; this page is the user-facing API).

## The three layers

```
12TET pc-set KERNEL   rules/set_theory.py    normal/prime form, ICV, Forte, Z
PATTERN LIBRARY       rules/patterns.py      Pattern, catalogues, rhythm
REALIZATION           rules/realize.py       Pattern -> MusicEvent[]
EXERCISES             rules/exercises.py     runnable, self-verifying drills
```

Everything is pure (no engine I/O, no musicpy, no music21 — pinned by tests)
and deterministic. `rules/subset_network.py` still works but is a thin alias
re-exporting from `rules.patterns`; prefer the new paths.

## Kernel (`rules.set_theory`)

```python
from rules.set_theory import (
    forte_name, pcs_from_forte,        # {0,4,7} <-> "3-11"
    z_partner, z_related, all_z_pairs, # Z-relation lookup, 23 pairs
    all_sets_of_cardinality,           # 12 trichords, 50 hexachords, ...
    icv_signature, prime_form, interval_vector,
)

forte_name([0, 4, 7])          # '3-11'
forte_name([0, 1, 4, 6])       # '4-Z15'
z_partner([0, 1, 4, 6])        # frozenset({0, 1, 3, 7})  (4-Z29)
len(all_z_pairs(6))            # 15  (the classic hexachord Z-pairs)
```

The Forte name table (`rules/forte_table.py`, 220 set classes) is GENERATED
from music21 by `scripts/gen_forte_table.py` and baked in as pure data, so
naming a set needs no dependency at runtime. Six set classes have different
prime-form representatives under Forte's original rule vs the modern
Rahn/Straus rule the kernel uses (5-20, 6-31, 6-Z29, 7-20, 7-Z18, 8-26); the
names are unaffected.

## Pattern library (`rules.patterns`)

```python
from rules.patterns import (
    Pattern, standard_patterns,         # 91-entry frozen library
    chromatic_triads, chromatic_tetrads,# 48 / 60
    diatonic_sets, modal_sets,          # 14 diatonic sets, 7 modes
    z_pair_catalogue, all_hexachords,   # 23 Z-pairs, 50 hexachords
    scale_pools,                        # wholetone/octatonic/blues/...
    RhythmPattern, RhythmPatternNetwork, named_rhythms, euclidean_rhythm,
)

p = Pattern("my_chord", frozenset({0, 1, 3, 7}))
p.forte          # '4-Z29'
p.tension        # 8.5
p.z_partner      # Pattern(... 4-Z15 ...)
p.complement     # 8-note complement as a Pattern

a, b = z_pair_catalogue(4)[0]     # the 4-Z29 / 4-Z15 pair as Patterns
assert {a.forte, b.forte} == {"4-Z15", "4-Z29"}
```

`standard_patterns()` returns its 91 patterns in a FROZEN ORDER — the
zero-drift golden hash walks it. Catalogue functions only add.

## Realization (`rules.realize`)

```python
from rules.realize import realize, realize_progression, place_in_register
from rules.patterns import patterns_from_degrees, RhythmPattern

# a single chord as events (absolute ticks)
events = realize(p, register=(48, 72), bar_ticks=1920)

# a progression with voice-leading continuity between sections
events = realize_progression(
    patterns_from_degrees(0, ("I", "V", "vi", "IV")),
    register=(48, 72), bars_per_pattern=1, smooth=True,
)

# with rhythm
events = realize(p, register=(48, 72),
                 rhythm=RhythmPattern("tresillo", 8, (0, 3, 6)))
```

Events are `structures.unit.MusicEvent` with absolute ticks — feed them
straight into `UnitMatrixComposer` (see the main AGENTS.md for the
composition workflow and its zero-drift gate).

## Exercises (`rules.exercises`)

```python
from rules.exercises import run_exercise, list_exercises

result = run_exercise("ABS-EX-001")                 # verify set logic only
result = run_exercise("CON-EX-001", to_midi=True)   # also export MIDI
result.ok, result.checks, result.artifacts
```

8 registered exercises: 4 abstract (Z-swap, tension arc, cardinality
expansion, mode walk) and 4 concrete (triad sweep, diatonic harmonisation,
rhythm rotation, register study). Each returns an `ExerciseResult` whose
`.checks` are per-assertion `(name, passed, detail)` records.

## Legacy System A (`legacy/`)

The old mode-centric model (`MusicPitchClassSet`, ionian/dorian rotations)
now lives in `legacy/pitchclass.py`. It is NOT reachable from `compose()`
and has pinned defects (see `tests/test_legacy_quarantine.py`). It is kept
because ~76 project scripts and `structures/project.py` still import it —
`structures.pitchclass` is a deprecation shim re-exporting from `legacy/`.

Bridge into the modern layer:

```python
modern = MusicPitchClassSet(
    "Dorian", PatternType.HEPTATONIC, rotation=1, initial=2
).to_pattern()
modern.forte        # '7-35'
```

New code must not import `legacy` (enforced by a test). New code should not
need to: `modal_sets(mode=...)` does what System A's rotations did, as a
plain pc-set.

## Import purity invariant

`import generators.generator_registry` (the method registry read by
`workflows.selector` and `workflows.paths`) must NOT load musicpy or
music21. `generators/__init__.py` resolves its exports lazily (PEP 562) for
this reason; `tests/test_generator_lazy_imports.py` pins it in a subprocess.
The same invariant holds for `rules.*`, `structures` and `legacy`.

History: an automated composition job once imported the registry, got the
legacy musicpy/music21 converters in `sys.modules`, and spent its entire
budget "fixing" them. The lazy import is what prevents a repeat.
