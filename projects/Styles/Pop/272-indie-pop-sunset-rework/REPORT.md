# 272-indie-pop-sunset-rework — Rework Report

## Source audit
- **Chosen source**: `Styles/Pop/indie-pop-sunset` (legacy project, mtime 2026-06-17)
- **Genre**: Indie Pop
- **Audit result**: **REDESIGN REQUIRED** — 4 standards failed:
  1. `engine`: authored via legacy `music21 + RhythmGenerator` (`src/regen.py`, `sys.path.insert('/root/musicom')`), NOT `UnitMatrixComposer` / `musicom_workflow`.
  2. `track_setup`: only 3 tracks (1 conductor + 2 voice), fewer than 4 voice tracks, no ch9 drum kit.
  3. `two_phase`: no `-phase1.mid`.
  4. `provenance`: `provenance.json` missing.
- **Passed**: zero-drift (2 voice tracks equal 15360 ticks), rhythm-grid (0 off-grid).
- Detailed audit: `../indie-pop-sunset/Analysis/rework_audit.json`

## Preserved musical identity (DNA)
- Key: **D Dorian** (D E F G A B C; pcs `[2,4,5,7,9,11,0]`)
- Pitch motif (semicolor contour): **(2,3,−2,0,5)** — step up, skip up, step down, hold, octave leap
- Rhythm: **Euclidean 5-in-8 clavé** (son 3-2 feel)
- Tempo: **120 BPM**

## What changed (redesign, from scratch via canonical engine)
- Rebuilt through `UnitMatrixComposer` (flat `structures` / `workflows` imports, no `sys.path` hack).
- 5 voice tracks: Lead (Flute 73), Pad (Warm Pad 88), Bass (Fretless 35), Counter (String Ensemble 48), Drums (ch9).
- Per-section harmonic regions — each section its own short progression, midpoint chord → root, quality from degree (kills the bar-0 tonic bug).

## Form: 26 bars / 8 sections (source was 8 bars / 1 section → +18 bars)
| Section | Bars | Progression |
|---|---|---|
| Intro | 2 | i — VII |
| VerseA | 4 | i — IV — i — v |
| PreChorus | 2 | VII — IV |
| Chorus | 4 | i — III — VII — IV |
| VerseB | 4 | i — VII — IV — v |
| Bridge | 4 | v — ii — VII — IV |
| FinalChorus | 4 | i — III — VII — IV |
| Outro | 2 | i — i |

## Variation techniques applied (5 distinct)
1. **Transposition / register shift** — VerseB lead is the VerseA contour played an octave up (chorus+outro non-transposed for contrast).
2. **Inversion** — Bridge lead inverts the core contour around the root/5th axis (descending arch `3,2,1,2,0`).
3. **Retrograde** — PreChorus lead reverses the motif contour order (`3,1,2,1,0`).
4. **Augmentation** — Outro lead halves onset density (half-note durations) for a closing fade.
5. **Density rise** — Chorus + FinalChorus add a string-ensemble counterline and a fuller drum pattern (open-hat + crash); FinalChorus is the densest.

## Two-phase architecture
- **Phase 1** (`-phase1.mid`): raw generative draft — single voice, off-grid onsets (jittered), scale-tone-quantized pitches only (no chord context). 138 notes, 133 off-grid (proves rawness).
- **Phase 2** (`-perfect.mid`): musicom rules — per-bar chord-tone quantization, rhythm-grid snap to 120/240, voice-leading/range enforcement. All 352 pitched onsets are chord tones of their own bar (0 scale / 0 chord violations).

## Dual-version humanization
- `-perfect` = grid-locked compositional truth (off-grid == 0).
- `-humanized` = style profile (`pop`, 4 ms) + per-instrument DNA, seeded (`hz_seed` in `composition_meta.json`). Off-grid > 0 proves jitter ran.
- Per-voice stats (mean_abs_shift_ticks): Lead 2.79, Pad 4.24, Bass 7.88 (layback), Counter 2.38, Drums 1.16 (tight anchor).

## Verification (real numbers)
See `Analysis/verify.json` and `Analysis/render.json`.