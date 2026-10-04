---
name: musicom
description: Compose, produce and analyze music through the musicom engine — a transparent, zero-drift UnitMatrix pipeline (forward MIDI generation + reverse analysis) designed to run together with a Hermes agent. Use when the user wants to write music, render MIDI to audio, or reverse-engineer an existing MIDI file into key/chords/grid.
version: 1.0.0
license: MIT
---

# Musicom — composition + production + analysis

A transparent educational framework: every stage is an explicit, inspectable
transformation. Two symmetric pipelines:

- **Forward** — `compose()` → `validate()` (zero-drift gate) → MIDI + provenance
  → `produce(SP-001/SP-011/…)` → WAV/OGG.
- **Reverse** — `analyze_midi()` → key / roman progression / Forte sets /
  high-contrast grid / voice-leading violations.

## The spine (one call each)

```python
from workflows.musicom_workflow import compose, produce
from workflows.analyze import analyze_midi

r = compose(style="pop", key="C", bpm=120)      # -> r.midi_path, r.provenance_path
p = produce(r.midi_path, method="SP-011")       # Karplus-Strong (no SoundFont needed)
a = analyze_midi(r.midi_path)                    # -> a.key, a.roman_progression, a.grid
```

Low-level control uses `UnitMatrixComposer`, in this exact order:
`create_matrix → add_voice → add_section → fill_voice_section → validate → to_midi`.

## Hard rules

1. **Zero-drift** — `validate()` MUST return `True` before export. Every voice's
   section units must end at the section's full tick length.
2. **Flat imports** — `from structures import UnitMatrix`, never
   `from musicom import …` and never relative `..` imports.
3. **Verify-don't-trust** — `assert os.path.getsize(path) > 40` after every
   MIDI/WAV write (empty files appear as 16–22 B).
4. **Purity** — importing the method registry / rules must not load
   `musicpy`/`music21`. Use mido READ-only for MIDI parsing.
5. **One env** — resolve python/fluidsynth/soundfont via `utilities.env`.

## Read next

1. `AGENTS.md` — canonical guide (wins over README on conflict).
2. `docs/AGENT_MANUAL.md` — the code-agent manual.
3. `docs/patterns.md`, `docs/methods.md`, `docs/instruments.md` — domain tables.
4. `hermes_agent/` — Hermes runtime KB.
5. `REPO_MAP.md` — where everything lives.
