# Zipf–Mandelbrot Rank–Frequency Composition (ZMRC)

**Method ID**: 084
**Paradigm**: Stochastic
**Layer**: concrete (emits note/chord events into UnitMatrix cells; feeds `generators/`)
**Candidate code path**: `generators/zipf_rank_frequency.py`
**Acronym**: ZMRC

## One-line description

Treats the piece as a text over a ranked musical vocabulary and samples tokens from a Zipf–Mandelbrot rank–frequency law $f(r) \propto (r+q)^{-s}$: rank 1 (tonic/HOME) saturates, the long tail (chromatic/TENSE) is rare, the exponent $s$ sets vocabulary richness, the shift $q$ sets dominance, and the ranking order is the tonal grammar — reproducing the same rank–frequency signature that separates real music from random (Manaris 2003; Zanette 2006; Levitin 2012).

## Extended math

### The Zipf–Mandelbrot law

Let the musical alphabet be $V$ tokens with ranks $r = 1, 2, \dots, V$ in descending frequency order. The probability mass of rank $r$ is

$$
f(r) = \frac{(r+q)^{-s}}{\sum_{k=1}^{V} (k+q)^{-s}} \;=\; \frac{(r+q)^{-s}}{\zeta_V(s,q)},
$$

where $\zeta_V(s,q) = \sum_{k=1}^V (k+q)^{-s}$ is the **truncated Hurwitz zeta**. $s > 0$ is the **Zipf exponent** (slope on a log-log rank–frequency plot), and $q \ge 0$ is the **Mandelbrot shift**. The normalization guarantees $\sum_r f(r) = 1$.

Mandelbrot's information-theoretic derivation: given a cost function $c(r)$ per symbol, the distribution maximizing entropy per unit cost is $f(r) \propto e^{-\lambda c(r)}$; with $c(r) = s \ln(r+q)$ this is exactly the Zipf–Mandelbrot law. So the exponent $s$ is a **Lagrange multiplier** — the price of a "rare" (high-rank) token. Raising $s$ makes rare tokens *more expensive*, flattening the tail toward the head; this is the quantitative handle on tonal pull.

### Slope estimation (fit-from-corpus)

Given observed counts $n_1 \ge n_2 \ge \dots \ge n_V$ (tokens sorted by frequency), the **maximum-likelihood** estimator for $s$ under a truncated Zipf is

$$
s^* = \arg\min_s \left[ \frac{1}{N}\sum_{r=1}^V n_r \ln(r+q) + \ln \zeta_V(s,q) \right],
\qquad N = \sum_r n_r .
$$

For large $V$ with $q=0$, the MLE approximates the **Hill estimator** $s^* \approx \left[\frac{1}{N}\sum_r n_r \ln\frac{r}{r_{\min}}\right]^{-1}$. Least-squares on $\log n_r$ vs $\log r$ is the fast but biased fallback (fine for diagnostics, avoid for composition).

### Sampling

The CDF is a step function $F(r) = \sum_{k \le r} f(k)$, precomputed as a length-$V$ table. **Inverse-CDF sampling** draws $u \sim U(0,1)$ and binary-searches $F^{-1}(u)$ in $\mathcal{O}(\log V)$; the **Walker alias method** builds an $\mathcal{O}(V)$ table once and then samples in $\mathcal{O}(1)$. Determinism = seed the RNG.

### The $(s,q,\text{ranking})$ macro-form

A piece is a sequence of sections; each section $j$ is a triple $(s_j, q_j, \pi_j)$ where $\pi_j$ is a permutation (the ranking order). Form = a **trajectory through the $(s,q)$ plane** with a possibly-rotating ranking:

- intro: steep $s$, small $q$, tiny vocab → near-ostinato on the tonic;
- verse: corpus-target $s^*$ → "natural" diatonic balance;
- chorus: even steeper $s$ → maximal tonic pull (HOME saturated);
- bridge: flat $s \to 0$, large $q$ → near-uniform, novelty burst (TENSE);
- outro: re-steepen toward the intro.

### Fitness (Manaris)

Manaris et al.'s aesthetic measure is the **goodness-of-fit of the generated rank–frequency curve to a target corpus**:

$$
d = \frac{1}{V}\sum_{r=1}^V \left| \hat f(r) - f_{\text{target}}(r) \right| \quad\text{(or rank correlation of the two curves)}.
$$

Minimizing $d$ (steering $s$ and the ranking) is exactly the optimizer that produced "pleasant" melodies in the original EvoWorkshops paper — the empirical warrant for using Zipf slope as a composition dial rather than a post-hoc description.

### Complexity

- Build vocabulary: $\mathcal{O}(V \log V)$ (sort by frequency) or $\mathcal{O}(V)$ (rule-imposed ranking).
- Fit slope (MLE): $\mathcal{O}(V)$ per Newton iteration, $\approx 10$ iterations.
- Sample $N$ events: $\mathcal{O}(V)$ once for the alias table + $\mathcal{O}(N)$ draws.
- Total: $\mathcal{O}(N)$ dominated by decoding; deterministic per seed, no training, no optimization loop.

## Python implementation sketch

```python
"""Zipf-Mandelbrot Rank-Frequency Composition (Method 084, ZMRC)."""
import math
import random

def zipf_mandelbrot_pmf(V, s, q=0.0):
    """Return normalized rank-frequency mass for ranks 1..V."""
    w = [(r + q) ** (-s) for r in range(1, V + 1)]
    Z = sum(w)
    return [x / Z for x in w]

def fit_slope_mle(hist, q=0.0, n_iter=50, lr=0.1):
    """ML estimate of s for a truncated Zipf-Mandelbrot from counts hist[rank-1]."""
    V = len(hist)
    N = sum(hist)
    s = 1.0  # start in the empirical pleasant band
    for _ in range(n_iter):
        weights = [(r + q) ** (-s) for r in range(1, V + 1)]
        Z = sum(weights)
        # d/ds log-likelihood
        grad = -sum(hist[r-1] * math.log(r + q) for r in range(1, V+1)) / N \
               + sum(weights[r-1] * math.log(r + q) for r in range(1, V+1)) / Z
        s -= lr * grad
        s = max(0.05, s)
    return s

class AliasTable:
    """O(1) discrete sampler (Walker-Vose)."""
    def __init__(self, weights):
        n = len(weights)
        total = sum(weights)
        self.prob = [w * n / total for w in weights]
        self.alias = [0] * n
        small, large = [], []
        for i, p in enumerate(self.prob):
            (small if p < 1.0 else large).append(i)
        while small and large:
            s_, l_ = small.pop(), large.pop()
            self.alias[s_] = l_
            self.prob[l_] = self.prob[l_] + self.prob[s_] - 1.0
            (small if self.prob[l_] < 1.0 else large).append(l_)
        while large:
            self.prob[large.pop()] = 1.0
        while small:
            self.prob[small.pop()] = 1.0

    def sample(self, rng):
        i = rng.randrange(len(self.prob))
        return i if rng.random() < self.prob[i] else self.alias[i]

def build_vocabulary(ranking):
    """ranking: list of tokens from rank-1 (tonic) to rank-V (rare)."""
    return {tok: r for r, tok in enumerate(ranking, start=1)}

def sample_events(ranking, s, q, n, seed=0):
    """Draw n rank-1..V indices from a Zipf-Mandelbrot law."""
    rng = random.Random(seed)
    pmf = zipf_mandelbrot_pmf(len(ranking), s, q)
    table = AliasTable(pmf)
    return [ranking[table.sample(rng)] for _ in range(n)]

# --- decode to pitch (diatonic example) ---
SCALE = [0, 2, 4, 5, 7, 9, 11]          # major scale degrees -> semitones
# Ranking: tonic first, then chord tones, then passing, then chromatic
RANKING = [0, 4, 7, 2, 9, 5, 11, 1, 3, 6, 8, 10]   # C E G D A F B Db Eb Gb Ab Bb

def compose_section(base=60, s=1.0, q=1.0, n=64, seed=0):
    """Emit n scale-degree tokens with Zipf-Mandelbrot pitch statistics."""
    tokens = sample_events(RANKING, s, q, n, seed)
    return [base + SCALE[t % len(SCALE)] + 12 * (t // len(SCALE)) for t in tokens]
```

**Musicom integration** (engine authors the MIDI; real imports per AGENTS.md):

```python
# from structures import MusicUnit
# from workflows.unitmatrix_composer import UnitMatrixComposer, create_note_unit, create_chord_unit
# composer = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
# composer.create_matrix(num_voices=V, num_sections=S)
# for v in range(V): composer.add_voice(f"voice{v}", ...)
# for s, (slope, shift, seed) in enumerate(section_specs):
#     pitches = compose_section(base=60, s=slope, q=shift, n=32, seed=seed)
#     for p in pitches:
#         composer.fill_voice_section("voice0", s, create_note_unit(p, 480))
# ok, msg = composer.validate()   # MUST be True before to_midi (per AGENTS.md)
```

## References

- Zipf, G. K. (1935). *The Psycho-Biology of Language: An Introduction to Dynamic Philology*. Houghton Mifflin.
- Mandelbrot, B. B. (1953). "An informational theory of the statistical structure of language." In *Communication Theory* (W. Jackson, ed.), 486–502. Butterworths.
- Manaris, B., Vaughan, D., Wagner, C., Romero, J., & Davis, R. B. (2003). "Evolutionary music and the Zipf–Mandelbrot law: developing fitness functions for pleasant music." *Applications of Evolutionary Computing (EvoWorkshops 2003)*, LNCS 2611, 522–534. Springer.
- Manaris, B., Romero, J., Machado, P., Krehbiel, D., Hirzel, T., Pharr, W., & Davis, R. B. (2005). "Zipf's law, music classification, and aesthetics." *Computer Music Journal* 29(1), 55–69. MIT Press.
- Zanette, D. H. (2006). "Zipf's law and the creation of musical context." *Musicae Scientiae* 10(1), 3–18.
- Levitin, D. J., Chordia, P., & Menon, V. (2012). "Musical rhythm spectra follow Zipf's law." *Psychological Science* 23(4), 365–371.
- Voss, R. F., & Clarke, J. (1975). "1/f noise in music and speech." *Nature* 258, 317–318.
- Newman, M. E. J. (2005). "Power laws, Pareto distributions and Zipf's law." *Contemporary Physics* 46(5), 323–351.
