# REPORT — 105-african-contour

**Project:** 105-african-contour
**Style:** African (polyrhythmic, call-and-response, kalimba + flute + marimba + djembe)
**Method:** 095 Contour Theory Composition (CTC)
**Layer:** `abstract`  ← first numeric abstract-layer method (weekly ~1-in-7 cadence; last abstract composition job was 097 on 2026-09-17)
**Date:** 2026-09-24 (Nightly Autonomous Composition Job, ID 1fc3fd65d359)
**Seed:** 20260924
**Key:** C major pentatonic (C D E G A) = pitch classes {0, 2, 4, 7, 9}
**BPM:** 112 · 4/4 · 480 TPB (bar = 1920, 16th = 120, 8th = 240)
**Form:** 6 sections × 4 bars = 24 bars = 46080 ticks — Intro | Theme | Variation | Development | Climax | Outro
**Project dir:** `/opt/data/repos/musicom/projects/Styles/African/105-african-contour`

---

## 1. Concept & Selection

| Item | Choice | Rationale |
|---|---|---|
| Style | **African** | Random pick from `/opt/data/projects/Styles/` genre folders (excl. _Comparison/_Data_Patterns/Research/Poetry/Production/Percussion/Other + numbered folders), seeded 20260924. |
| Method | **095 Contour Theory Composition (CTC)** | `abstract` layer. The only abstract method in the algorithmic table; first time used as a composition method. Exercises the abstract→concrete interpretation path end-to-end. |
| Layer cadence | **abstract** (~1-of-7) | Last abstract composition job = 097 (2026-09-17, ABS-002). 098/100/101/103 were concrete; tonight continues the abstract cadence. |
| Key | **C major pentatonic** {0,2,4,7,9} | Anhemitonic pentatonic — ubiquitous in sub-Saharan African melodic traditions (kalimba/balafon). |
| BPM / meter | 112 · 4/4 · 480 TPB | Upbeat dance tempo; bar = 1920, 16th = 120. |
| Form | 6×4 = 24 bars (Intro/Theme/Variation/Development/Climax/Outro) | Call → statement → inversion → jagged tension → rising peak → falling resolve. |

### Methods excluded (used in last 7 days)
019 (L-System, 103), 025 (Sieve, 101), 040 (Perlin, 102), 069 (Christoffel, 100),
075 (SOM, 098), 001 (Skeleton, 096) + abstract ABS-002/ABS-001/ABS-003.
095 (CTC) was free and is the designated abstract-layer method.

---

## 2. Method — Contour Theory Composition (CTC, abstract layer)

Contour Theory (Friedmann 1985; Marvin & Laprade 1987; Morris 1993) treats the
**shape** of a line as the primary compositional parameter, independent of exact
pitch-class content. The abstract layer designs **CSeg** (Contour Segment = a
normalized rank sequence where 0 = lowest, n−1 = highest) and its **CAS**
(Contour Adjacency Series = the up/down/same direction string), then transforms
it under the dihedral group {I (invert), R (retrograde), RI (retrograde-invert)}.

### Contour vocabulary (length-4 CSegs, keyed by section CAS template)

| Template | CSeg | CAS | Character |
|---|---|---|---|
| oscillate | [0,3,1,2] | `+-+` | undulating call |
| arch | [0,2,3,1] | `++-` | rise→fall |
| valley | [2,1,0,3] | `--+` | fall→rise |
| chaos | [1,3,0,2] | `+-+` | jagged (high direction-change) |
| rising | [0,1,2,3] | `+++` | build to peak |
| falling | [3,2,1,0] | `---` | resolve down |

### Contour tension curve (per-section seed)

| Section | Template | changes | max_run | entropy | score |
|---|---|---|---|---|---|
| Intro | oscillate | 2 | 1 | 0.918 | 3.918 |
| Theme | arch | 1 | 2 | 0.918 | 3.918 |
| Variation | valley | 1 | 2 | 0.918 | 3.918 |
| Development | chaos | 2 | 1 | 0.918 | 3.918 |
| Climax | rising | 0 | 3 | 0.0 | 3.0 |
| Outro | falling | 0 | 3 | 0.0 | 3.0 |

The macro-form arc is carried primarily by **register** (C4 → C4 → C4 → C5 →
C5 → C3) and **density** (1 motif/bar in Intro & Outro, 2 motifs/bar elsewhere),
with the jagged Development contour providing the textural peak.

### Two-phase architecture (mandatory)

- **Phase 1 (raw abstract draft)** — `MIDI/105-african-contour-phase1.mid`:
  single Kalimba voice. Each CSeg rank r realized as a **raw whole-tone pitch**
  `base + 2·r` (off the C-pentatonic grid by construction), placed on
  **fractional off-grid ticks** (16th ± 30-tick jitter). No scale/chord snap,
  no harmony/bass/drums. Own `validate()` gate PASS.
- **Phase 2 (rules)** — `MIDI/105-african-contour.mid`: 16th-grid lock →
  C-pentatonic snap → per-bar palette (chord-tone) quantize → full 5-voice
  African texture. Zero-drift enforced via `UnitMatrixComposer.validate()`.

The concrete layer maps rank → pentatonic degree via `PENT = [0,2,4,7,9]`
(semitones above tonic), so a rank-4 note is always the dominant-and-a-sixth
above the rank-0 tonic — contour direction preserved exactly, pitch content
pinned to the pentatonic.

---

## 3. Harmonic Framework

**Scale:** C major pentatonic — pc {0, 2, 4, 7, 9}.

**Palettes (4-note chord-tone subsets, one per bar; each drops ONE scale tone):**

| Palette | Pcs | Notes | Dropped |
|---|---|---|---|
| C  | {0,4,7,9}  | C E G A | D |
| D  | {2,4,7,9}  | D E G A | C |
| Am | {9,0,2,4}  | A C D E | G |
| G  | {7,9,0,2}  | G A C D | E |

**Progression (24 bars):**

| Section | Bar 1 | Bar 2 | Bar 3 | Bar 4 |
|---|---|---|---|---|
| Intro | C | C | G | C |
| Theme | C | Am | C | G |
| Variation | Am | G | D | G |
| Development | D | G | Am | D |
| Climax | G | C | D | C |
| Outro | C | G | C | C |

Every palette is a subset of the pentatonic, so chord-tone quantization
guarantees diatonic membership; the dropped tone per palette gives the harmony
audit teeth (a note mapped to the dropped tone is snapped to an adjacent chord
tone).

---

## 4. Voices & Instruments (from registry)

| # | Voice | Instrument | GM | Ch | Role |
|---|---|---|---|---|---|
| 1 | Kalimba | KALIMBA | 108 | 0 | lead contour melody (CTC) |
| 2 | Flute | FLUTE | 74 | 1 | call/response — plays I(contour) in upper register, answered beats 3–4 |
| 3 | Marimba | MARIMBA | 12 | 2 | balafon-style 3-3-2 bell interlock |
| 4 | Bass | DOUBLE_BASS | 43 | 3 | root + fifth foundation (low) |
| 5 | Drums | (GM kit) | — | 9 | djembe: cowbell bell pattern + kick/slap + shaker |

**African rhythm DNA** (16th-grid, ticks = position × 120):

- Bell pattern (cowbell + marimba): `[0, 3, 6, 8, 11, 14]` → the 3-3-2 "standard
  pattern" (tresillo-derived), 6 onsets/bar.
- Kick (djembe bass): beats 1 & 3 (`0`, `8`). Slap (snare): beats 2 & 4 (`4`, `12`).
- Shaker (maracas): straight 8ths (`0,2,4,...,14`).
- Lead kalimba syncopation: full-bar `[0,4,10,14]` or half-bar
  `[0,3,5,7]` / `[8,11,13,15]`.

---

## 5. Verification (REAL numbers)

### Phase 2 (deliverable) — from `Analysis/audit.json`

| Gate | Result |
|---|---|
| `validate()` Phase 2 | **PASS** |
| Zero-drift | 5 tracks all = 46080 ticks (equal length) ✓ |
| Total notes / pitched | 856 / 424 |
| **16th-grid off-grid** | **0 / 856** ✓ (enforced grid = 120 ticks) |
| 8th-grid off-grid | 216 (16th-note syncopation, by design — see note below) |
| **Out-of-scale** | **0 / 424** ✓ |
| **Out-of-chord** | **0 / 424** ✓ |

**Per-track audit (Phase 2):**

| Track | Ch | Notes | off16 | off8 | out-of-scale | out-of-chord |
|---|---|---|---|---|---|---|
| Kalimba | 0 | 160 | 0 | 96 | 0 | 0 |
| Flute | 1 | 72 | 0 | 24 | 0 | 0 |
| Marimba | 2 | 144 | 0 | 48 | 0 | 0 |
| Bass | 3 | 48 | 0 | 0 | 0 | 0 |
| Drums | 9 | 432 | 0 | 48 | — (percussion) | — |

**Grid note:** the enforced grid is the 16th (120 ticks). The 216 "off-8th"
onsets are the African 3-3-2 syncopation (odd-16th positions 3/5/7/11/13/15)
— still integer multiples of 120, i.e. fully on the 16th grid. The canonical
grid check (`abs_tick % 120 == 0 or abs_tick % 240 == 0`, cf. project 104) is
equivalent to "multiple of 120" and passes with 0 violations.

### Phase 1 (raw) — from `Analysis/audit.json`

| Gate | Result |
|---|---|
| `validate()` Phase 1 | **PASS** |
| Zero-drift | 1 track = 46080 ticks ✓ |
| Raw notes | 160 |
| Off-16th (raw fingerprint) | 159 / 160 (99.4% off-grid) ✓ |

### Audio (FluidSynth CLI, FluidR3_GM via `discover_soundfont()`)

| File | Size | Duration | Silence | Peak | Tonal frames |
|---|---|---|---|---|---|
| `105-african-contour.wav` | 10,087,980 B | 57.19 s | 9.55% | 0.913 | 111/114 (97.4%) |
| `105-african-contour.ogg` | 1,124,914 B | — | — | — | — |
| `105-african-contour-phase1.wav` | 10,093,612 B | 57.22 s | 19.11% | 0.281 | 111/114 (97.4%) |
| `105-african-contour-phase1.ogg` | 1,084,422 B | — | — | — | — |

No silent-render trap (silence ≪ 30%), phase-2 peak 0.913 (healthy level),
phase-1 peak 0.281 (single-voice, expected), tonal ratio 97.4% both (not noise).

---

## 6. Artifacts

```
MIDI/105-african-contour.mid                  (7136 B) + .provenance.json
MIDI/105-african-contour-phase1.mid           (1445 B) + .provenance.json
Audio/105-african-contour.wav                 (10.1 MB) + .provenance.json
Audio/105-african-contour.ogg                 (1.12 MB) + .provenance.json
Audio/105-african-contour-phase1.wav          (10.1 MB) + .provenance.json
Audio/105-african-contour-phase1.ogg          (1.08 MB) + .provenance.json
Analysis/grid_visualization.txt
Analysis/summary.json                         (contour progression + tension curve)
Analysis/audit.json                           (grid/harmony/zero-drift numbers)
Analysis/render_stats.json                    (silence/RMS/tonal numbers)
compose.py  render_audio.py  verify.py
```

All size asserts > 40 B passed. Zero-drift `validate()` PASS on both phases.
No raw mido authoring (mido used READ-ONLY in `verify.py`).

---

## 7. Notes / fixes applied

1. **Zero-drift clamp (initial bug, fixed):** first Phase-2 build let the 2nd
   half-bar motif end at tick 2000 (past the 1920 bar) and the flute response
   end at 2040, so the last bar of each section spilled past `SECTION_TICKS`
   (7680) → `validate()` failed with track-length mismatch `[46400, 46800,
   46080, 46080, 46080]`. Fixed by clamping every event into `[0,
   SECTION_TICKS]` inside `seal()` (start ≤ 7679, 7680 ≥ end > start).
2. **Register base pinned to C octaves.** The pentatonic rank→offset table
   `PENT=[0,2,4,7,9]` is anchored to the tonic C; transposing the base to an
   arbitrary pentatonic tone (e.g. D4=62) would have produced non-pentatonic
   pitches (F#, B). Register arcs therefore use octave shifts of C only:
   C4→C4→C4→C5→C5→C3.
3. **Contour transforms verified by construction.** I/R/RI are rank
   permutations, so they preserve the rank set {0..n−1} and thus always map
   onto the full pentatonic degree spread — no off-scale leakage from the
   abstract layer itself.
4. **Whole-tone raw → pentatonic rules.** Phase-1 raw (whole-tone, pcs
   {0,2,4,6,8,10}) snaps cleanly into C-pentatonic during Phase 2 — exactly
   the "generative draft → musicom rules" contract.
