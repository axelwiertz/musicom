# Report — Method 082: Random Boolean Network Criticality Composition (RBNCC)

## Summary
- **Method name**: Random Boolean Network Criticality Composition
- **Acronym**: RBNCC
- **ID**: 082 (dynamically resolved: max existing algorithmic ID = 081 NIRMC → 082)
- **Paradigm**: Nature-Led
- **LAYER**: **concrete** (emits note/chord events into UnitMatrix cells; feeds `generators/`)
- **One-line description**: Composes by running a synchronous random Boolean network (Kauffman's gene-regulatory model) at its critical point — the deterministic state trajectory falls into an attractor cycle decoded into a repeating groove/chord-progression loop, with connectivity $K$ and output bias $p$ as the edge-of-chaos creative dial and the pre-attractor transient as connective/tension material.

## ID resolution
- Scanned the summary table (`| **NNN** |` rows) at top of `methods_db.md`. Highest numeric algorithmic ID: **081** (Narmour Implication-Realization Melodic Composition, NIRMC).
- Cross-checked standalone `method_*.md` files: `method_081_NIRMC.md` was the highest algorithmic.
- Cross-checked `report_*.md` files: `report_081.md` confirmed max = 081. (The grep hit "report_202" seen earlier was the date string `2026` in `registration_report_2026-09-06.md`, NOT an ID — verified no `report_202*` file exists.)
- Next ID = **082**. Collision-free: no "Boolean network" / "Kauffman" / "canalizing" / "NK model" method exists in the DB (grep returned nothing).
- Note: ID 058 remains absent (known pre-existing gap, NODE-CTC unregistered). Not touched; 082 is clean.

## Classification details
| Field | Value |
|---|---|
| Method ID | 082 |
| Layer | concrete |
| Method Name | Random Boolean Network Criticality Composition (RBNCC) |
| Paradigm | Nature-Led |
| Primary Elements | Structure, Pitch, Harmony, Rhythm, Texture |
| Tonal Gravity | Weak (Self-Organizing) |
| Metric Binding | Grid-Locked / Continuous |
| Memory Depth | Meso / Attractor Cycle |
| Time Complexity | $\mathcal{O}(N \cdot T)$ |

## Summary-table row (appended at line 92, after 081)
```
| **082** | concrete | Random Boolean Network Criticality Composition (RBNCC) | **Nature-Led** | Structure, Pitch, Harmony, Rhythm, Texture | Weak (Self-Organizing) | Grid-Locked / Continuous | Meso / Attractor Cycle | $\mathcal{O}(N \cdot T)$ | Composes by running a synchronous random Boolean network (Kauffman's gene-regulatory model) at its critical point (edge of chaos): the deterministic state trajectory falls into an attractor cycle decoded into a repeating groove/chord-progression loop. Connectivity $K$ and output bias $p$ are the creative dials ($K_c = 1/[2p(1-p)]$; ordered $K<K_c$ = short catchy loop, critical $K\approx K_c$ = rich phrase, chaotic $K>K_c$ = tension/transient). Pre-attractor transient = connective/tension material; frozen node core = harmonic scaffold, unstable periphery = figuration. Self-organizing discrete counterpart to 036 ASAR / 071 HAM-C; deterministic-per-seed foil to 002 Markov. |
```

## Line counts
- **Before**: 16719 lines
- **After**: 16781 lines
- **Delta**: +62 lines total (+61 detail-section append, +1 summary-table row via patch)

## Files
- **Standalone file**: `/opt/data/projects/Research/CompositionMethods/method_082_RBNCC.md`
- **Report file**: `/opt/data/projects/Research/CompositionMethods/report_082.md`
- **DB**: `/opt/data/projects/Research/CompositionMethods/methods_db.md` (summary row at line 92 + full section at line 16721)

## Candidate code path
- **Module**: `generators/boolean_network.py` (new, alongside existing generator modules).
- **Public API sketch**: `build_rbn(N, K, p, seed) → nodes`; `step(nodes, x) → x'`; `detect_cycle(nodes, x0) → (mu, lam)`; `run(nodes, x0, n_steps) → iterator`; `decode_pcset(x) → pitches`; `compose_loop(N, K, p, n_steps, seed) → (loop, (mu, lam))`.
- **Abstract-layer note**: the network topology + attractor cycle (which binary/pc-set states recur, in what order) is transposition-invariant structural design that could feed `rules/subset_network.py` (ABS-001..005) as a pattern walk; as documented the method emits events → concrete layer.

## Complete method section text appended
(Full text identical to `method_082_RBNCC.md` and the `# Random Boolean Network Criticality Composition (RBNCC) (Method 082)` section in methods_db.md at line 16721. Headers: ### Source, ### Layer, ### Description, ### Musical Elements Framework, ### UnitMatrix Integration (Voices & Sections), ### Pitfalls, ### Comparison With Related Methods, ### References.)

## Quirks / pitfalls hit
1. **Table row placement**: the composition-method summary table ends at line 91 (`081`), immediately followed by `# Sound Production Methods Framework`. The new `082` row was inserted via `patch` (replace of the `081` row + following header), not appended — correct, since appending would land the row inside the Sound Production section.
2. **LaTeX escape check**: re-read line 92 after patching — single backslashes `$\mathcal{O}(N \cdot T)$`, `$\approx`, `$\cdot`, no `\\` double-escaping. Verified.
3. **`||` prefix check**: new row starts with single `|`. Verified.
4. **ID-resolution red herring**: `grep report_[0-9]` surfaced a "202" that was actually the `2026` date inside `registration_report_2026-09-06.md`, not an ID. Confirmed via `ls report_202*` (no such file) before settling on 082.
5. **Sparse-method rule**: a low-$p$ near-critical network yields sparse textures; documented in Pitfalls #5 (pair with 026 DPSM / sustained pad per the Method Hybridization rule).

## Next free ID
**083**
