# SP-021: Binaural Woodworth-Schlosberg Spatialization — Here Comes the Sun

## Production Summary

**Source Composition**: `original.mid` (Rock/001-here-comes-the-sun)
**Production Method**: SP-021 — Binaural Woodworth-Schlosberg Spatialization
**Date**: 2026-08-10
**Duration**: 180.5 seconds
**Sample Rate**: 44100 Hz, 16-bit stereo

## Method Description

SP-021 applies Head-Related Transfer Function (HRTF) emulation to create immersive 3D spatialization over headphones. Unlike simple stereo panning (which only scales amplitude), binaural spatialization models:

1. **Interaural Time Difference (ITD)**: Sub-millisecond propagation delay to the far ear using the Woodworth-Schlosberg formula: `τ(θ) = (a/c) × (sin|θ| + |θ|)` where `a` = head radius (0.0875m), `c` = speed of sound (343 m/s), `θ` = azimuth angle. Max delay at ±90°: ~656 μs (~29 samples @ 44.1kHz).

2. **Interaural Level Difference (ILD)**: Frequency-dependent head-shadowing via dynamic first-order lowpass filter. Cutoff frequency drops as the source moves to the side: `f_c(θ) = f_min + (f_max - f_min) × ((1 + cos θ)/2)^p` with f_min=1kHz, f_max=20kHz, p=2.0.

3. **Distance Attenuation**: Inverse distance scaling for depth perception.

## Track Spatialization Map (Dynamic Azimuth Choreography)

Unlike the static placement in the disco SP-021 study, this production uses **time-varying azimuth** — the sound sources slowly orbit the listener, creating a living, cinematic soundstage.

| Track | Source Track | Channel | Azimuth Choreography | Range | Distance | Spatial Role |
|-------|-------------|---------|----------------------|-------|----------|--------------|
| Lead (melody, G#3–G#5) | 0 | 0 | Sine drift, base +0.5 rad, amp 0.9 rad, period 44s | −22.9° … +80.2° | 1.4m | Slow panoramic sweep (right → left → right) |
| Bass (foundation, D2–E4) | 1 | 0 | Center anchor, base 0.0 rad, amp 0.2 rad, period 22s | −11.5° … +11.5° | 1.0m | Stable center, subtle counter-drift |

**Rationale**: The bass stays anchored near center (groove lock, head-shadow filtering barely colors low frequencies anyway), while the lead melody drifts across the stereo field over a 44s cycle (~2 sections per sweep). The counter-phase bass drift at half the period keeps the center of mass stable. The lead is placed slightly further back (1.4m) than the bass (1.0m) for depth layering.

## Processing Pipeline

1. **MIDI Split**: Separated source MIDI into per-track files (Lead = track 0, Bass = track 1) via mido (read-only analysis; both source tracks share channel 0, so splitting is by track index)
2. **Mono Render**: Each track rendered to mono WAV via FluidSynth CLI with TimGM6mb.sf2
3. **Binaural DSP**: Applied SP-021 spatialization per track with dynamic (time-varying) azimuth; **chunked streaming** implementation (1s blocks) to respect the 3.9 GB RAM budget — fractional delay and one-pole filter carry state between chunks
4. **Per-track Stereo Files**: Each spatialized track written to its own stereo WAV on disk, then freed (two-pass architecture: spatialize → sum)
5. **Stereo Sum**: Accumulated per-track stereo WAVs into master bus
6. **Normalization**: Peak normalized to −1.0 dB (0.89 linear)
7. **Export**: WAV (16-bit PCM) + OGG (Opus 128kbps)

## Output Files

- `Audio/here_comes_the_sun_binaural_SP021.wav` — 31.8 MB, 44100 Hz, 16-bit stereo
- `Audio/here_comes_the_sun_binaural_SP021.ogg` — 3.6 MB, Opus 128kbps
- `Audio/lead_mono.wav` — Lead pre-spatialization mono render (intermediate)
- `Audio/bass_mono.wav` — Bass pre-spatialization mono render (intermediate)
- `Audio/lead_spatial.wav` — Lead spatialized stereo (per-track stem)
- `Audio/bass_spatial.wav` — Bass spatialized stereo (per-track stem)
- `MIDI/lead.mid` — Lead track (658 notes, G#3–G#5)
- `MIDI/bass.mid` — Bass track (286 notes, D2–E4)
- `MIDI/here_comes_the_sun_source.mid` — Original source (copy)

## Listening Notes

**Best experienced with headphones.** The binaural processing creates a 3D soundstage where:

- **Bass** anchors the center with only ±11.5° drift, keeping the groove solid
- **Lead melody** slowly orbits from −23° to +80°, creating motion across the piece
- **ITD cues** (~29 samples max at 44.1kHz) create realistic directional perception
- **ILD filtering** adds natural timbral shift — the far ear sounds darker, most noticeable when the lead is at extreme azimuth
- The **44s sweep period** means the panoramic motion is perceptible but unhurried — listen for the melody's position change between verse sections

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

**Memory-constrained DSP**: The full-length vectorized implementation peaked at ~670MB per delay pass (OOM on the 3.9GB box). The final implementation processes 1-second chunks with carried filter state and delay tails; peak working set stays under ~300MB.

## Quality Verification

- Silence ratio: **2.4%** (< 30% gate) — real sustained audio, no silent-render trap
- RMS: **0.1212**
- Active seconds: **178/181**
- Peak normalized to −1.0 dB

## References

- Method definition: `/opt/data/projects/Research/CompositionMethods/methods_db.md` (SP-021)
- Woodworth & Schlosberg (1954): "Experimental Psychology" — ITD derivation
- Algazi et al. (2001): "The CIPIC HRTF Database" — HRTF measurement
- Production script: `produce.py` (full DSP implementation)

## Provenance

See `provenance.json` for complete metadata including source composition details, method parameters, and processing timestamp.
