# REPORT — 262-harmonic-chorale-variations

**Date:** 2026-10-24 · **Job:** musicom nightly rework agent · **Status:** complete + verified

## 1. Selection

| Field | Value |
|---|---|
| **Source project** | `Styles/Experimental/067-harmonic-chorale` (Method 023 Harmonic Series, age 71d) |
| **Genre** | **Experimental** (random draw, seed 262) |
| **Audit result** | **5/6 pass — FAIL on standard 6 (missing `index.html`)** |
| **Decision** | **REDESIGN** (full rebuild through canonical `UnitMatrixComposer`, preserving identity) |
| **New project** | `Styles/Experimental/262-harmonic-chorale-variations/` |

## 2. Source identity (preserved)

F major (ionian) · 92 BPM · 4/4 · SATB chorale · Method 023 Harmonic Series /
Overtone Composition. Core motif = the **natural overtone staircase** of G3
(MIDI 55): 12-TET-quantized partials 1..16, whose consecutive intervals form
the ascending overtone motif `[12,7,5,4,3,3,2,2,2,2,2,1,1,1,1]`. Rhythm DNA =
odd partial → quarter, even partial → eighth. Harmonic DNA = `I–vi–IV–V`
(F–Dm–Bb–C).

## 3. What changed — longer form + more variation

| | Source | New |
|---|---|---|
| Form | 4 sections × 2 bars = **8 bars** | 6 sections × 4 bars = **24 bars** (3×) |
| Duration | ~21 s | ~62 s |
| Voices | Soprano/Alto/Tenor/Bass | Soprano (Flute) / Alto (Strings) / Tenor (Cello) / Bass (Contrabass) |

**Section map + variation techniques (6 techniques, ≥3 required):**

| # | Section | Harmony (per-bar degrees) | Variation technique |
|---|---|---|---|
| 1 | A Theme | I vi IV V | (identity: original overtone staircase) |
| 2 | B Retrograde | V IV vi I | **retrograde** (intervals + rhythm reversed) |
| 3 | C Transposed | V I ii V | **transposition up a 5th** (+7 st, start C5→G5) |
| 4 | D Inversion | IV ii V I | **inversion** (intervals negated) |
| 5 | E Diminution | I IV ii V | **diminution** (durations halved → 2× density) + **register shift up** (soprano 72–88) |
| 6 | F Coda Augm | IV V I I | **augmentation** (durations doubled) + register shift down (60–84), cadence |

Every section has its OWN 4-bar progression (no bar-0 tonic bug — each section
lands on a different degree: V, I, V, I, V, I).

## 4. Two-phase architecture

**Phase 1 (raw draft):** single voice, overtone staircase walked per section
with the variation transform, chromatic (32/146 out-of-scale), off-grid onsets
(142/146), no harmony. Exported `-phase1.mid`, own zero-drift gate.

**Phase 2 (musicom rules):** per-bar chord-tone quantization (soprano), smooth
nearest-octave voice-leading block harmony (alto/tenor/bass via
`Scale7ChordDegree.get_diatonic_note`), 16th-grid onset snap, register/range
enforcement. Dedup collided `(start_tick, pitch)` keeping longest duration.

## 5. Grid + harmony audit (readback, real numbers)

| Version | tracks | voice len | pitched notes | off-grid | scale viol | chord viol (floor t//BAR) |
|---|---|---|---|---|---|---|
| **perfect** | 4 | 46080 | 215 | **0** | **0** | **0** |
| **humanized** | 4 | 46080 | 215 | 182 (>0 ✓) | **0** | 17* |
| **phase1** (raw) | 1 | 46080 | 146 | 142 | 32 | 97 |

\* The 17 humanized "chord violations" are bar-boundary whole-note onsets that
humanization jitter shifted back a few ticks — a `// BAR` attribution artifact,
NOT a pitch problem (scale violations stay 0; humanizer never moves pitch). The
authoritative chord/scale gate passes on the grid-locked perfect layer. Matches
the 261 reference (which enforces chord/scale on perfect only).

## 6. Humanization (always-on, style-derived, seeded) + dual-version export

`export_dual()` via `workflows.humanize`; style profile = `STYLE_HUMANIZE["experimental"]`
(timing 8.0 ms, vel 7.0, phrase_corr 0.5). **hz_seed = 263**.

| Voice | child seed | mean shift (ticks) | max shift | mean vel Δ |
|---|---|---|---|---|
| Soprano | 262*101+0 | 3.469 | 12 | (flute, melodic) |
| Alto | +1 | 2.458 | 9 | (strings, melodic) |
| Tenor | +2 | 3.083 | 8 | (cello, melodic) |
| Bass | +3 | 6.167 | 14 | (contrabass lays back 8 ms) |

Melodic voices style-governed; bass DNA holds (layback 8 ms) — as intended.

## 7. Zero-drift status

`validate()` passed on all three exports. Readback: perfect/humanized = 4 tracks
× 46080 ticks (equal); phase1 = 1 track × 46080. No drift.

## 8. Render + master

FluidSynth (FluidR3_GM.sf2, `-R no -C no`) → WAV → `master()` to
`target_for_style("Experimental")` = **−14 LUFS** (genre fallback), ceiling −1 dBTP
→ Opus OGG. See `Audio/render_stats.json`.

## 9. Files

```
MIDI/262-harmonic-chorale-variations-phase1.mid    (raw draft)
MIDI/262-harmonic-chorale-variations-perfect.mid   (grid-locked)
MIDI/262-harmonic-chorale-variations-humanized.mid
MIDI/*.provenance.json                              (3 sidecars)
Audio/262-harmonic-chorale-variations-{perfect,humanized,phase1}.ogg/.wav
Audio/render_stats.json
Analysis/grid_visualization.txt
Analysis/summary.json
Analysis/verify.json
compose.py · verify.py · render.py
README.md · index.html
```
