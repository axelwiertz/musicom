# Lesson — Hearing Phase Synchronization (Kuramoto, Method 038)

## What to listen for

1. **Bars 1–2 (K=0.5, r≈0.45):** the least locked. The soprano pulse train is
   irregular — oscillators drift past each other, no common downbeat pulse.
   Listen for the "breathing" irregularity of the attack spacing.
2. **Bars 3–4 (K=1.5, r≈0.48):** still loose, but the ensemble starts to
   entrain; note the density of attacks stabilizes.
3. **Bars 5–6 (K=2.5, r≈0.76):** the lock-in. All four oscillators emit at
   the same rate (wraps 9,9,9,9) — the four voices now move as one chordal
   block. This is the audible "phase transition".
4. **Bars 7–8 (K=4.0, r≈0.94):** fully locked, pulsing eighth-notes in block
   harmony, resolving to Fm. The cadence (Eb → Fm) lands like a settling.

## Why the rules pass works

- The raw draft's pitch is a continuous chromatic mapping of the oscillator's
  *effective frequency* — it wanders and leaks non-diatonic tones (4 of 31
  events in this seed). Phase 2 snaps every attack to the nearest chord tone
  of the active triad, so the melody is always a chord tone of
  Fm → Bbm → Eb → Fm.
- The rhythm (phase-wrap pulse train) is **not** quantized — the eighth-note
  grid of the locked sections is emergent, not imposed. The soprano keeps
  real oscillator timing; the block harmony follows it.
- Classical voice-leading pass (parallel/hidden fifth check + inversion
  rotation) reports 0 residual violations; the optimizer's minimal-distance
  voicings already avoid them.

## Genre rule tested

**Nature-led coupling as form.** The macro-form is not a harmonic template —
it is the physics of the order parameter. The same parameter sweep (K ramp)
in a different key/scale/progression would produce a different chorale with
the same dramatic arc.

## Next experiment ideas

- Add a 5th oscillator with a rational frequency (2.0) as a "conductor" —
  measure how fast r converges with K.
- Use the order-parameter *time series* (not the mean) to drive section
  boundaries: cut to the next chord exactly when r crosses 0.6.
- Couple the phase to tempo (oscillator frequency = BPM source) for a
  rubato chorale that slows as it locks.
