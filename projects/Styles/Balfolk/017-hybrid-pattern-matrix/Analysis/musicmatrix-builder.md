# MusicMatrix Builder — Exercise 1

This version rebuilds Exercise 1 using Musicom `UnitMatrix` semantics and `music21` export.

## Source semantics

Repo:

```text
/opt/data/repos/musicom
```

Classes loaded from repo files:

```text
structures/unit.py    -> MusicEvent, MusicUnit
structures/matrix.py  -> UnitMatrix
```

Meaning:

```text
Rows    = voices / pitch-space layers
Columns = measures / time-space segments
Cells   = MusicUnit bar material
```

## Why direct file loading?

The repo package import path currently pulls optional theory dependencies such as `networkx` through `structures/__init__.py` and `pitchclass.py`.

For this exercise, only `MusicEvent`, `MusicUnit`, and `UnitMatrix` are needed. The script loads those files directly, with a small stub for `visualization.Cycle`, then exports through `music21`.

## Python environment

Used:

```text
/opt/hermes/.venv/bin/python3
music21 10.1.0
```

Rendering:

```text
music21 Score -> MIDI -> FluidSynth + FluidR3_GM.sf2 -> WAV -> ffmpeg OGG/Opus
```

## Matrix rows per version

### A. Balfolk

```text
Row 1: Foot Pulse / Drums
Row 2: Bass Voice
Row 3: Harmony Voice
Row 4: Lead Voice
Columns: 8 bars of 6/8
```

### B. Jazz

```text
Row 1: Ride + Backbeat
Row 2: Walking Bass
Row 3: Piano Harmony
Row 4: Sax Lead
Columns: 8 bars of 4/4
```

### C. Hybrid

```text
Row 1: Jig Pulse / Drums
Row 2: Modal Bass
Row 3: Jazz Color Harmony
Row 4: Folk Lead
Columns: 8 bars of 6/8
```

Hybrid operation:

```text
Keep Balfolk rows: rhythm, bass, lead contour
Replace/extend row: harmony -> Dm9, Cmaj7, G13
```

## Generated files

- `MIDI/musicmatrix_exercise1a_balfolk_dorian_jig.mid`
- `MIDI/musicmatrix_exercise1b_jazz_ii_v_i_swing.mid`
- `MIDI/musicmatrix_exercise1c_hybrid_balfolk_jazz.mid`
- `Audio/musicmatrix_exercise1a_balfolk_dorian_jig.ogg`
- `Audio/musicmatrix_exercise1b_jazz_ii_v_i_swing.ogg`
- `Audio/musicmatrix_exercise1c_hybrid_balfolk_jazz.ogg`
- `Audio/musicmatrix_exercise1_all_three_compare.ogg`
- `Analysis/musicmatrix_manifest.json`

## Verification

- All OGG files decoded with `ffmpeg -f null`.
- All MIDI files non-empty.
- Manifest stores row names, columns, tempo, meter, and matrix semantics.
