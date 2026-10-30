# 274-groove-sieve-rework

Rework of **080-groove-sieve** (Groove / Method 025 **Xenakis Sieve Theory**).
Rebuilt from scratch through the canonical `UnitMatrixComposer` engine.

## Identity (preserved from source)

- **Genre:** Groove
- **Key:** G natural minor (G A Bb C D Eb F)
- **Tempo:** 110 BPM · 4/4 · 480 TPB (bar 1920, 8th 240, 16th 120)
- **Method:** 025 Xenakis Sieve — sieve C = A (mod 8, res {0,2,5}) ∩ B
  (mod 7, res {0,1,4}), period lcm(8,7) = 56, offsets `[0,8,18,21,29,32,42,50,53]`
- **Voices:** Lead (Soprano Sax 65) · Horns (Brass 61) · Rhodes (EP 4) ·
  Bass (EB 33) · Counter (Strings 48, chorus only) · Drums (ch9)

## What changed (redesign → longer + more varied)

- Source was 24 bars / 6 sections. New form is **32 bars / 8 sections**.
- Each section gets its **own harmonic region** (no bar-0 tonic collapse).
- **5 variation techniques**: register transposition (+12), inversion, retrograde,
  augmentation, density-rise + counterline.

## Two-phase architecture

- **Phase 1** (`MIDI/…-phase1.mid`): raw sieve walk, single voice, off-grid
  onsets, unquantized pitches, no harmony.
- **Phase 2** (`MIDI/…-perfect.mid`): grid snap → scale quantize →
  chord-tone quantize (own bar) → voice-leading → 6-voice arrangement.
- **Dual-version**: `-perfect` (grid-locked) + `-humanized` (style groove +
  per-instrument DNA, seeded).

## Files

- `MIDI/274-groove-sieve-rework-{phase1,perfect,humanized}.mid` (+ provenance)
- `Audio/274-groove-sieve-rework-{phase1,perfect,humanized}.ogg/.wav`
- `Analysis/{grid_visualization{,_phase1}.txt, verify.json, render_report.json}`
- `compose.py`, `verify.py`, `render.py`, `composition_meta.json`
- `README.md`, `REPORT.md`, `index.html`

## Verification

- Perfect: 6 tracks, 0 off-grid, 0 scale violations, 0 chord violations.
- Humanized: off-grid > 0 (jitter ran), 0 scale violations.
- See `REPORT.md` and `Analysis/verify.json` for exact numbers.
