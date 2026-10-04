# CLAUDE.md — musicom

Code-agent entry point (Claude Code, Hermes, etc.). Read in this order, then
open the task-specific doc:

1. `AGENTS.md` — canonical machine-facing guide (wins over README).
2. `docs/AGENT_MANUAL.md` — the agent manual (repo map, recipes, gates, failures).
3. Task-specific: `docs/patterns.md` · `docs/methods.md` · `docs/instruments.md`
   · `hermes_agent/*.md` · instrument `instrument.md`.

## Non-negotiables

- **Zero-drift**: `validate()` must pass before `to_midi()`.
- **Verify-don't-trust**: size-assert every artifact (`> 40` bytes for MIDI/WAV).
- **Flat imports**: `from structures import …` — never `from musicom import …`.
- **Purity**: don't eagerly import `musicpy`/`music21`; use mido READ-only.
- **Reverse**: use `workflows.analyze.analyze_midi` — never raw mido authoring.

## Output locations

- Public contributions / examples write to `./outputs/` (gitignored).
- The living corpus lives in `projects/` (nightly-synced; heavy artifacts gitignored).

See `REPO_MAP.md` for the full layout.
