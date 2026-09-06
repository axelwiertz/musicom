# Musicom Method Registration Report — 2026-09-06

Weekly prose→code promotion (SCALE registry + generator_registry). Ran from
`/opt/data/repos/musicom` with `/opt/data/micromamba/envs/musicom/bin/python`.

## Registered (numeric, concrete layer — SCALE L1–L4, spec-only)

| ID | Method | Layer | Level | Module |
|---|---|---|---|---|
| 070 | Coupled Map Lattice Composition (CML-C) | concrete | L2 | None (spec-only) — needs implementation |
| 071 | Hopfield Associative Memory Composition (HAM-C) | concrete | L4 | None (spec-only) — needs implementation |
| 072 | Normalizing Flow Composition (NFC) | concrete | L4 | None (spec-only) — needs implementation |
| 073 | Harmony Search Improvisational Composition (HSIC) | concrete | L4 | None (spec-only) — needs implementation |
| 074 | Restricted Boltzmann Machine Composition (RBM-C) | concrete | L4 | None (spec-only) — needs implementation |
| 075 | Self-Organizing Map Composition (SOM-C) | concrete | L4 | None (spec-only) — needs implementation |
| 076 | Prouhet–Thue–Morse Automatic Sequence Composition (PTM-ASC) | concrete | L3 | None (spec-only) — needs implementation (report names `generators/automatic_sequence.py`) |
| 077 | De Bruijn Universal Cycle Composition (DBUC) | concrete | L3 | None (spec-only) — needs implementation (report names `generators/debruijn_sequence.py`) |
| 078 | Ising Model Equilibrium Composition (IMEC) | concrete | L3 | None (spec-only) — needs implementation (report names `generators/ising_equilibrium.py`) |

Levels from DB Memory Depth: 070 Meso→L2; 071 Macro→L4; 072 Macro→L4; 073 Macro→L4; 074 Macro→L4; 075 Macro→L4; 076 None (self-similar recurrence)→L3 (deterministic substitution; nearest structural); 077 Local (length-k window)→L3; 078 Meso→L3.

## Registered (human, HC-* — SCALE + GENERATOR_REGISTRY, spec-only)

| ID | Method | Layer | Level | Module |
|---|---|---|---|---|
| HC-018 | Clave-Guided Montuno Construction (Cuban Son) | concrete (target) | L3 | None (spec-only) |
| HC-019 | Bulgarian Aksak Asymmetric-Meter Horo | concrete (target) | L3 | None (spec-only) |
| HC-020 | Tension-and-Release Arrangement (Drop/Buildup) | concrete (target) | L4 | None (spec-only) |
| HC-021 | Species Counterpoint | concrete (target) | L3 | None (spec-only) |
| HC-022 | Twelve-Bar Blues AAB Form & Blue-Note Melody | concrete (target) | L3 | None (spec-only) |
| HC-023 | Spectral Listening & Harmonic-Series Orchestration | concrete (target) | L3 | None (spec-only) |
| HC-024 | Graphic Score & Indeterminate Notation | concrete (target) | L4 | None (spec-only) |
| HC-025 | West African Kora Griot Ostinato-Song | concrete (target) | L3 | None (spec-only) |
| HC-026 | Scottish Pibroch Theme-and-Variation | concrete (target) | L3 | None (spec-only) |
| HC-027 | Tuvan Overtone Throat Singing | concrete (target) | L3 | None (spec-only) |

Levels from Memory Depth: HC-018/019/021/022/023/025/026/027 Meso→L3; HC-020 (macro-form energy arc)→L4; HC-024 (open-form/meta-composition, macro)→L4.

## Registered (sound production, SP-* — absolute layer, noted only)

SP-056..SP-064 are absolute-layer sound-production methods (SP_METHODS in
`workflows/musicom_workflow.py` covers the implemented render path). NOT
force-registered into SCALE (correct behavior). Candidate implementation
modules recorded, none exist yet:

| ID | Method | Layer | Candidate module (not implemented) |
|---|---|---|---|
| SP-056 | Walsh Function Synthesis (FWHT) | absolute · Synthesis Engines | `sound/synthesis/walsh.py` (not present) |
| SP-057 | Chua's Circuit Chaotic Oscillator (CCCOS) | absolute · Synthesis Engines | `sound/synthesis/chua_circuit.py` (not present) |
| SP-058 | Dispersive Waveguide Spring Reverb (DWSR) | absolute · Synthesis Engines | `sound/effects/spring_reverb.py` (not present) |
| SP-059 | Fractional Delay-Line Modulation (FDLMS) | absolute · Post-Processing/DSP | `sound/effects/fractional_delay_mod.py` (not present) |
| SP-060 | Denoising Diffusion Audio Synthesis (DDAS) | absolute · Synthesis Engines | `sound/synthesis/diffusion_audio.py` (not present) |
| SP-061 | Cepstral Liftering Synthesis (CLS) | absolute · Synthesis Engines | `sound/synthesis/cepstral.py` (not present) |
| SP-062 | Antiderivative Antialiasing (ADAA) | absolute · Post-Processing/DSP | `sound/effects/adaa_waveshaper.py` (not present) |
| SP-063 | Ring Modulation (Balanced Modulator) | absolute · Synthesis Engines | `sound/synthesis/ring_mod.py` (not present) |
| SP-064 | Shepard–Risset Glissando (SRG) | absolute · Synthesis Engines | `sound/synthesis/shepard_risset.py` (not present) |

## Skipped (dedup / sanity gate)

- **058 (NODE-CTC)** — pre-existing DB gap: detailed section exists in
  methods_db.md but NO summary-table row and NO standalone `method_058_*.md`
  file. Fails gate (b) — no DB row, no standalone file. Not registered.

## Master map index

`/opt/data/hermes_persistent/skills/musicom-method-master-map/references/methods/index.md`
updated: added 070–078 (numeric) and HC-018–HC-027 to the Master Map list.

## Test gate

`/opt/data/micromamba/envs/musicom/bin/python -m pytest tests/test_selector_step2.py tests/test_paths_step1.py -q`
→ **32 passed** (was 32 before; counts in `test_paths_step1.py::test_scale_counts_match_plan`
updated L4 15→22, L3 30→41 with documented-pattern comment).

## Commit

- Repo: `/opt/data/repos/musicom`
- Files: `workflows/paths.py`, `generators/generator_registry.py`, `tests/test_paths_step1.py`
- Commit SHA: `a50ba19e0b5d656125c51969b878fae5bedca20f` (commit "register methods 070-078, HC-018-027: ...")
- Not pushed (daily repo-sync owns pushing).
