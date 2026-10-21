# REPORT — 254-celtic-reel-variations

**Project:** 254-celtic-reel-variations
**Source:** Celtic/085-celtic-subset-walk (rework agent, nightly)
**Decision:** **EXTENSION** (identity-preserving) — source passed all 5 musical/engine
standards; only `index.html` was missing (doc gap, regenerated here). Clean material kept
as DNA seed, not discarded.
**Date:** 2026-10-21 · **Seed:** 20261021 · **Walk seed:** 7
**Key:** Ab major (Ab Bb C Db Eb F G) · **BPM:** 96 · **4/4** · 480 TPB (bar=1920, 8th=240, 16th=120)

---

## 1. Source identity (preserved)

| Field | Value |
|---|---|
| Genre | Celtic |
| Key / BPM / meter | Ab major · 96 · 4/4 |
| Method | ABS-002 Subset Walker (`rules.subset_network.PatternNetwork.walk`) + ABS-001 tension curve + method-006 cadence close |
| Chord anchors | Ab I, Bb-ii, C-iii, Db-IV, Eb-V, F-vi, Abmaj7, Eb7, Bbm7 |
| Voices | Marimba(12), French Horn(60), Cello(42), Violin(40), Bassoon(70), Double Bass(43), Drums(ch9) |
| Identity motif | violin answer line Db5 C5 Bb4 F5 Db5 C5 Bb4 G4 (chord-quantized) |
| Original form | 6 sections × 4 bars = 24 bars |

## 2. Audit result (against current standards)

| # | Standard | Result |
|---|---|---|
| 1 | Engine (`UnitMatrixComposer`, no raw mido authoring) | **PASS** |
| 2 | Zero-drift (all voice tracks equal length) | **PASS** (7 × 46080) |
| 3 | Rhythm-grid sync (pitched onsets % 120/240) | **PASS** (0 off-grid) |
| 4 | Track setup (≥ 4 voice tracks) | **PASS** (7) |
| 5 | Two-phase artifacts (`.mid` + `-phase1.mid`) | **PASS** |
| 6 | provenance.json + index.html | **FAIL** — `index.html` missing (provenance present) |

Only standard 6 failed, and only on the documentation side. Rebuilding from scratch would
discard a fully-compliant 24-bar piece, so the correct action per repo precedent is an
identity-preserving extension. Full audit: `085-celtic-subset-walk/Analysis/rework_audit.json`.

## 3. What changed (extension)

- **Form lengthened** 6 → **8 sections** (24 → **32 bars**): Intro | ReelA | ReelB | Lift |
  ReelA2 | Bridge | Climax | Outro. The subset-walk is re-run for 32 bars with a fresh
  walk seed (7) and a longer tension curve (intro sway → reel rise → lean → lift peak →
  dance return → bridge re-tension → climax peak → cadence down).
- **Per-section harmonic regions**: each section gets its own 4-bar subset-walk region;
  section roots are taken from the **midpoint chord** (2nd bar) and land on five distinct
  degrees (IV, ii, ii, V7, I, ii, IV, iii) — no bar-0 "always tonic" collapse.

## 4. Variation techniques (6 distinct, mapped to sections)

| Section | Technique |
|---|---|
| Intro | sparse (drums tacet, low lead density) |
| ReelA | baseline full texture (8th lead) |
| ReelB | counterline prominence (violin full 8th line) |
| Lift | **diminution** (16th subdivision, dense) |
| ReelA2 | **transposition** (diatonic sequence +2 scale degrees) |
| Bridge | **inversion + retrograde** (palindromic contour) |
| Climax | **register shift (+12) + octave doubling** + density rise |
| Outro | **augmentation** (sustain ×2) fade to tonic |

## 5. Two-phase architecture

- **Phase 1** (`-phase1.mid`): raw subset-walk draft — single marimba voice, off-grid
  fractional rhythm, pitch stream sampled from each bar's walked-subset pitch-class field.
  No harmony/bass/drums. Own `validate()` gate.
- **Phase 2** (dual-version): musicom rules — per-bar chord-tone quantization (root-position
  Ab realization), 8th/16th grid snap, dedup collided `(start_tick,pitch)`, voice-leading
  cap, register enforcement, full 7-voice texture. Exported **perfect** (grid-locked) then
  **humanized** via `workflows.humanize.export_dual`.

## 6. Humanization (always-on, style-derived, seeded)

- style `folk` (celtic → folk-family), seed `20515021`, per-voice instrument DNA from the
  registry. Drums anchor tightest (~1.0 tick ≈ 1.3 ms), bass lays back (~7.0 ticks),
  marimba percussive-tight (~1.4). Full per-voice stats in `Analysis/summary.json`.

## 7. Verification (readback audit, real numbers)

| Metric | perfect | humanized |
|---|---|---|
| Voice tracks (zero-drift) | 7 × 61440 | 7 × 61440 |
| Off-grid onsets (16th) | **0** | 1052 (jitter ran) |
| Out-of-key (scale) | **0** | 0 |
| Out-of-chord (per-bar t//BAR) | **0** | 21* |
| Pitched onsets | 1310 | 1310 |

\* the 21 humanized out-of-chord notes are onset micro-jitter crossing a bar line (pitch
unchanged by the humanizer); compositional chord discipline on the perfect layer is 0.
Audio is mastered to **−16.0 LUFS** (`target_for_style("folk")`, −1 dBTP ceiling); see
`Analysis/render_stats.json` for LUFS / true-peak / silence per render.

## 8. Files

```
254-celtic-reel-variations/
├── index.html               # VoltAgent dashboard
├── README.md / REPORT.md
├── MIDI/  -phase1.mid · -perfect.mid · -humanized.mid  (+ provenance sidecars)
├── Audio/ -phase1 / -perfect / -humanized .wav + .ogg
├── Analysis/ summary.json · grid_visualization.txt · render_stats.json
└── Scripts/ compose.py · render_audio.py
```
