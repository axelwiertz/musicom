# 069 — Kuramoto Chorale (Method 038 KOPS)

**Date:** 2026-08-15 (nightly autonomous composition job)
**Method:** Method 038 — Kuramoto Oscillator Phase Synchronization (KOPS)
**Paradigm:** Nature-Led | **Key:** F dorian | **BPM:** 92 | **Form:** 4×2 bars (8 bars)

## Concept

The piece is the synchronization transition itself. Four voices are Kuramoto
phase oscillators with incommensurate natural frequencies (0.85 / 1.0 / 1.15 /
1.35 events per beat). Coupling strength K rises every two bars (0.5 → 1.5 →
2.5 → 4.0), so the ensemble evolves from desynchronized polyrhythmic drift
into a phase-locked chorus that locks to a common pulse and resolves to the
F minor tonic. Progression: i – iv – VII – i (Fm – Bbm – Eb – Fm).

## Files

| File | Role |
|------|------|
| `MIDI/069-kuramoto-chorale.mid` | Phase 2 — rules-processed chorale (4 voices) |
| `MIDI/069-kuramoto-chorale-phase1.mid` | Phase 1 — raw KOPS draft (single voice, pre-rules) |
| `MIDI/*.provenance.json` | Provenance sidecars (both phases) |
| `Analysis/grid_visualization.txt` | High-contrast UnitMatrix timeline |
| `Notes/lesson-kuramoto-sync.md` | What to listen for |
| `compose.py` | Reproducible generator (seed 69, RK4, dt=0.005) |

## Measured synchronization (mean order parameter r per section)

| Section | K | mean r | wraps/oscillator |
|---------|---|--------|------------------|
| i (Fm) 1 | 0.5 | 0.451 | 7, 8, 9, 11 |
| iv (Bbm) | 1.5 | 0.477 | 7, 8, 9, 10 |
| VII (Eb) | 2.5 | 0.760 | 9, 9, 9, 9 |
| i (Fm) 2 | 4.0 | 0.943 | 8, 8, 8, 9 |

Phase lock is audible as the four block-harmony voices (soprano melody from
quantized oscillator-0 pulses; alto/tenor/bass diatonic block harmony) align
into a single pulsing chordal texture with the tonic resolution.

## Validation

- Phase 1 zero-drift gate: **PASS**
- Phase 2 zero-drift gate: **PASS**
- Parallel/hidden fifth violations (classical voice leading): **0**
- Harmonic function report: 1→4 legal (tonic→any), 4→7 legal
  (subdominant→dominant), 7→1 legal (perfect cadence)
- Phase 2c inversion-rotation corrections: 0 needed (optimizer already clean)
- Raw draft non-diatonic leak (pre-rules signature): 4 / 31 events

## Method choice rationale

Methods 019/021/002/003/023/043/048/055/057–068 already used in this series;
KOPS (038) is the natural next step — its order parameter gives a *measured,
quantifiable* musical form (desync → lock), and the two-phase rules pass has
an unusually clean story: the raw draft's chromatic wanderings are folded
into a dorian chorale while the pulse structure survives quantization.
