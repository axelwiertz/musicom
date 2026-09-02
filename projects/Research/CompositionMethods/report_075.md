# Report — Method 075: Self-Organizing Map Composition (SOM-C)

## Summary
- **Method ID**: 075 (next available after DB had advanced to 074 RBM-C)
- **Name**: Self-Organizing Map Composition (SOM-C)
- **Paradigm**: Stochastic
- **One-line description**: Train a Kohonen self-organizing map (topology-preserving, toroidal) on corpus atoms, then compose by walking stochastic/deterministic trajectories across it — adjacent nodes = smooth voice leading/conjunct melody, U-matrix ridges = section seams, waypoint regions = macro-form, concurrent walkers = voices.

## Summary-Table Row (appended)
```
| **075** | Self-Organizing Map Composition (SOM-C) | **Stochastic** | Pitch, Rhythm, Harmony, Structure, Texture | Moderate (Region-guided) | Grid-Locked / Continuous | Macro / Map Trajectory | $\mathcal{O}(E \cdot I \cdot N \cdot M)$ training, $\mathcal{O}(T \cdot M)$ generation | Trains a Kohonen self-organizing map (topology-preserving, toroidal) on corpus atoms (chord PC vectors, melodic contours, groove patterns), then composes by walking stochastic/deterministic trajectories across the map. Adjacent nodes = smooth voice leading/conjunct melody; U-matrix ridges = section seams; waypoint regions = macro-form; concurrent walkers = voices (coupling force = vertical coherence); map distance between walkers = dissonance/density texture. Discrete-topology counterpart to 046 VAE-LSI (learned similarity space) and 042 NST; learned-landscape sibling of 055 SAMC. |
```

## Line Count
- Before: 15112
- After: 15401 (delta +289)

## Files
- **DB**: `/opt/data/projects/Research/CompositionMethods/methods_db.md` (summary row at line 84; detailed section starts at line 15284)
- **Standalone**: `/opt/data/projects/Research/CompositionMethods/method_075_SOM-C.md`
- **Report**: `/opt/data/projects/Research/CompositionMethods/report_075.md`

## Classification Details
| Field | Value |
|---|---|
| Paradigm | Stochastic |
| Primary Elements | Pitch, Rhythm, Harmony, Structure, Texture |
| Tonal Gravity | Moderate (Region-guided) |
| Metric Binding | Grid-Locked / Continuous |
| Memory Depth | Macro / Map Trajectory |
| Time Complexity | O(E·I·N·M) training, O(T·M) generation |

## Complete Method Section (as appended to methods_db.md)
See the full section text in `method_075_SOM-C.md` (it is a verbatim superset of the DB section — the DB section was written first and the standalone file contains the extended math + implementation sketch + references).

The DB section appended begins:
```
# Self-Organizing Map Composition (SOM-C) (Method 075)
```
and contains the required subsections: ### Source, ### Description, ### Musical Elements Framework, ### UnitMatrix Integration (Voices & Sections), ### Technical Mechanics, ### Implementation Requirements (Python / NumPy), ### Pitfalls, ### Comparison With Related Methods, ### References.

## Quirks / Pitfalls Encountered
1. **Instruction said 059, but DB had already advanced to 074** (the task's stated "highest = 058" was stale). Verified via grep that 059–074 all exist (059 ESN-RC … 074 RBM-C), so the true next number is **075**. Used 075.
2. **Both known patch pitfalls were checked and are clean**: row 84 has a single leading `|` (no `||` prefix), and `\mathcal` appears with a single backslash (no `\\` double-escape). Verified by grep/sed.
3. **A sibling subagent warning** fired during the patch (the file was touched concurrently), but the final grep re-verified the row landed correctly and there is no corruption.
4. Research used the canonical SOM sources (Kohonen 1982/2001) and the music-specific work by Toiviainen (2005) + Toiviainen & Krumhansl (2003); a duckduckgo search confirmed these are the standard citations. Wikipedia and GeeksforGeeks confirm the algorithm details (competitive learning, Gaussian neighborhood, toroidal variant).
