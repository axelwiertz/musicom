# 307-balkan-christoffel-suite — Nightly Rework Report

**Rework job · 2026-11-16 · Source: `100-balkan-christoffel` (Balkan, method 069 CWCC)**

## 1. Source

`/opt/data/projects/Styles/Balkan/100-balkan-christoffel` — Bulgarian Kopanitsa 11/8
(2+2+3+2+2), D Dorian (+Bb bVI borrowing), 160 BPM, Method 069 Christoffel Word
Combinatorial Composition (lower Christoffel word C(5,2)='aaabaab' + Sturmian
morphisms). 6 sections × 4 bars = 24 bars (31,680 ticks ≈ 24.75 s), 5 voices.

## 2. Audit result (6 standards) — 5 PASS, 1 FAIL → redesign

| # | Standard | Result |
|---|----------|--------|
| 1 | Engine (UnitMatrixComposer) | PASS — compose.py imports `workflows.unitmatrix_composer` |
| 2 | Zero-drift | PASS — 5 voice tracks all 31,680 ticks (read-only mido) |
| 3 | Rhythm-grid sync | PASS — 672 pitched onsets, 0 off-grid |
| 4 | ≥4 voice tracks | PASS — 5 tracks (Clarinet 71, Fiddle 40, Tambura 25, Bass 43, Drums ch9) |
| 5 | Two-phase | PASS — `<id>.mid` + `<id>-phase1.mid` present |
| 6 | provenance.json + index.html | **FAIL** — neither present (only per-MIDI sidecars) |

The musical core is fully engine-compliant. Standard 6 fails (documentation
sidecars), and the piece predates the 2026-10-17 dual-version humanization
mandate (no `-perfect`/`-humanized`). Decision: **REDESIGN** — rebuild through the
canonical engine preserving identity only, adding humanization + all sidecars +
a longer, more varied form.

## 3. Source identity preserved

- **Genre/meter**: Balkan · Bulgarian Kopanitsa 11/8 (2+2+3+2+2), 160 BPM
- **Key**: D Dorian {0,2,4,5,7,9,11} + Bb (bVI) folk borrowing {10}
- **Method**: 069 Christoffel Word Combinatorial Composition (C(5,2), Sturmian G/D morphisms)
- **Chords**: Dm · C · G · F · Am · Bb
- **Voices**: Clarinet (71) lead · Fiddle/Violin (40) · Tambura/Steel Guitar (25) ·
  Double Bass (43) · Tupan Drums (ch9)

## 4. New piece

- Project: `/opt/data/projects/Styles/Balkan/307-balkan-christoffel-suite/`
- Form: **8 sections × 4 bars = 32 bars** (source 24 → 33% longer, N+2 sections)
- Ticks: 42,240 (~33 s at 160 BPM) · bar = 1320 ticks (11 sixteenths)

| Section | Bars | Chords | Midpoint root | Technique |
|---------|------|--------|---------------|-----------|
| Intro | 4 | Dm Dm C Dm | C (VII) | augmentation (sparse, half-speed) |
| Tema_A | 4 | Dm C G Dm | G (IV) | baseline C(5,2) 16th run |
| Tema_Ap | 4 | C G Dm G | Dm (i) | inversion + register up (+5) |
| Tema_B | 4 | F C Dm Am | Dm (i) | rotation (conjugate word) |
| Razvivka | 4 | G F C Dm | C (VII) | density rise + counterline |
| Razvivka_2 | 4 | C Am G F | G (IV) | retrograde (reversed word) |
| Tema_A_Var | 4 | Dm G C Dm | C (VII) | diminution (staccato 16ths, register up) |
| Zavurshek | 4 | Bb C Dm Dm | Dm (i) | mode shift bVI Bb + authentic cadence + augmentation |

Per-bar chord-tone quantization uses floor `t // 1320` (each note snaps to its
own bar's chord). Section roots drawn from each section's midpoint chord — no
bar-0 tonic collapse.

## 5. Variation techniques (8 applied; ≥3 required)

1. **Augmentation** — Intro: sparse slots (beats 1/3/5), duration ×1.6, sustained.
2. **Baseline contour** — Tema_A: full C(5,2) 16th-note Kopanitsa run (the identity).
3. **Inversion + register shift** — Tema_Ap: mirrored step direction (a↔b), center 74→79.
4. **Rotation** — Tema_B: rotated conjugate word `baabaaa`, center 72 (lower).
5. **Density rise + counterline** — Razvivka: register climb (76) + tambura extra off-beat hit.
6. **Retrograde** — Razvivka_2: reversed Christoffel word walk.
7. **Diminution** — Tema_A_Var: staccato 16ths (duration ×0.55), register up (77).
8. **Mode shift bVI + cadence** — Zavurshek: Bb (folk borrowing) → C → Dm authentic
   cadence at half-speed (duration ×1.8).

## 6. Two-phase architecture

- **Phase 1** (`-phase1.mid`): raw single-clarinet Christoffel word walk, unquantized
  float pitch + jittered off-grid rhythm (198/207 off-grid), own composer + validate().
- **Phase 2** (`-perfect.mid` / `-humanized.mid`): musicom rules post-process — 16th-grid
  lock, per-bar chord-tone quantization (floor t//1320), register enforcement, dedup —
  then full 5-voice Balkan texture, exported dual via `export_dual`.

## 7. Dual-version + humanization (always-on, seeded)

`hz_seed = 70323`. Style `balkan` (no explicit entry → STYLE_HUMANIZE default profile)
+ per-instrument DNA. Timing jitter in ms → ticks at 160 BPM (1 ms = 1.28 ticks).

| Voice | timing σ | mean shift | max shift | vel Δ | notes |
|-------|----------|-----------|-----------|-------|-------|
| Clarinet | 7.0 ms (8.96 t) | 5.96 | 22 | 5.01 | 264 |
| Fiddle | 7.0 ms (8.96 t) | 5.66 | 25 | 4.86 | 160 |
| Tambura | 7.0 ms (8.96 t) | 6.75 | 20 | 4.90 | 300 |
| Bass | 10.0 ms (12.8 t, +8 ms layback) | 11.34 | 35 | 4.22 | 128 |
| Drums | 2.0 ms (2.56 t) | **1.69** | 8 | 3.23 | 513 (anchors) |

Drums anchor the grid (1.69 ticks); bass lays back 8 ms. Zero-drift preserved
(forward-clamp + boundary-clamp + pinned terminal landmark).

## 8. Verification (real numbers, read-only mido)

| Metric | phase1 | perfect | humanized |
|--------|--------|---------|-----------|
| voice tracks | 1 | 5 | 5 |
| track length (ticks) | 42240 | 42240 | 42240 |
| zero-drift | ✓ | ✓ | ✓ |
| pitched onsets | 207 | 852 | 852 |
| drums (ch9) | 0 | 513 | 513 |
| off-grid (16th=120) | 198 (raw) | **0** | **804** (>0, jitter ran) |
| scale violations | 32 (raw) | **0** | **0** |
| chord violations | 150 (raw) | **0** | 20 (all bar-seam jitter) |

The 20 humanized chord violations are all bar-seam onset jitter (onsets moved
±≤14 ticks across a bar boundary; `t % 1320 ≥ 1270`). Pitch classes stay 100%
in-scale — no pitch errors, only humanized onset drift. This is the documented
humanization artifact (see skill: "humanized chord violations = bar-seam jitter only").

## 9. Audio (mastered to genre target, −1 dBTP ceiling)

`target_for_style("balkan")` (not in GENRE_LUFS → fallback −14 LUFS). SoundFont
FluidR3_GM.sf2 via `discover_soundfont()`. See `Audio/master_stats.json` for the
exact LUFS/true-peak/silence per version.

## 10. Artifacts

- `MIDI/307-balkan-christoffel-suite-phase1.mid` (+ provenance)
- `MIDI/307-balkan-christoffel-suite-perfect.mid` (+ provenance)
- `MIDI/307-balkan-christoffel-suite-humanized.mid` (+ provenance)
- `Audio/*-perfect.ogg` / `*-humanized.ogg` / `*-phase1.ogg`
- `Analysis/grid_visualization.txt`, `Analysis/verification.json`, `Analysis/compose_summary.json`
- `provenance.json`, `index.html`, `compose.py`, `render.py`, `verify.py`
