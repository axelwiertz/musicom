# Consonant Spectral Signatures for Vocal Synthesis

## Research Findings

| Consonant | Type | Spectral Characteristics | Envelope |
|-----------|------|-------------------------|----------|
| **S** | Sibilant | High-pass white noise. Energy peaks > 5000Hz. Sharp, narrow band. | 50ms attack, 50ms release. High sustain. |
| **SH** | Sibilant | Band-pass white noise. Energy peaks 2000Hz - 4000Hz. Broader than 'S'. | 60ms attack, 60ms release. High sustain. |
| **T** | Plosive | Sharp noise burst > 3000Hz. Rapid transient. | Immediate attack, 40ms decay. No sustain. |
| **P** | Plosive | Low-frequency "thud" < 200Hz + muted noise burst (0-1000Hz). | Rapid transient. 30ms-50ms decay. |

## Synthesis Logic
- **White Noise**: Base signal for all consonants.
- **Filtering**: Butter or IIR filters to shape the noise spectrum.
- **Envelopes**: ADSR or simple linear ramps to simulate articulation.
