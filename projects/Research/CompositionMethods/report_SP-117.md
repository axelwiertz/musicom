# Research Report: SP-117 — Harmonic Exciter Synthesis (HEX)

## Overview

- **Method ID:** SP-117
- **Method Name:** Harmonic Exciter Synthesis (HEX)
- **Acronym:** HEX
- **Layer:** `absolute` (Sound Production — Post-Processing / DSP)
- **One-line description:** Post-processing DSP that enhances brightness and presence by generating low-order harmonics from the high-frequency band only via an asymmetric cubic soft clipper and allpass phase shifter.
- **Next Free SP ID:** 118

## Summary Table Row

```
|| **SP-117** | Harmonic Exciter Synthesis (HEX) | **Post-Processing / DSP** | Split-Band Harmonic Enhancement / Presence & Air Restoration | Post-processing DSP that enhances brightness and presence by generating low-order harmonics from the high-frequency band only (crossover 1–10 kHz). Asymmetric cubic soft clipper produces both odd and even harmonics; allpass phase shifter adds air. Per-voice or bus configuration, $O(1)$ per sample, zero latency. Candidate: `sound/effects/harmonic_exciter.py`. |
```

## Line Count

- **Before:** 26199 lines (last SP-116 entry)
- **After:** 26444 lines
- **Delta:** +245 lines (includes ~243 line detailed section + 1 summary row + formatting)

## File Paths

| Artifact | Path |
|---|---|
| Methods DB (updated) | `/opt/data/projects/Research/CompositionMethods/methods_db.md` |
| Standalone method file | `/opt/data/projects/Research/CompositionMethods/sound_method_SP-117_HEX.md` |
| This report | `/opt/data/projects/Research/CompositionMethods/report_SP-117.md` |
| Candidate code path | `sound/effects/harmonic_exciter.py` |
| Integration point | `workflows.musicom_workflow.produce(method="SP-117")` |

## Verification

- ✅ `SP-117` row in summary table at line 303
- ✅ Detailed section `# Sound Production Method SP-117 — Harmonic Exciter Synthesis (HEX)` at line 26203
- ✅ Standalone file written: `sound_method_SP-117_HEX.md` (22,317 bytes)
- ✅ Report file written: `report_SP-117.md`
- ✅ Temp file cleaned up
- ✅ No duplicate SP detected (max was SP-116)
- ✅ All $\\mathcal{O}$ syntax uses single backslash (no double-escape)

## Technical Mechanics Summary

### Core Algorithm

1. Split input into dry path (full-band) and excite path (HF only)
2. **2nd-order Butterworth HPF** with cutoff $f_c \in [1, 10]$ kHz isolates HF band
3. **Optional RMS compressor** (threshold $-18$ dBFS, ratio 8:1) normalizes clipper input
4. **Pre-distortion gain** $G$ controls harmonic density
5. **Asymmetric cubic soft clipper**: $f(x) = x - x^3/3$ with DC offset $\delta$ for even harmonics
   - $\delta = 0$: pure odd harmonics (edgy)
   - $\delta > 0$: both odd and even harmonics (warm)
   - Even/odd ratio $R_{2/3} = 6\delta$
6. **Post-distortion gain** $1/G$ restores level
7. **DC blocker** removes offset from asymmetry
8. **1st-order allpass** (break $f_b$): frequency-dependent phase shift adds "air"
9. **Wet/dry blend**: $y = (1-\alpha)x + \alpha x_{\text{excite}}$

### Complexity
- $\mathcal{O}(1)$ per sample (no FFT, no frame, no table lookup)
- ~22 mult + ~14 add per sample (without compressor: ~16+10)
- Zero latency, deterministic, seed-independent

### Key Equations

$$f_{\text{clip}}(x) = \begin{cases}
-\frac{2}{3}, & x < -1 \\
x - \frac{x^3}{3}, & -1 \leq x \leq 1 \\
\frac{2}{3}, & x > 1
\end{cases}$$

$$H_{\text{AP}}(z) = \frac{a_1 + z^{-1}}{1 + a_1 z^{-1}}, \quad a_1 = \frac{\tan(\pi f_b / f_s) - 1}{\tan(\pi f_b / f_s) + 1}$$

$$y[n] = (1-\alpha) x[n] + \alpha \cdot H_{\text{AP}}(z)\, \frac{1}{G}\, f_{\text{clip}}(G \cdot H_{\text{HP}}(z) x[n] + \delta)$$

### Musical Parameters (5)
1. **Crossover $f_c$** (1–10 kHz): frequency above which harmonics are generated
2. **Pre-gain $G$** (0.1–3.0): harmonic density (more = brighter)
3. **Asymmetry $\delta$** (0.01–0.3): even/odd harmonic balance
4. **Allpass break $f_b$** (1–8 kHz): "air" and spatial texture
5. **Blend $\alpha$** (0.0–1.0): wet/dry mix

## Quirks & Pitfalls Hit

1. **Header merged with previous section**: The appended `# Sound Production Method SP-117` header got concatenated onto the end of the preceding section's last line (item 6 of the D3PM section). Fixed via patch by adding the missing newline.

2. **Summary table formatting**: The `|---|` separator at the bottom of the SP summary table needed careful handling. The old SP-116 row had a longer description that was partially truncated in the patch match; resolved by matching only the visible portion.

3. **Backslash escaping in LaTeX**: The existing DB uses single backslashes for $\mathcal{O}$, $\\sum$, etc. The new text was already using single backslashes correctly — no double-escape issues.

## Source Attribution

- Knoppel, C. A. (1979). U.S. Patent US4150253A — original Aphex Aural Exciter
- Shekar, P. & Smith, J. (2013). AES Convention 135, e-Brief 104 — digital FAUST model
- FAUST `effect.lib`: open-source `exciter()` and `exciterdemo()` implementations