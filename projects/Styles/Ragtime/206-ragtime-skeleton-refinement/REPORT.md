# 206-ragtime-skeleton-refinement — Composition Report

Date: 2026-09-26 (autonomous nightly composition job)
Style: **Ragtime** (solo-piano stride idiom, Scott Joplin tradition)
Method: **001 Skeleton-First Refinement**
Layer: **concrete**

## 1. Concept & Selection

| Field | Value |
|---|---|
| Project | 206-ragtime-skeleton-refinement |
| Genre | Ragtime |
| Method | **001 Skeleton-First Refinement** (Rules-Based) |
| Layer | **concrete** |
| Key | C major (pitch classes {0,2,4,5,7,9,11}) |
| Tempo / meter | 120 BPM, 4/4, 480 ticks/beat |
| Form | Intro(4) \| A(8) \| B(8) \| A2(8) \| Trio(8) \| Coda(4) = **40 bars** (82 s) |
| Instrumentation | Solo piano — 3 roles on one instrument |

**Layer cadence**: last abstract composition job was **095 CTC** (project
105, 2026-09-24). Tonight continues the **concrete** cadence (6-of-7 nights).

**Methods excluded (used in last 7 days)**: 016 (groove-locked), 019
(L-System), 025 (Sieve), 026 (DPSM phase-shift), 040 (Perlin), 048 (RBMPD),
069 (Christoffel), 075 (SOM-C), 095 (CTC, abstract), ABS-002 (subset walker).
Method 001 was last used 2026-09-15 (096-trap-skeleton-seoul) → outside the
7-day window, valid selection.

## 2. Method — Skeleton-First Refinement (001)

Rules-Based, Strict (static scale/key), Grid-Locked, Macro/Form, O(N).
"Baseline form-first drafting: establishes a deterministic structural
skeleton before micro-variations."

Implementation here:

1. **Skeleton (deep structure)** — three deterministic layers decided before
   any note is written:
   - **Form skeleton**: 6 sections (40 bars), ragtime multi-strain layout.
   - **Harmonic skeleton**: a fixed diatonic chord progression (one chord per
     bar, below), I–IV–V–I + ii–V turnarounds.
   - **Melodic skeleton**: a scale-degree *structural line* — one degree per
     half-bar — giving the deep-register contour of every strain (a
     "cantus-firmus"-like cantus line that is later refined).
2. **Refinement (surface)** — Phase 2 elaborates the skeleton:
   - each structural degree is snapped to the **nearest chord tone** of its
     bar (harmony realization),
   - diminished into a **syncopated 16th figure** (neighbor-tone alternation,
     3-3-2 / off-beat masks),
   - onsets snapped to the **16th grid**,
   - and the left-hand **stride bass** + **chord comp** fill out the texture.

## 3. Voices & Instruments (from registry)

All three roles use `PIANO` from the instrument registry
(`instrument_registry.PIANO` → GM program 1, "Acoustic Grand Piano",
range A0–C8). A solo-piano rag is authentic to the genre; the MIDI splits the
two hands into separate voices for DAW clarity.

| Voice | Channel | Program | Role |
|---|---|---|---|
| Melody | 0 | PIANO (1) | right-hand syncopated lead |
| Bass | 1 | PIANO (1) | left-hand stride root, beats 1 & 3 |
| Comp | 2 | PIANO (1) | left-hand chord stabs, beats 2 & 4 |

## 4. Harmonic Skeleton (full progression, one chord per bar)

All chords are **diatonic to C major** (chord tones ⊆ scale), so the harmony
audit has real teeth (chord-tone vs scale membership) while every note is
guaranteed in-key.

| Section | Bars | Progression |
|---|---|---|
| Intro | 1–4 | G7 G7 G7 G7 |
| A | 5–12 | C Cmaj7 Am Dm7 G7 C F G7 |
| B | 13–20 | F Fmaj7 Dm G7 Em7 Am Dm7 G7 |
| A2 | 21–28 | C Cmaj7 Am Dm7 G7 C G7 C |
| Trio | 29–36 | F F Dm G7 C Am F G7 |
| Coda | 37–40 | C G7 C C |

Chord PC sets: C{0,4,7}, Cmaj7{0,4,7,11}, Dm{2,5,9}, Dm7{2,5,9,0},
Em7{4,7,11,2}, F{5,9,0}, Fmaj7{5,9,0,4}, G7{7,11,2,5}, Am{9,0,4}, Am7{9,0,4,7}.

## 5. Two-phase architecture

- **Phase 1** (`-phase1.mid`): raw generative draft — single `Raw_Melody`
  voice. The skeleton's scale-degree line is read out as diatonic pitches with
  **unquantized micro-timing** (±70-tick jitter around the half-beat) and
  register folding. **No harmony** (no chord snapping, no bass, no comp). Own
  zero-drift gate passed. 78/80 onsets off-grid (raw character preserved).
- **Phase 2** (`.mid`): musicom rules — 16th-grid snap, per-bar chord-tone
  quantization, syncopated elaboration, stride bass + chord comp (full piano
  texture). Own zero-drift gate passed.

## 6. Verification (real numbers)

### Grid audit (phase 2, per voice — must be 0 off-grid 16th)

| Voice | Onsets | Off-grid 16th | Off-grid 8th |
|---|---|---|---|
| Melody | 280 | **0** | 80 (16th syncopation — expected) |
| Bass | 80 | **0** | 0 |
| Comp | 240 | **0** | 0 |

**Verdict: PASS — 0 onsets off the 16th grid.** (Melody's 80 "off-8th" onsets
are the intended 16th-note syncopation landing on odd 16ths.)

### Harmony audit (phase 2, per voice — must be 0 out-of-key AND 0 out-of-chord)

| Voice | Out-of-scale | Out-of-chord |
|---|---|---|
| Melody | **0** | **0** |
| Bass | **0** | **0** |
| Comp | **0** | **0** |

**Verdict: PASS — every pitched note is in C major and a chord tone of its bar.**

### Zero-drift

All 3 phase-2 tracks length = **76800 ticks** (equal) → **PASS**. Phase-1
single track also equal-length.

### Render / audio profile

| Metric | Value |
|---|---|
| Duration | 82.48 s (40 bars @ 120 BPM + reverb tail) |
| Peak | 0.874 (after volume normalize) |
| RMS | 0.139 |
| Silence ratio | 3.4% |
| Mid-track silent gaps | 0 |
| Active seconds | 81 / 83 |

Silence is only the reverb tail after the final C-major cadence — no
mid-track gaps. Render pipeline: FluidSynth CLI (`-ni -g 1.2`, FluidR3_GM.sf2)
→ WAV → `volume=2.85` normalize → ffmpeg libopus 128k OGG.

## 7. Files

| File | Size |
|---|---|
| `MIDI/206-ragtime-skeleton-refinement.mid` | 5103 B |
| `MIDI/206-ragtime-skeleton-refinement-phase1.mid` | 832 B |
| `Audio/206-ragtime-skeleton-refinement.wav` | ~14 MB |
| `Audio/206-ragtime-skeleton-refinement.ogg` | ~1.6 MB |
| `Analysis/grid_visualization.txt` | 3601 B |
| `Analysis/summary.json` | audit verdicts |
| `Analysis/render_stats.json` | audio profile |

## 8. Fixes applied this run

- None required post-generation: grid, harmony and zero-drift all passed on
  first export. One normalization fix: the environment's ffmpeg lacks the
  `peaknorm` filter → fell back to `volume=2.85` (peak 0.31 → 0.87), per the
  documented peaknorm-missing fallback.
