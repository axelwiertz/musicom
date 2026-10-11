# 235 — Arabic Rast Rework (report)

## Concept
A 24-bar, 6-section Arabic Rast maqam suite, rebuilt from source project
`071-arabic-rast-ant-colony` (Method 041 Ant-Colony Optimization Path Finding).
Preserves the source identity — genre Arabic, key D Rast (12-TET approximation
= D Phrygian: D Eb F G A Bb C), 100 BPM, 4/4, flute-lead + strings + bass +
pad + drums (maqsum 3+3+2) instrumentation, ant-colony generative DNA — and
extends it with 6 distinct variation techniques.

## Source identity (preserved)
| Field | Value |
|---|---|
| Genre | Arabic (Rast maqam) |
| Key | D Rast (Phrygian approx) |
| Tempo | 100 BPM |
| Meter | 4/4 |
| Method | 041 ACOPF (ant colony) |
| Rhythm | Maqsum 3+3+2 |
| Voices | Lead (flute), Harmony (strings), Bass, Pad, Drums (ch9) |

## Audit result (source 071)
| Standard | Result |
|---|---|
| 1 engine-authored | PASS (`UnitMatrixComposer`) |
| 2 zero-drift | PASS (5 tracks × 30720 ticks) |
| 3 rhythm-grid sync | **FAIL** (32 off-grid pitched onsets) |
| 4 ≥4 voice tracks | PASS (5) |
| 5 two-phase artifacts | PASS |
| 6 provenance.json + index.html | **FAIL** (both missing) |

→ **redesign_required = true**. Rebuilt from scratch through the canonical
`UnitMatrixComposer` workflow.

## What changed (redesign → new longer piece)
1. Form extended 16 bars (A/B/A2/C) → **24 bars, 6 sections**
   (Intro/A/B/A2/C/Outro).
2. Rhythm-grid sync fixed: every pitched onset snapped to the 120-tick
   (16th) grid; off-grid count 32 → **0**.
3. Per-section harmonic regions: each section has its own progression;
   section root taken from the **midpoint** chord (not bar-0 tonic). Section
   roots = Eb, Cm, Bb, Dm, Cm, Eb (varied, no all-tonic collapse).
4. Key/scale + chord discipline: every pitched note is a chord tone of its
   own bar (floor `t//BAR` attribution); scale + chord violations = 0.
5. Added a Counterline voice (violin) in C + Outro (density rise).
6. provenance.json sidecars (both phases) + index.html dashboard written.

## Variation techniques (6)
| Section | Bars | Technique |
|---|---|---|
| Intro | 0-3 | register shift −12 + sparsification |
| A | 4-7 | identity (ant-colony motif) |
| B | 8-11 | transposition +P4 (→ iv/bIII/bVI region) |
| A2 | 12-15 | retrograde (pitch contour reversed) |
| C | 16-19 | augmentation (durations ×2) + counterline (density) |
| Outro | 20-23 | inversion (around D4) + diminution (×0.5) → cadence |

## Per-section harmonic regions
| Section | Bars | Chords (per bar) | Midpoint root | Quality |
|---|---|---|---|---|
| Intro | 0-3 | i i bII i | Eb (bII) | maj |
| A | 4-7 | i bII bVII i | C (bVII) | min |
| B | 8-11 | iv bIII bVI iv | Bb (bVI) | maj |
| A2 | 12-15 | i bII i i | D (i) | min |
| C | 16-19 | bII bVI bVII bVII | C (bVII) | min |
| Outro | 20-23 | i bII bII i | Eb (bII) | maj |

## Verification (read-only mido)
Phase 2 (deliverable): 6 voice tracks × 46080 ticks (zero-drift PASS),
362 pitched onsets, **off-grid 0**, **scale violations 0**,
**chord violations 0**. Audio: FluidSynth WAV (64.8 s) → Opus OGG;
silence 9.0%, peak 1.0 (49 clipped samples → re-encoded with volume=0.89).

## Files
- `MIDI/235-arabic-rast-rework.mid` (phase 2, rules)
- `MIDI/235-arabic-rast-rework-phase1.mid` (phase 1, raw)
- `Audio/235-arabic-rast-rework.ogg` (Opus)
- `Audio/235-arabic-rast-rework.wav` (FluidSynth render)
- `Analysis/grid_visualization.txt`, `Analysis/grid_visualization_phase1.txt`
- `Analysis/rework_audit.json` (written into source 071)
- `index.html`, `README.md`, `compose.py`
