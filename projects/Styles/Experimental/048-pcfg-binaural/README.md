# Project 048: PCFG Recursion & Binaural Woodworth-Schlosberg Spatialization

Algorithmic music study leveraging Probabilistic Context-Free Grammar syntax model and 3D binaural spatialization.

## Methods
- **Composition**: Method 034: Probabilistic Context-Free Grammar (PCFG) Recursion
- **Sound Production**: Method SP-021: Binaural Woodworth-Schlosberg Spatialization

## Concepts
- **PCFG Recursion**: Models composition syntax using hierarchical grammar rules. Non-terminals (e.g. Phrase, Motif) recursively expand down to terminal note-gestures or rests, mapping exactly to 16 sixteenth-note steps (120 ticks each) per bar. This ensures a clean, hierarchical structure with zero track-drift.
- **Binaural Spatialization**: Simulates realistic 3D acoustic placement over headphones. Computes Interaural Time Difference (ITD) using the Woodworth-Schlosberg formula and Interaural Level Difference (ILD) via dynamic frequency-dependent head-shadowing lowpass filters.

## Structure
- **BPM**: 100
- **Scale**: C Dorian
- **Form**: 8 Bars of 1920 ticks each (zero track-drift aligned via `UnitMatrixComposer`).
- **Voices**: Lead (Violin), Pad (Synth string pad), Bass (Bass).
- **Spatial Map**:
  - `Lead`: Azimuth sweeps dynamically from left to right and back ($-\pi/2$ to $\pi/2$).
  - `Pad`: Spatialized to the left ($-\pi/4$).
  - `Bass`: Spatialized slightly right ($\pi/12$).

## Output Files
- `MIDI/048-pcfg-binaural.mid`: Full multi-track MIDI file.
- `Audio/048-pcfg-binaural.ogg`: Completed stereo master mix with true 3D spatialization. Peak-normalized to -1dB and compressed to high-quality Opus.
- `Analysis/grid_visualization.txt`: Rhythm DNA timeline.
- `index.html`: Black/Emerald VoltAgent dashboard.
