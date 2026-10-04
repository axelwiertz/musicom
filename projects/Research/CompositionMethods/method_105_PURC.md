# Method 105: Pólya Urn Reinforcement Composition (PURC)

**ID:** 105  
**Acronym:** PURC  
**Layer:** concrete  
**Paradigm:** Stochastic  
**Added:** 2026-10-04  
**Tonal Gravity:** Moderate (Reinforcement-guided, HOME/LIFT/TENSE/TURN via prior)  
**Metric Binding:** Grid-Locked / Continuous  
**Memory Depth:** Meso / Urn State  
**Time Complexity:** $\mathcal{O}(N \cdot K)$ per section (where $N$ = total draws, $K$ = vocabulary size)

---

## Overview

Pólya Urn Reinforcement Composition (PURC) generates musical material by simulating a **self-reinforcing Pólya urn process** for each musical dimension. The urn contains balls of $K$ colors representing the token vocabulary (pitch classes, scale degrees, duration labels, velocity levels, chord functions). At each step, a ball is drawn uniformly at random, its color is recorded (this is the musical event), and the ball is returned along with an *additional ball of the same color* — a positive feedback loop known as "the rich get richer" or preferential attachment.

This creates sequences where:
- **Frequent tokens become more frequent** → motifs and repeated patterns emerge naturally
- **First-mover advantage** → early pitches/rhythms dominate, establishing a musical identity
- **Exchangeability** → the joint distribution is symmetric under permutation (de Finetti representation)
- **Power-law asymptotics** → the distribution of tokens converges to a Dirichlet distribution with Zipfian rank-frequency (complementing method 084 ZMRC)
- **Controllable novelty** → innovation parameter allows controlled introduction of new material

## Mathematical Formulation

### Standard Pólya Urn

An urn initially contains $a_i \ge 0$ balls of color $i$, for $i = 1, \ldots, K$. Total initial balls: $A = \sum_i a_i$.

At each discrete step $t = 1, \ldots, N$:

1. Draw a ball uniformly at random from the urn.
2. Record its color $c_t$.
3. Return the drawn ball **plus one additional ball of the same color**.

The probability of drawing color $i$ at step $t+1$, given $n_i = \sum_{s=1}^t \mathbf{1}[c_s = i]$ previous draws of color $i$, is:

$$P(c_{t+1} = i \mid n_1, \ldots, n_K) = \frac{a_i + n_i}{A + t}$$

After $N$ draws, the count vector $\mathbf{n} = (n_1, \ldots, n_K)$ follows the **Dirichlet-multinomial (Pólya) distribution**:

$$P(\mathbf{n}) = \frac{N!}{\prod_i n_i!} \cdot \frac{\prod_i (a_i)^{\overline{n_i}}}{A^{\overline{N}}}$$

where $x^{\overline{m}} = x(x+1)\cdots(x+m-1)$ denotes the rising factorial.

### Marginal Distribution (Beta-Binomial, $K=2$)

For a binary urn (e.g., hit/silence, on-beat/off-beat), the probability of observing $k$ draws of color 1 out of $N$ total draws is:

$$P(k \mid N, a_1, a_2) = \binom{N}{k} \frac{B(k+a_1, N-k+a_2)}{B(a_1, a_2)}$$

where $B$ is the Beta function. This is the Beta-binomial distribution.

### Expected Evolution

The expected fraction of color $i$ after $N$ draws is:

$$\mathbb{E}[n_i / N] \approx \frac{a_i}{A} \text{ for } N \ll A \quad\text{(prior-dominated)}$$
$$\mathbb{E}[n_i / N] \to \text{Dirichlet}(\mathbf{a}) \text{ for } N \to \infty \quad\text{(asymptotic)}$$

The actual fraction converges to a random variable drawn from $\text{Dirichlet}(\mathbf{a})$, not to a fixed value — the urn does not "forget" its early random fluctuations.

### Innovation via Urn with Expanding Colors (Tria et al. 2014)

To allow genuinely new material not present in the initial vocabulary, a **triggering mechanism** is added:

$$P(\text{existing token } i) \propto a_i + n_i$$
$$P(\text{new token}) \propto \nu$$

where $\nu \ge 0$ is the innovation rate. When a new token is triggered, its color is novel (a previously unused pitch, duration, or chord) and the urn is augmented with an initial count of $a_{\text{new}}$ balls of that color.

New token types are drawn from a base distribution $G_0$ (e.g., uniform over the chromatic scale for pitch, or over a set of common durations for rhythm). This turns the Pólya urn into a **Dirichlet process** (in the $d=0$ case) or a **Pitman-Yor process** (in the $d>0$ case).

### Pitman-Yor Generalization

The two-parameter Poisson-Dirichlet / Pitman-Yor process introduces a **discount parameter** $d \in [0, 1)$ and a **strength parameter** $\theta > -d$:

$$P(c_{t+1} = \text{existing token } i \mid n_i) = \frac{n_i - d}{\theta + t}$$
$$P(c_{t+1} = \text{new token}) = \frac{\theta + d \cdot k}{\theta + t}$$

where $k$ is the number of distinct token types already observed (the "richness"). Key behaviors:
- $d = 0$: Standard Dirichlet process / Pólya urn (exponential tail).
- $d > 0$: **Power-law tail** — frequent tokens are *suppressed* by $-d$, actually making the tail heavier and more Zipfian (better match to real music statistics).
- $\theta$ large: Strong tendency toward new tokens (exploratory).
- $\theta$ small: Strong tendency to stick with existing tokens (exploitative).

## Musical Rationale

PURC is motivated by several empirical observations about real music:

1. **Zipf's law in music** (Manaris 2003, Zanette 2006): Pitch classes, intervals, and rhythm tokens in tonal music follow power-law (Zipf-Mandelbrot) distributions. The Pólya urn naturally generates such distributions.

2. **Motif persistence**: Real melodies are characterized by repeated patterns (motifs). The reinforcement mechanism creates exactly this — once a 2- or 3-note pattern appears, its constituent tokens become more likely, increasing the probability of the same pattern recurring.

3. **First-mover advantage in composition** (Simon 1955): The first few notes of a piece strongly influence its character. In the Pólya urn, early draws have outsized influence on the rest of the sequence — mirroring this cognitive phenomenon.

4. **Non-stationarity through innovation**: Music develops over time — new material appears. The innovation parameter $\nu$ provides a mathematically principled way to introduce novelty, directly connected to Bayesian nonparametric statistics (the Dirichlet process).

## Relation to the UnitMatrix

### Voices (Rows)

Each voice has its own set of urns. The **coupling** between voices is controlled by a shared harmonic state:

| Voice Role | Pitch Urn Prior ($a_i$) | Dur Urn | Innovation ($\nu$) | Discount ($d$) |
|---|---|---|---|---|
| Lead | High tonic/dominant, moderate chromatic | Short to medium durations | Medium | 0.1–0.3 |
| Bass | Very high tonic, low chromatic, low others | Long durations | Low | 0.0–0.1 |
| Pad | High chord tones only, zero non-chord | Very long durations | Very low | 0.0 |
| Percussion | Binary: hit/silence on partition | Onset grid positions | None | N/A |

**Coupling mechanism**: When a voice draws a chord-functional token (from its harmony urn), the compatible pitch counts in all other voices' urns are boosted by $\gamma > 0$ for that step. This is a form of **multi-urn coupling**:

$$a_i^{(w)} \gets a_i^{(w)} + \gamma \cdot \mathbf{1}[\text{pitch } i \in \text{chord}(c_v)]$$

where $c_v$ is the chord drawn by voice $v$ from its harmony urn, and chord($c_v$) is the set of pitch classes that constitute chord $c_v$.

### Sections (Columns)

Each section $s$ defines a full urn configuration vector $\Theta_s = \{\mathbf{a}_s, \nu_s, d_s, \lambda_s\}$:

- **Prior vector** $\mathbf{a}_s$: encodes the tonal center, rhythmic density, and register for the section.
- **Innovation rate** $\nu_s$: controls how much new material appears.
- **Pitman-Yor discount** $d_s$: controls the balance between focused repetition ($d$ small) and varied vocabulary ($d$ large).
- **Carry-over factor** $\lambda_s \in [0, 1]$: fraction of the previous section's urn state retained. $\lambda = 0$ = clean reset (new section, fresh material), $\lambda = 1$ = continuous (through-composed development).

A typical macro-form trajectory:

| Section | $a_{\text{tonic}}$ | $\nu$ | $d$ | $\lambda$ |
|---|---|---|---|---|
| Intro | High | 0.05 | 0.1 | 0.0 |
| Verse | Medium | 0.1 | 0.2 | 0.3 |
| Chorus | High | 0.02 | 0.05 | 0.4 |
| Bridge | Low | 0.3 | 0.5 | 0.1 |
| Outro | High | 0.01 | 0.0 | 0.5 |

### Cells (MusicUnit)

Each cell is filled by drawing $M$ events from the voice's coupled urn system, where $M$ is determined by the cell's time allocation (in ticks) and the durations drawn. The zero-drift invariant is maintained by ensuring the sum of drawn durations equals the section length.

## Algorithm

```
function generate_section(urns, section_len_ticks, voice_roles):
    for each voice v:
        reset or carry-over urn state for v
    t = 0
    while t < section_len_ticks:
        for each active voice v:
            c_pitch = draw_from_urn(urns[v].pitch)
            c_dur = draw_from_urn(urns[v].duration)
            c_vel = draw_from_urn(urns[v].velocity)
            record_note(v, c_pitch, c_vel, t, t + c_dur)
            update_urns(urns[v], c_pitch, c_dur, c_vel)  # reinforcement
            couple_voices(urns, c_pitch, gamma)           # vertical coherence
            if t + c_dur > section_len_ticks:
                truncate_note_duration(section_len_ticks - t)
        t += min_draw(voices)  # advance by the smallest duration drawn
```

The alias method provides $\mathcal{O}(1)$ draws:

```
# Alias table for urn with K colors
probs = [a_i + n_i for i in range(K)]
total = sum(probs)
alias_table = AliasMethod(probs)

for each draw:
    color = alias_table.sample()
    n_i += 1
    total += 1
    alias_table.update(color, probs[color] + 1)
```

## Connection to Bayesian Nonparametrics

PURC is the sequential generative process underlying the **Dirichlet process** (DP) and **Pitman-Yor process** (PYP):

| Model | Urn Analogy | Use Case |
|---|---|---|
| Dirichlet Process DP($\alpha, G_0$) | Pólya urn with $\nu = \alpha$, $d = 0$ | Standard reinforcement, exponential tail |
| Pitman-Yor Process PYP($\alpha, d, G_0$) | Pólya urn with $\nu = \alpha$, $d > 0$ | Power-law tail, long-tail phenomena |
| Hierarchical DP HDP($\alpha, \beta, G_0$) | Nested urns (corpus-level → piece-level) | Multi-style composition |

This means PURC can be extended to **learn** urn parameters from existing music via Dirichlet-process mixture model inference (collapsed Gibbs sampling or variational inference).

## Contrast to Related Methods

| Method | PURC vs. |
|---|---|
| **002 Markov** | PURC has **growing** probabilities (reinforcement), Markov has **fixed** transition matrix. Markov is stationary; PURC is non-stationary with exchangeability. |
| **053 LFC** | Lévy Flight generates step-length power laws directly; PURC generates token-count power laws (the two are related by the length-of-stay distribution). |
| **061 GPC** | Gaussian Process imposes covariance structure through a kernel; PURC imposes reinforcement through incremental count updates. GP is a prior over functions; PURC is a sequential process. |
| **064 MRFCC** | MRF is an undirected graphical model with pairwise potentials on a fixed lattice; PURC is a directed sequential process with growing state. |
| **067 FOGI** | Factor Oracle builds a determinized suffix automaton from a corpus; PURC has no automaton, only a count vector. |
| **068 CME-SSA** | Chemical Master Equation models mass-action kinetics with multiple reaction channels; PURC models a single urn with reinforcement. |
| **084 ZMRC** | Zipf-Mandelbrot imposes a **static** rank-frequency law; PURC **generates** the power-law sequentially. ZMRC describes *what* distribution to match; PURC describes *how* to produce it draw by draw. |
| **086 HMM** | HMM has a hidden Markov state chain with emission probabilities; PURC has no hidden states — the entire history is summarized by the count vector. |
| **097 MaxEnt-C** | MaxEnt finds the maximum-entropy distribution consistent with pairwise constraints, then samples from it; PURC is a specific parametric generative process (Dirichlet-multinomial) with reinforcement dynamics. |

## Implementation Sketch (Python)

```python
import random
import numpy as np
from collections import Counter

def draw_color(counts, innovation_rate=0.0, base_generator=None):
    """Draw from a Pólya urn with optional innovation."""
    total = sum(counts.values())
    if innovation_rate > 0 and random.random() < innovation_rate / (innovation_rate + total):
        # Innovation: generate a novel token
        new_token = base_generator() if base_generator else f"new_{random.randint(0, 999)}"
        counts[new_token] = counts.get(new_token, 0) + 1
        return new_token, True
    # Standard Pólya draw
    r = random.randint(0, total - 1)
    cum = 0
    for token, cnt in counts.items():
        cum += cnt
        if r < cum:
            counts[token] = cnt + 1  # reinforcement
            return token, False
    raise RuntimeError("Should not reach")

class AliasMethod:
    """O(1) sampling from a multinomial via Vose's alias method."""
    def __init__(self, weights):
        self.n = len(weights)
        self.probs = np.zeros(self.n)
        self.alias = np.zeros(self.n, dtype=int)
        total = sum(weights)
        scaled = [w * self.n / total for w in weights]
        small, large = [], []
        for i, w in enumerate(scaled):
            (small if w < 1.0 else large).append(i)
        while small and large:
            s, l = small.pop(), large.pop()
            self.probs[s] = scaled[s]
            self.alias[s] = l
            scaled[l] = (scaled[l] + scaled[s]) - 1
            (small if scaled[l] < 1.0 else large).append(l)
        for i in small + large:
            self.probs[i] = 1.0
    
    def sample(self):
        i = random.randint(0, self.n - 1)
        return i if random.random() < self.probs[i] else self.alias[i]

    def update(self, idx, new_weight):
        """Recompute alias table (O(n)). For frequent updates, use Fenwick tree instead."""
        total = sum(self.probs)  # approximate; recompute properly
        # In practice: use a Fenwick tree for O(log n) increment/decrement
        pass  # placeholder — full rebuild is O(n) per draw

class UrnVoice:
    def __init__(self, pitch_prior, dur_prior, vel_prior):
        self.pitch_counts = Counter(pitch_prior)
        self.dur_counts = Counter(dur_prior)
        self.vel_counts = Counter(vel_prior)
    
    def draw_note(self, innovation_rate=0.0):
        pitch, is_new_p = draw_color(self.pitch_counts, innovation_rate)
        dur, is_new_d = draw_color(self.dur_counts, 0.0)  # No innovation for duration
        vel, is_new_v = draw_color(self.vel_counts, 0.0)
        return {'pitch': pitch, 'duration': dur, 'velocity': vel, 'is_new': is_new_p}

class PólyaUrnComposer:
    def __init__(self, voices, section_params, coupling_gamma=0.5):
        self.voices = voices
        self.section_params = section_params
        self.gamma = coupling_gamma
    
    def compose(self):
        matrix = []
        for s, params in enumerate(self.section_params):
            section_notes = self._generate_section(s, params)
            matrix.append(section_notes)
        return matrix
    
    def _generate_section(self, s_idx, params):
        notes = {v: [] for v in range(len(self.voices))}
        tick = 0
        while tick < params['len_ticks']:
            for v_idx, voice in enumerate(self.voices):
                note = voice.draw_note(params['nu'])
                dur_ticks = self._dur_to_ticks(note['duration'])
                if tick + dur_ticks > params['len_ticks']:
                    dur_ticks = params['len_ticks'] - tick
                notes[v_idx].append((tick, note['pitch'], dur_ticks, note['velocity']))
                # Coupling: boost compatible pitches in other voices
                if self.gamma > 0 and hasattr(note['pitch'], 'chord'):
                    for w_idx, w_voice in enumerate(self.voices):
                        if w_idx != v_idx:
                            for p in note['pitch'].chord:
                                w_voice.pitch_counts[p] += self.gamma
            tick += min(self._dur_to_ticks(self.voices[v].dur_counts.most_common(1)[0][0])
                        for v in range(len(self.voices)))
            if tick >= params['len_ticks']:
                break
        return notes
```

## References

1. Pólya, G. (1923). "Über verschiedene Aufgaben der Wahrscheinlichkeitsrechnung." — The original urn formulation.
2. Eggenberger, J. & Pólya, G. (1923). "Über die Statistik verketteter Vorgänge." *Zeitschrift für Angewandte Mathematik und Mechanik* 1, 279–289.
3. Mahmoud, H. (2008). "Pólya Urn Models." Chapman and Hall/CRC. ISBN 978-1420059830. — Comprehensive textbook.
4. Pitman, J. & Yor, M. (1997). "The two-parameter Poisson-Dirichlet distribution derived from a stable subordinator." *Annals of Probability* 25, 855–900. — Pitman-Yor generalization.
5. Tria, F., Loreto, V., Gravino, P. & Servedio, V.D.P. (2014). "The dynamics of correlated novelties." *Nature Communications* 5, 136–145.
6. Simon, H. A. (1955). "On a class of skew distribution functions." *Biometrika* 42, 425–440. — Yule-Simon / preferential attachment.
7. Manaris, B., et al. (2003). "Zipf's law, power laws, and music." — Empirical basis for Zipfian pitch/interval distributions.
8. Teh, Y. W. (2010). "Dirichlet Process." *Encyclopedia of Machine Learning*. Springer. — Connection to Bayesian nonparametrics.