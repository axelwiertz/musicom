# 243-world-melisma-rework — REPORT

## Source
- Project: `World/072-world-melisma` (markov-harmony M-022)
- Identity: D dorian, 100 BPM, Pan Flute lead + String counter + Warm Pad + Fretless Bass + world percussion

## Audit result (current standards)
| Standard | Result |
|---|---|
| 1. Engine (UnitMatrixComposer) | PASS |
| 2. Zero-drift | PASS (5 voice tracks @ 38400 ticks) |
| 3. Rhythm-grid sync | **FAIL** — 100 pitched onsets off-grid (counter +60/+1020, pad +30 per section) |
| 4. >=4 voice tracks | PASS |
| 5. Two-phase artifacts | PASS |
| 6. provenance.json + index.html | **FAIL** — index.html missing |

**Decision: REDESIGN** (2 standards failed). Rebuilt from scratch through canonical
`UnitMatrixComposer`, preserving only identity. Non-compliant off-grid timing discarded.

## What changed (rework)
- Counter/pad onsets snapped to the 120-tick (16th) grid (was +60/+30/+1020 offsets).
- Added `index.html` dashboard.
- Longer form: 5 sections -> 8 sections (32 bars total).
- Per-section harmonic regions (each section its OWN 4-bar progression); section
  roots derived from MIDPOINT chord, avoiding the bar-0 tonic bug.
- Chord-tone quantization is chord-tone-preserving (no post-clamp that snapped
  chord tones to out-of-chord C).

## Form (8 sections x 4 bars = 32 bars, 100 BPM, D dorian)
```
Intro  i   i   VII IV
Verse  i   v   III IV
Chorus IV  v   VII i
Verse2 i   v   III IV
Bridge vi° ii  v   VII
Chorus2 IV v   VII i
Drop   i   VII i   v
Outro  i   IV  VII i
```
section_roots (midpoint): [C, F, C, F, A, C, D, C] — varied, not all tonic.

## Variation techniques (7, mapped to sections)
1. **Diminution** — Chorus (sec2): motif compressed to 8th-note subdivision, restated twice.
2. **Register shift (+12)** — Verse2 (sec3): motif octave-up.
3. **Inversion (axis D5)** — Bridge (sec4): motif mirrored around D5.
4. **Diatonic transposition (+1 scale degree)** — Chorus2 (sec5): motif shifted up one dorian degree.
5. **Retrograde** — Drop (sec6): motif pitch sequence reversed over the groove.
6. **Augmentation** — Outro (sec7): motif first half slowed 2x (half-notes).
7. **Density rise** — percussion ramp Intro .35 -> Chorus 1.0 -> Drop .2 -> Outro .1.

## Verification (read-only mido)
- phase2 MIDI: 5 voice tracks, length 61440 ticks, zero-drift PASS
- pitched onsets 328 | off-grid 0 | scale violations 0 | chord violations 0
- phase1 MIDI: 1 voice, 61440 ticks, raw (pre-rules) — chord-membership intentionally not enforced
- audio: 81.7 s, peak 0.963, silence ratio 5.5% (all 8 sections RMS ~0.16)

## Files
- MIDI/243-world-melisma-rework.mid
- MIDI/243-world-melisma-rework-phase1.mid
- Audio/243-world-melisma-rework.wav
- Audio/243-world-melisma-rework.ogg
- Analysis/grid_visualization.txt, Analysis/summary.json
