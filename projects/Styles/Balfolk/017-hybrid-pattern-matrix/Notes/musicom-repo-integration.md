# Musicom Repo Integration — MusicMatrix Semantics

Source repo: `axelwiertz/musicom`

Local path used for KB inspection:

```text
/opt/data/repos/musicom
```

## Canonical structure found

File:

```text
/opt/data/repos/musicom/structures/matrix.py
```

Class:

```python
class UnitMatrix:
    """
    Basic 2D matrix for MusicUnit objects:
    - horizontal rows are voices in pitch space
    - vertical columns are sections in time space
    """
```

## Reserved meaning

`MusicMatrix` / `UnitMatrix` is not a generic table.

It is reserved for:

- rows = voices / pitch-space layers
- columns = measures / sections / time-space segments
- cells = `MusicUnit` objects or measure-level musical material

So MusicMatrix combines:

- pitch dimension: voice rows and pitch operations
- time dimension: measure/section columns and time operations

## Current implemented operations

UnitMatrix supports:

- `get_unit(row, col)`
- `set_unit(row, col, unit)`
- `apply_to_row()`
- `apply_to_column()`
- `repeat_column()`
- `insert_column()`
- `reorder_columns()`
- `reorder_rows()`
- `units_in_row()`
- `units_in_col()`
- `mutate_unit()`
- `swap_units()`
- `transpose_matrix()`
- `diagonal_read()`
- `selective_erase()`
- `transpose_row()`
- `retrograde_row()`
- `invert_row()`
- `augment_row()`

## Genre Matrix relationship

The genre matrix is a semantic layer that fits inside MusicMatrix.

Use this mapping:

```text
Genre Pattern Matrix = metadata / design lens
MusicMatrix / UnitMatrix = actual compositional grid
```

Genre Pattern Matrix rows:

- rhythm DNA
- bass DNA
- harmony DNA
- melody DNA
- timbre DNA
- form DNA

MusicMatrix rows:

- percussion voice
- bass voice
- harmony voice
- lead voice
- pad/counterline voice

Genre Matrix columns:

- bar 1, bar 2, bar 3...
- or section A, section B, cadence...

MusicMatrix columns:

- measure-level `MusicUnit` cells
- same time segmentation

## Exercise 1 mapping

For Project 014 Exercise 1:

```text
MusicMatrix rows:
1. Foot Pulse / Drums
2. Bass
3. Harmony / Chords
4. Lead / Fiddle or Sax

MusicMatrix columns:
1..8 bars

Genre semantics:
- Balfolk: rhythm row uses jig gravity `█░░█░░`
- Jazz: harmony row uses ii-V-I and extended chords
- Hybrid: rhythm row remains Balfolk; harmony row borrows Jazz extensions
```

This means the hybrid is not vague fusion. It is a controlled matrix substitution:

```text
Keep rows: rhythm, bass, melody contour
Replace row: harmony color
Optional replace row: timbre
```

## Python environment note

`music21` is available in Hermes venv:

```text
/opt/hermes/.venv/bin/python3
music21 10.1.0
```

System Python has `mido` but not `music21`:

```text
/usr/bin/python3
mido yes
music21 no
```

Use `/opt/hermes/.venv/bin/python3` for music21-based MusicMatrix work.
Use `/usr/bin/python3` for existing mido-only fallback scripts unless mido is installed into venv.
