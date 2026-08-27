# Minimalism Style Patterns

## Rhythm DNA

### Phase Pattern (Reich-style)
```
Voice 1: █░░█░░█░░█░░ (E(4,12) at 120 BPM)
Voice 2: █░░█░░█░░█░░ (E(4,12) at 121 BPM)
Result:  Phasing over ~60 seconds
```

### Additive Pattern
```
Bar 1: █░░░░░░░ (1 onset)
Bar 2: █░░░█░░░ (2 onsets)
Bar 3: █░░█░░█░ (3 onsets)
Bar 4: █░█░█░█░ (4 onsets)
```

### Polyrhythm (3:2)
```
Voice 1: █░░█░░█░░ (triplet 8ths, 3 per beat)
Voice 2: █░░░█░░░ (straight 8ths, 2 per beat)
Alignment: Every 3 beats
```

### Ostinato Cell
```
Pattern: █░░█░░█░ (E(3,8))
Duration: 16 bars verbatim
Variation: Add 1 note at bar 17
```

## Pitch Patterns

### Diatonic Ostinato (C Major)
```
MIDI: [60, 62, 64, 65, 67, 69, 71, 72]
Cell: C-D-E-F-G-A-B-C (ascending stepwise)
Duration: Quarter notes, 8 bars
```

### Pentatonic Cell (C Major Pentatonic)
```
MIDI: [60, 62, 64, 67, 69]
Pattern: C-D-E-G-A (repeated with rhythmic variation)
Range: Octave (60-72)
```

### Modal Pedal (D Dorian)
```
Root: D (MIDI 62)
Scale: D-E-F-G-A-B-C (Dorian)
Harmony: Dm chord for 16 bars, then G for 8 bars
```

## Texture Patterns

### Layered Ostinati (4 voices)
```
Voice 1 (Bass):   Root pedal, whole notes (100% density)
Voice 2 (Pad):    Triad, sustained (100% density)
Voice 3 (Lead):   Ostinato cell, quarter notes (75% density)
Voice 4 (Perc):   Euclidean E(5,16), continuous (31% density)
```

### Phase Shift Implementation
```python
# Two identical patterns, different tempos
voice1_tempo = 120
voice2_tempo = 121
pattern = E(4, 12)  # 4 onsets in 12 steps
# After 60 seconds, voices are ~1 beat out of phase
```

## Harmony Patterns

### Static Modal
```
Key: C Major
Chord: C (C-E-G) for 32 bars
Bass: C pedal (whole notes)
Lead: Stepwise motion within C Major scale
```

### Slow Change
```
Bars 1-8:   C Major
Bars 9-16:  F Major
Bars 17-24: G Major
Bars 25-32: C Major
```

### Pedal Point
```
Bass: C (sustained or repeated)
Harmony: Changes above pedal (C → F → G → C)
Result: Tension from non-chord bass notes
```

## Form Patterns

### Additive Form
```
Section A (8 bars):  1 layer
Section B (8 bars):  2 layers
Section C (8 bars):  3 layers
Section D (8 bars):  4 layers (full texture)
```

### Subtractive Form
```
Section A (8 bars):  4 layers (full texture)
Section B (8 bars):  3 layers
Section C (8 bars):  2 layers
Section D (8 bars):  1 layer (exposed core)
```

### Process Form
```
Bars 1-16:   Pattern X (verbatim)
Bars 17-32:  Pattern X + 1 note added
Bars 33-48:  Pattern X + 2 notes added
Bars 49-64:  Pattern X + 3 notes added
```

## Density Targets

| Voice Type | Min Density | Continuous Layer |
|------------|-------------|------------------|
| Bass/Pad   | 100%        | Yes (sustained)  |
| Lead       | 75%         | Optional         |
| Percussion | 30-50%      | No (Euclidean)   |

## Tempo
- **Range**: 60-140 BPM
- **Stability**: Metronomic (no rubato)
- **Phase**: Slight tempo offset (±1 BPM) for phasing

## Key Signatures
- C Major, G Major, D Major (bright, consonant)
- A Minor, D Dorian, E Phrygian (modal color)
- Avoid: Chromatic keys, atonal
