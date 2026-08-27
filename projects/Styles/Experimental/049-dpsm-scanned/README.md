# Project 049: Deconstructive Phase-Shift Minimalism & Scanned Synthesis

Algorithmic music study leveraging Deconstructive Phase-Shift Minimalism (DPSM) and a custom Scanned Synthesis physical modeling engine.

## Methods
- **Composition**: Method 026: Deconstructive Phase-Shift Minimalism (DPSM)
- **Sound Production**: Method SP-018: Scanned Synthesis Engine

## Concepts
- **Deconstructive Phase-Shift Minimalism (DPSM)**: Superimposes identical melodic loops and slides them out of phase over time. Voice 1 (Piano 1) remains static, while Voice 2 (Piano 2) shifts its phase by exactly one sixteenth note (120 ticks) per bar. This phase-shifting deconstructs the initial unison motif, yielding complex syncopated polyrhythms and emergent melodic patterns.
- **Scanned Synthesis (SP-018)**: Combines physical mass-spring-damper string modeling with wavetable scanning. A 64-mass physical string is initialized with a plucked shape and solved at a 100Hz control rate. An audio-rate cursor scans the displacement profile of the string at the pitch's fundamental frequency, creating a highly dynamic, warm, evolving acoustic waveform.

## Structure
- **BPM**: 110
- **Scale**: C Dorian
- **Form**: 8 Bars of 1920 ticks each (zero track-drift aligned via `UnitMatrixComposer`).
- **Voices**:
  - `Piano1`: Left Panned (75% L, 25% R), synthesized using custom Scanned Synthesis.
  - `Piano2`: Right Panned (25% L, 75% R), synthesized using custom Scanned Synthesis.
  - `Bass`: Center Panned (50% L, 50% R), rendered via FluidSynth (TimGM6mb SoundFont).

## Output Files
- `MIDI/049-dpsm-scanned.mid`: Full multi-track MIDI file.
- `Audio/049-dpsm-scanned.ogg`: Completed stereo master mix.
- `Analysis/grid_visualization.txt`: Rhythm DNA timeline.
- `index.html`: Black/Emerald VoltAgent dashboard.
