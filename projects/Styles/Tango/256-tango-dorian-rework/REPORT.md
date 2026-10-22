# REPORT — 256-tango-dorian-rework

**Project:** 256-tango-dorian-rework
**Genre:** Tango (dramatic/abstract — milonga pulse, dorian darkness)
**Key:** D dorian (D E F G A B C) · **BPM:** 112 · 4/4 · 480 TPB
**Date:** 2026-10-22 (nightly rework job)
**Seed:** 20261022 · humanize seed 20261023

---

## 0. Source + audit

**Chosen source:** `Styles/Tango/087-tango-abstract-dorian` (24 bars, 6 sections,
subset-walk dorian harmony, sax/violin/cello/piano/bass/drums).

**Audit result — FAIL (redesign required).** 5 of 6 standards passed:

| Standard | Result |
|---|---|
| 1. Engine-authored (`UnitMatrixComposer`) | PASS |
| 2. Zero-drift (6 voice tracks == 46080) | PASS |
| 3. Rhythm-grid sync (0 off-grid pitched onsets) | PASS |
| 4. ≥4 voice tracks (6 voices) | PASS |
| 5. Two-phase artifacts (phase1 + main MIDI) | PASS |
| 6. provenance.json + **index.html** | **FAIL — index.html missing** |

Additional notes (not hard fails, fixed in rebuild):
- **Dorian chord-label bug**: source labeled `ii` as "Edim" (actually Em) and
  `IV` as "Gm" (actually G major). The pitch-class math was correct; the labels
  were wrong. Rebuild uses correct dorian labels.
- No humanization / dual-version (`-perfect`/`-humanized`) — predates the
  2026-10-17 contract. Rebuild adds it.
- `compose.py` used `sys.path.insert` for the instrument registry (code smell).

**Decision: REDESIGN** — rebuilt from scratch through the canonical
`UnitMatrixComposer` engine, preserving musical identity (Tango / D dorian /
112 BPM / 6-voice texture / VII-dorian half-cadence home).

Full audit: `087-tango-abstract-dorian/Analysis/rework_audit.json`.

---

## 1. Concept

A longer, more varied rework of the dorian tango. The harmonic DNA is still a
diatonic-in-D-dorian chord field, but now **each of 8 sections owns a distinct
harmonic region** (midpoint-chord root), and the lead line is subjected to a
different variation technique per section. The VII (C major) "dorian home"
half-cadence still frames the piece — it opens and closes on C.

---

## 2. Form: 8 sections × 4 bars = 32 bars (source had 24)

| Section | Bars | Midpoint root | Variation technique |
|---|---|---|---|
| Intro | 0–3 | VII (C) | register shift (lead low) + sparse |
| TangoA | 4–7 | IV (G) | base motif |
| TangoB | 8–11 | ii (Em) | **transposition** (+2 scale degrees) |
| Lift | 12–15 | i7 (Dm7) | **diminution** (16th runs) + **density rise** + 7th chords |
| TangoA2 | 16–19 | III (F) | **inversion** (pivot degree 4) |
| Bridge | 20–23 | v (Am) | **retrograde** + register shift + violin **counterline** |
| Finale | 24–27 | VII (C) | **augmentation** (×2) + tutti |
| Coda | 28–31 | i (Dm) | **diminution** fragment + fade |

Section roots (midpoint chord): **C, G, Em, Dm7, F, Am, C, Dm** — varied, never
all-tonic (fixes the bar-0 tonic bug). Chord quality derived from each
midpoint degree.

**8 distinct variation techniques** (> 3 required): transposition, inversion,
retrograde, augmentation, diminution, register shift, counterline, density rise.

---

## 3. Two-phase architecture

**Phase 1 (`-phase1.mid`)**: raw generative draft, single alto-sax voice.
Per-bar pitch-index **reflected random walk** in [0,1), fractional OFF-GRID
onsets (raw fingerprint). 325 notes, 322 off the 16th grid, all in-scale
(0 scale violations by construction), NOT chord-quantized (198 "chord
violations" = raw material, by design).

**Phase 2 (`-perfect.mid`)**: musicom rules post-process.
1. Onset snap to 16th grid (120 ticks).
2. `pitch_index → scale degree → nearest chord tone` of the bar its SNAPPED
   onset lands in (floor `t//BAR`).
3. Per-section variation transform (see table above).
4. Voice-leading leap cap (≤10 semitones between onsets ≤1 bar apart).
5. Register/range enforcement (sax 49–88, violin ≤96, cello 48–72, bass 38–50).
6. `(start, pitch)` collision dedupe (longest duration wins).
7. Full 6-voice texture + zero-drift terminal landmark per cell.

Result: **1217 notes (757 pitched), 0 off-grid / 0 out-of-scale / 0 out-of-chord.**

---

## 4. Humanization + dual version

Grid-locked phase-2 = the `-perfect` layer. Humanized in place via
`workflows.humanize.export_dual` (style `Tango`, per-instrument DNA from the
registry), seed 20261023, re-validated + re-exported as `-humanized`.

Per-voice humanize stats (mean_abs_shift_ticks / max / vel_delta):

| Voice | shift mean | shift max | vel Δ |
|---|---|---|---|
| LeadSax | 4.47 | 22 | 5.52 |
| Violin | 6.21 | 23 | 4.80 |
| Cello | 4.50 | 16 | 4.16 |
| Piano | 3.62 | 11 | 3.94 |
| Bass | 10.14 | 24 | 5.09 |
| Drums | 1.11 | 4 | 3.07 |

Drums anchor (tightest), bass lays back (+10 ticks), lead/violin in between —
the expected role profile.

---

## 5. Verification (real numbers)

| Metric | phase1 | perfect | humanized |
|---|---|---|---|
| bytes | 2680 | 9634 | 9522 |
| tracks | 2 | 7 | 7 |
| voice len (ticks) | 61440 | 61440 | 61440 |
| zero-drift | OK | OK | OK |
| duration | 68.57 s | 68.57 s | 68.57 s |
| total notes | 325 | 1217 | 1217 |
| pitched notes | 325 | 757 | 757 |
| **off-grid** | 322 (raw) | **0** | **702 (jitter proof)** |
| **scale violations** | 0 | **0** | **0** |
| **chord violations** | 198 (raw) | **0** | 34 (jitter × bar seams) |

- Perfect layer: 0 off-grid, 0 scale, 0 chord — the compositional truth.
- Humanized: off-grid 702 > 0 (jitter ran), scale still 0 (pitches unchanged).
  The 34 "chord violations" are onset jitter crossing bar seams (attribution
  artifact) — every pitch remains in-scale and chord-quantized; no wrong notes.

`Analysis/verify.json` holds the full audit.

---

## 6. What changed vs source

1. 24 → **32 bars** (8 sections, N+2).
2. Correct dorian chord labels (Em not "Edim", G not "Gm").
3. **Per-section harmonic regions** with midpoint roots (source let tension
   curve drive one global walk).
4. 8 variation techniques (source had one global walk, minimal variation).
5. Humanization + dual-version export (source had none).
6. `index.html` dashboard (source missing — the audit failure).
7. Sorted events before humanization (fixed a forward-clamp pinning bug that
   would have shifted dense drum cells hundreds of ticks).

---

## 7. Files

```
256-tango-dorian-rework/
├── compose.py  verify.py  render.py
├── README.md  REPORT.md  index.html
├── MIDI/
│   ├── 256-tango-dorian-rework-phase1.mid      + .provenance.json
│   ├── 256-tango-dorian-rework-perfect.mid     + .provenance.json
│   └── 256-tango-dorian-rework-humanized.mid   + .provenance.json
├── Audio/
│   ├── 256-tango-dorian-rework-perfect.wav/.ogg
│   └── 256-tango-dorian-rework-humanized.wav/.ogg
└── Analysis/
    ├── grid_visualization.txt  summary.json  verify.json
    └── render_stats.json
```
