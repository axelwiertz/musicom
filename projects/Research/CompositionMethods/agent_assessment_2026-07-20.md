# Musicom Companion Agent — Assessment & Development Plan
_2026-07-20 · reviewer: Musicom Agent_

## 1. Goal (as designed)
Transparent music companion. Loop: ingest → decompose → explain → compose → compare → select → render → publish.
Human-in-loop gates. Output MIDI + WAV (+ MusicXML). Zero-drift algorithmic MIDI. Genre-neutral.

## 2. Setup (as found)
- **Core engine**: `/opt/data/repos/musicom` — UnitMatrix / UnitMatrixComposer, generators (Markov, genetic, stochastic, harmonics, rhythm, pattern), rules (counterpoint, progression), converters (MIDI, MusicXML, audio, daw_bridge), analysis (music21/musicpy).
- **Env**: micromamba env `musicom`. Render chain: fluidsynth (TimGM6mb.sf2) → WAV → ffmpeg → OGG. Gain boost -g 1.2.
- **Ecosystem**: `musicom-agent` (workspace/skills), `musicom-api-backend` (main.py), `musicom-web-portal` (Next.js), `composer-crew-framework` (role-based), `DiffSinger_main` (vocal, heavy).
- **Outputs**: `/opt/data/projects/Research/outputs/` v1–v7, MIDI+WAV+OGG triplets present. Convention followed.
- **Skills**: role-spec, missing-link-plan, compose-loop, mail-review, project-workflow.

## 3. State (verified, real tool output)
| Check | Result |
|---|---|
| `import musicom` | OK but **namespace pkg, zero top-level exports** |
| `from musicom import UnitMatrix` | **FAIL** — not exported |
| `from musicom.workflows...` | **FAIL** — no module `musicom.workflows` |
| `pip show musicom` | **not installed** (no `pip install -e .` in env) |
| examples import style | `sys.path` hack + bare `from workflows` / `from structures` |
| pytest | **not installed in env** → test suite cannot run |
| git status | 9 modified, ~10 untracked new files uncommitted |
| README API | describes Note/Chord/Sequence/MIDIHandler — **does not match actual** MusicEvent/MusicUnit |
| QUICK_REFERENCE | same phantom API — **doc drift, misleading** |
| render pipeline | working (v1–v7 triplets exist) |

## 4. STRENGTHS
- **Strong conceptual core**: UnitMatrix (voices×sections×MusicUnit) is coherent, systematic, genre-neutral. Real differentiator.
- **Broad algorithm coverage**: stochastic / rules / nature-led paradigms all present — matches user taste for paradigm comparison.
- **Working render chain**: MIDI+WAV+OGG produced, zero-drift discipline, output convention obeyed.
- **Clear role spec + human gates**: honest, auditable, versioned philosophy encoded in skills.
- **numpy-backed MusicUnit**: efficient storage, scales to large works.

## 5. WEAKNESSES
- **Packaging broken** (CRITICAL): not installable/importable as `musicom.*`. Two competing layouts (namespace `musicom/musicom/` vs flat `structures/`,`workflows/`). Every entrypoint depends on cwd + path hacks. Fragile for any model/subagent to run.
- **No runnable test suite**: pytest absent from env; coverage claims unverifiable. No regression safety net.
- **Documentation drift** (HIGH): README + QUICK_REFERENCE document an API that does not exist. Any model reading docs to compose will fail.
- **Known code bugs** (from architecture-review, unfixed): `Counterpoint.has_crossing_voices()` inverted logic; Markov `generate_unit_from_sequence()` calls nonexistent `unit.append()`; missing `retrograde.py`; `CanonTransformer` TODOs; hardcoded Windows path in config.
- **Uncommitted WIP**: 19 dirty files — vocal_synth, daw_sync, visualizer, musicxml, audio, melodica_adapter — new features not committed, not tested, not integrated.
- **Ecosystem sprawl**: 9 repos, unclear which is canonical. `composer-crew-framework` duplicated in 3 places.
- **Missing-link gaps open**: vocal guide, live grid visualizer, DAW/MTC sync all still spec-only.

## 6. OPPORTUNITIES
- **Fix packaging once** → unlocks reliable agent-driven composition + safe subagent delegation.
- **Doc regeneration from actual code** → make agent self-consistent (docs match imports).
- **Grid visualizer** (missing-link Area 2) → cheap, high-value, matches user █/░ aesthetic, pure Python, testable.
- **Golden-file test harness** → deterministic MIDI hashing catches drift/regression, enables autonomous verified artifacts.
- **Paradigm-compare workflow** → user explicitly likes Stochastic vs Rules vs Nature-Led hybrids; ship a one-command A/B/C composer.
- **Provenance/rights layer** (role-spec §2–4) → differentiation beyond generation.

## 7. THREATS / RISKS
- Continued path-hack fragility → silent failures a flash model cannot debug.
- Doc drift → agent hallucinates API, wastes tokens, produces empty files (already a logged pitfall).
- Uncommitted work → loss risk on any reset.

---

## 8. DEVELOPMENT PLAN (Gemini-3-flash-preview executable)
Ordered. Each task = small, verifiable, no deep reasoning required. Written for a fast model: exact paths, exact commands, explicit verify step.

### Phase 0 — Stabilize foundation (do first, blocks everything)
- **T0.1 Install package**: `cd /opt/data/repos/musicom && /opt/data/micromamba/envs/musicom/bin/pip install -e .` then `pip install pytest`. Verify: `python -c "import musicom"` exit 0.
- **T0.2 Decide canonical import layout**: pick flat (`structures/`, `workflows/`) OR namespaced (`musicom.structures`). Recommend flat (matches examples). Verify: `python -c "from workflows.unitmatrix_composer import UnitMatrixComposer"`.
- **T0.3 Commit WIP**: `git add -A && git commit -m "wip: vocal_synth, daw_sync, visualizer, musicxml, audio"`. Verify: `git status` clean.

### Phase 1 — Truth in docs (cheap, high leverage)
- **T1.1 Regenerate README API section from real code**: replace phantom Note/Chord/Sequence examples with MusicEvent/MusicUnit/UnitMatrix. Source of truth = actual `structures/unit.py`, `workflows/unitmatrix_composer.py`.
- **T1.2 Rewrite QUICK_REFERENCE.md** to match. Verify: every code block runnable via `python -c`.
- **T1.3 Add `AGENTS.md`** at repo root: canonical import path, env path, render command, output-folder rule. So any model gets it right first try.

### Phase 2 — Fix known bugs (each ~1 edit + 1 test)
- **T2.1** `rules/counterpoint.py` — invert `has_crossing_voices()` return.
- **T2.2** `generators/markov.py` — replace `unit.append()` with valid MusicUnit construction.
- **T2.3** Create `transformers/retrograde.py` or remove dead import in `transformers/__init__.py`.
- **T2.4** `utilities/config.py` — replace Windows `DEFAULT_PATH` with `os.path` cross-platform.
- Verify each: add one pytest asserting fixed behavior.

### Phase 3 — Test harness (autonomous verification)
- **T3.1 Golden-file MIDI test**: compose fixed seed → hash MIDI bytes → store expected hash. Reruns must match (proves zero-drift + no regression).
- **T3.2 Non-empty artifact test**: after render, assert WAV/MIDI size > 1KB (encodes the logged empty-file pitfall).
- **T3.3** `pytest tests/ -q` must pass green. Verify: exit 0.

### Phase 4 — Missing-link features (spec → real)
- **T4.1 Grid visualizer** (Area 2): Python fn prints █/░ density timeline per voice/section to `Analysis/grid_visualization.txt` before render. Pure stdlib. Testable string output.
- **T4.2 Vocal guide synth** (Area 1): formant-filtered subtractive mono WAV from melody unit. Fallback to sine if fluidsynth path missing.
- **T4.3 DAW/MTC bridge** (Area 3): `mido` virtual port emitting MIDI clock 0xF8. Stub + smoke test only.

### Phase 5 — Companion workflows
- **T5.1 Paradigm-compare command**: one entrypoint generates Stochastic + Rules + Nature-Led variants of same seed material, renders all three, writes compare table. Matches user preference.
- **T5.2 Provenance tags**: write `provenance.json` next to each output (human/AI-assisted/AI-gen + source refs).

### Execution contract for the flash model
1. One task at a time, in order. Never skip Phase 0.
2. After every task: run the stated **Verify** command; paste real output.
3. If verify fails: stop, report, do not fabricate.
4. All new outputs → `/opt/data/projects/Research/outputs/<project>/`.
5. Commit after each phase.
