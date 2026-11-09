# REPORT — 292 Gamelan Isorhythmic Talea-Color

**Nightly composition job (ID 1fc3fd65d359) · 2026-11-08 · Method 032 (concrete layer)**

## 1. Selection (LAYERED METHODOLOGY)

| Field | Value |
|---|---|
| Style | **Gamelan** (46 candidate genre folders) |
| Method | **032 — Isorhythmic Talea-Color Mapping (ITCM)** (Rules-Based) |
| Layer | **concrete** (weekly abstract cadence not due; last abstract was 287 on 11-05) |
| Form | **through-composed** → sections `S1…S6`, bars `[4×6]` = **24 bars** (from `pick_form("gamelan")` — gamelan has no FORM_PALETTE hint, falls to the through-composed default, which fits the non-repeating colotomic gong cycle) |
| Key / mode | **C major pentatonic (sléndro)** — C D E G A (PC set {0,2,4,7,9}) |
| Tempo | 100 BPM · 4/4 · 480 TPB (bar = 1920, 8th = 240, 16th = 120) |

Method pool: concrete non-AI candidates, excluding the abstract layer
{95,99,104,113,127,131,133,134}, impractical AI-driven methods
{42,46,47,54,57,60,62,63,72,74,85,100,101,103,106,108,110,118}, and methods used
in the last 7 days {11,13,15,18,21,31,45,48,69,98,131}.

## 2. Concept — Isorhythmic Talea-Color Mapping (Method 032)

Method 032 decouples a **talea** (fixed rhythm) from a **color** (fixed pitch
sequence). Chosen **coprime** lengths make the two cycles drift out of phase and
realign only at their least common multiple:

- **Color** (5): `[C E A G D]` = pitch-class degrees `[0 2 4 3 1]` → MIDI
  `[72 76 81 79 74]` (an arch over C-major pentatonic).
- **Talea** (7): durations `[2 3 2 2 3 2 2]` sixteenths (sum = 16 = 1 bar).
- **LCM(5, 7) = 35** → the pitch/rhythm pairing shifts every bar and realigns
  only after 35 notes.

Mapped onto a **gamelan** texture — the isorhythmic line is the *balungan*
(core melody), over a colotomic *gong* cycle, an interlocking *kotekan*
16th-note figuration, and a sustained *saron* "sléndro trichord" pad.

## 3. Voices + Instruments (instrument registry — source of truth)

| Voice | Instrument | Program | Channel | Role |
|---|---|---|---|---|
| Balungan | Marimba | 12 | 0 | isorhythmic talea×color melody |
| Kotekan | Steel Drums | 114 | 1 | interlocking 16th figuration (gamelan interlock) |
| Saron | Celesta | 8 | 2 | sustained sléndro trichord per bar |
| Gong | Double Bass | 43 | 3 | colotomic low gong root (1/bar) |

## 4. Harmony (colotomic gong cycle, through-composed)

C-major-pentatonic "sléndro trichords" only — every chord pc is a pentatonic
scale tone, so the tiered audit is trivially satisfiable (no chromatic
anywhere). Each bar's trichord stacks every-other pentatonic degree around the
gong root (`{d, d+2, d+4} mod 5`):

```
gong degree cycle (24 bars):
  S1: C  G  E  C        S2: A  E  D  A
  S3: E  C  G  E        S4: D  A  C  D
  S5: G  D  A  G        S6: C  G  A  C
```

| Gong degree | Sléndro trichord (pcs) | names |
|---|---|---|
| 0 (C) | {0,4,9} | C E A |
| 1 (D) | {2,7,0} | D G C |
| 2 (E) | {4,9,2} | E A D |
| 3 (G) | {7,0,4} | G C E |
| 4 (A) | {9,2,7} | A D G |

## 5. Two-phase architecture

- **Phase 1** (`-phase1.mid`): raw generative draft — single-voice isorhythmic
  COLOR×TALEA stream with OFF-GRID onset jitter (±0.14 step) and unquantized
  pitch drift (±1.6 st). No harmony/kotekan/saron/gong. 167 audible events,
  162/167 off-grid (unquantized by design).
- **Phase 2** (`-perfect.mid` + `-humanized.mid`): grid-lock to 16th → tiered
  pitch discipline (`ScaleQuantizer(root=60, scale="pentatonic")` +
  `classify_weight`) → kotekan/saron/gong texture → zero-drift landmark →
  `validate()` → `export_dual`.

## 6. Grid audit (pre-humanization — perfect == 0 off-grid on 16th)

| Voice | 16th grid (120) | 8th grid (240) |
|---|---|---|
| Balungan | **0 / 167** | 72 / 167 |
| Kotekan | **0 / 384** | 192 / 384 |
| Saron | **0 / 159** | 0 / 159 |
| Gong | **0 / 24** | 0 / 24 |

All pitched voices: **0 off-grid on the 16th grid** (the finest required grid).
The Balungan/Kotekan 8th-grid non-zero counts are the 16th-note onsets that are
on-grid at 16th but off the coarser 8th grid — expected and correct.

## 7. Harmony audit (tiered — `workflows.pitch_audit.audit_voice`)

`strong_grid = (0, 960)`, `bar_ticks = 1920`, chord context per bar.

| Voice | status | audible | strong_ok | weak_in_scale | tagged | non_resolving | untagged_out | strong_viol |
|---|---|---|---|---|---|---|---|---|
| Balungan | **PASS** | 167 | 23 | 144 | 0 | 0 | 0 | 0 |
| Kotekan | **PASS** | 384 | 48 | 336 | 0 | 0 | 0 | 0 |
| Saron | **PASS** | 159 | 159 | 0 | 0 | 0 | 0 | 0 |
| Gong | **PASS** | 24 | 24 | 0 | 0 | 0 | 0 | 0 |

**0 untagged out-of-scale / 0 non-resolving / 0 strong violations / 0 collisions**
across all four pitched voices. No chromatic ornaments used (all material is
pentatonic chord/scale tone).

## 8. Humanization (always-on, style-derived, seeded)

`HZ_SEED = 263394696` (= `20261108 * 13 + 292`). Per-voice child seed =
`HZ_SEED * 101 + row`. Style "gamelan" has no entry in `STYLE_HUMANIZE`, so it
uses the default profile (timing 7 ms, layback 1 ms) for melodic voices; the
instrument-role DNA governs the rhythm section.

| Voice | timing (ms) | vel σ | layback (ms) | dur σ | mean shift (ticks) | max shift | vel delta |
|---|---|---|---|---|---|---|---|
| Balungan | 7.0 | 5.0 | 1.0 | 0.010 | 3.75 | 12 | 3.86 |
| Kotekan | 2.0 | 4.0 | 0.0 | 0.008 | **1.05** | 5 | 3.07 |
| Saron | 7.0 | 5.0 | 1.0 | 0.015 | 3.88 | 13 | 3.89 |
| Gong | 10.0 | 6.0 | 8.0 | 0.030 | **9.04** | 21 | 4.88 |

Kotekan (percussion-role steel drums) anchors tightest (0 layback, ~1 tick);
Gong (bass-role double bass) lays back +8 ms (largest mean shift 9.04) — matches
the instrument-role DNA contract.

## 9. Dual-version contract (perfect vs humanized)

- `-perfect.mid`: grid-locked, **0 off-grid** onsets (16th).
- `-humanized.mid`: **576 off-grid** onsets (16th) — proves the humanizer ran.
- `-phase1.mid`: 162 off-grid (raw draft, un-humanized by construction).

## 10. Zero-drift

`validate()` returns **OK on both phases** (equal-length tracks, terminal
landmark `MusicEvent(0,0,SECTION_TICKS-1,SECTION_TICKS)`). mido readback
confirms the four note tracks are length-consistent (~44.2k–46.0k ticks of
46,080 total; the per-voice last-note spread is intrinsic, not drift).

## 11. Render + master (all three versions)

SoundFont: `FluidR3_GM.sf2` (via `discover_soundfont()`). FluidSynth
`-ni -g 1.2 -R no -C no`. Target = `target_for_style("gamelan")` = **−14.0 LUFS**,
−1 dBTP ceiling.

| Version | LUFS | dBTP | silence | OGG (bytes) | WAV (bytes) |
|---|---|---|---|---|---|
| perfect | −14.0 | −1.0 | 4.46 % | 511,962 | 10,656,556 |
| humanized | −14.0 | −1.0 | 4.43 % | 510,238 | 10,658,092 |
| phase1 | −14.0 | −4.15 | 5.59 % | 610,257 | 10,653,740 |

Silence ratio is the ~2 s tail after the last note (RMS-per-second map holds
~0.10–0.21 throughout with a drop to ~0.0003 only in the final two seconds — no
mid-track gaps). `phase1` peaks at −4.15 dBTP rather than the −1 ceiling: a
sparse single-voice marimba draft reaches −14 LUFS of loudness before its peak
approaches the ceiling — correct `master()` behaviour (true-peak is a *ceiling*,
not a target).

## 12. File paths

```
/opt/data/projects/Styles/Gamelan/292-gamelan-talea-color/
├── compose.py
├── render_audio.py
├── verify.py
├── README.md
├── REPORT.md
├── MIDI/
│   ├── 292-gamelan-talea-color-phase1.mid      (1,521 B)
│   ├── 292-gamelan-talea-color-perfect.mid     (5,940 B)
│   ├── 292-gamelan-talea-color-humanized.mid   (5,939 B)
│   └── *.provenance.json  (×3)
├── Audio/
│   ├── 292-gamelan-talea-color-{perfect,humanized,phase1}.wav
│   ├── 292-gamelan-talea-color-{perfect,humanized,phase1}.ogg
│   └── master_stats.json
└── Analysis/
    ├── grid_visualization.txt
    ├── manifest.json
    └── readback.json
```

## 13. Fixes / notes

- Used the engine tiered quantizer (`ScaleQuantizer(root=60, scale="pentatonic")`
  + `classify_weight`) — no hand-rolled `% 7`/`% 5` diatonic wrappers.
- Kept harmony strictly C-major-pentatonic (sléndro trichords = pentatonic
  subsets), so no chromatic anywhere — the tiered audit is airtight.
- Phase-1 pitch is the fixed COLOR (anchored C5) with drift; phase-2 strong
  beats snap to the bar's sléndro trichord, weak beats stay pentatonic (the
  fixed color is preserved on weak beats — the "color is fixed" isorhythmic premise).
- Gamelan has no `FORM_PALETTE` style hint, so `pick_form("gamelan")` resolved
  to `through-composed` (no exact section repeat) — a good fit for the
  non-repeating colotomic gong cycle.