# 055 — Neural Spiking + Feedback Delay

**Composition Method:** 037 — FitzHugh-Nagumo Neural Spiking (FHNS)  
**Sound Production:** SP-013 — Feedback Delay Line with HF Damping  
**Key:** E minor (aeolian)  
**Tempo:** 100 BPM  
**Form:** A(4 bars) - B(8 bars) - A'(4 bars)  
**Duration:** ~41 seconds

---

## Overview

Project 055 explores the intersection of neural dynamics and algorithmic composition. Each voice runs an independent FitzHugh-Nagumo neuron simulation, where voltage threshold crossings trigger musical events. The resulting rhythms are organic and non-repetitive, shaped by the neuron's refractory periods and recovery dynamics.

The composition is then processed through a feedback delay line with high-frequency damping (SP-013), simulating analog tape warmth where each echo becomes progressively darker.

---

## Method 037: FitzHugh-Nagumo Neural Spiking

The FitzHugh-Nagumo model is a simplified neuron simulation with two state variables:

- **v**: Membrane voltage (fast variable)
- **w**: Recovery current (slow variable)

### Equations

```
dv/dt = v - v³/3 - w + I_ext
dw/dt = (v + a - b·w) / τ
```

### Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| a | 0.7 | Recovery dynamics |
| b | 0.8 | Damping factor |
| τ | 12.5 | Time constant |
| Threshold | 0.5 | Spike detection threshold |

### Voice Configuration

Each voice has a different external drive current (I_ext), creating distinct firing patterns:

| Voice | I_ext | Refractory (ticks) | Octave | Instrument |
|-------|-------|-------------------|--------|------------|
| Lead | 0.6 | 120 (eighth note) | 4 | Flute (73) |
| Tenor | 0.8 | 180 (dotted eighth) | 3 | Piano (0) |
| Bass | 0.35 | 480 (quarter note) | 2 | Electric Bass (33) |
| Pad | 0.25 | 960 (half note) | 3 | Strings (48) |

Higher drive = faster spiking = denser texture. The Tenor (I=0.8) fires most rapidly, while the Pad (I=0.25) produces sparse, sustained events.

### Pitch Mapping

Voltage values at spike onset are quantized to the E minor scale:
- v ∈ [-2, +2] → normalized to [0, 1]
- Mapped to scale degrees: E F# G A B C D
- Velocity proportional to voltage magnitude

---

## SP-013: Feedback Delay with HF Damping

Post-render DSP effect simulating analog tape delay characteristics.

### Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| Delay Time | 375 ms | Dotted eighth note at 100 BPM |
| Feedback | 0.45 | Echo regeneration amount |
| LP Coefficient | 0.3 | Low-pass filter cutoff (0=dark, 1=bright) |
| Normalization | -1 dB | Peak normalization target |

### Implementation

The delay line includes a first-order low-pass filter in the feedback path:

```
filtered[n] = α · delayed[n] + (1 - α) · filtered[n-1]
output[n] = input[n] + g · filtered[n]
```

Where:
- α = LP coefficient (0.3)
- g = feedback gain (0.45)

Each echo passes through the filter, progressively attenuating high frequencies. This creates the characteristic "warm" analog delay sound where repetitions become darker over time.

---

## File Structure

```
055-neural-spiking-delay/
├── README.md
├── index.html                    # Interactive dashboard
├── MIDI/
│   ├── 055-neural-spiking-delay.mid
│   └── 055-neural-spiking-delay.mid.provenance.json
├── Audio/
│   └── 055-neural-spiking-delay.ogg
├── Analysis/
│   └── grid_visualization.txt
└── src/
    ├── compose.py                # FHN composition engine
    └── apply_sp013.py            # Feedback delay processor
```

---

## Listening Guide

**What to listen for:**

1. **Organic Rhythms**: Unlike quantized patterns, the neural spikes create irregular, human-like timing. Notice how the Lead and Tenor interlock without mechanical precision.

2. **Refractory Gaps**: Each neuron has a recovery period after firing. These gaps create natural breathing room in the rhythm.

3. **Pitch Contours**: Voltage fluctuations map to melodic motion. Higher voltages = brighter timbre and higher velocity.

4. **Delay Tails**: After each phrase, listen for the echoing repetitions. Notice how they become progressively darker and softer.

5. **Textural Layers**: 
   - Lead (Flute): Fast, melodic spikes
   - Tenor (Piano): Dense, rhythmic foundation
   - Bass: Sparse, grounding pulses
   - Pad (Strings): Slow, atmospheric swells

---

## Reproduction

### Prerequisites

```bash
# Activate musicom environment
conda activate musicom

# Verify dependencies
python -c "import musicom; import numpy; print('OK')"
```

### Generate MIDI

```bash
cd /opt/data/projects/Styles/Experimental/055-neural-spiking-delay
python src/compose.py
```

This generates:
- `MIDI/055-neural-spiking-delay.mid`
- `MIDI/055-neural-spiking-delay.mid.provenance.json`
- `Analysis/grid_visualization.txt`

### Render Audio

```bash
# Render MIDI to WAV using FluidSynth
fluidsynth -ni /usr/share/sounds/sf2/FluidR3_GM.sf2 \
  MIDI/055-neural-spiking-delay.mid \
  -F Audio/055-neural-spiking-delay.wav

# Apply SP-013 feedback delay
python src/apply_sp013.py

# Convert to OGG
ffmpeg -i Audio/055-neural-spiking-delay_normalized.wav \
  -c:a libopus -b:a 64k \
  Audio/055-neural-spiking-delay.ogg

# Cleanup
rm Audio/055-neural-spiking-delay_normalized.wav
```

### View Dashboard

Open `index.html` in a web browser for interactive visualization of the rhythm DNA and composition parameters.

---

## Preflight Check

```bash
python /opt/data/projects/Research/preflight_check.py \
  /opt/data/projects/Styles/Experimental/055-neural-spiking-delay
```

Expected output: `✅ COMPLIANT`

---

## Technical Notes

### Zero-Drift Guarantee

The composition uses `UnitMatrixComposer` with strict validation:
- All tracks padded to exact section boundaries
- Note-off events sorted before note-on at identical ticks
- MIDI export validated for temporal consistency

### FHN Stability

The FitzHugh-Nagumo simulation uses Euler integration with dt=0.01. For these parameters (a=0.7, b=0.8, τ=12.5), the system is stable and produces limit-cycle oscillations (repetitive spiking) for I_ext > 0.3.

### Delay Line Artifacts

The feedback delay uses a circular buffer with linear interpolation. At 44.1kHz sample rate and 375ms delay, the buffer size is 16,537 samples. No audible artifacts expected at this resolution.

---

## References

- FitzHugh, R. (1961). "Impulses and Physiological States in Theoretical Models of Nerve Membrane." *Biophysical Journal*
- Nagumo, J. et al. (1962). "An Active Pulse Transmission Line Simulating Nerve Axon." *Proceedings of the IRE*
- Musicom Method 037 specification: `/opt/data/projects/Research/CompositionMethods/methods_db.md`
- SP-013 implementation notes: Same source

---

## License

Generated by Musicom AI composition system.  
Method 037 + SP-013 | 2026-08-01
