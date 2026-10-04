# examples/ — runnable snippets

Two kinds of examples live here:

## Curated (guaranteed to run — smoke-tested by `tests/test_examples_smoke.py`)

| File | Shows |
|---|---|
| `compose_demo.py` | forward spine: `compose()` → `produce(SP-001)` + `produce(SP-011)` |
| `compose_simple.py` | minimal `UnitMatrixComposer` → MIDI in ~12 lines |
| `produce_simple.py` | SP-011 (no-dep) vs SP-001 (SoundFont, opt-in) |
| `transform_simple.py` | transpose / retrograde / negative harmony |
| `analyze_simple.py` | reverse: MIDI → key / chords / grid |

Run any curated example from the repo root:

```bash
python examples/compose_simple.py
```

Outputs land in `./outputs/` (gitignored).

## Scratch (exploratory — not guaranteed to run)

Everything else under `examples/` is historical scratch / one-off experiments.
They may depend on host paths, removed modules, or external binaries. Use them
for reference only; the curated set above is the supported surface.
