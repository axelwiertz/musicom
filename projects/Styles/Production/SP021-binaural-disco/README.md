# SP-021: Binaural Woodworth-Schlosberg Spatialization — Classic Disco

## Production Summary

**Source Composition**: `classic_disco.mid` (Disco/classic/v1)  
**Production Method**: SP-021 — Binaural Woodworth-Schlosberg Spatialization  
**Date**: 2026-08-03  
**Duration**: 68.4 seconds  
**Sample Rate**: 44100 Hz, 16-bit stereo

## Method Description

SP-021 applies Head-Related Transfer Function (HRTF) emulation to create immersive 3D spatialization over headphones. Unlike simple stereo panning (which only scales amplitude), binaural spatialization models:

1. **Interaural Time Difference (ITD)**: Sub-millisecond propagation delay to the far ear using the Woodworth-Schlosberg formula: `τ(θ) = (a/c) × (sin|θ| + |θ|)` where `a` = head radius (0.0875m), `c` = speed of sound (343 m/s), `θ` = azimuth angle.

2. **Interaural Level Difference (ILD)**: Frequency-dependent head-shadowing via dynamic first-order lowpass filter. Cutoff frequency drops as source moves to the side: `f_c(θ) = f_min + (f_max - f_min) × ((1 + cos θ)/2)^p`

3. **Distance Attenuation**: Inverse distance scaling for depth perception.

## Track Spatialization Map

| Track | Channel | Azimuth | Distance | Spatial Position |
|-------|---------|---------|----------|------------------|
| Drums | 9 | 0.0° | 1.5m | Center, slightly back |
| Bass | 0 | 0.0° | 1.0m | Center, front |
| Strings | 1 | -45.8° | 1.2m | Left, mid-distance |
| Lead | 2 | +40.1° | 1.0m | Right, front |

**Rationale**: Disco production typically places drums and bass center for groove lock, strings panned left for warmth, lead synth right for melodic clarity. The binaural processing adds realistic 3D depth beyond simple panning.

## Processing Pipeline

1. **MIDI Split**: Separated source MIDI into per-track files (Drums, Bass, Strings, Lead)
2. **Mono Render**: Each track rendered to mono WAV via FluidSynth CLI with TimGM6mb.sf2
3. **Binaural DSP**: Applied SP-021 spatialization per track with unique azimuth/distance
4. **Stereo Sum**: Accumulated all spatialized tracks into master stereo bus
5. **Normalization**: Peak normalized to -1.0 dB (0.89 linear)
6. **Export**: WAV (16-bit PCM) + OGG (Opus 128kbps)

## Output Files

- `Audio/disco_binaural_SP021.wav` — 12.1 MB, 44100 Hz, 16-bit stereo
- `Audio/disco_binaural_SP021.ogg` — 1.1 MB, Opus 128kbps
- `MIDI/disco_drums.mid` — Drums only
- `MIDI/disco_bass.mid` — Bass only
- `MIDI/disco_strings.mid` — Strings only
- `MIDI/disco_lead.mid` — Lead only
- `MIDI/classic_disco_source.mid` — Original source (copy)

## Listening Notes

**Best experienced with headphones.** The binaural processing creates a 3D soundstage where:

- **Drums and Bass** anchor the center with slight depth separation (drums further back)
- **Strings** emerge from the left with high-frequency roll-off simulating head shadow
- **Lead synth** sits on the right with full bandwidth (closer to listener)
- **ITD cues** (~0.6ms max delay) create realistic directional perception
- **ILD filtering** adds natural timbral shift — far ear sounds darker

Compare with the original mono or simple-panned stereo mix to hear the spatial depth difference.

## Technical Details

**Woodworth-Schlosberg ITD Formula**:
```
τ(θ) = (a/c) × (sin|θ| + |θ|)
Max delay at ±90°: ~656 μs (~29 samples @ 44.1kHz)
```

**Head Shadow Filter**:
```
f_c(θ) = 1000 + 19000 × ((1 + cos θ)/2)^2
α = (2π f_c / f_s) / (2π f_c / f_s + 1)
y[n] = α × x[n] + (1-α) × y[n-1]
```

**Fractional Delay**: Linear interpolation for sub-sample ITD precision.

## References

- Method definition: `/opt/data/projects/Research/CompositionMethods/methods_db.md` (SP-021)
- Woodworth & Schlosberg (1954): "Experimental Psychology" — ITD derivation
- Algazi et al. (2001): "The CIPIC HRTF Database" — HRTF measurement
- Production script: `produce.py` (full DSP implementation)

## Provenance

See `provenance.json` for complete metadata including source composition details, method parameters, and processing timestamp.
