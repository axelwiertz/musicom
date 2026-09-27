# Musicom Method Registration Report — 2026-09-27

Weekly prose→code promotion (SCALE registry + generator_registry), closing the
prose→code gap (LAYER_ARCHITECTURE.md). Ran from `/opt/data/repos/musicom` with
`/opt/data/micromamba/envs/musicom/bin/python`.

Scope: reports that landed since the last run (`registration_report_2026-09-20.md`,
which covered numeric 086–091, HC-035–040, SP-072–075/087–089). New this week:
5 numeric (093–097), 7 HC (HC-041–047), 5 SP (SP-092–096).

## Registered — numeric algorithmic (SCALE + GENERATOR_REGISTRY)

| ID | Method | Layer | Level | Module | Notes |
|---|---|---|---|---|---|
| 093 | Percolation Process Network Criticality (PPNC) | concrete | L3 | None | spec-only — needs implementation (`generators/percolation_criticality.py`) |
| 094 | Apollonian Circle Packing Composition (ACPC) | concrete | L3 | None | spec-only — needs implementation (`generators/apollonian_generator.py`) |
| ABS-095 | Contour Theory Composition (CTC) | abstract | L3 | `rules.subset_network` | first abstract-layer numeric method — registered ABS-style (like ABS-001..005) |
| 096 | Dynamic Time Warping Composition (DTWC) | concrete | L3 | None | spec-only — needs implementation (`generators/dtwc_morph.py`) |
| 097 | Maximum Entropy Composition (MaxEnt-C) | concrete | L4 | None | spec-only — needs implementation (`rules/maxent.py` + `generators/maxent_generator.py`) |

Levels from DB Memory Depth:
- 093 "Meso / Cluster Lattice" → L3
- 094 "Meso / Apollonian Tree" → L3
- 095 "Meso / Contour Segment" → L3 (abstract layer → ABS-095)
- 096 "Meso / Warp Path" → L3
- 097 "Macro / Boltzmann-Gibbs Ensemble" → L4

## Registered — human craft (HC-*, concrete (target) → SCALE + GENERATOR_REGISTRY)

| ID | Method | Layer | Level | Module | Notes |
|---|---|---|---|---|---|
| HC-041 | Gagaku Kangen Orchestral Stratification & Jo-Ha-Kyū Acceleration | concrete (target) | L4 | None | spec-only (Jo-Ha-Kyū macro-form arc: Netori→Jo→Ha→Kyū→Tomede) |
| HC-042 | Andean Sikuri Hocket & Communal Tropa Craft (Ira-Arka Interlocking) | concrete (target) | L3 | None | spec-only (AABBCC strophic hocket interlock) |
| HC-043 | Cante Alentejano Choral Stratification & Parallel-Third Descant | concrete (target) | L3 | None | spec-only (Ponto–Alto–Baixos strophic parallel-third craft) |
| HC-044 | Zulu Isicathamiya/Mbube A Cappella Choral Craft | concrete (target) | L3 | None | spec-only (bass-root cyclic grid + block voicing) |
| HC-045 | Ethiopian Qañat Kiñit Modal System — Azmari Wax-and-Gold | concrete (target) | L3 | None | spec-only (pentatonic mode + ostinato + call-response) |
| HC-046 | Javanese Gamelan Gending Composition — Colotomic & Pathet | concrete (target) | L4 | None | spec-only (colotomic macro architecture: Buka→Mérong→Ngelik→Ompak→Minggah→Suwuk) |
| HC-047 | Barbershop Quartet Voicing & Overtone Ring Craft | concrete (target) | L3 | None | spec-only (close-harmony voicing + circle-of-fifths grid) |

Level rationale (structure scope, consistent with prior HC promotions):
- HC-041 (Jo-Ha-Kyū multi-section macro arc), HC-046 (colotomic multi-section
  architecture) → L4.
- HC-042/043/044/045/047 (phrase/cyclic/ostinato/voicing/modal craft) → L3.

All HC entered in both stores per established convention: SCALE `(level, False)`
+ `GENERATOR_REGISTRY[id] = (None, None, "...")`, so `impl_status()` is False
and the selector filters them as spec-only dead ends.

## Not registered — sound production (SP-*, absolute layer; noted only)

Per contract, SP-* methods are absolute-layer and are NOT force-registered into
SCALE (`SP_METHODS` in `workflows/musicom_workflow.py` covers the implemented
render path). Recorded for the ledger:

| ID | Method | Layer | Reported candidate module | Module present? |
|---|---|---|---|---|
| SP-092 | Scalar Auxiliary Variable Nonlinear String Synthesis (SAV-NSS) | absolute · Synthesis Engines | `sound/synthesis/sav_string.py` | no |
| SP-093 | Phase-Aligned Formant Synthesis (PAF) | absolute · Synthesis Engines | `sound/synthesis/paf.py` | no |
| SP-094 | Through-Zero Frequency Modulation Synthesis (TZFM) | absolute · Synthesis Engines | `sound/synthesis/tzfm.py` | collision — path occupied by SP-077 gear replication |
| SP-095 | Tonewheel Electromagnetic Modeling Synthesis (TWEMS) | absolute · Synthesis Engines | `sound/synthesis/twems.py` | no |
| SP-096 | Hard Sync Oscillator Synthesis (HSOS) | absolute · Synthesis Engines | `sound/synthesis/hard_sync.py` | no |

*(Note: SP-094's candidate path `sound/synthesis/tzfm.py` already exists but
belongs to SP-077's Korg Prologue Elixir TZFM gear replication — same collision
pattern as prior SP prose-vs-gear entries. SP-094 itself has no dedicated
implementation. None of SP-092..096 are force-registered in SCALE.)*

## Skipped (dedup / sanity gate)

- **092 (DLACG — Diffusion-Limited Aggregation Fractal Growth)** — has a DB
  summary-table row (methods_db.md line 102) but NO standalone
  `method_092_*.md` file and NO `report_092.md`. Fails gate (a): missing
  standalone method file. Historical gap (research job likely interrupted after
  the DB row landed). Not registered.

All 17 candidates that passed gate have: standalone method file present + DB
summary-table row present.

## Master map index

`/opt/data/hermes_persistent/skills/musicom-method-master-map/references/methods/index.md`
updated — Master Map list now includes 093, 094, ABS-095, 096, 097 and
HC-041..HC-047.

## Test gate

```
/opt/data/micromamba/envs/musicom/bin/python -m pytest tests/test_selector_step2.py tests/test_paths_step1.py -q
→ 32 passed in 3.52s
```

Count assertions in `tests/test_paths_step1.py::test_scale_counts_match_plan` updated:

| Level | before | after | delta |
|---|---|---|---|
| L4 | 37 | 40 | +3 (097 numeric; HC-041/046 human) |
| L3 | 52 | 61 | +9 (093/094/ABS-095/096 numeric; HC-042/043/044/045/047 human) |
| L2 | 20 | 20 | — |
| L1 | 9 | 9 | — |

## Commit

- Repo: `/opt/data/repos/musicom`
- Files: `workflows/paths.py`, `generators/generator_registry.py`, `tests/test_paths_step1.py`
- Commit message: `register methods 093-097, HC-041-047: weekly prose->code promotion into SCALE and GENERATOR_REGISTRY`
- Not pushed (daily repo-sync owns pushing).
- No prose files under `projects/` committed.
