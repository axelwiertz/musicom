# 280-ambient-pareto-variations — REPORT

Ambient × Method **098 Multi-Objective Evolutionary Pareto Composition (MOEPC)** — rework of `234-ambient-pareto-build`.

| Field | Value |
|---|---|
| Project | 280-ambient-pareto-variations |
| Style | Ambient |
| Method | 098 — MOEPC (NSGA-II, pop 64 × gen 70) |
| Layer / Paradigm | concrete · Stochastic · Grid-Locked |
| Key | D Aeolian (D E F G A B♭ C) = pc {2,4,5,7,9,10,0} |
| Tempo | 70 BPM · 4/4 · 480 TPB · BAR=1920 |
| Form | intro-build-rise-peak-bridge-resolve-coda = 44 bars, 7 sections |
| Date | 2026-11-02 (nightly rework job) |

## 1. Source identity (preserved)

`234-ambient-pareto-build` — D Aeolian, 70 BPM, method 098 MOEPC/NSGA-II,
cinematic-build form, 5 voices (Lead=Celesta 8, Pad=Organ 19, Bass=Cello 42,
Sparkle=Harp 46, Drums ch9), smooth/balanced/active Pareto-front archetypes.

## 2. Audit result

| Standard | Result |
|---|---|
| 1 engine (UnitMatrixComposer) | PASS |
| 2 zero-drift | PASS (5 voice tracks len 61440) |
| 3 rhythm-grid sync | PASS (0 off-16th, 457 pitched onsets) |
| 4 track setup | PASS (5 voices) |
| 5 two-phase | PASS (.mid + -phase1.mid) |
| 6 provenance + index.html | **FAIL — index.html missing (docs only)** |

5/6 pass, only the docs-only `index.html` gap fails → **extension**
(identity-preserving), not redesign. Audit recorded at
`234-ambient-pareto-build/Analysis/rework_audit.json`.

## 3. What changed (extension)

- Form grew 32 → **44 bars**, 5 → **7 sections** (added Bridge + Coda).
- Re-ran method 098 (fresh seed 20261102) → Pareto front rank-0 size 43,
  132-note genome (3 notes/bar × 44 bars).
- Applied **7 variation techniques** (each key-safe in D Aeolian).

## 4. Variation techniques (where they apply)

| # | Technique | Section | How |
|---|---|---|---|
| T1 | Retrograde | Bridge | Lead replays Build's balanced contour in reverse |
| T2 | Inversion | Bridge | Harp swaps arpeggio for a melodic counter-line: active motif mirrored around D4, then re-quantized to chord tones |
| T3 | Augmentation | Coda | Lead + Pad durations ×2 → spacious fade |
| T4 | Diminution | Rise | Lead durations ×0.5 → lighter forward drive |
| T5 | Register shift | Peak +12 / Intro·Resolve·Coda −12 | octave displacement of the lead |
| T6 | Relative-major re-orientation | Bridge | harmonic center shifts to the VI (B♭) region |
| T7 | Density rise | Rise | Harp 16th-note arpeggios + drums every bar |

## 5. Per-section harmonic regions (own progression, no bar-0-tonic bug)

| Section | Bars | Degrees (chords) | Technique |
|---|---|---|---|
| Intro | 0-3 | i i VI VI | T5 register −12 |
| Build | 4-11 | i VI VII VI iv i VI VII | baseline (balanced) |
| Rise | 12-19 | iv v VI VII iv v i VII | T4 diminution + T7 density |
| Peak | 20-27 | i VI iv v VI VII i i | T5 register +12 |
| Bridge | 28-35 | VI VI i iv VI VII i iv | T1 retrograde + T2 inversion + T6 relative-major |
| Resolve | 36-39 | i i VI i | T5 register −12 |
| Coda | 40-43 | i i i i | T3 augmentation |

Each section carries its own short progression; chord roots derive from each
bar's own degree (not a single bar-0 tonic).

## 6. Two-phase architecture

- **Phase 1** (`-phase1.mid`, 1155 B): balanced Pareto-front melody, single
  celesta voice, unquantized float pitch + off-grid onsets, 132 notes, own
  composer + validate() gate.
- **Phase 2** (`-perfect.mid` + `-humanized.mid`): per-bar chord-tone
  quantization (floor bar attribution), 8th-grid snap + dedup, voice-leading
  optimization/correction (0 corrections needed), register enforcement,
  5-voice ambient texture + variation techniques.

## 7. Dual-version + humanization (always-on, seeded)

`export_dual` → `-perfect.mid` (grid-locked) + `-humanized.mid` (style ambient
+ per-instrument DNA). `hz_seed=51229`. Per-voice mean abs shift 2.0-2.6 ticks,
max 7-10 ticks; drums tightest (2.02), Sparkle loosest (2.62). Recorded in
provenance + `compose_summary.json`.

## 8. Verification (real numbers, read-only mido)

| Metric | phase1 | perfect | humanized |
|---|---|---|---|
| voice tracks | 1 | 5 | 5 |
| track length (ticks) | 84480 | 84480 | 84480 |
| zero-drift | ✓ | ✓ | ✓ |
| pitched onsets | 132 | 684 | 684 |
| off-grid (16th) | 132 (raw) | **0** | **581** (jitter) |
| off-grid (8th) | 132 | 48 (16th harp) | 585 |
| scale violations | 41 (raw) | **0** | **0** |
| chord violations (blanket) | 93 (raw) | **0** | 46 (bar-boundary jitter) |
| strong-beat violations | 0 | 0 | **0** |

All hard gates pass. The 46 "blanket" chord hits in the humanized layer are
bar-boundary jitter (onsets shifted ≤3 ticks across a bar seam); strong-beat
discipline is 0 and pitch never leaves the key.

## 9. Artifacts

| File | Role |
|---|---|
| MIDI/280-ambient-pareto-variations-phase1.mid | raw generative draft |
| MIDI/280-ambient-pareto-variations-perfect.mid | grid-locked phase 2 |
| MIDI/280-ambient-pareto-variations-humanized.mid | humanized phase 2 |
| Audio/*-perfect.ogg / *-humanized.ogg / *-phase1.ogg | mastered Opus renders |
| Analysis/grid_visualization.txt (+phase1) | rhythm DNA grids |
| Analysis/compose_summary.json / verification.json / render_report.json | metrics |
| provenance sidecars | per MIDI artifact |
