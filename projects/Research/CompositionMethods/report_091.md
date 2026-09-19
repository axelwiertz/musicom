# Report — Method 091: Coxeter–Conway Frieze Pattern Composition (CCFPC)

**Date:** 2026-09-19 (methods-research cron job)
**Status:** APPENDED to methods_db.md + summary row added + standalone file written.

## Identification

- **Method ID:** 091 (resolved dynamically: max numeric ID in methods_db.md summary table + `method_*.md` / `report_*.md` scan was **090** GRDC; no `method_091*` or `report_091*` files existed; next free ID is 092)
- **Name:** Coxeter–Conway Frieze Pattern Composition (CCFPC)
- **Paradigm:** Rules-Based (combinatorial geometry, cluster algebra $A_n$ mutation, unimodular determinant lattices)
- **LAYER:** **concrete** (evaluates integer frieze matrices over triangulated polygons and unimodular $SL_2(\mathbb{Z})$ diamond lattices directly into UnitMatrix cells, voices, rhythms, and chord voicings; feeds `generators/`; L3/L2 SCALE levels — matrix coordination at L3, voice contours at L2, metric subdivisions at L1)
- **One-line description:** Generates polyphonic pitch, rhythm, and chord voicings from positive integer frieze patterns of unimodular $SL_2(\mathbb{Z})$ diamond lattices ($bc - ad = 1$) bounded by rows of 1s, classified bijectively by Conway–Coxeter triangulations of convex $(n+1)$-gons.

## Summary table row (as inserted at methods_db.md line 101)

| **091** | concrete | Coxeter–Conway Frieze Pattern Composition (CCFPC) | **Rules-Based** | Pitch, Rhythm, Harmony, Structure, Texture | Weak (Cluster-algebraic) | Grid-Locked | Macro / Polygon Period | $\mathcal{O}(w \cdot n)$ generation, $\mathcal{O}(1)$ step | Generates polyphonic pitch, rhythm, and chord voicings from positive integer frieze patterns of unimodular $SL_2(\mathbb{Z})$ diamond lattices ($bc - ad = 1$) bounded by rows of 1s, classified bijectively by Conway–Coxeter triangulations of convex $(n+1)$-gons. Rows = voices/polyphonic strata (quiddity row = voice 1, interior cluster depths = inner voices); columns = temporal metric pulses; glide-reflection symmetry ($180^\circ$ rotation + $(n+1)/2$ shift) enforces exact inverted and phase-shifted polyphonic canon relationships. Unimodular determinant constraint prohibits parallel collapse and harmonic drift; macro-form develops via Ptolemy diagonal flips (cluster algebra mutations) across section boundaries. Integrable combinatorial counterpart to 083 quasicrystal / 088 Voronoi and deterministic foil to 021 CA / 033 WFCGS. |

## Line counts

- **Before append:** 18,825 lines
- **After append (section):** 18,945 lines (+120)
- **After summary row:** 18,946 lines (+121 total)

## Files

- **methods_db.md:** section appended at line 18,826 (`# Coxeter–Conway Frieze Pattern Composition (CCFPC) (Method 091)`), summary row inserted at line 101 (after 090 GRDC, before the `# Sound Production Methods Framework` header).
- **Standalone file:** `/opt/data/projects/Research/CompositionMethods/method_091_CCFPC.md`
- **This report:** `/opt/data/projects/Research/CompositionMethods/report_091.md`
- **Candidate code path:** `generators/coxeter_frieze.py` (quiddity calculator, diamond rule propagation, Ptolemy mutation, and UnitMatrix realization) + SCALE entry in `workflows/paths.py` via `register_method("091", "L3", "generators.coxeter_frieze", "Coxeter-Conway frieze pattern composition")` when registered. Import-pure (no external heavy libraries, stdlib typing + core engine structures only) so `test_generator_lazy_imports` stays green.

## Research summary

A **Coxeter frieze pattern** (Coxeter 1971; Conway & Coxeter 1973; Baur & Marsh 2012) is a staggered 2D numerical array satisfying the unimodular diamond rule:
$$ad - bc = -1 \iff bc - ad = 1 \iff d = \frac{bc - 1}{a}$$
bounded by rows of 0s and 1s. Conway and Coxeter proved that every positive integral frieze of width $w = n-1$ non-trivial rows corresponds bijectively to a triangulation of a convex $(n+1)$-gon by non-intersecting internal diagonals. The second row is the **quiddity sequence** counting incident triangles at each polygon vertex, summing to $3(n+1) - 6 = 3n - 3$.

Musically:
- **Polyphonic voice strata:** Rows represent voices. Voice 1 carries the quiddity line; interior rows carry higher-order cluster variable lines; the final row is the glide-reflected partner.
- **Metric time steps:** Columns represent sequential metric beats or subdivision pulses.
- **Glide reflection symmetry:** $180^\circ$ rotation + horizontal $(n+1)/2$ shift enforces exact inverted and phase-shifted canon dialogue between upper and lower voice strata.
- **Unimodular determinant constraint ($bc - ad = 1$):** Prohibits parallel motion collapse, octave unison collisions, and harmonic drift.
- **Cluster algebra mutation (Ptolemy flips):** Macro-form transitions between sections are driven by flipping internal diagonals ($X_{uw}X_{vx} = X_{uv}X_{wx} + X_{vw}X_{ux}$), smoothly mutating local motifs while preserving global structural continuity.

## Musical Elements Framework (full)

- **PITCH:** Frieze integers $m_{r,j} \in \mathbb{N}^+$ map to pitch material via scale-degree indexing over an active harmonic scale or pitch-class pool $\mathcal{S}$ of cardinality $K$: $\text{pitch}(r, j) = \text{base\_pitch}_r + \text{scale\_lookup}(m_{r,j} - 1 \bmod K) + 12 \cdot \lfloor (m_{r,j} - 1) / K \rfloor$. Small integers keep motion conjunct, while high-valence vertices create dramatic leaps.
- **RHYTHM:** Frieze entries determine duration and metric subdivisions (e.g. $m_{r,j} \times \text{quantum}$), or modulate velocity/accents ($v(r,j) = \text{clamp}(45 + 18 \cdot m_{r,j}, 0, 127)$). Isochronous boundary rows provide steady metric pulses.
- **HARMONY:** Vertical column slices $\mathbf{v}_j = [m_{1,j}, \dots, m_{w,j}]^T$ define chord voicings. Unimodular determinant $m_{r,j+1}m_{r+1,j} - m_{r,j}m_{r+1,j+1} = 1$ ensures non-parallel, bounded voice motion.
- **STRUCTURE:** Sections map to polygon triangulations. Section transitions flip a diagonal, altering $1/(n-3)$ of the triangulation while preserving the rest of the motivic framework.
- **TEXTURE:** Frieze width $w$ sets polyphonic voice density; glide reflection creates antiphonal and hocketing texture between voice pairs.

## UnitMatrix Integration

- **Voices (rows):** Rows $r \in \{1, \dots, w\}$ of the frieze matrix map to UnitMatrix voice rows (Voice 1 = quiddity sequence, Voice $w$ = glide-reflected quiddity sequence, intermediate rows = inner voices).
- **Sections (columns):** Columns represent structural sections (Intro, Verse, Chorus, Bridge, Outro), each assigned an $(n+1)$-gon triangulation.
- **Cells (MusicUnit):** Each cell receives note events evaluated from frieze row $r$ over section duration $T_{\text{sec}}$, terminated and padded to satisfy the zero-drift equal-length invariant.
- **Fill order:** Sections filled column-by-column; within each section, the frieze matrix is computed via the Conway–Coxeter propagation algorithm and mapped to voices.

## Pitfalls encountered / documented

1. **Integer division rounding error:** The diamond formula $d = (bc - 1)/a$ is guaranteed to yield integers ONLY when the quiddity sequence is derived from a valid polygon triangulation. Arbitrary integer sequences produce non-integers and divide-by-zero singularities.
2. **Pitch range runaway on large polygons:** For polygons with $n > 12$, interior entries can grow beyond standard playable ranges ($>30$). Apply modulo-octave folding or scale wrapping.
3. **Glide-reflection phase alignment:** Horizontal offset of $(n+1)/2$ requires careful beat grid alignment so that top/bottom voice canons align with intended metric downbeats.
4. **Sparse rhythmic lock:** Repeated 1s in quiddities can cause rhythmic monotony if mapped strictly to note length; combine with continuous fill layers (pads, walking bass) per the Method Hybridization rule.
5. **Process verification:** Sanitized table insertion without `||` prefix and with single backslashes in `\mathcal{O}`. Appended section confirmed via grep and line counts.

## Verification

- `wc -l methods_db.md` → 18,946 (was 18,825; delta = +121 lines).
- `grep -n '091' methods_db.md` → line 101 (summary row) + line 18,827 (section header).
- Row format check: single `|` prefix, clean LaTeX `\mathcal{O}`, 10 classification columns present and properly aligned.
- `_temp_method_091.md` created, appended, and cleanly removed.
- **Next free ID: 092** (numeric); next free SP-ID remains SP-088.
