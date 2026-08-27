# Lesson — L-Systems: Music as String Rewriting

## What an L-system is

An L-system is a parallel string-rewriting grammar (A. Lindenmayer, 1968).
You have:

- an **axiom** (start string),
- **rules** mapping each symbol to a replacement string,
- an **iteration count**.

At every iteration, ALL symbols are rewritten at once (parallel — that is the
difference from Chomsky grammars, which rewrite one symbol at a time). The
engine's `LSystemCore` (in `sound/generators/event_core.py`) implements this
with `axiom`, `rules`, `generate(iterations)` and `generate_mapped(...)`.

## The Fibonacci word — the grammar we used

```
axiom:  A
rules:  A -> AB
        B -> A

iter 0: A
iter 1: AB
iter 2: ABA
iter 3: ABAAB
iter 4: ABAABABA
iter 5: ABAABABAABAAB
iter 6: ABAABABAABAABABAABABA   (21 symbols = F(8))
```

Properties that matter musically:

1. **Lengths are Fibonacci numbers** — the word grows exponentially
   (φ ≈ 1.618 per iteration).
2. **Self-similarity** — every word is two shifted copies of the previous
   word: `W(n) = W(n-1) + W(n-2)` (literally `ABAAB` = `ABA` + `AB`).
   So the *whole* piece's pitch contour contains the *first phrase* as a
   substring — the motif is embedded at every scale. That is the fractal
   fingerprint of Method 019.
3. **No periodicity** — the word never repeats exactly; every re-entry
   (we rotate by offsets 0, 5, 3, 8) starts at a different phase.

## Listen for this

- **Phase 1 (raw draft)**: a restless chromatic walk. Pitch ratchets +2,
  −2, +2, +2, −2… The quarter/eighth alternation comes straight from the
  A/B symbol count: 13 A's (quarters) and 8 B's (eighths). You can HEAR the
  fractal: the opening `A B A` (up–down–up, long-short-long) reappears inside
  later material at other scale positions.
- **Phase 2 (chorale)**: the same rhythm and the same contour, but every
  pitch now sits inside Am / F / Em / Am triads. The chromatic ratchet
  becomes a diatonic melody that ends where it started (i → VI → v → i).
  Compare: identical skeletons, totally different grammar — raw vs. tonal.

## The rule being tested

Method 019's claim: **self-similar rewrite rules generate melodic structure
that is coherent at multiple time scales without any probabilistic memory.**
The Phase-1 melody is deterministic (no rng) yet never repeats a bar exactly —
a contrast with 066 (Markov, probabilistic memory) and 065 (memoryless Monte
Carlo), and a sibling of 067 (harmonic series: physics) — 068's raw material
comes from *formal language theory*.

## Next experiments

1. **Dragon curve grammar** (`A → A+B`, `B → A-B`, with turning symbols) —
   more angular contour, larger step vocabulary.
2. **Koch curve grammar** (`F → F+F-F-F+F`) mapped to 5-note groups —
   the classic `F+F-F-F+F` self-similar snowflake melody (see old
   `examples/compose_v1_lsystem.py`).
3. **Multiple voices from one word** — bass takes symbols at half speed
   (augmentation), soprano at full speed; canon-like fractal layering.
4. **Non-uniform rotation offsets** (e.g. `(0, 7, 2, 11)`) to make the
   re-entries land on different chord tones per section.
