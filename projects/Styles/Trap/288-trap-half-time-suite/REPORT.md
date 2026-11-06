# 288-trap-half-time-suite — Rework Report

**Rework of:** `209-trap-half-time-rework` (Trap, which itself reworked `001-trap-half-time`)
**New project:** `288-trap-half-time-suite`
**Date:** 2026-11-06 · seed 20261106

## 1. Source identity (preserved)

| Attribute | Value |
|---|---|
| Genre | Trap (half-time) |
| Key | C natural minor (pcs {0,2,3,5,7,8,10}) |
| Tempo | 140 BPM |
| Motif | sparse square-lead contour (dark-minor interval pool) |
| Voices | square lead (80), saw counter (81), dark pad (88), 808 sub (38), drums (ch 9) |
| Groove | half-time: kick (1 + and-of-3) / snare (3) / 16th hats + 32nd rolls |
| Method | Brownian-walk pitch_index |
| Mood | dark, sparse, half-time bounce |

## 2. Audit result (source: 209-trap-half-time-rework)

| Standard | Result |
|---|---|
| 1. Engine (UnitMatrixComposer, no raw mido authoring) | **PASS** |
| 2. Zero-drift (all voice tracks equal length) | **PASS** (6 tracks @ 46080) |
| 3. Rhythm-grid sync (pitched onsets) | **PASS** (0 off-16th) |
| 4. Track setup (>=4 voices) | **PASS** (6 voices) |
| 5. Two-phase artifacts (`<id>.mid` + `-phase1.mid`) | **PASS** |
| 6. `provenance.json` + `index.html` | **FAIL** — root `provenance.json` missing (only per-MIDI sidecars) |

**Additional current-standard gaps:** no dual-version export (`-perfect`/`-humanized`),
no humanization (predates 2026-10-17 dual-version + always-on humanize), and a
hand-rolled `quantize_lead` instead of the canonical rules path.

**Decision:** `redesign_required = True` — rebuild fresh through the canonical
`UnitMatrixComposer` workflow, preserving only musical identity.

## 3. What changed (source → new)

- **Form extended**: 24 bars / 6 sections → **32 bars / 8 sections**
  (Intro / Verse / Chorus / Verse2 / Bridge / Chorus2 / Break / Outro).
- **Per-section harmonic regions**: each section its OWN 4-bar progression;
  section root read from the **midpoint chord** (bar 1). Midpoint roots:
  `Ab Gm Eb Ab Gm Eb Cm Ab` — varied, no bar-0 tonic monotony.
- **Dual-version export**: `-perfect.mid` + `-humanized.mid` (source: single MIDI).
- **Root `provenance.json`** + per-artifact sidecars added.
- **Blanket chord-tone quantization**: every pitched note snaps to ITS OWN
  bar's chord (across octaves) — 0 scale violations, 0 chord violations.

## 4. Variation techniques (8 applied, per section)

| Section | Technique |
|---|---|
| Intro | **Augmentation** (long notes) + register drop |
| Verse | baseline dark-minor Brownian contour walk |
| Chorus | **Register shift up** (center 72) + **diminution** (denser 16th + 32nd hat roll) |
| Verse2 | **Transposition** (lead center up a 4th, 66 → 71) + Fm/Ab region |
| Bridge | **Inversion** (mirrored contour) + Ddim dark region |
| Chorus2 | **Counterline** (arpeggiated 3rd/5th/octave saw voice) |
| Break | **Augmentation** + near-sparse (sustained pad only, low sub) |
| Outro | **Retrograde** (reversed contour) + register drop + fade |

## 5. Two-phase architecture

- **Phase 1** (`-phase1.mid`): single-voice raw dark-minor Brownian walk,
  unquantized pitch + jittered off-grid rhythm, no harmony. 212 notes,
  207 off-grid, 87 scale / 149 chord violations (intentionally raw).
- **Phase 2** (`-perfect.mid` / `-humanized.mid`): grid-lock to 16th (120 ticks)
  → blanket chord-tone quantization per bar → voice-leading cap (leap ≤ 9) →
  register clamp (48–84) → dedup → full 5-voice Trap texture.

## 6. Dual-version note (humanization)

- `-perfect`: grid-locked compositional truth — **0 off-grid**, 0 scale
  violations, 0 chord violations, 0 strong-beat violations.
- `-humanized`: trap style profile (timing 4 ms, velocity 4, layback 6 ms,
  phrase_corr 0.25) + per-instrument DNA. **409 off-grid** pitched onsets
  prove jitter ran. 0 scale violations. 2 blanket-chord "violations" are
  onset-boundary artifacts (notes shifted ≤3 ticks early at a bar line are
  attributed to the previous bar by `t // BAR`, pitch still correct).

| Voice | timing_ms | vel_sigma | layback_ms | mean abs shift (ticks) | max shift | vel delta |
|---|---|---|---|---|---|---|
| Lead | 4.0 | 4.0 | 6.0 | 6.52 | 18 | 3.26 |
| Counter | 4.0 | 9.0 | 6.0 | 6.32 | 17 | 7.91 |
| Pad | 4.0 | 4.0 | 6.0 | 8.87 | 16 | 3.28 |
| 808 | 5.0 | 4.0 | **8.0** | 8.82 | 19 | 3.50 |
| Drums | **2.0** | 4.0 | 0.0 | **1.44** | 6 | 3.10 |

Drums anchor (tightest), 808 lays back 8 ms — correct role DNA.

## 7. Verification (read-only mido readback)

| Layer | voices | track len (ticks) | off-grid (pitched) | scale viol | chord viol |
|---|---|---|---|---|---|
| phase1 | 1 | 61440 | 207 (raw) | 87 (raw) | 149 (raw) |
| perfect | 5 | 61440 ×5 | **0** | **0** | **0** |
| humanized | 5 | 61440 ×5 | **409** | **0** | 2 (boundary artifact) |

Zero-drift: all 5 voice tracks length 61440 ticks (32 bars × 1920). ✓
Drums 32nd rolls = 16 off-16th (ch9, exempt). All MIDI/WAV/OGG sizes > 40 B. ✓

## 8. Render + mastering

All three MIDIs rendered FluidSynth (FluidR3_GM.sf2) → WAV → `master()` →
Opus OGG. Target = `target_for_style("trap")` = **−8 LUFS**, −1 dBTP ceiling.

| version | duration | silence | integrated LUFS | true peak |
|---|---|---|---|---|
| phase1 | 57.08 s | 7.46% | −9.17 | −1.00 dBTP |
| perfect | 65.17 s | 13.72% | −9.46 | −1.00 dBTP |
| humanized | 65.17 s | 13.68% | −9.45 | −1.00 dBTP |

Silence < 14% (no mid-track gaps; the 13% is the sparse half-time trap texture
+ reverb tail). True peak at the −1 dBTP ceiling. LUFS lands ~1.4 dB under the
−8 target — crest-factor limited: the sparse half-time kick + sustained pad
cannot be pushed further without clipping (true-peak ceiling is binding, not a
mastering miss).

## 9. Files

```
MIDI/288-trap-half-time-suite-phase1.mid          (1823 B)
MIDI/288-trap-half-time-suite-perfect.mid         (7337 B)
MIDI/288-trap-half-time-suite-humanized.mid       (7300 B)
MIDI/*.mid.provenance.json × 3
Audio/288-trap-half-time-suite-phase1.ogg         (537 KB)
Audio/288-trap-half-time-suite-perfect.ogg        (462 KB)
Audio/288-trap-half-time-suite-humanized.ogg      (462 KB)
Audio/*.wav × 3 (mastered)
Analysis/grid_visualization.txt
Analysis/summary.json
Analysis/render_stats.json
provenance.json  ·  README.md  ·  REPORT.md  ·  compose.py  ·  render.py  ·  index.html
```
