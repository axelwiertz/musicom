# Report — Method 151: Matroid Basis-Exchange Composition (MBEC)

**Run:** scheduled cron research job, 2026-11-26
**DB:** `/opt/data/projects/Research/CompositionMethods/methods_db.md`
**Status:** complete, verified 10/10, appended

---

## 1. Identity

| Field | Value |
|---|---|
| Method ID | **151** (resolved dynamically: summary-table max = 150, file scan max = `method_150_MJETC.md` → 151) |
| Name | Matroid Basis-Exchange Composition |
| Acronym | MBEC |
| **LAYER** | **abstract** (LAYER_ARCHITECTURE.md: emits pitch-class subset plans + tension weights + exchange distances; no ticks, registers, durations, velocities) |
| Paradigm | **Rules-Based** |
| One-liner | Declare the harmony constraint as a matroid, take the provably optimal max-weight **basis** as the chord per section, and modulate by single-element **basis exchanges**. |
| Candidate code path | `rules/matroid.py` (new: `Matroid`, `partition_matroid`, `graphic_matroid`, `linear_matroid`, `dual`, `greedy_basis`, `rank`, `circuits`, `basis_lattice`, `exchange_path`, `exchange_distance`, `basis_to_pattern`) imported by `rules/subset_network.py` (`PatternNetwork` of `Pattern`(subset) + parsimonious edges). **Not** a `generators/` module — that would violate the abstract-layer contract. |
| Selector chain | `select_chain(["abstract", "concrete"])` → `[151 MBEC, 011/013/arranger]` |
| Standalone file | `/opt/data/projects/Research/CompositionMethods/method_151_MBEC.md` |
| Verification | `_web151_mbec/verify_mbec.py` → `_web151_mbec/verify_mbec_results.txt` — **10/10 PASS** |
| Sketch check | `_web151_mbec/sketch_test.py` runs the code block of the standalone doc **verbatim** (extracted by awk) — OK |
| Web cache | `_web151_mbec/matroid.json` (Wikipedia REST/API extract, fetched live) |
| Next free ID | **152** |

## 2. Layer classification (first, per contract)

- **abstract.** The method's output is exactly what LAYER_ARCHITECTURE.md assigns to the abstract layer: "subset (12TET pc-set) sequences, tension curves, pattern network (z-relations, P/L/R), form". MBEC's deliverable per cell is `{basis B_vs ⊆ E, weights w_vs, rank r(E), circuits hit, exchange distance}` — transposition- and register-invariant.
- Rejected alternatives: **concrete** would require resolved `MusicEvent`s filling `MusicUnit` cells with the zero-drift equal-length invariant; **absolute** is sound production (SP-*), out of scope for this DB section.
- Direct consequence: the concrete realisation must be a *different* method (011 voice-leading graph search, 013 transforms, or a style arranger). MBEC emitting ticks would duplicate concrete responsibility and break `selector.select_chain()`.

## 3. Line counts

| Moment | `wc -l methods_db.md` |
|---|---|
| Before this run | **33076** |
| After appending the method section | 33179 |
| After inserting the summary row (and one pitfall line edit) | **33180** |
| Delta | **+104** |

## 4. Summary-table row (verbatim, as inserted at line 161)

```
| **151** | abstract | Matroid Basis-Exchange Composition (MBEC) | **Rules-Based** | Pitch, Harmony, Rhythm, Structure, Texture | Moderate (Weight-and-rank defined: HOME = heavily weighted basis at low tension, TENSE = colour/chromatic-weighted basis; no functional tonic postulated; loops/coloops act as absolute bans/mandates) | Grid-Agnostic (abstract, tick-free; the onset-grid partition instantiation is Grid-Locked) | Meso / Phrase (one basis per cell) + Macro via exchange-distance path | $\mathcal{O}(n \log n)$ greedy per cell; $\mathcal{O}(m \log m)$ graphic; $\mathcal{O}(n^{3})$ intersection; Tutte polynomial #P-hard | Composes by optimising over a matroid (Whitney 1935): ground set = pitch classes, independent sets = an axiomatically closed harmony constraint, bases = chords, circuits = over-full/loop-closure sets, rank $r(E)$ = fixed note count per chord. Greedy max-weight basis (Rado–Edmonds) is provably optimal and one-pass, so per-section tension weights map directly to chord choice; the exchange axiom guarantees any two chords are a sequence of single-note swaps apart (parsimonious modulation with a proof); equicardinality fixes the voice count. Four instantiations: partition (per-region caps — tritone-axis $k=(1,1,1)$ gives 64 trichord bases; circle-of-fifths regions $k=(2,1,1)$ give rank 4 / 96 bases), graphic/cycle (spanning tree = loop-free progression, circuits = cadences, dual bond matroid = section seam), linear/representable (interval or Fourier-balance vectors give harmonic rank), transversal / matroid intersection (voicing = bipartite matching). Submodular rank = principled density saturation; beta invariant = 0 iff the form is disconnected. Verified 10/10 (greedy = brute force 300/300; the plausible non-matroid rule "no semitone, max 4 notes" fails (I3) and loses 13/300; Kruskal 200/200 on $K_4$; dual co-trees + $T(1,1)=16$; 4×8 abstract plan: all 32 cells are bases, 28/28 single-exchange moves, 16 distinct chords). Feeds `rules/subset_network.py`. |
```

Table-format checks after patching:
- column count = **11 pipes** (10 columns + leading pipe) — correct;
- single `|` prefix — no `||` artefact (verified `grep -c '^||'` = 0);
- LaTeX backslashes single, **no `\\`** (verified `grep -cF '\\'` = 0 on the row and across the whole appended section);
- all 10 header columns populated (Method ID, Layer, Method Name, Paradigm, Primary Elements, Tonal Gravity, Metric Binding, Memory Depth, Time Complexity, Description/UnitMatrix Integration).

## 5. Novelty evidence

Pre-write `grep -ci` on `methods_db.md`:

| Term | Hits | Meaning |
|---|---|---|
| `matroid` | 0 | — |
| `greedoid` | 0 | — |
| `ground set` | 0 | — |
| `rank function` | 0 | — |
| `basis exchange` | 0 | — |
| `independent set` | 0 | — |
| `whitney` | 0 | — |
| `tutte` | 5 | **all** are the substring in "s**tutte**ring" (false positives) |
| `matroid intersection` | 0 | — |

Nearest neighbours ruled out: **132 BIBDC** (block *designs*, incidence counts, no independence axiom / no exchange), **139 LSAC** (Latin squares, quasigroup completion), **145 DPBC** (Dyck paths, ballot counting), **134 CSCC** (sheaf cohomology, consistency rather than rank), **011** (voice-leading *shortest path* on a graph), **104 PSSC** (parsimonious subset *sequences*, a heuristic with no optimality theorem), **051 SGLM** (graph Laplacian spectra — eigen-decomposition of a graph Laplacian, not an independence system), **113 PCFSC** (Fourier balance of a set — used here only as an optional vector representation). No method in 001–150 uses matroid axioms, rank/greedy structure, duality or basis exchange.

## 6. The method section appended to `methods_db.md` (lines 33079–33180, verbatim)

# Matroid Basis-Exchange Composition (MBEC) (Method 151)

### Source

- **Wikipedia: "Matroid"** (fetched live 2026-11-26, cached `_web151_mbec/matroid.json`). A matroid is a pair $(E, \mathcal{I})$ — finite ground set $E$, family of *independent sets* $\mathcal{I} \subseteq 2^E$ — satisfying (I1) $\emptyset \in \mathcal{I}$; (I2) **hereditary**: $A' \subseteq A \in \mathcal{I} \Rightarrow A' \in \mathcal{I}$; (I3) **augmentation (exchange)**: if $A, B \in \mathcal{I}$ and $|A| > |B|$ then $\exists x \in A \setminus B$ with $B \cup \{x\} \in \mathcal{I}$. Maximal independent sets are **bases**; all bases of a matroid have the same cardinality $r(E)$ (**equicardinality**). Minimal dependent sets are **circuits**. The **rank function** $r(S)$ = size of the largest independent subset of $S$ is submodular and monotone. Five equivalent axiom systems exist (independence, bases, circuits, rank, closure/flats); a finite simple matroid is a geometric lattice.
- **Same article, algorithms section — the load-bearing theorem for this method.** A maximum-weight basis of a weighted matroid is found by the **greedy algorithm** (sort by weight, keep if independent). The converse is the characterisation: if a hereditary family is such that greedy is optimal for *every* weighting, that family *is* a matroid. Also stated: **matroid intersection** of two matroids on the same ground set is polynomial; of three or more it is **NP-complete**; **matroid partition / union** (fewest independent sets covering $E$, most disjoint spanning sets) is polynomial; maximum bipartite matching is the intersection of two *partition* matroids.
- **Same article, constructions.** *Uniform* $U_{k,n}$ (every $k$-subset a basis), *partition* matroid (blocks with caps $k_i$), *graphic / cycle* matroid (independent = forests, bases = spanning trees, circuits = simple cycles), *linear / representable* matroid (independent = linearly independent columns of a matrix; representability depends on the field), plus contraction, deletion, truncation, direct sum.
- **Same article, duality and invariants.** The **dual** $M^{*}$ has the same ground set and takes a set as a basis iff its complement is a basis of $M$; $(M^{*})^{*} = M$, and $r^{*}(S) = |S| - r(E) + r(E \setminus S)$. The **Tutte polynomial** satisfies $T_{M^{*}}(x,y) = T_M(y,x)$ and $T_M(1,1) = $ number of bases; the **characteristic polynomial** $p_M(\lambda) = \sum_{S \subseteq E} (-1)^{|S|}\lambda^{r(E)-r(S)}$; the **beta invariant** $\beta(M) = (-1)^{r(M)}\sum_{X\subseteq E}(-1)^{|X|}r(X) \ge 0$, and $\beta = 0$ iff $M$ is disconnected, empty, or a loop — a cheap connectivity diagnostic.
- **Whitney, H. (1935).** "On the abstract properties of linear dependence." *American Journal of Mathematics* 57(3), 509–533. — the founding paper; independence + exchange axioms.
- **Rado, R. (1957).** "Note on independence functions." *Proc. London Math. Soc.* 7(1), 300–320. — greedy optimality for matroids (the "Rado–Edmonds" theorem) and its converse characterisation.
- **Edmonds, J. (1970).** "Submodular functions, matroids, and certain polyhedra." In *Combinatorial Structures and Their Applications* (Calgary), 69–87. — polymatroids, matroid union/partition, rank as a submodular function.
- **Edmonds, J. (1971).** "Matroids and the greedy algorithm." *Mathematical Programming* 1, 127–136. — the canonical statement used here.
- **Tutte, W. T. (1954).** "A contribution to the theory of chromatic polynomials." *Canad. J. Math.* 6, 80–91. — deletion–contraction and the two-variable polynomial.
- **Oxley, J. (2011).** *Matroid Theory*, 2nd ed., Oxford University Press. — standard reference (axioms, duality, representation, chapter on applications).
- **White, N. (ed.) (1992).** *Matroid Applications*, Cambridge University Press. — matroids in network design, coding theory and optimisation; the template for treating a composition as an optimisation object.
- **Tymoczko, D. (2011).** *A Geometry of Music*, Oxford University Press. — chord space and *efficient voice leading* as minimal-note motion; MBEC's basis-exchange distance $|A \setminus B|$ is the formal skeleton of that intuition (one swap = one moving voice).
- **Novelty check (2026-11-26), `grep -ci` on `methods_db.md` before entry:** `matroid` = 0, `greedoid` = 0, `ground set` = 0, `rank function` = 0, `basis exchange` = 0, `independent set` = 0, `whitney` = 0, `tutte polynomial` = 0 (`tutte`'s 5 hits are all "st**utte**ring" substrings), `matroid intersection` = 0. Nearest neighbours and why they are not MBEC: **132 BIBDC** (balanced incomplete block *designs* — incidence counting, no independence structure, no exchange axiom), **139 LSAC** (Latin squares / orthogonal arrays — quasigroup completion, not rank-based), **145 DPBC** (Dyck paths — lattice-path ballot counting), **134 CSCC** (cellular sheaf cohomology — local-to-global consistency, cohomology classes rather than bases), **011** (voice-leading *graph search* — shortest path, not a matroid), **104 PSSC** (parsimonious subset *sequences* — a heuristic smoothness rule, no optimality guarantee). No existing method composes from matroid axioms, greedy/rank structure, or basis exchange → **Method 151 is novel.**
- **Verified prototype (this run):** `_web151_mbec/verify_mbec.py` → `_web151_mbec/verify_mbec_results.txt` — **10/10 checks pass** (results quoted in Technical Mechanics §9).

### Layer

**abstract** (LAYER_ARCHITECTURE.md). MBEC emits *pitch-class subsets with structure* — a ground set, an independence family, a rank, per-section weight vectors and a basis sequence, plus the exchange distance between consecutive bases. It contains **no ticks, no registers, no durations, no velocities**; those belong to the concrete layer that realises the plan. Because the output is exactly a `PatternNetwork` of `Pattern`(subset) objects with Tn/I/Z and parsimonious-move edges, the candidate code path is `rules/subset_network.py` (`matroid.py` helper imported there): `Matroid` (independence oracle), `greedy_basis`, `rank`, `circuits`, `dual`, `basis_lattice`, `exchange_distance`, `basis_to_pattern`. Contrast **132/139/145** (concrete counting methods) and **134/113** (abstract but cohomological/spectral). Same layer family as **104 PSSC** and **133 ZRNC**, but those have no optimality theorem attached to the subset choice.

### Description

MBEC treats a composition as **optimisation over an independence structure that is a matroid** — the only combinatorial structure for which greedy choice is provably optimal. Five pillars:

**1. The move law.** Declare a ground set $E$ (normally the 12 pitch classes, or a 24-tone / just-intonation grid) and a family $\mathcal{I}$ of "allowed" subsets that must satisfy (I1)–(I3). Bases of $\mathcal{I}$ are the chords; $r(E)$ is the chord size; circuits are the minimal over-full sets (the "one note too many" configurations); loops are pitch classes that can never appear; coloops are pitch classes that must appear in every chord. Composition = walking the **basis graph** (bases as vertices, single-element exchanges as edges) under a section-varying weight vector.

**2. Why the matroid axiom is the whole trick.** Three guarantees come free, and each maps onto a musical requirement:
- **Greedy optimality (Rado–Edmonds).** Sorting pitch classes by a section weight and keeping every candidate that preserves independence yields a maximum-weight basis in one pass, never revisiting a decision. That *is* the streaming, zero-backtracking behaviour a section-by-section composer wants — and it is only guaranteed if the constraint family is a matroid (verified: 300/300 against brute force on a partition matroid, and a deliberate 13/300 failure on a non-matroid family).
- **Exchange axiom.** For any two bases $A, B$, every $x \in A\setminus B$ can be swapped for some $y \in B \setminus A$ keeping a basis (verified exhaustively on both test matroids). So *any two chords in the vocabulary are $|A\setminus B|$ single-note moves apart*, and a modulation is a walk of single-note exchanges — one moving voice per step, i.e. parsimonious voice leading with a proof.
- **Equicardinality.** All bases have the same size $r(E)$: every chord in the progression has the same number of notes. Voice count is constant by construction (a zero-drift-friendly property for the concrete layer and for fixed-ensemble writing).

**3. Four instantiation families** (all genuine matroids, all musically meaningful):
- **Partition matroid** — split $E$ into function/region blocks with caps $k_i$; independent = at most $k_i$ notes per block. Two verified examples: the three diminished-seventh families with $k=(1,1,1)$ ("no note doubled inside a tritone-axis family"; 125 independents, 64 bases, every chord exactly 3 notes) and the three circle-of-fifths regions with $k=(2,1,1)$ ("no chord overloads the sharp side"; rank 4, 96 bases).
- **Graphic (cycle) matroid** — ground set = transitions of a chord graph; independent = acyclic transition sets; bases = spanning trees = a progression that visits everything with no closed loop; circuits = the loops (a circuit is a *cadence*: the point where the progression closes on itself); the dual (bond/cut matroid) = the section seams where all voices change at once.
- **Linear / representable matroid** — columns = interval-content or Fourier-balance vectors of each pitch class (the pitch-class Fourier spectrum of 113 gives natural coordinates); independent = linearly independent columns; rank = the true harmonic dimension of the field (how many independent "tonal axes" are active).
- **Transversal matroid / matroid intersection** — pitch classes matched to slots; the intersection of two partition matroids is exactly bipartite matching, so voicing assignment (which pitch goes to which voice) is the same object. Verified: intersecting "≤1 per tritone-axis family" with "≤1 per whole-tone class" caps a chord at 2 notes.

**4. Tension is a weight vector, form is exchange distance.** Each section supplies weights $w_s : E \to \mathbb{R}$ built from a tension target (root attraction, chromatic pull, colour-tone salience, register role). The greedy basis of $w_s$ is the "best chord for that tension". Because $r$ is **submodular**, adding material yields diminishing returns — density saturates instead of piling up (verified per-voice pitch-field growth $[4,5,7,8,8,8,8,8]$). Exchange distance $d(A,B) = |A\setminus B|$ is a metric on the basis graph, so "how far did the harmony move" is a number you can plot as the tension curve's derivative.

**5. Invariants as form diagnostics.** $T_M(1,1)$ = number of bases = how rich the vocabulary is (96 for the fifths matroid); the beta invariant is 0 exactly when the matroid is disconnected (verified: $\beta = 2$ for the connected $K_4$ cycle matroid, $\beta = 0$ for a two-triangle direct sum) — a cheap alarm for a form made of independent blocks that never interact; Whitney numbers count flats of each rank, i.e. how many distinct "harmonic regions" the vocabulary contains.

### Technical Mechanics

**1. Independence oracles.** Partition matroid: keep a counter per block, test is $\mathcal{O}(1)$ (total $\mathcal{O}(n)$ per candidate). Graphic: union-find, $\mathcal{O}(\alpha(n))$ amortised per edge. Linear: incremental Gaussian elimination over $\mathbb{Q}$ or $\mathrm{GF}(p)$, $\mathcal{O}(n \cdot r^2)$ total, or rank via numpy over $\mathbb{R}$ with a tolerance. Transversal: augmenting-path matching, $\mathcal{O}(n^{2.5})$.

**2. Greedy basis.** Sort $E$ by $(-w, \text{pc})$ — the pc tiebreak makes it deterministic — then accept $x$ iff $B \cup \{x\}$ is independent. Complexity $\mathcal{O}(n \log n + n \cdot t_{\text{ind}})$. On a partition matroid this degenerates to "take the top $k_i$ per block", which is the fastest possible implementation and is exactly optimal (verified 300/300).

**3. Basis exchange and distance.** $d(A,B) = |A \setminus B| = |B \setminus A|$; the symmetric-exchange property gives, for each $x \in A\setminus B$, a $y \in B \setminus A$ with $A - x + y$ a basis. Implementing `exchange_path(A, B)` as repeated proximity-improving swaps terminates in exactly $d(A,B)$ steps — a modulation routine with a step count you can print (verified: 28/28 consecutive section pairs are single-exchange reachable).

**4. Graphic instantiation = Kruskal on a chord graph.** Nodes = candidate sonorities, edges = allowed transitions, weight = transition desirability. Maximum-weight spanning tree = the best loop-free progression over all sonorities ($\mathcal{O}(m \log m)$; verified 200/200 against brute-force enumeration of the 16 spanning trees of $K_4$). Circuits (triangles, longer cycles) are *detected* loops: use them as cadence triggers. A tree has exactly $|V|-1$ edges, so a longer progression is a *sequence* of trees connected by exchange moves, or a multigraph.

**5. Dual matroid.** Bases of $M^{*}$ = complements of bases of $M$; $r^{*}(E) = |E| - r(E)$ (verified 3 = 6 − 3 on $K_4$). Musically the dual is the "everything not in the chord" set — an upper-structure/pedal layer, or (for the graphic matroid) the cut set that separates two sections. **Warning:** a co-tree need not be a forest (the complement of a $K_4$ star is a triangle), so never validate the dual with a forest test (this trap was hit and fixed during verification).

**6. Intersection, union, partition.** Two matroids: polynomial (matching, scheduling, arborescence). Three or more: NP-complete — a design with three simultaneous "at most $k$" constraints silently becomes a heuristic, so state it as such. Matroid union gives the maximum number of disjoint spanning sets = the maximum number of independent voices the constraint allows (Edmonds), and matroid partition gives the minimum number of independent sets covering $E$ = the minimum number of "layers" needed to use all material.

**7. Tension curve.** $\tau_s = \alpha \cdot (1 - \bar{w}_s / w_{\max}) + \beta \cdot d(B_{s-1}, B_s)/r$; both terms are $\mathcal{O}(n)$ to compute and both are already needed by the generator, so the tension curve is free.

**8. Complexity summary.** Greedy on a partition matroid $\mathcal{O}(n \log n)$; graphic $\mathcal{O}(m \log m)$ (Kruskal) or $\mathcal{O}(m\,\alpha(n))$ (streaming); linear oracle $\mathcal{O}(n r^2)$; matroid intersection $\mathcal{O}(n^3)$–$\mathcal{O}(n^{3.5})$; Tutte polynomial in general #P-hard (use deletion–contraction only on tiny matroids, cache the result).

**9. Verified prototype — 10/10.** `_web151_mbec/verify_mbec.py`: (1) (I1)–(I3) hold for the tritone-axis partition matroid (125 independents, 64 bases); (2) equicardinality, $r = 3$; (3) greedy = brute-force max-weight basis **300/300**; (4) the musically plausible family "≤4 notes, no minor second" violates (I3) (witness $A=\{0,2,4\}$, $B=\{1,3\}$, no augmenting element) and greedy is suboptimal in **13/300** random peaky weightings (explicit trap: greedy $\{0,2,5,7\}$ weight 1.30 vs optimal $\{4,6,9,11\}$ weight 1.40); (5) $K_4$ graphic matroid: 16 spanning trees, Kruskal = brute force **200/200**; (6) basis-exchange axiom verified exhaustively on both matroids; (7) dual matroid = co-trees (16 bases, rank $m-r$), exchange axiom holds on $M^{*}$, $T(1,1) = 16$ for both $M$ and $M^{*}$; (8) rank submodular (0 violations / 400 random pairs), $\beta(K_4) = 2 > 0$, $\beta(\text{two-triangle direct sum}) = 0$; (9) matroid intersection (tritone-axis × whole-tone partitions) caps a chord at 2 notes; (10) a $4 \times 8$ abstract UnitMatrix plan on the fifths-region matroid: all 32 cells are bases, 28/28 consecutive moves are single exchanges, 16 distinct chords, pitch-field growth $[4,5,7,8,8,8,8,8]$.

**10. Musical mapping summary.** weights → chord choice; basis → chord; rank $r(E)$ → note count per chord (constant); circuits → forbidden/over-full sets and loop-closure (cadence) points; loops → banned pitch classes; coloops → mandatory pitch classes (pedals); exchange distance → modulation distance / number of moving voices; dual basis → complement layer (upper structure, cut seam); $T(1,1)$ → vocabulary richness; $\beta$ → form connectivity; restriction $M|E_s$ → narrowing the pitch field per section; contraction $M/E_s$ → background held constant while foreground varies; matroid union → maximum simultaneous independent voices.

**11. Layer contract / zero drift.** MBEC outputs subset specs, weights and exchange distances only. A concrete method (011 voice-leading search, 013 transforms, or a style arranger) assigns registers, octaves, durations and velocities and is responsible for the equal-length invariant. Keeping MBEC tick-free is what lets `selector.select_chain()` compose it with any concrete generator; emitting ticks here would fork concrete-layer responsibilities and break chaining.

### Musical Elements Framework

- **PITCH**: the core. $E = \{0,\dots,11\}$, chords = bases, and the *family* of allowed chords is an axiomatically closed set rather than a hand-written list. Weight $w_s(\text{pc})$ is the "salience" of a pitch class under a section's tension target; greedy takes the heaviest set that stays independent, so the chord is optimal for that target by theorem, not by taste. Circuits say what may not be piled up (e.g. a third note from the same tritone-axis family); loops ban a pitch class outright (useful for "no leading tone until the coda" rules that cannot be violated); coloops force a pitch class into every chord (a pedal or drone that the constraint itself guarantees). Exchange distance gives melodic motion a metric: $d=1$ means one voice moves — the definition of smooth.
- **RHYTHM**: two clean readings. (a) *Partition matroid on the onset grid* — blocks = metric classes (downbeat, beat, offbeat, subdivision), caps $k_i$ = the maximum events allowed per class per bar; greedy on accent weights yields the densest pattern that respects the metric feel, and the cap vector *is* the groove's identity. (b) *Graphic matroid on the onset graph* — independent = no rhythmic cycle, so the bar can never literally repeat; or invert it and let circuits *be* the loop points. Basis size $r(E)$ = events per bar (constant = steady density). Rank submodularity gives a principled saturation curve instead of "add more notes until it is busy".
- **HARMONY**: the graphic instantiation is the harmonic engine — nodes are sonorities, a spanning tree is a progression covering the vocabulary without premature closure, and each cycle is a cadence. The dual (bond matroid) marks the cuts: sections where every voice changes at once. Representable matroids add a quantitative layer: if each pitch class is a vector of its interval content (or its Fourier balance coefficients), the rank of a section's matrix is the number of independent tonal axes in play, and a rank drop is a real simplification, not a notational one. No functional tonic is postulated; gravity comes from weights plus the coloop/loop structure.
- **STRUCTURE**: a section is a **restriction** $M|E_s$ (fewer available pitch classes = narrower field) or a **contraction** $M/E_s$ (fixed background, free foreground). Form = a path in the basis graph; its length in exchanges is the modulation plan. Direct sums build block forms whose blocks genuinely do not interact — and $\beta = 0$ warns when that disconnection was accidental rather than designed. Recapitulation = returning to an earlier basis along the same exchange path (the basis graph is undirected, so returns are free and exact).
- **TEXTURE**: matroid union/partition answers "how many independent layers fit?" — the arboricity of the constraint. Rank $r(E)$ sets the vertical size; adding voices beyond the union bound *forces* dependency (doubling, which may be exactly the thickening you want, but it is now a deliberate choice). Loops silence a pitch class in a layer, coloops pin it. The dual basis supplies a complementary layer whose content is by construction disjoint from the chord — the formal version of "put the extension in the upper register".

### UnitMatrix Integration (Voices & Sections)

**Rows = voices.** A voice is a *weight profile over the same matroid* (root-emphasis, guide-tone, colour-tone, top-line — the profile used in the verified plan) or, for stratified writing, its **own matroid** (e.g. the bass constrained by a partition matroid with tight caps, the pad by a loose one). Cell content = a subset spec, not events: `{ground: E, matroid: id, weights: w_vs, basis: B_vs, rank: r(E), circuits_hit: [...], exchange_distance_from_prev: d}`.

**Columns = sections.** A section declares `{tension_target, root/centre, restriction set E_s (optional), matroid variant, density target (rank or cap vector), cadence_policy (circuit allowed? which)}`. Section order defines the intended exchange-distance arc; the realized arc is computed, not assumed.

**Cells = MusicUnit (abstract).** One cell (voice $v$, section $s$) = one basis $B_{vs} \subseteq E$ plus its provenance (weights, rank, distance to $B_{v,s-1}$). No ticks. The concrete layer converts each basis into a `MusicUnit` of `MusicEvent`s (registers from the voice's ambitus, durations from the section's rhythmic method, velocities from $w$), pads to the section length, and only then runs `validate()`/`to_midi()`.

**Composition path.** `declare matroid (family + parameters) → per-section restriction + tension weights → greedy basis per (voice, section) → verify basis-graph connectivity (single-exchange reachability) → emit PatternNetwork (subsets + parsimonious edges + tension arc) → concrete realization (011/013/arranger) → validate() → to_midi() → SP render`.

**Selector chaining.** TaskProfile gains `layers_needed = ["abstract", "concrete"]`; `select_chain()` returns `[151 MBEC, <concrete method>]`, with MBEC's `PatternNetwork` piped into the concrete generator's subset input. Deterministic and cacheable: the whole abstract stage is $\mathcal{O}(n\log n)$ per cell.

### Pitfalls

1. **A plausible constraint family is usually not a matroid.** "At most 4 notes and no minor second" sounds like a sane harmonic rule; it violates (I3) ($A=\{0,2,4\}$, $B=\{1,3\}$, no augmenting element) and greedy is then suboptimal (13/300 random peaky weightings; explicit trap 1.30 vs 1.40). Always test (I3) exhaustively on a small ground set, or empirically compare greedy with brute force before trusting a new rule.
2. **Equicardinality forbids varying chord size inside one matroid.** Every basis of $M$ has $r(E)$ notes. To get 3-note and 5-note chords in the same piece you need two matroids, a truncation/erosion, or per-section restrictions — and changing a cap $k_i$ changes the rank globally, so re-verify the basis count.
3. **Loops and coloops act silently.** A loop never appears in any basis (a pitch class is quietly banned); a coloop appears in every basis (a pedal you did not ask for). Print both after building a matroid — accidental coloops are the usual explanation for "why is this note in every chord?".
4. **Greedy ties break reproducibility.** Equal weights make the accepted set order-dependent; always sort by $(-w, \text{pc})$ so the same seed and weights give byte-identical plans.
5. **The dual is not "the opposite chord".** The complement of a 4-note chord is 8 notes, and a co-tree need not be a forest (the complement of a $K_4$ star is a triangle — this broke the first version of the verification). Use the dual for complement/cut layers and validate with $r^{*}(E) = |E| - r(E)$ and the exchange axiom, not with a forest test. And implement the oracle as "the complement **spans** $M$" ($r(E \setminus S) = r(E)$), not as "the complement is independent" — the naive version returns rank 12 instead of 9 on the tritone-axis matroid (caught in verification).
6. **Three-matroid intersection is NP-complete.** Two simultaneous constraints are polynomial (matching etc.); a third silently turns "optimal" into "heuristic". Say which regime you are in.
7. **Graphic progression length is bounded by $\,|V|-1$.** A spanning tree has exactly $|V|-1$ edges; a 32-bar progression in one tree is impossible. Use sequential trees linked by exchange moves (each move is one modulation step) or a multigraph.
8. **Section-independent weights give identical chords.** Greedy is deterministic and saturating: without per-section tension and per-voice role weighting the plan collapses to one basis repeated (the first draft produced 4 distinct chords; after tension + role weights, 16).
9. **Respect the abstract-layer contract.** MBEC must not emit ticks, registers, durations or velocities. Doing so duplicates concrete-layer responsibility, breaks `selector.select_chain()` and invalidates the zero-drift invariant that only concrete generators enforce.
10. **Invariants are diagnostics, not quality.** $\beta = 0$ detects a disconnected matroid, not bad music; the Tutte polynomial is #P-hard in general (deletion–contraction is exponential) — compute it only on small section-level matroids and cache it. $T(1,1)$ = basis count is the cheap, always-safe invariant.

---

---

## 7. Classification details (framework mapping)

| Axis | Value | Justification |
|---|---|---|
| Paradigm | Rules-Based | generative engine is a deterministic axiom system + weighted greedy; randomness only via optional weight noise |
| Primary elements | Pitch, Harmony, Rhythm, Structure, Texture | basis/rank governs pitch+harmony; onset-grid partition instance governs rhythm; basis path = form; matroid union/partition bounds texture density |
| Tonal gravity | Moderate | HOME = heavily weighted (root/triad) basis at low tension; TENSE = colour/chromatic-weighted basis; loops (ban) and coloops (mandate) act as hard constraints; no functional tonic is postulated |
| Metric binding | Grid-agnostic (abstract) | no tick quantity is emitted; the onset-grid partition instantiation is grid-locked if used |
| Memory depth | Meso/Phrase + Macro | each cell needs only its section weights (Markovian); form needs the whole basis path via exchange distance (Macro) |
| Time complexity | $\mathcal{O}(n\log n)$ greedy; $\mathcal{O}(m\log m)$ graphic; $\mathcal{O}(n^3)$–$\mathcal{O}(n^{3.5})$ intersection; Tutte #P-hard | per-cell cheap; cross-section plan is a path, not a search |
| Determinism | total | greedy with $(-w, \text{pc})$ tiebreak → reproducible plans from (weights, matroid) alone |

## 8. Verification results (real run, not asserted)

`$MUSICOM_PYTHON _web151_mbec/verify_mbec.py` — **10/10**:

1. (I1)–(I3) hold for the tritone-axis partition matroid — 125 independents, 64 bases.
2. Equicardinality — all bases have 3 notes.
3. Greedy = brute-force max-weight basis — **300/300** random weightings.
4. Non-matroid control ("≤4 notes, no minor second") violates (I3) with witness $A=\{0,2,4\}$, $B=\{1,3\}$; greedy is suboptimal in **13/300** random peaky weightings; explicit trap greedy $\{0,2,5,7\}$ = 1.30 vs optimal $\{4,6,9,11\}$ = 1.40.
5. $K_4$ graphic matroid — 16 spanning trees, Kruskal = brute force **200/200**.
6. Basis-exchange axiom — exhaustive pass on both matroids.
7. Dual — co-trees (16 bases, rank $m-r = 3$), exchange axiom holds on $M^{*}$, $T(1,1) = 16 = |\text{bases}|$ for $M$ and $M^{*}$.
8. Rank submodularity — 0 violations / 400 random pairs; $\beta(K_4)=2>0$ (connected), $\beta(\text{two-triangle direct sum})=0$ (disconnected).
9. Matroid intersection — tritone-axis × whole-tone partitions cap a chord at 2 notes.
10. $4\times8$ abstract UnitMatrix plan — 32/32 cells are bases, 28/28 consecutive moves are single exchanges, 16 distinct chords, per-voice pitch-field growth $[4,5,7,8,8,8,8,8]$.

Additional: the Python sketch printed in the standalone doc was extracted with `awk` and executed verbatim (`sketch_test.py`) → `bases: 64, circuits: 18, greedy basis [3,5,10], path length 3, dual rank 9 = m−r, OK`.

## 9. Quirks / pitfalls hit this run

1. **Co-tree ≠ forest.** The first version validated the dual by testing `forest(complement)`; on $K_4$ the complement of a star is a triangle, so it failed. Correct validation: complement construction + $r^{*}(E) = |E|-r(E)$ + exchange axiom.
2. **Dual oracle gotcha.** `S` independent in $M^{*}$ iff the **complement spans** $M$ ($r(E\setminus S) = r(E)$), *not* iff the complement is independent. The naive version computed $r^{*}(E) = 12$ instead of 9; caught by the assertion in `sketch_test.py` and fixed in both the doc and the DB pitfall list.
3. **Circuits of a $k=1$ partition matroid are pairs, not whole blocks** — 18 two-element circuits ($\binom{4}{2}\times 3$), not 3 four-element ones. First assertion in the sketch test was wrong (12); corrected to 18.
4. **Patch pitfall (a) LaTeX doubling — did not occur:** `write_file` + `patch` preserved single backslashes (`grep -cF '\\'` = 0 on the row and the section). Verified explicitly because the job brief warns about it.
5. **Patch pitfall (b) `||` prefix — did not occur:** row starts with a single pipe; 11 pipes total = 10 columns.
6. **Deterministic greedy collapses if weights are section-independent.** The first $4\times8$ plan produced only 4 distinct chords (voice 1–2 identical everywhere). Adding per-section tension + per-voice role weights raised it to 16 distinct chords. Documented as pitfall #8.
7. **Rank saturates at $\sum k_i$ for a partition matroid.** This is why the plan's prefix *rank* was constant (4) and useless as a growth metric; switched to pitch-field *cardinality* $[4,5,7,8,8,8,8,8]$ to show accumulation/saturation. Worth remembering: for partition matroids, rank measures *simultaneous* capacity, cardinality measures *accumulated* material.
8. **`rank()` by brute-force combinations** is fine on 12 elements (4096 subsets) but would be exponential on a 24-tone or 60-EDO ground set — use the closed forms ($\sum \min(|S\cap B_i|,k_i)$ for partition, union-find for graphic) in production code.
9. **`md`/heredoc restrictions respected:** temp section written via `write_file`, appended with `cat`, file removed, table patched with `patch` (no heredoc, no `execute_code`).
10. **No web-search tool in this runtime:** sources were fetched with `curl` against the Wikipedia REST/API endpoints and parsed with `jq` (cached JSON kept under `_web151_mbec/`), plus literature facts confirmed against the article text. `python3 -c` was blocked by the approval gate (cron = no approver), so all scripting went through `$MUSICOM_PYTHON` files on disk.

## 10. Files touched

| Path | What |
|---|---|
| `methods_db.md` | summary row 151 (line 161) + full section (lines 33079–33180) |
| `method_151_MBEC.md` | standalone write-up (extended math, runnable Python sketch, references) |
| `report_151.md` | this report (primary record) |
| `_web151_mbec/verify_mbec.py` | 10-check verification harness |
| `_web151_mbec/verify_mbec_results.txt` | harness output |
| `_web151_mbec/mbec_sketch.py`, `_web151_mbec/sketch_test.py` | doc sketch extracted + executed verbatim |
| `_web151_mbec/matroid.json` | cached Wikipedia source |

**Next free ID: 152.**
