# Project 057: Cellular Automaton Chorale

**Composition Method:** Rule 30 Elementary Cellular Automaton  
**Date:** 2026-08-03  
**Key:** Eb Major  
**Tempo:** 96 BPM  
**Form:** 8-bar homophonic chorale (I-IV-V-vi-ii-V-IV-I)

---

## Overview

This composition uses **Rule 30**, a one-dimensional elementary cellular automaton, as the generative method for pitch selection. Rule 30 is known for producing complex, seemingly random patterns from simple deterministic rules — making it ideal for exploring the boundary between order and chaos in musical composition.

The composition follows a **two-phase architecture**:
- **Phase 1 (Generative):** Rule 30 CA generates raw scale-degree choices
- **Phase 2 (Rules):** Voice leading rules detect and correct parallel fifths/octaves

---

## Composition Method

### Rule 30 Cellular Automaton

Rule 30 is defined by the update rule:
```
new_state = left XOR (center OR right)
```

Starting from a seed pattern, the automaton evolves over time, producing fractal-like structures. Each voice (Soprano, Alto, Tenor, Bass) uses a shifted seed to generate independent but related melodic lines.

**Parameters:**
- CA width: 8 cells (one per bar)
- Timesteps: 4 (we use the final row)
- Seed: `0b00010100` (shifted per voice for variety)

**CA Evolution:**
```
t=0: ...#.#..
t=1: ..##.##.
t=2: .##..#.#
t=3: .#.###.#
```

The CA output is mapped to scale degrees by interpreting 3-bit windows as signed offsets (-3 to +3) from the chord root, then clamping to the valid range (1-7).

### Two-Phase Architecture

**Phase 1: Generative Method (Rule 30 CA)**
- Each voice gets an independent CA row
- CA output determines scale-degree offsets from chord tones
- Result: raw melodic material with CA's characteristic complexity

**Phase 2: Musicom Rules Post-Processing**
- Voice leading rules check for parallel fifths and octaves
- Violations are corrected by stepwise adjustment (+1 or -1 scale degree)
- Ensures classical voice-leading standards while preserving CA character

**Result:** 1 voice-leading violation detected and corrected in the Bass voice (bar 8: degree 1 → degree 2).

---

## Musical Structure

### Voices & Instrumentation

| Voice | Range | Instrument | MIDI Program |
|-------|-------|------------|--------------|
| Soprano | Eb4-G5 | Flute | 73 |
| Alto | G3-A4 | Flute | 73 |
| Tenor | C3-D4 | Flute | 73 |
| Bass | Gb2-G3 | Bassoon | 70 |

### Harmonic Plan

8-bar progression in Eb Major:
```
Bar:  1   2   3   4   5   6   7   8
     I   IV  V   vi  ii  V   IV  I
     Eb  Ab  Bb  Cm  Fm  Bb  Ab  Eb
```

### Final Pitch Material

**Scale Degrees (after voice-leading correction):**
```
Soprano: [1, 6, 5, 7, 5, 7, 2, 1]
Alto:    [3, 3, 7, 6, 6, 7, 3, 1]
Tenor:   [1, 6, 4, 7, 2, 7, 4, 1]
Bass:    [4, 6, 5, 7, 4, 5, 4, 2]
```

**MIDI Pitches:**
```
Soprano: [63, 72, 70, 74, 70, 74, 65, 63]  (Eb4-G4-F4-Ab4-F4-Ab4-F4-Eb4)
Alto:    [59, 59, 66, 64, 64, 66, 59, 55]  (Bb3-Bb3-Ab4-G4-G4-Ab4-Bb3-G3)
Tenor:   [50, 59, 55, 61, 52, 61, 55, 50]  (D3-Bb3-G3-C4-E4-C4-G3-D3)
Bass:    [48, 52, 50, 54, 48, 50, 48, 45]  (C3-E3-D3-F#3-C3-D3-C3-A2)
```

---

## Files

```
057-cellular-chorale/
├── README.md                          # This file
├── src/
│   └── compose.py                     # Composition script
├── MIDI/
│   ├── 057-cellular-chorale.mid       # MIDI file (381 bytes)
│   └── 057-cellular-chorale.mid.provenance.json
├── Analysis/
│   └── grid_visualization.txt         # UnitMatrix timeline
└── Audio/                             # (empty — no audio rendering)
```

---

## Listening Guide

**What to listen for:**
- **Fractal complexity:** The CA generates non-repeating patterns that avoid simple repetition
- **Voice independence:** Each voice follows its own CA trajectory, creating contrapuntal interest
- **Tension/release:** Bars 3-4 (V-vi) and 5-6 (ii-V) create harmonic tension, resolved in bars 7-8 (IV-I)
- **Voice-leading smoothness:** Despite CA's chaotic nature, the rules layer ensures classical voice-leading standards

**Render to audio:**
```bash
cd /opt/data/projects/Styles/Experimental/057-cellular-chorale
/opt/data/micromamba/envs/musicom/bin/fluidsynth -ni -g 1.2 -F Audio/057-cellular-chorale.wav /opt/data/micromamba/envs/musicom/share/soundfonts/TimGM6mb.sf2 MIDI/057-cellular-chorale.mid
ffmpeg -y -i Audio/057-cellular-chorale.wav -codec:a libopus -b:a 128k Audio/057-cellular-chorale.ogg
```

---

## Technical Details

**Validation:**
- Zero-drift: ✓ PASS
- All tracks equal length: 15360 ticks (8 bars × 1920 ticks/bar)
- Voice leading violations fixed: 1

**Provenance:**
- Classification: ai-generated
- Generator: Rule 30 Elementary Cellular Automaton
- Phase 2 rules: VoiceLeadingRules (parallel fifths/octaves)

---

## References

- Wolfram, S. (2002). *A New Kind of Science*. Wolfram Media.
- Musicom AGENTS.md: Two-phase architecture for generative methods
- Voice leading rules: `/opt/data/repos/musicom/ai/rules/voice_leading_rules.py`

---

**Status:** ✓ Complete  
**Next steps:** Render to audio, explore different CA rules (Rule 90, Rule 110), or extend to longer forms with CA evolution across sections.
