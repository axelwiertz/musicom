# 320-axel-style-study — the "axel" personal style (iteration 01)

First worked composition of the **`axel`** style — a genre-neutral personal
voice (guitar / violin / piano / percussion). This is iteration 01 of an
iterative development loop: compose → listen → refine → recompose.

## Style DNA

```
style = instrument DNA  ×  method paradigm  ×  (density · tempo · key)
```

| Axis | Value |
|---|---|
| **Instruments** | violin (40) · piano (1) · double_bass (43) · acoustic_guitar (24) · kit (ch9) |
| **Paradigm** | **abstract** (set-theory harmony) · **balanced** (hybrid density) · **harmonious** (tonal) · **changing** (variation operators) |
| **Envelope** | E major · 115 BPM · 4/4 · through-composed S1..S6 · −14 LUFS |

## What "changing" means here

One 16-note motif (`E G# B G# | A G# F# E | F# G# A B | C# B G# E`) evolves
across 6 sections through the engine's `variation.py` operators:

| Section | Harmony | Variation | What to listen for |
|---|---|---|---|
| S1 | I (E) | original | the seed motif |
| S2 | IV (A) | transpose +5 | motif lifted a 4th |
| S3 | vi (C#m) | invert (axis 68) | mirrored contour |
| S4 | V (B) | retrograde | the motif played backwards |
| S5 | ii (F#m) | density_scale 0.5 | sparse/thinned contrast |
| S6 | I (E) | transpose +12 | octave recap, resolve |

Two-phase: abstract variation (Phase 1) → snap to E-major scale (weak beats) +
section chord tones (strong beats 1 & 3), so every note stays diatonic
(harmonious). Harmony is a subset-walk I–IV–vi–V–ii–I with parsimonious
voice-leading (ABS-004 flavor).

## Files

```
MIDI/320-axel-style-study-perfect.mid     grid-locked truth (0 off-grid)
MIDI/320-axel-style-study-humanized.mid   style profile 5 ms / 5 / 0.35 / 2 ms
MIDI/320-axel-style-study.provenance.json
Audio/320-axel-style-study-{perfect,humanized}.wav / .ogg   (−14 LUFS)
Analysis/render_report.json               LUFS / true-peak / durations
Analysis/verification.json                zero-drift / off-grid / out-of-key / spectral
compose.py · render.py · verify.py
```

## Regenerate

```bash
cd /opt/data/repos/musicom/projects/Styles/Axel/320-axel-style-study
$MUSICOM_PYTHON compose.py && $MUSICOM_PYTHON render.py && $MUSICOM_PYTHON verify.py
```

## Verification (iteration 01)

| Gate | Result |
|---|---|
| zero-drift | ✓ all 5 note tracks = 46080 ticks |
| off-grid (perfect) | 0 |
| out-of-key (pitched) | 0 |
| LUFS | −14.0 / −14.0 |
| true peak | −1.77 / −1.74 dB |
| spectral dominant | E-major notes (E/G#/A/B/C#/F#) |
| harmonic energy (first 8) | ~30% (tonal) |

## Next iterations (refine with the user)

- ABS-002 subset-walker + ABS-003 Z-variation for the "abstract" axis
  (Z-variation needs tetrads, not triads — voice 7th chords).
- A production method (SP-*) for the humanized render (iteration 01 is dry).
- Register the variation arc itself as a reusable style-level build path.
