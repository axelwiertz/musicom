# Musicom Deduplication & Consolidation Plan

## Goal
Remove duplicate code, merge parallel implementations, absorb the `ai/` subtree into flat packages, and establish a single source of truth for each concept. Flat packages (`structures/`, `generators/`, `rules/`, etc.) are canonical.

## Decisions Made
- **Ecosystem**: Flat packages are canonical; `ai/` subtree is fully absorbed then removed
- **Time model**: Absolute ticks only; beat-based `ai/core/structures.py` is deprecated
- **Scope**: Full absorption of unique `ai/` features into flat packages

---

## Phase 1: Immediate Fixes (no structural changes)

### 1.1 Fix broken syntax
- **File**: `transformers/pitch.py` line 5
- **Issue**: `def pitch_shift:(pitch: int, semitones: int) -> int:` — invalid syntax
- **Action**: Fix to `def pitch_shift(pitch: int, semitones: int) -> int:` or remove if unused

### 1.2 Update outdated documentation
- **Files**: `README.md`, `QUICK_REFERENCE.md`
- **Issue**: Both still describe `MusicEvent.duration` as broken when `start_tick == 0` (fixed in Phase 2)
- **Action**: Remove the "known quirk" notes; document correct behavior

### 1.3 Remove deprecated re-export files
These files contain legacy code "kept for reference" and cause confusion:
- `converters/audio.py` → re-exports `sound/synthesis/granular.py`
- `converters/daw_bridge.py` → re-exports `sound/render/vst.py`
- `ai/generators/vocal_synth.py` → re-exports `sound/synthesis/vocal.py`

**Action**: Delete all three files. Update any imports that reference them.

---

## Phase 2: Remove Empty/Stub Modules

### 2.1 Remove or complete stubs
| File | Status | Action |
|------|--------|--------|
| `transformers/matrix.py` | Empty (3 lines) | Delete |
| `transformers/embellishment.py` | Pass-through only | Delete or implement |
| `visualization/dashboard.py` | Stub | Delete or implement |
| `converters/musicxml.py` | Stub (writes empty XML) | Delete; `ai/io/musicxml_io.py` has real implementation |
| `ai/generators/rhythm.py` | Minimal stubs | Features migrated in Phase 4, then delete |

---

## Phase 3: Consolidate Duplicates

### 3.1 DAWClockBridge
- **Canonical**: `sound/sync/clock.py`
- **Duplicate**: `ai/integration/daw_sync.py` (different API)
- **Action**: Delete `ai/integration/daw_sync.py`. Update `AGENTS.md` to reference `sound/sync/clock.py`.

### 3.2 Audio Analysis (PitchDetector, BeatTracker, OnsetDetector, ChromaExtractor)
- **Canonical**: `sound/analysis/` (pitch.py, rhythm.py, chroma.py)
- **Duplicate**: `ai/io/audio_analysis.py`
- **Action**: 
  - Check if `ai/io/audio_analysis.py` has unique features (e.g., `PitchDetector.to_phrase()`)
  - If yes, migrate unique features to `sound/analysis/pitch.py`
  - Delete `ai/io/audio_analysis.py`

### 3.3 Pitch Conversion
- **Location 1**: `sound/utils/pitch.py` (pure math)
- **Location 2**: `converters/pitch.py` (uses librosa)
- **Action**: 
  - Consolidate into `sound/utils/pitch.py`
  - If librosa functions are needed, add them to `sound/utils/pitch.py` with lazy import
  - Delete `converters/pitch.py`
  - Update imports

### 3.4 Markov Generators (3 implementations)
- **Location 1**: `generators/chain.py` — `MarkovChainGenerator` (MusicGenerator subclass)
- **Location 2**: `generators/markov.py` — `MarkovGenerator` (standalone)
- **Location 3**: `ai/generators/melody.py` — `MarkovChainGenerator` (different API)
- **Action**:
  - Keep `generators/chain.py` as canonical (follows MusicGenerator pattern)
  - Check if `generators/markov.py` or `ai/generators/melody.py` have unique features
  - Migrate unique features to `generators/chain.py`
  - Delete `generators/markov.py` and `ai/generators/melody.py`

### 3.5 Euclidean Rhythm
- **Location 1**: `generators/rhythm.py` — `euclidian()` function
- **Location 2**: `sound/generators/event_core.py` — `EuclideanCore` class
- **Action**:
  - Keep `generators/rhythm.py` (simpler, used in tests)
  - If `EuclideanCore` has unique features, migrate to `generators/rhythm.py`
  - Remove `EuclideanCore` from `sound/generators/event_core.py` or keep as internal implementation detail

### 3.6 Counterpoint Rules
- **Location 1**: `rules/counterpoint.py` — `Counterpoint` class
- **Location 2**: `ai/rules/theories.py` — `CounterpointRules` class
- **Action**:
  - Keep `rules/counterpoint.py` as canonical
  - Check if `CounterpointRules` has unique features
  - Migrate unique features to `rules/counterpoint.py`
  - Delete `ai/rules/theories.py` (or keep non-counterpoint parts if any)

### 3.7 Harmonic Rules
- **Location 1**: `rules/progression.py` — `PatternMovement`, `Scale7ChordDegree`
- **Location 2**: `ai/rules/harmonic_rules.py` — `FunctionalHarmony`
- **Action**:
  - Keep `rules/progression.py` as canonical
  - Migrate unique features from `FunctionalHarmony` (e.g., cadence detection) to `rules/progression.py`
  - Delete `ai/rules/harmonic_rules.py`

### 3.8 Transformers
- **Location 1**: `transformers/` (canon, pitchsequence, negative_harmony, etc.)
- **Location 2**: `ai/transformers/` (pitch_transformers.py, rhythm_transformers.py)
- **Action**:
  - `ai/transformers/pitch_transformers.py`: Check for overlap with `structures/unit.py` (MusicUnit already has transpose, invert, retrograde, augment). If redundant, delete. If unique, migrate to `transformers/`.
  - `ai/transformers/rhythm_transformers.py`: Contains unique features (SwingTransformer, Quantizer, RhythmicDisplacement). Migrate to `transformers/`.
  - Delete `ai/transformers/` after migration.

### 3.9 MIDI Export (3 paths)
- **Path 1**: `workflows/unitmatrix_composer.py` — `UnitMatrixComposer.to_midi()` (RECOMMENDED)
- **Path 2**: `converters/midi_converter.py` — `export_midi()`
- **Path 3**: `ai/io/midi_io.py` — `MIDIWriter.write()`
- **Action**:
  - Keep `UnitMatrixComposer.to_midi()` as the one true path
  - Check if `converters/midi_converter.py` or `ai/io/midi_io.py` have unique features
  - If `export_midi()` is used internally by `UnitMatrixComposer.to_midi()`, keep it as internal
  - Delete `ai/io/midi_io.py`
  - Document that users should use `UnitMatrixComposer.to_midi()`

---

## Phase 4: Migrate Unique ai/ Features

### 4.1 Set Theory Analysis
- **Source**: `ai/rules/set_theory.py` — `SetTheoryAnalyst`
- **Target**: `rules/set_theory.py` (new file)
- **Action**: Move file, update imports, delete `ai/rules/set_theory.py`

### 4.2 Voice Leading Rules
- **Source**: `ai/rules/voice_leading_rules.py` — `VoiceLeadingRules`
- **Target**: `rules/voice_leading.py` (new file)
- **Action**: Move file, update imports, delete `ai/rules/voice_leading_rules.py`

### 4.3 Rhythm Transformers
- **Source**: `ai/transformers/rhythm_transformers.py` — SwingTransformer, Quantizer, RhythmicDisplacement, RhythmicAugmentation
- **Target**: `transformers/rhythm.py` (new file)
- **Action**: Move file, update imports, delete `ai/transformers/rhythm_transformers.py`

### 4.4 MusicXML I/O
- **Source**: `ai/io/musicxml_io.py` — MusicXMLReader, MusicXMLWriter
- **Target**: `converters/musicxml.py` (replace stub)
- **Action**: Replace stub with real implementation, delete `ai/io/musicxml_io.py`

### 4.5 Grid Visualizer
- **Source**: `ai/utils/visualizer.py` — `render_grid()`, `write_grid_visualization()`
- **Target**: `visualization/grid.py` (new file)
- **Action**: Move file, update imports, delete `ai/utils/visualizer.py`

### 4.6 Check for other unique features
Review remaining `ai/` files for unique functionality not covered above:
- `ai/core/tet_system.py` — PitchClass, Interval, Scale, Key, TimeSignature
  - Check if these overlap with `structures/pitch.py` or `structures/pitchclass.py`
  - If unique and useful, migrate to `structures/`
  - If redundant, delete
- `ai/rules/theories.py` — HarmonyRules, StructuralRules (Hindemith, Fux, Schoenberg)
  - Check for unique features after counterpoint extraction
  - If unique, migrate to `rules/`
  - If redundant, delete
- `ai/integration/bridge.py` — LibraryBridge (unified interface for music21, musicpy, pypianoroll)
  - Check if useful or if `converters/` already covers this
  - If unique, migrate to `converters/` or `utilities/`
  - If redundant, delete
- `ai/integration/converters.py` — Music21Converter, MusicPyConverter, PyPianorollConverter
  - Check if these overlap with existing converters
  - If unique, migrate to `converters/`
  - If redundant, delete
- `ai/utils/` — constants.py, validators.py, helpers.py, exceptions.py, logging_config.py
  - Check for unique utilities
  - Migrate useful ones to `utilities/`
  - Delete redundant ones

---

## Phase 5: Deprecate ai/core/structures.py

### 5.1 Decision
- `ai/core/structures.py` (Note, Chord, Phrase, Score) uses beat-based time model
- This is incompatible with the canonical absolute-ticks model
- **Action**: Deprecate entirely

### 5.2 Migration Path
- Check if any code uses `ai/core/structures.py`
- If yes, provide migration guide: "Use MusicEvent/MusicUnit with absolute ticks"
- If the beat-based API is useful for high-level composition, consider adding a wrapper around MusicUnit that accepts beats and converts to ticks internally (out of scope for this plan; can be Phase 6)

### 5.3 Action
- Delete `ai/core/structures.py`
- Delete `ai/core/tet_system.py` if not migrated in Phase 4.6
- Delete `ai/core/` directory

---

## Phase 6: Remove ai/ Subtree

After Phases 1-5:
- All unique features have been migrated
- All duplicates have been removed
- `ai/` should only contain deprecated/empty files

**Action**:
- Delete entire `ai/` directory
- Remove `musicom_compat.pth` if it only exists for `ai/` compatibility
- Update `pyproject.toml` if needed
- Update `AGENTS.md` to remove all `ai/` references

---

## Phase 7: Fix Inconsistencies

### 7.1 Generator Return Types
- **Issue**: Some generators return `List[MusicUnit]`, others return single `MusicUnit`
- **Action**: Standardize on `List[MusicUnit]` per `MusicGenerator.generate()` abstract method
- Update all generators to conform

### 7.2 Validation APIs
- **Issue**: `UnitMatrix.validate_timing()` returns `bool`, `UnitMatrixComposer.validate()` returns `Tuple[bool, str]`
- **Action**: Keep both (different use cases), but document clearly

### 7.3 Import Path Cleanup
- Remove `sys.path.insert(0, ...)` hacks from `workflows/unitmatrix_composer.py`
- Fix circular imports in `structures/pitchclass.py` if possible

---

## Phase 8: Update Tests

### 8.1 Fix skipped test
- `test_pitch_class_set_and_graph` is skipped due to broken `MusicPitchGrid()` construction
- **Action**: Fix `structures/pitch.py` or update test to provide required `pitches` arg

### 8.2 Implement stub tests
- `test_rules.py` has empty stubs (test_pattern, test_movement both pass)
- **Action**: Implement actual tests or delete stubs

### 8.3 Update imports in tests
- After `ai/` removal, update any test imports that reference `ai/` modules

### 8.4 Run full test suite
```bash
cd /opt/data/repos/musicom
/opt/data/micromamba/envs/musicom/bin/python -m pytest tests/ -q
```
- All tests must pass (except documented skips)

---

## Phase 9: Update Documentation

### 9.1 README.md
- Remove outdated "known quirk" about `MusicEvent.duration`
- Remove references to `ai/` subtree
- Clarify the one true workflow: `UnitMatrixComposer`
- Update feature list to reflect consolidated structure

### 9.2 QUICK_REFERENCE.md
- Remove outdated "known quirk" about `MusicEvent.duration`
- Update import examples to remove `ai/` references

### 9.3 AGENTS.md
- Remove all `ai/` references
- Update file paths for migrated features (e.g., "Grid visualizer — visualization/grid.py")
- Update "Missing-link features" section
- Remove "Companion workflows" references to `ai/` if any

### 9.4 DOC.md
- Review and update if it references `ai/` or outdated features

---

## Phase 10: Validation

### 10.1 Run tests
```bash
cd /opt/data/repos/musicom
/opt/data/micromamba/envs/musicom/bin/python -m pytest tests/ -q
```
- All tests must pass

### 10.2 Verify golden file
```bash
cd /opt/data/repos/musicom
/opt/data/micromamba/envs/musicom/bin/python -m pytest tests/test_harness_golden.py -v
```
- GOLDEN_SHA256 must remain stable (no unintended MIDI format changes)

### 10.3 Check imports
```bash
cd /opt/data/repos/musicom
/opt/data/micromamba/envs/musicom/bin/python -c "from workflows.unitmatrix_composer import UnitMatrixComposer; from structures import UnitMatrix, MusicUnit, MusicEvent; print('OK')"
```
- Core imports must work

### 10.4 Verify no ai/ references
```bash
cd /opt/data/repos/musicom
grep -r "from ai\." --include="*.py" .
grep -r "import ai\." --include="*.py" .
```
- Should return no results (except in git history)

### 10.5 File size verification
- After any MIDI/WAV writes during testing, assert file size > 40 bytes

---

## Execution Order

1. **Phase 1** — Immediate fixes (low risk, high value)
2. **Phase 2** — Remove empty/stub modules (low risk)
3. **Phase 3** — Consolidate duplicates (medium risk, high value)
4. **Phase 4** — Migrate unique ai/ features (medium risk)
5. **Phase 5** — Deprecate ai/core/structures.py (medium risk)
6. **Phase 6** — Remove ai/ subtree (high impact, requires Phases 3-5 complete)
7. **Phase 7** — Fix inconsistencies (low risk)
8. **Phase 8** — Update tests (required after Phases 3-6)
9. **Phase 9** — Update documentation (required after Phases 3-6)
10. **Phase 10** — Validation (required)

**Commit after each phase** per AGENTS.md agent execution contract.

---

## Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| Breaking existing code that imports from `ai/` | Search all imports before deletion; update all references |
| Losing unique features during migration | Review each `ai/` file carefully; migrate before deleting |
| GOLDEN_SHA256 changes | Do not modify MIDI export logic; only consolidate duplicates |
| Circular imports after consolidation | Test imports after each phase; fix immediately |
| Test failures after consolidation | Run tests after each phase; fix before proceeding |

---

## Out of Scope

- Adding new features (this is a cleanup plan)
- Changing the time model (absolute ticks is canonical)
- Adding a beat-based high-level API (can be Phase 6+ if needed)
- Refactoring `sound/` package structure (already well-organized)
- Completing TODO items in `transformers/canon.py`, `rules/progression.py`, etc. (separate plan)

---

## Success Criteria

- [ ] No duplicate implementations (each concept has one canonical location)
- [ ] `ai/` directory removed
- [ ] All unique features from `ai/` migrated to flat packages
- [ ] All tests pass (except documented skips)
- [ ] GOLDEN_SHA256 unchanged
- [ ] Documentation updated (README, QUICK_REFERENCE, AGENTS.md)
- [ ] No broken syntax or empty modules
- [ ] Import paths work without `sys.path` hacks
- [ ] Single ecosystem: flat packages only
