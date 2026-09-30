# Volterra Series Synthesis (VSS) — Sound Method SP-100

## Overview

**Volterra Series Synthesis (VSS)** uses the Volterra series expansion — a Taylor series with memory — to model and generate nonlinear audio transformations in a mathematically rigorous framework. It is the most general representation of an analytic, fading-memory nonlinear system, generalizing convolution (linear system theory) to multi-order nonlinear interactions with delay.

VSS operates as a post-process or inline effects module on rendered audio buffers. It transforms UnitMatrix voice renders via parallel multidimensional convolutions (Volterra kernels), producing harmonic/inharmonic intermodulation, saturation, spectral enrichment, and cross-voice nonlinear coupling.

## Layer

**absolute** — sound production (post-processing / DSP). Candidate code path: `sound/effects/volterra_synthesis.py`.

## Source

- Araujo-Simon, J. (2023). "Compositional nonlinear audio signal processing with Volterra series." arXiv:2308.07229.
- Schetzen, M. (1980/2006). *The Volterra and Wiener Theories of Nonlinear Systems*. Krieger / Wiley.
- Rugh, W. J. (1981). *Nonlinear System Theory: The Volterra/Wiener Approach*. Johns Hopkins.
- Orcioni, S. et al. (2018). "Identification of Volterra Models of Tube Audio Devices Using Multiple Tone Excitation." *J. Audio Eng. Soc.*
- Bussgang, J. J., Ehrman, L. & Graham, J. W. (1974). "Analysis of nonlinear systems with multiple inputs." *Proc. IEEE* 62(8), 1088–1119.
- Marmarelis, V. Z. (1993). "Identification of nonlinear biological systems using Laguerre expansions of kernels." *Annals of Biomedical Engineering* 21(6), 573–589.

## Technical Mechanics

### 1. Continuous-Time Volterra Series

The output $y(t)$ of a nonlinear system with input $x(t)$ is:

$$y(t) = h_0 + \int_{-\infty}^{\infty} h_1(\tau_1) x(t-\tau_1) d\tau_1$$
$$+ \iint_{-\infty}^{\infty} h_2(\tau_1,\tau_2) x(t-\tau_1) x(t-\tau_2) d\tau_1 d\tau_2$$
$$+ \iiint_{-\infty}^{\infty} h_3(\tau_1,\tau_2,\tau_3) x(t-\tau_1) x(t-\tau_2) x(t-\tau_3) d\tau_1 d\tau_2 d\tau_3$$
$$+ \cdots$$

where $h_p(\tau_1,\ldots,\tau_p)$ is the **$p$-th order Volterra kernel**.

### 2. Discrete-Time Form (Causal, Finite Memory M)

$$y[n] = h_0 + \sum_{m_1=0}^{M-1} h_1[m_1] x[n-m_1] + \sum_{m_1=0}^{M-1} \sum_{m_2=0}^{M-1} h_2[m_1,m_2] x[n-m_1] x[n-m_2]$$
$$+ \sum_{m_1=0}^{M-1} \sum_{m_2=0}^{M-1} \sum_{m_3=0}^{M-1} h_3[m_1,m_2,m_3] x[n-m_1] x[n-m_2] x[n-m_3] + \cdots$$

### 3. Symmetric Kernels

Without loss of generality, kernels are assumed symmetric under index permutation. This reduces the count from $M^p$ to $\binom{M+p-1}{p}$.

### 4. Frequency-Domain Analysis

$$Y(f) = H_1(f)X(f) + \sum_{f_1+f_2=f} H_2(f_1,f_2)X(f_1)X(f_2) + \sum_{f_1+f_2+f_3=f} H_3(f_1,f_2,f_3)X(f_1)X(f_2)X(f_3) + \cdots$$

- **2nd-order kernels**: sum/difference frequencies $f_1\pm f_2$ (intermodulation, subharmonics)
- **3rd-order kernels**: triple-beat frequencies $f_1\pm f_2\pm f_3$ (tube saturation, compression)

### 5. Pruned Kernel Structures for Practical Use

| Structure | # Coefficients | Cost/sample |
|---|---|---|
| Full symmetric $(P=3, M=64)$ | $\binom{64+3}{3} \approx 45,760$ | $\mathcal{O}(M^P)$ |
| Diagonal-only $(P=3, M=64)$ | $3\cdot 64 = 192$ | $\mathcal{O}(P\cdot M)$ |
| Laguerre-pruned $(P=3, L=5)$ | $L^P = 125$ | $\mathcal{O}(P\cdot L)$ |
| Parallel-trilinear $(P=3, K=10, M=64)$ | $3\cdot 10\cdot 64 = 1,920$ | $\mathcal{O}(P\cdot K\cdot M)$ |

The **Laguerre expansion** projects each kernel onto $L$ orthonormal Laguerre basis functions $\ell_j[m]$:

$$h_p[m_1,\ldots,m_p] \approx \sum_{j_1=1}^{L}\cdots\sum_{j_p=1}^{L} c_p(j_1,\ldots,j_p)\, \ell_{j_1}[m_1]\cdots\ell_{j_p}[m_p]$$

The Laguerre filter outputs $L_j[n] = \sum_m \ell_j[m] x[n-m]$ are computed by cascaded first-order IIR filters ($\mathcal{O}(L)$ per sample total). The Volterra output then becomes:

$$y[n] \approx \sum_{p=1}^{P} \sum_{j_1=1}^{L}\cdots\sum_{j_p=1}^{L} c_p(j_1,\ldots,j_p) \prod_{q=1}^{p} L_{j_q}[n]$$

### 6. Diagonal (Memoryless) + Banded Structure

The simplest useful structure: the diagonal of each kernel ($\tau_1=\tau_2=\cdots=\tau_p$) corresponds to a pure power-law waveshaper with per-tap filtering:

$$y[n] = \sum_{m=0}^{M-1} \big( h_1[m] x[n-m] + h_2[m] x[n-m]^2 + h_3[m] x[n-m]^3 + \cdots \big)$$

This is a **parallel Hammerstein model** — each delay tap feeds its own polynomial, and the results are summed. Adding a band of width $W$ around the diagonal captures the most significant intermodulation cross-terms without full $M^p$ cost.

## Python / NumPy Implementation

```python
import numpy as np

class VolterraSeriesSynthesis:
    """
    Volterra Series Synthesis (VSS) — SP-100.
    
    Applies a P-th order Volterra series with Laguerre basis pruning
    as a post-process on rendered audio buffers.
    """
    
    def __init__(self, sr=44100):
        self.sr = sr
        self._laguerre_filters = None  # (L,) list of filter state per Laguerre basis
        self._c = None                  # kernel coefficients, nested lists per order
    
    def design_laguerre_basis(self, L=5, alpha=0.5):
        """
        Design L Laguerre basis functions as cascaded first-order IIR filters.
        
        Laguerre function (z-domain): L_j(z) = sqrt(1-alpha^2) * (z^{-1} - alpha)^j / (1 - alpha z^{-1})^{j+1}
        Implemented as cascaded first-order sections for O(L) per sample.
        """
        b0 = np.sqrt(1.0 - alpha*alpha)
        # State per Laguerre channel: (1,) for first-order
        self._laguerre_filters = {
            'alpha': alpha,
            'b0': b0,
            'state': np.zeros(L)
        }
        return self
    
    def set_kernel_coefficients(self, c_list):
        """
        Set kernel coefficients from a nested coefficient list.
        
        c_list[p-1] = array of shape (L^p,) for order p.
        For P=3, L=5: c_list[0] shape (5,), c_list[1] shape (25,), c_list[2] shape (125,)
        """
        self._c = c_list
        return self
    
    def _compute_laguerre_outputs(self, x):
        """
        Compute L Laguerre filter outputs for one sample.
        Cascaded first-order IIR: each Laguerre channel = single-pole section.
        """
        L = len(self._laguerre_filters['state'])
        alpha = self._laguerre_filters['alpha']
        b0 = self._laguerre_filters['b0']
        s = self._laguerre_filters['state']
        
        # L_0 (first channel)
        out = np.zeros(L)
        s0 = s[0]
        out[0] = b0 * x + alpha * s0
        s[0] = out[0] - alpha * x
        # Equivalent to: s[0] = alpha * s[0] + b0 * x - alpha * (b0 * x + alpha * s0)
        # Simplified: s[0] = alpha * s[0] - alpha * b0 * x + b0 * x
        s[0] = alpha * s0 + b0 * x - alpha * out[0]
        
        # Higher orders
        for j in range(1, L):
            s_j = s[j]
            # L_j[n] = (z^{-1} - alpha) / (1 - alpha z^{-1}) * L_{j-1}[n]
            out[j] = s_j + alpha * out[j-1]
            s[j] = out[j-1] - alpha * out[j]
        
        self._laguerre_filters['state'] = s
        return out
    
    def process_sample(self, x_n):
        """Process one audio sample through the Volterra series."""
        L = self._compute_laguerre_outputs(x_n)
        y = 0.0
        
        # Order 1 (linear): L_0 * c_0
        y += np.dot(L, self._c[0])
        
        # Order 2 (quadratic): sum over all L_i * L_j * c_ij
        if len(self._c) > 1:
            idx = 0
            for i in range(len(L)):
                for j in range(i, len(L)):
                    w = L[i] * L[j]
                    if i != j:
                        w *= 2.0  # symmetry: h2(i,j) = h2(j,i)
                    y += w * self._c[1][idx]
                    idx += 1
        
        # Order 3 (cubic): sum over L_i * L_j * L_k * c_ijk
        if len(self._c) > 2:
            idx = 0
            for i in range(len(L)):
                for j in range(i, len(L)):
                    for k in range(j, len(L)):
                        w = L[i] * L[j] * L[k]
                        # Symmetry factor: count permutations
                        perm = 1
                        if i == j == k:
                            perm = 1
                        elif i == j or j == k or i == k:
                            perm = 3
                        else:
                            perm = 6
                        y += w * perm * self._c[2][idx]
                        idx += 1
        
        return y
    
    def process_buffer(self, audio_in):
        """Process entire audio buffer through the Volterra series."""
        N = len(audio_in)
        out = np.zeros(N)
        # Reset Laguerre filter states
        if self._laguerre_filters is not None:
            self._laguerre_filters['state'] = np.zeros_like(self._laguerre_filters['state'])
        
        for n in range(N):
            out[n] = self.process_sample(audio_in[n])
        
        return out
    
    def render(self, audio_buffer, params=None):
        """
        Render audio through VSS post-process.
        
        Parameters
        ----------
        audio_buffer : np.ndarray (N,) or (N, C)
            Input audio buffer (mono or multi-channel).
        params : dict or None
            Override parameters: kernel_structure, h1_coeffs, h2_magnitude, 
            h3_magnitude, laguerre_order, laguerre_pole, kernel_seed.
        
        Returns
        -------
        np.ndarray : Processed audio buffer, same shape as input.
        """
        if params is not None:
            self._apply_params(params)
        
        if audio_buffer.ndim == 1:
            return self.process_buffer(audio_buffer)
        else:
            # Multi-channel: process each channel independently
            out = np.zeros_like(audio_buffer)
            for c in range(audio_buffer.shape[1]):
                out[:, c] = self.process_buffer(audio_buffer[:, c])
            return out
    
    def _apply_params(self, params):
        """Apply parameter overrides from section/cell configuration."""
        L = params.get('laguerre_order', 5)
        alpha = params.get('laguerre_pole', 0.5)
        self.design_laguerre_basis(L, alpha)
        
        # Build kernels from energy controls or explicit coefficients
        if 'c_list' in params:
            self.set_kernel_coefficients(params['c_list'])
        else:
            # Design kernels from magnitude knobs
            h1_mag = params.get('h1_magnitude', 1.0)
            h2_mag = params.get('h2_magnitude', 0.1)
            h3_mag = params.get('h3_magnitude', 0.0)
            seed = params.get('kernel_seed', 42)
            rng = np.random.RandomState(seed)
            
            # Random orthogonalized kernels
            c1 = h1_mag * rng.randn(L) * 0.1
            
            n2 = L * (L + 1) // 2
            c2 = h2_mag * rng.randn(n2) * 0.05
            
            n3 = L * (L + 1) * (L + 2) // 6
            c3 = h3_mag * rng.randn(n3) * 0.02
            
            self.set_kernel_coefficients([c1, c2, c3])


# =====================================================================
# Utility: Design targeted Volterra kernels for musical effects
# =====================================================================

def design_tube_warmth_kernel(L=5, alpha=0.5, drive=0.3):
    """
    Design a mild tube-warmth kernel: 
    - Strong linear pass-through (h1 ≈ 1)
    - Moderate second-order (even harmonics)
    - Weak third-order (odd harmonics)
    
    Returns VolterraSeriesSynthesis instance ready for rendering.
    """
    vss = VolterraSeriesSynthesis()
    vss.design_laguerre_basis(L, alpha)
    
    rng = np.random.RandomState(0)
    c1 = np.zeros(L)
    c1[0] = 1.0                     # Linear pass-through (dominant)
    c1[1:] = 0.05 * rng.randn(L-1)  # Mild spectral shaping
    
    n2 = L * (L + 1) // 2
    c2 = drive * 0.3 * rng.randn(n2)  # Even-harmonic intermodulation
    c2[0] *= 0.5                       # Don't over-saturate DC
    
    n3 = L * (L + 1) * (L + 2) // 6
    c3 = drive * 0.1 * rng.randn(n3)   # Weak odd-harmonic
    
    vss.set_kernel_coefficients([c1, c2, c3])
    return vss


def design_intermodulation_texture(L=5, alpha=0.8, density=0.5):
    """
    Design a dense intermodulation texture kernel.
    
    High Laguerre pole (alpha=0.8) = long memory, smeared intermodulation.
    High density = many off-diagonal cross-terms active.
    Produces diffuse, evolving spectral fog from any input.
    """
    vss = VolterraSeriesSynthesis()
    vss.design_laguerre_basis(L, alpha)
    
    rng = np.random.RandomState(1)
    n2 = L * (L + 1) // 2
    n3 = L * (L + 1) * (L + 2) // 6
    
    # Sparse random kernels: only density fraction of coefficients non-zero
    mask2 = rng.uniform(size=n2) < density
    mask3 = rng.uniform(size=n3) < density
    
    c2 = mask2.astype(float) * rng.randn(n2) * 0.2
    c3 = mask3.astype(float) * rng.randn(n3) * 0.1
    
    # Weak linear (the texture dominates)
    c1 = np.zeros(L)
    c1[0] = 0.3
    
    vss.set_kernel_coefficients([c1, c2, c3])
    return vss


def design_harmonic_enhancer(harmonic=2, L=5, alpha=0.3, strength=0.5):
    """
    Design a kernel that emphasizes a specific harmonic.
    
    For harmonic=2 (octave doubling): set h2 diagonal peak at the 
    Laguerre index corresponding to the pitch period.
    This creates a targeted second-harmonic generator.
    """
    vss = VolterraSeriesSynthesis()
    vss.design_laguerre_basis(L, alpha)
    
    rng = np.random.RandomState(harmonic)
    c1 = np.zeros(L)
    c1[0] = 1.0
    
    n2 = L * (L + 1) // 2
    c2 = np.zeros(n2)
    # Place a strong diagonal coefficient at the Laguerre channel 
    # that captures the harmonic's delay
    diag_idx = min(harmonic - 1, L - 1)
    c2[diag_idx * (diag_idx + 1) // 2 + diag_idx] = strength
    
    c3 = np.zeros(L * (L + 1) * (L + 2) // 6)
    
    vss.set_kernel_coefficients([c1, c2, c3])
    return vss
```

## Musical Elements Framework

**PITCH**: Volterra kernels act on the waveform directly. $h_1$ is an EQ (boosts/cuts registers). $h_2$ generates sum/difference frequencies — two input pitches produce intermodulation at $f_1\pm f_2$. $h_3$ generates triple-beat intermodulation for odd/even harmonic control. Kernels are pitch-independent — consistent spectral coloring across all pitches.

**RHYTHM**: Largely transparent — timing of onsets passes through unchanged. Nonlinear terms introduce amplitude-dependent phase shifts and transient intermodulation: sharp attacks through 3rd-order kernel generate trailing intermodulation bursts (exciter effect). Laguerre pole $\alpha$ controls rhythmic smear (low = crisp, high = diffuse).

**HARMONY**: Intermodulation between simultaneous pitches creates emergent harmonic content. A dyad $(f_1, f_2)$ through 2nd-order kernel produces $f_1+f_2$ and $|f_1-f_2|$ — the latter can be subharmonic. Different chords produce qualitatively different intermodulation spectra, making VSS an adaptive harmonizer: output harmony is a nonlinear function of input harmony.

**STRUCTURE**: Kernel coefficients, memory length $M$, Laguerre pole $\alpha$, and kernel structure are all time-varying per section. Each section gets its own VSS patch. Section transitions interpolate coefficients. Per-sample cost is constant regardless of section complexity.

**TEXTURE**: Sparse kernel → targeted harmonic enhancement. Dense kernel → intermodulation fog approaching noise at high nonlinearity. Kernel energy ratio $\|h_2\|/\|h_1\|$ is a one-knob texture dial. Laguerre pole $\alpha$ controls texture smoothing (short $\alpha$ = gritty/instant, long $\alpha$ = washy/smeared).

## UnitMatrix Integration

**Voices**: Each voice $v$ is rendered independently (via FluidSynth or other SP method), then VSS is applied per-voice or to the master sum. Per-voice VSS enables voice-specific nonlinear character. Master-bus VSS creates cross-voice intermodulation — the unique contribution: **inter-voice nonlinear coupling** without explicit routing.

**Sections**: Each section carries its own VSS parameter set:
- `kernel_structure`: "diagonal", "full", "laguerre", "hammerstein"
- `h1_coeffs`: $M$-length linear FIR
- `h2_magnitude`, `h3_magnitude`: scalar energy controls
- `laguerre_pole` $\alpha \in [0,1)$
- `laguerre_order` $L \in [3, 20]$

**Workflow**:
1. UnitMatrixComposer → MIDI (symbolic, per-voice)
2. `produce(method="SP-001")` → Audio via FluidSynth
3. `produce(method="SP-100")` → VSS post-process on buffer(s)
4. Output: enriched buffer with intermodulation harmonics, saturation, spectral enhancement

## Pitfalls

1. **Computational cost**: Full 3rd-order kernel with $M=64$ requires 45,760 coefficients — use Laguerre pruning ($L=5$ → 125 coefficients) for production.
2. **Stability**: Feedforward VSS is unconditionally stable. Feedback loop VSS may diverge — use energy bounding.
3. **Kernel identification ill-conditioning**: Ridge/LASSO regularization essential.
4. **Phase distortion**: Multi-order kernels introduce non-intuitive phase shifts. Creative use: ignore phase, use magnitude-only design.
5. **Laguerre pole sensitivity**: $\alpha \in [0.3, 0.9]$ typical; $\alpha=0.5$ recommended default.
6. **No feedback topology emulation**: Use WDF (SP-051) for circuit feedback loops.
7. **Post-process limitation**: Cannot fix poor MIDI — enriches existing content only.

## References

- Araujo-Simon, J. (2023). "Compositional nonlinear audio signal processing with Volterra series." arXiv:2308.07229.
- Schetzen, M. (1980). *The Volterra and Wiener Theories of Nonlinear Systems*. Krieger.
- Marmarelis, V. Z. (1993). "Identification of nonlinear biological systems using Laguerre expansions of kernels." *Annals of Biomedical Engineering* 21(6), 573–589.
- Orcioni, S. et al. (2018). "Identification of Volterra Models of Tube Audio Devices Using Multiple Tone Excitation." *J. Audio Eng. Soc.*
- Bussgang, J. J. et al. (1974). "Analysis of nonlinear systems with multiple inputs." *Proc. IEEE* 62(8), 1088–1119.
- Rugh, W. J. (1981). *Nonlinear System Theory: The Volterra/Wiener Approach*. Johns Hopkins.