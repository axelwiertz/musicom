# 046 - PCFG Recursion & Digital Waveguide Woodwind (Clarinet) Synthesis

A hybrid composition project combining algorithmic music structures and custom digital audio synthesis.

## Methods Used
- **Method 034: Probabilistic Context-Free Grammar (PCFG) Recursion**
  - Synthesizes Lead, Pad, and Bass tracks from recursive probabilistic grammar rules mapped to diatonic Bb Major scale degrees, preserving thematic symmetry across 8 bars.
- **Method SP-023: Digital Waveguide Woodwind (Clarinet) Synthesis**
  - The Lead melody voice is synthesized using a physical modeling bidirectional delay-line woodwind clarinet model with a non-linear reed table equation, simulating breath pressure, breath noise, and open bell LPF reflections.

## File Structure
- `compose.py` - PCFG grammar expansion, multi-track MIDI generation, accompaniment FluidSynth rendering, custom NumPy physical clarinet modeling lead synthesis, mixing/mastering, and cleanup.
- `index.html` - VoltAgent-themed (Black/Emerald) portfolio dashboard with rhythm DNA and download links.
- `MIDI/046-pcfg-clarinet.mid` - The final multi-track MIDI file.
- `Audio/046-pcfg-clarinet.ogg` - The final hybrid audio file (Physical Clarinet Lead + FluidSynth Accompaniment).
- `Analysis/grid_visualization.txt` - High-contrast rhythm DNA density timeline.

## How to Run
```bash
/opt/data/micromamba/envs/musicom/bin/python compose.py
/opt/data/micromamba/envs/musicom/bin/python /opt/data/projects/Research/preflight_check.py .
```
