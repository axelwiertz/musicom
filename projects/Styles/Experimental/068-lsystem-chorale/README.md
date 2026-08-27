# 068 — L-System Chorale (Method 019)

**Composition method:** 019 — L-System Algorithmic Composition (`sound/generators/event_core.py` → `LSystemCore`)

## Concept

An **L-system (Lindenmayer system)** generates structure by string rewriting:
start from an axiom, replace every symbol by a rule, repeat. Method 019 uses
the canonical **Fibonacci word** grammar — axiom `A`, rules `{A → AB, B → A}` —
which is the same grammar the engine's own `LSystemCore` smoke test runs.
After 6 iterations the word has **21 symbols** (length F(8)=21) and is
strictly self-similar at every scale: `ABAABABAABAABABAABABA` is literally
built from two shifted copies of the previous word. That fractal property is
the musical idea: motif fragments recur at nested scales, never identically.

Raw symbol semantics (Phase 1): `A` steps pitch **+2 semitones** (quarter
note), `B` steps pitch **−2 semitones** (eighth note). The word cycles re-enter
at rotation offsets `(0, 5, 3, 8)` so every re-entry of the word starts at a
different phase — self-similar, never a literal repeat. Timeline truncated at
the 8-bar boundary.

## Parameters

| Param | Value |
|-------|-------|
| Key | A minor (aeolian) |
| BPM | 76 |
| Meter | 4/4 (480 tpb, 1920 ticks/bar) |
| Form | 4 sections × 2 bars = 8 bars |
| Harmony | i - VI - v - i (Am - F - Em - Am) |
| Voices | Soprano (Flute), Alto/Tenor (Strings), Bass |
| Grammar | axiom `A`, rules `{A: AB, B: A}`, 6 iterations → 21-symbol Fibonacci word |
| Symbol semantics | A → pitch +2 st, quarter; B → pitch −2 st, eighth |
| Cycle offsets | (0, 5, 3, 8) |
| Start pitch | A4 (MIDI 69), clamp G3..C6 |
| Seed | 68 (deterministic grammar — no rng) |

## Why the Raw Draft Leaks (pre-rules signature)

The raw pitch walk is **chromatic**, not diatonic: a +2 step taken from scale
degree 2 (B) or 7 (E) of A minor lands on C♯ / D♯ — outside the key. The
Fibonacci word is rich in such moments, so **13 of 40 raw events (33%) are
non-diatonic**, proof the Phase 1 file is genuinely pre-rules: no scale
enforcement, no chord context, no voice leading. (Sibling: 067 leaked 34% via
harmonic partials; 068 leaks via the fractal symbol walk.)

## Two-Phase Architecture

- **Phase 1 — raw draft** (`MIDI/068-lsystem-chorale-phase1.mid`):
  single voice, raw ±2-semitone chromatic walk, rhythm = symbol identity
  (A:quarter / B:eighth). Chromatic leak present (see above).
- **Phase 2 — rules-processed** (`MIDI/068-lsystem-chorale.mid`):
  each raw pitch snapped to the nearest diatonic triad tone (soprano,
  range 65–86), Alto/Tenor/Bass built as diatonic block harmony via the
  canonical `Scale7ChordDegree.get_diatonic_note()`, voice-leading optimized,
  Phase 2c inversion-rotation correction applied, harmonic function validated.

## Validation

- Phase 1 zero-drift `validate()`: **PASS (True)**
- Phase 2 zero-drift `validate()`: **PASS**
- Both files: max track end tick = 15360 (= 4 × 3840), all tracks equal length
- Parallel/hidden fifth violations (classical): **0** (0 chords needed re-voicing)
- Harmonic function report: i→VI (tonic→any, legal), VI→v (prolongation,
  free), v→i (dominant→tonic, **perfect cadence**) — closed form.

## Artifacts

```
MIDI/068-lsystem-chorale.mid              (1569 B, 5 tracks / 4 voices)
MIDI/068-lsystem-chorale-phase1.mid       (417 B, 1 raw voice)
MIDI/*.mid.provenance.json                (both artifacts)
Analysis/grid_visualization.txt           (4×4, 3840 ticks/section)
Notes/lesson-lsystem-fractal.md
compose.py                                (generator, deterministic)
```

## Status

DONE — MIDI only (no audio render, per composition-job contract). Standalone
project under `Styles/Experimental/`.
