# Musicom

**Musicom** is a Python-based music composition and analysis framework that combines music theory, algorithmic generation, and computational analysis. It leverages both `music21` and `musicpy` libraries to provide a comprehensive toolkit for creating, analyzing, and transforming musical compositions.

## Features

### 🎼 Core Music Theory
- **12-Tone Equal Temperament (12-TET)** system implementation
- **Pitch Register** management with chromatic helix representation
- **Diatonic patterns** including scales, modes, chords (triads, seventh chords, extended chords)
- **Music scales** with support for all 7 modes (Ionian, Dorian, Phrygian, Lydian, Mixolydian, Aeolian, Locrian)
- **Pitch class sets** and serial transformations (Prime, Inversion, Retrograde, Retrograde-Inversion)

### 🎵 Musical Structures
- **MusicUnit**: Core structure representing sequences of pitches with timing and dynamics
- **MusicVoice**: Collections of musical units with instrument assignments
- **MusicComposition**: Complete compositions with multiple voices, scales, and progressions
- **MusicMatrix**: Matrix-based compositional framework for systematic musical development
- Support for both **Music21** and **MusicPy** data structures

### 🎹 Harmony & Composition Rules
- **Harmonic progressions** with chord degree functions (Tonic, Dominant, Subdominant)
- **Voice leading rules** for classical harmony
- **Scale degree movement rules** for pitch progression
- Support for both **major** and **minor mode** chord progressions
- **Chord function analysis** with Roman numeral notation

### 🥁 Rhythm
- **Quantized time grid** system with customizable timesteps
- **Meter and tempo** management
- **Euclidean rhythm** generation
- **Hierarchical metrical structures** with beat depth analysis
- Support for various rhythmic patterns (Tresillo, Son Clave, etc.)

### 🎨 Matrix-Based Composition
- **MusicMatrix**: 2D compositional framework organizing musical material
- **Voice transformations**: Transpose, invert, retrograde, augment/diminish individual voices
- **Sectional development**: Repeat, vary, interpolate, and reorder temporal sections
- **Cell operations**: Transform individual musical units, cross-pollinate between voices
- **Matrix operations**: Transpose entire structures, diagonal reading, rotation, selective erasure
- Integration with **MusicUnit** for seamless musical content management

### 🤖 Algorithmic Generation
Multiple generator modules for creative composition:

- **Markov Chain Generator**: Probabilistic sequence generation for chords and melodies
- **Genetic Algorithm**: Evolutionary composition with fitness functions, crossover, and mutation
- **Harmonic Series Generator**: Overtone-based composition
- **Random Generator**: Stochastic music creation with configurable parameters
- **Counterpoint Generator**: Two-voice counterpoint following classical rules
- **Scale Library**: Extensive collection of musical scales

### 🔊 Sound Synthesis
- **SoundWave class** for audio synthesis
- **Sine wave generation** with overtones
- **ADSR envelope** support (Attack, Decay, Sustain, Release)
- WAV file I/O and visualization
- Frequency spectrum analysis

### 🔍 Analysis Tools
- **Key detection** and analysis
- **Chord identification** and classification
- **Roman numeral analysis** with key context
- **Metrical analysis** with beat depth
- Integration with **Music21** and **MusicPy** analysis algorithms

### 🔄 Transformations
- **Pitch transformations**: transposition, inversion, retrograde
- **Note splitting**: neighbor tones, passing tones
- **Modulation** between scales
- **Interval network** analysis with chord progressions and voice leading

### 📁 File I/O & Conversion
- **MIDI file** import/export
- **MusicXML** support via Music21
- Bidirectional conversion between **Music21** and **MusicPy** structures
- Visual score rendering (notation display)
- Audio playback support

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Dependencies

```bash
pip install music21 musicpy numpy scipy pandas matplotlib networkx
```

**Core dependencies:**
- `music21` - Music notation and analysis
- `musicpy` - Computational music structures
- `numpy` - Numerical computing
- `scipy` - Scientific computing (for audio processing)
- `pandas` - Data manipulation
- `matplotlib` - Visualization
- `networkx` - Network/graph analysis

## Project Structure

```
musicom/
├── analysis/              # Scripts for analyzing musical structures
├── constants/             # Basic constants for music theory (e.g., MIDI numbers)
├── converters/            # Converters between different music representations
├── generators/            # Algorithmic music generators
├── projects/              # Jupyter notebooks for experiments and projects
├── rules/                 # Rules for harmony and composition
├── structures/            # Core data structures for music representation
│   ├── matrix.py         # Matrix-based compositional framework
│   └── ...
├── testers/               # Tests for the different modules
├── utilities/             # Helper functions and configuration
├── README.md              # Project documentation
├── requirements.txt       # Project dependencies
└── __init__.py            # Package initialization
```

## Quick Start

### Creating a Simple Composition

This example uses the lower-level `MusicUnit` to construct a voice from precise note data.

```python
from constants import TwelveTET, MidiInstrument
from structures.composition import MusicComposition, MusicUnit, MusicVoice
from structures.pattern import MusicPattern
from structures.regularity import Diatonic, PitchRegister
from structures.rhythm import MusicTime
from converters import comp_to_visual

# Create a time grid (16 timesteps, 4/4 time, 120 BPM)
time = MusicTime(16, 4, 4, 120)

# Create a pitch register
reg = PitchRegister()

# Create a musical unit with pitches, durations, and velocities
unit = MusicUnit(
    time, reg,
    pitch_nodes=[reg.index_of(TwelveTET.C, 4), reg.index_of(TwelveTET.E, 4)],
    onset_intervals=[4],
    durations=[3, 5],
    velocities=[100, 100]
)

# Create a voice
voice = MusicVoice('Piano Voice', [unit], MidiInstrument.PIANO)

# Create a composition
comp = MusicComposition(
    'My Composition',
    MusicScale(Diatonic.HEPTA, Diatonic.SCALE, TwelveTET.C, Diatonic.major_mode),
    [voice],
    [1, 4, 5, 1],  # Chord progression
    [0]
)

# Display the composition
comp_to_visual(comp)
```

### Matrix-Based Composition

```python
from structures import MusicMatrix, MusicalUnit
from structures.rhythm import MusicTime
from structures.composition import PitchRegister
from constants import TwelveTET

# Create a 4x4 musical matrix (4 voices, 4 sections)
matrix = MusicMatrix(rows=4, cols=4)

# Create musical units
time = MusicTime(16, 4, 4, 120)
reg = PitchRegister()

motif_a = MusicalUnit(
    unit_type="motif",
    content=[reg.index_of(TwelveTET.C, 4), reg.index_of(TwelveTET.E, 4)],
    metadata={"pitch": 60, "dynamics": "mf"}
)

motif_b = MusicalUnit(
    unit_type="phrase",
    content=[reg.index_of(TwelveTET.G, 4), reg.index_of(TwelveTET.B, 4)],
    metadata={"pitch": 67, "dynamics": "f"}
)

# Populate the matrix
matrix.set_cell(0, 0, motif_a)
matrix.set_cell(1, 0, motif_b)

# Apply compositional transformations

# Row operations (voice transformations)
matrix.transpose_row(0, 2)           # Transpose voice 1 up by 2 semitones
matrix.retrograde_row(1)             # Play voice 2 backward
matrix.invert_row(2, pivot=60)       # Mirror melodic contours around middle C
matrix.augment_row(3, factor=2.0)    # Double note durations in voice 4

# Column operations (sectional development)
matrix.repeat_column(0, 3)           # Repeat section 1 at position 3
transition = MusicalUnit(unit_type="transition", content=[])
matrix.insert_column(2, transition)  # Insert transitional material
matrix.reorder_columns([0, 2, 1, 3]) # Non-linear narrative structure

# Cell operations (unit manipulation)
matrix.swap_cells((0, 0), (1, 1))    # Exchange material between voices
matrix.mutate_cell(0, 0, lambda cell: cell.transpose(5) if cell else None)

# Matrix operations
diagonal = matrix.diagonal_read()     # Extract diagonal pattern
transposed = matrix.transpose()       # Swap rows and columns (voices ↔ sections)
matrix.selective_erase(
    condition=lambda cell: cell is None or cell.metadata.get("density", 0) < 0.5
)

# Display the matrix
print(matrix)
```

### Using Generators

```python
from generators.chain import MarkovChain
from regularity.progression import Scale7ChordHarmony

# Create a Markov chain for chord progressions
chord_chain = MarkovChain(Scale7ChordHarmony.movement_rules)
progression = chord_chain.sample('1', length=16)
print(f"Generated progression: {progression}")
```

### Genetic Algorithm Composition

```python
from generators.genetic import generate_population, single_point_crossover, mutation

# Define a fitness function
def fitness_func(genome):
    return sum(genome)  # Simple example

# Generate initial population
population = generate_population(size=10, genome_length=16)

# Evolve the population
# (See genetic.py for complete evolution loop)
```

## Key Concepts

### MusicUnit
The fundamental building block representing a sequence of musical events with precise timing and pitch information. It contains:
- **pitch_nodes**: MIDI pitch numbers
- **onset_intervals**: Time between note onsets
- **durations**: Note durations
- **velocities**: Note dynamics (0-127)

### MusicalUnit
A flexible container for musical content used in matrix-based composition:
- **unit_type**: Classification (motif, phrase, chord, rhythm, etc.)
- **content**: Musical data (can be pitches, durations, or any musical information)
- **metadata**: Additional attributes (dynamics, articulation, pitch center, etc.)
- **Methods**: transpose(), invert(), retrograde(), augment()

### MusicVoice
A collection of `MusicUnit` objects representing a single instrumental or vocal line, assigned to a specific MIDI instrument.

### MusicComposition
A complete piece containing multiple voices, a main scale, chord progression, and formal structure.

### MusicMatrix
A 2D compositional framework where:
- **Rows** represent independent voices or parts (melody, harmony, bass, percussion, etc.)
- **Columns** represent temporal sections or measures
- **Cells** contain `MusicalUnit` objects (motifs, phrases, chords, rhythmic patterns)

**Matrix Structure Example:**
```
        Section 1   Section 2   Section 3   Section 4
Voice 1:   [A₁]       [A₂]        [A₃]        [A₁']
Voice 2:   [B₁]       [B₂]        [B₁]        [B₃]
Voice 3:   [C₁]       [C₁]        [C₂]        [C₂']
Voice 4:   [D₁]       [D₂]        [D₃]        [D₁]
```

**Compositional Operations:**
- **Row Operations**: Transform entire voices (transpose, invert, retrograde, augment/diminish)
- **Column Operations**: Develop sections (repeat, insert, reorder)
- **Cell Operations**: Modify individual units (mutate, swap)
- **Matrix Operations**: Global transformations (transpose matrix, diagonal reading, rotation, selective erasure)

### Diatonic Theory
Comprehensive support for diatonic harmony including:
- 7 scale modes
- Triad qualities (Major, Minor, Diminished, Augmented, Sus2, Sus4)
- Seventh chords (Major7, Minor7, Dominant7, etc.)
- Harmonic functions and voice leading rules

## Analysis Examples

```python
from analysis import analyze
from converters import file_to_comp

# Load a MIDI file
comp = MusicComposition('Analysis Example')
file_to_comp(comp, 'path/to/file.mid')

# Analyze the composition
analyze(comp)
# Outputs: key, chord progressions, Roman numerals, metrical structure
```

## Advanced Matrix Techniques

### Systematic Development
```python
# Create a theme and develop it systematically
theme = MusicalUnit(unit_type="theme", content=[60, 64, 67])
matrix = MusicMatrix(rows=4, cols=8)

# Voice 1: Original theme
matrix.set_cell(0, 0, theme)

# Voice 2: Inverted theme
matrix.set_cell(1, 0, theme)
matrix.invert_row(1, pivot=64)

# Voice 3: Retrograde theme
matrix.set_cell(2, 0, theme)
matrix.retrograde_row(2)

# Voice 4: Augmented theme
matrix.set_cell(3, 0, theme)
matrix.augment_row(3, factor=2.0)

# Develop across sections
for col in range(1, 8):
    matrix.repeat_column(0, col)
    # Apply variations to each section
    matrix.transpose_row(0, offset=col % 12, start_col=col, end_col=col)
```

### Cross-Voice Material Exchange
```python
# Create contrasting materials
material_a = MusicalUnit(unit_type="motif", content=[60, 62, 64])
material_b = MusicalUnit(unit_type="motif", content=[67, 65, 64])

matrix = MusicMatrix(rows=2, cols=4)
matrix.set_cell(0, 0, material_a)
matrix.set_cell(1, 0, material_b)

# Cross-pollinate materials
matrix.swap_cells((0, 1), (1, 1))  # Exchange at section 2
matrix.repeat_column(1, 2)          # Stabilize the exchange
matrix.repeat_column(0, 3)          # Return to original
```

## Contributing

Contributions are welcome! Areas for enhancement:
- Additional generator algorithms
- More music theory rules
- Extended analysis capabilities
- Performance optimizations
- Documentation improvements
- Advanced matrix operations and transformations

## License

[Specify your license here]

## Acknowledgments

- Built with [music21](https://web.mit.edu/music21/) - MIT's music analysis toolkit
- Built with [musicpy](https://github.com/Rainbow-Dreamer/musicpy) - Computational music composition library
- Inspired by classical music theory and algorithmic composition techniques
- Matrix-based composition inspired by serialism and systematic compositional techniques

## Contact

[Your contact information]

---

**Note**: This is a research and educational project for exploring computational music composition and analysis. It's designed for composers, music theorists, and developers interested in algorithmic music generation.
