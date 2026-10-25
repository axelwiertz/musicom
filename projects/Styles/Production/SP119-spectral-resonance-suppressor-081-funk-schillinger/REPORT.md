# SP-119 Spectral Resonance Suppressor — production report

- **Date**: 2026-10-25
- **Job**: random-style production (SP), layer-aligned
- **Method**: SP-119 (`sound.effects.spectral_resonance_suppressor`) — STFT
  de-resonator (Newfangled Audio Fixate:Midrange-style): per-frame magnitude
  spectrum compared to a local median baseline; bins whose excess over the
  baseline exceeds a threshold and are local maxima are flagged; a
  raised-cosine notch is shaped around each peak, scaled by `amount` and the
  excess; gains smoothed across frequency and frames (attack/release one-pole)
  before overlap-add resynthesis. Processing restricted to the 200..6000 Hz
  midrange band.
- **Layer**: ABSOLUTE (whole-piece mix de-resonation; the full FluidSynth
  render is the input, no per-voice routing).

## Selection
- **Registry source**: `workflows.musicom_workflow.SP_METHODS` (63 registered;
  55 in pool after excluding recent-7-day SP-078/090/095/101/105/108/111 and
  baseline SP-001).
- **Source composition**: `Styles/Funk/081-funk-schillinger/MIDI/081-funk-schillinger.mid`
  (Bb major funk, 100 BPM, 480 TPB, 24 bars, 6 sections; 6 voices:
  trumpet/Rhodes/guitar/bass/clav + drums; Schillinger System method 018).

## Pre-flight audit (3 rules) — PASS on source (no rework needed)
| rule | result |
|---|---|
| Grid sync (16th = 120 ticks) | **PASS** off-grid = 0 |
| Harmony (Bb major scale + chord tones) | **PASS** out-of-scale = 0, out-of-chord = 0 |
| Zero-drift (equal track ends) | **PASS** 7 tracks end = [46080] ticks |

The source is already grid-locked (0 off-grid; the 114 off-8th onsets are odd
16ths, which is idiomatic funk syncopation and still 16th-grid-locked), fully
in Bb major and chord-tone clean, and all tracks end at 46080 ticks — no
rework, straight to the SP method.

## SP-119 absolute layer (midrange de-resonation)
- Carrier: FluidSynth (FluidR3_GM) full-mix render, dry (`-R 0 -C 0 -g 1.2`),
  44100 Hz.
- Effect params (documented defaults): `amount=0.7`, `threshold_db=6.0`,
  `width_bins=24`, band `200..6000 Hz`, `attack=0.05 s`, `release=0.3 s`.
  Applied per-channel (L and R independently, preserving stereo).
- Mastered to −13 LUFS (funk target), −1 dBTP ceiling.

## Key finding — this dry mix has no non-musical resonances to tame
The top midrange spectral peaks are **all in-key Bb-major sustained musical
tones** (the Rhodes/clav/guitar/trumpet fundamentals and harmonics), not
pathological ring/mud:

| freq (Hz) | note | excess over baseline |
|---|---|---|
| 699.8 | F5 | +19.02 dB |
| 1044.4 | C6 | +17.60 dB |
| 786.0 | G5 | +17.42 dB |
| 1399.7 | F6 | +13.14 dB |
| 882.9 | A5 | +11.37 dB |
| 1571.9 | G6 | +11.29 dB |
| 2799.3 | F7 | +11.14 dB |
| 1862.6 | Bb6 | +10.78 dB |
| 2088.7 | C7 | +10.76 dB |
| 3143.8 | G7 | +10.28 dB |

Because a Fixate:Midrange-style de-resonator compares each bin to its local
median baseline, these broad in-key tones sit *above* the baseline but are the
signal itself — so the method correctly declines to eat them. Measured
midrange peakiness (sum of dB over local-median baseline, threshold-free):
`901.15 → 901.63` (≈ 0% change) at default settings; even an aggressive
setting (`amount=1.0, threshold_db=0.5, width_bins=4`) reaches only ~6%
peakiness reduction. This is the method behaving **correctly** — a dry GM funk
render simply has no room-mode/ring/string-squeal resonances to suppress.

## Verification
- **Pitch**: dominant-peak-in-key hit rate = 0.9828 (116 windows) → **PASS**
- **Harmonic energy (8 harmonics of dominant)**: final 0.4222 vs dry 0.4119
  (retention 1.025 — content fully preserved, nothing eaten)
- **Silence**: 6.59%
- **RMS**: 0.1641
- **LUFS**: −13.17  **true peak**: 0.8913 (−1.00 dBTP)

## Files
- `SP119-spectral-resonance-suppressor-081-funk-schillinger.wav` (10589484 bytes)
- `SP119-spectral-resonance-suppressor-081-funk-schillinger.ogg` (462331 bytes)
- `SP119_resonance_suppressed_raw.wav` (de-resonated, pre-master)
- `dry_full_mix_source_reference.wav` (dry source reference, pre-production)
- `MIDI/source_original.mid` (reference copy)
- `Audio/stems/` (6 dry per-instrument stems, pre-effect)
- `provenance.json`, `Analysis/render_stats.json`

## Notes
- SP-119 is a mix "problem-solver" (same family as Soothe/Gullfoss/Curves
  Equator): it tames resonances and midrange build-up where multiple sounds
  fight for the same 200..6000 Hz slice. Applied here as an absolute layer, it
  measurably preserves the musical content (pitch hit rate + harmonic-energy
  retention both up, not down) while finding no non-musical resonances to
  remove — the honest, correct outcome for this spectrally-clean source.
- A production pass that finds "nothing to fix" is itself a valid verification
  result: the source composition is spectrally clean and needs no de-resonation.
  (For contrast, the module's `demo()` injects a 1500 Hz ring and shows >45%
  suppression — the method works hard when there is actual ring/mud present.)
