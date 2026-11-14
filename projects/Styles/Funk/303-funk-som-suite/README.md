# 303-funk-som-suite

Extended rework of `098-funk-som` (Funk / Method 075 Self-Organizing Map
Composition). F minor, 104 BPM, 4/4. 8 sections × 4 bars = 32 bars.

## What it is

A two-phase SOM-C funk suite: Phase 1 is a raw 4×4 toroidal Self-Organizing
Map trajectory walk (unquantized pitch + rhythm, single trumpet). Phase 2 is
musicom rules post-processing (16th-grid snap, per-bar chord-tone quantization,
voice-leading cap) expanded into a 5-voice Funk arrangement: Lead Trumpet,
Tenor Sax counterline, Piano comping, Double Bass slap groove, Drum Kit (ch9).

## Variation techniques

1. Transposition +4th / subdominant Bb region (Verse2)
2. Register shift +1 octave (Chorus2)
3. Retrograde contour (Bridge)
4. Augmentation ×2 durations (Breakdown)
5. Density contrast (Breakdown sparse vs Chorus full)
6. Sax offbeat counterline

## Files

- `MIDI/303-funk-som-suite-phase1.mid` — raw generative draft (pre-rules)
- `MIDI/303-funk-som-suite-perfect.mid` — grid-locked rules layer
- `MIDI/303-funk-som-suite-humanized.mid` — humanized layer
- `Audio/303-funk-som-suite-perfect.ogg` / `-humanized.ogg` — mastered listening renders
- `index.html` — dashboard · `provenance.json` — identity + technique record
- `REPORT.md` — full report · `Analysis/verification.json` — read-only audit

## Regenerate

```bash
cd /opt/data/projects/Styles/Funk/303-funk-som-suite
$MUSICOM_PYTHON compose.py      # MIDI (phase1 + perfect + humanized)
$MUSICOM_PYTHON render.py       # FluidSynth -> master -> OGG
$MUSICOM_PYTHON verify.py       # read-only audit asserts
```
