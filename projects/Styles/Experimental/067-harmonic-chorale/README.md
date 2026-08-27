# 067 — Harmonic Series Chorale (Method 023)

**Composition method:** 023 — Harmonic Series / Overtone Composition (`generators/harmonics.py`)

## Concept

The **natural harmonic series** is the acoustic fingerprint of every pitched
sound: for a fundamental `f0`, the partials sound at `f0 × n` (n = 1, 2, 3, …).
Musicom's `HarmonicsGenerator` materializes that series through music21's
`note.Pitch.getHarmonic(n)`. The raw draft walks the partials of a **G3 (MIDI
55)** fundamental in acoustic order (1…16) with a per-cycle stride pattern
`(3,4,5,4)` so later cycles re-enter the series at different partials instead
of repeating 1…16. Rhythm is a *direct acoustic by-product*: odd partials get
a quarter, even partials get an eighth. The key contrast with 066 (Markov
chains — probabilistic memory) and 065 (memoryless Monte Carlo) is that this
method is **deterministic physics**: the raw material comes from a natural
resonance table, not a random walk.

## Parameters

| Param | Value |
|-------|-------|
| Key | F major (ionian) |
| BPM | 92 |
| Meter | 4/4 (480 tpb, 1920 ticks/bar) |
| Form | 4 sections × 2 bars = 8 bars |
| Harmony | I - vi - IV - V (F - Dm - Bb - C) |
| Voices | Soprano (Flute), Alto/Tenor (Strings), Bass |
| Fundamental | G3 (MIDI 55), partials 1..16 |
| Cycle strides | (3, 4, 5, 4) |
| Duration rule | odd partial → quarter, even partial → eighth |
| Seed | 67 |

## Why the Raw Draft Leaks (pre-rules signature)

Harmonics 7, 11, 13, 14, 15 of any fundamental are **not** members of a
diatonic scale — and in nature they are microtonal (just intonation) anyway.
12-TET rounding puts them on B♭, F♯, A♯, B♭, C♯ — all outside F major.
**14 of 41 raw events (34%) are non-diatonic**, proof the Phase 1 file is
genuinely pre-rules: no scale enforcement, no chord context, no voice leading.

## Two-Phase Architecture

- **Phase 1 — raw draft** (`MIDI/067-harmonic-chorale-phase1.mid`):
  single voice, pitch range 55–103, raw acoustic partials in harmonic order,
  rhythm from partial parity. Chromatic leak present (see above).
- **Phase 2 — rules-processed** (`MIDI/067-harmonic-chorale.mid`):
  each raw partial snapped to the nearest diatonic triad tone (soprano,
  range 65–86), Alto/Tenor/Bass built as diatonic block harmony via the
  canonical `Scale7ChordDegree.get_diatonic_note()`, voice-leading optimized,
  Phase 2c inversion-rotation correction applied, harmonic function validated.

## Validation

- Phase 1 zero-drift `validate()`: **PASS (True)**
- Phase 2 zero-drift `validate()`: **PASS**
- Both files: max track end tick = 15360 (= 4 × 3840), all tracks equal length
- Parallel/hidden fifth violations (classical): **0** (0 chords needed re-voicing)
- Harmonic function report: I→vi (tonic→any, legal), vi→IV (prolongation,
  free), IV→V (subdominant→dominant, legal) — builds a perfect V→I cadence.

## Artifacts

```
MIDI/067-harmonic-chorale.mid              (1605 B, 5 tracks / 4 voices)
MIDI/067-harmonic-chorale-phase1.mid       (426 B, 1 raw voice)
MIDI/*.mid.provenance.json                 (both artifacts)
Analysis/grid_visualization.txt            (4×4, 3840 ticks/section)
Notes/lesson-harmonic-series.md
compose.py                                 (generator, reproducible seed)
```

## Status

DONE — MIDI only (no audio render, per composition-job contract). Standalone
project under `Styles/Experimental/`.
