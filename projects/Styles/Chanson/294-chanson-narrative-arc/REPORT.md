# REPORT — 294 Chanson Narrative Arc

**Nightly composition job (ID 1fc3fd65d359) · 2026-11-09 · Method 007 (concrete layer)**

## 1. Selection (LAYERED METHODOLOGY)

| Field | Value |
|---|---|
| Style | **Chanson** (47 candidate genre folders) |
| Method | **007 — Narrative Arc Register Planning** (Rules-Based) |
| Layer | **concrete** (weekly abstract cadence not due; last abstract was 287 on 11-05) |
| Form | **strophic** → sections `Verse1…Verse4`, bars `[8×4]` = **32 bars** (from `pick_form("chanson")` — "chanson" matches the strophic/aabb/verse-chorus hints) |
| Key / mode | **F major** — F G A Bb C D E (PC set {5,7,9,10,0,2,4}) |
| Tempo | 72 BPM · 4/4 · 480 TPB (bar = 1920, 8th = 240, 16th = 120) |

Method pool: concrete non-AI candidates, excluding the abstract layer
{95,99,104,113,127,131,133,134}, impractical AI-driven methods, and methods
used in the last 7 days {11,13,15,18,21,31,32,45,48,69,98,131}.

## 2. Concept — Narrative Arc Register Planning (Method 007)

Method 007 maps a **story arc to register**: the melodic register rises through
the piece toward a climax, then falls back (exposition → rising action → climax
→ denouement). The verse-level register plan:

| Verse | Register center | Role |
|---|---|---|
| Verse1 | 67 (G4) | exposition — low, intimate |
| Verse2 | 72 (C5) | rising action |
| Verse3 | 77 (F5) | **climax** — peak register |
| Verse4 | 69 (A4) | denouement — falling back |

Within each verse the contour rises to a **local climax at ~62% through** (the
golden-ratio peak), then falls. Phase-1 measured per-verse mean pitch proves the
arc: `{V1 67.22 → V2 72.0 → V3 76.81 → V4 68.86}`.

Mapped onto a **chanson** texture — the narrative line is a lyrical violin, over
a sustained accordion pad, a double-bass root/fifth, and an off-beat clarinet
counterline.

## 3. Voices + Instruments (instrument registry — source of truth)

| Voice | Instrument | Program | Channel | Role |
|---|---|---|---|---|
| Lead | Violin | 40 | 0 | narrative-arc melody (register-planned) |
| Counter | Clarinet | 71 | 1 | off-beat scale-step counterline |
| Accordion | Accordion | 21 | 2 | sustained triad per bar |
| Bass | Double Bass | 43 | 3 | root (beat 1) + fifth (beat 3) per bar |

## 4. Harmony (F major, strophic)

8-bar verse progression `I vi ii V I vi IV V` (degrees 1 6 2 5 1 6 4 5, ending
on the V half-cadence to lead the next verse); the final verse resolves to I
(`1 6 2 5 1 6 4 1`). Bass roots: F2=41, D2=38, G2=43, C2=36, Bb2=46.

| Degree | Triad (pcs) | Name |
|---|---|---|
| I (1) | {5,9,0} | F A C |
| ii (2) | {7,10,2} | G Bb D |
| IV (4) | {10,2,5} | Bb D F |
| V (5) | {0,4,7} | C E G |
| vi (6) | {2,5,9} | D F A |

All chord pcs are F-major scale tones, so the tiered audit is fully satisfiable
with zero chromatic anywhere.

## 5. Two-phase architecture

- **Phase 1** (`-phase1.mid`): raw generative draft — single-voice
  narrative-arc stream (register center per verse + intra-verse rise/fall),
  OFF-GRID onset jitter (±0.16 step) and unquantized pitch drift (±1.3 st).
  No harmony/counter/bass/pad. 253 audible events, **252/253 off-grid**
  (unquantized by design).
- **Phase 2** (`-perfect.mid` + `-humanized.mid`): grid-lock to 16th → tiered
  pitch discipline (`ScaleQuantizer(root=53, scale="major")` +
  `classify_weight`) → counterline/pad/bass texture → zero-drift landmark →
  `validate()` → `export_dual`.

## 6. Grid audit (pre-humanization — perfect == 0 off-grid on 16th)

| Voice | 16th grid (120) | 8th grid (240) |
|---|---|---|
| Lead | **0 / 253** | 142 / 253 |
| Counter | **0 / 128** | 0 / 128 |
| Accordion | **0 / 203** | 0 / 203 |
| Bass | **0 / 64** | 0 / 64 |

All pitched voices: **0 off-grid on the 16th grid** (the finest required grid).
The Lead 8th-grid non-zero count (142) is the 16th-note onsets that are on-grid
at 16th but off the coarser 8th grid — expected and correct.

## 7. Harmony audit (tiered — `workflows.pitch_audit.audit_voice`)

`strong_grid = (0, 960)`, `bar_ticks = 1920`, chord context per bar.

| Voice | status | audible | strong_ok | weak_in_scale | tagged | non_resolving | untagged_out | strong_viol |
|---|---|---|---|---|---|---|---|---|
| Lead | **PASS** | 253 | 27 | 226 | 0 | 0 | 0 | 0 |
| Counter | **PASS** | 128 | 0 | 128 | 0 | 0 | 0 | 0 |
| Accordion | **PASS** | 203 | 203 | 0 | 0 | 0 | 0 | 0 |
| Bass | **PASS** | 64 | 64 | 0 | 0 | 0 | 0 | 0 |

**0 untagged out-of-scale / 0 non-resolving / 0 strong violations / 0 collisions**
across all four pitched voices. No chromatic ornaments used (all material is
F-major chord/scale tone).

## 8. Humanization (always-on, style-derived, seeded)

`HZ_SEED = 263394711` (= `20261109 * 13 + 294`). Per-voice child seed =
`HZ_SEED * 101 + row`. Style "chanson" is explicit in `STYLE_HUMANIZE`
(timing 8 ms, vel σ 6, phrase_corr 0.45, layback 2 ms) — the melodic voices
(Violin/Clarinet/Accordion) return `None` for timing/layback in their DNA, so
the style wins; Double Bass overrides to its bass-role DNA (timing 10 ms,
layback +8 ms).

| Voice | timing (ms) | vel σ | layback (ms) | dur σ | mean shift (ticks) | max shift | vel delta |
|---|---|---|---|---|---|---|---|
| Lead | 8.0 | 6.0 | 2.0 | 0.030 | 3.00 | 12 | 4.37 |
| Counter | 8.0 | 7.0 | 2.0 | 0.020 | 3.21 | 9 | 5.36 |
| Accordion | 8.0 | 5.0 | 2.0 | 0.015 | 4.62 | 10 | 3.85 |
| Bass | 10.0 | 6.0 | **8.0** | 0.030 | **5.27** | 13 | 4.89 |

Bass (bass-role double bass) lays back +8 ms → largest mean shift (5.27 ticks),
matching the instrument-role DNA contract (bass lags, melodic voices sit on the
style timing).

## 9. Dual-version contract (perfect vs humanized)

- `-perfect.mid`: grid-locked, **0 off-grid** onsets (16th).
- `-humanized.mid`: **597 off-grid** onsets (16th) — proves the humanizer ran.
- `-phase1.mid`: 252 off-grid (raw draft, un-humanized by construction).

## 10. Zero-drift

`validate()` returns **OK on both phases** (equal-length tracks, terminal
landmark `MusicEvent(0,0,SECTION_TICKS-1,SECTION_TICKS)`). mido readback
confirms every note track totals **61,440 ticks** (32 bars × 1920) for the
perfect, humanized, and phase-1 exports — no drift.

## 11. Render + master (all three versions)

SoundFont: `FluidR3_GM.sf2` (via `discover_soundfont()`). FluidSynth
`-ni -g 1.2 -R no -C no`. Target = `target_for_style("chanson")` = **−14.0 LUFS**,
−1 dBTP ceiling.

| Version | LUFS | dBTP | silence | OGG (bytes) | WAV (bytes) |
|---|---|---|---|---|---|
| perfect | −14.0 | −1.65 | 2.11 % | 731,104 | 19,215,404 |
| humanized | −14.0 | −1.74 | 2.12 % | 735,001 | 19,224,620 |
| phase1 | −14.0 | −1.0 | 4.41 % | 894,374 | 19,212,332 |

Silence ratio is the ~2 s tail after the last note (RMS-per-second map holds
~0.07–0.20 throughout, dropping to ~0.0001 only in the final second — no
mid-track gaps). `perfect`/`humanized` peak at −1.65/−1.74 dBTP rather than the
−1 ceiling: the sustained accordion+bass texture reaches −14 LUFS before its
peak approaches the ceiling — correct `master()` behaviour (true-peak is a
*ceiling*, not a target).

## 12. File paths

```
/opt/data/projects/Styles/Chanson/294-chanson-narrative-arc/
├── compose.py
├── render_audio.py
├── verify.py
├── README.md
├── REPORT.md
├── MIDI/
│   ├── 294-chanson-narrative-arc-phase1.mid      (2,229 B)
│   ├── 294-chanson-narrative-arc-perfect.mid     (5,457 B)
│   ├── 294-chanson-narrative-arc-humanized.mid   (5,458 B)
│   └── *.provenance.json  (×3)
├── Audio/
│   ├── 294-chanson-narrative-arc-{perfect,humanized,phase1}.wav
│   ├── 294-chanson-narrative-arc-{perfect,humanized,phase1}.ogg
│   └── master_stats.json
└── Analysis/
    ├── grid_visualization.txt
    ├── manifest.json
    └── readback.json
```

## 13. Fixes / notes

- Used the engine tiered quantizer (`ScaleQuantizer(root=53, scale="major")` +
  `classify_weight`) — no hand-rolled `% 7` diatonic wrappers.
- Kept harmony strictly F-major diatonic (all chord pcs are scale tones), so no
  chromatic anywhere — the tiered audit is airtight (0/0/0/0).
- Phase-1 pitch is the raw narrative-arc contour (register center + intra-verse
  arc + drift); phase-2 strong beats snap to the bar's triad, weak beats to the
  F-major scale — the "register-planned" arc survives as the pitch envelope.
- Chanson matches the `strophic` FORM_PALETTE hint, so `pick_form("chanson")`
  resolved to a 4×8-bar strophic layout (not verse-chorus).
- Background render used the explicit `$MUSICOM_ENV/bin/python` path (the bare
  `$MUSICOM_PYTHON` var was not sourced in the background shell → "Permission
  denied" on first attempt); foreground compose/verify ran fine.
