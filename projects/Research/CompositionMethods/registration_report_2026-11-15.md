# Registration Report — 2026-11-15

Weekly prose→code promotion (method-registration cron). Closes the prose→code gap
(LAYER_ARCHITECTURE.md) by promoting newly researched methods from
`methods_db.md` / `human_methods_db.md` into the machine-readable CODE truth
(`workflows/paths.py` METHOD_LEVELS + `generators/generator_registry.py`
GENERATOR_REGISTRY).

> Covers two research weeks (no 2026-11-08 registration ran): numeric 131–142,
> HC-081..092, SP-130..141.

## Registered (24)

### Numeric algorithmic (12) — 8 concrete spec-only + 4 abstract

| ID | Layer | Level | Module | Status |
|---|---|---|---|---|
| 132 | concrete | L4 | — (spec-only) | BIBDC — Balanced Incomplete Block Design Composition. needs implementation (`generators/design_blocks.py` TBD) |
| 135 | concrete | L4 | — (spec-only) | SIRC — Susceptible-Infected-Recovered Composition. needs implementation (`generators/sir_contagion.py` TBD) |
| 136 | concrete | L1 | — (spec-only) | CHC — Collatz Hailstone Composition. needs implementation (`generators/collatz_hailstone.py` TBD) |
| 137 | concrete | L4 | — (spec-only) | TMPC — Tropical (Max-Plus) Algebra Composition. needs implementation (`generators/tropical_maxplus.py` TBD) |
| 138 | concrete | L4 | — (spec-only) | HCC — Huffman Coding Composition. needs implementation (`generators/huffman_code.py` TBD) |
| 140 | concrete | L3 | — (spec-only) | LDATAC — Latent Dirichlet Allocation Texture-Archetype Composition. needs implementation (`generators/lda_topics.py` TBD) |
| 141 | concrete | L4 | — (spec-only) | ACMTPC — Arnold Cat Map Torus Permutation Composition. needs implementation (`generators/cat_map_torus.py` TBD) |
| 142 | concrete | L4 | — (spec-only) | GFNC — Generative Flow Network Composition. needs implementation (`generators/gflownet_composition.py` TBD) |
| ABS-131 | abstract | L3 | `rules.subset_network` | TDRPC — Tonality Diamond Ratio-Pool Composition (first just-intonation/microtonal method) |
| ABS-133 | abstract | L4 | `rules.subset_network` | ZRNC — Z-Relation Network Composition |
| ABS-134 | abstract | L4 | `rules.subset_network` | CSCC — Cellular Sheaf Cohomology Composition |
| ABS-139 | abstract | L4 | `rules.subset_network` | LSAC — Latin Square & Orthogonal-Array Composition |

Level mapping from DB Memory Depth (contract: Macro→L4, Meso→L3, Voice→L2,
Local→L1):
- 132 "Macro / Design" → L4
- 135 "Macro / Wave Schedule" → L4
- 136 "None (state = current integer)" → L1 (stateless one-step map)
- 137 "Macro / Form (Kleene star)" → L4
- 138 "Macro / Code Tree" → L4
- 140 "Meso / Phrase" → L3
- 141 "Macro / Form" → L4
- 142 "Macro / Reward Horizon" → L4
- 131 "Meso / Identity Trajectory" → L3 (abstract → ABS-131)
- 133 "Macro / Network Trajectory" → L4 (abstract → ABS-133)
- 134 "Macro / Section-Graph" → L4 (abstract → ABS-134)
- 139 "Macro / Full Design" → L4 (abstract → ABS-139)

131/133/134/139 are the 7th–10th abstract-layer methods (after ABS-095/099/104/
113/127 and the ABS-001..005 originals), all routed to `rules.subset_network`
→ `impl=True` in both stores. The eight concrete numerics have no shared
generator module yet (reports name `generators/*.py` candidates, none present)
→ registered spec-only in SCALE (`(level, False)`), not in GENERATOR_REGISTRY
(matching the numeric spec-only convention: 098/100–103, 105–111, 112/114–125,
126/128–130 are SCALE-only).

### Human craft (12) — concrete (target), spec-only (SCALE + GENERATOR_REGISTRY)

| ID | Layer | Level | Module | Status |
|---|---|---|---|---|
| HC-081 | concrete (target) | L4 | — (spec-only) | Gnawa Lila/Derdeba Ritual Composition — The Treq Seven-Suite Architecture |
| HC-082 | concrete (target) | L4 | — (spec-only) | Jingju (Beijing Opera) Aria Composition — Xipi/Erhuang Modes × Banshi Chains |
| HC-083 | concrete (target) | L3 | — (spec-only) | Mariachi Son Jalisciense — Sesquialtera Armonía × Parallel-Thirds |
| HC-084 | concrete (target) | L3 | — (spec-only) | Rebetiko (Greek Urban Song) — Dromos × Taximi × Dance-Rhythm |
| HC-085 | concrete (target) | L4 | — (spec-only) | Danmono (Koto Sectional Variation) — Fixed-Length Dan Architecture |
| HC-086 | concrete (target) | L4 | — (spec-only) | Steelband Panorama Arrangement — Theme-and-Variation Competition |
| HC-087 | concrete (target) | L3 | — (spec-only) | Znamenny Chant Popevka (Kokiza) Formula Assembly |
| HC-088 | concrete (target) | L3 | — (spec-only) | Bebop Contrafact Head Composition |
| HC-089 | concrete (target) | L3 | — (spec-only) | Canon — Strict Imitation & Canonic Counterpoint |
| HC-090 | concrete (target) | L3 | — (spec-only) | Kalevala-Meter Rune Song — Oral-Formulaic Parallelistic Craft |
| HC-091 | concrete (target) | L3 | — (spec-only) | Mongolian Urtiin Duu (Long Song) — Shilber Skeleton × Khooslol Ornament |
| HC-092 | concrete (target) | L4 | — (spec-only) | Gospel Music Vamp & Modulation-Ladder Arrangement |

Level rationale (structure scope, consistent with prior HC promotions):
- L4 (piece-level form / multi-section arrangement architecture): HC-081
  (seven-mlouk treq ritual suite chain S0→S8, like HC-069 Afrobeat), HC-082
  (banshi aria chain 导板→回龙→慢板→原板→流水→散板, like HC-070 kriti),
  HC-085 (N-dan sectional-variation, like HC-066 ground-bass set / HC-072 tabla),
  HC-086 (Panorama Intro→Statement→Variations→Jam→Coda, like HC-011),
  HC-092 (verse→chorus→vamp→tag→shout song-form architecture, like HC-069).
- L3 (groove / interlock / voicing / melody-over-changes / counterpoint /
  formula craft): HC-083 (sesquialtera hemiola + parallel-thirds, like HC-058
  samba / HC-053 bossa), HC-084 (dromos song craft, like HC-057 fado),
  HC-087 (popevka formula assembly, like HC-068 figurenlehre), HC-088 (head
  melody over borrowed changes, like HC-009 motivic), HC-089 (dux/comes
  counterpoint, like HC-021 species), HC-090 (oral-formulaic line craft, like
  HC-039 Irish), HC-091 (skeleton + ornament vocal craft, like HC-027 throat
  singing).

All HC entered in both stores per established convention: SCALE `(level, False)`
+ `GENERATOR_REGISTRY[id] = (None, None, "...")`, so `impl_status()` is False and
the selector filters them as spec-only dead ends.

## Not registered — sound production (SP-*, absolute layer; noted only)

Per contract, SP-* methods are absolute-layer and are NOT force-registered into
SCALE (`SP_METHODS` in `workflows/musicom_workflow.py` covers the implemented
render path). Recorded for the ledger:

| ID | Method | Layer | Reported candidate module | Module present? |
|---|---|---|---|---|
| SP-130 | Colored Noise Synthesis (CNS) | absolute · Synthesis Engines | `sound/generators/complex_noise.py` | yes |
| SP-131 | Two-Mass Vocal Fold Physical Modeling (TMVF) | absolute · Synthesis Engines | `sound/synthesis/vocal_fold_model.py` | no |
| SP-132 | Rotary Speaker Doppler-AM Spatialization (RSDA) | absolute · Post-Processing/DSP | `sound/effects/rotary_speaker.py` | no |
| SP-133 | Theremin Heterodyne Synthesis (THS) | absolute · Synthesis Engines | `sound/synthesis/theremin.py` | no |
| SP-134 | Conical Single-Reed Saxophone (CSRB) | absolute · Synthesis Engines | `sound/synthesis/conical_reed.py` | no |
| SP-135 | WaveNet Autoregressive Sample Synthesis (WNAS) | absolute · Synthesis Engines | `sound/synthesis/wavenet_synthesis.py` | no |
| SP-136 | Syahi-Loaded Tension-Modulated Membrane (SLTM) | absolute · Synthesis Engines | `sound/synthesis/tabla_membrane.py` | no |
| SP-137 | Magnetic Tape Echo Physical Modeling (TEPM) | absolute · Post-Processing/DSP | `sound/effects/tape_echo.py` | no |
| SP-138 | Struck-Tine Electromechanical Piano (STEPS) | absolute · Synthesis Engines | `sound/synthesis/rhodes_ep.py` | no |
| SP-139 | Conical Double-Reed Bore (CDRB) | absolute · Synthesis Engines | `sound/synthesis/double_reed.py` | no |
| SP-140 | Schroeder Reverberator (SRB) | absolute · Post-Processing/DSP | `sound/effects/reverb.py` | yes (AlgorithmicReverb) |
| SP-141 | Supersaw Oscillator Stack Synthesis (SOSS) | absolute · Synthesis Engines | `sound/synthesis/supersaw_swarm.py` | yes (SupersawSwarm) |

None force-registered into SCALE. Three (SP-130/140/141) have a shared `sound/`
antecedent module already present; the other nine are genuinely new candidates
(no shared module yet).

## Skipped (dedup / sanity gate)

None. All 24 code-target candidates (12 numeric + 12 HC) passed the gate:
standalone method file present (`method_<ID>_*.md` / `human_method_HC-*.md`)
+ DB summary-table row present (`methods_db.md` rows 141–152;
`human_methods_db.md` rows 87–98). SP-130..141 also verified (sound_method files
+ `methods_db.md` rows 344–355) but are noted-only by design.

## Test result

```
/opt/data/micromamba/envs/musicom/bin/python -m pytest tests/test_selector_step2.py tests/test_paths_step1.py -q
→ 32 passed
```

SCALE-count assertion in `tests/test_paths_step1.py::test_scale_counts_match_plan`
updated:

| Level | before | after | delta |
|---|---|---|---|
| L4 | 77 | 91 | +14 (132/135/137/138/141/142 numeric; ABS-133/134/139 abstract; HC-081/082/085/086/092 human) |
| L3 | 84 | 93 | +9 (140 numeric; ABS-131 abstract; HC-083/084/087/088/089/090/091 human) |
| L2 | 22 | 22 | 0 |
| L1 | 13 | 14 | +1 (136 numeric) |

## Skill master-map index

Updated `/opt/data/hermes_persistent/skills/musicom-method-master-map/references/methods/index.md`
Master Map list with the 24 new IDs (ABS-131, 132, ABS-133, ABS-134, 135–138,
ABS-139, 140–142, HC-081..HC-092).

## Commit

- Repo: `/opt/data/repos/musicom`
- Files: `workflows/paths.py`, `generators/generator_registry.py`, `tests/test_paths_step1.py`
- Commit message: `register methods 131-142, HC-081-092: weekly prose->code promotion into SCALE and GENERATOR_REGISTRY`
- Not pushed (daily repo-sync owns pushing).
- No prose files under `projects/` committed (daily sync owns those).
