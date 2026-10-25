# Method 125 — Low-Discrepancy Sequence Composition (LDSC)

**Paradigm:** Rules-Based (deterministic equidistributed digital sequences) · **Layer:** concrete · **ID:** 125 · **Date:** 2026-10-25

> Replace the random number generator and the periodic grid with a
> deterministic *equidistributed* sequence. The van der Corput radical
> inverse $g_b(n)$ — the digits of $n$ in base $b$, reversed after the
> radix point — fills the timeline by *recursive bisection*: each new
> onset lands in the largest empty gap. Star discrepancy
> $D_N^* \le C(\log N)^s/N$ proves every window gets its fair share of
> events. Evenness with a proof, without periodicity, and without
> randomness: the aperiodic complement to Euclidean rhythm (012), the
> proof-backed replacement for RNG-driven placement (040/048/053), and
> the "quasi-random" layer every stochastic method can lean on.

---

## 1. The object

For $n \ge 1$ with base-$b$ digits $n = \sum_{k=0}^{L-1} d_k(n)\, b^k$, the
**radical inverse** (van der Corput, 1935) is

$$g_b(n) \;=\; \sum_{k=0}^{L-1} d_k(n)\, b^{-k-1} \;=\; 0.\,d_{L-1}\cdots d_0 \text{ (base } b\text{)}.$$

The first values (verified exactly):

| $n$ | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| $g_2(n)$ | 1/2 | 1/4 | 3/4 | 1/8 | 5/8 | 3/8 | 7/8 | 1/16 |
| $g_3(n)$ | 1/3 | 2/3 | 1/9 | 4/9 | 7/9 | 2/9 | 5/9 | 8/9 |

**Star discrepancy.** With $D_N^*$ the supremum over prefix intervals $[0,x)$
of $|\#\{n \le N : g_b(n) < x\}/N - x|$:

$$D_N^*(g_b(1), \dots, g_b(N)) \;\le\; C\,\frac{\log N}{N},$$

and for the $s$-dimensional Halton sequence $x(n) = (g_{b_1}(n), \dots,
g_{b_s}(n))$ with pairwise-coprime bases (Halton 1960):

$$D_N^*(x(1), \dots, x(N)) \;\le\; C'\,\frac{(\log N)^s}{N}.$$

Random i.i.d. points only reach $\Theta(N^{-1/2})$ *in expectation* —
measured here $D^*_{1024}(g_2) = 0.00098$ against a random mean of
$0.02922$ (30× better), inside the bound $(\log_2 N + 2)/N = 0.01172$.
This single inequality is the method: **balance, guaranteed** — the
periodic evenness of 012/069 made aperiodic, the statistical frequency
law of 084 ZMRC made exact, the ergodic guarantee of 121 IETC made by
digit reversal instead of rotation.

## 2. The three musical identities

**Identity 1 — the largest-gap bisection (rhythm).** Every new point of
$g_2$ lands in the largest currently-empty gap of the timeline (verified for
$n = 1..255$). The van der Corput rhythm *is* the sound of recursive
bisection: onset 1 at the half, onset 2 at a quarter, onset 3 at three
quarters, onset 4 at an eighth — each new onset fills the biggest silence
so far. This is the aperiodic, self-organizing counterpart of Euclidean
groove (012): same maximal evenness, no bar periodicity.

**Identity 2 — visit frequency = region width (harmony).** Partition
$[0,1)$ into regions $R_j$ (HOME/LIFT/TENSE/TURN) of widths $w_j$. Then
$\lim_{N\to\infty} \#\{n \le N : g_b(n) \in R_j\}/N = w_j$ (equidistribution),
and for finite $N$ the deviation is bounded by the discrepancy. Verified:
widths $[0.35, 0.20, 0.20, 0.25]$ at $N = 2000$ gave visit frequencies
$[0.350, 0.200, 0.200, 0.249]$ — max deviation $0.0010$. Tonal gravity is
a *dial with a proof*: widen HOME and the tonic provably recurs more often.

**Identity 3 — coprime bases = independent balanced streams (texture).**
With pairwise-coprime bases, the multi-dimensional Halton theorem bounds the
*joint* discrepancy: two streams built on coprime bases are jointly
equidistributed. Verified: the 2D Halton (3,5) fills a 4×4 cell grid with
max deviation 2.0 vs expected 25/cell at $N = 400$. Voices on coprime bases
are provably independent-and-balanced — no correlation tuning, no
orthogonalization step.

## 3. The family

| member | construction | discrepancy | musical use |
|---|---|---|---|
| **van der Corput** $g_b$ | digit reversal in base $b$ | $C\log N/N$ | 1-D: onsets ($b=2$), pitch ($b=3$) |
| **Halton** $(g_{b_1}, \dots, g_{b_s})$ | $s$ coprime bases | $C'(\log N)^s/N$ | 2-D (time, pc), 3-D (+ velocity) |
| **Hammersley** $(g_{b_1}, \dots, g_{b_{s-1}}, n/N)$ | one exact endpoint | $C(\log N)^{s-1}/N$ | closed form: the $N$-th event lands exactly on the cadence |
| **Sobol'** | GF(2) direction numbers, Gray code | digital-net bounds | high-dimensional axes ($s \ge 4$) |
| **Scrambled** (Owen 1997) | digit permutation + digital shift | bound preserved | section variation with preserved balance |

Scrambling is *mandatory* for a multi-section piece: the raw sequence is
deterministic, so without a per-section key every section has an identical
skeleton. Verified: two XOR masks reorder $g_2$ while both keep
$D^* \le (\log_2 64 + 2)/64$ — variation for free, balance intact.

## 4. Verified invariants

Script: `projects/Research/outputs/ldsc_validate/verify_ldsc.py` (musicom env,
numpy 1.26.4, deterministic — no RNG except the explicit random baselines).

| property | statement | measured |
|---|---|---|
| $g_2$ values | first 8 exact fractions | 1/2, 1/4, 3/4, 1/8, 5/8, 3/8, 7/8, 1/16 (dev 0) |
| $g_3$ values | first 8 exact fractions | 1/3, 2/3, 1/9, 4/9, 7/9, 2/9, 5/9, 8/9 (dev < 1e-12) |
| star discrepancy | $D^*_N(g_2) \le (\log_2 N + 2)/N$ | $N{=}1024$: 0.00098 ≤ 0.01172 |
| vs random | $D^*$ far below i.i.d. mean | 0.00098 vs 0.02922 (20 trials) → **30×** |
| largest gap | each new $g_2$ point bisects largest empty gap | $n = 1..255$: 255/255 |
| rhythm evenness | min inter-onset gap, $N{=}16$ | 0.0312 vs random mean 0.0032 → **9.7×** |
| pc balance | Halton(2,3) pc histogram, $N{=}120$ | max|dev| 2.0 vs random 5.0 |
| region visits | frequency = width exactly | widths [.35,.20,.20,.25], dev 0.0010 (N=2000) |
| scrambling | order varies, balance kept | two masks differ; $D^*$ 0.0142/0.0147 ≤ 0.125 bound |
| determinism | pure function of $n$ | identical arrays (trivially, asserted) |
| joint balance | 2D Halton (3,5), 4×4 cells, $N{=}400$ | max|dev| 2.0 (expected 25/cell) |

**Musical reading.** The N=16 min-gap number is the groove statement: random
placement lets two onsets land 0.003 of a bar apart (machine-gun clump);
$g_2$ keeps every inter-onset gap ≥ 0.031 of the bar while *still* placing 16
onsets — even spread, no periodicity, no RNG.

## 5. Python implementation sketch (the verified core, condensed)

```python
import numpy as np

def radical_inverse(n, b):
    """Van der Corput radical inverse g_b(n), n >= 1."""
    out, inc = 0.0, 1.0 / b
    while n > 0:
        d = n % b
        out += d * inc          # least-significant digit -> most significant output
        n //= b
        inc /= b
    return out

def vdc(n, b=2):
    return radical_inverse(n, b)

def halton(n, bases=(2, 3)):
    return tuple(radical_inverse(n, b) for b in bases)

def scramble(xs, mask, bits=24):
    """Digital-shift (XOR) scramble: variation with preserved discrepancy."""
    out = []
    for x in xs:
        xi = int(round(x * (1 << bits)))
        out.append(((xi ^ mask) & ((1 << bits) - 1)) / (1 << bits))
    return np.array(out)

def region_of(x, widths):
    """Map x in [0,1) to a region index given cumulative region widths."""
    return int(np.searchsorted(np.cumsum(widths), x, side="right"))

def ldsc_cell(n_start, n_stop, widths, len_ticks, seed, b_t=2, b_p=3,
              scale_deg=None, k=12):
    """Fill one UnitMatrix cell: onsets + pcs + harmonic region from LDSC.
    Returns (events, region_counts) with events as (tick, pc, region)."""
    rng = np.random.default_rng(seed)
    mask = int(rng.integers(0, 2**24))            # per-section scramble key
    events = []
    counts = np.zeros(len(widths), dtype=int)
    for n in range(n_start, n_stop):
        t = int(scramble([vdc(n, b_t)], mask)[0] * len_ticks)
        p = int(vdc(n, b_p) * k)                  # pc index 0..k-1
        r = region_of(vdc(n, b_p), widths)        # harmonic function
        counts[r] += 1
        if scale_deg is not None:
            p = scale_deg[p % len(scale_deg)]     # map through the scale
        events.append((t, p, r))
    return events, counts
```

(Sobol' direction numbers, Hammersley endpoint and digit-permutation
scrambling are drop-in variants of the same loop; the verification script
`verify_ldsc.py` implements all checks in section 4 and exits non-zero on
any failure.)

## 6. Musical mapping

| axis | sequence | decode |
|---|---|---|
| onset ticks | $\varphi_2(n)$ | $t_n = \lfloor \varphi_2(n) \cdot \text{len}_\text{cell} \rfloor$ (grid) or raw ticks (continuous) |
| pitch class | $\varphi_3(n)$ | $p_n = \lfloor \varphi_3(n) \cdot k \rfloor$ → scale degree / tessitura |
| harmony | region of $\varphi_3(n)$ | $[0,1)$ partition → HOME/LIFT/TENSE/TURN; visit freq = width |
| velocity | $\varphi_5(n)$ | 3-D Halton (2,3,5) → balanced dynamics |
| form | scrambling keys + windows | section $s$ = indices $[N_s, N_{s+1})$ + key; repetition = key reuse |
| cadence | Hammersley endpoint $n/N$ | last event lands exactly on the seam |
| voices | coprime base pairs | voice $v$: time base shared ($b_t$), pitch base from {3,5,7,11,…} |

**Candidate code path:** `generators/lds_composition.py` — class
`LDSComposer` with `radical_inverse()`, `halton()`, `hammersley()`,
`sobol()`, `scramble()`, `region_partition()`, `realize_cell()`; consumed by
`workflows/unitmatrix_composer.py` (cells padded via `_unit_from_events` for
the zero-drift gate). The abstract pre-pass (per-section region partitions
exported as weighted tension curves) feeds `rules/subset_network.py`.

## 7. References

- van der Corput, J. G. (1935). "Verteilungsfunktionen (Erste Mitteilung)." *Proc. Koninklijke Akademie van Wetenschappen te Amsterdam* 38, 813–821.
- Halton, J. H. (1960). "On the efficiency of certain quasi-random sequences of points in evaluating multi-dimensional integrals." *Numerische Mathematik* 2, 84–90.
- Hammersley, J. M. (1960). "Monte Carlo methods for solving multivariable problems." *Ann. N. Y. Acad. Sci.* 86, 844–874.
- Sobol', I. M. (1967). "On the distribution of points in a cube and the approximate evaluation of integrals." *USSR Comput. Math. Math. Phys.* 7(4), 86–112. Bratley, P. & Fox, B. L. (1988). "Algorithm 659: Implementing Sobol's quasirandom sequence generator." *ACM TOMS* 14(1), 88–100.
- Niederreiter, H. (1992). *Random Number Generation and Quasi-Monte Carlo Methods.* SIAM CBMS-NSF 63.
- Kuipers, L. & Niederreiter, H. (1974/2005). *Uniform Distribution of Sequences.* Dover (pp. 129, 158).
- Owen, A. B. (1997). "Monte Carlo variance of scrambled net quadrature." *SIAM J. Numer. Anal.* 34(5), 1884–1910.
- Wikipedia: "Van der Corput sequence", "Low-discrepancy sequence", "Halton sequence" (fetched 2026-10-25) — radical-inverse definition + Python implementation, star-discrepancy bounds $C\log N/N$, $C'(\log N)^s/N$, $C(\log N)^{s-1}/N$, golden-ratio Kronecker case.
- Novelty check (2026-10-25): arXiv API / Crossref API / DuckDuckGo — no dedicated music-composition literature for van der Corput/Halton/low-discrepancy sequences found; the family is proposed here as a novel composition technique on documented QMC mathematics.
- In-catalogue: 012 Euclidean, 069 Christoffel (periodic evenness); 076 Thue-Morse (binary digital balance); 084 ZMRC (statistical rank-frequency); 121 IETC (ergodic exact frequencies); 040 Perlin / 048 RBMPD / 053 Lévy (RNG-driven placement).
