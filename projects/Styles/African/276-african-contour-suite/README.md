# 276-african-contour-suite

African polyrhythmic composition — an **extension** of `105-african-contour`
(Method 095 Contour Theory Composition, abstract layer). Longer form, more
variation, a new counterline voice.

## Concept

- **Style:** African (kalimba lead + flute call/response + marimba interlock + djembe)
- **Method:** 095 CTC — melodies designed as contour *shapes* (CSeg rank
  sequences + CAS direction strings), transformed under {I,R,RI}, realized onto
  the C-major pentatonic.
- **Key:** C major pentatonic (C D E G A) · **BPM:** 112 · 4/4 · 480 TPB
- **Form:** Intro | Theme | Variation | Development | Bridge | Climax | Outro |
  Coda (8 × 4 = 32 bars)

## Two-phase architecture

1. **Phase 1** (`-phase1.mid`) — raw whole-tone contour, single Kalimba,
   off-grid, no harmony.
2. **Phase 2** (`-perfect.mid`) — 16th-grid snap → pentatonic + per-bar palette
   quantize → voice-leading → 6-voice African texture.
3. **Humanized** (`-humanized.mid`) — style + per-instrument DNA jitter.

## Variation techniques

Retrograde · Inversion · register shift (+12) · rhythmic augmentation ·
rhythmic diminution · Pan Flute counterline · density rise + thinning.

## Files

- `MIDI/` — phase1 / perfect / humanized (+ provenance sidecars)
- `Audio/` — FluidSynth → LUFS master → Opus OGG (all three versions)
- `Analysis/` — grid visualizations, verify.json, render_report.json
- `compose.py` — generates both phases via `UnitMatrixComposer` + `export_dual`
- `verify.py` — mido read-only audit
- `render.py` — FluidSynth CLI → master → OGG
