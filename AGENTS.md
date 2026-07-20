# AGENTS.md — Musicom operating guide for AI agents

Canonical, machine-facing entry point. Read this first before composing.
If this file and README/QUICK_REFERENCE disagree, this file wins.

## Environment (exact)

| Thing | Value |
|---|---|
| Python env | `/opt/data/micromamba/envs/musicom/bin/python` |
| Package | `musicom` 0.1.0, installed **editable** (`pip install -e ".[dev]"`) |
| Repo root | `/opt/data/repos/musicom` |
| SoundFont | `TimGM6mb.sf2` (via `/opt/data/micromamba/envs/musicom/bin/fluidsynth`) |

## Import rules (do not guess)

Flat layout — **top-level dirs ARE the packages**:

```python
from structures import MusicUnit, MusicEvent, UnitMatrix, MidiInstrument
from workflows.unitmatrix_composer import UnitMatrixComposer, create_note_unit, create_chord_unit
```

- ✅ `from structures import ...`, `from workflows.unitmatrix_composer import ...`
- ✅ `from musicom.ai.core.tet_system import ...` (legacy alias, works via `musicom_compat.pth`)
- ❌ never `from ..structures import ...` (raises "beyond top-level package")
- ❌ do NOT expect `from musicom import UnitMatrix` — the `musicom` name is an alias namespace only

Imports are **cwd-independent** after the editable install.

## Core model (memorize)

- **Time is ABSOLUTE ticks.** `MusicEvent(pitch, volume, start_tick, end_tick)`.
- `UnitMatrix`: rows = voices, cols = sections, cells = `MusicUnit`. **All rows MUST be equal length** — this is the zero-drift invariant.
- Standard resolution: `ticks_per_beat=480`, `beats_per_bar=4` → `BAR = 1920` ticks.

## The one true composition workflow

```python
from workflows.unitmatrix_composer import UnitMatrixComposer, create_note_unit
from structures import MidiInstrument

composer = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
composer.create_matrix(num_voices=N, num_sections=M)   # 1. shape
composer.add_voice("Lead", program=MidiInstrument.FLUTE, channel=0)  # 2. voices
composer.add_section("A", bars=1)                      # 3. sections
composer.fill_voice_section("Lead", "A", create_note_unit(72, 1920))  # 4. fill cells
ok, msg = composer.validate()                          # 5. zero-drift gate — MUST be True
composer.to_midi("out.mid")                            # 6. export
```

Order: `create_matrix → add_voice → add_section → set_unit/fill_voice_section → validate → to_midi`.
Tempo meta lives in track 0. Percussion is channel 9 (`MidiPercussion`).

## Rendering MIDI → audio

```bash
PY=/opt/data/micromamba/envs/musicom/bin
$PY/fluidsynth -ni -g 1.2 -F out.wav TimGM6mb.sf2 out.mid   # -g 1.2 prevents tail truncation
ffmpeg -y -i out.wav out.ogg
```

## Output location (hard rule)

All composition artifacts (`.mid`, `.wav`, `.ogg`) go in a dedicated project
subfolder under `/opt/data/projects/Research/` (e.g.
`/opt/data/projects/Research/outputs/<project>/`). **Never** write outputs into
the repo or a raw root folder.

## Verify-don't-trust (mandatory)

After ANY MIDI/WAV write:

```python
import os
assert os.path.getsize(path) > 40, "empty/corrupt output — regenerate"
```

Empty files historically appear as 16–22 bytes. `stat` and assert size every time.

## Testing

```bash
cd /opt/data/repos/musicom
/opt/data/micromamba/envs/musicom/bin/python -m pytest tests/ -q
```

Suite is **green** (25 passed, 1 documented skip). Key files:
- `tests/test_harness_golden.py` — **zero-drift regression net**: a fixed
  composition must export byte-identical MIDI (`GOLDEN_SHA256`), be deterministic,
  non-empty, and have equal-length tracks. Update `GOLDEN_SHA256` only when the
  export format changes *intentionally*.
- `tests/test_phase2_bugfixes.py` — regression guards for the 5 fixed bugs.
- `tests/test_docs_smoke.py` — proves documented code runs.

1 skip: `test_pitch_class_set_and_graph` — `MusicPitchClassSet` construction is
broken (`MusicPitchGrid()` called without required `pitches` arg, pitchclass.py:301).
The pitch subsystem (`structures/pitch.py`) is minimal stubs pending completion.

## Known code quirks

_All four Phase-1-era quirks are fixed as of Phase 2:_
- ✅ `MusicEvent.duration` now returns `end_tick - start_tick` correctly (including when `start_tick == 0`).
- ✅ `Counterpoint.has_crossing_voices()` returns `True` on a real crossing (both directions).
- ✅ `MarkovChainGenerator.generate_unit_from_sequence()` and `StochasticGenerator.generate()` build events via `MusicUnit.add_event(MusicEvent(...))` with absolute ticks (no phantom `unit.append()`).
- ✅ `utilities/config.py` `DEFAULT_PATH` is now cross-platform (`tempfile.gettempdir()/Music`).

`MusicUnit` has **no** `append()` method — use `add_event(MusicEvent(...))`.

## Missing-link features (Phase 4)

- **Grid visualizer** — `ai/utils/visualizer.py`: `render_grid(matrix, ...)` returns
  a █/░ density timeline (per-voice Density %); `write_grid_visualization(matrix, path)`
  persists it (e.g. `.../Analysis/grid_visualization.txt`).
- **Vocal guide synth** — `ai/generators/vocal_synth.py`: `FormantVocalGuide` renders
  formant-filtered guide vocals. `render_syllable(freq, dur, vowel, path)` and
  `render_melody(unit, path, vowels=[...])` (MusicUnit -> mono WAV). Sine fallback
  when scipy is unavailable; stdlib `wave` fallback for writing.
- **DAW clock bridge** — `ai/integration/daw_sync.py`: `DAWClockBridge(bpm).run_clock(pulses, dry_run=)`
  emits MIDI Clock (24 PPQN) via virtual mido port; headless fallback prints markers.
  Use `dry_run=True` in tests (skips real-time sleeps).

## Agent execution contract

1. One task at a time, in order.
2. After each task run the stated verify command; report the **real** output.
3. If verify fails: stop, report honestly, never fabricate results.
4. Outputs → `/opt/data/projects/Research/outputs/<project>/`.
5. Commit after each logical phase.
