# 247 — Metal Fourier Spectrum

**Method 113 — Pitch-Class Fourier Spectrum Composition (PCFSC)** · layer **abstract** · paradigm **Rules-Based**

Autonomous nightly composition job · 2026-10-16 · seed 247.

---

## 1. Concept

| Field | Value |
|---|---|
| Style | Metal |
| Method | 113 Pitch-Class Fourier Spectrum Composition (PCFSC) |
| Layer | **abstract** (abstract→concrete interpretation path exercised) |
| Paradigm | Rules-Based |
| Form | head-solos-head → Head1(8) · Solo1(8) · Solo2(8) · Head2(8) = 32 bars |
| Key | E minor (tonic pc 4) |
| Tempo | 140 BPM · 4/4 · 480 TPB · BAR = 1920 · 16th grid = 120 ticks |
| Length | 32 bars · ~57 s |

## 2. Method essence (PCFSC, Amiot 2016)

A pitch-class *pool* (subset of ℤ₁₂) maps to 12 Fourier coefficients
`f_A(k) = Σ_{a∈A} e^{2πika/12}`. **Magnitude |f_A(k)| = chord/scale quality**;
**phase arg f_A(k) = tonic position** (transposition = phase rotation; major/
minor triads are magnitude-twins — mode lives in phase). Composition = a
trajectory through Fourier space: per-section target quality profile + designed
phase walk → pool sequence + tension curve.

## 3. Fourier pools (per section) — measured spectra

| Section | Pool | \|f5\| | \|f7\| | \|f6\| | \|f3\| | \|f4\| | Role |
|---|---|---|---|---|---|---|---|
| Head1 | E natural minor {0,2,4,6,7,9,11} | **3.7321** | **3.7321** | 1.0 | 1.0 | 1.0 | diatonic peak k=5,7 → HOME |
| Solo1 | E harmonic minor {0,3,4,6,7,9,11} | 1.9319 | 1.9319 | 1.0 | 2.2361 | 2.6458 | leading tone D♯ → LIFT |
| Solo2 | E half-whole octatonic {1,2,4,5,7,8,10,11} | 0.0 | 0.0 | 0.0 | 0.0 | **4.0** | energy only k=4,8 (dim7 lattice) → TENSE |
| Head2 | E natural minor (HOME) | 3.7321 | 3.7321 | 1.0 | 1.0 | 1.0 | return to anchor → resolution |

Head1's |f5|=|f7|=2+√3 is the exact maximally-even maximum (verified). Solo2's
|f4|=4.0 (energy only at k=4,8) is the exact octatonic dim7 lattice signature.

## 4. Fourier tension curve (TIV distance)

| Transition | Tension |
|---|---|
| Head1 → Solo1 | 15.19 |
| Solo1 → Solo2 | **26.49** (peak) |
| Solo2 → Head2 | 24.00 |
| Head2 → loop | 0.00 (HOME) |

## 5. Ensemble (instrument registry)

| Voice | Instrument | GM program | Channel | Role |
|---|---|---|---|---|
| Lead | Overdriven Guitar | 29 | 0 | chord-tone arpeggio lead / sweep solos |
| Rhythm | Overdriven Guitar | 29 | 1 | power chords (5th/tritone/octave), chug |
| Bass | Electric Bass | 33 | 2 | root lock, 8th→16th |
| Drums | Drum Kit | 0 | 9 | metal kit (double-kick in solos) |

## 6. Full chord progression (32 bars)

```
Head1  (E natural minor):  Em Em C G D C D Em          (aeolian cadence bVI-bVII-i)
Solo1  (E harmonic minor): Em Am B Em C F#dim B Em     (leading-tone V)
Solo2  (E half-whole oct): Em Edim7 Fdim7 Em Edim7 Bdim Fdim7 Em   (dim7 lattice)
Head2  (E natural minor):  Em Em C G D C D Em          (HOME)
```
Every chord is a subset of its section pool (⇒ chord-tone quantization = in-pool).

## 7. Verification — grid + harmony audit (PRE-humanization)

| Voice | notes | off-16th | off-8th | out-of-scale | out-of-chord |
|---|---|---|---|---|---|
| Lead | 448 | **0** | 192 | **0** | **0** |
| Rhythm | 1152 | **0** | 384 | **0** | **0** |
| Bass | 384 | **0** | 128 | **0** | **0** |
| Drums | 676 | **0** | 192 | — | — |

- Grid verdict: **0 off-grid (16th) across all pitched voices** ✓
- Harmony verdict: **0 out-of-scale, 0 out-of-chord** ✓
- (off-8th counts are by design — 16th-note figures are the metal grid.)

## 8. Humanization (always-on, seeded, style-derived)

Style `metal` (falls through `profile_for_style` to the default base, since
"metal" has no entry in `STYLE_HUMANIZE`; per-instrument DNA supplies role
tuning). Master seed = 247; per-voice child seed = 247·101 + row.

| Voice | seed | timing σ (ms) | vel σ | layback (ms) | mean shift (t) | max shift (t) | vel Δ |
|---|---|---|---|---|---|---|---|
| Lead | 24947 | 6.0 | 6.0 | 1.0 | 4.7 | 15 | 4.8 |
| Rhythm | 24948 | 6.0 | 6.0 | 1.0 | 5.1 | 20 | 4.8 |
| Bass | 24949 | 5.0 | 4.0 | 8.0 | 8.1 | 20 | 3.3 |
| Drums | 24950 | 2.0 | 4.0 | 0.0 | **1.4** | 6 | 3.1 |

Drums anchor (σ 2 ms, mean 1.4 t); bass lays back (8 ms → mean 8.1 t). Readback
proof: 1826/1984 pitched onsets off-grid after humanization.

## 9. Zero-drift

- Phase 1: ✅ validate() passed · 1 track × 61440 ticks.
- Phase 2: ✅ validate() passed · 4 tracks × 61440 ticks, equal (readback).

## 10. Render + master (FluidSynth → LUFS → Opus)

| Item | Phase 2 | Phase 1 |
|---|---|---|
| SoundFont | FluidR3_GM.sf2 | FluidR3_GM.sf2 |
| Integrated LUFS | **−11.13** | −12.24 |
| True peak | −1.0 dBTP | −1.0 dBTP |
| Silence ratio | 0.0386 (3.9%) | 0.0443 (4.4%) |
| Duration | 57.36 s | 56.92 s |

Loudness: `target_for_style("metal")` → −14.0 (fallback; "metal" is not a key in
`GENRE_LUFS`). Metal is a loud-first rock subgenre, so the piece was mastered to
**−11.0 (rock target)**; measured −11.13 LUFS, −1.0 dBTP ceiling. Silence < 5%
is trailing reverb tail only — no mid-track gaps (continuous metal texture).

## 11. Files

```
MIDI/247-metal-fourier-spectrum.mid          (19431 B)  phase-2 rules
MIDI/247-metal-fourier-spectrum-phase1.mid   (2247 B)   phase-1 raw draft
Audio/247-metal-fourier-spectrum.wav         (10.1 MB)  mastered −11 LUFS
Audio/247-metal-fourier-spectrum-phase1.wav  (10.0 MB)
Audio/247-metal-fourier-spectrum.ogg         (995 KB)   Opus listen
Audio/247-metal-fourier-spectrum-phase1.ogg  (1.09 MB)
Analysis/summary.json                        spectra/tension/audit/humanize
Analysis/grid_visualization.txt              onset grid
Analysis/render_stats.json                   LUFS/silence/verify
MIDI/*.provenance.json                       per-artifact sidecars (phase 1 & 2)
README.md · index.html · compose.py · render.py
```

## 12. Fixes applied this run

1. **Duplicate section names** ("Head" twice in head-solos-head) collapsed the
   matrix to 3 columns → disambiguated to Head1/Head2.
2. **Diminished "power chord" bug**: rhythm used root+perfect-5th for all
   chords, but the Solo2 dim7 chords contain a *tritone* (root+6), not a 5th →
   64 out-of-scale / 96 out-of-chord. Fixed: derive the upper interval from the
   chord's actual pc set (5th → tritone → minor 3rd fallback). Every rhythm tone
   is now a chord tone (0/0).
3. **Zero-drift 4–12-tick shortfall** after humanization: `len_ticks()` = max
   `end_tick`, and the humanizer can pull a note's tail inward, leaving no event
   pinned at the section end. Fixed: always append a silent terminal landmark
   `(pitch 0, end=length)` so every cell ends exactly at the section length
   (passes through the humanizer untouched).
4. **Drums catastrophic humanization** (mean 443 t, max 1802 t): drums events
   were built kick-block/snare-block/hat-block (unsorted), so the humanizer's
   forward-clamp (which assumes ascending onsets) mangled them. Fixed: sort all
   events by onset before filling cells.
5. **18 readback out-of-chord notes** (0.9%): downbeat notes jittered ≤20 ticks
   early across a bar line, landing in the previous bar's chord. Added a
   post-humanize bar-line guard (index-matched to pre-humanize events, since the
   humanizer preserves order/pitch) that snaps straddled onsets back onto their
   intended downbeat. Readback out-of-chord now **0**.

## 13. Voice-leading note

`VoiceLeadingRules(classical)` flags 64 parallel-motion violations across the
rhythm power-chord voicings. This is **idiomatic metal** (parallel power chords
are the genre texture) — reported informational, intentionally not "corrected".
