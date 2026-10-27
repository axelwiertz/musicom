# REPORT — 270-een-klein-meisje-suite

**Project:** 270-een-klein-meisje-suite
**Source:** Folk/239-een-klein-meisje-rework (rework agent, nightly)
**Decision:** **EXTEND** (identity-preserving) + dual-version/humanization upgrade.
**Date:** 2026-10-27 · **hz_seed:** 78280 · **raw_seed:** (md5 "raw-270")

---

## 1. Audit of source (239-een-klein-meisje-rework)

| Standard | Result |
|---|---|
| 1. Engine (UnitMatrixComposer) | **PASS** — compose.py imports `workflows.unitmatrix_composer.UnitMatrixComposer` |
| 2. Zero-drift (all voice tracks equal length) | **PASS** — 5 voice tracks × 46080 ticks |
| 3. Rhythm-grid sync (pitched onsets % 120/240) | **PASS** — 0 of 732 pitched onsets off-grid |
| 4. ≥ 4 voice tracks | **PASS** — 5 voices (Lead/Counter/Harmony/Bass/Drums) |
| 5. Two-phase artifacts (`<id>.mid` + `-phase1.mid`) | **PASS** — both present |
| 6. provenance.json + index.html | **PASS** — per-artifact provenance sidecars + index.html |

**Verdict:** all 6 core standards PASS → no redesign. One current-engine gap:
the source predates the 2026-10-17 dual-version (perfect/humanized) +
humanization mandate — it ships a single grid-locked phase-2 MIDI, no
`-perfect`/`-humanized` pair and no humanization. This rebuild closes that
gap and EXTENDS the form.

Full audit: `Analysis/rework_audit.json` (this project + source project).

## 2. Identity preserved (from source)

| Field | Value |
|---|---|
| Genre | Dutch Folk / Child Folk (Kleuterlied nursery) |
| Key | G Major = pcs {7,9,11,0,2,4,6} |
| Tempo / Meter | 105 BPM, 4/4, 480 TPB (bar 1920, 8th 240, 16th 120) |
| Method | Markov interval walk over scale degrees (transition table from source melody) |
| Band | Lead (Choir Aahs 53) · Counter (Violin 41) · Harmony (Steel Guitar 25) · Bass (33) · Drums (ch9) |
| Core motif | I-arpeggio 1-3-5-5-3-1 + neighbor 2-3; IV/dominant cadence 4-2-1-5-3-1 |

## 3. Form — longer + more varied

**32 bars = 8 sections × 4 bars** (source = 24 bars / 6 sections).

| Section | Bars | Progression | Midpoint root | Lead variation |
|---|---|---|---|---|
| Intro | 0–3 | I IV V I | V (D) | register shift −12 + thin |
| A | 4–7 | I vi ii V | ii (Am) | identity (I-arpeggio motif) |
| Ap | 8–11 | vi IV iii V | iii (Bm) | retrograde (contour reversed) |
| B | 12–15 | IV V vi I | vi (Em) | transposition +P5 (bright lift) |
| C | 16–19 | V ii V vi | V (D) | augmentation ×2 + violin counterline |
| D | 20–23 | vi IV V I | V (D) | inversion (mirror around G4) |
| E | 24–27 | I V vi IV | vi (Em) | diminution ×0.5 (fast run) |
| Outro | 28–31 | IV V I I | I (G) | inversion + diminution → cadence |

Variation techniques (7, requirement ≥3): register-shift-down, retrograde,
transposition (+P5), augmentation + counterline, inversion, diminution,
inversion+diminution.

## 4. Two-phase architecture

- **Phase 1** (`-phase1.mid`): raw Markov-interval walk, unquantized float
  pitch + jittered eighth-note rhythm, single voice (Lead), pre-rules.
  Own `UnitMatrixComposer` + own `validate()` gate (passed).
- **Phase 2** (`-perfect.mid`): rules post-process — per-bar chord-tone
  quantization (floor `s//BAR` attribution), 120-tick grid snap, dedup of
  collided `(start_tick, pitch)`, voice-leading correction, per-section
  harmonic regions (midpoint root), 5-voice arrangement.

## 5. Dual-version + humanization (2026-10-17 mandate)

Exported via `workflows.humanize.export_dual` — grid-locked `-perfect` first,
then humanize in place, re-validate, export `-humanized`. Style `folk`
(timing σ 9 ms, vel σ 6.5, phrase_corr 0.50) + per-instrument DNA.

| Voice | mean abs shift (ticks) | max shift | mean vel Δ |
|---|---|---|---|
| Lead | 4.50 | 14 | 7.67 |
| Counter | 5.79 | 18 | 4.62 |
| Harmony | 5.83 | 21 | 4.79 |
| Bass | 6.50 | 15 | 3.45 |
| Drums | 1.20 | 5 | 3.32 |

Drums tightest (anchors grid), bass lays back, lead loosest — as expected.

## 6. Verification (read-only mido)

| Check | phase1 (raw) | perfect | humanized |
|---|---|---|---|
| File size > 40 B | 1737 B ✓ | 11413 B ✓ | 11136 B ✓ |
| Zero-drift | 1 track × 61440 ✓ | 5 tracks × 61440 ✓ | 5 tracks × 61440 ✓ |
| Off-grid pitched onsets | 172/188 | **0**/1068 ✓ | 1007/1068 (>0, jitter ran) |
| Scale violations (G Major) | 24 | **0** ✓ | **0** ✓ |
| Chord violations (per-bar t//BAR) | 103 | **0** ✓ | 12 (bar-boundary jitter, in-key) |

Humanized chord violations (12) are onset-jitter crossings of a bar seam —
identical to the canonical 268 rework (11). Scale stays 0; perfect layer is
fully 0/0/0.

## 7. Audio

Render + master to `target_for_style("folk")` = −16 LUFS (−1 dBTP ceiling),
then Opus OGG. See `Analysis/render_report.json` for LUFS/true-peak/silence.

## 8. Regenerate

```bash
cd /opt/data/projects/Styles/Folk/270-een-klein-meisje-suite
$MUSICOM_PYTHON compose.py     # MIDI (phase1 + perfect + humanized)
$MUSICOM_PYTHON render.py      # WAV + OGG (mastered)
$MUSICOM_PYTHON verify.py      # read-only audit
```
