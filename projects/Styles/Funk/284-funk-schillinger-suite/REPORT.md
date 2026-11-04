# 284-funk-schillinger-suite — Rework Report

**Rework of:** `081-funk-schillinger` (Funk / Method 018 Schillinger)
**New project:** `284-funk-schillinger-suite`
**Date:** 2026-11-04

## 1. Source identity (preserved)

| Attribute | Value |
|---|---|
| Genre | Funk |
| Key | Bb major |
| Tempo | 100 BPM |
| Method | 018 Schillinger System (rhythmic interference resultant) |
| Voices | Trumpet lead (56), Rhodes (4), Electric Guitar (27), Electric Bass (33), Clavinet (7), Drums (ch 9) |
| Core DNA | Schillinger resultant rhythm (a=5,b=3) × sine-projection pitch contour |

## 2. Audit result (source: 081-funk-schillinger)

| Standard | Result |
|---|---|
| 1. Engine (UnitMatrixComposer, no raw mido authoring) | PASS |
| 2. Zero-drift (all voice tracks equal length) | PASS (6 tracks × 46080 ticks) |
| 3. Rhythm-grid sync (pitched onsets on 8th/16th) | PASS (0 off-grid) |
| 4. Track setup (>=4 voices) | PASS (6 voices) |
| 5. Two-phase artifacts (`<id>.mid` + `<id>-phase1.mid`) | PASS |
| 6. `provenance.json` + `index.html` present | **FAIL** — both missing (per-artifact `.provenance.json` sidecars only) |

**Decision:** `redesign_required = True` (standard 6 fail). Full rebuild through the
canonical `UnitMatrixComposer` workflow, preserving only musical identity, discarding
the source's non-compliant packaging.

## 3. What changed (source → new)

- **Form extended**: 6 sections → **8 sections** (Intro / Verse / Chorus / Verse2 /
  Chorus2 / Bridge / Chorus3 / Outro), 24 → **32 bars** (N+2 sections).
- **Per-section harmonic regions**: source used one global 24-bar cycle (bar-0 tonic
  bug risk). New version gives each section its OWN 4-bar progression; section root is
  read from the **midpoint chord** (bar 1), not bar 0. Midpoint roots:
  `IV vi V vi V IV V IV` (varied — bug avoided).
- **Dual-version export**: `-perfect.mid` + `-humanized.mid` (source shipped only one
  `<id>.mid`).
- **`index.html` dashboard + root `provenance.json`** added (source lacked both).
- **Register-safe lead quantization**: source snapped lead to one base-octave triad;
  new version snaps to the nearest chord tone in ANY octave (better voice leading).

## 4. Variation techniques (8 applied, documented per section)

| Section | Technique |
|---|---|
| Intro | **Augmentation** (resultant durations ×2) + sparse density |
| Verse | baseline Schillinger (a=5,b=3), sine contour |
| Chorus | **Register shift** up (lead center 76) + full texture |
| Verse2 | **Transposition** (lead up a perfect 4th) |
| Chorus2 | register shift (center 78) |
| Bridge | **Per-section method change** (Schillinger a=7,b=4) + **inversion** (mirrored contour) + **mode shift** (relative-minor Gm region) |
| Chorus3 | **Counterline** (Clav plays diatonic-third harmony of lead) |
| Outro | **Retrograde** (reversed resultant) + register drop (66) |

## 5. Two-phase architecture

- **Phase 1** (`-phase1.mid`): single-voice raw Schillinger walk — fractional off-grid
  durations, raw sine/inverted projection + register drift, no harmony. 244 events,
  235 off-grid (intentionally raw).
- **Phase 2** (`-perfect.mid` / `-humanized.mid`): grid-lock to 16th (120 ticks) →
  scale quantization → per-bar chord-tone quantization → voice-leading (leap cap ≤ 9,
  `rules.voice_leading` check) → dedup → full 6-voice funk texture.

## 6. Dual-version note (humanization)

- `-perfect`: grid-locked compositional truth — **0 off-grid**, 0 scale violations,
  0 chord violations.
- `-humanized`: style profile (funk: 4 ms timing, 6 velocity, layback 2 ms) +
  per-instrument DNA (bass +8 ms layback, drums anchor 2 ms). **598 off-grid** onsets
  prove jitter ran. Scale violations 0 (pitch unchanged). 7 chord "violations" are
  onset-boundary artifacts: notes played ≤3 ticks early at a bar line are attributed
  to the previous bar by the `t // BAR` audit, but their PITCH is correct for the
  intended bar — a timing artifact, not a harmonic error.

## 7. Verification (read-only mido readback)

| Layer | voices | track len (ticks) | off-grid | scale viol | chord viol |
|---|---|---|---|---|---|
| phase1 | 1 | 61440 | 235 | 98 (raw, unquantized) | 177 (raw) |
| perfect | 6 | 61440 ×6 | **0** | **0** | **0** |
| humanized | 6 | 61440 ×6 | **598** | **0** | 7 (boundary artifact) |

Zero-drift: all 6 voice tracks length 61440 ticks (32 bars × 1920). ✓
All MIDI/WAV/OGG sizes > 40 B. ✓

## 8. Files

- `MIDI/284-funk-schillinger-suite-phase1.mid`
- `MIDI/284-funk-schillinger-suite-perfect.mid`
- `MIDI/284-funk-schillinger-suite-humanized.mid`
- `Audio/284-funk-schillinger-suite-perfect.ogg`
- `Audio/284-funk-schillinger-suite-humanized.ogg`
- `Analysis/grid_visualization.txt`, `Analysis/summary.json`, `Analysis/rework_audit.json`
- `index.html` (dashboard), `README.md`
