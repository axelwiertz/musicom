# 253-pop-moepc-pareto

Pop composition — Method 098 **Multi-Objective Evolutionary Pareto Composition
(MOEPC)**, two-phase architecture.

- **Key**: C major (ionian) · **Tempo**: 112 BPM · 4/4
- **Form**: intro-verse-chorus-bridge-outro (4+8+8+4+4 = 28 bars)
- **Method**: NSGA-II evolves 4 conflicting objectives (harmonic quality,
  melodic conjunctness, rhythmic coherence, voice independence) → Pareto front
  supplies the macro-form (smooth/balanced/active archetypes).
- **Instrumentation**: Piano lead, Synth Pad, Electric Bass, Glockenspiel
  sparkle, Drum Kit (ch9).
- **Harmony**: I-V-vi-IV pop bestseller, C major.

## Artifacts

- `MIDI/253-pop-moepc-pareto-phase1.mid` — raw NSGA-II draft (single piano,
  unquantized, no harmony)
- `MIDI/253-pop-moepc-pareto-perfect.mid` — grid-locked rules-processed
- `MIDI/253-pop-moepc-pareto-humanized.mid` — same + seeded humanization
- `Audio/*.ogg` — listening renders (perfect + humanized mastered to −9 LUFS,
  phase1 raw)
- `Analysis/summary.json`, `Analysis/grid_visualization.txt`,
  `Analysis/render_stats.json`
- `REPORT.md` — full record (method, harmony, audits, humanization, render)

## Verification

- Grid audit: perfect **0 off-grid** / humanized **> 0 off-grid** (humanizer ran)
- Harmony: **0 out-of-scale**, **0 out-of-chord** (both versions)
- Zero-drift: 5 tracks @ 53760 ticks (equal)
