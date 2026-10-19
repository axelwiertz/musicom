# Method 120: Random Matrix Theory Composition (RMTC)

## Overview

- **ID**: 120
- **Name**: Random Matrix Theory Composition
- **Acronym**: RMTC
- **Paradigm**: Stochastic
- **Layer**: concrete
- **Line**: Generates composition parameters from eigenvalue statistics of random matrices (GOE/GUE/GSE): Wigner semicircle law drives pitch distribution; Wigner surmise (level repulsion) drives melodic intervals; Dyson-Mehta spectral rigidity drives chord voicing balance; Tracy-Widom extremes drive climax/range; ensemble-type switching drives macro-form.

## Mathematical Foundation

### Random Matrix Ensembles

The three classical invariant ensembles are defined by their joint eigenvalue distribution:

$$P_{\beta}(\lambda_1,\dots,\lambda_N) = \frac{1}{Z_N} \prod_{i<j} |\lambda_i - \lambda_j|^{\beta} \exp\left(-\frac{1}{2}\sum_{i=1}^N \lambda_i^2\right)$$

where:
- $\beta = 1$: **GOE** (Gaussian Orthogonal Ensemble) — real symmetric matrices, eigenvalues on $\mathbb{R}$
- $\beta = 2$: **GUE** (Gaussian Unitary Ensemble) — complex Hermitian matrices, eigenvalues on $\mathbb{R}$
- $\beta = 4$: **GSE** (Gaussian Symplectic Ensemble) — quaternion self-dual matrices, eigenvalues on $\mathbb{R}$ with double degeneracy

The parameter $\beta$ controls the strength of level repulsion: $P(\lambda_i \approx \lambda_j) \propto |\lambda_i - \lambda_j|^{\beta}$, so higher $\beta$ → stronger repulsion → wider spacing between successive eigenvalues.

### Wigner Semicircle Law — Pitch Distribution

For an $N \times N$ Wigner matrix with independent entries (zero mean, variance $\sigma^2 = 1/N$), the empirical spectral density converges almost surely to the semicircle law as $N \to \infty$:

$$\rho(\lambda) = \lim_{N\to\infty} \frac{1}{N} \sum_{i=1}^N \delta(\lambda - \lambda_i) = \frac{1}{2\pi} \sqrt{4 - \lambda^2}, \quad |\lambda| \le 2$$

**Musical mapping**: Eigenvalues $\lambda_i$ are scaled and quantized to MIDI pitch values. The semicircle density peaks at $\lambda = 0$ (tonic region) and vanishes at $\lambda = \pm 2$ (chromatic extremes):

$$p_{\text{MIDI}}(i) = \text{round}\left(p_0 + K \cdot \lambda_i\right)$$

where $p_0$ is the tonic MIDI note (e.g., 60 for C4) and $K$ is the scaling factor in semitones (typically $K \in [2, 5]$).

The cumulative distribution function of the semicircle law:

$$F(\lambda) = \frac{1}{2} + \frac{\lambda\sqrt{4-\lambda^2}}{4\pi} + \frac{1}{\pi}\arcsin\left(\frac{\lambda}{2}\right), \quad |\lambda| \le 2$$

enables inverse-transform sampling: for $u \sim U(0,1)$, solve $F(\lambda) = u$ for $\lambda$ to generate eigenvalues with the desired semicircle distribution.

### Wigner Surmise — Melodic Interval Distribution

The nearest-neighbor spacing distribution for the three ensembles (Wigner surmise):

$$P_{\beta}(s) = a_{\beta} \, s^{\beta} \, e^{-b_{\beta} s^2}$$

where:

| $\beta$ | Ensemble | $a_{\beta}$ | $b_{\beta}$ | Mean spacing | $P(s \to 0)$ |
|:---:|:---:|:---:|:---:|:---:|:---:|
| 1 | GOE | $\pi/2$ | $\pi/4$ | 1.0 | $\propto s$ |
| 2 | GUE | $32/\pi^2$ | $4/\pi$ | 1.0 | $\propto s^2$ |
| 4 | GSE | $2^{18}/(3^6\pi^3)$ | $64/(9\pi)$ | 1.0 | $\propto s^4$ |

Here $s_i = (\lambda_{i+1} - \lambda_i) / \Delta$ is the normalized spacing, and $\Delta$ is the local mean spacing.

**Musical mapping**: Each normalized gap $s_i$ maps to a melodic interval in semitones:

$$\text{interval}_i = \text{round}(s_i \cdot M)$$

where $M$ is the interval scaling factor (typically $M \in [3, 7]$). The key property is **level repulsion**: $P_{\beta}(s) \to 0$ as $s \to 0$, meaning the probability of a unison or zero-interval repetition is zero. This emerges naturally from the eigenvalue statistics — no explicit rule needed.

For comparison, the Poisson (integrable) spacing distribution is $P(s) = e^{-s}$, which has $P(0) = 1$ (maximal probability of zero spacings), corresponding to uncorrelated random intervals.

### Dyson-Mehta Spectral Rigidity — Chord Voicing

The $\Delta_3(L)$ statistic measures the variance of the number of eigenvalues in an interval of length $L$ (in units of mean spacing):

$$\Delta_3(L; \{\lambda_i\}) = \frac{1}{L} \min_{A,B} \int_{x}^{x+L} \bigl(N(\lambda) - A - B\lambda\bigr)^2 \, d\lambda$$

where $N(\lambda)$ is the eigenvalue counting function. The ensemble average for GOE:

$$\langle \Delta_3(L) \rangle_{\text{GOE}} = \frac{1}{\pi^2} \log L + 0.057 + \mathcal{O}(L^{-1}), \quad L \gg 1$$

For Poisson (uncorrelated) eigenvalues: $\langle \Delta_3(L) \rangle_{\text{Poisson}} = L/15$.

**Musical mapping**: Simultaneous eigenvalues from a single matrix sample define chord voicings. The spectral rigidity ensures that eigenvalues are *more evenly spaced* than random — this translates to balanced chord voicing with no collisions and no overly clustered intervals. For an $n$-voice chord at time $t$:

1. Sample a fresh $N \times N$ matrix from ensemble $\beta_s$ (section $s$'s ensemble)
2. Compute its $n$ smallest eigenvalues $\lambda_1 < \lambda_2 < \dots < \lambda_n$
3. Map $\lambda_i \to$ scale degree $d_i$ of voice $i$ via:
   $$d_i = \text{quantize}\big(p_0 + K_s \cdot \lambda_i, \; \text{scale}(s)\big)$$

The rigidity ensures $|d_i - d_j|$ is never too small (no 0- or 1-semitone voice collisions), and the mean spacing $\Delta$ automatically adjusts to the chord size.

### Tracy-Widom Law — Climax and Dynamic Range

The distribution of the largest eigenvalue $\lambda_{\max}$ of an $N \times N$ GOE matrix follows:

$$\lim_{N \to \infty} \mathbb{P}\left(N^{2/3}(\lambda_{\max} - 2) \le t\right) = F_1(t)$$

where $F_1$ is the Tracy-Widom distribution for $\beta = 1$ (for $F_2$, $F_4$ for GUE/GSE respectively). Key statistics:

| $\beta$ | Mean | Std Dev | Skewness |
|:---:|:---:|:---:|:---:|
| 1 (GOE) | $-1.21 N^{-2/3}$ | $1.27 N^{-2/3}$ | $0.224$ |
| 2 (GUE) | $-1.77 N^{-2/3}$ | $0.90 N^{-2/3}$ | $0.093$ |
| 4 (GSE) | $-2.31 N^{-2/3}$ | $0.73 N^{-2/3}$ | $0.050$ |

**Musical mapping**: The largest eigenvalue $\lambda_{\max}$ sets the registral climax of a section:

$$p_{\max}^{(\text{climax})} = p_0 + K_s \cdot \lambda_{\max}$$

The right tail of $F_{\beta}$ controls how rare extreme-high-register events are (GUE has a thinner tail than GOE → fewer extreme leaps). The spectral width $\lambda_{\max} - \lambda_{\min}$ determines the total registral range of the section.

### Dyson Brownian Motion — Section Transitions

The eigenvalues of a random matrix evolve under Dyson Brownian motion:

$$d\lambda_i = \frac{\beta}{2} \sum_{j \neq i} \frac{dt}{\lambda_i - \lambda_j} + dB_i$$

where $dB_i$ are independent Brownian motions. This provides a smooth interpolation between section boundaries: instead of a discontinuous jump from one matrix sample to the next, we can evolve the eigenvalues under DBM, creating smooth harmonic/melodic transitions.

## Python Implementation Sketch

```python
import numpy as np
from scipy import linalg, special
from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer, create_note_unit

# ── Ensemble sampling ────────────────────────────────────────────

def sample_goe(N):
    """Sample N×N GOE matrix (real symmetric)."""
    A = np.random.randn(N, N)
    H = (A + A.T) / np.sqrt(2 * N)   # variance = 1/N
    return H

def sample_gue(N):
    """Sample N×N GUE matrix (complex Hermitian)."""
    A = np.random.randn(N, N) + 1j * np.random.randn(N, N)
    H = (A + A.conj().T) / np.sqrt(4 * N)  # variance = 1/N
    return H

def sample_gse(N):
    """Sample N×N GSE matrix (quaternion self-dual) as 2N×2N real."""
    A = np.random.randn(N, N, 2, 2)  # quaternion entries
    H = np.zeros((2*N, 2*N))
    for i in range(N):
        for j in range(N):
            # 2×2 block: [a+id, -b+ic; b+ic, a-id]
            a, b, c, d = A[i, j, 0, 0], A[i, j, 0, 1], A[i, j, 1, 0], A[i, j, 1, 1]
            H[2*i:2*i+2, 2*j:2*j+2] = [[a+d, -b+c],
                                        [b+c,  a-d]]
    H = (H + H.T) / np.sqrt(8 * N)  # variance = 1/N
    return H

def eigenvalues(H, ensemble='GOE'):
    """Compute eigenvalues of the sampled matrix."""
    if ensemble == 'GOE':
        return linalg.eigh(H, turbo=True)[0]  # real symmetric
    elif ensemble == 'GUE':
        return linalg.eigh(H)[0]  # complex Hermitian
    elif ensemble == 'GSE':
        return linalg.eigh(H)[0]  # real symmetric (double-sized)

# ── Wigner Surmise PDF/CDF ──────────────────────────────────────

def wigner_surmise_pdf(s, beta=1):
    """Wigner surmise P_beta(s) for nearest-neighbor spacing."""
    if beta == 1:       # GOE
        return (np.pi * s / 2) * np.exp(-np.pi * s**2 / 4)
    elif beta == 2:     # GUE
        return (32 * s**2 / np.pi**2) * np.exp(-4 * s**2 / np.pi)
    elif beta == 4:     # GSE
        a, b = 2**18 / (3**6 * np.pi**3), 64 / (9 * np.pi)
        return a * s**4 * np.exp(-b * s**2)

def wigner_surmise_sample(n, beta=1, seed=None):
    """Sample n spacings from Wigner surmise via rejection sampling."""
    if seed is not None:
        np.random.seed(seed)
    samples = []
    while len(samples) < n:
        s = np.random.exponential(scale=1.0)  # proposal: exponential
        u = np.random.uniform()
        # Acceptance probability = P_beta(s) / (C * exp(-s))
        # where C >= max(P_beta(s)/exp(-s)) ≈ 1.2 for beta=1
        if u < wigner_surmise_pdf(s, beta) / (1.3 * np.exp(-s)):
            samples.append(s)
    return np.array(samples[:n])

# ── Pitch mapping ────────────────────────────────────────────────

def semicircle_cdf_inv(u):
    """Inverse CDF of Wigner semicircle law (numerical)."""
    # Solve F(lambda) = u for lambda in [-2, 2]
    # F(lambda) = 1/2 + lambda*sqrt(4-lambda^2)/(4*pi) + arcsin(lambda/2)/pi
    from scipy.optimize import brentq
    def F(x): return 0.5 + x*np.sqrt(4-x**2)/(4*np.pi) + np.arcsin(x/2)/np.pi
    # For extreme u near 0 or 1, clamp to [-1.999, 1.999] for stability
    return np.array([brentq(lambda x: F(x) - ui, -1.999, 1.999) for ui in u])

def map_eigenvalues_to_pitch(eigenvalues, tonic=60, scale_factor=4.0,
                               scale_degrees=None):
    """Map sorted eigenvalues to MIDI pitch values.
    
    Args:
        eigenvalues: sorted eigenvalue array
        tonic: MIDI pitch of tonic
        scale_factor: semitones per eigenvalue unit
        scale_degrees: optional list of valid scale degrees (e.g., [0,2,4,5,7,9,11])
    """
    # Normalize to zero mean, unit variance
    lam = (eigenvalues - np.mean(eigenvalues)) / np.std(eigenvalues)
    # Clip to semicircle support
    lam = np.clip(lam, -2.0, 2.0)
    # Scale to pitch range
    pitch_cont = tonic + scale_factor * lam
    if scale_degrees is not None:
        # Quantize to nearest scale degree within the current octave
        octave = np.floor(pitch_cont / 12) * 12
        chroma = np.round(pitch_cont % 12).astype(int)
        # Find nearest scale degree
        chroma_quant = np.array([min(scale_degrees, key=lambda d: abs(d - c))
                                  for c in chroma])
        return (octave + chroma_quant).astype(int)
    else:
        return np.round(pitch_cont).astype(int)

# ── Section parameter tuples ────────────────────────────────────

class RMTCSectionConfig:
    """Configuration for one section's RMT parameters."""
    def __init__(self, name, bars, ensemble='GOE', N=8, K=4.0, M=5.0,
                 scale_degrees=None):
        self.name = name
        self.bars = bars
        self.ensemble = ensemble        # 'GOE', 'GUE', 'GSE'
        self.N = N                       # matrix dimension
        self.K = K                       # pitch scaling (semitones per eigenvalue)
        self.M = M                       # interval scaling
        self.scale_degrees = scale_degrees  # None = chromatic

# ── Full composition pipeline ────────────────────────────────────

def compose_rmtc(sections, bpm=120, tonic=60, seed=42):
    """Full RMTC composition pipeline.
    
    Args:
        sections: list of RMTCSectionConfig
        bpm: tempo in BPM
        tonic: tonic MIDI note
        seed: random seed
        
    Returns:
        composer: UnitMatrixComposer with filled cells
    """
    np.random.seed(seed)
    
    ensemble_samplers = {
        'GOE': sample_goe,
        'GUE': sample_gue,
        'GSE': sample_gse,
    }
    
    V = len(sections)  # one voice per section config (or use multi-voice)
    
    composer = UnitMatrixComposer(bpm=bpm, ticks_per_beat=480, beats_per_bar=4)
    composer.create_matrix(num_voices=3, num_sections=len(sections))
    
    for v in range(3):
        composer.add_voice(f"Voice_{v}", program=0, channel=v)
    
    for s_idx, sec in enumerate(sections):
        composer.add_section(sec.name, bars=sec.bars)
        sec_ticks = sec.bars * 1920
        
        # Sample matrix for this section
        sampler = ensemble_samplers[sec.ensemble]
        H = sampler(sec.N)
        lam = eigenvalues(H, sec.ensemble)
        lam.sort()
        
        # Compute normalized spacings
        spacings = np.diff(lam) / np.mean(np.diff(lam))
        
        # Map eigenvalues to pitch for each voice
        for v in range(min(3, sec.N)):
            # Use v-th eigenvalue as voice seed
            lambda_v = lam[v % sec.N]
            pitch_seed = map_eigenvalues_to_pitch(
                np.array([lambda_v]), tonic, sec.K, sec.scale_degrees)[0]
            
            # Build interval contour from spacings
            contour = [pitch_seed]
            for s in spacings[:sec.bars * 4]:  # ~4 events per bar
                interval = int(round(s * sec.M))
                next_pitch = contour[-1] + interval
                # Clamp to MIDI range
                next_pitch = max(0, min(127, next_pitch))
                if abs(next_pitch - contour[-1]) <= 24:  # limit leaps
                    contour.append(next_pitch)
            
            # Create events
            events = []
            tick_per_event = sec_ticks // len(contour) if len(contour) > 0 else sec_ticks
            for i, p in enumerate(contour):
                start = i * tick_per_event
                end = start + tick_per_event // 2
                if end <= sec_ticks:
                    events.append(MusicEvent(
                        pitch=int(p),
                        volume=64,
                        start_tick=start,
                        end_tick=end
                    ))
            
            # Fill cell
            composer.fill_voice_section(v, s_idx,
                create_note_unit(contour[0] if contour else 60, sec_ticks))
    
    ok, msg = composer.validate()
    assert ok, f"Validation failed: {msg}"
    
    return composer
```

## Tracy-Widom CDF (numerical evaluation)

The Tracy-Widom distributions $F_{\beta}$ are given by the Fredholm determinant:

$$F_2(t) = \det(I - K_{\text{Airy}}|_{(t,\infty)})$$

where $K_{\text{Airy}}$ is the Airy kernel:

$$K_{\text{Airy}}(x,y) = \frac{\text{Ai}(x)\text{Ai}'(y) - \text{Ai}'(x)\text{Ai}(y)}{x - y}$$

and $F_1(t)^2 = F_2(t) \cdot \exp(-\int_t^{\infty} q(u) \, du)$ or via the Painlevé II connection:

$$F_1(t) = F_2(t)^{1/2} \exp\left(-\frac{1}{2}\int_t^{\infty} q(u) \, du\right)$$

where $q(u)$ solves $q'' = uq + 2q^3$ with $q(u) \sim \text{Ai}(u)$ as $u \to \infty$.

For practical implementation, pre-computed tables or the `tracy_widom` R package / scipy-based approximations give the quantiles.

## References

1. Wigner, E. P. (1955). "Characteristic vectors of bordered matrices with infinite dimensions." *Annals of Mathematics* 62(3), 548–564.
2. Dyson, F. J. (1962). "Statistical theory of the energy levels of complex systems." *Journal of Mathematical Physics* 3(1), 140–156.
3. Mehta, M. L. (2004). *Random Matrices* (3rd ed.). Elsevier/Academic Press.
4. Tracy, C. A. & Widom, H. (1994). "Level-spacing distributions and the Airy kernel." *Communications in Mathematical Physics* 159(1), 151–174.
5. Bohigas, O., Giannoni, M. J. & Schmit, C. (1984). "Characterization of chaotic quantum spectra and universality of level fluctuation laws." *Physical Review Letters* 52(1), 1–4.
6. Wigner, E. P. (1957). "Statistical properties of real symmetric matrices with many dimensions." *Canadian Journal of Mathematics* 9, 149–152.
7. Tao, T. (2012). *Topics in Random Matrix Theory*. Graduate Studies in Mathematics 132, AMS.

## Related Methods

- **002 Markov**: RMTC is a contrasting stochastic approach — eigenvalue statistics instead of transition matrices
- **048 RBMPD**: Brownian motion diffusion vs. eigenvalue repulsion — both continuous, different generative mechanisms
- **085 NMF-C**: Matrix factorization vs. matrix statistics — spectral-grounded counterparts
- **053 LFC**: Heavy-tailed distributions over intervals vs. Wigner-surmise distributions
- **051 SGLM**: Graph Laplacian eigenvalues (deterministic structure) vs. random matrix eigenvalues (universal statistics)
- **045 HPSEC**: Self-exciting point processes vs. eigenvalue-gap-driven processes
- **097 MaxEnt-C**: Maximum-entropy Potts models vs. random-matrix spectral models

## UnitMatrix Integration Summary

| Component | RMT Mapping | UnitMatrix Mapping |
|---|---|---|
| Ensemble type $\beta_s$ | Harmonic character | Per-section parameter |
| Matrix dimension $N_s$ | Vocabulary size / density | Section texture |
| Eigenvalues $\{\lambda_i\}$ | Pitch seeds, scale degrees | Cell pitch material |
| Wigner spacings $\{s_i\}$ | Melodic intervals | Per-voice contour |
| Spectral rigidity $\Delta_3$ | Chord voicing balance | Vertical voice coherence |
| Tracy-Widom $\lambda_{\max}$ | Climactic registral peak | Section macro-boundary |
| Dyson Brownian motion | Smooth section transitions | Section seam interpolation |