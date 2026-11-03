# SP-107 Bit Crusher / Fidelity Reducer — 062-brownian-chorale

**Job:** random-style production (SP methods) — LAYER-ALIGNED
**Date:** 2026-11-03  **Seed:** 20261103

## Selection

| Field | Value |
|---|---|
| Registry source | `workflows.musicom_workflow.SP_METHODS` — the **implemented** dict (79 registered), NOT `methods_db.md` spec-only, NOT stale ranges |
| Method | `SP-107` |
| Module | `sound.effects.bit_crusher` → `BitCrusher`, `FidelityConfig` |
| Description | Bit Crusher / Fidelity Reducer — linked sample-rate/bit-depth macro, Iron/Worn character voicing, aliasing foldover emphasis (Modbap Fidelity Theory-style) |
| Layer | ABSOLUTE — one "fidelity coordinate" (linked SR + bit-depth) + Worn character voicing + ring foldover applied to the whole FluidSynth dry mix; no new notes written |
| Recent excluded (7d) | 42 methods (SP-009…SP-127; mtimes touched by nightly auto-sync, pool still 39) |
| Baseline excluded | SP-001 (carrier) |
| Pool size | 39 |

**Source composition:** `Styles/Experimental/062-brownian-chorale/MIDI/062-brownian-chorale.mid`
- 8-bar four-voice Brownian chorale, **C natural minor** (C D Eb F G Ab Bb), **84 BPM**, 4/4, TPB 480, 8 bars = 15360 ticks = 22.86 s nominal.
- 3 flute voices (program 74, channels 0/1/2 — soprano/alto/tenor) + fingered bass (program 33, channel 3). 96 notes = 12/bar, all durations 456 ticks (uniform chorale texture).
- Per-bar sonority (4-voice homophony): **Cm · Ab · Eb · Bb · Cm · Ab · Eb · Cm** (i · VI · III · VII · i · VI · III · i in C minor).

## PRE-FLIGHT AUDIT (3-rule gate)

| Rule | Count (before) | Count (after) | Verdict |
|---|---|---|---|
| Grid sync (8th = 240 ticks) | **0 off-grid** | 0 | PASS |
| Harmony — in scale (C natural minor) | **0 out-of-scale** | 0 | PASS |
| Harmony — chord tone of bar | **0 out-of-chord** | 0 | PASS |
| Zero-drift (note tracks equal length) | [0,15360,15360,15360,15360] | equal | PASS |

**Rework applied: NONE.** The Brownian chorale was authored against musicom's
two-phase rules and already passes the gate cleanly on first inspection —
every onset sits on the 8th-note grid, every pitch class lies in C natural
minor and is a chord tone of its bar's sonority, and all four note tracks
share the exact 15360-tick length (zero-drift intact).

`MIDI/composition.mid` = byte copy of source; `MIDI/source_original.mid` =
byte copy preserved. Re-audit recorded in `Analysis/rework_audit.json`.

## Layer discipline (absolute)

SP-107 is a fidelity-reduction pass: the FluidSynth dry render (SP-001
carrier, 3× flute 74 + fingered bass 33) is routed through a single
`BitCrusher` with one **fidelity coordinate** — linked sample-rate + bit-depth
reduction — plus Worn character voicing and a subtle ring-foldover aliasing
emphasis. No per-voice variation (per-track application is a later refinement).

| Param | Value |
|---|---|
| fidelity coordinate | 0.30 → **18 600 Hz / 9-bit** (linked SR × bit-depth) |
| mode | `worn` (800 Hz low-mid emphasis + softened highs + asymmetric saturation) |
| ring | 0.15 (aliasing foldover emphasis) |
| mix | 1.0 (full wet) |
| carrier | FluidSynth SP-001, `-R 0 -C 0 -g 1.2` (dry) |
| mastering | `normalize_to_lufs(-14.0)` → `Limiter(-1 dBTP)` LAST |

The linked coordinate halves the sample rate to ~18.6 kHz (bandwidth ≈ 9.3 kHz)
and drops bit depth to 9 (quantization noise floor ≈ −48 dB), giving the clean
chorale a warm lo-fi "worn tape" grain while Worn mode's 800 Hz emphasis keeps
the choir body present and the ring foldover adds a faint metallic sheen.

## Verification

| Metric | Value | Verdict |
|---|---|---|
| Pitch (FFT dominant peak / 0.5 s window, 50–1000 Hz) | **hit 1.0000** (50/50 valid windows) | PASS |
| Harmonic energy (first 8 harmonics of dom. peak) | **0.3310** wet / 0.4435 dry (retention 0.746) | PASS (≥ 0.30) |
| Pitch classes | ⊆ C natural minor {0,2,3,5,7,8,10} | PASS |
| Silence ratio | **0.19%** (release tail only) | PASS (< 30%) |
| RMS | 0.1580 | — |
| Integrated LUFS | **−14.00** | on target (experimental → −14) |
| True peak | 0.5841 (−4.7 dBTP; below −1 dB ceiling, correct for a non-peaky sustained texture) | PASS |
| Zero-drift | all 4 note tracks span exactly 15360 ticks | PASS |

Per-second RMS map: steady choral texture through the 8 bars, then FluidSynth
release tail; no mid-track gaps. Bit-crush quantization noise lowers harmonic
energy 44.4% → 33.1% (expected fidelity loss) but pitch tracking stays
perfect (fundamentals + first 8 harmonics all below the 9.3 kHz bandwidth limit).

## Files

| Path | Size | Role |
|---|---|---|
| `SP107-bitcrusher-062-brownian-chorale.wav` | 4 421 676 B | mastered full mix (stereo 44.1 kHz, 25.07 s) |
| `SP107-bitcrusher-062-brownian-chorale.ogg` | 135 681 B | Opus 48k voip (delivery) |
| `dry_full_mix_reference.wav` | 4 421 676 B | pre-crush dry reference |
| `Audio/stems_dry/track0{0,1,2}_Recorder.wav` | — | 3 flute stems (program 74 → "Recorder") |
| `Audio/stems_dry/track03_Electric_Bass_finger.wav` | — | bass stem (program 33) |
| `Audio/stems_dry/full_mix_CRUSH.wav` | 4 421 676 B | crushed (pre-master) full mix |
| `MIDI/composition.mid` | byte copy | normalized source (no rework) |
| `MIDI/source_original.mid` | byte copy | original source preserved |
| `provenance.json`, `Analysis/render_stats.json`, `Analysis/rework_audit.json` | — | records |

## Verdict

SP-107 applied as an absolute-layer fidelity-reduction pass on an 8-bar
C-minor four-voice Brownian chorale. Pre-flight found the source already
clean (0 off-grid / 0 out-of-scale / 0 out-of-chord / zero-drift) — no rework
needed. Single fidelity coordinate 0.30 (18.6 kHz / 9-bit) + Worn voicing +
0.15 ring foldover degrades the FluidSynth dry render into a warm lo-fi
chorale. Pitch verifies clean (FFT hit 1.000, harmonic energy 0.331 — retained
0.746 of dry), silence 0.19% (tail-only), mastered to −14 LUFS / 0.584 peak.

**Method-adaptation note (for the next SP-107 run):** `normalize_to_lufs`,
`measure_lufs`, and `Limiter` in `sound.effects.mastering` all expect
**time-major (N, 2)** arrays. Passing channel-major (2, N) makes the LUFS
meter read the 2-sample "time" axis as silence (−70 LUFS) and apply a huge
+ gain, slamming the limiter. Fix: `.T` to time-major before the mastering
stage (already corrected in `Scripts/produce_sp107_cron.py`).