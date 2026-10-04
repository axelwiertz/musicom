# AGENT_MANUAL.md — using musicom as a code agent

A concise operating manual for code agents (Claude, Hermes, etc.) working with
the musicom codebase. Read `AGENTS.md` first (it is canonical on conflict);
this manual turns that reference into runnable recipes.

## 1. Repo map (short form)

- **Engine** (ships in the wheel): `structures/`, `workflows/`, `generators/`,
  `rules/`, `sound/`, `transformers/`, `converters/`, `analysis/`,
  `visualization/`, `utilities/`, `legacy/`.
- **Docs**: `docs/` + root `*.md` (`AGENTS.md`, `QUICK_REFERENCE.md`,
  `CLAUDE.md`, `SKILL.md`, `REPO_MAP.md`).
- **Corpus**: `projects/` (educational compositions, instrument tree, research).
- **Skill**: `skills/` + `hermes_agent/`.

See `REPO_MAP.md` for the full table.

## 2. Import rules + environment

- Flat layout — top-level dirs ARE the packages:
  ```python
  from structures import MusicUnit, MusicEvent, UnitMatrix, MidiInstrument
  from workflows.unitmatrix_composer import UnitMatrixComposer, create_note_unit
  from workflows.musicom_workflow import compose, produce
  from workflows.analyze import analyze_midi
  ```
- ❌ Never `from musicom import …` (alias namespace only) and never relative
  `..` imports.
- One env: resolve binaries/paths via `utilities.env` (`repo_root`,
  `python_bin`, `fluidsynth_bin`, `soundfont_path`) — never hardcode
  `/opt/data/...`.

## 3. Forward recipe (compose → produce)

```python
from workflows.musicom_workflow import compose, produce

r = compose(style="pop", key="C", bpm=120)      # -> r.midi_path, r.provenance_path
assert r.midi_path and r.provenance_path

p1 = produce(r.midi_path, method="SP-011")      # Karplus-Strong (no SoundFont)
p2 = produce(r.midi_path, method="SP-001")      # FluidSynth (needs a SoundFont)
```

Low-level (full control), in this exact order:

```python
composer = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
composer.create_matrix(num_voices=2, num_sections=1)      # 1. shape
composer.add_voice("Lead", program=MidiInstrument.FLUTE, channel=0)  # 2. voices
composer.add_section("A", bars=1)                          # 3. sections
composer.fill_voice_section("Lead", "A", create_note_unit(72, 1920))  # 4. fill
ok, msg = composer.validate()                              # 5. zero-drift gate
assert ok, msg
composer.to_midi("out.mid")                                # 6. export
```

## 4. Reverse recipe (analyze)

```python
from workflows.analyze import analyze_midi

rep = analyze_midi("out.mid")                # headless, mido READ-only
print(rep.key, rep.mode)                     # "C", "major"
print(rep.roman_progression)                 # ["I", "V", "vi", "IV", ...]
print(rep.forte_names)                       # ["3-11", ...]
print(rep.grid)                              # █/░ high-contrast timeline
print(rep.violations)                        # voice-leading issues
rep = analyze_midi("out.mid", to_score=True) # opt-in: rep.score = music21 stream
```

## 5. MD reading order

`AGENTS.md` → `docs/patterns.md` → `docs/methods.md` → `hermes_agent/*.md` →
instrument `instrument.md` → `docs/instruments.md`.

## 6. Gates (do not skip)

1. `validate()` MUST return `True` before any `to_midi()`.
2. Size-assert every artifact: `assert os.path.getsize(p) > 40` (empty MIDI/WAV
   appears as 16–22 B).
3. Purity: importing the method registry / `rules` must not load
   `musicpy`/`music21` (pinned by `tests/test_generator_lazy_imports.py`).
4. Golden hashes: `tests/test_harness_golden.py` (`GOLDEN_SHA256`) and
   `tests/test_realize_bridge.py` (`ABS_GOLDEN_SHA256`) pin byte-identical
   export — update only for an *intentional* format change.

## 7. Output locations

- Public contributions / examples write to `./outputs/` (gitignored).
- The living corpus (`projects/`) is nightly-synced by the host cron; heavy
  artifacts (`*.wav`, `*.log`, `outputs/`) stay gitignored.

## 8. Failure table

| Symptom | Cause | Fix |
|---|---|---|
| MIDI/WAV is 16–22 B | empty/corrupt export | regenerate + size-assert `> 40` |
| `validate()` "Track length mismatch" | unequal voice section lengths | pad via `_unit_from_events(events, section_len)` |
| `No SoundFont found` | SP-001 with no sf2 on disk | use SP-011 (pure Python) or `discover_soundfont()` |
| `music21` display call hangs/crashes headless | `analysis.score_analyze` plots | use `analyze_midi`, never `score.plot()` headless |
| eager `musicpy`/`music21` import | registry loads heavy deps | keep lazy; see purity gate |
| `from musicom import …` fails | alias namespace | use flat `from structures import …` |

## 9. Testing

```bash
cd /opt/data/repos/musicom
/opt/data/micromamba/envs/musicom/bin/python -m pytest tests/ -q
```

Key files: `test_harness_golden.py` (zero-drift regression net),
`test_realize_bridge.py` (ABS byte-neutrality), `test_generator_lazy_imports.py`
(import purity), `test_docs_smoke.py` (documented snippets must run),
`test_analyze_reverse.py` (reverse path round-trip).
