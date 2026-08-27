# Project 036 — Kate Bush Harmonic & Structural Analysis
**Source**: The Man with the Child in His Eyes (.mid)

## 🧬 Harmonic DNA
Analysis of pitch sets across the piece reveals a characteristic "Dark Pop" modal interchange:

| Pitch Set | Note Names (Relative) | Character | Occurrences |
|---|---|---|---|
| `[7, 11, 2]` | G, B, D | **G Major** (Anchor) | 20 |
| `[2, 5, 10]` | D, F, Bb | **Bb Major** (Modal Interchange) | 19 |
| `[0, 4, 7]` | C, E, G | **C Major** (Subdominant) | 17 |
| `[2, 5, 7]` | D, F, G | **G7sus / Open tension** | 21 |

### Harmonic Observation
The movement between **G Major** and **Bb Major** creates a chromatic mediant-like tension characteristic of Kate Bush’s piano-driven compositions.

## 🔲 Reconstructed UnitMatrix
Vertical density analysis (notes per bar) mapped to Musicom structures:

```text
SECTION      | BARS    | RHYTHMIC DENSITY (1-16) | DYNAMICS
-------------|---------|-------------------------|----------
Intro/Verse  | 01 - 26 | [██░░░░░░░░░░░░░░] (2-8) | Piano/Delicate
Bridge       | 56 -104 | [░░░░░░░░░░░░░░░░] (0-2) | Sustained/Sparse
Chorus       | 105-162 | [████████████████] (12-16)| Forte/Agitated
Outro        | 163-216 | [██████░░░░░░░░░░] (6-9)  | Mezzo/Fading
```

## 📈 Melodic Contour (Pitch Patterns)
Sample Interval Vector: `[7, -4, 2, 0, -2, 0, -3, 0, -9, 7]`
- **Stagnation**: Frequent `0` intervals indicate repeated tone phrasing (pedal points in the melody).
- **Leaps**: Large intervals (`7`, `-9`) represent the emotive emotional shifts in vocal delivery.

## 🛠️ Variation Strategy
The variation script (`generate_kate_bush_variation.py`) uses the following rules:
1. **Structural Logic**: Follows the 8-bar sparse/4-bar dense transition found in the source.
2. **Harmonic Constraint**: Cycles through the identified DNA chords (G, D, Bb, F).
3. **Density Modulation**: Uses the `slot_ticks` method to scale from density 4 (verse) to 14 (chorus).
