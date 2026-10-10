# REPORT — 233-blues-aco-rework

**Project:** 233-blues-aco-rework
**Source:** Blues/214-blues-antcolony (rework agent, nightly)
**Decision:** **REDESIGN** — source failed audit standard 6 (no top-level
`provenance.json`, no `index.html`). Rebuilt from scratch through the canonical
`UnitMatrixComposer` workflow, preserving musical identity only.
**Date:** 2026-10-10 · **Seed:** 20261010

---

## 1. Audit of source (214-blues-antcolony)

| Standard | Result |
|---|---|
| 1. Engine (UnitMatrixComposer, not hand-rolled mido) | PASS |
| 2. Zero-drift (all voice tracks equal length) | PASS — 5 tracks × 46080 |
| 3. Rhythm-grid sync (pitched onsets % 120/240) | PASS — 516 onsets, 0 off-grid |
| 4. ≥ 4 voice tracks | PASS — 5 tracks |
| 5. Two-phase artifacts (`<id>.mid` + `-phase1.mid`) | PASS |
| 6. `provenance.json` + `index.html` | **FAIL — both missing** |

Full audit: `Analysis/rework_audit.json` (in the SOURCE project).

## 2. Identity preserved (from source)

| Field | Value |
|---|---|
| Genre | Blues |
| Key | E blues scale = {E G A B♭ B D} = pcs {4,7,9,10,11,2} |
| Tempo / Meter | 100 BPM, 4/4, 480 TPB (bar = 1920, 8th = 240) |
| Method | 041 ACOPF (Ant Colony Optimization Path Finding), stochastic, concrete |
| Band | Piano (comp) · Double Bass (walking) · Harmonica (ACO lead) · Trumpet (call-response) · Drums (ch9 shuffle backbeat) |
| Core motif | ACO best-tour contour (smooth chromatic wander) |

## 3. Form — longer + more varied

**32 bars = 8 sections × 4 bars** (source was 24 = 6).

| Section | Bars | Progression | Midpoint degree | Lead variation |
|---|---|---|---|---|
| Intro | 0–3 | I IV I V | IV | augmentation (half-speed, sparse) |
| Verse1 | 4–7 | I I IV I | I | identity (head) |
| Verse2 | 8–11 | IV IV I I | IV | identity + trumpet call-response |
| Chorus | 12–15 | V IV I V | IV | identity (higher register, density up) |
| Solo1 | 16–19 | I IV V IV | IV | **register shift +12** (octave up) |
| Solo2 | 20–23 | IV I V I | I | **transposition +5** (perfect 4th) |
| Bridge | 24–27 | V V IV I | V | **inversion + augmentation** |
| Outro | 28–31 | I V IV I | V | **retrograde + thinning** |

**Per-section harmonic regions**: each section has its own 4-bar progression
(no global 12-bar cycle), so section roots are NOT all degree i. Section roots
(from midpoint degree) = `[IV, I, IV, IV, IV, I, V, V]` → `[45,40,45,45,45,40,47,47]`.

## 4. Variation techniques (6, each mapped to a section)

1. **Augmentation** — Intro: lead holds each tone 2× (half-speed, only even 8ths).
2. **Register shift (+12)** — Solo1: lead an octave up (quantize register 67–91).
3. **Transposition (+5)** — Solo2: lead up a perfect 4th (to the IV region).
4. **Inversion** — Bridge: contour reflected around tonic E4.
5. **Retrograde** — Outro: contour played backward.
6. **Density rise/fall** — Intro/Bridge sparse (hats-only/soft), Chorus/Solo
   full backbeat; Outro thins to quarter-note feel.

## 5. Two-phase architecture

- **Phase 1** (`233-blues-aco-rework-phase1.mid`): raw ACO draft, single voice
  (Raw_Lead harmonica), chromatic nodes, micro-jitter OFF the 120/240 grid. Own
  `validate()` gate (passed).
- **Phase 2** (`233-blues-aco-rework.mid`): musicom rules post-process —
  (a) every onset snapped to the 8th grid, (b) every pitch snapped to its bar's
  blues chord-tone set (floor `t//BAR` attribution), (c) 5-voice band added,
  (d) zero-drift `validate()` gate (passed).

## 6. Verification (read-only mido audit)

| Check | Value |
|---|---|
| MIDI sizes | phase2 7837 B, phase1 2308 B (both > 40) |
| Voice tracks | 5 × 61440 ticks (32 bars) — zero-drift OK |
| Off-grid pitched onsets | **0** |
| Scale violations (pc ∉ blues scale) | **0** |
| Chord violations (pc ∉ own bar chord) | **0** |
| Audio | OGG 644 KB, 81.7 s, peak 0.612, silence 6.2% (OK) |

## 7. Artifacts

- `MIDI/233-blues-aco-rework.mid` (+ provenance sidecar)
- `MIDI/233-blues-aco-rework-phase1.mid` (+ provenance sidecar)
- `Audio/233-blues-aco-rework.ogg` · `Audio/233-blues-aco-rework.wav`
- `Analysis/grid_visualization.txt`
- `provenance.json` · `index.html` · `README.md` · `REPORT.md`
