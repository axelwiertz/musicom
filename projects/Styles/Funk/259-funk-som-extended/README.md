# 259 - Funk Style, Rework of 098-funk-som (Method 075 SOM-C)

**Status:** Complete (2026-10-23)
**Style:** Funk
**Method:** 075 Self-Organizing Map Composition (SOM-C) — rework/extension
**Key:** F minor (aeolian) · **BPM:** 104 · 4/4 · 480 TPB
**Form:** 8 sections × 4 bars = 32 bars (Intro | Verse | Chorus | Bridge | Verse2 | Chorus2 | Break | Outro) = 61,440 ticks (~73.9 s)
**Source:** `098-funk-som` (6 sections × 4 bars = 24 bars)

---

## What this is

Nightly rework of `098-funk-som`. The source core passed 5/6 engine standards
(engine, zero-drift, grid-sync, track setup, two-phase); it failed standard 6
(missing `index.html` + root `provenance.json`). This is a full REBUILD through
the canonical `UnitMatrixComposer` engine, preserving the Funk / F-minor /
104 BPM / SOM-C melodic contour / trumpet+sax+piano+bass+drum-kit identity,
made **longer** (24 → 32 bars) and **more varied** (7 variation techniques).

## Two-Phase Architecture

- **Phase 1 (`259-funk-som-extended-phase1.mid`)**: single-voice raw SOM-C draft.
  4×4 toroidal Kohonen map trained on 8 funk atoms; Markov walk yields the
  pitch-index trajectory. Off-grid onsets (133/134 off 16th grid by design),
  in-scale, no harmony.
- **Phase 2 (perfect + humanized)**: musicom rules post-processing —
  16th-grid snap, chord-tone quantization per bar (floor `t//BAR`), per-section
  variation transform, voice-leading cap (≤10 semitones), register/range
  enforcement, dedupe collisions, 5-voice texture, zero-drift landmark padding.

## Variation techniques (per section)

| Section | Technique |
|---|---|
| Intro | register shift (low) + sparse |
| Verse | base motif (SOM-C contour) |
| Chorus | transposition (+3 scale degrees) + density rise |
| Bridge | retrograde + register shift (upper) |
| Verse2 | inversion (pivot degree 3) |
| Chorus2 | augmentation (×2) + 7th chord color |
| Break | diminution (16th runs) + sax counterline |
| Outro | diminution fragment + fade |

## Verification

| Gate | Result |
|---|---|
| Zero-drift | PASS — 5 voice tracks × 61,440 ticks |
| Off-grid (perfect) | 0 / 614 pitched onsets |
| Off-grid (humanized) | 575 / 614 (jitter ran) |
| Scale violations | 0 (perfect, humanized, phase1) |
| Chord violations | 0 (perfect); 14 (humanized, bar-seam jitter only) |
| LUFS / peak | mastered to −13 LUFS, −1 dBTP |

## Artifacts

- `MIDI/259-funk-som-extended-phase1.mid` (+ provenance)
- `MIDI/259-funk-som-extended-perfect.mid` (+ provenance)
- `MIDI/259-funk-som-extended-humanized.mid` (+ provenance)
- `Audio/259-funk-som-extended-{perfect,humanized,phase1}.{wav,ogg}`
- `Analysis/grid_visualization.txt`, `Analysis/summary.json`, `Analysis/verify.json`
- `index.html` (VoltAgent dashboard), `REPORT.md`
