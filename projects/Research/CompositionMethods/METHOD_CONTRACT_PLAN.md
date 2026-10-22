# Method Contract & Cron Migration Plan — Phase 4 (2026-10-22)

**Status: P0 BUILT. P1/P2/P3 pending.**

- P0 (method contract + realization spine) — `workflows/method_contract.py` (`RawNote`/`CellMethod`/`DefaultMethod`/`registry_method`) + `workflows/realize_spine.py` (`realize()`: snap→harmonize→dedup→zero-drift), byte-neutral, 14 tests.
- P1 (adapters for the 9 implemented concrete methods) — pending.
- P2 (style-aware fillers) — pending.
- P3 (cron rewire) — pending.

Completes the Phase-3 arc by wiring the cell engine to REAL methods and
migrating the nightly composition cron onto the shared realization spine —
"Option 1" of the adoption question.

---

## 0. The honest constraint (verified live)

The nightly composition cron (`daily-algorithmic-composition-production`)
picks a method from `methods_db.md` — which has **~100 spec-only methods with
no code**. Only **9 concrete methods** have real code in
`generator_registry` (`001/002/003/010/012/018/023/040/079`). Last night it
composed with method **065** (Twelve-Tone Serial), which is NOT in the
registry — `get_generator("065")` raises `KeyError`.

Consequence: the cron's bespoke `compose.py` is **not pure duplication** — for
spec-only methods it is the *realization of the spec* (the interpretation work
IS the composition). Option 1 therefore cannot fully delete the bespoke
script. What it CAN do is split the bespoke work into its two halves and keep
only the legitimate one:

| Half | Today | After Option 1 |
|---|---|---|
| **Raw generation** (method-specific) | bespoke per night | bespoke for spec-only; registry adapter for the 9 implemented |
| **Realization** (snap → harmonize → vary → embellish → audit) | bespoke per night | **shared `CellComposer` spine** |

Every historical bug lived in the *realization* half, not the raw generation:
the 078 off-key counterline, the 084 bar-attribution mismatch, the 078
off-grid slots, the hardcoded C-major counterline in F-minor. A shared spine
deletes that whole bug class from the cron. That is the value of Option 1 —
not "no more bespoke code", but "no more bespoke *realization*".

---

## 1. What Phase 3 already shipped (the substrate)

- `workflows/cell_engine.py` — `CellContext`, `CellComposer`, `ROLE_FILLERS`
  (P0). Position-based `default_resolve_role`; 5 legacy fillers, output-neutral.
- `scale_quantizer` — `classify_weight` + `tiered_quantize` + `StructuralNote`
  (P1).
- `rules/ornament.py` — 4 tagged chromatic ornaments + `resolve_by_step` (P1).
- `workflows/pitch_audit.py` — `audit_voice` with tagged exemption (P1).
- `workflows/variation.py` — invert/retrograde/transpose/density_scale/displace (P2).
- `harmony_writer.counterline` — the counter role (P2).
- Option-2 cron edit (done): tiered snap + ornament allowance + `audit_voice`
  in the composition cron. **Verified live** last night (0/0/0 harmony).

What is **still missing** is the two stages the plan §2 always promised but P0
deferred: **`resolve_role` (method-driven) and `generate` (raw material)**. The
engine can fill cells, but nothing yet *drives* it with a method.

---

## 2. Architecture: the method contract + the full 5-stage loop

### 2.1 `CellMethod` protocol (the missing piece)

```python
# workflows/cell_engine.py (extension) or workflows/method_contract.py
from typing import Protocol, Sequence

class CellMethod(Protocol):
    def resolve_role(self, ctx: CellContext) -> str: ...
    def generate(self, ctx: CellContext, role: str) -> Sequence[RawNote]: ...
```

`RawNote` = the phase-1 raw event: `(pitch_index: float, onset: float,
velocity: int)` — unquantized, method-character preserved (this is exactly what
the cron's phase-1 draft already produces). The method is a black box: Markov,
tendency-masking, serial, FHN — interchangeable because stages snap→harmonize→
vary→embellish don't care how the raw came out.

### 2.2 The full loop (what `CellComposer.fill_cell` grows into)

```
1. resolve_role   role  = method.resolve_role(ctx)          # fork-3: method decides
2. generate       raw   = method.generate(ctx, role)        # unquantized raw
3. snap           snapped = tiered_snap(raw, ctx, role)     # classify_weight + tiered_quantize
4. harmonize      harmonized = harmonize(snapped, ctx, role)  # chord-tone, role-aware
5. vary+embellish unit = vary(embellish(harmonized, role), ...)  # variation + tagged ornaments
   → validate (zero-drift) → fill cell
```

Stages 3–5 already exist as standalone modules (P1/P2). This plan **wires them
into the loop** and adds stages 1–2. The P0 legacy fillers remain as the
*default* `CellMethod` (`DefaultMethod` — the position-based resolver + the 5
hardcoded fillers) so `compose()`'s byte-identical output and the golden hashes
are untouched.

### 2.3 The shared realization spine (what the cron gains)

A single entry point the cron calls instead of re-writing snap/harmonize/audit:

```python
# workflows/realize_spine.py (or a method on CellComposer)
def realize(raw_notes, ctx, role) -> MusicUnit:
    """method-agnostic: snap -> harmonize -> vary -> embellish -> validate."""
```

Both the 9 implemented methods AND the cron's bespoke spec-only generators
feed raw notes into this spine. The cron keeps writing `generate()`, stops
writing `snap/harmonize/audit`.

---

## 3. File map

### New
| File | Responsibility |
|---|---|
| `workflows/method_contract.py` | `CellMethod` protocol, `RawNote`, `DefaultMethod` (wraps the P0 fillers), `registry_method()` — resolves a method ID to a `CellMethod` (implemented) or a spec-only marker |
| `workflows/realize_spine.py` | `realize(raw_notes, ctx, role) -> MusicUnit` — the shared snap→harmonize→vary→embellish→validate chain, role-aware |

### Modified
| File | Change |
|---|---|
| `workflows/cell_engine.py` | `CellComposer.fill_cell(method, ...)` — accept a `CellMethod`, run the full 5-stage loop; keep `ROLE_FILLERS` path as `DefaultMethod` for byte-neutrality |
| `workflows/method_contract.py` → adapters | one thin adapter per implemented method (`002` Markov, `023` tendency-masking, `012` euclidean, …) exposing `resolve_role` + `generate` over the existing `generators/*` classes |
| `generators/generator_registry.py` | add a `method_class_or_callable` hook (no behavior change — `get_generator()` still returns the existing class; the adapter wraps it) |

### Cron (deferred to P3, after the library is solid)
| File | Change |
|---|---|
| cron `1fc3fd65d359` prompt | implemented method → route through `registry_method()` + spine; spec-only → bespoke `generate()`, shared spine for realization; delete the bespoke snap/harmonize/audit instructions |
| `musicom-composer` skill | mirror the two-half split (raw generation bespoke, realization shared) |

---

## 4. Tiers (build order)

### P0 — Method contract + shared realization spine (library only, no cron)
Deliver `CellMethod` protocol, `RawNote`, `DefaultMethod`, `registry_method()`,
and `realize()`. Prove the spine reproduces `compose()`'s output byte-identically
when fed the default method's raw (golden-hash gate: `test_harness_golden` +
`test_realize_bridge` stay green). No cron change.
- Gate: `compose()` golden hashes unchanged; a `realize()` smoke test turns raw
  notes into a validated `MusicUnit` with 0 un-tagged / 0 strong-viol via
  `audit_voice`.

### P1 — Adapters for the 9 implemented concrete methods
Thin wrappers: `MarkovMethod`, `TendencyMaskingMethod`, `EuclideanMethod`,
`SchillingerMethod`, `GeneticMethod`, `PerlinMethod`, `TintinnabuliMethod`,
`FunctionMethod` (+ `HC-012` if trivial). Each exposes `resolve_role` (mostly
"lead"/"rhythm"/"bass" from the method's nature) + `generate` (delegating to the
existing class). Prove one end-to-end: `compose(method="023")` produces a
method-driven piece whose phase-1 differs from the default but whose phase-2
passes `audit_voice`.
- Gate: per-adapter unit test (role resolves, raw emits the method's character,
  e.g. Markov state-walk vs Euclidean onsets), plus one interactive listen.

### P2 — Style-aware fillers (the musical bulk)
The 5 legacy fillers are pop-generic. Add a `style → role → filler` table so
jazz swing lead ≠ pop 8th arp. This is the largest creative surface and is
**separately reviewable** — it changes what music comes out, so it must not
ship silently into the cron.
- Gate: per-style golden fixtures for ≥3 styles (pop/jazz/techno), each
  validated + audited 0/0/0, human-listenable.

### P3 — Cron rewire (Option 1 lands)
Update the composition cron + `musicom-composer` skill to the two-half split.
Keep: two-phase export, grid sync, mastering, humanization, dual-version,
tiered audit (all verified working). Change: realization goes through the
spine; spec-only methods keep bespoke `generate()` only.
- Gate: a supervised `cronjob run` produces a piece with 0/0/0 harmony and the
  REPORT.md shows the spine (not bespoke audit) ran.

---

## 5. What I would NOT do

- ❌ Force spec-only methods through `registry_method()` — they have no code;
  the bespoke interpretation is the composition. Mark them "spec-only" and keep
  their `generate()` bespoke.
- ❌ Break the golden hashes — P0 keeps `DefaultMethod` byte-identical; the
  spine is proven output-neutral before any cron change.
- ❌ Ship style-aware fillers (P2) into the cron without a human listen — that's
  a musical change, not plumbing; it gets its own review.
- ❌ Delete the phase-1 raw draft — it stays (single voice, unquantized), now
  it's just the `generate()` output fed through the spine.

---

## 6. Risks

1. **Adapter surface ≠ small.** 9 methods × (resolve_role + generate) is real
   work, and each generator's API differs (some return `MusicUnit`, some
   `(pitch, dur)` tuples, some need a seed in the ctor vs `generate()`). P1 must
   read each class's real signature first (`inspect.signature`), not guess.
2. **`generate()` shape drift.** Raw pitch_index [0,1] vs absolute pitch varies
   by method (FHN emits floats, Markov emits pitch classes). The `RawNote`
   contract must normalize at the adapter boundary, not leak method internals
   into the spine.
3. **Style-aware fillers = taste.** P2 is where "sounds good" lives and is the
   only tier that can't be regression-gated by hashes alone — it needs ears.
4. **Cron regression.** The cron currently works (verified last night). Any P3
   change must be `cronjob run`-verified before the next 23:00 tick, with the
   `jobs.json.bak-phase3` backup + git as rollback.

---

## 7. Reference

- `VOICE_ROLE_WORKFLOW_PLAN.md` (this dir) — the Phase-3 plan this completes
  (§2 stage list, §6 file map, the four invariants).
- `generators/generator_registry.py` — the 9 implemented concrete methods.
- `workflows/cell_engine.py`, `workflows/pitch_audit.py`, `workflows/variation.py`,
  `rules/ornament.py` — the substrate already shipped.
- Cron `1fc3fd65d359` prompt (edited 2026-10-22, Option 2) — the current
  verified-working target of the P3 rewire.
