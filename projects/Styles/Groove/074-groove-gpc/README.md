# 074-groove-gpc

Groove style / Method 061 **Gaussian Process Composition (GPC)**.

## Concept

A groove study where the lead melody is a **posterior draw from a Gaussian
Process prior** — smooth RBF kernel (phrase-length memory horizon) plus a
periodic bar-cycle component (ostinato). Anchor points pull the curve toward
tonic per section, giving a macro-form arc (Intro wander → Verse → Chorus
strong tonic → Outro settle).

- **Key:** G natural minor
- **BPM:** 106
- **Bars:** 24 (6 sections × 4 bars)
- **Form:** Intro | Verse | Chorus | Verse2 | Chorus2 | Outro
- **Progression:** i–III–iv–V (×2) | i–iv–V–i | i–V–i–VI | i–III–iv–V | i–V–iv–i

## Voices

| Voice | Program | Role |
|-------|---------|------|
| Lead | 80 Square Lead | GP-sampled quantized melody |
| Horns | 61 Brass Section | Syncopated offbeat stabs (2& / 4&) |
| Rhodes | 4 Electric Piano | 3rd+7th sustained comp |
| Bass | 33 Electric Bass | Funk octave pulse + 16th push |
| Drums | 0 (ch9) | Kick 1&3, snare 2&4, hats 8ths, chorus claps+ride |

## Two-Phase

- **Phase 1** (`MIDI/074-groove-gpc-phase1.mid`): raw GP posterior sample,
  single voice, continuous unquantized semitone curve, no harmony. Sounds
  like a wandering, smoothly-connected solo line with no tonal center.
- **Phase 2** (`MIDI/074-groove-gpc.mid`): chord-tone quantization per bar +
  voice-leading leap cap + full groove texture. The same contour becomes a
  tonal, danceable lead locked to the groove.

## Files

- `MIDI/074-groove-gpc.mid`, `MIDI/074-groove-gpc-phase1.mid`
- `Audio/074-groove-gpc.ogg/.wav`, `Audio/074-groove-gpc-phase1.ogg/.wav`
- `Analysis/grid_visualization.txt`, `Analysis/summary.json`, `Analysis/silence_check.py`

## Verification

- `validate()` PHASE1: OK, PHASE2: OK (zero-drift gate passed)
- Preflight: compliant (exit 0)
- Silence check: 3.8% (only tail pad), healthy per-second RMS
