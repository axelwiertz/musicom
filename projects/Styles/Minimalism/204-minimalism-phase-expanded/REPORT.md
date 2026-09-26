# 204-minimalism-phase-expanded — Rework Report

Date: 2026-09-26 (autonomous nightly rework agent)
Genre: Minimalism
Source: `Minimalism/001-minimalism-phase-study`

## Concept

Steve Reich "Clapping Music"-style phase piece, rebuilt and expanded on the
musicom `UnitMatrixComposer` engine. Two identical E(5,12) Euclidean marimba
cells on C major pentatonic; voice B phase-walks +1 beat per section while the
cell itself is transformed section-by-section (transpose / invert / retrograde
/ augment / diminish). Sustained pad + bass pedal give 100% continuous layers.

## Source identity (preserved)

| Dimension | Value |
|---|---|
| Style | Reich phase process |
| Key | C major pentatonic (C D E G A) |
| Tempo | 120 BPM, 4/4 |
| Motif | E(5,12) marimba cell, two voices phase-walking |
| Instrumentation | Marimba (GM 12) x2, String Ensemble pad, Bass, ch9 perc |
| Original form | 8 sections x 3 bars = 24 bars |

## Audit result (against current standards)

| Standard | Result |
|---|---|
| 1. Engine (UnitMatrixComposer) | PASS |
| 2. Zero-drift (all voice tracks equal) | PASS (5 tracks x 46080 ticks) |
| 3. Rhythm-grid sync (onset % 120/240) | PASS (0 off-grid / 128 pitched) |
| 4. >= 4 voice tracks | PASS (5) |
| 5. Two-phase artifacts (phase1 present) | **FAIL** (no phase1 mid) |
| 6. provenance.json + index.html | **FAIL** (both missing) |

Decision: **redesign_required = True** (standards 5 + 6 failed).

## What changed

- Rebuilt from scratch via canonical `UnitMatrixComposer` workflow (discarded
  non-compliant code, kept only musical identity).
- **Longer form**: 8 -> 10 sections, 24 -> 30 bars.
- **More variation**: 6 distinct techniques applied across sections (below).
- **Two-phase architecture**: raw Phase-1 draft (single voice, off-grid
  chromatic walk) + Phase-2 rules post-process (per-bar chord-tone
  quantization, 16th-grid snap, dedup).
- **Per-section harmonic regions**: each section has its own 3-bar chord
  progression drawn from C / Am / Gsus / Dsus (all pentatonic subsets; roots
  never collapse to tonic).
- Added `provenance.json`-style sidecars, `grid_visualization.txt`,
  `index.html`, and this report (fixes standard 6).

## Variation techniques (6)

| Section | Technique |
|---|---|
| 0 Intro | (establish base cell) |
| 1-3 Phase1-3 | Phase walk +1 beat/section (per-section method change) |
| 4 Transpose | Transposition +P5 (register shift) |
| 5 Inversion | Inversion around axis 64 |
| 6 Retrograde | Retrograde (reverse onset order) |
| 7 Augment | Augmentation (step 480 -> 960, half speed) |
| 8 Climax | Diminution (8th notes) + octave up + percussion density rise |
| 9 Outro | Return to base cell, thins out |

## Per-section harmonic regions

| Section | Bars (chords) |
|---|---|
| Intro | C C C |
| Phase1 | C Gsus C |
| Phase2 | Am Dsus C |
| Phase3 | Dsus C Gsus |
| Transpose | Gsus C Am |
| Inversion | C Am Dsus |
| Retrograde | Am Dsus Gsus |
| Augment | Dsus Dsus Gsus |
| Climax | Gsus Am Dsus |
| Outro | C C C |

## Verification (real numbers)

- MIDI sizes: phase1 556 B, phase2 3900 B (both > 40).
- Zero-drift: 5 voice tracks, all 57600 ticks.
- Pitched onsets: 259; off-grid 0; scale violations 0; chord violations 0.
- Audio: FluidSynth 67.2 s, peak 0.813, RMS 0.114, silence 8.82% (< 30% flag).

## Files

- `MIDI/204-minimalism-phase-expanded.mid` (Phase 2, rules)
- `MIDI/204-minimalism-phase-expanded-phase1.mid` (Phase 1, raw)
- `Audio/204-minimalism-phase-expanded.ogg` / `.wav`
- `Analysis/grid_visualization.txt`, `Analysis/rework_audit.json` (source),
  `Analysis/rework_verify.json`, `Analysis/render_stats.json`
- `index.html`, `README.md`
