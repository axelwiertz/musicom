# 044 - Isorhythmic Spatial Composition Study

Experimental composition project using the **musicom** engine.

## Methods Used
- **Method 032: Isorhythmic Talea-Color Mapping (ITCM)**
  - Decoupled, coprime rhythm loops (Talea) and pitch loops (Color) across 4 tracks: Lead, Bass, Pad, and Drums.
- **Method SP-021: Binaural Woodworth-Schlosberg Spatialization**
  - High-fidelity 3D spatialization post-processing DSP simulating ITD and frequency-dependent ILD head-shadowing. The Lead violin orbits the head continuously at 0.125 Hz.

## File Structure
- `compose.py` - Core composition, rendering, spatialization, and cleanup pipeline script.
- `index.html` - VoltAgent-themed dashboard with rhythm DNA and download links.
- `MIDI/044-isorhythmic-spatial.mid` - The final multi-track MIDI file.
- `Audio/044-isorhythmic-spatial.ogg` - The final spatialized binaural audio file.
- `Analysis/grid_visualization.txt` - High-contrast rhythm DNA density timeline.

## How to Run
```bash
/opt/data/micromamba/envs/musicom/bin/python compose.py
/opt/data/micromamba/envs/musicom/bin/python /opt/data/projects/Research/preflight_check.py .
```
