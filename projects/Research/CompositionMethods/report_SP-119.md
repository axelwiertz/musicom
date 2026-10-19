# Report SP-119 — Auto-Pan / Dynamic Stereo Modulation Synthesis (APMS)

**Date**: 2026-10-19  
**Researched by**: Hermes Agent (cron job)

---

## Method Summary

| Field | Value |
|:---|:---|
| **SP ID** | SP-119 |
| **Method Name** | Auto-Pan / Dynamic Stereo Modulation Synthesis |
| **Acronym** | APMS |
| **Layer** | absolute — Post-Processing / DSP |
| **Code Path** | `sound/effects/autopan.py` |
| **Next Free SP ID** | SP-120 |

**One-line description**: Continuously varies the stereo pan position of a mono (or stereo) signal via LFO-driven constant-power panning law (sine/cosine amplitude distribution), with multiple waveforms (sine, triangle, square, sawtooth, random S&H), stereo phase offset for rotary/wide effects, and tempo-synced rate.

---

## Summary Table Row (inserted into methods_db.md)

```
|| **SP-119** | Auto-Pan / Dynamic Stereo Modulation Synthesis (APMS) | **Post-Processing / DSP** | Stereo Field Modulation / Spatial Animation | Continuously varies the stereo pan position of a mono (or stereo) signal via LFO-driven constant-power panning law. Multiple waveforms (sine, triangle, square, sawtooth, random S&H) control the pan trajectory; stereo phase offset sets rotation style; rate can be tempo-synced. Per-voice independent parameters, $O(1)$ per sample, zero latency. Candidate: `sound/effects/autopan.py`. |
```

---

## File Inventory

| File | Path | Status |
|:---|:---|:---:|
| methods_db.md (updated) | `/opt/data/projects/Research/CompositionMethods/methods_db.md` | ✅ Appended + summary row added |
| Standalone method file | `/opt/data/projects/Research/CompositionMethods/sound_method_SP-119_APMS.md` | ✅ Written |
| Report | `/opt/data/projects/Research/CompositionMethods/report_SP-119.md` | ✅ Written |
| Temp file | `/opt/data/projects/Research/CompositionMethods/_temp_sp119.md` | ✅ Deleted |

---

## Line Counts

| Before | After | Delta |
|:---:|:---:|:---:|
| 26,967 | 27,222 | +255 lines |

(Before: 26967 lines; After: 27222 lines; Delta = +255 lines)

---

## Technical Mechanics Summary

**Core algorithm**: LFO-driven constant-power sinusoidal panning.

```
Pan position from LFO:  p[n] = depth * waveform(2*pi*rate*n/fs + phase)
Pan angle:              theta[n] = pi/4 * (1 + p[n])
Gains:                  gL[n] = cos(theta[n])
                        gR[n] = sin(theta[n])
Output:                 yL[n] = gL[n] * x[n]
                        yR[n] = gR[n] * x[n]
```

**Key properties**:
- **Constant power**: cos² + sin² = 1 ⇒ equal perceived loudness at every pan position
- **Zero latency**: sample-by-sample processing, no FFT frames
- **O(1) per sample**: 2 trig calls + 4 multiplies per sample (precomputable LFO table reduces to 2 multiplies + 2 table reads)
- **Waveforms**: sine (smooth), triangle (uniform sweep), square (hard L/R jumps), sawtooth (slow-snap), random S&H (stepped hopping)
- **Stereo phase offset**: 0° = pure pan, 90° = rotary, 180° = max width
- **Tempo sync**: rate = BPM / (60 × note-division)
- **M/S mode**: modulates only the side component of stereo inputs

**Distinct from**:
- SP-007 (M/S masking EQ — EQ application of M/S, not continuous pan modulation)
- SP-021 (binaural HRTF — psychoacoustic 3D, not 2-channel amplitude panning)
- SP-034 (Ambisonics — full-sphere B-format, not 2-channel panning)
- SP-043 (Wave Field Synthesis — physical wavefront reconstruction)
- SP-053 (VBAP — static vector-based panning, not LFO-driven)
- SP-059 (FDLMS — modulated delay lines, not amplitude panning)
- SP-102 (AMS — two-quadrant volume tremolo, not four-quadrant opposite-channel panning)
- SP-106 (Phaser — allpass comb-filter sweep, not amplitude-based panning)

---

## Musical Elements Framework Mapping

| Element | Contribution |
|---|---|
| PITCH | None (no pitch modification; mild phasing artifact at rapid rates) |
| RHYTHM | Tempo-synced rate adds spatial accent pattern; polyrhythmic interplay with meter |
| HARMONY | Spatial counterpoint: per-voice independent rates create non-pitch polyphony; phase-offset voices form "spatial chords" |
| STRUCTURE | Per-section parameter trajectory (rate, depth, waveform, phase) defines macro-form through spatial gesture |
| TEXTURE | Primary domain: slow sine = ambient, medium triangle = engaging, fast square = aggressive, random = chaotic |

---

## UnitMatrix Integration

- **Voices**: Each voice gets independent APMS parameters (rate_v, depth_v, waveform_v, phi_v)
- **Sections**: Per-section APMS config; rate tempo-synced to section BPM; linear parameter interpolation at boundaries
- **Cell filling**: APMS applied post-render on audio buffer b_{v,m}[n]; mono→2-channel with identical sample count (zero drift)

---

## Quirks and Pitfalls Encountered

1. **LaTeX backslash escaping**: `write_file` preserves single backslashes in raw strings, while the existing methods_db.md uses double backslashes (`\\mathcal{O}` vs `\mathcal{O}`). Both produce identical LaTeX output; the file convention varies between sections. Maintained single backslash throughout for consistency within the new section.

2. **Table pipe formatting**: The summary table uses `|| **SP-ID** | ...` (double-pipe prefix) for most rows. After patching, verified the patched line matches the surrounding formatting. Also noted the `|---|` table separator.

3. **Append without trailing newline**: The `cat >>` append attached SP-119 header to the last line of the file (which lacked a trailing newline). Fixed with a patch that added a blank line between sections.

4. **Patch double-escape hazard**: The `patch` tool's old_string/new_string parameters interpret backslashes as escape sequences, requiring `\\` to represent a literal `\` in LaTeX. This caused `\mathcal{O}(1)` to become `\\mathcal{O}(1)` and `S\&H` to become `S\\&H`. Fixed by a second patch with corrected escaping.

5. **Name collision**: The acronym `APS` (Auto-Pan Synthesis) conflicts with SP-106 (Phaser/Allpass Modulation Synthesis, "APS"). Chose `APMS` instead.

6. **`O(1)` vs `\mathcal{O}(1)`**: The summary table uses `$O(1)$` (matching SP-117/SP-118 convention) rather than the more precise `$\mathcal{O}(1)$`. Used `$O(1)$` for consistency.

---

## Candidate Code Path

`sound/effects/autopan.py` — pluggable into `workflows.musicom_workflow.produce(method="SP-119")` as a post-render DSP stage.