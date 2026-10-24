# Method 124 — Determinantal Point Process Composition (DPPC)

**Paradigm:** Stochastic (exactly-normalized subset distribution) · **Layer:** concrete · **ID:** 124 · **Date:** 2026-10-24

> Put a positive-semidefinite kernel $L$ on your candidate musical items (pitch
> classes, metric slots, instrument slots) and sample subsets with probability
> $P(Y) \propto \det(L_Y)$. The determinant rewards sets that are individually
> good AND mutually diverse: quality $q_i$ says *how much you want item $i$*,
> similarity $S_{ij}$ says *how much two items compete*. The result is the
> probabilistic, exactly-normalized, exactly-sampleable form of the classical
> voicing/orchestration rules: "don't double the third" becomes a probability,
> the tritone becomes a determinant, and the sampler needs no burn-in.

---

## 1. The object

A determinantal point process (DPP) over a universe of $n$ candidate items is a
probability distribution over all $2^n$ subsets. With a real symmetric
positive-semidefinite kernel $L \in \mathbb{R}^{n \times n}$, the **L-ensemble**
defines

$$P(Y) \;=\; \frac{\det(L_Y)}{\det(L + I)}, \qquad Y \subseteq [n],$$

where $L_Y$ is the submatrix of $L$ indexed by $Y$ ($\det(L_\emptyset) = 1$).
The partition function is closed form (Cauchy–Binet):

$$\det(L + I) \;=\; \sum_{Y \subseteq [n]} \det(L_Y).$$

This single identity is the difference between DPPC and every energy-based
method in the catalogue (064 MRFCC, 078 IMEC, 055 SAMC): those sample an
unnormalized energy by MCMC and *never know the normalizer*; DPPC *is* its
normalizer, computable in $O(n^3)$.

**Quality–diversity decomposition** (Kulesza & Taskar 2012). Factor the kernel
as

$$L_{ij} \;=\; q_i\, S_{ij}\, q_j, \qquad q_i \ge 0, \quad S \succcurlyeq 0, \quad S_{ii} = 1,$$

with $q$ the *quality* vector (how much the composer wants item $i$: chord-tone
affinity, metric emphasis, tessitura fit) and $S$ the *similarity* kernel (how
much two items compete: pitch proximity, temporal proximity, timbral proximity).
Then $\det(L_Y) = \big(\prod_{i \in Y} q_i^2\big) \det(S_Y)$ — a set is
probable when its members are individually high-quality *and* their feature
directions are spread (large $\det(S_Y)$ = diverse).

## 2. The two musical identities

**Marginals.** With $K = L(L+I)^{-1}$ (a PSD matrix with eigenvalues in
$[0,1]$):

$$P(A \subseteq Y) \;=\; \det(K_A), \qquad P(i \in Y) = K_{ii}.$$

The probability that the tonic appears in the sampled voicing is one matrix
entry. No other method in this catalogue can answer that question in closed
form *before* generating.

**Pairwise repulsion.** For any two items $i, j$:

$$P(i, j \in Y) - P(i)P(j) \;=\; -K_{ij}^{\,2} \;\le\; 0.$$

Proof: $P(i,j) = \det\!\big(\begin{smallmatrix} K_{ii} & K_{ij} \\ K_{ji} & K_{jj} \end{smallmatrix}\big) = K_{ii}K_{jj} - K_{ij}^2$, and $P(i)P(j) = K_{ii}K_{jj}$. ∎

This is the "soft rule" generalization of Fux: "do not double the
dissonance" becomes "doubling is $K_{ij}^2$ less likely than independence" —
a rule with units and a dial, and the *only* provable repulsion mechanism in
the catalogue (090 GRDC / 112 CADDC guarantee distinctness only by exhaustive
search over rigid combinatorial objects; 064 / 078 get repulsion from an energy
but cannot normalize it).

**Expected size.** $\mathbb{E}|Y| = \operatorname{tr}(K) = \sum_n
\lambda_n/(\lambda_n+1)$ — the spectrum is the density dial.

## 3. Exact sampling (no MCMC)

Eigendecompose $L = \sum_n \lambda_n v_n v_n^T$ ($O(n^3)$).

**Plain L-ensemble (SAMPLE_DPP, Hough et al. 2006 / Kulesza & Taskar Alg. 1).**

1. Keep eigenvector $n$ with probability $\lambda_n/(\lambda_n+1)$; let $V$
   hold the kept columns. If none are kept, $Y = \emptyset$.
2. Iterative restriction: maintain $C$ (orthonormal basis of the current
   coefficient space), set $B = V C$ ($n \times m$, orthonormal columns), and
   select item $i$ with probability $\|B_{i,:}\|^2$ (a projection-DPP marginal:
   $\|B_{i,:}\|^2 = \|\mathrm{proj}_{E'} e_i\|^2$). Then restrict to the
   hyperplane $x_i = 0$: build $D = I_m - vv^\top/\|v\|^2$ with
   $v = B_{i,:}$, drop one column, QR, and set $C \leftarrow C D$. Each
   selection consumes one dimension, so the loop runs exactly $\mathrm{rank}(V)$
   times.

**k-DPP (fixed size $k$, Kulesza & Taskar 2011).** Condition on $|Y| = k$:
the normalizer becomes the elementary symmetric polynomial
$e_k(\lambda) = \sum_{|S|=k} \prod_{n \in S} \lambda_n$ (computed by the $O(nk)$
recurrence $e[i][j] = e[i-1][j] + \lambda_i e[i-1][j-1]$), the eigenvector
subset is drawn with probability $\propto \prod_{n \in S} \lambda_n / e_k(\lambda)$,
and the same iterative sampler then returns exactly $k$ items.

**Greedy MAP (deterministic mode).** $f(S) = \log\det(L_S)$ is monotone
submodular on PSD kernels, so greedy subset selection achieves
$\ge (1 - 1/e) \cdot \mathrm{OPT}$. Seed-stable, golden-hash-safe.

**Complexity.** Eigendecomposition $O(n^3)$ once per kernel (cached per
section); per draw $O(nk^2)$; k-DPP cardinality draw $O(nk)$; greedy MAP
$O(n^2)$ per item (incremental Cholesky). For the musicom scale ($n \le 128$:
a 128×128 kernel eigendecomposes in milliseconds) this is real-time capable.

## 4. Verified invariants

Script: `projects/Research/outputs/dppc_validate/verify_dppc.py` (musicom env,
numpy). Kernel: periodic RBF $\exp(-2\sin^2(\pi d/12)/\ell^2)$, $\ell = 1.0$,
on pitch-class space; quality = C-major chord affinity; exhaustive enumeration
where feasible ($2^{12} = 4096$ subsets; $C(12,3) = 220$ k-subsets).

| property | statement | measured |
|---|---|---|
| normalizer | $\sum_Y \det(L_Y) = \det(L+I)$ | 13.227449 = 13.227449 |
| marginal identity | $P(i \in Y) = [L(L+I)^{-1}]_{ii}$ | max dev 0.000000 (exact) |
| sampler correctness | spectral sampler vs exact law, 60 000 draws | max 0.0041, mean 0.0015 |
| negative correlation | $P(i,j) - P(i)P(j) = -K_{ij}^2$ | matches to 5 decimals (pc 0&2: −0.01171) |
| k-DPP cardinality | exactly $k$ | 20 000/20 000 draws, $k=3$ |
| k-DPP subset law | empirical vs $\det(L_Y)/e_k(\lambda)$ conditional | max dev 0.0030 over 220 subsets |
| k-DPP normalizer | $e_3(\lambda) = \sum_{|Y|=3}\det(L_Y)$ | 2.673900 = 2.673900 |
| repulsion | mean nearest-neighbor pc distance, $k=3$ | 2.303 (DPP) vs 1.766 (i.i.d. quality-weighted) → **1.30×** wider |
| tonal gravity | chord-tone mass (pcs 0,4,7,11) | 1.330 of $\mathbb{E}|Y|=1.854$ → **71.7 %** |
| chromatic suppression | P(chromatic pc ∈ sample) | ≤ 0.022 vs P(tonic) = 0.399 |
| expected size | $\mathbb{E}|Y| = \sum_n \lambda_n/(\lambda_n+1)$ | 1.854 theory vs 1.855 measured |
| determinism | same seed + kernel | identical sample ($k=4$ → exactly 4 items) |
| greedy MAP | log-det mode | pcs {0,4,7} = C major triad, spread 3.0 |

**Musical reading of the exact marginals** (C-major kernel, $n = 12$):
P(C)=0.399, P(G)=0.391, P(E)=0.329, P(B)=0.211, P(A)=0.200, P(D)=0.144,
P(F)=0.085; chromatic neighbors all ≤ 0.022. Top-5 exact k=3 voicings:
{C,E,G} 0.158, {E,G,B} 0.078, {C,E,A} 0.070, {C,G,A} 0.059, {C,D,G} 0.046 —
a C-major-family voicing distribution with real spread.

## 5. Python implementation sketch (the verified sampler, condensed)

```python
import numpy as np

def sample_kdpp(L, k, rng):
    """Exact k-DPP sample (Kulesza & Taskar 2011/2012). L PSD, k <= rank."""
    n = L.shape[0]
    lam, V = np.linalg.eigh(L)
    lam = np.clip(lam, 0.0, None)
    # e[i][j] = e_j(lambda_1..lambda_i); elementary symmetric polynomials
    e = np.zeros((n + 1, k + 1)); e[0, 0] = 1.0
    for i in range(1, n + 1):
        e[i, 0] = 1.0
        for j in range(1, min(i, k) + 1):
            e[i, j] = e[i - 1, j] + lam[i - 1] * e[i - 1, j - 1]
    # sample eigenvector subset of size k with prob ∝ prod(lambda) / e_k
    S, i, j = [], n, k
    while j > 0:
        if i == j:
            S.extend(range(j - 1, -1, -1)); break
        if rng.random() < lam[i - 1] * e[i - 1, j - 1] / e[i, j]:
            S.append(i - 1); j -= 1
        i -= 1
    Vk = V[:, S]
    # iterative subspace restriction: exactly k items
    C = np.eye(k); selected = np.zeros(n, dtype=bool); items = []
    while C.shape[1] > 0:
        B = Vk @ C; B[selected, :] = 0.0          # selected -> prob 0
        probs = np.einsum('ij,ij->i', B, B)
        probs /= probs.sum()
        idx = int(rng.choice(n, p=probs))
        items.append(idx); selected[idx] = True
        v = B[idx, :]
        D = np.eye(C.shape[1]) - np.outer(v, v) / (v @ v)   # restrict x_idx=0
        D = D[:, :-1]
        Q, _ = np.linalg.qr(D)
        C = C @ Q[:, :C.shape[1] - 1]
    return np.array(sorted(items))
```

(For the plain L-ensemble, replace the eigenvector-subset block with
`keep = rng.random(n) < lam/(lam+1)` and `Vk = V[:, keep]`; for greedy MAP,
select items greedily by $\log\det$ increment via Cholesky. Full script with
all checks: `projects/Research/outputs/dppc_validate/verify_dppc.py`.)

## 6. Musical mapping

| musical object | items in the pool | quality $q_i$ | similarity $S_{ij}$ | cardinality $k$ |
|---|---|---|---|---|
| voicing / chord | scale pcs (n = 12, 7, …) | chord-tone/tonic affinity | pitch-proximity RBF | 3 (triad), 4 (7th) |
| rhythm / groove | metric slots per bar | downbeat/metrical weight | temporal-proximity RBF | notes per bar |
| orchestration | (instrument × register) slots | tessitura/role fit | timbral+pitch proximity | instruments playing |
| section pool | pcs of a harmonic region | pivot-tone weights | pitch proximity (block-structured) | pool size |

**Candidate code path:** `generators/dpp_composition.py` — class `DPPComposer`
with `build_kernel()`, `eigendecompose()` (cached per section),
`sample_dpp()`, `sample_kdpp()`, `greedy_map()`, `condition()` (zero-forced
items), `realize_cell()`; consumed by `workflows/unitmatrix_composer.py`
(cells = k-DPP draws padded via `_unit_from_events` for the zero-drift gate).
The abstract pre-pass (per-region kernels + quality vectors as weighted
pc-pools) feeds `rules/subset_network.py`.

## 7. References

- Macchi, O. (1975). "The coincidence approach to stochastic point processes." *Adv. Appl. Probab.* 7(1), 83–122. (origin: fermions / Pauli repulsion)
- Hough, J. B., Krishnapuram, M., Bolin, M. & Keller, J. B. (2006). "Determinantal point processes and independence." *Probability Surveys* 3, 206–242. (exact spectral sampling)
- Kulesza, A. & Taskar, B. (2011). "k-DPPs: Fixed-Size Determinantal Point Processes." *ICML 2011*, 1193–1200.
- Kulesza, A. & Taskar, B. (2012). "Determinantal Point Processes for Machine Learning." *Found. Trends Mach. Learn.* 5(2–3), 123–286. arXiv:1207.6083 (verified via arXiv API 2026-10-24).
- El-Nouby, A. et al. (2021). "GDPP: Learning Diverse Generations Using Determinantal Point Process." *ICLR 2021*. arXiv:1812.00068 (verified 2026-10-24). (learned-quality variant)
- arXiv:2607.06063 (2026). "Determinantal point process sampling for bioacoustic active learning." (audio-domain application; verified 2026-10-24)
- Wikipedia: "Determinantal point process" (fetched 2026-10-24).
- In-catalogue: 090 GRDC, 112 CADDC (deterministic distinct-difference cousins); 064 MRFCC, 078 IMEC (unnormalized energy repulsion); 097 MaxEnt-C (no diversity mechanism).
