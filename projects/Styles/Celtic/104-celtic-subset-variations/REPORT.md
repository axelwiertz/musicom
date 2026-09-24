# REPORT — 104-celtic-subset-variations

**Project:** 104-celtic-subset-variations
**Style:** Celtic
**Method:** ABS-002 Subset Walker (ABSTRACT) + ABS-001 tension-curve steering + method-006 cadence close (rules)
**Rework of:** 085-celtic-subset-walk
**Decision:** redesign (std6 index.html missing) + extend
**Date:** 2026-09-24 (nightly rework agent)
**Key:** Ab major (Ab Bb C Db Eb F G) · **BPM:** 96 · 4/4 · 480 TPB (bar = 1920, 8th = 240, 16th = 120)
**Form:** 8 sections × 4 bars = 32 bars — Intro | ReelA | ReelB | Lift | Bridge | ReelA2 | ReelC | Outro

---

## 1. Audit of source 085-celtic-subset-walk

6 current standards checked against the source project:

| # | Standard | Result |
|---|---|---|
| 1 | Engine (UnitMatrixComposer, not hand-rolled mido) | **PASS** |
| 2 | Zero-drift (all voice tracks equal length) | **PASS** (7 tracks × 46080) |
| 3 | Rhythm-grid sync (onsets % 120/240) | **PASS** (0 off-grid) |
| 4 | ≥ 4 voice tracks | **PASS** (7 tracks) |
| 5 | Two-phase artifacts (.mid + -phase1.mid) | **PASS** |
| 6 | provenance.json + index.html | **FAIL** — `index.html` missing |

`Analysis/rework_audit.json` written to the source project. **redesign_required = true**
(only std6 failed — the source is otherwise fully compliant, so the rebuild preserves
its identity and focuses on the extension + the missing dashboard).

## 2. What changed

- **Longer form**: 6 sections / 24 bars → **8 sections / 32 bars**. New sections:
  **Bridge** (bar 16–19, contrast) and **ReelC** (bar 24–27, second energy peak).
- **Fresh subset walk** (walk seed 7): 9 distinct degrees over 32 bars, V7 peak at
  bar 14 (Lift), authentic V7→I close at bars 30–31. Per-section harmonic regions
  derived from each section's **midpoint chord** (never bar-0 tonic — see §4).
- **7 variation techniques** applied (source had none explicit) — see §5.
- **index.html** dashboard added (the missing artifact), VoltAgent styling.
- **Bug fix carried forward**: the source's phase-1 raw melody was generated per-bar
  but concatenated WITHOUT bar offset, so the lead collapsed into bar 0 of each
  section. This rework offsets every bar (phase 1) and re-times per bar (phase 2),
  so the lead now spans all 32 bars (12–14 notes/bar).

## 3. The subset walk (32 bars, generative core)

```
Bar:    0   1   2   3 |  4   5   6   7 |  8   9  10  11 | 12  13  14  15 | 16  17  18  19 | 20  21  22  23 | 24  25  26  27 | 28  29  30  31
Degree: I  iii  I  iii | IV   I  ii  IV |  I iii  ii ii7 | vi  I7  V7 ii7 | IV  ii   I  ii |  I  IV  ii   I | IV   I  I7   V | iii IV  V7   I
```

Arc: Intro I–iii sway → ReelA IV–I–ii–IV rise → ReelB I–iii–ii–ii7 lean → **Lift
vi–I7–V7–ii7 peak (V7 @ bar 14)** → Bridge IV–ii–I–ii contrast → ReelA2 dance
return → ReelC IV–I–I7–V second peak → Outro iii–IV–**V7–I** cadence.

## 4. Per-section harmonic regions (midpoint chord)

| Section | Midpoint bar | Degree | Quality | Root pc |
|---|---|---|---|---|
| Intro | 2 | I | major | Ab (8) |
| ReelA | 6 | ii | minor | Bb (10) |
| ReelB | 10 | ii | minor | Bb (10) |
| Lift | 14 | V7 | dom7 | Eb (3) |
| Bridge | 18 | I | major | Ab (8) |
| ReelA2 | 22 | ii | minor | Bb (10) |
| ReelC | 26 | I7 | maj7 | Ab (8) |
| Outro | 30 | V7 | dom7 | Eb (3) |

Not every section lands on degree i (bar-0 tonic bug avoided): sections root on
ii, V7, I7, dom7 across the form.

## 5. Variation techniques (7)

| # | Technique | Where |
|---|---|---|
| V1 | Retrograde | Bridge lead: raw subset pitch stream reversed per bar |
| V2 | Inversion | Bridge violin: answer phrase inverted around pivot 74 |
| V3 | Register shift | Bridge lead low window (60–76); ReelC lead +12 (octave up) |
| V4 | Transposition | ReelC violin: answer phrase +7 (perfect fifth) |
| V5 | Augmentation | Outro bassoon: root counter 8ths → whole-bar |
| V6 | Diminution | ReelC bassoon: root counter 8ths → 16ths |
| V7 | Density/method change | Drum density curve 0.35 → 1.0 across 8 sections |

## 6. Two-phase architecture

**Phase 1** (`MIDI/104-celtic-subset-variations-phase1.mid`): raw abstract draft.
Single marimba voice (GM 12). Each bar's pitch stream samples the current walked
subset's pitch-class field (octave copies in the lead window); rhythm events land
on fractional, off-grid ticks. No harmony/bass/drums. 412 raw notes, 376 off-grid
(by design). Own `validate()` gate PASS. 0 scale violations, 0 chord violations
(each note stays in its own bar's walked subset).

**Phase 2** (`MIDI/104-celtic-subset-variations.mid`): musicom rules post-process.
Lead derived from phase-1 raw → per-section variation → 16th-grid snap → per-bar
chord-tone quantization → dedup → voice-leading cap (max leap 10). Full celtic
texture added (marimba / french horn / cello / violin / bassoon / double bass /
drum kit).

## 7. Verification (REAL numbers)

Phase 2 (deliverable):
- **7 voice tracks, all length 61440 ticks** (zero-drift PASS).
- **Pitched onsets 1105, off-grid 0**.
- **Scale violations 0** (every pc ∈ Ab-major).
- **Chord violations 0** (per-bar `t // BAR` attribution).
- Voice-leading leaps>12 flags: **0**.

Phase 1 (raw): 1 track, 61440 ticks, 412 onsets, 376 off-grid (raw by design),
0 scale / 0 chord violations.

Audio (FluidSynth CLI, FluidR3_GM via discover_soundfont):
- `104-celtic-subset-variations.wav` 14.6 MB — silence 3.02%, peak 0.928, 82.8 s.
- `104-celtic-subset-variations.ogg` 571 KB.
- phase1 wav 14.6 MB — silence 3.72%, peak 0.383; phase1 ogg 792 KB.
- No silent-render trap (silence ≪ 30%, peak well above 0.1).

## 8. Artifacts

```
MIDI/104-celtic-subset-variations.mid          (12958 B) + provenance.json
MIDI/104-celtic-subset-variations-phase1.mid   (3352 B)  + provenance.json
Audio/104-celtic-subset-variations.wav         (14.6 MB) + provenance.json
Audio/104-celtic-subset-variations.ogg         (571 KB)  + provenance.json
Audio/104-celtic-subset-variations-phase1.wav  (14.6 MB) + provenance.json
Audio/104-celtic-subset-variations-phase1.ogg  (792 KB)  + provenance.json
Analysis/grid_visualization.txt   Analysis/summary.json   Analysis/verify.json
Analysis/render_stats.json
compose.py  render_audio.py  verify.py  gen_dashboard.py
index.html  README.md  REPORT.md
```

All size asserts > 40 B passed. Zero-drift validate PASS on both phases.
