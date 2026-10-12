# 237 — Kuramoto Chorale Extended (rework of 069)

**Date:** 2026-10-12 (nightly rework agent)
**Source:** 069-kuramoto-chorale (Experimental, Method 038 KOPS)
**Decision:** REDESIGN (audit failed) — rebuild from scratch, preserve identity.

## Source identity (preserved)

- **Method:** 038 Kuramoto Oscillator Phase Synchronization (KOPS) — Nature-Led
- **Key:** F dorian | **BPM:** 92 | **Instrumentation:** SATB chorale
  (Flute / StringEnsemble / StringEnsemble / Bass) — now + Drums (ch9)
- **Core motif:** the synchronization transition — coupling K rises per
  section (desync → phase lock), order parameter r drives velocity.

## Audit result (069)

| # | Standard | Result |
|---|----------|--------|
| 1 | Engine (UnitMatrixComposer) | PASS |
| 2 | Zero-drift | PASS (4 tracks × 15360) |
| 3 | Rhythm-grid sync | **FAIL — 124 off-grid onsets** |
| 4 | Track setup (≥4 voices) | PASS |
| 5 | Two-phase artifacts | PASS |
| 6 | provenance.json + index.html | **FAIL — no index.html** |

Root cause of #3: the raw KOPS phase-wrap onsets (`round(beat*480)`) were
exported directly into the Phase-2 MIDI without snapping to the 120/240 grid.
Phase-2 scale discipline was already clean (0 violations). `i–iv–VII` was
mislabeled "Bbm" in the source — diatonic thirds yield **Bb major** (dorian IV).

## What changed (fixes)

1. **Grid snap:** every onset snapped to the 120-tick (16th) grid, then deduped
   by `(start_tick, pitch)` keeping longest. Off-grid count now **0**.
2. **Per-bar chord quantization:** every note quantized to its own bar's chord
   (`t // BAR`), each section its own progression. Chord violations **0**.
3. **Voice-leading optimization:** `VoiceLeadingRules.optimize_voice_leading`
   + inversion-rotation fix → parallel/hidden fifths **0** (was 10 canonical).
4. **Dashboard + provenance:** index.html + project provenance.json added.

## New form (longer + more varied)

18 bars / 8 sections (source had 8 bars / 4 sections):

| Section | Bars | K | Degrees | Variation |
|---------|------|---|---------|-----------|
| Intro | 2 | 0.5 | i | (sparse) |
| Verse A | 2 | 0.8 | i → IV | baseline motif |
| Verse A' | 2 | 1.2 | IV → VII | **augmentation + register shift (+12)** |
| Chorus | 3 | 1.5 | VII → IV → i | **density rise (drums in)** |
| Bridge | 2 | 2.0 | i → III | **inversion + modal color (Ab)** |
| Verse B | 2 | 2.5 | v → VII | **retrograde** |
| Chorus' | 3 | 3.2 | IV → VII → i | **octave doubling** |
| Outro | 2 | 4.0 | i | **diminution (fade)** |

Midpoint-chord roots per section: i, IV, VII, IV, III, VII, VII, i — no
bar-0 tonic collapse.

## Verification (phase 2)

```
voice tracks = 5, zero-drift = True, len = 34560 ticks
pitched onsets (excl ch9) = 290
off-grid = 0        (MUST be 0)
scale violations = 0  (MUST be 0)
chord violations = 0  (MUST be 0)
size = 4224 bytes (> 40)
```

Phase 1 (raw draft): 76 onsets, off-grid 68, scale-viol 19 — intentional
pre-rules signature, single voice.

Audio: Fluidsynth FluidR3_GM → WAV (peak 0.87, RMS −17 dB, silence 10.9%) →
Opus OGG 48k (54 s incl. reverb tail).
