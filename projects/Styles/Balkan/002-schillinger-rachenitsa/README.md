# 002 — Schillinger Rachenitsa (Balkan)

Balkan rachenitsa (7/8 dance) composed with the **Schillinger resultant** method
(`generators/schillinger.SchillingerGenerator`, a=7, b=2).

## Concept

- **Style**: Balkan (Rachenitsa, 7/8)
- **Key**: D harmonic minor (D E F G A Bb C#)
- **Tempo**: 132 BPM (eighth = 132)
- **Bars**: 8 × 7/8 (bar = 3360 ticks)
- **Harmony**: Dm – Bb – Gm – A (i – VI – iv – V), 2 cycles
- **Voices**: Lead flute, 3× string pads, bass, tapan (Balkan frame drum)

## Method

Phase 1 (raw draft): Schillinger resultant durations from generators 7 and 2,
sine-coordinate pitch projection on the scale — no harmony, single voice.

Phase 2 (rules): same resultant rhythm, pitches quantized to chord tones per
bar (chord-tone quantization), modal pads + walking drone bass + tapan
accents on pulses 1/4/6, zero-drift UnitMatrixComposer assembly.

## Files

- `MIDI/002-schillinger-rachenitsa.mid` — final Phase 2 (1221 B)
- `MIDI/002-schillinger-rachenitsa-phase1.mid` — raw Phase 1 (130 B)
- `Audio/002-schillinger-rachenitsa.wav` — FluidSynth render (5.2 MB, 30.5 s)
- `Audio/002-schillinger-rachenitsa.ogg` — Opus/Telegram (208 KB)
- `Analysis/grid_visualization.txt`, `provenance.json`, `summary.json`

## Verification

- validate() Phase 1: True (OK)
- validate() Phase 2: True (OK)
- Preflight: exit 0 (compliant)
- All artifacts > 40 bytes
- Silence: 14.1% (sustaining pads, healthy)

## Status

Fresh nightly composition 2026-08-22. Playable draft; next iteration could
add a second section (lesnoto 7/8 with different resultant, e.g. a=7, b=3),
or a paidushko (2-2-3) variation.
