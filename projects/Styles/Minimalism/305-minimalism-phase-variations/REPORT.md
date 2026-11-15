# 305-minimalism-phase-variations — REPORT

Minimalism × **E(5,12) Euclidean phase cell** (Steve Reich "Clapping Music"
method) — redesign of `001-minimalism-phase-study`.

| Field | Value |
|---|---|
| Project | 305-minimalism-phase-variations |
| Style | Minimalism |
| Method | E(5,12) Euclidean phase cell (5 pulses / 12 quarter steps) |
| Layer / Paradigm | concrete · Process · Grid-Locked |
| Key | C major (Ionian) = pc {0,2,4,5,7,9,11} (source C-pentatonic DNA re-expressed as chord-tone arpeggios) |
| Tempo | 120 BPM · 4/4 · 480 TPB · BAR=1920 |
| Form | intro-phase1-6-bridge-resolve-coda = 32 bars, 10 sections |
| Date | 2026-11-15 (nightly rework job) |

## 1. Source identity (preserved)

`001-minimalism-phase-study` — C pentatonic (C D E G A), 120 BPM, E(5,12)
Euclidean marimba cell, two marimba voices phase-walking +1 beat/section,
pad (string ensemble C4-E4-G4), bass pedal C2, perc E(5,16) kick. 8 sections
× 3 bars = 24 bars.

## 2. Audit result

| Standard | Result |
|---|---|
| 1 engine (UnitMatrixComposer) | PASS |
| 2 zero-drift | PASS (5 voice tracks len 46080) |
| 3 rhythm-grid sync | PASS (0 off-grid, 128 pitched onsets) |
| 4 track setup | PASS (5 voices) |
| 5 two-phase | **FAIL — phase1.mid missing** |
| 6 provenance.json + index.html | **FAIL — index.html missing** (+ no dual-version) |

2/6 fail → **redesign** (identity-preserving, non-compliant code discarded).
Audit recorded at `001-minimalism-phase-study/Analysis/rework_audit.json`.

## 3. What changed (redesign)

- Rebuilt through canonical `UnitMatrixComposer` + two-phase architecture.
- Form grew 24 → **32 bars**, 8 → **10 sections** (phase process extended
  through a Bridge + Resolve re-lock + Coda).
- Applied **7 variation techniques** (each key-safe in C major).

## 4. Variation techniques (where they apply)

| # | Technique | Section | How |
|---|---|---|---|
| T1 | Phase-walk (identity) | Phase1→Phase6 | MarimbaB rotates the E(5,12) cell +1 beat/section (0→6) |
| T2 | Retrograde | Phase5 | MarimbaB pitch sequence reversed |
| T3 | Inversion | Bridge | MarimbaB mirrored around axis C5 (=72), re-quantized to chord tones |
| T4 | Augmentation | Coda | MarimbaB durations ×2 → spacious fade |
| T5 | Register shift | Phase4 +12 / Intro·Resolve·Coda −12 | octave displacement |
| T6 | Density / diminution | Phase4 + Phase6 | MarimbaA cell step 8th-note (×2 hit density) |
| T7 | Relative-minor re-orientation | Bridge | harmonic center → vi (Am) region |

## 5. Per-section harmonic regions (own progression, no bar-0-tonic bug)

| Section | Bars | Degrees (chords) | Technique |
|---|---|---|---|
| Intro | 0-1 | C C | T5 register −12 (MarimbaA only) |
| Phase1 | 2-5 | C C C C | baseline unison (phase 0) |
| Phase2 | 6-9 | C F C Am | T1 phase +1 |
| Phase3 | 10-13 | C G C F | T1 phase +2 |
| Phase4 | 14-17 | C Dm G C | T1 +3 · T5 +12 · T6 density |
| Phase5 | 18-21 | Am G Dm Am | T1 +4 · T2 retrograde |
| Bridge | 22-25 | Am Dm Am C | T1 +5 · T3 inversion · T7 vi region |
| Phase6 | 26-27 | G Am | T1 +6 · T6 8th cell |
| Resolve | 28-29 | C C | phase re-lock · T5 −12 |
| Coda | 30-31 | C C | T4 augmentation fade |

Chord roots derive from each bar's own degree; section midpoint chord used for
section root (no single bar-0 tonic collapse).

## 6. Two-phase architecture

- **Phase 1** (`-phase1.mid`, 565 B): raw E(5,12) phase cell, single marimba
  voice, unquantized float pitch (seeded random walk) + off-grid onsets, 51
  notes, own composer + validate() gate.
- **Phase 2** (`-perfect.mid` + `-humanized.mid`): per-bar chord-tone
  quantization (floor bar attribution), 8th-grid snap + dedup, voice-leading
  optimization (0 corrections needed), register enforcement, 5-voice texture
  + variation techniques.

## 7. Dual-version + humanization (always-on, seeded)

`export_dual` → `-perfect.mid` (grid-locked) + `-humanized.mid` (style
minimalism + per-instrument DNA). `hz_seed=84978`. Per-voice mean abs shift
~4.8 ticks; recorded in provenance + `compose_summary.json`.

## 8. Verification (real numbers, read-only mido)

| Metric | phase1 | perfect | humanized |
|---|---|---|---|
| voice tracks | 1 | 5 | 5 |
| track length (ticks) | 61440 | 61440 | 61440 |
| zero-drift | ✓ | ✓ | ✓ |
| pitched onsets | 51 | 287 | 287 |
| drums (ch9) | 0 | 59 | 59 |
| off-grid (16th) | 50 (raw) | **0** | **248** (jitter) |
| off-grid (8th) | 50 | **0** | 248 |
| scale violations | 17 (raw) | **0** | **0** |
| chord violations (blanket) | 40 (raw) | **0** | 18 (bar-boundary jitter) |
| strong-beat violations | 0 | 0 | **0** |

All hard gates pass. The 18 "blanket" chord hits in the humanized layer are
bar-boundary jitter (onsets shifted ≤3 ticks across a bar seam); strong-beat
discipline is 0 and pitch never leaves the key.

## 9. Audio (mastered to style target −18 LUFS, −1 dBTP ceiling)

| Version | LUFS | true-peak | silence | OGG |
|---|---|---|---|---|
| phase1 | −19.21 | −2.47 | 0.310 (raw sparse) | 489 KB |
| perfect | −18.00 | −4.05 | 0.064 | 480 KB |
| humanized | −18.00 | −3.68 | 0.065 | 478 KB |

Perfect + humanized silence < 7% (healthy). Phase-1 silence 31% is expected
(raw single-voice sketch, no pad/bass). True-peaks sit below the −1 ceiling
(ceiling, not target).

## 10. Artifacts

| File | Role |
|---|---|
| MIDI/305-minimalism-phase-variations-phase1.mid | raw generative draft |
| MIDI/305-minimalism-phase-variations-perfect.mid | grid-locked phase 2 |
| MIDI/305-minimalism-phase-variations-humanized.mid | humanized phase 2 |
| Audio/*-perfect.ogg / *-humanized.ogg / *-phase1.ogg | mastered Opus renders |
| Analysis/grid_visualization.txt (+phase1) | rhythm DNA grids |
| Analysis/compose_summary.json / verification.json / render_report.json | metrics |
| provenance sidecars | per MIDI artifact |
| index.html | dashboard (VoltAgent styling) |
