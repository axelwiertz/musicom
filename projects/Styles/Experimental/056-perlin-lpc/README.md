# 056 — Perlin Noise × LPC Synthesis

**Style:** Experimental
**Composition Method:** 040 — Perlin Noise Composition (Nature-Led)
**Sound Production:** SP-028 — Linear Predictive Coding (LPC) Synthesis

## Concept

Perlin noise (fractal Brownian motion) drives all musical parameters:
- **Pitch**: Noise contour mapped to D Dorian scale degrees
- **Rhythm**: Noise threshold gates event density per voice
- **Velocity**: Noise amplitude modulates dynamic expression
- **Harmony**: Perlin-selected diatonic triads per bar

Post-processing via LPC analysis/synthesis extracts formant-like spectral
envelopes from the FluidSynth render and resynthesizes through an all-pole
IIR filter, adding vocal-tract coloration to the instrumental texture.

## Musical DNA

| Element | Value |
|---------|-------|
| Key | D Dorian |
| Tempo | 80 BPM |
| Form | ABA' (3 × 4 bars = 12 bars) |
| Voices | Lead (Flute), Pad (Strings), Bass (Electric Bass), Drums |
| Perlin Seed | 42 |
| FBM Octaves | 4 |
| LPC Order | 12 |
| Frame Size | 1024 samples |

## Files

- `MIDI/056-perlin-lpc.mid` — editable MIDI
- `Audio/056-perlin-lpc.ogg` — Opus render (LPC-processed)
- `Analysis/grid_visualization.txt` — rhythm DNA grid
- `src/compose.py` — composition script
- `src/apply_lpc.py` — LPC post-processing

## Run

```bash
/opt/data/micromamba/envs/musicom/bin/python src/compose.py
/opt/data/micromamba/envs/musicom/bin/fluidsynth -ni -g 1.2 -F Audio/056-perlin-lpc_raw.wav /path/to/sf2 MIDI/056-perlin-lpc.mid
/opt/data/micromamba/envs/musicom/bin/python src/apply_lpc.py
/opt/data/micromamba/envs/musicom/bin/python src/normalize.py
ffmpeg -i Audio/056-perlin-lpc_norm.wav -codec:a libopus -application voip -b:a 48k Audio/056-perlin-lpc.ogg -y
```
