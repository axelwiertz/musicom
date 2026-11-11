# 297-flamenco-falseta-suite — Rework Report

## Source
- **Project**: `Flamenco/random-flamenco-001` (mtime 2026-09-14)
- **Primary MIDI**: `MIDI/flamenco-001.mid` (5 tracks, 28 bars)
- **Identity**: Flamenco · A major · 130 BPM · ascending triad arpeggio motif
  (1→3→5, A→C#→E) · progression A–E–F#m–D–A · Flute lead / acoustic steel
  guitar / double bass / ch9 palmas percussion

## Audit result
2 of 6 standards FAILED → **redesign required** (rebuild from scratch, keep identity).

| # | Standard | Result | Evidence |
|---|---|---|---|
| 1 | engine (UnitMatrixComposer) | PASS | provenance: `musicom_workflow.compose(style=flamenco, method=001)` |
| 2 | zero-drift | PASS | 4 voice tracks all 53760 ticks (28 bars) |
| 3 | rhythm-grid sync | PASS | 0 off-grid pitched onsets |
| 4 | track setup >= 4 | PASS | Flute / Guitar / Bass / Drums ch9 |
| 5 | two-phase artifacts | **FAIL** | no `-phase1.mid` |
| 6 | provenance + index | **FAIL** | only per-artifact `.mid.provenance.json`; no project `provenance.json`, no `index.html` |

## What changed (redesign)
- Rebuilt through canonical `UnitMatrixComposer` (5 voices × 7 sections).
- Saved a real `compose.py` (source had none on disk).
- Zero-drift enforced by terminal landmark (pitch-0) + `validate()` gate on both phases.
- Added Phase-1 raw draft, dual-version export, project provenance, dashboard.
- Flute program normalized 74 (Recorder) → 73 (Flute); guitar kept at 25 (steel).

## Form (longer + more varied)
32 bars, 7 sections (source was 28 bars / 5 sections):

| Section | Bars | Chords | Lead technique |
|---|---|---|---|
| Intro | 0-3 | I - I - I - V | statement (ascending 1→3→5 arpeggio) |
| Falseta I | 4-7 | I - vi - IV - V | run (quarter-note arpeggio, falseta flourish) |
| Letra I | 8-11 | V - V - V - I | transposition (motif over V region) |
| Falseta II | 12-15 | vi - vi - IV - V | inversion (descending 5→3→1 mirror) |
| Letra II | 16-19 | IV - IV - ii - V | register shift (motif +1 octave) |
| Falseta III | 20-25 | I - V - vi - IV - V - I | diminution (8th-note ostinato, density peak) |
| Cierre | 26-31 | IV - V - I - I - V - I | retrograde (reversed close) |

Per-section harmonic regions (midpoint-chord roots): Intro A(I), Falseta I D(IV),
Letra I E(V), Falseta II F#(vi), Letra II D(IV), Falseta III F#(vi), Cierre A(I) —
varied, not all tonic.

## Variation techniques (7)
1. **Transposition** — Letra I restates the arpeggio over the V (E) region.
2. **Inversion** — Falseta II mirrors the ascending motif into a descending 5→3→1.
3. **Register shift** — Letra II replays the motif one octave higher (D region).
4. **Diminution** — Falseta III doubles the arpeggio rate to 8th notes (density peak).
5. **Retrograde** — Cierre reverses the Intro's A→C#→E into a descending close.
6. **Counterline** — Violin sustains chord-tone harmony (call-response) in
   Letra I and Falseta III.
7. **Falseta run** — Falseta I adds a quarter-note arpeggio flourish (density rise).

## Two-phase architecture
- **Phase 1** (`-phase1.mid`): seeded random walk (seed 20261111), single voice,
  unquantized onsets + chromatic pitch by construction (raw draft).
- **Phase 2** (`-perfect.mid` + `-humanized.mid`): per-bar chord-tone quantization
  (floor `t//BAR`), rhythm-grid snap (120 ticks), `(start,pitch)` dedup, register
  clamp, `validate()` → `export_dual`.

## Humanization (dual-version)
- Style `flamenco` (no explicit STYLE_HUMANIZE key → default profile).
- Seed `3312682339` (md5 of id-style-key-bpm).
- Per-voice DNA: drums anchor (2 ms), bass lays back (+8 ms), melodic voices use style timing.
- Measured per-voice mean/max abs shift (ticks) + velocity delta:
  Lead Flute 5.21/17, Guitar 6.62/22, Bass 9.08/27, Counterline 7.0/20, Drums 1.33/5.

## Verification (read-only mido)
- `phase1`: 1 track len 61440, zero-drift OK (raw: 162 off-grid, 73 scale, 119 chord — expected).
- `perfect`: 5 tracks len 61440, zero-drift OK, **off-grid 0, scale 0, chord 0**.
- `humanized`: 5 tracks len 61440, zero-drift OK, **off-grid 446 (>0, jitter ran),
  scale 0**, chord 14 (bar-seam micro-timing crossings; notes still in-key).
