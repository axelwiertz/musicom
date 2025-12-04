# Musicom

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
- **MusicUnit**: Core structure representing sequences of pitches with timing and dynamics
- **MusicSection**: Complete compositions with multiple voices, scales, and progressions
- **MusicMatrix**: Matrix-based compositional framework for systematic musical development
- **MusicVoice**: Collections of musical units with instrument assignments
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

### Regulation & Constraints
- **Harmonic constraints**: Enforce chord progression rules
- **Voice leading constraints**: Limit pitch leaps and ensure smooth transitions
- **Rhythmic constraints**: Maintain metrical consistency and avoid syncopation issues
- **Fitness evaluation** for generated compositions based on musicality criteria

### 🎶 Melody & Motif Development
- **Motif extraction** from existing compositions
- **Melodic variation** techniques: augmentation, diminution, inversion, retrograde
- **Thematic development** across sections and voices

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

See projects/examples for a guide.

### Matrix-Based Composition


### Using Generators


## Key Concepts

### MusicPattern


### MusicUnit
The fundamental building block representing a sequence of musical events with precise timing and pitch information. It contains:
- **pitch_nodes**: MIDI pitch numbers
- **onset_intervals**: Time between note onsets
- **durations**: Note durations
- **velocities**: Note dynamics (0-127)

### MusicVoice
A single instrumental or vocal line, assigned to a specific instrument or voice.

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

## Advanced Matrix Techniques

### Systematic Development

See projects/examples/systematic.ipynb


### Cross-Voice Material Exchange

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
