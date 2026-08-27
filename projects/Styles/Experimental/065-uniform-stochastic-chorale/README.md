# 065 — Uniform Stochastic (Monte Carlo) Chorale (Method 001)

**Method:** 001 — Uniform Stochastic (Monte Carlo) sampling
**Engine:** `generators/stochastic.py` + musicom rules
**Date:** 2026-08-11 (autonomous nightly composition job)
**Status:** Complete — MIDI only (no audio render, per composition-job contract)

## Concept

A four-voice chorale in **D minor (aeolian)** whose raw generative seed is the
**purest form of stochastic music**: every pitch is drawn **uniformly at random**
from the full chromatic pool `[50..88]` and every duration from the discrete set
`{120, 240, 360, 480}` ticks — with **no Markov memory, no scale membership, no
voice-range bound, and no chord context** in the raw draft.

This method was chosen as the **maximal contrast to 064 (Markov-Constraint)**:
where MCWS imposes local stepwise bias + global wavefront constraints in *Phase
1 itself*, uniform stochastic puts **zero** musical structure in the raw draft.
The entire musical grammar is demonstrated to live in **Phase 2** — the musicom
rules post-processing layer. Nothing demonstrates the value of the
two-phase architecture better than watching a fully chaotic draft become a
consonant chorale.

- **Key:** D minor (aeolian) — `D E F G A Bb C`
- **Tempo:** 88 BPM, 4/4
- **Form:** 4 sections × 2 bars = 8 bars total
- **Voices:** Soprano (Flute), Alto (Strings), Tenor (Strings), Bass (Bass)

## Harmonic Progression (rules-validated)

```
i  -> VI -> III -> VII   (Dm - Bb - F - C)
```

Validated against the `Scale7ChordDegree` function map in `rules/progression.py`:

| Pair | Function class | Verdict |
|------|---------------|---------|
| 1 -> 6 | tonic -> tonic-prolongation | legal (tonic -> any) |
| 6 -> 3 | tonic-prolongation -> tonic-prolongation | legal (prolongation, free) |
| 3 -> 7 | tonic-prolongation -> dominant | legal (prolongation, free) |

The cycle returns `VII (C)` — dominant of D minor — implying a perfect cadence
back to `i (Dm)` on the loop. Triads computed through the canonical
`Scale7ChordDegree.get_diatonic_note()` helper — no off-by-octave scale
inversions on wrap degrees.

## Two-Phase Architecture

**Phase 1 (generative draft)** — `065-uniform-stochastic-chorale-phase1.mid`:

Raw uniform-random pitch draw (first 24):
```
[68, 78, 85, 64, 66, 52, 60, 57, 73, 64, 75, 53, 71, 67, 77, 85, 60, 77, 70, 69, 62, 69, 68, 58]
```
Raw uniform-random durations: `[480, 240, 480, 480, 480, 480, 120, 240, 360, 360, ...]`

Single voice, full chromatic range 52–88, 51 events, no harmony. Musically
incoherent — deliberate.

**Phase 2 (musicom rules)** — `065-uniform-stochastic-chorale.mid`:

- Soprano quantized to nearest section-triad tone (consonant melody). Example:
  raw `68→69 (A), 78→69, 85→69, 64→65 (F), 66→65, 52→65, 60→65, 57→65` — the
  chaotic chromatic run collapses onto the Dm triad tones.
- Alto/Tenor/Bass = diatonic block harmony from the section triad.
- `VoiceLeadingRules.optimize_voice_leading()` minimizes voice-leading distance.
- Phase 2c correction pass: inversion rotations searched — **final: 0
  parallel/hidden-fifth violations** (0 chords needed re-voicing).
- Zero-drift gate: `UnitMatrixComposer.validate()` **PASS** for both MIDIs.

## Artifacts

```
MIDI/065-uniform-stochastic-chorale-phase1.mid        (496 bytes)  raw draft
MIDI/065-uniform-stochastic-chorale.mid               (1885 bytes) rules result
MIDI/*.provenance.json                                (phase 1 + phase 2)
Analysis/grid_visualization.txt
compose.py
verify.py
Notes/lesson-uniform-stochastic.md
```

## Reproducibility

`SEED = 65` — rerunning `compose.py` produces identical artifacts
(deterministic random + fixed structure).

## Next Moves

- Render with a production method (SP series) for listening.
- Compare MCWS (064) vs uniform stochastic (065) on the same progression.
- Try a weighted (non-uniform) stochastic distribution to bias toward
  diatonic tones in the raw draft.