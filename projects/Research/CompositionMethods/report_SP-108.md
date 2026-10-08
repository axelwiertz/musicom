# Report: McAulay-Quatieri Sinusoidal Analysis/Synthesis (MQSAS) — Sound Production Method SP-108

## Overview

| Item | Value |
|------|-------|
| **Method ID** | SP-108 |
| **Method Name** | McAulay-Quatieri Sinusoidal Analysis/Synthesis (MQSAS) |
| **Layer** | absolute (Sound Production — Post-Processing / DSP) |
| **One-line description** | Decomposes a signal into time-varying sinusoidal partials via FFT peak tracking with parabolic interpolation and frame-to-frame partial matching (birth/continuation/death), resynthesized with cubic phase interpolation for continuous instantaneous frequency. |
| **Candidate code path** | `sound/effects/sinusoidal_modeling.py` |

## Summary Table Row

```
| **SP-108** | McAulay-Quatieri Sinusoidal Analysis/Synthesis (MQSAS) | **Post-Processing / DSP** | Sinusoidal Resynthesis / Spectral Editing | Decomposes a signal into time-varying sinusoidal partials via FFT peak tracking with parabolic interpolation and frame-to-frame partial matching (birth/continuation/death). Resynthesizes with cubic phase interpolation for continuous instantaneous frequency. Enables independent partial editing, pitch-shift, time-stretch, and cross-synthesis. The foundational analysis-resynthesis method for spectral editing (SPEAR, SNDAN, Loris). O(K) synthesis per sample. Candidate: `sound/effects/sinusoidal_modeling.py`. |
```

## Files

| File | Path | Lines |
|------|------|-------|
| **Methods DB (updated)** | `/opt/data/projects/Research/CompositionMethods/methods_db.md` | 24203 (prev: 24035) |
| **Standalone method file** | `/opt/data/projects/Research/CompositionMethods/sound_method_SP-108_MQSAS.md` | New, ~120 lines |
| **Report file** | `/opt/data/projects/Research/CompositionMethods/report_SP-108.md` | This file |

## Line Counts

- **Before**: 24035 lines in methods_db.md
- **After**: 24203 lines in methods_db.md
- **Delta**: +168 lines (+1 summary table row + ~167 lines detailed section)

## Verification

- `wc -l /opt/data/projects/Research/CompositionMethods/methods_db.md` → 24203 lines
- `grep 'SP-108' methods_db.md` → 2 matches (summary row + detailed section header)
- Summary table row at lines 285 (content `| **SP-108** | ...`)
- Detailed section header at the end of file: `# McAulay-Quatieri Sinusoidal Analysis/Synthesis (MQSAS) — Sound Production Method SP-108`
- Standalone file exists: `sound_method_SP-108_MQSAS.md`
- Report file exists: `report_SP-108.md`

## Technical Mechanics Summary

### Core Algorithm

MQSAS = three-stage pipeline:

1. **Peak Detection**: STFT → spectral peak picking with parabolic interpolation for sub-bin frequency resolution. Each frame yields $(f_k, A_k, \phi_k)$ for the $K$ largest peaks.

2. **Partial Tracking**: Frame-to-frame peak matching via MQ nearest-neighbor algorithm (Euclidean distance in (semitone, dB) space). Birth threshold $T_b(f)$ compensates for spectral rolloff; death threshold $T_d$ controls partial retention. Prediction via linear extrapolation or Burg-method LP.

3. **Oscillator Bank Synthesis**: Cubic phase interpolation $\theta(t)=a+bt+ct^2+dt^3$ matching phase AND instantaneous frequency at both frame boundaries guarantees $C^1$ continuity. Linear amplitude interpolation. Sum of partials $y[n]=\sum A_i \cos(\theta_i[n])$.

### Key Innovation (vs earlier methods)

Cubic phase interpolation eliminates the frequency discontinuities that occur with linear phase (or constant-frequency) frame-to-frame interpolation. This is the signature MQ contribution (1986). SMS (SP-027) builds on MQ by adding a stochastic residual; MQSAS has no residual.

### Complexity

- Analysis: $\mathcal{O}(N \log N)$ per frame for FFT + $\mathcal{O}(N_m \log N_m)$ for peak matching
- Synthesis: $\mathcal{O}(K)$ per sample oscillator bank

### Distinction from Nearest SP Methods

| Method | Difference |
|--------|------------|
| SP-026 Phase Vocoder | Fixed STFT bins vs. adaptive peak tracking; no partial tracking |
| SP-027 SMS | MQ has no stochastic residual; SMS = deterministic + stochastic |
| SP-039 IFFT Additive | SP-039 builds spectra from scratch; MQ extracts from audio |
| SP-031 Cross-Synthesis | SP-031 mixes spectral envelopes; MQ enables per-partial editing |

## Quirks & Pitfalls Hit

1. **Patch double-pipe issue**: The summary table row replacement introduced `||` (double pipe) prefix because the patch matched the `|` in the old_string as the leading cell delimiter rather than the content line delimiter. Fixed by a second patch normalizing `||` → `|`. This is a known table-editing quirk in the methods_db.

2. **File append location**: The detailed section was appended to the end of the file, which already contained composition method 108 and 109 detailed sections. The Sound Production Methods Framework's detailed sections are mixed with composition method details in the file — append-order not section-order. Verified SP-108's detailed section lands correctly at the file end.

3. **Summary table row formatting**: The correct leading pipe count in the summary table is a single `|` at the start of each data row, consistent with lines 190+ (`| **SP-001** | ...`). The read_file tool's output prefix `NN|` can be confusing to parse.

## Next Free SP ID

**SP-109** is the next available ID for a future sound production method.