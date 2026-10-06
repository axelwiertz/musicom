# 225-country-steel-rework — Rework Report

## Decision: REDESIGN

Source `Country/038-steel-guitar-demo` failed 6/6 current engine standards
(hand-rolled mido, drift, off-grid, too few tracks, no phase1, no provenance/index).
Rebuilt from scratch via `UnitMatrixComposer`; only the musical DNA (Country,
G major, 90 BPM, steel-slide `1→3→5` motif, G–C–D) was carried over.

## Source identity

```
genre   Country        key  G major       bpm  90
motif   steel slide 1->3->5 (G->B->D), ascending slide contour
prog    G C D (I-IV-V)
instr   steel guitar, acoustic guitar, acoustic bass, drums
```

## Audit JSON

`Analysis/rework_audit.json` (written into the source project at
`Country/038-steel-guitar-demo/Analysis/rework_audit.json`).

## New form — 24 bars, 5 sections

Intro(2) → Verse(8) → Chorus(8) → Bridge(4) → Outro(2)

Per-section harmonic regions (midpoint chord = section root):
- Intro: G G — root **G (I)**
- Verse: G C D G / C G D G — midpoint **C (IV)**
- Chorus: C G Am D / C G D G — midpoint **C (IV)**
- Bridge: Em C Am D — midpoint **Am (ii/vi)**
- Outro: C G — root **G (I)**

## Variation techniques applied

| # | Technique | Where |
|---|-----------|-------|
| 1 | Register shift (+octave) | Chorus lead 79–88 vs verse 64–79 |
| 2 | Retrograde | Bridge reverses hook contour (descent) |
| 3 | Augmentation | Outro lead + bridge/outro bass (whole/half notes) |
| 4 | Counterline | Fiddle (violin) pads in chorus, answer in bridge |
| 5 | Per-section harmonic regions | distinct progression per section |
| 6 | Density rise | drums sparse→backbeat→16ths→breakdown |

## Two-phase architecture

- **Phase 1** `MIDI/225-country-steel-rework-phase1.mid` — raw steel-slide random
  walk, single voice, sub-grid onset jitter (±30 ticks) + occasional out-of-key
  pitch deviation. 141 onsets, all off-grid, 25 scale + 55 chord violations
  **by design** (pre-rules draft).
- **Phase 2** `MIDI/225-country-steel-rework.mid` — musicom rules post-process:
  chord-tone quantization per bar (`t//BAR`), 120-tick grid snap, dedup of
  collided (onset,pitch), register enforcement (55–90). 5 voices.

## Verification numbers (read-only mido)

```
phase2: 5 voice tracks x 46080 ticks (zero-drift OK)
        off_grid = 0, scale_violations = 0, chord_violations = 0
phase1: 1 voice track (raw), 141 off-grid onsets (expected)
```
