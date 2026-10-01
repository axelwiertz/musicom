# 216-lsystem-fractal

**Style:** Electronic · **Method:** 019 L-System Algorithmic Composition (concrete)
**Key:** A natural minor · **BPM:** 120 · **Form:** 8×4 bars (32 bars)

Fractal electronic piece built with a Lindenmayer rewrite system
(`generators.interval_lsystem`). The lead melody is a self-similar interval
walk; phase-2 musicom rules grid-lock (16th) and chord-quantize it onto
A-minor diatonic triads, with full pad/bass/arpeggio/sparkle/drum texture.

## Listen
- `Audio/216-lsystem-fractal.ogg` — full phase-2 render
- `Audio/216-lsystem-fractal-phase1.ogg` — raw L-system draft (single lead)

## Edit
- `MIDI/216-lsystem-fractal.mid` — phase 2 (DAW-ready)
- `MIDI/216-lsystem-fractal-phase1.mid` — phase 1 raw draft

## Verify (real numbers)
- Grid: **0 off-16th** across all 1515 onsets (6 voices).
- Harmony: **0 out-of-scale / 0 out-of-chord** across all 1199 pitched notes.
- Zero-drift: `validate()` PASSED both phases (61440 ticks all tracks).
- Audio: silence 6.6% (P2) / 7.4% (P1), tonal ≥ 97%.

## Regenerate
```bash
/opt/data/micromamba/envs/musicom/bin/python compose.py
/opt/data/micromamba/envs/musicom/bin/python render_audio.py
```

Full detail: `REPORT.md`.
