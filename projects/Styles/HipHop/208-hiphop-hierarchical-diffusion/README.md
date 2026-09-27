# 208-hiphop-hierarchical-diffusion

**HipHop × Method 010 Hierarchical Diffusion** — autonomous nightly composition (2026-09-27).

- **Style:** HipHop (boom-bap backbeat, sub bass, chord stabs, swung 16ths)
- **Method:** 010 Hierarchical Diffusion (concrete, Stochastic) — multi-level
  top-down step-wise expansion from macro plans to MIDI events.
- **Key:** A natural minor · **BPM:** 90 · **Form:** 8 sections × 4 bars = 32 bars
- **Progression:** i–VI–III–VII (Am–F–C–G), Bridge F–C–G–Am

## Voices (instrument registry)

| Voice | Instrument | Program | Channel |
|---|---|---|---|
| LeadHook | Piano | 1 | 0 |
| KeysPad | Church Organ | 19 | 1 |
| SubBass | Double Bass | 43 | 2 |
| SparkleStab | Celesta | 8 | 3 |
| Drums | Drum Kit | 0 | 9 |

## Two-phase architecture

- **Phase 1** (`MIDI/...-phase1.mid`): raw hierarchical-diffusion draft — single
  voice, unquantized onsets + Ornstein-Uhlenbeck drift-diffusion chromatic pitch.
- **Phase 2** (`MIDI/....mid`): musicom rules post-processing — 16th-grid onset
  quantization + chord-tone snap + full 5-voice hip-hop texture.

## Verification (all green)

- Grid audit: **0 off-grid** (775 onsets all on 16th grid).
- Harmony audit: **0 out-of-scale / 0 out-of-chord** (359 pitched notes).
- Zero-drift: `validate()` PASSED both phases (5 tracks × 61440 ticks).

## Files

- `MIDI/` — phase1 + phase2 MIDI (+ provenance sidecars)
- `Audio/` — Opus OGG + WAV renders (phase1 + phase2)
- `Analysis/` — `grid_visualization.txt`, `summary.json`
- `compose.py`, `render_audio.py` — generators
- `REPORT.md` — full record
- `index.html` — dashboard
