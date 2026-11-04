# SP-117 Reverse Reverb — 089-electronic-subset-minor

**Job:** random-style production (SP methods) — LAYER-ALIGNED
**Date:** 2026-11-04  **Seed:** 20261104

## Selection

| Field | Value |
|---|---|
| Registry source | `workflows.musicom_workflow.SP_METHODS` — the **implemented** dict (79 registered), NOT `methods_db.md` spec-only, NOT stale ranges |
| Method | `SP-117` |
| Module | `sound.effects.reverse_reverb` → `ReverseReverb`, `make_reverb_ir` |
| Description | Reverse Reverb — reverse → IR convolution (decaying-noise reverb, pre-delay) → reverse back → wet/dry mix, align-to-hit trimming + boundary fades (Bixlab Reverse Reverb-style) |
| Layer | ABSOLUTE — one reverse-reverb wash (reverse → IR conv → reverse-back swell) over the whole FluidSynth dry mix; no new notes written |
| Recent excluded (7d) | 42 methods (SP-009…SP-127; mtimes touched by nightly auto-sync) |
| Baseline excluded | SP-001 (carrier) |
| Pool size | 39 |

**Source composition:** `Styles/Electronic/089-electronic-subset-minor/MIDI/089-electronic-subset-minor.mid`

- 24-bar 6-voice electronic subset-walk piece, **A natural minor** (A B C D E F G), **112 BPM**, 4/4, TPB 480, 24 bars = 46080 ticks = 54.21 s.
- Voices: Lead Marimba (prog 12, ch0, 219 notes) · Clarinet (71, ch1, 96) · Cello (42, ch2, 72) · Dulcimer (15, ch3, 384) · Bass (43, ch4, 192) · Drums (ch9, 300 hits). **963 pitched notes** + 300 drum hits.
- Progression (24 bars, all diatonic to A natural minor): Am · Em · F · C · F · C · G7 · Dm7 · G7 · Em7 · G7 · Cmaj7 · G · Em · Dm · F · Dm · Em · F · C · Dm · C · G7 · Am.

## PRE-FLIGHT AUDIT (3-rule gate)

| Rule | Count (before) | Count (after) | Verdict |
|---|---|---|---|
| Grid sync (16th = 120 ticks @ 480 TPB) | **0 off-grid** | 0 | PASS |
| Harmony — in scale (A natural minor) | **0 out-of-scale** | 0 | PASS |
| Harmony — chord tone of bar | **0 out-of-chord** | 0 | PASS |
| Zero-drift (note tracks equal length) | [0, 46080 ×6] | equal | PASS |

**Rework applied: NONE.** The 089 electronic piece was authored against musicom's
two-phase rules (16th-grid locked, A-minor scale snap + chord-tone quantize per
bar, voice-leading corrected) and already passes the gate cleanly on first
inspection — 963 pitched notes all on the 16th grid, all pitch classes in
`{9,11,0,2,4,5,7}`, all chord tones of their bar's subset sonority, and all six
note tracks span exactly 46080 ticks (zero-drift intact). The project's own
`audit.py` records the same (`AUDIT PASS`).

`MIDI/composition.mid` = byte copy of source; `MIDI/source_original.mid` =
byte copy preserved. Re-audit recorded in `Analysis/rework_audit.json`.

## Layer discipline (absolute)

SP-117 is a reverse-reverb wash: the FluidSynth dry render (SP-001 carrier,
Marimba + Clarinet + Cello + Dulcimer + Bass + Drums) is routed through a single
`ReverseReverb` — reverse → convolve with a synthetic decaying-noise IR → reverse
back, mixed wet/dry. Because the signal is reversed twice, the dry transient
keeps its original position while its reverb tail now *precedes* it: a swelling
build into each hit. No per-voice variation (per-track application is a later
refinement).

`ReverseReverb.process` is mono; L and R channels were processed independently
with a **shared IR seed** so the stereo image stays phase-coherent.

| Param | Value |
|---|---|
| decay_sec | 2.0 (reverb tail) |
| wet | 0.40 (60% dry retained) |
| pre_delay_ms | 20.0 |
| ir_density | 0.9 |
| ir_seed | 20261104 (deterministic) |
| align_to_hit | **False** (preserve full 54.21 s length — no trim) |
| fade_ms | 15.0 (boundary de-click) |
| carrier | FluidSynth SP-001, `-R 0 -C 0 -g 1.2` (dry) |
| mastering | `normalize_to_lufs(-14.0)` → `Limiter(-1 dBTP)` LAST |

`align_to_hit=False` keeps the piece length and section map intact — the reverse
reverb adds the swelling pre-attack texture rather than re-timing anything, so
the form (Intro/Verse/Chorus/Break/Verse2/Outro) is preserved while each
transient gains an atmospheric "whoosh-in".

## Verification

| Metric | Value | Verdict |
|---|---|---|
| Pitch (FFT dominant peak / 0.5 s window, 50–1000 Hz) | **hit 1.0000** (108/108 valid windows) | PASS |
| Harmonic energy (first 8 harmonics of dom. peak) | **0.3312** wet / 0.4072 dry (retention 0.813) | PASS (≥ 0.30) |
| Pitch classes | ⊆ A natural minor {9,11,0,2,4,5,7} | PASS |
| Silence ratio | **1.89%** (intro + tail only) | PASS (< 30%) |
| RMS | 0.1414 | — |
| Integrated LUFS | **−14.00** | on target (electronic → −14 fallback) |
| True peak | 0.878 (−1.13 dBTP; below −1 dB ceiling, correct for a non-peaky mix) | PASS |
| Zero-drift | all 6 note tracks span exactly 46080 ticks | PASS |

Per-second RMS map: 0.018 (quiet intro) → steady 0.12–0.20 through the 24 bars →
0.065 → 0.0 (outro fade tail). No mid-track gaps. The reverse-reverb wash lowers
harmonic energy 40.7% → 33.1% (expected — the decaying-noise IR adds broadband
swell energy) but pitch tracking stays perfect (hit rate actually *rises*
0.981 → 1.000, as the swell smooths the attack into clean sustained frames).

## Files

| Path | Size | Role |
|---|---|---|
| `SP117-reverse-reverb-089-electronic-subset-minor.wav` | 9 562 668 B | mastered full mix (stereo 44.1 kHz, 54.21 s) |
| `SP117-reverse-reverb-089-electronic-subset-minor.ogg` | 371 642 B | Opus 48k voip (delivery) |
| `dry_full_mix_reference.wav` | 9 562 668 B | pre-reverb dry reference |
| `Audio/stems_dry/track0{0,1,2,3,4}_*.wav` | — | 5 pitched stems (Marimba/Clarinet/Cello/Dulcimer/Contrabass) |
| `Audio/stems_dry/track05_Drums.wav` | — | drum stem (ch9) |
| `Audio/stems_dry/full_mix_REVERSE_REVERB.wav` | 9 562 668 B | reverse-reverb (pre-master) full mix |
| `MIDI/composition.mid` | byte copy | normalized source (no rework) |
| `MIDI/source_original.mid` | byte copy | original source preserved |
| `provenance.json`, `Analysis/render_stats.json`, `Analysis/rework_audit.json` | — | records |

## Verdict

SP-117 applied as an absolute-layer reverse-reverb wash on a 24-bar A-minor
six-voice electronic piece. Pre-flight found the source already clean
(0 off-grid / 0 out-of-scale / 0 out-of-chord / zero-drift) — no rework needed.
Decay 2.0 s / wet 0.40 / pre-delay 20 ms reverse reverb layered over the dry
FluidSynth mix adds a swelling "whoosh-in" to every transient while preserving
the piece's form and length (align_to_hit=False). Pitch verifies clean (FFT hit
1.000, harmonic energy 0.331 — retained 0.813 of dry), silence 1.89%
(intro+tail only), mastered to −14 LUFS / 0.878 peak.
