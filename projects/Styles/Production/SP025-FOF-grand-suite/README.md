# SP-025: Formant-Wave-Function (FOF) Synthesis

**Production Date:** 2026-08-04  
**Source Composition:** grand_suite_v1_3.mid (Balfolk Grand Suite)  
**Method ID:** SP-025  
**Method Name:** Formant-Wave-Function (FOF) Synthesis

---

## Overview

This production applies **Formant-Wave-Function (FOF) synthesis** to the Balfolk Grand Suite composition. FOF synthesis is a time-domain audio synthesis method developed at IRCAM for synthesizing singing voices and resonant instrument timbres.

Instead of using traditional wavetable synthesis or physical modeling, FOF synthesis triggers decaying cosine wave-packets at the fundamental frequency of each MIDI note. Multiple formant channels sum to create vocal-like, resonant timbres with precise control over spectral characteristics.

---

## Technical Implementation

### FOF Synthesis Engine

Each MIDI note is synthesized using the FOF algorithm:

1. **Wave Packet Generation**: A single FOF wave packet is defined as:
   ```
   g(τ) = a · e^(-α·τ) · sin(2π·fc·τ)
   ```
   where:
   - `τ` = time since packet onset
   - `a` = amplitude
   - `fc` = formant center frequency (Hz)
   - `α` = decay coefficient (determines bandwidth)

2. **Periodic Triggering**: Wave packets are triggered at intervals of `T0 = 1/f0` (fundamental period), creating a continuous tone.

3. **Multi-Formant Summation**: Multiple formant channels (F1, F2, F3, F4) run in parallel, each with distinct center frequencies and bandwidths. The outputs sum to create complex timbres.

### Formant Presets by Track

Each track receives a distinct formant preset to create timbral variety:

| Track | Formant Preset | F1 (Hz) | F2 (Hz) | F3 (Hz) | F4 (Hz) | Character |
|-------|----------------|---------|---------|---------|---------|-----------|
| **Violin** | Soprano "Ah" | 800 | 1200 | 2500 | 3500 | Bright, open, forward |
| **Piano** | Alto "Oh" | 500 | 1000 | 2400 | 3300 | Warm, rounded, mellow |
| **Acoustic Guitar** | Tenor "Ee" | 400 | 2200 | 2800 | 3600 | Bright, nasal, articulate |
| **Woodblock** | Percussive Click | 1000 | 3000 | 6000 | — | Wide bandwidth, noise-like |

### Processing Parameters

- **Sample Rate:** 44100 Hz
- **Attack Time:** 8 ms (smooth onset)
- **Decay Time:** 30 ms (formant settling)
- **Sustain Level:** 0.6 (steady-state amplitude)
- **Release Time:** 40 ms (smooth offset)
- **Jitter:** 2 ms (subtle humanization of trigger timing)
- **Master Gain:** -1 dB peak normalization

---

## Output Files

### Master Mix
- **grand_suite_fof_synthesis.wav** (6.3 MB) — Full mix, all tracks summed
- **grand_suite_fof_synthesis.ogg** (204 KB) — Compressed Opus for streaming/Telegram

### Individual Stems (per-track renders)
- **stems/Violin_fof.wav** — Violin track with Soprano "Ah" formants
- **stems/Piano_fof.wav** — Piano track with Alto "Oh" formants
- **stems/Acoustic Guitar_fof.wav** — Guitar track with Tenor "Ee" formants
- **stems/Woodblock_fof.wav** — Percussion track with wide-bandwidth click formants

### Source Material
- **source_midi.mid** — Original MIDI file (5.0 KB)

---

## Listening Guide

### What to Listen For

1. **Vocal Quality**: The FOF synthesis creates a choir-like, vocal quality. Each track sounds like a different voice type singing the melody.

2. **Formant Character**: 
   - Violin (Soprano "Ah"): Bright, open, forward projection
   - Piano (Alto "Oh"): Warm, rounded, mellow
   - Guitar (Tenor "Ee"): Bright, nasal, articulate attack
   - Woodblock (Percussive): Click-like, wide bandwidth, noise-like

3. **Resonant Decay**: Unlike traditional synthesis, FOF creates a natural resonant decay as the formant wave-packets overlap and sum.

4. **Humanization**: Subtle 2ms jitter on trigger timing creates organic micro-timing variations.

5. **Timbral Contrast**: The different formant presets create distinct timbral identities for each track, even though they all use the same synthesis engine.

---

## Method Notes

### Why FOF Synthesis?

FOF synthesis is particularly suited for:
- **Vocal-like timbres**: Directly models vocal tract resonances in the time domain
- **Smooth transitions**: Overlapping wave-packets create seamless, continuous tones
- **Precise spectral control**: Each formant's center frequency and bandwidth are independently adjustable
- **Computational efficiency**: Avoids expensive post-excitation resonant filters

### Comparison to Other Methods

- **vs. SP-015 (Formant Vowel Filter Synthesis)**: FOF operates in time-domain (wave-packets), while SP-015 uses frequency-domain parallel bandpass filters
- **vs. SP-028 (LPC Synthesis)**: FOF uses overlapping wave-packets (time-domain), while LPC uses all-pole IIR filters (parametric, compact)
- **vs. SP-001 (SoundFont)**: FOF synthesizes from scratch using mathematical models, while SoundFont uses pre-recorded samples

### Integration with Musicom

This production demonstrates the **two-phase architecture**:
- **Phase 1**: MIDI composition (Balfolk Grand Suite) defines pitch, rhythm, harmony, structure
- **Phase 2**: FOF synthesis engine renders the symbolic MIDI data into acoustic audio using formant-based physical modeling

The MIDI structure (zero-drift, UnitMatrix-validated) is preserved exactly; only the timbral rendering changes.

---

## Provenance

See `provenance.json` for machine-readable metadata including:
- Source composition path and ID
- Production method ID and parameters
- Output file hashes and timestamps
- Processing chain documentation

---

## References

- **Method Documentation**: `/opt/data/projects/Research/CompositionMethods/methods_db.md` (SP-025 section)
- **Source Composition**: `/opt/data/projects/Styles/Balfolk/030-balfolk-grand-suite/`
- **IRCAM FOF Theory**: Rodet, X., & Depalle, P. (1992). "Formant Wave Function (FOF) — Riding the Old Wave to the New Wave."

---

**Production completed:** 2026-08-04  
**Total duration:** 73.72 seconds  
**Tracks rendered:** 4 (Violin, Piano, Acoustic Guitar, Woodblock)  
**Total notes synthesized:** 528
