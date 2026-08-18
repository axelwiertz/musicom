# Changelog

All notable changes to Musicom are documented here. The project follows a
phase-based development history (see git log for full detail).

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

## [0.1.0] — 2024-2026

### Phase 5 — Companion workflows
- Paradigm comparison (`workflows/paradigm_compare.py`): stochastic vs rules vs nature.
- Provenance (`workflows/provenance.py`): sha256 + classification sidecars.

### Phase 4 — Missing-link features
- Grid visualizer (`visualization/grid.py`) — █/░ density timeline.
- Vocal guide synth (`sound/synthesis/vocal.py`) — formant-filtered guide vocals.
- DAW clock bridge (`sound/sync/clock.py`) — MIDI clock/MTC.

### Phase 3 — Green test suite
- Zero-drift golden-file harness (`tests/test_harness_golden.py`) — byte-identical
  deterministic MIDI export regression net.

### Phase 2 — Bugfixes
- Fixed 5 Phase-1 bugs (MusicEvent.duration, Counterpoint crossing, generator
  event construction, cross-platform DEFAULT_PATH).

### Phase 1 — Docs truth
- API docs now match real code.

### Phase 0 — Packaging
- Editable install + pyproject.toml, flat package layout.

### Sound production (surveillance replication)
- Synthesis: modal, granular, phase-mod, vocal, additive, bowed, mass-spring,
  west-coast, binaural, polysynth, scale-quantizer, voice-allocator, polyrhythm.
- Effects: reverb, FDN reverb, filter, vowel filter, tape delay, multiband,
  quantize mod, mastering (LUFS/DynamicEQ/StereoImager/Limiter).
- Modular: node graph, math modulators, patch loader, chaos CV.
- Generators: event cores (Markov/Stochastic/Euclidean/LSystem/WeightedRandom),
  dice, ratchet sequencer.
- Tuning: just intonation, ratio lattice.
- Render: fluidsynth, VST (DawDreamer), pipeline (stems).

## License

MIT — see [LICENSE](LICENSE).
