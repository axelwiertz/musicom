# Report — Method 087: Multiple Viewpoint Systems Composition (MVS-C)

## Summary
- **Method name**: Multiple Viewpoint Systems Composition
- **Acronym**: MVS-C
- **ID**: 087 (dynamically resolved: max existing algorithmic ID = 086 HMM-C → 087)
- **Paradigm**: Stochastic
- **LAYER**: **concrete** (emits note/onset/duration events into UnitMatrix cells via sampling/argmax-decoding the product-of-experts next-event distribution; feeds `generators/`)
- **One-line description**: Composes by combining many specialized statistical predictors (viewpoints: pitch, pitch-interval, contour, scale-degree, onset-interval, duration, metric-position, chord — plus linked product viewpoints) into one product-of-experts distribution over the next event, then sampling or argmax-decoding it. Backoff with PPM* escape adapts context order automatically; a long-term corpus model (style) and a short-term within-piece model (structure/repetition) are blended in log space (IDyOM). Entropy-based viewpoint selection drops redundant features.

## ID resolution
- Scanned the summary table (`| **NNN** |` rows) at top of `methods_db.md`. Highest numeric algorithmic ID: **086** (Hidden Markov Model Latent-State Composition, HMM-C), at table row line 96.
- Cross-checked standalone `method_*.md` files: `method_086_HMM-C.md` is highest.
- Cross-checked `report_*.md` files: `report_086.md` confirmed max = 086.
- Historical gaps noted: 058 (NODE-CTC) remains unregistered — pre-existing, not touched.
- Next ID = **087**. Collision-free: grep for "multiple viewpoint" / "MVS" / "IDyOM" / "Pearce" / "Conklin" surfaced NO existing entry in the DB.

## Classification details
| Field | Value |
|---|---|
| Method ID | 087 |
| Layer | concrete |
| Method Name | Multiple Viewpoint Systems Composition (MVS-C) |
| Paradigm | Stochastic |
| Primary Elements | Pitch, Rhythm, Harmony, Structure, Texture |
| Tonal Gravity | Strong (Ensemble-constrained) |
| Metric Binding | Grid-Locked / Continuous |
| Memory Depth | Meso / Variable-Order Context |
| Time Complexity | $\mathcal{O}(N \cdot k)$ amortized, $\mathcal{O}(N \cdot k \cdot V)$ naive |

## Summary-table row (inserted at line 97, after 086, before the Sound Production header)
```
| **087** | concrete | Multiple Viewpoint Systems Composition (MVS-C) | **Stochastic** | Pitch, Rhythm, Harmony, Structure, Texture | Strong (Ensemble-constrained) | Grid-Locked / Continuous | Meso / Variable-Order Context | $\mathcal{O}(N \cdot k)$ amortized, $\mathcal{O}(N \cdot k \cdot V)$ naive | Composes by combining many specialized statistical predictors (viewpoints: pitch, pitch-interval, contour, scale-degree, onset-interval, duration, metric-position, chord — plus linked product viewpoints) into one product-of-experts distribution over the next event, then sampling or argmax-decoding it. Backoff with PPM* escape adapts context order automatically; a long-term corpus model (style) and a short-term within-piece model (structure/repetition) are blended in log space (IDyOM). Entropy-based viewpoint selection drops redundant features. Ensemble counterpart to 002 Markov (single viewpoint) / 067 Factor Oracle (single automaton); count-based ancestor of 054 ATS attention. |
```

## Line counts
- **Before (append)**: 17542 lines
- **After (detail-section append via `cat >>`)**: 17630 lines (+88)
- **After (summary row via patch)**: 17631 lines (+1)
- **Delta**: +89 lines total

## Files
- **Standalone file**: `/opt/data/repos/musicom/projects/Research/CompositionMethods/method_087_MVS-C.md`
- **Report file**: `/opt/data/repos/musicom/projects/Research/CompositionMethods/report_087.md`
- **DB**: `/opt/data/repos/musicom/projects/Research/CompositionMethods/methods_db.md` (summary row at line 97 + full section at line 17544)
- **Temp file**: `_temp_method_087.md` written, appended, and removed (per workflow).

## Candidate code path
- **Module**: `generators/multiple_viewpoint.py` (new, alongside existing generator modules — sibling to `chain.py` Markov, `stochastic.py`).
- **Public API sketch**: `class ViewpointModel(max_order, escape)` (fixed-order counter with PPM* method-D escape); `class MultipleViewpointComposer(viewpoints, alpha, seed)` with methods `train_ltm(event_seq)`, `predict(candidates)` (log-space product-of-experts), `compose_next(candidates, mode="sample"|"argmax")` (samples/decodes + updates STM incrementally). All log-space; deterministic per seed.
- **Registration note**: NOT registered in SCALE/generator_registry — this is a prose-only nightly research job. The weekly `weekly-method-code-registration` job (Sun 08:00) closes the loop (scan → dedup → `register_method()` → skill index → pytest → commit). This report's "candidate code path" above is what that job will promote.

## Complete method section text appended
Headers: ### Source, ### Layer, ### Description, ### Technical Mechanics, ### Musical Elements Framework, ### UnitMatrix Integration (Voices & Sections), ### Pitfalls, ### Comparison With Related Methods, ### References. (Identical to the content that was in `_temp_method_087.md`, now folded into `methods_db.md` at line 17544 and expanded with a Python sketch + references in `method_087_MVS-C.md`.)

## Quirks / pitfalls hit
1. **Table row placement**: the composition-method summary table ends at line 96 (`086`), immediately followed by `# Sound Production Methods Framework`. The new `087` row was inserted via `patch` (replace of the `086` row's trailing text + following header), not appended — appending would have landed the row inside the Sound Production section. Verified at line 97.
2. **LaTeX escape check**: re-read line 97 after patching — single backslashes `$\mathcal{O}(N \cdot k)$`. Grep for `\\mathcal`, `\\pi`, `\\cdot`, `\\rightarrow`, `\\approx` returned **0 matches** (no double-escape). Clean.
3. **`||` prefix check**: grep for `^|| **087` returned **0 matches**; new row starts with single `|`. Clean.
4. **`_warning` on patch**: the patch tool warned the file was "modified since last read" — this is the expected `cat >>` append from step 5b, not an external editor. Re-read line 97 after patching to confirm the row landed correctly.
5. **Paradigm placement rationale**: classified **Stochastic** (probabilistic count-based ensemble model), consistent with the DB convention that classical statistical/ML models without deep gradient training sit in Stochastic (002 Markov, 045 Hawkes, 061 GPC, 086 HMM-C, 084 ZMRC), while deep gradient-trained nets (054 ATS, 060 S4SC, 072 NFC) sit in AI-Driven. IDyOM/MVS uses only counting + backoff (PPM), no gradient descent → Stochastic.
6. **Gap exploited**: DB has *single-viewpoint* sequence models (002 Markov fixed-order), *single-automaton* variable-order models (067 Factor Oracle), *hidden-state* models (086 HMM-C), and *deep attention* models (054 ATS) — but **no ensemble/combination framework that fuses many feature predictors into one distribution**. MVS-C fills the "multiple-viewpoint combination" gap and is the count-based, interpretable ancestor of attention (the product-of-experts over viewpoints plays the role attention plays over tokens). It carries the canonical Conklin–Witten (1995) and Pearce IDyOM (2005) lineage.
7. **Tonal gravity label**: "Strong (Ensemble-constrained)" — the scale-degree + chord linked viewpoints hard-constrain pitch to the key/function, but unlike a strict mode it is a soft (probabilistic) constraint, so it sits between the "Strict" and "Weak" poles; "Strong" with the ensemble qualifier captures this.
8. **Network unavailable**: outbound web fetch (`curl`) was blocked (pending-approval / no egress in this cron context), so no live web search was possible. The method was instead researched from the canonical literature already encoded in the skill's reference material and confirmed absent from the DB. All citations (Conklin & Witten 1995; Cleary & Witten 1984; Conklin 2003; Pearce 2005; Pearce & Wiggins 2006; Pearce et al. 2010) are standard, verifiable primary sources.

## Next free ID
**088**
