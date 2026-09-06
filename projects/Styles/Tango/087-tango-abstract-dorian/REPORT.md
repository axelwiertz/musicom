# REPORT — 087-tango-abstract-dorian

**Project:** 087-tango-abstract-dorian
**Style:** Tango (dramatic/abstract lean — milonga-style pulse, dorian darkness)
**Method:** ABS-002 Subset Walker (**ABSTRACT layer**) + ABS-001 tension-curve
steering + method-006 cadence close (rules layer)
**Date:** 2026-09-05 (nightly autonomous composition job)
**Seed:** 20260905
**Key:** D dorian (D E F G A B C) · **BPM:** 112 · 4/4 · 480 TPB
(bar = 1920, 8th = 240, 16th = 120)
**Form:** 6 sections × 4 bars = 24 bars — Intro | TangoA | TangoB | Lift |
TangoA2 | Outro (section = 7680 ticks, total 46080)

---

## 1. Concept

Tango study whose ENTIRE harmony is designed by the abstract layer: a walk
over the 12TET subset network (`rules.subset_network.PatternNetwork`) steered
by a per-bar tension curve. All anchor subsets are *fully diatonic in D
dorian*, so the walked harmony is a functional dorian progression with real
tonic pull. The concrete layer realizes each walked subset as chord tones and
locks a six-voice texture (alto sax lead, violin counterline, cello pad,
piano marcato comp, double-bass tango roots, drum kit) to the 16th grid.

Dorian was chosen over natural minor for tango: the raised 6th (B natural)
gives the IV (Gm) and ii (Edim) chords their characteristic color and makes
the VII (C major) a strong half-cadence home — the classic tango "andaluz
flavor" without the phrygian cliché.

## 2. The subset walk (24 bars, the generative core)

Anchor library (all fully diatonic in D dorian — pcs verified ⊆ {0,2,4,5,7,9,11}):

| degree | chord | pattern id | pcs (D-space) | tension |
|---|---|---|---|---|
| i   | Dm    | min2  | {2,5,9}    | 2.0 |
| ii  | Edim  | min4  | {4,7,11}   | 2.0 |
| III | F     | maj5  | {0,5,9}    | 2.0 |
| IV  | Gm    | maj7  | {2,7,11}   | 2.0 |
| v   | Am    | min9  | {0,4,9}    | 2.0 |
| vi  | Bdim  | dim11 | {2,5,11}   | 4.0 |
| VII | C     | maj0  | {0,4,7}    | 2.0 |
| i7  | Dm7   | min72 | {0,2,5,9}  | 5.0 |
| ii7 | Edim7 | min74 | {2,4,7,11} | 5.0 |
| IIImaj7 | Fmaj7 | maj75 | {0,4,5,9} | 5.5 |
| IV7 | Gm7   | dom77 | {2,5,7,11} | 7.0 |
| v7  | Am7   | min79 | {0,4,7,9}  | 5.0 |
| VII7| Cmaj7 | maj70 | {0,4,7,11} | 5.5 |

Per-bar tension targets (ABS-001 curve): intro sway (2.0) → TangoA rise
(2.3–2.9) → TangoB lean (2.6) → Lift peak (3.0–5.4, pulls the 7th chords
Am7/Edim7/Dm7 into the walk — bars 14-16) → TangoA2 dance return
(3.0→2.0) → Outro resolve (2.0). Because triads are all tension 2.0 and
tetrads 5.0–7.0, the Lift section is exactly where the 7th-chord color enters.

```
Bar:       0    1    2    3  |  4    5    6    7  |  8    9   10   11 |  12   13   14   15 |  16   17   18   19 |  20   21   22   23
Walk pid:  maj0 min2 maj5 maj0| min2 maj7 min2 maj5| maj7 maj0 min2 maj7| maj0 min79 min74 min72| min2 maj0 min2 maj0| maj5 min2 maj0 maj0
Degree:    VII  i    III  VII | i    IV   i    III | IV   VII  i    IV | VII  v7   ii7  i7  | i    VII  i    VII | III  i    VII  VII
D real:    C    Dm   F    C   | Dm   Gm   Dm   F  | Gm   C    Dm   Gm | C    Am7  Edim7 Dm7 | Dm   C    Dm   C   | F    Dm   C    C
```

Functional shape: the walk opens VII→i→III→VII (the dorian half-cadence home,
C major acting as the "tonic-ish" resolution of the mode's flat-7 pull),
oscillates i/IV/III through the body, peaks in the Lift with the 7th chords
(v7–ii7–i7, bar 14-16 = Am7 → Edim7 → Dm7), dances back over tonic-rooted
i/VII material, and the **cadence-close rule (method 006)** forced bar 23 to
`maj0` (C) so the piece ends on the dorian home chord — same gesture it
opened with.

## 3. Voices + instruments (all from the importable registry)

| # | Voice | Instrument (registry) | GM | Channel | Register | Role |
|---|-------|----------------------|----|---------|----------|------|
| 0 | LeadSax | Alto Saxophone | 65 | 0 | 60–84 | melodic lead, 8th/16th, chord tones |
| 1 | Violin  | Violin | 40 | 1 | 72–96 | answering counterline on beats 2 & 4 |
| 2 | Cello   | Cello | 42 | 2 | 48–72 | sustained pad: root + 5th/3rd whole-bar |
| 3 | Piano   | Piano | 1 | 3 | 60–84 | tango marcato staccato comp, beats 1 & 3 |
| 4 | Bass    | Double Bass | 43 | 4 | 38–50 | roots on 1 + offbeat-4 pickup pushes |
| 5 | Drums   | Drum Kit (ch9) | 0 | 9 | GM | kick 1&3 (all 4 beats in Lift), snare 2&4, hat 8ths/16ths, habanera accent |

Texture by section: Intro sparse (bass root only + light snare, no hat
16ths), TangoA/TangoB full pulse, Lift max density (kick every beat, 16th
hats), TangoA2 dance return, Outro quiet (bass root drops pickup pushes,
drums thin to kick/snare).

## 4. Two-phase architecture

**Phase 1** (`MIDI/087-tango-abstract-dorian-phase1.mid`): RAW abstract-layer
draft. Single alto-sax voice. Each bar's pitch stream samples the CURRENT
WALKED SUBSET's pitch-class field (octave copies, D-dorian window 55–88) —
the subset walk is directly audible as raw material. Rhythm events land on
fractional, deliberately OFF-GRID ticks (10–14 events per bar at randomized
fractional slots). No harmony, no bass, no drums. 285 raw notes (audit shows
283/285 off the 16th grid — the raw fingerprint).

**Phase 2** (`MIDI/087-tango-abstract-dorian.mid`): musicom rules
post-process.
1. Texture events built per voice from each bar's walked-subset chord tones
   (root-position realization via `pc_to_pitch`, octave-shifted pools per
   voice register).
2. GRID LOCK: every pitched onset snapped to the 16th (120 ticks) — the
   mandatory rhythm-grid-sync rule (078 bugfix).
3. CHORD-TONE quantization: each event re-pitched to the nearest tone of the
   chord belonging to the bar its SNAPPED onset lands in (octave-aware,
   ±12 search).
4. Voice-leading: leap cap ≤ 10 semitones between onsets ≤ 1 bar apart on
   lead + violin (nudged toward nearest chord tone of destination bar).
5. Dedupe of (start, pitch) collisions from grid snapping.
6. Full texture + zero-drift landmark padding per section cell.
   Cadence close: bar 23 forced to `maj0` (C).

## 5. Verification (REAL numbers)

### Grid audit (16th = 120, 8th = 240 ticks) — from `Analysis/audit.json`

| Voice | notes | off 16th | off 8th | out-of-scale | out-of-chord |
|---|---|---|---|---|---|
| Alto Sax lead (ch0) | 195 | **0** | 64* | 0 | 0 |
| Violin (ch1) | 96 | 0 | 0 | 0 | 0 |
| Cello (ch2) | 48 | 0 | 0 | 0 | 0 |
| Piano (ch3) | 144 | 0 | 0 | 0 | 0 |
| Double Bass (ch4) | 44 | 0 | 0 | 0 | 0 |
| Drums (ch9) | 344 | 0 | 56† | — (perc) | — |
| **TOTAL** | 871 | **0** | 120 | **0** | **0** |

\* Lead's 64 off-8th onsets are intentional 16th-level syncopation
(16th subdivisions in the tango melody) — all exact multiples of 120.
† Drums' off-8th are the 16th hat subdivisions + habanera 16th accents.
**Verdict: 0 off-grid on the 16th grid — PASS.**

Phase 1 (raw, by design unquantized): 285 notes, 283 off 16th / 284 off 8th —
the raw generative fingerprint. Not required to be on-grid.

### Harmony audit (phase-2 exported MIDI, mandatory)

Pitch-class membership vs D-dorian pcs {0,2,4,5,7,9,11} and per-bar chord pcs
(from the walked subset). Percussion skipped.

| Voice | notes | out-of-scale | out-of-chord |
|---|---|---|---|
| Alto Sax lead | 195 | **0** | **0** |
| Violin | 96 | **0** | **0** |
| Cello | 48 | **0** | **0** |
| Piano | 144 | **0** | **0** |
| Double Bass | 44 | **0** | **0** |

**Verdict: 0 out-of-scale, 0 out-of-chord — PASS.** (Every pitch in every
bar is a member of that bar's walked-subset chord.)

### Zero-drift status

- Phase 1 `validate()`: **OK** (2334 B)
- Phase 2 `validate()`: **OK** (7151 B)
- All cells end exactly at section boundary (7680 ticks); terminal landmark
  `MusicEvent(0,0,len,len)` appended per cell; all tracks identical absolute
  length (46080 ticks).

## 6. Audio render + silence/RMS profile

FluidSynth CLI SP-001 via `workflows.musicom_workflow.produce()`
(`discover_soundfont()` auto-resolved), `-g 1.2`; ffmpeg → Opus 48k VoIP.
Full analysis: `Analysis/render_stats.json`.

| Render | Duration | Silence ratio | Silent secs | Peak | RMS mean |
|--------|----------|---------------|-------------|------|----------|
| Phase 2 | 54.18 s | **4.7%** | 2 (tail 52-53) | 0.807 | 0.1209 |
| Phase 1 | 53.73 s | **8.6%** | 1 (tail 52) | 0.518 | 0.0752 |

Silent seconds are end-of-file reverb tail only (last audio at sec 51) —
**no mid-track gaps**. Phase-2 peak 0.807 (~-1.9 dBFS), no clipping. **PASS.**
(Stats are stereo-aware — mean of both channels. FluidSynth emits 2ch WAV;
an earlier mono-only read doubled the apparent duration; corrected.)

## 7. Fixes applied during the run

1. **Anchor bookkeeping bug**: initial hand-written rel-pc anchor tables had
   off-by-one subset errors (`iv`/`v` computed with a wrong interval stack).
   Rewrote to deterministic degree-stacking (`chord_pcs(deg)` from the dorian
   offset vector) with subset-equality lookup — all anchors then verified
   fully diatonic.
2. **Walk ending off-tonic**: raw walk landed bar 23 on `maj5` (F/III).
   Applied method-006 cadence close: bar 23 forced to `maj0` (C) → piece
   opens AND closes on the dorian home chord.
3. **Beat-math bug (musical correctness)**: drum/violin/piano/bass
   accompaniment used `beat * BAR//2` (2-beat steps = beats 1,3,5,7...) which
   placed beats 2&4 hits one beat late. Fixed with `BEAT = BAR//4` — the
   grid audit cannot catch this (all hits stay on-grid either way); caught by
   manual beat-position review. After fix: snare on real beats 2&4, kick 1&3,
   violin answers on beats 2&4, piano marcato on 1&3.
4. **Stereo-read duration bug (stats only)**: first stats pass read the
   interleaved 2ch WAV as mono, doubling apparent duration to 108 s. Audio
   was correct all along (54.18 s = 46080 ticks @ 112 BPM). Fixed with
   `getnchannels()`-aware downmix in `compose.py` stats + `audio_stats.py`;
   `render_stats.json` regenerated with true numbers.

## 8. Files

```
087-tango-abstract-dorian/
├── README.md
├── REPORT.md
├── compose.py
├── audit.py
├── audio_stats.py
├── probe_anchors.py / probe2.py / gen_part1.py   (anchor-probe scratch)
├── MIDI/
│   ├── 087-tango-abstract-dorian.mid          (7151 B) + .provenance.json
│   └── 087-tango-abstract-dorian-phase1.mid   (2334 B) + .provenance.json
├── Audio/
│   ├── 087-tango-abstract-dorian.wav      (9.56 MB) + .provenance.json
│   ├── 087-tango-abstract-dorian.ogg      (371 KB) + .provenance.json
│   ├── 087-tango-abstract-dorian-phase1.wav  (9.48 MB) + .provenance.json
│   └── 087-tango-abstract-dorian-phase1.ogg  (446 KB) + .provenance.json
└── Analysis/
    ├── grid_visualization.txt
    ├── summary.json
    ├── audit.json
    └── render_stats.json
```

## 9. Verification checklist

- [x] Style: Tango; Method: ABS-002 (abstract layer) + ABS-001 + 006 close
- [x] Two-phase: phase-1 raw (unquantized single voice, 285 notes) +
      phase-2 rules (6 voices, grid+chord locked), both validated
- [x] Engine-only: structures + workflows.unitmatrix_composer +
      rules.subset_network; mido read-only in audit
- [x] Instrument registry: SAXOPHONE/VIOLIN/CELLO/PIANO/DOUBLE_BASS/DRUM_KIT
- [x] Zero-drift: validate() OK both phases, landmark-padded cells
- [x] Grid audit: 0 off-16th on all 6 phase-2 voices
- [x] Harmony audit: 0 out-of-scale / 0 out-of-chord on all 5 pitched voices
- [x] Audio: WAV + OGG both phases, sizes > 40 B, silence < 30%, tail-only
- [x] Provenance sidecars on all 6 artifacts (2 MIDI + 4 audio)
- [x] Analysis/grid_visualization.txt, summary.json, audit.json,
      render_stats.json
