# Musicom Repo Review & Improvement Plan

Date: 2026-09-02. Author: agent review. Scope: `/opt/data/repos/musicom`
(+ its relationship to `projects/`, `hermes_persistent/skills/`, and the
sibling repos that vend `lib/musicom/`).

Every finding below was verified against the live repo (imports run, `git`
counts checked, byte-comparisons done). Findings are grouped: **duplication**,
**unlogic/bugs**, **obsolete/stale**, **layering** (the recent
Abstract/Concrete/Absolute work).

---

## 1. Duplication

### 1.1 Set theory implemented three times (and they disagree)

| Module | Functions |
|---|---|
| `rules/set_theory.py` | `SetTheoryAnalyst.normal_form`, `.prime_form`, `.interval_vector` |
| `structures/intervals.py` | `interval_class_vector`, `z_related`, `set_prime_form` |
| `rules/subset_network.py` | `interval_vector` (wraps set_theory), `tension`, `icv_distance`, `voice_leading_distance` |

**Confirmed divergence (a real bug):**

```
structures/intervals.set_prime_form([0,4,7])  -> (0, 3, 8)   # WRONG
rules/set_theory.SetTheoryAnalyst.prime_form   -> [0, 3, 7]   # correct (Forte)
```

`set_prime_form` normalizes rotations but **never normalizes inversions**, so
a major triad reports the wrong canonical form. Both modules claim "Forte
prime form"; only `set_theory.py` is correct.

**Fix:** single canonical set-theory kernel in `rules/set_theory.py`;
`structures/intervals.py` and `rules/subset_network.py` delegate to it. Delete
the private implementations. `z_related` in `intervals.py` also misses the
inversion check (only checks transposition) — the network in `subset_network.py`
does it right (TN/INV/Z distinction).

### 1.2 Harmony/progression tables duplicated four times

- `workflows/paths.py`: `KEY_OFFSET`, `CHORD_SHAPES`, `QUALITY_INTERVALS`, `MAJOR_DEGREES`, `PROGRESSIONS`
- `workflows/musicom_workflow.py`: **local copies** of `KEY_OFFSET`, `CHORD_SHAPES`, `PROG` (lines 224–233) — a second, divergent copy inside the same repo
- `generators/tonal_network.py`: `CHORD_QUALITY` (same data as `QUALITY_INTERVALS`)
- `rules/progression.py`: `PatternMovementRules`, `Scale7ChordDegree`, `PatternProgressions` (degree→interval mappings again)

**Fix:** one `rules/harmony.py` (or extend `structures/intervals.py`) exporting
`KEY_OFFSET`, `CHORD_SHAPES`, `QUALITY_INTERVALS`, `MAJOR_DEGREES`,
`PROGRESSIONS`. `paths.py`, `musicom_workflow.py`, `tonal_network.py` import it.
Delete the local `musicom_workflow.py` copy (it diverges: `KEY_OFFSET` there is
missing the relative-minor entries that `paths.py` has).

### 1.3 Voice-leading / movement rules scattered across four modules

- `rules/voice_leading.py` — `VoiceLeadingRules` (parallel motion, voice crossing, hidden fifths, `calculate_voice_leading_distance`, `optimize_voice_leading`)
- `rules/movement.py` — `Scale7DegreeFunction`, `Scale7PitchDegree` (degree movement)
- `rules/progression.py` — `PatternMovementRules.movement_rules` (degree 1–7 movement, overlaps movement.py)
- `rules/subset_network.py` — `voice_leading_distance` (duplicates `VoiceLeadingRules.calculate_voice_leading_distance`)
- `generators/tonal_network.py` — functional-affinity graph (tonic/dominant/mediant weights)

**Fix:** consolidate the numeric metric (`voice_leading_distance`) into one
place (keep `rules/subset_network.py` as the abstract-layer metric, have
`voice_leading.py` delegate or vice-versa — pick one, document it). Merge
`movement.py` into `progression.py` (they both encode heptatonic degree
movement; `movement.py` is 40 lines and nearly orphaned).

### 1.4 Docs duplicated byte-identical across trees

```
cmp docs/methods.md            projects/Research/CompositionMethods/methods_db.md      -> IDENTICAL (15,112 lines)
cmp docs/human-methods.md      projects/Research/CompositionMethods/human_methods_db.md -> IDENTICAL
```

This is **by design** (see AGENTS.md "Data sync"): `docs/*.md` is a synced
mirror of `projects/Research/...` produced by `scripts/sync_to_repo.py`. So it
is not duplication to remove — but there are still **two** manual homes to
worry about: the *content* lives in `projects/Research/CompositionMethods/*`
(the source), and the engine-level truth lives in code
(`generators/generator_registry.py` + `workflows/paths.py` SCALE). The 15k-line
`methods_db.md` is **not** auto-generated from the registry, so it can drift
from code (see L2 below — ABS methods aren't in it).

**Fix:** keep the sync mirror. Make `methods_db.md`/`human_methods_db.md` the
documented *human-readable* source, but add a header note pointing at the code
truth (`generator_registry.py`) and note that the ABS-* abstract methods are
not yet listed. Optionally generate the method table from the registry into
`docs/` (already possible via `registry_table()`), leaving the long-form prose
in the DB files.

### 1.5 Agent knowledge duplicated across three locations

- `hermes_agent/*.md` (composition.md, sound-production.md, methods-registry.md, sound-methods-overview.md, decisions.md, surveillance.md)
- repo-root `AGENTS.md` (canonical machine-facing guide)
- `README.md` / `QUICK_REFERENCE.md`
- `hermes_persistent/skills/musicom-method-master-map/` + `skills/music/musicom-onboarding/`

`hermes_agent/composition.md` restates the "core model" and "one true workflow"
that AGENTS.md already has. `hermes_agent/methods-registry.md` restates
SP-method tables also present in `workflows/musicom_workflow.py:SP_METHODS`
and `docs/methods.md`.

**Fix:** shrink `hermes_agent/` to the *delta* (operational decisions, surveillance
findings, cron playbooks) and link back to AGENTS.md for the canonical
workflow. Remove the SP-method tables that are auto-derivable from code.

### 1.6 Sibling repos vend copies of the engine

`composer-crew-framework/`, `musicom-agent/`, `musicom_framework/`,
`musicom_platform/` all carry a `lib/musicom/` tree (seen in `find` output).
These are parallel copies of the same engine at different stages.

**Fix:** not in this repo's control, but flag it: the engine is installed
editable from `/opt/data/repos/musicom`; any repo still vendoring `lib/musicom`
should switch to the editable install or a git submodule. Add a note to
AGENTS.md so agents don't edit the vendored copies.

---

## 2. Unlogic / bugs

| # | Where | Problem | Severity |
|---|---|---|---|
| B1 | `structures/intervals.py:set_prime_form` | returns `(0,3,8)` for major triad; missing inversion normalization → wrong prime forms | **high** (silently wrong set-theory results) |
| B2 | `structures/instrument.py:MidiInstrument.PIANO = 1` | General MIDI Acoustic Grand Piano is **program 0**, not 1 | medium (off-by-one on a published constant) |
| B3 | `structures/instrument.py:MidiInstrument.PERCUSSION = 128` | 128 is not a valid GM program (0–127); percussion is **channel 10**, not a program number | medium (conflates program with channel; `MidiChannel.PERCUSSION=10` already exists) |
| B4 | `musicom_compat.pth` + `musicom_compat.py` in site-packages | stale alias from the pre-flat-package era; `decisions.md` claims it was removed but it still exists; `import musicom` yields an **empty** module | medium (dead shim; confusing empty namespace) |
| B5 | `generators/tonal_network.py` docstring | claims to be "the same idea" as `research/intervalnetwork.py` but does **not** reuse it (duplicated graph-building) | low (misleading comment) |
| B6 | `rules/progression.py:PatternMovement.loungejazz_progression2 = (4,2,5,1),` | trailing comma makes it a **tuple**, not a list, unlike every sibling | low (type inconsistency) |

---

## 3. Obsolete / stale

| # | Where | Stale fact | Reality |
|---|---|---|---|
| S1 | `README.md:325,364` | "214 passed" | **342 passed** |
| S2 | `README.md:376` | "309 commits" | **346 commits** |
| S3 | `README.md:146` | "`music21py`" | real package is `music21` (and `music21py` is a different, essentially-unused PyPI package); confusing |
| S4 | `README.md:303` | lists `examples/3voices.py` | **file missing** |
| S5 | `README.md:3` | badge "Python 3.8+" | env is 3.11 (and 3.13 per host); pyproject doesn't pin — badge is decorative/untested |
| S6 | `AGENTS.md:125` | "263 passed" | **342 passed** |
| S7 | `plans/architecture-review.md` | mermaid diagram predates flat-package + 3-layer work | rewrite or archive |
| S8 | `hermes_agent/surveillance-reports/report_2026-08-31.md` | date-stamped snapshot | will rot; move to a rolling file or link |
| S9 | `hermes_agent/decisions.md` | references `.kilo/plans/1785873858229-...` | external tooling path, not in this repo |
| S10 | `research/trainmodel.py` | "TensorFlow imports commented out" | seed is half-functional; either wire or mark clearly |

---

## 4. Layering findings (from the recent Abstract/Concrete/Absolute work)

The 3-layer plan landed cleanly (`rules/subset_network.py`, `select_chain`,
`ABS-001..005`). Review surfaced three follow-ups:

1. **`subset_network.py` re-implements metrics that already exist** — its
   `interval_vector` wraps `set_theory.py` (good), but its
   `voice_leading_distance` duplicates `rules/voice_leading.py:
   calculate_voice_leading_distance` (not good). Pick one owner.
2. **ABS methods are registered in 3 places** — `SCALE`, `GENERATOR_REGISTRY`,
   `skills/methods index`. Unavoidable (each serves a different consumer) but
   brittle; a future `register_method()` helper that updates all three in one
   call would remove drift.
3. **Abstract layer has no generator class** — `ABS-*` resolve to module
   `rules.subset_network` (functions), not a `MusicGenerator` subclass. Fine
   for walks; `ABS-003` (Z-variation) and `ABS-005` (complement) deserve
   proper generator classes when they graduate beyond the walk.

---

## 5. Improvement plan (prioritized)

### P0 — correctness + docs (safe, do now)

1. **Fix `set_prime_form`** (B1): add inversion normalization (compute normal
   form of the inversion, pick the more left-packed — mirror `set_theory.py`).
2. **De-dup set theory** (1.1): make `structures/intervals.py` and
   `rules/subset_network.py` delegate to `rules/set_theory.py`; keep
   Hindemith/delta/Bartók where they are (unique to `intervals.py`).
3. **Fix instrument constants** (B2, B3): `PIANO = 0`; drop
   `MidiInstrument.PERCUSSION` (use `MidiChannel.PERCUSSION`/`_INDEX`).
   Keep backward-compat shims only if a grep shows external users.
4. **Fix the README/AGENTS/QUICK_REFERENCE stale facts** (S1–S6): test count,
   commit count, `music21py`, missing `3voices.py` (remove from list),
   `PIANO` value.
5. **Remove `musicom_compat.pth`/`.py`** (B4): reinstall editable to drop the
   stale shim; update `decisions.md` to record the true removal.

### P1 — consolidation (structural, medium)

6. **Single harmony table** (1.2): `rules/harmony.py` exporting `KEY_OFFSET`,
   `CHORD_SHAPES`, `QUALITY_INTERVALS`, `MAJOR_DEGREES`, `PROGRESSIONS`; delete
   the `musicom_workflow.py` local copy; `tonal_network.py` imports it.
7. **Merge `movement.py` → `progression.py`** (1.3); unify the
   `voice_leading_distance` metric into one owner.
8. **Collapse `hermes_agent/`** to the operational delta (1.5); link canonical
   workflow to AGENTS.md.
9. **Dedup method docs** (1.4): pick one canonical tree for
   `methods_db.md`/`human_methods_db.md`; make `docs/` a generated mirror.

### P2 — cleanup (low risk, later)

10. **Archive/rewrite** `plans/architecture-review.md` (S7).
11. **Resolve** `research/trainmodel.py` + `intervalnetwork.py` status (S10):
    wire or mark clearly as inert.
12. **Add `register_method()`** to remove the 3-place ABS registration drift (L2).
13. **Note the vendored `lib/musicom/` copies** (1.6) in AGENTS.md.

### Explicitly NOT doing now (needs user decision)

- Deleting the `projects/` git mirror (1994 files) — it may be a deliberate
  daily-sync artifact; flagging only.
- Rewriting `musicom_workflow.compose()` to fully route through the abstract
  layer — the ABS path is additive; a full refactor is a separate change.

---

## 6. What was updated in this pass

README.md / AGENTS.md / QUICK_REFERENCE.md stale facts (test counts, commit
count, `music21py`, missing example, `PIANO`/instrument table) — see commit.
