# Method 121 — Interval Exchange Transformation Composition (IETC)

- **ID**: 121
- **Acronym**: IETC
- **Paradigm**: Rules-Based
- **Layer**: concrete
- **One-line**: Compose by iterating a piecewise-translation map of the unit interval — interval widths are the tonal-gravity weights (exact by unique ergodicity), the permutation is the melodic grammar, and Rauzy–Veech induction supplies self-similar macro-form.

---

## 1. Definition

Let $n \ge 2$, let $\lambda = (\lambda_1,\dots,\lambda_n)$ with $\lambda_i > 0$ and $\sum_i \lambda_i = 1$, and let $\pi$ be a permutation of $\{1,\dots,n\}$ describing the order in which the blocks are laid back down. With block starts

$$\alpha_i = \sum_{j<i}\lambda_j, \qquad \alpha'_i = \sum_{j:\,\pi(j)<\pi(i)}\lambda_j$$

the interval exchange transformation is

$$T_{\pi,\lambda}(x) = x - \alpha_i + \alpha'_i, \qquad x \in [\alpha_i, \alpha_{i+1}).$$

$T$ is a bijection of $[0,1)$ onto itself, preserves Lebesgue measure, and is a *translation* on each block (derivative exactly 1). The only nonlinearity is the $(n-1)$-fold discontinuity at the block seams.

**Verified**: for $\lambda=(0.5,0.3,0.2)$, $\pi=(3,2,1)$, the image of a $2\times10^5$-point grid re-sorts onto itself with maximum error $1.1\times10^{-16}$, and $T(x)-x$ takes exactly three values: $-0.8$, $-0.3$, $+0.5$.

### The irreducible (Keane) condition

$\pi$ is **irreducible** iff

$$\pi(1)=n,\qquad \pi(n)=1,\qquad \pi(\{1,\dots,k\}) \neq \{1,\dots,k\} \ \ \forall\, 1 \le k < n.$$

Irreducibility is what forbids the exchange from splitting into independent sub-exchanges. If $\pi$ is reducible there is an invariant union of blocks and the orbit never leaves it — musically, a permanent pedal/drone subset. Test in $O(n)$ before generating.

---

## 2. Why the dynamics is the composition

### 2.1 Minimality (Keane 1975)

For irreducible $\pi$ and *every* $\lambda$, every orbit is dense in $[0,1)$. Consequence: the melodic line can approach any point of the pitch circle arbitrarily closely — no dead regions, no absorbing subset, regardless of how the widths are chosen.

### 2.2 Unique ergodicity (Keane's conjecture; Masur 1982, Veech 1982)

For irreducible $\pi$ and almost every $\lambda$, Lebesgue measure is the *unique* $T$-invariant probability. Birkhoff's ergodic theorem then gives, for **every** starting point $x$ (not merely a.e.),

$$\lim_{N\to\infty}\frac{1}{N}\#\{0\le t<N : T^t x \in I_k\} = \lambda_k .$$

This is the design primitive of the method:

> **Interval width is tonal gravity, and it is exact.** Set $\lambda_{\text{tonic}} = 0.26$ and the tonic region receives 26 % of the events — in every run, from every seed, with no preference model, no fitness function and no corpus.

Verified over $4\times10^5$ iterates with $\lambda=(0.5,0.3,0.2)$: empirical frequencies $0.50000 / 0.30000 / 0.20000$, maximum absolute error $0.00000$.

Because the exchange is minimal, the convergence is not "eventually on average" only in the weak sense: for rational-independent widths the discrepancy of the visit counts is bounded by the number of discontinuities crossed (a bounded-remainder / three-distance-type statement), so even a 16-bar section has the designed balance.

### 2.3 Renormalization (Rauzy 1979; Rauzy–Veech induction)

Let $s = 1-\min(\lambda_1,\lambda_n)$ and induce $T$ on $[0,s)$ — replace $T$ by its first-return map. The result is *again an interval exchange*: same permutation class, at most $n+1$ blocks, with an updated width vector. Iterating this is the interval-exchange analogue of the continued-fraction (Gauss) map; its orbits organize the space of exchanges into **Rauzy classes**, and the substitution read off a full induction cycle generates the exchange's symbolic dynamics.

Verified: inducing $T_{((0.5,0.3,0.2),(3,2,1))}$ on $[0,0.62)$ gives a return map with exactly 3 translation displacements $\{-0.3,+0.2,+0.5\}$ and first-return times $\{1,2\}$ — still an IET, now with a two-valued return-time structure (i.e. a two-note duration vocabulary at the next scale).

Musical reading: **each induction level is a section that is literally a rescaled copy of the piece**, and the return-time multiset of the level is the section's rhythmic vocabulary. Form is generated, not pasted.

### 2.4 Deviation and tension (Zorich 1996; Forni 2002)

For a smooth observable $f$ (registral height, density, roughness), Birkhoff sums satisfy

$$S_N f(x) = N\!\int f\,d\lambda + O\!\left(N^{\theta}\right), \qquad \theta < 1,$$

and for typical exchanges the fluctuation exponents are the Lyapunov exponents of the **Zorich–Kontsevich cocycle** over the Rauzy–Veech flow. Design consequence: tension does not track a designed linear ramp; it fluctuates sublinearly around the designed mean, and the *Rauzy class* of $\pi$ sets the fluctuation rate. Widening a block moves the mean; changing the class changes the volatility.

### 2.5 Geometry: the Rauzy fractal

For $n = 3$ the substitution associated with the induction cycle (Tribonacci: $\sigma(1)=12,\ \sigma(2)=13,\ \sigma(3)=1$) has a self-affine attractor — the **Rauzy fractal** (Arnoux–Rauzy 1991) — which tiles the plane periodically in three homothetic parts. That is the geometric picture of "three sections, each a scaled copy": the exchange's renormalization is a tiling, and the tiling is the form.

---

## 3. Musical parameter mapping

| Musical dimension | Exchange object | Control |
|---|---|---|
| Pitch class | position $x \in [0,1)$ of the orbit | quantizer table $\{0,2,4,5,7,9,11,\dots\}$ |
| Harmonic function | block index $k$ (address of $x$) | $\lambda_k$ = frequency weight |
| Melodic succession | the permutation $\pi$ | which block follows which |
| Duration | block index under pulse coding, or roof $h|_k$ under suspension coding | $\lambda_k$, $c_k$ |
| Register | voice (row), not the orbit | instrument choice |
| Tempo/period | winding number / Rauzy class | rationality of $\lambda$ |
| Form | Rauzy–Veech induction level | section count |
| Density | $1/\overline{h}$ (mean roof) | roof scale |
| Tension | Zorich-cocycle fluctuation of a designed observable | $\pi$'s Rauzy class |

### Two rhythm codings

1. **Pulse coding** (grid-locked, MIDI-native): one iterate = one metric subdivision; the block the point occupies selects the duration class. $\lambda$ then serves simultaneously as the pitch histogram and the duration histogram.
2. **Suspension coding** (fluid): attach a roof $h$, piecewise constant with $h|_{I_k} = c_k$; place events at $t_{m+1} = t_m + h(T^m x)$. Inter-onset intervals are sums of $c_k$ over visited blocks — a strictly rational-ratio but aperiodic groove whose return statistics are the Rokhlin-tower heights of the induction.

---

## 4. Relationship to existing methods

| Method | Relation |
|---|---|
| 012 Euclidean Groove Locking | $n{=}2$ special case (mechanical/Christoffel word) |
| 069 Christoffel Word / Sturmian | $n{=}2$ special case; IETC is the permutation-bearing parent |
| 083 Aperiodic Quasicrystal Tiling | sibling aperiodic construction (substitution tiling vs. exchange + induction) |
| 115 Keplerian Orbital Resonance | sibling continuous-time flow method (physical vs. measure-theoretic) |
| 048 Reflected Brownian Pitch Diffusion | stochastic foil — IETC is deterministic and exactly equidistributed |
| 084 Zipf–Mandelbrot | frequency law imposed by statistics vs. guaranteed by ergodicity |
| 111 Vuza Tiling Canon | exact tiling of time; IETC tiles the pitch circle by an exchange |
| 099 SSM / 010 Hierarchical Diffusion | designed form vs. renormalization-generated form |

Uniqueness claim: no catalogued method composes from a *single continuous coordinate* iterated by a piecewise translation, and none derives tonal weight from an ergodic theorem rather than from rules, corpora or fitness.

---

## 5. Implementation sketch (validated)

```python
import numpy as np

def cum(lam):
    return np.concatenate(([0.0], np.cumsum(lam)))

def iet(x, lam, pi):
    """T_{pi,lam}(x). pi = 0-based permutation naming each block's image slot."""
    lam = np.asarray(lam, float); pi = np.asarray(pi)
    a = cum(lam)
    aimg = np.array([lam[pi < pi[i]].sum() for i in range(len(lam))])
    x = np.asarray(x, float)
    k = np.clip(np.searchsorted(a, x, side="right") - 1, 0, len(lam) - 1)
    return (x - a[k] + aimg[k]) % 1.0, k          # % 1.0 kills boundary fp drift

def is_irreducible(pi):
    n = len(pi)
    if pi[0] != n - 1 or pi[-1] != 0:
        return False
    return all(set(pi[:k]) != set(range(k)) for k in range(1, n))

def first_return(x0, lam, pi, s, maxit=100_000):
    """Return map on [0,s): the renormalized (induced) exchange."""
    x, t = float(x0), 0
    while t < maxit:
        x, _ = iet(x, lam, pi); t += 1
        if x < s:
            return float(x), t

# --- composition -----------------------------------------------------------
LAM = np.array([0.26, 0.17, 0.06, 0.13, 0.09, 0.21, 0.08])   # tonal weights
PI  = np.array([6, 1, 2, 3, 4, 5, 0])                        # irreducible
SLOT = [0, 2, 4, 5, 7, 9, 11, 12, 14, 16, 17, 19]            # 12-slot quantizer

def orbit_events(x0, base_pitch, n_steps, ticks_per_step, bar):
    ev, x, t = [], float(x0), 0
    for _ in range(n_steps):
        slot  = int(x * 12) % 12
        pitch = base_pitch + SLOT[slot]
        _, k  = iet(x, LAM, PI)
        dur   = (bar // 4) * (1 + k % 3)
        ev.append((t, pitch, dur))
        t += dur
        x  = iet(x, LAM, PI)[0]
        if t >= ticks_per_step:
            break
    return ev
```

Then feed `musicom`: build one `MusicUnit(events=[MusicEvent(...)])` per (voice, section) cell, pad the terminal event to `section_len`, and run `validate()` (zero-drift gate) before `to_midi()`. Full demo: `projects/Research/outputs/ietc_validate/iet_demo.py`.

### Complexity

| Operation | Cost |
|---|---|
| one iterate (1 event) | $\mathcal{O}(n)$ (searchsorted) or $\mathcal{O}(\log n)$ |
| full piece (N events, V voices) | $\mathcal{O}(NV)$ |
| irreducibility test | $\mathcal{O}(n)$ |
| one induction step | $\mathcal{O}(n)$ |
| Rauzy cycle of length $L$ | $\mathcal{O}(nL)$ |
| visit-frequency check | $\mathcal{O}(N)$ |

Memory is $\mathcal{O}(1)$ per voice: the state is a single real number. Coherence is bought by ergodicity, not by context.

---

## 6. Verification log (this build)

| Check | Result |
|---|---|
| piecewise-translation bijection | max error $1.1\times10^{-16}$; 3 distinct displacements |
| visit frequencies | $0.50000/0.30000/0.20000$ vs $\lambda$, error $0.00000$ (400 000 iterates) |
| $n{=}2$ → Sturmian | $P(I_0)=0.6125$ vs $\alpha=0.6180$; $\sup_m\lvert N_0(m)-\lfloor m\alpha\rfloor\rvert = 1$ |
| induced map is an IET | 3 displacements, return times $\{1,2\}$ on $[0,0.62)$ |
| UnitMatrix integration | 4 voices × 3 sections × 2 bars, `validate() -> True`, 579-byte MIDI, 15.0 s |
| pitch content | 9–10 distinct pitches/voice; ranges 72–89, 60–79, 48–67, 36–53 |
| render | FluidR3 WAV 3.85 MB |
| preflight | COMPLIANT |

---

## 7. Pitfalls

1. Reducible $\pi$ → orbit trapped in a block union (permanent drone).
2. Rational $\lambda$ → periodic orbit (period = lcm of denominators); use deliberately or not at all.
3. Floating-point boundary hits (observed: an iterate at exactly $\alpha_1$ evaluating to $1.0$) distort the visit law — reduce mod 1, use half-open blocks, one `searchsorted` side.
4. $n{=}2$ is not novel (rotation ⇒ Sturmian); the method's content is $n\ge3$ + induction.
5. Equidistribution governs frequency, not consonance — the map is discontinuous, so semitone rubs are possible; control them with the quantizer table.
6. Coincident seeds never separate ($T$ bijective).
7. Induced sections are exact scale-copies — switch Rauzy class if contrast is wanted.
8. Continuous time vs. tick grid: quantize and pad to `section_len` or `validate()` fails.

---

## 8. References

- Keane, M. (1975). Interval exchange transformations. *Mathematische Zeitschrift* 141, 25–31.
- Rauzy, G. (1979). Échanges d'intervalles et transformations induites. *Acta Arithmetica* 34, 315–328.
- Masur, H. (1982). Interval exchange transformations and measured foliations. *Annals of Mathematics* 115, 169–200.
- Veech, W. A. (1982). Gauss measures for transformations on the space of interval exchange maps. *Annals of Mathematics* 115, 201–242.
- Veech, W. A. (1984). The metric theory of interval exchange transformations I. *American Journal of Mathematics* 106, 1331–1421.
- Boshernitzan, M. D. (1985). A condition for minimal interval exchange maps to be uniquely ergodic. *Duke Mathematical Journal* 52, 723–752.
- Arnoux, P. & Rauzy, G. (1991). Représentation géométrique de suites de complexité $2n+1$. *Bulletin de la SMF* 119, 199–215.
- Zorich, A. (1996). Finite Gauss measure on the space of interval exchange transformations. Lyapunov exponents. *Annales de l'Institut Fourier* 46, 325–370.
- Kontsevich, M. & Zorich, A. (1997). Lyapunov exponents and Hodge structure. *Advanced Series in Mathematical Physics* 24, 318–332.
- Forni, G. (2002). Deviation of ergodic averages for area-preserving flows on surfaces of higher genus. *Annals of Mathematics* 155, 1–103.
- Viana, M. (2006). Ergodic theory of interval exchange maps. *Revista Matemática Complutense* 19(1), 7–100.
- Clough, J. & Douthett, J. (1991). Maximally even sets. *Journal of Music Theory* 35, 93–173 (degenerate $n{=}2$ evenness).
- Toussaint, G. (2013). *The Geometry of Musical Rhythm*. CRC Press (Sturmian/Christoffel rhythms).
