# REPORT — 221-celtic-subset-walk-extended

**Project:** 221-celtic-subset-walk-extended
**Style:** Celtic
**Method:** ABS-002 Subset Walker (ABSTRACT) + ABS-001 tension-curve steering + method-006 cadence close (rules)
**Rework of:** 104-celtic-subset-variations
**Decision:** extension (source audited 6/6 standards PASS — no redesign needed)
**Date:** 2026-10-04 (nightly rework agent)
**Key:** Ab major (Ab Bb C Db Eb F G) · **BPM:** 96 · 4/4 · 480 TPB (bar = 1920, 8th = 240, 16th = 120)
**Form:** 10 sections × 4 bars = 40 bars — Intro | ReelA | ReelB | Lift | Bridge | ReelA2 | ReelC | Hornpipe | Finale | Outro

---

## 1. Audit of source 104-celtic-subset-variations

6 current standards checked against the source project (fresh mido read-only parse):

| # | Standard | Result |
|---|---|---|
| 1 | Engine (UnitMatrixComposer, not hand-rolled mido) | **PASS** |
| 2 | Zero-drift (all voice tracks equal length) | **PASS** (7 tracks × 61440) |
| 3 | Rhythm-grid sync (onsets % 120/240) | **PASS** (0 off-grid, 1105 pitched) |
| 4 | ≥ 4 voice tracks | **PASS** (7 tracks) |
| 5 | Two-phase artifacts (.mid + -phase1.mid) | **PASS** |
| 6 | provenance.json + index.html | **PASS** |

`Analysis/rework_audit.json` written to the source project. **redesign_required = false**.
Fully compliant → **extension path**: keep identity, use existing material as DNA seed,
extend to a longer, more varied form.

## 2. What changed

- **Longer form**: 8 sections / 32 bars → **10 sections / 40 bars**. Two new sections:
  **Hornpipe** (bar 28–31, offbeat-clap groove, 16th-note bassoon drive) and
  **Finale** (bar 32–35, full-texture peak with flute doubling lead).
- **Fresh subset walk** (walk seed 13, distinct from source's seed 7): 9 distinct
  degrees over 40 bars, V7 peaks at **bar 14 (Lift)** and **bar 33 (Finale)**,
  authentic V7→I close at bars 38–39 (Outro). Per-section harmonic regions derived
  from each section's **midpoint chord** (never bar-0 tonic — see §4).
- **8th voice added**: Flute (GM 74, channel 6) as a new ornament counterline (V8).
- **8 variation techniques** applied (source had 7, none were flute-related) — see §5.
- Bug fix carried forward (from 104): phase-1 raw melody offsets every bar within its
  section, so the lead spans all 40 bars instead of collapsing to bar 0.

## 3. The subset walk (40 bars, generative core)

```
Bar:    0   1   2   3 |  4   5   6   7 |  8   9  10  11 | 12  13  14  15 | 16  17  18  19 | 20  21  22  23 | 24  25  26  27 | 28  29  30  31 | 32  33  34  35 | 36  37  38  39
Degree: I  iii  ii  IV | iii  I  IV   I | IV   I  I7   V | ii  ii7  V7  ii7 | vi   I  IV  ii |  I  iii  I  IV | iii I7 iii   I | I7 iii  ii  IV | ii  V7  IV  ii |  I  iii  V7   I
```

Arc: Intro I–iii–ii–IV sway → ReelA iii–I–IV–I rise → ReelB IV–I–I7–V lean →
**Lift ii–ii7–V7–ii7 peak (V7 @ bar 14)** → Bridge vi–I–IV–ii contrast (the vi!) →
ReelA2 dance return → ReelC iii–I7–iii–I second rise → **Hornpipe I7–iii–ii–IV
drive** → **Finale ii–V7–IV–ii peak (V7 @ bar 33)** → **Outro I–iii–V7–I cadence**.

## 4. Per-section harmonic regions (midpoint chord)

| Section | Midpoint bar | Degree | Quality | Root pc |
|---|---|---|---|---|
| Intro | 2 | ii | minor | Bb (10) |
| ReelA | 6 | IV | major | Db (1) |
| ReelB | 10 | I7 | maj7 | Ab (8) |
| Lift | 14 | V7 | dom7 | Eb (3) |
| Bridge | 18 | IV | major | Db (1) |
| ReelA2 | 22 | I | major | Ab (8) |
| ReelC | 26 | iii | minor | C (0) |
| Hornpipe | 30 | ii | minor | Bb (10) |
| Finale | 34 | IV | major | Db (1) |
| Outro | 38 | V7 | dom7 | Eb (3) |

Sections root on ii, IV, I7, V7, iii across the form — never all on degree i
(bar-0 tonic bug avoided).

## 5. Variation techniques (8)

| # | Technique | Where |
|---|---|---|
| V1 | Retrograde | Bridge lead: raw subset pitch stream reversed per bar |
| V2 | Inversion | Bridge violin: answer phrase inverted around pivot 74 |
| V3 | Register shift | Bridge lead low window (60–76); ReelC + Hornpipe lead +12 (octave up) |
| V4 | Transposition | Finale violin: answer phrase +7 (perfect fifth) |
| V5 | Augmentation | Outro bassoon: root counter 8ths → whole-bar |
| V6 | Diminution | Hornpipe bassoon: root counter 8ths → 16ths |
| V7 | Density/method change | Drum density curve 0.35→1.0 + Hornpipe offbeat-clap method change |
| V8 | Counterline addition | NEW flute voice: chord ornament in dance sections, octave-arpeggio doubling in Finale |

## 6. Two-phase architecture

**Phase 1** (`MIDI/221-celtic-subset-walk-extended-phase1.mid`): raw abstract draft.
Single marimba voice (GM 12). Each bar's pitch stream samples the current walked
subset's pitch-class field (octave copies in the lead window); rhythm events land
on fractional, off-grid ticks. No harmony/bass/drums. 516 raw notes, 474 off-grid
(by design). Own `validate()` gate PASS. 0 scale violations, 0 chord violations.

**Phase 2** (`MIDI/221-celtic-subset-walk-extended.mid`): musicom rules post-process.
Lead derived from phase-1 raw → per-section variation → 16th-grid snap → per-bar
chord-tone quantization → dedup → voice-leading cap (max leap 10). Full 8-voice
celtic texture (marimba / french horn / cello / violin / bassoon / double bass /
drum kit / flute).

## 7. Verification (REAL numbers)

Phase 2 (deliverable):
- **8 voice tracks, all length 76800 ticks** (zero-drift PASS).
- **Pitched onsets 1586, off-grid 0**.
- **Scale violations 0** (every pc ∈ Ab-major).
- **Chord violations 0** (per-bar `t // BAR` attribution).
- Voice-leading leaps>12 flags: **0**.

Phase 1 (raw): 1 track, 76800 ticks, 516 onsets, 474 off-grid (raw by design),
0 scale / 0 chord violations.

Audio (FluidSynth CLI, FluidR3_GM via discover_soundfont):
- `221-celtic-subset-walk-extended.wav` 18.1 MB — 102.8 s, silence 2.59%, peak 0.962, RMS 0.156.
- `221-celtic-subset-walk-extended.ogg` 715 KB.
- phase1 wav 18.1 MB — silence 3.05%, peak 0.356; phase1 ogg 998 KB.
- No silent-render trap (silence ≪ 30%, peak well above 0.1).

## 8. Artifacts

```
MIDI/221-celtic-subset-walk-extended.mid          (18140 B) + provenance.json
MIDI/221-celtic-subset-walk-extended-phase1.mid   (4185 B)  + provenance.json
Audio/221-celtic-subset-walk-extended.wav         (18.1 MB)
Audio/221-celtic-subset-walk-extended.ogg         (715 KB)
Audio/221-celtic-subset-walk-extended-phase1.wav  (18.1 MB)
Audio/221-celtic-subset-walk-extended-phase1.ogg  (998 KB)
Analysis/grid_visualization.txt   Analysis/summary.json
compose.py  REPORT.md  README.md  index.html
```

All size asserts > 40 B passed. Zero-drift validate PASS on both phases.
