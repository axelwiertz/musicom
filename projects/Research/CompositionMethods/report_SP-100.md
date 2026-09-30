# Report: SP-100 — Volterra Series Synthesis (VSS)

## Method Overview

| Field | Value |
|---|---|
| **Method ID** | SP-100 |
| **Name** | Volterra Series Synthesis (VSS) |
| **Layer** | absolute — sound production (post-processing / DSP) |
| **One-line Description** | General nonlinear synthesis framework using Volterra series expansion (Taylor series with memory) for harmonic/inharmonic intermodulation, saturation, and spectral enrichment. |
| **Candidate Code Path** | `sound/effects/volterra_synthesis.py` |
| **Workflow Integration** | `workflows.musicom_workflow.produce(method="SP-100")` |

## Summary Table Row (added)

```
|| **SP-100** | Volterra Series Synthesis (VSS) | **Post-Processing / DSP** | Nonlinear Distortion / Intermodulation Enrichment | General nonlinear synthesis framework using Volterra series expansion (Taylor series with memory). Multi-order kernels generate harmonic/inharmonic intermodulation, saturation, and spectral enrichment as a post-process on rendered audio. Laguerre pruning reduces cost to $\mathcal{O}(L^P)$ per sample. Candidate: `sound/effects/volterra_synthesis.py`. |
```

## Line Count

| Before | After | Delta |
|---|---|---|
| 22,073 | 22,236 | +163 |

## Files Created / Modified

| File | Action |
|---|---|
| `methods_db.md` | Modified (summary table row + detailed section appended) |
| `sound_method_SP-100_VSS.md` | Created (standalone full write-up, 18,152 bytes) |
| `report_SP-100.md` | Created (this file) |
| `_temp_sp100.md` | Created then deleted (temporary staging file) |

## Detailed Section Text (Appended to methods_db.md)

The section "Sound Production Method SP-100 — Volterra Series Synthesis (VSS)" was appended after line 22,073 of `methods_db.md`. It contains:

### Source
References: Araujo-Simon (2023) compositional Volterra series, Schetzen (1980) Volterra/Wiener theory, Rugh (1981) nonlinear systems, Orcioni et al. (2018) tube device identification, Bussgang (1974) multiple-input analysis.

### Layer
**absolute** — sound production (post-processing / DSP). Candidate: `sound/effects/volterra_synthesis.py`.

### Description
The Volterra series generalizes convolution to nonlinear systems with memory. Output $y(t)$ = sum of linear convolution (1st-order kernel) plus higher-order multidimensional convolutions (2nd, 3rd, ... order Volterra kernels). Subsumes memoryless waveshaping (SP-019, SP-062), Hammerstein/Wiener models, parallel bilinear filters, and mild tape/tube saturation.

### Technical Mechanics
- **Discrete-time**: $y[n] = h_0 + \sum h_1[m_1] x[n-m_1] + \sum\sum h_2[m_1,m_2] x[n-m_1] x[n-m_2] + \ldots$
- **Frequency-domain**: $Y(f) = H_1(f)X(f) + \sum_{f_1+f_2=f} H_2(f_1,f_2)X(f_1)X(f_2) + \ldots$
- **Laguerre pruning**: project kernels onto $L$ orthonormal Laguerre functions → $L^P$ coefficients instead of $M^P$
- **Kernel identification**: linear least-squares with ridge/LASSO regularization
- **Complexity**: full $O(M^P)$, Laguerre $O(P\cdot L)$, diagonal $O(P\cdot M)$ per sample

### Musical Elements Framework
- **PITCH**: $h_1$ = EQ, $h_2$ = sum/difference intermodulation, $h_3$ = triple-beat (odd/even harmonic control)
- **RHYTHM**: Transparent timing; transient intermodulation from 3rd-order kernels
- **HARMONY**: Emergent intermodulation — dyads produce sum/difference tones; chord-dependent spectra
- **STRUCTURE**: Per-section kernel parameters; section transitions interpolate coefficients
- **TEXTURE**: Sparse kernel = targeted enhancement; dense kernel = intermodulation fog; $\|h_2\|/\|h_1\|$ = texture dial

### UnitMatrix Integration
- **Voices**: Per-voice post-process or master bus. Master bus creates inter-voice nonlinear coupling.
- **Sections**: Per-section VSS parameter set (structure, magnitude, Laguerre pole/order)
- **Workflow**: MIDI → Audio (FluidSynth) → VSS post-process → enriched buffer

### Pitfalls
1. Full kernel cost prohibitive ($M=64$, $P=3$ → 45,760 coefficients) — use Laguerre pruning
2. Feedforward only (unconditionally stable); feedback loop VSS may diverge
3. Ill-conditioned kernel identification — use ridge/LASSO
4. Non-intuitive phase distortion from higher-order kernels
5. Laguerre pole sensitivity ($\alpha \in [0.3, 0.9]$ recommended)
6. Cannot emulate feedback-based circuits (use SP-051 WDF)
7. Post-process limitation: enriches only, does not create content

## Technical Mechanics Summary

VSS is the most general representation of an analytic, fading-memory nonlinear system. Key equations:

1. **Discrete Volterra**: $y[n] = \sum_{p=0}^P \sum_{m_1=0}^{M-1} \cdots \sum_{m_p=0}^{M-1} h_p[m_1,\ldots,m_p] \prod_{q=1}^p x[n-m_q]$

2. **Symmetric kernel**: $h_p$ invariant under index permutation, reducing coefficients from $M^p$ to $\binom{M+p-1}{p}$

3. **Laguerre expansion**: $h_p[m_1,\ldots,m_p] \approx \sum_{j_1=1}^{L}\cdots\sum_{j_p=1}^{L} c_p(j_1,\ldots,j_p) \ell_{j_1}[m_1]\cdots\ell_{j_p}[m_p]$

4. **Frequency response**: 2nd-order → $f_1\pm f_2$, 3rd-order → $f_1\pm f_2\pm f_3$

5. **Identification**: least-squares on regressor matrix $X$ containing all $p$-fold products of delayed inputs

## Quirks and Pitfalls Hit During Execution

1. **Summary table row overlaps**: The SP-099 row had a `|||` (three-pipe) prefix from prior editing, while SP-097 used `||` (two-pipe). My SP-100 row matched the adjacent SP-099/SP-098 style. This is a pre-existing formatting inconsistency, not introduced by this method.

2. **LaTeX double-backslash**: The `$\\mathcal{O}$` LaTeX constructs in the patched summary table row had double-escaped backslashes (`$\\\\mathcal{O}$`) which had to be manually corrected back to `$\mathcal{O}$`. This is a known patch tool issue with Markdown LaTeX escaping.

3. **Patch corruption of adjacent row**: When fixing the double-backslash issue on SP-100, the SP-099 row lost its `|| **SP-099** | ...` prefix and was reduced to `inharmonicity. $\mathcal{O}(1)$ ...` — requiring a second fix to restore the full SP-099 row content.

4. **Laguerre basis implementation**: The Laguerre filter cascade in Python is subtle — the standard formula $L_j(z) = \sqrt{1-\alpha^2} \cdot (z^{-1}-\alpha)^j / (1-\alpha z^{-1})^{j+1}$ requires careful state management for the cascaded first-order sections. The implementation shown is correct but should be validated with unit tests.

5. **Kernel symmetry handling**: The symmetric kernel sum in the Python implementation carefully accounts for permutation factors (1 for equal indices, 3 for one pair equal, 6 for all distinct) to avoid double-counting while preserving the correct output.

## Next Free SP ID

SP-101

## Standalone File Path

`/opt/data/projects/Research/CompositionMethods/sound_method_SP-100_VSS.md`

## Report File Path

`/opt/data/projects/Research/CompositionMethods/report_SP-100.md`