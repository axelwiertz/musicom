# 312-groove-sieve-suite

Extension of **274-groove-sieve-rework** (which reworked 080-groove-sieve).
Groove / Method 025 **Xenakis Sieve Theory**.

## Identity (preserved from source)

- **Genre:** Groove
- **Key:** G natural minor (G A Bb C D Eb F)
- **Tempo:** 110 BPM · 4/4 · 480 TPB (bar 1920, 8th 240, 16th 120)
- **Method:** 025 Xenakis Sieve — C = A (mod 8, res {0,2,5}) ∩ B
  (mod 7, res {0,1,4}), period lcm(8,7) = 56, offsets `[0,8,18,21,29,32,42,50,53]`
- **Voices:** Lead (Soprano Sax 65) · Horns (Brass 61) · Rhodes (EP 4) ·
  Bass (EB 33) · Counter (Strings 48) · Drums (ch9)

## What changed (extension → longer + more varied)

- Source was 32 bars / 8 sections. New form is **40 bars / 10 sections** (N+2).
- **8 variation techniques** (3 new vs source): transposition (+12), inversion,
  retrograde, augmentation, **diminution** (PreChorus), **register shift −12**
  (Break), **canon imitation** (Chorus2 counterline echoes lead −12 @ +1 beat),
  density-rise + counterline (Chorus).
- Each section keeps its own harmonic region (per-bar degrees; section midpoint
  roots span G·C·D·F·Eb·Bb — no bar-0 tonic collapse).

## Two-phase architecture

- **Phase 1** (`MIDI/…-phase1.mid`): raw sieve walk, single voice, off-grid
  onsets, unquantized chromatic wander, no harmony.
- **Phase 2** (`MIDI/…-perfect.mid`): grid snap (16th) → scale quantize →
  chord-tone quantize per bar (`t // BAR`) → voice-leading → 6-voice arrangement.
- **Dual-version**: `-perfect` (grid-locked) + `-humanized` (style groove +
  per-instrument DNA, seeded).

## Verification

- Perfect: 6 tracks, 0 off-grid, 0 scale violations, 0 chord violations.
- Humanized: off-grid > 0 (jitter ran), 0 scale violations.
- See `REPORT.md` and `Analysis/verify.json` for exact numbers.

## Files

- `MIDI/312-groove-sieve-suite-{phase1,perfect,humanized}.mid` (+ provenance)
- `Audio/312-groove-sieve-suite-{phase1,perfect,humanized}.ogg/.wav`
- `Analysis/{grid_visualization{,_phase1}.txt, verify.json, render_report.json}`
- `compose.py`, `verify.py`, `render.py`, `composition_meta.json`
- `README.md`, `REPORT.md`, `index.html`
