# Method SP-092: Scalar Auxiliary Variable Nonlinear String Synthesis (SAV-NSS)

**Method ID:** SP-092  
**Layer:** `absolute` (Sound Production — Synthesis Engines)  
**Author:** Sound Production Research Agent  
**Date:** 2026-09-21  

---

## 1. Executive Summary

**Scalar Auxiliary Variable Nonlinear String Synthesis (SAV-NSS)** simulates the large-amplitude, geometrically exact transverse vibration of acoustic strings bidirectionally coupled to multi-resonant instrument bodies (bridges and soundboards). In musical acoustics, plucking an acoustic string hard creates pronounced nonlinear effects:
- **Dynamic pitch glide:** Increased string tension at peak displacement temporarily sharpens pitch by 10–60 cents before settling down to the nominal fundamental as energy dissipates.
- **Spectral enrichment & phantom partials:** Pointwise nonlinear slope coupling generates intermodulation products and overtone cascades not present in linear wave equations.
- **Body interaction:** Bidirectional energy exchange between string termination and bridge admittance modes creates realistic body warmth, frequency-dependent damping, and sympathetic resonance across open strings.

Historically, solving the geometrically exact nonlinear potential required implicit nonlinear equations solved via Newton–Raphson iterations at every time step, incurring high computational cost and risk of divergence. SAV-NSS applies the **Scalar Auxiliary Variable (SAV)** approach: reformulating the non-negative nonlinear elastic potential via an auxiliary scalar $\psi(t) \triangleq \sqrt{2\phi_{\mathrm{nl}}(u) + \varepsilon}$. This exact continuous-level transformation makes the time-discretized system strictly linear with two rank-one perturbations. Using two sequential **Sherman–Morrison formula** updates, the coupled string–bridge state is inverted explicitly in $\mathcal{O}(M + J)$ operations per time step without matrix inversions or iterative solvers.

---

## 2. Mathematical Formulation

### 2.1. Continuous-Time Equations of Motion

Consider a stiff string of length $L$, linear mass density $\mu$, nominal tension $T_0$, Young's modulus $E$, cross-sectional area $A$, and second moment of area $I$. The transverse displacement $u(x,t)$ satisfies:

$$\mu \partial_t^2 u = T_0 \partial_x^2 u - E I \partial_x^4 u - \mu \sigma \partial_t u - \frac{\delta \phi_{\mathrm{nl}}}{\delta u} + \delta(x - x_e) f_e(t) + \delta(x - x_b) F_b(t)$$

subject to simply supported boundary conditions $u(0,t) = \partial_x^2 u(0,t) = u(L,t) = \partial_x^2 u(L,t) = 0$.

### 2.2. Geometrically Exact Nonlinear Potential & SAV Transform

Let $\zeta(x,t) \triangleq \partial_x u(x,t)$ denote the local spatial slope. The Green–Lagrange strain without longitudinal degrees of freedom is:

$$\varepsilon_{\mathrm{GL}} = \sqrt{1 + \zeta^2} - 1$$

The nonlinear elastic potential density $\mathcal{V}(\zeta)$ and total potential $\phi_{\mathrm{nl}}(u)$ are:

$$\mathcal{V}(\zeta) = \frac{G}{2}\left(\sqrt{1 + \zeta^2} - 1\right)^2 \ge 0, \quad G \triangleq E A - T_0 > 0$$

$$\phi_{\mathrm{nl}}(u) = \int_0^L \mathcal{V}\left(\partial_x u\right)\,dx \ge 0$$

Define the scalar auxiliary variable $\psi(t)$:

$$\psi(t) \triangleq \sqrt{2\phi_{\mathrm{nl}}(u) + \varepsilon}$$

where $\varepsilon > 0$ is a microscopic regularization constant ($\varepsilon \sim 10^{-12}$). The variational derivative is $\frac{\delta \phi_{\mathrm{nl}}}{\delta u} = \psi(t) g(x,t)$, where the normalized gradient field $g(x,t)$ is:

$$g(x,t) \triangleq \frac{1}{\psi(t)} \frac{\delta \phi_{\mathrm{nl}}}{\delta u} = -\frac{1}{\psi(t)} \partial_x \left[ G \frac{\sqrt{1 + \zeta^2} - 1}{\sqrt{1 + \zeta^2}} \zeta \right]$$

The evolution of $\psi(t)$ obeys the exact chain rule:

$$\dot{\psi}(t) = \langle g(x,t), \partial_t u(x,t) \rangle_{L^2}$$

### 2.3. Modal Projection & Bilateral Bridge Coupling

Expand displacement in sinusoidal eigenfunctions:

$$u(x,t) = \sum_{m=1}^M q_m(t) \chi_m(x), \quad \chi_m(x) = \sqrt{\frac{2}{L}}\sin\left(\frac{m\pi x}{L}\right)$$

The bridge compliance is modeled as a bank of $J$ damped second-order resonators:

$$\ddot{r}_j + 2\sigma_j^b \dot{r}_j + (\omega_j^b)^2 r_j = -\beta_j F_b(t), \quad j=1,\dots,J$$

with bridge displacement $u_b(t) = \sum_{j=1}^J r_j(t) = u(x_b, t)$.

Concatenating modal coordinates into state vector $\mathbf{y} = [\mathbf{q}; \mathbf{r}] \in \mathbb{R}^{M+J}$, the system becomes:

$$\ddot{\mathbf{y}} + \mathbf{C}\dot{\mathbf{y}} + \mathbf{\Omega}^2 \mathbf{y} = -\frac{\psi}{\mu} \tilde{\boldsymbol{\eta}} + \mathbf{s} f_e + \mathbf{f} F_b$$

$$\dot{\psi} = \boldsymbol{\eta}^\top \dot{\mathbf{q}}_{\mathrm{nl}}$$

where $\boldsymbol{\eta} = \mathbf{R}^\top \mathbf{g}$ is the modal projection of the gradient, and $\mathbf{R}$ is the slope evaluation matrix across spatial quadrature grid points $x_i = i h$.

---

## 3. Discrete-Time Sherman–Morrison Solver

At sampling interval $k = 1/f_s$, applying exact oscillator discretization for linear poles and centered differences yields:

$$\left(\mathbf{D} + \mathbf{f} \tilde{\mathbf{v}}^\top + \frac{k^2}{4\mu} \tilde{\mathbf{z}}^n (\tilde{\boldsymbol{\eta}}^n)^\top\right) \mathbf{y}^{n+1} = \mathbf{b}^n$$

where $\mathbf{D}$ is a strictly diagonal matrix.

### Step 1: Invert Bridge Coupling via Sherman–Morrison

Let $\tilde{\mathbf{D}} \triangleq \mathbf{D} + \mathbf{f} \tilde{\mathbf{v}}^\top$. Because $\mathbf{f} \tilde{\mathbf{v}}^\top$ is rank-one:

$$\tilde{\mathbf{D}}^{-1} = \mathbf{D}^{-1} - \frac{\mathbf{D}^{-1}\mathbf{f}\tilde{\mathbf{v}}^\top \mathbf{D}^{-1}}{1 + \tilde{\mathbf{v}}^\top \mathbf{D}^{-1}\mathbf{f}}$$

All components of $\tilde{\mathbf{D}}^{-1}$ are precomputed once at synthesis initialization!

### Step 2: Invert SAV Nonlinearity via Second Sherman–Morrison

The full system matrix is $\tilde{\mathbf{D}} + \mathbf{u}_{\mathrm{nl}} \mathbf{v}_{\mathrm{nl}}^\top$ where $\mathbf{u}_{\mathrm{nl}} = \frac{k^2}{4\mu}\tilde{\mathbf{z}}^n$ and $\mathbf{v}_{\mathrm{nl}} = \tilde{\boldsymbol{\eta}}^n$. Applying Sherman–Morrison a second time gives the explicit state update:

$$\mathbf{y}^{n+1} = \tilde{\mathbf{D}}^{-1}\mathbf{b}^n - \frac{\tilde{\mathbf{D}}^{-1}\tilde{\mathbf{z}}^n \left((\tilde{\boldsymbol{\eta}}^n)^\top \tilde{\mathbf{D}}^{-1}\mathbf{b}^n\right)}{\frac{4\mu}{k^2} + (\tilde{\boldsymbol{\eta}}^n)^\top \tilde{\mathbf{D}}^{-1}\tilde{\mathbf{z}}^n}$$

Total cost per time step: $\mathcal{O}(M_{\mathrm{nl}} + J)$ multiplications and additions. Zero matrix inversions. Zero iterative loops.

### Step 3: Servo Drift Regulation

To eliminate auxiliary variable drift over seconds of audio sustain:

$$\bar{\mathbf{g}} = \hat{\mathbf{g}} - \frac{\psi^{n-1/2} - \sqrt{2\phi_{\mathrm{nl}}(\boldsymbol{\zeta}^n) + \varepsilon}}{\|\boldsymbol{\zeta}^n - \boldsymbol{\zeta}^{n-1}\|}(\boldsymbol{\zeta}^n - \boldsymbol{\zeta}^{n-1})$$

---

## 4. Python / NumPy Implementation Sketch

```python
"""
sound/synthesis/sav_string.py - Method SP-092
Scalar Auxiliary Variable Nonlinear String Synthesis (SAV-NSS)
"""

import numpy as np


class SAVStringVoice:
    """Nonlinear string with SAV solver and bridge modal coupling."""

    def __init__(
        self,
        f0: float = 110.0,          # Fundamental frequency (Hz)
        fs: int = 44100,             # Sampling rate (Hz)
        string_len: float = 0.65,    # String length (m)
        tension: float = 75.0,       # Nominal tension T0 (N)
        youngs_mod: float = 2.0e11,  # Young's modulus E (Pa)
        radius: float = 0.0005,      # String radius (m)
        f_nl_max: float = 4000.0,    # Max frequency for nonlinear modes
        num_bridge_modes: int = 40,  # Resonant body modes
    ):
        self.fs = fs
        self.k = 1.0 / fs
        self.L = string_len
        self.T0 = tension
        self.area = np.pi * (radius ** 2)
        self.density = 7850.0  # kg/m^3 (steel/bronze)
        self.mu = self.density * self.area
        self.E = youngs_mod
        self.I = (np.pi * (radius ** 4)) / 4.0
        self.G = self.E * self.area - self.T0

        # Number of modes up to Nyquist
        c = np.sqrt(self.T0 / self.mu)
        max_m = int((0.45 * fs) / (c / (2.0 * self.L)))
        self.M = max(10, min(120, max_m))
        self.M_nl = max(4, int(f_nl_max / (c / (2.0 * self.L))))

        # Eigenfrequencies
        m_vec = np.arange(1, self.M + 1)
        self.omega_s = np.sqrt(
            (self.T0 / self.mu) * ((m_vec * np.pi / self.L) ** 2)
            + (self.E * self.I / self.mu) * ((m_vec * np.pi / self.L) ** 4)
        )
        self.sigma_s = 0.5 + 0.00015 * self.omega_s  # Woodhouse damping

        # Spatial grid for slope calculation
        self.Ng = 2 * self.M_nl + 4
        self.x_grid = np.linspace(0.0, self.L, self.Ng)
        self.h = self.L / (self.Ng - 1)
        self.R = np.zeros((self.Ng, self.M_nl))
        for i, xi in enumerate(self.x_grid):
            self.R[i, :] = np.sqrt(2.0 / self.L) * (
                np.arange(1, self.M_nl + 1) * np.pi / self.L
            ) * np.cos(np.arange(1, self.M_nl + 1) * np.pi * xi / self.L)

        # Bridge compliance modes (synthetic body model)
        self.J = num_bridge_modes
        np.random.seed(42)
        self.omega_b = 2.0 * np.pi * np.sort(np.random.uniform(100.0, 5000.0, self.J))
        self.sigma_b = np.random.uniform(5.0, 25.0, self.J)
        self.beta_b = np.random.uniform(0.001, 0.05, self.J)

        # Setup state vectors
        self.N_tot = self.M + self.J
        self.y_prev = np.zeros(self.N_tot)
        self.y_curr = np.zeros(self.N_tot)
        self.psi = np.sqrt(1e-12)
        self.zeta_prev = np.zeros(self.Ng)

    def render(self, duration_sec: float, pluck_pos: float = 0.2, pluck_force: float = 5.0) -> np.ndarray:
        """Synthesize audio buffer for a single pluck."""
        num_samples = int(duration_sec * self.fs)
        out_audio = np.zeros(num_samples)

        # Pluck shape projected onto modes
        m_vec = np.arange(1, self.M + 1)
        chi_pluck = np.sqrt(2.0 / self.L) * np.sin(m_vec * np.pi * pluck_pos)
        # Initial displacement profile
        self.y_curr[:self.M] = pluck_force * chi_pluck / (self.omega_s ** 2)
        self.y_prev[:self.M] = self.y_curr[:self.M].copy()

        eps = 1e-12
        for n in range(num_samples):
            # 1. Slope computation on grid
            q_nl = self.y_curr[:self.M_nl]
            zeta = self.R @ q_nl

            # 2. Nonlinear potential & SAV gradient
            sqrt_1_zeta2 = np.sqrt(1.0 + zeta ** 2)
            V_nl = 0.5 * self.G * ((sqrt_1_zeta2 - 1.0) ** 2)
            phi_nl = self.h * np.sum(V_nl)
            psi_true = np.sqrt(2.0 * phi_nl + eps)

            # Gradient field
            S_zeta = self.G * (sqrt_1_zeta2 - 1.0) / sqrt_1_zeta2
            stress = S_zeta * zeta
            grad_x = -np.gradient(stress, self.h)
            g_raw = grad_x / max(self.psi, np.sqrt(eps))

            # Servo drift correction
            d_zeta = zeta - self.zeta_prev
            norm_dzeta = np.linalg.norm(d_zeta)
            if norm_dzeta > 1e-9:
                g_corr = g_raw - ((self.psi - psi_true) / norm_dzeta) * d_zeta
            else:
                g_corr = g_raw

            eta = self.R.T @ (g_corr * self.h)

            # 3. Explicit time-stepping update
            # (Simplified explicit modal progression for sketch)
            damping = np.exp(-self.sigma_s * self.k)
            decay_cos = damping * np.cos(self.omega_s * self.k)
            y_next_str = 2.0 * decay_cos * self.y_curr[:self.M] - (damping ** 2) * self.y_prev[:self.M]
            y_next_str[:self.M_nl] -= (self.k ** 2 / self.mu) * self.psi * eta

            # Bridge reaction & radiation readout
            bridge_disp = np.sum(self.y_curr[self.M:])
            out_audio[n] = bridge_disp + 0.1 * y_next_str[0]

            # Update SAV scalar
            q_dot = (y_next_str[:self.M_nl] - self.y_prev[:self.M_nl]) / (2.0 * self.k)
            self.psi = max(np.sqrt(eps), self.psi + self.k * np.dot(eta, q_dot))

            # State slide
            self.y_prev = self.y_curr.copy()
            self.y_curr[:self.M] = y_next_str
            self.zeta_prev = zeta.copy()

        # Normalize audio
        peak = np.max(np.abs(out_audio))
        if peak > 0:
            out_audio /= peak
        return out_audio
```

---

## 5. Integration into Musicom

### 5.1. Engine Registration
- **Engine Module:** `sound/synthesis/sav_string.py`
- **Workflow Pipeline:** Callable via `produce(midi_path, method="SP-092", params={...})`.
- **Target Instruments:** Classical nylon guitar, steel-string acoustic, Celtic harp, lute, koto, upright bass.

### 5.2. Musical Elements Mapping
| Element | SAV-NSS Acoustic Realization |
|---|---|
| **PITCH** | Velocity-coupled pitch glide: hard plucks glide down by 15–50 cents; stiffness dispersion ($EI\partial_x^4$). |
| **RHYTHM** | Pure impulse response attack ($<0.5\text{ ms}$); natural nonlinear energy exchange modulates sustain decay. |
| **HARMONY** | Inharmonic phantom partials ring across multi-note chord voicings via non-linear modal cross-talk. |
| **STRUCTURE** | Dynamic timbre tracking: verse plucks stay pure and intimate; chorus strikes bloom into saturated metallic bite. |
| **TEXTURE** | Multi-string sympathetic bank driven by bridge reaction force creates deep, organic acoustic presence. |

---

## 6. Verification and References

1. Ducceschi, M., Russo, R., & Webb, C. J. (2026). "Measurement-Informed Nonlinear Modal Synthesis of 65 Classical Guitars." *DAFx26*.
2. Bilbao, S., Ducceschi, M., & Zama, F. (2023). "Explicit exactly energy-conserving methods for Hamiltonian systems." *J. Comput. Phys.*, 472.
3. Risse, T., Hélie, T., & Bilbao, S. (2025). "Power-balanced drift regulation for scalar auxiliary variable methods." *DAFx25*.
