# REPORT — 289 Bossa Nova Motivic Transforms

**Nightly composition job · 2026-11-06 · Method 013 (concrete layer)**

## 1. Selection (LAYERED METHODOLOGY)

| | |
|---|---|
| Style | **BossaNova** (46 candidate genre folders) |
| Method | **013 — Inversion / Retrograde Transform** |
| Layer | **concrete** (roll 0.649 → concrete path, ~6/7 cadence) |
| Form | **intro-a-a-b-a** (5 sections, 36 bars) — from `pick_form("BossaNova")` |
| Key / mode | **F major** — F G A Bb C D E (PC set {5,7,9,10,0,2,4}) |
| Tempo | 120 BPM, 4/4 (480 TPB, BAR = 1920) |
| Seed | 20261106 |

Concrete pool = 95 methods (range 1–136 minus abstract {95,99,104,113,127,131,133},
AI-driven set, and last-7-days {117,95,36,38,98,11,69,21,18,31,131,48,40,25}).
Method 013 drawn at random.

## 2. Method interpretation (concrete — strict geometric transforms)

Method 013 is **classic motivic permutation via strict geometric transforms**.
One 8-note pitch motif (scale degrees in F major) is the sole melodic DNA; each
section realizes a different permutation of it:

| form | degree contour | pitches (F major) | section |
|---|---|---|---|
| Prime (P) | [0,1,3,2,4,2,1,0] | F G Bb A C A G F | Intro · A1 · A3 |
| Retrograde (R) | [0,1,2,4,2,3,1,0] | F G A C A Bb G F | A2 |
| Inversion (I) | [4,3,1,2,0,2,3,4] | C Bb G A F A Bb C | B |
| Retro-Inv. (RI) | [4,3,2,0,2,1,3,4] | C Bb A F A G Bb C | (unused) |

- **Retrograde** = reversed degree sequence (mirror in time).
- **Inversion** = mirrored around degree axis 2.0 (mirror in pitch space).
- Section transform map: **Intro=P · A1=P · A2=R · B=I · A3=P** (recapitulation
  returns to Prime).

**Rhythm**: the motif sits on the **bossa nova anticipation figure**
(16th offsets 0·3·6·8·11·14), the classic syncopated "clave" of Bossa Nova.

## 3. Progression (per section, 4-bar rotation; midpoint = section identity)

| Section | bars | rotation | midpoint |
|---|---|---|---|
| Intro | 4 | Fmaj7 · Bbmaj7 · Gm7 · C7 | Bbmaj7 |
| A1 | 8 | Fmaj7 · Dm7 · Gm7 · C7 | Dm7 |
| A2 | 8 | Fmaj7 · Dm7 · Gm7 · C7 | Dm7 |
| B | 8 | Bbmaj7 · Gm7 · Am7 · Dm7 | Gm7 |
| A3 | 8 | Fmaj7 · Dm7 · Gm7 · C7 | Dm7 |

Classic bossa nova **I–vi–ii–V** cycle (Fmaj7–Dm7–Gm7–C7) with an IV-region
contrast (Bbmaj7) in the B section. Midpoint roots `Bbmaj7 Dm7 Dm7 Gm7 Dm7` —
varied, no bar-0 tonic monotony.

## 4. Voices (from instrument registry)

| Voice | Instrument | GM program | channel | role |
|---|---|---|---|---|
| Flute | flute | 73 | 0 | lead melody (motif) |
| Guitar | acoustic_guitar (nylon) | 24 | 1 | bossa comp rhythm |
| Rhodes | rhodes | 4 | 2 | chord pad |
| Bass | acoustic_bass | 32 | 3 | root-5th walk |
| Drums | drum_kit | 0 | 9 | bossa kit |

## 5. Two-phase architecture

- **Phase 1 (`-phase1.mid`)**: single-voice raw draft — the transformed motif
  laid on the bossa anticipation rhythm with Gaussian-jittered **off-grid**
  onsets, random octave drift, no chord context, no harmony. Exported with its
  own zero-drift gate + provenance (phase=1).
- **Phase 2 (`-perfect.mid` / `-humanized.mid`)**: musicom rules post-process —
  grid-lock to 16th (120 ticks) → **tiered pitch discipline**
  (`classify_weight` + `ScaleQuantizer.tiered_quantize`: strong beats snap
  scale-then-chord, weak beats snap scale only) → pc-preserving octave
  normalize into flute range → voice-leading cap (leap ≤ 9) → dedup → full
  5-voice Bossa Nova texture.

## 6. Grid audit (perfect layer — pre-humanization)

| Voice | onsets | off-16th | off-8th |
|---|---|---|---|
| Flute | 204 | **0** | 68 (idiomatic 16th syncopation) |
| Guitar | 528 | **0** | 0 |
| Rhodes | 144 | **0** | 0 |
| Bass | 100 | **0** | 0 |
| Drums | 432 | **0** | 0 |

**Verdict: 0 off-16th on every voice.** The flute's 68 off-8th are the idiomatic
bossa 16th-note anticipations (still on the 16th grid), not drift.

## 7. Harmony audit (tiered, `workflows.pitch_audit.audit_voice`)

| Voice | total | untagged_out_of_scale | tagged_non_resolving | strong_violations | weak_in_scale | strong_ok |
|---|---|---|---|---|---|---|
| Flute | 204 | **0** | **0** | **0** | 135 | 69 |
| Guitar | 528 | **0** | **0** | **0** | 256 | 272 |
| Rhodes | 144 | **0** | **0** | **0** | 0 | 144 |
| Bass | 100 | **0** | **0** | **0** | 32 | 68 |

**Verdict: 0 untagged / 0 non-resolving / 0 strong violations on every pitched
voice.** All diatonic F major; the chromatic-ornament path was unused by
construction (no tagged passing/neighbor tones needed).

## 8. Humanization + dual-version export

`export_dual` (canonical), `hz_seed = 20261106`, style profile **bossa**
(timing 7 ms, velocity 6, layback 2 ms, phrase_corr 0.4). Per-instrument DNA:

| Voice | timing_ms | vel_sigma | layback_ms | mean abs shift (ticks) | max shift | vel delta |
|---|---|---|---|---|---|---|
| Flute | 7.0 | 7.0 | 2.0 | 4.93 | 17 | 5.76 |
| Guitar | 7.0 | 6.0 | 2.0 | 4.96 | 20 | 5.18 |
| Rhodes | 7.0 | 5.0 | 2.0 | 5.99 | 18 | 3.98 |
| Bass | 5.0 | 4.0 | **8.0** | **7.10** | 17 | 3.43 |
| Drums | 2.0 | 4.0 | 0.0 | **1.28** | 5 | 3.07 |

Drums anchor (tightest), bass lays back 8 ms — correct role DNA. Humanized
layer off-16th total = **1236** (>0, proving the humanizer ran; pitched = 915),
perfect = 0.

## 9. Zero-drift

| artifact | zero-drift | length (ticks) |
|---|---|---|
| phase1 | ✓ | 69120 |
| perfect | ✓ | 69120 |
| humanized | ✓ | 69120 |

69120 ticks = 36 bars × 1920. All note tracks equal length; `validate()` passed
on both phases.

## 10. Render + mastering

All three MIDIs rendered FluidSynth (FluidR3_GM.sf2) → WAV → `master()` → Opus
OGG. Target = `target_for_style("BossaNova")` = **−14 LUFS** (no explicit bossa
entry in `GENRE_LUFS`; falls back to −14, matching jazz — correct for bossa
nova's gentle acoustic character), −1 dBTP ceiling.

| version | duration | silence | RMS/s (mean) | integrated LUFS | true peak |
|---|---|---|---|---|---|
| phase1 | 74.20 s | 5.76% | 0.062 | −14.02 | −1.00 dBTP |
| perfect | 74.96 s | 4.31% | 0.106 | −14.02 | −1.00 dBTP |
| humanized | 75.21 s | 4.64% | 0.105 | −14.05 | −1.00 dBTP |

Silence < 6% (no mid-track gaps — the small ratio is inter-note decay + the
outro tail), LUFS ≈ target, true peak at the −1 dBTP ceiling.

## 11. Files

```
MIDI/289-bossanova-motivic-transforms-phase1.mid          (1799 B)
MIDI/289-bossanova-motivic-transforms-perfect.mid         (10780 B)
MIDI/289-bossanova-motivic-transforms-humanized.mid       (10758 B)
MIDI/*.mid.provenance.json × 3
Audio/289-bossanova-motivic-transforms-phase1.ogg         (647 KB)
Audio/289-bossanova-motivic-transforms-perfect.ogg        (534 KB)
Audio/289-bossanova-motivic-transforms-humanized.ogg      (539 KB)
Audio/*.wav × 3 (mastered, ~13 MB each)
Analysis/grid_visualization.txt
Analysis/summary.json
Analysis/render_stats.json
provenance.json  ·  README.md  ·  REPORT.md  ·  index.html  ·  compose.py  ·  render.py
```

## 12. Fixes applied

1. **Register-clamp pitch-class bug**: the original `min(96, max(60, p))` clamp
   could change a note's pitch class — octave-jittered phase-1 notes below 60
   (e.g. G3=55) were hard-clamped to C4=60, producing 3 strong-beat
   out-of-chord notes (pitch 60 vs Gm7). Fixed with a **pc-preserving octave
   normalize** (`while p<60: p+=12`) plus chord-tone lists restricted to the
   flute range 60–96. Strong violations: 3 → 0.
2. **Empty accompaniment voices**: the `acc` dict was filled but never written
   to the matrix (missing `set_unit` loop), leaving Guitar/Rhodes/Bass empty.
   Added the `for (r,s),evs in acc.items(): phase2.set_unit(...)` loop.
   Accompaniment onsets: 0 → 528/144/100.
