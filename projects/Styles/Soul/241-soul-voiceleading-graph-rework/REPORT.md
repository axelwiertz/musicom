# REPORT — 241-soul-voiceleading-graph-rework

**Project:** 241-soul-voiceleading-graph-rework
**Source:** Soul/084-soul-voiceleading-graph (rework agent, nightly)
**Decision:** **REDESIGN** — source failed 2 of 6 standards (std1: compose
script gone, no engine-evidence in repo; std6: no root provenance.json + no
index.html). Rebuilt from scratch through canonical `UnitMatrixComposer`,
preserving musical identity only. The source MIDI itself was clean
(zero-drift / grid / tracks / two-phase all PASS), so identity extraction was
straightforward.
**Date:** 2026-10-14 · **Seed:** 20261014

---

## 1. Audit of source (084-soul-voiceleading-graph)

| Standard | Result |
|---|---|
| 1. Engine (UnitMatrixComposer, not hand-rolled mido) | **FAIL** — `compose_084.py` no longer in repo (README references it but file gone); no engine-evidence remains |
| 2. Zero-drift (all voice tracks equal length) | PASS — 6 voice tracks × 46080 ticks |
| 3. Rhythm-grid sync (pitched onsets % 120/240) | PASS — 0 off-grid of 899 pitched onsets |
| 4. ≥ 4 voice tracks | PASS — 6 voice tracks |
| 5. Two-phase artifacts (`<id>.mid` + `-phase1.mid`) | PASS — both present |
| 6. `provenance.json` + `index.html` | **FAIL** — neither present (only per-file `.provenance.json` sidecars) |

Full audit: `Analysis/rework_audit.json` (in the SOURCE project).

## 2. Identity preserved (from source)

| Field | Value |
|---|---|
| Genre | Soul |
| Key | D minor (aeolian) = pcs {2,4,5,7,9,10,0} |
| Tempo / Meter | 92 BPM, 4/4, 480 TPB (bar = 1920, 8th = 240, 16th = 120) |
| Method | 011 Voice-Leading Graph Search — weighted random walk over a tonal-function graph |
| Band | Tenor Sax (66) lead · Rhodes (4) · Violin (41) · Acoustic Guitar (25) · Electric Bass (33) · Drums (ch9) |
| Harmonic vocab | D-aeolian triads: i Dm, III F, iv Gm, v Am, VI Bb, VII C |

## 3. Form — longer + more varied

**32 bars = 8 sections × 4 bars** (source was 24 bars = 6 sections).

| Section | Bars | Progression | Midpoint root | Lead variation |
|---|---|---|---|---|
| Intro | 0–3 | i VI iv VII | iv (Gm) | register shift −12 + thin |
| Verse | 4–7 | i III VII iv | VII (C) | identity (graph-walk motif) |
| Chorus | 8–11 | III VII VI VII | VI (Bb) | transposition +m3 (to relative major F) |
| Bridge | 12–15 | iv v III VI | III (F) | retrograde (contour reversed) |
| Verse2 | 16–19 | i iv VI VII | VI (Bb) | augmentation ×2 |
| Chorus2 | 20–23 | III VII VI VII | VI (Bb) | inversion + density rise |
| Break | 24–27 | v iv III VII | III (F) | diminution ×0.5 |
| Outro | 28–31 | iv v i i | i (Dm) | recapitulation → cadence |

Variation techniques (6 distinct): register-shift-down+thin, transposition
(+m3, diatonic degree shift), retrograde, augmentation, inversion (diatonic
mirror around tonic), diminution — plus identity + recapitulation. All
transforms are degree-based (diatonic), so raw material stays in the D-aeolian
scale even before Phase-2 quantization.

## 4. Two-phase architecture

- **Phase 1** (`-phase1.mid`): raw weighted graph walk (degree + octave) with
  fractional-tick rhythm — off-grid and out-of-chord by design, single voice
  (Tenor Sax). Own `UnitMatrixComposer` + own `validate()` gate (passed).
- **Phase 2** (`.mid`): rules post-process — 120-tick grid snap, per-bar
  chord-tone quantization (floor `t//BAR`), dedup of collided
  `(start_tick, pitch)`, leap-cap voice-leading (≤12 semitones), per-section
  harmonic regions (midpoint root), min-motion violin pad (voice-leading
  graph identity) + chorus/break arpeggio counterline (density rise),
  6-voice arrangement.

## 5. Verification (read-only mido, phase 2)

| Check | Result |
|---|---|
| File size > 40 B | PASS — 13278 B (phase1 1430 B) |
| Zero-drift | PASS — 6 voice tracks × 61440 ticks |
| Off-grid pitched onsets | **0** of 1318 |
| Scale violations (D aeolian) | **0** |
| Chord violations (per-bar t//BAR) | **0** |
| Audio (FluidR3_GM.sf2) | 89.12 s, peak 0.821, silence 6.02% (< 30%) |

Phase 1 intentionally raw: 142 off-grid, 74 chord-viol (pre-rules); scale 0.

## 6. Files

| Path | Size |
|---|---|
| `MIDI/241-soul-voiceleading-graph-rework.mid` | 13278 B (+ provenance.json) |
| `MIDI/241-soul-voiceleading-graph-rework-phase1.mid` | 1430 B (+ provenance.json) |
| `Audio/241-soul-voiceleading-graph-rework.wav` | 15721004 B |
| `Audio/241-soul-voiceleading-graph-rework.ogg` | 631835 B |
| `Audio/241-soul-voiceleading-graph-rework-phase1.wav` | 15117612 B |
| `Audio/241-soul-voiceleading-graph-rework-phase1.ogg` | 737452 B |
| `Analysis/grid_visualization.txt` | — |
| `Analysis/grid_visualization_phase1.txt` | — |
| `Analysis/summary.json` / `verification.json` / `render_stats.json` | — |
| `index.html` (VoltAgent dashboard) | — |

## 7. Provenance

Engine-only composition: `structures`, `workflows.unitmatrix_composer`,
`workflows.provenance`, `visualization.grid`. No raw `mido` authoring (mido
used read-only for the independent audit). Both phase MIDIs pass `validate()`
(zero-drift) and carry `classification=ai-assisted` provenance sidecars.
