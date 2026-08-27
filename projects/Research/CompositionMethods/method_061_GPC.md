# Gaussian Process Composition (GPC) — Method 061

**Paradigm:** Stochastic (Bayesian nonparametric)
**Acronym:** GPC
**Classification:** Tonal Gravity = Strict (Anchor-conditioned) · Metric Binding = Continuous/Fluid · Memory Depth = Macro/Kernel Horizon · Time Complexity = $\mathcal{O}(N^3)$ exact / $\mathcal{O}(N M^2)$ sparse

---

## 1. Overview

Gaussian Process Composition places a Bayesian prior over musical parameters as smooth functions of time, conditions that prior on harmonic/structural anchor points, and samples the posterior to fill the UnitMatrix. It is the kernel-supervised member of the stochastic family — the principled, closed-form sibling of 002 Markov (discrete state) and the Bayesian counterpart to 040 Perlin (unsupervised noise), 048 RBMPD (reflected diffusion), and 053 Lévy Flight (heavy-tailed diffusion).

## 2. Mathematical Foundation

A Gaussian Process is a distribution over functions:

$$f(t) \sim \mathcal{GP}\big(m(t),\, k(t,t')\big)$$

Fully specified by a mean $m(t)$ and covariance kernel $k(t,t')$. Given $N$ anchor observations $(T, y)$ at times $T$ with noise $\sigma_n^2$, the posterior at new times $t_*$ is again Gaussian:

$$m_*(t_*) = m(t_*) + K_{*T}\,(K_{TT} + \sigma_n^2 I)^{-1}(y - m(T))$$

$$\Sigma_*(t_*) = K_{**} - K_{*T}\,(K_{TT} + \sigma_n^2 I)^{-1} K_{T*}$$

where $K_{TT}=k(T,T)$, $K_{*T}=k(t_*,T)$, $K_{**}=k(t_*,t_*)$.

### Kernels (the melodic-character language)

| Kernel | Form | Musical effect |
|---|---|---|
| RBF (squared-exponential) | $\sigma^2\exp(-r^2/2\ell^2)$ | Smooth, conjunct, legato melodies |
| Matérn-3/2 | $\sigma^2(1+\sqrt{3}r/\ell)\exp(-\sqrt{3}r/\ell)$ | Angular, motivic leaps, rougher contour |
| Matérn-5/2 | $\sigma^2(1+\sqrt{5}r/\ell+5r^2/3\ell^2)\exp(-\sqrt{5}r/\ell)$ | Intermediate smoothness |
| Periodic | $\sigma^2\exp(-2\sin^2(\pi r/p)/\ell^2)$ | Ostinato / rondo repetition, period $p$ |
| Linear | $\sigma^2\, t\, t'$ | Directional drift (ascending/descending) |
| Changepoint | $k_1$ for $t<t_c$, else $k_2$ | Hard sectional contrast |

The lengthscale $\ell$ is the "memory horizon" — the time separation beyond which pitches decorrelate — and maps directly to phrase length.

### Multi-output (coregionalized) GPs for voices

$$K_{multi} = B \otimes K_{time}, \qquad B = AA^T \in \mathbb{R}^{V \times V}$$

$V$ voices share $Q$ latent GPs $g_q(t)$ through mixing coefficients $a_{vq}$: $f_v(t) = \sum_q a_{vq} g_q(t)$. Off-diagonals of $B$ set voice coupling (diagonal = independent, dense = homophonic, low-rank = shared motifs).

## 3. Musical Elements Framework

- **PITCH** — posterior mean (deterministic) or sample (stochastic), scale-quantized. Kernel sets melodic character; anchors pin to chord tones.
- **RHYTHM** — second GP over log-IOI, or derivative process $|f'(t)|$: rapid contour change → dense onsets, flat → sparse. Periodic kernel (period = 1 bar) injects meter.
- **HARMONY** — chord function (HOME/LIFT/TENSE/TURN) encoded as anchors; posterior forced through chord tones. $\sigma_n^2$ sets binding strength (small = strict counterpoint, large = loose jazz).
- **STRUCTURE** — per-section kernel + mean function. Periodic = rondo, long-$\ell$ RBF = through-composed, changepoint = sectional contrast. Mean encodes arc (rising = LIFT, falling = TURN).
- **TEXTURE** — posterior variance $\Sigma_*$ drives ornamentation/density; high variance = free to ornament, low = pinned. Coregionalization matrix $B$ sets voice coupling.

## 4. UnitMatrix Integration

- **Rows (Voices)** — each voice = one output of a coregionalized GP. Lead = high-register + small $\ell$; Bass = low-register + long $\ell$; Pad = chord-tone anchors (low variance); Percussion = log-IOI GP with periodic kernel.
- **Columns (Sections)** — each section = its own kernel $k_s$ + mean $m_s$; conditioned on chord anchors and prior-section cadence for smooth joins.
- **Cells** — `{PITCH}` = posterior pitch at onsets; `{RHYTHM}` = derivative/IOI onsets; `{TEXTURE}` = variance-driven density.

## 5. Python Implementation Sketch

```python
import numpy as np

def rbf_kernel(X1, X2, lengthscale=1.0, variance=1.0):
    sq = (X1[:, None] - X2[None, :]) ** 2
    return variance * np.exp(-0.5 * sq / lengthscale ** 2)

def periodic_kernel(X1, X2, period=1.0, lengthscale=1.0, variance=1.0):
    d = np.sin(np.pi * (X1[:, None] - X2[None, :]) / period)
    return variance * np.exp(-2.0 * d ** 2 / lengthscale ** 2)

class GPComposer:
    def __init__(self, kernel=rbf_kernel, noise=1e-3, mean=0.0):
        self.kernel, self.noise, self.mean = kernel, noise, mean

    def condition(self, X_anchor, y_anchor):
        self.X, self.y = X_anchor, y_anchor
        K = self.kernel(X_anchor, X_anchor) + self.noise * np.eye(len(X_anchor))
        self.L = np.linalg.cholesky(K)                    # O(N^3)
        self.alpha = np.linalg.solve(self.L.T,
                    np.linalg.solve(self.L, y_anchor - self.mean))

    def predict(self, X_new):
        Ks = self.kernel(X_new, self.X)
        mean = self.mean + Ks @ self.alpha
        v = np.linalg.solve(self.L, Ks.T)
        var = self.kernel(X_new, X_new) - (v ** 2).sum(0)
        return mean, var

    def sample(self, X_new, n=1, seed=0):
        mean, var = self.predict(X_new)
        rng = np.random.default_rng(seed)
        L = np.linalg.cholesky(np.diag(var) + 1e-9 * np.eye(len(var)))
        return mean[:, None] + L @ rng.standard_normal((len(var), n))
```

## 6. Pitfalls

1. **Cubic blow-up** — $\mathcal{O}(N^3)$ exact; use inducing points ($M \ll N$) or per-section tiling.
2. **Ill-conditioning** — near-duplicate anchors or tiny $\ell$; add jitter $\sigma_n^2 \ge 10^{-6}$.
3. **Over-smoothing** — large-$\ell$ RBF blurs melody; use Matérn or add periodic component.
4. **Anchor over-constraint** — $\sigma_n^2 \to 0$ forces stiff counterpoint; soften anchors or anchor only at stress points.
5. **Voice collapse** — rank-1 $B$ collapses voices to scaled copies (cf. FHNS 037); keep $B$ full-rank.
6. **Periodic metric mismatch** — period $p$ not aligned to bar grid drifts; set $p$ to integer ticks, snap onsets, run `validate()`.
7. **Variance miscalibration** — raw variance as density yields empty/chaotic cells; normalize to target range.

## 7. References

- Rasmussen, C. E., & Williams, C. K. I. (2006). *Gaussian Processes for Machine Learning*. MIT Press.
- Matheron, G. (1963). "Principles of geostatistics." *Economic Geology* 58(8).
- Williams, C. K. I., & Rasmussen, C. E. (1996). "Gaussian processes for regression." *NeurIPS 1996*.
- Grindlay, G., & Helmbold, D. (2006). "Modeling, analyzing, and synthesizing expressive piano performance with graphical models." *Machine Learning* 65.
- Álvarez, M. A., Rosasco, L., & Lawrence, N. D. (2012). "Kernels for vector-valued functions: a review." *Foundations and Trends in ML* 4(3).
- Duvenaud, D. (2014). "Automatic model construction with Gaussian processes." *PhD thesis, Cambridge*.
