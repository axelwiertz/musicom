# Maximum Entropy Composition (MaxEnt-C) — Method 097

## Classification

| Field | Value |
|---|---|
| **Method ID** | 097 |
| **Layer** | concrete |
| **Paradigm** | Stochastic |
| **Primary Elements** | Pitch, Rhythm, Harmony, Structure, Texture |
| **Tonal Gravity** | Moderate (Constraint-guided) |
| **Metric Binding** | Grid-Locked / Continuous |
| **Memory Depth** | Macro / Boltzmann-Gibbs Ensemble |
| **Time Complexity** | $\mathcal{O}(K \cdot q^2 \cdot N)$ learning, $\mathcal{O}(I \cdot N \cdot q)$ sampling |

## Source

Sakellariou, J., Tria, F., Loreto, V. & Pachet, F. (2017). "Maximum entropy models capture melodic styles." *Scientific Reports* 7, 9172. DOI: 10.1038/s41598-017-08028-4. arXiv:1610.03414 [stat.ML].

Jaynes, E. T. (1957). "Information theory and statistical mechanics." *Physical Review* 106, 620–630.

## Principle: Jaynes' Maximum Entropy

Given a set of testable constraints (empirical averages of functions over the data), the **least biased** probability distribution is the one that maximizes Shannon entropy $H = -\sum P \log P$ subject to those constraints (Jaynes 1957). Any lower-entropy distribution would introduce structure not justified by the constraints.

For music: constraints are typically the marginal frequencies of musical tokens (pitch classes, durations, chord labels) and their pairwise co-occurrence statistics at multiple distances.

## Mathematical Formulation

### Boltzmann-Gibbs Distribution

The MaxEnt solution for pairwise constraints at distances $k = 1 \ldots K_{\max}$ is:

$$P(s_1, \ldots, s_N) = \frac{1}{Z} \exp\left( \sum_{i=1}^{N} h_{s_i} + \sum_{k=1}^{K_{\max}} \sum_{i=1}^{N-k} J_k(s_i, s_{i+k}) \right)$$

where:
- $s_i \in \{1, \ldots, q\}$ = musical token at position $i$ (pitch class, duration class, chord symbol)
- $h_a$ = local field (bias) for token $a$ — controls unary frequencies
- $J_k(a,b)$ = interaction potential between tokens $a$ and $b$ at distance $k$ — controls pairwise statistics
- $Z$ = partition function: $\sum_{\{s\}} \exp(\cdots)$

This is a **Potts model** ($q$-state generalization of the Ising model) on a 1D chain with distance-dependent couplings.

### Parameter Learning

Exact maximum likelihood requires computing $Z$, which sums over $q^N$ configurations — intractable for $N > 20$. Two practical approaches:

**1. Pseudo-likelihood (PL)**: Maximize the product of conditional probabilities:

$$\mathcal{L}_{\text{PL}} = \sum_{i=1}^{N} \log P(s_i | s_{\setminus i})$$

where $P(s_i | s_{\setminus i})$ depends only on the Markov blanket (nearby positions within $K_{\max}$). PL is convex and consistent for Potts models. Solved via L-BFGS or iterative scaling.

**2. Minimum Probability Flow (MPF)**: Minimize the KL divergence between the data distribution and the distribution after an infinitesimal step of MCMC dynamics.

**3. Contrastive Divergence (CD)**: Run $L$ Gibbs steps from a data sample, then update parameters to reduce the energy of data samples relative to the model samples.

### Sampling / Generation

Sample from $P$ via MCMC:

- **Metropolis-Hastings**: Propose a single-site flip $s_i \to s_i'$ with acceptance:

  $$A = \min\left(1, \frac{P(s')}{P(s)}\right) = \min\left(1, \exp(-\Delta E)\right)$$

  where $\Delta E = [h_{s_i'} - h_{s_i}] + \sum_{k: i \pm k \in [1,N]} [J_k(s_{i-k}, s_i') - J_k(s_{i-k}, s_i) + J_k(s_i', s_{i+k}) - J_k(s_i, s_{i+k})]$

- **Gibbs sampling**: Resample $s_i$ from its full conditional:

  $$P(s_i | s_{\setminus i}) \propto \exp\left(h_{s_i} + \sum_{k=1}^{K_{\max}} [J_k(s_{i-k}, s_i) + J_k(s_i, s_{i+k})]\right)$$

  Faster mixing than Metropolis because every proposal is accepted.

- **Wolff cluster algorithm** (for ferromagnetic $J_k$): Flip entire connected clusters of aligned spins simultaneously — dramatically reduces critical slowing down near phase transitions.

### Relation to Markov Models

Unlike a $k$-th order Markov chain whose parameters scale as $q^{k+1}$ (exponential in order), MaxEnt-C parameters scale as $K_{\max} \cdot q^2$ (linear in interaction range). The $K_{\max}$ parameter acts as a **smooth structural dial**: $K_{\max}=1$ captures adjacent transitions only (pairwise Markov equivalent), $K_{\max}>1$ captures phrase-level and period-level constraints simultaneously.

Critically, MaxEnt-C does NOT factorize as $P(s_i | s_{i-1}, \ldots, s_{i-k})$ — it's an **undirected** model. This means long-range structure is not imposed via sequential conditioning but emerges from competing pairwise interactions. Sakellariou et al. (2017) showed this outperforms fixed-order and variable-order Markov models in reproducing melodic statistics without plagiarism.

## Musical Elements Framework

### PITCH

**Representation**: Tokens are pitch classes ($q=12$), scale degrees ($q=7$), or MIDI note numbers ($q=128$).

**Tonal gravity via local fields $h$**: Set $h_{\text{tonic}} > h_{\text{dominant}} > h_{\text{mediant}} > h_{\text{chromatic}}$ to bias marginal probabilities. The log-odds ratio $\log(P(\text{tonic})/P(\text{chromatic})) \approx h_{\text{tonic}} - h_{\text{chromatic}}$ directly controls tonal stability.

**Melodic contour via $J_k$**: 
- $J_1(a,b)$: Interval preference (step vs. leap). Positive values for $|a-b| \in \{1,2\}$ (conjunct), negative for large intervals.
- $J_2(a,b)$: Neighbor-tone and passing-tone patterns. $J_2(a,a)$ favors the same pitch after one intervening note (neighbor tone pattern).
- $J_{k>2}(a,b)$: Phrase-level arch and melodic shape. $J_4(a,a)$ would favor a return to the same pitch after 4 notes (melodic arch).

**Alphabet selection**: A recommended encoding uses the **diatonic index** (0–6) plus an accidental flag, yielding $q=12$ but with hierarchical structure: $h(\text{C}) > h(\text{C#})$ when C is in-scale.

### RHYTHM

**Representation**: Duration labels (whole=0, half=1, quarter=2, eighth=3, sixteenth=4) or IOI classes. Alternative: binary onset vector ($q=2$: onset or no onset per grid slot).

**Metric binding**: Couple the rhythm chain with a fixed periodic "beat phase" token $b_i = i \bmod P$ (where $P = \text{subdivisions per bar}$) via $J_{\text{metric}}(dur_i, b_i)$. Positive $J$ for longer durations on strong beats.

**Groove dynamics**: $J_1^{\text{rhythm}}$ captures short–long and long–short patterns (syncopation). $J_k^{\text{rhythm}}$ for $k$ corresponding to 2, 4, 8 bars captures periodicity and groove repetition. Learning from a corpus automatically encodes the corpus's characteristic rhythmic profiles.

### HARMONY

**Representation**: Chord quality classes (major, minor, dim, aug, sus4, dom7, maj7, m7, dim7) × root pitch class = up to $q=12 \times 5 = 60$ tokens.

**Functional grammar via stationary distribution**: The local field $h$ of the isolated chord model yields a stationary distribution $\pi(c) \propto e^{h_c}$, which biases toward tonic chords (C, Am) and away from unstable chords (Bdim).

**Transition grammar via $J_1$**: $J_1(c_i, c_{i+1})$ encodes chord transition weights (IV–V–I is highly favored, V–IV is less so). These are learned from a corpus or designed explicitly for a style.

**Multi-voice harmony**: The full model couples $V$ independent Potts chains (one per voice) via cross-chain interaction terms:

$$P = \frac{1}{Z} \exp\left( \sum_{v} [\cdots] + \sum_{v<w} \sum_{i} J_{\text{cross}}^{(v,w)}(s_i^{(v)}, s_i^{(w)}) \right)$$

The cross-terms $J_{\text{cross}}(a,b)$ favor consonant intervals (thirds, sixths, perfect fifths) and discourage dissonant clusters. This is equivalent to a 2D Potts model where rows = voices, columns = time.

### STRUCTURE

**$K_{\max}$ as a form dial**:
- $K_{\max} = 2$: Local ornamentation only (motif-level)
- $K_{\max} = 8$: Phrase-level (2-bar patterns)
- $K_{\max} = 16$: Period-level (4-bar antecedent/consequent)
- $K_{\max} = 32$: Section-level (8-bar phrases)

**Section switching via non-stationarity**: Compose with piecewise-constant parameters $\theta_m = (h_m, J_{k,m})$ for section $m$. Form = sequence $(\theta_1, \ldots, \theta_M)$. Transition sections linearly interpolate potentials.

**Entropy as a structural metric**: Compute the entropy rate $h_\infty$ per section:

$$h_\infty = -\lim_{N\to\infty} \frac{1}{N} \log Z_N$$

Lower $h_\infty$ = more deterministic/constrained section (chorus, structural downbeat); higher $h_\infty$ = more chaotic (bridge, development). The form trajectory in entropy-space provides a quantitative tension curve.

### TEXTURE

**Voice coupling via inter-chain $J_k$**:
- Strong $J_{\text{cross}}$ → homophony (voices move in lockstep)
- Weak $J_{\text{cross}}$ → polyphony (independent voices)
- Intermediate $J_{\text{cross}}$ → melody + accompaniment

**Temperature $\beta$ as texture density**: Scale all potentials by $\beta$:

$$P_\beta \propto \exp(\beta \cdot \text{energy})$$

- $\beta \to 0$: Uniform distribution → fully random, pointillistic texture (maximum entropy/uncertainty)
- $\beta = 1$: Standard model → learned statistics
- $\beta \to \infty$: MAP sequence → frozen, deterministic texture

**Expected density at equilibrium**: The expected number of note onsets per time window under $P_\beta$ can be derived from the Potts model's magnetization (expected fraction of active tokens). This acts as a texture density knob.

## UnitMatrix Integration

### Voices

Each voice $v$ is a separate Potts chain with:
- Own alphabet $q^{(v)}$ (e.g., piano: 88 MIDI notes; bass: 128 MIDI notes limited to low register; percussion: $\{0,1\}$)
- Own parameters $\theta^{(v)} = (h^{(v)}, J_k^{(v)})$
- Cross-chain coupling $J_{\text{cross}}^{(v,w)}(s_i^{(v)}, s_i^{(w)})$ with other voices at the same time step

**Percussion voice**: 2-state Potts ($q=2$: hit/no-hit) with rhythm-only $J_k$. Equivalent to a Bernoulli process with pairwise memory.

**Implementation**: $V$ parallel MCMC chains. Each sweep updates all sites in all voices. Cross-terms enforce harmonic coherence after every sweep.

### Sections

Sections in the UnitMatrix map directly to parameter regions:

| Section | $h$, $J_k$ | $K_{\max}$ | $\beta$ | Entropy $h_\infty$ | Role |
|---|---|---|---|---|---|
| Intro | Low contrast, narrow range | 4 | 0.8 | Moderate | Setup |
| Verse A | Medium contrast | 8 | 1.0 | Medium | Narrative |
| Chorus | High tonic bias, strong $J_1$ | 8 | 1.5 | Low | Anchor |
| Bridge | Weak fields, wide $K_{\max}$ | 16 | 0.6 | High | Tension |
| Outro | Fade: $\beta \to 0$, $h \to$ uniform | 4 | 0.3 → 0 | Max | Dissolve |

### Cell Filling Algorithm

```
For each cell (voice v, section m):
  1. Set parameters to θ_m^{(v)}
  2. Seed first token: s_1 = last token of previous cell (voice-leading)
  3. Run N_gibbs Gibbs sweeps through the cell's S token positions
  4. Decode token sequence → MusicEvent[] (pitch + duration)
  5. Pack into MusicUnit and place in UnitMatrix[v][m]
```

The number of Gibbs sweeps $N_{\text{gibbs}}$ is set by autocorrelation time $\tau_{\text{int}}$ of the energy time series (typically 10–100 sweeps).

## Python Implementation Sketch

```python
import numpy as np
from scipy.optimize import minimize

class MaxEntComposer:
    def __init__(self, q=12, Kmax=8, beta=1.0):
        self.q = q          # alphabet size
        self.Kmax = Kmax    # max interaction range
        self.beta = beta    # inverse temperature
        self.h = np.zeros(q)          # local fields
        self.J = np.zeros((Kmax, q, q))  # interaction potentials

    def learn_from_corpus(self, sequences, l2_reg=1e-3):
        """
        Learn h and J from list of token sequences via pseudo-likelihood.
        sequences: list of 1D np arrays of ints in [0, q-1]
        """
        def neg_pl(params):
            h = params[:self.q]
            J = params[self.q:].reshape(self.Kmax, self.q, self.q)
            nll = 0.0
            for seq in sequences:
                N = len(seq)
                for i in range(N):
                    # Energy of token a at position i
                    energy = h[seq[i]]
                    for k in range(1, min(self.Kmax+1, N-i)):
                        energy += J[k-1, seq[i], seq[i+k]]
                    for k in range(1, min(self.Kmax+1, i+1)):
                        energy += J[k-1, seq[i-k], seq[i]]
                    # Z_i = sum over all q tokens
                    Z_i = 0.0
                    for a in range(self.q):
                        e = h[a]
                        for k in range(1, min(self.Kmax+1, N-i)):
                            e += J[k-1, a, seq[i+k]]
                        for k in range(1, min(self.Kmax+1, i+1)):
                            e += J[k-1, seq[i-k], a]
                        Z_i += np.exp(e)
                    nll -= (energy - np.log(Z_i))
            # L2 regularization
            nll += l2_reg * np.sum(params**2)
            return nll

        x0 = np.zeros(self.q + self.Kmax * self.q * self.q)
        res = minimize(neg_pl, x0, method='L-BFGS-B')
        self.h = res.x[:self.q]
        self.J = res.x[self.q:].reshape(self.Kmax, self.q, self.q)
        return self

    def sample_gibbs(self, N, n_sweeps=100, seed_token=None):
        """Generate a sequence of N tokens via Gibbs sampling."""
        s = np.random.randint(0, self.q, size=N).astype(int)
        if seed_token is not None:
            s[0] = seed_token

        for _ in range(n_sweeps):
            for i in range(N):
                # Compute conditional energy for each token a
                energies = np.zeros(self.q)
                for a in range(self.q):
                    e = self.h[a]
                    for k in range(1, min(self.Kmax + 1, N - i)):
                        e += self.J[k-1, a, s[i+k]]
                    for k in range(1, min(self.Kmax + 1, i + 1)):
                        e += self.J[k-1, s[i-k], a]
                    energies[a] = self.beta * e
                # Gibbs sample
                probs = np.exp(energies - np.max(energies))
                probs /= probs.sum()
                s[i] = np.random.choice(self.q, p=probs)
        return s

    def compose_section(self, N, n_gibbs=100, seed_token=None):
        """Sample a section of N tokens."""
        return self.sample_gibbs(N, n_sweeps=n_gibbs, seed_token=seed_token)

    def compose_multi_voice(self, voices_params, length, n_gibbs=100, cross_J=None):
        """
        Generate for multiple coupled voices.
        voices_params: list of (MaxEntComposer instance, seed) per voice
        cross_J: (V, V, q, q) — cross-voice interaction potentials
        """
        V = len(voices_params)
        S = np.random.randint(0, self.q, size=(V, length)).astype(int)

        for _ in range(n_gibbs):
            for v in range(V):
                for i in range(length):
                    energies = np.zeros(self.q)
                    for a in range(self.q):
                        e = voices_params[v][0].h[a]
                        for k in range(1, min(self.Kmax + 1, length - i)):
                            e += voices_params[v][0].J[k-1, a, S[v, i+k]]
                        for k in range(1, min(self.Kmax + 1, i + 1)):
                            e += voices_params[v][0].J[k-1, S[v, i-k], a]
                        # Cross-voice coupling
                        if cross_J is not None:
                            for w in range(V):
                                if w != v:
                                    e += cross_J[v, w, a, S[w, i]]
                        energies[a] = self.beta * e
                    probs = np.exp(energies - np.max(energies))
                    probs /= probs.sum()
                    S[v, i] = np.random.choice(self.q, p=probs)
        return S
```

### UnitMatrix integration code sketch

```python
from structures import UnitMatrix, MusicUnit, MusicEvent
from workflows.unitmatrix_composer import create_note_unit, UnitMatrixComposer

def fill_cell_with_maxent(
    composer: UnitMatrixComposer,
    voice: str, section: str,
    model: MaxEntComposer,
    n_tokens: int = 8,
    seed_token: int | None = None
):
    """Fill a UnitMatrix cell using MaxEnt-C sampling."""
    tokens = model.compose_section(n_tokens, seed_token=seed_token)
    # Decode tokens to pitch events (simple: map token 0→60, 1→62, ...)
    events = []
    tick = 0
    ticks_per_token = 240  # 1/8 note at 120bpm, 480 tpb
    for t in tokens:
        pitch = 60 + t       # crude mapping; use scale degrees in practice
        events.append(MusicEvent(pitch, 80, tick, tick + ticks_per_token))
        tick += ticks_per_token
    # Pad to section length
    section_len = composer._get_section_len(section)
    unit = create_note_unit(pitch=60, duration=min(tick, section_len))
    if events:
        from workflows.unitmatrix_composer import _unit_from_events
        unit = _unit_from_events(events, section_len)
    composer.fill_voice_section(voice, section, unit)
```

## References

1. Sakellariou, J., Tria, F., Loreto, V. & Pachet, F. (2017). "Maximum entropy models capture melodic styles." *Scientific Reports* 7, 9172.
2. Jaynes, E. T. (1957). "Information theory and statistical mechanics." *Physical Review* 106, 620–630.
3. Schneidman, E., Berry, M. J., Segev, R. & Bialek, W. (2006). "Weak pairwise correlations imply strongly correlated network states in a neural population." *Nature* 440, 1007–1012.
4. Baxter, R. J. (1982). *Exactly Solved Models in Statistical Mechanics*. Academic Press.
5. Moulieras, S. & Pachet, F. (2016). "Maximum entropy models for generation of expressive music." *arXiv:1610.03606*.