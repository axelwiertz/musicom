# SP-136 — Syahi-Loaded Tension-Modulated Membrane Synthesis (SLTM)

**Layer:** absolute (sound production)
**Category:** Synthesis Engines → Physical Modeling → Pitched Membrane
**Candidate code path:** `sound/synthesis/tabla_membrane.py`
**Summary-table row (as inserted):**

```
| **SP-136** | Syahi-Loaded Tension-Modulated Membrane Synthesis (SLTM) | **Synthesis Engines** | Physical Tabla (Dayan/Bayan) / Pitched Harmonic Drum Timbre | Solves the density-graded circular-membrane eigenproblem ... Candidate: `sound/synthesis/tabla_membrane.py`. |
```

---

## 1. Why a tabla is a *pitched* drum

A uniform circular membrane of radius $a$, tension $T$ and areal density $\sigma_s$ has modes at the zeros of Bessel functions:

$$f_{mn}=\frac{\alpha_{mn}}{2\pi a}\sqrt{\frac{T}{\sigma_s}},\qquad J_m(\alpha_{mn})=0$$

$$\alpha_{01},\alpha_{11},\alpha_{21},\alpha_{02},\alpha_{31},\alpha_{12},\alpha_{41},\alpha_{22},\alpha_{03}
=2.40483,\ 3.83171,\ 5.13562,\ 5.52008,\ 6.38016,\ 7.01559,\ 7.58834,\ 8.41724,\ 8.65373$$

Normalised: **1, 1.5933, 2.1355, 2.2954, 2.6531, 2.9173, 3.1555, 3.5001, 3.5985** — no octave, no fifth, no pitch.

Reality check on a tabla: measured dayan eigenfrequencies (Sathej & Adhikari 2009, Table 1, normalised so the first overtone is 2.00) are

| mode | measured |
| :--- | :--- |
| $\psi_{01}$ | 1.03 |
| $\psi_{11}$ | 2.00 |
| $\psi_{21}$ | 3.00 |
| $\psi_{02}$ | 3.00 |
| $\psi_{31}$ | 4.00 |
| $\psi_{12}$ | 4.00 |
| $\psi_{03}$ | 5.04 |
| $\psi_{41}$ | 5.03 |
| $\psi_{22}$ | 5.08 |

i.e. an almost exact harmonic series with a fundamental ~3% sharp. The cause is the **syahi**: a layered paste (~8× the areal density of the goatskin, ~a quarter of the head area) applied concentrically on the dayan and **eccentrically** on the bayan.

---

## 2. The governing eigenproblem

Membrane with non-uniform areal density $\rho(\mathbf r)$ (dimensionless, 1 = bare skin):

$$\rho(\mathbf r)\frac{\partial^2u}{\partial t^2}=T\nabla^2u,\qquad u(a,\theta,t)=0$$

With $u=\psi(\mathbf r)e^{j\omega t}$:

$$-\nabla^2\psi=\frac{\omega^2}{T}\rho(\mathbf r)\,\psi$$

Density profile (Sathej & Adhikari Eq. 1–2), on the unit-radius head:

$$\rho(r,\theta)=1+\frac{\sigma^2-1}{2}\left[1-\tanh\left(\frac{R(r,\theta)-k}{\xi}\right)\right],\qquad
R(r,\theta)=\sqrt{(r\cos\theta-\epsilon)^2+(r\sin\theta)^2}$$

| parameter | meaning | daya | bayan |
| :--- | :--- | :--- | :--- |
| $\sigma^2$ | centre / edge density ratio | 6.6–9.8 | similar |
| $k$ | load radius; $k^2$ = loaded area fraction | 0.492 → 24% | 0.4–0.5 |
| $\xi$ | edge smoothness of the paste | 0.091 | 0.091 |
| $\epsilon$ | eccentricity of the patch | 0 | 0.3–0.4 |

Discretised (finite volume, cell centres $r_i=(i+\tfrac12)h$, $R(1)=0$):

$$\left[-\frac{1}{r_i h^2}\Big(r_{i+1/2}\psi_{i+1}-(r_{i+1/2}+r_{i-1/2})\psi_i+r_{i-1/2}\psi_{i-1}\Big)+\frac{m^2}{r_i^2}\psi_i\right]=\lambda\,\rho(r_i)\psi_i$$

i.e. $\mathbf A\boldsymbol\psi=\lambda\mathbf B\boldsymbol\psi$ with $\mathbf B=\operatorname{diag}(\rho)$, $\lambda=\omega^2/T$.

**Verified numbers** (`_web136/sp136_verify.py`, $N{=}1400$, $m{=}0\ldots4$):

- $\sigma{=}3.125$, $k{=}0.4$, $\xi{=}0.091$ → 1.0344, 2.0000, 3.0393, 3.0535, 4.0085, 4.1466, 4.7778, 5.0021, 5.2496
- published smooth-model column → 1.0345, 2.0000, 3.0393, 3.0534, 4.0086, 4.1463, 4.7784, 5.0023, 5.2491
- max deviation **0.0009 (≈0.5 cent)**; centre/edge density **9.76 / 1.00**
- unconstrained optimum: $\sigma{=}2.57$, $k{=}0.492$ → 1.0994, 2.0000, 2.9584, 3.0535, 3.9545, 4.0203, 4.9038

Physically: added mass with (nearly) unchanged stiffness lowers every $\omega_n$, and lowers $\omega_1$ the most, compressing the spectrum toward integers. The residual +10% sharpness of mode 1 at the optimised $\sigma$ is the model's known trade-off and is why harmonicity must be judged against the **first overtone**, not the fundamental.

Degeneracy: for $\epsilon=0$ the $m\ge1$ modes are doublets ($\cos m\theta,\sin m\theta$) with equal frequency; $\epsilon>0$ splits each doublet into two frequencies a few Hz apart → beating ("wobble") — the bayan's signature.

---

## 3. Synthesis stage: modal sum with a moving frequency

$$y(t)=\sum_{n=1}^{N}g_n\,a_n(t)\,\sin\varphi_n(t),\qquad
\varphi_n(t)=2\pi\int_0^tf_n(\tau)\,d\tau+\phi_n,\qquad
a_n(t)=\exp\left(-\int_0^t\frac{d\tau}{\tau_n(\tau)}\right)$$

Discrete:

```python
phase += 2*np.pi*f_n/fs          # per-sample accumulator (correct)
# NOT np.sin(2*np.pi*f(t)*t)     # instantaneous freq = f + t*df/dt  (wrong)
```

Excitation projection (strike at $r_s,\theta_s$, contact half-width $w$):

$$g_{mn}\propto R_{mn}(r_s)\cos(m\theta_s)\,\big|\operatorname{sinc}(\pi f_{mn}w)\big|$$

so the strike position *is* the articulation: rim → ring modes ($na$), syahi ring → $m{=}0$ ($tin$), damped centre → closed thud ($ta$), bayan open + heel → low modes with glide ($ghe$).

Loss model: $\tau_n^{-1}=\tau_{n,\text{body}}^{-1}+\kappa_{\text{kinar}}f_n^{2}$ (edge flap damps highs; $\tau_1\approx0.4$–1.0 s, $\tau_{n\ge3}\approx40$–150 ms).

---

## 4. Tension modulation (the glide)

Heel pressure $p(t)\in[0,1]$ stretches the unloaded sector:

$$T(t)=T_0\,(1+\beta p(t)),\qquad f_n(t)=f_n^{(0)}\sqrt{T(t)/T_0},\qquad
\Delta_{\text{st}}=6\log_2\frac{T}{T_0}$$

| bend | $T/T_0$ |
| :--- | :--- |
| −2 st | 0.794 |
| −3 st | 0.707 |
| −5 st | 0.561 |
| −7 st | 0.445 |
| +2 st | 1.260 |

All modes scale together → the series stays harmonic through the bend, which is why the bayan keeps its identity while sliding.

---

## 5. NumPy implementation sketch

```python
import numpy as np
from scipy.special import jn_zeros

class SyahiProfile:
    def __init__(self, sigma=3.125, k=0.4, xi=0.091, eps=0.0):
        self.sigma, self.k, self.xi, self.eps = sigma, k, xi, eps

    def rho(self, r):                      # concentric case, r in [0,1]
        return 1.0 + (self.sigma**2 - 1)/2*(1 - np.tanh((r - self.k)/self.xi))

class RadialMembraneSolver:
    """A psi = lam B psi  with  B = diag(rho)."""
    def __init__(self, profile, n_cells=1400, m_max=4):
        self.p, self.N, self.m_max = profile, n_cells, m_max

    def solve(self, n_modes=12):
        N, h = self.N, 1.0/self.N
        r = (np.arange(N) + 0.5)*h
        B = np.diag(self.p.rho(r))
        modes = []
        for m in range(self.m_max + 1):
            A = np.zeros((N, N))
            for i in range(N):
                rip, rim = r[i] + h/2, r[i] - h/2
                if i + 1 < N: A[i, i+1] += -rip/(r[i]*h*h)
                if i > 0:     A[i, i-1] += -rim/(r[i]*h*h)
                A[i, i] += (rip + rim)/(r[i]*h*h) + m*m/r[i]**2
            lam = np.linalg.eigvals(np.linalg.solve(B, A))
            lam = np.sort(np.real(lam[lam > 1e-6]))[:n_modes]
            for n, l in enumerate(lam, start=1):
                modes.append((m, n, float(np.sqrt(l))))
        modes.sort(key=lambda t: t[2])
        return modes[:n_modes]

class TablaVoice:
    def __init__(self, f0=146.8, ratios=None, fs=44100):
        self.fs = fs
        self.f0 = f0
        # ratios from the solved eigenproblem (harmonic for a syahi head)
        self.ratios = np.asarray(ratios or [1.0, 2.0, 3.0, 3.05, 4.0, 4.15, 4.78])

    def stroke(self, dur, vel=0.9, amps=None, taus=None,
               glide_st=0.0, glide_ms=150.0, noise=0.2, seed=0):
        n = int(dur*self.fs); t = np.arange(n)/self.fs
        target = 2**(glide_st/12)
        s = 1 + (target - 1)*(1 - np.exp(-t/(glide_ms/1000)))   # sqrt(T/T0)
        amps = np.full(len(self.ratios), 0.5) if amps is None else np.asarray(amps)
        taus = np.geomspace(0.5, 0.06, len(self.ratios)) if taus is None else np.asarray(taus)
        y = np.zeros(n)
        for r_, a, tau in zip(self.ratios, amps, taus):
            phase = 2*np.pi*np.cumsum(self.f0*r_*s)/self.fs   # integral of f(t)
            y += a*np.exp(-t/tau)*np.sin(phase)
        rng = np.random.default_rng(seed)
        nz = np.diff(np.r_[0.0, rng.standard_normal(n)*np.exp(-t/0.004)])
        y += noise*vel*nz
        return vel*y/(np.max(np.abs(y)) + 1e-12)
```

Measured on the prototype: `na` (dayan, 146.8 Hz, 0.9 s) spectral centroid **5660 Hz**; `ghe` (bayan, 73.4 Hz, 1.2 s, −5 st over 160 ms) centroid **3066 Hz** — the bayan is darker and longer, as expected.

---

## 6. References

1. Raman, C. V., & Kumar, S. (1920). Musical drums with harmonic overtones. *Nature* 104, 500–501.
2. Ramakrishna, B. S., & Sondhi, M. M. (1954). Vibrations of Indian musical drums regarded as composite membranes. *JASA* 26(4), 523–529.
3. Sathej, G., & Adhikari, R. (2009). The eigenspectra of Indian musical drums. *JASA* 125(2), 831–838. arXiv:0809.1320.
4. Malu, S. S., & Siddharthan, A. (2000). Acoustics of the Indian Drum. arXiv:math-ph/0001030.
5. Rossing, T. D., & Sykes, W. A. (1982). Acoustics of Indian drums. *Percussionist* 19, 58–67.
6. Rossing, T. D. (2000). *Science of Percussion Instruments*. World Scientific.
7. Patranabis, A., et al. (2015). Harmonic and Timbre Analysis of Tabla Strokes. arXiv:1510.04880.
8. Bilbao, S. (2009). *Numerical Sound Synthesis*. Wiley (variable-coefficient FDTD, CFL).
9. Fletcher, N. H., & Rossing, T. D. (1998). *The Physics of Musical Instruments*, 2nd ed. Springer.

---

## 7. Pitfalls (short form)

1. Normalise harmonicity against the first overtone, not the fundamental (mode 1 is 3–10% sharp by design).
2. Phase-integrate the glide; $\sin(2\pi f(t)t)$ overshoots.
3. $f\propto\sqrt T$: −6 st per halving of tension, not −12.
4. Syahi is **mass**, not stiffness.
5. Eccentric load ($\epsilon>0$) is required for the bayan's beating wobble.
6. Decay must follow the moving tension, $\exp(-\int d\tau/\tau(t))$.
7. Band-limit strike noise to the mode range; couple level and brightness to velocity.
8. Budget the tail inside the cell; fade 5–20 ms at section seams — never trim, never retro-retune a ringing tail.
9. Cache the eigen-solve keyed on $(\sigma,k,\xi,\epsilon)$; store $f_n,\tau_n,g_n$, not matrices.
10. FDTD CFL uses $\rho_{\min}$ (bare edge).
11. Band-limit the mode list below Nyquist when retuning up.
12. Distinct from SP-040 (uniform FDTD), SP-042 (uniform MBED), SP-087/098 (analog drum circuits), SP-120 (particle percussion).
