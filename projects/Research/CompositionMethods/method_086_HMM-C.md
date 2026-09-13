# Hidden Markov Model Latent-State Composition (HMM-C)

**Method ID**: 086
**Paradigm**: Stochastic
**Layer**: concrete (emits note/chord events into UnitMatrix cells; feeds `generators/`)
**Candidate code path**: `generators/hmm_composition.py`
**Acronym**: HMM-C

## One-line description

Generates music as the emission from a hidden Markov chain: latent states are tonal functions / chord regions / form sections, observed tokens are pitch classes, rhythmic cells, and velocity levels. The transition matrix $A$ encodes the harmonic grammar (state→state movement = chord progression), the emission matrix $B$ encodes the surface vocabulary, and the initial distribution $\pi$ seeds the piece. Composition = sample or Viterbi-decode the hidden state path (forced per section), then emit from $B$; Baum–Welch (EM) learns $A$ and $B$ from a corpus.

## Extended math

### The model

An HMM is a doubly stochastic process with hidden states $q_t \in \{1..S\}$ and emissions $o_t$:

$$\lambda = (A, B, \pi), \qquad \pi_i = P(q_1=i), \quad A_{ij} = P(q_{t+1}=j \mid q_t=i), \quad B_i(o) = P(o_t=o \mid q_t=i).$$

The joint probability of a state path and observation sequence factorizes as

$$P(q_{1:T}, o_{1:T} \mid \lambda) = \pi_{q_1} \prod_{t=2}^{T} A_{q_{t-1},q_t} \prod_{t=1}^{T} B_{q_t}(o_t).$$

### Forward–backward (inference)

$$\alpha_t(j) = \left[\sum_i \alpha_{t-1}(i) A_{ij}\right] B_j(o_t), \qquad \alpha_1(j) = \pi_j B_j(o_1),$$

$$\beta_t(i) = \sum_j A_{ij} B_j(o_{t+1}) \beta_{t+1}(j), \qquad \beta_T(i) = 1,$$

so $P(O\mid\lambda) = \sum_i \alpha_T(i)$. The posterior state occupancy and transition occupancy are

$$\gamma_t(i) = \frac{\alpha_t(i)\beta_t(i)}{P(O\mid\lambda)}, \qquad
\xi_t(i,j) = \frac{\alpha_t(i) A_{ij} B_j(o_{t+1}) \beta_{t+1}(j)}{P(O\mid\lambda)}.$$

### Baum–Welch (EM training)

$$A_{ij} \leftarrow \frac{\sum_{t=1}^{T-1} \xi_t(i,j)}{\sum_{t=1}^{T-1} \gamma_t(i)}, \qquad
B_i(k) \leftarrow \frac{\sum_{t:\,o_t=k} \gamma_t(i)}{\sum_{t=1}^{T} \gamma_t(i)}, \qquad
\pi_i \leftarrow \gamma_1(i).$$

Each iteration is an EM step monotonically increasing $P(O\mid\lambda)$; convergence to a local optimum. **Complexity** $\mathcal{O}(I \cdot T \cdot S^2)$ for $I$ iterations over $T$ frames and $S$ states.

### Viterbi (best-path decoding)

$$\delta_t(j) = \max_i \left[ \delta_{t-1}(i) A_{ij} \right] B_j(o_t), \qquad \psi_t(j) = \arg\max_i \left[ \delta_{t-1}(i) A_{ij} \right],$$

with $\delta_1(j) = \pi_j B_j(o_1)$; the optimal path is recovered by backtracking through $\psi$. **Complexity** $\mathcal{O}(T \cdot S^2)$ (plus emission evaluation, giving $\mathcal{O}(T \cdot S^2 \cdot V)$ with $V$ emission symbols).

### Musical state/emission interpretation

- Hidden state $i$ = tonal function / chord region / section. With a 4-state functional model, $\{1,2,3,4\} = \{\text{HOME}, \text{LIFT}, \text{TENSE}, \text{TURN}\}$; with a chord-region model each state is a chord/scale identity.
- Emission alphabet = pitch classes (melody), or a factored (multi-stream) alphabet: pitch-class × rhythmic-cell × velocity for full event generation.
- Dwell time in state $i$ is geometric with mean $1/(1-A_{ii})$ — the phrase-length dial.

## Python implementation sketch

```python
"""Hidden Markov Model Latent-State Composition (Method 086, HMM-C).

Everything in log-space to avoid underflow; deterministic per seed for the
zero-drift gate. The musicom engine (UnitMatrixComposer) authors the MIDI —
this module only produces (state, emission) event tuples.
"""
import numpy as np

def _logsumexp(a, axis=None):
    m = np.max(a, axis=axis, keepdims=True)
    return m.squeeze(axis) + np.log(np.exp(a - m).sum(axis=axis))

class HMMComposer:
    def __init__(self, n_states, n_symbols, seed=0):
        self.rng = np.random.default_rng(seed)
        self.S = n_states
        self.V = n_symbols
        # log-domain parameters
        self.logA = np.full((n_states, n_states), np.log(1e-9))
        self.logB = np.full((n_states, n_symbols), np.log(1e-9))
        self.logpi = np.full(n_states, np.log(1e-9))

    def set_functional_prior(self, self_loop=0.6, off=0.05):
        """Hand-seed A with a HOME->LIFT->TENSE->TURN functional grammar."""
        A = np.full((self.S, self.S), off)
        for i in range(self.S):
            A[i, i] = self_loop
            if i + 1 < self.S:
                A[i, i + 1] = 0.3              # forward functional motion
        A[-1, 0] = 0.3                          # TURN resolves to HOME
        A = A / A.sum(axis=1, keepdims=True)
        self.logA = np.log(A)
        self.logpi = np.log(np.eye(1, self.S, 0).ravel() + 1e-9)
        # uniform emissions (smoothed)
        self.logB = np.full((self.S, self.V), -np.log(self.V))

    def sample_path(self, T, allowed=None):
        """Sample a hidden state path; `allowed` = per-t state subsets (sections)."""
        q = []
        p = np.exp(self.logpi) if allowed is None or allowed[0] is None \
            else _mask(np.exp(self.logpi), allowed[0])
        q.append(self.rng.choice(self.S, p=p / p.sum()))
        for t in range(1, T):
            p = np.exp(self.logA[q[-1]])
            if allowed is not None and allowed[t] is not None:
                p = _mask(p, allowed[t])
            q.append(self.rng.choice(self.S, p=p / p.sum()))
        return q

    def emit(self, q):
        """Sample one emission symbol per hidden state."""
        return [self.rng.choice(self.V, p=np.exp(self.logB[s]) / np.exp(self.logB[s]).sum())
                for s in q]

    def forward_backward(self, obs):
        """Log-domain alpha/beta; returns P(O|lambda)."""
        T = len(obs)
        logA, logB, logpi = self.logA, self.logB, self.logpi
        alpha = np.zeros((T, self.S))
        alpha[0] = logpi + logB[:, obs[0]]
        for t in range(1, T):
            alpha[t] = _logsumexp(alpha[t - 1][:, None] + logA, axis=0) + logB[:, obs[t]]
        beta = np.zeros((T, self.S))
        for t in range(T - 2, -1, -1):
            beta[t] = _logsumexp(logA + logB[:, obs[t + 1]] + beta[t + 1], axis=1)
        return _logsumexp(alpha[-1])

    def baum_welch(self, obs, n_iter=50):
        """EM re-estimation of A, B, pi (log-domain)."""
        T = len(obs)
        for _ in range(n_iter):
            logA, logB = self.logA, self.logB
            alpha = np.zeros((T, self.S)); alpha[0] = self.logpi + logB[:, obs[0]]
            for t in range(1, T):
                alpha[t] = _logsumexp(alpha[t - 1][:, None] + logA, axis=0) + logB[:, obs[t]]
            beta = np.zeros((T, self.S))
            for t in range(T - 2, -1, -1):
                beta[t] = _logsumexp(logA + logB[:, obs[t + 1]] + beta[t + 1], axis=1)
            logP = _logsumexp(alpha[-1])
            gamma = alpha + beta - logP
            xi = alpha[:-1, :, None] + logA[None] + logB[:, obs[1:]].T[:, None, :] \
                 + beta[1:, None, :] - logP
            self.logA = _logsumexp(xi, axis=0) - _logsumexp(gamma[:-1], axis=0)[:, None]
            denom = _logsumexp(gamma, axis=0)
            self.logB = np.full_like(self.logB, -np.inf)
            for k in range(self.V):
                idx = np.where(np.array(obs) == k)[0]
                if len(idx):
                    self.logB[:, k] = _logsumexp(gamma[idx], axis=0) - denom
            self.logpi = gamma[0]

    def viterbi(self, obs):
        """Most probable hidden path for an observation sequence."""
        T = len(obs)
        delta = np.zeros((T, self.S)); psi = np.zeros((T, self.S), dtype=int)
        delta[0] = self.logpi + self.logB[:, obs[0]]
        for t in range(1, T):
            v = delta[t - 1][:, None] + self.logA
            psi[t] = np.argmax(v, axis=0)
            delta[t] = np.max(v, axis=0) + self.logB[:, obs[t]]
        q = [int(np.argmax(delta[-1]))]
        for t in range(T - 1, 0, -1):
            q.append(int(psi[t, q[-1]]))
        return q[::-1]


def _mask(p, allowed):
    m = np.zeros_like(p); m[list(allowed)] = 1.0; return p * m


# --- Musicom integration (engine authors the MIDI) ---
# from workflows.unitmatrix_composer import UnitMatrixComposer, create_note_unit, create_chord_unit
# composer = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
# composer.create_matrix(num_voices=V, num_sections=S)
# hmm = HMMComposer(n_states=4, n_symbols=12, seed=7)
# hmm.set_functional_prior()
# q = hmm.sample_path(T, allowed=section_state_subsets)   # per-column forcing
# for t, s in enumerate(q):
#     pc = hmm.emit([s])[0]
#     composer.fill_voice_section("lead", section_of(t), create_note_unit(pc, 480))
# ok, msg = composer.validate()   # MUST be True before to_midi (per AGENTS.md)
```

## References

- Baum, L. E., & Petrie, T. (1966). "Statistical Inference for Probabilistic Functions of Finite State Markov Chains." *Annals of Mathematical Statistics* 37(6), 1554–1563.
- Rabiner, L. R. (1989). "A Tutorial on Hidden Markov Models and Selected Applications in Speech Recognition." *Proceedings of the IEEE* 77(2), 257–286.
- Viterbi, A. J. (1967). "Error Bounds for Convolutional Codes and an Asymptotically Optimum Decoding Algorithm." *IEEE Transactions on Information Theory* 13(2), 260–269.
- Ponsford, D., Wiggins, G., & Mellish, C. (1999). "Statistical Learning of Harmonic Movement." *Journal of New Music Research* 28(2), 150–177.
- Raphael, C. (2002). "A Hybrid Graphical Model for Rhythmic Parsing." *Artificial Intelligence* 137(1–2), 217–238.
- Sheh, A., & Ellis, D. P. W. (2003). "Chord Segmentation and Recognition Using EM-Trained Hidden Markov Models." *Proceedings of ISMIR*.
- Allan, M., & Williams, C. K. I. (2005). "Harmonising Chorales by Probabilistic Inference." *Advances in Neural Information Processing Systems (NeurIPS) 17*.
