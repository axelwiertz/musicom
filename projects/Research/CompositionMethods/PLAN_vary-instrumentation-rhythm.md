# PLAN — Vary instrumentation & rhythm progression by style (and method)

Date: 2026-11-11 · Status: **BUILT (P0 + P1 + P2)** · Author: agent / Axel

## Problem (why every piece sounds the same)

All engine composition funnels into ONE chokepoint and TWO constants:

1. **Rhythm chokepoint** — `workflows/cell_engine.py::ROLE_FILLERS` is a fixed
   dict of 5 style-agnostic recipes:
   `lead=8th-arp / pad=sustained / bass=1&3 / arp=16ths / drums=grid`.
   `compose()` (musicom_workflow.py:584-612), `compose_middle_out()`, and the
   `DefaultMethod` all route through it. There is **no style parameter and no
   method parameter** anywhere in the fill path.

2. **Instrumentation constant** — the default voice stack is hardcoded in TWO
   places, both `("Lead","Flute"), ("Pad","Piano"), ("Bass","Double Bass"),
   ("Arp","Clarinet"), ("Drums","Drum Kit")`:
   - `build_framework()` (paths.py:407-414) — ignores `STYLE_REGISTRY` entirely.
   - `compose()` fallback (musicom_workflow.py:490-492).
   `STYLE_REGISTRY.default_voices` exists but covers **6 of 58 genre dirs**
   (pop/bossa_nova/flamenco/jazz/techno/chanson). The other 52 fall back to the
   pop stack.

3. **Method is never wired** — Phase-4 contract `CellMethod.resolve_role` /
   `generate` exists (method_contract.py), but `registry_method()` raises
   `NotImplementedError` for all 9 implemented methods (adapters = P1, unbuilt).
   So `DefaultMethod` is the only filler and no method ever drives a cell.

Existing-but-unused assets (avoid duplication): `orchestrator.py`
(`ORCHESTRATION_PRESETS`, `ROLE_PROFILES`, `SECTION_DYNAMICS`,
`allocate_registers`), the `PALETTES` concept in the instruments skill, and the
per-genre rhythm/density recipes in `genre-composition-patterns` (four-on-floor,
shuffle, 12-beat compás, log-drum, oom-pah, swing ride) — all prose, none wired.

## Target architecture

Make the fill path **style-aware** and **method-aware** at the cell level:

```
style ──► INSTRUMENTATION(style)  ──► voice stack (role→instrument)
style ──► RHYTHM(style)           ──► per-role filler recipes
method ─► CellMethod(adapter)     ──► resolve_role + generate(raw notes)
        └──► realize_spine.realize() ──► snap/harmonize/landmark ──► MusicUnit
```

## Tiers

### P0 — Style-aware rhythm recipes (kills "same rhythm progression")

- Add `workflows/style_rhythm.py` — `RHYTHM_BY_STYLE: {style: {role: recipe}}`.
  Content sourced from genre-composition-patterns (techno 4-on-floor, blues/
  jazz shuffle + swing ride, flamenco 12-beat compás, pop backbeat, amapiano
  log-drum + rolling shaker, chanson oom-pah, ambient drone/no-drums, minimal
  sparse).
- Thread `style` into `CellContext`; replace the bare `ROLE_FILLERS[role]`
  dispatch with `style_fillers(style)[role]`.
- **Byte-neutral gate**: `style_fillers("pop")` MUST return the current 5
  fillers verbatim so `GOLDEN_SHA256` + `ABS_GOLDEN_SHA256` stay green.
  New styles add new recipe sets; pop is the pinned legacy default.
- Verify: compose pop + 3 new styles, assert different per-role onset grids
  (mido onset audit), zero-drift intact, golden hashes unchanged.

### P1 — Style-aware instrumentation (kills "same instrumentation")

- Expand `STYLE_REGISTRY.default_voices` (or add `INSTRUMENTATION_BY_STYLE`
  backed by `orchestrator.ORCHESTRATION_PRESETS`/`PALETTES`) to cover all 58
  genre dirs — one role→instrument palette per style.
- Wire `build_framework()` + `compose()` to consume it (they currently
  hardcode / ignore the registry).
- Range-check every palette (existing pitfall): assert each role's notes sit in
  `instrument_registry.by_name(inst).range_min..max`; the 4-voice styles
  (techno/bossa/flamenco/jazz) must not break the 5-voice assumption.

### P2 — Method drives (a part of) the piece

- Build the P1 method adapters so `registry_method(id)` returns a real
  `CellMethod` for the 9 implemented methods (001/002/003/010/012/018/023/040/079).
- Per-section method table (style→section→method, already sketched for pop:
  Intro=023, Verse=002+011, Chorus=026, Bridge=032, Outro=018) so ONE method
  fills ONE section — the "method for part of the piece" requirement.
- Route cells through `CellComposer.fill_cell(method=...)` +
  `realize_spine.realize()` (raw → snap → landmark), replacing the
  `default_resolve_role` position-mapping with `method.resolve_role(ctx)`.

## Sequencing & adoption

- P0 and P1 are independent (rhythm vs instrumentation). P2 builds on P0
  (method emits raw notes the spine realizes inside a style's rhythm context).
- Nightly cron (`1fc3fd65d359`) writes bespoke compose.py per night that
  hand-codes per-style instruments — it is NOT the sameness source; the ENGINE
  default path is. Adoption follows the standing preference: wire the smallest
  blast radius first (audit/gate), defer full rewire.

## Verification (real numbers, no file-size asserts)

1. Off-grid onset audit per voice per style (drums beat-aligned, swing-aware).
2. Per-voice pitch-class ∈ key, chord-tone audit (0 violations).
3. Zero-drift readback: all note tracks equal length.
4. Golden-hash gates (`test_harness_golden.py`, `test_realize_bridge.py`) green
   for the pop default after every tier.

## Status: BUILT (2026-11-11)

All three tiers landed. New/changed modules:

| Module | Change |
|---|---|
| `workflows/style_rhythm.py` | NEW — `RHYTHM_BY_STYLE` (11 families) + `style_fillers()` |
| `workflows/style_instruments.py` | NEW — 36 palettes, 84 aliases + `instrument_palette()` |
| `workflows/method_adapters.py` | NEW — CellMethod adapters for 9 implemented methods |
| `workflows/cell_engine.py` | `CellContext.style` + style-aware `fill_cell` |
| `workflows/method_contract.py` | style-aware `DefaultMethod` + `registry_method` → adapters |
| `workflows/musicom_workflow.py` | `compose(style=…, section_methods=…)` + `SECTION_METHODS` + `_fill_method_cell` |
| `workflows/paths.py` | `build_framework` consumes `instrument_palette(style)` |
| `tests/test_style_variation.py` | NEW — 8 gates (rhythm roles, pop byte-neutral, palette resolve/range/genre-dir) |
| `tests/test_method_contract.py` | updated stale "adapter pending" test → adapters now resolve |

Verification (measured):
- Golden-hash gates green (pop byte-identical) — `GOLDEN_SHA256` +
  `ABS_GOLDEN_SHA256` unchanged.
- Full suite: **769 passed, 1 skipped**.
- Real-number onset audit (7 styles, `humanize=False`): distinct drum grids —
  pop `0/240/480…`, techno four-on-floor, jazz swing `0/320/480/800…`,
  flamenco compás `0/320/480/800/960/1120…`, ambient `[]` (no kit), metal
  double-kick `0/120/240/360…`, blues swing. All zero-drift.
- Distinct instrumentation: pop `[flute,piano,double_bass,clarinet]`,
  techno `[synth_voice,synth_pad,synth_bass_1,clavi]`, jazz
  `[trumpet,piano,double_bass,jazz_guitar]`, etc.
- `compose(section_methods=SECTION_METHODS["pop"])` → zero-drift, 6303 B MIDI.

Note: `compose_middle_out()` (Path C) still owns its 5 hardcoded `fill_*`
funcs — migrating it onto `CellComposer` remains a separate TODO (unchanged).
