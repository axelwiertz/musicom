# Report — Method 085: Non-negative Matrix Factorization Composition (NMF-C)

## Summary
- **Method name**: Non-negative Matrix Factorization Composition
- **Acronym**: NMF-C
- **ID**: 085 (dynamically resolved: max existing algorithmic ID = 084 ZMRC → 085)
- **Paradigm**: AI-Driven
- **LAYER**: **concrete** (learns a parts dictionary $W$ and emits note/chord events into UnitMatrix cells; feeds `generators/`)
- **One-line description**: Factors a piano-roll/chromagram/spectrogram $V \approx WH$ into a non-negative parts dictionary $W$ (learned chord/PC-set voicings, rhythmic cells) and an activation matrix $H$ (onset-energy envelopes). Non-negativity forces additive, parts-based atoms — the learned $W$ is the "style", a designed/structured $H$ is the "piece". Rank $K$ = vocabulary/harmonic complexity; block structure of $H$ = macro-form; co-activation = harmony; activation sparsity = texture.

## ID resolution
- Scanned the summary table (`| **NNN** |` rows) at top of `methods_db.md`. Highest numeric algorithmic ID: **084** (Zipf–Mandelbrot Rank–Frequency Composition, ZMRC).
- Cross-checked standalone `method_*.md` files: `method_084_ZMRC.md` highest algorithmic (`method_ABS_abstract-layer.md` is a layer doc, not an ID).
- Cross-checked `report_*.md` files: `report_084.md` confirmed max = 084.
- Next ID = **085**. Collision-free: grep for NMF / non-negative / matrix-factorization / tensor-decomposition / PARAFAC / Tucker / SVD / PCA / ICA surfaced no existing matrix-factorization composition method (only an unrelated "nonnegative symmetric matrices" Fiedler reference in 051 SGLM and SP-030 vector-phase shaping).
- Known pre-existing gap: ID 058 absent (NODE-CTC unregistered). Not touched; 085 is clean.

## Classification details
| Field | Value |
|---|---|
| Method ID | 085 |
| Layer | concrete |
| Method Name | Non-negative Matrix Factorization Composition (NMF-C) |
| Paradigm | AI-Driven |
| Primary Elements | Pitch, Rhythm, Harmony, Structure, Texture |
| Tonal Gravity | Strong (Learned-basis) |
| Metric Binding | Grid-Locked / Continuous |
| Memory Depth | Macro / Corpus |
| Time Complexity | $\mathcal{O}(I \cdot K \cdot F \cdot T)$ |

## Summary-table row (inserted at line 95, after 084, before the Sound Production header)
```
| **085** | concrete | Non-negative Matrix Factorization Composition (NMF-C) | **AI-Driven** | Pitch, Rhythm, Harmony, Structure, Texture | Strong (Learned-basis) | Grid-Locked / Continuous | Macro / Corpus | $\mathcal{O}(I \cdot K \cdot F \cdot T)$ | Factors a piano-roll/chromagram/spectrogram $V \approx WH$ into a non-negative parts dictionary $W$ (learned chord/PC-set voicings, rhythmic cells) and an activation matrix $H$ (onset-energy envelopes). Non-negativity forces additive, parts-based atoms — the learned $W$ is the "style", a designed/structured $H$ is the "piece". Rank $K$ = vocabulary/harmonic complexity; block structure of $H$ = macro-form; co-activation = harmony; activation sparsity = texture. The factorization ancestor of 046 VAE / 072 NFC / 074 RBM-C, with the Smaragdis-Brown transcription lineage; linear non-negative foil to the learned-transition 054 ATS. |
```

## Line counts
- **Before (append)**: 17187 lines
- **After (detail-section append via `cat >>`)**: 17263 lines (+76)
- **After (summary row via patch)**: 17264 lines (+1)
- **Delta**: +77 lines total

## Files
- **Standalone file**: `/opt/data/repos/musicom/projects/Research/CompositionMethods/method_085_NMFC.md`
- **Report file**: `/opt/data/repos/musicom/projects/Research/CompositionMethods/report_085.md`
- **DB**: `/opt/data/repos/musicom/projects/Research/CompositionMethods/methods_db.md` (summary row at line 95 + full section at line 17188)

## Candidate code path
- **Module**: `generators/nmf_composition.py` (new, alongside existing generator modules).
- **Public API sketch**: `nmf_kl(V, K, n_iter, seed)` (KL multiplicative updates), `nmf_euclid(V, K, n_iter, seed)` (squared-Euclidean variant), `sparse_activation(H, lam)` (L1 proximal), `decode_events(W, H, pitch_map, threshold)` (argmax-decode atoms to (pitch, onset, velocity)).
- **Abstract-layer note**: the learned basis dictionary $W$ is a set of transposition/register-invariant pitch-class subsets — exactly the objects `rules/subset_network.py` (ABS-001..005) manipulates. Each basis column can seed a PatternNetwork walk, so NMF-C has a clean abstract-layer affinity; documented as concrete because it emits events.

## Complete method section text appended
Headers: ### Source, ### Layer, ### Description, ### Technical Mechanics, ### Musical Elements Framework, ### UnitMatrix Integration (Voices & Sections), ### Pitfalls, ### Comparison With Related Methods, ### References. (Identical to `_temp_method_085.md` content, now folded into `methods_db.md` at line 17188 and expanded in `method_085_NMFC.md`.)

## Quirks / pitfalls hit
1. **Table row placement**: the composition-method summary table ends at line 94 (`084`), immediately followed by `# Sound Production Methods Framework`. The new `085` row was inserted via `patch` (replace of the `084` row + following header), not appended — appending would have landed the row inside the Sound Production section. Verified at line 95.
2. **LaTeX escape check**: re-read line 95 after patching — single backslashes `$\mathcal{O}(I \cdot K \cdot F \cdot T)$`, `$V \approx WH$`. Grep for `\\mathcal`, `\\propto`, `\\text`, `\\odot` returned **0 matches** (no double-escape). Clean.
3. **`||` prefix check**: grep for `^|| **085` returned **0 matches**; new row starts with single `|`. Clean.
4. **Paradigm placement rationale**: classified **AI-Driven** (learned factorization, corpus-trained) rather than Rules-Based or Stochastic — consistent with how the DB tags the other learned-representation methods (046 VAE, 072 NFC, 074 RBM-C, 075 SOM-C), which are all AI-Driven. The method itself is deterministic per seed and linear, but its "intelligence" is the learned basis dictionary.
5. **Dimensionality/gap exploited**: DB has *learned non-linear* latent methods (VAE, flow, RBM, SOM) and *statistical marginal-law* methods (084 ZMRC), but **no linear matrix-factorization (parts-based) method**. NMF-C fills the "linear learned representation" gap and is the natural factorization ancestor of the deep latent family, grounded in the well-established Smaragdis–Brown transcription lineage.
6. **`_warning` on patch**: the patch tool warned the file was "modified since last read" — this is the expected `cat >>` append from step 5b, not an external editor. Re-read lines 94–96 after patching to confirm the row landed correctly.
7. **Note**: `wc -l` reported 17187 before append (report_084 said 17093 + SP-method appends since then — the DB grows daily via the sound job; the number is current as of this run, not an error).

## Next free ID
**086**
