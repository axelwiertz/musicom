# SP-023 — Klezmer Freylekhs → Digital Waveguide Clarinet

## Overview
This project applies **Method SP-023** (Digital Waveguide Woodwind / Clarinet Synthesis) to a traditional Klezmer freylekhs melody, transforming the original MIDI composition into a physically modeled clarinet sound.

## Source Composition
- **File**: `original.mid`
- **Source**: `/opt/data/projects/Styles/Klezmer/klezmer-freylekhs-daily-2026-06-25/composition.mid`
- **Notes**: 162
- **Duration**: ~54.5 seconds
- **Style**: Klezmer freylekhs (lively Jewish dance, 2/4 or 4/4)

## Production Method: SP-023
**Digital Waveguide Woodwind (Clarinet) Synthesis**

Physical modeling synthesis simulating a single-reed wind instrument:
- Bidirectional delay line models wave propagation in cylindrical bore
- Non-linear reed junction (pressure-dependent scattering)
- Open-end bell reflection with frequency-dependent damping
- Self-sustained oscillation via breath pressure feedback

### Technical Parameters
- **Sampling rate**: 44.1 kHz
- **Model**: Closed-open pipe waveguide (clarinet acoustics)
- **Mouth pressure envelope**: ADSR-like, velocity-scaled (0.6–0.9)
- **Reed stiffness**: velocity-dependent (-0.4 to -0.25 slope)
- **Bell reflection**: 0.95 gain
- **Tube loss LPF**: 0.6 coefficient
- **Breath noise**: 0.015 (low turbulence)

### Key Features
- Natural woodwind embouchure and breath character
- Organic attack transients and decay tails
- Pitch-dependent resonance (delay line length = fs/(2*f0))
- No samples or wavetables — pure physical modeling

## Output Files

| File | Description | Size |
|------|-------------|------|
| `MIDI/original.mid` | Original Klezmer MIDI source | 4.3 KB |
| `Audio/SP023-klezmer-clarinet-wind.wav` | 16-bit PCM, mono, 44.1 kHz | 4.6 MB |
| `Audio/SP023-klezmer-clarinet-wind.ogg` | Opus VOIP, 48 kbps, mono | 342 KB |
| `Analysis/provenance.json` | Production metadata | — |
| `README.md` | This file | — |

## Listening Notes

### What to Hear
- **Breathy attacks**: Each note begins with reed turbulence and breath noise
- **Woody resonance**: Formant structure of cylindrical bore (odd-harmonic emphasis)
- **Natural decay**: High frequencies damp faster than lows (air absorption model)
- **Dynamic shaping**: Louder notes (higher velocity) have brighter, more intense timbre
- **Klezmer character preserved**: Rhythmic lilt and melodic contour intact, timbre transformed

### Technical Achievements
- 162 notes synthesized independently with correct timing
- No clicks or discontinuities (proper DC removal and normalization)
- Waveguide model stable across full pitch range (note 52–78)
- Polyphony handled via additive mixing (no inter-note artifacts)

## Production Workflow

1. **MIDI Analysis** — Parse note events (pitch, velocity, start/end times) from source MIDI
2. **Physical Modeling** — For each note, run SP-023 waveguide simulation at target pitch
3. **Mixing** — Additive superposition of all note waveforms at correct temporal positions
4. **Mastering** — Peak normalization to -0.5 dB, DC offset removal
5. **Export** — WAV (PCM) + OGG (Opus) for distribution

## Method Reference

See `/opt/data/projects/Research/CompositionMethods/methods_db.md` (lines 87, 1998–2141) for full technical specification of SP-023 Digital Waveguide Woodwind Synthesis.

## Verification

```bash
# File sizes
stat -c '%s %n' Audio/*.wav Audio/*.ogg MIDI/original.mid

# WAV integrity
file Audio/SP023-klezmer-clarinet-wind.wav

# Duration check
ffprobe -i Audio/SP023-klezmer-clarinet-wind.ogg -show_entries format=duration -v quiet
```

## Project ID
**SP-023** — Sound Production Method 023 applied to Klezmer source material.

---
*Generated autonomously by Hermes music production agent using musicom engine and SP-023 physical modeling synthesis.*
