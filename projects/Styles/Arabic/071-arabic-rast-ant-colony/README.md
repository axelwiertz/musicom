# 071 — Arabic Rast Ant Colony

**Style:** Arabic (Rast maqam, maqsum rhythm)
**Method:** 041 — Ant Colony Optimization Path Finding (ACOPF), Stochastic paradigm
**Date:** 2026-08-17 (nightly autonomous composition job)
**Classification:** ai-generated
**Status:** Complete

## Concept

Ant agents walk a pitch graph, choosing hops by pheromone × consonance
heuristic. Pheromone evaporation + deposit creates emergent melodic
attractors — repeated motifs crystallize where ants keep re-depositing.
Bounded, aperiodic trajectory mapped to the Rast maqam.

**Musical story:** D Rast foundation (bars 0-3) → A Nahawand jins lift
(bars 4-7) → Rast return (bars 8-11) → cadence (bars 12-15), over a driving
maqsum (3+3+2) percussion groove.

## Parameters

- **Key:** D Rast (D, E-quarter-flat, F, G, A, B-quarter-flat, C, D) — MIDI grid approx [62, 63, 65, 67, 69, 70, 72, 74]
- **Tempo:** 100 BPM | **Meter:** 4/4 | **Bars:** 16
- **Form:** A(4) D Rast | B(4) A Nahawand | A2(4) D Rast | C(4) cadence
- **Harmony per group:** Dm — Am — F — Dm (Rast-tone only voicings)
- **Rhythm:** Maqsum 3+3+2 (DUM TEK TEK DUM TEK) on 16th grid, offbeat hat ticks
- **Voices:** Lead (Flute), Harmony (String Ensemble), Bass, Drums (ch 10), Pad (Synth Pad)
- **Seed:** 20260817

## Two-Phase Architecture

### Phase 1: Raw Generative Draft (PRE-RULES)
`MIDI/071-arabic-rast-ant-colony-phase1.mid`

- **Pitch DNA:** ant-colony trajectory in MIDI pitch space; continuous float
  jitter (±0.45 st) NOT quantized to Rast → chromatic leak (notes like 81, 82,
  51 outside the maqam); pheromone deposit pulls ants into recurring attractor
  cells = emergent motifs.
- **Rhythm DNA:** inter-onset gaps drawn from a skewed power distribution
  (chaotic clustering), clipped [0.5, 4.0] beats, NOT snapped to the maqsum
  grid — bursts and silences.
- **Dynamics DNA:** velocity proportional to |pitch - anchor| (big leaps louder).
- Single voice, no harmony, no voice leading.

### Phase 2: Rules Post-Process (POST-RULES)
`MIDI/071-arabic-rast-ant-colony.mid`

- Quantized to Rast maqam tones per section anchor (Rast jins on D, Nahawand
  jins on A).
- Harmony: whole-bar Rast-tone chord pads per section group.
- Voice-leading fix: stale repeated unisons nudged one scale degree (in-maqam),
  parallel perfect-5th motion broken.
- Bass + maqsum drums added; zero-drift UnitMatrix cells (4 sections × 7680
  ticks), validate() True.

## Artifacts

| File | Bytes |
|------|-------|
| `MIDI/071-arabic-rast-ant-colony-phase1.mid` | 4583 |
| `MIDI/071-arabic-rast-ant-colony.mid` | 4583 |
| `Audio/071-arabic-rast-ant-colony.wav` | 7692588 |
| `Audio/071-arabic-rast-ant-colony.ogg` | 285593 |
| `Analysis/grid_visualization.txt` (+ phase1) | 4617 |
| `Analysis/summary.json` | 1036 |

All `.mid`/`.wav`/`.ogg` > 40 bytes. Preflight: exit 0 (see run log).
