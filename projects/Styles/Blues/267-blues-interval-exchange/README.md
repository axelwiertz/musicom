# 267 — Blues Interval Exchange (Method 121 IETC)

Nightly autonomous composition. **Method 121 IETC** (concrete, Rules-Based):
a 7-block Interval Exchange Transformation whose block widths encode tonal
gravity. Unique ergodicity (irrational rotation number α = 1/φ²) forces each
scale degree's visit frequency to equal its width — verified at 5.4e-6 over
400k iterates.

| axis | pick |
|---|---|
| style | Blues |
| form | `blues-12` (12-bar minor blues) |
| key | Ab natural minor (aeolian) |
| tempo | 100 BPM |
| voices | Harmonica (lead) · Drawbar Organ (comp) · Double Bass (bass) · Drum Kit |

**Harmony** (diatonic m7): `i7 i7 i7 i7 | iv7 iv7 | i7 i7 | v7 iv7 | i7 i7`

**Two-phase**: phase-1 raw IET orbit (single harmonica, off-grid) →
phase-2 tiered weight-aware snap (strong→chord, weak→scale) + blues texture,
dual-exported (perfect + humanized).

**Verify (real numbers)**: zero-drift 23040 × 4 voices · perfect off-grid **0**
· humanized off-grid **187** · harmony 0/0/0 on all 3 pitched voices (strict
chord) · ergodicity max err **5.4e-6** · mastered −14.08 LUFS / −1.0 dBTP
(target −14, blues). See `REPORT.md` + `Analysis/verify.json`.

## Files

- `MIDI/*-phase1.mid` — raw IET draft (off-grid, single voice)
- `MIDI/*-perfect.mid` — grid-locked rules-processed
- `MIDI/*-humanized.mid` — blues-profile jitter (A/B the human feel)
- `Audio/*.ogg` / `*.wav` — mastered −14 LUFS
- `Analysis/grid_visualization.txt` — rhythm-DNA grid
