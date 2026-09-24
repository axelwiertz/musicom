# 104-celtic-subset-variations

Celtic rework of **085-celtic-subset-walk**. Longer (32 bars), more varied (7
variation techniques), fully re-verified through the canonical `UnitMatrixComposer`
engine.

- **Key** Ab major · **BPM** 96 · 4/4 · 480 TPB
- **Form** 8 sections × 4 bars = 32 bars
  `Intro | ReelA | ReelB | Lift | Bridge | ReelA2 | ReelC | Outro`
- **Method** ABS-002 Subset Walker + ABS-001 tension curve + method-006 cadence
- **Voices** Marimba (lead), French Horn (pad), Cello (pad), Violin (counterline),
  Bassoon (root counter), Double Bass (roots), Drum Kit (ch9)

## Files

- `MIDI/104-celtic-subset-variations.mid` — phase 2 (rules), full texture
- `MIDI/104-celtic-subset-variations-phase1.mid` — phase 1 (raw subset-walk draft)
- `Audio/*.ogg` / `Audio/*.wav` — FluidSynth renders
- `index.html` — dashboard (VoltAgent styling)
- `REPORT.md` — full audit, walk, variation, verification detail
- `Analysis/grid_visualization.txt`, `summary.json`, `verify.json`, `render_stats.json`

## Verification (phase 2)

7 voice tracks @ 61440 ticks (zero-drift) · 1105 pitched onsets · **0 off-grid ·
0 scale violations · 0 chord violations**.
