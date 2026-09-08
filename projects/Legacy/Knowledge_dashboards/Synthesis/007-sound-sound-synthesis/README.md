# Pillar 2: Sound Synthesis

This project explores technical implementations of instrument synthesis without external libraries.

## Instruments
1. **Piano**: Traditional additive synthesis (fundamental + low-order harmonics) with an exponential decay envelope.
2. **Guitar**: Karplus-Strong string modeling. This uses a circular buffer of white noise that is averaged/filtered over time to simulate a plucked string's physical properties.
3. **Violin**: Sawtooth harmonic summation with frequency-modulated vibrato (6Hz) and a slow-attack bowing envelope.

## Scripts
- `synth_compare.py`: Generates A4 comparison notes.

## Results
Audio samples are generated as WAV and converted to OGG for instant playback.
