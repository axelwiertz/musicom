# Registration Report — 2026-10-18

Weekly prose→code promotion (method-registration cron). Closes the prose→code gap
(LAYER_ARCHITECTURE.md) by promoting newly researched methods from
`methods_db.md` / `human_methods_db.md` into the machine-readable CODE truth
(`workflows/paths.py` METHOD_LEVELS + `generators/generator_registry.py`
GENERATOR_REGISTRY).

## Registered (14)

### Numeric algorithmic (7)

| ID | Layer | Level | Module | Status |
|---|---|---|---|---|
| 112 | concrete | L3 | — (spec-only) | CADDC — Costas Array Distinct-Displacement Composition. needs implementation (`generators/costas_array_generator.py` TBD) |
| ABS-113 | abstract | L3 | `rules.subset_network` | PCFSC — Pitch-Class Fourier Spectrum Composition. implemented (abstract path, like ABS-001..005/095/099/104) |
| 114 | concrete | L4 | — (spec-only) | FSBC — Farey–Stern–Brocot Composition. needs implementation (`generators/farey_composer.py` TBD) |
| 115 | concrete | L4 | — (spec-only) | KORC — Keplerian Orbital Resonance Composition. needs implementation (`generators/kepler_orbit_composer.py` TBD) |
| 116 | concrete | L3 | — (spec-only) | PNC — Petri Net Composition. needs implementation (`generators/petri_net_composition.py` TBD) |
| 117 | concrete | L4 | — (spec-only) | PSOC — Particle Swarm Optimization Composition. needs implementation (`generators/metaheuristic_psoc.py` TBD) |
| 118 | concrete | L4 | — (spec-only) | D3PM-C — Discrete Denoising Diffusion Probabilistic Model Composition. needs implementation (`generators/d3pm_generator.py` TBD) |

Levels chosen from DB Memory Depth (Macro→L4, Meso→L3): 112 Meso/Array Order→L3,
113 Meso/Phase Trajectory→L3, 114 Macro/Tree→L4, 115 Macro/Orbital Period→L4,
116 Meso/Net State→L3, 117 Macro/Global Optimum→L4, 118 Macro/Denoising Trajectory→L4.

### Human craft (7)

| ID | Layer | Level | Module | Status |
|---|---|---|---|---|
| HC-062 | concrete (target) | L4 | — (spec-only) | Twelve-Tone Serial Composition — Dodecaphonic Row-Based Architecture |
| HC-063 | concrete (target) | L3 | — (spec-only) | Improvisation-to-Notation Composition Workflow |
| HC-064 | concrete (target) | L3 | — (spec-only) | Funk Groove Construction |
| HC-065 | concrete (target) | L4 | — (spec-only) | Thai Piphat Thang Elaboration |
| HC-066 | concrete (target) | L4 | — (spec-only) | Ground-Bass Variation Set — Chaconne & Passacaglia |
| HC-067 | concrete (target) | L3 | — (spec-only) | Call-and-Response (Antiphonal) Composition |
| HC-068 | concrete (target) | L3 | — (spec-only) | Musical-Rhetorical Figures Composition (Figurenlehre) |

All HC spec-only (no shared generator module yet). Level assigned from method
nature/architecture per the Macro→L4 / Meso→L3 heuristic (human DB has no Memory
Depth column): full-work/form architecture → L4; groove/gesture/phrase craft → L3.

## Skipped (reason)

- **SP-056..SP-075, SP-087..SP-117 (51 absolute-layer methods)** — NOT SCALE
  methods by design. Absolute layer is handled by `SP_METHODS` in
  `workflows/musicom_workflow.py` + the daily sound-research job. Candidate
  `sound/` modules referenced in these reports are almost entirely not yet
  implemented (only `sound/synthesis/tzfm.py` and `sound/effects/spectral_gate.py`
  exist, both already adopted into SP_METHODS). Recorded as absolute/implemented-path,
  not force-registered into SCALE.
- No sanity-gate skips: every numeric/HC candidate had both its standalone method
  file (`method_*_*.md` / `human_method_*.md`) and a DB summary-table row.

## Test result

`python -m pytest tests/test_selector_step2.py tests/test_paths_step1.py -q` →
**32 passed**. SCALE-count assertion in `tests/test_paths_step1.py` updated
(L4 58→65, L3 71→78) to reflect the 14 new entries.

## Skill master-map index

Updated `/opt/data/hermes_persistent/skills/musicom-method-master-map/references/methods/index.md`
Master Map list with the 14 new IDs.

## Commit

`f88d81bc0a1d52a80c620ff535544d17ce3fccf3` — "register methods 112-118, HC-062-068:
weekly prose->code promotion into SCALE and GENERATOR_REGISTRY"
(3 files: `workflows/paths.py`, `generators/generator_registry.py`, `tests/test_paths_step1.py`).
Not pushed (daily repo-sync autopushes).
