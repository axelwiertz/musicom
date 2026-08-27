# 045 - Wave Function Collapse Grid Synthesis & Wave Terrain Synthesis

A hybrid composition project combining algorithmic music structures and custom digital audio synthesis.

## Methods Used
- **Method 033: Wave Function Collapse Grid Synthesis (WFCGS)**
  - Resolves a 3x8 matrix (Lead, Pad, Bass over 8 bars) of musical superpositions using local horizontal and vertical adjacency constraints.
- **Method SP-022: Wave Terrain Synthesis (WTS)**
  - The entire Lead melody voice is synthesized by scanning a 2D sine-product terrain with a 1.5 ratio Lissajous orbit, using an envelope-controlled radius modulation to produce dynamic, filter-like vocal sweeps.

## File Structure
- `compose.py` - Complete grid collapse, multi-track MIDI generation, accompaniment FluidSynth rendering, custom NumPy WTS lead synthesis, mixing/mastering, and cleanup script.
- `index.html` - VoltAgent-themed (Black/Emerald) portfolio dashboard with rhythm DNA and download links.
- `MIDI/045-wfc-terrain.mid` - The final multi-track MIDI file.
- `Audio/045-wfc-terrain.ogg` - The final hybrid audio file (WTS Lead + FluidSynth Accompaniment).
- `Analysis/grid_visualization.txt` - High-contrast rhythm DNA density timeline.

## How to Run
```bash
/opt/data/micromamba/envs/musicom/bin/python compose.py
/opt/data/micromamba/envs/musicom/bin/python /opt/data/projects/Research/preflight_check.py .
```
