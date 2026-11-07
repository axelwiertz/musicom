# Method 137 — Tropical (Max-Plus) Algebra Composition (TMPC)

**Paradigm:** Rules-Based · **Layer:** concrete · **Registered:** 2026-11-07
**Candidate code path:** `generators/tropical_maxplus.py`
**Prototype:** `_web138/tmpc_sketch.py` (runs, output in `_web138/tmpc_sketch_output.txt`), fact-checks in `_web138/verify_137_TAC.py`

---

## 1. The idea in one line

Compose in the **idempotent max-plus semiring** — where "add" means "take the larger" and "multiply" means "add" — so that the piece *is* a timed event graph: each voice's next onset is the latest of its causal predecessors' requirements, the max cycle mean is the tempo, the eigenvector is the groove, and the cyclicity is the bar.

## 2. The algebra

On $S=\mathbb{R}\cup\{-\infty\}$:

$$a\oplus b=\max(a,b),\qquad a\otimes b=a+b,\qquad \varepsilon=-\infty,\qquad e=0 .$$

- $(S,\oplus)$ is a commutative, associative, **idempotent** monoid: $a\oplus a=a$. Hence no additive inverse — **no subtraction**.
- $(S,\otimes)$ is a commutative group on $\mathbb{R}$ with identity $e=0$ and absorbing $\varepsilon$.
- $\otimes$ distributes over $\oplus$: $a\otimes(b\oplus c)=(a\otimes b)\oplus(a\otimes c)$.
- Verified on 2000 random triples: idempotent, commutative, associative, distributive, identities all hold.

Matrix product in this semiring, for $A\in S^{n\times m}$, $B\in S^{m\times p}$:

$$(A\otimes B)_{ij}=\bigoplus_{k=1}^{m}A_{ik}\otimes B_{kj}=\max_k\left(A_{ik}+B_{kj}\right).$$

**Theorem (path interpretation).** $(A^{\otimes k})_{ij}$ = maximum weight of a walk of **exactly** $k$ edges from $i$ to $j$; $-\infty$ if none exists. Verified by brute force over all $n^{k+1}$ paths, $k=1..4$, $3\times3$.

## 3. The four spectral quantities, and what they mean musically

### 3.1 Max cycle mean = tempo
$$\lambda(A)=\max_{C\ \text{cycle}}\frac{|C|_{\otimes}}{|C|}=\max_C\frac{\sum_{e\in C}w(e)}{|C|}.$$

**Karp (1978)** computes it in $O(n^3)$ from the walk table $F_k(v)$ (best walk of length $k$ from a fixed source to $v$):

$$\lambda=\max_{v}\ \min_{0\le k\le n-1}\frac{F_n(v)-F_k(v)}{n-k}.$$

*Verified honesty note:* the `min_v max_k` nesting that looks like the textbook statement matched brute-force cycle enumeration only **147/300** random matrices in my probe; the `max_v min_k` form above matched **300/300** for every source (`_web138/probe_karp.py`). If you implement Karp from memory, test it against brute force first.

Musically: with durations in $A$, $\lambda$ is the asymptotic inter-onset interval — the tempo, fixed by the *slowest* cycle, not by an average. $\lambda$ is always rational with denominator $\le n$ (verified 200/200), so tempo ratios are simple by construction.

### 3.2 Eigenvector = groove
$v\in S^n$, $v\ne\varepsilon$, with $A\otimes v=\lambda\otimes v$, i.e. $v_i=\max_j(A_{ij}+v_j)-\lambda$. It is unique up to tropical scaling ($v\mapsto v+c$) for irreducible $A$. Reading: the steady-state **phase offset** of each voice — the groove's micro-timing skeleton.

Computation: relax the reduced system from a reference node $r$ ($v_r=0$, others $\varepsilon$) for $n$ rounds. Because no cycle has positive *reduced* weight ($w(e)-\lambda\le0$), the supremum over walks is attained on a simple path, so $n$ rounds suffice.

> **Trap (measured).** Normalised power iteration does **not** converge when the cyclicity $c>1$; the iterates orbit with period $c$. On a critical 4-cycle with waits $(1,0.5,1.5,1)$ it returned $(0,0,0,0)$; the true eigenvector is $(0,0,0.5,0)$.

### 3.3 Cyclicity = bar
$c$ = gcd of the lengths of the cycles in the **critical graph** (edges on cycles attaining $\lambda$). Ultimate periodicity:

$$A^{\otimes(k+c)}=\lambda c\otimes A^{\otimes k}\quad\text{for all }k\ge n-1 .$$

Verified for $c=2,3,4$ at $k=3c$. Musically $c$ is the bar length in steps — derived, not chosen. Transient length $\le n$.

### 3.4 Kleene star = form
$$A^{*}=I\oplus A\oplus A^{\otimes2}\oplus\cdots=\sup_{k\ge0}A^{\otimes k}.$$
For a cycle-free (DAG) matrix this is the all-pairs **longest path**; with cycles, the star diverges unless $\lambda\le0$ (rescale by $-\lambda$ to get a finite closure). Verified on a DAG: $0\to2=5$ direct, $0\to3=8$ via 2.

## 4. The combinatorial layer

**Tropical determinant** (= max over permutations; for generic matrices equals the tropical permanent):
$$\operatorname{tdet}(M)=\max_{\sigma\in S_n}\sum_{i=1}^{n}M_{i\sigma(i)}.$$
This is the **assignment problem** (Hungarian, $O(n^3)$), i.e. the maximum-weight bijection. Verified: $6\times6$ case $=48$ over all 720 permutations. Musically: the bijective voice exchange — which line goes to which voice for maximal total motion.

**Tropical rank** = the largest $r$ such that some $r\times r$ minor is tropically nonsingular (its tdet is finite and attained at a unique permutation). It counts *independent* voices — the real polyphonic thickness, and it can be strictly smaller than the classical rank (e.g. a $3\times3$ matrix of classical rank 3 can have tropical rank 2).

**Tropical polynomial and roots.** For $p(x)=\bigoplus_{i=0}^{d}a_i\otimes x^{\otimes i}=\max_i(a_i+ix)$, the graph is a convex piecewise-linear function; the *roots* are the breakpoints where two terms tie. A degree-$d$ polynomial has at most $d$ roots (tropical fundamental theorem) and they factor as $p(x)=a_d\otimes\bigotimes_i(x\oplus r_i)$ with
$$\sum_i r_i=a_0-a_d,\qquad \max_i r_i=a_1-a_d\ \ (\text{for } d=2).$$
Verified for $0\oplus3x\oplus0x^2$: roots $\{-3,+3\}$, sum $0$, max $3$.

**Dequantization (Litvinov).** For $h>0$,
$$x\oplus_h y=h\log\left(e^{x/h}+e^{y/h}\right)\xrightarrow[h\to0^+]{}\max(x,y).$$
Measured error: $3.1\times10^{-1}$ at $h=1$, $4.5\times10^{-6}$ at $h=0.1$, $0$ at $h=0.01$. This is the one-parameter bridge from the idempotent (hard, machine-locked) algebra to the classical (smooth, humanized) one.

## 5. Musical mapping

| Matrix entry | Reading |
|---|---|
| $A_{ij}=w$, $w\in\mathbb{R}$ | voice $i$ waits $w$ after a firing of $j$ (rhythm) / moves $w$ semitones from state $j$ to $i$ (pitch) |
| $A_{ij}=-\infty$ | forbidden: no causal link / no melodic move |
| $x^{(k)}_i$ | onset time of voice $i$'s $k$-th note |
| $\lambda$ | tempo (duration units) / drift rate (semitone units) |
| $v$ | groove offsets |
| $c$ | bar length |
| $\operatorname{tdet}$ | bijective voice exchange |
| $A^*$ | formal arcs (longest reachable span) |
| tropical rank | number of independent voices |
| tropical roots | pivot tones where two readings tie |
| $h$ | humanized ↔ grid-locked blend |

## 6. Implementation sketch (runs on the musicom python)

```python
NEG = float('-inf')

class TropMat:
    def __init__(self, rows): self.r = [list(x) for x in rows]

    def __matmul__(self, other):                       # max-plus product, O(n^3)
        n, m, p = len(self.r), len(other.r), len(other.r[0])
        out = [[NEG] * p for _ in range(n)]
        for i in range(n):
            for j in range(p):
                for k in range(m):
                    a, b = self.r[i][k], other.r[k][j]
                    if a != NEG and b != NEG:
                        out[i][j] = max(out[i][j], a + b)
        return TropMat(out)

    def pow(self, k):                                  # square-and-multiply for large k
        n = len(self.r)
        R = TropMat([[0 if i == j else NEG for j in range(n)] for i in range(n)])
        for _ in range(k):
            R = R @ self
        return R


def max_cycle_mean(A):
    """Karp 1978, dual nesting (verified 300/300 vs brute force)."""
    n = len(A.r)
    F = [[NEG] * n for _ in range(n + 1)]
    for s in range(n):
        F[0] = [NEG] * n; F[0][s] = 0
        for k in range(1, n + 1):
            for j in range(n):
                F[k][j] = max((F[k-1][i] + A.r[i][j] for i in range(n)
                               if F[k-1][i] != NEG and A.r[i][j] != NEG), default=NEG)
        best = NEG
        for v in range(n):
            if F[n][v] == NEG: continue
            mn = min((F[n][v] - F[k][v]) / (n - k) for k in range(n) if F[k][v] != NEG)
            best = mn if best == NEG else max(best, mn)
        if s == 0: lam = best
        elif abs(best - lam) > 1e-9: raise AssertionError("reducible matrix: lambda is per-component")
    return lam


def eigenvector(A, lam, r=0):
    """v with A (x) v = lam + v ; relaxation, NOT power iteration (orbit period c)."""
    n = len(A.r)
    v = [NEG] * n; v[r] = 0
    for _ in range(n):
        nv = list(v)
        for i in range(n):
            cand = max((A.r[i][j] + v[j] - lam for j in range(n)
                        if A.r[i][j] != NEG and v[j] != NEG), default=NEG)
            if cand != NEG and cand > nv[i]: nv[i] = cand
        v = nv
    for i in range(n):                                  # assert the eigen-equation
        lhs = max((A.r[i][j] + v[j] for j in range(n)
                   if A.r[i][j] != NEG and v[j] != NEG), default=NEG)
        if lhs != NEG: assert abs(lhs - (lam + v[i])) < 1e-9
    return v


def schedule(A, k_max, x0):
    """x^(k+1)_i = max_j (A_ij + x^(k)_j)  -> onset times in ticks/beats."""
    xs = [list(map(float, x0))]
    for _ in range(k_max):
        x = xs[-1]
        xs.append([max(A.r[i][j] + x[j] for j in range(len(x)) if A.r[i][j] != NEG)
                   for i in range(len(A.r))])
    return xs
```

Example run (4 voices, critical 4-cycle with waits 1, 0.5, 1.5, 1):

```
lambda (beats/step) = 1.0
eigenvector (groove offsets, beats) = [0, 0.0, 0.5, 0.0]
cyclicity (bar, steps) = 4
  k=1 onsets=[1.0, 0.5, 1.5, 1.0]
  k=2 onsets=[1.5, 2.0, 2.5, 2.0]
  k=3 onsets=[3.0, 3.0, 3.5, 2.5]
  k=4 onsets=[4.0, 4.0, 4.0, 4.0]      <- bar closes exactly
tropical determinant (best bijective voice exchange) = 20
tropical roots of 0 (+) 3x (+) 0x^2 = [-3.0, 3.0]
```

Note the swing: chords sit 0.5 beat inside the beat, and the bar closes exactly at $k=4$ because $c=4$ and $\lambda=1$. That exactness *is* the method.

## 7. Filling the UnitMatrix

```python
from workflows.unitmatrix_composer import UnitMatrixComposer, create_note_unit
from structures import MidiInstrument

c = UnitMatrixComposer(bpm=120)
c.create_matrix(num_voices=4, num_sections=4)
for name, prog in [("Bass", 33), ("Chords", 0), ("Lead", 73), ("Drums", 0)]:
    c.add_voice(name, program=prog, channel=9 if name == "Drums" else 0)
for s in "ABCD":
    c.add_section(s, bars=1)
# xs[k] = onset beat of every voice at firing k -> event list per section window
# pad each cell to section_len via _unit_from_events(events, section_len)
ok, msg = c.validate()          # must be True (zero drift)
c.to_midi("tmpc137.mid")
```

**Voices = rows = states.** A voice is defined by its dependencies in $A$, not by a stored melody; re-orchestration is a matrix edit.

**Sections = columns = $k$-windows** of length $c$ (or blocks of the matrix's block decomposition). Re-estimating $\lambda$ per column gives an explicit tempo map; a reducible $A$ gives poly-tempo form for free.

**Cells = MusicUnit.** One firing → one event; coincident firings → one chord unit; every cell padded to `section_len`.

## 8. Worked compositional recipe

1. Choose the form as a block structure: block-triangular = through-composed, irreducible = returning.
2. Set $\lambda$ = tempo by choosing the intended slowest loop (the critical graph). Other edges may be anything $\le\lambda$ on average.
3. Read $v$ as the groove's phase; if it is all zeros, the bar is metrically square — add a non-$\lambda$ wait to swing it.
4. Read $c$ as the bar; use $A^{\otimes k}$ residual periodicity to confirm the bar closes.
5. Build countersubjects by editing rows (which predecessor each voice waits for), not by writing notes.
6. Choose the modulation pivot from the tropical roots of the pitch polynomial.
7. Assign lines to voices with $\operatorname{tdet}$ (max motion) or $-\operatorname{tdet}$ (min motion, by negating $M$).
8. Render at $h=0$ for the structural checks; blend with $h>0$ for the humanized pass.

## 9. References

1. Cuninghame-Green, R. A. (1979). *Minimax Algebra.* LNMES 166, Springer.
2. Cohen, G., Dubois, D., Quadrat, J.-P., & Viot, M. (1985). "A linear-system-theoretic view of discrete-event processes…" *IEEE TAC* 30(3), 210–220.
3. Baccelli, F., Cohen, G., Olsder, G. J., & Quadrat, J.-P. (1992). *Synchronization and Linearity.* Wiley.
4. Karp, R. M. (1978). "A characterization of the minimum cycle mean in a digraph." *Discrete Math.* 23, 309–311.
5. Simon, I. (1988). "Recognizable sets with multiplicities in the tropical semiring." *MFCS*, LNCS 324, 107–120.
6. Pin, J.-É. (1998). "Tropical semirings." In *Idempotency*, Newton Inst. Publ. 11, CUP, 50–69.
7. Litvinov, G. L. (2007). "The Maslov dequantization, idempotent and tropical mathematics." *J. Math. Sci.* 135(5), 3061–3083.
8. Butkovič, P. (2010). *Max-linear Systems: Theory and Algorithms.* Springer.
9. Develin, M., & Sturmfels, B. (2004). "Tropical convexity." *Documenta Math.* 9, 1–27.
10. Maclagan, D., & Sturmfels, B. (2015). *Introduction to Tropical Geometry.* AMS GSM 161.
11. Joswig, M. (2021). *Essentials of Tropical Combinatorics.* AMS.
12. Howard, R. A. (1960). *Dynamic Programming and Markov Processes.* MIT Press — policy iteration, the fast alternative for $\lambda$/$v$ at scale.
13. Wikipedia, "Tropical geometry" (cached `_web138/wiki_tropical_geometry.txt`).

## 10. Verification log

`_web138/verify_137_TAC.py` → `verify_137_output.txt` (all pass):

```
0. semiring axioms (2000 random triples): all True
1. A^(x)k == exact-length-k max walk, k=1..4, 3x3, all paths
2. Karp lambda == brute-force simple cycles, 50 random 3x3, sources agree
3. cyclicity: c-cycle graphs, A^(k+c) = A^k + lambda*c exactly (c=2,3,4)
4. tropical determinant: 3x3 = 11, 6x6 = 48 over 720 permutations
5. tropical roots 0 (+) 3x (+) 0x^2 = [-3, 3]; convex envelope
6. Kleene star on DAG == longest paths (0->2=5, 0->3=8)
7. asymptotic increment of A^k at k=40 == lambda exactly
probes: lambda rational with denom <= n (200/200); soft-max error 4.5e-6 at h=0.1
```
