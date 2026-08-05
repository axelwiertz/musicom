# Architecture Decision Log

Why the musicom repo looks the way it does. Newest first.

## 2026-08: Deduplication & ai/ subtree absorption

**Decision**: Flat packages canonical; `ai/` subtree fully absorbed then deleted.
**Plan**: `.kilo/plans/1785873858229-musicom-deduplication-consolidation.md`
**Migrations**:
- `ai/utils/*` → `utilities/` (constants, exceptions, validators, music_helpers, logging)
- `ai/rules/set_theory.py` → `rules/set_theory.py`
- `ai/rules/voice_leading_rules.py` → `rules/voice_leading.py`
- `ai/transformers/rhythm_transformers.py` → `transformers/rhythm.py`
- `ai/utils/visualizer.py` → `visualization/grid.py`
- `ai/io/musicxml_io.py` → real `converters/musicxml.py`

**Deleted duplicates**: converters/audio.py, converters/pitch.py,
converters/daw_bridge.py, generators/markov.py, ai/core/structures.py
(beat-based model incompatible with absolute ticks).

**Result**: 42 tests passing, musicom_compat.pth removed, no ai.* imports remain.

## 2026-08: sound/ package structure (Option A — by function)

**Decision**: Separate `sound/` top-level package, organized by function.
**Structure**: synthesis/ analysis/ render/ effects/ generators/ sync/ utils/
**Rationale**: Matches how audio engineers think; clear boundaries;
effects/ ready for growth; render/pipeline.py extracts hardcoded
FluidSynth+ffmpeg from example scripts into reusable API.
**Backward compat**: re-export shims existed at old locations, removed in
the dedup pass (ai/generators/vocal_synth.py etc.).

## 2026-08: Mastering tools added

**Decision**: Implement mastering DSP in sound/effects/mastering.py per
ITU-R BS.1770-4 and MusicTech mastering workflow.
**Tools**: LUFSMeter, DynamicEQ, StereoImager, Limiter, MasteringChain,
normalize_to_lufs (streaming targets).

## 2026-08: Stem rendering

**Decision**: Production pipeline renders individual track WAVs (stems)
alongside the full mix via RenderPipeline.render_stems().
**Rationale**: Per-track audio needed for DAW import and per-track DSP.

## Standing rules

- Time model: absolute ticks only (zero-drift invariant)
- Engine stays generic; style-specific content lives in projects, never in the engine
- Output artifacts go to /opt/data/projects/Research/outputs/<project>/, never into the repo
- Commit after each logical phase; verify-don't-trust (assert file size > 40 bytes)
