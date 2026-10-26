# 269-techno-contour-theory

**Method 095 — Contour Theory Composition (CTC)** · layer: **abstract** → concrete interpretation
**Style:** Techno · **Key:** A natural minor · **BPM:** 128 · **Form:** intro-break-drop-outro (24 bars)

## Concept

A melodic contour (CSEG) is the *shape* of a melody — an ordered sequence of
pitch positions described by up/down/same relations, independent of exact
pitch. This piece composes a minimal-techno track by walking a 4-member
**contour class** (Prime + Inversion + Retrograde + Retrograde-Inversion), then
mapping each contour *rank* to a scale degree of A-natural-minor pentatonic
(A C D E G).

Two-phase architecture:
- **Phase 1** (`-phase1.mid`): raw contour draft — single clavi voice, off-grid
  onsets, octave register drift, no harmony. The abstract layer.
- **Phase 2** (`-perfect.mid` / `-humanized.mid`): grid-lock to 16ths, tiered
  weight-aware snap (strong → in-scale AND in-chord, weak → in-scale), full
  techno texture (clavi contour lead + synth pad + synth bass + 4-on-floor drums).

## Harmony

4-bar cycle `i — bVI — bVII — i` (Am — F — G — Am), repeated across all 24 bars.

## Voices (instrument registry)

| Voice | Instrument | Program | Channel |
|-------|-----------|---------|---------|
| Lead  | Clavi      | 7       | 0       |
| Pad   | Pad 1 (new age) | 88 | 1       |
| Bass  | Synth Bass 1 | 38    | 2       |
| Drums | Drum Kit    | 0       | 9       |

## Contour class

```
BASE (P)  = [0, 3, 1, 2, 4, 1]   [+, -, +, +, -]
I         = [4, 1, 3, 2, 0, 3]   [-, +, -, -, +]
R         = [1, 4, 2, 1, 3, 0]   [+, -, -, +, -]
RI        = [3, 0, 2, 3, 1, 4]   [-, +, +, -, +]
```

rank 0..4 → A3 C4 D4 E4 G4 (A-minor pentatonic degrees).

## Files

- `MIDI/` — phase1 + perfect + humanized (each with provenance sidecar)
- `Audio/` — perfect + humanized + phase1 OGG (Opus) + WAV
- `Analysis/` — grid_visualization.txt, summary.json, verify.json
- `REPORT.md` — full audit report

## Scripts

- `compose.py` — two-phase composition + dual export
- `verify.py` — grid / harmony / zero-drift audit (mido read-only)
- `render.py` — FluidSynth render + master (LUFS) + Opus encode
