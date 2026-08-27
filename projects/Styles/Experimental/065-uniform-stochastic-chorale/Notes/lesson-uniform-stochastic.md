# Lesson — Why Phase 2 (Musicom Rules) Is Mandatory

**Project:** 065 — Uniform Stochastic Chorale · **Method:** 001

## The core idea

Some generative methods (Markov, L-systems, cellular automata, FHN) embed
musical grammar in their *generative* step. **Uniform stochastic sampling
embeds none.** It draws pitch and duration uniformly at random with zero
constraint — the raw output is musical noise.

That makes it the perfect teacher for the two-phase architecture:

```
Phase 1 (generative method)  ->  raw, unconstrained, chaotic material
Phase 2 (musicom rules)      ->  quantize -> harmonize -> voice-lead -> validate
```

## Listening / reading checklist

1. **Open `-phase1.mid` first.** One voice, pitches bounce across a 3-octave
   chromatic range (52–88), durations random. There is no key, no chord, no
   phrase. This is what "pure randomness" sounds like.

2. **Open `065-uniform-stochastic-chorale.mid`.** Four voices. The SAME 51
   onset points, but every pitch now sits on a D-minor diatonic chord tone;
   Alto/Tenor/Bass fill the triad; voice leading is smooth. It is a coherent
   chorale.

3. **Compare onset counts.** Both files have exactly **51** events — Phase 2
   did not add or remove notes; it only *re-pitched* them. That is the defining
   property of musicom rules post-processing: it repairs harmony without
   destroying the generative rhythm.

## What to notice

- **Quantization is lossy in pitch, faithful in time.** Raw `85` (a Bb5, off
  the Dm triad) lands on `69` (A4) — a big downward snap. The rhythm cell
  (start/end tick) is untouched.
- **Block harmony = the whole triad moves together.** Alto/Tenor/Bass play the
  same onset rhythm as soprano, on the triad's other two tones plus root.
  This is the "chordal texture" voice role.
- **Voice leading fixes register.** The final corrected triads
  `[[50,53,57],[62,65,70],[60,65,69],[60,64,67]]` keep the outer-voice motion
  small and the voicing inside comfortable ranges — 0 parallel/hidden fifths.

## The mental model

> Generative method = **what** (raw material, the seed of character).
> Musicom rules   = **why it works** (harmony, voice leading, form).

Choose a generative method for its *character* (MCWS = stepwise singable
wavefront; uniform stochastic = total entropy). The rules layer guarantees the
result is *musical* regardless of how chaotic the seed is.

## Next exercises

- Weight the stochastic distribution toward diatonic tones and listen to how
  much "cleaner" the raw draft already is.
- Apply Phase 2 to two different seeds and compare how much of the raw
  character survives quantization.
- Raise the voice-leading strictness to also flag hidden fifths automatically.