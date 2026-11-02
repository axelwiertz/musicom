# SP-080 Cadence Engine Rhythmic Variator — 034-irish-jig-study

**Job:** random-style production (SP methods) — LAYER-ALIGNED
**Date:** 2026-11-02  **Seed:** 20261102

## Selection

| Field | Value |
|---|---|
| Registry source | `workflows.musicom_workflow.SP_METHODS` (79 registered) — the **implemented** dict, NOT `methods_db.md` spec-only, NOT stale ranges |
| Method | `SP-080` |
| Module | `sound.generators.cadence_variator` → `CadenceEngine`, `FluxRandomizer`, `CadenceLayer` |
| Description | Cadence Engine Rhythmic Variator w/ Flux Randomizer (Emergence Audio Envoy-style) |
| Layer | ABSOLUTE — two CadenceLayers drive time-varying gain/pan/LP-filter modulation over the whole piece's dry render |
| Recent excluded (7d) | SP-111, SP-115, SP-092, SP-127, SP-109, SP-094 |
| Also excluded | SP-075 (voice-like hybrid — inapplicable to a single flute melody; first random roll re-rolled), SP-001 (baseline carrier) |
| Pool size | 71 |

**Source composition:** `Styles/"Celtic / Irish Traditional"/034-irish-jig-study/MIDI/irish_jig.mid`
- 6-bar Irish jig, **G major** (G A B C D E F#), **120 BPM**, 4/4, TPB 480, 6 bars = 11520 ticks = 12.0 s.
- Single flute melody (channel 0, program 73). 56 onsets = **48 structural 8th notes** + **8 ornament "cut" grace notes** (+30-tick offset, velocity 90) — authentic Irish ornamentation.
- Beat-1 harmonic anchors → progression: **G · D · C · G · C · D**.

## PRE-FLIGHT AUDIT (3-rule gate)

| Rule | Count (before) | Count (after) | Verdict |
|---|---|---|---|
| Grid sync (8th = 240 ticks) | **8 off-grid** | 0 | FAIL → reworked |
| Harmony — in scale (G major) | **2 out-of-scale** | 0 | FAIL → reworked |
| Harmony — chord tone (beat-1 anchor) | **1 out-of-chord** | 0 | FAIL → reworked |
| Zero-drift (note tracks equal length) | [11520] single track | [11520] | PASS |

**Rework applied (two-phase, composition fixed FIRST):**
1. **Grid** — dropped the 8 ornament "cut" grace notes (start tick % 240 == 30,
   velocity 90). They are non-structural Irish ornaments; the 48 structural
   melody notes already sit on the 8th-note grid (0 off-grid after).
2. **Harmony** — snapped two chromatic leading tones into G major:
   C#5 (note 73, bar 4 beat 1) → **D5 (74)**, and G#4 (note 68, bar 6) →
   **A4 (69)**. Both are 1-semitone leading-tone resolutions; each lands on a
   chord tone of its bar (D ∈ G, A ∈ D).

Source preserved byte-for-byte as `MIDI/source_original.mid`; pre-rework kept
as `MIDI/irish_jig-phase1.mid`. Reworked zero-drift-normalized source written
to `MIDI/composition.mid` (48 notes, 11520 ticks).

**Re-audit after rework:** off-grid 0, out-of-scale 0, out-of-chord 0,
zero-drift PASS. Recorded in `Analysis/rework_audit.json`.

## Layer discipline (absolute)

SP-080 is applied as an **absolute-layer** production pass: no new notes are
written; the FluidSynth dry render (SP-001 carrier, flute program 73) is
re-shaped by the Cadence Engine's two layers (Envoy's two-layer design) driving
time-varying gain, constant-power pan, and blockwise SVF low-pass envelopes.

| Param | Value |
|---|---|
| bpm | 120.0 |
| master LFO rate | 0.7 Hz |
| layer "low" | blocks [8,6,8,7], rate 2.0, forward, straight, root D4(62), gain 1.05, LFO 0.30 Hz / depth 0.20 |
| layer "high" | blocks [7,5,8,8], rate 3.0, pingpong, swing, root D5(74), gain 0.95, LFO 0.45 Hz / depth 0.25 |
| FluxRandomizer | depth 0.22, blocks [0,2] |
| carrier | FluidSynth SP-001, flute program 73 |
| reverb | room 0.55, damping 0.45, wet/dry 0.10, width 0.85 |
| mastering | `normalize_to_lufs(-14.0)` → `Limiter(-1 dBTP)` LAST |

Cadence events rendered: **456** over 8 loops (covering the 14.30 s padded
stem). The two layers' different block counts/rates/directions produce
polyrhythmic modulation for free (rate 2.0 vs 3.0 → 2:3 cross-rhythm on the
gain/pan/LP lanes).

## Verification

| Metric | Value | Verdict |
|---|---|---|
| Pitch (FFT dominant peak / 0.5 s window, 50–1000 Hz) | **hit 1.0000** (26/26 valid windows) | PASS |
| Harmonic energy (first 8 harmonics of dom. peak) | **0.8341** wet / 0.8394 dry (retention 0.994) | PASS (≥ 0.30) |
| Flute pitch classes | ⊆ G major {0,2,4,6,7,9,11} | PASS |
| Silence ratio | **11.17%** (release/reverb tail only) | PASS (< 30%) |
| RMS | 0.1306 | — |
| Integrated LUFS | −14.00 | on target (celtic → −14) |
| True peak | 0.8913 (−1.0 dBTP ceiling applied) | PASS |
| Zero-drift | single note track spans exactly 11520 ticks | PASS |

Per-second RMS map: `[0.168, 0.166, 0.157, 0.151, 0.112, 0.124, 0.094, 0.167,
0.107, 0.145, 0.162, 0.129, 0.032, 0.0004, 0.0]` — steady music through 12 s,
then tail-only decay (last ~2.3 s = FluidSynth release + reverb). No
mid-track gaps.

## Files

| Path | Size | Role |
|---|---|---|
| `SP080-cadence-variator-034-irish-jig-study.wav` | 2 523 180 B | mastered full mix (stereo 44.1 kHz, 14.3 s) |
| `SP080-cadence-variator-034-irish-jig-study.ogg` | 127 470 B | Opus 48k voip (delivery) |
| `dry_full_mix_jig_reference.wav` | 2 523 180 B | pre-Cadence dry reference |
| `Audio/stems_dry/track00_Flute.wav` | 2 523 180 B | dry flute stem |
| `Audio/stems_wet/track00_Flute_CADENCE.wav` | 2 523 180 B | Cadence-modulated flute stem |
| `MIDI/composition.mid` | 489 B | reworked (zero-drift normalized) source |
| `MIDI/source_original.mid` | 525 B | byte copy of original source |
| `MIDI/irish_jig-phase1.mid` | 525 B | pre-rework sidecar |
| `provenance.json`, `Analysis/render_stats.json`, `Analysis/rework_audit.json` | — | records |

## Verdict

SP-080 applied as an absolute-layer rhythmic-variator production pass on a
6-bar G-major Irish jig (single flute melody). Pre-flight caught three real
issues — 8 off-grid ornament cuts and 2 out-of-scale chromatic leading tones —
all fixed before the sound pass; re-audit all-0. Two-layer Cadence Engine
(rate 2.0 vs 3.0 polyrhythm) + FluxRandomizer modulate gain/pan/LP over the
dry flute render. Pitch verifies clean (FFT hit 1.000, harmonic energy 0.834),
silence 11.2% (tail-only), mastered to −14 LUFS / 0.891 peak.
