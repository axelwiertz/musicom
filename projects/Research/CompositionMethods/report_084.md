# Report — Method 084: Zipf–Mandelbrot Rank–Frequency Composition (ZMRC)

## Summary
- **Method name**: Zipf–Mandelbrot Rank–Frequency Composition
- **Acronym**: ZMRC
- **ID**: 084 (dynamically resolved: max existing algorithmic ID = 083 QTSC → 084)
- **Paradigm**: Stochastic
- **LAYER**: **concrete** (emits note/chord events into UnitMatrix cells; feeds `generators/`)
- **One-line description**: Treats the piece as a text over a ranked musical vocabulary and samples tokens from a Zipf–Mandelbrot rank–frequency law $f(r) \propto (r+q)^{-s}$ — rank 1 (tonic/HOME) saturates, the long tail (chromatic/TENSE) is rare, $s$ sets vocabulary richness, $q$ sets dominance, and the ranking order is the tonal grammar — reproducing the same rank–frequency signature that separates real music from random (Manaris 2003; Zanette 2006; Levitin 2012).

## ID resolution
- Scanned the summary table (`| **NNN** |` rows) at top of `methods_db.md`. Highest numeric algorithmic ID: **083** (Aperiodic Quasicrystal Tiling Composition, QTSC).
- Cross-checked standalone `method_*.md` files: `method_083_QTSC.md` was the highest algorithmic (`method_ABS_abstract-layer.md` is a layer doc, not an ID).
- Cross-checked `report_*.md` files: `report_083.md` confirmed max = 083. (Report files for SP-*, HC-*, and date-stamped registration files excluded — they are not algorithmic IDs.)
- Next ID = **084**. Collision-free: grep for Zipf/rank-frequency/Mandelbrot-Zipf/Manaris/lexical-richness surfaced only a tangential reference to Levitin 2012 rhythm spectra in the 053 LFC reference list — **no existing rank–frequency method**.
- Known pre-existing gap: ID 058 absent (NODE-CTC unregistered). Not touched; 084 is clean.

## Classification details
| Field | Value |
|---|---|
| Method ID | 084 |
| Layer | concrete |
| Method Name | Zipf–Mandelbrot Rank–Frequency Composition (ZMRC) |
| Paradigm | Stochastic |
| Primary Elements | Pitch, Rhythm, Harmony, Structure, Texture |
| Tonal Gravity | Strong (Ranking-imposed) |
| Metric Binding | Grid-Locked / Continuous |
| Memory Depth | Macro / Vocabulary |
| Time Complexity | $\mathcal{O}(N)$ |

## Summary-table row (inserted at line 94, after 083, before the Sound Production header)
```
| **084** | concrete | Zipf–Mandelbrot Rank–Frequency Composition (ZMRC) | **Stochastic** | Pitch, Rhythm, Harmony, Structure, Texture | Strong (Ranking-imposed) | Grid-Locked / Continuous | Macro / Vocabulary | $\mathcal{O}(N)$ | Treats the piece as a text over a ranked musical vocabulary and samples tokens from a Zipf–Mandelbrot rank–frequency law $f(r) \propto (r+q)^{-s}$. Rank 1 = tonic/HOME (saturating), long tail = chromatic/TENSE (rare); exponent $s$ = vocabulary richness, shift $q$ = dominance ceiling, ranking order = tonal grammar. Macro-form = a per-section trajectory in $(s,q,\text{ranking})$ space. Empirical basis: pitch/rhythm/chord distributions in real music are Zipfian (Manaris 2003; Zanette 2006; Levitin 2012). Statistical foil to 002 Markov (marginal vs conditional) and 053 Lévy (rank vs step-length). |
```

## Line counts
- **Before**: 17020 lines
- **After (append)**: 17092 lines (+72 detail-section append)
- **After (summary row)**: 17093 lines (+1 summary-table row via patch)
- **Delta**: +73 lines total

## Files
- **Standalone file**: `/opt/data/projects/Research/CompositionMethods/method_084_ZMRC.md`
- **Report file**: `/opt/data/projects/Research/CompositionMethods/report_084.md`
- **DB**: `/opt/data/projects/Research/CompositionMethods/methods_db.md` (summary row at line 94 + full section at line 17020)

## Candidate code path
- **Module**: `generators/zipf_rank_frequency.py` (new, alongside existing generator modules).
- **Public API sketch**: `zipf_mandelbrot_pmf(V, s, q)` (normalized rank mass); `fit_slope_mle(hist, q)` (truncated-Zipf ML estimator); `build_vocabulary(ranking)` (rank map); `sample_events(ranking, s, q, n, seed)` (alias-table sampler); `compose_section(base, s, q, n, seed)` (decode to pitch list).
- **Abstract-layer note**: the ranking order (rank 1 = tonic, rank bands = HOME/LIFT/TENSE/TURN) is a transposition/register-invariant subset hierarchy that could feed `rules/subset_network.py` (ABS-001..005) as a rank-ordered pattern network; documented as concrete because it samples concrete events.

## Complete method section text appended
Headers: ### Source, ### Layer, ### Description, ### Musical Elements Framework, ### UnitMatrix Integration (Voices & Sections), ### Pitfalls, ### Comparison With Related Methods, ### References. (Identical to `_temp_method_084.md` content, now folded into `methods_db.md` at line 17020 and `method_084_ZMRC.md`.)

## Quirks / pitfalls hit
1. **Table row placement**: the composition-method summary table ends at line 93 (`083`), immediately followed by `# Sound Production Methods Framework`. The new `084` row was inserted via `patch` (replace of the `083` row tail + following header), not appended — appending would have landed the row inside the Sound Production section. Verified at line 94.
2. **LaTeX escape check**: re-read line 94 after patching — single backslashes `$\mathcal{O}(N)$`, `$f(r) \propto (r+q)^{-s}$`, `$(s,q,\text{ranking})$`; grep for `\\mathcal|\\propto|\\text` returned **0 matches** (no double-escape). Clean.
3. **`||` prefix check**: new row starts with single `|`. Clean.
4. **Not `\propto` vs `\sim`**: used `\propto` for the rank–frequency law (correct proportionality) rather than `\sim`; consistent with existing DB rows.
5. **Dimensionality/gap exploited**: DB has power-law *step-length* methods (053 Lévy) and *marginal-free* conditional methods (002 Markov), but **no rank–frequency (Zipf–Mandelbrot) marginal-law method**. ZMRC is the genuinely new statistical-linguistics addition, agnostic to the Lévy/Markov prior art.
6. **Sparse-method rule**: captured in Pitfalls #6 (pair with 026 DPSM / sustained pad / walking bass when ZMRC is the sole rhythmic generator, per the Method Hybridization rule).
7. **Note**: `wc -l` reported the file as "modified since last read" in the patch response — this is the expected append via `cat >>` from step 5b, not an external editor. Re-read the row after patching to confirm correctness.

## Next free ID
**085**
