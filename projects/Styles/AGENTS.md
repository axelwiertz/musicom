# AGENTS.md — Composition project policy (Styles)

**Auto-injected** when a job runs with a workdir under this tree. Read before composing.

## HARD RULE: use the musicom engine, not custom code

All MIDI composition in this folder MUST go through the installed `musicom`
engine. Do **not** hand-roll MIDI with raw `mido`, custom note loops, or ad-hoc numpy event arrays.

**Python env:** `$MUSICOM_PYTHON` → `/opt/data/micromamba/envs/musicom/bin/python` (ONE-ENV contract; bare `fluidsynth` on PATH via `~/.bashrc`)

### Required imports (work from any cwd)

```python
from structures import MusicUnit, MusicEvent, UnitMatrix, MidiInstrument, MidiPercussion
from workflows.unitmatrix_composer import (
    UnitMatrixComposer, create_note_unit, create_chord_unit, create_empty_unit,
)
from visualization.grid import write_grid_visualization
from workflows.provenance import write_provenance, AI_ASSISTED
```

No `sys.path.insert(...)` — package is installed editable.

### Sanctioned workflow

```python
composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=480, beats_per_bar=4)
composer.create_matrix(num_voices=N, num_sections=M)
composer.add_voice("Lead", program=MidiInstrument.FLUTE, channel=0)
composer.add_voice("Drums", program=0, channel=9)
composer.add_section("A", bars=4)
composer.fill_voice_section("Lead", "A", melody_unit)
ok, msg = composer.validate()     # zero-drift gate — MUST be True
composer.to_midi(out_path)
```

### FORBIDDEN

| Don't | Why |
|---|---|
| `import mido` + manual `MidiTrack()`/`note_on` | bypasses zero-drift → track desync |
| `sys.path.insert("/opt/data/repos/musicom")` | stale; package is installed |
| writing `.mid` without `validate()` | silent drift/corruption |

`mido` import is allowed ONLY for *reading/analyzing* existing MIDI.

## Output rules

- Outputs live **in the project subfolder** (e.g. `Styles/Jazz/my-project/MIDI/`, `Audio/`, etc.)
- After render: `assert os.path.getsize(path) > 40` (empties historically 16-22 B)
- Write `provenance.json` sidecar per artifact
- Write `grid_visualization.txt` before trusting timing

## Preflight

```bash
$MUSICOM_PYTHON \
  $MUSICOM_ROOT/projects/Research/preflight_check.py <your_project_dir>
```

## Starter template

Copy from `$MUSICOM_ROOT/projects/Research/_TEMPLATE/` (alias:
`/opt/data/projects/Research/_TEMPLATE/` — symlinked).

## Reference

Full engine guide: `/opt/data/repos/musicom/AGENTS.md`
