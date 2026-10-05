# Coupled Resonant Filter Bank Synthesis (CRFBS) — SP-105

**Layer**: absolute — Sound Production (Synthesis Engines)
**Code path**: `sound/synthesis/coupled_resonator.py`
**Type**: Synthesis Engine — Nonlinear Modal Interaction via Coupled Resonators

## Overview

Coupled Resonant Filter Bank Synthesis (CRFBS) models nonlinear vibrating objects as a bank of N parallel Mathews-Smith complex-format IIR resonators that exchange vibrational energy through a controllable redistribution matrix. Each resonator represents one vibration mode (natural frequency ω_i, damping α_i). Energy flows between modes when a mode's instantaneous power exceeds a threshold, modeling nonlinear mode coupling.

**Reference**: Poirot, S., Kronland-Martinet, R., & Bilbao, S. (2023). "A Coupled Resonant Filter Bank for the Sound Synthesis of Nonlinear Sources." DAFx23, Copenhagen.

## Core Equations

### Mathews-Smith Complex Resonator (per mode)

$$z_i(n+1) = Z_i z_i(n) + u_i(n), \quad y_i(n) = \operatorname{Im}(z_i(n))$$

$$Z_i = e^{-\alpha_i/f_s} e^{j\omega_i/f_s}$$

Real/imaginary recurrence (coupled-form):
$$\begin{aligned}
x_i(n+1) &= X_i \tilde{x}_i(n) - Y_i \tilde{y}_i(n) + u_i(n) \\
y_i(n+1) &= Y_i \tilde{x}_i(n) + X_i \tilde{y}_i(n)
\end{aligned}$$

where:
$$X_i = e^{-\alpha_i/f_s}\cos(\omega_i/f_s), \quad Y_i = e^{-\alpha_i/f_s}\sin(\omega_i/f_s)$$

### Instantaneous Power

$$P_i(n) = \frac{|z_i(n)|^2}{2} = \frac12\bigl(x_i(n)^2 + y_i(n)^2\bigr)$$

### Energy Transfer (Modulus Scaling, Phase Preserved)

$$|z_i(n+1)| = \sqrt{|z_i(n)|^2 + 2T_i(n)} \; e^{-\alpha_i/f_s}$$

$$z_i(n+1) = \begin{cases}
\sqrt{2T_i(n)}\, Z_i + u_i(n), & z_i(n)=0 \\[4pt]
\sqrt{1 + 2T_i(n)/|z_i(n)|^2} \; Z_i z_i(n) + u_i(n), & \text{else}
\end{cases}$$

### Redistribution Matrix

$$\mathbf{t}(n) = \mathbf{M}\,[\mathbf{p}(n) - \boldsymbol{\tau}]_+$$

with $[\zeta]_+ = \tfrac12(\zeta + |\zeta|)$, $\mathbf{p}=[P_1,\dots,P_N]^\mathsf{T}$, and $\boldsymbol{\tau}=[\tau_1,\dots,\tau_N]^\mathsf{T}$.

### Matrix Coefficient Parametrization

$$M_{ij} = \eta \lambda \frac{a_{ij}}{\sum_i a_{ij}} - \lambda \delta_{ij}$$

- $\eta \in [0,1]$: transfer efficiency
- $\lambda \in [0,1]$: transfer rate per step
- $a_{ij} \geq 0$: redistribution weights from mode $j$ to $i$
- $\delta_{ij}$: Kronecker delta
- Column sum $\sum_i M_{ij} \leq 0$ ensures stability (no energy creation)

### Output

$$s(n) = \sum_{i=1}^{N} y_i(n)$$

## Python/NumPy Implementation Sketch

```python
import numpy as np

class CoupledResonatorBank:
    """
    Coupled Resonant Filter Bank Synthesis.
    
    Parameters
    ----------
    freqs : ndarray (N,) — mode natural frequencies in Hz
    dampings : ndarray (N,) — mode damping coefficients α_i
    thresholds : ndarray (N,) — energy transfer thresholds τ_i
    eta : float — transfer efficiency in [0, 1]
    lam : float — transfer rate per step in [0, 1]
    weights : ndarray (N, N) — redistribution weights a_{ij}
    fs : int — sample rate in Hz
    """
    def __init__(self, freqs, dampings, thresholds, eta, lam, weights, fs=48000):
        self.N = len(freqs)
        self.fs = fs
        self.eta = eta
        self.lam = lam
        
        # Per-mode rotation + damping
        self.X = np.exp(-dampings / fs) * np.cos(2*np.pi*freqs / fs)
        self.Y = np.exp(-dampings / fs) * np.sin(2*np.pi*freqs / fs)
        
        # Thresholds
        self.tau = np.asarray(thresholds)
        
        # Redistribution matrix M (N×N)
        self.a = np.asarray(weights, dtype=np.float64)
        col_sums = np.sum(self.a, axis=0, keepdims=True)
        col_sums = np.where(col_sums == 0, 1, col_sums)  # avoid div-by-zero
        self.M = eta * lam * self.a / col_sums
        np.fill_diagonal(self.M, self.M.diagonal() - lam)
        # Column sum = -lam*(1-eta) <= 0 guaranteed
        
        # State
        self.x = np.zeros(self.N)   # real parts
        self.y = np.zeros(self.N)   # imag parts (output)
    
    def _compute_transfer(self):
        """Compute T_i(n) from current power and matrix M."""
        p = 0.5 * (self.x**2 + self.y**2)          # power vector
        excess = np.maximum(p - self.tau, 0)        # positive part
        return self.M @ excess                      # transfer vector
    
    def process_sample(self, excitation):
        """
        Process one sample.
        
        excitation : ndarray (N,) — per-mode excitation u_i(n)
        returns : float — summed output s(n)
        """
        u = np.asarray(excitation, dtype=np.float64)
        
        # Compute energy transfer terms
        T = self._compute_transfer()
        
        # Modulus scaling factor per mode
        p = 0.5 * (self.x**2 + self.y**2)
        z_sq = self.x**2 + self.y**2
        scale = np.ones(self.N)
        
        # Modes with zero current state
        zero_mask = z_sq == 0
        scale[~zero_mask] = np.sqrt(np.maximum(
            1 + 2 * T[~zero_mask] / z_sq[~zero_mask], 0))
        
        # Special case for zero-state: sqrt(2T) * Z
        x_tilde = np.where(zero_mask, np.sqrt(np.maximum(2*T[zero_mask], 0)), scale * self.x)
        y_tilde = np.where(zero_mask, 0, scale * self.y)
        
        # Mathews-Smith recurrence
        x_new = self.X * x_tilde - self.Y * y_tilde + u
        y_new = self.Y * x_tilde + self.X * y_tilde
        
        self.x, self.y = x_new, y_new
        
        return np.sum(self.y)   # summed output

    def process_buffer(self, excitation_buffer):
        """Process a buffer of samples. excitation_buffer: (samples, N)."""
        T = excitation_buffer.shape[0]
        output = np.zeros(T)
        for n in range(T):
            output[n] = self.process_sample(excitation_buffer[n])
        return output
```

## Usage Example

```python
# 30-mode coupling bank for a struck plate sound
N = 30
freqs = 200 * (np.arange(N, dtype=float) + 1)**1.8   # inharmonic plate series
dampings = 0.5 + 5 * np.arange(N) / (N-1)            # increasing damping per mode
thresholds = 0.02 * np.ones(N)
eta, lam = 0.85, 0.5

# Nearest-neighbor coupling: modes exchange energy with adjacent modes
a = np.zeros((N, N))
for i in range(N):
    if i > 0:   a[i, i-1] = 0.5
    if i < N-1: a[i, i+1] = 0.5
    a[i, i] = 1.0

bank = CoupledResonatorBank(freqs, dampings, thresholds, eta, lam, a, fs=48000)

# Strike: impulse on first 5 modes
T = 48000  # 1 second at 48 kHz
excitation = np.zeros((T, N))
excitation[0, :5] = 1.0

output = bank.process_buffer(excitation)

# Optional: normalize and save
# import soundfile as sf
# output /= np.max(np.abs(output))
# sf.write("plate_strike.wav", output, 48000)
```

## Musical Elements Framework

| Element | Implementation |
|---------|---------------|
| **PITCH** | Mode frequencies ω_i define the harmonic/inharmonic spectrum. Inharmonic series (ω_i ∝ i^2) for metallic timbres. |
| **RHYTHM** | Excitation u_i(n) controls onset. Energy transfer creates delayed "aftershock" onsets. |
| **HARMONY** | Mode clusters = chord structures. Coupling topology determines harmonic grammar. |
| **STRUCTURE** | Section-level macro-form via swapping M_s, τ_s per section. ηλ is a one-knob form control. |
| **TEXTURE** | Density = count of active modes with P_i > τ_i. Dense coupling = spectral wash, sparse = clear tones. |

## UnitMatrix Integration

- **Voices (Rows)**: Each voice is an independent coupled resonator bank.
- **Sections (Columns)**: Each section defines a coupling regime (M, τ, η, λ).
- **Cells U_{v,s}**: `{mode_table: [(ω_i, α_i, τ_i)], coupling_matrix: a_{ij}, coupling_params: (η, λ), excitation: u(n)}`.
- Mapping: section → load (M, τ, η, λ) → run coupled resonator loop → sum N mode outputs → voice audio.

## References

1. Poirot, S., Kronland-Martinet, R., & Bilbao, S. (2023). "A Coupled Resonant Filter Bank for the Sound Synthesis of Nonlinear Sources." DAFx23.
2. Mathews, M. & Smith, J. O. "Methods for Synthesizing Very High Q Parametrically Well Behaved Two Pole Filters."
3. Skare, K. & Abel, S. (2019). Real-Time Modal Synthesis of Crash Cymbals with GPU-Accelerated Modal Filterbank.
4. Ducceschi, M. & Touzé, C. (2022). Modal Resolution of the Föppl-von Kármán System with Coupling Coefficients.