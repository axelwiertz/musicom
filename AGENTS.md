# AGENTS.md — Musicom operating guide for AI agents

Canonical, machine-facing entry point. Read this first before composing.
If this file and README/QUICK_REFERENCE disagree, this file wins.

## Environment (exact)

| Thing | Value |
|---|---|
| Python env | `$MUSICOM_PYTHON` → `/opt/data/micromamba/envs/musicom/bin/python` (ONE-ENV contract, see `utilities/env.py`) |
| Package | `musicom` 0.1.0, installed **editable** (`pip install -e ".[dev]"`) |
| Repo root | `$MUSICOM_ROOT` → `/opt/data/repos/musicom` (env vars in `~/.bashrc`, auto-sourced) |
| Fluidsynth | `$MUSICOM_FLUIDSYNTH` → `/opt/data/micromamba/envs/musicom/bin/fluidsynth`; bare `fluidsynth` on PATH via env |
| SoundFont | `$MUSICOM_SOUNDFONT` → FluidR3_GM.sf2 (preferred) or TimGM6mb.sf2 (fallback) via `discover_soundfont()` |
| Project tree | `/opt/data/repos/musicom/projects/` is the SINGLE working tree; `/opt/data/projects/{Styles,Research,Instruments}` are symlinks to it (2026-09-08 restructure) |

Resolution helpers (never hardcode absolute paths in new code):
```python
from utilities.env import repo_root, python_bin, fluidsynth_bin, soundfont_path
```

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
$PY/fluidsynth -ni -g 1.2 -F out.wav FluidR3_GM.sf2 out.mid   # -g 1.2 prevents tail truncation
ffmpeg -y -i out.wav out.ogg
```

SoundFont preference (auto-resolved by `discover_soundfont()`):
1. `FluidR3_GM.sf2` (141 MB, proper woodwind/brass/strings — the default)
2. `TimGM6mb.sf2` (6 MB minimal GM set — thin/buzzy oboe, bassoon, flute;
   fallback only). Never hardcode TimGM6mb in new code; call
   `from sound.render.fluidsynth import discover_soundfont`.

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

Suite is **green** (626 passed, 1 skipped + the voice-hybrid file run
separately). Key files:
- `tests/test_harness_golden.py` — **zero-drift regression net**: a fixed
  composition must export byte-identical MIDI (`GOLDEN_SHA256`), be deterministic,
  non-empty, and have equal-length tracks. Update `GOLDEN_SHA256` only when the
  export format changes *intentionally*.
- `tests/test_realize_bridge.py` — second golden gate: `compose()`'s abstract
  (ABS-*) path must stay byte-identical (`ABS_GOLDEN_SHA256`), pinning the
  `rules/realize.py` refactor as output-neutral.
- `tests/test_generator_lazy_imports.py` — **import purity**: importing the
  method registry must NOT load `musicpy`/`music21` (see History below).
- `tests/test_set_theory_kernel.py`, `tests/test_patterns_library.py`,
  `tests/test_realize_bridge.py`, `tests/test_exercises.py`,
  `tests/test_patterns_docs.py` — the pattern layer (see `docs/patterns.md`;
  the docs test re-executes every snippet on that page).
- `tests/test_legacy_quarantine.py` — pins the quarantined System A defects
  and proves its consumers still work.
- `tests/test_phase2_bugfixes.py` — regression guards for the 5 fixed bugs.
- `tests/test_docs_smoke.py` — proves documented code runs.

## Pattern layer (post-reorganization)

Pitch-class-set work has one sanctioned path — `docs/patterns.md` is the guide:

- `rules/set_theory.py` — kernel: normal/prime form, ICV, Forte names
  (`forte_name`, `pcs_from_forte`), Z-relations (`z_partner`, `all_z_pairs` —
  23 pairs incl. all 15 hexachord pairs).
- `rules/patterns.py` — `Pattern` (`.forte`, `.z_partner`, roles/tags), the
  frozen 91-entry `standard_patterns()` (ORDER IS GOLDEN-HASH-LOADING), and
  the catalogues (48 triads / 60 tetrads / 7 modes / 50 hexachords / 8 scale
  pools) plus the rhythm side (`RhythmPattern`, `RhythmPatternNetwork`,
  `euclidean_rhythm`).
- `rules/realize.py` — the abstract→concrete bridge: `Pattern →
  MusicEvent[]` with register placement, voicings, articulation and
  voice-leading continuity (`realize_progression(..., smooth=True)`).
- `rules/exercises.py` — `run_exercise("ABS-EX-001" … "CON-EX-004")`:
  runnable, self-verifying abstract and concrete exercises.
- `legacy/` — the old mode-centric `MusicPitchClassSet` model. Quarantined,
  partly broken (defects pinned by test), still imported by ~76 project
  scripts through the `structures.pitchclass` shim. Bridge out with
  `MusicPitchClassSet(...).to_pattern()`. **Do not import `legacy` in new
  code** and do not "fix" it — build on `rules/` instead.

History worth knowing: an automated composition job imported
`generators.generator_registry`, got the legacy `musicpy`/`music21`
converters loaded via an eager package `__init__`, and burned its whole
budget "fixing" converters instead of composing. The lazy-import fix and the
purity tests exist so that cannot repeat.

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

## Maintenance notes

- **Vendored engine copies**: several sibling repos (`composer-crew-framework`,
  `musicom-agent`, `musicom_framework`, `musicom_platform`) carry a `lib/musicom/`
  tree — parallel copies of this engine at older stages. Do NOT edit those
  copies. The engine is installed **editable** from this repo
  (`/opt/data/repos/musicom`); those vendored trees are frozen snapshots.
- **Method DB code truth**: the canonical, machine-readable method catalog is
  `generators/generator_registry.py` + `workflows/paths.py` (`SCALE`). The
  long-form `methods_db.md` / `human_methods_db.md` prose (synced to `docs/`)
  is human-readable reference and may lag code — when they disagree, code wins.
- **Abstract layer** (`rules/subset_network.py`, `ABS-001..005`) is the newest
  addition (see `projects/Research/CompositionMethods/LAYER_ARCHITECTURE.md`).
  ABS methods are registered in `SCALE` + `GENERATOR_REGISTRY`; they are NOT
  yet listed in the prose `methods_db.md`.

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
