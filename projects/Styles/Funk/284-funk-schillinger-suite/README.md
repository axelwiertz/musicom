# 284-funk-schillinger-suite

**Style:** Funk · **Method:** 018 Schillinger System of Musical Design
**Date:** 2026-11-04 · **Key:** Bb major · **Tempo:** 100 BPM
**Form:** Intro / Verse / Chorus / Verse2 / Chorus2 / Bridge / Chorus3 / Outro
(8 × 4 bars = 32 bars) — rework of `081-funk-schillinger`.

## Concept

A funk suite built from Joseph Schillinger's rhythmic interference system. Two
periodic generators interfere into a resultant duration pattern — the raw
rhythmic DNA — which drives the trumpet lead. Phase 2 locks it to the 16th grid,
quantizes every pitch to its bar's chord, and wraps it in a classic funk texture:
trumpet lead, Rhodes comp, wah guitar stabs, octave bass pulse, clavinet horn
stabs + counterline, backbeat drums.

Eight variation techniques span the form: augmentation (Intro), register shift
(Choruses), transposition (Verse2), per-section method change + inversion + mode
shift (Bridge), counterline (Chorus3), retrograde (Outro).

## Per-section harmonic regions

| Section | Progression | Midpoint root |
|---|---|---|
| Intro | I – IV – V – I | IV |
| Verse | I – vi – ii – V | vi |
| Chorus | IV – V – I – vi | V |
| Verse2 | I – vi – ii – V | vi |
| Chorus2 | IV – V – I – vi | V |
| Bridge | vi – IV – I – V | IV |
| Chorus3 | IV – V – I – vi | V |
| Outro | I – IV – I – V | IV |

## Voices

Trumpet (lead) · Rhodes (comp) · Electric Guitar (wah stabs) · Electric Bass
(octave pulse) · Clavinet (horn stabs / counterline) · Drums (backbeat, ch 9).

## Two-phase architecture

- **Phase 1** (`-phase1.mid`): raw single-voice Schillinger walk, off-grid
  durations, no harmony.
- **Phase 2** (`-perfect.mid` / `-humanized.mid`): grid-lock → scale + per-bar
  chord-tone quantization → voice-leading → full texture. `-perfect` is the
  grid-locked truth (0 off-grid); `-humanized` adds style-derived micro-timing.

## Listen

- [perfect (grid-locked)](Audio/284-funk-schillinger-suite-perfect.ogg)
- [humanized (micro-timed)](Audio/284-funk-schillinger-suite-humanized.ogg)
- [MIDI (perfect)](MIDI/284-funk-schillinger-suite-perfect.mid)
- [MIDI (humanized)](MIDI/284-funk-schillinger-suite-humanized.mid)
- [MIDI (phase 1 raw)](MIDI/284-funk-schillinger-suite-phase1.mid)

## Notes

See `REPORT.md` for the full audit, variation plan, and verification numbers.
