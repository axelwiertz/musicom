# Method 053: Lévy Flight Composition (LFC)

**Paradigm:** Stochastic · **ID:** 053 · **Added:** 2026-08-11
**Tonal Gravity:** Weak (Scale-guided) · **Metric Binding:** Continuous / Fluid · **Memory Depth:** Meso / Trajectory · **Time Complexity:** $\mathcal{O}(N)$

---

## Overview

Lévy Flight Composition (LFC) generates musical material by simulating **Lévy flights** — random walks whose step lengths are drawn from a **heavy-tailed power-law distribution** $P(\ell) \propto \ell^{-(1+\alpha)}$ with stability index $\alpha \in (0, 2]$. The defining contrast with classical random walks:

| Property | Gaussian / Brownian ($\alpha=2$) | Lévy flight ($\alpha<2$) |
|---|---|---|
| Step lengths | Thin-tailed, all moderate | Heavy-tailed, mostly small + rare huge |
| Variance | Finite | Infinite (for $\alpha < 2$) |
| Trajectory | Uniform diffusion | **Clustered** — patches of short steps separated by long jumps |
| Self-similarity | Weak | Strong fractal scaling at all zoom levels |

## Musical Rationale

Real melodies are already Lévy-like:
- **Voss (1994)**: pitch intervals in folk songs, classical themes, and jazz solos follow power laws with $\alpha \approx 1.0$–$1.5$.
- **Levitin, Chordia & Menon (2012)**: musical rhythm spectra follow Zipf's law (power-law scaling).
- **Dubnov (2006)**: musical style characterized as a Lévy flight process.

LFC does not impose an artificial statistical model — it captures the empirical structure of human-composed music and turns it into a controllable generator.

## Mathematics

### α-stable distributions
A random variable $X$ is $\alpha$-stable if for any $a, b > 0$ there exists $c, d$ such that $aX_1 + bX_2 \stackrel{d}{=} cX + d$. The characteristic function:
$$\phi(t) = \exp\left( i\mu t - |\sigma t|^\alpha (1 - i\beta \operatorname{sign}(t) \Phi) \right), \quad \Phi = \begin{cases} \tan(\pi\alpha/2) & \alpha \neq 1 \\ -\frac{2}{\pi}\log|t| & \alpha = 1 \end{cases}$$
Parameters: stability $\alpha \in (0,2]$, skewness $\beta \in [-1,1]$, scale $\sigma > 0$, location $\mu$.

### Chambers–Mallows–Stuck simulation (symmetric case)
$$X = S \cdot \left( \frac{\sin(\alpha \pi U)}{W} \right)^{1/\alpha} \cdot \left[ \frac{\sin((\alpha-1)\pi U / \alpha)}{\sin(\pi U / \alpha)} \right]^{(\alpha-1)/\alpha}$$
with $U \sim \text{Uniform}(-\pi/2, \pi/2)$, $W \sim \text{Exp}(1)$, $S \sim \text{Rademacher}$.

### Key scalings
- **Mean step**: undefined for $\alpha \le 1$; finite for $\alpha > 1$.
- **Variance**: infinite for $\alpha < 2$.
- **Hurst exponent**: $H = 1/\alpha$ — long-range dependence (persistence for $H > 0.5$).
- **Fractal dimension** (Higuchi): $D_f = 2 - H$ for 1D trajectories.

## Musical Elements Framework

### PITCH
Trajectory $p_{n+1} = p_n + \Delta p_n$, $\Delta p_n \sim S_\alpha(\sigma, \beta, 0)$ in MIDI pitch space.
- $\alpha = 2.0$ → Brownian (conjunct, stepwise)
- $\alpha = 1.5$ → typical melody (steps + 3rds–5ths leaps)
- $\alpha = 1.0$ → Cauchy (frequent large leaps, dramatic contour)
- $\alpha = 0.5$ → extreme (massive rare jumps, static stretches)
- $\beta$ biases ascent ($\beta>0$) or descent ($\beta<0$).

### RHYTHM
IOIs drawn from Lévy distribution → **bursty/clustered rhythms**: rapid runs cluster, separated by long sustained notes/rests. Independent $\alpha_{pitch}$ / $\alpha_{rhythm}$ decouple melodic and rhythmic clustering.

### HARMONY
Multi-voice independent flights yield vertical structures. Uncorrelated flights → dense unpredictable clusters; correlated flights (shared seeds, similar $\alpha$) → consonant stacks. Lévy index of vertical distribution measures spacing: low $\alpha$ = sparse wide chords, high $\alpha$ = dense clusters.

### STRUCTURE
Fractal self-similarity yields hierarchy at multiple scales: short clusters = motifs, medium = phrases/sections, long = movements. $H = 1/\alpha$ = directional persistence. Section boundaries: explicit parameter changes, or automatic at large jumps.

### TEXTURE
Local clustering governs density: cluster regions = dense/active; jump regions = sparse/static. Local fractal dimension $D_f$ (box-counting / Higuchi) = textural complexity scalar.

## UnitMatrix Integration

- **Rows (Voices)**: each voice = independent flight with parameters $(\alpha_v, \sigma_v, \beta_v)$ — contrasting $\alpha$ per voice yields layered textural density.
- **Columns (Sections)**: per-section parameter set $(\alpha_s, \sigma_s, \beta_s)$ or new seed/origin. Section A: $\alpha=1.5$; Section B: $\alpha=1.0$ (dramatic); return for ABA.
- **Cells**:
  - `{PITCH}`: flight value $p_{v,s}$, scale-quantized
  - `{RHYTHM}`: Lévy IOI → quantized duration
  - `{TEXTURE}`: local $D_f^{(v,s)}$ fractal dimension
- **Mapping Flow**: define per-section parameters → init pitches → CMS-generate steps → clip → cumsum → compute $D_f$ → quantize to scale → quantize IOIs → fill cells.

## Python Implementation

```python
import numpy as np

def levy_stable_sample(alpha, sigma=1.0, beta=0.0, size=1):
    """α-stable samples via CMS. α=2 → Gaussian, α=1 → Cauchy."""
    if alpha == 2.0:
        return sigma * np.random.randn(size)
    if alpha == 1.0 and beta == 0.0:
        return sigma * np.tan(np.pi * (np.random.rand(size) - 0.5))
    U = np.random.uniform(-np.pi/2, np.pi/2, size)
    W = np.random.exponential(1.0, size)
    if beta == 0.0:
        S = np.sign(np.random.randn(size))
        X = S * sigma * (np.sin(alpha * U) / W)**(1.0/alpha) * \
            (np.sin((alpha-1) * U / alpha) / np.sin(U / alpha))**((alpha-1)/alpha)
        return X
    from scipy.stats import levy_stable
    return levy_stable.rvs(alpha, beta, scale=sigma, size=size)

def levy_flight_compose(initial_pitch, alpha, sigma, n_steps, max_step=24):
    steps = np.clip(levy_stable_sample(alpha, sigma, 0.0, n_steps), -max_step, max_step)
    return np.cumsum(steps) + initial_pitch

def quantize_to_scale(pitches, key_root, scale_intervals):
    scale_pitches = sorted(
        key_root + o * 12 + iv for o in range(-2, 3) for iv in scale_intervals)
    scale_pitches = np.array(scale_pitches)
    return np.array([scale_pitches[np.argmin(np.abs(scale_pitches - p))] for p in pitches])

def compute_local_fractal_dimension(trajectory, window_size=50, k_max=10):
    """Higuchi fractal dimension per local window."""
    n = len(trajectory); n_windows = n // window_size; D_f = np.zeros(n_windows)
    for w in range(n_windows):
        seg = trajectory[w*window_size:(w+1)*window_size]
        L_k = np.zeros(k_max)
        for k in range(1, k_max+1):
            L_mk = 0.0
            for m in range(1, k+1):
                nseg = (len(seg) - m) // k
                if nseg > 0:
                    L_mk += np.sum(np.abs(seg[m::k][:nseg] - seg[m-1::k][:nseg])) / (k*nseg)
            L_k[k-1] = L_mk / k
        log_k = np.log(1.0 / np.arange(1, k_max+1))
        D_f[w] = np.polyfit(log_k, np.log(L_k + 1e-10), 1)[0]
    return D_f
```

## Pitfalls (10)

1. Infinite variance ($\alpha<2$) → clip steps to ±24 semitones.
2. Undefined mean ($\alpha \le 1$) → add mean-reversion (OU drift toward tonic).
3. CMS numerical instability near $\alpha \in \{0, 2\}$ → restrict to $[0.1, 1.99]$, special-case endpoints.
4. Scale quantization bias → inverse-CDF sampling / dithering.
5. Rhythmic quantization artifacts → probabilistic nearest-duration assignment or micro-timing.
6. Multi-voice dissonance → shared seeds / correlated $\alpha$ / harmonic post-filter (022 MCWS).
7. Uneven auto section boundaries → explicit boundaries + per-section params.
8. Noisy $D_f$ estimates on short windows → ≥50–100 samples per window.
9. Cost: CMS trig per sample → vectorize; pre-generate trajectories in bulk.
10. Style mismatch → match $\alpha$ to genre (Baroque ≈1.5, minimalist ≈2.0).

## References

- Lévy, P. (1937). *Théorie de l'addition des variables aléatoires*. Gauthier-Villars.
- Mandelbrot, B. B. (1982). *The Fractal Geometry of Nature*. W. H. Freeman.
- Shlesinger, West & Klafter (1987). "Lévy dynamics of enhanced diffusion." *PRL* 58(11).
- Chambers, Mallows & Stuck (1976). *JASA* 71(355), 231–236.
- Voss, R. F. (1994). "Fractal scaling of melodies." *AIP Conf. Proc.* 375, 54–73.
- Dubnov, S. (2006). "Musical style as a Lévy flight process." *ICMC*.
- Levitin, Chordia & Menon (2012). "Musical rhythm spectra follow Zipf's law." *Psych. Science* 23(4).
- Samorodnitsky & Taqqu (2019). *Stable Non-Gaussian Random Processes*. CRC Press.
- Higuchi, T. (1988). *Physica D* 31(2), 277–283.

## Relationship to other methods

- Extends **002 Markov** (local transitions) and **048 RBMPD** (Gaussian Brownian) from thin-tailed to heavy-tailed diffusion.
- Contrast: **040 Perlin** (smooth continuous noise, $H$ fixed ~0.7) vs LFC (tunable $\alpha$ incl. discontinuous jumps).
- **052 QWC** = quantum interference (non-classical); LFC = classical heavy-tailed (no interference).
- Pairs with **022 MCWS** (harmonic constraint post-filter) and **023 Tendency Masking** (Lévy trajectory as corridor bounds).
