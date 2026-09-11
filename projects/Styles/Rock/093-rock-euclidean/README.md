# 093-rock-euclidean

Rock · **Method 012 Euclidean Groove Locking (Bjorklund)** · layer `concrete` ·
E aeolian · 128 BPM · 24 bars.

Nightly autonomous composition (two-phase architecture) — 2026-09-11.

## What this is

A 45-second minor-key rock piece in which **every rhythmic layer is a
Euclidean pattern** produced by `generators.rhythm.euclidian()` (the engine's
implementation of method 012), locked to the metric grid:

| Voice | Euclidean cell | Locked to |
|---|---|---|
| Fiddle lead | 6 in 16, rotated per bar | 16th (120) |
| Acoustic guitar | 4 in 16 | 16th |
| Piano stabs | 3 in 8, rotated | 8th (240) |
| Organ pad | 1 in 4 | whole bar |
| Double bass | 8 in 8 | 8th |
| Kick / snare / hats | 4-in-16 / 2-in-8 (rot 2 = backbeat) / 8-in-16 | 16th / 8th |

Key: **E aeolian**. Progression (24 bars):
`i i ♭VI ♭VII | i ♭VI ♭III ♭VII | ♭VI ♭VII i i | iv ♭VI ♭III ♭VII |
♭VI ♭VII i i | i i ♭VI i`

## Listen for

1. **Intro → Verse:** the lead cell rotates; the pattern is the same but lands
   differently against the bar line.
2. **Chorus:** the progression starts on ♭VI, so the tonic arrives late — the
   pull you feel is the missing `i` in bar 1 of each chorus.
3. **Bridge:** `iv` (A minor) is the only subdominant in the piece; it is the
   harmonic "cold water".
4. **Outro:** plagal ♭VI → i close, no dominant. Modal rock, not functional
   classical.
5. **Backbeat:** the snare is `euclidian(2,8)` unrotated `[0,960]` — the
   downbeats — rotated two steps to `[480,1440]`. Two-step rotation is the
   entire difference between a wrong-feeling pattern and a rock backbeat.

## Files

| Path | What |
|---|---|
| `MIDI/093-rock-euclidean-phase1.mid` | Phase 1: raw generative draft, 1 voice, **off-grid by design** |
| `MIDI/093-rock-euclidean.mid` | Phase 2: rules-processed, 6 voices, grid-locked |
| `Audio/*.ogg` | Opus renders of both phases (Telegram-ready) |
| `Audio/*.wav` | FluidSynth masters (peak −1 dBFS) |
| `Analysis/summary.json` | all audit verdicts + numbers |
| `Analysis/grid_visualization.txt` | 24-bar onset density map per voice |
| `Analysis/tonal_check.json` | pitch/harmonic verification of the render |
| `REPORT.md` | **the full record** (method, audits, fixes, rationale) |
| `Scripts/run_all.sh` | rerun the entire pipeline |

## Verdicts

```
grid (phase 2)      PASS  0 off-grid / 972 notes (16th = 120)
harmony             PASS  0 out-of-scale, 0 out-of-chord
range               PASS  all voices inside registry ranges
zero-drift          PASS  both phases end at 46080 ticks
tonal (phase 1)     PASS  54/54 fundamentals + harmonic content
tonal (phase 2)     PASS  80.7 % 12TET windows, 97.9 % chroma in key
silence             PASS  19.3 % total, all of it the post-music tail
```

Engine-only build (no raw MIDI authoring); `preflight_check.py` exits 0.
