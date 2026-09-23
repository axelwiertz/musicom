# Report — Method 094: Apollonian Circle Packing Composition (ACPC)

**Date:** 2026-09-23 (methods-research cron job)  
**Status:** APPENDED to methods_db.md + summary row added + standalone file written + verified.

## Identification

- **Method ID:** 094 (resolved dynamically: max numeric algorithmic-method ID in methods_db.md summary table was **093** PPNC; verified against all existing `method_*.md` and `report_*.md` files; next free ID is 095)
- **Name:** Apollonian Circle Packing Composition (ACPC)
- **Paradigm:** **Nature-Led** (fractal conformal geometry, Diophantine number theory, Apollonian reflection groups)
- **LAYER:** **concrete** (generates discrete note events, fractal proportional durations, polyphonic voice allocations, and consonant chord quadruples directly into UnitMatrix cells; feeds `generators/`; operating at L3 meso section coordination and L2 voice contours)
- **One-line description:** Composes polyphony and fractal rhythmic durations from recursive integral Apollonian circle packings governed by Descartes' kissing theorem and Apollonian group reflections $S_i \in GL(4, \mathbb{Z})$.

## Summary table row (as inserted at methods_db.md line 104)

```markdown
| **094** | concrete | Apollonian Circle Packing Composition (ACPC) | **Nature-Led** | Pitch, Rhythm, Harmony, Structure, Texture | Strict (Descartes-quadruple consonance) | Grid-Locked / Continuous | Meso / Apollonian Tree | $\mathcal{O}(3^D)$ tree, $\mathcal{O}(1)$ step | Composes polyphony and fractal rhythmic durations from recursive integral Apollonian circle packings governed by Descartes' theorem $(k_1+k_2+k_3+k_4)^2 = 2\sum k_i^2$ and Apollonian group reflections $S_i \in GL(4, \mathbb{Z})$. Curvatures $k_i \in \mathbb{Z}^+$ map logarithmically/modally to pitch; radii $r_i = 1/k_i$ govern self-similar fractal note durations ($D_f \approx 1.3057$); mutually tangent quadruples form consonant 4-voice chords with parsimonious single-voice voice-leading pivots ($k_i' = 2\sum_{j \neq i} k_j - k_i$). Geometric packing counterpart to 088 VTEP / 092 DLACG and number-theoretic cousin of 069 CWCC / 091 CCFPC. |
```

## Line counts

- **methods_db.md before:** 19,595 lines
- **After detailed section append:** 19,789 lines (+194 lines)
- **After summary table row insertion:** 19,790 lines (+1 line)
- **Total delta:** +195 lines

## File artifacts

- **Standalone file:** `/opt/data/projects/Research/CompositionMethods/method_094_ACPC.md`
- **Verification script:** `/opt/data/projects/Research/CompositionMethods/verify_094_ACPC.py`
- **Generated MIDI test:** `/opt/data/projects/Research/outputs/test_094/test_094_acpc.mid` (948 bytes, size > 40 B verified)
- **This report:** `/opt/data/projects/Research/CompositionMethods/report_094.md`

## Candidate Code Path

- **Target Module:** `generators/apollonian_generator.py` or `generators/geometric_packing.py`
- Feeds `rules/realize.py` and `workflows/unitmatrix_composer.py`.

## Classification Details

- **Tonal Gravity:** Strict (Descartes-quadruple consonance)
- **Metric Binding:** Grid-Locked / Continuous
- **Memory Depth:** Meso / Apollonian Tree
- **Time Complexity:** $\mathcal{O}(3^D)$ tree, $\mathcal{O}(1)$ step
- **Primary Elements:** Pitch, Rhythm, Harmony, Structure, Texture

## Complete Appended Method Section Text

```markdown
# Apollonian Circle Packing Composition (ACPC) (Method 094)

### Source
- Descartes, R. (1643). Letter to Princess Elisabeth of Bohemia (Oeuvres de Descartes, IV, 45–50).
- Soddy, F. (1936). "The Kiss Precise." Nature, 137, 1021.
- Graham, R. L., Lagarias, J. C., Mallows, C. L., Wilks, A. R., & Yan, C. H. (2003). "Apollonian circle packings: number theory." Journal of Number Theory, 100(1), 1–45.
- Graham, R. L., Lagarias, J. C., Mallows, C. L., Wilks, A. R., & Yan, C. H. (2005). "Apollonian circle packings: geometry and group theory I. The Apollonian group." Discrete & Computational Geometry, 34(4), 547–585.
- Kontorovich, A., & Oh, H. (2011). "Almost all integers are curvatures in Apollonian packings." Journal of the American Mathematical Society, 24(4), 1079–1102.
- Bourgain, J., & Kontorovich, A. (2014). "On the strong density conjecture for Apollonian packings." Annals of Mathematics, 180(2), 415–486.

### Layer
concrete — generates discrete pitch events, fractal durations, harmonic quadruples, and polyphonic voice assignments directly into UnitMatrix cells (feeds generators/; operating at L3 meso section coordination and L2 voice contours).

### Description
Apollonian Circle Packing Composition (ACPC) is a nature-led, fractal-geometric, and number-theoretic composition method based on recursive Apollonian circle packings and the Descartes kissing-circle theorem. Starting from an initial configuration of four mutually tangent circles—a Descartes configuration—with curvatures (reciprocals of radii) v = (k1, k2, k3, k4)^T, the theorem of René Descartes (1643) and Frederick Soddy (1936) states:
(k1 + k2 + k3 + k4)^2 = 2 (k1^2 + k2^2 + k3^2 + k4^2)

When three mutually tangent circles are given, exactly two distinct circles are tangent to all three. If their curvatures are k4 and k4', they satisfy:
k4 + k4' = 2(k1 + k2 + k3) ==> k4' = 2(k1 + k2 + k3) - k4

Remarkably, if the starting root quadruple v0 consists entirely of integers (e.g. the primitive root quadruple v0 = (-1, 2, 2, 3)^T, where -1 represents the enclosing bounding circle of radius 1, and circles 2, 2, 3 pack within it), then every subsequent circle in the infinite recursive packing has an exact integer curvature (Graham et al., 2003). The transition from one Descartes quadruple to an adjacent tangent quadruple is governed by the four integer reflection generators S1, S2, S3, S4 in GL(4, Z) of the Apollonian group A.

Musically, ACPC models polyphony, rhythm, and harmonic structure through this discrete conformal fractal:
1. Curvature as Harmonic & Registral Scale: Circle curvature k in Z+ corresponds directly to acoustic frequency or pitch height. Smaller circles (high curvature k) represent fast, high-register ornamental figurations, while large circles (small curvature k) represent foundational, low-register fundamental tones and cantus firmus structural pillars.
2. Radius as Duration (Fractal Metric Proportions): The Euclidean radius r = 1/k directly governs rhythmic duration: large circles possess broad, sustained rhythmic values, while nested micro-circles occupy brief, staccato subdivisions. Because the packings tile space with Hausdorff dimension alpha approx 1.30568, the rhythmic distribution naturally follows an organic, fractal self-similar hierarchy.
3. Descartes Quadruples as Four-Voice Harmonic Consonance: Every quadruple of mutually tangent circles forms a vertical chord across the 4 voices of the UnitMatrix. Tangency enforces acoustic proximity and harmonic compatibility: transitioning via generator Si corresponds to an optimal voice-leading parsimonious step where exactly one voice pivots while the other three voices hold common tones (pedal/harmonic anchor).
4. Tree Depth as Structural Form: Traversing the Apollonian tree from the root quadruple down into high-depth branches generates a deterministic, non-repeating macro-form progressing from spacious foundational consonance to micro-polyphonic complexity.

### Musical Elements Framework

- PITCH: Each positive curvature k in Z+ is mapped to pitch space. In modal/tonal contexts, k indexes a diatonic, acoustic, or synthetic pitch scale S via logarithmic mapping (p = round(C * ln k)) or scale-degree projection (p = S[k mod |S|]). The root curvatures (k=2, 3) anchor the tonic and dominant fundamentals, while deeper reflections yield higher partials and chromatic embellishments without wandering arbitrarily.
- RHYTHM: Duration is strictly proportional to radius r_i = 1/k_i. In discrete grid time (120 ticks per 16th note), duration D(k) = max(D_min, round(B / ln(1 + k))) or D(k) = round(K_base / k). Large circles produce whole-note and dotted-half structural nodes; tiny interstitial circles produce 16th- and 32nd-note decorative bursts. Tangency points between circles define precise metric onset alignments.
- HARMONY: Each Descartes quadruple (k1, k2, k3, k4) defines a vertical harmonic slice across the four UnitMatrix voices. Because k_i satisfies Descartes' quadratic equation, the frequency ratios of mutually tangent circles maintain natural acoustic consonances (octaves, fifths, fourths, and resonant triads). Moving between quadruples via Apollonian reflections S_i ensures smooth parsimonious voice-leading: three voices remain constant while one voice steps to its Apollonian conjugate k_i' = 2 sum_{j != i} k_j - k_i.
- STRUCTURE: Macro-form corresponds to an ordered exploration of the Apollonian Cayley tree:
  - Section A (Root Quadruple): Grounded, deep low-frequency foundation (k in {2, 3, 6}). Slow rhythmic pulse, wide consonant intervals.
  - Section B (Depth-1 Interstices): Medium curvatures (k in {11, 14, 15, 23}). Polyphonic emergence of counter-melodies and rhythmic diminution.
  - Section C (Depth-2 & Depth-3 Micro-Packings): Dense fractal clusters (k in {26, 35, 47, 62, 71, ...}). Intricate hocketing, high-register arabesques, and shimmering textural cascades.
  - Section D (Return / Dual Reflection): Inversion or contraction back to low curvatures, resolving accumulated harmonic tension to the root attractor.
- TEXTURE: Polyphonic 4-voice stratification. The 4 faces of the packing assign naturally to Soprano, Alto, Tenor, and Bass. When a voice reflects to a high curvature, its texture shifts from sustained drone to rapid granular figuration, creating a dynamic exchange of foreground and background roles across voices.

### UnitMatrix Integration (Voices & Sections)

- Voices (rows): Four canonical polyphonic voices corresponding to the four tangent circles in the Descartes quadruple:
  - Voice 0: Bass (pedal / root circle k1)
  - Voice 1: Tenor (harmonic support circle k2)
  - Voice 2: Alto (counter-melody circle k3)
  - Voice 3: Soprano (lead melodic interstice circle k4)
- Sections (columns): Columns represent structural sections (e.g. Sections A, B, C, D) mapped to increasing depths or distinct subtree branches of the Apollonian packing.
- Cells (MusicUnit): Each cell receives a sequence of MusicEvent instances derived from the active circles along that voice's branch, quantized to metric tick boundaries.
- Zero-Drift Invariant: Track lengths are strictly balanced by appending a silent padding event (pitch=0, volume=0) terminating precisely at section_total_ticks, guaranteeing zero drift across polyphonic channels.
- Method Hybridization: ACPC can be hybridized with continuous spatial panning (e.g. SP-053 VBAP) or reverberant delay networks (SP-032 FDN), matching the circular geometric topology to physical acoustic space.

### Pitfalls

1. Curvature Explosion / Unplayable Pitch Registers: As tree depth increases, curvatures grow rapidly (k exceeds 10^3 within 6–7 reflections), which if mapped linearly would blow past MIDI pitch 127.
   Fix: Map curvatures logarithmically into pitch space (p ~ log2 k) or apply modulo octave folding (k mod |S|) into the vocal range [36, 84].
2. Micro-Duration Grid Desynchronization: Raw reciprocal radii r = 1/k produce irrational or fractional tick durations that do not align with integer subdivision grids.
   Fix: Quantize all event durations to multiples of the fundamental metric quantum (e.g. 120 ticks = 16th note), with a defined lower bound (D_min >= 120 ticks).
3. Bounding Circle Negative Curvature (k1 < 0): The outer enclosing circle in a bounded packing has negative curvature (k = -1), which has no physical frequency meaning.
   Fix: Treat the negative curvature as a structural bounding framework: map it to a resting pedal point, section duration anchor, or exclude it from audible pitch generation while keeping the three positive internal curvatures.
4. Duplicate Quadruple Cycles: Unrestricted reflection can backtrack immediately (S_i^2 = I), causing trivial 2-element looping between identical states.
   Fix: Maintain a visited-quadruple registry and prohibit immediate reflection along the incoming edge (i != parent_index).
```

## Quirks & Verification

- Workflow strictly adhered to `write_file` -> `cat >>` -> `rm temp` -> patch summary table.
- Python verification ran against `UnitMatrixComposer`, producing valid 4-track MIDI (`test_094_acpc.mid`, 948 bytes) with zero drift.
- Next free method ID for subsequent jobs: **095**.
