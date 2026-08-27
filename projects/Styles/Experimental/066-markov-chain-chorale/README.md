# 066 — Markov Chain Chorale (Method 020)

**Composition method:** 020 — First-Order Markov Chain Sequencing (`generators/chain.py`)

## Concept

Discrete-time stochastic process **with memory**: each pitch-class transition
depends only on the current state (Markov property). A 12-state pitch-class
chain biased toward stepwise neighbour motion (diatonic *and* chromatic
neighbours + fifth-leap escape states) is learned via
`MarkovChainGenerator`'s transition table and walked deterministically
(`seed=66`). A second first-order chain over duration states {1/8, 1/4}
governs rhythm. The key contrast with 065 (memoryless uniform Monte Carlo)
is **memory + stepwise contour** — yet the chromatic escape states still leak
non-diatonic tones into the raw draft.

## Parameters

| Param | Value |
|-------|-------|
| Key | F major (ionian) |
| BPM | 92 |
| Meter | 4/4 (480 tpb, 1920 ticks/bar) |
| Form | 4 sections × 2 bars = 8 bars |
| Harmony | I - vi - IV - V (F - Dm - Bb - C) |
| Voices | Soprano (Flute), Alto/Tenor (Strings), Bass |
| Seed | 66 |

## Two-Phase Architecture

- **Phase 1 — raw draft** (`MIDI/066-markov-chain-chorale-phase1.mid`):
  unquantized first-order Markov pitch path. 19 of 46 raw events are
  non-diatonic (chromatic leak) — proof the draft is pre-rules.
- **Phase 2 — rules-processed** (`MIDI/066-markov-chain-chorale.mid`):
  each raw pitch snapped to the nearest diatonic triad tone (soprano),
  Alto/Tenor/Bass built as diatonic block harmony via the canonical
  `Scale7ChordDegree.get_diatonic_note()`, voice-leading optimized, Phase 2c
  inversion-rotation correction applied, harmonic function validated.

## Validation

- Phase 1 zero-drift `validate()`: **PASS (True)**
- Phase 2 zero-drift `validate()`: **PASS**
- Parallel/hidden fifth violations (classical): **0**
- Harmonic function report: I→vi (tonic→any, legal), vi→IV (prolongation,
  free), IV→V (subdominant→dominant, legal) — builds a perfect V→I cadence.

## Artifacts

```
MIDI/066-markov-chain-chorale.mid              (1785 B, 4 voices)
MIDI/066-markov-chain-chorale-phase1.mid       (471 B, 1 raw voice)
MIDI/*.mid.provenance.json                     (both artifacts)
Analysis/grid_visualization.txt                (tip: 4×4, 3840 ticks/section)
Scripts/compose.py                             (generator, reproducible seed)
```

## Status

DONE — MIDI only (no audio render, per composition-job contract). Standalone
project under `Styles/Experimental/`.