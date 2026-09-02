# Quick Reference Guide

> Every code block here is executed verbatim by the doc-verification script
> (`tests/test_docs_smoke.py` when present) and passes against the real API.

## Installation

Flat package layout — top-level dirs are the packages.

```bash
pip install -e ".[dev]"
```

```python
from structures import MusicUnit, MusicEvent, UnitMatrix
from workflows.unitmatrix_composer import UnitMatrixComposer
```

## Core Concepts

| Concept | Reality |
|---|---|
| Time | **Absolute ticks** (`start_tick`, `end_tick`), not relative durations |
| `MusicEvent` | `(pitch, volume, start_tick, end_tick)`, numpy-backed |
| `MusicUnit` | sequence of events in a structured numpy array |
| `UnitMatrix` | rows = voices, cols = sections, cells = `MusicUnit` |
| `UnitMatrixComposer` | high-level, zero-drift MIDI export workflow |

## 1. MusicEvent

```python
from structures import MusicEvent

e = MusicEvent(pitch=60, volume=100, start_tick=0, end_tick=480)  # C4, one beat
e.pitch        # 60
e.volume       # 100
e.start_tick   # 0
e.end_tick     # 480
e.duration     # 480
```

## 2. MusicUnit

```python
from structures import MusicUnit, MusicEvent

melody = MusicUnit(events=[
    MusicEvent(60, 100, 0,    480),
    MusicEvent(62, 100, 480,  960),
    MusicEvent(64, 100, 960,  1440),
])

melody.pitches            # [60, 62, 64]
melody.volumes            # [100, 100, 100]
melody.pitch_intervals    # [2, 2]
melody.onset_intervals    # [480, 480]
melody.len_ticks()        # 1440
len(melody)               # 3

# In-place transformations
melody.transpose(12)      # shift all pitches +12
melody.retrograde()       # reverse event order
melody.invert(60)         # mirror pitches around pivot 60
melody.augment(2.0)       # scale durations x2

# Utilities
a, b = melody.split(1)    # two MusicUnits
combined = a + b          # concatenate
clone = melody.clone()
```

## 3. UnitMatrix

```python
from structures import UnitMatrix

matrix = UnitMatrix(shape=(4, 8))     # 4 voices x 8 sections
matrix.set_unit((0, 0), melody)       # (row, col) tuple
matrix.get_unit((0, 0))               # -> MusicUnit or None
matrix.get_all_row_lengths()          # list of per-row lengths in ticks
matrix.validate_timing()              # True when all rows equal length
matrix.get_track_length()             # total ticks
```

## 4. UnitMatrixComposer (recommended)

```python
from workflows.unitmatrix_composer import (
    UnitMatrixComposer, create_note_unit, create_chord_unit, create_empty_unit,
)
from structures import MidiInstrument

composer = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
composer.create_matrix(num_voices=3, num_sections=1)

composer.add_voice("Lead",  program=MidiInstrument.FLUTE,          channel=0)
composer.add_voice("Chord", program=MidiInstrument.STRING_ENSEMBLE, channel=1)
composer.add_voice("Bass",  program=MidiInstrument.BASS,           channel=2)
composer.add_section("A", bars=1)

BAR = 480 * 4
composer.fill_voice_section("Lead",  "A", create_note_unit(72, BAR))
composer.fill_voice_section("Chord", "A", create_chord_unit([60, 64, 67], BAR))
composer.fill_voice_section("Bass",  "A", create_note_unit(36, BAR))

ok, msg = composer.validate()          # (True, "OK")
composer.to_midi("out.mid")            # zero-drift, equal-length tracks
data = composer.to_midi_bytes()        # or get bytes directly
```

**Canonical order:** `create_matrix()` → `add_voice()` → `add_section()` →
`set_unit()` / `fill_voice_section()` → `validate()` → `to_midi()`.

### Cell helpers

```python
create_note_unit(pitch, duration_ticks, start_tick=0)   # single note
create_chord_unit([p1, p2, p3], duration_ticks, start_tick=0)  # simultaneous
create_empty_unit(duration_ticks)                        # silent rest (pitch=0)
```

### Pre-built form

```python
from workflows.unitmatrix_composer import create_blues_form_matrix
composer, info = create_blues_form_matrix(bpm=80, num_bars=12)
# info -> {'form': '12-bar blues', 'sections': [...], 'harmony': ['I','I',...]}
```

## 5. Generators

```python
from generators.markov import MarkovGenerator
# See generators/ for: markov, genetic, stochastic, harmonics, rhythm,
# pitchpattern, chord_degrees, schillinger, tendency_masking, markov_constraint.
```

## 6. Rules

```python
from rules.counterpoint import Counterpoint
from rules.progression import PatternMovement, Scale7ChordDegree, MusicForm
```

## MIDI Reference

### MidiInstrument (program numbers)

| Name | # |
|---|---|
| `PIANO` | 0 |
| `CHURCH_ORGAN` | 20 |
| `ACOUSTIC_GUITAR` | 25 |
| `BASS` | 33 |
| `VIOLIN` | 41 |
| `STRING_ENSEMBLE` | 49 |
| `TRUMPET` | 57 |
| `FLUTE` | 74 |
| `SYNTH_PAD` | 88 |

`MidiPercussion` (channel 9): `BASS_DRUM=36`, `ACOUSTIC_SNARE=38`,
`CLOSED_HI_HAT=42`, `CRASH_CYMBAL=49`, `RIDE_CYMBAL=51`, `LOW_TOM=45`, ...

## Pitch System (12-TET)

- C=0, C#=1, D=2, D#=3, E=4, F=5, F#=6, G=7, G#=8, A=9, A#=10, B=11
- Middle C (C4) = 60, A440 (A4) = 69, range 0–127
- `pitch_class = pitch % 12`, `octave = (pitch // 12) - 1`

## Rendering MIDI → Audio (headless)

```bash
# WAV via fluidsynth (boost gain to avoid decay-tail truncation)
fluidsynth -ni -g 1.2 -F out.wav /path/to/soundfont.sf2 out.mid
# WAV -> OGG via ffmpeg
ffmpeg -y -i out.wav out.ogg
```

## Troubleshooting

| Symptom | Fix |
|---|---|
| `ModuleNotFoundError: structures` | `pip install -e ".[dev]"` from repo root |
| `attempted relative import beyond top-level package` | use flat absolute imports (`from structures.base import Base`), not `..structures` |
| MIDI file 16–22 bytes (empty) | export failed silently — `stat` file, assert size, regenerate |
| Track length mismatch on `validate()` | pad rows to equal length; matrix is zero-drift only when rows match |
