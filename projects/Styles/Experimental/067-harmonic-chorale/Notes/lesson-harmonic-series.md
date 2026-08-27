# Lesson — The Harmonic Series as a Composition Engine (067)

## What the harmonic series is

Every pitched sound (a string, an air column, a voice) vibrates not at one
frequency but at a stack of integer multiples of its fundamental:

```
f0, 2·f0, 3·f0, 4·f0, ...
```

In 12-TET semitone terms (rounded), starting from G3 = 55:

| Partial | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 |
|---------|---|---|---|---|---|---|---|---|---|----|----|----|----|----|----|----|
| MIDI    | 55 | 67 | 74 | 79 | 83 | 86 | 89 | 91 | 93 | 95 | 97 | 98 | 99 | 101 | 102 | 103 |
| Name    | G3 | G4 | D5 | G5 | B5 | D6 | B♭6 | G6 | A6 | B6 | F♯7 | D7 | E7 | B♭7 | C♯8 | G8 |

## Why partials 7, 11, 13, 14, 15 break the diatonic scale

The overtone series is a **just-intonation** structure: partial 7 is a
*harmonic seventh* (B♭ tuned ~31 cents flat of 12-TET B♭), partial 11 is
~49 cents sharp of F♯, partial 13 ~40 cents sharp of A♯/B♭. Even after
12-TET rounding, these land on non-diatonic pitch classes in F major —
that is why 34% of the raw draft leaks outside the key. This is not an
error; it is the acoustic truth the two-phase pipeline is designed to
tame. **Listening exercise:** compare the raw phase-1 file (open, brassy,
"slightly wrong" notes) against phase 2 — the same contour, now consonant.

## What Phase 2 did (musicom rules)

1. **Chord-tone quantization** — every raw partial snapped to the nearest
   tone of the section triad (I: F-A-C, vi: D-F-A, IV: B♭-D-F, V: C-E-G).
   E.g. raw 55 (G) → 65 (F); raw 89 (B♭) → 72 (C) in section I.
2. **Diatonic block harmony** — Alto/Tenor/Bass double the triad through
   `Scale7ChordDegree.get_diatonic_note()` (canonical helper; no
   off-by-octave wraps on degrees like vii/iii).
3. **Voice leading** — `optimize_voice_leading()` + Phase 2c inversion
   rotation: 0 parallel/hidden fifths remain.
4. **Harmonic function** — I→vi→IV→V all legal per the `function` map,
   ending on a perfect V→I cadence.

## Why rhythm followed the partials

Duration came from harmonic-number parity (odd → quarter, even → eighth).
Because the stride pattern (3,4,5,4) cycles through partials unevenly, the
quarter/eighth alternation itself shifts across sections — the "melody" and
the "groove" are one and the same data. That is the purest form of the
Musicom principle: **every musical element is a pattern**, and here the
pitch pattern *is* the rhythm pattern.

## Listening checklist

1. Phase 1: hear the acoustic "brass overtone" feel — partials climbing.
2. Phase 2: same contour, now harmonized; soprano jumps between chord tones.
3. Bars 5–6 (IV section): partials 9–12 (A6, B6, F♯7, D7) quantize to the
   B♭ chord — listen for the widest soprano leap.
4. Final V→I: C major → F major, the perfect cadence the function map promised.

## Next experiments

- Use a *different fundamental per section* (e.g. section tonic) — the
  overtone field then re-roots itself every two bars.
- Quantize raw partials to a *pentatonic* filter instead of triads (more
  blues, fewer leading tones).
- Feed phase-1 partial contours into a Markov chain (066) for a hybrid
  physics × probability method.
