# Changelog

All notable changes to Musicom are documented here. This changelog is
organized by development era, mirroring the phases visible in the git history
(310+ commits, 2024-05 → present). Each era groups the logical work behind the
commit clusters.

The project is stable and testable since the 2026-07 hardening pass
(Phase 0-5); earlier eras are retained for historical accuracy.

## [Unreleased]

### Added
- Interval-based composition primitives (`structures/intervals.py`): Forte
  interval-class vectors, Hindemith Series 2 hierarchy, Bartók-style interval
  expansion, delta encoding.
- Interval generators: `generators/interval_chain.py` (transposition-invariant
  Markov), `generators/interval_lsystem.py` (fractal interval melodies).
- Just-intonation ratio lattice (`sound/tuning/ratio_lattice.py`).
- Ratchet step sequencer (`sound/generators/ratchet_seq.py`) — SuperOS-808-style.
- Digital chaos CV (`sound/modular/chaos_cv.py`) — Sofia2/Leibniz-style.
- Sound methods overview (`hermes_agent/sound-methods-overview.md`).
- 31 new tests (183 total).

### Changed
- Corrected `ai.utils.visualizer` → `visualization.grid` import across docs/skills.
- Hindemith rank corrected to authentic Series 2 (12 ranks, tritone = 11).

## [0.1.0] — 2024-05 → present

### 2026-08 — Sound synthesis & modular gear
- `sound/` package: synthesis (modal, granular, phase-mod, vocal, additive,
  bowed, mass-spring, west-coast, binaural, polyrhythm, **polysynth**
  multi-engine), effects (reverb, FDN reverb, filter, vowel filter, tape delay,
  multiband, quantize mod, mastering LUFS/DynamicEQ/StereoImager/Limiter),
  modular (node graph, math modulators, patch loader, chaos CV), tuning
  (just intonation), generators (event cores, dice, ratchet sequencer),
  render (fluidsynth, VST/DawDreamer, stereo pipeline), analysis.
- **Bowed-string physical modeling** (SP-024).
- **Surveillance gear replication** (2026-08): 12 HIGH/MEDIUM targets,
  ratchet sequencer, chaos CV, methods registry.
- 3 versatile compositions/examples (pop 16-bar, flute + ProductionChain DSP,
  stereo pipeline regression fixes).

### 2026-08 — Structure rebuild
- `hermes_agent/` knowledge base added (composition + sound-production
  workflows, method registry, surveillance findings, decision log).
- Flat package structure finalized (top-level dirs = packages), imports
  cleaned up, legacy `ai/` subtree migrated.

### 2026-07 — Hardening (Phase 0-5)
- **Phase 0**: packaging — `pyproject.toml`, editable install, flat layout.
- **Phase 1**: docs truth — API docs now match real code.
- **Phase 2**: 5 known bugs fixed + regression tests (MusicEvent.duration,
  Counterpoint crossing, generator event construction, cross-platform config).
- **Phase 3**: green suite (183 tests) + zero-drift golden-file harness.
- **Phase 4**: missing-link features — grid visualizer, vocal guide, DAW clock.
- **Phase 5**: companion workflows — paradigm compare + provenance sidecars.

### 2026-06 — Repo consolidation
- `musicom_ai` + `musicom_research` consolidated into the main repo
  (brings genetics, tonal-model research, agent workflows together).
- Onboarding skill + environment validation.
- Markov generator implemented; `.pyproject` config fixed.

### 2026-01 — Pitch theory & examples
- `MusicPitchClassPattern` → `MusicPitchClassSet` refactor (backwards
  compatible); `PitchClassSet` module.
- Architecture review document; 3-voice example w/ debug report & review;
  `BYT` project; composition examples & docs.

### 2025-11 → 2026-01 — Core model formed
- **UnitMatrix** = `np.array`, `MusicProject`, `MusicSection`, `MusicVoice`,
  `MusicUnit` = pitch + time; `MusicEvent` as event sequence.
- Patterns unified: **scales are patterns**; pitch-class patterns separated
  from absolute pitches; rhythm patterns; pattern hierarchy & diatomic
  constants merged.
- Converters: music21 (score/stream/note/pattern), musicpy, MIDI file,
  pypianoroll.
- Generators & transformers decoupled from structures; genetic algorithm;
  timegrid, meter & timescale; composition via unit + matrix operations.
- Theory classes: harmony, numeric theory, 12TET & diatonic class hierarchy,
  Helix classes, time circle & transformation.

### 2025-08 → 2025-10 — Theory & generation focus
- Reference library, chord library, harmony progressions.
- `class Composition`, genetic music creation, stable genetic generation.
- MusicVoice, Composing, soundlayer, theory classes, transformations.
- `Create intervalnetwork.py`, `network.py` (voice-leading graphs, in
  `research/`).

### 2025-05 → 2025-08 — Routines & transformations
- Creation/Library routines, note & chord transformation, rhythm creation,
  percussion, reference library, model (analysis).
- Rhythm deleted → reorganized; song files renamed to `library.py`;
  simplification & integration pass.

### 2024-05 → 2025-04 — Origins (exploration)
- Early prototype: collecting parts & samples, MIDI loading, pieces & DAW
  sync, rules/datastructure notes, scratch files, musicpy archiving.
- Mostly low-signal `Sync` commits — exploratory groundwork, no stable API
  yet.

## License

MIT — see [LICENSE](LICENSE).