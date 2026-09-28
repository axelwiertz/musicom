# Report 099 — Self-Similarity Matrix Composition (SSMC)

## Summary
- **Method ID**: 099
- **Method Name**: Self-Similarity Matrix Composition (SSMC)
- **Paradigm**: Rules-Based
- **Layer**: abstract
- **Acronym**: SSMC
- **One-line description**: Designs macro-form repetition structure as a self-similarity matrix (SSM) — pairwise similarity targets between all time positions — then solves the inverse problem to produce a feature sequence whose SSM matches the target, decoded into per-bar profiles for concrete generators.

## Summary Table Row (inserted at line 109)
| **099** | abstract | Self-Similarity Matrix Composition (SSMC) | **Rules-Based** | Structure, Texture, Pitch, Rhythm | Weak (Template-guided) | Grid-Locked / Continuous | Macro / Form | $\mathcal{O}(N^2 \cdot M)$ | Designs macro-form repetition structure as a self-similarity matrix (SSM) — pairwise similarity targets between all time positions. Solves the inverse problem: optimize a feature sequence whose SSM matches the target, then decode to per-bar feature profiles. Novelty curve identifies section boundaries for UnitMatrix layout. First abstract-layer form-design method: feeds rules/ssm_composition.py. |

## Classification Details
| Attribute | Value |
|-----------|-------|
| Tonal Gravity | Weak (Template-guided) — the SSM encodes similarity in chroma space; tonal centers emerge from chroma distribution per section, not from explicit tonic enforcement |
| Metric Binding | Grid-Locked / Continuous — the SSM operates over discrete time positions (bars/beats); within-bar time can be continuous |
| Memory Depth | Macro / Form — the SSM captures the entire piece's repetition structure in a single $N \times N$ matrix |
| Time Complexity | $\mathcal{O}(N^2 \cdot M)$ — SSM construction $\mathcal{O}(N^2 d)$, optimization over $M$ steps |
| Primary Elements | Structure, Texture, Pitch, Rhythm |

## Line Count
- Before: 21212 lines
- After: 21309 lines
- Delta: +97 lines (+1 table row + 96 lines of method section)

## Standalone File Path
`/opt/data/projects/Research/CompositionMethods/method_099_SSMC.md`

## Report File Path
`/opt/data/projects/Research/CompositionMethods/report_099.md`

## Candidate Code Path
`rules/ssm_composition.py` — alongside `rules/subset_network.py` in the abstract layer. The method produces an abstract structural blueprint (feature vectors per bar/voice) that feeds concrete generators (any concrete-layer method) for note-level realization.

## Appended Method Section Text
The complete method section appended to `methods_db.md` (starting at line 21311 after table row insert at 109):

```
### **099** | Self-Similarity Matrix Composition (SSMC) | **Rules-Based** | Structure, Texture, Pitch, Rhythm | Weak (Template-guided) | Grid-Locked / Continuous | Macro / Form | $\mathcal{O}(N^2 \cdot M)$ target matching; $\mathcal{O}(N^2)$ SSM construction

### Source
Foote, J. (1999). ... Jhamtani & Berg-Kirkpatrick (2019). ... Hager et al. (2024). ... Lattner et al. (2016). ...

### Layer
**abstract** — designs the macro-form repetition structure encoded as a self-similarity matrix (SSM). Transposition- and register-invariant structural blueprint. Feeds concrete generators.

### Paradigm
**Rules-Based** — deterministic structural template. Constrained optimization with deterministic matching criteria.

### Description
[Full description of SSMC including structural encoding, generative workflow, mathematical formalization, and optimization strategies]

### Musical Elements Framework
[PITCH, RHYTHM, HARMONY, STRUCTURE, TEXTURE analysis using SSM framework]

### UnitMatrix Integration (Voices & Sections)
[Multi-voice feature vectors, section boundaries from novelty curve, cell decoding strategies]

### Pitfalls
[7 pitfalls: inverse problem ill-posedness, feature engineering, boundary precision, optimization cost, granularity limitations, corpus dependency, similarity threshold sensitivity]
```

## Quirks / Pitfalls Hit
1. **Summary table prefix**: The existing summary table rows have a leading `|` (single pipe) prefix. The `read_file` output displays `||` prefix but the actual file content has `|`. Verified via `cat -A`.
2. **LaTeX backslash issue**: The `patch` tool failed 3 times when trying to match `$\mathcal{O}$` — likely due to backslash escaping issues with the dollar-sign LaTeX delimiters. Used `sed -i` with a line number (`108a`) to insert the new row instead.
3. **File size validation**: The methods_db.md is ~2MB (21309 lines). The `patch` tool's fuzzy matching may have issues with such large files, especially when earlier reads used offset/limit pagination (see `_warning` about re-reading the whole file).

## Next Free ID
099 (just used). Next free algorithmic method ID: **100**.
Next free human method HC ID: HC-049 (max HC methods go up to HC-048).
Next free sound production SP ID: SP-098 (max SP is SP-097).

## Method Coverage Summary
SSMC fills a gap in the methods DB: there was no method specifically for designing repetition/form structure via pairwise similarity targets. Existing methods that touch structure/form include:
- 001 Skeleton-First (form-first drafting, but no explicit repetition encoding)
- 026 DPSM (phase-shift minimalism, uses phasing not SSM)
- 034 PCFG (hierarchical grammar for form, not pairwise similarity)
- 098 MOEPC (Pareto front as form, not similarity-based)

SSMC is the first method to use the self-similarity matrix (Foote 1999, standard MIR tool) as a *generative* blueprint for controllable repetition/contrast structure, and the second **abstract**-layer method (after 095 CTC).