# 214-blues-antcolony

**Style:** Blues · **Method:** 041 Ant Colony Optimization Path Finding (ACOPF) · **Layer:** concrete · **Date:** 2026-09-30

12-bar blues (two choruses, 24 bars) in E, composed with a two-phase ant-colony
pipeline:

- **Phase 1** (`MIDI/214-blues-antcolony-phase1.mid`): raw ACO draft — a colony of
  8 ants traverses a chromatic pitch graph over 192 eighth-note slots; the
  emergent best-tour is an unquantized, chromatic melodic contour.
- **Phase 2** (`MIDI/214-blues-antcolony.mid`): musicom rules post-processing —
  onsets snapped to the 8th grid, pitches snapped to per-bar blues chord tones,
  plus a full 5-voice band (Piano, Bass, Harmonica, Trumpet, Drums).

## Listen

- `Audio/214-blues-antcolony.ogg` — full arrangement (Opus)
- `Audio/214-blues-antcolony-phase1.ogg` — raw phase-1 draft (Opus)

## Verification (see REPORT.md for full numbers)

- Grid audit: **0 off-grid** across all 5 voices (828 onsets)
- Harmony audit: **0 out-of-scale / 0 out-of-chord** (516 pitched notes)
- Zero-drift: `validate()` PASSED both phases
- Audio: 62.47 s, 7.68% silence (tail only), peak 0.58, 99.2% tonal

## Files

```
MIDI/       214-blues-antcolony.mid (+ -phase1.mid)
Audio/      *.wav + *.ogg (+ -phase1.*)
Analysis/   grid_visualization.txt, summary.json
REPORT.md   full composition record
provenance  .json sidecars next to every artifact
```