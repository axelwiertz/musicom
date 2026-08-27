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
- ❌ never `from ..structures import ...` (raises "beyond top-level package")
- ❌ do NOT expect `from musicom import UnitMatrix` — the `musicom` name is an alias namespace only

Imports are **cwd-independent** after the editable install.

## Core model (memorize)

- **Time is ABSOLUTE ticks.** `MusicEvent(pitch, volume, start_tick, end_tick)`.
- `UnitMatrix`: rows = voices, cols = sections, cells = `MusicUnit`. **All rows MUST be equal length** — this is the zero-drift invariant.
- Standard resolution: `ticks_per_beat=480`, `beats_per_bar=4` → `BAR = 1920` ticks.

## The one true composition workflow

### Fast path (recommended): the workflow spine

For a complete design → realization loop in one call, use `musicom_workflow`
(Phase 2 reorganization — this is the sanctioned entry point):

```python
from workflows.musicom_workflow import compose, produce

# DESIGN: framework + note material, validated, zero-drift guaranteed
r = compose(style="pop", key="C", bpm=120)          # style from STYLE_REGISTRY
# r.midi_path, r.provenance_path

# REALIZATION: two production methods on the same MIDI
p1 = produce(r.midi_path, method="SP-001")          # FluidSynth WAV + OGG
p2 = produce(r.midi_path, method="SP-011")          # Karplus-Strong WAV + OGG
```

- `compose()` picks a style template (bpm, form, default voices), fills a
  real I–V–vi–IV framework across intro/verse/chorus/bridge/outro, validates,
  exports MIDI + provenance.
- `produce()` dispatches SP methods to the shared `sound/` modules.
- Tables for docs/ are generated: `method_table()`, `sp_method_table()`,
  `style_table()` — never hand-maintain them.

### Low-level (when you need full control)

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

**Equal-length rule**: every voice's section units MUST end at the section's
full length in ticks (terminal landmark at `section_len`). If `validate()`
reports "Track length mismatch", pad the shorter units — see
`_unit_from_events(events, section_len)` in `musicom_workflow.py` for the pattern.

## Rendering MIDI → audio

```bash
PY=/opt/data/micromamba/envs/musicom/bin
$PY/fluidsynth -ni -g 1.2 -F out.wav TimGM6mb.sf2 out.mid   # -g 1.2 prevents tail truncation
ffmpeg -y -i out.wav out.ogg
```

## Output location (hard rule)

All composition artifacts (`.mid`, `.wav`, `.ogg`) go in a dedicated project
subfolder under the Hermes working FS: `/opt/data/projects/Styles/<Genre>/<project>/`
(for compositions) or `/opt/data/projects/Research/outputs/<project>/` (for
experiments). **Never** write outputs into the repo or a raw root folder.
The daily sync mirrors them into this repo's `projects/`.

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

Suite is **green** (263 passed, 0 skipped). Key files:
- `tests/test_harness_golden.py` — **zero-drift regression net**: a fixed
  composition must export byte-identical MIDI (`GOLDEN_SHA256`), be deterministic,
  non-empty, and have equal-length tracks. Update `GOLDEN_SHA256` only when the
  export format changes *intentionally*.
- `tests/test_phase2_bugfixes.py` — regression guards for the 5 fixed bugs.
- `tests/test_docs_smoke.py` — proves documented code runs.

The previously skipped `test_pitch_class_set_and_graph` now runs: the
`@dataclass` decorator was removed from the `PatternType`/`PatternCategory`
enums (it broke enum hashing/equality) and `MusicPitchGrid()` accepts an
optional `pitches` arg. The pitch subsystem (`structures/pitch.py`) remains
minimal stubs pending completion.

## Known code quirks

_All four Phase-1-era quirks are fixed as of Phase 2:_
- ✅ `MusicEvent.duration` now returns `end_tick - start_tick` correctly (including when `start_tick == 0`).
- ✅ `Counterpoint.has_crossing_voices()` returns `True` on a real crossing (both directions).
- ✅ `MarkovChainGenerator.generate_unit_from_sequence()` and `StochasticGenerator.generate()` build events via `MusicUnit.add_event(MusicEvent(...))` with absolute ticks (no phantom `unit.append()`).
- ✅ `utilities/config.py` `DEFAULT_PATH` is now cross-platform (`tempfile.gettempdir()/Music`).

`MusicUnit` has **no** `append()` method — use `add_event(MusicEvent(...))`.

## Missing-link features (Phase 4)

- **Grid visualizer** — `visualization/grid.py`: `render_grid(matrix, ...)` returns
  a █/░ density timeline (per-voice Density %); `write_grid_visualization(matrix, path)`
  persists it (e.g. `.../Analysis/grid_visualization.txt`).
- **Vocal guide synth** — `sound/synthesis/vocal.py`: `FormantVocalGuide` renders
  formant-filtered guide vocals. `render_syllable(freq, dur, vowel, path)` and
  `render_melody(unit, path, vowels=[...])` (MusicUnit -> mono WAV). Sine fallback
  when scipy is unavailable; stdlib `wave` fallback for writing.
- **DAW clock bridge** — `sound/sync/clock.py`: `DAWClockBridge(bpm).run_clock(pulses, dry_run=)`
  emits MIDI Clock (24 PPQN) via virtual mido port; headless fallback prints markers.
  Use `dry_run=True` in tests (skips real-time sleeps).

## Companion workflows (Phase 5)

- **Paradigm compare** — `workflows/paradigm_compare.py`:
  `run_comparison(output_dir, bpm, seed)` generates the same slot three ways —
  `stochastic` (seeded random), `rules` (diatonic stepwise), `nature`
  (Schillinger resultant) — renders MIDI + grid per paradigm, writes a markdown
  comparison table + a provenance sidecar for each. Run as a script to print the table.
- **Provenance** — `workflows/provenance.py`: `write_provenance(artifact, classification,
  generator, sources=, parameters=)` writes `<artifact>.provenance.json`
  (classification ∈ human-made / ai-assisted / ai-generated, sha256, sources,
  params, UTC time). `policy_warnings(record)` surfaces rights/monetization risks.

## Hermes agent knowledge base

Agent-operational knowledge lives in `hermes_agent/` (composition + sound
production workflows, SP method registry, surveillance findings, decision log).
This file (AGENTS.md) stays the canonical guide; `hermes_agent/` extends it.
See `hermes_agent/README.md`.

## Agent execution contract

1. One task at a time, in order.
2. After each task run the stated verify command; report the **real** output.
3. If verify fails: stop, report honestly, never fabricate results.
4. Outputs → Hermes working FS (`/opt/data/projects/Styles/`, `/opt/data/projects/Research/`, etc. — see below). Jobs write there; do NOT write directly into this repo's `projects/` mirror.
5. Do NOT commit per-job. The daily sync job (`daily-repo-sync`) stages + commits everything into this repo.

## Data sync (Hermes FS → repo)

The working tree for all project data is the **Hermes agent filesystem** under
`/opt/data/projects/` (Styles/, Research/, Instruments/, Production/). This repo
holds a **synced, versioned mirror** of that data.

### What syncs (daily, `scripts/sync_to_repo.py` → cron `daily-repo-sync` 23:00 UTC)

| Hermes FS | Repo mirror |
|---|---|
| `/opt/data/projects/Styles/` | `projects/Styles/` |
| `/opt/data/projects/Research/` | `projects/Research/` |
| `/opt/data/projects/Instruments/` | `projects/Instruments/` |
| Instruments registry + methods DBs | `docs/instruments.md`, `docs/methods.md`, `docs/human-methods.md` |

### Tracked extensions (synced)

`.md`, `.py`, `.json`, `.mid`, `.ogg`, `.txt`, `.yaml`, `.yml`, `.toml`

### Ignored (NOT synced)

- `*.wav` — large raw audio, renderable from MIDI (OGG is the tracked, playable form)
- `.env*` — secrets
- `__pycache__/`, `_test/`, `outputs/`, `node_modules/`, `.venv/` — ephemeral

### Manual sync

```bash
/opt/data/micromamba/envs/musicom/bin/python scripts/sync_to_repo.py
```

### Push

The daily sync commits AND pushes to origin/main automatically (autopush —
user decision 2026-08-27). The sync script exits non-zero on push failure so
Hermes alerts if the remote is unreachable.

### Sync script location

- Repo copy: `scripts/sync_to_repo.py` (source of truth)
- Cron copy: `~/.hermes/scripts/sync_to_repo.py` (referenced by the cron job)
