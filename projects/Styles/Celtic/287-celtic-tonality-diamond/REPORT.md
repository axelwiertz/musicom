# REPORT — 287 Celtic Tonality Diamond

**Nightly composition job · 2026-11-05 · Method 131 TDRPC (abstract layer)**

## 1. Selection (LAYERED METHODOLOGY)

| | |
|---|---|
| Style | **Celtic** |
| Method | **131 — Tonality Diamond Ratio-Pool Composition (TDRPC)** |
| Layer | **abstract** (weekly ~1/7 cadence → abstract→concrete interpretation path) |
| Form | **intro-verse-chorus-verse-chorus-outro** (6 sections, 40 bars) |
| Key / mode | **D Mixolydian** — D E F# G A B C (PC set {2,4,6,7,9,11,0}) |
| Tempo | 112 BPM (reel), 4/4 |
| Seed | 20261105 |

Method 131 drawn from the **abstract** pool `{95,99,104,113,127,131,133}` on the
weekly cadence. Excluded from the concrete pool: AI-driven methods and the
last-7-days set `{31,21,11,38,36,117,40,25,18,95,98,69}`. The abstract layer
designs the ratio pool / hexad vocabulary / identity lattice / height curve; the
concrete layer realizes them as a D Mixolydian Celtic reel.

## 2. Method interpretation (abstract → concrete)

**Abstract layer — Harry Partch's tonality diamond D(7):** 13 just-intonation
ratios (odd limit 7), each carrying a Tenney height H(a/b)=log2(a·b) and cents:

| ratio | cents | H | nearest semi (from D) |
|---|---|---|---|
| 1/1 | 0.00 | 0.000 | 0 |
| 8/7 | 231.17 | 5.807 | 2 |
| 7/6 | 266.87 | 5.392 | 3 |
| 6/5 | 315.64 | 4.907 | 3 |
| 5/4 | 386.31 | 4.322 | 4 |
| 4/3 | 498.04 | 3.585 | 5 |
| 7/5 | 582.51 | 5.129 | 6 |
| 10/7 | 617.49 | 6.129 | 6 |
| 3/2 | 701.96 | 2.585 | 7 |
| 8/5 | 813.69 | 5.322 | 8 |
| 5/3 | 884.36 | 3.907 | 9 |
| 12/7 | 933.13 | 6.392 | 9 |
| 7/4 | 968.83 | 4.807 | 10 |

- **Hexads** (n=7, identities {1,3,5,7}, 4 tones each):
  - Oto(1) = {1, 8/7, 4/3, 8/5} · Uto(1) = {1, 5/4, 3/2, 7/4}
  - Oto(3) = {1, 6/5, 3/2, 12/7} · Uto(3) = {1, 7/6, 4/3, 5/3}
- **Identity lattice** common-tone counts (1-3, 3-5, 5-7): oto-oto = 1, oto-uto = 2 → smooth polarity flips with retained common tones.
- **Height curve** (tension arc): Intro H=0 → Verse H≈3.6 → Chorus H≈4.8 → Outro H=0 (cadence = return to the 1/1 nexus).

**Concrete realization:** the diamond's low-height otonality tones project to a
D Mixolydian scale. The **7/4 harmonic seventh** (968.8 c ≈ minor 7th) is the
diamond's signature — it is the Mixolydian b7 that gives Celtic melody its
colour. Ratios are realized nearest-12-TET with cents deviation recorded in
provenance (`provenance.json` → `diamond`).

**Chord map (identity walk, common-tone retention):**

| Chord | Root ratio (rel D) | H | Role |
|---|---|---|---|
| D (I) | 1/1 | 0.000 | identity 1 nexus (HOME) |
| Am (v) | 3/2 | 2.585 | identity 3 dominant fifth |
| G (IV) | 4/3 | 3.585 | subdominant (utonality) |
| C (bVII) | 7/4 | 4.807 | identity 7 harmonic seventh (TENSE) |

## 3. Progression (per section, 4-bar rotation; midpoint = section identity)

| Section | bars | rotation | midpoint (H) |
|---|---|---|---|
| Intro | 4 | D D G D | D (0.000) |
| Verse | 8 | D G C G | G (3.585) |
| Chorus | 8 | C G D C | G (3.585) |
| Verse2 | 8 | D Am G D | Am (2.585) |
| Chorus2 | 8 | C G D G | G (3.585) |
| Outro | 4 | G D G D | D (0.000) |

Cadence = bVII→I (C→D), the classic Mixolydian close, resolving to the 1/1 nexus.

## 4. Voices (from instrument registry)

| Voice | Instrument | GM program | channel |
|---|---|---|---|
| Fiddle | violin | 40 | 0 |
| Flute | flute | 73 | 1 |
| Guitar | steel_acoustic | 25 | 2 |
| Bass | acoustic_bass | 32 | 3 |
| Drums | drum_kit | 0 | 9 |

## 5. Two-phase architecture

- **Phase 1 (raw draft):** height-directed random walk over the 13 diamond
  ratios (drift toward each section's height target), nearest-12-TET pitch,
  jittered off-grid onsets. Single voice, no harmony. Exported as
  `-phase1.mid` with its own zero-drift gate + provenance (phase=1).
- **Phase 2 (musicom rules):** tiered pitch discipline (`classify_weight` +
  `ScaleQuantizer.tiered_quantize`) — strong beats snap scale+chord, weak beats
  snap scale; 16th-grid lock; voice-leading cap (leap ≤ 9); dedup; full 5-voice
  Celtic texture. Exported as dual versions (`-perfect.mid` + `-humanized.mid`).

## 6. Grid audit (perfect layer — pre-humanization)

| Voice | onsets | off-16th | off-8th |
|---|---|---|---|
| Fiddle | 228 | **0** | 101 (16th-note runs, on 16th grid) |
| Flute | 52 | **0** | 0 |
| Guitar | 320 | **0** | 0 |
| Bass | 160 | **0** | 0 |
| Drums | 361 | **0** | 64 (16th hats) |

**Verdict: 0 off-16th on every voice.** The 8th-grid "off" counts are the
idiomatic 16th-note reel subdivisions (still on the 16th grid), not drift.

## 7. Harmony audit (tiered, `workflows.pitch_audit.audit_voice`)

| Voice | total | untagged_out_of_scale | tagged_non_resolving | strong_violations | weak_in_scale | strong_ok |
|---|---|---|---|---|---|---|
| Fiddle | 228 | **0** | **0** | **0** | 197 | 31 |
| Flute | 52 | **0** | **0** | **0** | 0 | 52 |
| Guitar | 320 | **0** | **0** | **0** | 240 | 80 |
| Bass | 160 | **0** | **0** | **0** | 80 | 80 |

**Verdict: 0 untagged out-of-scale / 0 non-resolving / 0 strong violations on
every pitched voice.** All diatonic D Mixolydian — ornament path unused by
construction (no chromatic passing/neighbor tones were needed).

## 8. Humanization + dual-version export

`export_dual` (canonical), `hz_seed = 20261105`, style profile **celtic**
(timing 7 ms, velocity 6, layback 1 ms, phrase_corr 0.4). Per-instrument DNA:

| Voice | timing_ms | vel_sigma | layback_ms | mean abs shift (ticks) | max shift | vel delta |
|---|---|---|---|---|---|---|
| Fiddle | 7.0 | 6.0 | 1.0 | 3.85 | 14 | 4.80 |
| Flute | 7.0 | 7.0 | 1.0 | 3.69 | 11 | 4.50 |
| Guitar | 7.0 | 6.0 | 1.0 | 4.54 | 13 | 5.02 |
| Bass | 5.0 | 4.0 | **8.0** | **6.56** | 18 | 2.84 |
| Drums | 2.0 | 4.0 | 0.0 | **1.14** | 5 | 3.40 |

Drums anchor (tightest), bass lays back 8 ms — correct role DNA. Humanized
layer off-16th total = **958** (>0, proving the humanizer ran), perfect = 0.

## 9. Zero-drift

| artifact | zero-drift | length (ticks) |
|---|---|---|
| phase1 | ✓ | 76800 |
| perfect | ✓ | 76800 |
| humanized | ✓ | 76800 |

76800 ticks = 40 bars × 1920. All note tracks equal length; `validate()` passed
on both phases.

## 10. Render + mastering

All three MIDIs rendered FluidSynth (FluidR3_GM.sf2) → WAV → `master()` →
Opus OGG. Target = `target_for_style("celtic")` = **−14 LUFS**, −1 dBTP ceiling.

| version | duration | silence | RMS/s (mean) | integrated LUFS | true peak |
|---|---|---|---|---|---|
| phase1 | 88.32 s | 7.78% | — | −14.25 | −1.00 dBTP |
| perfect | 95.97 s | 9.59% | — | −14.06 | −1.00 dBTP |
| humanized | 95.97 s | 9.61% | — | −14.01 | −1.00 dBTP |

Silence < 10% (no mid-track gaps — the 7-9% is inter-note decay in a sparse
fiddle texture + reverb tail), LUFS ≈ target, true peak at the −1 dBTP ceiling.

## 11. Files

```
MIDI/287-celtic-tonality-diamond-phase1.mid          (2046 B)
MIDI/287-celtic-tonality-diamond-perfect.mid         (9539 B)
MIDI/287-celtic-tonality-diamond-humanized.mid       (9529 B)
MIDI/*.mid.provenance.json × 3
Audio/287-celtic-tonality-diamond-phase1.ogg         (703 KB)
Audio/287-celtic-tonality-diamond-perfect.ogg        (718 KB)
Audio/287-celtic-tonality-diamond-humanized.ogg      (716 KB)
Audio/*.wav × 3 (mastered)
Analysis/grid_visualization.txt
Analysis/summary.json
Analysis/render_stats.json
provenance.json  ·  README.md  ·  REPORT.md  ·  compose.py  ·  render.py
```

## 12. Fixes applied

None required — first-pass clean: grid PASS, harmony PASS, zero-drift on all
three, LUFS on target.
