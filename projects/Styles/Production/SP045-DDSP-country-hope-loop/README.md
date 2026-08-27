# SP-045 DDSP — Country Hope Loop v7

**Date:** 2026-08-19 (nightly SP production)
**Composition source:** `Styles/Country/001-country-hope-loop/MIDI/country-hope-loop-v7.mid`
**Production method:** SP-045 — Differentiable Digital Signal Processing (DDSP)

## What was done

Translated the symbolic MIDI melody into audio using the DDSP synthesis
architecture (Engel et al. 2020, Google Magenta): audio is the sum of a
**harmonic additive oscillator bank** and a **filtered-noise component**, then
passed through **algorithmic reverb**.

Since symbolic pitch is available (MIDI), the CREPE pitch tracker is bypassed
(method pitfall #1): `f0` is computed exactly from MIDI note →
`440 * 2^((p-69)/12)`, and velocity → loudness shapes the envelope.

### Synthesis chain

- **Harmonic bank:** 48 partials, amplitude profile `1/k^1.6 * exp(-k·z)` timbre
  code (flute-like rolloff), phase-accumulated so vibrato (5 Hz, on registers
  above MIDI 50) glides without discontinuity. Harmonics capped below Nyquist
  per note (pitfall #2): `k_max = SR/(2·f0)`.
- **Filtered noise:** lowpassed (24-tap moving average) white noise at 15% gain
  for breath/transient "chiff", envelope `env^1.5` (pitfall #3 keeps it subtle,
  not hissy).
- **ADSR:** attack 12 ms, decay 80 ms (sustain 0.6), release 120 ms — anti-click
  (pitfall #4).
- **Reverb:** synthetic decaying-noise IR (RT60 1.4 s), FFT convolution, 35% wet,
  normalized — short tail so transients stay crisp (pitfall #5).

## Outputs

| File | Role |
|------|------|
| `Audio/SP045-DDSP-country-hope-loop-fullmix.ogg` | listenable render (Opus, Telegram) |
| `Audio/SP045-DDSP-country-hope-loop-fullmix.wav` | full mix master |
| `Audio/stem_harmonic.wav` | harmonic-only stem (pitched tone) |
| `Audio/stem_noise.wav` | noise-only stem (breath/transient) |
| `MIDI/original_country_hope_loop_v7.mid` | original composition (copied) |
| `provenance.json` | full metadata |

## Source MIDI summary

- 96 BPM, 4/4, G major, 2 tracks (META + melody), 64 notes.
- Pitch range MIDI 36–74, velocity 80–100.
- ~82.5 s duration → render ~84 s (incl. reverb tail).

## Notes / listen for

- DDSP decouples **pitch from timbre**: same f0 material could render as
  bowed-string, brass, or vocal by swapping the latent timbre code `z` and the
  harmonic rolloff — the melody is preserved, the instrument is the variable.
- Harmonic/noise balance is the texture knob: drop `noise_gain` for a pure
  organ-like tone, raise it for breathy/percussive.
- Reverb is the final DFPM stage synced from SP-032 (FDN) conceptual lineage.

## Analysis

- Silence fraction: 1.9% (healthy — no dead mid-track gaps; only tail padding).
- Peak normalized to ~-1 dB. See `analysis.json` for per-second RMS map.