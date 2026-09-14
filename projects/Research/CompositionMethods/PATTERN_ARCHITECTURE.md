# Pattern & Pitch-Class-Set Architecture — Design + Migration Plan

**Status: EXECUTED — P0–P6 all landed.** Phases map to commits:
P0+P1 `875f8ad`, P2 `36e3873`, P3 `d4870a1`, P4 `1ad146a`, P5 `6d074ea`,
P6 (docs: `docs/patterns.md`, this file's status, AGENTS.md) = the commit
introducing this line. User-facing guide: `docs/patterns.md`. The five
decisions in §5 were taken per the recommendations below (P4 = quarantine
to `legacy/`; musicpy/music21 demoted out of the composition path's import
graph — they remain deps only for MusicXML and the build-time table
generator; rhythm side built to network parity; exercises checked into
`rules/exercises.py`).
**Author:** agent (musicom), 2026-09-13
**Trigger:** the `daily-algorithmic-composition-production` cron spent an entire
budget fixing `musicpy`/`music21` converters (project 095) and never composed
anything. The user's response: *"I thought we used a generic pattern library
based on pitch class set and not this code anymore. If so, plan for a thorough
pattern and pitch(class)set structure that is usable for abstract and concrete
exercises."*

---

## 0. Verdict on the premise

**The premise is correct, with one correction to the framing.** There is not one
pitch-class-set system — there are **two parallel ones**, and only the newer one
is wired to the composition entry point.

| | **System A — legacy** | **System B — current** |
|---|---|---|
| Lives in | `structures/pitchclass.py` (776 lines) | `rules/set_theory.py` (95) + `rules/subset_network.py` (352) |
| Core types | `MusicPitchClassSet`, `PatternType`, `PatternGraph`, `PatternRegistry`, `MusicPattern.dict` | `Pattern`, `PatternNetwork`, `ChordQuality`-free pure 12TET |
| Model | **mode-centric** (ionian/dorian/aeolian rotations, string mode names) | **set-theoretic** (Forte/Straus: prime form, ICV, Z-relations, P/L/R) |
| Reachable from `compose()`? | **No** | **Yes** (`ABS-*` path) |
| Health | partially broken (§2) | works, tested, used |

**`compose()` never touches `musicpy`/`music21`.** Verified:

```
compose(style='pop', method='ABS-002')   →  4333-byte MIDI
  method: ABS-002:subset_walk=maj0,min2,maj5,maj0,min2
```

That path calls `rules/subset_network.py` directly. So the cron was fixing
**dead code** — and the reason it found that dead code is a real structural
trapdoor (§1.1), not bad luck.

### Why the cron ended up there

`generators/__init__.py` line 2:

```python
from .chord_degrees import ChordDegreeGenerator     # ← the trapdoor
```

`chord_degrees.py` imports `converters.musicpy_converter` and
`converters.music21_pattern`, which `import musicpy` / `from music21 import ...`
at module level. Because Python executes a package's `__init__` on **any**
submodule import, this happens:

| import | musicpy loaded? |
|---|---|
| `import generators` | **True** |
| `import generators.generator_registry` | **True** |
| load `generator_registry.py` *directly*, bypassing `__init__` | **False** |

`workflows/selector.py` and `workflows/paths.py` both do
`from generators.generator_registry import GENERATOR_REGISTRY`. So the *method
registry* — a pure data table — drags the entire legacy musicpy bridge into
every session that touches method selection. That is how a composition job ends
up "fixing converters" instead of composing.

**Three** eager imports in `__init__` pull a heavy/legacy dependency, not one:

| line | module | dependency |
|---|---|---|
| 2 | `chord_degrees` | `musicpy` + `music21` (+ `converters.musicpy_converter`, `converters.music21_pattern`) |
| 4 | `harmonics` | `from music21 import note, interval` |
| 7 | `stochastic` | docstring says "music21 streams" (verify at implementation) |

The other nine generators are dependency-free. So the fix is the same lazy
pattern for all three, and the invariant to assert is broader: **importing the
method registry must not require `musicpy` or `music21`.**

**Precedent:** `structures/` is clean — `import structures` loads neither
`musicpy` nor `music21`.

---

## 1. Findings (all verified, no claims)

### 1.1 The trapdoor is the root cause of the cron failure
See §0. Fixing this alone would have prevented the wasted run.

### 1.2 System A is half-broken

| defect | evidence |
|---|---|
| `rotation_name` is a `@staticmethod` that takes `self` | `inspect.getattr_static(...)` → `staticmethod`; `p.rotation_name()` → `TypeError: missing 1 required positional argument` |
| `__init__` signature is `(name, definition, rotation, initial)` | `MusicPitchClassSet(rotation_index=...)` → `TypeError: unexpected keyword argument` |
| `converters/pattern.py` reads attributes that don't exist | `pattern.modes` → **MISSING**, `pattern.modes_helix` → **MISSING** (13-line module, would raise at runtime) |
| `PatternRegistry` hierarchy (`parent`, `degree_indices`) | defined, never consumed by anything |

These are the exact crashes the cron spent its budget on.

### 1.3 No realization primitive (the real architectural gap)

There is **no shared** `Pattern → MusicEvent[]` function anywhere:

```
grep -rn "def realize\|def to_events\|def to_unit"  rules/ workflows/  →  (nothing)
```

`compose()`'s ABS path does it **ad-hoc and inline**:

```python
for pid in walk:
    pat = net_lib.patterns[pid]
    root_pc = min(pat.subset)
    base = 48 + root_pc                       # C3 register, hardcoded
    tones = [base + ((pc - root_pc) % 12) for pc in sorted(pat.subset)]
```

This is the Abstract→Concrete bridge, and it exists only as 6 lines inside a
workflow. Every new consumer (concrete exercises, cron jobs, HITL variants) has
to reinvent it — or wanders off into legacy code looking for it.

### 1.4 The pattern library is thin where it matters most

`standard_patterns()` → **91** patterns, cardinality histogram
`{3: 48, 4: 40, 6: 1, 8: 2}`. It is a triad/tetrad catalogue. Consequences:

- **1 Z-pair** discovered in the whole network: `z0137` / `z0146`.
  `subset_theory.md` documents **15 hexachord Z-pairs** (6-Z3/6-Z36 … 6-Z29/6-Z50) —
  none are in the library. Verified independently with the repo's own kernel:
  enumerating all 6-pc subsets and grouping by ICV yields **exactly 15
  two-member Z-groups**, matching the doc. So the theory is correct and the
  catalogue is the thing that's missing. The canonical generative idea ("swap a
  chord for its Z-partner: same tension, fresh harmony") is effectively
  unavailable.
- Edge histogram: `{tn: 1212, plr: 1832, vl: 3150, z: 2}` — 0.03% of edges are
  Z-relations. The tension/resolution model is dominated by transposition.
- No **Forte name table** anywhere (`3-11`, `4-Z15`, …). `grep` → nothing.
  So `subset_theory.md`'s own vocabulary can't be used to name a pattern.

### 1.5 Dead fields and orphaned modules

| item | state |
|---|---|
| `Pattern.role` (`"harmony" \| "lead" \| "bass" \| "texture"`) | set, copied by `complement`/`transposed`, **never read** |
| `structures/intervals.py` (198 lines) | genuinely useful: Hindemith stability ranks, Bartók interval expansion, delta encoding. `interval_class_vector`/`z_related`/`set_prime_form` delegate correctly to the kernel. **Correction to my first read:** the Hindemith/Bartók/encoding half is *not* dead — it is covered by `tests/test_interval_structures.py` and used by `examples/compose_interval_methods.py`. But it is **not wired into the sanctioned `compose()` path or the abstract layer**, which is the actual gap: these primitives exist but the pattern architecture above them doesn't consume them. |
| `MusicRhythmPattern` (`structures/timegrid.py`) | 15 named rhythms (Tresillo, Son Clave, Bembe, …) but stores `(cycle, onsets)` as one opaque tuple — no `.cycle` / `.onsets` accessors. No rhythm-side sibling to `PatternNetwork`. |
| `subset_theory.md` | the design doc for this area, tracked at `projects/Research/CompositionMethods/subset_theory.md` (beside `LAYER_ARCHITECTURE.md`). Not in `docs/`, so it is invisible to anyone reading the docs tree — the code references it but the docs don't. |

### 1.6 What is already *right* (do not rebuild)

- `rules/set_theory.py` is a proper **canonical kernel**: `normal_form`,
  `prime_form`, `interval_vector`, all correct. `structures/intervals.py` and
  `rules/subset_network.py` both **delegate** to it rather than re-implementing.
  This is the pattern to keep.
- `PatternNetwork` relations (`tn`/`inv`/`z`/`compl`/`plr`/`vl`) with
  closeness weights, plus `walk(start, length, tension_curve, home)`, are a
  sound abstract-layer API.
- `diatonic_degree_patterns(0)` correctly yields
  `{'I': 'maj0', 'V': 'maj7', 'vi': 'min9', 'IV': 'maj5', …}` — the
  tonal↔set-theoretic bridge already works.
- `structures/` has **no** musicpy/music21 dependency. Keep it that way.
- Golden zero-drift gate at `GOLDEN_SHA256 = d6c847a4…`, 484 tests collected.

---

## 2. Proposed architecture

One concept, three layers, two entry points. No second System A.

```
12TET pc-set KERNEL        rules/set_theory.py            (exists, keep)
        │                  normal_form, prime_form, ICV,
        │                  Forte name, Z-pair lookup
        ▼
PATTERN LIBRARY            rules/patterns.py              (NEW — one library)
        │                  Pattern (pc-set + role + tags)
        │                  PITCH: PatternNetwork (tn/z/plr/compl)
        │                  RHYTHM: RhythmPattern + RhythmNetwork
        │                  catalogue: diatonic ∪ chromatic ∪ Z-pairs
        ▼
REALIZATION                rules/realize.py               (NEW — the bridge)
        │                  realize(pattern, register, rhythm, voice) → MusicEvent[]
        │                  place_in_register(), voicing, delta-encode
        ▼
ABSTRACT EXERCISES    →    rules/subset_network.abs_*     (exists, extend)
CONCRETE EXERCISES    →    concrete Exercise objects → UnitMatrixComposer
```

### 2.1 Kernel — extend `rules/set_theory.py` (do not replace)

Add only what's genuinely missing:

| function | purpose | notes |
|---|---|---|
| `forte_name(pcs) -> str` | `{0,4,7}` → `"3-11"`, `{0,1,4,6}` → `"4-Z15"` | static table over the **220 set classes** of cardinality 2–10 (measured with the repo's own kernel: 6/12/29/38/50/38/29/12/6). Z-sets carry the `Z` infix. Needed to use `subset_theory.md`'s own vocabulary. |
| `pcs_from_forte(name) -> FrozenSet[int]` | inverse; `"4-Z15"` → `{0,1,4,6}` | makes the library addressable by catalogue name |
| `z_partner(pcs) -> Optional[FrozenSet]` | the Z-relation lookup | currently only discoverable by building a whole `PatternNetwork` |
| `all_sets_of_cardinality(k)` | enumerate the distinct prime forms of size k | for "exercise every trichord" drills |
| `icv_signature(pcs)` | ICV as a hashable tuple | already implicit; needed for grouping |

**Invariant:** this stays a pure, import-free, deterministic module (no engine,
no I/O, no musicpy). Enforced by a test that asserts `musicpy`/`music21` are
absent from `sys.modules` after import.

### 2.2 Pattern library — new `rules/patterns.py`

`Pattern` currently lives in `subset_network.py` with a dead `role` field. Move
it to its own module and make the library **queryable**:

```python
@dataclass(frozen=True)
class Pattern:
    id: str
    subset: FrozenSet[int]
    roles: Tuple[str, ...] = ("harmony",)   # actually used (was dead `role`)
    tags: Tuple[str, ...] = ()              # "diatonic", "z-pair", "modal", "blues"
    label: str = ""                          # "Dorian tetrachord", …

    @property
    def forte(self) -> str: ...              # via kernel
    @property
    def z_partner(self) -> Optional[str]: ...
    @property
    def icv(self) -> List[int]: ...
    @property
    def tension(self) -> float: ...
    def transposed(self, n): ...
    def inverted(self): ...
    def complement(self): ...
```

Catalogue functions (each returns `List[Pattern]`, all deterministic):

| function | content | today |
|---|---|---|
| `diatonic_sets(tonic_pc)` | the 7 triads + 7 tetrads of a major scale | partial (`diatonic_degree_patterns` ids only) |
| `chromatic_triads()` / `chromatic_tetrads()` | all 12 transpositions × quality | **48 / 40 exist** (keep) |
| `z_pair_catalogue(cardinality)` | the true Forte Z-pairs, incl. the 15 hexachord pairs from `subset_theory.md` | **missing** — only 1 pair found |
| `modal_sets(tonic_pc, mode)` | the 7 modes as patterns | System A's job, done properly |
| `all_hexachords()` | 50 hexachords (complements included) | **missing** |
| `scale_pools()` | wholetone / octatonic / pentatonic / blues | partial |

**Rhythm side.** Promote `MusicRhythmPattern` into the same shape, with real
accessors and a network:

```python
@dataclass(frozen=True)
class RhythmPattern:
    id: str
    cycle: int
    onsets: Tuple[int, ...]
    tags: Tuple[str, ...] = ()      # "clave", "aksak", "ternary", …

    def density(self) -> float: ...
    def rotated(self, n): ...
    def is_rotation_of(self, other): ...    # clave direction matters musically
```

`RhythmPatternNetwork` mirrors `PatternNetwork`: edges = rotation /
complement-of-onsets / same-cycle-sharing-pulse / density-distance. This gives
the abstract layer a **rhythm partner** for its pitch partner, which is what a
"thorough" structure needs — right now rhythm is a flat dict of 15 tuples.

**Backwards compatibility:** `rules/subset_network.Pattern` is re-exported from
`rules/patterns.py` so existing imports keep working. `MusicPitchClassSet` gets a
`.to_pattern()` adapter rather than being deleted (see §3, phase P4).

### 2.3 Realization bridge — new `rules/realize.py`

The missing abstraction. Turns an abstract `(Pattern, RhythmPattern)` into
concrete `MusicEvent[]`:

```python
def place_in_register(pcs, register, *, anchor="root", spread=None) -> List[int]:
    """pc-set → sorted MIDI pitches inside a register band."""

def realize(pattern, *, register=(60, 72), rhythm=None,
            bar_ticks=1920, articulation=0.95, velocity=90,
            voicing="close", seed=0) -> List[MusicEvent]:
    """Abstract Pattern (+ optional rhythm) → concrete events."""

def realize_progression(patterns, *, ...) -> List[MusicEvent]:
    """A walked pattern sequence → one continuous concrete line."""
```

Rules it must own (each currently reinvented per call-site):

- register placement with an explicit anchor (root / lowest / nearest-to-previous)
- voicing spread (close position vs open vs drop-2)
- **voice-leading continuity** between consecutive patterns (reuse
  `rules/voice_leading.py` / `subset_network.voice_leading_distance`)
- articulation vs legato (the `.95` duration trim used ad-hoc today)
- optional `structures/intervals.delta_encode` round-trip for
  transposition-invariant storage

`compose()`'s inline 6 lines get replaced by a call to this. That is the
concrete proof the bridge is real (and the zero-drift golden hash stays put
because output is byte-compared — see §4).

**Also wire in the existing `structures/intervals.py` primitives** (they are
tested and correct but currently unconsumed by the pattern layer):

- `hindemith_rank` / `harmonic_fluctuation` → a **tension metric for melodic
  intervals**, complementing the harmonic tension already in `Pattern.tension`.
  `realize()` can enforce a `max_hindemith_rank` on a line.
- `interval_expansion` / `interval_contraction` → Bartók-style motivic
  development over a pattern sequence; belongs in the abstract exercises (§2.4).
- `delta_encode` / `delta_decode` / `transposition_invariant` → the storage
  form for patterns, so a realised line can be stored transposition-invariantly
  (exactly what the Abstract layer claims to be).

### 2.4 Exercises — the two entry points the user asked for

An **Exercise** = a named, self-describing unit of work that the engine can run
and verify. Two kinds, matching the layer architecture:

```python
@dataclass
class Exercise:
    id: str                     # "ABS-EX-001"
    layer: str                  # "abstract" | "concrete"
    title: str
    patterns: List[str]         # pattern ids
    rhythm: Optional[str]
    form: List[int]             # bars per section
    key: str
    bpm: int
    tags: Tuple[str, ...]
```

**Abstract exercises** (no MIDI, pure verification of set logic):

| id | exercise | asserts |
|---|---|---|
| ABS-EX-001 | Z-swap: walk a progression, replace one chord with its Z-partner | tension unchanged, harmony changed, voice-leading distance reported |
| ABS-EX-002 | Tension arc: follow `[0.2,0.4,0.6,0.8,0.3]` across 5 sections | realised tension curve matches target within tolerance |
| ABS-EX-003 | Cardinality expansion: triad → tetrad → hexachord | each step shares ≥1 pc with the previous (smooth growth) |
| ABS-EX-004 | Mode walk: 7 modes on one tonic | prime form identical, subset differs, tonic fixed |

**Concrete exercises** (produce validated MIDI, zero-drift gate):

| id | exercise | produces |
|---|---|---|
| CON-EX-001 | Triad catalogue sweep: all 48 triads, one bar each | MIDI + grid viz |
| CON-EX-002 | Diatonic harmonisation: 7 degrees, 4-voice realisation | MIDI, no voice crossing (via `rules/counterpoint`) |
| CON-EX-003 | Rhythm rotation: same pc-set under 3 clave rotations | MIDI, onsets verified against the rhythm pattern |
| CON-EX-004 | Register study: one pattern across 4 register bands | MIDI, each band within its instrument range |

An `EXERCISE_REGISTRY` maps id → spec, and `run_exercise(id)` returns
`(artifacts, assertions_passed)`. This is "usable for abstract and concrete
exercises" in concrete terms.

---

## 3. Migration plan

Ordered, each phase independently shippable and testable. **Nothing is deleted
until its replacement is proven.**

### P0 — Close the trapdoor *(small, high value, do first)*
- **Change:** `generators/__init__.py` — stop importing `chord_degrees` eagerly.
  Replace the eager `from .X import Y` block with a lazy PEP 562 `__getattr__`
  that resolves each name on first access.
- **Constraint (verified):** this must be lazy, **not** deletion. **77** project
  scripts do `from generators import ...` — 75× `RhythmGenerator`, 1×
  `TonalNetworkGenerator`, 1× `TintinnabuliGenerator`. Those imports must keep
  working unchanged — a lazy `__getattr__` preserves them exactly while keeping
  the musicpy-backed `chord_degrees` off the import path until something
  actually asks for it.
- **Test:** `import generators.generator_registry` must leave `musicpy` and
  `music21` absent from `sys.modules`; `from generators import RhythmGenerator`
  must still work; each of the 9 exported names must resolve via `__getattr__`.
- **Impact:** the cron stops wandering into the converter subtree. This single
  change prevents a repeat of the failed run.

### P1 — Kernel completion *(additive, no breakage)*
- **Add** to `rules/set_theory.py`: `forte_name`, `pcs_from_forte`, `z_partner`,
  `all_sets_of_cardinality`, `icv_signature`.
- **Test:** Forte round-trip for every set of cardinality 2–6; the 15 hexachord
  Z-pairs from `subset_theory.md` all resolve; purity test (§2.1).

### P2 — Pattern library *(additive)*
- **New** `rules/patterns.py` with `Pattern`, the catalogue functions, and the
  rhythm types. `rules/subset_network.py` re-exports `Pattern` for compat.
- **Test:** catalogue sizes (48 triads / 40 tetrads / ≥15 hexachord Z-pairs);
  every pattern's `forte` resolves; determinism; no musicpy import.

### P3 — Realization bridge *(the architectural gap)*
- **New** `rules/realize.py`. Refactor `compose()`'s ABS path to call it.
- **Test:** golden MIDI hash unchanged (`d6c847a4…`); register placement within
  bounds; voice-leading distance between consecutive realisations ≤ a threshold;
  a realization round-trips through `delta_encode`/`delta_decode`.

### P4 — Quarantine System A *(needs your call — see §5)*
- Decide fate of `structures/pitchclass.py` (776 lines) and the
  `converters/music*` subtree: delete, or move to a clearly-marked
  `legacy/` package that nothing imports.
- Add `.to_pattern()` adapter so live consumers keep working:
  `structures/project.py`, `examples/three_voices.py`,
  `projects/Styles/Groove/019-soul-groove/src/regen.py`.
- Fix or delete the broken `converters/pattern.py` (`modes`/`modes_helix`).

### P5 — Exercises
- **New** `rules/exercises.py` + `EXERCISE_REGISTRY`. 8 exercises above.
- **Test:** every exercise runs, produces non-empty artifacts
  (`> 40 bytes`), passes its assertions.

### P6 — Docs
- Promote/cross-link `subset_theory.md` and this plan from `docs/` (they are
  referenced by code but the docs tree never points at them).
- Add the pattern/rhythm/realize API to `docs/`.
- Update `AGENTS.md`: document the layer entry points and the musicpy-free
  invariant.

---

## 4. Verification strategy

| gate | how |
|---|---|
| **No regression** | `GOLDEN_SHA256 = d6c847a4…` must stay byte-identical through P0–P3. Any change means the refactor altered output — investigate before accepting. |
| **Purity** | test asserts `musicpy`/`music21` not in `sys.modules` after importing `rules.*`, `structures`, `generators.generator_registry`. |
| **Kernel correctness** | Forte round-trip 2–6; the 15 documented hexachord Z-pairs; ICV identities straight from `subset_theory.md` (e.g. `interval_vector([0,4,7]) == [0,0,1,1,1,0]`, 4-28 fully-dim = `[0,0,0,4,0,4]`). |
| **Realization** | register bounds, voice-leading threshold, articulation, determinism, delta round-trip. |
| **Exercises** | each runs; artifacts `> 40` bytes; assertions pass; prose claims match measured values. |
| **Suite** | 484 currently collected → all green at every phase. |

---

## 5. Decisions I need from you

1. **P4 — System A's fate.** `structures/pitchclass.py` is 776 lines, partly
   broken, unused by `compose()`, but touched by `structures/project.py`,
   `examples/three_voices.py`, and one project script.
   *(a)* delete it + fix the 3 consumers, *(b)* move to `legacy/` with an
   adapter, *(c)* leave it alone and only add the adapter.
   **My recommendation: (b)** — quarantining is reversible and honest, while
   deletion is not; the adapter keeps the consumers alive.

2. **musicpy/music21 as a dependency at all.** They are in `requirements.txt`
   as core deps but the sanctioned composition path needs neither. Do you want
   them demoted to optional extras (used only for MusicXML import/export),
   or kept as-is?

3. **Rhythm scope.** Do you want the rhythm side built out to parity with the
   pitch side (RhythmPattern + RhythmNetwork, §2.2), or is pitch the priority
   for now?

4. **Exercises as a permanent library** (checked into `rules/`), or as a
   throwaway verification harness under `projects/Research/`?

---

## 6. What this fixes

| problem | fixed by |
|---|---|
| Cron wanders into legacy converters and wastes its budget | P0 |
| Method registry drags `musicpy`+`music21` into every session (via `chord_degrees`, `harmonics`, `stochastic`) | P0 |
| No way to name a set (`3-11`, `4-Z15`) | P1 |
| Only 1 Z-pair available; the key generative idea is unusable | P2 |
| No shared Pattern→MIDI bridge; every consumer reinvents it | P3 |
| Two competing pc-set systems, one half-broken | P4 |
| "Abstract and concrete exercises" have no home | P5 |
| Design doc referenced by code but not in `docs/` | P6 |

## 7. Scope estimate

| phase | new/changed | risk |
|---|---|---|
| P0 | 1 file, ~15 lines | very low |
| P1 | 1 file, ~120 lines + tests | low (additive) |
| P2 | 2 new modules, ~450 lines + tests | medium (must not break `subset_network` imports) |
| P3 | 1 new module (~250 lines) + `compose()` refactor | medium (golden-hash guarded) |
| P4 | 1–4 files deleted/moved + 3 adapters | **high — needs your decision** |
| P5 | 1 module, ~350 lines + tests | low |
| P6 | docs | low |

**Recommended first delivery: P0 + P1 only.** P0 stops the bleeding immediately;
P1 is purely additive and unlocks the vocabulary the rest needs. Review those,
then green-light P2–P6.
