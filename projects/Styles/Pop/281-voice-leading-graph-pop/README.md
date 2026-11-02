# 281 — Voice-Leading Graph Pop

**Nightly composition · 2026-11-02 · Method 011 Voice-Leading Graph Search (concrete, Rules-Based)**

| | |
|---|---|
| Genre / style | Pop |
| Method | 011 — Voice-Leading Graph Search (Neo-Riemannian, diatonic) |
| Layer | concrete |
| Form | intro–verse–chorus–bridge–outro (4/8/8/4/4 = 28 bars) |
| Key | C major (ionian) |
| Tempo | 118 BPM |
| Voices | Lead=Piano(1), Harmony=Rhodes(4), Pad=Synth Pad(88), Bass=Electric Bass(33), Drums=Drum Kit(ch9) |

**Concept.** A weighted walk over the diatonic Neo-Riemannian voice-leading graph
(R relative / L leading-tone exchange / plagal / authentic edges) generates the
28-bar chord sequence, steered section-by-section toward cadence anchors. The
raw draft is the audible *voice-leading line* — the minimal-movement voice note
at each chord change plus a triad arpeggio — emitted as a single off-grid,
chromatically-jittered voice (Phase 1). Phase 2 applies the musicom rules stack:
weight-aware tiered pitch quantization (strong = scale+chord, weak = scale),
16th grid snap, dedup, parallel-5th/octave voice-leading break, tagged chromatic
approach ornaments, and a full 5-voice pop texture.

## Files

- `MIDI/281-voice-leading-graph-pop-phase1.mid` — raw generative draft (off-grid, unquantized)
- `MIDI/281-voice-leading-graph-pop-perfect.mid` — grid-locked rules layer (0 off-grid)
- `MIDI/281-voice-leading-graph-pop-humanized.mid` — style pop + per-instrument DNA
- `Audio/*.ogg` — mastered listening renders (perfect + humanized + phase1)
- `Analysis/` — grid visualizations, pitch audit, render report, summary
- `REPORT.md` — full method/audit/humanization/mastering record

See `REPORT.md` for the complete technical record.
