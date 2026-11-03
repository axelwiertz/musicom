# REPORT — 282-balkan-christoffel-variations

**Rework of:** `100-balkan-christoffel` (Balkan, Method 069 Christoffel Word)
**Date:** 2026-11-03 (nightly rework job)
**Seed:** 20261103

---

## 1. Source audit result

| Standard | Result |
|---|---|
| 1. Engine (UnitMatrixComposer, no raw mido) | PASS |
| 2. Zero-drift (all voice tracks equal length) | PASS (31680) |
| 3. Rhythm-grid sync (onsets % 120/240) | PASS (0 off-grid) |
| 4. Valid track setup (>= 4 voices) | PASS (5 voices) |
| 5. Two-phase artifacts (`<id>.mid` + `-phase1.mid`) | PASS |
| 6. provenance.json + index.html | **FAIL** — no `index.html`, no standalone `provenance.json` |

**Decision: redesign** (fails standard 6). Auxiliary gaps also fixed: 6 out-of-key
pitches (Bb borrowing never folded into the declared key set) and no dual-version
(`-perfect`/`-humanized`) export.

## 2. What changed

- Rebuilt through the canonical `UnitMatrixComposer` two-phase workflow.
- **Longer form:** 6 -> **8 sections** (24 -> **32 bars**), 42240 ticks (~33 s @ 160).
- **Key declared to include the b6 (Bb) borrowing** (`KEY_PCS = D Dorian + Bb`) so
  the scale audit is 0 by construction (no hidden out-of-key pitches).
- **Dual-version export** (`-perfect` + `-humanized`) via `export_dual`.
- Added `index.html` dashboard, standalone `provenance.json`, and per-artifact
  provenance sidecars.

## 3. Variation techniques (where)

| # | Technique | Section |
|---|---|---|
| 1 | **Inversion** — lead step sign flipped (a->-2,b->+1), fiddle contour mirrored | 4 `Tema_A_Inv` |
| 2 | **Augmentation** — lead 16th->8th (half-speed), tambura->sustained pad, bass->sparse, drums->8th hat | 5 `Tema_B_Aug` |
| 3 | **Retrograde** — Christoffel word reversed (`base_word[::-1]`) | 6 `Tema_A_Retro` |
| 4 | **Register shift** — lead 74->79 (D5->G5), fiddle 57-77->60-81 | 3 `Razvivka` |
| 5 | **Density rise** — tambura->16th arpeggio, bass->walking 8ths, drums->tom fill | 3 `Razvivka` |
| 6 | **Mode shift / b6 borrowing** — Bb chord (Folk-Minor coloring) | 7 `Zavurshek` |

## 4. Per-section harmonic regions

Each section carries its own 4-bar progression (no all-tonic "bar-0" collapse).
Section root taken from the MIDPOINT chord (bar index 2):

```
0 Intro:        Dm  C  Dm  Dm   (mid Dm -> root D)
1 Tema_A:       Dm  C  G   Dm   (mid G  -> root G)
2 Tema_B:       F   C  Dm  Am   (mid Dm -> root D)
3 Razvivka:     G   F  C   Dm   (mid C  -> root C)
4 Tema_A_Inv:   Am  Dm G   C    (mid G  -> root G)
5 Tema_B_Aug:   C   G  Dm  F    (mid Dm -> root D)
6 Tema_A_Retro: G   Dm C   Dm   (mid C  -> root C)
7 Zavurshek:    Bb  C  Dm  Dm   (mid Dm -> root D)  [b6 borrowing]
```

## 5. Two-phase architecture

- **Phase 1** (`-phase1.mid`): raw Christoffel/Sturmian walk, unquantized pitch
  (float) + rhythm, single voice (Clarinet). 205 notes, 196 off-grid — the raw
  generative character, pre-rules. Own `validate()` gate passed (42240 ticks).
- **Phase 2** (`-perfect.mid`): musicom rules post-process — per-bar chord-tone
  quantization, 16th-grid snap (120 ticks), register/range enforcement, dedup of
  `(start_tick, pitch)` collisions keeping longest, per-section harmonic regions.

## 6. Verification (real numbers)

| Check | phase1 | perfect | humanized |
|---|---|---|---|
| Voice tracks | 1 | 5 | 5 |
| Track length (ticks) | 42240 | 42240 (x5) | 42240 (x5) |
| Zero-drift | PASS | PASS | PASS |
| Pitched notes (excl. ch9) | 205 | 816 | 816 |
| Off-grid onsets | 196 (raw) | **0** | **786** (jitter ran) |
| Scale violations | 26 (raw) | **0** | **0** |
| Chord violations | 114 (raw) | **0** | 20* |

\* humanized 20 = notes whose jittered onset crossed a bar boundary (t//BAR
mis-attribution), not compositional error — pitch unchanged, scale still 0.

**Humanization (style `balkan-folk`, seeded 20261103):** per-voice stats
(mean_abs_shift_ticks / max / vel_delta): Clarinet 7.9/32/5.4, Fiddle 7.3/32/4.4,
Tambura 8.0/25/4.8, Bass 11.7/40/5.1 (lays back 8 ms), Drums 1.8/6/3.2 (anchors).

## 7. Audio (see render_stats.json)

Mastered to **-16.0 LUFS** (`target_for_style("balkan-folk")`), -1 dBTP ceiling.

## 8. Artifacts

- `MIDI/282-balkan-christoffel-variations-phase1.mid`
- `MIDI/282-balkan-christoffel-variations-perfect.mid`
- `MIDI/282-balkan-christoffel-variations-humanized.mid`
- `Audio/...-perfect.ogg`, `Audio/...-humanized.ogg`, `Audio/...-phase1.ogg`
- `Analysis/rework_audit.json`, `Analysis/verify.json`, `Analysis/grid_visualization.txt`, `Analysis/render_stats.json`
- `compose.py`, `verify.py`, `render_audio.py`, `index.html`, `README.md`, `REPORT.md`
