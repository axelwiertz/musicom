# Quick Reference Guide

## Installation

```bash
pip install -r requirements.txt
pip install -e .
```

## Basic Usage

### 1. Create a Note
```python
from musicom.structures import Note

note = Note(pitch=60, duration=1.0, velocity=80, start_time=0.0)
print(f"Pitch class: {note.pitch_class}")  # 0 (C)
print(f"Octave: {note.octave}")  # 4
```

### 2. Create a Chord
```python
from musicom.structures import Chord, MAJOR_TRIAD

# Method 1: From intervals
chord = Chord.from_intervals(60, MAJOR_TRIAD, duration=1.0)

# Method 2: From notes
notes = [Note(60, 1.0), Note(64, 1.0), Note(67, 1.0)]
chord = Chord(notes=notes, name="C Major")
```

### 3. Create a Scale
```python
from musicom.structures import Scale, MAJOR_SCALE

c_major = Scale(root=0, intervals=MAJOR_SCALE, name="C Major")
pitches = c_major.get_pitches(octave=4, num_octaves=1)
# [60, 62, 64, 65, 67, 69, 71] - C major scale
```

### 4. Generate a Melody
```python
from musicom.generators import MelodyGenerator

gen = MelodyGenerator(c_major, seed=42)

# Random melody
melody = gen.generate_random(length=8)

# Stepwise melody
melody = gen.generate_stepwise(length=16, start_pitch=60)

# Arpeggio
arpeggio = gen.generate_arpeggio([0, 4, 7], root_pitch=60, repetitions=2)
```

### 5. Generate Chord Progression
```python
from musicom.generators import ChordProgressionGenerator

gen = ChordProgressionGenerator(key_root=0, is_major=True)
chords = gen.generate_progression(num_chords=4)
```

### 6. Apply Transformations
```python
from musicom.transformers import (
    TranspositionTransformer,
    TimeTransformer,
    DynamicsTransformer
)

# Transpose
transposed = TranspositionTransformer.transpose_note(note, semitones=5)

# Time stretch
stretched = TimeTransformer.time_stretch(melody, factor=2.0)

# Add crescendo
with_crescendo = DynamicsTransformer.add_crescendo(melody, 40, 100)

# Quantize
quantized = TimeTransformer.quantize(melody, grid=0.25)
```

### 7. Pattern Transformations
```python
from musicom.transformers import PatternTransformer

# Reverse
reversed_melody = PatternTransformer.reverse(melody)

# Retrograde (reverse pitches, keep rhythm)
retrograde = PatternTransformer.retrograde(melody)

# Inversion
inverted = PatternTransformer.inversion(melody, axis=60)
```

### 8. Validate with Rules
```python
from musicom.rules import HarmonicRule, MelodicRule, ScaleRule

# Check chord quality
quality = HarmonicRule.identify_chord_quality(chord)

# Analyze melodic contour
contour = MelodicRule.analyze_contour(melody)

# Check if note is in scale
is_valid = ScaleRule.check_note_in_scale(note, c_major)
```

### 9. Save to MIDI
```python
from musicom.io import MIDIHandler
from musicom.structures import Sequence

# Create sequence
sequence = Sequence(events=melody, tempo=120.0, time_signature=(4, 4))

# Save
midi = MIDIHandler()
midi.save_midi(sequence, "output.mid")

# Load
loaded = midi.load_midi("input.mid")
```

### 10. Piano Roll Representation
```python
from musicom.io import PianoRollHandler

handler = PianoRollHandler()
multitrack = handler.sequence_to_pianoroll(sequence, resolution=24)

# Access piano roll matrix
piano_roll = multitrack.tracks[0].pianoroll
# Shape: (time_steps, 128)
```

## Predefined Constants

### Scales
- `MAJOR_SCALE` = [0, 2, 4, 5, 7, 9, 11]
- `MINOR_SCALE` = [0, 2, 3, 5, 7, 8, 10]
- `HARMONIC_MINOR` = [0, 2, 3, 5, 7, 8, 11]
- `MELODIC_MINOR` = [0, 2, 3, 5, 7, 9, 11]
- `PENTATONIC_MAJOR` = [0, 2, 4, 7, 9]
- `PENTATONIC_MINOR` = [0, 3, 5, 7, 10]
- `BLUES_SCALE` = [0, 3, 5, 6, 7, 10]
- `CHROMATIC_SCALE` = [0, 1, 2, ..., 11]

### Chords
- `MAJOR_TRIAD` = [0, 4, 7]
- `MINOR_TRIAD` = [0, 3, 7]
- `DIMINISHED_TRIAD` = [0, 3, 6]
- `AUGMENTED_TRIAD` = [0, 4, 8]
- `MAJOR_SEVENTH` = [0, 4, 7, 11]
- `MINOR_SEVENTH` = [0, 3, 7, 10]
- `DOMINANT_SEVENTH` = [0, 4, 7, 10]
- `DIMINISHED_SEVENTH` = [0, 3, 6, 9]

## Pitch System (12TET)

### Pitch Classes
- C = 0, C# = 1, D = 2, D# = 3
- E = 4, F = 5, F# = 6, G = 7
- G# = 8, A = 9, A# = 10, B = 11

### MIDI Pitch Numbers
- Middle C (C4) = 60
- A440 (A4) = 69
- Range: 0-127

### Octave Calculation
```python
pitch_class = pitch % 12
octave = (pitch // 12) - 1
```

## Common Workflows

### Complete Composition
```python
# 1. Setup
c_major = Scale(root=0, intervals=MAJOR_SCALE)
melody_gen = MelodyGenerator(c_major, seed=42)
chord_gen = ChordProgressionGenerator(key_root=0, is_major=True)

# 2. Generate
melody = melody_gen.generate_stepwise(16)
chords = chord_gen.generate_progression(4)

# 3. Transform
melody = TimeTransformer.quantize(melody, grid=0.25)
melody = DynamicsTransformer.add_crescendo(melody, 50, 90)

# 4. Validate
contour = MelodicRule.analyze_contour(melody)
print(f"Contour: {contour}")

# 5. Export
sequence = Sequence(events=melody, tempo=120.0)
MIDIHandler().save_midi(sequence, "composition.mid")
```

## Module Structure

```
musicom/
├── structures/     # Note, Chord, Scale, Sequence
├── generators/     # MelodyGenerator, ChordProgressionGenerator, etc.
├── transformers/   # Transposition, Time, Dynamics, etc.
├── io/            # MIDIHandler, MusicXMLHandler, PianoRollHandler
└── rules/         # HarmonicRule, MelodicRule, etc.
```

## Running Examples

```bash
# Basic examples
python examples.py

# Advanced composition
python advanced_example.py

# Run tests
python tests/test_musicom.py
```

## Tips

1. **Use seeds** for reproducible random generation
2. **Quantize** for precise timing on grid
3. **Validate** with rules before export
4. **Humanize** for natural feel
5. **Check** notes are in scale with `ScaleRule`

## Common Patterns

### Creating Harmony
```python
# Harmonize at thirds and fifths
harmonized = HarmonicTransformer.harmonize(melody, intervals=[4, 7])
```

### Creating Bass Line
```python
for chord in chords:
    root = chord.root.pitch - 12  # Octave below
    bass = gen.generate_arpeggio([0, 7], root, repetitions=2)
```

### Applying Swing
```python
from musicom.transformers import RhythmicTransformer
swung = RhythmicTransformer.swing(melody, swing_ratio=0.67)
```

### Voice Leading
```python
from musicom.rules import VoiceLeadingRule
smoothness = VoiceLeadingRule.smooth_voice_leading(chord1, chord2)
```

## Troubleshooting

### Import Error
```bash
pip install -r requirements.txt
```

### Module Not Found
```bash
pip install -e .
```

### Music21 Setup
```python
import music21
music21.configure.run()
```

## Next Steps

- Check `INTEGRATION.md` for library integration details
- See `examples.py` for basic usage
- See `advanced_example.py` for complete workflow
- Read `README.md` for full documentation
