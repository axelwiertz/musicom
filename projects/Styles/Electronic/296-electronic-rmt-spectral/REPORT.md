# REPORT — 296 Electronic RMTC Spectral

**Nightly composition job (ID 1fc3fd65d359) · 2026-11-10 · Method 120 (concrete layer)**

## 1. Selection (LAYERED METHODOLOGY)

| Field | Value |
|---|---|
| Style | **Electronic** (48 candidate genre folders) |
| Method | **120 — Random Matrix Theory Composition (RMTC)** (Stochastic) |
| Layer | **concrete** (weekly abstract cadence not due; last abstract composition was 287 on 11-05) |
| Form | **cinematic-build** → sections `Intro·Build·Rise·Peak·Resolve`, bars `[4,8,8,8,4]` = **32 bars** (from `pick_form("electronic", rng=default_rng(FORM_SEED))` — FORM_SEED = SEED·10+3 = 202611103) |
| Key / mode | **C natural minor** — C D Eb F G Ab Bb (PC set {0,2,3,5,7,8,10}) |
| Tempo | 128 BPM · 4/4 · 480 TPB (bar = 1920, 8th = 240, 16th = 120) |

Method pool: concrete non-AI candidates, excluding the abstract layer
{95,99,104,113,127,131,133,134,139}, the AI-Driven methods (042/046/047/054/057/
060/062/063/072/074/085/100/101/103/106/108/110/118), and methods used in the
last 7 days {7,11,13,15,18,21,31,32,41,45,48,69,98,131}.

## 2. Concept — Random Matrix Theory Composition (Method 120)

RMTC generates musical material from the **eigenvalue statistics of random
matrices**. Each section diagonalizes a matrix from one of the three classical
invariant ensembles, and the spectral properties are read as musical DNA:

- **Wigner semicircle law** → pitch distribution (eigenvalues are semicircle-
  distributed, so pitch density peaks at the tonic and vanishes at the extremes).
- **Wigner-surmise level repulsion** → melodic intervals. The nearest-neighbour
  spacing `P_β(s) → 0` as `s → 0`, so unison/zero-interval repeats are
  *suppressed by construction* — no explicit rule needed.
- **Ensemble β-switching** → macro-form. β=1 GOE (linear repulsion), β=2 GUE
  (quadratic), β=4 GSE (quartic, strongest — most evenly spaced).
- **Tracy–Widom largest eigenvalue λ_max** → the registral climax (Peak section
  lifts its lead ceiling).

Section plan (ensemble → matrix dimension → role):

| Section | Ensemble | β | N | Role |
|---|---|---|---|---|
| Intro (4) | GOE | 1 | 8 | sparse exposition |
| Build (8) | GUE | 2 | 12 | groove builds |
| Rise (8) | GUE | 2 | 16 | density rises |
| Peak (8) | GSE | 4 | 20 | **climax** — strongest repulsion + λ_max register |
| Resolve (4) | GOE | 1 | 8 | thinning return |

Measured λ_max per section: `{Intro 1.884, Build 1.856, Rise 1.579, Peak 1.872,
Resolve 1.200}`. Phase-1 measured per-section mean pitch proves the macro-arc
register climb: `{Intro 44.03 → Build 47.59 → Rise 50.86 → Peak 59.36 →
Resolve 48.28}`.

## 3. Voices + Instruments (instrument registry — source of truth)

| Voice | Instrument | Program | Channel | Role |
|---|---|---|---|---|
| Lead | Sawtooth synth lead | 81 | 0 | RMTC spectral contour, grid-locked + tiered snap |
| Bass | Synth bass 1 | 38 | 1 | root (beat 1) + fifth (beat 3) per bar |
| Pad | Synth pad | 88 | 2 | sustained triad per bar (spectral-rigidity voicing) |
| Arp | Calliope | 82 | 3 | 16th-note chord-tone arpeggio (denser in Rise/Peak) |
| Drums | Drum kit | — | 9 | four-on-the-floor kick + offbeat hat + clap |

## 4. Harmony (C natural minor)

`i – VI – III – VII` (Cm – Ab – Eb – Bb), the classic dark electronic
progression; the Resolve section ends `i – VII – VI – i` (cadential return).

| Degree | Triad (pcs) | Name | Root |
|---|---|---|---|
| i (1) | {0,3,7} | Cm | 36 |
| VI | {8,0,3} | Ab | 32 |
| III | {3,7,10} | Eb | 39 |
| VII | {10,2,5} | Bb | 34 |

All chord pcs are C-minor scale tones, so the tiered audit is fully satisfiable
with zero chromatic anywhere.

## 5. Two-phase architecture

- **Phase 1** (`-phase1.mid`): raw generative draft — single-voice saw lead.
  Per section: sample the ensemble matrix, diagonalize, build a chromatic
  contour from the eigenvalue spectrum (semicircle pitch pool + Wigner-surmise
  level-repulsion intervals). OFF-GRID onset jitter (±18 ticks) + unquantized
  chromatic pitch. No harmony/bass/pad/drums. 256 audible events, **253/256
  off-grid** (unquantized by design).
- **Phase 2** (`-perfect.mid` + `-humanized.mid`): grid-lock the lead to the
  8th grid (078 rule) → tiered pitch discipline (`ScaleQuantizer(root=48,
  scale="minor")` + `classify_weight`) → bass/pad/arp/drums texture → zero-drift
  landmark → `validate()` → `export_dual`.

## 6. Grid audit (pre-humanization — perfect == 0 off-grid on 16th)

| Voice | 16th grid (120) | 8th grid (240) |
|---|---|---|
| Lead | **0 / 248** | 0 / 248 |
| Bass | **0 / 64** | 0 / 64 |
| Pad | **0 / 208** | 0 / 208 |
| Arp | **0 / 384** | 128 / 384 |
| Drums | 0 / 320 | — (percussion) |

All pitched voices: **0 off-grid on the 16th grid**. The Arp 8th-grid non-zero
(128) is the 16th-note arpeggio onsets that are on-grid at 16th but off the
coarser 8th grid — expected and correct.

## 7. Harmony audit (tiered — `workflows.pitch_audit.audit_voice`)

`strong_grid = (0, 960)`, `bar_ticks = 1920`, chord context per bar.

| Voice | status | audible | strong_ok | weak_in_scale | tagged | non_resolving | untagged_out | strong_viol | collisions |
|---|---|---|---|---|---|---|---|---|---|
| Lead | **PASS** | 248 | 64 | 184 | 0 | 0 | 0 | 0 | 0 |
| Bass | **PASS** | 64 | 64 | 0 | 0 | 0 | 0 | 0 | 0 |
| Pad | **PASS** | 208 | 208 | 0 | 0 | 0 | 0 | 0 | 0 |
| Arp | **PASS** | 384 | 64 | 320 | 0 | 0 | 0 | 0 | 0 |

**0 untagged out-of-scale / 0 non-resolving / 0 strong violations / 0
collisions** across all four pitched voices. No chromatic ornaments used — all
material is C-minor chord/scale tone. (Lead/Arp "weak" counts are 8th/16th
off-beats snapped to the scale; strong counts are beats 1&3 snapped to the
bar's triad.)

## 8. Humanization (always-on, style-derived, seeded)

`HZ_SEED = 263394726` (= `20261110 * 13 + 296`). Per-voice child seed =
`HZ_SEED * 101 + row`. Style "electronic" is not an explicit `STYLE_HUMANIZE`
key, so `profile_for_style` returns the default profile (timing 7 ms, vel σ 6,
phrase_corr 0.4, layback 1 ms); melodic-voice DNA returns `None` for
timing/layback so the style timing wins; Bass overrides to bass-role DNA
(timing 5 ms, layback +8 ms); Drums anchor (2 ms / 0 layback).

| Voice | timing (ms) | vel σ | layback (ms) | dur σ | mean shift (ticks) | max shift | vel delta |
|---|---|---|---|---|---|---|---|
| Lead | 7.0 | 9.0 | 1.0 | 0.040 | 4.69 | 18 | 7.36 |
| Bass | 5.0 | 4.0 | **8.0** | 0.010 | **7.59** | 17 | 3.09 |
| Pad | 7.0 | 4.0 | 1.0 | 0.010 | 6.42 | 19 | 3.44 |
| Arp | 7.0 | 4.0 | 1.0 | 0.010 | 4.69 | 18 | 3.16 |
| Drums | **2.0** | 4.0 | **0.0** | 0.008 | **1.33** | 7 | 3.22 |

Drums are tightest (mean shift 1.33 ticks, 0 layback) and bass lays back the
most (+8 ms → 7.59 ticks) — exactly the instrument-role DNA contract.

## 9. Dual-version contract (perfect vs humanized)

- `-perfect.mid`: grid-locked, **0 off-grid** onsets (16th).
- `-humanized.mid`: **1089 off-grid** onsets (16th) — proves the humanizer ran.
- `-phase1.mid`: 253 off-grid (raw draft, un-humanized by construction).

## 10. Zero-drift

`validate()` returns **OK on both phases** (equal-length tracks, terminal
landmark `MusicEvent(0,0,SECTION_TICKS-1,SECTION_TICKS)`). mido readback: every
note track totals **61,440 ticks** (32 bars × 1920) in the perfect, humanized,
and phase-1 exports — no drift.

## 11. Render + master (all three versions)

SoundFont: `FluidR3_GM.sf2` (via `discover_soundfont()`). FluidSynth
`-ni -g 1.2 -R no -C no`. Target = `target_for_style("electronic")` = **−14.0
LUFS** (fallback — "electronic" has no explicit key in the genre map; the
nearest dance keys are techno −10 / edm −9, but the contract uses
`target_for_style(style)`), −1 dBTP ceiling.

| Version | LUFS | dBTP | silence | dur | OGG (B) | WAV (B) |
|---|---|---|---|---|---|---|
| perfect | −14.25 | −1.0 | 8.57 % | 67.2 s | 433,735 | 11,861,036 |
| humanized | −14.27 | −1.0 | 8.58 % | 67.3 s | 434,151 | 11,864,876 |
| phase1 | −14.1 | −1.0 | 5.18 % | 62.2 s | 541,267 | 10,975,276 |

Silence is the ~7 s tail after the final chord (sustained synth-pad release
rings out ~6 s past the 60 s of notated music): the RMS-per-second map holds
0.12–0.17 through seconds 0–59, drops to ~0.015 at second 60 (final pad
decay), then near-silent seconds 61–67 — **no mid-track gaps**. `perfect`/
`humanized` hit the −1.0 dBTP ceiling exactly (four-on-the-floor kick + dense
drop drives peaks to the limiter) and land at −14.25/−14.27 LUFS against the
−14.0 target — correct `master()` behaviour (true-peak ceiling stops further
gain; the integrated loudness sits within 0.3 LUFS of target).

## 12. File paths

```
/opt/data/projects/Styles/Electronic/296-electronic-rmt-spectral/
├── compose.py
├── render_audio.py
├── verify.py
├── README.md
├── REPORT.md
├── index.html
├── MIDI/
│   ├── 296-electronic-rmt-spectral-phase1.mid      (2,293 B)
│   ├── 296-electronic-rmt-spectral-perfect.mid     (10,111 B)
│   ├── 296-electronic-rmt-spectral-humanized.mid   (10,115 B)
│   └── *.provenance.json  (×3)
├── Audio/
│   ├── 296-electronic-rmt-spectral-{perfect,humanized,phase1}.wav
│   ├── 296-electronic-rmt-spectral-{perfect,humanized,phase1}.ogg
│   └── master_stats.json
└── Analysis/
    ├── grid_visualization.txt
    ├── manifest.json
    └── readback.json
```

## 13. Fixes / notes

- Used the engine tiered quantizer (`ScaleQuantizer(root=48, scale="minor")` +
  `classify_weight`) — no hand-rolled `% 7` diatonic wrappers.
- Kept harmony strictly C-minor diatonic (all chord pcs are scale tones), so
  no chromatic anywhere — the tiered audit is airtight (0/0/0/0).
- **Lead collision fix**: the first pass left 7 duplicate (onset, pitch) pairs
  where two raw 8th-notes collapsed to the same grid position + same snapped
  chord tone. Added a post-snap `(start_tick, pitch)` dedup → collisions 0.
- RMTC GSE implemented as the real 2N×2N quaternion self-dual matrix (not a
  β-approximation), so the β=4 quartic repulsion is authentic.
- Form landed on cinematic-build (not verse-chorus) via `pick_form("electronic")`
  with a seeded rng — the λ_max climax in the Peak section maps 1:1 onto the
  form's Peak.
