---
name: musicom-onboarding
description: Use when starting fresh with the musicom engine — first-time environment setup, the canonical forward compose→produce and reverse analyze recipes, and the zero-drift/verify-don't-trust gates. Pairs the codebase with a Hermes agent.
version: 1.0.0
author: Musicom Agent
license: MIT
metadata:
  hermes:
    tags: [musicom, onboarding, workflow, composition, analysis]
    related_skills: [musicom-composer, music-project-workflow]
---

# Musicom Onboarding

Musicom is a transparent composition + production + analysis library: every
stage is an explicit, inspectable transformation (no black-box prompt→audio).
It runs together with a Hermes agent.

## Canonical recipes

### Forward — compose → produce
```python
from workflows.musicom_workflow import compose, produce

r = compose(style="pop", key="C", bpm=120)      # -> r.midi_path, r.provenance_path
p = produce(r.midi_path, method="SP-011")       # Karplus-Strong (no SoundFont)
```

### Reverse — analyze
```python
from workflows.analyze import analyze_midi

rep = analyze_midi(r.midi_path)
print(rep.key, rep.roman_progression, rep.grid)
```

### Low-level — full control
```python
from structures import MidiInstrument
from workflows.unitmatrix_composer import UnitMatrixComposer, create_note_unit

composer = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
composer.create_matrix(num_voices=2, num_sections=1)
composer.add_voice("Lead", program=MidiInstrument.FLUTE, channel=0)
composer.add_voice("Bass", program=MidiInstrument.PIANO, channel=1)
composer.add_section("A", bars=1)
composer.fill_voice_section("Lead", "A", create_note_unit(72, 1920))
composer.fill_voice_section("Bass", "A", create_note_unit(48, 1920))
ok, msg = composer.validate()            # MUST be True
composer.to_midi("outputs/out.mid")
```

Order is fixed: `create_matrix → add_voice → add_section →
fill_voice_section → validate → to_midi`.

## Environment

Resolve binaries/paths through `utilities.env` (`repo_root`, `python_bin`,
`fluidsynth_bin`, `soundfont_path`) — never hardcode host paths. Flat imports:
`from structures import …` (never `from musicom import …`).

## Hard rules

1. `validate()` MUST pass before `to_midi()` (zero-drift invariant).
2. Size-assert artifacts: `assert os.path.getsize(p) > 40`.
3. Keep imports pure — don't eagerly load `musicpy`/`music21`; use mido
   READ-only for MIDI parsing.
4. Outputs go to `./outputs/` (gitignored); the living corpus is `projects/`.

## Read next

`AGENTS.md` → `docs/AGENT_MANUAL.md` → `REPO_MAP.md`.
