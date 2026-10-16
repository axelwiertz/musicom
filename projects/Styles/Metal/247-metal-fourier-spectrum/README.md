# 247 — Metal Fourier Spectrum

**Method 113 — Pitch-Class Fourier Spectrum Composition (PCFSC)** · layer **abstract** · paradigm Rules-Based.

A 55-second metal piece composed entirely in Amiot's Fourier space over ℤ₁₂:
each section's harmony is a pitch-class *pool* whose **magnitude spectrum
|f(k)|** is the chord/scale *quality*, and whose **Fourier phase** is the
tonic *position*. The composition is a designed trajectory through quality
space — natural minor (HOME) → harmonic minor (LIFT) → octatonic dim-lattice
(TENSE) → natural minor (HOME).

| Field | Value |
|---|---|
| Style | Metal |
| Form | head-solos-head (Head1 · Solo1 · Solo2 · Head2) |
| Key | E minor (tonic pc 4) |
| Tempo | 140 BPM · 4/4 · 480 TPB |
| Length | 32 bars · ~55 s |
| Ensemble | Lead guitar · Rhythm guitar · Electric bass · Drum kit |

## Files

- `MIDI/247-metal-fourier-spectrum.mid` — phase-2 (rules-processed) full texture
- `MIDI/247-metal-fourier-spectrum-phase1.mid` — phase-1 raw Fourier-pool draft
- `Audio/*.wav` — FluidSynth renders (mastered to −11 LUFS)
- `Audio/*.ogg` — Opus listening renders
- `Analysis/summary.json` — spectra, tension curve, audits, humanization
- `Analysis/grid_visualization.txt` — high-contrast onset grid
- `REPORT.md` — full record (primary)
- `compose.py` / `render.py` — generator + render/master pipeline

## What to listen for

- **Head** (0:00): locked E-minor riff — diatonic quality, |f5|=|f7|=2+√3
  (the maximally-even maximum), stable tonic anchor.
- **Solo1**: harmonic-minor leading tone (D♯) drives the V–i pull; 16th-note
  ascending sweeps (the phase drift / transposition walk).
- **Solo2**: half-whole octatonic shred — energy only at Fourier k=4,8 (the
  diminished-seventh lattice); descending dim7 sweeps over double-kick.
- **Head (return)**: the riff returns, phase resolves to the opening anchor
  (HOME).

See `REPORT.md` for the full Fourier spectra, tension curve, and all
verification numbers.
