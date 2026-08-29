# Composition Path Layer — Plan & Advice (2026-08-28)

**Status: PLAN ONLY. No structural changes made.** Review, then approve in parts.

Adds a routing layer on top of the existing framework (methods DB + generators +
workflow spine) that answers four questions the current setup leaves open:

1. On what **abstraction scale** does each method operate?
2. Which **sequence direction** should a piece be built in (top-down,
   bottom-up, middle-out, random)?
3. How do **genetic/iterative selection** (rule fitness or human-in-the-loop)
   wrap any path?
4. Which method to **pick**, given the factors of the task?

---

## 1. The abstraction scale (L4 → L1)

Derived from the DB's own `Memory Depth` column (Macro/Form → Meso/Phrase →
Local), split into 4 levels. Every method gets one **primary** level; some
span two (noted as `→`).

### L4 — MACRO: form, sections, tonal plans (output: skeleton)
| ID | Method | Why L4 |
|---|---|---|
| 001 | Skeleton-First Refinement | deterministic structure before detail |
| 006 | Cadence & Closure Mapping | section-end strengths |
| 007 | Narrative Arc Register Planning | peaks across columns |
| 010 | Hierarchical Diffusion | top-down multi-level expansion |
| 017 | Cascaded Diffusion Hierarchies | multi-agent form→lead→accompaniment |
| 034 | PCFG Recursion | rewrite tree = macro-form |
| 044 | Persistent Homology (PHTDA) | topology across scales |
| 049 | IFS Fractal Generation | attractor geometry = macro-form |
| 066 | GTTM-HC | prolongation tree first |
| HC-001 | Partimento Schemata | bass skeleton = spine |
| HC-006 | Big Band Shout Chorus | planned 8–16 bar architecture |
| HC-011 | Orchestration | form-level timbre plan |
| HC-016 | Drumband Showcraft | show arc (Opener→Ballad→Feature→Closer) |

### L3 — MESO: phrase, motif, loop, groove (output: cells per section)
| ID | Method | Why L3 |
|---|---|---|
| 004/005 | Prosodic Coupling/Syntax | phrase-level cadences |
| 008 | Call-Response Allocation | conversational blocks |
| 009 | Rhyme Density Control | per-phrase density |
| 012 | Euclidean Groove Locking | loop-level rhythm |
| 015 | Ostinato Constraint | loop anchor |
| 016 | Groove-Locked Patterns | genre groove loops |
| 018 | Schillinger Resultants | interference patterns |
| 021 | Cellular Automata | cell-grid evolution |
| 025 | Xenakis Sieves | periodic point sets |
| 026 | DPSM Phase-Shift | phased loops |
| 032 | Isorhythm Talea-Color | coprime motif cycles |
| 033 | Wave Function Collapse | neighborhood constraint fill |
| 056 | Species Counterpoint | phrase-level dissonance rules |
| 064 | MRFCC | lattice neighborhood potentials |
| 069 | Christoffel Words | balanced step-pattern words |
| HC-002 | Gamelan Kotekan | stratified elaboration layers |
| HC-004 | Raga-Tala | bandish phrases in tala cycle |
| HC-005 | Ewe Cross-Rhythm | timeline + support parts |
| HC-008 | Minimalist Process | cell + process states |
| HC-009 | Motivic Development | Grundgestalt → themes |
| HC-012 | Flamenco Compás | 12-beat cycle + falsetas |
| HC-013 | Georgian Polyphony | drone + woven blocks |
| HC-014 | Pygmy Hocket | interlocking cycle periods |
| HC-015 | Sacred Harp | air + dispersed harmony |
| HC-017 | Sanjo Jangdan | jangdan stages + kernel |

### L2 — VOICE/CONTOUR: one line at a time (output: melodic lines)
| ID | Method | Why L2 |
|---|---|---|
| 013 | Inversion/Retrograde | transform an existing line |
| 014 | Negative Harmony | chord-axis mirroring |
| 020 | Sound-Mass Trajectory | kinematic event clouds |
| 023 | Tendency Masking | bounded stochastic line |
| 029 | Continuous Portamento Glide | gliding voicings |
| 031 | Boids Flocking | agents as voices |
| 036 | Abelian Sandpile | avalanche density |
| 037 | FitzHugh-Nagumo Spiking | voltage → pitch contour |
| 038 | Kuramoto Phase Sync | coupled-oscillator lines |
| 040 | Perlin Noise | organic contour |
| 043 | Strange Attractors (SATM) | trajectory → line |
| 048 | Reflected Brownian Motion | particle = voice |
| 051 | Spectral Graph Laplacian | eigenvector orderings |
| 053 | Lévy Flight | heavy-tailed contour |
| 059 | ESN Reservoir | decoded state → contour |
| 061 | Gaussian Process | smooth function of time |
| 068 | CME-SSA | reaction network counts |
| 070 | Coupled Map Lattice | cluster sync → harmony |
| HC-003 | Makam Seyir | tonal journey contour |
| HC-010 | Fanfare | harmonic-series line |

### L1 — MICRO: one note → next note (output: transitions)
| ID | Method | Why L1 |
|---|---|---|
| 002 | Markov Transitions | state-1 local memory |
| 011 | Voice-Leading Graph Search | shortest chord-to-chord path |
| 022 | Markov-Constraint Wavefront | local transitions + constraints |
| 045 | Hawkes Self-Exciting | event history → next event |
| 050 | Optimal Transport Voice Leading | per-chord transport plan |
| 052 | Quantum Walk | one unitary step at a time |
| 065 | TTSMC Row Forms | aggregate note-by-note |
| 067 | Factor Oracle (FOGI) | per-symbol automaton walk |
| HC-007 | Lyric-Melody Prosody | syllable stress → single note |

**Key observation**: the scale is NOT evenly populated. L4 and L1 are
populated by the strongest, best-tested methods (001, 006, 034 vs 002, 011,
050). L2 is where the "exotic" Nature-Led methods live. A path that only uses
one level produces either all-skeleton or all-noise; **every good composition
chains at least two levels.**

---

## 2. Sequence paths (directions through the scale)

### Path A — TOP-DOWN (skeleton-first)
```
L4 skeleton → L3 sections → L2 lines → L1 micro-fills
```
Pick an L4 method, let it decide form; each level refines the previous
level's output. Deterministic, golden-testable, best for through-composed
and form-heavy work.
- Chain: `001 skeleton → 034 PCFG phrase tree → 056 SCCC per phrase → 011 voice-leading → 002 Markov fills`
- Human model: HC-001 Partimento (bass first, realize above).

### Path B — BOTTOM-UP (notes-first, induce structure)
```
L1/L2 material → cluster to motifs (L3) → group to sections (L4) → cadences
```
Generate raw material, then *discover* structure in it. Best for
corpus-driven and texture work.
- Chain: `002 Markov corpus walk → 067 FOGI automaton → 044 PHTDA topology → 006 cadence placement`
- Human model: HC-007 Prosody (syllables dictate the line, lines dictate the phrase).

### Path C — MIDDLE-OUT (anchor + spread)  ← the human default
```
L3 anchor (loop/timeline/compás/cycle) → L4 form around it, L2/L1 on top
```
Fix an invariant mid-level spine; structure grows around it, variation
grows on top. **9 of 17 human methods are middle-out** — timeline (HC-005),
compás (HC-012), tala (HC-004), jangdan (HC-017), cycle spine (HC-014),
ostinato cell (HC-008), air-in-tenor (HC-015), battery spine (HC-016),
kotekan pokok (HC-002). This is the empirically strongest default for
style-faithful composition.
- Chain: `016 groove anchor → 015 ostinato bass → 014 harmony loop → 007 register arc → 023 melody above`
- Human model: HC-005 Ewe (bell never changes; everything else orbits it).

### Path D — RANDOM/EXPLORATORY (candidates + selection)
```
parallel generation (any level) → fitness evaluation → select/mutate → repeat
```
Not a building direction but a *search*. Wraps any of A/B/C: generate K
variants of any stage, keep the best.
- Engines: 003 Genetic (fitness hook exists), 041 Ant Colony, 052 Quantum Walk, 053 Lévy Flight.
- This is where genetic/iterative selection lives — see §3.

### Path recommendation matrix
| Task | Default path |
|---|---|
| Style-faithful genre piece | **C middle-out** |
| Through-composed / cinematic / baroque | **A top-down** |
| Corpus remix / variation of existing piece | **B bottom-up** |
| Sound design / texture exploration | **D random + selection** |
| Unknown style, first attempt | **D → then C** once a good anchor emerges |

---

## 3. Genetic / iterative selection layer

### 3.1 What already exists (build on, don't fork)
- `generators/genetic.py` — `GeneticGenerator` with a **`fitness_func` callback**
  and `fitness_limit` stop condition. The callback is the entire hook needed:
  rule-based OR human-based fitness plugs in with zero changes to the class.
- `workflows/paradigm_compare.py` — already renders 3 variants of one slot
  (stochastic/rules/nature) with comparison table + provenance. Same machinery,
  K=3.
- Zero-drift `validate()` — hard fitness gate (any candidate failing it is
  killed before scoring).
- RenderPipeline → OGG — Telegram-playable candidates.

### 3.2 Two selection modes

**(a) Rule-based fitness (automatic)**
Weighted musical energy functional — the DB *already specifies this exact
design* in method 055 SAMC: "energy weights make tonal gravity, groove,
counterpoint, texture density, structure explicit and tunable." Concrete terms,
all already computable with existing code:

| Term | How | Existing asset |
|---|---|---|
| Zero-drift valid | `composer.validate()` | hard gate |
| On-grid ratio | onset ticks mod 240 == 0 | `align_rhythm.py` verification code |
| Tonal gravity | pitch-class fit vs key profile (Lerdahl–Krumhansl, DB 066) | `structures/pitch.py` |
| Voice independence | crossing/parallel checks | `rules/counterpoint.py` |
| Range/playability | `instrument_registry.by_program(p).in_range(n)` | Phase-1b registry |
| Style match | density/tempo vs STYLE_REGISTRY template | workflow spine |
| Density arc | monotonic sparse→dense across sections (HC pattern) | grid visualizer data |

Fitness = weighted sum; weights **per style** (flamenco weighs compás
alignment high; ambient weighs density-arc low and texture high).

**(b) Human-in-the-loop fitness (Axel as judge)**
Interactive Genetic Algorithm (IGA — Biles 1994, GenJam lineage), wired
through Telegram which is already connected:

```
round r:
  1. generate K candidates (K ≤ 4 — cognitive-load cap)
  2. render 15–30 s excerpt of each → OGG (Telegram-friendly, tracked format)
  3. send all K + one-line metadata (method, seed, style) to chat
  4. Axel replies with pick/ranking
  5. selection → crossover+mutation → round r+1
  6. stop: winner chosen | 3–5 rounds | plateau
```
All generations persist in `<project>/evolution/gen_<N>/` + `evolution.json`
(picks, fitnesses, seeds) → provenance sidecar gets a `path` field.

**Fatigue mitigation (the known IGA killer — Takagi 2001):**
- Cap: 4 candidates, 5 rounds, 30 s excerpts. Non-negotiable.
- After ~10 human ratings: train a **surrogate** (ridge regression: audio
  features → Axel's ratings). Surrogate pre-filters candidates; human only
  rates the uncertain ones (active learning). This is the upgrade path,
  phase 2 of the HITL layer.
- Epsilon-wildcard: always keep 1 of 4 candidates as a random outlier
  (exploration vs exploitation; prevents premature convergence on the
  judge's current taste).

### 3.3 Where evolution sits in the paths
Evolution is **orthogonal to A/B/C** — it can wrap any single step:
- Evolve the L4 skeleton (top-down path, variant forms)
- Evolve the L3 anchor (middle-out path, variant grooves) ← **highest value**
- Evolve L2 line choices within a fixed harmony
- Evolve full pieces (expensive; only with surrogate)

---

## 4. Method selector (factors → method)

The DB columns ARE the selector factors. Proposed routing table:

| Factor | Question | Routes to |
|---|---|---|
| Tonal gravity | Strict functional harmony? | Strict: 006, 011, 025, 033, 050, 056, 065, 066, 069 · Weak/organic: 023, 040, 043, 048, 053 |
| Metric binding | Grid or free time? | Grid: 012, 016, 018, 026, 032, 069 · Fluid: 020, 023, 029, 031, 040, 043 |
| Memory depth | How much coherence horizon? | Macro: 001, 034, 047, 060, 066 · Meso: 033, 056, 064 · Local: 002, 011, 022, 045 |
| Cost budget | Nightly cron vs interactive? | Cheap O(N) for cron: 002, 012, 018, 023, 040, 069 · Heavy (training/GPU): 047, 054, 057, 060, 062 — skip headless for now |
| Corpus available? | Is there source material? | Yes: 039 SMA, 044 PHTDA, 067 FOGI · No: pure generators |
| Determinism | Golden-test needed? | Seedable exact: 001, 012, 013, 018, 025, 032, 056, 065, 069 |
| Style fidelity | Human-craft flavor? | Style → HC mapping (flamenco→HC-012, gamelan→HC-002, ...) |
| Execution status | Does code exist? | Check `generator_registry` — 026/048 are spec-only today; selector must filter these |

**Selector = pure function** `(task profile) → ordered method list`. No
state, fully testable, and it makes the "why this method?" decision auditable
in provenance (`path: [016, 015, 014, 023]`, `selector_reason: {...}`).

---

## 5. Concrete examples (the plan in action)

### Example A — "Flamenco-flavored pop hybrid" (middle-out + evolution)
```
1. L3 anchor:  016 Groove-Lock → 12-beat compás timeline (HC-012 accents {3,6,8,10,12})
2. L2 harmony: 014 Negative-Harmony variant → Andalusian loop Am–G–F–E
3. L4 form:    006 Cadence Mapping → llamada/remate/cierre placement
4. L1 melody:  002 Markov on Phrygian set, bounded by 023 Tendency Masking
5. Selection:  4 variants (Markov seeds) → auto-fitness = compás-onset ratio
               + cadence resolution + range check → top-4 within ε →
               send 4 OGGs to Axel → his pick becomes the final.
```

### Example B — "Two-part invention, baroque" (top-down, zero random)
```
034 PCFG → exposition/episodes/recap phrase tree
→ 056 SCCC fills each phrase (cantus + counter)
→ 013 Inversion/Retrograde for episode material
→ 006 cadences at tree leaves
Deterministic → golden-hash testable → perfect for regression suite.
```

### Example C — "Evolving ambient mass" (bottom-up)
```
045 Hawkes point process → event cloud
→ cluster events into gestures
→ 007 register arc across clusters
→ 026 DPSM phases the texture
No skeleton exists until step 3 — structure is induced, not imposed.
```

### Example D — "Motif hunt with human judge" (pure evolution)
```
003 Genetic, genome = 8-note motif over pentatonic
Gen 1–2: rule fitness (stepwise ratio ≥ 0.7, tension→resolution present)
Gen 3:   top-4 rendered → Telegram → Axel picks
Gen 4:   winner seeds crossover+mutation; fitness re-weighted toward
         features of his pick (learned implicitly from the choice)
Gen 5:   final pick. All gens persisted, evolution.json → provenance.
```

---

## 6. Placement decision: on top, not inside

**Recommendation: add the path layer ON TOP of the framework**, as three new
workflow modules. Reasons:

1. **The substrate already fits.** UnitMatrix cells are granularity-agnostic:
   L4 methods fill section groups, L3 fills cells, L1 fills single events.
   Nothing in `structures/` needs to change.
2. **The generators already exist.** Markov, genetic, Schillinger, tendency
   masking, euclidean — the selector routes to them; it doesn't replace them.
3. **Selection is a cross-cutting concern.** Putting fitness logic inside
   generators would fork them (exactly the anti-pattern AGENTS.md forbids).
4. **Golden-test stability.** `test_harness_golden` pins byte-identical MIDI
   export. Any structural change to structures/workflows risks that; an
   orchestration layer above them cannot.

```
workflows/paths.py       # Path A/B/C/D orchestrators + SCALE registry (L1–L4)
workflows/selector.py    # (task profile) → method list; filters by registry impl status
workflows/evolution.py   # GeneticEngine wrapper: rule fitness | HITL rounds
```
**One justified in-framework touch** (extension, not restructure): add
`path` and `evolution` keys to the provenance record schema
(`workflows/provenance.py` — it takes `**kwargs` already, so zero code
change needed, only convention).

### What I would NOT do
- ❌ Rewrite methods_db.md into the scale — keep it, generate a
  `methods_by_scale.md` table from a new `SCALE` registry (auto-doc, same
  pattern as `method_table()`).
- ❌ Let the selector pick methods that have no implementation.
  `generator_registry` says 026/048 are spec-only; the selector must read
  that registry, not the DB, or it will route to dead ends (the exact
  spec-vs-code drift the assessment found).
- ❌ HITL with K>4 or excerpts >30 s. Fatigue kills IGA sessions faster than
  anything else (Takagi 2001 survey is unambiguous on this).

---

## 7. Review & advice (my assessment of the approach itself)

**The approach is sound, and your data already contains 80% of it.** The DB's
Memory Depth column IS the abstraction scale; SAMC's energy functional IS the
fitness spec; the 17 HC methods ARE the path-library (9/17 middle-out is a
real empirical finding, not coincidence — entrainment research (London 2004)
and cross-cultural ostinato studies say the same: musicians anchor on an
invariant cycle and vary around it).

Specific advice:

1. **Ship middle-out first.** It matches the strongest human-method bias in
   your own data (9/17), the STYLE_REGISTRY already holds anchor-friendly
   templates, and it degrades gracefully (a bad top layer still leaves a
   working groove). Top-down second (baroque/cinematic requests), bottom-up
   third (corpus remixes).
2. **Fitness gates hard, aesthetics soft.** Zero-drift + range + on-grid are
   hard gates (reject); everything else is weighted score. Goodhart risk: a
   rule-fitness-optimized piece sounds like a rule — keep the ε-wildcard
   candidate in every HITL round.
3. **Selector must be registry-aware.** Route by `generator_registry`
   implementation status, not DB presence. Otherwise day-1 the selector will
   recommend DPSM (026) which is spec-only — the drift bug class we just
   fixed elsewhere.
4. **HITL budget is the real constraint.** Design for ≤20 human ratings per
   week. That's ~5 IGA sessions. Log every rating — they are training data
   for the surrogate model (phase 2), and they also document taste in
   provenance (rights-relevant under the existing provenance policy).
5. **Evolution wraps steps, not pieces.** Evolving full pieces is expensive
   and produces incoherent mutants (crossover across form boundaries breaks
   macro-structure). Evolving the L3 anchor or L2 line within a fixed form
   is where IGA works in practice (that's also what GenJam did — evolve
   phrases, not songs).
6. **Keep the path layer stateless per run.** Seed everything. Every path
   run should be reproducible from `(style, path, methods, seed)` — matches
   the golden-test philosophy and makes `evolution.json` a true audit trail.
7. **Cost guard in the selector.** The 8 AI-Driven methods (042, 046, 047,
   054, 057, 060, 062, 063) mostly need training or GPU. The selector should
   carry an `executable_headless` flag per method and filter them out of
   cron jobs automatically, keeping them available for explicit selection.

---

## 8. Proposed build order (when approved)

| Step | Deliverable | Effort |
|---|---|---|
| 1 | `workflows/paths.py`: SCALE registry (L1–L4 per method) + Path C middle-out orchestrator only | small |
| 2 | `workflows/selector.py`: factor routing + registry-impl filtering + tests | small |
| 3 | `workflows/evolution.py`: rule-fitness IGA over Path C anchor (K=4, auto-select) | medium |
| 4 | HITL rounds: Telegram candidate delivery + pick capture + evolution.json | medium |
| 5 | Paths A and B orchestrators | medium |
| 6 | Surrogate model from accumulated human ratings | later |
| 7 | `methods_by_scale.md` auto-doc + AGENTS.md section | small |

Each step independently testable; steps 1–2 unblock everything else.
