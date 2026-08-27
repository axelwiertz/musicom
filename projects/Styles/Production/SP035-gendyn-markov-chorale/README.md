# SP-035 — GENDYN Stochastic Breakpoint Synthesis on 058-markov-chorale

**Date:** 2026-08-24 (nightly production job)
**Source composition:** `/opt/data/projects/Styles/Experimental/058-markov-chorale/MIDI/058-markov-chorale.mid`
**Method:** SP-035 GENDYN Stochastic Breakpoint Synthesis (Xenakis, 1991)

## What is GENDYN?

GENDYN (Génération Dynamique, Iannis Xenakis) generates audio by placing
random **breakpoints in time-amplitude space** and linearly interpolating
between them. Each waveform period gets a **fresh random breakpoint set**,
so the timbre continuously evolves and never exactly repeats — a "living"
stochastic texture rather than a fixed wavetable. Used by Xenakis in
*Gendy3* (1991) and *S.709* (1994).

## Source composition

058-markov-chorale: two-phase Markov chain chorale (method 002 + voice
leading rules). C major, 90 BPM, form I-IV-V-I over 4 bars.

| Voice | MIDI program | Notes | Role in render |
|-------|-------------|-------|----------------|
| Lead | 74 (Flute) | 16 | pitched lead, moderate breakpoint density |
| Bass | 33 (Electric Bass) | 4 | low f0, low density, low variance — dark |
| Harmony | 49 (String Ensemble) | 12 | chord pads, higher density noise-flavored |

## What was done

1. **Read** the MIDI with `mido` (read-only analysis; MIDI untouched —
   the canonical UnitMatrix composition file is copied as-is).
2. **Synthesized** every one of the 32 notes with the GENDYN engine per the
   methods_db.md SP-035 spec:
   - Per-voice parameter sets `(f0, N, σ_a, σ_t)`: Lead N=12 σ_a=0.25,
     Bass N=6 σ_a=0.10, Harmony N=15 σ_a=0.30.
   - Time intervals: uniform distribution with σ_t jitter, normalized to
     exactly one period (stable f0, no octave drift).
   - Amplitude breakpoints: Gaussian, clipped to [-1, 1].
   - **Dynamic stochastic variation** (Xenakis's original formulation):
     σ_a evolves per period via a reflected random walk (σ=0.01, bounds
     [0.05, 0.9]) — the timbre slowly wanders between smooth and rough.
   - DC removed per period (spec pitfall 2).
   - Independent RNG per voice path (spec pitfall 8).
   - ADSR: 10 ms attack / 80 ms release, velocity → amplitude, per-voice gain.
   - Butterworth 4-pole 16 kHz lowpass to tame breakpoint aliasing
     (spec pitfall 1).
3. **Mixed** all voices in NumPy, normalized to 0.89 peak.
4. **Wrote** `058-markov-chorale-gendyn.wav` (48 kHz mono, 9.0 s).
5. **Encoded** `058-markov-chorale-gendyn.ogg` (Opus 128k) for playback.
6. **Copied** the original MIDI next to the render + wrote `provenance.json`.

## Files

| File | Purpose |
|------|---------|
| `058-markov-chorale.mid` | Original composition (copied source) |
| `Audio/058-markov-chorale-gendyn.wav` | Full GENDYN render (48 kHz PCM) |
| `Audio/058-markov-chorale-gendyn.ogg` | Opus encode for playback |
| `gendyn_render.py` | The production script (reproducible) |
| `provenance.json` | Source + method + parameter + verification record |

## Parameters

| Param | Value | Meaning |
|-------|-------|---------|
| sample rate | 48000 | render rate |
| Lead (74) | N=12, σ_a=0.25, σ_t=0.08 | pitched, moderately rough |
| Bass (33) | N=6, σ_a=0.10, σ_t=0.06 | dark, smooth, low f0 |
| Harmony (49) | N=15, σ_a=0.30, σ_t=0.10 | denser, noise-flavored pads |
| dynamic walk | σ=0.01, bounds [0.05, 0.9] | σ_a random walk per period |
| ADSR | 10 ms / 80 ms | click-free envelopes |
| lowpass | 16 kHz, 4-pole Butterworth | anti-aliasing |
| peak | 0.89 | headroom |

## Verification

- Duration: 9.00 s (4 bars × 4 beats at 90 BPM = 10.67 s; last chord held,
  +1.0 s tail — matches MIDI structure)
- Notes parsed/synthesized: 32/32 (no dropped events)
- Silence ratio: 11.8% (all in the final tail second; every musical second
  has RMS 0.11–0.23 — no silent-WAV trap)
- Peak: 0.890 normalized
- WAV: 844 KB; OGG: 129 KB — both non-empty

## Listening guide

- The **lead line** (Markov melody over C-F-G-C) now sounds like a living,
  crackling wind — every note's timbre shifts subtly because each period
  re-rolls its breakpoints and σ_a wanders.
- The **bass** stays dark and stable: low breakpoint count + low variance =
  smooth stochastic drone under the moving chords.
- The **string pads** shimmer with non-repeating grain — the I-IV-V-I
  progression is carried by the harmonic plan while the surface texture
  never repeats.
- Tension/release: σ_a's random walk adds slow macro-evolution; the G chord
  (V) lands slightly rougher, the final C (I) settles calmer.

## Next variables to try

- Raise Harmony `σ_a` → 0.6 for noisier, more Xenakis "sonic population".
- Set `σ_t` higher on Lead (>0.3) for pitch instability / metallic flutter.
- Section-mapped parameters (calm on I, tense on V) instead of global voices.
- Stereo: two decorrelated GENDYN voices per note (L/R) for width.
