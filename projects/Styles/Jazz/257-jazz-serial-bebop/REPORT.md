# REPORT — 257-jazz-serial-bebop

**Project:** 257-jazz-serial-bebop
**Genre:** Jazz (bebop swing, ii-V-I)
**Method:** 065 — Twelve-Tone Serial Matrix Composition (TTSMC) · **Layer:** concrete
**Form:** `intro-a-a-b-a` (Intro 4 + A1 8 + A2 8 + B 8 + A3 8 = 36 bars)
**Key:** F major (F G A Bb C D E) · **BPM:** 120 · 4/4 · 480 TPB
**Date:** 2026-10-22 (nightly composition job)
**Seed:** 20261022 · humanize seed 20261023

---

## 1. Concept

A twelve-tone serial row drives the melodic DNA; Phase 2 projects it onto
bebop ii-V-I harmony. The row's P/R/I/RI transformations supply the form's
contrast: each of the 5 sections is a distinct row-form region. The serial
aggregate property (all 12 pitch classes, once per statement) is preserved in
the raw draft; the diatonic layer snaps it onto F-major 7th chords so it reads
as swing bebop, not Schoenberg.

**12-tone row P0** (seeded, deterministic): `[4, 7, 10, 2, 9, 0, 5, 11, 1, 8, 3, 6]`
- I0 (inversion) = `[8, 5, 2, 10, 3, 0, 7, 1, 11, 4, 9, 6]`
- R0 (retrograde) = `[6, 3, 8, 1, 11, 5, 0, 9, 2, 10, 7, 4]`
- RI0 (retrograde-inversion) = `[6, 9, 4, 11, 1, 7, 0, 3, 10, 2, 5, 8]`

---

## 2. Form + harmony (36 bars, diatonic 7th chords in F major)

| Section | Bars | Row form | Midpoint root | Progression |
|---|---|---|---|---|
| Intro | 0–3 | P0 | vi (Dm7) | I–vi–ii–V (Fmaj7 Dm7 Gm7 C7) |
| A1 | 4–11 | P0 | I (Fmaj7) | ii–V–I–vi · ii–V–I–I |
| A2 | 12–19 | R0 (retrograde) | I (Fmaj7) | ii–V–I–vi · ii–V–I–I |
| B | 20–27 | I0 (inversion) | ii (Gm7) | iii–vi–ii–V ×2 (circle of 5ths) |
| A3 | 28–35 | RI0 (retro-inversion) | I (Fmaj7) | ii–V–I–vi · ii–V–I–I |

Chord symbols (F major): `Imaj7=Fmaj7, ii7=Gm7, iii7=Am7, IVmaj7=Bbmaj7,
V7=C7, vi7=Dm7, viiø7=Eø7`. All chords are diatonic → every chord tone is an
F-major scale tone (the tiered discipline's in-scale ∩ in-chord requirement is
satisfiable with zero chromaticism).

---

## 3. Two-phase architecture

**Phase 1 (`-phase1.mid`)** — raw serial draft, single sax voice. The 12-tone
row's pitch classes (60 + row_pc, chromatic) in P/R/I/RI section regions, with
fractional OFF-GRID onsets. **Serial fingerprint verified: all 12 pitch
classes present** (raw_pc_count = 12), 259 notes, 256 off-grid, deliberately
out-of-scale (chromatic) — the serial identity, not a bug.

**Phase 2 (`-perfect.mid`)** — musicom rules post-process:
1. Onset snap to 16th grid (120 ticks).
2. Row pc → nearest F-major scale degree → nearest chord tone of the bar's
   7th chord (ii-V-I family).
3. Section variation (B = density/16th runs, A3 = fade, Intro = sparse).
4. Full 5-voice swing texture (sax lead / trumpet guide-tones / piano comp /
   walking bass / swing drums).
5. Voice-leading leap cap (≤11 semitones) + register enforcement.
6. `(start, pitch)` dedupe + zero-drift terminal landmark per cell.

**Result: 1185 notes (761 pitched), 0 off-grid, 0/0/0 harmony violations.**

---

## 4. Tiered pitch discipline (Phase 3 role-first engine)

Weight-aware snap via `sound.synthesis.scale_quantizer` + audit via
`workflows.pitch_audit.audit_voice` (strong_grid = 4/4 beats 1&3 = (0, 960)):

- **Strong beats (1, 3)** = chord tones (in-scale AND in-chord).
- **Weak beats (2, 4)** = in-scale (bass beat-4 uses a diatonic leading tone
  one semitone below the next bar's root — a genuine scale-but-not-chord note
  that exercises the weak/scale-only path).
- Lead/counter/bass/pad/rhythm: **zero chromatic ornaments** (bass/pad/harmony
  MUST be chromatic-free; lead MAY carry tagged ornaments — none needed here
  since the row is already diatonicized cleanly).

Harmony audit (perfect layer, strict in-chord):

| Voice | audible | strong_ok | weak_in_scale | untagged | non-resolving | strong_viol | PASS |
|---|---|---|---|---|---|---|---|
| LeadSax | 257 | 37 | 220 | 0 | 0 | 0 | ✅ |
| Trumpet | 72 | 0 | 72 | 0 | 0 | 0 | ✅ |
| Piano | 288 | 0 | 288 | 0 | 0 | 0 | ✅ |
| Bass | 144 | 72 | 72 | 0 | 0 | 0 | ✅ |

`passes == True` on every voice: **0 untagged / 0 non-resolving / 0 strong
violations.**

---

## 5. Humanization + dual version

Grid-locked phase-2 = `-perfect`. Humanized in place via
`workflows.humanize.export_dual` (style `Jazz`, per-instrument DNA from the
registry), seed 20261023, re-validated + exported as `-humanized`.

Per-voice DNA (timing_sigma_ms / velocity_sigma / layback_ms) + measured stats:

| Voice | profile (ms/vel/lay) | shift mean | shift max | vel Δ |
|---|---|---|---|---|
| LeadSax | 8.0 / 7.0 / 1.0 | 5.45 | 23 | 5.50 |
| Trumpet | 7.0 / 8.0 / 4.0 | 6.61 | 16 | 6.40 |
| Piano | 6.0 / 5.0 / 0.0 | 4.24 | 14 | 3.77 |
| Bass | 10.0 / 6.0 / 8.0 | 9.52 | 26 | 4.47 |
| Drums | 2.0 / 4.0 / 0.0 | 1.37 | 5 | 3.07 |

Drums anchor (tightest, ±1.4 ticks), bass lays back (+9.5 ticks / 8 ms), lead
+ trumpet breathe in between — the expected role profile. Humanized off-grid =
**726 > 0** (jitter proof the humanizer ran); perfect off-grid = **0**.

---

## 6. Verification (real numbers)

| Metric | phase1 | perfect | humanized |
|---|---|---|---|
| bytes | 2319 | 9405 | 9293 |
| voice tracks | 1 | 5 | 5 |
| voice len (ticks) | 69120 | 69120 | 69120 |
| zero-drift | OK | OK | OK |
| duration | 72 s | 72 s | 72 s |
| total notes | 259 | 1185 | 1185 |
| pitched notes | 259 | 761 | 761 |
| **off-grid** | 256 (raw) | **0** | **726 (jitter)** |
| **harmony untagged/non-resolving/strong** | — (chromatic by design) | **0/0/0** | **0/0/0** (scale-only) |
| serial 12-pc fingerprint | ✅ all 12 | — | — |

- Perfect layer: 0 off-grid, 0/0/0 harmony — the compositional truth.
- Humanized: off-grid 726 > 0 (jitter ran), pitches unchanged (scale-only
  audit still 0/0/0 — jitter moves onsets, never pitches).
- Phase 1: chromatic 12-tone raw (all 12 pcs), off-grid by construction.

---

## 7. Audio mastering (genre target)

Style `Jazz` → `target_for_style` = **−14.0 LUFS**, true-peak ceiling −1 dBTP.
All three renders (perfect / humanized / phase1) mastered via
`sound.effects.mastering.master()` before Opus encode.

| Render | LUFS | dBTP | silence % | peak | duration |
|---|---|---|---|---|---|
| perfect | −14.01 | −1.0 | 5.47 | 0.884 | 76.09 s |
| humanized | −14.02 | −1.0 | 5.54 | 0.882 | 76.09 s |
| phase1 | −14.04 | −1.0 | 19.29 | 0.889 | 74.20 s |

All three hit the −14 LUFS target (Jazz) with true-peak −1.0 dBTP (the
ceiling, not a target — this is a full combo mix, so it saturates at the
ceiling). Silence ratios 5.5% (perfect/humanized — no mid-track gaps, only the
release tail past 72 s) and 19.3% (phase1 — a single sparse raw voice, by
design).

`Analysis/render_stats.json` + `Analysis/verify.json` hold the raw numbers.

---

## 8. Files

```
257-jazz-serial-bebop/
├── compose.py  render.py  verify.py
├── README.md  REPORT.md  index.html
├── MIDI/
│   ├── 257-jazz-serial-bebop-phase1.mid      + .provenance.json
│   ├── 257-jazz-serial-bebop-perfect.mid     + .provenance.json
│   └── 257-jazz-serial-bebop-humanized.mid   + .provenance.json
├── Audio/
│   ├── 257-jazz-serial-bebop-perfect.wav/.ogg
│   ├── 257-jazz-serial-bebop-humanized.wav/.ogg
│   └── 257-jazz-serial-bebop-phase1.wav/.ogg
└── Analysis/
    ├── grid_visualization.txt  summary.json  verify.json
    └── render_stats.json
```

## 9. Fixes applied this run

- **verify.py KeyError** (dict key `serial_all_12_pcs` vs assert `serial_ok`)
  → added `serial_ok` alias to the phase1 result dict.
- Humanized harmony audit runs **scale-only** (`chord_pcs_by_bar=None`) because
  onset jitter re-classifies notes across bar seams; pitch truth (in-scale) is
  what humanization preserves. Perfect layer runs the strict in-chord audit.
