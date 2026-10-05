# Research Report: SP-105 — Coupled Resonant Filter Bank Synthesis (CRFBS)

## Method Overview

| Field | Value |
|-------|-------|
| **Method ID** | SP-105 |
| **Method Name** | Coupled Resonant Filter Bank Synthesis (CRFBS) |
| **Layer** | absolute — Sound Production (Synthesis Engines) |
| **Type** | Synthesis Engine — Nonlinear Modal Interaction |
| **Candidate Code Path** | `sound/synthesis/coupled_resonator.py` |
| **One-line Description** | Banks of N parallel Mathews-Smith complex-format IIR resonators exchanging energy through a redistribution matrix M to model nonlinear modal coupling in vibrating objects. |

## Summary Table Row (as inserted)

```
|| **SP-105** | Coupled Resonant Filter Bank Synthesis (CRFBS) | **Synthesis Engines** | Nonlinear Modal Interaction / Impact, Cymbal & Plate Timbres | Banks of $N$ parallel Mathews-Smith complex-format IIR resonators exchanging energy through a redistribution matrix $\mathbf{M}$ to model nonlinear modal coupling. Captures delayed tonal components, spectral enrichment during impacts, and energy cascades that linear modal synthesis cannot produce. $\mathcal{O}(N)$ per sample. Candidate: `sound/synthesis/coupled_resonator.py`. |
```

## Line Count

| Before | After | Delta |
|--------|-------|-------|
| 23,329 | 23,459 | +130 |

(Delta = 130 lines: 1 summary table row + 129 lines detailed section including blank lines.)

## Files Created

| File | Path |
|------|------|
| Detailed section (appended to DB) | `/opt/data/projects/Research/CompositionMethods/methods_db.md` (lines 23331–23459) |
| Standalone method file | `/opt/data/projects/Research/CompositionMethods/sound_method_SP-105_CRFBS.md` |
| This report | `/opt/data/projects/Research/CompositionMethods/report_SP-105.md` |
| Temp file (deleted) | `/opt/data/projects/Research/CompositionMethods/_temp_sp105.md` |

## Section Text (Complete Appended Content)

```
# Coupled Resonant Filter Bank Synthesis (CRFBS) (Sound Production Method SP-105)

### Source
Poirot, S., Kronland-Martinet, R., & Bilbao, S. (2023). "A Coupled Resonant Filter Bank for the Sound Synthesis of Nonlinear Sources." In *Proceedings of the 26th International Conference on Digital Audio Effects (DAFx23)*, Copenhagen, Denmark.

Also: Mathews, M. & Smith, J. O. "Methods for Synthesizing Very High Q Parametrically Well Behaved Two Pole Filters."

### Layer
absolute — Sound Production (Synthesis Engines)

### Description
Coupled Resonant Filter Bank Synthesis (CRFBS) models nonlinear vibrating objects (thin plates, crash cymbals, colliding structures) as a bank of N parallel second-order digital resonators that exchange vibrational energy through a controllable redistribution matrix. Each resonator represents one vibration mode (natural frequency ω_i, damping α_i) using the Mathews-Smith coupled-form complex filter — a numerically stable, constant-Q IIR structure with independent frequency and decay control.

Unlike standard linear modal synthesis (where modes oscillate independently and the output is a fixed weighted sum), CRFBS allows energy to flow between modes through a redistribution matrix M. When a mode's instantaneous power P_i(n) exceeds a threshold τ_i, the surplus power is proportionally redistributed to other modes according to matrix weights. This models the nonlinear mode coupling observed in real-world objects at moderate vibration amplitudes: delayed tonal components that grow over time (rather than decaying), spectral enrichment during impacts, energy cascades from low to high frequencies in crash cymbals, and the "pitch glide" of colliding plates — effects that independent linear modes cannot produce.

The method is perception-driven rather than physically exact: the coupling matrix is a design tool, not a physical PDE solution. This makes CRFBS computationally efficient (O(N) per sample per voice, no matrix inversions at runtime) while capturing the salient acoustic signatures of nonlinear sources. It fills the gap between linear modal synthesis (SP-003/SP-042), full FDTD simulation (SP-040), and wave digital filters (SP-051) — offering nonlinear mode interaction at modal-synthesis cost.

[Full technical mechanics, musical elements framework, UnitMatrix integration, and pitfalls sections as documented in the method file.]
```

## Technical Mechanics Summary

| Component | Equation / Formula |
|-----------|-------------------|
| Mode impulse response | h_i(t) = (1/ω_i) e^{-α_i t} sin(ω_i t) |
| Complex recurrence | z_i(n+1) = Z_i z_i(n) + u_i(n) |
| Z-parameter | Z_i = e^{-α_i/f_s} e^{jω_i/f_s} = X_i + jY_i |
| Coupled-form real/imag | x_i(n+1) = X_i·x̃_i(n) - Y_i·ỹ_i(n) + u_i(n); y_i(n+1) = Y_i·x̃_i(n) + X_i·ỹ_i(n) |
| Instantaneous power | P_i(n) = ½|x_i(n)² + y_i(n)²| |
| Energy transfer scaling | |z_i(n+1)| = √(|z_i(n)|² + 2T_i(n))·e^{-α_i/f_s} |
| Redistribution | t(n) = M·[p(n) - τ]_+ |
| Matrix construction | M_ij = ηλ·a_ij/(Σ_i a_ij) - λδ_ij |
| Stability | Σ_i T_i(n) ≤ 0 (== Σ_i M_ij ≤ 0) |
| Output | s(n) = Σ_i y_i(n) |
| Complexity | O(N) per sample |

## Quirks and Pitfalls Encountered

1. **LaTeX backslash double-escaping**: The write_file tool outputs raw content. When reading back, the file viewer shows `\\` for `\`, but the actual file content is correct single-backslash LaTeX. Verified by checking the diff output carefully.

2. **Summary table prefix format**: The existing SP table uses `|| **SP-NNN** | ...` with double-pipe at the start. My new row matches this exactly. No `||` normalization issue.

3. **Appended content separator**: The temp file started with `---` (YAML separator), which got concatenated with the previous section's last line during the append (no trailing newline at end of methods_db.md). Had to patch to separate it into its own line, then remove it entirely.

4. **SP number resolution**: The highest existing SP in the summary table was SP-104 (line 279), confirmed by scanning both sound_method_SP-*.md files (47 files up to SP-104) and report_SP-*.md files (36 files up to SP-104). SP-105 is the next available.

5. **Section insertion point**: The file is a mix of composition methods and SP methods in detailed sections. SP-104's detailed section starts at line 23066 within the file. The new SP-105 section was appended to the very end of the file.

## Verification

```
$ grep -c "SP-105" /opt/data/projects/Research/CompositionMethods/methods_db.md
2

$ wc -l /opt/data/projects/Research/CompositionMethods/methods_db.md
23459 /opt/data/projects/Research/CompositionMethods/methods_db.md
```

Two occurrences of SP-105 confirmed: 1 in the summary table, 1 in the detailed section header.

## Next Steps

- Implement `sound/synthesis/coupled_resonator.py` with the Python/NumPy class provided in the standalone file.
- Add tests for: (a) uncoupled mode → linear modal ring; (b) single-direction coupling; (c) stability guarantee; (d) energy conservation test (η=0 → zero coupling).
- Integrate with `produce()` workflow in `workflows/musicom_workflow.py` as a new production method.

## References

1. Poirot, S., Kronland-Martinet, R., & Bilbao, S. (2023). "A Coupled Resonant Filter Bank for the Sound Synthesis of Nonlinear Sources." DAFx23, Copenhagen, Denmark. [Online: www.dafx.de/paper-archive/2023/DAFx23_paper_42.pdf]
2. Mathews, M. & Smith, J. O. "Methods for Synthesizing Very High Q Parametrically Well Behaved Two Pole Filters." [CCRMA, Stanford]
3. Skare, K. & Abel, S. (2019). Real-Time Modal Synthesis of Crash Cymbals with GPU-Accelerated Modal Filterbank.
4. Ducceschi, M. & Touzé, C. (2022). Modal Resolution of the Föppl-von Kármán System with Coupling Coefficients.
5. Bilbao, S. (2009). *Numerical Sound Synthesis: Finite Difference Schemes and Simulation in Musical Acoustics*. Wiley.