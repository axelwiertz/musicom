# REPORT — 085-celtic-subset-walk

**Project:** 085-celtic-subset-walk
**Style:** Celtic
**Method:** ABS-002 Subset Walker (ABSTRACT layer) + ABS-001 tension-curve steering + method-006 cadence close (rules layer)
**Layer:** abstract (weekly abstract-cadence run, 1-in-7)
**Date:** 2026-09-03 (nightly autonomous composition job)
**Seed:** 20260903 · walk seed: 3
**Key:** Ab major (Ab Bb C Db Eb F G) · **BPM:** 96 · 4/4 · 480 TPB (bar = 1920, 8th = 240, 16th = 120)
**Form:** 6 sections × 4 bars = 24 bars — Intro | ReelA | ReelB | Lift | ReelA2 | Outro (section = 7680 ticks)

---

## 1. Concept

Celtic dance piece whose ENTIRE harmony is designed by the abstract layer: a
walk over the 12TET subset network (`rules.subset_network.PatternNetwork`)
steered by a per-bar tension curve. The subset walk is the generative method;
the concrete layer realizes the walked subsets as root-position diatonic
Ab-major chords and locks a marimba lead + horn/cello pads + violin
counterline + bassoon counter + double-bass roots + drum kit to the rhythmic
grid.

Anchor subset library (all fully diatonic in Ab major — verified subset pcs
transposed +8 ⊆ Ab-major pcs):

| id | subset (C-space) | Ab realization | degree | tension |
|---|---|---|---|---|
| maj0  | {0,4,7}   | Ab major      | I   | 2.0 |
| min2  | {2,5,9}   | Bb minor      | ii  | 2.0 |
| min4  | {4,7,11}  | C minor       | iii | 2.0 |
| maj5  | {0,5,9}   | Db major      | IV  | 2.0 |
| maj7  | {2,7,11}  | Eb major      | V   | 2.0 |
| min9  | {9,0,4}   | F minor       | vi  | 2.0 |
| maj70 | {0,4,7,11}| Abmaj7        | I7  | 5.5 |
| dom77 | {2,5,7,11}| Eb7           | V7  | 7.0 |
| min72 | {9,0,4,7} | Fm7           | vi7 | 5.0 |

Per-bar tension targets (ABS-001 curve): intro sway (2.0) → ReelA rise
(2.5–3.0) → ReelB lean (3.5–4.0) → Lift peak (4.5–5.5, pulls V7/I7 into the
walk) → ReelA2 dance return (3.0–2.0) → Outro resolve (1.5–1.0). Because the
triad anchors are all tension-2.0 and the 7th anchors are 5.0–7.0, peaks
≥ 4.5 are what bring the dominant into the design.

## 2. The subset walk (24 bars, the generative core)

```
Bar:       0    1    2    3  |  4    5    6    7  |  8    9   10   11 |  12   13   14   15 |  16   17   18   19 |  20   21   22   23
Degree:    I    ii   IV   iii |  I    iii  IV   ii |  IV   iii  I7   V |  I7   iii  V7   iii |  I    ii   IV   ii |  IV   iii  V7   I
Ab real:  Ab   Bbm  Db   Cm  |  Ab   Cm   Db   Bbm|  Db   Cm   Abmaj7 Eb|  Abmaj7 Cm  Eb7  Cm |  Ab   Bbm  Db   Bbm|  Db   Cm   Eb7  Ab
Tension:  2.0  2.0  2.0  2.0    2.5  2.5  3.0  3.0   3.5  3.5  5.5  2.0   5.5  2.0  7.0  2.0   3.0  2.5  2.0  2.0   2.0  2.0  7.0  2.0
```

Structural reading of the walk (seed 3):
- **Intro** I–ii–IV–iii — tonic sway, opening statement.
- **ReelA** I–iii–IV–ii — rise; motion without dominant.
- **ReelB** IV–iii–**I7–V** — cadence INTO the Lift: bar 11 = V (Eb) resolves
  to bar 12 = I7. Dominant function enters the dance half.
- **Lift** I7–iii–**V7**–iii — the peak: full dominant-seventh (Eb7, tension
  7.0) at bar 14, the walk's single most-tense event.
- **ReelA2** I–ii–IV–ii — dance return, tonic-rooted, full drum energy.
- **Outro** IV–iii–V7–I — cadence close. Bar 22 was walked as `ii`; the
  cadence-and-closure post-rule (rules layer, cf. method 006) replaced it with
  V7 (`dom77`) so the piece closes authentically V7→I. Bar 23 I forced (walk
  `home`).

## 3. Voices + instruments (all from the importable registry)

| # | Voice | Instrument (registry) | GM | Channel | Register used | Role |
|---|-------|----------------------|----|---------|---------------|------|
| 0 | Lead  | Marimba (prog 12) | 12 | 0 | 48–96 (sweet 60–84) | lead melody |
| 1 | Horns | French Horn (prog 60) | 60 | 1 | 52–84 (sweet 55–72) | pad harmony (root-position) |
| 2 | Cello | Cello (prog 42) | 42 | 2 | 40–72 (sweet 48–67) | low pad (root + fifth) |
| 3 | Violin| Violin (prog 40) | 40 | 3 | 60–96 (sweet 67–96) | answering counterline |
| 4 | Bassoon| Bassoon (prog 70) | 70 | 4 | root+12 (48–64) | root counter (8ths in dance) |
| 5 | Bass  | Double Bass (prog 43) | 43 | 5 | 28–52 (sweet 40–55) | roots, 4/4 pulse + 16th pushes |
| 6 | Drums | Drum Kit (ch9, KIT constants) | 0 | 9 | GM drums | kick 1&3, snare 2&4, hats 8ths, ride, claps, woodblock |

Texture rules by section: Intro sparse (0.35 drum density, whole-bar horns,
whole-bar bassoon root), ReelA 0.85, ReelB + ReelA2 full dance (1.0: claps
doubling snare, 16th bass pushes, woodblock 2& tick, bassoon 8ths), Lift 0.7
(drums open up while harmony peaks), Outro 0.4 (whole-bar pads, quiet close).

## 4. Two-phase architecture

**Phase 1** (`MIDI/085-celtic-subset-walk-phase1.mid`): RAW abstract-layer
draft. Single marimba voice. Each bar's pitch stream samples the CURRENT
WALKED SUBSET's pitch-class field (octave copies in the lead window) — the
subset walk is directly audible as raw material. Rhythm events land on
fractional, deliberately OFF-GRID ticks (mean slot = BAR/14 ≈ 137 ticks, not a
grid multiple). No harmony, no bass, no drums. 274 raw notes.

**Phase 2** (`MIDI/085-celtic-subset-walk.mid`): musicom rules post-process.
Lead: 16th-grid lock FIRST (snap → then quantize to the chord of the bar the
SNAPPED onset lands in — a raw onset in the last 120 ticks of bar N snaps into
bar N+1 and takes bar N+1's chord), octave-aware chord-tone quantization to
the root-position walked-subset realization, dedup of collided
(start_tick, pitch) pairs, voice-leading cap (max leap 10 semitones between
adjacent onsets ≤ 1 beat apart). Full texture added (horns/cello/violin/
bassoon/bass/drums). 180 lead notes (was 274 raw — dedup + grid collisions).

## 5. Verification (REAL numbers)

### Grid audit (16th = 120, 8th = 240 ticks) — from `Analysis/audit.json`

| Voice | notes | off 16th | off 8th | out-of-scale | out-of-chord |
|---|---|---|---|---|---|
| Marimba lead | 180 | **0** | 89* | 0 | 0 |
| French Horn | 94 | 0 | 0 | 0 | 0 |
| Cello | 34 | 0 | 0 | 0 | 0 |
| Violin | 96 | 0 | 0 | 0 | 0 |
| Bassoon | 104 | 0 | 0 | 0 | 0 |
| Double Bass | 104 | 0 | 0 | 0 | 0 |
| Drums (ch9) | 352 | 0 | 0 | — (perc) | — (perc) |
| **TOTAL** | 964 | **0** | 97 | **0** | **0** |

\* Lead is intentionally 16th-locked: 89 notes land on 16ths between 8ths —
that is ON the 16th grid (off8 counts are expected for 16th-note material;
the contract grid is the 16th). All voices 0 off-16th.

Phase 1 raw (by design unquantized): 274 notes, 251 off 16th / 253 off 8th —
the raw fingerprint, 0 out-of-scale.

### Harmony audit
Every pitched voice: every note's pitch class ∈ Ab-major scale AND ∈ the
walked subset's chord (per bar where the onset starts). Counts: **0
out-of-scale, 0 out-of-chord** across all 612 pitched notes.

### Zero-drift
`validate()` gate PASSED for BOTH phases (phase 1: OK, phase 2: OK). All
cells normalized to exact section boundary (7680 ticks) with terminal
landmark; equal track lengths guaranteed by the engine.

### Audio (SP-001 FluidSynth, FluidR3_GM via discover_soundfont)
| file | bytes | silence ratio | low-RMS secs | tonal windows |
|---|---|---|---|---|
| 085-celtic-subset-walk.wav | 11,069,996 | 4.1% | 1/62 | 122/124 |
| 085-celtic-subset-walk.ogg | 411,152 | — | — | — |
| phase1 wav | 10,937,132 | 70.0%* | 44/62 | 42 |
| phase1 ogg | 322,054 | — | — | — |

\* Phase-1 raw is a sparse solo marimba draft (no accompaniment) — 70%
silence is expected and consistent with prior phase-1 renders (078: solo
tenor-sax draft). Phase-2 full mix 4.1% silence = healthy. Dominant FFT
peaks 50–1000 Hz: 66 Hz (bass fundamental), 104/350/830 Hz region —
pitched content present, not noise. 1 low-RMS second out of 62 (the final
reverb tail).

## 6. Fixes applied during this run (learned)

1. **Chord realization transposition bug (v1)**: first realization re-anchored
   transposed pcs in C-space (48 + raw pc) instead of root-position in Ab —
   produced wrong roots (C bass under Db chords, etc.). Fixed by parsing the
   root pc from the subset id (`maj5` → root pc 5 → Ab-space pc 1 = Db) and
   building root + (pc − root) % 12 diffs.
2. **Tension curve too flat (v1)**: triad anchors are all tension 2.0, so
   peaks ≤ 3.4 never admitted V/V7 — the walk was a pure triad loop with no
   dominant function. Raised peak targets to 4.5–5.5 so 7th anchors enter at
   the Lift; verified the walk now places V7/I7 at the structural peak.
3. **Violin line spilled into the next bar**: 8-note line at 240-tick offsets
   from 240 (240..1920) put the last note in bar N+1 → 3 out-of-chord notes.
   Changed offsets to 0..1680.
4. **Section-relative bar indexing bug (lead, critical)**: lead quantization
   used `bar = start // BAR` on SECTION-RELATIVE ticks (0–7679), indexing
   WALK_IDS[0..3] instead of the absolute bar — section 2+ leads were
   harmonized against section-1 chords (43 out-of-chord notes on IV bars).
   Fixed with `bar = s*4 + (start // BAR)`.
5. **16th-push ends beyond grid**: bass push ended at 1910, not on the 16th
   grid → snapped to 1900 (16th 15); all drum/bass note-offs moved to
   16th-aligned offsets.
6. **Audit drum channel**: ch9 percussion excluded from scale/chord checks
   (drums are not pitched voices).

## 7. Artifacts

```
MIDI/085-celtic-subset-walk.mid            (8218 B)  + provenance.json
MIDI/085-celtic-subset-walk-phase1.mid     (2128 B)  + provenance.json
Audio/085-celtic-subset-walk.wav           (11.07 MB) + provenance.json
Audio/085-celtic-subset-walk.ogg           (411 KB)  + provenance.json
Audio/085-celtic-subset-walk-phase1.wav    (10.94 MB) + provenance.json
Audio/085-celtic-subset-walk-phase1.ogg    (322 KB)  + provenance.json
Analysis/grid_visualization.txt
Analysis/audit.json
Analysis/render_stats.json
Analysis/summary.json
compose.py  audit.py  render_audio.py  audio_stats.py  audio_provenance.py
README.md  REPORT.md
```

All size asserts > 40 B passed. Zero-drift validate PASS on both phases.
AUDIT PASS: 0 off-grid (16th), 0 out-of-scale, 0 out-of-chord.
