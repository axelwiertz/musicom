# Lesson — Tendency Masking Stochastic Bounds (Method 023)

**Project:** 063-tendency-masking-chorale — D minor aeolian chorale, 8 bars, 92 BPM.
**Listen for:** `MIDI/063-tendency-masking-chorale.mid` (Soprano = Flute, Alto/Tenor = String Ensemble, Bass = Bass).

## What this method teaches

**Tendency masking** is stochastic pitch generation inside *dynamic frequency envelopes*. Instead of drawing from the whole scale uniformly (white-noise melody), the sampler is confined to a window `[lower, upper]` that glides linearly from a start bound to an end bound across each section. The envelope *masks* the tendency of the random walk: rising windows push the line up (growth, tension), falling windows pull it down (relaxation, resolution).

## The four sections as envelope experiments

| Section | Envelope | What you hear |
|---|---|---|
| i (Dm)  | 62→84 rising | opening arch: line climbs into the first phrase |
| VI (Bb) | 82→62 falling | relaxation: the line sinks back |
| III (F)  | 62→84 rising | second lift, pushing toward the dominant |
| VII (C) | 84→62 falling | final descent resolving to the tonic |

This is a **macro-level shape control**: the stochastic process keeps micro-level variety (which pitch inside the window is random), while the envelope guarantees macro-level phrasing (the overall rise/fall). That combination is exactly why the method is called "tendency masking" — the tendency (direction) is imposed, the detail (exact pitches) stays stochastic.

## Why the harmony works

`i - VI - III - VII` in D minor maps onto the `Scale7ChordDegree` function map:

- **i (Dm)** = tonic
- **VI (Bb)** and **III (F)** = tonic prolongation (share tones with i; F is the common third)
- **VII (C)** = dominant function (aeolian has no leading-tone diminished V — VII replaces it)
- **VII → i** = the authentic aeolian cadence (C major triad resolving to D minor), equivalent of V→I in major

The soprano was quantized to chord tones *after* the envelope draft, so every melody note is consonant with its section's triad — the "two-phase" architecture in one sentence: generate freely, then snap to the harmonic grid.

## Voice-leading flags — a real lesson

`VoiceLeadingRules(style="classical")` flagged **2 violations** on the i→VI transition:
- **Parallel fifths** between voices 1 and 3 (D-F-A → Bb-D-F: both chords contain the pitch F as a perfect fifth above the bass / root, moving in parallel).
- **Hidden fifth** in the outer voices (both outer voices move the same direction into the fifth).

These are **structurally unavoidable** in block homophony — any two chords a third apart sharing a common tone will produce one of these when voiced in root position. This is not a bug in the composition: it is the rule system *honestly surfacing* the classic textbook trap. Real chorale writers break the parallelism with passing tones, or composers accept it (pop/jazz style allows it).

## Listening checklist

1. Can you hear the four phrases rise → fall → rise → fall?
2. Does the VII (C) section feel like "the dominant" pulling back to Dm?
3. Tap the 16th-note grid — density is constant (~75%), so the *contour* does the storytelling, not the rhythm.
4. Note the SATB registers: soprano 64-74, alto 53-64, tenor 57-67, bass 38-48 — no crossings, classical spacing.

## Next exercises

- **Sparser texture:** density 0.5 — gaps between onsets become rests; the chorale turns antiphonal.
- **Style flip:** `VoiceLeadingRules(style="pop")` — the i→VI parallel fifths are permitted; compare how much "stricter" classical sounds.
- **Register contrast:** make the VII envelope extreme (e.g. 84→62) for a dramatic dominant plunge.
- **Chain the method:** run tendency masking per voice with *different* envelopes (soprano rising while bass falls) for independent-voice counterpoint.
