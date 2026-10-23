# 258-groove-rbn-critical

**Genre:** Groove · **Method:** 082 Random Boolean Network Criticality
Composition (RBNCC) · **Layer:** concrete · **Paradigm:** Nature-Led

**Key:** A natural minor · **BPM:** 104 · **4/4** · **Form:** aba (A 8 | B 8 | A 8 = 24 bars)

## Concept

A Kauffman random Boolean network (N=24, K=2, p=0.5 — the critical point,
edge of chaos) drives the composition. Its synchronous state trajectory
falls into an attractor cycle (transient μ=6, cycle λ=22); the transient is
connective/tension material and the attractor cycle is the repeating groove.
Phase 2 projects the raw chromatic draft onto A-natural-minor 7th-chord
harmony and a full groove texture.

## Two-phase architecture

- **Phase 1** (`-phase1.mid`) — raw RBN draft, single voice, chromatic
  (off-scale) pitch classes, OFF-GRID onsets. No harmony.
- **Phase 2** (`-perfect.mid` + `-humanized.mid`) — grid snap + tiered pitch
  quantization (strong beats = in-scale AND in-chord, weak = in-scale) + full
  5-voice groove texture (clavi lead / rhodes comp / electric bass / synth
  pad on B / groove drums).

## Harmony (all diatonic to A natural minor)

| Section | Bars | Progression |
|---|---|---|
| A1 | 0–7 | i7 · i7 · VI7 · VII7 · i7 · i7 · VI7 · VII7 |
| B  | 8–15 | III7 · VI7 · iv7 · v7 · III7 · VI7 · iv7 · v7 |
| A2 | 16–23 | i7 · i7 · VI7 · VII7 · i7 · i7 · VI7 · VII7 |

(Am7 · Am7 · Fmaj7 · G7 · Am7 · Am7 · Fmaj7 · G7 · Cmaj7 · Fmaj7 · Dm7 · Em7 …)

## Voices (instrument registry)

| Voice | Instrument | GM program | Channel |
|---|---|---|---|
| Clavi | Clavinet | 7 | 0 |
| Rhodes | Electric Piano 1 | 4 | 1 |
| Bass | Electric Bass (finger) | 33 | 2 |
| Pad | Pad 1 (new age) | 88 | 3 |
| Drums | Drum Kit | — | 9 |

## Artifacts

- `MIDI/258-groove-rbn-critical-phase1.mid` — raw RBN draft
- `MIDI/258-groove-rbn-critical-perfect.mid` — grid-locked phase 2
- `MIDI/258-groove-rbn-critical-humanized.mid` — humanized phase 2
- `Audio/*.ogg` — mastered listening renders (perfect / humanized / phase1)
- `Analysis/verify.json`, `Analysis/summary.json`, `Analysis/grid_visualization.txt`
- `REPORT.md` — full record (the primary document)

See `REPORT.md` for the full grid/harmony/humanization/mastering audit.
