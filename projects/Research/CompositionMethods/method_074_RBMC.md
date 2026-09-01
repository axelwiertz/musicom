# Method 074 — Restricted Boltzmann Machine Composition (RBM-C)

**Paradigm**: AI-Driven (Deep Generative / Energy-Based)
**Primary Elements**: Pitch, Rhythm, Harmony, Structure, Texture
**Classification**: Tonal Gravity = Strong (Learned-energy) · Metric Binding = Grid-Locked / Continuous · Memory Depth = Macro / Hidden Feature · Time Complexity = $\mathcal{O}(E \cdot N \cdot H)$ training, $\mathcal{O}(N \cdot H)$ per Gibbs step

---

## One-line description

Learns an **energy landscape** over per-voice piano-rolls via a bipartite visible↔hidden Restricted Boltzmann Machine trained by contrastive divergence, then composes by **block Gibbs sampling** from the Boltzmann distribution — hidden units become learned chord/motif/register features that fire jointly to produce coherent multi-voice music, with RNN-RBM recurrence (or a chord/section conditioning schedule) supplying macro-form.

## Why this is novel (not a duplicate)

001–073 already cover hand-crafted Markov Random Fields (064 MRFCC, whose clique potentials are *set by hand*) and Hopfield associative memories (071 HAM-C, whose weights are *Hebbian one-shot stored*). Neither **learns** its energy function from a corpus. RBM-C is the missing **learned, energy-based generative model**: the same Boltzmann/Gibbs mathematics as 064/071, but with the weight matrix $W$ discovered by contrastive divergence so the hidden units become *data-driven musical features* (chords, motifs, registers) rather than hand-tuned or memorized patterns. Verified absent from the DB (grep for "Restricted Boltzmann", "RBM", "contrastive divergence", "Smolensky" → 0 hits). The RNN-RBM (Boulanger-Lewandowski 2012) is the canonical bridge from this to polyphonic symbolic music generation.

---

## Extended mathematics

### 1. The energy function and Boltzmann distribution

An RBM is a bipartite graph: visible units $v \in \{0,1\}^{N}$ (the piano-roll: pitch × time-step × voice onsets) and hidden units $h \in \{0,1\}^{H}$ (learned features), weights $W \in \mathbb{R}^{N \times H}$, biases $a \in \mathbb{R}^N$, $b \in \mathbb{R}^H$. No visible–visible or hidden–hidden edges. The joint energy is

$$E(v, h) = -\sum_i a_i v_i - \sum_j b_j h_j - \sum_{i,j} W_{ij}\, v_i h_j \;=\; -a^\top v - b^\top h - h^\top W v,$$

and the joint probability is the Gibbs/Boltzmann distribution

$$P(v, h) = \frac{1}{Z} e^{-E(v,h)}, \qquad Z = \sum_{v,h} e^{-E(v,h)}.$$

Low energy = high probability = "plausible music"; high energy = noise. Composition is the act of finding low-energy configurations.

### 2. Factorized conditionals (block Gibbs)

Because there are no within-layer edges, the conditional distributions factorize completely:

$$P(h_j = 1 \mid v) = \sigma\!\Big(b_j + \sum_i W_{ij} v_i\Big), \qquad P(v_i = 1 \mid h) = \sigma\!\Big(a_i + \sum_j W_{ij} h_j\Big),$$

with $\sigma(x) = 1/(1+e^{-x})$. One Gibbs step = sample all $h$ given $v$, then all $v$ given $h$. Alternating these steps is a Markov chain whose stationary distribution is exactly $P(v, h)$; after $T$ steps a seed configuration relaxes toward the model's high-probability region.

### 3. Contrastive divergence (CD-k)

The log-likelihood gradient of a data point $v^{(0)}$ is

$$\frac{\partial \log P(v^{(0)})}{\partial W_{ij}} = \langle v_i h_j \rangle_{\text{data}} - \langle v_i h_j \rangle_{\text{model}},$$

where the second term requires samples from the model (intractable because of $Z$). CD-k approximates the model term by running the Gibbs chain $k$ steps from the *data point itself*:

$$\Delta W_{ij} \approx \eta\left( v^{(0)}_i h^{(0)}_j - v^{(k)}_i h^{(k)}_j \right), \qquad h^{(0)}_j = \sigma\!\Big(b_j + \sum_i W_{ij} v^{(0)}_i\Big), \qquad v^{(k)} = \text{Gibbs}^k(v^{(0)}).$$

Bias updates are the same without the outer product: $\Delta a \propto v^{(0)} - v^{(k)}$, $\Delta b \propto h^{(0)} - h^{(k)}$. Persistent CD (PCD) keeps a running set of Markov chains (not restarted at data points) to reduce the CD bias.

### 4. Music-specific visible encodings

- **Binary one-hot**: $v_i \in \{0,1\}$ = a specific (voice, pitch, time-step) is active. The sampled piano-roll *is* the composition.
- **Replicated softmax** (RNN-RBM): each time step has one softmax group over pitch classes plus a "no-note" symbol, so exactly one note fires per step — correct for monophonic lead lines. Energy per softmax group $\mathcal{G}$: $E_{\mathcal{G}} = -\sum_{k \in \mathcal{G}} \left(a_k + \sum_j W_{kj} h_j\right) v_k$ with the constraint $\sum_{k \in \mathcal{G}} v_k = 1$.
- **Gaussian-visible**: $E$ gains $\frac{1}{2}\sum_i (v_i - a_i - \sum_j W_{ij}h_j)^2$ (unit variance), so $v_i$ is real-valued → velocity/duration/dynamics on a continuous axis.

### 5. Conditioning and RNN-RBM

A **conditional RBM** makes the biases affine in a context $c$: $a \leftarrow a + A c$, $b \leftarrow b + B c$. The **RNN-RBM** replaces time-constant biases with a recurrently-evolved context:

$$a^{(t)} = a + A\, h_{rnn}^{(t-1)}, \quad b^{(t)} = b + B\, h_{rnn}^{(t-1)}, \quad h_{rnn}^{(t)} = \tanh\!\Big(W_{rnn}\, v^{(t)} + R\, h_{rnn}^{(t-1)} + b_{rnn}\Big).$$

The RNN hidden state $h_{rnn}$ accumulates the piece's global history and shapes the *local* energy each step — the RNN supplies macro-form grammar, the RBM supplies note-level flesh (the same temporal-split idea as 057 MT-GAC's $G_{temp} \to G_{bar}$).

### 6. Sampling temperature and annealing

At temperature $T$: $P(v) \propto e^{-E(v)/T}$. Low $T$ → crisp, corpus-typical samples (stable groove); high $T$ → exploratory wandering of the energy landscape (variation, passing material). An annealing schedule (hot → cold over Gibbs steps) mirrors 055 SAMC and yields a coherent-to-committed trajectory.

---

## Musical Elements Framework

- **PITCH**: Visible units = one-hot (or replicated-softmax) groups per voice per time step. The sampled $v$ *is* the melody; a firing hidden unit $j$ raises $P(v_i{=}1) = \sigma(a_i + \sum_j W_{ij} h_j)$, biasing the pitch toward the chord tone/register the feature encodes. Tonal gravity is **learned** — a C-major corpus makes out-of-key notes high-energy automatically.
- **RHYTHM**: The time axis is the visible layer's second dimension; onset patterns are the "black pixels" of the sampled piano-roll. Hidden features capture groove (backbeat, tresillo, swing). Conditional RBM (biases affine in a clock/section signal) shifts the onset distribution for grid-locked metric binding; Gaussian-visible models velocity/duration richness.
- **HARMONY**: Hidden units are the model's harmonic vocabulary — a weight vector $W_{j,:}$ is a vertical chord template (all simultaneous pitches of a progression). Harmony generation = *which hidden units fire*; conditioning $b$ on a chord-function vector (HOME/LIFT/TENSE/TURN) makes the model sample pitch configurations consistent with that function. Progression = a sequence of hidden-bias conditions.
- **STRUCTURE**: A plain RBM is memoryless (no recurrent edges). RNN-RBM supplies the section grammar via recurrent hidden state carried across joins; the conditioning schedule $[c_1 \dots c_S]$ = macro-form. Each section samples its own conditional pass with shared RNN state for smooth transitions.
- **TEXTURE**: Active-visible-unit count (or velocity in Gaussian-visible) = texture. Sparse hidden activation → thin texture; dense hidden pattern → full chordal texture. Hidden units can be gated (fixed 0/1) during sampling, so texture density is directly controllable per section.

## UnitMatrix Integration (Voices & Sections)

- **Rows (Voices)**: Each voice = a contiguous visible-unit block (its own pitch × time-step slab). Shared hidden layer → learned **vertical coherence** (a "C-major-triad, bass-root, melody-on-E" feature jointly constrains all voices). Voice independence via weight structure: fully-shared hidden units couple voices (homophony); block-diagonal $W$ decouples them (independent counterpoint). Per-voice conditional bias $a^{(v)}$ marks lead vs. pad vs. bass.
- **Columns (Sections)**: Each section = conditioning vector $c_s$ (chord function, register, density) shifting biases during that section's sampling pass; $[c_1 \dots c_S]$ = macro-form. RNN-RBM carries hidden state across $c_s \to c_{s+1}$ for continuous joins. A section may also be a separately trained RBM crossfaded at the boundary (parallel to 046 VAE latent interpolation).
- **Cells** $U_{v,s}$: `{PITCH}` = sampled visible pitch units decoded to MIDI, `{RHYTHM}` = sampled onset units → ticks, `{HARMONY}` = active hidden features / conditioning chord, `{TEXTURE}` = active-unit count/velocity.
- **Mapping Flow**: train/load RBM on per-voice piano-rolls → define conditioning schedule (macro-form) → per-section block Gibbs sampling → decode visible units to cells → 022 scale-quantize post-filter → `validate()` + musicom export (never hand-roll mido). Sparse samples → honor the hybridization rule (add a 026 DPSM fill voice).

---

## Implementation (Python / NumPy)

```python
from __future__ import annotations
import numpy as np
from numpy.random import default_rng

class RBM:
    """Binary-binary RBM trained by contrastive divergence (Hinton 2002)."""
    def __init__(self, n_vis, n_hid, lr=0.01, seed=0):
        self.rng = default_rng(seed)
        self.W = self.rng.normal(0, 0.01, (n_vis, n_hid))
        self.a = np.zeros(n_vis)
        self.b = np.zeros(n_hid)
        self.lr = lr

    def _sig(self, x):
        return 1.0 / (1.0 + np.exp(-x))

    def _h_given_v(self, v):
        return self._sig(self.b + v @ self.W)

    def _v_given_h(self, h):
        return self._sig(self.a + self.W @ h)

    def _gibbs(self, v, k=1):
        for _ in range(k):
            h = self.rng.binomial(1, self._h_given_v(v))
            v = self.rng.binomial(1, self._v_given_h(h))
        return v

    def train(self, data, epochs=100, k=1):
        for _ in range(epochs):
            for v0 in data:
                h0 = self._h_given_v(v0)
                vk = self._gibbs(v0, k)
                hk = self._h_given_v(vk)
                self.W += self.lr * (np.outer(v0, h0) - np.outer(vk, hk))
                self.a += self.lr * (v0 - vk)
                self.b += self.lr * (h0 - hk)

    def sample(self, v_seed, steps=100, temperature=1.0):
        v = v_seed.copy()
        for _ in range(steps):
            h = self.rng.binomial(1, self._sig((self.b + v @ self.W) / temperature))
            v = self.rng.binomial(1, self._sig((self.a + self.W @ h) / temperature))
        return v

# --- Musicom integration sketch (conceptual — engine does the MIDI authoring) ---
# rolls = corpus_of_piano_rolls(style)            # N x (V*P*T) binary
# rbm = RBM(n_vis=V*P*T, n_hid=512).train(rolls)
# for s in range(num_sections):
#     v = rbm.sample(condition_seed(c_s), steps=200)
#     for voice, pitch_units, onset_units in decode(v):
#         composer.fill_voice_section(voice, s, create_note_unit(pitch, dur, tick))
# ok, msg = composer.validate()   # MUST be True before to_midi (per AGENTS.md)
```

**Tooling**: NumPy suffices for a binary RBM (explicit CD updates); PyTorch/JAX makes energy gradients automatic for Gaussian-visible / RNN-RBM variants. The musicom engine handles UnitMatrix fill and zero-drift MIDI export upstream.

## Pitfalls

1. **Intractable partition function** → exact likelihood (and gradient) uncomputable; only sampling possible. Fix: CD-k/PCD; monitor reconstruction error & log-pseudo-likelihood; never report a likelihood value.
2. **CD bias** → CD-1 underestimates the model term → mushy features. Fix: PCD or $k \ge 10$; L2 weight decay; anneal learning rate.
3. **Poor mixing / mode collapse** → short Gibbs chain stuck in one basin → repeated bars. Fix: more steps, higher temperature, or parallel tempering (multi-chain $T$-swapping, the RBM analogue of 055 SA).
4. **Binary units lose dynamics** → velocity-flat, robotic piano-roll. Fix: Gaussian-visible for velocity/duration; hybrid real-valued density layer; 026 DPSM fills.
5. **Memoryless RBM → no form** → long pieces wander. Fix: RNN-RBM (Boulanger-Lewandowski 2012) or explicit $c_s$ chord/section schedule.
6. **Off-key samples** → corpus-plausible but out of *current* key. Fix: 022 MCWS post-quantization to active scale; or scale-conditioned visible groups gating out-of-key units.
7. **Sparse/staccato output** → low firing rate → mostly silent cells + MIDI tail truncation. Fix: hybridization rule (add continuous fill layer); append absolute silent padding event at `total_section_ticks - 1`.
8. **Single-layer capacity** → only pairwise visible correlations. Fix: deep belief network stack (Hinton et al. 2006) or ConvRBM (Lattner et al. 2018) for translation-invariant features.
9. **Ignoring the validation gate** → high-probability sample can still violate zero-drift. Fix: `composer.validate()`; re-sample or pad on failure.

## References

- Smolensky, P. (1986). "Information processing in dynamical systems: foundations of harmony theory." In Rumelhart & McClelland (eds.), *Parallel Distributed Processing* Vol. 1, MIT Press.
- Hinton, G. E. (2002). "Training products of experts by minimizing contrastive divergence." *Neural Computation* 14(8), 1771–1800.
- Hinton, G. E., Osindero, S., & Teh, Y.-W. (2006). "A fast learning algorithm for deep belief nets." *Neural Computation* 18(7), 1527–1554.
- Boulanger-Lewandowski, N., Bengio, Y., & Vincent, P. (2012). "Modeling temporal dependencies in high-dimensional sequences: application to polyphonic music generation and transcription." *ICML 2012* (arXiv:1206.6392).
- Lattner, S., Grachten, M., & Widmer, G. (2018). "Imposing higher-level structure in polyphonic music generation using convolutional restricted Boltzmann machines and constraints." *ISMIR 2018*.
- Mandel, M., Pascanu, R., Larochelle, H., & Bengio, Y. (2011). "Autotagging music with conditional restricted Boltzmann machines." *arXiv:1103.2832*.
