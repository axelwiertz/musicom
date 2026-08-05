# Composition Workflow Knowledge Base

Operational guide for Hermes agent composition tasks on the musicom engine.

## Core Model

- **Time is ABSOLUTE ticks.** `MusicEvent(pitch, volume, start_tick, end_tick)`
- `UnitMatrix`: rows = voices, cols = sections, cells = `MusicUnit`
- **Zero-drift invariant**: all rows MUST be equal length
- Standard resolution: `ticks_per_beat=480`, `beats_per_bar=4` → `BAR = 1920` ticks

## The One True Workflow

```python
from workflows.unitmatrix_composer import UnitMatrixComposer, create_note_unit
from structures import MidiInstrument

composer = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
composer.create_matrix(num_voices=N, num_sections=M)   # 1. shape
composer.add_voice("Lead", program=MidiInstrument.FLUTE, channel=0)  # 2. voices
composer.add_section("A", bars=1)                      # 3. sections
composer.fill_voice_section("Lead", "A", create_note_unit(72, 1920))  # 4. fill cells
ok, msg = composer.validate()                          # 5. zero-drift gate
composer.to_midi("out.mid")                            # 6. export
```

Order is mandatory: `create_matrix → add_voice → add_section → fill → validate → to_midi`.
Tempo meta lives in track 0. Percussion on channel 9.

## Two-Phase Architecture (mandatory for generative methods)

**Phase 1: Generative draft** — algorithm produces raw material:
- Rhythm: event timings from the generative process
- Pitch indices: raw floats [0,1], NOT quantized to scale/chord
- Velocity: from generative dynamics

**Phase 2: Musicom rules post-process**:
1. Chord-tone quantization: `pitch_index → nearest chord tone` per section progression
2. Voice leading check: parallel fifths/octaves detection
3. Voice leading correction: stepwise shift to adjacent chord tone

Pure generative output without Phase 2 is mathematically interesting but
musically incoherent. Never ship Phase-1-only output.

## Generative Methods (available in generators/)

| Module | Method |
|--------|--------|
| `chain.py` | Markov chains (canonical — MusicGenerator pattern) |
| `genetic.py` | Genetic algorithms with fitness/crossover/mutation |
| `harmonics.py` | Overtone-based composition |
| `rhythm.py` | Euclidean rhythms (canonical impl) |
| `stochastic.py` | Stochastic generation |
| `tendency_masking.py` | Tendency mask stochastic bounds |
| `markov_constraint.py` | Markov-constraint wavefront sequencing (MCWS) |
| `schillinger.py` | Schillinger system (resultants) |
| `pitchpattern.py` | Scale-based pitch patterns |
| `chord_degrees.py` | Diatonic chord progressions |

Plus `sound/generators/event_core.py` for event cores:
MarkovCore, StochasticCore, EuclideanCore, LSystemCore, WeightedRandomCore, PatternSequencer.

## Pitfalls (learned)

- `MusicUnit` has NO `append()` — always `add_event(MusicEvent(...))`
- Off-by-octave on chord wrapping: route diatonic pitch math through
  `Scale7ChordDegree.get_diatonic_note()`, never custom `% 7` wrappers
- `MidiInstrument` enum only has 10 instruments — use raw program numbers (0-127) for others
- Multi-section split: events have absolute ticks, sections expect relative — use pad/split pattern
- FHN monophonic bug: map inter-spike interval to pitch, not voltage at threshold

## Output Rules

- All artifacts (`.mid`, `.wav`, `.ogg`) → `/opt/data/projects/Research/outputs/<project>/`
- NEVER write outputs into the repo
- After every write: `assert os.path.getsize(path) > 40` (empties appear as 16-22 bytes)
