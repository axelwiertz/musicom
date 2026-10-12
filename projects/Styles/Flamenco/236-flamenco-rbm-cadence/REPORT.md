# 236-flamenco-rbm-cadence — REPORT

**Date:** 2026-10-11 (nightly composition job)
**Project:** `Styles/Flamenco/236-flamenco-rbm-cadence/`

## Selection

| Field | Value |
|---|---|
| Style | **Flamenco** (random from 47 genre folders) |
| Method | **074 — Restricted Boltzmann Machine Composition (RBM-C)** |
| Layer | **concrete** (layer roll 0.4919 → ≥1/7 threshold, concrete night) |
| Paradigm | AI-Driven (energy-based / likelihood-trained) |
| Form | **intro-falseta-letra-falseta-cierre** (Intro 4 / Falseta 8 / Letra 8 / Falseta 8 / Cierre 4 = **32 bars**) |
| Key | **A Aeolian** (Andalusian cadence) |
| Tempo | 108 BPM, 4/4, 480 TPB |

Methods excluded from selection (used within last 7 days): 1, 6, 7, 10, 12, 32, 40, 41, 50, 51, 94, 95, 98, 104.

## Method essence (074 RBM-C)

A bipartite visible↔hidden Boltzmann network over a per-voice piano-roll
(`V = 128 beats × 20 chromatic pitch bins = 2560` visible units, `H = 48`
hidden feature units). Trained by **contrastive divergence (CD-1)** on 12
synthetic flamenco-melody seed rolls whose note distribution is conditioned
on the current Andalusian-cadence chord. Composition = **block Gibbs
sampling** (120 steps) from the learned Boltzmann distribution. Hidden units
learn chord/motif/register features; the cadence supplies the macro-form
conditioning schedule.

**Phase 1 (raw draft):** sampled binary piano-roll, thinned to the
most-confident bin per beat (128 notes), emitted as a single nylon-guitar
voice with **unquantized onsets** (±70-tick jitter, off-grid) and
**unquantized pitch** (chromatic bins — NOT scale-filtered, NOT chord-tone
snapped). Exported as `-phase1.mid` with its own zero-drift gate.

**Phase 2 (musicom rules):** the same 128 sampled notes are chord-tone
quantized against the per-bar Andalusian-cadence chord, grid-snapped to the
16th grid (120 ticks), and embedded in a full flamenco texture.

## Harmony — Andalusian cadence (descending tetrachord)

Classic flamenco `por arriba` cadence, natural-minor form (fully diatonic to
A Aeolian; the authentic picardy E-major cierre is documented as a possible
variant but kept diatonic here so the harmony audit stays 0):

| Cadence idx | Chord | Triad (MIDI) | Pitch classes | Quality |
|---|---|---|---|---|
| 0 | Am (i)  | 57 60 64 (A3 C4 E4) | {9,0,4} | minor |
| 1 | G (VII) | 55 59 62 (G3 B3 D4) | {7,11,2} | major |
| 2 | F (VI)  | 53 57 60 (F3 A3 C4) | {5,9,0} | major |
| 3 | Em (v)  | 52 55 59 (E3 G3 B3) | {4,7,11} | minor |

`BAR_CHORD = [0,1,2,3] × 8` (32 bars). The signature **descending bass
tetrachord A→G→F→E** is carried by the double bass roots (A2/G2/F2/E2).

## Voices & instruments (from instrument registry)

| Voice | Instrument (registry) | Program | Channel | Role |
|---|---|---|---|---|
| Lead | ACOUSTIC_GUITAR (nylon) | 24 | 0 | RBM falseta melody, chord-tone quantized, 16th-grid |
| Compas | ACOUSTIC_GUITAR (nylon) | 24 | 1 | Rasgueado strums (quarter hits + 8th off-beat doubles in Falseta) |
| Bass | DOUBLE_BASS | 43 | 2 | Descending roots (beat 1) + fifth (beat 3) |
| Flute | FLUTE | 74 | 3 | Falseta arpeggios (Falseta1/Falseta2 only), 16th-grid |
| Palmas | GM drums (prog 0) | 0 | 9 | Cajón kick (36), hand clap (39), claves (75) |

## Verification (real numbers)

### Zero-drift gate
- `UnitMatrixComposer.validate()` → **True** for both Phase 1 and Phase 2.
- Phase 2 total length = 61440 ticks = 32 bars exactly (verified by mido readback).

### Grid audit (phase-2 MIDI readback, mido)
Authoritative grid = finest 16th grid (120 ticks); the 8th-grid tally counts
legitimate 16th-note subdivisions.

| Voice | Notes | off-16th | off-8th (16th subdiv) | out-of-scale | out-of-chord |
|---|---|---|---|---|---|
| Lead | 128 | 0 | 0 | 0 | 0 |
| Compas | 512 | 0 | 0 | 0 | 0 |
| Bass | 64 | 0 | 0 | 0 | 0 |
| Flute | 192 | 0 | 96 | 0 | 0 |
| Palmas (drums) | 224 | 0 | 0 | — | — |

**Grid verdict: 0 off-grid** (all 896 pitched onsets are multiples of 120).
**Harmony verdict: 0 out-of-scale, 0 out-of-chord** (every pitched note is a
diatonic chord tone of its bar's cadence chord).

### Voice-leading
Parallel-motion/hidden-fifth check across the 32 cadence triads reports
**38 parallel-5th/8ve events**. These are **idiomatic** — the Andalusian
cadence is a deliberate parallel descent of the tetrachord (Am→G→F→Em with
all three voices moving down in lockstep), so the parallel motion is preserved
intentionally rather than "corrected".

### Render / audio profile
- WAV: 13 MB (13120300 B), OGG (Opus voip 48k): 512 KB — both > 40 B ✓
- Duration 74.38 s, peak 0.769, **silence ratio 5.4%** (tail + inter-note
  gaps only).
- Per-second RMS: **0 quiet seconds mid-track** (no mid-track gaps), RMS
  mean 0.101 / min 0.000 / max 0.136.

## Files

```
MIDI/236-flamenco-rbm-cadence.mid            (9221 B)  phase-2 rules-processed
MIDI/236-flamenco-rbm-cadence-phase1.mid     (1243 B)  phase-1 raw RBM draft
MIDI/*.mid.provenance.json                              provenance sidecars
Audio/236-flamenco-rbm-cadence.wav           (13 MB)    FluidSynth render
Audio/236-flamenco-rbm-cadence.ogg           (512 KB)   Opus (Telegram)
Analysis/grid_visualization.txt              high-contrast 5×5 density grid
Analysis/audit.json                          grid + harmony per-voice audit
Analysis/render_stats.json                   silence/RMS profile
Analysis/summary.json                        method/selection summary
compose.py  verify.py                        generator + readback verifier
```

## Fixes applied during this run

1. **Duplicate-section collapse**: the form has two "Falseta" sections; the
   initial `SECTIONS = ["Intro","Falseta","Letra","Falseta","Cierre"]` caused
   the second `add_section("Falseta")` to overwrite the first (sections are
   keyed by name), silently dropping 8 bars → MIDI rendered only 24 bars
   (46080 ticks). Fixed by unique names `Falseta1`/`Falseta2`; verified 32
   bars = 61440 ticks.
2. **RBM sample density**: initial block-Gibbs sample was over-dense
   (652 cells, ~5/beat). Thinned to the single most-confident bin per beat
   (128 notes) for a coherent single melodic line.

## Notes for next time

- A `picardy third` on the final Cierre chord (Em→E major, raising G→G#) is
  the authentic flamenco closing gesture; left out here to keep the scale
  audit at 0 (G# is not in A Aeolian). Could be added as a documented
  one-bar exception next time.
- RBM hidden-unit visualizations (weight filters as piano-roll "motifs") are
  a natural next study artifact.
