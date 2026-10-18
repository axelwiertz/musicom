# Research Report: Method 119 — Tensor Decomposition Composition (TDC)

## Metadata

| Field | Value |
|-------|-------|
| Method ID | **119** |
| Method Name | Tensor Decomposition Composition |
| Acronym | TDC |
| Paradigm | **Rules-Based** |
| Layer | **concrete** |
| Date | 2026-10-18 |
| Agent | Hermes Agent (cron job) |

## Summary Table Row

```
|| **119** | concrete | Tensor Decomposition Composition (TDC) | **Rules-Based** | Pitch, Rhythm, Harmony, Structure, Texture | Moderate (Factor-guided) | Grid-Locked / Continuous | Macro / Low-Rank Core | $\mathcal{O}(R \cdot V \cdot T \cdot P)$ | Generates polyphonic music from CP/Tucker low-rank decomposition of a 3-way music tensor (voices × time × pitch). Factor matrices define voice character, rhythmic profile, and pitch vocabulary; core tensor controls their multiplicative interaction. Deterministic, designable, no-training counterpart to 085 NMF-C (2D→3D), 046 VAE-LSI (learned vs designed), and 097 MaxEnt-C (structure via low-rank rather than constraints). |
```

## Classification

### Paradigm: Rules-Based

All factor matrices (A, B, C) and the core tensor (G) are **explicitly designed** as structural templates by the composer or a higher-level planning method. No training, no stochastic sampling at decomposition time, no nature-inspired dynamics.

### Layer: concrete

Generates events that fill UnitMatrix cells. The reconstructed tensor entries decode directly to pitch/onset/duration/velocity values for each voice×time cell. The thresholded binary tensor maps to note-on/off events suitable for direct injection into the UnitMatrix composer.

This is an **algorithmic** method (not AI-driven) — the factors are designed, not learned.

## One-Line Description

Generates polyphonic music from CP/Tucker low-rank decomposition of a 3-way music tensor (voices × time × pitch); factor matrices encode voice character, rhythmic profile, and pitch vocabulary; the core tensor controls their interactions.

## Why This Method is Novel

TDC fills a gap not covered by any existing method in the DB:

1. **085 NMF-C** uses 2D matrix factorization (rank-2 decomposition of a 2D array). TDC uses 3D+ tensor decomposition (CP/Tucker), which captures voice×time×pitch interactions that are impossible in 2D.

2. **046 VAE-LSI** uses learned latent representations from autoencoder training. TDC's factors are *designed*, not learned — a fundamentally different epistemological approach.

3. **097 MaxEnt-C** captures structure via constrained entropy maximization. TDC captures structure via low-rank approximation — the algebraic dual approach.

4. All Nature-Led and Stochastic methods (048 RBMPD, 053 LFC, 040 Perlin) generate events from random processes. TDC is entirely deterministic from designed factors.

5. **024 Additive Mass** operates in the frequency/synthesis domain. TDC operates in the symbolic/polyphonic domain.

6. Methods like 069 CWCC, 076 PTM, 077 DBUC generate one-dimensional sequences. TDC generates the full multi-voice, multi-pitch tensor in one algebraic operation.

## Musical Elements Framework

| Element | Description |
|---------|-------------|
| **PITCH** | Factor matrix $\mathbf{C}$ defines pitch vocabulary per component. Multi-component interaction via core tensor yields chord structures. |
| **RHYTHM** | Factor matrix $\mathbf{B}$ encodes onset patterns. Periodic patterns = meter; clustered blocks = motifs; exponentials = resonance. |
| **HARMONY** | Emerges from simultaneous $\mathbf{c}_r$ vectors with overlapping pitches. Core tensor $\mathcal{G}$ controls co-activation. |
| **STRUCTURE** | Block-diagonal tensor form with per-section factor triplets. Factor sharing = development; replacement = contrast. |
| **TEXTURE** | Tensor density and rank $R$. Low rank + low density = pointillistic; high rank + high density = dense polyphonic mass. |

## UnitMatrix Integration

- **Voices** = Tensor mode 1. Slice $\mathcal{X}_{v,:,:}$ = complete piano-roll for voice $v$.
- **Sections** = Block-diagonal time structure. Each section has independent factor triplets.
- **Cells** = Thresholded entries $\mathcal{X}_{v,t,p} > \theta$ → note-on events.
- **Validation**: The thresholded binary tensor is fed into the UnitMatrixComposer via `set_unit()`/`fill_voice_section()`, then validated for zero-drift.

## Source References

1. Hitchcock, F. L. (1927). "The expression of a tensor or a polyadic as a sum of products." *Journal of Mathematics and Physics* 6(1-4), 164–189. — CP decomposition origin.
2. Tucker, L. R. (1966). "Some mathematical notes on three-mode factor analysis." *Psychometrika* 31(3), 279–311. — Tucker decomposition.
3. Carroll, J. D. & Chang, J. J. (1970). "Analysis of individual differences in multidimensional scaling via an N-way generalization of 'Eckart–Young' decomposition." *Psychometrika* 35(3), 283–319. — CANDECOMP/PARAFAC.
4. Kolda, T. G. & Bader, B. W. (2009). "Tensor decompositions and applications." *SIAM Review* 51(3), 455–500. — Comprehensive survey.
5. Bro, R. & Kiers, H. A. L. (2003). "A new efficient method for determining the number of components in PARAFAC models." *Journal of Chemometrics* 17(5), 274–286. — CORCONDIA diagnostic.

## Key Insights

1. **Low-rank = compositional structure**: In music, the "low rank" of the voice×time×pitch tensor corresponds to the fact that musical textures are built from a small number of simultaneous layers (components).

2. **Factor design is composition**: Designing $\mathbf{A}$ (voice participation), $\mathbf{B}$ (rhythmic profile), and $\mathbf{C}$ (pitch vocabulary) IS the creative act. The tensor reconstruction is just the algebraic expansion of that design.

3. **CP independence vs Tucker interaction**: CP = independent texture layers (like separate instrumental parts that don't interact); Tucker = coupled layers where the core tensor enriches harmonic interaction.

4. **The quantization gap**: Real-valued → binary is the hardest step. A fixed threshold produces the wrong texture density. Adaptive per-voice thresholding with a sparsity target is essential.

## Candidate Code Path

`generators/tensor_decomposition_composer.py`

This module would implement:
- `cp_als()` — CP decomposition via alternating least squares
- `tucker_hosvd()` — Tucker via higher-order SVD
- `reconstruct_cp()` / `reconstruct_tucker()` — tensor reconstruction
- `threshold_tensor()` — adaptive binary thresholding
- `TensorDesigner` class — DSL for specifying factor matrices
- `SectionAssembler` — block-diagonal section structure
- Integration with `UnitMatrixComposer` validation gate

## Pitfalls Encountered & Qirks

1. **LaTeX escaping in methods_db.md**: The `\cdots` in the summary row was corrupted when using sed with `\cdot` (unescaped backslashes). Had to use plain text `O(R*V*T*P)` as intermediate then patch to add LaTeX back.

2. **sed line duplication**: First sed attempt to insert the row after line 128 resulted in `\u0004ot` corruption. The subsequent fix doubled the line content. Had to do `sed -i '129s/.*/...'` to overwrite completely.

3. **File content appending**: The SP-117 sound method's final line had no trailing newline, so `cat >>` appended my method's summary row to the same line. Fixed via patch to split the concatenated content.

4. **Summary row format**: Following the existing pattern of `|| **<ID>** | concrete | Name (Acr) | **Paradigm** | ... |` with `||` prefix. Note that the file viewer adds an extra `|` in the line number gutter display.

## Verification

| Check | Result |
|-------|--------|
| Summary row added to table (line 129) | ✓ Present: `|| **119** | concrete | TDC ...` |
| Detailed section appended (end of file) | ✓ All sections present: Source, Layer, Paradigm, Description, Musical Elements, UnitMatrix, Pitfalls, Code Path |
| Standalone method file created | ✓ `method_119_TDC.md` (11,067 bytes) |
| Report file created | ✓ `report_119.md` (this file) |
| wc -l before | 26,446 lines (original) |
| wc -l after | 26,546 lines (+100 additional: ~99 for the detailed section + 1 for the summary row) |

## Next Free ID

**120** — the next method number after 119.

## Appendices

### A. Complete Appended Method Section Text

The following text was appended to `methods_db.md` after line 129 (summary table row) and as the last section of the file:

```
|| **119** | concrete | Tensor Decomposition Composition (TDC) | **Rules-Based** | ... |

### Source
Hitchcock, F. L. (1927). ... — Tucker, L. R. (1966). ... — Carroll, J. D. & Chang, J. J. (1970). ... — Kolda, T. G. & Bader, B. W. (2009). ...

### Layer
**concrete** — generates events that fill UnitMatrix cells. ...

### Paradigm
**Rules-Based** — all factor matrices (A, B, C) and the core tensor (G) are explicitly designed...

### Description
**Tensor Decomposition Composition (TDC)** represents a full polyphonic composition as a 3-way tensor X in R^{V×T×P}...

### Musical Elements Framework
- PITCH: ...
- RHYTHM: ...
- HARMONY: ...
- STRUCTURE: ...
- TEXTURE: ...

### UnitMatrix Integration
- Voices: Mode 1 of tensor...
- Sections: Block-diagonal...
- Cells: Individual entries...

### Pitfalls
- CP rank selection...
- Tucker core explosion...
- Quantization gap...
- Sign problem...
- Sparsity hallucination...
- Computational scaling...

### Candidate code path
generators/tensor_decomposition_composer.py
```

### B. File Listing

```
methods_db.md          — Summary table (line 129) + detailed section (end of file)
method_119_TDC.md      — Standalone full write-up (11,067 bytes)
report_119.md          — This report (primary record)
```