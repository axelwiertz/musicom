# AGENTS.md — Composition project policy (Research)

**Auto-injected** when a job runs with a workdir under this tree. Read before writing any composition code.

## HARD RULE: use the musicom engine, not custom code

All MIDI/composition work in this folder MUST go through the installed `musicom`
engine at `/opt/data/repos/musicom`. Do **not** hand-roll MIDI with raw `mido`,
custom note loops, or ad-hoc numpy event arrays.

### Required imports (work from any cwd — package is installed editable)

```python
from structures import MusicUnit, MusicEvent, UnitMatrix, MidiInstrument
from workflows.unitmatrix_composer import UnitMatrixComposer, create_note_unit, create_chord_unit
```

Do NOT add `sys.path.insert(...)` — the package is installed; imports resolve globally.

### The only sanctioned composition workflow

```python
composer = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
composer.create_matrix(num_voices=N, num_sections=M)
composer.add_voice("Lead", program=MidiInstrument.FLUTE, channel=0)
composer.add_section("A", bars=1)
composer.fill_voice_section("Lead", "A", create_note_unit(72, 1920))
ok, msg = composer.validate()     # zero-drift gate — MUST be True before export
composer.to_midi(out_path)
```

Order: `create_matrix → add_voice → add_section → fill/set_unit → validate → to_midi`.
This is what guarantees **zero track drift** — the whole reason the engine exists.

### FORBIDDEN patterns (why)

| Don't | Because |
|---|---|
| `import mido` + manual `MidiTrack()`/`note_on` | bypasses zero-drift padding → track desync |
| custom pitch loops writing `.mid` directly | no validation gate, silent empty files |
| `sys.path.insert("/opt/data/repos/musicom")` | package is installed editable; hack is stale |
| new "generator" reimplementing Markov/stochastic | already in `generators/` — extend, don't fork |

`mido` is allowed ONLY for *reading/analyzing* existing MIDI, never for authoring.

## Output rules

- Every artifact → its own subfolder: `$MUSICOM_ROOT/projects/Research/outputs/<project>/`
  (alias: `/opt/data/projects/Research/outputs/<project>/` — symlinked)
- After render: assert file size > 40 bytes (empties historically 16–22 B).
- Write a `provenance.json` sidecar (`from workflows.provenance import write_provenance`).
- Visualize before trusting: `from visualization.grid import write_grid_visualization`.

## Before you commit / finish — run the preflight

```bash
$MUSICOM_PYTHON \
  $MUSICOM_ROOT/projects/Research/preflight_check.py <your_project_dir>
```

Exit 0 = compliant. Non-zero = you used forbidden raw-MIDI/custom code — fix it.

## Reference

Full engine guide: `$MUSICOM_ROOT/AGENTS.md` (alias:
`/opt/data/repos/musicom/AGENTS.md`). Copy a fresh project from
`$MUSICOM_ROOT/projects/Research/_TEMPLATE/`.
