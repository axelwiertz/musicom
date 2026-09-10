# Pop Ballad — HITL Project

Human-in-the-loop evolution project for a dramatic pop ballad.

## Concept

- **Genre**: Pop ballad (minor-aeolian drama)
- **Key**: D (aeolian) — i–VI–III–VII harmonic regions
- **Tempo**: 72 BPM (slow ballad)
- **Form**: Intro(4) → Verse(8) → Chorus(8) → Bridge(4) → Outro(4) = 28 bars, ~93 s
- **Voices**: Lead (Flute), Pad (Piano), Bass (Double Bass), Arp (Clarinet), Drums (Drum Kit)

## Phase 1 — Composition (MIDI)

Framework via **Path C middle-out** (`workflows/paths.py`), then per-part
method swaps on the SAME framework + base patterns:

| Part | Bars | Comp method | Effect |
|---|---|---|---|
| Framework | all | 001 Skeleton-First + 012 Euclidean bass + 018 Schillinger density | spine |
| Intro | 0-4 | 001 skeleton | sparse held tones |
| Verse | 4-12 | 004 Prosodic Narrative | lyrical contour |
| Chorus | 12-20 | 011 Voice-Leading Graph | nearest-chord leaps, octave lift |
| Bridge | 20-24 | 023 Tendency Masking | tension walk, wide intervals |
| Outro | 24-28 | 013 Inversion/Retrograde | retrograde motif, resolve |

Per-section harmonic regions (ballad arc): Intro i-VI, Verse full aeolian
cycle, Chorus lift on III-VII-i-VI, Bridge peak on VII, Outro resolve to i.

Zero-drift validated (`validate()` gate), provenance sidecar, grid viz.

## Phase 2 — Production (Audio)

Different production method per VOICE (on stems) AND per SECTION (on bus):

| Voice (stem label) | SP method |
|---|---|
| Lead (Recorder) | SP-032 FDN reverb wash (wet .3) |
| Pad (Bright Acoustic Piano) | SP-020 SVF lowpass 4.5 kHz |
| Bass (Contrabass) | SP-020 SVF lowpass 700 Hz (sub body) |
| Arp (Clarinet) | SP-019 Chebyshev waveshape (drive 1.5) |
| Drums (Drums) | SP-008 multiband compressor (punch) |

| Section | SP method |
|---|---|
| Intro | SP-020 lowpass 1200 Hz (muffled build-in) |
| Verse | dry (lyric clarity) |
| Chorus | SP-021 stereo widen 1.35× |
| Bridge | SP-032 FDN wash (size .85, wet .4) |
| Outro | SP-020 lowpass 800 Hz + fade to 0 |

Master: `normalize_to_lufs(-14)` → `Limiter(-1 dB)` LAST.

## Verification

```
LUFS -14.01  peak 0.891  silence 3.2%
```

- MIDI: `MIDI/pop-ballad-hitl.mid` (3292 B, zero-drift)
- Audio: `Audio/pop-ballad-hitl.wav` (16.5 MB) + `.ogg` (670 KB)
- Stems: `Audio/stems/track*_*.wav`
- Grid: `Analysis/grid_phase1.txt`

## HITL hook

Next: run `workflows.hitl.run_hitl_round()` over this anchor to evolve
density/offset variants; human pick recorded in `evolution.json`.
