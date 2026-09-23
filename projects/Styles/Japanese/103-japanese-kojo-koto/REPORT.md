# 103-japanese-kojo-koto — Composition Report

**Project:** 103-japanese-kojo-koto
**Style:** Japanese (koto + shakuhachi + shamisen + taiko, Jo-Ha-Kyu form)
**Method:** 019 L-System Algorithmic Composition (dragon-curve / paperfolding grammar)
**Layer:** `concrete`
**Date:** 2026-09-23 (Nightly Autonomous Composition Job)
**Project dir:** `/opt/data/repos/musicom/projects/Styles/Japanese/103-japanese-kojo-koto`

---

## 1. Concept & Selection

| Item | Choice | Rationale |
|---|---|---|
| Style | **Japanese** | Random pick from genre folders (excl. _Comparison/_Data_Patterns/Research/Poetry/Production/Percussion/Other). |
| Method | **019 L-System Algorithmic Composition** | `concrete` layer; has shared engine code (`generators/interval_lsystem.py`); not used in the last 7 days. |
| Layer cadence | **concrete** (6-of-7 nights) | Last abstract run was 097 (2026-09-17); 098–102 were concrete, tonight continues concrete. |
| Key | **A hirajoshi pentatonic** (A Bb D E G) → pc {9,10,2,4,7} | Authentic Japanese koto scale; pentatonic drone idiom. |
| BPM / meter | 80 · 4/4 · 480 TPB | Meditative koto tempo; Bar = 1920 ticks, 16th = 120, 8th = 240. |
| Form | **Jo | Ha1 | Ha2 | Kyu1 | Kyu2 | Jo_Coda** (6×4 = 24 bars) | Classical Japanese Jo-Ha-Kyu acceleration arc. |
| Seed | 20260923 | Deterministic. |

### Methods excluded (used in last 7 days)
001, 002, 006, 018, 023, 025, 040, 069, 075, 079 (numeric) + ABS-002/003/004 (abstract).
019 was free and has clean engine code.

---

## 2. Method — L-System (019)

**Grammar (dragon-curve / paperfolding):**

```
axiom   : "A"
rules   : A -> "A+B",  B -> "A-B"
symbols : "+" = +2 semitones,  "-" = -2 semitones,  "=" = unison
iterations : 8  ->  255 terminal deltas
```

- Self-similar and **bounded**: +/− counts stay within 1 of each other (128 vs 127),
  so the raw pitch stays inside [69, 85] — a tight, balanced fractal contour.
- Verified via `generators.interval_lsystem.IntervalLSystem.generate_deltas()`.

**Two-phase architecture (mandatory):**

- **Phase 1 (raw):** single Koto voice walks the fractal. Pitch folded into a
  3-octave koto window (57–91) preserving contour direction; micro-rhythm drawn
  unquantized (~235±25 ticks/note). No scale/chord snapping. → `-phase1.mid`.
- **Phase 2 (rules):** every pitched voice snapped to the 16th/8th grid, then to
  the A-hirajoshi scale, then to the per-bar palette (chord tones). Full 5-voice
  texture. Zero-drift enforced via `UnitMatrixComposer.validate()`. → `.mid`.

---

## 3. Harmonic Framework

**Scale:** A hirajoshi pentatonic — pc {9, 10, 2, 4, 7} (A, Bb, D, E, G).

**Palettes (4-note chord-tone subsets, one per bar):**

| Name | Pcs | Dropped tone |
|---|---|---|
| A  | {9,10,2,4}  (A Bb D E)  | G |
| G  | {9,10,2,7}  (A Bb D G)  | E |
| Bb | {10,2,4,7}  (Bb D E G)  | A |
| E  | {9,10,4,7}  (A Bb E G)  | D |

**Progression (24 bars):**

| Section | Bar 1 | Bar 2 | Bar 3 | Bar 4 |
|---|---|---|---|---|
| Jo | A | A | G | A |
| Ha1 | A | G | Bb | A |
| Ha2 | Bb | G | E | Bb |
| Kyu1 | E | Bb | A | E |
| Kyu2 | A | G | Bb | A |
| Jo_Coda | A | E | A | A |

Every palette is a subset of the scale, so chord-tone quantization guarantees
diatonic membership; the dropped tone per palette gives the harmony audit teeth.

---

## 4. Voices & Instruments (from registry)

| # | Voice | Instrument | GM | Ch | Role |
|---|---|---|---|---|---|
| 1 | Koto | KOTO | 107 | 0 | lead fractal melody (L-system) |
| 2 | Shakuhachi | FLUTE | 74 | 1 | sustained upper counterline |
| 3 | Shamisen | SHAMISEN | 106 | 2 | rhythmic pluck ostinato |
| 4 | KotoBass | KOTO | 107 | 3 | low whole-note drone |
| 5 | Taiko | DRUM_KIT | — | 9 | low-tom thumps + rim texture |

Lead density follows the Jo-Ha-Kyu arc: Jo quarter-notes → Ha eighth-notes →
Kyu full 16th runs → Jo_Coda gentles back (visible in `grid_visualization.txt`).

---

## 5. Verification (real numbers)

| Gate | Result |
|---|---|
| `validate()` Phase 1 | **PASS** |
| `validate()` Phase 2 | **PASS** |
| Zero-drift | all 5 voices = 46080 ticks (equal length) ✓ |
| 16th-grid off-grid (Phase 2) | **0 / 556** ✓ |
| Out-of-scale (Phase 2) | **0 / 556** ✓ |
| Out-of-chord (Phase 2) | **0 / 556** ✓ |
| Phase 1 raw fingerprint | **190 / 192 (99.0%) off-grid** — raw unquantized ✓ |
| Phase 2 silence ratio | 6.45% (≤ 30%, healthy) |
| Phase 2 tonal frames | 150 / 150 (100% tonal, 50–1000 Hz) |
| Phase 1 silence ratio | 7.4% |
| Phase 1 tonal frames | 148 / 150 (98.7%) |

**Per-track audit (Phase 2):**

| Track | Notes | off16 | out-of-scale | out-of-chord |
|---|---|---|---|---|
| Koto (ch0) | 228 | 0 | 0 | 0 |
| Shakuhachi (ch1) | 48 | 0 | 0 | 0 |
| Shamisen (ch2) | 160 | 0 | 0 | 0 |
| KotoBass (ch3) | 24 | 0 | 0 | 0 |
| Taiko (ch9) | 96 | 0 | — (percussion, not audited) | — |

---

## 6. Artifacts

| File | Size |
|---|---|
| `MIDI/103-japanese-kojo-koto.mid` | 5089 B |
| `MIDI/103-japanese-kojo-koto-phase1.mid` | 1699 B |
| `Audio/103-japanese-kojo-koto.wav` | 13,284,396 B |
| `Audio/103-japanese-kojo-koto.ogg` | 1,543,048 B |
| `Audio/103-japanese-kojo-koto-phase1.wav` | 13,285,164 B |
| `Audio/103-japanese-kojo-koto-phase1.ogg` | 1,643,957 B |
| `Analysis/grid_visualization.txt` | 3685 B |
| `Analysis/audit.json` + `Analysis/render_stats.json` + `Analysis/summary.json` | — |

Provenance sidecars (`.provenance.json`) written for both MIDI files.

---

## 7. Render pipeline

- FluidSynth CLI (`-ni -g 1.2`) with auto-discovered `FluidR3_GM.sf2`.
- OGG via ffmpeg Opus 128k.
- No raw mido authoring (mido used only for READ audit).

---

## 8. Notes / fixes applied

- L-System module docstring is misleading (`"-": 1` actually means **+1** — the
  symbol value is used verbatim). Used explicit `"-": -2` to get a descending step.
- Unbalanced grammars (e.g. `A->A+B-A, B->A-B`) drift monotonically; chose the
  classic dragon-curve grammar (perfectly balanced, bounded) for a clean fractal.
- Whole-tone raw contour (pcs {9,11,1,3,5,7}) snaps cleanly into hirajoshi during
  Phase 2 — exactly the "generative draft → musicom rules" contract.
