# Harmonization Method Plan — method-driven harmony (abstract → concrete → absolute)

Design reference. Non-executive until approved. Root question: *the last two
nightly compositions came out harmonically near-identical. Harmony today is a
fixed post-process, not a selected method. Make harmonisation selectable per
piece, driven by a randomly chosen method, able to run with or without the
melody method's phase-1 result, ordered abstract → concrete → absolute.*

## Status

- **P0 BUILT (2026-11-23).** `workflows/harmony_plan.py` (Chord / HarmonyPlan),
  `workflows/harmony_method.py` (contract + 4 harmonisers + profiles), per-bar
  snap in `realize_spine`, per-bar fillers in `cell_engine`, `compose(harmonizer=…)`
  opt-in, `tests/test_harmony_method.py` (17 tests). Suite green (786 passed,
  1 skipped), default path byte-neutral (golden hashes unchanged). Verified
  probe: default = static per-section roots `[48,48,48,48][55,55,55,55]…` vs
  `functional` = per-bar I–V–vi–IV `[48,55,57,53,…]` vs `abstract` = subset walk
  `[48,48,48,48,50,48,48,50]`; all zero-drift.
- **P1 BUILT (2026-11-23).** `plan_from_method(method_id, …, seed)` derives a
  `HarmonyPlan` from the method's process over chord space: Markov 002/010 →
  weighted degree walk, Tendency 023 → harmonic band, Skeleton 001 → strong/weak;
  each forces V→I. `source="template"` methods (012/018/040/079/003) fall back to
  their profile's template harmoniser (the "without phase-1" path). Suite 790
  passed, 1 skipped. Commits `d3a91fe` (P0) + `b9f1a2b` (P1).
- **P2 BUILT (2026-11-23).** `select_harmonizer(method_id, rng)` draws from the
  four templates + (method-source methods) a `"method:<id>"` option; rhythm/contour
  methods auto-fallback to template. `harmonizer_plan()` accepts `"method:<id>"`.
  Composition cron prompt wired (step 5 + REPORT CONTRACT; `jobs.json`). Cron still
  paused on HTTP 402 credits — resumes via the 2026-12-06 job. Commit `c6b990d`.

---

## 0. Diagnosis — why two songs harmonise alike

Trace the harmonisation data flow today:

1. `compose()` / `build_framework()` lays the **I–V–vi–IV template** across
   intro/verse/chorus/bridge/outro (AGENTS.md, `workflows/musicom_workflow.py`).
   `ctx.chord_tones` is populated from that template — **the same four degrees
   every night**, key/transposition aside.
2. `realize_spine.realize()` → `_snap()` quantises every strong beat *to
   `ctx.chord_tones`*. So the harmony is literally the template, regardless of
   which composition method was selected.
3. The method adapters (`workflows/method_adapters.py`) all emit **monophonic
   `RawNote`** per role; the "harmony" role is just another line snapped to the
   same `chord_tones`. No method emits a chordal layer or a progression.
4. Two real harmonisation assets exist but sit OFF the main spine:
   - `sound/generators/harmony_writer.py::HarmonyWriter` — SATB rule-based
     harmoniser (styles 1–5), **melody-derived** (`choose_chords` reads the
     melody, then voice-leads under it), deterministic.
   - `sound/generators/chord_arranger.py::ChordDrivenArranger` —
     **progression-derived** 3-track arranger (chord/arp/bass, 8 macros + 16-step
     lanes), UNA-style.
5. `rules/subset_network.py` (ABS-001…005) is the **abstract** harmony-design
   layer (progression as subset walk / tension curve / Z-swap / parsimonious VL /
   complement) — present, and already proven in the Celtic/pop subset-walk
   projects, but invoked only when an ABS method is *the* composition method.

**Conclusion:** harmonisation is (a) a fixed key-agnostic template, (b) applied
uniformly in the realisation half, ignoring the selected method. It is not a
selectable axis. That is the duplication the two songs expose.

---

## 1. The design — harmonisation as a full method chain

Harmonisation should be the **same abstract → concrete → absolute journey the
melody already walks**, but with its own selected method. Three layers:

| layer | produces | assets | output shape |
|---|---|---|---|
| **abstract** | WHAT chords (the harmony plan) | `rules/subset_network.py` ABS-001…005 · functional Roman-numeral template · `HarmonyWriter.choose_chords` (melody-derived) | per-bar progression / tension curve / subset-ID walk | 
| **concrete** | HOW to voice into notes (raw → rules) | `HarmonyWriter` (SATB) · `ChordDrivenArranger` (chord/arp/bass) · pad · comp · arp · counter | harmony note events |
| **absolute** | sound | `sound/` SP-\* (FluidSynth / synthesis / effects) | stems → WAV/OGG (existing, unchanged) |

The abstract layer needs a canonical output object — **`HarmonyPlan`**: a
per-bar sequence of `(root/degree, quality-or-subset-id, tension)` plus optional
per-bar voicing register. Today that data is implicit in `ctx.chord_tones`
(single chord per *section*, not per bar). Generalising `chord_tones` into a
per-bar `HarmonyPlan` is the single most load-bearing unification — it is what
both the abstract layer and the concrete voice-leaders already need in slightly
different forms.

### 1.1 The two harmonisation "sources" (includes / without phase-1)

The user's "either including or without the phase-1 result" is a **source
flag** on the harmonisation method, not a new phase:

- **`source = "method"`** (include phase-1 result): the harmony plan is *derived
  from the selected composition method's phase-1 raw* — the method's `generate()`
  output is re-read as a harmonic projection, not as a melody. Method-specific
  meaning (see §2).
- **`source = "template"`** (without phase-1): the harmony plan comes from a
  functional template (I–V–vi–IV + cadence), or an abstract ABS walk, or the
  melody (`HarmonyWriter.choose_chords`). The melody method's raw output is
  never touched for harmony.

Both sources converge on the same `HarmonyPlan` → concrete voice-lead →
realise → absolute pipeline. Only the *origin* of the plan differs.

### 1.2 Generic pipeline (abstract → concrete → absolute)

```
0. select composition method M            (existing)
1. select harmonisation method H          (NEW, randomly chosen)
      H = (abstract_rule, concrete_mode, source∈{method,template})

2. ABSTRACT — build HarmonyPlan
      source=method   → H.plan_from_method(M.generate(ctx, role))   # §2
      source=template → H.plan_from_template(key, form, seed)       # ABS / roman / melody
      → HarmonyPlan: [(root, quality|subset, tension) per bar]

3. CONCRETE — voice the plan (phase 1 raw)
      H.voice(plan, ctx, lead?, M.phase1?) → raw harmony notes (unquantised)

4. CONCRETE — realise (phase 2 rules)      [shared, unchanged realise_spine]
      snap(scale+chord) → voice-leading correct → grid-lock → dedup → landmark

5. ABSOLUTE — SP-* production               [existing]
   (not part of this plan; listed for ordering completeness)
```

Steps 3–4 are exactly the existing two-phase split (`musicom-composition-workflow`),
but applied to the **harmony role** with `H` driving the raw match instead of a
fixed chord-tone quantise.

---

## 2. Flexible phases per method — do we need them?

**Yes — and the phase semantics are a property of the method, not a global
constant.** Today every method is force-fitted into "emit monophonic RawNote,
snap to a fixed chord." That is the core over-constraint. Each method's phase-1
output has a *natural* harmonic reading; forcing one reading onto all methods is
what flattens the harmony.

| method | natural phase-1 harmonic reading | `source=method` meaning | phase structure needed |
|---|---|---|---|
| **002 MarkHyp / 010 HD** | transition weights over pitch index → **chord-transition table** | walk the chord space with the same weights → progression | melodic phase-1 + a *second* chordal phase-1 (two interpretations of one walk) |
| **023 Tendency Masking** | corridor bounds `L(t),U(t)` → **harmonic band** (which scale degrees are live when) | harmonic window per bar from corridor | corridor phase-1 → quantise band → progression |
| **001 Skeleton-First** | strong-beat chord tones / weak passing | already chord-aware → emit progression explicitly | phase-1 = progression + melody skeleton together |
| **018 Schillinger / 012 Euclid** | **rhythm only** (resultant / onset grid) | no harmonic content — harmony must come from template/melody | `source=method` is a no-op → force `template` |
| **040 Perlin / 079 Tintin.** | smooth contour / stepwise walk | contour → voice-lead under it, not a progression | melody-derived harmony (needs `choose_chords`) |
| **ABS-001…005** | the walk/curve IS the harmony plan | `where source=template` already *is* the abstract layer | abstract phase-1 = HarmonyPlan directly |

**Consequence:** the harmonisation method descriptor carries a
**`phase_semantics`** field from a small enum:

- `progression` — phase-1 projects onto a per-bar chord sequence (Markov, Skeleton, Tendency).
- `band` — phase-1 bounds a harmonic window (Tendency corridor).
- `rhythm` — phase-1 is rhythm-only; harmony must be sourced externally (Euclid, Schillinger).
- `contour` — phase-1 is a line; harmonise under it via voice-leading (Perlin, Tintin., any lead).
- `none` — `source=method` unsupported; force `source=template`.

This is *not* "more phases everywhere" — it is **one fixed abstract→concrete→absolute
journey, plus a per-method decision about where the `HarmonyPlan` comes from**.
The realisation (concrete phase-2: snap/voice-lead/grid/landmark) stays ONE
shared spine for every method. Only the plan *origin* is method-flexible.

---

## 3. Priority tiers

### P0 — Harmonisation as a selectable axis (the mechanism)

1. Introduce `HarmonyPlan` (per-bar `(root, quality|subset, tension[, register])`)
   in a new `workflows/harmony_plan.py` (pure, engine deps only).
2. Introduce `HarmonizationMethod` contract (parallel to `CellMethod`):
   ```
   plan(ctx, source="template", phase1=None) -> HarmonyPlan      # abstract
   voice(plan, ctx, role="harmony") -> Sequence[MethodOutput]     # concrete, phase-1 raw
   ```
   Plus `source ∈ {"method","template"}` and `phase_semantics` descriptors.
3. **Four concrete harmonisors** (fold existing assets, no re-invention):
   - `FunctionalHarmonizer` — I–V–vi–IV + cadence → `HarmonyPlan`; `voice` via pad/comp (the current default path, re-encoded).
   - `SATBHarmonizer` — wraps `HarmonyWriter` (melody-derived `choose_chords` + voice-led SATB).
   - `ChordArpHarmonizer` — wraps `ChordDrivenArranger` (progression-driven chord/arp/bass).
   - `AbstractHarmonizer` — wraps `rules.subset_network` ABS-001…005 (walk/curve/Z/parsimonious/complement → `HarmonyPlan`).
4. Wire the `realize_spine`/`CellContext` so `chord_tones` is looked up **from a
   `HarmonyPlan` per bar**, not a single section chord. This is the load-bearing
   data-flow change; keep it backward-compatible (single-chord section = a
   1-bar plan).

**Gate (hard):** byte-neutrality — the default path (`FunctionalHarmonizer` +
existing fillers) must reproduce `compose()` output byte-for-byte, pinned by the
existing `GOLDEN_SHA256` / `ABS_GOLDEN_SHA256` golden gates. Do this the same
way `DefaultMethod` kept `compose()` byte-identical in Phase 4 P0.

### P1 — Per-method `source=method` adapters (the flexible phase semantics)

5. Build the §2 `phase_semantics` table as a real registry
   (`HARMONY_PROFILES = {method_id: {source, phase_semantics, harmonizer}}`).
6. For the methods with a natural `progression`/`band` reading (002/010, 023,
   001), add `plan_from_method(phase1) -> HarmonyPlan` — the *second* harmonic
   interpretation of their phase-1 output. For `rhythm`/`contour` methods, the
   profile forces `source=template` (harmonise externally).
7. Unit-probe each `plan_from_method`: assert the produced `HarmonyPlan` is
   in-key and cadences V→I (or the method's home bias), mirroring the
   `abs002-subset-walker` verification contract.

### P2 — Random harmonisation selection in the cron + drift guard

8. The nightly composition cron randomly draws `H` (from the four harmonisors),
   independent of the melodic method `M` — breaking the harmonic monotony that
   produced the two lookalike songs. Pick distribution: ~1/4 functional (default
   baseline), ~1/4 SATB, ~1/4 chord-arp, ~1/4 abstract.
9. When `H.source == "method"` AND `M` is `rhythm`/`contour`, auto-fallback to
   `template` (never silently drop harmony).
10. Report the chosen harmoniser + source + a one-line "why different from last
    night" in `REPORT.md`, so drift is auditable, not silent.

### Explicitly out of scope
- Absolute-layer sound production (SP-\*) — already exists; unchanged.
- Changing the melodic method contract — harmonisation is additive.

---

## 4. Abstract / concrete / absolute work-order summary (the deliverable)

> Harmonisation follows the methods, not a fixed post-process. Each selected
> method declares (a) what its phase-1 output *means* harmonically
> (`phase_semantics`), and (b) whether harmony is sourced from that phase-1
> (`source=method`) or from a template/melody (`source=template`). Regardless of
> source, everything flows through the ONE abstract → concrete → absolute spine:
> build a `HarmonyPlan` (abstract) → voice it into raw notes (concrete phase-1)
> → realise via the shared snap/voice-lead/grid/landmark (concrete phase-2) →
> SP-\* render (absolute). Flexible phases are needed, but only at the plan
> *origin* — the realisation spine stays single and shared.

---

## 5. File map

- `workflows/harmony_plan.py` — `HarmonyPlan`, `HarmonyPlan.chord_at(bar)`.
- `workflows/harmony_method.py` — `HarmonizationMethod` contract, `Harmonizer`s
  (functional / SATB / chord-arp / abstract), `HARMONY_PROFILES`, `plan_from_method`.
- `workflows/realize_spine.py` — consume `HarmonyPlan` per bar (backward-compatible).
- `workflows/method_adapters.py` — optional `plan_from_method` hooks for 002/010/023/001.
- `tests/test_harmony_method.py` — byte-neutrality golden gate + per-method plan probes.

Existing assets reused verbatim: `sound/generators/harmony_writer.py`,
`sound/generators/chord_arranger.py`, `rules/subset_network.py`.