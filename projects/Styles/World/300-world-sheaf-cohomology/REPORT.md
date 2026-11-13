# REPORT — 300 World Sheaf Cohomology

**Nightly composition job (ID 1fc3fd65d359) · 2026-11-12 · Method 134 (abstract layer)**

## 1. Selection (LAYERED METHODOLOGY)

| Field | Value |
|---|---|
| Style | **World** |
| Method | **134 — Cellular Sheaf Cohomology Composition (CSCC)** (Rules-Based) |
| **Layer** | **abstract** (weekly ~1/7 cadence → abstract→concrete interpretation path) |
| Form | **intro-verse-chorus-verse-chorus-outro** (6 sections, 40 bars) |
| Key / mode | **D natural minor** — D E F G A B♭ C (PC set {0,2,4,5,7,9,10}) |
| Tempo | 100 BPM, 4/4 |
| Length | 40 bars × 1920 = 76800 ticks ≈ 96 s |
| Seed | 20261112 · humanize seed 263394756 · form seed 202611127 |

Method 134 drawn from the **abstract** pool `{95,99,104,113,127,133,134,139}` on
the weekly cadence (last abstract was 287 / Method 131 on 11-05). Excluded from
the concrete pool: the last-7-days set `{1,7,13,15,32,41,45,53,120}`. The
abstract layer builds a cellular sheaf and computes real cohomology; the
concrete layer realizes each section's harmonic state (stalk) as a World texture.

## 2. Method interpretation (abstract → concrete)

**Abstract layer — a cellular sheaf over the section graph.** The 6 sections are
the vertices of a cycle C6; each vertex carries a **stalk** = a 4-dimensional
pitch-class indicator vector (one coordinate per chord tone of that section's
chord). Each of the 6 seams (edges) carries a **common-tone gluing** restriction
map (recipe R1): the seam demands that the two adjacent sections agree on their
shared pitch classes.

| Section | Chord (stalk) | pcs | common w/ next |
|---|---|---|---|
| Intro (v0) | Dm7 | {0,2,5,9} | {2,5} |
| Verse (v1) | Gm7 | {2,5,7,10} | {2,5,10} |
| Chorus (v2) | Bbmaj7 | {2,5,9,10} | {5,9} |
| Verse2 (v3) | Fmaj7 | {0,4,5,9} | {5,9} |
| Chorus2 (v4) | Bbmaj7 | {2,5,9,10} | {2,5,9} |
| Outro (v5) | Dm7 | {0,2,5,9} | {0,2,5,9} (identity) |

**Cohomology (exact Fraction elimination):**

| quantity | value |
|---|---|
| Σ d_v (vertex stalks) | 24 |
| Σ d_e (seam stalks) | 16 |
| rank δ | 15 |
| **dim H⁰ (coherence budget)** | **9** |
| **dim H¹ (rigidity)** | **1** |
| Euler–Poincaré | 9 − 1 = 8 = 24 − 16 ✓ |
| holonomy (cycle) | identity T₀ — loop closes, Outro returns to Intro |
| spanning trees τ(C6) | 6 (six cadence-cut choices) |

**Tension grammar** (§3.6): seam demands `b` encode the arc
`LIFT(+2) → LIFT(+1) → relax(−1) → LIFT(+1) → RELEASE(−3) → HOME(0)` on each
seam's shared pcs. The least-squares repair residual is **0.0 at every seam** —
the common-tone sheaf admits a global harmonic section that honours the entire
demand arc, so the loop carries zero harmonic strain (the single H¹ = 1
obstruction is the one degree of rigidity a spanning-tree cadence cut removes).
The **section lift** `[0,2,3,2,3,0]` (cumulative register push) is therefore the
driver of the concrete layer's register/density arc.

**Concrete realization:** each stalk's chord tones project to D natural minor;
the lift arc moves the shakuhachi lead register up (Intro 57→Chorus 63+) and
back down (Outro), and gates the koto 8th-note density + taiko fills.

## 3. Progression (per section; one harmonic state per section)

| Section | bars | chord | role |
|---|---|---|---|
| Intro | 4 | Dm7 (i7) | HOME |
| Verse | 8 | Gm7 (iv7) | LIFT |
| Chorus | 8 | Bbmaj7 (VI maj7) | TENSE (relative-major lift) |
| Verse2 | 8 | Fmaj7 (III maj7) | relax |
| Chorus2 | 8 | Bbmaj7 (VI maj7) | TENSE (second peak) |
| Outro | 4 | Dm7 (i7) | HOME (cadence return) |

## 4. Voices (instrument registry)

| Voice | Instrument | GM program | channel | role |
|---|---|---|---|---|
| Lead | Shakuhachi | 77 | 0 | stalk-walk melody |
| Bass | Acoustic Bass | 32 | 1 | root/fifth |
| Drone | Sitar | 104 | 2 | sustained chord tones |
| Koto | Koto | 107 | 3 | plucked 8th arpeggio |
| Drums | Drum Kit | — | 9 | taiko-flavour kick+toms |

## 5. Two-phase architecture

- **Phase 1** (`-phase1.mid`): raw single-voice chromatic walk pulled toward
  each section's chord tones (the stalk), off-grid onset jitter, unquantized
  pitch, no harmony. **312 / 320 onsets off the 16th grid** — deliberately raw.
- **Phase 2** (`-perfect.mid` + `-humanized.mid`): 8th-grid lock → tiered snap
  (`classify_weight` + `ScaleQuantizer.tiered_quantize`: strong beat → chord
  tone, weak → D-minor scale tone) → full 5-voice World texture → zero-drift
  landmark → `validate()` → `export_dual`.

## 6. Grid audit (perfect layer — pre-humanization)

Every pitched voice: **0 off-grid** on both 16th (120) and 8th (240).

| Voice | onsets | off-16th | off-8th |
|---|---|---|---|
| Lead | 318 | **0** | **0** |
| Bass | 80 | **0** | **0** |
| Drone | 368 | **0** | **0** |
| Koto | 224 | **0** | **0** |

## 7. Harmony audit (tiered, `workflows.pitch_audit.audit_voice`)

| Voice | total | strong_ok | weak_in_scale | untagged_out | non_resolving | strong_viol |
|---|---|---|---|---|---|---|
| Lead | 318 | 79 | 239 | **0** | **0** | **0** |
| Bass | 80 | 80 | 0 | **0** | **0** | **0** |
| Drone | 368 | 368 | 0 | **0** | **0** | **0** |
| Koto | 224 | 80 | 144 | **0** | **0** | **0** |

**Verdict: 0 untagged out-of-scale / 0 non-resolving ornaments / 0 strong
violations on every pitched voice.** Pure diatonic D natural minor — the
chromatic-ornament path was unused by construction (drone/bass/koto stay
chromatic-free; the lead carries no tagged ornaments).

## 8. Humanization + dual-version export

`export_dual` (canonical), `hz_seed = 263394756`, style profile **world**
(timing 7 ms, velocity 6, layback 1 ms, phrase_corr 0.4). Per-instrument DNA:

| Voice | timing σ (ms) | layback (ms) | mean abs shift (ticks) | max shift | vel δ |
|---|---|---|---|---|---|
| Lead | 7.0 | 1 | 3.69 | 14 | 4.84 |
| Drone | 7.0 | 1 | 5.35 | 14 | 4.77 |
| Koto | 7.0 | 1 | 3.86 | 17 | 4.77 |
| Bass | 5.0 | **8** | **6.83** | 12 | 2.70 |
| Drums | 2.0 | **0** | **0.99** | 3 | 3.45 |

Drums anchor (tightest, 0.99 ticks), bass lays back 8 ms — correct role DNA.
Humanized layer off-16th = **1092** (>0, humanizer ran), perfect = 0.

## 9. Zero-drift

| artifact | zero-drift | length (ticks) |
|---|---|---|
| phase1 | ✓ | 76800 |
| perfect | ✓ | 76800 (5 voice tracks) |
| humanized | ✓ | 76800 (5 voice tracks) |

76800 ticks = 40 bars × 1920. `validate()` passed on both phases; mido readback
confirms all note tracks equal length.

## 10. Render + mastering

All three MIDIs rendered FluidSynth (FluidR3_GM.sf2, `-R no -C no`) → WAV →
`master()` → Opus OGG. Target = `target_for_style("world")` = **−14 LUFS**,
−1 dBTP ceiling. (See `Audio/master_stats.json`.)

## 11. Files

```
300-world-sheaf-cohomology/
├── compose.py / render_audio.py / verify.py
├── README.md / REPORT.md / index.html
├── MIDI/   300-…-phase1.mid / -perfect.mid / -humanized.mid (+ provenance ×3)
├── Audio/  300-…-perfect.ogg / -humanized.ogg / -phase1.ogg (+ .wav, master_stats.json)
└── Analysis/ grid_visualization.txt / manifest.json / readback.json
```

## 12. Fixes applied

1. `pick_form("world")` returned the 6-section
   `intro-verse-chorus-verse-chorus-outro` form (not the 4-section head-solos-head
   used by the first draft); the sheaf, section-chord arc, and tension arc were
   generalized to 6 sections (C6 cycle).
2. Lead grid-lock could round a note onset up to the section boundary (`bar` =
   N_BARS, `KeyError`); added a `start_tick >= span` guard and `bar` clamp.
3. Voice→row mismatch: `add_voice` order (Lead,Koto,Drone,Bass,Drums) did not
   match the row-filling order, so the koto arpeggio rendered with the bass
   timbre and vice-versa. Reordered `VOICES` to (Lead,Bass,Drone,Koto,Drums) so
   each role's program matches its content.

## Layer: abstract

Method 134 (Cellular Sheaf Cohomology Composition) is an **abstract** method —
it designs the harmonic *structure* (stalks, restriction maps, cohomology,
cadence cuts) which the concrete layer then realizes as a D natural minor World
piece. The abstract layer produced verified numbers: dim H⁰ = 9, dim H¹ = 1,
rank δ = 15, Euler–Poincaré 9−1=8, holonomy identity, τ(C6) = 6.
