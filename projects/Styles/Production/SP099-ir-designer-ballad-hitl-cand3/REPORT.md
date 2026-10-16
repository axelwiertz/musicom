# SP-099 Impulse Response Designer — ballad-hitl-cand3

**Job:** random-style production (SP methods) — LAYER-ALIGNED
**Date:** 2026-10-16  **Seed:** 20261016

## Selection

| Field | Value |
|---|---|
| Registry source | `workflows.musicom_workflow.SP_METHODS` (48 registered) |
| Method | `SP-099` |
| Module | `sound.effects.ir_designer` |
| Description | Impulse Response Designer — 10 algorithmic IR synthesis techniques (Convolution Playground-style) |
| Layer | ABSOLUTE — one convolution-reverb IR applied to the whole piece |
| Recent excluded (7d) | SP-006, SP-026, SP-028, SP-032, SP-074, SP-085, SP-098, SP-103 |
| Pool size | 40 |
| Well-formed candidates | 235 / 345 |

**Source composition:** `Styles/Pop/ballad-hitl/HITL/round0/candidates/cand3-pViol-ldX-ar4-pdpuls-drful-bXo0.mid`
- HITL round-0 candidate (variant 3, role "texture+bed"), D aeolian, 72 BPM, 4/4, TPB 480, 28 bars (~93 s)
- Voices: Lead (Violin 40), Pad (Piano 1), Bass (Cello 42), Arp (Viola 41), Drums (ch9)
- Progression: i–VI–III–VII (Dm–Bb–F–C), section-rotated: Intro i–VI, Verse i–VI–III–VII, Chorus III–VII–i–VI, Bridge VII–VI, Outro i–VI
- spec: arp_on=[Verse, Chorus], arp_rate=4, pad_style=pulse, drum_level=full

## PRE-FLIGHT AUDIT (3-rule gate)

| Rule | Before | After | Verdict |
|---|---|---|---|
| Grid sync (16th = 120 ticks) | 0 off-grid | 0 | PASS |
| Harmony — in scale (D aeolian) | 1 out-of-scale | 0 | PASS |
| Harmony — chord tone of bar | 100 out-of-chord | 0 | PASS |
| Zero-drift (equal track lengths) | 52560/53700/53760/38160/45960 | 53760 ×5 | PASS |

**Verdict: FAIL → reworked → PASS.**

### Rework applied (two-phase, engine-based — `UnitMatrixComposer`)

- Phase-1 sidecar: `MIDI/cand3-…-phase1.mid` (raw original preserved).
- Phase-2 (`Scripts/rework_cand3.py`):
  - **Chord-tone quantize** every pitched voice (Lead/Pad/Arp) to its bar's
    triad from the bass-root region map (100 pitch changes, register/octave
    preserved, nearest-octave mapping).
  - **Out-of-scale fix:** bridge lead Eb (pc 3) @ bar 22 → D (chord tone of Bb).
  - **Zero-drift:** every voice padded to 28 bars = 53760 ticks (terminal
    landmark); `validate()` → True.
  - **Channel collision fix:** the original put all 4 pitched voices on
    channel 0 (violin/piano/cello/viola), so FluidSynth's last program-change
    wins and the multitimbral render collapses. Rework assigns distinct
    channels: Lead ch0, Pad ch1, Bass ch2, Arp ch3, Drums ch9.
- Re-audit: 0 off-grid / 0 out-of-scale / 0 out-of-chord / all 5 note tracks
  53760 ticks. PASS.

Chord-tone sets per bar (D aeolian triads): Dm {D,F,A}, Bb {Bb,D,F},
F {F,A,C}, C {C,E,G}.

## Method parameters (SP-099)

| Param | Value |
|---|---|
| Recipe | `reverb` (Schroeder-style stochastic noise, exponential decay) |
| RT60 | 2.0 s (ballad hall) |
| IR duration | 3.0 s |
| Wet gain | 0.35 |
| Dry gain | 0.80 |
| Convolution | `scipy.signal.fftconvolve` per channel |
| Master | `master()` → LUFS −14.0, true-peak ceiling −1 dBTP |

Pipeline: dry FluidSynth (FX off) → design IR → fftconvolve (wet) →
dry/wet mix → master → WAV + Opus OGG.

## Pitch verification (mandatory for synthesis/effects)

| Metric | Wet | Dry (SP-001 ref) |
|---|---|---|
| Valid 0.5 s windows | 189 | 189 |
| FFT pitch-class hit rate | **1.0000** | 0.9947 |
| Mean harmonic energy (8 harmonics) | 0.6419 | 0.5307 |
| HE retention | **1.21** | — |

**Pitch verdict: PASS** (hit rate ≥ 0.60 and HE retention ≥ 0.40).
Convolution reverb is a linear filter — the fundamental is preserved (hit rate
held at 100%) and the reverb tail *enriches* harmonic energy (retention > 1),
so the ballad reads warmer, not pitch-shifted.

## Silence / RMS profile

- Silence ratio: **5.08%** (well below the 30% suspect threshold; only
  section-gap rests + the intro's sparse held tones).
- Overall RMS: 0.1342
- LUFS: −14.00  |  Peak: 0.7798 (−2.16 dBTP — true-peak is a ceiling, not a
  target; a dynamic ballad legitimately lands below −1 dB).
- Mono correlation: 0.649

## Artifacts

| File | Size |
|---|---|
| `SP099-ir-designer-ballad-hitl-cand3.wav` | 17,479,000 B |
| `SP099-ir-designer-ballad-hitl-cand3.ogg` | 647,484 B |
| `dry_full_mix_sp001_reference.wav` | 16,949,804 B |
| `MIDI/cand3-…-phase1.mid` (original preserved) | 4,691 B |
| `MIDI/cand3-…-bXo0.mid` (reworked, phase-2) | 4,691 B |
| `Audio/stems_dry/*.wav` (5 stems) | 16.8–16.9 MB |
| `Audio/stems_wet/*_IR.wav` (5 stems) | 17.3–17.5 MB |
| `provenance.json`, `Analysis/render_stats.json`, `Analysis/select_20261016.json` | — |

Stem labels: `track00_Violin`, `track01_Bright_Acoustic_Piano`,
`track02_Cello`, `track03_Viola`, `track04_Drums`.

## Notes

- Selection script: `Production/select_job_20261016.py`.
- Rework script: `Scripts/rework_cand3.py`; produce script:
  `Scripts/produce_sp099_cron.py`.
- The source is a HITL round-0 candidate still awaiting a human pick; the
  original file was NOT modified — the rework lives entirely under this
  Production output (phase-1 sidecar + reworked phase-2).
- Trailing `SameFileError` at the end of both scripts is cosmetic (each script
  already resides in `Scripts/`); all artifacts were written before it.
