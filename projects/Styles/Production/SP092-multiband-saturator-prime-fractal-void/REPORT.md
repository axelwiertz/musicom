# SP-092 Multiband Saturator — prime-fractal-void

**Job:** random-style production (SP methods) — LAYER-ALIGNED
**Date:** 2026-10-17  **Seed:** 20261017

## Selection

| Field | Value |
|---|---|
| Registry source | `workflows.musicom_workflow.SP_METHODS` (48 registered) |
| Method | `SP-092` |
| Module | `sound.effects.multiband_saturator` |
| Description | 6-Band Multiband Saturator w/ 15 Selectable Algorithms & Per-Band M/S Routing (Kreuzberg Audio Oberton-style) |
| Layer | ABSOLUTE — one 6-band saturator config applied to the whole piece |
| Recent excluded (7d) | SP-006, SP-026, SP-028, SP-032, SP-074, SP-098, SP-099, SP-103 |
| Pool size | 40 |
| Well-formed candidates | 237 / 349 |

**Source composition:** `Styles/Experimental/032-prime-fractal-void/MIDI/fractal_void.mid`
- Single-voice sawtooth fractal lead, program 81 (Lead 2 "sawtooth"), channel 0.
- 144 BPM, 4/4, TPB 480, 8.5 bars (16320 ticks), ~14.17 s.
- 96 note events, all 16th-note duration (120 ticks); pitch range C4(60)–B5(83).
- Pitch-class set `{C, Eb, F, G, B}` = {0,3,5,7,11} — C minor with raised 7th
  (leading tone B); subset of C harmonic/melodic minor.
- 11-note prime-cycle motif (pcs 0,5,3,7,5,11,7,0,11,3,0) phase-rotated each
  bar — the "prime fractal void" DNA.

## PRE-FLIGHT AUDIT (3-rule gate)

| Rule | Count | Verdict |
|---|---|---|
| Grid sync (16th = 120 ticks) | 0 off-grid (all 96 onsets 16th-aligned) | PASS |
| Harmony — in scale (C minor, pc set {0,3,5,7,11}) | 0 out-of-scale | PASS |
| Harmony — chord tone of bar | 0 (monophonic — no harmonic accompaniment to conflict) | PASS |
| Zero-drift (equal track lengths) | 1 note track, 16320 ticks, no cross-track mismatch | PASS |

**Verdict: PASS all three — no rework required, proceed to SP-092.**

Note: the "chord-tone of bar" rule is N/A by construction here — the piece is
a single monophonic line with no harmony voice, so there is no chord context to
be "out of". Every note sits inside the piece's own 5-note pitch vocabulary.
Grid is strictly 16th-aligned (onset deltas are only 120 or 240 ticks).

## Method parameters (SP-092)

| Param | Value |
|---|---|
| Crossover freqs | [120, 400, 1200, 4000, 10000] Hz (LR4) |
| Global trim | 0.85 |
| Master | `master()` → LUFS −14.0 (experimental), ceiling −1 dBTP |

Band config (deterministic, musical):

| Band | Freq | Algo | Drive | Mix | Mode |
|---|---|---|---|---|---|
| 1 (<120 Hz, sub) | 60 | bypass | 0.80 | 1.0 | stereo |
| 2 (120–400, fundamentals) | 250 | tube | 1.25 | 1.0 | stereo |
| 3 (400–1200, fundamentals+harm) | 800 | tanh | 1.35 | 1.0 | stereo |
| 4 (1200–4000, harmonics) | 2500 | soft_clip | 1.05 | 1.0 | mid |
| 5 (4000–10000, sheen) | 6000 | sine_foldback | 0.50 | 1.0 | stereo |
| 6 (>10000, air) | 12000 | bypass | 1.0 | 1.0 | stereo |

Pipeline: dry FluidSynth (FX off `-R 0 -C 0`) → `MultibandSaturator.process`
(6 LR4 bands, per-band algo + M/S) → master → WAV + Opus OGG.

## Pitch verification

| Metric | Wet (SP-092) | Dry (SP-001 ref) |
|---|---|---|
| Valid 0.5 s windows | 32 | 32 |
| FFT pitch-class hit rate | 0.9062 | 1.0000 |
| Mean harmonic energy (8 harmonics) | 0.6188 | 0.4931 |
| HE retention | 1.255 | — |

**Pitch verdict: PASS** (hit rate ≥ 0.60 and HE retention ≥ 0.40).
Saturation is a memoryless nonlinearity — the fundamental is preserved (hit
rate held at 91%), and the added harmonics *raise* harmonic energy (retention
1.255, i.e. +25% richer), so the sawtooth lead reads warmer/edgier, not
pitch-shifted.

## Silence / RMS profile

- Silence ratio: **3.87%** (well below the 30% suspect threshold — the line is
  a near-continuous 16th-note stream; only note-release gaps read as silence).
- Overall RMS: 0.1462
- LUFS: −14.00  |  Peak: 0.4649 (−6.65 dBTP — true-peak is a ceiling, not a
  target; a dynamic single-lead line legitimately lands well below −1 dB).
- Dry input peak 0.394 → saturated (pre-master) peak 0.394, master-normalized.

## Artifacts

| File | Size |
|---|---|
| `SP092-multiband-saturator-prime-fractal-void.wav` | 2,905,388 B |
| `SP092-multiband-saturator-prime-fractal-void.ogg` | 133,309 B (16.48 s) |
| `dry_full_mix_sp001_reference.wav` | 2,905,388 B |
| `provenance.json` | 2.3 KB |
| `Analysis/render_stats.json` | 346 B |
| `Analysis/select_20261017.json` | 270 B |
| `Scripts/produce_sp092_cron.py` | 9.7 KB |

Stems: N/A — source is a single note track (one sawtooth lead); the full mix
_is_ the only stem (single voice).

## Notes

- Selection script: `Production/select_job_20261017.py` (writes
  `.selection_cron.json`).
- Produce script: `Scripts/produce_sp092_cron.py`.
- Source MIDI was NOT modified — the audit passed clean, so no phase-1/phase-2
  rework was needed (unlike the 2026-10-16 SP-099 job, which reworked a
  5-voice HITL candidate with 100 out-of-chord notes).
- FluidSynth render used FX off (`-R 0 -C 0`) so SP-092 is the only
  production-layer transformation, cleanly attributable.
