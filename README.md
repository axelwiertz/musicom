# Musicom

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-0.1.0-green.svg)](https://github.com/musicom/musicom)

**Musicom** is a Python-based music composition and analysis framework that combines music theory, algorithmic generation, and computational analysis. It leverages both `music21` and `musicpy` libraries to provide a comprehensive toolkit for creating, analyzing, and transforming musical compositions.

Algorithmic and structured music composition is treated as a series of transformations on organized data structures, allowing for systematic and generative approaches to creating music.

## Features

| 🎼 Core Music Theory
- **12-Tone Equal Temperament (12-TET)** system implementation (in `structures.pitchclass`)
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
- **MusicPitchClassSet**: Pattern-based pitch sequences with cardinality and mode

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

### 🔊 Sound Synthesis & Processing
- **Modal synthesis** — ResonatorBank for physical modeling (marimba, bell, drum, string, etc.)
- **Granular synthesis** — AperiodicGranulator for stochastic grain clouds
- **Phase modulation** — PhaseModSynth and FDSSynth for wavetable-based FM
- **Formant synthesis** — FormantVocalGuide for vowel synthesis
- **Additive synthesis** — SoundWave with harmonic overtone control
- **Audio effects** — AlgorithmicReverb (Schroeder), StateVariableFilter, BiquadFilter
- **Mastering tools** — LUFSMeter (ITU-R BS.1770-4), DynamicEQ, StereoImager, Limiter, MasteringChain
- **Audio analysis** — PitchDetector, BeatTracker, OnsetDetector, ChromaExtractor
- **Generative patterns** — MarkovCore, StochasticCore, EuclideanCore, LSystemCore
- **Rendering pipeline** — FluidSynth integration with stem rendering (per-track WAV export)
- **DAW synchronization** — DAWClockBridge for MIDI clock sync

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Install from source

Musicom uses a **flat package layout** — the top-level directories
(`structures/`, `workflows/`, `generators/`, ...) *are* the importable packages.

```bash
git clone https://github.com/axelwiertz/musicom.git
cd musicom
pip install -e ".[dev]"     # editable install + pytest/pytest-cov
```

After install, imports work from any working directory:

```python
from structures import MusicUnit, MusicEvent, UnitMatrix
from workflows.unitmatrix_composer import UnitMatrixComposer
```

> working by a compatibility alias, so both import styles resolve.

### Install dependencies only

```bash
pip install numpy mido scipy music21 networkx pandas matplotlib
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
├── converters/            # Format converters
├── generators/            # Algorithmic generators
├── rules/                 # Music theory rules
├── sound/                 # Sound synthesis, effects, and analysis
│   │   ├── modal.py      # ResonatorBank, ModalSynth
│   │   ├── granular.py   # AperiodicGranulator
│   │   ├── phase_mod.py  # PhaseModSynth, FDSSynth
│   │   ├── vocal.py      # FormantVocalGuide
│   │   └── additive.py   # SoundWave
│   │   ├── reverb.py     # AlgorithmicReverb, Freeverb
│   │   └── filter.py     # StateVariableFilter, BiquadFilter
│   │   ├── pitch.py      # PitchDetector
│   │   ├── rhythm.py     # BeatTracker, OnsetDetector
│   │   └── chroma.py     # ChromaExtractor
│   │   ├── fluidsynth.py # FluidSynthRenderer
│   │   └── pipeline.py   # RenderPipeline (with stem rendering)
│   │   └── event_core.py # MarkovCore, StochasticCore, EuclideanCore, LSystemCore
│   │   └── clock.py      # DAWClockBridge
│       ├── pitch.py      # Pitch conversion utilities
│       ├── io.py         # Audio I/O (WAV read/write)
│       └── envelope.py   # ADSR envelope generator
├── structures/            # Core data structures
├── transformers/          # Musical transformations
├── visualization/         # Visual representations
├── utilities/             # Helper utilities
├── examples/              # Example scripts
├── projects/              # Project notebooks
├── research/              # Research experiments
├── tests/                 # Unit tests
├── pyproject.toml        # Project configuration
├── requirements.txt      # Dependencies
└── README.md             # This file
```

## Quick Start

All snippets below are executed verbatim by the doc-verification script and pass.

### 1. MusicEvent & MusicUnit

```python
from structures import MusicUnit, MusicEvent

# MusicEvent uses ABSOLUTE ticks: (pitch, volume, start_tick, end_tick)
events = [
    MusicEvent(pitch=60, volume=100, start_tick=0,   end_tick=480),   # C4
    MusicEvent(pitch=62, volume=100, start_tick=480, end_tick=960),   # D4
    MusicEvent(pitch=64, volume=100, start_tick=960, end_tick=1440),  # E4
]
melody = MusicUnit(events=events)

melody.pitches        # [60, 62, 64]
melody.volumes        # [100, 100, 100]
melody.len_ticks()    # 1440

# In-place unit operations
melody.transpose(12)  # up an octave  -> pitches become [72, 74, 76]
melody.retrograde()   # reverse event order
melody.invert(60)     # mirror pitches around a pivot
```

### 2. UnitMatrix (voices × sections)

```python
from structures import UnitMatrix

matrix = UnitMatrix(shape=(2, 2))   # 2 voices (rows) x 2 sections (cols)
matrix.set_unit((0, 0), melody)     # place a MusicUnit in a cell
matrix.get_unit((0, 0))             # retrieve it
matrix.validate_timing()            # True when all rows share equal length
```

### 3. UnitMatrixComposer — recommended workflow

The composer guarantees **zero-drift**: every track is padded to identical
absolute length before MIDI export.

```python
from workflows.unitmatrix_composer import (
    UnitMatrixComposer, create_note_unit, create_chord_unit, create_empty_unit,
)
from structures import MidiInstrument

composer = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
composer.create_matrix(num_voices=2, num_sections=1)
composer.add_voice("Lead", program=MidiInstrument.FLUTE, channel=0)
composer.add_voice("Bass", program=MidiInstrument.BASS,  channel=1)
composer.add_section("A", bars=1)

BAR = 480 * 4  # ticks per bar
composer.fill_voice_section("Lead", "A", create_note_unit(pitch=72, duration_ticks=BAR))
composer.fill_voice_section("Bass", "A", create_note_unit(pitch=36, duration_ticks=BAR))

ok, msg = composer.validate()       # (True, "OK") — zero-drift gate
composer.to_midi("composition.mid") # export equal-length tracks
```

**Canonical order:** `create_matrix()` → `add_voice()` → `add_section()` →
`set_unit()` / `fill_voice_section()` → `validate()` → `to_midi()`.
Tempo meta goes in track 0. `MidiPercussion` lives on channel 9.

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

### MusicPitchClassSet
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
- `research_advanced.py` - Advanced composition workflow (merged from musicom_research)
- `research_examples.py` - Multi-library usage examples
- `research_verify.py` - Installation verification script

## Testing

Run the test suite (from the repo root):

```bash
pytest tests/
```

Run with coverage over the flat packages:

```bash
pytest tests/ --cov=structures --cov=workflows --cov=generators --cov-report=html
```

> **Suite status:** green — 25 passed, 1 documented skip. Includes a
> golden-file MIDI regression harness (`tests/test_harness_golden.py`) that
> locks in zero-drift, deterministic, non-empty exports.

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
