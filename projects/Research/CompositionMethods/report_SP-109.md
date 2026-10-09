# Report: SP-109 — Spectral Gating Adaptive Noise Reduction (SG-ANR)

## Overview

| Field | Value |
|-------|-------|
| **SP-ID** | SP-109 |
| **Method Name** | Spectral Gating Adaptive Noise Reduction (SG-ANR) |
| **Layer** | absolute |
| **Category** | Post-Processing / DSP |
| **Description** | Frequency-domain noise reduction via per-bin STFT gain masking. Estimates noise profile from silent/noise-only segment (stationary mode) or via continuous EMA noise floor tracking (non-stationary mode), computes a sigmoid gain mask from the per-bin SNR, and applies it to the magnitude STFT while preserving original phase. |
| **Candidate Code Path** | `sound/effects/spectral_gate.py` |
| **Standalone File** | `sound_method_SP-109_SG-ANR.md` |
| **Report File** | `report_SP-109.md` |

## Summary Table Row

```
|| **SP-109** | Spectral Gating Adaptive Noise Reduction (SG-ANR) | **Post-Processing / DSP** | Noise Suppression / Spectral Cleanup | Frequency-domain noise reduction via per-bin STFT gain masking. Estimates noise profile from silent/noise-only segment (stationary mode) or via continuous EMA noise floor tracking (non-stationary mode), computes a sigmoid gain mask from the per-bin SNR, and applies it to the magnitude STFT while preserving original phase. Reconstructs via overlap-add IFFT. Produces cleaned audio with reduced background hiss, rumble, and ambience. Candidate: `sound/effects/spectral_gate.py`. |
```

## Line Counts

| Metric | Value |
|--------|-------|
| **Before** | 24293 lines |
| **After** | 24424 lines |
| **Delta** | +131 lines |
| **Summary row location** | Line 287 |
| **Detailed section start** | Line 24296 |

## Technical Mechanics Summary

**Signal model**: $y[n] = x[n] + d[n]$ (clean + additive noise)

**Core algorithm**:
1. STFT analysis (Hann window, 75% overlap, FFT size N=1024–4096)
2. Noise profile estimation: stationary (mean of noise-only frames) or non-stationary (EMA per-bin tracker with time constant $\tau$)
3. Gain mask: sigmoid $G = \sigma(s \cdot (|Y|/|\hat{D}| - t))$ or power-spectral subtraction $G = \sqrt{\max((|Y|^2 - \beta|\hat{D}|^2)/|Y|^2, \gamma^2)}$
4. Smoothing: frequency-domain (moving average across bins) + time-domain (IIR across frames)
5. Apply gain to magnitude, preserve phase, reconstruct via IFFT + overlap-add

**Complexity**: $O(L \log N)$ per buffer of length $L$

**Key parameters**: $t$ (threshold ratio), $s$ (sigmoid slope), $\beta$ (over-subtraction), $\gamma$ (spectral floor), $\tau$ (time constant), $W_f$ (freq smoothing), $\tau_{\text{smooth}}$ (time smoothing)

## Musical Elements Framework

| Element | Effect |
|---------|--------|
| **PITCH** | Indirect — tonal content above noise floor passes through; weak partials attenuated |
| **RHYTHM** | Preserved — but aggressive gating with long time constants smears transients |
| **HARMONY** | Preserved — frequency ratios unchanged; quiet chord tones may be attenuated |
| **STRUCTURE** | Unaffected — gate operates uniformly or adaptively across sections |
| **TEXTURE** | Primary target — noise floor reduction, spectral cleanup; risk of musical noise artifacts |

## UnitMatrix Integration

Pipeline: `UnitMatrix → [SP-001/SP-011/...] → per-voice WAV stems → SG-ANR → cleaned stems → mix → final WAV/OGG`

Per-voice `SpectralGateConfig` dataclass with: `mode`, `n_fft`, `hop_length`, `noise_profile_path`, `time_constant_s`, `threshold_ratio`, `sigmoid_slope`, `freq_smooth_hz`, `time_smooth_ms`, `floor_gamma`.

## Pitfalls Encountered

1. **Summary table format inconsistency**: SP-105–108 use `| ` (single leading pipe) while most earlier rows use `||` (double leading pipe). The new row was added with `||` matching the majority format, but the table already had mixed styles. Verified: the row renders correctly between SP-108 and `|---`.
2. **LaTeX backslash escaping**: The existing file uses single backslashes in LaTeX ($\mathcal{O}$, $\sum$, etc.). The temp file was written with single backslashes, avoiding the double-escape pitfall.
3. **No existing SP-109 files to conflict with**: Verified no `sound_method_SP-109*` or `report_SP-109*` existed before creation.
4. **File location via symlink**: `/opt/data/projects/Research/CompositionMethods/` is a symlink to `/opt/data/repos/musicom/projects/Research/CompositionMethods/`. Files resolve correctly via the symlink.

## Verification

```
$ grep -n 'SP-109' methods_db.md
287:|| **SP-109** | ... (summary table row)
24296:# Spectral Gating Adaptive Noise Reduction (SG-ANR) — Sound Production Method SP-109 (detailed section)

$ wc -l methods_db.md
24424 methods_db.md

$ ls -la sound_method_SP-109_SG-ANR.md
exists, 9319 bytes

$ ls -la report_SP-109.md
exists (this file)
```

## Next Free SP-ID

**SP-110** — the next available Sound Production method ID.
