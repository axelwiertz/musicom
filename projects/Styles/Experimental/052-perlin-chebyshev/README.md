# 052-perlin-chebyshev

**Perlin Noise Composition (Method 040) + Chebyshev Waveshaping (SP-019)**

## Concept
- **Method 040**: Perlin noise drives pitch contour (fractal Brownian motion) and rhythm density
- **SP-019**: Chebyshev T5 polynomial shapes velocity mapping for harmonic-rich articulation
- **Key**: D minor (D E F G A Bb C)
- **Tempo**: 100 BPM
- **Structure**: 3 sections (A-B-C), 4 bars each
- **Voices**: Lead (Flute), Pad (Synth), Bass

## DNA
- **Pitch**: Perlin FBM → scale degree selection (continuous contour)
- **Rhythm**: 16 steps per section, quarter-note grid
- **Velocity**: Chebyshev T5(x) = 16x^5 - 20x^3 + 5x maps pitch index to dynamic range
- **Harmony**: Static chord per section (root-position D minor triad + 7th)

## Files
- `MIDI/052-perlin-chebyshev.mid` — editable DAW file
- `Audio/052-perlin-chebyshev.ogg` — Opus render (FluidSynth + peak norm)
- `Analysis/grid_visualization.txt` — rhythm DNA grid
- `src/compose.py` — generation script

## Run
```bash
/opt/data/micromamba/envs/musicom/bin/python src/compose.py
/opt/data/micromamba/envs/musicom/bin/python /opt/data/projects/Research/preflight_check.py .
```
