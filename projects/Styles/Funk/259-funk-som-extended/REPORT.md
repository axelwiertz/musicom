# REPORT — 259-funk-som-extended (nightly rework 2026-10-23)

**Source:** `098-funk-som` (Funk / Method 075 SOM-C / F minor / 104 BPM / 24 bars)
**New project:** `259-funk-som-extended` (Funk / F minor / 104 BPM / 32 bars)

---

## 1. Audit of source (6 standards)

| # | Standard | Result |
|---|---|---|
| 1 | Engine (UnitMatrixComposer) | PASS — `to_midi()` via canonical composer, no raw mido authoring |
| 2 | Zero-drift | PASS — 5 voice tracks × 46,080 ticks |
| 3 | Rhythm-grid sync | PASS — 0 pitched off-grid onsets |
| 4 | Valid track setup | PASS — 5 voice tracks |
| 5 | Two-phase artifacts | PASS — `098-funk-som.mid` + `098-funk-som-phase1.mid` |
| 6 | provenance.json + index.html | **FAIL** — `index.html` missing; only per-artifact `.provenance.json` sidecars, no root `provenance.json` |

**Decision:** `redesign_required = true` (standard 6 failed) → full rebuild from
scratch through the canonical engine, preserving musical identity only.

## 2. What changed (source → new)

- **Form:** 6 sections × 4 bars = 24 bars → **8 sections × 4 bars = 32 bars** (N+2).
- **Variation:** 7 distinct techniques added (source had none — uniform 6-section form).
- **Dual-version:** added `-perfect` + `-humanized` export (2026-10-17 contract).
- **Per-section harmonic regions:** each section owns its progression with
  MIDPOINT-chord root — varied (iv, VI, VII, i, III, VII, VI, v), no bar-0 tonic collapse.
- **7th-chord color** in Chorus2 + Break (source used triads only).
- **Compliance:** added `index.html` + provenance for every artifact + `verify.py`.

## 3. Identity preserved

- Genre Funk, F minor (aeolian, tonic F=5), 104 BPM, 4/4, 480 TPB.
- Method 075 SOM-C: 4×4 toroidal Kohonen map + Markov walk → pitch-index contour.
- Instrumentation: Lead Trumpet (GM56), Tenor Sax (GM65), Piano (GM1),
  Double Bass (GM43), Drums (ch9).

## 4. Variation map

| Section | Bars | Midpoint root | Technique |
|---|---|---|---|
| Intro | 0–3 | iv (Bbm) | register shift (low) + sparse |
| Verse | 4–7 | VI (Db) | base motif |
| Chorus | 8–11 | VII (Eb) | transposition +3 + density rise |
| Bridge | 12–15 | i (Fm) | retrograde + register shift (upper) |
| Verse2 | 16–19 | III (Ab) | inversion (pivot deg 3) |
| Chorus2 | 20–23 | VII (Eb) | augmentation ×2 + 7th color |
| Break | 24–27 | VI (Db) | diminution (16th) + counterline |
| Outro | 28–31 | v (Cm) | diminution fragment + fade |

## 5. Verification (real numbers, read-only mido)

| Metric | phase1 | perfect | humanized |
|---|---|---|---|
| MIDI size | 1,176 B | 10,183 B | 10,177 B |
| Voice tracks | 1 | 5 | 5 |
| Track length (ticks) | 61,440 | 61,440 × 5 | 61,440 × 5 |
| Zero-drift | PASS | PASS | PASS |
| Total notes | 134 | 1,314 | 1,314 |
| Pitched notes | 134 | 614 | 614 |
| Off-grid onsets | 133 (raw) | **0** | **575** (jitter) |
| Scale violations | 0 | **0** | **0** |
| Chord violations | 83 (raw, expected) | **0** | 14 (bar-seam jitter) |

- Humanization seed: `20261024` (SEED+1); per-voice profiles from instrument registry.
- Off-grid perfect == 0 (compositional truth); humanized > 0 proves jitter ran.

## 6. Audio (FluidSynth → master → Opus)

Rendered with FluidR3_GM.sf2, mastered to `target_for_style("Funk") = −13 LUFS`,
−1 dBTP ceiling. See `Audio/render_stats.json` for LUFS/peak/silence per render.

## 7. Artifacts

- `MIDI/259-funk-som-extended-phase1.mid` + `.provenance.json`
- `MIDI/259-funk-som-extended-perfect.mid` + `.provenance.json`
- `MIDI/259-funk-som-extended-humanized.mid` + `.provenance.json`
- `Audio/259-funk-som-extended-{perfect,humanized,phase1}.{wav,ogg}`
- `Analysis/grid_visualization.txt`, `Analysis/summary.json`, `Analysis/verify.json`
- `index.html` (VoltAgent dashboard), `README.md`

## 8. Lead-timing fix (2026-10-23 rebuild)

Straight-16th funk groove — no swing, so the jazz swing bug does not apply; the
lead is already on the correct grid. The real lead-timing issue was humanization:
the lead trumpet carried the Brass family default (7.0 ms σ, **4.0 ms layback**)
so it sat ~4 ms behind and drifted up to 16 ticks against a 2.0 ms drum anchor.
Funk lead must sit on top, so `hz_instruments["Lead"]` is overridden to
`(4.0, 8.0, 0.0, 0.02)` → layback 4.0 → 0.0 ms, σ 7.0 → 4.0 ms. Lead mean |dev|
2.16 ticks (was 4.69), max 7 (was 16). Re-composed + re-verified + re-rendered.
