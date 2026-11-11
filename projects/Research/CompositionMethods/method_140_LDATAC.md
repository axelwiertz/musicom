# Method 140 — Latent Dirichlet Allocation Texture-Archetype Composition (LDATAC)

**Layer:** concrete · **Paradigm:** AI-Driven · **Status:** verified prototype (`_web140/verify_140_LDATAC.py`, 11/11 checks)
**Summary row added to `methods_db.md`:** yes (line 150) · **Method section appended:** line 31018

---

## 1. One-line idea

A piece is a **topic model**: sections are documents, gesture tokens are words, and
texture archetypes are topics. Compose by sampling the **posterior predictive**
$p(w\mid d)=\sum_k\hat\theta_{dk}\hat\phi_{kw}$ — one draw per note — and let the
simplex position $\theta_d$ be the form/texture control surface.

## 2. Why this is not already in the database

`grep -ic` on `methods_db.md` on 2026-11-11: `latent dirichlet` = 0, `topic model` = 0,
`LDA` (word-boundary) = 0, `bag of words` = 0, `perplexity` = 0, `plate notation` = 0.
All music-LDA literature found (raga ID 2011, mood classification 2016, tonal profiles
2021) is **analysis/classification**; LDA's posterior predictive is used here as a
*generator* — no DB method does that.

Nearest neighbours and why they are different:

| Method | Model | Why LDATAC differs |
|---|---|---|
| 086 HMM-C | latent discrete **chain**, memory-1, $P(z_t\mid z_{t-1})$ | LDA has no transition matrix; it is **exchangeable** |
| 085 NMF-C | non-generative matrix factorization | no Dirichlet prior, no per-token latent assignment, no posterior predictive draw |
| 034 PCFG | grammar recursion over symbols | no syntax; statistics come from a corpus |
| 066 GTTM-HC | hand-written rules | parameters are *learned* |
| 046 VAE-LSI / 118 D3PM | deep continuous / denoising latents | conjugate closed form, no gradients, no training loop |
| 084 ZMRC | rank–frequency law | no latent structure, no mixture |

## 3. Model and math

### 3.1 Generative story

For section $d=1..S$ (a UnitMatrix **column**), with vocabulary size $V$, $K$ topics:

$$
\theta_d \sim \mathrm{Dir}(\alpha),\quad
z_{dn}\mid\theta_d \sim \mathrm{Cat}(\theta_d),\quad
w_{dn}\mid z_{dn}{=}k \sim \mathrm{Cat}(\phi_k),\quad
\phi_k \sim \mathrm{Dir}(\eta)
$$

Joint density (conjugate, all factors in the exponential family):

$$
p(w,z,\theta,\phi\mid\alpha,\eta)=
\prod_{k=1}^{K}\mathrm{Dir}(\phi_k\mid\eta)\;
\prod_{d=1}^{S}\mathrm{Dir}(\theta_d\mid\alpha)
\prod_{n=1}^{N_d}\theta_{d,z_{dn}}\,\phi_{z_{dn},w_{dn}}
$$

### 3.2 Collapsing to a closed form

Integrating $\theta$ and $\phi$ out (Dirichlet–multinomial conjugacy) gives the marginal

$$
p(w,z\mid\alpha,\eta)=
\prod_{d}\frac{\Gamma(K\alpha)}{\Gamma(n_d+K\alpha)}
\prod_{k}\frac{\Gamma(n^{(d)}_k+\alpha_k)}{\Gamma(\alpha_k)}
\;\cdot\;
\prod_{k}\frac{\Gamma(V\eta)}{\Gamma(n^{(k)}+V\eta)}
\prod_{w}\frac{\Gamma(n^{(k)}_w+\eta_w)}{\Gamma(\eta_w)}
$$

so the only latents left are the token–topic indicators:

$$
p(z_{dn}=k\mid z_{-dn},w)\;\propto\;
\big(n^{(d)}_k+\alpha_k\big)\,
\frac{n^{(k)}_w+\eta_w}{n^{(k)}+\sum_{w'}\eta_{w'}}
$$

This is the Griffiths–Steyvers (2004) update. One sweep is $\mathcal{O}(NK)$; the
verified demo uses $I=300$, $K=3$, $S=48$, $N_d=28$ (≈ 0.4 s in pure NumPy).

### 3.3 The composition operator

$$
\hat\theta_{dk}=\frac{n^{(d)}_k+\alpha_k}{n^{(d)}+K\alpha},\qquad
\hat\phi_{kw}=\frac{n^{(k)}_w+\eta_w}{n^{(k)}+V\eta},\qquad
p(w\mid d)=\sum_{k=1}^{K}\hat\theta_{dk}\,\hat\phi_{kw}
$$

$p(w\mid d)$ is a **Dirichlet-compound-multinomial** — the posterior predictive of a new
token given the section. Generating a cell $=$ drawing $N$ tokens from it, until the
clock is full. Nothing else is needed: the model *is* the composer.

Voice coloration multiplies the mixture by a row prior:

$$
p(z{=}k\mid d,v)\;\propto\;\theta_{dk}\,\beta_{vk},\qquad \beta_v\sim\mathrm{Dir}(\delta_v)
$$

### 3.4 Tension curve

$$
\bar\theta=\frac1S\sum_{d=1}^{S}\theta_d,\qquad
D_d=\mathrm{KL}(\theta_d\,\Vert\,\bar\theta)=\sum_k\theta_{dk}\log\frac{\theta_{dk}}{\bar\theta_k}
$$

* $D_d\approx0$ → HOME (the section *is* the corpus mean)
* $\arg\max_d D_d$ → TENSE (most archetype-dominated section)
* a *new* archetype appearing mid-piece → LIFT
* an archetype blend the corpus never uses that way → TURN

Verified on the designed 8-section plan: $D_d \in \{0.441, 0.111, 0.029, 0.314, 0.765, 0.116, 0.094, 0.441\}$, a **26× spread**.

### 3.5 Zero-drift law

Token durations are drawn from the token's duration coordinate and clamped to the cell:

$$
t_0=0,\qquad t_{n+1}=t_n+\min(d_n,\,L-t_n),\qquad \text{stop at } t_n=L
$$

$\Rightarrow t_N=L$ exactly, no padding pass. Verified: 32/32 cells ended at 7680 ticks
(4 bars, tpb = 480).

### 3.6 What the model cannot do (a theorem, not a caveat)

LDA is exchangeable: for any permutation $\pi$,

$$
p(w_1,\dots,w_N\mid d)=p(w_{\pi(1)},\dots,w_{\pi(N)}\mid d)
$$

Measured: $|\Delta\log p| = 0.0$ exactly for a shuffled document. Consequence: a cell and
its retrograde are the *same object* to LDATAC. Ordering must come from a rhythm layer
(012 Euclidean, 016 groove anchors) or from bigram tokens. This is the honest price of
mixture structure.

### 3.7 Model selection and the nonparametric extension

Fixing $K$ is the main commitment. Over-specifying $K$ does not invent archetypes — it
**splits** them (measured at $K{=}5$: best cosine per planted archetype 0.995 / 0.998 / 0.991,
the two surplus topics absorbing split mass). The HDP (Teh et al. 2006) replaces
$\mathrm{Dir}(\alpha)$ with a Chinese-restaurant franchise and infers $K$ from the corpus:

$$
G_0\sim\mathrm{DP}(\gamma,H),\qquad G_j\sim\mathrm{DP}(\alpha,G_0),\qquad
\theta_{dj}\sim G_j
$$

with the CRP/CRF predictive $\frac{n^{(-j)}_{k}}{\cdot+\gamma}$ and $\frac{n^{(j)}_{k}}{\cdot+\alpha}$ — the
composition analogue of "how many textures does this style actually contain?".

### 3.8 Variational alternative (if a corpus is huge)

Mean-field $q(\theta_d,\phi_k,z_{dn})=q(\theta_d)q(\phi_k)\prod_n q(z_{dn})$ with
$\lambda_{dn}\propto\exp\{\mathbb{E}[\log\theta_d]+\mathbb{E}[\log\phi_{z}]\}$ and the
standard digamma updates gives $\mathcal{O}(NK)$ per iteration with a monotone ELBO —
useful when $N>10^6$, unnecessary at piece scale.

## 4. Musical mapping (Musical Elements Framework)

* **PITCH** — token = (step $\in\{-2..+2\}$, duration, velocity class). Realized by
  cumulative sum along the voice's register ladder ($p_{n+1}=p_n+s_n$, clipped), then a
  key/scale map. $\phi_k$ is transposition-invariant → key is a realization parameter.
  Functional-harmony variant: swap the step coordinate for a pc-set/chord-degree coordinate.
* **RHYTHM** — duration is a token coordinate; local density $=L/\sum_k\theta_{dk}\mathbb{E}[d\mid k]$,
  so texture controls rhythm automatically (sustain-heavy section ⇒ sparse, 480-tick
  tokens; flourish-heavy ⇒ dense, 120-tick).
* **HARMONY** — $\theta_d$ is the harmonic object (interval/ pc content per column);
  KL drift is the harmonic tension curve; columns comparable on one simplex.
* **STRUCTURE** — $\alpha<1$ ⇒ block form with hard seams; $\alpha\approx1$ ⇒ through-composed
  morphing; HDP ⇒ form that grows new archetypes.
* **TEXTURE** — the core axis: a section's texture is a *point on the simplex*, so texture
  crossfades are continuous; $\beta_v$ distributes the blend across voices
  ("one texture, four functions").

## 5. UnitMatrix integration

| UnitMatrix | LDA object | Role |
|---|---|---|
| Row = voice | $\beta_v$ (row prior) + register ladder | which archetypes the instrument may speak |
| Column = section | document $d$, $\theta_d$ | texture/tension plan, one point per column |
| Cell = `MusicUnit` | token run, clamped to $L$ | concrete `MusicEvent` list for `fill_voice_section` |

Verified build: 4 voices × 8 sections × 4 bars (tpb 480) → **1049 events**,
`validate() == True`, `ldatac_140.mid` = 8983 B.

## 6. Python implementation sketch

```python
"""generators/lda_topics.py — LDATAC: topic-model texture-archetype composition."""
import itertools
import numpy as np


class GestureVocabulary:
    def __init__(self, steps=(-2, -1, 0, 1, 2), durs=(120, 240, 480), dyns=(64, 100)):
        self.tokens = list(itertools.product(steps, durs, dyns))
        self.index = {t: i for i, t in enumerate(self.tokens)}
        self.V = len(self.tokens)

    def encode(self, seq):
        return [self.index[t] for t in seq]


class ArchetypeModel:
    """Collapsed-Gibbs LDA over gesture tokens; sections are documents."""

    def __init__(self, K=3, alpha=0.1, eta=0.01, iters=300, seed=0):
        self.K, self.alpha, self.eta = K, alpha, eta
        self.iters, self.seed = iters, seed

    def fit(self, docs, vocab):
        V = vocab.V
        self.vocab = vocab
        self.durs = np.array([t[1] for t in vocab.tokens], dtype=float)
        rng = np.random.default_rng(self.seed)
        K, a, e = self.K, self.alpha, self.eta
        ndk, nkw, nk = (np.zeros((len(docs), K)), np.zeros((K, V)), np.zeros(K))
        z = []
        for d, doc in enumerate(docs):
            zz = rng.integers(0, K, size=len(doc))
            z.append(zz)
            for n, w in enumerate(doc):
                ndk[d, zz[n]] += 1
                nkw[zz[n], w] += 1
                nk[zz[n]] += 1
        for _ in range(self.iters):
            for d, doc in enumerate(docs):
                for n, w in enumerate(doc):
                    k0 = z[d][n]
                    ndk[d, k0] -= 1; nkw[k0, w] -= 1; nk[k0] -= 1
                    p = (ndk[d] + a) * (nkw[:, w] + e) / (nk + V * e)
                    k1 = rng.choice(K, p=p / p.sum())
                    z[d][n] = k1
                    ndk[d, k1] += 1; nkw[k1, w] += 1; nk[k1] += 1
        self.theta = (ndk + a) / (ndk.sum(1, keepdims=True) + K * a)
        self.phi = (nkw + e) / (nk[:, None] + V * e)
        self.ndk, self.nkw, self.z = ndk, nkw, z
        self.canonicalize()
        return self

    def canonicalize(self):
        """Label switching fix: order topics by mean token duration."""
        order = np.argsort(self.phi @ self.durs)      # slow archetypes first
        self.phi, self.theta = self.phi[order], self.theta[:, order]

    def predictive(self, d, beta=None):
        p = self.theta[d]
        if beta is not None:
            p = p * beta
        return p / p.sum() @ self.phi

    def sample_cell(self, d, section_len, voice_pitch, rng, k_ladder, beta=None):
        w_p = self.predictive(d, beta)
        t, pitch, events = 0, voice_pitch, []
        while t < section_len:
            w = int(rng.choice(len(w_p), p=w_p))
            step, dur, dyn = self.vocab.tokens[w]
            dur = min(dur, section_len - t)            # zero-drift clamp
            pitch = int(np.clip(pitch + step * k_ladder, 36, 88))
            events.append((pitch, dyn, t, t + dur))
            t += dur
        return events

    def tension_curve(self):
        bar = self.theta.mean(0)
        return np.array([np.sum(th * np.log(np.clip(th, 1e-12, None) /
                                            np.clip(bar, 1e-12, None))) for th in self.theta])
```

(Full working version, including tokenization of a MIDI corpus and the engine build, is
`_web140/verify_140_LDATAC.py`.)

## 7. Measured results

| Check | Result |
|---|---|
| topic → archetype recovery (cosine, 1-1) | 0.991 / 0.994 / 0.998 |
| per-section mixture recovery | mean 0.994, min 0.941 |
| held-out perplexity vs uniform | **9.28** vs 30.0 |
| exchangeability | $\lvert\Delta\log p\rvert$ = 0.0 (exact) |
| determinism (same seed) | max $\lvert\Delta\phi\rvert$ = 0.0 |
| $\alpha$ → $\theta$ entropy | 0.289 / 0.551 / 0.943 nats ($\alpha$ = 0.05 / 1 / 8) |
| zero drift | 32/32 cells end at 7680 ticks |
| tension spread | 26× (0.029 → 0.765) |
| held-out mixture inference | mean 0.995, min 0.977 |
| $K{=}5$ over-specification | archetypes still covered at 0.995 / 0.998 / 0.991 |
| engine build | `validate() == True`, 1049 events, 8983 B MIDI |

## 8. Pitfalls (see full prose in `methods_db.md`)

1. Exchangeable ⇒ no order (use 012/016 or bigrams).
2. Short documents ⇒ meaningless $\theta$ (keep documents at section scale).
3. Label switching ⇒ canonicalize topic order before writing per-topic automation.
4. $\alpha$, $\eta$ extremes ⇒ blocky-oatmeal axis; measure entropy first.
5. Homogeneous corpus ⇒ $D_d\approx0$ ⇒ no form.
6. Corpus mismatch is silent (vocabulary, not $\alpha$, is the fix).
7. Clamp at draw time, exactly once.
8. Not 085 NMF-C / 086 HMM-C / 034 PCFG / 046 / 118.

## 9. References

1. Blei, D. M., Ng, A. Y., & Jordan, M. I. (2003). Latent Dirichlet Allocation. *JMLR* 3, 993–1022.
2. Griffiths, T. L., & Steyvers, M. (2004). Finding scientific topics. *PNAS* 101(suppl. 1), 5228–5235. doi:10.1073/pnas.0307752101
3. Pritchard, J. K., Stephens, M., & Donnelly, P. (2000). Inference of population structure using multilocus genotype data. *Genetics* 155(2), 945–959.
4. Teh, Y. W., Jordan, M. I., Beal, M. J., & Blei, D. M. (2006). Hierarchical Dirichlet Processes. *JASA* 101(476), 1566–1581. doi:10.1198/016214506000000302
5. Moss, F. C., & Rohrmeier, M. (2021). Discovering Tonal Profiles with Latent Dirichlet Allocation. *Music & Science* 4. doi:10.1177/20592043211048827
6. Latent Dirichlet Allocation Model for Raga Identification of Carnatic Music. *J. Computer Science* 7(11), 2011. doi:10.3844/jcssp.2011.1711.1716
7. Music mood classification based on lyrical analysis of Hindi songs using LDA. INCITE 2016. doi:10.1109/incite.2016.7857593
8. Wikipedia: "Latent Dirichlet allocation" (pageid 4605351).
