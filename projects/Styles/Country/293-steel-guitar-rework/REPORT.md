# 293-steel-guitar-rework — Rework Report

## Source
- **Project**: `Country/038-steel-guitar-demo` (mtime 2026-06-26)
- **Primary MIDI**: `MIDI/country_ensemble_16bar.mid` (2 tracks, hand-rolled mido)
- **Identity**: Country · G major · 90 BPM · I-IV-V (G-C-D) · steel-slide 1→3→5 motif
  (G→B→D ascending with one descending reset) · steel guitar / acoustic guitar /
  acoustic bass / drums

## Audit result
ALL 6 standards FAILED → **redesign required** (rebuild from scratch, keep identity).

| # | Standard | Result | Evidence |
|---|---|---|---|
| 1 | engine (UnitMatrixComposer) | FAIL | raw mido.MidiTrack/note_on in `src/16bar_ensemble.py` |
| 2 | zero-drift | FAIL | Bass 30480 ticks vs Guitar 34330 ticks |
| 3 | rhythm-grid sync | FAIL | 448/576 pitched onsets off 120/240 grid |
| 4 | track setup >= 4 | FAIL | only 2 voice tracks |
| 5 | two-phase artifacts | FAIL | no phase1.mid |
| 6 | provenance + index | FAIL | both missing |

## What changed (redesign)
- Hand-rolled mido replaced by canonical `UnitMatrixComposer` (5 voices × 6 sections).
- Zero-drift enforced by terminal landmark (pitch-0) in every cell + `validate()` gate.
- Rhythm grid: every pitched onset snapped to 120-tick grid (off-grid 0).
- New voices: Steel Guitar (lead, GM 25), Fiddle (counterline, GM 40),
  Rhythm Guitar (GM 24), Bass (GM 32), Drums (ch9).
- Full provenance + grid visualization + dashboard.

## Form (longer + more varied)
20 bars, 6 sections (source was 16 bars / 2 tracks):

| Section | Bars | Chords | Lead technique |
|---|---|---|---|
| Intro | 0-1 | I - IV | statement (ascending 1→3→5 slide) |
| Verse | 2-5 | I - IV - I - V | generative walk (quantized) |
| Chorus | 6-9 | I - IV - V - I | transposition (motif over I-IV-V-I) |
| Bridge | 10-13 | IV - I - ii - V | inversion (descending 5→3→1) |
| Verse2 | 14-17 | I - IV - I - V | register shift (verse +1 octave) |
| Outro | 18-19 | V - I | retrograde (D→B→G close) |

Per-section harmonic regions (midpoint-chord roots): Intro C(IV), Verse G(I),
Chorus D(V), Bridge A(ii), Verse2 G(I), Outro D(V) — varied, not all tonic.

## Variation techniques (6)
1. **Transposition** — Chorus restates the motif over the I-IV-V-I region
   (diatonic re-harmonization/transposition of the 1→3→5 shape).
2. **Inversion** — Bridge mirrors the ascending motif into a descending 5→3→1 contour.
3. **Retrograde** — Outro reverses the Intro's G→B→D statement into D→B→G.
4. **Register shift** — Verse2 replays the Verse walk one octave higher.
5. **Density rise** — Chorus/Verse2 add off-beat kick + crash + fuller strum.
6. **Counterline** — Fiddle sustains 3rd/5th harmony (call-response) in
   Verse/Chorus/Bridge/Verse2.

## Two-phase architecture
- **Phase 1** (`-phase1.mid`): seeded random walk (seed 293), single voice,
  unquantized onsets + out-of-key pitches by construction (raw draft).
- **Phase 2** (`-perfect.mid` + `-humanized.mid`): chord-tone quantization
  (per bar, floor `t//BAR`), rhythm-grid snap (120 ticks), `(start,pitch)`
  dedup keeping longest, register clamp (50-79), voice-leading leap clamp
  (≤ 9 semitones). `voice_leading_corrections = 0` (walk was already smooth).

## Humanization (dual-version)
- Style `country` (timing σ 9 ms, vel σ 6.5, phrase_corr 0.5, layback 2 ms).
- Seed `3258718210` (md5 of id-style-key-bpm).
- Per-voice DNA: drums anchor (2 ms), bass lays back (8 ms), melodic voices
  use style timing.
- Measured per-voice mean/max abs shift (ticks) + velocity delta:
  Steel 3.61/17, Fiddle 4.78/13, Rhythm 5.49/14, Bass 6.40/12, Drums 0.98/4.

## Verification (read-only mido)
- `phase1`: 1 track, len 38400, zero-drift OK (raw: 111 off-grid, 51 scale, 79 chord — expected).
- `perfect`: 5 tracks len 38400, zero-drift OK, **off-grid 0, scale 0, chord 0**.
- `humanized`: 5 tracks len 38400, zero-drift OK, **off-grid 255 (>0, jitter ran),
  scale 0**, chord 9 (bar-seam micro-timing crossings; notes still in-key).
