# SP-035 — GENDYN Stochastic Breakpoint Synthesis on 073-soul-rbmpd

**Date:** 2026-08-20 (nightly production job)
**Source composition:** `/opt/data/projects/Styles/Soul/073-soul-rbmpd/MIDI/073-soul-rbmpd.mid`
**Method:** SP-035 GENDYN Stochastic Breakpoint Synthesis

## What is GENDYN?

GENDYN (Génération Dynamique, Iannis Xenakis) generates audio by placing
random **breakpoints in time-amplitude space** and linearly interpolating
between them. Each waveform period gets a **fresh random breakpoint set**,
so the timbre is continuously evolving and never exactly repeats — a
"living" stochastic texture rather than a fixed wavetable.

## What was done

1. **Read** `073-soul-rbmpd.mid` with `mido` (analysis-only read; no MIDI authoring).
   - 11037 notes, 5 voices (Lead Pan Flute, Horns, Rhodes, Bass, Drums ch9),
     92 BPM, C minor soul.
2. **Synthesized** every note with the GENDYN engine:
   - Each period of the note gets `DENSITY=12` random amplitude breakpoints.
   - Time spacing jittered via exponential distribution (`TIME_VAR=0.6`).
   - Amplitude jumps scaled by `AMP_VAR=0.7` (wild but bounded).
   - Linear interpolation between breakpoints → the waveform.
   - ADSR envelope (A=20ms, D=100ms, S=0.6, R=300ms) shaped each note.
   - Velocity maps to amplitude; full mix normalized to 0.89 peak.
3. **Wrote** `073-soul-rbmpd-gendyn.wav` (48 kHz, mono, 62.9 s).
4. **Encoded** `073-soul-rbmpd-gendyn.ogg` (Opus 128k) for playback.

## Files

| File | Purpose |
|------|---------|
| `073-soul-rbmpd.mid` | Original composition (copied source) |
| `073-soul-rbmpd-gendyn.wav` | Full GENDYN render (48 kHz PCM) |
| `073-soul-rbmpd-gendyn.ogg` | Opus encode for playback |
| `provenance.json` | Source + method + parameter record |

## Parameters

| Param | Value | Meaning |
|-------|-------|---------|
| density | 12 | breakpoints per period |
| amp_var | 0.7 | amplitude jump variance |
| time_var | 0.6 | time-spacing irregularity |
| ADSR | 20ms/100ms/0.6/300ms | amplitude envelope |
| SR | 48000 | sample rate |

## Verification

- Duration: 62.91 s (matches 24-bar 92 BPM soul structure)
- Silence ratio: 1.5% (no silent-WAV trap; RMS present every second)
- Peak: 0.890 (normalized, headroom for clipping)
- WAV size: 6.0 MB; OGG size: 0.95 MB — both non-empty

## Listening guide

- The lead line now sounds like a **living, crackling wind** — every note's
  timbre shifts subtly because each period re-rolls its breakpoints.
- Drums (kick/snare/hats) become **noise-burst particles** — GENDYN at high
  density on unpitched hits reads as short stochastic transients.
- Rhodes comp chords shimmer with **non-repeating grain** — classic Xenakis
  "sonic population" effect instead of fixed static chords.
- Tension/release: stochastic volatility is constant, so the harmonic
  progression (i iv V III) carries the form; the intro's free-wander section
  sounds more chaotic, the outro's tonic pull more stable.

## Next variables to try

- Raise `density` → 24 for brighter, noisier timbre.
- Lower `amp_var` → 0.3 for a calmer, more vocal-like texture.
- `TIME_VAR=0` → uniform breakpoint spacing = smoother, less chaotic.
- Per-voice GENDYN params (drums get high density, pads low) instead of global.
