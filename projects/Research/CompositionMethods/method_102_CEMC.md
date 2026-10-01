# Method 102: Cross-Entropy Method Composition (CEMC)

## Paradigm
**Stochastic**

## Layer
**concrete** — generates concrete pitch, rhythm, harmony, and texture events that fill UnitMatrix cells.

## One-line Description
Iterative distribution optimization: sample sequences of musical tokens from a parametric distribution, keep elite (top-fitness) samples, refit the distribution via cross-entropy minimization, repeat until convergence.

## Summary Table Row
| **102** | concrete | Cross-Entropy Method Composition (CEMC) | **Stochastic** | Pitch, Rhythm, Harmony, Structure, Texture | Strong (Elite-guided) | Continuous / Fluid | Macro / Distribution | $\mathcal{O}(I \cdot N \cdot L)$ | Iterative distribution optimization: sample sequences, keep elite (top fitness), refit parametric distribution via CE minimization. |

---

## Mathematical Formulation

### Core Algorithm

The Cross-Entropy Method (Rubinstein 1997, 2004) solves optimization by converting it into a rare-event estimation problem. For composition, we maximize a musical fitness function $S(X)$ over token sequences $X$ (length $L = V \times \sum_m K_m$).

**Given**: parametric family $\{f(\cdot; \theta)\}$ of probability distributions (e.g., independent categoricals per position, or product of per-voice categoricals).

**Initialize**: $\theta_0$ (uniform or prior-informed), $t = 0$, elite ratio $\rho \in (0,1)$, smoothing $\alpha \in (0,1)$.

**Iterate** until convergence:

1. **Sample**: $X_1, \ldots, X_N \overset{\text{i.i.d.}}{\sim} f(\cdot; \theta_t)$
2. **Evaluate**: $S_i = S(X_i)$ for all $i$
3. **Select elite**: $\mathcal{E} = \{i: S_i \geq \gamma_t\}$ where $\gamma_t$ = $(1-\rho)$-quantile of $\{S_i\}$ (or top $\lceil \rho N \rceil$ by rank)
4. **Update via cross-entropy minimization**:
   $$\theta_{t+1} = \arg\max_{\theta} \frac{1}{|\mathcal{E}|} \sum_{i \in \mathcal{E}} \log f(X_i; \theta)$$
   This is **maximum likelihood estimation** on the elite set.
5. **Smooth**:
   $$\theta_{t+1} = \alpha \theta_{t+1}^{\text{MLE}} + (1-\alpha) \theta_t$$
6. $t \leftarrow t+1$

### Convergence criteria
- Maximum iterations $T_{\max}$ reached
- Elite fitness variance $< \varepsilon$
- Parameter change $\|\theta_t - \theta_{t-1}\| < \delta$

### Exponential family closed form

For categorical distributions (pitch, duration, chord symbols), the MLE at each position is:
$$p_j^{(t+1)} = \frac{1}{|\mathcal{E}|} \sum_{i \in \mathcal{E}} \mathbb{I}\{X_i^{(j)} = 1\}$$

For Gaussian distributions (velocity, microtiming), the MLE is:
$$\mu^{(t+1)} = \frac{1}{|\mathcal{E}|} \sum_{i \in \mathcal{E}} X_i$$
$$\sigma^{2(t+1)} = \frac{1}{|\mathcal{E}|} \sum_{i \in \mathcal{E}} (X_i - \mu^{(t+1)})^2$$

### Multi-voice factorization

The joint distribution factorizes as:
$$f(X; \theta) = \prod_{v=1}^{V} f_v(X^{(v)}; \theta_v) \cdot \prod_{v<w} \psi_{vw}(X^{(v)}, X^{(w)})$$

where:
- $f_v$ = per-voice marginal (product of independent categoricals or a Markov chain)
- $\psi_{vw}$ = pairwise coupling factors (consonance, voice-leading parsimony, crossing avoidance)

The global fitness $S(X)$ includes cross-voice terms, so the joint optimization naturally learns coordinated voicings.

### Musical fitness function components

$$S(X) = \sum_{m=1}^{M} \left[ w_{\text{tonal}} \cdot S_{\text{tonal}}^{(m)} + w_{\text{rhythm}} \cdot S_{\text{rhythm}}^{(m)} + w_{\text{harmony}} \cdot S_{\text{harmony}}^{(m)} + w_{\text{voice}} \cdot S_{\text{voice}}^{(m)} + w_{\text{texture}} \cdot S_{\text{texture}}^{(m)} \right]$$

where each $S_\cdot^{(m)}$ is normalized to $[0,1]$ per section $m$. Total $O(NML)$ cost per iteration: $N$ candidates × $M$ sections × $L$ tokens.

Scale-invariant defaults: $w_{\text{tonal}} = 0.25$, $w_{\text{rhythm}} = 0.20$, $w_{\text{harmony}} = 0.25$, $w_{\text{voice}} = 0.15$, $w_{\text{texture}} = 0.15$.

---

## Musical Elements Framework

### PITCH
- **Tokenization**: Categorical distribution over 12 pitch classes or 7 scale degrees
- **Fitness $S_{\text{tonal}}$**: Rewards pitch-class occurrence matching target scale profile (tonic/dominant frequency ≥ 30%, mediant ≥ 15%, chromatic passing tones ≤ 5%)
- **Convergence behavior**: Initial uniform distribution → concentrated on scale degrees with highest fitness (tonic home)
- **Register**: Optional continuous Gaussian per octave band with mean = target register, variance narrowing over iterations
- **Contour**: Token position encoding as MIDI pitch permits continuous-Gaussian modeling (ordinal)

### RHYTHM
- **Tokenization**: Categorical over $q=8$ duration classes (1/1, 1/2, 1/4, 1/8, 1/16, dotted, triplet, rest)
- **Fitness $S_{\text{rhythm}}$**: Rewards downbeat onsets (beat 1, 3), penalizes offbeat-only patterns, rewards metric groove templates
- **Microtiming**: Continuous Gaussian offset (mean = swing ratio for eighth notes, variance controls looseness)
- **Syncopation**: Balance reward — rewards moderate syncopation density ($\approx 20-40\%$ offbeat) over zero-syncopation or hyper-syncopation

### HARMONY
- **Tokenization**: Categorical over chord symbols (C, Dm, Em, F, G, Am, Bdim + extensions)
- **Fitness $S_{\text{harmony}}$**: Rewards functional progressions by root motion type (perfect 5th down = +1.0, 4th up = +0.8, 2nd up/down = +0.2, tritone = -0.5)
- **HOME/LIFT/TENSE/TURN**: Per-section target chord sets — HOME (I, vi), LIFT (IV, ii), TENSE (V, vii°), TURN (bridge chromatic chords)
- **Cadence bias**: V–I weighted $+2.0$, IV–I $+1.5$, ii–V–I $+2.5$, deceptive V–vi $+0.5$
- **Multi-voice**: Per-voice chord-tone assignment rewarded via $S_{\text{voice}}$ (triad/7th completeness)

### STRUCTURE
- **Section parameters**: Each section $m$ has independent $\theta^{(m)}$ (pitch, rhythm, harmony distributions)
- **Transition smoothing**: $ \theta^{(m)}_t = \alpha \theta^{\text{MLE}}_m + (1-\alpha)\theta^{(m)}_{t-1} + \beta(\theta^{(m-1)}_t - \theta^{(m)}_t)$
- **Form templates**: Verse/Chorus/Bridge/Intro/Outro with target contrast profiles (e.g., chorus: higher event density, wider pitch range)
- **Fitness $S_{\text{structure}}$**: Within-section consistency (low entropy of merged section samples), between-section contrast (KL divergence between section distributions)

### TEXTURE
- **Emergent from density**: Per-voice event count per time window
- **Fitness $S_{\text{texture}}$**: Target homophony index $H = \frac{\text{simultaneous onsets}}{\text{total onsets}}$ per window
  - Homophony: $H_{\text{target}} \approx 0.8-1.0$
  - Polyphony: $H_{\text{target}} \approx 0.3-0.6$
  - Pointillism: $H_{\text{target}} \approx 0.0-0.2$
- **Voice separation**: Adjacent voice pitch gap rewarded at 4-12 semitones, >18 semitones penalized (register gap)
- **Uniformity**: Onset-time jitter per voice tracked — low jitter = chorusing, high jitter = independent

---

## UnitMatrix Integration

### Voices (rows)
- Each voice $v$ gets its own parameter vector $\theta_v$ (pitch + rhythm + velocity categorical distributions)
- Voice coupling through joint fitness: $S_{\text{voice}}$ penalizes parallel fifths/octaves, voice crossings, and unison saturation
- Percussion: binary alphabet $\{\text{hit}, \text{rest}\}$ with rhythmic fitness only
- $V$ independent CEM chains with shared elite selection = coordinated voice emergence

### Sections (columns)
- Section $m$ defines length $K_m$ tokens × $V$ voices
- $\theta^{(m)}$ initialized from section-type prior (verse = narrow range, chorus = wide range)
- Section boundary: parameter contrast enforced via $S_{\text{structure}}$
- Transition sections: interpolation $\theta_{\text{trans}} = (1-t)\theta_A + t\theta_B$ for $t \in [0,1]$

### Cell decoding
- Token → pitch: categorical mode → scale step → MIDI note (register from per-voice continuous Gaussian)
- Token → duration: categorical mode → tick length ($\times$ tempo at section)
- Token → velocity: continuous Gaussian mode → MIDI velocity 0-127
- Zero-drift: cells padded to section tick-length during post-processing

---

## Python Implementation Sketch

```python
import numpy as np
from typing import Optional, Callable

class CEMComposer:
    """
    Cross-Entropy Method Composition (CEMC).

    Maintains categorical distributions over musical tokens
    and iteratively refines them toward elite (high-fitness) sequences.
    """
    def __init__(
        self,
        n_voices: int = 4,
        n_sections: int = 8,
        tokens_per_cell: int = 16,
        alphabet_size: int = 12,       # pitch classes
        duration_size: int = 8,        # duration classes
        elite_ratio: float = 0.1,
        smoothing: float = 0.7,
        n_samples: int = 500,
        max_iters: int = 100,
        seed: int = 42
    ):
        self.V = n_voices
        self.M = n_sections
        self.K = tokens_per_cell
        self.L = self.V * self.M * self.K  # total token positions
        self.q_pitch = alphabet_size
        self.q_dur = duration_size
        self.rho = elite_ratio
        self.alpha = smoothing
        self.N = n_samples
        self.T = max_iters
        self.rng = np.random.default_rng(seed)

        # Initialize categorical parameters (uniform over alphabet)
        # shape: (n_voices, n_sections, K, q_pitch + q_dur + 1_velocity)
        self.theta_pitch = np.ones((self.V, self.M, self.K, self.q_pitch)) / self.q_pitch
        self.theta_dur   = np.ones((self.V, self.M, self.K, self.q_dur))   / self.q_dur
        self.theta_vel   = np.ones((self.V, self.M, self.K, 1)) * 0.5       # Gaussian mean (normalized 0-1)

        self.best_seq = None
        self.best_fitness = -np.inf

    def sample_sequences(self) -> np.ndarray:
        """Draw N candidate sequences from current distributions."""
        # pitch: (N, V, M, K) categorical samples
        pitch_flat = np.zeros((self.N, self.L), dtype=int)
        dur_flat   = np.zeros((self.N, self.L), dtype=int)
        vel_flat   = np.zeros((self.N, self.L))

        for v in range(self.V):
            for m in range(self.M):
                for k in range(self.K):
                    idx = v * self.M * self.K + m * self.K + k
                    # Sample pitch class
                    pitch_flat[:, idx] = self.rng.choice(
                        self.q_pitch, size=self.N, p=self.theta_pitch[v, m, k]
                    )
                    # Sample duration
                    dur_flat[:, idx] = self.rng.choice(
                        self.q_dur, size=self.N, p=self.theta_dur[v, m, k]
                    )
                    # Sample velocity (Gaussian, clipped)
                    vel_flat[:, idx] = np.clip(
                        self.theta_vel[v, m, k, 0]
                        + self.rng.normal(0, 0.15, size=self.N),
                        0.0, 1.0
                    )
        return pitch_flat, dur_flat, vel_flat

    def evaluate_fitness(self, pitch: np.ndarray, dur: np.ndarray, vel: np.ndarray) -> np.ndarray:
        """Compute musical fitness for all candidates.

        Pitch, dur, vel shapes: (N, L)
        Returns: (N,) array of fitness scores.
        """
        N = pitch.shape[0]
        fitness = np.zeros(N)

        for n in range(N):
            # --- Tonal gravity ---
            # Count occurrences per pitch class
            pc_counts = np.bincount(pitch[n] % 12, minlength=12) / self.L
            # Reward tonic (0) and dominant (7) prevalence
            tonal_score = 0.5 * (pc_counts[0] + pc_counts[7])

            # --- Rhythmic coherence ---
            # Reward downbeat-aligned onsets (every K tokens within a section)
            # Simple proxy: uniform onset density with beat-1 bias
            beat1_mask = np.zeros(self.L, dtype=bool)
            for s in range(self.M):
                beat1_idx = s * self.V * self.K + v_idx for v_idx in range(self.V)  # simplified
            rhythm_score = 0.3  # placeholder

            # --- Harmonic fitness (circle of 5ths) ---
            # Simplified: reward V-I chord motion at section boundaries
            harmony_score = 0.3  # placeholder

            # --- Voice-leading (smoothness) ---
            voice_score = 0.2  # placeholder

            # --- Texture density ---
            texture_score = 0.2  # placeholder

            fitness[n] = tonal_score + rhythm_score + harmony_score + voice_score + texture_score

        return fitness

    def update_distributions(self, pitch, dur, vel, fitness):
        """Update categorical distributions via MLE on elite set."""
        # Select elite
        threshold = np.quantile(fitness, 1 - self.rho)
        elite_mask = fitness >= threshold
        n_elite = elite_mask.sum()
        if n_elite < 2:
            n_elite = max(2, int(self.N * self.rho))
            elite_idx = np.argsort(fitness)[-n_elite:]
            elite_mask = np.zeros(self.N, dtype=bool)
            elite_mask[elite_idx] = True

        for v in range(self.V):
            for m in range(self.M):
                for k in range(self.K):
                    idx = v * self.M * self.K + m * self.K + k
                    # Pitch MLE: empirical distribution over elite samples
                    elite_pitch = pitch[elite_mask, idx]
                    pitch_counts = np.bincount(elite_pitch, minlength=self.q_pitch)
                    theta_new_p = (pitch_counts + 1) / (n_elite + self.q_pitch)

                    # Duration MLE
                    elite_dur = dur[elite_mask, idx]
                    dur_counts = np.bincount(elite_dur, minlength=self.q_dur)
                    theta_new_d = (dur_counts + 1) / (n_elite + self.q_dur)

                    # Velocity MLE (Gaussian)
                    elite_vel = vel[elite_mask, idx]
                    theta_new_v = np.mean(elite_vel)

                    # Smooth update
                    self.theta_pitch[v, m, k] = (
                        self.alpha * theta_new_p + (1 - self.alpha) * self.theta_pitch[v, m, k]
                    )
                    self.theta_dur[v, m, k] = (
                        self.alpha * theta_new_d + (1 - self.alpha) * self.theta_dur[v, m, k]
                    )
                    self.theta_vel[v, m, k, 0] = (
                        self.alpha * theta_new_v + (1 - self.alpha) * self.theta_vel[v, m, k, 0]
                    )

    def compose(self, progress_callback: Optional[Callable] = None):
        """Run CEM optimization to fill the UnitMatrix."""
        for t in range(self.T):
            # 1. Sample
            pitch, dur, vel = self.sample_sequences()

            # 2. Evaluate
            fitness = self.evaluate_fitness(pitch, dur, vel)

            # Track best
            best_idx = np.argmax(fitness)
            if fitness[best_idx] > self.best_fitness:
                self.best_fitness = fitness[best_idx]
                self.best_seq = (pitch[best_idx], dur[best_idx], vel[best_idx])

            # 3-4. Update
            self.update_distributions(pitch, dur, vel, fitness)

            # Optional early stopping
            if t > 20 and np.std(
                fitness[np.argsort(fitness)[-int(self.rho * self.N):]]
            ) < 0.01:
                break

            if progress_callback:
                progress_callback(t, self.T, self.best_fitness)

        return self.best_seq

    def decode_to_unitmatrix(self) -> list:
        """Decode best sequence into UnitMatrix-compatible MusicUnit lists."""
        # Placeholder: reshape (L,) sequence back to (V, M, K) and convert to MusicEvent
        pitch, dur, vel = self.best_seq
        units = []
        for v in range(self.V):
            voice_units = []
            for m in range(self.M):
                start = (v * self.M + m) * self.K
                tokens_p = pitch[start:start + self.K]
                tokens_d = dur[start:start + self.K]
                tokens_v = vel[start:start + self.K]
                # Convert to MIDI (simplified: scale degree 0..11 → MIDI 60..71)
                events = [
                    MusicEvent(
                        pitch=int(60 + tp),
                        volume=int(tv * 127),
                        start_tick=k * 480,  # quarter note per token
                        end_tick=(k + td) * 480  # duration in quarter-note multiples
                    )
                    for k, (tp, td, tv) in enumerate(zip(tokens_p, tokens_d, tokens_v))
                ]
                voice_units.append(events)
            units.append(voice_units)
        return units
```

---

## References

- Rubinstein, R. Y. (1997). "Optimization of computer simulation models with rare events." *European Journal of Operational Research* 99, 38–45.
- Rubinstein, R. Y. & Kroese, D. P. (2004). *The Cross-Entropy Method: A Unified Approach to Combinatorial Optimization, Monte-Carlo Simulation, and Machine Learning*. Springer.
- de Boer, P.-T., Kroese, D. P., Mannor, S. & Rubinstein, R. Y. (2005). "A tutorial on the cross-entropy method." *Annals of Operations Research* 134, 655–680. arXiv:0408054.
- Botev, Z. I., Kroese, D. P. & Rubinstein, R. Y. (2013). "The cross-entropy method for optimization." In *Handbook of Statistics* 31, 35–60.
- Hansen, N., Su, H. & Wang, X. (2022). "Temporal Difference Learning for Model Predictive Control." *ICML* 2022. (TD-MPC uses CEM for planning.)
- Huang, K., Lale, S., Rosolia, U., Shi, Y. & Anandkumar, A. (2021). "CEM-GD: Cross-Entropy Method with Gradient Descent Planner." arXiv:2112.07746.

## Candidate Code Path
`generators/cemc_generator.py` — generates UnitMatrix cell contents via stochastic CEM optimization loop.

## Distinction from Similar Methods
- **vs 003 Genetic (Genome)**: CEMC maintains an explicit probability distribution updated via MLE, not a population of individuals subject to crossover/mutation. Population is resampled from scratch each iteration.
- **vs 055 SAMC (Simulated Annealing)**: CEMC evaluates a full batch of N candidates in parallel and updates distribution parameters analytically, not a single candidate with temperature-based acceptance.
- **vs 062 RLPOC (Reinforcement Learning)**: CEMC has no value function, no bootstrapping, no temporal-difference learning — it is a pure black-box optimizer with no neural network.
- **vs 073 HSIC (Harmony Search)**: CEMC uses CE minimization (KL divergence) for distribution update, not memetic operators (HMCR/PAR). CEMC's update is analytical, HSIC's is constructive.
- **vs 097 MaxEnt-C**: CEMC iteratively refines a distribution toward high fitness; MaxEnt-C finds the maximum-entropy distribution consistent with constraints and samples once. CEMC never needs to compute a partition function.
- **vs 098 MOEPC**: CEMC uses scalarized fitness; MOEPC uses Pareto dominance. They could be combined (CEMC with dominance-based elite selection for multi-objective composition).