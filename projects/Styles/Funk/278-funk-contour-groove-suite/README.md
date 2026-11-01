# 278-funk-contour-groove-suite

**Funk × Contour Theory (CTC) — extension of 220-funk-contour-groove.**

- **Style:** Funk
- **Method:** 095 Contour Theory Composition (abstract layer)
- **Key:** E minor pentatonic (E G A B D) = pc {4,7,9,11,2}
- **Tempo:** 100 BPM · 4/4 · 480 TPB
- **Form:** Intro → ThemeA → ThemeB → Variation → Development → Bridge → Climax → Outro (8 × 4 = **32 bars**)
- **Voices:** Trumpet (56) · Tenor Sax (66) · Clavi (7) · Contrabass (43) · Drums (ch9)

## What changed vs. source (220)

Extended 24 → **32 bars** (6 → 8 sections) and layered **7 documented variation
techniques**: inversion, retrograde, augmentation, diminution, register shift,
counterline, and a D-pedal bridge palette color. Preserved the source identity
(genre, key, tempo, contour vocabulary, palettes, 5-voice funk texture).

## Files

- `MIDI/278-funk-contour-groove-suite-phase1.mid` — raw whole-tone contour draft
- `MIDI/278-funk-contour-groove-suite-perfect.mid` — grid-locked (compositional truth)
- `MIDI/278-funk-contour-groove-suite-humanized.mid` — style-profile + instrument-DNA humanization
- `Audio/*-perfect.ogg|.wav` + `Audio/*-humanized.ogg|.wav` — mastered render (Funk LUFS −13, −1 dBTP)
- `Analysis/` — verify.json, grid_visualization.txt, summary.json, render_stats.json
- `index.html` — dashboard

## Verification (all primary gates PASS)

- Zero-drift: 5 voice tracks = 61440 ticks (perfect & humanized)
- Perfect: 0 off-grid · 0 out-of-scale · 0 out-of-chord (656 pitched onsets)
- Humanized: 586 off-grid (>0 proves jitter) · 0 out-of-scale · 2 out-of-chord (bar-boundary jitter)
- Phase1: 224 raw notes, 221 off-grid (raw draft keeps its character), 0 out-of-scale-by-design