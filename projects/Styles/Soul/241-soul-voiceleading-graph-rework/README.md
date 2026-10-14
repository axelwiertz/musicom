# 241 — Soul Voice-Leading Graph Rework

Nightly rework of `084-soul-voiceleading-graph` (Soul, Method 011). Source
audit failed two standards (missing compose.py + missing provenance/index), so
the piece was **rebuilt from scratch** through the canonical
`UnitMatrixComposer` workflow, preserving identity and extending the form.

## Identity

- **Genre**: Soul
- **Key**: D minor (aeolian) — pcs {2,4,5,7,9,10,0}
- **Tempo**: 92 BPM, 4/4, 480 TPB (bar = 1920 ticks)
- **Form**: 32 bars = 8 sections × 4 bars (source was 24 = 6 sections)
- **Band**: Tenor Sax (66) · Rhodes (4) · Violin (41) · Acoustic Guitar (25) ·
  Electric Bass (33) · Drums (ch9)
- **Method**: 011 Voice-Leading Graph Search — weighted random walk over a
  D-aeolian tonal-function graph

## Listen / Use

- **Full mix**: `Audio/241-soul-voiceleading-graph-rework.ogg`
- **Raw draft (phase 1)**: `Audio/241-soul-voiceleading-graph-rework-phase1.ogg`
- **MIDI**: `MIDI/*.mid` (phase1 + phase2, zero-drift validated)
- **Dashboard**: `index.html`

## Variation techniques (6)

register-shift-down+thin · transposition (+m3) · retrograde · augmentation ·
inversion · diminution — plus identity + recapitulation.

## Verification

`Analysis/verification.json` — phase 2: **0 off-grid, 0 out-of-scale,
0 out-of-chord**, 6 tracks × 61440 ticks (zero-drift).

## Files

- `compose.py` — two-phase composition (engine-only)
- `Analysis/` — grid visualization, summary, verification, render stats
- `Audio/` — WAV + OGG renders (FluidR3_GM.sf2 via discover_soundfont)
