# Vocal Singing Generation Research - Objectives

## Consonant Spectral Signatures
| Consonant | Type | Spectral Characteristic | Envelope |
|-----------|------|-------------------------|----------|
| **S** | Sibilant | High-pass noise > 5000Hz | 50ms Attack/Release |
| **SH** | Sibilant | Bandpass noise 2000-4500Hz | 50ms Attack/Release |
| **T** | Plosive | High-frequency burst > 3000Hz | 40ms Decay (Sharp) |
| **P** | Plosive | Low-frequency "thud" < 200Hz + Muted Noise | Rapid Decay |

## Progress Log: 2026-06-11
- Synthesized 'S' and 'SH' using filtered white noise (Butterworth filters).
- Generated vowel 'A' using sawtooth carrier and resonant peak filters (IIRPEAK) at F1=730, F2=1090, F3=2440.
- Successfully concatenated 'S' and 'A' for basic syllable synthesis.
- Exported PCM 16-bit WAV file.

## Next Steps
- Implement plosive 'T' and 'P' bursts.
- Smooth transitions between consonants and vowels (cross-fading).
- Implement pitch vibrato (LFO on carrier frequency).
