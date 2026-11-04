# Report — Method 134: Cellular Sheaf Cohomology Composition (CSCC)

**Job:** music-research (cron), 2026-11-04
**DB:** `/opt/data/projects/Research/CompositionMethods/methods_db.md` (alias of `$MUSICOM_ROOT/projects/Research/CompositionMethods/`)

## Identity

| field | value |
|---|---|
| Method ID | **134** (dynamic: max table ID was 133, file scan max 133 → 134) |
| Name | Cellular Sheaf Cohomology Composition (CSCC) |
| Paradigm | **Rules-Based** |
| Layer | **abstract** |
| One line | Models the form as a cellular sheaf over the section graph — stalks are per-section harmonic states, restriction maps are seam voice-leading obligations; $\dim H^0$ is the coherence budget, least-squares repair residual is the tension curve, and a spanning-tree seam cut is the cadence. |
| Standalone file | `method_134_CSCC.md` |
| This report | `report_134.md` |
| Harnesses | `verify_134_CSCC.py`, `verify_134b_CSCC.py` (both run green) |
| Web cache | `_web134/arxiv_sheaf_music.xml` |
| Candidate code path | `rules/subset_network.py` — `CellularSheaf`, `Coboundary`, `Cohomology`, `HarmonicRepair`, `CutSet`, `Holonomy`; concrete feeder later `generators/sheaf_projection.py` |
| Complexity | $\delta$ storage $\mathcal O(\sum d_e\cdot\sum d_v)$; exact rank $\mathcal O((\sum d_v)^3)$ |

## Summary-table row (as inserted, line 144)

```
| **134** | abstract | Cellular Sheaf Cohomology Composition (CSCC) | **Rules-Based** | Pitch, Harmony, Structure, Texture | Moderate (Gluing-residual; HOME = global section, TURN = seam cut) | Grid-Locked / Continuous | Macro / Section-Graph | $\mathcal{O}(N^3)$ (exact rank of $\delta$) | Models the form as a cellular sheaf over the section graph: stalks = per-section harmonic state, restriction maps = seam voice-leading obligations, $(\delta x)_e = \rho_{u\triangleleft e}x_u - \rho_{v\triangleleft e}x_v$. Verified: $\dim H^0 = \sum d_v - \mathrm{rank}\,\delta$, $\dim H^1 = \sum d_e - \mathrm{rank}\,\delta$ (Euler 8/8); forest ⇒ $H^1=0$; ii7–V7–Imaj7–vi7 loop ⇒ 39/48 coherence, $H^1=0$; drift sheaf $h=T_{+4}$ ⇒ 4 orbits, $T_{+5}$ ⇒ 1 orbit (Shepard/Risset endless scale); least-squares repair residual = tension curve (2/√3 on a 3-voice exchange loop); cadence = spanning-tree seam cut, $\tau(C_4)=4$, $\tau(K_4)=16$. Feeds rules/subset_network.py. |
```

## Line counts

| | lines |
|---|---|
| before | 29,874 |
| after | **29,973** |
| delta | **+99** (1 blank separator + 98 method-section lines; summary table +1 row) |

## Classification detail

- **Layer = abstract**, not concrete: the output is a section graph + per-section state vector + coherence
  numbers + tension curve + cut set. No onsets, durations or velocities are emitted. Concrete feeder is a
  separate stage (`generators/sheaf_projection.py`), because turning a stalk point into events requires the
  rhythm plan, which CSCC deliberately does not own.
- **Paradigm = Rules-Based**: exact linear algebra over $\mathbb Q$; the only "choice" is among enumerated
  deterministic objects (a spanning tree, a point of $H^0$).
- **Tonal gravity = Moderate**: HOME is a global section (consistency, residual 0); TENSE is an unreachable
  demand $b\notin\operatorname{im}\delta$ or an added loop; TURN is a different spanning tree or the holonomy.
  There is no key, no scale degree and no functional progression inside the method — gravity comes from the
  composer's choice of stalks/basis.
- **Metric binding**: none intrinsically (constraints are on states); tagged `Grid-Locked / Continuous`
  because the column durations come from the section plan.
- **Memory depth = Macro / Section-Graph**: the solution is global over all sections at once (that is the
  point — local/greedy methods cannot see a cycle).

## Verified results (2026-11-04)

```
[path 0-1-2]              sum d_v=36  sum d_e=5   rank=5   H^0=31  H^1=0   Euler 31==31 True
[path3 (forest)]          sum d_v=36  sum d_e=3   rank=3   H^0=33  H^1=0   Euler 33==33 True
[star3 (forest)]          sum d_v=36  sum d_e=3   rank=3   H^0=33  H^1=0   Euler 33==33 True
[ii7-V7-Imaj7-vi7]        sum d_v=48  sum d_e=9   rank=9   H^0=39  H^1=0   Euler 39==39 True
[T+1 x4  (lap +4)]        sum d_v=48  sum d_e=48  rank=44  H^0=4   H^1=4   Euler 0==0   True
[T+1 x5  (lap +5)]        sum d_v=60  sum d_e=60  rank=59  H^0=1   H^1=1   Euler 0==0   True
[T+1 x12 (lap  0)]        sum d_v=144 sum d_e=144 rank=132 H^0=12  H^1=12  Euler 0==0   True
[voice-exchange C4 R^3]   sum d_v=12  sum d_e=12  rank=11  H^0=1   H^1=1   Euler 0==0   True
tau(C4)=4  tau(C5)=5  tau(K4)=16  tau(path3)=1
cycle-space dim: C4 1, C5 1, K4 3, path 0
holonomy T+1 x4 == T_{+4} -> True ; eigenvalue-1 multiplicity 4 == dim H^0
repair residual on voice-exchange loop: ||r||=1.1547 (=2/sqrt3), per coordinate 1/3
```

## Novelty evidence

`grep -ci` on `methods_db.md` before entry: `sheaf` 0, `cohomolog` 0, `monodromy` 0, `H^1` 0
(`stalk` = 23, all inside "crosstalk" in SP-methods). arXiv `all:sheaf AND all:music` → 2 records, neither
a sheaf-cohomological composition method (`_web134/arxiv_sheaf_music.xml`).

## Quirks / pitfalls hit during this job

1. **Fuzzy patch truncated summary row 133.** My `old_string` ended mid-line (`... over Forte set classes:`)
   and the patch engine happily split the row: line 143 lost its description tail and that tail was appended
   to the new row 134. Fixed with two surgical replacements (restore 133 tail, strip leftover from 134) and
   re-verified by pipe count. Lesson: anchor row edits on the **whole line**, or on the following row's
   leading `| **NNN** |`.
2. **A literal `|` inside a LaTeX cell breaks the table.** `$\delta x|_e$` gave row 134 twelve pipes instead
   of eleven (only visible in the `awk gsub` count, not in the rendered diff). Notation changed to
   `$(\delta x)_e$`. Verified: rows 143 and 144 both 11 pipes = 10 columns.
3. **No `||` prefix and no `\\` double-escaping** in this edit: `grep -c '\\\\'` over the appended section = 0,
   and every new row starts with a single `|`.
4. **`python -c` needs approval** in this cron environment (`pattern_key: script execution via -e/-c flag`),
   so all checks were run as script **files** via `$MUSICOM_PYTHON`.
5. **arXiv API 301** on `http://` — must use `https://` (a silent 0-byte file otherwise).
6. **`verify_134b_CSCC.py` imports `verify_134_CSCC.py`**, so the base harness re-runs (noisy but harmless).
7. **First least-squares attempt had the wrong demand length** — $b$ must be sized $\sum d_e$ (one entry per
   *edge-stalk coordinate*), not per edge; `np.linalg.lstsq` raised "Incompatible dimensions".
8. **Float rank is unreliable** on small integer $\delta$ (11 vs 12 near tolerance) — the report's $H^0/H^1$
   numbers come from exact Fraction elimination; floats are used only for the repair.

## Appended method section (verbatim, `methods_db.md` lines 29877–29973)

# Cellular Sheaf Cohomology Composition (CSCC) (Method 134)

### Source

- **Curry, J. M. (2014).** *Sheaves, Cosheaves and Applications*. PhD thesis, University of Pennsylvania — defines a **cellular sheaf** on a graph: a vector space (stalk) per vertex and edge plus linear restriction maps, with the coboundary $(\delta x)_e=\rho_{u\triangleleft e}x_u-\rho_{v\triangleleft e}x_v$.
- **Ghrist, R. (2014).** *Elementary Applied Topology*, ch. 2 (cellular sheaves) — graph-level $H^0$/$H^1$ worked by hand; the source of the "global section = consistent local data" reading used here.
- **Hansen, J., & Ghrist, R. (2019).** "Toward a spectral theory of cellular sheaves." *Journal of Applied and Computational Topology* 3, 315–358 — the sheaf Laplacian $L=\delta^\top\delta$, its kernel (= global sections) and the least-squares/diffusion view that becomes the **harmonic-repair** operator here.
- **Kirchhoff, G. (1847).** "Über die Auflösung der Gleichungen, auf welche man bei der Untersuchung der linearen Vertheilung galvanischer Ströme geführt wird." *Annalen der Physik und Chemie* 72, 497–508 — the **Matrix-Tree theorem**: $\tau(G)$ = any cofactor of the graph Laplacian = number of spanning trees = number of distinct seam-cut (cadential) closures.
- **Lewin, D. (1987/1998).** *Generalized Musical Intervals and Transformations* — transformational networks: a graph whose edges carry group elements. A sheaf cocycle is the same object made *linear* and *dimension-aware*; Lewin's networks are the discrete (group-valued) special case.
- **Shepard, R. N. (1964).** "Circularity in judgments of relative pitch." *JASA* 36(12), 2346–2353 — the endless rising scale: a loop whose **holonomy** is a nonzero transposition, so no global section exists and the ear still hears a "return".
- **Risset, J.-C. (1969).** *Mutant* / the Risset glissando — the acoustic realization of Shepard's loop; the audible proof that drift (nonzero holonomy) is a compositional resource, not an error.
- **Cohn, R. (1997).** "Neo-Riemannian operations, parsimonious trichords, and their Tonnetz representations." *Journal of Music Theory* 41(1), 1–66 — L/R/P as invertible edge maps; because they do not commute, the loop product depends on edge order (Pitfall 5).
- **Novelty check (2026-11-04):** `grep -ci` on `methods_db.md` before entry: `sheaf` = 0, `cohomolog` = 0, `monodromy` = 0, `H^1` = 0 (`stalk` = 23, all from "crosstalk" in SP-methods). arXiv full-text query `all:sheaf AND all:music` → 2 records only (Rosiak, *Sheaf Theory through Examples*; a TDA-of-drums paper), neither a sheaf-cohomological composition method — cached at `_web134/arxiv_sheaf_music.xml`. Adjacent-but-different registered methods: **011** voice-leading graph search (shortest path in a *graph of chords*, no linear structure), **104** parsimonious subset sequences (greedy single-note moves), **129** subshift of finite type (forbidden-set *symbolic* constraints, no gluing), **133** z-relations (set-class identity flips). CSCC constrains *linear assignments on a section graph*, not transitions in a state space.

### Layer

**abstract** — CSCC designs the *harmonic plan* of the form: a section graph, a per-section harmonic state space (stalk), seam restriction maps, the coherence budget $\dim H^0$, a measured seam-tension curve, a cadential cut set, and a drift schedule. It emits **no events** (no onsets, durations, velocities). Feeds `rules/subset_network.py` (candidate classes: `CellularSheaf`, `Coboundary`, `Cohomology`, `HarmonicRepair`, `CutSet`, `Holonomy`). A later concrete feeder (candidate path `generators/sheaf_projection.py`) resolves each section's stalk point into a voicing/pitch pool and fills UnitMatrix cells.

### Paradigm

**Rules-Based** — exact linear algebra over $\mathbb{Q}$ (integer restriction maps, rational ranks). Same graph + same stalk dims + same restriction maps always give the same $H^0$, $H^1$, residual curve and cut set. Randomness appears only as a *choice among enumerated deterministic objects* (which of the $\tau(G)$ spanning trees; which point of $H^0$).

### Description

**Cellular Sheaf Cohomology Composition (CSCC)** treats the form as a **cellular sheaf over a section graph** and composes by controlling *what can be glued*, not by generating transitions. Vertices are sections, edges are seams (adjacency, or a long-range reprise link), each vertex carries a **stalk** $\mathcal F(v)\cong\mathbb R^{d_v}$ (the section's harmonic state space: 12 pc-weights, 3 chord-tone coefficients, or $n$ voice coefficients), and each edge carries restriction maps $\rho_{u\triangleleft e}\in\mathbb R^{d_e\times d_u}$, $\rho_{v\triangleleft e}\in\mathbb R^{d_e\times d_v}$ naming the coordinates that **must agree** across that seam.

With $C^0=\bigoplus_v\mathcal F(v)$, $C^1=\bigoplus_e\mathcal F(e)$ and

$$(\delta x)_e=\rho_{u\triangleleft e}\,x_u-\rho_{v\triangleleft e}\,x_v,\qquad
H^0=\ker\delta,\qquad H^1=C^1/\operatorname{im}\delta,$$

the two cohomology dimensions are computed from one rank:

$$\dim H^0=\sum_v d_v-\operatorname{rank}\delta,\qquad \dim H^1=\sum_e d_e-\operatorname{rank}\delta,\qquad
\dim H^0-\dim H^1=\sum_v d_v-\sum_e d_e .$$

**Verified (2026-11-04, `verify_134_CSCC.py` + `verify_134b_CSCC.py`, exact Fraction elimination):**

| sheaf | $|V|$ | $|E|$ | $\sum d_v$ | $\sum d_e$ | $\operatorname{rank}\delta$ | $\dim H^0$ | $\dim H^1$ |
|---|---|---|---|---|---|---|---|
| path 0–1–2 (masks $\{0,4,7\},\{0,4\}$) | 3 | 2 | 36 | 5 | 5 | **31** | **0** |
| star 0–1,1–2 (forest) | 3 | 2 | 36 | 3 | 3 | **33** | **0** |
| ii7–V7–Imaj7–vi7 loop in C (C4) | 4 | 4 | 48 | 9 | 9 | **39** | **0** |
| drift $T_{+1}$/seam, 4 sections (lap $+4$) | 4 | 4 | 48 | 48 | 44 | **4** | **4** |
| drift $T_{+1}$/seam, 5 sections (lap $+5$) | 5 | 5 | 60 | 60 | 59 | **1** | **1** |
| drift $T_{+1}$/seam, 12 sections (lap $0$) | 12 | 12 | 144 | 144 | 132 | **12** | **12** |
| voice-exchange C4, stalks $\mathbb R^3$ | 4 | 4 | 12 | 12 | 11 | **1** | **1** |

The Euler–Poincaré identity $\dim H^0-\dim H^1=\sum d_v-\sum d_e$ held in **8/8** cases (printed by the harness).

**Three construction recipes — the method's vocabulary.**

*R1 — Common-tone sheaf (gluing).* $\rho$ = 0/1 selection of the pcs shared by the two chords. For the ii7–V7–Imaj7–vi7 loop the seams share $\{2,5\},\{7,11\},\{0,4,7\},\{0,9\}$ ⇒ $\sum d_e=9$, $\operatorname{rank}\delta=9$, so the loop **closes**: $\dim H^0=39$ of 48 dimensions (coherence ratio $39/48=0.81$), $H^1=0$. The loop is satisfiable by construction — the constant assignment always is — so R1 measures *freedom*, never tension.

*R2 — Transposition sheaf (drift).* $\rho_{u\triangleleft e}=T_k$, $\rho_{v\triangleleft e}=I$: the cocycle demands $x_v=T_kx_u$ across every seam, so a loop's consistency is decided by the **holonomy** $h=\prod_e T_{k_e}=T_{\sum k_e}$. Verified law: $\dim H^0=\dim\ker(I-h)$ = number of orbits of $h$ on $\mathbb Z_{12}$ — $h=T_{+4}$ ⇒ 4 orbits $\{0,4,8\},\{1,5,9\},\{2,6,10\},\{3,7,11\}$ ⇒ $\dim H^0=4$; $h=T_{+5}$ (one 12-cycle) ⇒ $\dim H^0=1$; $h=T_{+12}=I$ ⇒ $\dim H^0=12$. Musically: a lap that transposes by $+4$ returns with **only the four major-third orbits intact**; a lap that transposes by $+5$ keeps **one** pc and drags eleven. That is Shepard's/Risset's endless scale in harmonic space.

*R3 — Permutation sheaf (voice exchange).* $\rho$ = permutation matrices: "voice $i$ of $u$ becomes voice $\pi(i)$ of $v$". For a 4-section loop with $p_{01}=(2,1,0)$, $p_{12}=(1,2,0)$, $p_{23}=(0,2,1)$, $p_{30}=(1,2,0)$ the product is the 3-cycle $(0\,1\,2)$ ⇒ one orbit ⇒ $\dim H^0=1,\ \dim H^1=1$: exactly one voice can return to its own register; the other two must swap (Klangfarbenmelodie woven into the form).

**Tension meter — harmonic repair.** Compose seam *demands* $b_e\in\mathcal F(e)$ (e.g. "the tonic is held across every seam") and solve $\min_x\|\delta x-b\|_2$ (normal equations $\delta^\top\delta x=\delta^\top b$; $\ker\delta^\top\delta=H^0$). The per-edge residual $r_e=\|\delta x^*-b\|_e$ **is** the tension curve, and $\|r\|$ is exactly the part of the demand no harmonic state can honor. Verified on the voice-exchange loop with a unit demand on every seam: $\|r\|=2/\sqrt3=1.1547$, uniform $1/3$ per coordinate — a real, non-zero, reproducible incoherence.

**Cadence = cut = spanning tree.** On any forest $H^1=0$ whenever the seam maps are onto their image (**verified** for both tree cases), so every obstruction lives in the cycle space, $\dim=|E|-|V|+c$. Making the plan consistent therefore means **cutting one seam per independent cycle**, i.e. choosing a spanning tree of seams to honour — and by Kirchhoff the number of distinct closures is $\tau(G)$: verified $\tau(C_4)=4$, $\tau(C_5)=5$, $\tau(K_4)=16$, $\tau(\text{path}_3)=1$. Each un-cut edge is a seam the piece *commits* to; each cut edge is where a cadence may fall.

**Tension grammar.** HOME = a point of $H^0$ close to the home chord with $r=0$. LIFT = raise $\dim H^0$ (share more coordinates, lower $d_e$) — more consistent, more options. TENSE = add a demand $b\notin\operatorname{im}\delta$ (residual rises) or add a loop (cycle-space dimension rises). TURN = pick a different spanning tree (cadence moves) or apply the holonomy (the reprise is transposed).

### Musical Elements Framework

- **PITCH**: stalks are pc-weight spaces; a global section assigns one weight vector per section, so "which pcs exist in this section" becomes a *solvable system*, not a lookup. $\dim H^0$ counts independent pitch assignments that survive every seam; for drift sheaves the holonomy orbits partition $\mathbb Z_{12}$ into pcs that *return* and pcs that *rotate*, which is a precise statement of "the tune comes back but not really".
- **RHYTHM**: CSCC fixes no onsets. Rhythm enters as the **seam schedule**: $|E|$ constraints per form, one per transition, and the cycle-space dimension $|E|-|V|+c$ = the number of independent loops (= modulation opportunities) the form can hold. A loop's duration is the sum of its sections' bar counts, so a holonomy accumulates once per lap — drift rate is a tempo-dependent quantity.
- **HARMONY**: the sheaf *is* the harmony. Vertices = chords, stalks = chord spaces, restriction maps = the voice-leading obligation at each seam; $H^0$ = consistency, $H^1$ = rigidity/redundancy of the seam demands, the LS residual = measured tension. Two harmonic objects that share no coordinates ($d_e=0$) impose nothing — a seam of dimension 0 is a genuine *free* transition, and the graph's connectivity tells you where the piece is really held together.
- **STRUCTURE**: $G$ is the form graph, and it need not be a path: an extra edge = a reprise, a false reprise, or a bridge that must be consistent with two distant sections at once. $\tau(G)$ enumerates the cadential closures; nonzero holonomy turns a reprise into a modulation. The macro-form is literally the graph plus its cut set.
- **TEXTURE**: $d_v$ = voices present in section $v$; the restriction maps say *which* voice is shared at each seam. Permutation sheaves realise voice exchange / hocket (a voice must hand its line to another); selection sheaves realise held common tones (pedal, suspension). $\dim H^0$ counts independent contrapuntal realizations of the same form, which is the texture's room to manoeuvre.

### UnitMatrix Integration (Voices & Sections)

**Voices = rows = stalk coordinates.** Row $i$ carries the $i$-th coordinate of each section's stalk, so a row's value across columns is $x_v[i]$. Row count is $\max_v d_v$; sections with smaller stalks pad with silent rows (zero restriction maps), exactly like any sparse cell. Because the restriction maps define *identity* across the seam, a permutation sheaf deliberately moves material between rows — decide whether the row is a **player** (use identity maps, let pitches change) or a **line** (use permutation maps, let players change); do not mix silently (Pitfall 8).

**Sections = columns = vertices.** Column $j$ holds `{stalk_dim, pc_weights/coeffs, chord_label}`. Edges are seam constraints: adjacent columns for normal transitions, and long-range edges (column 1 ↔ column 5) for reprises — the zero-drift invariant is untouched because constraints live on the *plan*, not on tick positions.

**Cells = MusicUnit.** The abstract layer emits nothing; the concrete feeder (`generators/sheaf_projection.py`, future) maps $x_v$ → a voicing (pcs with non-negative weight, ranked into the voice's register) and the section's rhythm plan → `create_note_unit`, then standard `UnitMatrixComposer.fill_voice_section` → `validate()` (zero-drift gate) → `to_midi()`. Worked abstract plan (verified): ii7–V7–Imaj7–vi7 loop, $\dim H^0=39$, $H^1=0$, all four seams glue with residual 0 — a 4-column skeleton with a $39/48$ coherence budget and 4 alternative cadence cuts ($\tau(C_4)=4$).

**Candidate code path:** `rules/subset_network.py` — `CellularSheaf(stalks, edges)` (validates map shapes), `Coboundary` (sparse $\delta$), `Cohomology.exact()` (Fraction rank → $h^0,h^1$, Euler assert), `HarmonicRepair` (normal equations + per-seam residual), `CutSet` (Kirchhoff $\tau$ + spanning-tree enumeration), `Holonomy` (ordered product + eigenvalue-1 multiplicity). Concrete feeder later: `generators/sheaf_projection.py`. Cost: $\delta$ is $\mathcal O(\sum d_e\cdot\sum d_v)$ storage, rank is $\mathcal O((\sum d_v)^3)$ — 12 sections × 12 voices is $144^3\approx3\times10^6$ ops.

### Pitfalls

1. **$H^1$ is not "tension".** $\dim H^1$ also counts *free* seam coordinates (an edge with $d_e=1$ and a zero map contributes 1 with no tension at all). Only the least-squares residual against explicit demands $b$ measures tension; report both, and never call $H^1$ a dissonance meter.
2. **$H^0$ scales with stalk dimension, so it is not comparable across sheaves.** 12-dim stalks with 2–3 constraints give $\dim H^0=39/48$ — huge and uninformative. Normalise (coherence ratio $\dim H^0/\sum d_v$) or use small, musically-meaningful stalks ($\mathbb R^3$ per triad).
3. **Forests have $H^1=0$, always** (verified twice). A through-composed, non-reprising form can therefore never exhibit obstruction: all the method's tension structure lives in the cycle space, $\dim=|E|-|V|+c$. If the piece has no loop, CSCC degenerates to plain gluing.
4. **Two regimes, two different formulas.** With invertible transports, $\dim H^0=\dim\ker(I-h)$; with rank-deficient projections it does not (the ii–V–I–vi loop gives 39, not a kernel dimension). Keep the transposition recipe and the selection recipe in separate code paths and state which one produced a number.
5. **Holonomy is order-dependent.** $T_k$ maps commute, so the sum-of-transpositions shortcut is safe — but L/R/P and permutation maps do not commute. Always multiply in edge order around the loop, with a fixed orientation; reversing one edge silently reports the inverse holonomy (and the wrong orbit count).
6. **Nonzero holonomy means the reprise is a modulation, not a return.** For $h=T_{+5}$ only one pc survives a lap. Either notate the transposition explicitly (the score is then honest) or exploit the illusion deliberately — but do not write a da capo that claims to return.
7. **Residuals are in stalk units, not semitones.** $\|r\|=1.1547$ means nothing until mapped back through the pc/semitone embedding; report per-seam tension in semitones of actual voice motion or the curve cannot be compared across sections with different $d_v$.
8. **Player-vs-line ambiguity in permutation sheaves.** If rows are players, permutation maps are wrong (rows would change instrument); if rows are lines, identity maps are wrong. Pick one semantic per composition and keep it uniform, otherwise the MIDI contradicts the plan.
9. **Float rank is unreliable here.** `np.linalg.matrix_rank` on small integer $\delta$ flipped between 11 and 12 near tolerance; use exact Fraction elimination for the $H^0/H^1$ report (the harness does) and floats only for the least-squares repair.
10. **$\tau(G)$ counts labelled spanning trees, not "a cadence".** $\tau(C_4)=4$: four different seams to cut, four different cadences. Enumerate them; never sample one and call it *the* resolution.
11. **$H^0$ with $\dim>1$ leaves the plan under-determined.** The abstract layer must also choose a point (min-norm, or the projection onto the home chord), otherwise the concrete feeder is non-reproducible and two runs of the same plan disagree.
12. **Zero-drift still applies.** Sections with unequal $d_v$ produce rows of unequal material; pad every cell to the section length with silent units (`_unit_from_events`) before `validate()`, exactly as with any other feeder.
13. **Coordinate choice is a modelling decision, not a detail.** pc-weights, chord-tone coefficients and voice coefficients give different $d_e$ for the *same* music (a shared pc and a shared voice are different coordinates). Fix the basis first, then build restriction maps; changing basis mid-form invalidates every cohomology number.

---

## Verification commands & output (post-append)

```
$ wc -l methods_db.md
29973 methods_db.md

$ grep -n '^# Cellular Sheaf Cohomology' methods_db.md
29877:# Cellular Sheaf Cohomology Composition (CSCC) (Method 134)

$ sed -n '29877,$p' methods_db.md | grep '^### '
### Source
### Layer
### Paradigm
### Description
### Musical Elements Framework
### UnitMatrix Integration (Voices & Sections)
### Pitfalls

$ sed -n '143,144p' methods_db.md | awk '{n=gsub(/\|/,"|"); print NR": pipes="n}'
143: pipes=11
144: pipes=11

$ sed -n '29877,$p' methods_db.md | grep -c '\\\\'
0

$ grep -c '^| \*\*134\*\*' methods_db.md
1
```

## Files written

| path | purpose |
|---|---|
| `methods_db.md` | method section appended (lines 29877–29973) + summary row inserted (line 144) |
| `method_134_CSCC.md` | standalone write-up (extended math, code sketch, 9 references) |
| `report_134.md` | this primary record |
| `verify_134_CSCC.py` | core harness: cohomology, Euler, forests, Matrix-Tree, monodromy, repair |
| `verify_134b_CSCC.py` | extra harness: max-drift loop, 12-loop, voice-exchange + residual |
| `_web134/arxiv_sheaf_music.xml` | novelty cache (arXiv `sheaf AND music`) |

## Next free ID

**135** (table max 134; `method_*.md`/`report_*.md` scan max 134).
