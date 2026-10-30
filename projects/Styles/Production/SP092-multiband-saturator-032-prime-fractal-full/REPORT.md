# SP-092 Multiband Saturator — 032-prime-fractal-full

**Job:** random-style production (SP methods) — LAYER-ALIGNED
**Date:** 2026-10-30  **Seed:** 20261030

## Selection

| Field | Value |
|---|---|
| Registry source | `workflows.musicom_workflow.SP_METHODS` (72 registered) |
| Method | `SP-092` |
| Module | `sound.effects.multiband_saturator` |
| Description | 6-Band Multiband Saturator w/ 15 Selectable Algorithms & Per-Band M/S Routing (Kreuzberg Audio Oberton-style) |
| Layer | ABSOLUTE — one 6-band saturator config applied to the whole piece |
| Recent excluded (7d) | SP-078, SP-094, SP-095, SP-109, SP-119, SP-127 |
| Already-on-source | (none) |
| Pool size | 65 |
| Well-formed candidates | 289 / 401 |

**Source composition:** `Styles/Experimental/032-prime-fractal-full/daily-2026-06-26_experimental_032-prime-fractal-v6.mid`
- Monophonic Acoustic Grand Piano (program 0), channel 0, single track.
- 120 BPM, 4/4, TPB 480, 65 note events, 10200 ticks (~10.62 s).
- ABCBA form — three harmonic centres:
  - A (C-based): `[60,63,67,71,72]` → pcs `{0,3,7,11}`
  - B (F-based): `[65,68,72,76,77]` → pcs `{5,8,0,4}`
  - C (G-based): `[55,59,62,66,67]` → pcs `{7,11,2,6}`
- Pitch-class union `{0,2,3,4,5,6,7,8,11}` — no C#/A/A#.
- Onset deltas: 60×16th (120 ticks) + 4×600-tick rests → strictly 16th-aligned.

## PRE-FLIGHT AUDIT (3-rule gate)

| Rule | Count | Verdict |
|---|---|---|
| Grid sync (16th = 120 ticks) | 0 off-grid (all 65 onsets 16th-aligned) | PASS |
| Harmony — in scale (piece union `{0,2,3,4,5,6,7,8,11}`) | 0 out-of-scale | PASS |
| Harmony — chord tone of bar | N/A (monophonic, no simultaneous harmony voice) | PASS |
| Zero-drift (equal track lengths) | 1 note track, end 10200, no cross-track mismatch | PASS |

**Verdict: PASS all three — no rework required, proceed to SP-092.**

`out_section` = 7 transitional notes (section-seam bridge notes, e.g. the 2-note
B tail entering the C bar, the C tail entering the B bar). All 7 sit inside the
piece-wide pitch vocabulary — they are the fractal line's connective tissue, not
out-of-scale crud. No phase-1/phase-2 rework was needed.

## Method parameters (SP-092)

| Param | Value |
|---|---|
| Crossover freqs | [120, 400, 1200, 4000, 10000] Hz (LR4) |
| Global trim | 0.85 |
| Master | `master()` → LUFS −14.0 (experimental fallback), ceiling −1 dBTP |

Band config (piano-tuned, deterministic):

| Band | Freq | Algo | Drive | Mix | Mode |
|---|---|---|---|---|---|
| 1 (<120 Hz, sub) | 60 | bypass | 1.00 | 1.0 | stereo |
| 2 (120–400, low fundamentals G3/C4/Eb4) | 250 | tube | 1.20 | 1.0 | stereo |
| 3 (400–1200, mid fundamentals + 1st harm) | 800 | tanh | 1.30 | 1.0 | stereo |
| 4 (1200–4000, hammer-attack harmonics) | 2500 | soft_clip | 1.10 | 1.0 | mid |
| 5 (4000–10000, string/action sheen) | 6000 | sine_foldback | 0.45 | 1.0 | stereo |
| 6 (>10000, air) | 12000 | bypass | 1.00 | 1.0 | stereo |

Pipeline: dry FluidSynth (FX off `-R 0 -C 0 -g 1.2`) → `MultibandSaturator.process`
(6 LR4 bands, per-band algo + M/S) → master → WAV + Opus OGG.

## Pitch verification

| Metric | Wet (SP-092) | Dry (SP-001 ref) |
|---|---|---|
| Valid 0.5 s windows | 21 | 21 |
| FFT pitch-class hit rate | 1.0000 | 1.0000 |
| Mean harmonic energy (8 harmonics) | 0.7118 | 0.6542 |
| HE retention | 1.088 | — |

**Pitch verdict: PASS** (hit rate ≥ 0.60 and HE retention ≥ 0.40).
Saturation is a memoryless nonlinearity — the fundamental is preserved (hit
rate 100% both wet and dry), and the added harmonics *raise* harmonic energy
(retention 1.088, +8.8% richer), so the piano line reads warmer/edgier, not
pitch-shifted.

## Silence / RMS profile

- Silence ratio: **6.44%** (well below the 30% suspect threshold — the line is
  a near-continuous 16th-note stream; only note-release gaps read as silence).
- Overall RMS: 0.1072
- LUFS: −14.00  |  Peak: 0.3473 (−9.19 dBTP — true-peak is a ceiling, not a
  target; a dynamic single-piano line legitimately lands well below −1 dB).
- Dry input peak 0.148 → saturated (pre-master) peak 0.317 → master-normalized.

## Artifacts

| File | Size |
|---|---|
| `SP092-multiband-saturator-032-prime-fractal-full.wav` | 2,227,756 B |
| `SP092-multiband-saturator-032-prime-fractal-full.ogg` | 96,947 B (~10.6 s) |
| `dry_full_mix_sp001_reference.wav` | 2,227,756 B |
| `MIDI/source.mid` | 609 B |
| `provenance.json` | 3.1 KB |
| `Analysis/render_stats.json` | 576 B |

Stems: N/A — source is a single note track (one monophonic piano line); the
full mix _is_ the only stem (single voice).

## Notes

- Selection script: `Production/select_job_20261030.py` (writes
  `.selection_cron.json`).
- Produce script: `Scripts/produce_sp092_cron.py`.
- Source MIDI was NOT modified — the audit passed clean (grid 0, out-of-scale 0,
  zero-drift), so no phase-1/phase-2 rework was needed.
- FluidSynth render used FX off (`-R 0 -C 0`) so SP-092 is the only
  production-layer transformation, cleanly attributable.
