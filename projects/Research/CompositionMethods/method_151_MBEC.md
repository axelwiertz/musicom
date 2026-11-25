# Method 151 — Matroid Basis-Exchange Composition (MBEC)

**Layer:** abstract · **Paradigm:** Rules-Based · **Elements:** Pitch, Harmony, Rhythm, Structure, Texture
**Feeds:** `rules/subset_network.py` (via `rules/matroid.py`) · **Status:** verified 10/10 (`_web151_mbec/verify_mbec.py`)

---

## 1. One-line idea

Declare the harmony constraint as a **matroid** on the 12 pitch classes; then a section's chord is the provably optimal maximum-weight **basis** found by one-pass greedy, every modulation is a sequence of single-note **basis exchanges**, and every chord has the same number of notes **by theorem**.

## 2. Why a matroid specifically

A matroid $(E, \mathcal{I})$ is the unique combinatorial structure for which the following are all true simultaneously:

| Property | Statement | Musical payoff |
|---|---|---|
| Greedy optimality | max-weight basis = sort by weight, accept if independent | one-pass, non-backtracking section composition; no search |
| Converse | if greedy is optimal for every weighting, the family **is** a matroid | the axiom is a *design requirement*, not decoration |
| Exchange | $A, B$ bases, $x \in A\setminus B \Rightarrow \exists y \in B\setminus A$ with $A-x+y$ a basis | any two chords are $d$ single-note moves apart → parsimonious modulation with proof |
| Equicardinality | all bases have size $r(E)$ | chord size (voice count) is constant → fixed-ensemble / zero-drift friendly |
| Submodular rank | $r(A)+r(B) \ge r(A\cup B)+r(A\cap B)$ | density saturates with diminishing returns |
| Duality | bases of $M^{*}$ = complements of bases of $M$ | a free "everything not in the chord" layer (upper structure, cut seam) |

Formal basis of the first two: Rado (1957), Edmonds (1971). Exchange: Whitney (1935); strong (symmetric) form: Brualdi. Rank: Edmonds (1970).

## 3. The algorithm

```
build(E, family, params) -> M                     # independence oracle + rank
for each section s:
    w_s = tension_weights(s)                      # root, colour, role, chromatic pull
    for each voice v:
        B[v][s] = greedy_basis(M, w_s ⊙ role_weight[v])
        assert is_basis(M, B[v][s])
    check exchange_path(B[v][s-1], B[v][s])       # |A\B| single swaps, each a basis
emit PatternNetwork(bases, exchange_distances, tension_arc)
```

Reference implementation sketch (pure Python, mirrors the verification harness):

```python
from itertools import combinations

class Matroid:
    """Independence oracle. Partition or graphic in practice."""
    def __init__(self, E, indep): self.E, self.indep = frozenset(E), indep
    def is_indep(self, S):  return self.indep(frozenset(S))
    def rank(self, S):
        for r in range(len(S), -1, -1):
            if any(self.is_indep(c) for c in combinations(tuple(S), r)): return r
        return 0
    def bases(self):
        out = {S for r in range(len(self.E) + 1)
                 for S in map(frozenset, combinations(self.E, r)) if self.is_indep(S)}
        return {S for S in out if all(not self.is_indep(S | {x}) for x in self.E - S)}
    def circuits(self):
        return {S for S in self._dep() if all(self.is_indep(S - {x}) for x in S)}
    def _dep(self):
        return {frozenset(c) for r in range(1, len(self.E) + 1)
                for c in combinations(self.E, r) if not self.is_indep(c)}

def partition_matroid(blocks, caps):
    def indep(S): return all(sum(x in b for x in S) <= k for b, k in zip(blocks, caps))
    return Matroid(range(12), indep)

def greedy_basis(M, w):
    B, acc = frozenset(), set()
    for x in sorted(M.E, key=lambda p: (-w[p], p)):     # deterministic ties
        if M.is_indep(B | {x}): B |= {x}
    B = frozenset(B)
    assert all(not M.is_indep(B | {x}) for x in M.E - B)   # is a basis
    return B

def exchange_path(M, A, B):
    """d(A,B) single-element basis exchanges."""
    path, cur = [A], A
    while cur != B:
        for x in cur - B:
            for y in B - cur:
                nxt = frozenset(cur - {x} | {y})
                if M.is_indep(nxt) and len(nxt & B) > len(cur & B):
                    path.append(nxt); cur = nxt; break
            else: continue
            break
    return path

def dual(M):
    """S is independent in M* iff E\\S SPANS M (r(E\\S) = r(E)) — not "complement is independent"."""
    return Matroid(M.E, lambda S: M.rank(M.E - frozenset(S)) == M.rank(M.E))
```

## 4. Four instantiations

**4.1 Partition matroid** — `E = 12 pcs`, blocks $B_i$, caps $k_i$; $S$ independent iff $\#(S \cap B_i) \le k_i$. Rank $=\sum_i \min(|S\cap B_i|, k_i)$, so rank is *capped by the caps* — the whole ground set has rank $\sum k_i$ (verified: 4 for the fifths matroid, which is why every chord there is a 4-note chord).

- Tritone-axis version: blocks = the three diminished-seventh tetrads $\{0,3,6,9\}, \{1,4,7,10\}, \{2,5,8,11\}$, $k=(1,1,1)$ → 125 independents, 64 trichord bases. Musical reading: no note doubled inside a symmetric family.
- Fifths-region version: blocks $\{0,7,2,9\}, \{5,10,3,8\}, \{1,6,11,4\}$, $k=(2,1,1)$ → 96 tetrad bases. Musical reading: a chord may take at most two notes from the sharp side of the circle of fifths.

**4.2 Graphic (cycle) matroid** — ground set = edges of a chord-transition multigraph; independent = acyclic. Bases = spanning trees ($|V|-1$ edges); circuits = simple cycles = *cadences* (the progression returned to a sonority); dual = bond matroid, whose bases are the co-trees = the cuts = places where all voices move at once (section seams). Max-weight basis = Kruskal = the best loop-free progression across the vocabulary.

**4.3 Linear / representable matroid** — column $j$ = a vector for pitch class $j$ (interval-content vector, or pitch-class Fourier-balance coefficients); independent = linearly independent columns over $\mathbb{Q}$ or $\mathbb{R}$. Rank = number of independent tonal axes active in the section; rank drop = genuine simplification. Representability depends on the field — the Fano matroid is the standard warning that not every matroid is representable over every field.

**4.4 Transversal / intersection** — a transversal matroid comes from bipartite matching between ground elements and slots; conversely, **maximum bipartite matching = intersection of two partition matroids**, so voicing assignment ("which chord tone goes to which voice") is the same optimisation. Two constraints are polynomial; **three or more is NP-complete** (verified cap: tritone-axis × whole-tone intersection admits only 2-note chords).

## 5. Tension, form and invariants

- Per-section weights $w_s(p) = \alpha\, \text{root}(p) + \beta\, \text{quality}(p) + \gamma\, \text{colour}(p) + \delta\, t_s \cdot \text{pull}(p)$; greedy basis = argmax chord for that target.
- Exchange distance $d(B_{s-1}, B_s)$ = number of notes that move between sections; a modulation plan is a path with prescribed step counts.
- Tension curve $\tau_s = a (1 - \bar w_s/w_{\max}) + b\, d(B_{s-1},B_s)/r(E)$.
- $T(1,1)$ = #bases (vocabulary size; 96 for the fifths matroid, 16 for $K_4$'s cycle matroid).
- $\beta(M) = (-1)^{r(E)}\sum_{X \subseteq E} (-1)^{|X|} r(X)$; $\beta \ge 0$ and $\beta = 0$ iff $M$ is disconnected (verified: 2 for $K_4$ cycle matroid, 0 for a two-triangle direct sum). A form with $\beta = 0$ is built from blocks that cannot interact — sometimes intended, often a bug.
- Whitney numbers $W_i$ = number of rank-$i$ flats = number of distinct harmonic regions of each dimension.

## 6. Verified numbers (this run)

| # | Check | Result |
|---|---|---|
| 1 | (I1)–(I3) for tritone-axis partition matroid | pass — 125 independents, 64 bases |
| 2 | equicardinality | pass — $r = 3$ for all 64 bases |
| 3 | greedy = brute-force max-weight basis | 300/300 |
| 4 | non-matroid "≤4 notes, no minor second" | fails (I3) with witness $A=\{0,2,4\}, B=\{1,3\}$; greedy loses 13/300; explicit trap 1.30 vs 1.40 |
| 5 | $K_4$ graphic matroid | 16 spanning trees; Kruskal = brute force 200/200 |
| 6 | basis-exchange axiom | pass, exhaustive, both matroids |
| 7 | dual / Tutte | co-trees = 16 bases, rank $m-r = 3$; exchange holds on $M^{*}$; $T(1,1)=16$ both |
| 8 | rank submodularity + beta invariant | 0 violations/400; $\beta=2>0$ connected, $\beta=0$ disconnected |
| 9 | matroid intersection | 2-note chord cap |
| 10 | 4×8 abstract plan | 32/32 cells are bases; 28/28 single-exchange moves; 16 distinct chords; pitch-field growth $[4,5,7,8,8,8,8,8]$ |

Reference plan produced (voice rows × 8 sections, pitch-class sets in hex):

```
V0  0347 | 0349 | 059B | 257B | 2347 | 059B | 257B | 0347
V1  047A | 0489 | 0459 | 257B | 278B | 0459 | 257B | 0347
V2  047A | 249A | 2459 | 257B | 247A | 2459 | 257B | 0457
V3  0478 | 0489 | 059B | 579B | 789B | 059B | 579B | 0478
```

## 7. UnitMatrix contract (abstract layer)

| UnitMatrix slot | MBEC content |
|---|---|
| Row = voice | weight profile over one shared matroid, or a per-voice matroid |
| Column = section | tension target, restriction set $E_s$, matroid variant, density target, cadence policy |
| Cell = `MusicUnit` (abstract) | `{basis B_vs, weights, rank r(E), circuits_hit, exchange_distance_from_prev}` — no ticks, no registers, no durations |

Realisation is a separate concrete method (011 voice-leading search, 013 transforms, or a style arranger), which owns registers/durations/velocities, the equal-length invariant, `validate()` and `to_midi()`.

## 8. Pitfalls

1. Most natural constraint families are **not** matroids — test (I3) or greedy-vs-brute-force before trusting a rule.
2. Equicardinality fixes chord size inside one matroid; vary size via restriction, truncation, erosion, or a second matroid.
3. Loops and coloops act silently (banned / mandatory pitch classes) — always print them.
4. Break greedy ties by $(-w, \text{pc})$ for reproducibility.
5. The dual is not "the opposite chord": complements are large, and a co-tree may contain a cycle (a $K_4$ star's complement is a triangle).
6. Three-matroid intersection is NP-complete; two is polynomial.
7. A spanning tree has exactly $|V|-1$ edges; long progressions need linked trees or multigraphs.
8. Without per-section tension and per-voice role weights, deterministic greedy returns the same basis everywhere.
9. MBEC must stay tick-free — emitting events breaks layer chaining and zero-drift responsibility.
10. $\beta = 0$ and the Tutte polynomial are diagnostics; the polynomial is #P-hard in general, so cache it.

## 9. References

- Whitney, H. (1935). "On the abstract properties of linear dependence." *Amer. J. Math.* 57(3), 509–533.
- Rado, R. (1957). "Note on independence functions." *Proc. London Math. Soc.* 7(1), 300–320.
- Edmonds, J. (1970). "Submodular functions, matroids, and certain polyhedra." *Combinatorial Structures and Their Applications*, 69–87.
- Edmonds, J. (1971). "Matroids and the greedy algorithm." *Math. Programming* 1, 127–136.
- Tutte, W. T. (1954). "A contribution to the theory of chromatic polynomials." *Canad. J. Math.* 6, 80–91.
- Oxley, J. (2011). *Matroid Theory*, 2nd ed. Oxford University Press.
- White, N., ed. (1992). *Matroid Applications*. Cambridge University Press.
- Tymoczko, D. (2011). *A Geometry of Music*. Oxford University Press. (efficient voice leading = minimal-note motion)
- Wikipedia: "Matroid" (fetched 2026-11-26; axioms, greedy characterisation, intersection complexity, duality, Tutte/beta invariants).
