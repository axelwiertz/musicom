# REPORT — 220-funk-contour-groove

Autonomous nightly composition job · 2026-10-03 · job `1fc3fd65d359`

## Method selection (LAYERED METHODOLOGY)

| Field | Value |
|---|---|
| Style | **Funk** (random from `Styles/` genre folders, excl. _Comparison/_Data_Patterns/Research/Poetry/Production/Percussion/Other + numbered dirs) |
| Method | **095 — Contour Theory Composition (CTC)** |
| Layer | **abstract** |
| Layer roll | 0.0282 < 1/7 → abstract pool (weekly ~1-in-7 cadence; last abstract job = 105 on 2026-09-24, method 095) |
| Seed | 20261003 (date-seeded RNG) |
| Excluded (last 7d) | methods used 2026-09-27 → 10-03: 001,002,010,018,019,025,031,032,040,041,075,082,095 (095 was *last* week's abstract job → excluded by the 7-day window, re-selected by the abstract-cadence roll this time — see note) |

> **Note:** the abstract pool is {095 CTC, 099 SSMC, 104 PSSC}. 095 was used
> 2026-09-24 (9 days ago, outside the 7-day exclusion) and is the designated
> abstract-layer method with the cleanest existing engine mapping
> (`rules/subset_network.py` alias + concrete rank→degree layer). Re-selected
> for the weekly abstract cadence.

## Concept

A **funk** groove where the melodic DNA is the *shape* of the line, not its
notes. Contour Theory (Friedmann 1985; Marvin & Laprade 1987; Morris 1993)
treats contour (the up/down/same direction string) as the primary parameter.
Phase 1 emits a raw whole-tone realization of abstract contour prototypes on
off-grid ticks; Phase 2 imposes the funk grammar: E-minor-pentatonic scale,
per-bar chord-tone palettes, strict 16th-grid rhythm, and a 5-voice funk
texture (trumpet lead, tenor-sax stabs, clavinet comp, contrabass funk bass,
backbeat kit).

## Musical parameters

| Field | Value |
|---|---|
| Key | E minor pentatonic: E G A B D → pcs `{4,7,9,11,2}` (rank offsets `[0,3,5,7,10]`) |
| Tempo | 100 BPM |
| Meter | 4/4 · 480 TPB · BAR = 1920 ticks · 16th = 120 · 8th = 240 |
| Form | 6 sections × 4 bars = **24 bars** = 46080 ticks |
| Instruments (registry) | Trumpet (56) · Tenor Sax (66) · Clavinet/Clavi (7) · Contrabass (43) · Drum Kit (ch9) |

## Method — Contour Theory Composition (CTC, abstract layer)

Length-4 **CSeg** (Contour Segment = normalized rank sequence) + **CAS**
(Contour Adjacency Series = `+`/`-`/`0` direction string), transformed under
the dihedral group {I, R, RI}.

### Contour vocabulary (per section)

| Section | Template | CSeg | CAS | Tension score |
|---|---|---|---|---|
| Intro | oscillate | [0,3,1,2] | `+-+` | 3.918 |
| Theme | arch | [0,2,3,1] | `++-` | 3.918 |
| Variation | valley | [2,1,0,3] | `--+` | 3.918 |
| Development | chaos | [1,3,0,2] | `+-+` | 3.918 |
| Climax | rising | [0,1,2,3] | `+++` | 3.0 |
| Outro | falling | [3,2,1,0] | `---` | 3.0 |

Macro-form arc is carried by **register** (E4 → E4 → E4 → E5 → E5 → E3) and
**density** (1 motif/bar in Intro/Outro, 2 motifs/bar elsewhere).

## Harmonic framework

**Scale:** E minor pentatonic pc `{4,7,9,11,2}`.

**Palettes** (4-note chord-tone subsets, one per bar; each drops ONE scale tone):

| Palette | Pcs | Notes | Dropped |
|---|---|---|---|
| Em | {4,7,11,2} | E G B D | A |
| G | {7,9,11,2} | G A B D | E |
| A | {9,4,11,2} | A E B D | G |
| D | {2,7,9,4} | D G A E | B |

**Progression (24 bars):**

| Section | Bar 1 | Bar 2 | Bar 3 | Bar 4 |
|---|---|---|---|---|
| Intro | Em | Em | G | Em |
| Theme | Em | A | Em | G |
| Variation | A | G | D | G |
| Development | D | G | A | D |
| Climax | G | Em | D | Em |
| Outro | Em | G | Em | Em |

Every palette is a subset of the pentatonic, so chord-tone quantization
guarantees diatonic membership; the dropped tone per palette gives the harmony
audit teeth.

## Voices & instruments (from registry)

| # | Voice | Instrument | GM | Ch | Role |
|---|---|---|---|---|---|
| 1 | Trumpet | TRUMPET | 56 | 0 | lead contour melody (CTC) |
| 2 | Sax | TENOR_SAX | 66 | 1 | offbeat horn stabs (call/response) |
| 3 | Clav | CLAVI | 7 | 2 | staccato 16th "chicken-scratch" comp |
| 4 | Bass | DOUBLE_BASS | 43 | 3 | funk bass root/octave/fifth syncopation |
| 5 | Drums | (GM kit) | 0 | 9 | backbeat + 16th hats + sync kick + clap |

**Funk rhythm DNA (16th-grid, ticks = position × 120):**

- Lead syncopation: full-bar `[0,6,10,14]` (on the one + offbeat hits) or
  half-bar `[0,3,5,7]`/`[8,11,13,15]`.
- Bass "on the one": `[0=root, 6=octave, 8=root, 11=fifth, 14=octave]`.
- Clav scratch: offbeats `[2,4,7,10,12,15]`, muted short stabs.
- Drums: kick `[0,8]` + ghost `[14]`; snare backbeat `[4,12]` + clap layer;
  closed hat straight 16ths `[0..15]`.

## Two-phase architecture

**Phase 1 (raw abstract draft)** — single Trumpet voice. Contour ranks realized
as whole-tone pitches (`rank → base + 2·rank`, chromatic, off the pentatonic
grid by construction), placed on fractional off-grid ticks (16th ±30 jitter).
No scale/chord snapping, no harmony/bass/drums. Own `validate()` PASS.

**Phase 2 (musicom rules)** — 16th-grid lock → E-minor-pentatonic snap →
per-bar palette (chord-tone) quantize → full 5-voice funk texture.
Zero-drift enforced via `UnitMatrixComposer.validate()`.

## Verification (real numbers)

**Grid audit — every pitched voice onset modulo 120 (16th) and 240 (8th):**

| Voice | Ch | Notes | off-16th | off-8th | out-of-scale | out-of-chord |
|---|---|---|---|---|---|---|
| Trumpet | 0 | 160 | 0 | 96 | 0 | 0 |
| Sax | 1 | 72 | 0 | 0 | 0 | 0 |
| Clav | 2 | 144 | 0 | 48 | 0 | 0 |
| Bass | 3 | 120 | 0 | 24 | 0 | 0 |
| Drums | 9 | 552 | 0 | 192 | — (perc) | — |
| **Total** | — | **1048** | **0** | 360 | **0** | **0** |

- **Zero-drift** — all 5 voice tracks = 46080 ticks (24 bars × 1920).
  `validate()` PASS on both phases.
- **off-8th = 360** is the funk 16th-note syncopation (odd-16th positions
  1/3/5/7/9/11/13/15) — fully on the 16th grid (multiples of 120), by design.
- **Phase 1 fingerprint** — 160 notes, 159 off-16th (99.4%) → confirms the raw
  draft keeps its unquantized character (as intended).

**Audio (FluidSynth CLI, FluidR3_GM.sf2 via `discover_soundfont()` → Opus):**

| File | Size | Duration | Silence | Peak | Tonal |
|---|---|---|---|---|---|
| `220-funk-contour-groove.wav` | 10,613,292 B | 60.17 s | 5.7% | 0.767 | 120/120 (100%) |
| `220-funk-contour-groove.ogg` | 1,173,894 B | — | — | — | — |
| `220-funk-contour-groove-phase1.wav` | 10,555,436 B | 59.84 s | 14.85% | 0.452 | 119/119 (100%) |
| `220-funk-contour-groove-phase1.ogg` | 1,192,509 B | — | — | — | — |

No silent-render trap (silence ≪ 30%), healthy peaks, tonal ratio 100% (not noise).

## Files

| Path | Size | Note |
|---|---|---|
| `MIDI/220-funk-contour-groove.mid` | 8776 B | phase 2 (rules) + `.provenance.json` |
| `MIDI/220-funk-contour-groove-phase1.mid` | 1436 B | phase 1 (raw) + `.provenance.json` |
| `Audio/220-funk-contour-groove.wav` / `.ogg` | 10.1 MB / 1.12 MB | + `.provenance.json` |
| `Audio/220-funk-contour-groove-phase1.wav` / `.ogg` | 10.1 MB / 1.14 MB | + `.provenance.json` |
| `Analysis/grid_visualization.txt` | — | 5-voice metrical-gravity grid |
| `Analysis/summary.json` | — | contour progression + tension curve |
| `Analysis/audit.json` | — | grid/harmony/zero-drift numbers |
| `Analysis/render_stats.json` | — | silence/RMS/tonal numbers |
| `compose.py` · `verify.py` · `render_audio.py` | — | generator / read-only audit / render |

All size asserts > 40 B passed. Zero-drift `validate()` PASS on both phases.
No raw mido authoring (mido used READ-ONLY in `verify.py`).

## Fixes applied

- **None required (first-pass clean).** The established safety patterns were
  applied up front: (1) `seal()` clamps every event into `[0, SECTION_TICKS]`
  and appends a terminal zero-drift landmark, so no track-length mismatch;
  (2) chord-tone candidates are restricted to the voice register *before*
  nearest-neighbour (`quantize_to_chord(raw, pal_pcs, min, max)`), so no
  clamp lands on a non-chord pitch; (3) register bases are octave shifts of
  the tonic E only, so `base + PENT[r]` stays inside the pentatonic.
