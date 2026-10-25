# Registration Report — 2026-10-25

Weekly prose→code promotion (method-registration cron). Closes the prose→code gap
(LAYER_ARCHITECTURE.md) by promoting newly researched methods from
`methods_db.md` / `human_methods_db.md` into the machine-readable CODE truth
(`workflows/paths.py` METHOD_LEVELS + `generators/generator_registry.py`
GENERATOR_REGISTRY).

## Registered (13)

### Numeric algorithmic (7) — all concrete layer, spec-only (SCALE only)

| ID | Layer | Level | Module | Status |
|---|---|---|---|---|
| 119 | concrete | L4 | — (spec-only) | TDC — Tensor Decomposition Composition. needs implementation (`generators/tensor_decomposition_composer.py` TBD) |
| 120 | concrete | L3 | — (spec-only) | RMTC — Random Matrix Theory Composition. needs implementation (`generators/eigenvalue/rmtc.py` TBD) |
| 121 | concrete | L1 | — (spec-only) | IETC — Interval Exchange Transformation Composition. needs implementation (`generators/iet_composition.py` TBD) |
| 122 | concrete | L1 | — (spec-only) | HCSC — Hilbert Curve Space-Filling Composition. needs implementation (`generators/hilbert_composition.py` TBD) |
| 123 | concrete | L2 | — (spec-only) | GTBRC — Game-Theoretic Best-Response Composition. needs implementation (`generators/game_theoretic.py` TBD) |
| 124 | concrete | L2 | — (spec-only) | DPPC — Determinantal Point Process Composition. needs implementation (`generators/dpp_composition.py` TBD) |
| 125 | concrete | L1 | — (spec-only) | LDSC — Low-Discrepancy Sequence Composition. needs implementation (`generators/lds_composition.py` TBD) |

No abstract-layer numerics this week (all 7 report `concrete`), so no ABS-<n>
additions. None have a shared generator module yet → registered spec-only in
SCALE (`(level, False)`), not in GENERATOR_REGISTRY (matching the established
numeric spec-only convention: 098/100–103, 105–111, 112/114–118 are SCALE-only).

Level mapping from DB Memory Depth (contract: Macro→L4, Meso→L3, Voice/Local→L2, None→L1):
- 119 "Macro / Low-Rank Core" → L4
- 120 "Meso / Spectral" → L3
- 121 "None (State = one point)" → L1
- 122 "None (State = one grid point)" → L1
- 123 "Local / Round (profile + play history)" → L2
- 124 "Local / Cell (kernel-defined)" → L2
- 125 "None (State = index n)" → L1

### Human craft (6) — concrete (target), spec-only (SCALE + GENERATOR_REGISTRY)

| ID | Layer | Level | Module | Status |
|---|---|---|---|---|
| HC-069 | concrete (target) | L4 | — (spec-only) | Afrobeat Layer-Vamp Architecture & Interlocking Groove Craft |
| HC-070 | concrete (target) | L4 | — (spec-only) | Carnatic Kriti Composition — Sangati-Built Sahitya Architecture |
| HC-071 | concrete (target) | L3 | — (spec-only) | Chorale Harmonization (Four-Part SATB Setting) |
| HC-072 | concrete (target) | L4 | — (spec-only) | Tabla Solo Composition — Gharana Theme-and-Variation Architecture |
| HC-073 | concrete (target) | L3 | — (spec-only) | Lithuanian Sutartinės Polyphonic Craft — Secondal-Cluster Interlock |
| HC-074 | concrete (target) | L4 | — (spec-only) | Isorhythmic Motet Composition — Talea & Color Cyclic Architecture |

Level rationale (structure scope, consistent with prior HC promotions):
- L4 (piece-level form / multi-section arrangement architecture): HC-069
  (12-section layer-build arc, like HC-049 Kecak / HC-054 Bluegrass), HC-070
  (pallavi–anupallavi–charanam + sangati elaboration, like HC-065 thang),
  HC-072 (multi-section solo theme-and-variation arc), HC-074 (talea/color
  pre-compositional macro planning).
- L3 (groove / interlock / voicing / harmony craft): HC-071 (given-melody
  harmonization + voice-leading, like HC-021 species counterpoint), HC-073
  (secondal interlock + staggered canon, like HC-061 paghjella).

All HC entered in both stores per established convention: SCALE `(level, False)`
+ `GENERATOR_REGISTRY[id] = (None, None, "...")`, so `impl_status()` is False and
the selector filters them as spec-only dead ends.

## Not registered — sound production (SP-*, absolute layer; noted only)

Per contract, SP-* methods are absolute-layer and are NOT force-registered into
SCALE (`SP_METHODS` in `workflows/musicom_workflow.py` covers the implemented
render path). Recorded for the ledger:

| ID | Method | Layer | Reported candidate module | Module present? |
|---|---|---|---|---|
| SP-118 | Transient Envelope Synthesis (TES) | absolute · Post-Processing/DSP | `sound/effects/transient_shaper.py` | no |
| SP-119 | Auto-Pan / Dynamic Stereo Modulation (APMS) | absolute · Post-Processing/DSP | `sound/effects/autopan.py` | no |
| SP-120 | PhISEM Particle Percussion Physical Modeling (PPPM) | absolute · Synthesis Engines | `sound/synthesis/phisem_percussion.py` | no |
| SP-121 | Van der Pol Oscillator Synthesis (VDPS) | absolute · Synthesis Engines | `sound/synthesis/van_der_pol_synthesis.py` | no |
| SP-122 | Noise-Shaped Dither Quantization (NSDQ) | absolute · Post-Processing/DSP | `sound/render/dither.py` | no |
| SP-123 | Dynamic Convolution Synthesis (DCL) | absolute · Post-Processing/DSP | `sound/effects/dynamic_convolution.py` | no |
| SP-124 | Free-Reed Aerophone Physical Modeling (FRAP) | absolute · Synthesis Engines | `sound/synthesis/free_reed.py` | no |

None of SP-118..124 are force-registered in SCALE; none have a shared `sound/`
implementation module yet.

## Skipped (dedup / sanity gate)

None. All 13 code-target candidates (7 numeric + 6 HC) passed the gate:
standalone method file present (`method_<ID>_*.md` / `human_method_HC-*.md`)
+ DB summary-table row present.

## Test result

```
/opt/data/micromamba/envs/musicom/bin/python -m pytest tests/test_selector_step2.py tests/test_paths_step1.py -q
→ 32 passed
```

SCALE-count assertion in `tests/test_paths_step1.py::test_scale_counts_match_plan`
updated:

| Level | before | after | delta |
|---|---|---|---|
| L4 | 65 | 70 | +5 (119 numeric; HC-069/070/072/074 human) |
| L3 | 78 | 81 | +3 (120 numeric; HC-071/073 human) |
| L2 | 20 | 22 | +2 (123/124 numeric) |
| L1 | 9 | 12 | +3 (121/122/125 numeric) |

## Skill master-map index

Updated `/opt/data/hermes_persistent/skills/musicom-method-master-map/references/methods/index.md`
Master Map list with the 13 new IDs (119–125, HC-069..HC-074).

## Commit

- Repo: `/opt/data/repos/musicom`
- SHA: `586f8a3379a5cccb000ef72d0636ad328edb95a7`
- Files: `workflows/paths.py`, `generators/generator_registry.py`, `tests/test_paths_step1.py`
- Commit message: `register methods 119-125, HC-069-074: weekly prose->code promotion into SCALE and GENERATOR_REGISTRY`
- Not pushed (daily repo-sync owns pushing).
- No prose files under `projects/` committed.
