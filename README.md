# Musicom

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-0.1.0-green.svg)](https://github.com/musicom/musicom)

**Musicom** is a Python-based music composition and analysis framework that combines music theory, algorithmic generation, and computational analysis. It leverages both `music21` and `musicpy` libraries to provide a comprehensive toolkit for creating, analyzing, and transforming musical compositions.

Algorithmic and structured music composition is treated as a series of transformations on organized data structures, allowing for systematic and generative approaches to creating music.

## Features

### 🎼 Core Music Theory
- **12-Tone Equal Temperament (12-TET)** system implementation
- **Chromatic pitches** management with helix representation
- **Diatonic patterns** including scales, modes, chords (triads, seventh chords, extended chords)
- **Music scales** with support for all 7 modes (Ionian, Dorian, Phrygian, Lydian, Mixolydian, Aeolian, Locrian)
- **Pitch sequences** serial transformations (Prime, Inversion, Retrograde, Retrograde-Inversion)

### 🎵 Musical Structures
- **MusicEvent**: Individual musical events with pitch, volume, start/end ticks
- **MusicUnit**: Core structure representing sequences of MusicEvents with numpy-based storage
- **MusicVoice**: Collections of musical units with instrument assignments
- **MusicSection**: Complete sections with multiple voices
- **MusicProject**: Full project management with multiple sections
- **UnitMatrix**: Matrix-based compositional framework for systematic musical development
- **MusicPitchClass** & **MusicPitch**: Pitch representation with direction and range
- **MusicPitchClassPattern**: Pattern-based pitch sequences with cardinality and mode

### 🎹 Harmony & Composition Rules
- **Scale7PitchDegree**: Scale degree definitions for 7-note scales
- **Scale7ChordDegree**: Chord degree definitions for diatonic harmony
- **PatternMovementRules**: Harmonic functions (Tonic, Dominant, Subdominant)
- **PatternMovement**: Pre-defined chord progression patterns
- **Counterpoint**: Two-voice counterpoint rules and constraints
- Support for both **major** and **minor mode** chord progressions

### 🥁 Rhythm
- **MusicTimeGrid**: Quantized time grid system with customizable timesteps
- **MusicRhythmPattern**: Rhythmic pattern definitions
- **Euclidean rhythm** generation
- **Hierarchical metrical structures** with beat depth analysis
- Support for various rhythmic patterns (Tresillo, Son Clave, etc.)

### 🎨 Matrix-Based Composition
- **UnitMatrix**: 2D compositional framework organizing musical material
- **Voice transformations**: Transpose, invert, retrograde, augment/diminish individual voices
- **Sectional development**: Repeat, vary, interpolate, and reorder temporal sections
- **Cell operations**: Transform individual musical units, cross-pollinate between voices
- **Matrix operations**: Transpose entire structures, diagonal reading, rotation, selective erasure
- Integration with **MusicUnit** for seamless musical content management

### 🤖 Algorithmic Generation
Multiple generator modules for creative composition:

- **PatternGenerator**: Generate pitch patterns based on scales and modes
- **MarkovChainGenerator**: Probabilistic sequence generation for chords and melodies
- **GeneticGenerator**: Evolutionary composition with fitness functions, crossover, and mutation
- **HarmonicsGenerator**: Overtone-based composition
- **StochasticGenerator**: Stochastic music creation with configurable parameters
- **RhythmGenerator**: Rhythmic pattern generation
- **ChordDegreeGenerator**: Chord progression generation based on scale degrees

### 🔄 Transformations
- **CanonTransformer**: Canon generation and voice imitation
- **PitchSequenceTransformer**: Serial transformations (invert, retrograde)
- **Matrix transpose**: Full matrix transposition operations
- **Pitch transformations**: Transposition, inversion, retrograde
- **Note splitting**: Neighbor tones, passing tones
- **Modulation** between scales

### 📊 Visualization
- **Helix**: 3D helix visualization of pitch space
- **Cycle**: Circular pitch class visualization
- Integration with matplotlib for custom plots

### 🔍 Analysis Tools
- **score_analyze**: Music21-based score analysis
- **piece_analyze**: MusicPy-based piece analysis
- **Key detection** and analysis
- **Chord identification** and classification
- **Roman numeral analysis** with key context
- **Metrical analysis** with beat depth

### 📁 File I/O & Conversion
- **MIDI file** import/export
- **MusicXML** support via Music21
- Bidirectional conversion between **Music21** and **MusicPy** structures
- Visual score rendering (notation display)
- **MIDI instrument** and **percussion** mappings

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Install from source

```bash
git clone https://github.com/musicom/musicom.git
cd musicom
pip install -e .
```

### Install with development dependencies

```bash
pip install -e ".[dev]"
```

### Install dependencies only

```bash
pip install music21 musicpy numpy scipy pandas matplotlib networkx
```

### Core Dependencies
| Package | Version | Description |
|---------|---------|-------------|
| `music21` | ≥9.9.1 | Music notation and analysis |
| `musicpy` | ≥7.11 | Computational music structures |
| `numpy` | ≥2.3.5 | Numerical computing |
| `scipy` | ≥1.10.0 | Scientific computing |
| `pandas` | ≥2.0.0 | Data manipulation |
| `matplotlib` | ≥3.7.0 | Visualization |
| `networkx` | ≥3.1 | Network/graph analysis |

## Project Structure

```
musicom/
├── analysis/              # Music analysis tools (Music21 & MusicPy)
│   ├── music21_analysis.py
│   └── musicpy_analysis.py
├── converters/            # Format converters
│   ├── midi_converter.py  # MIDI import/export
│   ├── music21_*.py       # Music21 conversions
│   ├── musicpy_converter.py
│   └── ...
├── generators/            # Algorithmic generators
│   ├── base.py           # Base generator class
│   ├── chain.py          # Markov chain generator
│   ├── chord_degrees.py  # Chord progression generator
│   ├── genetic.py        # Genetic algorithm generator
│   ├── harmonics.py      # Harmonic series generator
│   ├── pitchpattern.py   # Pattern generator
│   ├── rhythm.py         # Rhythm generator
│   └── stochastic.py     # Stochastic generator
├── rules/                 # Music theory rules
│   ├── counterpoint.py   # Counterpoint rules
│   ├── movement.py       # Scale degree movement
│   └── progression.py    # Chord progressions
├── structures/            # Core data structures
│   ├── base.py           # Base classes
│   ├── instrument.py     # MIDI instruments
│   ├── matrix.py         # UnitMatrix
│   ├── pitch.py          # Pitch classes
│   ├── pitchpattern.py   # Pitch patterns
│   ├── project.py        # MusicSection, MusicVoice, MusicProject
│   ├── time.py           # Time patterns
│   ├── timepattern.py    # Rhythm patterns
│   └── unit.py           # MusicEvent, MusicUnit
├── transformers/          # Musical transformations
│   ├── canon.py          # Canon transformer
│   ├── embellishment.py  # Embellishments
│   ├── matrix.py         # Matrix operations
│   ├── pitch.py          # Pitch transformations
│   └── pitchsequence.py  # Serial transformations
├── visualization/         # Visual representations
│   ├── cycle.py          # Pitch cycle visualization
│   └── helix.py          # Pitch helix visualization
├── utilities/             # Helper utilities
│   ├── config.py         # Configuration
│   ├── helpers.py        # Helper functions
│   └── music21_init.py   # Music21 initialization
├── examples/              # Example scripts
├── projects/              # Project notebooks
├── research/              # Research experiments
├── tests/                 # Unit tests
├── pyproject.toml        # Project configuration
├── requirements.txt      # Dependencies
└── README.md             # This file
```

## Quick Start

### Basic Usage

```python
from musicom import MusicUnit, MusicEvent, MusicVoice, MusicSection

# Create a simple melody as MusicEvents
events = [
    MusicEvent(pitch=60, volume=100, start_tick=0, end_tick=480),    # C4
    MusicEvent(pitch=62, volume=100, start_tick=480, end_tick=960),  # D4
    MusicEvent(pitch=64, volume=100, start_tick=960, end_tick=1440), # E4
    MusicEvent(pitch=65, volume=100, start_tick=1440, end_tick=1920),# F4
]

# Create a MusicUnit from events
melody = MusicUnit(events=events)

# Or create from pitches only
simple_melody = MusicUnit(pitches=[60, 62, 64, 65, 67])
```

### Using Generators

```python
from musicom.generators import PatternGenerator, MarkovChainGenerator

# Generate a pattern-based melody
pattern_gen = PatternGenerator()
pattern = pattern_gen.generate()

# Generate using Markov chains
markov_gen = MarkovChainGenerator()
sequence = markov_gen.generate()
```

### Matrix-Based Composition

```python
from musicom import UnitMatrix, MusicUnit

# Create a compositional matrix
matrix = UnitMatrix(voices=4, sections=8)

# Fill with musical units
for voice in range(4):
    for section in range(8):
        unit = MusicUnit(pitches=[60 + voice * 4, 62 + voice * 4])
        matrix.set_cell(voice, section, unit)

# Apply transformations
matrix.transpose_voice(0, 12)  # Transpose first voice up an octave
```

### Analysis

```python
from musicom.analysis import score_analyze, piece_analyze

# Analyze a Music21 score
result = score_analyze(score)

# Analyze a MusicPy piece
result = piece_analyze(piece)
```

## Key Concepts

### MusicEvent
A single musical event with:
- **pitch**: MIDI pitch number (0-127)
- **volume**: Velocity/dynamics (0-127)
- **start_tick**: Start time in ticks
- **end_tick**: End time in ticks

### MusicUnit
A sequence of MusicEvents stored efficiently using numpy structured arrays:
- Efficient memory layout for large compositions
- Supports slicing, iteration, and numpy operations
- Core building block for all compositional structures

### MusicVoice & MusicSection
Organizational structures:
- **MusicVoice**: A single instrumental line with assigned instrument
- **MusicSection**: Multiple voices playing together
- **MusicProject**: Complete composition with multiple sections

### UnitMatrix
A 2D compositional framework where:
- **Rows** represent independent voices or parts
- **Columns** represent temporal sections
- **Cells** contain `MusicUnit` objects

```
        Section 1   Section 2   Section 3   Section 4
Voice 1:   [A₁]       [A₂]        [A₃]        [A₁']
Voice 2:   [B₁]       [B₂]        [B₁]        [B₃]
Voice 3:   [C₁]       [C₁]        [C₂]        [C₂']
Voice 4:   [D₁]       [D₂]        [D₃]        [D₁]
```

### MusicPitchClassPattern
Pattern-based pitch organization with:
- **Cardinality**: Number of pitches in pattern
- **PatternType**: Type of pattern (scale, chord, etc.)
- **PatternRotation**: Mode of the pattern

## Examples

See the `examples/` directory for working examples:
- `3voices.py` - Three-voice composition
- `compose.py` - Basic composition workflow
- `cross_voice.py` - Cross-voice techniques
- `systematic.py` - Systematic composition
- `guide.ipynb` - Interactive tutorial

## Testing

Run the test suite:

```bash
pytest tests/
```

Run with coverage:

```bash
pytest tests/ --cov=musicom --cov-report=html
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

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [music21](https://web.mit.edu/music21/) - MIT's music analysis toolkit
- Built with [musicpy](https://github.com/Rainbow-Dreamer/musicpy) - Computational music composition library
- Inspired by classical music theory and algorithmic composition techniques
- Matrix-based composition inspired by serialism and systematic compositional techniques

---

**Note**: This is a research and educational project for exploring computational music composition and analysis. It's designed for composers, music theorists, and developers interested in algorithmic music generation.
