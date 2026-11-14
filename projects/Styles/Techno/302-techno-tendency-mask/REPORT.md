# REPORT — 302 Techno Tendency Mask

**Nightly composition job (ID 1fc3fd65d359) · 2026-11-13 · Method 023 (concrete layer)**

## 1. Selection (LAYERED METHODOLOGY)

| Field | Value |
|---|---|
| Style | **Techno** (47 candidate genre folders) |
| Method | **023 — Tendency Masking Stochastic Bounds (TM-SB)** (Stochastic) |
| **Layer** | **concrete** (weekly abstract cadence not due — last abstract composition was 300 on 11-12, one day ago) |
| Form | **intro-break-drop-outro** → sections `Intro·Break·Drop·Outro`, bars `[4,8,8,4]` = **24 bars** (from `pick_form("techno")` — techno matches the intro-break-drop hint) |
| Seed | 20261113 · humanize seed 263394771 · form seed 202611137 |

Method pool: concrete non-AI candidates, excluding the abstract layer
{95,99,104,113,127,131,133,134,139}, the AI-Driven methods
{42,46,47,54,57,60,62,63,72,74,85,100,101,103,106,108,110,118,140}, and the
last-7-days methods {1,7,13,15,31,32,41,45,53,120,134} → 102 candidates.

## 2. Method 023 — Tendency Masking Stochastic Bounds

A stochastic pitch walk whose **every step is bounded by a dynamic tendency
mask**: a per-section lower/upper frequency envelope `[lo(t), hi(t)]` that opens
and closes across a section (filter-sweep gesture). The raw walk is clipped into
the band at each step. The mask — not the individual notes — is the musical idea.

| Section | lo start→end | hi start→end | band width start→end | Gesture |
|---|---|---|---|---|
| Intro  | 45→43 | 60→74 | 29→17 | opening |
| Break  | 48→50 | 58→66 | 18→8  | narrow breakdown |
| Drop   | 57→62 | 84→96 | 39→22 | wide open, peak energy |
| Outro  | 62→55 | 96→68 | 6→41  | closing / collapse |

Phase-1 mean pitch per section: Intro 60.59 · Break 52.56 · Drop 64.42 · Outro
79.31 — the breakdown visibly collapses the band (mean −8 vs Intro), the Drop
re-opens it. Max leap per section: 9 / 5 / 9 / 7 (stochastic small-steps with
rare leaps, bounded by the mask).

## 3. Key, tempo, instruments

- **Key**: A natural minor, `{0,2,4,5,7,9,11}` = A B C D E F G. Tonic A3 (57).
- **Tempo**: 128 BPM, 4/4, TPB 480 (BAR = 1920).

| Voice | Instrument | GM | Channel | Role |
|---|---|---|---|---|
| Lead | Singing Saw | 81 | 0 | tendency-masked saw lead |
| Bass | Synth Bass 1 | 38 | 1 | offbeat 8th pump (Drop), root/fifth elsewhere |
| Pad | Synth Pad | 88 | 2 | breakdown pad (Break/Intro/Outro, silent in Drop) |
| Stab | Synth Brass 1 | 62 | 3 | offbeat rave stab (Drop only) |
| Drums | Drum Kit | 0 | 9 | 4-on-floor kick, offbeat open hat, clap, 16th closed hat |

All from `projects/Instruments/instrument_registry.py` (source of truth).

## 4. Harmony — i · VI · VII (Am · F · G)

| Section | Progression |
|---|---|
| Intro  | Am Am Am Am |
| Break  | Am ×8 |
| Drop   | Am Am F G Am Am F G |
| Outro  | Am Am Am Am |

Minimal techno pedal on Am; the VI→VII lift only in the Drop's second half is
the harmonic "filter open" moment, matching the tendency-mask widening.

## 5. Two-phase pipeline

**Phase 1** (raw): single saw-lead voice, stochastic walk clipped into the
tendency mask, off-grid onset jitter (±14 ticks), unquantized chromatic pitch,
no harmony. Exported `302-techno-tendency-mask-phase1.mid` (own zero-drift
gate). **187 off-grid onsets** — deliberately imperfect.

**Phase 2** (rules): grid-lock lead to 8th grid → tiered snap (`ScaleQuantizer`
root A + `classify_weight`: strong beat → bar chord tone, weak → A-minor scale
tone) → full techno texture (bass/pad/stab/drums) → landmark → `validate()`.
Exported via `export_dual` → `-perfect.mid` + `-humanized.mid`.

## 6. Grid audit (pre-humanization, phase 2)

| Voice | 16th off-grid | 8th off-grid |
|---|---|---|
| Lead | 0/191 | 0/191 |
| Bass | 0/88 | 0/88 |
| Pad | 0/112 | 0/112 |
| Stab | 0/104 | 0/104 |

**Perfect layer: 0 off-grid on every pitched voice** ✓ (the 16th closed-hats
in Drums sit on the 16th grid — `off16 == 0` globally, `off8 == 64` are the
legitimate odd-16th hats).

## 7. Harmony audit (tiered pitch discipline)

`workflows.pitch_audit.audit_voice` per pitched voice (strong_grid = 4/4 beats
1&3, bar 1920, grid 240):

| Voice | total | strong_ok | weak_in_scale | untagged_out | non_resolving | strong_viol | PASS |
|---|---|---|---|---|---|---|---|
| Lead | 191 | 48 | 143 | 0 | 0 | 0 | ✓ |
| Bass | 88 | 40 | 48 | 0 | 0 | 0 | ✓ |
| Pad | 112 | 112 | 0 | 0 | 0 | 0 | ✓ |
| Stab | 104 | 0 | 104 | 0 | 0 | 0 | ✓ |

All voices: **0 untagged out-of-scale, 0 non-resolving ornaments, 0 strong
violations** ✓. No chromatic ornaments used (techno is chromatic-free; the
lead's chromatic raw walk is fully snapped to scale/chord tones).

## 8. Humanization (always-on, seeded, dual-version)

`export_dual(style="techno", seed=263394771)` — per-voice instrument DNA from
the registry; techno profile governs melodic timing (tight 2 ms):

| Voice | timing σ ms | vel σ | layback ms | mean\|shift\| (ticks) | max\|shift\| | mean\|velΔ\| |
|---|---|---|---|---|---|---|---|
| Lead | 2.0 | 9.0 | 0 | 1.466 | 5 | 6.623 |
| Bass | 5.0 | 4.0 | 8.0 | 8.057 | 19 | 3.023 |
| Pad | 2.0 | 4.0 | 0 | 1.706 | 5 | 3.250 |
| Stab | 2.0 | 4.0 | 0 | 1.779 | 5 | 2.913 |
| Drums | 2.0 | 4.0 | 0 | 1.494 | 6 | 3.318 |

Drums anchor (2 ms / 0 layback), bass lays back (+8 ms), lead tight — all
within profile bounds. Deterministic per seed.

**Dual-version readback** (mido, read-only):

| Version | off-grid 16th | off-grid 8th | note-ons |
|---|---|---|---|
| perfect | **0** | 64 | 863 |
| humanized | **702** | 712 | 863 |

Perfect == 0 off-grid, humanized > 0 — proves the humanizer ran.

## 9. Zero-drift

`validate()` OK on both phases. Exported readback: all 6 tracks = **46080 ticks**
(24 bars × 1920), identical length. ✓

## 10. Render + master (all three)

FluidSynth (`FluidR3_GM.sf2`, `-g 1.2 -R no -C no`) → `master()` → Opus OGG.
Style target `target_for_style("techno")` = **−10.0 LUFS**, −1 dBTP ceiling.

| Version | target LUFS | measured LUFS | true peak dBTP | silence | OGG bytes |
|---|---|---|---|---|---|
| perfect | −10.0 | −11.21 | −1.0 | 10.74% | 348618 |
| humanized | −10.0 | −11.25 | −1.0 | 10.76% | 345886 |
| phase1 | −10.0 | −10.67 | −1.0 | 7.07% | 396158 |

Measured LUFS sits slightly below target because the −1 dBTP true-peak ceiling
is binding (dense 4-on-floor kick + stab) — the documented "true-peak is a
ceiling" behaviour, correct for a percussion-heavy piece. Silence is tail
padding after the last note (RMS map shows continuous 0.14–0.26 through the
music, then the final 5–6 s decay to ~0); no mid-track gaps.

## 11. Files

| Path | Size |
|---|---|
| `MIDI/302-techno-tendency-mask-phase1.mid` | 1750 B |
| `MIDI/302-techno-tendency-mask-perfect.mid` | 6861 B |
| `MIDI/302-techno-tendency-mask-humanized.mid` | 6849 B |
| `Audio/302-techno-tendency-mask-perfect.wav` | 9217068 B |
| `Audio/302-techno-tendency-mask-humanized.wav` | 9221676 B |
| `Audio/302-techno-tendency-mask-phase1.wav` | 8344620 B |
| `Audio/302-techno-tendency-mask-perfect.ogg` | 348618 B |
| `Audio/302-techno-tendency-mask-humanized.ogg` | 345886 B |
| `Audio/302-techno-tendency-mask-phase1.ogg` | 396158 B |

Plus `provenance.json` per MIDI, `Analysis/grid_visualization.txt`,
`Analysis/manifest.json`, `Analysis/readback.json`, `Audio/master_stats.json`,
`README.md`, `index.html`.

## 12. Fixes applied

None — first-pass clean. All gates green: validate, grid audit, tiered harmony
audit, zero-drift readback, humanization DNA, master loudness.
