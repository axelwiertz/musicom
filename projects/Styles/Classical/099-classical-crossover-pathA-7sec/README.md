# 099 - Classical Crossover, Path A Top-Down, 7 Sections

**Status:** complete (2026-09-17)
**Form:** Intro 4 | A 8 | B 8 | Dev 8 | A' 8 | B' 8 | Coda 8 = 52 bars @ 96 BPM, C major
**Path:** A (top-down L4→L3→L2→L1), framework-first + per-section method swap

## Method map

| Section | Bars | Method | Character |
|---|---|---|---|
| Intro | 4 | 023 Tendency Masking | solo piano corridor, rising bounds |
| A | 8 | 001 skeleton + 002 Markov | diatonic theme, half notes |
| B | 8 | 079 Tintinnabuli (T pos 1) | M-voice arch + triad shadow, counter joins |
| Dev | 8 | ABS-003 Z-swap + ABS-004 | tension peak, tremolo pad |
| A' | 8 | 002 variant | same theme, denser quarters, +12 register |
| B' | 8 | 079 Tintinnabuli (T pos 2) | same talea, shifted shadow |
| Coda | 8 | 018 Schillinger 3x2 | decelerating, progressive dropout |

ABS-001 tension targets: 0.0 / 0.3 / 0.5 / 1.0 / 0.4 / 0.5 / 0.1
Harmonic regions per section (no global loop); roots via midpoint chord;
all degrees through `rules/harmony.parse_degree` + `MODE_OFFSETS`.

## Artifacts

- `MIDI/099-classical-7sec.mid` (8401 B) — phase 2, rules-processed
- `MIDI/099-classical-7sec-phase1.mid` (2351 B) — raw method drafts, pre-rules
- `Audio/099-classical-7sec.wav` (23.4 MB) + `.ogg` (923 KB) — SP-001 FluidSynth
- `Analysis/grid_visualization.txt`, `tension_curve.json`, `audit.json`

## Verification (real output)

- zero-drift: voice tracks all 99840 ticks — PASS
- harmony: scale 0/1047, chord 0/1047 violations — PASS (after fixing
  counter-flute: was blind pitch-5 shift = 55 chord violations; now
  chord-quantized third below lead)
- pitch variety: Lead 17 unique, Counter 9, Piano 10, Bass 5 — PASS
- off-grid onsets (120-tick grid): 0/1047 — PASS
- Coda dropout: Lead 48 notes bars 0-3, Counter 0, Piano/Pad 18, Bass 12 — PASS
- bass motion: 5 distinct roots [36,38,41,43,45] — PASS
- render: 132.6 s, 2.4% silence — PASS
- preflight: COMPLIANT, exit 0

## Notes

- Markov states are degree indices 0..6, converted via scale table, then
  chord-quantized in phase 2 (never pitch classes as states).
- Dev's Z-swap: triads have no Z-partner (Z starts at tetrads), so the swap
  resolves to the identity for triad bars — the parsimonious VL (≤2 semitone
  octaver-hunt) is the audible tension driver. True Z-swap pairs start at
  4-Z29/4-Z15; a future Dev-2 would use seventh chords to trigger real swaps.
- Tintinnabuli `position=-1` clamps to the pool's lowest tone (engine quirk,
  all-notes-equal) — B' uses position 2 instead of -1 for its variation.
