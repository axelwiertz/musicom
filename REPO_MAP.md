# REPO_MAP.md — what lives where

Single source of truth for the musicom repository layout. One line per folder:
what it contains, who it's for, and whether it ships in the pip wheel.

| Folder | Contains | Audience | Ships in wheel? |
|---|---|---|---|
| `structures/` | `MusicUnit`, `MusicEvent`, `UnitMatrix`, `MidiInstrument` | engine users | ✅ |
| `workflows/` | `UnitMatrixComposer`, `compose()`, `produce()`, `analyze_midi()` | engine users | ✅ |
| `generators/` | method registry (SCALE/GENERATOR), interval chains, L-systems | engine users | ✅ |
| `rules/` | set theory, harmony, voice leading, patterns, realize | engine users | ✅ |
| `sound/` | render (FluidSynth/KS), analysis, effects, tuning, modular | engine users | ✅ |
| `transformers/` | transpose, retrograde, negative harmony, canon | engine users | ✅ |
| `converters/` | MIDI/music21 conversion (forward + reverse) | engine users | ✅ |
| `analysis/` | score/piece analysis helpers (music21/musicpy-coupled) | engine users | ✅ |
| `visualization/` | grid render | engine users | ✅ |
| `utilities/` | `env.py` (ONE-ENV path resolution) | engine users | ✅ |
| `legacy/` | quarantined old `MusicPitchClassSet` shim | maintenance only | ✅ |
| `docs/` | guides, generated tables, AGENT_MANUAL, patterns/methods | learners | ✅ (tables + manual) |
| `examples/` | curated runnable snippets + `README.md` (curated vs scratch) | learners | ❌ (repo only) |
| `projects/Styles/` | **educational compositions** (MIDI + OGG + REPORT) | learners | ❌ |
| `projects/Instruments/` | **instrument reference tree** (18 instruments + registry) | learners | ❌ |
| `projects/Research/` | **composition-method research**: DBs, method notes, reports | learners | ❌ |
| `projects/Legacy/` | **older projects**, kept for reference/history | curious | ❌ |
| `projects/Styles/Production/` | **rendered production pipeline output** (WAV-heavy, host-FS only) | maintainers | ❌ |
| `skills/` | Hermes-agent skill (SKILL.md + scripts) | agents | ❌ |
| `hermes_agent/` | Hermes runtime KB + `surveillance-reports/` (agent ops logs) | agents | ❌ |
| `research/` | experimental seeds (`trainmodel.py`, `intervalnetwork.py`) | devs | ❌ |
| `scripts/` | setup + table-generation tools | maintainers | ❌ |
| `tests/` | test suite (zero-drift golden harness) | maintainers | ❌ |

## Root files

| File | Purpose |
|---|---|
| `README.md` | human-facing overview, forward + reverse pipeline, quick start |
| `AGENTS.md` | canonical machine-facing guide — wins over README on conflict |
| `QUICK_REFERENCE.md` | terse API cheat-sheet |
| `CLAUDE.md` | pointer for Claude Code / code agents |
| `SKILL.md` | skill entry (pairs the codebase with a Hermes agent) |
| `REPO_MAP.md` | this file |
| `CHANGELOG.md` | release history |
| `LICENSE` | MIT |
| `pyproject.toml` | package + version + deps |
| `environment.yml`, `requirements.lock` | env setup |

## Conventions

- **Engine** = the packages that ship in the wheel (`structures/` … `utilities/`,
  plus `legacy/`). Keep these portable — no host-specific absolute paths.
- **Corpus** = everything under `projects/`. Educational reference material,
  nightly-synced by the host cron; heavy/derived artifacts (`*.wav`, `*.log`,
  `outputs/`) are gitignored.
- **Docs** = `docs/` + the root `*.md` files. `docs/methods.md`,
  `docs/human-methods.md`, `docs/instruments.md`, `docs/patterns.md` tables are
  generated — never hand-maintain them.
- **Reverse** analysis lives in `workflows/analyze.py` (`analyze_midi`), not in
  the `analysis/` music21/musicpy helpers (those stay as opt-in notation tools).
