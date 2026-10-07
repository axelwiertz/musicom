# Report SP-107 — Look-Ahead Brickwall Limiter (LBL)

## Method ID
**SP-107**

## Method Name
Look-Ahead Brickwall Limiter (LBL)

## Layer
**absolute** — Sound Production method (Post-Processing / DSP)

## One-Line Description
Look-ahead brickwall limiter that delays the input signal, computes gain reduction via peak detection with attack/hold/release envelope shaping, applies the smoothed gain curve to the delayed signal, and ensures no sample exceeds the threshold. The final dynamics-control stage before render.

## Summary Table Row
```
| **SP-107** | Look-Ahead Brickwall Limiter (LBL) | **Post-Processing / DSP** | Peak Control / Loudness Maximization | Look-ahead brickwall limiter that delays the input signal, computes gain reduction via peak detection with attack/hold/release envelope shaping, applies the smoothed gain curve to the delayed signal, and ensures no sample exceeds the threshold. The final dynamics-control stage before render. |
```

## Line Counts

| Metric | Before | After | Delta |
|--------|--------|-------|-------|
| methods_db.md | 23823 lines | 23962 lines | +139 |
| sound_method file | 0 | 289 lines (SP-107_LBL.md) | +289 |
| report file | 0 | this file | this |

## Standalone File Path
`/opt/data/projects/Research/CompositionMethods/sound_method_SP-107_LBL.md`

## Candidate Code Path
`sound/effects/brickwall_limiter.py`

## Complete Section Text Appended

The section "Look-Ahead Brickwall Limiter (LBL) (Sound Production Method SP-107)" was inserted after line 23736 (end of SP-106 APS section) and before the HDCC section.

### Section contents cover:
- ### Source
- ### Layer (absolute — Post-Processing / DSP)
- ### Description
- ### Technical Mechanics (6 sub-sections: gain computer, peak-hold, release, FIR smoothing, look-ahead delay, makeup gain, true-peak, complexity)
- ### Musical Elements Framework (PITCH, RHYTHM, HARMONY, STRUCTURE, TEXTURE)
- ### UnitMatrix Integration (Rows=Voices, Columns=Sections, Cells, zero-drift)
- ### Pitfalls (8 numbered items)

## Technical Mechanics Summary

The LBL processes audio in four cascaded stages:
1. **Gain Computer**: Per-sample $g_{\max}[n] = \min(1, T/|x[n]|)$ — the maximum gain that keeps the sample below threshold $T$.
2. **Peak-Hold**: Moving minimum of $g_{\max}$ over $H = \tau_{\text{hold}} \cdot f_s$ samples, preventing premature gain recovery between transients. Implemented as a min-queue (two-stack) for $\mathcal{O}(1)$ amortized.
3. **Exponential Release**: First-order IIR smoothing: $g_{\text{rel}}[n] = g_{\text{rel}}[n-1] + \alpha(g_{\text{PH}}[n] - g_{\text{rel}}[n-1])$ with $\alpha = 1 - \exp(-1/(\tau_{\text{release}} f_s))$.
4. **FIR Smoothing (Attack)**: Cascade of $K=3$ box-averaging filters of length $L_a = \tau_{\text{attack}} \cdot f_s$, producing a Gaussian-like kernel with zero overshoot.
5. **Look-Ahead Delay**: Input delayed by $D = \tau_{\text{attack}} \cdot f_s$ samples before gain multiplication.
6. **Makeup Gain**: $y_{\text{out}} = G_{\text{MU}} \cdot y$, where $G_{\text{MU}} = 10^{\text{dB}/20}$.

Total latency = $\tau_{\text{attack}}$ (1.5–10 ms). Total cost = $\mathcal{O}(1)$ per sample.

## Quirks and Pitfalls Hit

1. **Patch double-escaped LaTeX**: The `patch` tool converted `\mathcal{O}` to `\\mathcal{O}` (double backslash) in the summary table. Fixed in a second pass by rewriting the row with `$\mathcal{O}(N)$` without escapes — but had to be careful that the old_string matched what was actually in the file (with double backslash `\\\\mathcal{O}` in the raw file).

2. **SP-105 was accidentally dropped**: The first patch attempt to fix SP-106's LaTeX and normalize pipes used an old_string that included SP-105. Since the old_string matched (but didn't explicitly keep SP-105 in the new_string), SP-105 was deleted. A second patch restored it using the context from surrounding lines.

3. **Insertion point**: The SP detailed sections are intermixed with composition method sections (CP/HDCC etc.). The SP-107 section had to be inserted after the last SP section (SP-106 ending at line 23736) and before the next non-SP section (HDCC at line 23737). Used head/tail/mv instead of sed to avoid template-processing issues with the $ signs in the markdown content.

4. **Table pipe consistency**: Existing SP rows use inconsistent pipe prefixes (`|`, `||`, `|||`) at lines 278-283. Normalized SP-105/106/107 to single `|` to match the convention of SP-001 through SP-102.

## Next Free SP ID
SP-108

## Verification

- [x] Summary table updated with SP-107 row
- [x] Detailed section appended to methods_db.md at correct position
- [x] Standalone file created: `sound_method_SP-107_LBL.md`
- [x] Report file created: `report_SP-107.md`
- [x] LaTeX escaping verified (single backslash in `\mathcal{O}`)
- [x] Table pipe prefixes normalized
- [x] SP-105 preserved (restored after accidental removal)
- [x] grep SP-107 confirms both summary row and detailed section present