# 231 — Perlin Noise × LPC Rework

**Method 040** (Perlin Noise Composition) — a redesign/extension of
`056-perlin-lpc`.

## Concept

Perlin noise (fractal Brownian motion, seed 42) drives pitch contour, rhythm
density, and velocity. A raw chromatic single-voice draft is rules-processed into
a 16-bar, 4-voice texture in D Dorian (Flute lead + String pad + Electric Bass +
ch9 drums) with per-bar chord quantization, rhythm-grid snapping, and
voice-leading correction.

## Parameters

| Param | Value |
|-------|-------|
| Key | D Dorian (D E F G A B C) |
| BPM | 80 |
| Meter | 4/4 (480 tpb, 1920 ticks/bar) |
| Form | 8 sections × 2 bars = 16 bars |
| Harmony | per-bar Dorian progressions; midpoint degrees `[VII, IV, III, v, IV, VII, v, i]` |
| Voices | Lead (Flute), Pad (Strings), Bass (Electric Bass), Drums (ch9) |
| Seed | 42 |

## Variation techniques

1. Transposition (+5 / +12 / −12)
2. Inversion (axis 67, 65)
3. Diminution (×0.5)
4. Augmentation (×2.0)
5. Register shift (+12 / −12)
6. Density rise (16th hi-hat in Chorus)

## Two-phase architecture

- **Phase 1** `-phase1.mid`: raw Perlin fBm draft, chromatic, single voice, pre-rules.
- **Phase 2** `.mid`: rules-processed multi-voice (chord quantization,
  grid snap, block harmony, voice-leading, zero-drift gate).

## Files

- `MIDI/` — phase 1 + phase 2 (`.mid` + provenance sidecars)
- `Audio/` — WAV + OGG renders
- `Analysis/` — `grid_visualization.txt`
- `index.html` — dashboard
- `provenance.json` — root sidecar
- `compose.py` — generator (run with `$MUSICOM_PYTHON compose.py`)
