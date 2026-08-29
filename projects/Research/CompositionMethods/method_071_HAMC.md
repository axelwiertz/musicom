# Method 071 — Hopfield Associative Memory Composition (HAM-C)

**Paradigm:** Nature-Led (physical/emergent — spin-glass attractor dynamics)
**Classification:** Tonal Gravity = Strong (Memory-attractor) · Metric Binding = Grid-Locked / Continuous · Memory Depth = Macro / Attractor · Time Complexity = $\mathcal{O}(N^2 \cdot I)$ recall, $\mathcal{O}(P \cdot N^2)$ store

---

## One-line description

Stores musical patterns (riffs, progressions, grooves) as attractors of a Hopfield spin-glass network via one-shot Hebbian storage; composes by content-addressable recall — a partial cue relaxes by asynchronous threshold updates to a stored memory.

---

## Extended mathematics

### 1. The memory model

A Hopfield network is a set of $N$ Ising spins $\mathbf{x} \in \{-1,+1\}^N$ with symmetric zero-diagonal weights $W \in \mathbb{R}^{N \times N}$, $W_{ij}=W_{ji}$, $W_{ii}=0$. $P$ patterns $\boldsymbol{\xi}^\mu \in \{-1,+1\}^N$ ($\mu = 1\dots P$) are stored by the **Hebbian outer-product rule**:

$$W_{ij} = \frac{1}{N}\sum_{\mu=1}^{P}\xi^\mu_i \xi^\mu_j \qquad (i \neq j).$$

Equivalently in matrix form:

$$\mathbf{W} = \frac{1}{N}\sum_{\mu=1}^{P}\left(\boldsymbol{\xi}^\mu {\boldsymbol{\xi}^\mu}^\top - \mathbf{I}\right).$$

### 2. Energy landscape (Lyapunov function)

The network defines an energy over all $2^N$ states:

$$E(\mathbf{x}) = -\frac{1}{2}\sum_{i\neq j}W_{ij}x_i x_j + \sum_i \theta_i x_i = -\frac{1}{2}\mathbf{x}^\top \mathbf{W} \mathbf{x} + \boldsymbol{\theta}^\top \mathbf{x}.$$

Every asynchronous update

$$x_i \leftarrow \operatorname{sign}\!\left(\sum_{j} W_{ij} x_j - \theta_i\right)$$

satisfies $\Delta E = -\Delta x_i \sum_j W_{ij} x_j \le 0$, so $E$ is a Lyapunov function: the dynamics monotonically descend to a **local minimum** of $E$. These minima are (for $P$ below capacity) exactly the stored patterns $\boldsymbol{\xi}^\mu$, plus a set of **spurious states** — stable linear combinations of memories — at higher energy.

The **energy barrier** between two memories $\boldsymbol{\xi}^\mu, \boldsymbol{\xi}^\nu$ is proportional to their separation; for random patterns with Hamming distance $d_{\mu\nu}$ the barrier scales with $d_{\mu\nu}$. This is the voice-leading/harmonic-distance interpretation: two stored chords close in Hamming space have a low barrier (smooth transition), distant chords a high barrier (dramatic modulation). Spurious states at basin boundaries are the network's built-in **passing harmonies**.

### 3. Capacity

For random uncorrelated patterns the storage capacity is $P_{\max} \approx 0.138 N$ (Amit–Gutfreund–Sompolinsky 1985). Correlated patterns (the norm in music — shared diatonic vocabulary) reduce effective capacity but increase generalization: recalls of correlated patterns blend into musically plausible passing material. Two improved storage rules raise capacity:

- **Storkey rule** (iterative, subtracts leakage): $W_{ij}^{(\mu)} = W_{ij}^{(\mu-1)} + \frac{1}{N}\xi^\mu_i\xi^\mu_j - \frac{1}{N}\xi^\mu_i h^\mu_{ji} - \frac{1}{N}\xi^\mu_j h^\mu_{ij}$, where $h^\mu_{ji}=\sum_k W_{jk}^{(\mu-1)}\xi^\mu_k$.
- **Pseudo-inverse rule**: $\mathbf{W} = \boldsymbol{\Xi}(\boldsymbol{\Xi}^\top\boldsymbol{\Xi})^{-1}\boldsymbol{\Xi}^\top$ stores up to $N$ linearly independent patterns exactly.

### 4. Finite-temperature recall (Boltzmann / Metropolis)

At temperature $T$ the update becomes stochastic:

$$\Pr(x_i = +1) = \sigma\!\left(\frac{2h_i}{T}\right),\qquad h_i = \sum_j W_{ij} x_j - \theta_i, \quad \sigma(z) = \frac{1}{1+e^{-z}}.$$

This is a Metropolis walk over the energy landscape: $T=0$ = clean descent to one attractor; low $T$ = stable motif (stays in basin); higher $T$ = basin hopping (variation, passing harmonies, ornamentation); very high $T$ = randomization (texture/noise).

### 5. Musical encoding

The state vector is a concatenation of per-voice fields:

$$\mathbf{x} = \underbrace{\text{pitch}^{(1)}\,\text{onset}^{(1)}\,\text{vel}^{(1)}}_{\text{voice 1}} \;\big|\; \underbrace{\text{pitch}^{(2)}\,\text{onset}^{(2)}\,\text{vel}^{(2)}}_{\text{voice 2}} \;\big|\; \cdots \;\big|\; \text{voice } V.$$

- **pitch field**: one-hot over $n_{\text{pitch}}$ scale degrees (exactly one active unit = one note) or thermometer (cumulative = chord in one field).
- **onset field**: one-hot over $n_{\text{onset}}$ time steps (active = note onset at that step).
- **vel field**: thermometer over $n_{\text{vel}}$ levels (active count = velocity).

The **mixing ratio** of field lengths sets pitch-vs-rhythm-vs-dynamics resolution. Decoding reads the settled state's per-voice sub-vectors back into notes.

### 6. Composition as recall

Given the learned $W$ and a form program of cues $[\mathbf{c}_1,\dots,\mathbf{c}_S]$:

1. Initialize $\mathbf{x} = \mathbf{c}_s$ (partial cue for section $s$).
2. Relax by asynchronous updates at temperature $T_s$ to convergence.
3. Decode the settled state → per-voice pitch/rhythm/velocity → UnitMatrix column $s$.

The **cue schedule is the macro-form**: rondo = A–B–A–C–A (cue switches re-settle into the target basin); through-composed = cues engineered to land in spurious states (no memory recalled twice).

---

## Python implementation sketch

```python
from __future__ import annotations
import numpy as np

def encode_pattern(notes: list[tuple[int, int, int]], n_pitch: int, n_onset: int) -> np.ndarray:
    """Encode a polyphonic fragment as a binary {-1,+1} pattern.
    notes: list of (voice, pitch_degree, onset_step). One-hot pitch + onset fields per voice."""
    n_voices = max(v for v, _, _ in notes) + 1
    fields = []
    for v in range(n_voices):
        p = np.full(n_pitch, -1.0); o = np.full(n_onset, -1.0)
        for vv, pp, oo in notes:
            if vv == v:
                p[pp] = 1.0; o[oo] = 1.0
        fields.append(np.concatenate([p, o]))
    return np.concatenate(fields)

def hebbian_store(patterns: list[np.ndarray]) -> np.ndarray:
    """One-shot Hebbian weights (zero diagonal). patterns: list of {-1,+1} vectors."""
    N = patterns[0].size
    W = np.zeros((N, N))
    for xi in patterns:
        W += np.outer(xi, xi)
    W /= N
    np.fill_diagonal(W, 0.0)
    return W

def storkey_store(patterns: list[np.ndarray]) -> np.ndarray:
    """Storkey rule — higher capacity, less crosstalk than plain Hebbian."""
    N = patterns[0].size
    W = np.zeros((N, N))
    for xi in patterns:
        h = W @ xi
        W += (np.outer(xi, xi) - np.outer(xi, h) - np.outer(h, xi)) / N
        np.fill_diagonal(W, 0.0)
    return W

def recall(W: np.ndarray, cue: np.ndarray, theta: np.ndarray | None = None,
           temperature: float = 0.0, sweeps: int = 20, seed: int = 0) -> np.ndarray:
    """Content-addressable recall: relax `cue` to an attractor by asynchronous updates."""
    rng = np.random.default_rng(seed)
    x = np.asarray(cue, dtype=np.float64).copy()
    b = np.zeros_like(x) if theta is None else theta
    order = np.arange(x.size)
    for _ in range(sweeps):
        rng.shuffle(order)
        for i in order:
            h = float(W[i] @ x) - b[i]
            if temperature <= 0.0:
                x[i] = 1.0 if h >= 0 else -1.0
            else:
                x[i] = 1.0 if rng.random() < 1.0 / (1.0 + np.exp(-2 * h / temperature)) else -1.0
    return x

def energy(W: np.ndarray, x: np.ndarray, theta: np.ndarray | None = None) -> float:
    b = np.zeros_like(x) if theta is None else theta
    return -0.5 * float(x @ W @ x) + float(b @ x)

# --- Musicom integration sketch (conceptual — engine does the MIDI authoring) ---
# patterns = [encode_pattern(riff_a, n_pitch=12, n_onset=16),   # stored memories
#             encode_pattern(riff_b, n_pitch=12, n_onset=16),
#             encode_pattern(progression_chorus, n_pitch=12, n_onset=16)]
# W = hebbian_store(patterns)
# cues = [partial_cue_verse, partial_cue_chorus, ...]           # the form program
# for s, cue in enumerate(cues):
#     x = recall(W, cue, temperature=0.05, sweeps=20)            # settle into an attractor
#     decoded = decode_pattern(x)                                # per-voice pitch/onset/velocity
#     for v in decoded:  # route into UnitMatrix row v, column s
#         composer.fill_voice_section(voice=v, section=s, create_note_unit(pitch, dur, start_tick))
# ok, msg = composer.validate()   # MUST be True before to_midi (per AGENTS.md — never hand-roll mido)
```

**Tooling:** NumPy for Hebbian/Storkey store and the vectorized recall loop; GPU optional ($N$ in the thousands is still cheap). The musicom engine handles UnitMatrix fill and zero-drift MIDI export upstream; HAM-C emits the symbolic pitch/onset/velocity data that fills each cell.

---

## UnitMatrix integration summary

- **Rows (Voices):** each voice is a block of units; the network recalls all voices jointly (shared attractor = vertical coherence); block-diagonal weights = independent lines; strong cross-block coupling = coordinated voicing.
- **Columns (Sections):** each section is a cue pattern $\mathbf{c}_s$ + temperature $T_s$; the settled memory identity = the section's material.
- **Cells $U_{v,s}$:** `{PITCH}` = recalled pitch-field block; `{RHYTHM}` = recalled onset-field block; `{HARMONY}` = recalled memory identity + settled energy (deep = stable, spurious = transitional); `{TEXTURE}` = active-unit count + velocity field.

---

## Pitfalls (condensed)

1. Capacity overflow → blended garbage (keep $P \lesssim 0.1 N$, use Storkey, verify fixed points).
2. Spurious-state off-key recall → reject by energy threshold, zero-T for harmonic-critical material.
3. Binary encoding loses nuance → multi-field (velocity/octave/duration).
4. Sparse staccato recall → hybridization rule: layer continuous fill (026 DPSM / pad).
5. Symmetric weights = undirected recall → sequential/asymmetric variant or cue-schedule directionality.
6. Stuck in one basin → cue jitter, finite temperature, spurious-state cues.
7. Wrong-basin cue → engineer basin-separated cues, verify one-step recall.
8. $N$ too small → store short patterns, chain via cue schedule (associative sequencing).

---

## References

- Little, W. A. (1974). "The existence of persistent states in the brain." *Mathematical Biosciences* 19, 101–120.
- Hopfield, J. J. (1982). "Neural networks and physical systems with emergent collective computational abilities." *Proceedings of the National Academy of Sciences* 79(8), 2554–2558.
- Hopfield, J. J. (1984). "Neurons with graded response have collective computational properties like those of two-state neurons." *PNAS* 81(10), 3088–3092.
- Sherrington, D., & Kirkpatrick, S. (1975). "Solvable model of a spin-glass." *Physical Review Letters* 35(26), 1792–1796.
- Amit, D. J., Gutfreund, H., & Sompolinsky, H. (1985). "Storing infinite numbers of patterns in a spin-glass model of neural networks." *Physical Review Letters* 55(14), 1530–1533.
- Storkey, A. (1997). "Increasing the capacity of a Hopfield network without sacrificing functionality." In *Proceedings of ICANN*, 451–456.
- Ramsauer, H., et al. (2020). "Hopfield Networks is All You Need." *arXiv:2008.02217*.
- Todd, P. M. (1989). "A Connectionist Approach to Algorithmic Composition." *Computer Music Journal* 13(4), 27–43.
- Lewis, J. P. (1991). "Creation by refinement and the problem of algorithmic music composition." In *Music and Connectionism*, MIT Press, 212–228.
- Bharucha, J. J., & Todd, P. M. (1989). "Modeling the perception of tonal structure with neural nets." *Computer Music Journal* 13(4), 44–53.
