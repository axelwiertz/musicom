# REPORT — 291 HipHop Ostinato Loop

**Nightly composition job (ID 1fc3fd65d359) · 2026-11-08 · Method 015 (concrete layer)**

## 1. Selection (LAYERED METHODOLOGY)

| Field | Value |
|---|---|
| Style | **HipHop** (46 candidate genre folders) |
| Method | **015 — Ostinato Constraint Writing** (Rules-Based) |
| Layer | **concrete** (weekly abstract cadence not due; last abstract was 287 on 11-05) |
| Form | **aabb** → sections `A A B B`, bars `[4,4,4,4]` = **16 bars** (from `pick_form("HipHop")`) |
| Key / mode | **A natural minor** — A B C D E F G (PC set {0,2,4,5,7,9,11}) |
| Tempo | 92 BPM · 4/4 · 480 TPB (bar = 1920, 8th = 240, 16th = 120) |

Method pool: 102 concrete non-AI candidates, excluding the abstract layer
{95,99,104,113,127,131,133,134}, impractical AI-driven methods
{42,46,47,54,57,60,62,63,72,74,85,100,101,103,106,108,110,118}, and methods used
in the last 7 days {11,13,18,21,31,45,69,131}.

## 2. Concept — Ostinato Constraint Writing (Method 015)

Method 015 prescribes a **static structural loop in the lower voices** while
**variations are composed on top**. Realised as:

- **Static lower voice**: a fixed 8th-note bass ostinato (root/fifth/octave
  contour) whose *rhythm is identical across all 16 bars*; only the pitch
  tracks the chord root. This is the ostinato cell.
- **Variations on top**: the lead (flute) plays **four distinct passes** over
  the same ostinato:
  1. **A (bars 0-3)** — *theme* (half-note spacing, 8 onsets)
  2. **A (bars 4-7)** — *diminution* (quarter-note spacing, 2× onsets of the theme)
  3. **B (bars 8-11)** — *register shift (+12) + new contour*
  4. **B (bars 12-15)** — *retrograde* of the theme (sparse, half notes)

## 3. Voices + Instruments (instrument registry — source of truth)

| Voice | Instrument | Program | Channel | Role |
|---|---|---|---|---|
| Lead | Flute | 73 | 0 | variations on top (4 passes) |
| Bass | Synth Bass 1 | 38 | 1 | static ostinato (lower voice) |
| Pad | Rhodes (E. Piano) | 4 | 2 | whole-bar triad harmony |
| Drums | Drum Kit | 0 | 9 | boom-bap groove |

## 4. Harmony (per-section regions)

A natural-minor diatonic triads only (no chromatic anywhere — every chord tone
⊂ the A-minor scale, so the tiered audit is trivially satisfiable):

```
A (bars 0-3, 4-7):  i  -  VI  - III - VII   = Am  F  C  G
B (bars 8-11,12-15): iv -  v  -  VI  - VII  = Dm  Em  F  G
```

| Degree | Quality | Root MIDI | Triad |
|---|---|---|---|
| i | m | 57 | A C E |
| VI | M | 53 | F A C |
| III | M | 48 | C E G |
| VII | M | 55 | G B D |
| iv | m | 50 | D F A |
| v | m | 52 | E G B |

## 5. Two-phase architecture

- **Phase 1** (`-phase1.mid`): raw generative draft — single-voice 8th-note
  bass ostinato with OFF-GRID fractional onset jitter (±0.16 step) and
  unquantized pitch drift (±1.4 st). No harmony/pad/lead/drums. 126 audible
  events, 126/126 off-grid (unquantized by design).
- **Phase 2** (`-perfect.mid` + `-humanized.mid`): grid-lock to 16th → chord
  snap → tiered pitch discipline (engine `ScaleQuantizer` +
  `classify_weight`) → zero-drift landmark → `validate()` → `export_dual`.

## 6. Grid audit (pre-humanization — perfect == 0 off-grid)

| Voice | 16th grid (120) | 8th grid (240) |
|---|---|---|
| Lead | **0 / 48** | 0 / 48 |
| Bass | **0 / 140** | 12 / 140 (the 16th-note bar-pickups, on-grid at 16th) |
| Pad | **0 / 42** | 0 / 42 |
| Drums | **0 / 240** | 0 / 240 |

All pitched voices: **0 off-grid on the 16th grid** (the finest required grid).

## 7. Harmony audit (tiered — `workflows.pitch_audit.audit_voice`)

`strong_grid = (0, 960)`, `bar_ticks = 1920`, chord context per bar.

| Voice | status | audible | strong_ok | weak_in_scale | tagged | non_resolving | untagged_out | strong_viol |
|---|---|---|---|---|---|---|---|---|
| Lead | **PASS** | 48 | 32 | 16 | 0 | 0 | 0 | 0 |
| Bass | **PASS** | 140 | 32 | 108 | 0 | 0 | 0 | 0 |
| Pad | **PASS** | 42 | 42 | 0 | 0 | 0 | 0 | 0 |

**0 untagged out-of-scale / 0 non-resolving / 0 strong violations** across all
pitched voices. No chromatic ornaments used (all material diatonic chord tones).

## 8. Humanization (always-on, style-derived, seeded)

`HZ_SEED = 141827757` (= `20261108 * 7 + 1`). Per-voice child seed =
`HZ_SEED * 101 + row`.

| Voice | timing (ms) | vel σ | layback (ms) | dur σ | mean shift (ticks) | max shift | vel delta |
|---|---|---|---|---|---|---|---|
| Lead | 4.0 | 7.0 | 6.0 | 0.02 | 4.04 | 9 | 5.38 |
| Bass | 5.0 | 4.0 | 8.0 | 0.01 | 6.21 | 14 | 3.09 |
| Pad | 4.0 | 5.0 | 6.0 | 0.015 | 4.95 | 10 | 3.81 |
| Drums | 2.0 | 4.0 | 0.0 | 0.008 | **0.99** | 4 | 3.03 |

Drums anchor tightest (0 layback, ~1 tick jitter); bass lays back (+8 ms) —
matches the instrument-role DNA contract.

## 9. Dual-version contract (perfect vs humanized)

`-perfect.mid`: grid-locked, **0 off-grid** onsets (16th).
`-humanized.mid`: **397 off-grid** onsets (16th) — proves the humanizer ran.
`-phase1.mid`: 126 off-grid (raw draft, un-humanized by construction).

## 10. Zero-drift

`validate()` returns **OK on both phases** (equal-length tracks, terminal
landmark `MusicEvent(0,0,SECTION_TICKS-1,SECTION_TICKS)`). mido readback
confirms sane last-note positions (28.8k–30.5k ticks of 30,720 total).

## 11. Render + master (all three versions)

SoundFont: FluidR3_GM.sf2 (via `discover_soundfont()`). FluidSynth `-ni -g 1.2 -R no -C no`.
Target = `target_for_style("hiphop")` = **−9.0 LUFS**, −1 dBTP ceiling.

| Version | LUFS | dBTP | silence | OGG (bytes) | WAV (bytes) |
|---|---|---|---|---|---|
| perfect | −9.50 | −1.0 | 5.370 % | 340,622 | 7,808,044 |
| humanized | −9.48 | −1.0 | 5.307 % | 339,384 | 7,808,300 |
| phase1 | −9.37 | −1.0 | 6.720 % | 411,679 | 7,813,676 |

Silence ratio is the ~2 s reverb tail after the last note (RMS-per-second map
holds ~0.20–0.29 throughout, no mid-track gaps). Peak sits at the −1 dBTP
ceiling (hiphop is a dynamic/percussive style — see `master()` true-peak note).

## 12. File paths

```
/opt/data/projects/Styles/HipHop/291-hiphop-ostinato-loop/
├── compose.py
├── render_audio.py
├── verify.py
├── README.md
├── REPORT.md
├── MIDI/
│   ├── 291-hiphop-ostinato-loop-phase1.mid      (1,145 B)
│   ├── 291-hiphop-ostinato-loop-perfect.mid     (3,941 B)
│   ├── 291-hiphop-ostinato-loop-humanized.mid   (3,938 B)
│   └── *.provenance.json  (×3)
├── Audio/
│   ├── 291-hiphop-ostinato-loop-{perfect,humanized,phase1}.wav
│   ├── 291-hiphop-ostinato-loop-{perfect,humanized,phase1}.ogg
│   └── master_stats.json
└── Analysis/
    ├── grid_visualization.txt
    ├── manifest.json
    ├── readback.json
    └── summary.json
```

## 13. Fixes / notes

- Used the engine tiered quantizer (`ScaleQuantizer(root=57, scale="minor")` +
  `classify_weight`) rather than any hand-rolled `% 7` wrapper (diatonic-note
  scaling rule).
- Kept harmony strictly natural-minor (no harmonic-minor V), so no chromatic
  anywhere — every chord tone is a scale tone, the tiered audit is airtight.
- Phase-1 bass centre was folded into bass register to keep raw drift inside
  `[36,60]`.