# Sound Production Method SP-128 — Empirical Mode Decomposition / Hilbert–Huang Adaptive Resynthesis (EMD-HAR)

**ID:** SP-128
**Layer:** absolute (sound production — LAYER_ARCHITECTURE.md)
**Category:** Post-Processing / DSP (data-driven modal decomposition)
**Candidate code path:** `sound/effects/emd_resynthesis.py`
**Dispatch:** `workflows/musicom_workflow.py::produce(method="SP-128", params={...})`
**Status:** documented + numerically verified 2026-10-30 (script: `projects/Research/outputs/sp128_research/verify_sp128_emd.py`)

---

## 1. One-line definition

A rendered audio buffer is decomposed, without any fixed basis, into a small set of
narrowband AM–FM modes (*intrinsic mode functions*, IMFs) plus a residual trend by
iterative cubic-spline envelope sifting; each mode is then resynthesized from its own
Hilbert instantaneous amplitude and frequency, so individual modes can be gained,
transposed, gated or deleted — with an exactly invertible analysis
($x=\sum_j c_j+r_n$, verified $1.4\times10^{-14}$).

---

## 2. Why EMD is not one of the existing methods

| Method | Basis | Linear? | Exact inverse? | Unit of decomposition |
|---|---|---|---|---|
| SP-026 phase vocoder | fixed STFT (window/hop) | yes | yes (with phase propagation) | frequency bin |
| SP-027 SMS | sinusoids + stochastic residual | yes | approximate | spectral peak track |
| SP-069 wavelet packets | fixed QMF pair | yes | yes | octave band (fixed) |
| SP-072 HPSS | none (median masks) | no (nonlinear mask) | yes | harmonic vs percussive *texture* |
| SP-108 McAulay-Quatieri | harmonic partials on an F0 grid | yes | approximate | partial |
| SP-127 STRAIGHT | F0-adaptive envelope | yes | approximate | {F0, envelope, aperiodicity} |
| **SP-128 EMD** | **none — built from the signal's extrema** | **no** | **yes (exact)** | **IMF (data-driven band)** |

The unique combination: **basis-free + nonlinear + exactly invertible + per-mode
instantaneous frequency**. Nothing else in the DB has all four.

---

## 3. Algorithm

### 3.1 Sifting (inner loop)

Given $x(t)$ sampled at $f_s$:

1. Find local maxima $\{t_i^{\max}\}$ and minima $\{t_i^{\min}\}$.
2. Interpolate $e_{\max}(t)$ through $(t_i^{\max}, x(t_i^{\max}))$ and $e_{\min}(t)$
   through $(t_i^{\min}, x(t_i^{\min}))$ — natural cubic splines in the reference
   implementation; Rilling's boundary conditions (mirror the first/last two extrema,
   antisymmetric at the ends) are the better edge treatment.
3. $m(t)=\tfrac12\,[e_{\max}(t)+e_{\min}(t)]$, $h(t)\leftarrow h(t)-m(t)$.
4. Repeat until
   $$\mathrm{SD}_k=\frac{\sum_t\lvert h_{k-1}(t)-h_k(t)\rvert^2}{\sum_t h_{k-1}^2(t)}<\theta,\qquad \theta\approx0.2 .$$
5. Stop also on a fixed cap $K_{\max}$ (5–12) — SD alone over-sifts noisy material and
   manufactures spurious low-frequency modes (observed: a 1.2 Hz trend split into four
   near-1.5 Hz IMFs with $\theta=0.2$, $K_{\max}=10$).

An **IMF** satisfies: (i) $\#\{\text{extrema}\}-\#\{\text{zero crossings}\}\in\{-1,0,1\}$;
(ii) the mean of its upper and lower envelopes is zero everywhere (by construction,
after convergence). Only then is $\mathcal{H}[c_j]$ physically meaningful.

### 3.2 Outer loop

$$r_0=x,\qquad c_j=\mathrm{sift}(r_{j-1}),\qquad r_j=r_{j-1}-c_j,$$
stop when $r_j$ has $<3$–$4$ extrema (it is a trend) or $j=J$.
Reconstruction is exact by telescoping:
$$x(t)=\sum_{j=1}^{J}c_j(t)+r_J(t).$$

### 3.3 Hilbert spectral analysis

For each IMF:
$$z_j(t)=c_j(t)+j\,\mathcal{H}[c_j](t),\quad
a_j(t)=\lvert z_j(t)\rvert,\quad
\varphi_j(t)=\arg z_j(t),\quad
f_j(t)=\frac{1}{2\pi}\frac{d\varphi_j}{dt}.$$

Discrete implementation: `z = scipy.signal.hilbert(c)`, `a = np.abs(z)`,
`phi = np.unwrap(np.angle(z))`, `f = np.gradient(phi) * fs / (2*np.pi)`.

**Hilbert spectrum:** $H(\omega,t)=\sum_j a_j(t)\,\delta(\omega-\omega_j(t))$;
**marginal spectrum:** $h(\omega)=\int H(\omega,t)\,dt$ — a non-stationary,
leak-free analogue of the power spectrum, and the natural visualization for choosing
which modes to keep.

### 3.4 Resynthesis and per-mode editing

$$y(t)=\sum_j \gamma_j\,g_j(t)\,a_j(t)\cos\!\Big(2\pi r_j\!\int_0^t f_j(\tau)\,d\tau+\varphi_j(0)\Big)+g_r\,r_J(t).$$

- $\gamma_j$ — static per-mode gain (band balance)
- $g_j(t)$ — per-mode envelope (swell, gate, rhythmic shape)
- $r_j$ — phase-rate transposition ($f\to r f$), envelope untouched
- $g_r$ — residual/DC handling (usually 0 or a 20 Hz high-pass)

**Verified transposition:** $r=1.5$ on narrowband modes gave argmax
660 → 990 Hz and 220 → 330 Hz, ratio **1.500** in both cases.
**Verified failure:** the broadband 1 Hz trend mode shifted 1.0 → 2.0 Hz (ratio 2.000,
nonsense) — bandwidth gating is mandatory before transposition.

### 3.5 Mode-mixing cures

**EEMD** (Wu & Huang 2009): $x_i=x+\epsilon w_i$, $w_i\sim\mathcal N(0,1)$, decompose each,
average by index: $\bar c_j=\frac1M\sum_i c_j^{(i)}$. Removes the *random* part of mode
mixing at the cost of completeness: measured $\lVert\sum_j\bar c_j-x\rVert/\lVert x\rVert
= 0.45$ ($M=6$, $\epsilon=0.3\sigma$) vs $1.4\times10^{-14}$ for plain EMD.

**CEEMDAN** (Torres et al. 2011): add $\beta_j E_1[w^{(i)}]$ to the *residual* at stage $j$
instead of to $x$; the final residual is carried explicitly, so completeness is restored and
the spurious early IMFs of EEMD disappear. Cost: $M\times$ sifting.

**Masking signal** (cheap alternative): add a strong sinusoid at the frequency you want
isolated, sift, subtract. Deterministic, one extra decomposition, no ensemble.

### 3.6 Filter-bank property (Flandrin, Rilling & Gonçalves 2004)

For wide-sense-stationary noise EMD behaves like a dyadic filter bank: the $j$-th IMF has
mean period $\propto 2^{j}$ and its spectrum is a self-similar octave band, with
$\mathbb E[J]\approx\log_2 N-1$. Consequence for production: "keep IMFs 1–3" is a
zero-phase, adaptive octave crossover **with no filter design**, and per-mode count is a
brightness control.

Measured on a real `compose(style="pop")` + `produce(method="SP-001")` render (44.1 kHz,
2 s): IMF spectral centroids **4657 / 1986 / 810 / 330 / 184 / 57 Hz** (ratios
2.3 / 2.5 / 2.5 / 1.8 / 3.2), reconstruction error $1.7\times10^{-16}$, 0.04 s for 2 s of
audio (45× realtime).

---

## 4. Python / NumPy implementation sketch

```python
import numpy as np
from scipy.interpolate import CubicSpline
from scipy.signal import hilbert

FS = 44100

def _extrema(x):
    d = np.diff(np.sign(np.diff(x)))
    return np.where(d < 0)[0] + 1, np.where(d > 0)[0] + 1     # maxima, minima

def _envelopes(x):
    """Upper/lower natural-cubic-spline envelopes (edge-clamped at the ends)."""
    n = len(x); maxi, mini = _extrema(x)
    if len(maxi) < 2 or len(mini) < 2:
        return None, None
    g = np.arange(n)
    up = CubicSpline(np.r_[0, maxi, n - 1], np.r_[x[maxi[0]], x[maxi], x[maxi[-1]]],
                     bc_type="natural")(g)
    lo = CubicSpline(np.r_[0, mini, n - 1], np.r_[x[mini[0]], x[mini], x[mini[-1]]],
                     bc_type="natural")(g)
    return up, lo

def sift(x, sd_thresh=0.2, max_iter=10):
    h = np.asarray(x, float).copy()
    for _ in range(max_iter):
        up, lo = _envelopes(h)
        if up is None:
            return h
        h_new = h - 0.5 * (up + lo)
        sd = np.sum((h - h_new) ** 2) / max(np.sum(h ** 2), 1e-30)
        h = h_new
        if sd < sd_thresh:
            break
    return h

def emd(x, max_imfs=6, sd_thresh=0.2, max_sift=10, min_extrema=4):
    res = np.asarray(x, float).copy(); imfs = []
    for _ in range(max_imfs):
        if np.count_nonzero(np.diff(np.sign(np.diff(res)))) < min_extrema:
            break
        imf = sift(res, sd_thresh, max_sift)
        if np.count_nonzero(np.diff(np.sign(np.diff(imf)))) < 2:
            break
        imfs.append(imf); res = res - imf
    return np.array(imfs), res

def modes(imf):
    """Instantaneous amplitude / frequency / phase of one mode."""
    z = hilbert(imf)
    return np.abs(z), np.gradient(np.unwrap(np.angle(z))) * FS / (2 * np.pi), np.angle(z)

def resynth(imfs, gain=None, transpose=None, residue=None):
    n = len(imfs[0]); y = np.zeros(n)
    for j, c in enumerate(imfs):
        a, f, _ = modes(c)
        g = 1.0 if gain is None else gain[j]
        r = 1.0 if transpose is None else transpose[j]
        bw = np.std(f[a > 0.3 * a.max()]) / max(np.median(f[a > 0.3 * a.max()]), 1e-9)
        if bw > 0.3:                      # wideband -> Bedrosian fails, do not transpose
            y += g * c
        else:
            y += g * a * np.cos(2 * np.pi * np.cumsum(r * f) / FS)
    if residue is not None:
        y += residue
    return y

def eemd(x, M=32, eps=0.3, seed=0, **kw):
    rng = np.random.default_rng(seed)
    imfs, _ = emd(x, **kw); acc = np.zeros((len(imfs), len(x)))
    for _ in range(M):
        im, _ = emd(x + eps * np.std(x) * rng.standard_normal(len(x)), max_imfs=len(imfs), **kw)
        pad = np.zeros_like(acc); pad[:len(im)] = im[:len(imfs)]; acc += pad
    return acc / M
```

**Production wrapper (proposed `sound/effects/emd_resynthesis.py`):**

```python
class EMDResynthesizer:
    def __init__(self, max_imfs=6, sd_thresh=0.2, edge_mode="mirror",
                 seam_xfade_ms=12, eemd_ensembles=0, seed=None):
        ...
    def process(self, x, keep=None, gain=None, transpose=None, residue_gain=0.0):
        """x: (n,) or (n,2). Returns edited buffer + provenance dict
        {imf_count, centroids, sd_thresh, max_sift, edge_mode, seed}."""
```

---

## 5. Cost (measured, single core, 44.1 kHz mono)

| Duration | IMFs | Time | Realtime factor |
|---|---|---|---|
| 0.5 s | 6 | 0.02 s | 25× |
| 1.0 s | 6 | 0.03 s | 32× |
| 2.0 s | 6 | 0.09 s | 21× |
| 2.0 s real render | 6 | 0.04 s | 45× |

Complexity: $O(J\cdot K\cdot N)$ sample operations plus a tridiagonal spline solve per
sift, $O(N_{\text{extrema}})$. No FFT per iteration (the Hilbert transform is one FFT
pair per mode). Non-causal: offline render stage only.

---

## 6. Verified claims (2026-10-30, `verify_sp128_emd.py`)

Test signal: 220 Hz + 660 Hz + 45 ms noise burst at t=0.40 s + 1.2 Hz trend, 1.0 s @ 44.1 kHz.

| # | Claim | Result |
|---|---|---|
| 1 | Exact reconstruction | 6 IMFs, max rel. error **1.394e-14** |
| 2 | Quasi-dyadic filter bank | centroids 9255 / 1429 / 88.5 / 13.7 / 6.4 / 5.4 Hz, strictly decreasing |
| 3 | Hilbert IF tracks partials | IMF1 median IF 658.9 Hz (660 Hz partial); IMF2 mixed (123 Hz median vs 220 Hz argmax) |
| 4 | IF-scaling transposition | 660→990 Hz and 220→330 Hz, ratio **1.500** exactly; 1 Hz trend mode → 2.0 Hz (wrong, wideband) |
| 5 | Mode mixing | 220 Hz landed in IMF index `[1,3,3,3,3]` across 0.05σ perturbations → **unstable** |
| 6 | EEMD breaks completeness | ensemble-mean reconstruction error **0.451** vs 1.4e-14 (plain) |
| 7 | Not a transient separator | burst energy share 3.6 % (IMF1) / 3.2 % (IMF2) < 4.5 % uniform → no isolation |
| 8 | Cost | 21–32× realtime synthetic, 45× realtime on a real engine render |
| 9 | Real render | `compose(style="pop")`+`produce("SP-001")`: 6 IMFs, err 1.7e-16, centroids 4657/1986/810/330/184/57 Hz |

---

## 7. Musical applications

- **Register re-orchestration of a rendered stem** — move the top stratum up a fifth
  ($r_1=1.5$), darken the bottom ($\gamma_{5,6}<1$), keep the body. No MIDI change.
- **Mode-selective thinning** — drop modes 2 and 5 to unclutter a dense mix while keeping
  attacks (IMF1) and weight (residue); the data-driven analogue of SP-007's static EQ.
- **Breath/rosin/air layer extraction** — keep only the top mode of a wind or bowed stem
  and gain it up: an "air band" derived from the material itself rather than a shelf.
- **Colored noise beds** — sift a field recording, keep the noise modes, transpose/gain
  them per section: texture continuity without a sample library.
- **Data-driven band ducking** — cross-modulate a mode's envelope $a_j$ by another row's
  envelope: band-specific sidechain compression.
- **Morphing** — interpolate per-mode gains/transpositions between two rows across a
  column boundary (a modal crossfade, complementary to SP-127's envelope morph).

---

## 8. Pitfalls (short form)

1. Mode mixing is the default (verified) — decompose per stem, or use EEMD/CEEMDAN/masking.
2. EEMD/CEEMDAN are not complete — verify $\lVert\hat x-x\rVert$ if a null test matters.
3. End effects are structural; mirror-pad ≥2 periods of the lowest mode, discard 20–50 ms,
   crossfade section seams.
4. EMD does **not** separate transients (verified, 3.6 % < 4.5 %) — use SP-072/SP-073/SP-118.
5. Bedrosian: bandwidth-gate before transposition or IF is not a physical frequency.
6. Parameters ($\theta$, $K_{\max}$, spline, edge rule) must be in provenance.
7. Nonlinear: no superposition — never reuse one decomposition across different mixes.
8. Non-causal: offline only.
9. Do not sift per cell (cost, inconsistent mode numbering).
10. "Drop IMF1 = denoise" is a musical decision, not a default; high-pass the residue.

---

## 9. References

1. Huang, N. E., Shen, Z., Long, S. R., Wu, M. C., Shih, H. H., Zheng, Q., Yen, N.-C.,
   Tung, C. C., Liu, H. H. (1998). "The empirical mode decomposition and the Hilbert
   spectrum for nonlinear and non-stationary time series analysis." *Proc. R. Soc. Lond. A*
   **454**(1971), 903–995. DOI 10.1098/rspa.1998.0193
2. Wu, Z., Huang, N. E. (2009). "Ensemble empirical mode decomposition: a noise-assisted
   data analysis method." *Advances in Adaptive Data Analysis* **1**(1), 1–41.
   DOI 10.1142/S1793536909000047
3. Flandrin, P., Rilling, G., Gonçalves, P. (2004). "Empirical mode decomposition as a
   filter bank." *IEEE Signal Processing Letters* **11**(2), 112–114.
   DOI 10.1109/LSP.2003.821662
4. Torres, M. E., Colominas, M. A., Schlotthauer, G., Flandrin, P. (2011). "A complete
   ensemble empirical mode decomposition with adaptive noise." *Proc. ICASSP 2011*,
   4144–4147. DOI 10.1109/ICASSP.2011.5947265
5. Boudraa, A.-O., Cexus, J.-C. (2007). "EMD-based signal filtering." *IEEE Trans.
   Instrumentation and Measurement* **56**(6), 2196–2202. DOI 10.1109/TIM.2007.907967
6. Rilling, G., Flandrin, P., Gonçalves, P. (2003). "On empirical mode decomposition and
   its algorithms." *Proc. IEEE-EURASIP Workshop on Nonlinear Signal and Image Processing
   (NSIP)*, Grado.
7. Molla, Md. K. I., Hirose, K., Minematsu, N. (2004). "Audio source separation from the
   mixture using empirical mode decomposition with independent subspace analysis."
   *Interspeech 2004*, 2449–2452. DOI 10.21437/interspeech.2004-395
8. Lai, W.-H., Chou, T.-Y., Chou, M.-C., Schuller, B. W. (2023). "Robust audio
   watermarking based on empirical mode decomposition and group differential relations."
   *J. Audio Eng. Soc.* **71**(3), 100–117. DOI 10.17743/jaes.2022.0067
9. Huang, N. E., Shen, S. S. P. (eds.) (2005). *Hilbert–Huang Transform and Its
   Applications.* World Scientific. — the standard monograph (boundary conditions,
   interpolation choices, EMD variants).
