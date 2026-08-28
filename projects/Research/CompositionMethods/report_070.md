# Report — Method 070 (Coupled Map Lattice Composition)

## Method identity
- **Method ID:** 070
- **Name:** Coupled Map Lattice Composition
- **Acronym:** CML-C
- **Paradigm:** Nature-Led (Physical/Emergent)
- **One-line description:** Generates music from the spatiotemporal chaos of a ring of diffusively coupled logistic maps — site state → pitch, Lyapunov exponent → rhythm, cluster synchronization → harmony, Kaneko pattern regime → macro-form.

## Classification (summary-table columns)
| Column | Value |
|---|---|
| Primary Elements | Pitch, Rhythm, Harmony, Structure, Texture |
| Tonal Gravity | Moderate (Cluster-sync) |
| Metric Binding | Grid-Locked / Continuous |
| Memory Depth | Meso / Cluster State |
| Time Complexity | $\mathcal{O}(L \cdot T)$ |

## Summary-table row (as appended)
| **070** | Coupled Map Lattice Composition (CML-C) | **Nature-Led** | Pitch, Rhythm, Harmony, Structure, Texture | Moderate (Cluster-sync) | Grid-Locked / Continuous | Meso / Cluster State | $\mathcal{O}(L \cdot T)$ | Generates music from spatiotemporal chaos of a ring of $L$ diffusively coupled logistic maps $x_i(t{+}1)=(1-\varepsilon)f(x_i)+\tfrac{\varepsilon}{2}(f(x_{i-1})+f(x_{i+1}))$. Site state → pitch (folded/scale-quantized), Lyapunov exponent $\lambda$ → rhythmic density, cluster synchronization → harmony/voicing (cluster merge/split = chord change), Kaneko pattern regime (frozen/pattern/turbulent) → macro-form, spatiotemporal fluctuation amplitude → texture. Continuous-state, Nature-Led counterpart to 021 Cellular Automata; spatiotemporal sibling of 043 SATM. |

## Line-count before/after
- **Before:** 13518 lines (`wc -l` at start)
- **After:** 13650 lines (after appending the 132-line method section + 1 summary row)
- **Delta:** +132 lines

## Files written
- **Append to DB:** `/opt/data/projects/Research/CompositionMethods/methods_db.md` (via `_temp_method_070.md` → `cat >>` → `rm`)
- **Standalone write-up:** `/opt/data/projects/Research/CompositionMethods/method_070_CML-C.md`
- **Report:** `/opt/data/projects/Research/CompositionMethods/report_070.md` (this file)

## Research summary
Method chosen: **Coupled Map Lattice Composition (CML-C)**. Confirmed novel vs the DB: no existing entry uses *continuous-state spatiotemporal chaos* for composition. 043 SATM = single temporal attractor; 028 CMCG = coupled maps used only to modulate granular-synthesis micro-timing (DSP role, not compositional); 021 CA = discrete-state binary cells; 036 ASAR = discrete-state integer toppling. CML-C is the continuous-state, Nature-Led lattice method. Canonical source: Kaneko (1983–1993), *Theory and Applications of Coupled Map Lattices* (Wiley 1992).

Decoding map (dynamical quantity → musical parameter):
- Site state $x_i(t)$ → PITCH (arcsin-flattened fold + scale quantization)
- Largest Lyapunov exponent $\lambda(a,\varepsilon)$ → RHYTHM (dense chaos vs sparse periodic)
- Cluster synchronization (merge/split) → HARMONY / voicing
- Kaneko pattern regime → STRUCTURE / macro-form (frozen → pattern → turbulent arcs)
- Spatiotemporal fluctuation amplitude $D(t)$ → TEXTURE (note count/velocity)

## Classification details (rationale)
- **Paradigm: Nature-Led** — deterministic physical dynamical system, emergent patterns, no training, no random number injection at generation time (chaotic but seedable). Matches the "Physical/Emergent" family (030, 031, 036, 037, 038, 043, 048, 049).
- **Tonal Gravity: Moderate** — cluster synchronization pulls voices toward block consonance (unison/octave), but there is no explicit tonal function; the scale quantization imposes the tonal center. Weaker than Strict, stronger than Weak.
- **Metric Binding: Grid-Locked / Continuous** — discrete CML time steps can map to a fixed pulse grid (one step = one 16th), but the underlying dynamics are continuous-valued and the regime is continuous in $(a,\varepsilon)$.
- **Memory Depth: Meso / Cluster State** — the relevant context is the local synchronization cluster + recent state history (fading in chaos), not the whole form.
- **Time Complexity: $\mathcal{O}(L \cdot T)$** — one scalar map evaluation per site per step; linear, embarrassingly parallel. Cluster detection adds $\mathcal{O}(L^2)$ naive / $\mathcal{O}(L)$ sorted.

## Quirks / pitfalls hit (and how I handled them)
1. **Documentation "next number" discrepancy** — the task prompt asserted the highest ID was 058 and the next was 059, but the DB had actually advanced to 069 (Christoffel Word). Verified via `grep '^# .*\(Method 0'`: the last method header is 069 CWCC. **Resolution: used 070**, the true next number.
2. **Append-point confusion** — the "last detailed section" in the file is not 069 (a composition method) but a *Sound Production* entry (Frequency Shifter, line 13390). The composition methods (069) sit *above* several SP-* sections in the file. Resolved by appending at end-of-file (after 069 CWCC), which is the established pattern — the summary table already lists 070 correctly and the method headers are not strictly monotonic in file position.
3. **Patch double-escaping** — checked the summary row after patching; LaTeX backslashes remain single (`\varepsilon`, `\tfrac`, `\mathcal{O}`) with no `\\` double-escaping. Confirmed via `read_file` of lines 77–79.
4. **`||` prefix normalization** — verified the appended 070 row has a single leading `|` (matches the 069 row above it). No `||` prefix introduced.
5. **Existing DB (unrelated to my task)** — the DB header already cites a "Method 070" via the internal narrative of methods 059/060 (e.g. "S4SC ... trained counterpart to 059 ESN-RC") — those references are pre-existing and consistent (059 ESN-RC, 060 S4SC already exist). My 070 slot was genuinely free: `grep '070'` returned no summary row or method section before my edit.

## Verification
- `wc -l` before: 13518; after: 13650 (delta +132). ✅
- Summary row present: `grep -n '| \*\*070\*\*'` → line 79. ✅
- Method section header present: `grep -n 'Coupled Map Lattice Composition (CML-C) (Method 070)'` → present. ✅
- Standalone file: `method_070_CML-C.md` written (13,664 bytes). ✅

## Complete method section text appended
The full section (Source / Description / Musical Elements Framework / UnitMatrix Integration / Technical Mechanics / Implementation Requirements / Pitfalls / Comparison / References) was appended verbatim to `methods_db.md` after the 069 CWCC section. It is reproduced in its entirety inside the standalone file `method_070_CML-C.md` (identical content, plus the extended write-up with Python implementation sketch and the invariant-density/arcsin discussion).
