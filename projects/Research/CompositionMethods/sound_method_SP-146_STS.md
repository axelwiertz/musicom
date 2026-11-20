# SP-146 — Sound Texture Synthesis via Filter Statistics (STS)

- **Method ID:** SP-146
- **Layer:** absolute (sound production — `LAYER_ARCHITECTURE.md`)
- **Category:** Synthesis Engines
- **Candidate code path:** `sound/synthesis/texture_statistics.py`
- **Dispatch:** `produce(midi_path, method="SP-146", params={...})`
- **Prototype:** `_web146_sts/sts_prototype.py` (verified, see §7)
- **Prerequisites:** NumPy, SciPy (`hilbert`, `butter/sosfiltfilt`), soundfile. No training, no corpus, no GPU.

---

## 1. What it is

A sound texture (rain on a roof, wind, fire, surf, a crowd, insects, machinery, vinyl
surface noise) is a superposition of very many rapid micro-events whose individual
identities are inaudible but whose *aggregate statistics* are highly recognisable. STS
models such a sound as a **stationary stochastic process** and resynthesises it by
imposing a compact vector of summary statistics — measured on a reference recording, or
authored directly — onto white noise.

The premise is perceptual, not signal-theoretic: the auditory system is hypothesised to
represent textures by exactly these statistics (McDermott & Simoncelli 2009; McDermott,
Oxenham & Simoncelli 2011). Even if that claim is only partly true, the practical result
holds — the statistics are sufficient to make a synthetic texture recognisable, and they
are *few enough to be compositional parameters*.

The method's defining negative result: **matching only the marginal statistics of each
frequency band (variance, kurtosis) yields "filtered noise", not a texture.** What makes
many micro-events fuse into one perceived object is the **cross-band envelope
correlation matrix**. That term is the method.

---

## 2. Analysis

### 2.1 Cochlear filterbank (ERB)

The bank is deliberately *auditory*, not musical: bands are equally spaced on the
Glasberg–Moore ERB-rate scale, so low bands are narrow in Hz and high bands wide.

$$E(f)=21.4\log_{10}\!\left(1+0.00437f\right),\qquad
f_b=E^{-1}\!\left(E(f_{\min})+\frac{b}{B}\big[E(f_{\max})-E(f_{\min})\big]\right)$$

Canonical parameters: $B=30$, $f_{\min}=52$ Hz, $f_{\max}=8848$ Hz (2011 paper);
the prototype uses $B=24$, 60–8000 Hz at $f_s=22.05$ kHz.

The filters must be a **partition of unity**:

$$\sum_{b=1}^{B}H_b(f)=1\quad\Longrightarrow\quad \sum_{b=1}^{B}x_b[n]=x[n]$$

Implementation: flat passband + short (≈15 % of band width) raised-cosine crossfade into
each neighbour. Two failure modes to avoid:

* wide crossfades (a band then overlaps its neighbour over a whole band width, so
  re-analysis smears energy across bands);
* an **unclamped cosine taper** — `0.5+0.5·cos(π(f−hi)/w)` keeps oscillating for
  $f\gg hi$ and is non-zero across the entire spectrum, which silently makes every
  band broadband while the bank still sums to 1. Clamp the taper argument to $[0,1]$.

### 2.2 Analytic envelope, compression, decimation

$$x^{a}_b[n]=x_b[n]+j\,\mathcal{H}\{x_b\}[n],\qquad
e_b[n]=\left|x^{a}_b[n]\right|,\qquad
c_b[n]=e_b[n]^{0.3}$$

The 0.3 power is the cochlear compressive nonlinearity; it is not cosmetic — all
statistics are computed on $c_b$, and synthesis must undo it with $(\cdot)^{1/0.3}$.

Envelopes vary slowly, so they are decimated to $f_e=400$ Hz. **$f_e$ is part of the
model**: at 400 Hz, "correlation" means "co-fluctuation within 2.5 ms frames". Compute
envelopes at audio rate and the correlation matrix becomes near-diagonal — a silently
different model.

The **fine structure** $u_b=x^{a}_b/|x^{a}_b|$ carries within-band phase. It is kept from
the base signal; it is what makes the output sound like a recording instead of a noise
generator. (But do not use $u_b$ directly as a multiplier: normalising by a near-zero
envelope explodes. Modulate the *band signal* by a smoothed envelope ratio instead.)

### 2.3 Modulation filterbank

Each $c_b$ is split into $N_G\approx20$ logarithmic modulation bands over 0.5–200 Hz:

$$m_{b,k}=g_k * c_b,\qquad k=1\dots N_G$$

This is the "grain-rate" description: rain has broadband 20–200 Hz modulation, surf has
0.1–1 Hz swells, fire has 5–50 Hz crackle bursts, a crowd has 2–8 Hz syllabic modulation.

---

## 3. Statistics (the parameter vector)

With $E_w[\cdot]$ a windowed expectation (window $w$ sums to 1 to avoid DFT circular
boundary artefacts):

**$S_1$ — marginals** (per band, $L=4$):

$$M_1=E_w[c_b],\qquad M_2=\frac{E_w[(c_b-M_1)^2]}{M_1^2},\qquad
M_l=\frac{E_w[(c_b-M_1)^l]}{\sigma_b^{l}},\ l=3,4$$

**$S_2$ — cross-band envelope correlation** (the fusion term):

$$C_{kl}=\frac{E_w[(c_k-\mu_k)(c_l-\mu_l)]}{\sigma_k\sigma_l},\qquad
S_2=\operatorname{vech}(\mathbf{C})\in\mathbb{R}^{B(B-1)/2}$$

**$S_3$ — modulation power profile** (per band, normalised):

$$S_{3,b}=\frac{\big(\sqrt{\operatorname{Var}(m_{b,1})},\dots,\sqrt{\operatorname{Var}(m_{b,N_G})}\big)}{\sqrt{\operatorname{Var}(c_b)}}$$

**$S_4$ — modulation correlation within a band** (octave-spaced rates):

$$S_{4,b}=\operatorname{vech}\operatorname{corr}(m_{b,1},\dots,m_{b,N_G})$$

**$S_5$ — modulation correlation across bands at the same rate**:

$$S_{5,k}=\operatorname{vech}\operatorname{corr}(m_{1,k},\dots,m_{B,k})$$

Distance (the TexStat loss, arXiv:2506.04073):

$$\mathcal{L}_{\alpha,\beta}(x,y)=\sum_{j=1}^{5}\beta_j\,\mathrm{MSE}\big(S_j(x),S_j(y)\big)$$

with $\alpha$ weighting the moment orders and $\beta$ the five families. For pure
synthesis $\beta$ mostly matters through the iteration budget: $S_2$ carries the
perceptual load.

**Dimension check.** $B=30$, $N_G=20$ gives $|S_1|=120$, $|S_2|=435$, $|S_3|=600$,
$|S_4|=30\cdot190=5700$, $|S_5|=20\cdot435=8700$ — over 15 000 numbers on a few thousand
envelope samples. The system is badly over-determined: use long windows (≥ 3–5 s) and/or
drop $S_4$/$S_5$ to diagonal terms. The prototype keeps $S_1$, $S_2$ and a diagonal
$S_3$.

---

## 4. Synthesis

### 4.1 Alternating projections instead of gradient descent

The 2011 paper imposes statistics band-by-band by gradient descent, highest-power band
first, which is slow and order-dependent. The equivalent in convex-projection form is a
two-operator alternation on the envelope matrix $\mathbf{E}\in\mathbb{R}^{B\times T}$:

**(a) Marginal projection (exact, closed form).** 1-D optimal transport between two
empirical distributions is the monotone map between their quantiles, i.e. rank-order
assignment of the target's sorted values:

$$\tilde{E}_{b,(i)}=c^{\text{tgt}}_{b,(i)},\qquad (i)=\operatorname{rank}\big(E_b[i]\big)$$

One `argsort` matches **all** moments of the marginal exactly — no learning rate, no
divergence. This replaces the moment-matching gradient step entirely.

**(b) Correlation recolouring (exact, linear).** Whiten with the current covariance and
recolour with the target:

$$\mathbf{E}\leftarrow\mathbf{C}_{\text{cur}}^{-1/2}\,\mathbf{C}_{\text{tgt}}^{1/2}\,\mathbf{E},
\qquad
\mathbf{C}^{\pm1/2}=\mathbf{V}\boldsymbol{\Lambda}^{\pm1/2}\mathbf{V}^{\!\top}$$

Since $\operatorname{Cov}(\mathbf{E}')=\mathbf{C}_{\text{cur}}^{-1/2}\mathbf{C}_{\text{tgt}}\mathbf{C}_{\text{cur}}^{-1/2}
\operatorname{Cov}(\mathbf{E})\,\mathbf{C}_{\text{cur}}^{-1/2}\dots=\mathbf{C}_{\text{tgt}}$
(symmetrically), the correlation is matched in one linear step. Ridge the eigenvalues
($\lambda\ge10^{-6}$) because narrow high bands can be nearly collinear.

The two projections do not commute, so iterate 10–20 times. Measured convergence in the
prototype: $\|\mathbf{C}-\mathbf{C}_{\text{tgt}}\|_F/\|\mathbf{C}_{\text{tgt}}\|_F$
$=0.032\to0.0009$.

### 4.2 Resynthesis

Expand the projected compressed envelopes, undo the compression, smooth, and
amplitude-modulate the base bands:

$$E_b[n]=\operatorname{LP}_{150\,\mathrm{Hz}}\Big[\big(\hat c_b[n]\big)^{1/0.3}\Big],\qquad
B_b[n]=\operatorname{LP}_{150\,\mathrm{Hz}}\Big[\big(\hat c^{\text{base}}_b[n]\big)^{1/0.3}\Big]$$

$$y[n]=\sum_{b=1}^{B}x_b[n]\cdot\frac{E_b[n]}{B_b[n]}$$

The low-pass is not optional: piecewise-linear interpolation of a 400 Hz envelope has
derivative discontinuities every 2.5 ms that splatter broadband noise (−20 dB-ish
artefacts at 8–11 kHz in the first prototype version, completely changing the spectral
centroid).

### 4.3 Outer consistency iterations

Re-analysing $y$ does not return the imposed envelopes, because band overlap
redistributes energy (the 2019 thesis calls this the consistency problem, analogous to
STFT consistency). Remedy: 2–3 outer iterations

```
E ← project(E_target, C_target)          # inner sweeps
repeat 2–3 times:
    y ← resynthesise(E)                  # AM of base fine structure
    E ← normalise(analyse_envelopes(y))  # re-analyse the acoustic result
    E ← project(E, C_target)             # re-impose
```

Prototype: acoustic correlation error $0.142\to0.119$.

### 4.4 Morphing in statistics space

$$\mathbf{L}_\lambda=(1-\lambda)\mathbf{L}_A+\lambda\mathbf{L}_B,\qquad
\mathbf{C}_\lambda=\frac{\mathbf{L}_\lambda\mathbf{L}_\lambda^{\!\top}}{\|\mathbf{L}_\lambda\mathbf{L}_\lambda^{\!\top}\|},
\qquad Q_\lambda=(1-\lambda)Q_A+\lambda Q_B$$

where $\mathbf{L}=\mathbf{C}^{1/2}$ (Cholesky or symmetric square root) and $Q$ is the
quantile function of a band's envelope. Interpolate **factors**, never raw correlation
matrices — a linear blend of two PSD matrices is PSD, but a linear blend of two
*correlation* matrices need not be a correlation matrix (unit diagonal), and a blend of
Cholesky factors keeps both properties after renormalisation. This gives seamless
rain→fire morphs with no audio crossfade and no loop point.

---

## 5. Musical Elements Framework

- **PITCH** — none. STS is unpitched by design; pitched material (bells, speech, chimes,
  music) is a documented failure class. Pitch can enter as a brightness anchor (band-gain
  tilt or resampling ratio tracking a MIDI note) or as an emergent buzz when a modulation
  band dominates.
- **RHYTHM** — the modulation spectrum $S_3$ *is* the rhythm: event rate, grain density,
  swell rate. Boosting the modulation band at $\text{BPM}/60$ makes a texture pulse
  without any onset events; 0.05–0.5 Hz = swells, 4–16 Hz = shimmer/tremolo, >40 Hz =
  roughness.
- **HARMONY** — no pitch classes; the spectral-envelope vector plays the harmonic role
  (register/brightness changes read as instrumentation changes). Complementary band
  profiles avoid masking between rows (SP-007 downstream).
- **STRUCTURE** — the model is stationary, so form must be imposed as a **trajectory in
  statistics space** (intensity arc, brightness arc, coherence arc). Textures morph or
  are cut; they never cadence. Ideal for intros, transitions, beds, codas.
- **TEXTURE** — the method's home axis, four-dimensional: density (modulation rate),
  grain size (which modulation bands carry power), noisiness (kurtosis: Gaussian hiss vs
  impulsive crackle), coherence (off-diagonal mass of $\mathbf{C}$: one fused source vs
  many independent ones), plus stationarity (window length).

---

## 6. UnitMatrix integration

| UnitMatrix | STS object |
|---|---|
| **Row = voice** | one texture layer: `{ref or preset, B, fmin, fmax, env_fs, seed, base}` |
| **Column = section** | statistics state: `{intensity, brightness, coherence_scale, grain_rate, morph_to, morph_lambda}` |
| **Cell = MusicUnit** | a *region* (`start_tick`…`end_tick`) where the texture is present; pitch = optional brightness anchor, velocity = intensity |
| **Section boundary** | morph in statistic space over N ticks, not an audio crossfade |

```python
produce(midi_path, method="SP-146", params={
    "rows": {
        "rain":  {"ref": "assets/rain_roof.wav", "B": 24, "fmin": 60, "fmax": 8000, "seed": 3},
        "crowd": {"preset": "babble", "coherence": 0.35, "seed": 11},
    },
    "columns": {
        "A": {"intensity": 0.35, "brightness_db": -3},
        "B": {"intensity": 0.85, "grain_rate": 1.3, "morph_to": "rain_roof", "morph_lambda": 0.25},
    },
})
```

Generate **once per (row, section)** for the whole section length plus tail, then slice —
never per note, or stationarity breaks at every event boundary. Zero drift still binds:
the buffer must fill exactly `section_ticks` at the row's sample rate (pad/trim
deterministically, assert the sample count before mixing).

---

## 7. Verified prototype (measured, not asserted)

`_web146_sts/sts_prototype.py` (24 ERB bands 60–8000 Hz, 400 Hz envelopes, 15 inner ×
3 outer sweeps, 4 s at 22.05 kHz, seed 7):

| check | measured |
|---|---|
| projection-domain correlation error | **0.032 → 0.0009** |
| acoustic (re-analysed) correlation error | **0.142 → 0.119** over outer iterations |
| per-band RMS error | **0.34 dB** median, **0.57 dB** max |
| spectral centroid | 2553.5 Hz vs 2574.8 Hz target (**0.83 %**) |
| kurtosis | max 8.09 vs 9.08 target (abs. err ≤ 0.99) |
| peak / DC | 0.89 / −3.0e−18 |
| WAV | `sts_out.wav`, 176,444 B |
| runtime | 1.9 s for 4 s audio (CPU, NumPy) |

Artefacts: `sts_stats.json`, `sts_out.wav`, `sts_target.wav`, plus research dumps in
`_web146_sts/`.

---

## 8. NumPy implementation sketch

```python
import numpy as np
from scipy.signal import butter, hilbert, sosfiltfilt
import soundfile as sf

FS, DEC, NB = 22050, 55, 24          # 400 Hz envelopes
FS_ENV = FS // DEC

def erb_edges(nb, fmin, fmax):
    h2e = lambda f: 21.4 * np.log10(1 + 0.00437 * f)
    e2h = lambda e: (10 ** (e / 21.4) - 1) / 0.00437
    return e2h(np.linspace(h2e(fmin), h2e(fmax), nb + 1))

def band_gains(n, nb=NB, fmin=60.0, fmax=8000.0, frac=0.15):
    edges = erb_edges(nb, fmin, fmax)
    f = np.fft.rfftfreq(n, 1 / FS)
    H = np.zeros((nb, f.size))
    for b in range(nb):
        lo, hi = edges[b], edges[b + 1]
        w = frac * (hi - lo)
        up = 0.5 - 0.5 * np.cos(np.pi * np.clip((f - (lo - w)) / w, 0, 1))
        dn = 0.5 + 0.5 * np.cos(np.pi * np.clip((f - hi) / w, 0, 1))
        g = np.where(f < lo, up, 1.0)
        H[b] = np.where(f > hi, dn, g)
    return H / np.maximum(H.sum(0), 1e-12)

def bands_of(x, H):
    return np.fft.irfft(np.fft.rfft(x)[None, :] * H, n=x.size, axis=1)

def env_stats(x, H):
    e = np.abs(hilbert(bands_of(x, H), axis=1)) ** 0.3
    m = (e.shape[-1] // DEC) * DEC
    c = e[:, :m].reshape(len(H), -1, DEC).mean(2)          # (B, T) at 400 Hz
    mu, sd = c.mean(1, keepdims=True), c.std(1, keepdims=True)
    z = (c - mu) / np.maximum(sd, 1e-9)
    mom = np.stack([mu[:, 0], (sd[:, 0] / mu[:, 0]) ** 2,
                    (z ** 3).mean(1), (z ** 4).mean(1)], 1)
    return c, mom, np.nan_to_num(np.corrcoef(c))

def sqrtm(C, inv=False):
    w, V = np.linalg.eigh(C)
    w = np.clip(w, 1e-6, None) ** (-0.5 if inv else 0.5)
    return (V * w) @ V.T

def quantile_project(row, tgt_sorted):
    out = np.empty_like(row)
    out[np.argsort(row)] = tgt_sorted
    return out

def project(E, Ct, tgt_sorted, sweeps=15):
    for _ in range(sweeps):
        E = (sqrtm(np.corrcoef(E), True) @ sqrtm(Ct)).T @ E
        E = np.array([quantile_project(E[b], tgt_sorted[b]) for b in range(len(E))])
    return E

# ... resynthesis: y = sum_b x_b * (Efull_b / Bfull_b), envelopes low-passed at 150 Hz
```

Full working version (with the base-noise handling, outer consistency loop and the
verification harness) is `_web146_sts/sts_prototype.py`.

---

## 9. Pitfalls (condensed)

1. Statistics are necessary but not sufficient — pitched/rhythmic/reverberant targets fail.
2. Marginal-only matching = filtered noise; $S_2$ is mandatory.
3. Verify on the re-analysed output, not on the internal envelope matrix.
4. $f_e=400$ Hz is part of the model; changing it changes what "correlation" means.
5. Never regenerate the fine structure or divide by a raw (near-zero) envelope.
6. Statistic count must respect window length (≥ 3–5 s, or drop $S_4/S_5$).
7. Time-invariance is the feature: no null test against the reference.
8. Stereo needs a joint $2B$ correlation matrix, not two independent channels.
9. Fades/gates are statistical events; keep them short and outside steady sections.
10. Zero drift still binds: buffers must fill the section exactly.
11. Seed everything; record the seed and statistics hash for reproducible renders.
12. Neighbour audit: SP-016 grains, SP-044 corpus units, SP-069 wavelet reweighting,
    SP-026/027/039 sinusoidal models, SP-035 GENDYN, SP-072 HPSS — none is statistical
    generation from a summary-statistics vector.

---

## 10. References

1. J. H. McDermott, E. P. Simoncelli, "Sound texture synthesis via filter statistics,"
   *Proc. IEEE WASPAA*, 2009, 297–300. DOI 10.1109/ASPA.A.2009.5346467.
2. J. H. McDermott, A. J. Oxenham, E. P. Simoncelli, "Sound texture perception via
   statistics of the auditory periphery: evidence from sound synthesis," *Neuron* 70(6),
   2011, 1178–1192. DOI 10.1016/j.neuron.2011.06.032.
3. J. H. McDermott, M. Schemitsch, E. P. Simoncelli, "Summary statistics in auditory
   perception," *Nature Neuroscience* 16, 2013, 493–498.
4. M. Lagrange, S. Marchand, M. Raspaud, "State of the art in sound texture synthesis,"
   *Proc. DAFx-11*, 2011. HAL hal-01161296.
5. "Sound texture synthesis from summary statistics," PhD thesis, 2019, ch. 4
   (eqs. 4.1–4.11). HAL tel-03789695.
6. "A Statistics-Driven Differentiable Approach for Sound Texture Synthesis and Analysis"
   (TexStat / TexEnv / TexDSP), arXiv:2506.04073, 2025.
7. B. C. J. Moore, B. R. Glasberg, "Suggested formulae for calculating auditory-filter
   bandwidths and excitation patterns," *JASA* 74, 1983 (ERB scale).
8. A. J. E. M. Janssen, R. N. J. Veldhuis, L. B. Vries, "Adaptive interpolation of
   discrete-time signals," *IEEE Trans. ASSP*, 1986 (interpolation/decimation of
   envelopes).
