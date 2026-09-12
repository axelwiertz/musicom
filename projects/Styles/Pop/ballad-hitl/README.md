# Pop Ballad — HITL Project

Human-in-the-loop evolution project for a dramatic pop ballad.

## Concept

- **Genre**: Pop ballad (minor-aeolian drama)
- **Key**: D (aeolian) — i–VI–III–VII harmonic regions
- **Tempo**: 72 BPM (slow ballad)
- **Form**: Intro(4) → Verse(8) → Chorus(8) → Bridge(4) → Outro(4) = 28 bars, ~93 s
- **Voices**: Lead (Flute), Pad (Piano), Bass (Double Bass), Arp (Clarinet), Drums (Drum Kit)

## Phase 1 — Composition (MIDI)

Framework via **Path C middle-out** (`workflows/paths.py`), then per-part
method swaps on the SAME framework + base patterns:

| Part | Bars | Comp method | Effect |
|---|---|---|---|
| Framework | all | 001 Skeleton-First + 012 Euclidean bass + 018 Schillinger density | spine |
| Intro | 0-4 | 001 skeleton | sparse held tones |
| Verse | 4-12 | 004 Prosodic Narrative | lyrical contour |
| Chorus | 12-20 | 011 Voice-Leading Graph | nearest-chord leaps, octave lift |
| Bridge | 20-24 | 023 Tendency Masking | tension walk, wide intervals |
| Outro | 24-28 | 013 Inversion/Retrograde | retrograde motif, resolve |

Per-section harmonic regions (ballad arc): Intro i-VI, Verse full aeolian
cycle, Chorus lift on III-VII-i-VI, Bridge peak on VII, Outro resolve to i.

Zero-drift validated (`validate()` gate), provenance sidecar, grid viz.

## Phase 2 — Production (Audio)

Different production method per VOICE (on stems) AND per SECTION (on bus):

| Voice (stem label) | SP method |
|---|---|
| Lead (Recorder) | SP-032 FDN reverb wash (wet .3) |
| Pad (Bright Acoustic Piano) | SP-020 SVF lowpass 4.5 kHz |
| Bass (Contrabass) | SP-020 SVF lowpass 700 Hz (sub body) |
| Arp (Clarinet) | SP-019 Chebyshev waveshape (drive 1.5) |
| Drums (Drums) | SP-008 multiband compressor (punch) |

| Section | SP method |
|---|---|
| Intro | SP-020 lowpass 1200 Hz (muffled build-in) |
| Verse | dry (lyric clarity) |
| Chorus | SP-021 stereo widen 1.35× |
| Bridge | SP-032 FDN wash (size .85, wet .4) |
| Outro | SP-020 lowpass 800 Hz + fade to 0 |

Master: `normalize_to_lufs(-14)` → `Limiter(-1 dB)` LAST.

## Verification

```
LUFS -14.01  peak 0.891  silence 3.2%
```

- MIDI: `MIDI/pop-ballad-hitl.mid` (3292 B, zero-drift)
- Audio: `Audio/pop-ballad-hitl.wav` (16.5 MB) + `.ogg` (670 KB)
- Stems: `Audio/stems/track*_*.wav`
- Grid: `Analysis/grid_phase1.txt`

## Phase 3 — HITL evolution round (human pick)

`Scripts/phase3_hitl.py` drives the engine's HITL machinery
(`workflows.hitl`) over **this ballad's own framework** — the generic
`run_hitl_round` builds a plain I–V–vi–IV pop anchor, which would discard
the per-section regions and per-part methods from phase 1.

**Search space**: the L3 anchor (bass) groove — Euclidean density ×
on/off-beat offset. Macro-structure (form, harmony, per-part methods) is
frozen, per plan advice #5 ("evolve phrases/anchors, not whole songs").

```bash
PY=/opt/data/micromamba/envs/musicom/bin/python
$PY Scripts/phase3_hitl.py                       # round 0
$PY Scripts/phase3_hitl.py --round 1 \
      --parent-density 4 --parent-offset 240     # mutate around winner
$PY Scripts/phase3_hitl.py --pick 2              # record the human pick
```

### Round 0 candidates (seed 7)

| # | density | offset | bass onsets/bar | onset grid | fitness |
|---|---|---|---|---|---|
| 0 | 3 | 0 | 3 (walking) | {0, 480, 960} | 0.599 |
| 1 | 4 | 0 | 4 (pulse) | {0, 480, 960, 1440} | 0.616 |
| 2 | 5 | 0 | 5 (syncopated) | {0, 240, 720, 960, 1440} | 0.568 |
| 3 | 4 | 240 | 4, pushed off-beat | {240, 720, 1200, 1680} | 0.616 [wildcard] |

Fitness ties between cand 1 and cand 3 (the rule metric is phase-invariant)
— exactly the ambiguity the human judge resolves.

**Round 0 result: human pick = 0** (density=3, on-beat walking). Recorded in
`HITL/round0/evolution.json` + provenance sidecar on the winner.

### Round 1 candidates (seed 108, mutated around the round-0 winner d3/off0)

| # | density | offset | bass onsets/bar | onset grid | fitness | note |
|---|---|---|---|---|---|---|
| 0 | 3 | 0 | 3 | {0, 480, 960} | 0.599 | incumbent (stay slot) |
| 1 | 4 | 0 | 4 | {0, 480, 960, 1440} | 0.616 | denser |
| 2 | 3 | 240 | 3, pushed off-beat | {240, 720, 1200} | 0.599 | flip phase |
| 3 | 4 | 240 | 4, pushed off-beat | {240, 720, 1200, 1680} | 0.616 | wildcard |

Note the mutant at density−1 (2 → clamped to 3) would have duplicated the
stay slot; `_variant_set` de-duplicates and fills the freed slot from the
unexplored pool.

Artifacts per round: `HITL/roundN/candidates/cand*-d*-off*.{mid,ogg}`,
`HITL/roundN/round.json`, and on a pick `HITL/roundN/evolution.json` +
provenance sidecar on the winner.

### Engine fix shipped with phase 3

The mode-aware root lookup (`rules/harmony.progression_roots`) replaced a
duplicated bug in **four** places (`workflows/paths.py`,
`workflows/hitl.py`, `workflows/evolution.py`, and this project's phase 1).
The old code did `MAJOR_DEGREES.index(deg.upper())`, collapsing every
uppercase minor-mode degree (VI/III/VII) and every lowercase major-mode
degree (ii/iii/vi/vii) onto index 0 — e.g. `i–VI–III–VII` in D produced
`[38, 38, 38, 38]` (static harmony). Now: `[38, 46, 41, 48]` = D–B♭–F–C.

Regression-locked by `tests/test_harmony_degrees.py` (16 tests).

## HITL hook

Round 0 is rendered and awaiting the human pick. Reply with a candidate
number (0–3); the agent records it via `phase3_hitl.py --pick N`, writes
`evolution.json` + provenance, and spawns round 1 mutated around the winner.
