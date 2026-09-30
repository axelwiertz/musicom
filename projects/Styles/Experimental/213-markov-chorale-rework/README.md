# 213 — Markov Chain Chorale Rework

**Method 020** (First-Order Markov Chain Sequencing) — a rework/extension of
`066-markov-chain-chorale`.

## Concept

A stepwise-Markov pitch-class chain (neighbour-biased, with chromatic escape
states that leak non-diatonic tones into the raw draft) drives a 16-bar chorale in
F major. A second first-order chain over durations {1/8, 1/4} governs rhythm. The
raw single-voice draft is rules-processed into a 5-voice texture (SATB + ch9 drums)
with per-bar chord quantization, rhythm-grid snapping, and voice-leading correction.

## Parameters

| Param | Value |
|-------|-------|
| Key | F major (ionian) |
| BPM | 92 |
| Meter | 4/4 (480 tpb, 1920 ticks/bar) |
| Form | 8 sections × 2 bars = 16 bars |
| Harmony | per-bar progressions; midpoint chords `[IV, I, ii, V, V, IV, iii, I]` |
| Voices | Soprano (Flute), Alto/Tenor (Strings), Bass, Drums (ch9) |
| Seed | 213 |

## Variation techniques

1. Transposition (+5 / +12 / −12)
2. Inversion (axis 69, 66)
3. Diminution (×0.5)
4. Augmentation (×2.0)
5. Register shift (+12 / −12)
6. Density rise (16th hi-hat in Chorus)

## Two-phase architecture

- **Phase 1** `-phase1.mid`: raw Markov draft, chromatic, single voice, pre-rules.
- **Phase 2** `.mid`: rules-processed multi-voice (chord quantization,
  grid snap, block harmony, voice-leading, zero-drift gate).

## Files

- `MIDI/` — phase 1 + phase 2 (`.mid` + provenance sidecars)
- `Audio/` — WAV + OGG renders
- `Analysis/` — `grid_visualization.txt`, audit + summary
- `index.html` — dashboard
- `provenance.json` — root sidecar
- `compose.py` — generator (run with `$MUSICOM_PYTHON compose.py`)