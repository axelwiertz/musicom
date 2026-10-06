# Method 107: Stochastic Differential Equation Composition (SDEC)

**Layer:** concrete
**Paradigm:** Nature-Led
**Acronym:** SDEC

## Overview

Generates music by simulating continuous-time stochastic differential equations (Itō SDEs) whose drift fields encode tonal gravity, voice-leading, and section structure, and whose diffusion fields encode creative uncertainty, ornamentation density, and texture. Each voice is a multi-dimensional SDE; voices are coupled through correlated noise and mutual drift terms that enforce harmonic coherence. The method generalizes 048 RBMPD (single reflected Brownian motion) to arbitrary state- and time-dependent drift/diffusion fields across all musical parameters.

## Mathematical Framework

### Core SDE

$$dX_t = \mu(X_t, t)\,dt + \sigma(X_t, t)\,dW_t$$

- $X_t \in \mathbb{R}^d$: musical state vector (pitch, log-duration, velocity, harmonic interval, metric phase)
- $\mu$: drift field (deterministic tendency — tonal gravity, voice-leading, form)
- $\sigma$: diffusion field (stochasticity — ornamentation, micro-timing, density)
- $W_t$: Wiener process (independent Brownian motion)

### Multi-Voice Coupling

$$dX_t^{(v)} = \mu_v(X_t, t)\,dt + \sum_{u} \sigma_{vu}(X_t^{(u)},t)\,dW_t^{(u)}$$

Noise correlation $\rho_{vw}$ controls ensemble texture: positive = parallel motion, negative = contrary, zero = independent.

### Drift-as-Potential-Gradient

$$\mu(x,t) = -\nabla \Phi(x,t)$$

The potential $\Phi$ can be:
- **Single-well**: $\Phi(x) = \frac{1}{2}\gamma(x-c)^2$ — Ornstein-Uhlenbeck, mean-reverting to tonic $c$
- **Multi-well**: $\Phi(x) = \sum_i w_i \exp(-(x-c_i)^2/2\ell_i^2)$ — multiple tonal centres with different depths (HOME > LIFT > TENSE > TURN)
- **Periodic**: $\Phi(x) = \frac{1}{2}\sin(12x)$ — 12 wells per octave for chromatic space
- **Time-dependent**: $\Phi(x,t)$ — section-wise changes in key, harmony, tension

### Integration (Euler-Maruyama)

$$X_{t+\Delta t} = X_t + \mu(X_t,t)\Delta t + \sigma(X_t,t) \sqrt{\Delta t}\, \xi,\quad \xi \sim \mathcal{N}(0,1)$$

### Fokker-Planck Density Evolution

$$\frac{\partial p}{\partial t} = -\frac{\partial}{\partial x}[\mu(x,t) p] + \frac{1}{2}\frac{\partial^2}{\partial x^2}[\sigma^2(x,t) p]$$

The time-dependent probability density $p(x,t)$ describes the ensemble distribution of musical parameters at each time.

## Python Implementation Sketch

```python
import numpy as np
from scipy.linalg import cholesky

class SdeEngine:
    """Generic SDE integrator with Euler-Maruyama scheme."""
    
    def __init__(self, drift_fn, diffusion_fn, dt=1.0):
        """
        drift_fn: callable(X, t) -> np.ndarray — drift field
        diffusion_fn: callable(X, t) -> np.ndarray — diffusion field (std dev)
        dt: time step size in ticks
        """
        self.drift = drift_fn
        self.diffusion = diffusion_fn
        self.dt = dt
    
    def step(self, X, t):
        """Single Euler-Maruyama step."""
        dW = np.random.randn(*X.shape)
        X_new = X + self.drift(X, t) * self.dt + self.diffusion(X, t) * np.sqrt(self.dt) * dW
        return X_new
    
    def integrate(self, X0, n_steps):
        """Integrate from X0 for n_steps, returning full trajectory."""
        d = len(X0)
        traj = np.zeros((n_steps + 1, d))
        traj[0] = X0
        X = X0.copy()
        for i in range(n_steps):
            t = i * self.dt
            X = self.step(X, t)
            traj[i + 1] = X
        return traj


class TonalPotential:
    """Tonal gravity as gradient of a potential well."""
    
    @staticmethod
    def single_well(x, center=60.0, gamma=0.1):
        """Ornstein-Uhlenbeck: linear restoring force toward center."""
        return -gamma * (x - center)
    
    @staticmethod
    def multi_well(x, centers, weights, length_scales):
        """Multi-well potential: sum of Gaussians weighted by depth."""
        grad = np.zeros_like(x)
        for c, w, l in zip(centers, weights, length_scales):
            dx = x - c
            grad += -w * dx / l**2 * np.exp(-dx**2 / (2 * l**2))
        return grad
    
    @staticmethod
    def periodic_pitch(x, n_wells=12):
        """Periodic potential for chromatic space: n_wells per octave."""
        return -0.25 * np.sin(2 * np.pi * n_wells * x / 12.0)


class CouplingMatrix:
    """Voice coupling for multi-SDE composition."""
    
    def __init__(self, n_voices, coupling_strength=0.1, correlation=0.5):
        self.n = n_voices
        self.kappa = coupling_strength  # drift coupling strength
        # Cholesky factor for correlated noise
        rho = correlation * np.ones((n_voices, n_voices))
        np.fill_diagonal(rho, 1.0)
        # Ensure PSD
        eigvals = np.linalg.eigvalsh(rho)
        if eigvals.min() < 0:
            rho -= 1.1 * eigvals.min() * np.eye(n_voices)
        self.L = cholesky(rho, lower=True)
    
    def coupling_drift(self, X, consonance_fn):
        """Drift contribution from voice-leading coupling."""
        # For each voice pair, add gradient of consonance cost
        grad = np.zeros_like(X)
        V, d = X.shape
        for v in range(V):
            for w in range(v + 1, V):
                interval = X[v, 0] - X[w, 0]
                dC = consonance_fn(interval, derivative=True)
                grad[v, 0] -= self.kappa * dC
                grad[w, 0] += self.kappa * dC
        return grad
    
    def correlated_noise(self, n_steps):
        """Generate correlated Wiener increments across voices."""
        dW_indep = np.random.randn(n_steps, self.n)
        dW_corr = dW_indep @ self.L.T
        return dW_corr


class SdeComposer:
    """High-level composer wrapping SDEC for UnitMatrix workflow."""
    
    def __init__(self, bpm=120, ticks_per_beat=480, beats_per_bar=4):
        self.bpm = bpm
        self.tpb = ticks_per_beat
        self.bpb = beats_per_bar
        self.tick_dt = 60.0 / (bpm * ticks_per_beat)  # seconds per tick
    
    def make_tonal_drift(self, tonic=60, key_strength=0.1, scale_degrees=None):
        """Create drift field for tonal gravity."""
        if scale_degrees is None:
            scale_degrees = [0, 2, 4, 5, 7, 9, 11]  # major scale
        
        def drift(X, t):
            # Pitch coordinate is X[..., 0]
            pitch = X[0] if X.ndim == 1 else X[:, 0]
            # Pull toward nearest scale degree
            grad = TonalPotential.single_well(pitch, tonic, key_strength)
            return np.array([grad] + [0.0] * (len(X) - 1))
        
        return drift
    
    def compose(self, n_voices, n_bars, sections, seed=42):
        """
        sections: list of dicts with {'bars': int, 'drift': fn, 'diffusion': float, 'coupling': float}
        Returns: dict of voice -> list of note events
        """
        np.random.seed(seed)
        total_ticks = n_bars * self.tpb * self.bpb
        
        # Initialize state: shape (n_voices, d)
        d = 3  # pitch, log-IOI, velocity
        X = np.zeros((n_voices, d))
        X[:, 0] = 60.0  # starting pitch
        
        events = {v: [] for v in range(n_voices)}
        tick = 0
        
        for sec in sections:
            sec_ticks = sec['bars'] * self.tpb * self.bpb
            drift_fn = sec['drift']
            sigma = sec['diffusion']
            coupling = sec.get('coupling', 0.0)
            
            def full_drift(X, t):
                drift_part = drift_fn(X, t)
                # Add coupling if multi-voice
                if n_voices > 1 and coupling > 0:
                    # Simple consonance coupling: prefer consonant intervals
                    for v in range(n_voices):
                        for w in range(v + 1, n_voices):
                            interval = X[v, 0] - X[w, 0]
                            # Target: consonant intervals (unison, 3rd, 5th, 6th)
                            targets = [0, 4, 7, 9]
                            best = min(targets, key=lambda t: abs(interval % 12 - t))
                            diff = (interval % 12) - best
                            drift_part[v, 0] -= coupling * diff
                            drift_part[w, 0] += coupling * diff
                return drift_part
            
            def full_diffusion(X, t):
                return sigma * np.ones_like(X)
            
            engine = SdeEngine(full_drift, full_diffusion, dt=1.0)
            
            for i in range(sec_ticks):
                t = tick + i
                X = engine.step(X, t)
                # Detect note onsets: when pitch crosses a semitone boundary
                for v in range(n_voices):
                    pitch = int(round(X[v, 0]))
                    if 0 <= pitch <= 127:
                        vel = int(np.clip(X[v, 2] * 60 + 60, 0, 127))
                        events[v].append((t, pitch, vel, 120))  # tick, pitch, vel, duration
                tick += 1
        
        return events
```

## References

1. Oksendal, B. (2003). *Stochastic Differential Equations: An Introduction with Applications*, 6th ed. Springer.
2. Gardiner, C. W. (2009). *Handbook of Stochastic Methods*, 4th ed. Springer.
3. Risken, H. (1996). *The Fokker-Planck Equation*, 2nd ed. Springer.
4. Temko, A. (2005). "Drift-diffusion models for musical pitch and rhythm generation." *Proc. Int. Conf. Music and AI*, Edinburgh.
5. Wannenmacher, T. & Purwins, H. (2006). "Stochastic differential equations for audio synthesis and composition." *DAFx-06*, Montreal.
6. Song, Y., Sohl-Dickstein, J., Kingma, D. P., et al. (2021). "Score-Based Generative Modeling through Stochastic Differential Equations." *ICLR 2021*. (Score-SDE framework — related, AI-driven counterpart.)

## Candidate Code Path

`generators/sde_composition.py` — implements `SdeEngine` (base integrator), `TonalPotential` (drift families), `CouplingMatrix` (voice interaction), and `SdeComposer` (UnitMatrix workflow wrapper). Lives under the `concrete` layer alongside the MCWS, NMF, and SAMC generators.