# Musicom Method Registration Report — 2026-09-13

Weekly prose→code promotion (SCALE registry + generator_registry), closing the
prose→code gap (LAYER_ARCHITECTURE.md). Ran from `/opt/data/repos/musicom` with
`/opt/data/micromamba/envs/musicom/bin/python`.

Scope: the 7 numeric reports (079–085), the 7 HC reports (HC-028–HC-034) and
the 7 SP reports (SP-065–SP-071) that landed since the last run
(`registration_report_2026-09-06.md`).

## Registered — numeric algorithmic (concrete layer → SCALE)

| ID | Method | Layer | Level | Module | Notes |
|---|---|---|---|---|---|
| 079 | Tintinnabuli Composition (TINC) | concrete | L3 | `generators.tintinnabuli` | **IMPLEMENTED** — module already existed (commit `938952d`, `TintinnabuliGenerator` + `isorhythmize`), now routable. impl=True |
| 080 | Messiaen Modes of Limited Transposition (MMLT) | concrete | L3 | None | spec-only — needs implementation (report names `generators/messiaen_modes.py`) |
| 081 | Narmour Implication-Realization Melodic (NIRMC) | concrete | L3 | None | spec-only — needs implementation (`generators/narmour_ir.py`) |
| 082 | Random Boolean Network Criticality (RBNCC) | concrete | L3 | None | spec-only — needs implementation (`generators/boolean_network.py`) |
| 083 | Aperiodic Quasicrystal Tiling (QTSC) | concrete | L4 | None | spec-only — needs implementation (`generators/quasicrystal_tiling.py`) |
| 084 | Zipf–Mandelbrot Rank–Frequency (ZMRC) | concrete | L4 | None | spec-only — needs implementation (`generators/zipf_rank_frequency.py`) |
| 085 | Non-negative Matrix Factorization (NMF-C) | concrete | L4 | None | spec-only — needs implementation (`generators/nmf_composition.py`) |

Levels from DB Memory Depth: 079/080/081/082 Meso→L3 (082 "Meso / Attractor
Cycle"); 083 "Macro / Inflation Level"→L4; 084 "Macro / Vocabulary"→L4;
085 "Macro / Corpus"→L4.

**079 is the notable one**: unlike every method registered in the last three
weekly batches, it has real shared code. `generators/tintinnabuli.py` was
promoted to the library on 2026-08-18 but was never wired into SCALE or
GENERATOR_REGISTRY — so the selector could not route it. Now it can
(`impl_status("079") is True`, `get_generator("079")` resolves).

## Registered — human craft (HC-*, concrete (target) → SCALE + GENERATOR_REGISTRY)

| ID | Method | Layer | Level | Module | Notes |
|---|---|---|---|---|---|
| HC-028 | Jazz Chord-Scale Improvisation & Comping (Bebop/Hard-Bop) | concrete (target) | L3 | None | spec-only (meso / per-chorus phrase craft) |
| HC-029 | Shakuhachi Honkyoku Breath-Phrase & Ma (Ichi-On Jōbutsu) | concrete (target) | L4 | None | spec-only (macro breath-arch: ro→kan→ro) |
| HC-030 | Argentine Tango Marcato Counterpoint (Orquesta Típica) | concrete (target) | L4 | None | spec-only (Intro→A→B→A'→Coda arrangement arc) |
| HC-031 | Persian Radif Dastgah–Gusheh Ordering | concrete (target) | L4 | None | spec-only (whole-piece gusheh ordering = macro form) |
| HC-032 | Guqin Jianzipu Tablature & Dapu Reconstruction | concrete (target) | L4 | None | spec-only (report states "arch macro-form" explicitly) |
| HC-033 | Inuit Katajjaq Throat-Singing Duet (Breath-Game Hocket) | concrete (target) | L3 | None | spec-only (motif/round-level interlock) |
| HC-034 | Choro Rondo & Baixaria Counterpoint (Roda de Choro) | concrete (target) | L3 | None | spec-only (fixed AABBACCA module form, cf. HC-022 blues AAB → L3) |

Entered in both stores to mirror the HC-018..HC-027 pattern: SCALE
`(level, False)` + `GENERATOR_REGISTRY[id] = (None, None, "...")`, so
`impl_status()` is False and the selector filters them as spec-only dead ends
(verified: `HC-033` not selectable).

## Not registered — sound production (SP-*, absolute layer; noted only)

Per contract, SP-* methods are **absolute-layer** and are NOT force-registered
into SCALE (`SP_METHODS` in `workflows/musicom_workflow.py` is the implemented
render path). Recorded for the ledger:

| ID | Method | Layer | Reported candidate module | Module present? |
|---|---|---|---|---|
| SP-065 | Brass Lip-Reed Physical Modeling (LIPS) | absolute · Synthesis Engines | `sound/synthesis/lip_reed.py` | no |
| SP-066 | Air-Jet Labium Flute Physical Modeling (FLUE) | absolute · Synthesis Engines | `sound/synthesis/flute_jet.py` | no |
| SP-067 | Kelly-Lochbaum Acoustic Tube Model (KLAT) | absolute · Synthesis Engines | `sound/synthesis/kelly_lochbaum.py` | no |
| SP-068 | Bytebeat Synthesis | absolute · Synthesis Engines | `sound/synthesis/bytebeat.py` | no |
| SP-069 | Wavelet Packet Spectral Synthesis (WPSS) | absolute · Synthesis Engines | `sound/synthesis/wavelet_packet.py` | no |
| SP-070 | Feedback Amplitude Modulation (FBAM) | absolute · Synthesis Engines | `sound/synthesis/fbam.py` | no |
| SP-071 | Dattorro Plate Reverb (DPR) | absolute · Post-Processing/DSP | `sound/effects/dattorro_plate.py` | no |

### ⚠ ID collision discovered (flagged, not fixed — out of scope)

SP-069 / SP-070 / SP-071 are claimed **twice**:

- prose research reports (2026-09-10/11/12): SP-069 WPSS, SP-070 FBAM, SP-071 DPR
- code `SP_METHODS` (commit `cb44440`, 2026-09-10): SP-069 topology_distortion
  (FuzzBillion), SP-070 morph_filter (ZERO9), SP-071 severance (ZERO9) — all
  three **implemented and already used in production** (`SP071-severance-techno-brownian`).

The nightly research job did not see the gear-replication reservation and re-used
the ID range. This is a prose-side divergence, not a code defect; needs an ID
re-number on the prose side (next free global max is SP-075). Flagged for the
method-master-map / sound-research jobs — cannot be resolved from the
registration contract, which must not touch SP-* prose or `SP_METHODS`.

## Skipped (dedup / sanity gate)

- **058 (NODE-CTC)** — still fails gate (a)+(b): no summary-table row in
  `methods_db.md` (`grep -c '^| \*\*058\*\*' → 0`), no `report_058.md`, no
  `method_058_*.md`. Pre-existing gap, unchanged since 2026-09-06. Not registered.

All 21 candidates passed the gate: every one has its standalone method file
(`method_0{79..85}_*.md`, `human_method_HC-0{28..34}_*.md`,
`sound_method_SP-0{65..71}_*.md`) and a DB summary-table row
(`methods_db.md` lines 89–95 & 167–173; `human_methods_db.md` lines 35–41).

## Master map index

`/opt/data/hermes_persistent/skills/musicom-method-master-map/references/methods/index.md`
updated — Master Map list now includes 079–085 and HC-028–HC-034.

## Test gate

```
/opt/data/micromamba/envs/musicom/bin/python -m pytest tests/test_selector_step2.py tests/test_paths_step1.py -q
→ 32 passed
```

Count assertions in `tests/test_paths_step1.py::test_scale_counts_match_plan`
updated via the documented pattern (comment + literal):

| Level | before | after | delta |
|---|---|---|---|
| L4 | 22 | 29 | +7 (083/084/085 numeric; HC-029/030/031/032) |
| L3 | 41 | 48 | +7 (079/080/081/082 numeric; HC-028/033/034) |
| L2 | 20 | 20 | — |
| L1 | 9 | 9 | — |

Full suite also run green: **400 passed** in 75.6s.

## Route verification

```
079 resolves -> generators.tintinnabuli
SCALE 079: ('L3', True)  impl: True
079 selectable: True
HC-028 in SCALE: True  spec-only: True
HC-033 selectable (should be False): False
```

## Commit

- Repo: `/opt/data/repos/musicom`
- Files: `workflows/paths.py`, `generators/generator_registry.py`, `tests/test_paths_step1.py`
- Commit SHA: `0101ab2d352524ff04856bbe13b7d663597d05e6` (commit "register methods 079-085, HC-028-034: ...")
- Not pushed (daily repo-sync owns pushing).
- No prose files under `projects/` were staged (daily sync owns those).
