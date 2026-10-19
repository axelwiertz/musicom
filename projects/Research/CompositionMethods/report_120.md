# Registration Report — Method 120: Random Matrix Theory Composition (RMTC)

## Basic Information

| Field | Value |
|---|---|
| **ID** | 120 |
| **Method Name** | Random Matrix Theory Composition |
| **Acronym** | RMTC |
| **Paradigm** | Stochastic |
| **Layer** | concrete |
| **One-line Description** | Generates composition parameters from eigenvalue statistics of random matrices (GOE/GUE/GSE): Wigner semicircle law drives pitch distribution; Wigner surmise (level repulsion) drives melodic intervals; Dyson-Mehta spectral rigidity drives chord voicing balance; Tracy-Widom extremes drive climax/range; ensemble-type switching drives macro-form. |
| **Date** | 2026-10-19 |
| **Registration Agent** | Hermes Cron (automated research) |

## Summary Table Row (as inserted)

```
|| **120** | concrete | Random Matrix Theory Composition (RMTC) | **Stochastic** | Pitch, Rhythm, Harmony, Structure, Texture | Weak (Eigenvalue-guided) | Continuous / Fluid | Meso / Spectral | $\mathcal{O}(N^3)$ | Generates composition parameters from eigenvalue statistics of random matrices (GOE/GUE/GSE): Wigner semicircle law drives pitch distribution; Wigner surmise (level repulsion) drives melodic intervals; Dyson-Mehta spectral rigidity drives chord voicing balance; Tracy-Widom extremes drive climax/range; ensemble-type switching drives macro-form. Stochastic-spectral counterpart to 002 Markov / 048 RBMPD / 085 NMF-C. |
```

## Database Changes

| Metric | Before | After | Delta |
|---|---|---|---|
| methods_db.md line count | 26,850 | 26,967 | +117 |
| Summary table rows (alg. methods) | 119 | 120 | +1 |
| method_\*.md file count | 72 | 73 | +1 |
| report_\*.md file count | ~50 | 51 | +1 |

## Files Created

| File | Description |
|---|---|
| `/opt/data/projects/Research/CompositionMethods/method_120_RMTC.md` | Full standalone method write-up (290+ lines): extended math, Python implementation sketch with Goe/GUE/GSE samplers, pitch mapping, interval generation, full compose_rmtc pipeline, Tracy-Widom numerical evaluation notes, references. |
| `/opt/data/projects/Research/CompositionMethods/report_120.md` | This report — the PRIMARY record. |

## Detailed Method Section (appended to methods_db.md)

The following complete section was appended to `methods_db.md` after the summary table:

```
### Source
[Wigner, Dyson, Mehta, Tracy-Widom, Bohigas-Giannoni-Schmit references]

### Layer
**concrete** — random eigenvalue ensemble statistics are sampled to produce concrete pitch values (scaled and quantized to scale degrees), inter-onset intervals (from eigenvalue gaps), chord voicings (from spectral rigidity), and macro-form templates (from ensemble-type switching).

### Description
**Random Matrix Theory Composition (RMTC)** treats musical parameters as the eigenvalue statistics of large random matrices drawn from the classical invariant ensembles (GOE/GUE/GSE)...

Key mathematical components:
1. **Wigner Semicircle Law** — eigenvalue density ρ(λ) = (1/2π)√(4−λ²) → pitch distribution peaking at tonic
2. **Wigner Surmise** — P_β(s) ∝ s^β e^{-b s²} → melodic interval distribution with level repulsion
3. **Dyson-Mehta Spectral Rigidity** — ⟨Δ₃(L)⟩ ≈ (1/π²)log L + c → chord voicing balance
4. **Tracy-Widom Law** — F_β(t) for largest eigenvalue → registral climax
5. **Ensemble switching** (GOE→GUE→GSE) → macro-form arc
6. **Dyson Brownian Motion** — smooth section transitions

### Musical Elements Framework
[PITCH: semicircle → tonic-weighted distribution; RHYTHM: eigenvalue gaps → IOIs; HARMONY: simultaneous eigenvalues + spectral rigidity → balanced voicing; STRUCTURE: per-section ensemble tuple trajectory; TEXTURE: matrix dimension N → density]

### UnitMatrix Integration
[Per-section matrix sampling → eigenvalue set → per-voice pitch seeds + per-voice interval contour from spacings → MusicEvents]

### Pitfalls
1. Eigenvalue scaling sensitivity — always normalise to unit variance
2. Determinism vs stochasticity — fix seed for reproducibility
3. Ensemble boundary transitions — use Dyson Brownian motion bridges
4. Matrix diagonalisation cost — keep N in 6–20 for efficiency
5. No fine-grained pitch control — combine with 095 CTC for motivic constraints
6. Eigenvector interpretation — map squared components to velocity
7. Overly uniform spacing — use Poisson spacing for aleatoric styles
```

## Classification Details

| Attribute | Classification | Rationale |
|---|---|---|
| **Paradigm** | Stochastic | RMT is fundamentally about the *statistical* properties of random matrix eigenvalues; the generative process samples from random matrix ensembles and maps the resulting random eigenvalue statistics to musical parameters. No deterministic rewrite rules, no nature-inspired dynamics, no learned neural parameters. |
| **Layer** | concrete | The method directly produces concrete pitch values (scale-quantized MIDI notes), inter-onset intervals (from eigenvalue gaps), chord voicings (from simultaneous eigenvalues), and per-voice contours that fill UnitMatrix cells. It is NOT abstract (pitch-class sets without register) and NOT absolute (sound production). |
| **Tonal Gravity** | Weak (Eigenvalue-guided) | The semicircle law ensures pitch distribution peaks at the center (tonic region), but there is no explicit HOME/LIFT/TENSE/TURN functional-harmony enforcement. Tonal gravity emerges statistically, not from rule-based cadences. |
| **Metric Binding** | Continuous / Fluid | Eigenvalue gaps are real-valued (continuous); IOIs derived from them are naturally continuous. Optional quantization to a grid can be applied post-hoc. |
| **Memory Depth** | Meso / Spectral | Memory is limited to the current matrix sample's eigenvalue set — the spectral statistics within a section. No long-range memory beyond the section boundary unless Dyson Brownian motion bridges are used. |
| **Time Complexity** | 𝒪(N³) | Symmetric eigenvalue decomposition (tridiagonal QR / divide-and-conquer) is 𝒪(N³) for an N×N matrix. For N in 6–20 (typical section vocabulary size), this is negligible (~10³–10⁴ operations). |

## Evaluation

### Novelty Assessment

RMTC is genuinely distinct from all 119 existing methods in the database:

- **Distinct from 002 Markov** (probabilistic transitions over discrete states): RMTC uses continuous eigenvalue statistics, not transition matrices.
- **Distinct from 048 RBMPD** (Gaussian Brownian motion diffusion): RMTC uses eigenvalue repulsion with Wigner-Dyson statistics, not simple diffusion.
- **Distinct from 051 SGLM** (deterministic graph Laplacian): RMTC uses random matrices, not fixed graphs.
- **Distinct from 053 LFC** (power-law interval distribution): RMTC uses bounded semicircle + Wigner surmise, not unbounded Lévy.
- **Distinct from 085 NMF-C** (non-negative factorization): RMTC uses matrix *statistics*, not matrix *factorization*.
- **Distinct from 097 MaxEnt-C** (maximum-entropy Potts model): RMTC uses eigenvalue repulsion, not pairwise interaction constraints.

No existing method in the database uses random matrix theory, eigenvalue level repulsion, spectral rigidity, or Tracy-Widom statistics as generative mechanisms.

### Quirks and Pitfalls Encountered

1. **Table formatting**: The last rows of the summary table (101–119) use `||` (double pipe) prefix instead of the canonical `|` (single pipe) used by rows 001–100. Method 119's row had `|||` (triple pipe). My patch text inadvertently included line numbers from the read_file view, requiring sed cleanup. The final table renders correctly but has formatting inconsistency in pipe counts.

2. **Section header spacing**: The table-to-section transition uses `||||### Source` instead of a clean separator. The detailed section appending worked correctly.

3. **File size**: The methods_db.md is 26,967 lines / 2.76 MB — a substantial file. Appending at the end is reliable.

### Candidate Code Path

The RMTC method would live in:
```
generators/eigenvalue/rmtc.py
```
or as a submodule of the stochastic generators:
```
generators/stochastic/rmtc.py
```

Since it generates pitch/rhythm/harmony content for the concrete layer, it belongs under `generators/`. The eigenvalue decomposition utility could also live in `utilities/random_matrix.py` for shared use with other methods that might need spectral computations.

## Next Free ID

The next free algorithmic method ID after this registration is **121**.