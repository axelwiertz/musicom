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
├── __init__.py              # Package initialization
├── config.py                # Configuration settings
├── constants.py             # Music constants (12-TET, MIDI mappings)
├── theory.py                # Music theory (scales, intervals, patterns)
├── structures.py            # Core data structures (Unit, Voice, Composition)
├── harmony.py               # Harmonic rules and progressions
├── rhythm.py                # Rhythm and meter structures
├── compose.py               # Composition examples and utilities
├── converters.py            # Format conversion utilities
├── analysis.py              # Analysis tools
├── transformation.py        # Musical transformations
├── network.py               # Interval networks and voice leading
├── soundwave.py             # Audio synthesis
├── generators/              # Algorithmic generators
│   ├── __init__.py
│   ├── chain.py            # Markov chain generator
│   ├── genetic.py          # Genetic algorithm
│   ├── harmonic.py         # Harmonic series generator
│   ├── random.py           # Random generation
│   ├── counterpoint.py     # Counterpoint generator
│   ├── scale_library.py    # Scale definitions
│   └── trainmodel.py       # ML training utilities
└── projects/                # Example projects
    ├── notebook.py
    └── project.ipynb
```

## Quick Start

### Creating a Simple Composition

```python
from constants import TwelveTET, MIDIinstrument
from structures import MusicComposition, MusicUnit, MusicVoice
from structures.theory import MusicScale, Diatonic, PitchRegister
from structures.rhythm import MusicTime
from converters import comp_to_visual

# Create a time signature (16 timesteps, 4/4 time, 120 BPM)
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
voice = MusicVoice('Piano Voice', [unit], MIDIinstrument.PIANO)

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

### Using Generators

```python
from generators.chain import MarkovChain
from rules.harmony import Scale7ChordHarmony

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
The fundamental building block representing a sequence of musical events with:
- **pitch_nodes**: MIDI pitch numbers
- **onset_intervals**: Time between note onsets
- **durations**: Note durations
- **velocities**: Note dynamics (0-127)

### MusicVoice
A collection of `MusicUnit` objects representing a single instrumental or vocal line with a specific MIDI instrument.

### MusicComposition
A complete piece containing multiple voices, a main scale, chord progression, and formal structure.

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

## Contributing

Contributions are welcome! Areas for enhancement:
- Additional generator algorithms
- More music theory rules
- Extended analysis capabilities
- Performance optimizations
- Documentation improvements

## License

[Specify your license here]

## Acknowledgments

- Built with [music21](https://web.mit.edu/music21/) - MIT's music analysis toolkit
- Built with [musicpy](https://github.com/Rainbow-Dreamer/musicpy) - Computational music composition library
- Inspired by classical music theory and algorithmic composition techniques

## Contact

[Your contact information]

---

**Note**: This is a research and educational project for exploring computational music composition and analysis. It's designed for composers, music theorists, and developers interested in algorithmic music generation.

