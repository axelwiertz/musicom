# 262 — Harmonic Chorale Variations (Experimental)

Rework of **067-harmonic-chorale** (Method 023 Harmonic Series / Overtone
Composition). Source failed audit standard 6 (missing `index.html`) → full
rebuild through the canonical `UnitMatrixComposer`, then extended into a
**longer, more varied** piece.

## Concept

The **natural harmonic series** of a fundamental G3 (MIDI 55) produces an
ascending "overtone staircase" — consecutive 12-TET-quantized partials yield
the interval motif `[12,7,5,4,3,3,2,2,2,2,2,1,1,1,1]`. That contour is the
melodic DNA. In the raw draft it leaks chromatic tones (harmonics 7/11/13/14/15
are non-diatonic); Phase 2 quantizes each note to its bar's chord tone and
builds a four-part chorale around it.

## Parameters

| Param | Value |
|---|---|
| Key | F major (ionian) |
| BPM | 92 · 4/4 (480 tpb, 1920 ticks/bar) |
| Form | 6 sections × 4 bars = **24 bars** |
| Voices | Soprano (Flute 73) / Alto (Strings 48) / Tenor (Cello 42) / Bass (Contrabass 43) |
| Harmony | per-section: I-vi-IV-V · V-IV-vi-I · V-I-ii-V · IV-ii-V-I · I-IV-ii-V · IV-V-I-I |
| Method | 023 Harmonic Series / Overtone Composition |
| Seed | 262 (humanize 263) |

## Variation techniques (6)

1. **Retrograde** — section B (intervals + rhythm reversed)
2. **Transposition up a 5th** — section C (+7 semitones)
3. **Inversion** — section D (intervals negated)
4. **Diminution** — section E (durations halved → 2× density)
5. **Register shift up** — section E (soprano 72–88)
6. **Augmentation** — section F (durations doubled) + register shift down

## Files

- `MIDI/` — `-phase1.mid` (raw), `-perfect.mid` (grid-locked), `-humanized.mid`
- `Audio/` — Opus OGG + WAV renders of all three
- `Analysis/` — `grid_visualization.txt`, `summary.json`, `verify.json`
- `index.html` — dashboard (VoltAgent styling)

See `REPORT.md` for the full audit, verification numbers, and method notes.
