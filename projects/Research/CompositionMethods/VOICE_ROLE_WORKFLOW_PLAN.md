# Voice-Role Workflow Plan — Phase 3 (2026-10-22)

**Status: PLAN ONLY. No structural changes made.** Review, then approve in parts.

Extends the simple workflow (`method → 1 voice → snap to scale → harmonize`)
into a **role-first, method-independent cell recipe engine**: the method decides
each voice's *role* per section FIRST, then the voice is *refined* under that
role — with per-voice/section method variation, a second independent melody
(countermelody), and tagged chromatic ornaments, all without breaking the
zero-drift / grid-lock / in-key / no-collision invariants.

---

## 0. Decisions locked this round (the four forks)

| # | Fork | Decision |
|---|---|---|
| 1 | Tiered-snap weight source | **Default from onset grid** (strong vs weak beat); method MAY tag notes to override. |
| 2 | Chromatic scope per role | **Follow the assumption**: bass/pad/harmony = zero chromatic; lead/counter = allowed (tagged). |
| 3 | Countermelody / role architecture | Countermelody was only an illustration. **The method determines the role of the voice per section FIRST, then the voice is refined.** Role is a method *output*, not a static recipe tag. |
| 4 | Depth of this document | **Written repo design plan** (this file). |

Fork 3 is the load-bearing correction: role is **not** a static column in a
recipe table. The method runs per `(voice, section)` and its first act is to
*choose a role*; the generation, snap, and harmonize stages then *obey* that
role. This is what makes the workflow genuinely method-independent — any
generator can drive role assignment, so the engine never hardcodes "voice 0 is
the lead".

---

## 1. Evaluation of the current simple workflow

In `workflows/musicom_workflow.py` + `sound/synthesis/scale_quantizer.py` +
`sound/generators/harmony_writer.py` the pipeline today is:

```
method → 1 voice (raw pitch_index, onset, velocity)
   → snap to pattern (ScaleQuantizer.quantize → nearest scale degree)
   → harmonize (chord-tone quantize + voice leading)
```

Three facts constrain the extension:

1. **Method is not really method-driven.** In `compose()` (lines 573–602) the
   fill is *hardcoded* — lead = 8th arpeggio, pad = sustained chord, bass =
   root on 1&3, arp = 16ths, drums = grid. `method` is mostly a provenance
   tag. Only the ABS-* path (`_is_abs`, lines 506–542) actually walks a real
   generator (`rules.subset_network`). `paths.py::compose_middle_out` is the
   same shape: `fill_drums / fill_anchor / fill_pad / fill_lead / fill_arp`
   are five hardcoded functions, not a recipe loop. So "method-independent"
   is not yet true at the engine level.

2. **Snap is a hard wall.** `ScaleQuantizer.quantize()` maps every value to
   the *nearest* scale degree (lines 49–62). No concept of "sometimes leave it
   chromatic." This is the rigidity to open.

3. **Harmonize is one-directional.** `HarmonyWriter` always writes harmony
   *under* a given melody (SATB styles 1–5). There is no notion of a *second
   independent melody* that must coexist with the lead.

So the extension is not "add a feature" — it is **replace the hardcoded fill
with a spec-driven, role-first cell engine**, and **replace the hard scale-wall
with a tiered pitch discipline**.

---

## 2. Architecture: role-first cell engine

Every `(voice, section)` cell flows through the same five stages with
cell-local parameters. The method is a **black-box contract** that (a) resolves
a role, then (b) emits raw `(pitch_index, onset, velocity)` tuples under that
role:

```
CellComposer.per_voice_section(method, voice_idx, section_idx, context) -> MusicUnit

  1. resolve_role   role = method.resolve_role(context)   # METHOD DECIDES ROLE FIRST
  2. generate       raw  = method.generate(context, role)  # raw pitch_index/onset/velocity
  3. snap           snapped = tiered_snap(raw, context.pattern, role)
  4. harmonize      harmonized = harmonize(snapped, context.chord, role)  # role-aware
  5. vary+embellish unit = vary(embellish(harmonized, role), role, variation_ops)
     → validate (zero-drift) → fill cell
```

**Method-independence**: stages 2–5 do not care *how* the raw came out. Markov,
tendency-masking, DPSM, FHN, Lévy, Euclid — all interchangeable because the
method only has to expose two methods: `resolve_role(context) -> str` and
`generate(context, role) -> list[(pitch_index, onset, velocity)]`. A method that
does not want to choose a role returns the default (`"lead"`), so existing
generators keep working unchanged.

**The `context` object** is the single read-only input bag every stage shares:

```python
@dataclass(frozen=True)
class CellContext:
    key: str              # "C", "Eb", ...
    pattern: str          # scale/mode name: "major", "aeolian", "phrygian_dominant", ...
    chord_tones: tuple    # current chord's absolute tones (sorted)
    register: tuple       # (lo, hi) MIDI range for this voice
    density: float        # target events per bar (0.2 sparse .. 1.0 dense)
    density_budget: float # remaining density for this voice (decremented by role choice)
    strong_beat_grid: tuple  # tick offsets that are "strong" in this section (e.g. (0, 960))
    seed: int             # master_seed ⊕ (voice_idx, section_idx) — derived, reproducible
    other_roles: frozenset  # roles already assigned to sibling voices THIS section
    counter_mode: str = "independent"  # "independent" (default) | "transform" (lead-derived)
```

`other_roles` is what lets the method make a *coherent* role choice — it can
see that the lead is already taken and pick `"counter"` instead of doubling.

### Role taxonomy (method output, not a static column)

| Role | snap | harmonize | chromatic | notes |
|---|---|---|---|---|
| **lead** | scale (tiered) | strong-beat chord quantize | yes, tagged | primary melody |
| **counter** | own scale (tiered) | strong-beat chord quantize | yes, tagged | + contrast + complementary-density constraints |
| **harmony** | chord tones only | n/a (already chord) | no | HarmonyWriter-style inner voices |
| **bass** | root + chord tones | root emphasis | no | no chromatic bass |
| **pad** | chord tones | n/a | no | sustained |
| **rhythm** | grid only | n/a | no | drums / unpitched |

The `counter` role carries two constraints the current engine lacks:
- **contrast**: counter must not double the lead (register separation + prefer
  contrary/oblique motion);
- **complementary density**: counter active when lead rests (call-and-response),
  so they don't collide. This is a hard post-check, not a soft hint.

---

## 3. Tiered pitch discipline (chromatic allowance)

Replace the binary "in-scale / out-of-scale" wall with a **structural weight**
per note:

| Weight | Definition | Pitch rule |
|---|---|---|
| **Strong** | strong-beat onset, OR chord-tone target | MUST be in-scale AND in-chord (hard snap) |
| **Weak** | off-beat, short, between two strong targets | MAY be chromatic, but MUST resolve by step |

**Weight source (fork 1)**: default is derived from the onset grid — a note
whose onset falls on a `strong_beat_grid` tick is Strong, else Weak. The method
MAY tag a note (`{"weight": "strong"}` or `{"weight": "weak"}`) to override the
grid default. No tag → grid default. This keeps the common path automatic while
leaving the door open for a method that knows a given off-beat note is
structurally important.

Chromatic non-scale pitches become legal *only* through the four classical
ornaments — each a rule, each countable, each tagged:

| Ornament | Rule | Example |
|---|---|---|
| **Chromatic passing tone** | fills a whole-step gap, half-step in travel direction | C→D = C **C♯** D |
| **Chromatic neighbor** | half-step above/below a chord tone, returns | C **D♭** C |
| **Approach note** | chromatic lead-in to a strong target | **B**→C |
| **Secondary leading tone** | raises 7th toward next chord root | **F♯**→G |

Chromatic scope per role (fork 2) is **hard**: `bass`/`pad`/`harmony`/`rhythm`
may NOT emit chromatic ornaments (the snap stage refuses to tag them); `lead`
and `counter` may. This is exactly the species-counterpoint discipline already
in the method map (056 SCCC) — the extension *uses* it without *being* it.

---

## 4. The invariant change (the part that must be airtight)

The current audit demands `pitch % 12 ∈ KEY_PCS` for every pitched note → **0
violations**. That cannot survive chromatic passing tones. New invariant:

```
every pitched note is EITHER
  (a) in-scale AND in-chord,  OR
  (b) tagged chromatic_ornament AND resolves by step to a scale tone within 1 grid step
```

Same hardness — still **0 un-tagged out-of-scale** — but the tagged set is a
countable, auditable population. Chromatic ornaments that don't resolve are
still flagged. The four existing invariants stay untouched:

- **zero-drift** — terminal silent landmark at exact cell length (unchanged)
- **grid-lock** — onsets on grid unless genre is fluid (unchanged)
- **no-collision** — dedup by `(start_tick, pitch)` (unchanged; the ornament
  stage MUST run this, see §6 pitfalls)
- **bar-attribution** — `t // BAR` floor, not round (unchanged)

---

## 5. Per-section / per-voice variation + countermelody

The role-first engine makes "different method/pattern per section or voice"
fall out naturally:

- **Per-section**: Verse uses Markov(002)+aeolian, Chorus uses
  tendency-masking(023)+ionian, same key family. This is the existing
  "Framework-First with per-section method variation" — now expressed as
  per-cell context instead of prose.
- **Per-voice**: Lead = method A, Counter = method B. Both snap to the same
  scale, then harmonize into the same chord, but B is *independent*, not
  derived from A.
- **Countermelody** is a *role*, resolved by the method (fork 3): the method
  sees `other_roles` already contains `lead`, picks `counter`, and generates an
  independent line that satisfies the contrast + complementary-density
  constraints.

The `vary` stage applies deterministic transforms (invert, retrograde,
transpose, density scale, displacement) as pure functions over a `MusicUnit`;
the `embellish` stage applies the four ornaments. Each transform is tagged so
provenance records *which* operator fired per cell.

---

## 6. File map

### New modules
| File | Responsibility |
|---|---|
| `workflows/cell_engine.py` | `CellContext`, `CellComposer.per_voice_section`, the 5-stage loop, role registry |
| `workflows/variation.py` | pure `MusicUnit` transforms: invert, retrograde, transpose, density_scale, displace |
| `rules/ornament.py` | the 4 chromatic ornaments + `resolve_by_step()` checker + tag schema |

### Modified modules
| File | Change |
|---|---|
| `sound/synthesis/scale_quantizer.py` | add `tiered_quantize(pitch, weight)` + `classify_weight(onset, strong_grid)` + `StructuralNote` tag path; keep `quantize()` for back-compat |
| `sound/generators/harmony_writer.py` | add role-aware `harmonize(melody, role=...)`; add `counter` role (contrast + complementary density); keep SATB styles 1–5 |
| `workflows/musicom_workflow.py` | replace hardcoded `compose()` fill (lines 573–602) with the `CellComposer` loop; keep `produce()`, `_fill_loop_section`, ABS-* path untouched |
| `workflows/paths.py` | (later) route `compose_middle_out` fills through `CellComposer` instead of the 5 hardcoded `fill_*` funcs |
| `rules/harmony.py` | no change — chord tables already canonical |

### New audit
| File | Responsibility |
|---|---|
| `workflows/pitch_audit.py` | revised scale/chord audit: (a) 0 un-tagged out-of-scale, (b) every tagged ornament resolves by step, (c) 0 collisions, (d) zero-drift — reports counts per voice |

The existing audit functions stay; `pitch_audit.py` is additive so the golden
hash gates (`test_harness_golden.py`, `test_realize_bridge.py`) are untouched.

---

## 7. Tiers (build order, P0 → P2)

### P0 — Role-first cell engine (replaces hardcoded fill)
`compose()` stops hardcoding lead/pad/bass/arp and becomes a recipe loop driven
by `CellComposer`. Prove it with ONE method across ONE voice, then N voices.
- Deliverable: `workflows/cell_engine.py` + `musicom_workflow.compose()` rewire.
- Gate: `test_harness_golden.py` still passes (byte-identical when a method
  emits the same hardcoded default as today — the rewire must be output-neutral
  for the default path, exactly like the `rules/realize.py` bridge was pinned).

### P1 — Tiered pitch discipline + tagged chromatic ornaments
`scale_quantizer.tiered_quantize` + `rules/ornament.py` + `workflows/pitch_audit.py`.
This is the risky correctness core — the scale/chord audit gets rewritten with
the tagged-ornament exemption.
- Gate: a chromatic-passing-tone fixture produces **0 un-tagged** and **N
  tagged+resolving** ornaments; a non-resolving ornament still FAILS.

### P2 — Variation operators + countermelody role
`workflows/variation.py` transforms + `counter` role in `harmony_writer.py` +
per-section/per-voice recipe assignment + contrast/complementary-density checks.
- Gate: a two-voice lead+counter fixture has **0 collisions**, **0 un-tagged**
  violations, and counter onsets that never double the lead.

Each tier ships with its own audit (scale/chord count, off-grid count,
zero-drift), so no tier lands "smooth but sour."

---

## 8. What I would NOT do

- ❌ Rewrite `rules/harmony.py` or `structures/` — the substrate already fits;
  this is an orchestration layer above them (same argument as PATH_LAYER_PLAN §6).
- ❌ Let the snap stage tag chromatics on `bass`/`pad`/`harmony`/`rhythm` — fork 2
  is a hard rule, not a default.
- ❌ Hand-roll a new Markov/stochastic generator — `generators/` already has
  001/002/003/012/018/023/040/079/HC-012 with real code; route to them.
- ❌ Break the golden-hash gates. The P0 rewire is output-neutral for the default
  path and pinned by `test_harness_golden.py` before anything else ships.
- ❌ Let `compose_middle_out` in `paths.py` diverge — once P0 lands, it must be
  migrated to `CellComposer` so there is exactly ONE fill mechanism in the repo.

---

## 9. Open questions — RESOLVED (2026-10-22 continued)

Resolved with the defaults recommended in §9 of the first draft. No blocking
decisions remain before P2.

### Q1 — Strong/weak grid per time signature → per-meter table + style override

Default strong-beat grids live in a per-meter table (not per-style). A style
may override (e.g. backbeat pop flips to beats 2&4):

```python
# tick offsets within one bar that count as "strong" (BAR = 1920 @ 4/4)
STRONG_GRID = {
    "4/4":  (0, 960),        # beats 1 & 3 (downbeats)
    "2/4":  (0,),            # beat 1 only
    "3/4":  (0,),            # beat 1 only
    "6/8":  (0, 960),        # two dotted-quarter pulses
    "12/8": (0, 960),
}
# STYLE_REGISTRY override: style entry may carry "strong_beats": (480, 1440)
# for backbeat genres (pop/rock/soul) — beats 2 & 4 are the strong accents.
```

Resolution order: `STYLE_REGISTRY[style]["strong_beats"]` if present, else
`STRONG_GRID[time_sig]`, else `(0,)`. The `classify_weight()` helper reads the
resolved tuple.

### Q2 — Counter derivation → both, `counter_mode` in CellContext

`counter_mode="independent"` (default): the counter is its own generative run
under the `counter` role. `counter_mode="transform"`: the counter is a
`vary`-stage transform of the lead (invert/transpose/offset), then re-snapped
to the scale and re-checked for contrast + complementary density. Both are
legal; independent is the default because it is the more genuinely
"second melody" behavior (fork 3's spirit). Transform is the cheaper,
guaranteed-harmonic option — exposed, not forced.

### Q3 — Density budget allocation → yes, `density_budget` in CellContext

The method's `resolve_role()` receives `density_budget` (the section's target
density minus what sibling voices already claimed). A method picking `lead`
with high density, or `counter` with complementary-density, must decrement the
budget so lead+counter do not double the section's target. The engine enforces
this as a soft ceiling (exceeding it is logged, not fatal), because a
genuinely dense climactic section may legitimately overshoot — but the default
stays budget-respecting.

---

## 10. Reference

- `PATH_LAYER_PLAN.md` (this dir) — the L1–L4 scale + Path C orchestrator this
  layer sits on top of.
- `LAYER_ARCHITECTURE.md` (this dir) — abstract/concrete/absolute layer split;
  `CellComposer` is concrete-layer realization.
- `sound/synthesis/scale_quantizer.py`, `sound/generators/harmony_writer.py`,
  `workflows/musicom_workflow.py` — the three files this plan modifies.
- `workflows/paths.py`, `generators/generator_registry.py` — method registry and
  impl status the engine routes through.
