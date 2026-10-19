# 252-balkan-spectral-extended

**Balkan × Method 051 (SGLM) — rework of 228** · 32 bars · 4 voices

G Dorian · 7/8 (dajčovo 2+2+3) · 132 BPM · double bass / accordion / clarinet / violin

Rework of `228-balkan-spectral`: same identity (key, tempo, method, instruments),
**longer form (32 vs 24 bars)** and **6 variation techniques** (register shift,
counterline prominence, diminution, retrograde, augmentation, octave doubling).

## Listen for (A/B the humanization)

- **`-perfect.ogg`** — grid-locked (0 off-grid), the compositional truth.
- **`-humanized.ogg`** — style + per-instrument micro-timing (641 off-grid), the
  human feel. Bass lays back; clarinet/violin breathe.
- **Dajčovo groove** — bass roots on group starts (2+2+3), accordion stabs on
  offbeats; asymmetric 7/8 is the Balkan DNA.
- **Dorian brightness** — raised 6th makes IV (C major) shine against the i (Gm).
- **Spectral tension arc** — VerseB/Bridge drop to λ₁≈1.51 (TENSE), Climax returns
  to λ₁≈2.92 (HOME) with sustained octave-doubled notes.

## Variation map

| Section | Technique |
|---|---|
| Intro | sparse (violin tacet) |
| VerseA | baseline full texture |
| LiftA | register shift UP (+12) |
| VerseB | counterline prominence (violin eig2 lead) |
| Dance | diminution (16th notes) |
| Bridge | retrograde contour + register DOWN (−12) |
| Climax | augmentation (sustain ×2) + octave doubling |
| Coda | diminution fade to tonic |

## Voices

| Voice | Instrument | Program |
|---|---|---|
| Bass | Double Bass | 43 |
| Accordion | Accordion | 21 |
| Clarinet | Clarinet | 71 |
| Violin | Violin | 40 |

## Audits (mido read-back, real numbers)

| Gate | Perfect | Humanized |
|---|---|---|
| tracks (equal len) | 4 × 53760 | 4 × 53760 |
| off-grid (not %120) | 0 | 641 |
| out-of-key | 0 | 0 |
| out-of-chord | 0 | 17* |

\* 17 humanized out-of-chord = onset micro-jitter crossing a bar line (pitch unchanged).

## Files

- `MIDI/252-balkan-spectral-extended-phase1.mid` (+ provenance)
- `MIDI/252-balkan-spectral-extended-perfect.mid` (+ provenance)
- `MIDI/252-balkan-spectral-extended-humanized.mid` (+ provenance)
- `Audio/*-perfect.ogg`, `Audio/*-humanized.ogg`, `Audio/*-phase1.ogg`
- `Analysis/rework_audit.json`, `grid_visualization.txt`, `summary.json`, `render_stats.json`
- `index.html`, `REPORT.md`

See `REPORT.md` for full audit, progression, and fixes.