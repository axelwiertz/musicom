# 263-chanson-frieze-canon

**Genre:** Chanson · **Method:** 091 — Coxeter–Conway Frieze Pattern Composition (CCFPC) · **Layer:** concrete (Rules-Based)
**Key:** D major (ionian) · **BPM:** 92 · 4/4 · **Form:** verse-chorus (Intro 4 | Verse 8 | Chorus 8 | Verse2 8 | Chorus2 8 | Outro 4 = 40 bars)
**Date:** 2026-10-24 (nightly composition job) · **Seed:** 20261024 · humanize seed 20261025

## Concept

A lyrical chanson whose melody is the vertical contour of a Coxeter–Conway
frieze pattern (period n=16, one 4/4 bar of 16ths). The fan-triangulation
quiddity `[14,1,2,…,2,1]` generates the frieze via Euler continuants; section
development comes from **Ptolemy diagonal flips** (quiddity mutation) across
section boundaries. The oboe lead reads the frieze rows; a clarinet reads the
**glide-reflection mirror row** at the off-16ths as an inverted canon.

## Two-phase

- **Phase 1** (`-phase1.mid`): raw frieze draft, single oboe voice, chromatic
  (off-scale pcs {0,3,5,8,10}), off-grid onsets. No harmony, no grid.
- **Phase 2** (`-perfect.mid` + `-humanized.mid`): grid snap + tiered pitch
  quantization (strong → in-scale AND in-chord; weak → in-scale) + full 6-voice
  chanson texture. Dual-version export (perfect grid-locked / humanized).

## Files

- `MIDI/263-chanson-frieze-canon-{phase1,perfect,humanized}.mid`
- `Audio/263-chanson-frieze-canon-{perfect,humanized,phase1}.ogg`
- `Analysis/{grid_visualization.txt,summary.json,verify.json}`
- `REPORT.md` — full record (grid/harmony/humanization/mastering audits)

Full detail: `REPORT.md`.
