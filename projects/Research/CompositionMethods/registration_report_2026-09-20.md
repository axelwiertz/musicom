# Musicom Method Registration Report — 2026-09-20

Weekly prose→code promotion (SCALE registry + generator_registry), closing the
prose→code gap (LAYER_ARCHITECTURE.md). Ran from `/opt/data/repos/musicom` with
`/opt/data/micromamba/envs/musicom/bin/python`.

Scope: the 6 numeric reports (086–091), the 6 HC reports (HC-035–HC-040) and
the 7 SP reports (SP-072–SP-075, SP-087–SP-089) that landed since the last run
(`registration_report_2026-09-13.md`).

## Registered — numeric algorithmic (concrete layer → SCALE)

| ID | Method | Layer | Level | Module | Notes |
|---|---|---|---|---|---|
| 086 | Hidden Markov Model Latent-State Composition (HMM-C) | concrete | L3 | None | spec-only — needs implementation (report names `generators/hmm_composition.py`) |
| 087 | Multiple Viewpoint Systems Composition (MVS-C) | concrete | L3 | None | spec-only — needs implementation (`generators/multiple_viewpoint.py`) |
| 088 | Voronoi Tessellation Event Partitioning (VTEP) | concrete | L4 | None | spec-only — needs implementation (`generators/voronoi_partition.py`) |
| 089 | Change-Ringing Combinatorial Method (CRCM) | concrete | L4 | None | spec-only — needs implementation (`generators/change_ringing.py`) |
| 090 | Golomb Ruler Distinct-Difference Composition (GRDC) | concrete | L4 | None | spec-only — needs implementation (`generators/golomb_ruler.py`) |
| 091 | Coxeter–Conway Frieze Pattern Composition (CCFPC) | concrete | L4 | None | spec-only — needs implementation (`generators/coxeter_frieze.py`) |

Levels from DB Memory Depth:
- 086 "Meso / Hidden Chain" → L3
- 087 "Meso / Variable-Order Context" → L3
- 088 "Macro / Seed Plan" → L4
- 089 "Macro / Lead-Head Cycle" → L4
- 090 "Macro / Ruler Span" → L4
- 091 "Macro / Polygon Period" → L4

## Registered — human craft (HC-*, concrete (target) → SCALE + GENERATOR_REGISTRY)

| ID | Method | Layer | Level | Module | Notes |
|---|---|---|---|---|---|
| HC-035 | Shona Mbira Kushaura/Kutsinhira Interlocking | concrete (target) | L3 | None | spec-only (closed cyclic phrase unit interlock) |
| HC-036 | Norwegian Hardanger Fiddle Slått Craft | concrete (target) | L4 | None | spec-only (multi-section dance-phase form figuring→lausdans→samdans) |
| HC-037 | Klezmer Ornament-Led Ensemble Craft | concrete (target) | L4 | None | spec-only (wedding-set multi-movement suite doina→dances→parting) |
| HC-038 | Sonata Form Process | concrete (target) | L4 | None | spec-only (macro exposition–development–recapitulation arc) |
| HC-039 | Irish Traditional Dance Tune Setting & Ornamentation | concrete (target) | L3 | None | spec-only (32-bar AABB binary dance grid) |
| HC-040 | Andalusi Nūbah Suite Architecture & Mīzān Metric Acceleration | concrete (target) | L4 | None | spec-only (5-movement suite macro-acceleration arc) |

Levels from Memory Depth / Structure:
- HC-035: L3 (closed cyclic phrase unit ostinato/interlock)
- HC-036: L4 (macro dance phases figuring→lausdans→samdans arc)
- HC-037: L4 (wedding-set script macro arc)
- HC-038: L4 (macro-form sonata tonal architecture)
- HC-039: L3 (32-bar AABB binary cycle / phrase craft)
- HC-040: L4 (5-movement suite mawāzīn macro-acceleration arc)

Entered in both stores per contract: SCALE `(level, False)` + `GENERATOR_REGISTRY[id] = (None, None, "...")`, so `impl_status()` is False and the selector filters them as spec-only dead ends.

## Not registered — sound production (SP-*, absolute layer; noted only)

Per contract, SP-* methods are **absolute-layer** and are NOT force-registered into SCALE (`SP_METHODS` in `workflows/musicom_workflow.py` covers the implemented render path). Recorded for the ledger:

| ID | Method | Layer | Reported candidate module | Module present? |
|---|---|---|---|---|
| SP-072 | Harmonic-Percussive Source Separation (HPSS) | absolute · Post-Processing/DSP | `sound/effects/hpss.py` | no |
| SP-073 | Transient Shaping via Differential Envelope Processing (TSDE) | absolute · Post-Processing/DSP | `sound/effects/transient_shaper.py` | no |
| SP-074 | Piano Hammer-String Physical Modeling (PHSP) | absolute · Synthesis Engines | `sound/synthesis/piano_hammer.py` | no |
| SP-075 | Image-Source Room Acoustics Synthesis (ISRA) | absolute · Post-Processing/DSP | `sound/effects/image_source_room.py` | no |
| SP-087 | TR-808 Analog Snare Drum Synthesis (TASS) | absolute · Synthesis Engines | `sound/synthesis/drum_synth_808.py` | no |
| SP-088 | Jiles–Atherton Magnetic Tape Saturation Synthesis (JAMS) | absolute · Post-Processing/DSP | `sound/effects/tape_saturation.py` | no |
| SP-089 | TR-808 Analog Cymbal Physical-Circuit Synthesis (TACS) | absolute · Synthesis Engines | `sound/synthesis/drum_synth_808.py` | no |

*(Note: SP-072..SP-075 in prose collide with earlier code `SP_METHODS` gear replications, as flagged in prior reports. Per contract, not force-registered in SCALE.)*

## Skipped (dedup / sanity gate)

- **058 (NODE-CTC)** — fails gate (a)+(b): no summary-table row in `methods_db.md`, no `report_058.md`, no `method_058_*.md`. Pre-existing historical gap, unchanged. Not registered.

All 19 candidates passed gate: standalone method file exists, DB summary-table row exists.

## Master map index

`/opt/data/hermes_persistent/skills/musicom-method-master-map/references/methods/index.md`
updated — Master Map list now includes 086–091 and HC-035–HC-040.

## Test gate

```
/opt/data/micromamba/envs/musicom/bin/python -m pytest tests/test_selector_step2.py tests/test_paths_step1.py -q
→ 32 passed in 2.69s
```

Count assertions in `tests/test_paths_step1.py::test_scale_counts_match_plan` updated:

| Level | before | after | delta |
|---|---|---|---|
| L4 | 29 | 37 | +8 (088/089/090/091 numeric; HC-036/037/038/040 human) |
| L3 | 48 | 52 | +4 (086/087 numeric; HC-035/039 human) |
| L2 | 20 | 20 | — |
| L1 | 9 | 9 | — |

Full test suite also green: **677 passed, 1 skipped** in 156.16s.

## Commit

- Repo: `/opt/data/repos/musicom`
- Files: `workflows/paths.py`, `generators/generator_registry.py`, `tests/test_paths_step1.py`
- Commit SHA: `670e72f5fc1040f02dac4650dfef8dcc7ec4e828`
- Commit message: `register methods 086-091, HC-035-040: weekly prose->code promotion into SCALE and GENERATOR_REGISTRY`
- Not pushed (daily repo-sync owns pushing).
- No prose files under `projects/` committed.
