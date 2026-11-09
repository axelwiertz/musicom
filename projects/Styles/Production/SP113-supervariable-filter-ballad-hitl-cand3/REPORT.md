# SP-113 Supervariable VCF — pop-ballad HITL candidate (reworked)

Random-style production job (SP methods), layer-aligned, **2026-11-09**.

## Selection

| Item | Value |
|---|---|
| Seed | `20261109` |
| Registry | `workflows.musicom_workflow.SP_METHODS` (87 pickable methods) |
| Selected method | **SP-113** — `sound.effects.supervariable_filter` |
| Method desc | Supervariable VCF: 4-D filter (cutoff/resonance/bandwidth/profile), continuous HP→notch→LP character morph via SVF output blending (Shear Electronics Relic-style) |
| Source composition | `Pop/ballad-hitl/HITL/round0/candidates/cand3-pViol-ldX-ar4-pdpuls-drful-bXo0.mid` |
| Pool (after exclusions) | 78 methods |
| Recent excluded (≤7 d) | SP-080, SP-097, SP-107, SP-117, SP-119, SP-143, SP-146 |
| Baseline excluded | SP-001 |
| Already on source | SP-099 |

## Source composition

- **Genre/role**: pop ballad — a HITL round-0 "texture+bed" candidate (pad = pulse
  style, arp rate 4, drums full).
- **Key**: D aeolian (`Dm`), progression **i–VI–III–VII** (Dm–B♭–F–C) with
  per-section regions (Intro i–VI · Verse full cycle · Chorus III–VII lift ·
  Bridge VII–VI · Outro i).
- **Tempo**: 72 BPM · **Form**: Intro(4)+Verse(8)+Chorus(8)+Bridge(4)+Outro(4) =
  28 bars ≈ 93.3 s.
- **Voices**: Violin (lead, ch0), Piano (pad), Cello (bass), Viola (arp), Drum Kit (ch9).

## Pre-flight rules audit (BEFORE rework)

| Rule | Verdict | Numbers |
|---|---|---|
| 1. Grid sync | **PASS** | 0 / 362 pitched onsets off-grid (16th = 120 ticks) |
| 2. Harmony | **FAIL** | 1 / 362 out-of-scale · 100 / 362 out-of-chord |
| 3. Zero-drift | **PASS** | all 5 note tracks = 53760 ticks (28 bars) |

- The single out-of-scale note: **D♯5** (pc 3), bridge bar 22 — chromatic
  tendency tone from the lead's 023 Tendency-Masking method.
- The 100 out-of-chord notes: mostly the **pad's "pulse" voicing** playing
  seventh/extension tones (e.g. B♭/C over Dm, A over B♭) plus lead passing tones
  — idiomatic but strictly non-triad under the gate's triad-only harmony rule.

## Rework (chord-tone quantize — all pitched voices)

- Snap every non-drum pitched note to the **nearest chord tone of its bar**,
  register-preserving (octave-relative to the bar's triad root).
- **104 / 362** notes snapped. Timing (grid), durations, velocities, and the
  terminal landmarks untouched → zero-drift preserved.
- Output: `MIDI/pop-ballad-hitl-cand3-reworked.mid` (4691 B).

## Post-rework audit

| Rule | Verdict | Numbers |
|---|---|---|
| Grid sync | **PASS** | 0 off-grid |
| Harmony | **PASS** | 0 out-of-scale · 0 out-of-chord |
| Zero-drift | **PASS** | 5 note tracks = 53760 ticks |

All three read 0. SP-113 applied on the clean reworked MIDI.

## SP-113 application (absolute layer, whole mix)

Dry FluidSynth render (`-ni -g 1.2 -R no -C no`, FluidR3_GM.sf2), then the
Supervariable VCF as the single production layer:

| Variant | Parameters |
|---|---|
| `svcf_sweep` (main) | classic profile morph, cutoff 1200 Hz, res 0.35, bandwidth 0.2, order 2, `profile_mod = cos(2π·t/72 s)·0.85` — slow voltage-controlled HP→notch→LP character sweep |
| `svcf_lp24` (alt) | mode `lp24` (4-pole LP), cutoff 2600 Hz, res 0.2 — dark warmth |
| `full_mix` (reference) | dry, no filter |

## Mastering (`master()`, target for style `pop` = −9.0 LUFS, −1 dBTP ceiling)

| Render | Integrated LUFS | True peak |
|---|---|---|
| `svcf_sweep` | −11.03 | −1.0 dB |
| `svcf_lp24` | −9.33 | −1.0 dB |
| `full_mix` | −9.47 | −1.0 dB |

`svcf_sweep` reads ~ −11 LUFS because the profile sweep periodically passes
through the notch/HP region, reducing average energy — correct behaviour for the
character morph, not a mastering bug (true-peak is a ceiling, not a target).

## Pitch / spectral verification

FFT over the full mix, dominant peak in 50–1000 Hz + band-energy fraction:

| Render | Dominant Hz | Band-energy frac (50–1000 Hz) |
|---|---|---|
| full_mix | 232.8 (B♭3) | 0.820 |
| svcf_sweep | 232.8 (B♭3) | 0.634 |
| svcf_lp24 | 232.8 (B♭3) | 0.880 |

- Dominant **232.8 Hz = B♭3**, the VI-degree root — **tonal content confirmed**,
  not noise (harmonic band-energy ≫ single digits).
- The filter shifts *character*, not pitch: dominant stays at 232.8 Hz in all
  three renders, as expected for a state-variable filter.

## Silence profile

| Render | Silence ratio | Low-RMS seconds (of 95) |
|---|---|---|
| full_mix | 2.79 % | 1 |
| svcf_sweep | 3.14 % | 1 |
| svcf_lp24 | 2.77 % | 1 |

All far below the 30 % suspect threshold; the single low-RMS second is the outro
fade, not a mid-track gap.

## Files

```
Audio/full_mix.wav          17 MB   (dry reference, mastered)
Audio/full_mix.ogg           1.7 MB
Audio/svcf_sweep.wav        17 MB   (main SP-113 treatment, mastered)
Audio/svcf_sweep.ogg         1.6 MB
Audio/svcf_sweep_raw.wav    17 MB   (pre-master)
Audio/svcf_lp24.wav         17 MB   (alt SP-113 treatment, mastered)
Audio/svcf_lp24.ogg          1.6 MB
Audio/svcf_lp24_raw.wav     17 MB   (pre-master)
Audio/provenance.json
MIDI/pop-ballad-hitl-cand3-reworked.mid   4.7 KB
MIDI/rework_provenance.json
Analysis/silence_profile.json
Analysis/spectral.json
process_sp113.py
```

Stems not generated: SP-113 is a **mix-level absolute-layer effect** (applies to
the summed bus, not per-track), consistent with the effects-job precedent.

## Verdict

Composition failed harmony gate (1 out-of-scale + 100 out-of-triadic-chord) →
reworked by chord-tone quantize → re-audit clean (0/0/0) → SP-113 applied,
mastered, pitch-verified (B♭3 dominant, tonal) and silence-checked (≤3.1 %).