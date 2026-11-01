# Registration Report — 2026-11-01

Weekly prose→code promotion (method-registration cron). Closes the prose→code gap
(LAYER_ARCHITECTURE.md) by promoting newly researched methods from
`methods_db.md` / `human_methods_db.md` into the machine-readable CODE truth
(`workflows/paths.py` METHOD_LEVELS + `generators/generator_registry.py`
GENERATOR_REGISTRY).

## Registered (11)

### Numeric algorithmic (5) — 4 concrete spec-only + 1 abstract

| ID | Layer | Level | Module | Status |
|---|---|---|---|---|
| 126 | concrete | L4 | — (spec-only) | KTC — Knight's Tour Composition. needs implementation (`generators/knight_tour_composition.py` TBD) |
| ABS-127 | abstract | L3 | `rules.subset_network` | SGNC — Sprague-Grundy Nimber Composition (abstract layer, routed like ABS-095/099/104/113) |
| 128 | concrete | L4 | — (spec-only) | VESC — Van Eck Sequence Composition. needs implementation (`generators/van_eck.py` TBD) |
| 129 | concrete | L4 | — (spec-only) | ABGC — Artin Braid Group Composition. needs implementation (`generators/braid_group.py` TBD) |
| 130 | concrete | L1 | — (spec-only) | SFT-C — Subshift of Finite Type Composition. needs implementation (`generators/subshift_sft.py` TBD) |

Level mapping from DB Memory Depth (contract: Macro→L4, Meso→L3, Voice→L2,
Local→L1):
- 126 "Macro / Hamiltonian Path" → L4
- 127 "Meso / Nimber Trajectory" → L3 (report tags **abstract** → ABS-127)
- 128 "Macro / Full-history associative" → L4
- 129 "Macro / Braid Word (non-abelian group element)" → L4
- 130 "Local (order-k state)" → L1

127 (SGNC) is the 6th abstract-layer method (after 095/099/104/113 and the
ABS-001..005 originals). Registered as `ABS-127` with `rules.subset_network`
module path → `impl=True` in both stores. None of the four concrete numerics
have a shared generator module yet (126 has a one-off verify script; 129 has a
one-off demo composer, both under `projects/Research/outputs/` — not shared
`generators/` code) → registered spec-only in SCALE (`(level, False)`), not in
GENERATOR_REGISTRY (matching the numeric spec-only convention: 098/100–103,
105–111, 112/114–125 are SCALE-only).

### Human craft (6) — concrete (target), spec-only (SCALE + GENERATOR_REGISTRY)

| ID | Layer | Level | Module | Status |
|---|---|---|---|---|
| HC-075 | concrete (target) | L4 | — (spec-only) | Bel Canto Aria Construction — La Solita Forma |
| HC-076 | concrete (target) | L4 | — (spec-only) | Pansori Madang Composition — Sori/Aniri/Ballim over Jangdan Cycles |
| HC-077 | concrete (target) | L3 | — (spec-only) | Kulintang/Palabunibunyan — Rhythmic-Mode Binding & Ornamental Improvisation |
| HC-078 | concrete (target) | L4 | — (spec-only) | Tin Pan Alley 32-Bar AABA Song Form |
| HC-079 | concrete (target) | L4 | — (spec-only) | Musique Concrète Tape-Music Composition — Studio Montage |
| HC-080 | concrete (target) | L3 | — (spec-only) | Notre-Dame Organum & Rhythmic-Mode Composition |

Level rationale (structure scope, consistent with prior HC promotions):
- L4 (piece-level form / multi-section arrangement architecture): HC-075
  (four-movement scena→cantabile→tempo di mezzo→cabaletta chain, like HC-038
  sonata / HC-070 kriti), HC-076 (madang→daemok narrative scene chain, like
  HC-070), HC-078 (four 8-bar AABA sections + bridge design, like HC-038/055),
  HC-079 (montage-timeline form S0→S4).
- L3 (groove / interlock / voicing / counterpoint craft): HC-077 (rhythmic-mode
  binding + ornament-within-parameters, like HC-002 kotekan / HC-017 sanjo),
  HC-080 (cantus-firmus polyphonic elaboration + six rhythmic modes, like
  HC-021 species counterpoint / HC-071 chorale harmonization).

All HC entered in both stores per established convention: SCALE `(level, False)`
+ `GENERATOR_REGISTRY[id] = (None, None, "...")`, so `impl_status()` is False and
the selector filters them as spec-only dead ends.

## Not registered — sound production (SP-*, absolute layer; noted only)

Per contract, SP-* methods are absolute-layer and are NOT force-registered into
SCALE (`SP_METHODS` in `workflows/musicom_workflow.py` covers the implemented
render path). Recorded for the ledger:

| ID | Method | Layer | Reported candidate module | Module present? |
|---|---|---|---|---|
| SP-125 | Jawari Buzz-Bridge Sitar Synthesis (JBSS) | absolute · Synthesis Engines | `sound/synthesis/jawari_sitar.py` | no |
| SP-126 | Perceptual Loudness Normalization (PLN) | absolute · Post-Processing/DSP | `sound/effects/loudness_normalizer.py` | no |
| SP-127 | STRAIGHT Pitch-Adaptive Spectral Resynthesis (PASR) | absolute · Synthesis Engines | `sound/synthesis/straight_vocoder.py` | no |
| SP-128 | Empirical Mode Decomposition / Hilbert–Huang (EMD-HAR) | absolute · Post-Processing/DSP | `sound/effects/emd_resynthesis.py` | no |
| SP-129 | Transaural Crosstalk-Cancelled Binaural Rendering (TCCR) | absolute · Post-Processing/DSP | `sound/effects/transaural.py` | no |

None of SP-125..129 are force-registered in SCALE; none have a shared `sound/`
implementation module yet.

## Skipped (dedup / sanity gate)

None. All 11 code-target candidates (5 numeric + 6 HC) passed the gate:
standalone method file present (`method_<ID>_*.md` / `human_method_HC-*.md`)
+ DB summary-table row present (`methods_db.md` rows 136–140; `human_methods_db.md`
rows 81–86).

## Test result

```
/opt/data/micromamba/envs/musicom/bin/python -m pytest tests/test_selector_step2.py tests/test_paths_step1.py -q
→ 32 passed
```

SCALE-count assertion in `tests/test_paths_step1.py::test_scale_counts_match_plan`
updated:

| Level | before | after | delta |
|---|---|---|---|
| L4 | 70 | 77 | +7 (126/128/129 numeric; HC-075/076/078/079 human) |
| L3 | 81 | 84 | +3 (ABS-127 numeric; HC-077/080 human) |
| L2 | 22 | 22 | 0 |
| L1 | 12 | 13 | +1 (130 numeric) |

## Skill master-map index

Updated `/opt/data/hermes_persistent/skills/musicom-method-master-map/references/methods/index.md`
Master Map list with the 11 new IDs (126, ABS-127, 128–130, HC-075..HC-080).

## Commit

- Repo: `/opt/data/repos/musicom`
- SHA: `bc0ea8929f331a2375f84f06eb1505b48d0824b2`
- Files: `workflows/paths.py`, `generators/generator_registry.py`, `tests/test_paths_step1.py`
- Commit message: `register methods 126-130, HC-075-080: weekly prose->code promotion into SCALE and GENERATOR_REGISTRY`
- Not pushed (daily repo-sync owns pushing).
- No prose files under `projects/` committed (daily sync owns those).
