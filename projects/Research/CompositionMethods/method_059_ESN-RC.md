# Echo State Network Reservoir Composition (ESN-RC) — Method 059

**Paradigm**: Nature-Led (Physical/Emergent) — untrained recurrent dynamics + supervised linear readout.
**Classification**: Tonal Gravity = Weak (Fading-memory) · Metric Binding = Continuous / Fluid · Memory Depth = Meso / Echo State · Time Complexity = O(N²T) dense, O(NkT) sparse.

## Overview

Echo State Network Reservoir Composition (ESN-RC) generates music by driving a fixed, randomly-connected recurrent neural network (the "reservoir") with a time-varying input signal, then decoding the reservoir's high-dimensional state trajectory into musical parameters via a single trained linear readout. The reservoir's recurrent weights are **never trained** — they are fixed at initialization subject only to the Echo State Property (ESP), $\rho(W) < 1$. All learning is a one-shot ridge regression on the readout, making training convex, gradient-free, and immune to vanishing/exploding gradients.

The method sits at the boundary of the Nature-Led and AI-Driven paradigms: the *dynamics* are emergent and untrained (like 037 FHNS, 038 KOPS, 043 SATM), but a supervised readout is learned (like 042 NST, 046 VAE). It is the reservoir-computing counterpart to 002 Markov (fading memory vs. state-1 memory) and 040 Perlin (high-dimensional echo state vs. high-dimensional noise field).

## Mathematical Foundations

### Leaky-Integrator ESN State Update

$$x(t+1) = (1 - \alpha)\, x(t) + \alpha \cdot \tanh\!\big(W\, x(t) + W_{in}\, u(t) + b\big)$$

- $x(t) \in \mathbb{R}^N$ — reservoir state (N = 100–1000 units).
- $u(t) \in \mathbb{R}^{N_u}$ — input (clock pulse, chord embedding, section label).
- $W \in \mathbb{R}^{N \times N}$ — fixed sparse recurrent weights, entries $\sim \mathcal{N}(0,1)$, rescaled so $\rho(W) = \rho_{target} < 1$.
- $W_{in} \in \mathbb{R}^{N \times N_u}$ — fixed input weights.
- $b \in \mathbb{R}^N$ — bias.
- $\alpha \in (0,1]$ — leak rate (state update speed).

### Echo State Property (ESP)

The reservoir has the ESP iff $\rho(W) < 1$: the state trajectory asymptotically forgets its initial condition $x(0)$ and becomes a deterministic *fading-memory* function of the input history. This is what bounds the output (no runaway drift) and guarantees the readout sees a stable, reproducible echo of the input.

### Linear Readout

$$y(t) = W_{out}\, x(t)$$

Trained by ridge regression:

$$W_{out} = \arg\min_W \|Y - W X\|_F^2 + \lambda \|W\|_F^2 \quad\Rightarrow\quad W_{out} = Y X^\top (X X^\top + \lambda I)^{-1}$$

where $X$ is the collected state matrix (washout period discarded) and $Y$ the target. Closed-form, $\mathcal{O}(N^2 T + N^3)$.

### Memory Capacity

$MC \approx N$ — the number of independent past inputs the reservoir can recall. Grows with $N$ and as $\rho \to 1$ (edge of chaos). This directly sets the musical phrase length: small $N$ / small $\rho$ = short sectional memory, large $N$ / $\rho \to 1$ = through-composed continuity.

### Edge of Chaos

Near $\rho = 1$ the reservoir operates at the edge of chaos, producing the richest, most varied state trajectories (and hence textures). Far below 1 it is nearly linear and produces bland, repetitive output. $\rho$ is the primary "richness" knob.

## Musical Elements Framework

| Element | Mechanism |
|---|---|
| **PITCH** | Readout $W_{out}^v$ maps state to real-valued contour per voice, scale-quantized at onsets. ESP keeps contour bounded. Shared state + independent rows = coherent yet independent lines. |
| **RHYTHM** | Onsets at readout-energy threshold crossings / state-derivative peaks. Injected beat clock biases metric regularity; reservoir nonlinearity perturbs into organic micro-timing. $\alpha$, $\rho$ control density. |
| **HARMONY** | Chord function injected as $u(t)$; fading memory blends recent chords → smooth voice-leading. Multiple readout rows decode same state → vertical consonance. |
| **STRUCTURE** | Input sequence $u(t)$ per section defines macro-form. State not reset at boundaries → natural connective tissue. Memory horizon sets phrase length; conceptors gate hard section switches. |
| **TEXTURE** | Reservoir dimensionality $N$ is the texture engine. Voice count = readout rows (decoupled from $N$). Density = local state energy $\|x(t)\|^2$. $\rho$ tunes richness. |

## UnitMatrix Integration

- **Rows (Voices)**: one readout row $W_{out}^v$ per voice; all read the same shared state $x(t)$.
- **Columns (Sections)**: each section injects input $u_s(t)$ over $[T_{s-1}, T_s]$; state driven continuously, never reset.
- **Cells** $U_{v,s}$: `{PITCH}` = scale-quantized $W_{out}^v x(t)$ at onsets; `{RHYTHM}` = threshold-crossing onset times; `{TEXTURE}` = $\|x(t)\|^2$ density.
- **Flow**: init reservoir → build $u(t)$ → drive → decode per voice → extract events → fill cells → validate zero-drift → export via musicom engine.

## Implementation Sketch (NumPy)

```python
import numpy as np

class ESNComposer:
    def __init__(self, n_res=500, n_in=8, rho=0.9, leak=0.5,
                 connectivity=0.05, seed=0):
        rng = np.random.default_rng(seed)
        mask = rng.random((n_res, n_res)) < connectivity
        W = rng.normal(0, 1, (n_res, n_res)) * mask
        W *= rho / max(abs(np.linalg.eigvals(W)))   # enforce ESP
        self.W = W
        self.Win = rng.uniform(-0.5, 0.5, (n_res, n_in))
        self.b = rng.uniform(-0.1, 0.1, n_res)
        self.leak = leak

    def drive(self, U, washout=50):
        T = U.shape[0]
        X = np.zeros((T, self.W.shape[0]))
        x = np.zeros(self.W.shape[0])
        for t in range(T):
            x = (1 - self.leak) * x + self.leak * np.tanh(
                self.W @ x + self.Win @ U[t] + self.b)
            X[t] = x
        return X[washout:]

    def train_readout(self, X, Y, lam=1e-6):
        A = X.T @ X + lam * np.eye(X.shape[1])
        return (np.linalg.solve(A, X.T @ Y)).T

    def compose(self, U, Wout, Wvel, scale):
        X = self.drive(U)
        pitches = Wout @ X.T
        energy = 1 / (1 + np.exp(-(Wvel @ X.T)))
        events = []
        for v in range(Wout.shape[0]):
            onsets = np.where((energy[v, 1:] > 0.5) & (energy[v, :-1] <= 0.5))[0]
            for t in onsets:
                midi = scale[round(pitches[v, t]) % len(scale)]
                events.append((v, t, midi, int(energy[v, t] * 127)))
        return events
```

## Pitfalls

1. **ESP violation** ($\rho \ge 1$): chaotic/unstable output. Always rescale $W$ to $\rho_{target} < 1$ and verify eigenvalues.
2. **Readout overfitting**: small $T$ + large $N$ → brittle readout. Ridge-regularize, discard washout.
3. **Input saturation**: $\tanh$ saturates → memory collapse. Scale $W_{in}$ to $[-0.5, 0.5]$, normalize inputs.
4. **Echo/repetition artifacts**: fading memory literally echoes past input. Tune $\rho$/$\alpha$, inject noise, use conceptors.
5. **Reservoir too small**: $MC \approx N$ lost → short structure. Scale $N \ge 200$ for multi-bar coherence.
6. **Clock dominance**: strong clock → rigid metronome. Attenuate clock, let nonlinearity perturb.
7. **Monophonic collapse**: saturated state → near-constant pitch (cf. FHNS 037 pitfall). Add noise, raise $\rho$ toward edge of chaos.

## References

- Jaeger, H. (2001). "The 'echo state' approach to analysing and training recurrent neural networks." *GMD Report 148*.
- Maass, W., Natschläger, T., & Markram, H. (2002). "Real-time computing without stable states: a new framework for neural computation based on perturbations." *Neural Computation* 14(11): 2531–2560.
- Jaeger, H. (2002). "Tutorial on training recurrent neural networks, covering BPTT, RTRL, EKF and the 'echo state network' approach." *GMD Report 159*.
- Lukoševičius, M., & Jaeger, H. (2009). "Reservoir computing approaches to recurrent neural network training." *Computer Science Review* 3(3): 127–149.
- Jaeger, H. (2014). "Controlling recurrent neural networks by conceptors." arXiv:1403.3369.
- Scardapane, S., & Wang, D. (2017). "Randomness in neural networks: an overview." *WIREs Data Mining and Knowledge Discovery* 7(2).
- Kiebel, S. J. (2009). "Dynamic causal modeling and the brain's musical grammar."
