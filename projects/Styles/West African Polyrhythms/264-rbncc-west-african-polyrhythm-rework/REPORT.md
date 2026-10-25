# REPORT — 264-rbncc-west-african-polyrhythm-rework

**Project:** 264-rbncc-west-african-polyrhythm-rework
**Genre:** West African Polyrhythms (Ewe/Ghana timeline ensemble — gankogui double bell, kalimba/kora lead, balafon counter, dunun bass, djembe/shaker drums)
**Key:** G major (G A B C D E F#) · **BPM:** 112 · 4/4 · 480 TPB (bar = 1920, 16th = 120)
**Date:** 2026-10-25 (nightly rework job)
**Seed:** 20260928 · init 20260935 · humanize seed 20260929

---

## 0. Source + audit

**Chosen source:** `Styles/West African Polyrhythms/210-rbncc-west-african-polyrhythm`
(32 bars, 8 sections, Method 082 RBNCC, 5-voice timeline ensemble).

**Audit result — FAIL (redesign required).** 5 of 6 standards passed:

| Standard | Result |
|---|---|
| 1. Engine-authored (`UnitMatrixComposer`) | PASS |
| 2. Zero-drift (5 voice tracks == 61440) | PASS |
| 3. Rhythm-grid sync (0 off-grid pitched onsets) | PASS |
| 4. ≥4 voice tracks (5 voices) | PASS |
| 5. Two-phase artifacts (phase1 + main MIDI) | PASS |
| 6. provenance.json (root) + **index.html** | **FAIL — both missing** |

Additional notes (fixed in rebuild, not hard fails):
- No humanization / dual-version (`-perfect`/`-humanized`) — predates the
  2026-10-17 contract.
- `compose.py` used `sys.path.insert` for the instrument registry (code smell).
- Lead rest handling (25% RBN rests) preserved but made explicit in the new lead builder.

**Decision: REDESIGN** — rebuilt from scratch through the canonical
`UnitMatrixComposer` engine, preserving musical identity (West African
Polyrhythms / G major / 112 BPM / 3:4 cross-rhythm from the 12-step RBN
attractor cycle / 5-voice texture / I-IV-V-I + I-vi-IV-V harmony).

Full audit: `210-rbncc-west-african-polyrhythm/Analysis/rework_audit.json`.

---

## 1. Concept

A longer, more varied rework of the West African polyrhythm. The method DNA is
unchanged — the same RBN (N=16, K=2, p=0.5, seed 20260928) yields the same
attractor cycle (transient 1, cycle 12, frozen node [5]) — so the signature
**3:4 cross-rhythm** (12-step lead cycle vs 16-sixteenth bar) is identical.
The piece is extended by continuing the attractor cycle into 8 new bars, and
each of 10 sections now owns a **distinct harmonic region** (midpoint-chord
root) plus a **distinct variation technique** applied to the lead.

---

## 2. Form: 10 sections × 4 bars = 40 bars (source had 32)

| Section | Bars | Midpoint root | Variation technique |
|---|---|---|---|
| Intro | 0–3 | V (D) | register shift (lead low) + sparse |
| Verse | 4–7 | V (D) | base motif (3:4 polyrhythm) |
| Chorus | 8–11 | IV (C) | density rise (tutti) |
| Verse2 | 12–15 | V (D) | **transposition** (+2 scale degrees) |
| Chorus2 | 16–19 | I (G) | **inversion** (pivot degree 4) |
| Break | 20–23 | ii (Am) | **retrograde** + darker progression (vi–IV–ii–I) |
| Bridge | 24–27 | iii (Bm) | **register shift** (high) + balafon **counterline** |
| Chorus3 | 28–31 | IV (C) | **augmentation** (×2 lead durations) |
| Finale | 32–35 | V (D) | **diminution** (16th runs) + **density rise** |
| Coda | 36–39 | I (G) | **retrograde** recap + diminution fragment + fade |

Section roots (midpoint chord): **D, D, C, D, G, Am, Bm, C, D, G** — varied,
never all-tonic (fixes the bar-0 tonic bug). Chord quality derived from each
midpoint degree (diatonic G-major triads).

**8 distinct variation techniques** (> 3 required): transposition, inversion,
retrograde, augmentation, diminution, register shift, counterline, density rise.

---

## 3. Two-phase architecture

**Phase 1 (`-phase1.mid`)**: raw RBN draft, single kalimba voice. Onsets carry
±18-tick micro-jitter OFF the 16th grid; pitch is raw chromatic
(48 + lead_deg×3), NOT snapped to key/chord. 479 notes, 442 off-grid,
106 out-of-scale, 384 out-of-chord (raw material, by design).

**Phase 2 (`-perfect.mid`)**: musicom rules post-process.
1. Onset snap to 16th grid (120 ticks).
2. `lead_deg → scale degree → nearest chord tone` of the bar its snapped
   onset lands in (floor `t//BAR`).
3. Per-section variation transform (table above).
4. Voice-leading leap cap (≤10 semitones between onsets ≤1 bar apart).
5. Register/range enforcement (lead 48–91, balafon ≤96, bass 36–50).
6. `(start, pitch)` collision dedupe (longest duration wins).
7. Full 5-voice texture + zero-drift terminal landmark per cell.

Result: **1727 notes (964 pitched), 0 off-grid / 0 out-of-scale / 0 out-of-chord.**

---

## 4. Humanization + dual version

Grid-locked phase-2 = the `-perfect` layer. Humanized in place via
`workflows.humanize.export_dual` (style "West African Polyrhythms",
per-instrument DNA from the registry), seed 20260929, re-validated +
re-exported as `-humanized`.

Per-voice humanize stats (mean_abs_shift_ticks / max / vel_delta):

| Voice | shift mean | shift max | vel Δ |
|---|---|---|---|
| Gankogui | 4.11 | 16 | 3.98 |
| LeadKora | 3.95 | 18 | 5.06 |
| BassDunun | 8.37 | 27 | 5.10 |
| Balafon | 3.85 | 15 | 4.30 |
| Drums | 1.15 | 5 | 3.09 |

Drums anchor (tightest, 1.15 ticks), bass lays back (+8.4 ticks), bell/lead
in between — the expected role profile.

---

## 5. Verification (real numbers)

| Metric | phase1 | perfect | humanized |
|---|---|---|---|
| bytes | 3787 | 13975 | 13882 |
| tracks | 2 | 6 | 6 |
| voice len (ticks) | 76800 | 76800 | 76800 |
| zero-drift | OK | OK | OK |
| duration | 85.71 s | 85.71 s | 85.71 s |
| total notes | 479 | 1727 | 1727 |
| pitched notes | 479 | 964 | 964 |
| **off-grid** | 442 (raw) | **0** | **893 (jitter proof)** |
| **scale violations** | 106 (raw) | **0** | **0** |
| **chord violations** | 384 (raw) | **0** | 21 (jitter × bar seams) |

- Perfect layer: 0 off-grid, 0 scale, 0 chord — the compositional truth.
- Humanized: off-grid 893 > 0 (jitter ran), scale still 0 (pitches unchanged).
  The 21 "chord violations" are onset jitter crossing bar seams (attribution
  artifact) — every pitch remains in-scale and chord-quantized; no wrong notes.

`Analysis/verify.json` holds the full audit.

---

## 6. What changed vs source

1. 32 → **40 bars** (10 sections, N+2).
2. **8 variation techniques** mapped per section (source had one global cycle).
3. **Per-section harmonic regions** with midpoint roots (source used a
   4-bar global I-IV-V-I / I-vi-IV-V cycle repeated per section).
4. New **Bridge** section (register-shift + balafon counterline) — the only
   wholly new formal unit.
5. Humanization + dual-version export (source had none).
6. `index.html` dashboard + root `provenance.json` (the audit failures).
7. Explicit RBN rest handling (25% rests) preserved in the new lead builder.

---

## 7. Files

```
264-rbncc-west-african-polyrhythm-rework/
├── compose.py  verify.py  render.py  gen_index.py
├── README.md  REPORT.md  index.html
├── MIDI/
│   ├── 264-rbncc-west-african-polyrhythm-rework-phase1.mid   + .provenance.json
│   ├── 264-rbncc-west-african-polyrhythm-rework-perfect.mid  + .provenance.json
│   └── 264-rbncc-west-african-polyrhythm-rework-humanized.mid + .provenance.json
├── Audio/
│   ├── 264-rbncc-west-african-polyrhythm-rework-perfect.wav/.ogg
│   └── 264-rbncc-west-african-polyrhythm-rework-humanized.wav/.ogg
└── Analysis/
    ├── grid_visualization.txt  summary.json  verify.json
    └── render_stats.json (after render)
```
