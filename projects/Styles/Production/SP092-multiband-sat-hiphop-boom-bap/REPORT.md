# SP-092 Multiband Saturator — HipHop Boom-Bap Production Pass

**Job**: random-style production (SP) — layer-aligned
**Date**: 2026-10-08
**Seed**: 20261008

---

## Method + Selection

| | |
|---|---|
| **Method** | SP-092 |
| **Registry source** | `workflows.musicom_workflow.SP_METHODS` (implemented registry, 42 entries) |
| **Module** | `sound.effects.multiband_saturator` |
| **Description** | 6-Band Multiband Saturator w/ 15 Selectable Algorithms & Per-Band M/S Routing (Kreuzberg Audio Oberton-style) |
| **Layer discipline** | ABSOLUTE layer — replaces the timbre/saturation layer for the WHOLE piece (full mix + every stem go through the same band config) |

Selection procedure (per skill): pick an implemented method from `SP_METHODS`,
exclude methods used in the last 7 days (`SP-021, SP-069, SP-072, SP-080,
SP-083, SP-086, SP-091`) plus baseline `SP-001`. Seeded `random.choice`
landed on **SP-092**.

**Re-roll note**: the first composition draw landed on
`Country/001-country-hope-loop/MIDI/country-hope-loop-v7.mid`, which is
degenerate — the mido delta-time bug (`time=` is DELTA, not absolute) made
each "bar" 7916 ticks instead of 1920 (4/4 @ 480 tpb), stretching an 8-bar
96 BPM loop to 82.5 s, with no program changes. Per the SP-069 precedent
("tpb 10080, no programs → re-rolled to well-formed candidate"), it was
re-rolled to a well-formed candidate (219 / 328 candidates passed the
well-formed filter).

## Source Composition

| | |
|---|---|
| **Project** | `Styles/HipHop/boom-bap/v1/hiphop_boom_bap.mid` |
| **Genre** | Boom-bap hip-hop |
| **Key / tempo** | E minor, 90 BPM |
| **Form** | 32 bars (2 × 16-bar sections A/B) |
| **Voices** | Drums (ch9), Bass (ch0 GM33 Electric Bass finger), Lead (ch1 GM1 Bright Acoustic Piano), Pad (ch2 GM88 Pad 1 new age) |
| **Composition methods** | 011 Euclidean (drums), 002 Markov (lead), 026 DPSM (pad) |
| **Source PCS (non-drum)** | `[0, 2, 4, 5, 6, 7, 9, 11]` — E natural minor + the pad's F/C chord tones |

## Parameters

Sample rate 44100 Hz. 6 bands via 5 LR4 crossovers `[120, 400, 1200, 4000, 10000]` Hz.

| Band | Freq | Q | Drive | Mix | Algo | Mode |
|---|---|---|---|---|---|---|
| 1 | 60 | 0.70 | 0.60 | 1.00 | germanium | mid |
| 2 | 250 | 0.80 | 1.10 | 0.90 | tube | stereo |
| 3 | 700 | 1.00 | 1.00 | 0.80 | silicon | stereo |
| 4 | 2000 | 1.00 | 0.90 | 0.60 | tanh | sides |
| 5 | 6000 | 1.10 | 0.80 | 0.50 | soft_clip | stereo |
| 6 | 12000 | 1.00 | 0.50 | 0.30 | bypass | stereo |

`global_trim = 1.0`. Design intent: warm the sub/bass (germanium on mid for
mono-safe low end, tube on bass), edge the low-mid (silicon), widen the mid
(tanh on sides), gentle top (soft_clip), mostly-clean air (bypass) — avoids
harsh high-end from a full-drive high band.

Mastering: `normalize_to_lufs(-14)` → `Limiter(-1 dBFS)` (last).

Rendering: FluidSynth `-ni -g 1.2 -R 0 -C 0` (internal reverb/chorus off) on
`FluidR3_GM.sf2`; OGG via `ffmpeg -codec:a libopus -application voip -b:a 48k`.

## Verification

### Pitch verification (FFT dominant peak per 0.5 s window, 50–1000 Hz)

| Metric | Wet (SP-092) | Dry (SP-001 ref) |
|---|---|---|
| Valid windows | 186 | — |
| Dominant-peak hit rate | **1.0000** | 1.0000 |
| Harmonic energy (8 harmonics) | **0.3020** | 0.3159 |
| HE retention (wet/dry) | **0.956** | 1.000 |

**Verdict: PASS** (hit rate ≥ 0.60 and HE retention ≥ 0.50). The multiband
saturator preserves the tonal content exactly (100% pitch-class hit rate) and
retains 95.6% of the harmonic energy — the added saturation harmonics do not
collapse to noise (a collapse would show single-digit retention / 0 Hz frames).

### Loudness / silence / stereo

| Metric | Value |
|---|---|
| Integrated LUFS | −14.00 |
| Peak | 0.6118 (−4.27 dBFS) |
| Silence ratio | **3.26%** |
| Overall RMS | 0.1469 |
| L/R mono correlation | 0.955 |

Silence 3.26% is healthy (no mid-track gaps; the limiter never engaged since
the −14 LUFS-normalized mix peaks below −1 dBFS, so headroom is preserved).

## Artifacts

| File | Size |
|---|---|
| `SP092-multiband-sat-hiphop-boom-bap.wav` | 16,454,956 B |
| `SP092-multiband-sat-hiphop-boom-bap.ogg` | 531,324 B |
| `dry_full_mix_sp001_reference.wav` | 16,454,956 B |
| `MIDI/hiphop_boom_bap.mid` | (source copy) |
| `Audio/stems_dry/trackXX_*.wav` (4) | ~60 MB total |
| `Audio/stems_wet/trackXX_*_MBSAT.wav` (4) | ~60 MB total |
| `provenance.json`, `Analysis/{render_stats,pitch_verification,select_20261008}.json` | — |

Stem labels (verified): `track00_Drums`, `track01_Electric_Bass_finger`,
`track02_Bright_Acoustic_Piano` (GM1 → Bright, not "Acoustic_Grand"),
`track03_Pad_1_new_age`.

## Fixes / Notes

- **No module fixes required** — `MultibandSaturator.process()` ran clean
  (unlike SP-026 phase_vocoder's phase-accumulation silence collapse, and
  SP-035 GENDYN's noise redraw — both documented in prior reports).
- `shutil.copy2(__file__, …)` at the end hit a `SameFileError` because the
  script already lives at its target path (`Scripts/produce_sp092_cron.py`) —
  harmless; the script is correctly placed.
