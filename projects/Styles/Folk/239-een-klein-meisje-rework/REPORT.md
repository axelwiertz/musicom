# REPORT — 239-een-klein-meisje-rework

**Project:** 239-een-klein-meisje-rework
**Source:** Folk/029-een-klein-meisje (rework agent, nightly)
**Decision:** **REDESIGN** — source failed all 6 standards (hand-rolled mido
engine, zero-drift, grid, track-count, two-phase, provenance). Rebuilt from
scratch through the canonical `UnitMatrixComposer` workflow, preserving
musical identity only.
**Date:** 2026-10-13 · **Seed:** 20261013

---

## 1. Audit of source (029-een-klein-meisje)

| Standard | Result |
|---|---|
| 1. Engine (UnitMatrixComposer, not hand-rolled mido) | **FAIL** — no compose.py; MIDI authored via live_composer.py / stream_engine.py (raw mido), inconsistent TPB 10080 vs 480 |
| 2. Zero-drift (all voice tracks equal length) | **FAIL** — live_render.mid voice tracks 61400 / 61390 / 61410 |
| 3. Rhythm-grid sync (pitched onsets % 120/240) | **FAIL** — 256 of 612 pitched onsets off-grid |
| 4. ≥ 4 voice tracks | **FAIL** — 3 voice tracks (Piano/Guitar/Bass), no drums |
| 5. Two-phase artifacts (`<id>.mid` + `-phase1.mid`) | **FAIL** — no phase1.mid |
| 6. `provenance.json` + `index.html` | **FAIL** — provenance.json missing (index.html present) |

Full audit: `Analysis/rework_audit.json` (in the SOURCE project).

## 2. Identity preserved (from source)

| Field | Value |
|---|---|
| Genre | Dutch Folk / Child Folk (Kleuterlied nursery) |
| Key | G Major = pcs {7,9,11,0,2,4,6} |
| Tempo / Meter | 105 BPM, 4/4, 480 TPB (bar = 1920, 8th = 240, 16th = 120) |
| Method | Markov interval walk over scale degrees (transition table estimated from source melody) |
| Band | Lead (Choir Aahs 53) · Counter (Violin 41) · Harmony (Steel Guitar 25) · Bass (33) · Drums (ch9) |
| Core motif | I-arpeggio 1-3-5-5-3-1 + neighbor 2-3; IV/dominant cadence 4-2-1-5-3-1 |

## 3. Form — longer + more varied

**24 bars = 6 sections × 4 bars** (source was ~3.5 bars of eighth-note melody).

| Section | Bars | Progression | Midpoint root | Lead variation |
|---|---|---|---|---|
| Intro | 0–3 | I IV V I | V (D) | register shift −12 + thin |
| A | 4–7 | I vi ii V | ii (Am) | identity (I-arpeggio motif) |
| B | 8–11 | vi IV iii V | iii (Bm) | transposition +P5 (bright lift) |
| A2 | 12–15 | IV V vi I | vi (Em) | retrograde (contour reversed) |
| C | 16–19 | V ii V vi | V (D) | augmentation ×2 + violin counterline |
| Outro | 20–23 | IV V I I | I (G) | inversion + diminution → cadence |

Variation techniques (6): register-shift-down, identity, transposition-P5,
retrograde, augmentation+counterline, inversion+diminution.

## 4. Two-phase architecture

- **Phase 1** (`-phase1.mid`): raw Markov-interval walk, unquantized float
  pitch + jittered eighth-note rhythm, single voice (Lead), pre-rules.
  Own `UnitMatrixComposer` + own `validate()` gate (passed).
- **Phase 2** (`.mid`): rules post-process — per-bar chord-tone quantization
  (floor `s//BAR` attribution), 120-tick grid snap, dedup of collided
  `(start_tick, pitch)`, voice-leading correction, per-section harmonic
  regions, 5-voice arrangement.

## 5. Verification (read-only mido, phase 2)

| Check | Result |
|---|---|
| File size > 40 B | PASS — 8023 B (phase1 1263 B) |
| Zero-drift | PASS — 5 voice tracks × 46080 ticks |
| Off-grid pitched onsets | **0** of 732 |
| Scale violations (G Major) | **0** |
| Chord violations (per-bar t//BAR) | **0** |
| Audio | 59.92 s, peak 0.689, silence 7.9% (< 30%) |

Phase 1 intentionally raw: 126 off-grid, 8 scale-viol, 68 chord-viol (pre-rules).
