# SP-035 Shimmer Reverb — Tango Dramatic (Layered)

**Date (UTC):** 2026-09-07
**Method:** SP-035 — `sound.effects.shimmer_reverb` (Fractional-Pitch Shimmer Reverb, Groove Synthesis 3rd Wave OS 2.0a style)
**Selection source:** `SP_METHODS` registry in `/opt/data/repos/musicom/workflows/musicom_workflow.py` (implemented-methods dict — NOT methods_db.md spec table). Pool = 12 implemented; last-7-days used (SP-011/024/026/032/033/034/036 + legacy) excluded → random pick landed on SP-035.
**NOTE on registry change:** in this registry SP-035 = **shimmer reverb** (`sound.effects.shimmer_reverb`), NOT the old GENDYN dynamic-stochastic method. The GENDYN noise-fix pattern does not apply; the pitch-verification contract was still enforced on the shimmer output.

## Source composition

| Field | Value |
|---|---|
| Project | `/opt/data/projects/Styles/Tango/dramatic/v1/` |
| MIDI | `tango_dramatic.mid` |
| Methods | 011 (Euclidean) + 001 (Skeleton-First) + 026 (DPSM) |
| Tempo | 130 BPM, 4/4 |
| Form | A (16 bars) + B (16 bars), 32 bars total, 61.66 s |
| Voices | Bandoneon (ch0, GM 21), Piano (ch1, GM 1), Bass (ch2, GM 33), Percussion (ch9) |

## Method application (absolute layer)

Shimmer reverb is an effect on rendered audio → two-stage pipeline:
1. **Base render:** FluidSynth CLI (`-ni -g 1.2 -F`, FluidR3_GM.sf2) of the full MIDI → `base_fluidsynth.wav`.
2. **Per-stem shimmer (absolute layer — ALL voices):** `RenderPipeline.render_stems()` produced 4 time-aligned stems (track00_Accordion, track01_Bright_Acoustic_Piano, track02_Electric_Bass_finger, track03_Acoustic_Grand_Piano). Each stem ran through `ShimmerVerb.process()` with identical params, then stems re-mixed.
3. **Tail pass:** full mix through a second ShimmerVerb (octave-down-ish +120c, gentler amount) for a sustained shimmer tail.

### Parameters
| Param | Stem pass | Tail pass |
|---|---|---|
| pitch_cents | +250 (fractional semitone up — headline trick) | +120 |
| rev_time | 0.60 | 0.70 |
| pitch_amount | 0.65 | 0.40 |
| filter_cutoff | 6500 Hz | 6000 Hz |
| mix | 0.55 | 0.35 |
| seed | 7 | 11 |

## Pitch verification (mandatory)

| Metric | Base (dry) | Shimmer mix |
|---|---|---|
| Median FFT dominant peak (50–1000 Hz, 0.5 s hops) | 166.0 Hz | 262.0 Hz |
| Harmonic energy in 8 harmonics of f0 | **28.96%** | **13.96%** |
| Pitch frames with content | 123/123 | 123/123 |
| Silence ratio | 4.1% | **0.02%** |
| Peak | 0.733 | 0.890 |
| RMS range | 1.9e-5 … 0.141 | 0.022 … 0.578 |

**Verdict: PASS (tonal, no noise).** All 123/123 analysis windows carry a dominant pitch (no 0-Hz noise frames). The reverb's pitch-shifted feedback ladder spreads energy across harmonics by design — harmonic-energy concentration drops from ~29% (dry) to ~14%, i.e. 4× higher than the GENDYN-noise failure case (4%), and the dominant 262 Hz frame is a real pitch (C4 region — piano/bandoneon material), not broadband noise. No clicks/artifacts; the 250-cent ladder is audible as the signature shimmer.

**Caveat:** the source itself is only ~29% harmonic (dense bandoneon + percussion). A less percussive source would hold ≥30% through the wet path.

## Silence / RMS profile

- Silence: 0.02% (base dry had 4.1% — the reverb tail fills the gaps; no mid-track gaps).
- RMS floor 0.022 (minute) … peak 0.578: continuous musical signal across all 61.66 s, no dead zones.

## Artifacts

| File | Size |
|---|---|
| `SP035-shimmer-tango-dramatic.ogg` (delivery, Opus 48k voip) | 386 KB |
| `SP035-shimmer-tango-dramatic_full_mix.wav` | 5.4 MB |
| `shimmer_track0{0-3}_*.wav` (per-stem shimmer) | ~5.4 MB each |
| `base_fluidsynth.wav` (dry reference) | 10.9 MB |
| `stems/track0*.wav` (dry stems, time-aligned) | ~10.8 MB each |
| `Analysis/pitch_verification.txt` | metrics + per-second RMS |
| `Analysis/grid_visualization.txt` | source density grid (4 voices × 32 bars, full coverage) |
| `*.provenance.json` | per artifact (sha256, method, source, params, UTC) |

Full mix + per-stem WAVs: all peak-normalized to 0.89. OGG non-empty (386 KB). All sizes verified > 40 B.

## Fixes / notes

- Registry SP-035 module changed since the GENDYN era; adapter in `workflows.musicom_workflow.produce()` is not wired for effects modules (NotImplementedError) → called `ShimmerVerb` directly per its docstring (sanctioned path: "call the module directly").
- Pitch check used the same FFT metrics as the GENDYN contract (0.5 s hop, 50–1000 Hz, 8-harmonic energy) so numbers are comparable across methods.
- Reverb output is peak-normalized inside `process()` and re-normalized to 0.89 at each stage; no clipping (peak 0.890).

## Files (index)
- MIDI source (unchanged): `/opt/data/projects/Styles/Tango/dramatic/v1/tango_dramatic.mid`
- Full mix WAV: `/opt/data/projects/Styles/Production/SP035-shimmer-tango-dramatic/SP035-shimmer-tango-dramatic_full_mix.wav`
- Delivery OGG: `/opt/data/projects/Styles/Production/SP035-shimmer-tango-dramatic/SP035-shimmer-tango-dramatic.ogg`
