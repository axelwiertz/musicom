# Non-negative Matrix Factorization Composition (NMF-C)

**Method ID**: 085
**Paradigm**: AI-Driven
**Layer**: concrete (emits note/chord events into UnitMatrix cells; feeds `generators/`)
**Candidate code path**: `generators/nmf_composition.py`
**Acronym**: NMF-C

## One-line description

Factors a piano-roll/chromagram/spectrogram $V \approx WH$ into a non-negative parts dictionary $W$ (learned chord/PC-set voicings, rhythmic cells) and an activation matrix $H$ (onset-energy envelopes): the learned $W$ is the "style", a designed or structured $H$ is the "piece" — additive parts-based atoms give interpretable harmony, co-activation gives chords, and the block structure of $H$ is the macro-form.

## Extended math

### The factorization

Let $V \in \mathbb{R}_{\ge 0}^{F \times T}$ be the target representation (piano-roll: $F$ = pitch classes, $T$ = time steps; or a chromagram/spectrogram). NMF seeks

$$
V \approx W H, \qquad W \in \mathbb{R}_{\ge 0}^{F \times K},\; H \in \mathbb{R}_{\ge 0}^{K \times T},
$$

minimizing a divergence $D(V \| WH)$ under the **non-negativity constraint** $W, H \ge 0$. Because atoms can only be *added*, the optimizer is forced into **sparse, parts-based atoms**: each basis column $w_k$ is a whole musical object (a chord voicing, a pitch-class set, a rhythmic cell), not an abstract signed combination.

### The two standard costs

- **Squared Euclidean**: $\|V - WH\|_F^2 = \sum_{f,t} (V_{ft} - (WH)_{ft})^2$ — Gaussian-noise model.
- **Generalized Kullback–Leibler** (musically preferred, Poisson maximum-likelihood):

$$
D(V \| WH) = \sum_{f,t} \left[ V_{ft} \ln \frac{V_{ft}}{(WH)_{ft}} - V_{ft} + (WH)_{ft} \right].
$$

The KL objective weights quiet and loud entries proportionally, so soft pitch classes survive instead of being washed out — empirically the better fit for music (Abdallah & Plumbley 2004).

### Multiplicative updates (Lee & Seung 2001)

For the KL objective, the following updates are non-increasing in $D$ and preserve non-negativity:

$$
H \leftarrow H \odot \frac{W^\top \frac{V}{WH}}{W^\top \mathbf{1}}, \qquad
W \leftarrow W \odot \frac{\frac{V}{WH} H^\top}{\mathbf{1} H^\top},
$$

with $\odot$ elementwise product and elementwise division. Add $\varepsilon = 10^{-9}$ to denominators on silent entries. For squared Euclidean the numerators/denominators become $W^\top V \,/\, W^\top W H$ and $V H^\top \,/\, W H H^\top$. Normalize each basis column to unit norm after every update and fold the scale into $H$ to fix the scale ambiguity $WH = (WD)(D^{-1}H)$.

**Complexity**: $\mathcal{O}(I \cdot K \cdot F \cdot T)$ for $I$ iterations; a few hundred iterations typically suffice. Non-convex in $(W,H)$ jointly → seed the RNG and fix the iteration count for determinism (zero-drift gate).

### Structured NMF (Hoyer 2004)

Add penalties to control $H$:
- **L1 sparsity** on $H$: fewer active atoms per column → sparse texture;
- **Temporal continuity**: small $\|h_{t+1} - h_t\|$ → smooth activation envelopes (legato phrasing);
- **Group/block structure**: constrain $H$ to be block-constant over section intervals → the *learned* $H$ carries macro-form directly.

### Composition modes

1. **Learn-and-recombine**: fit $W$ on a corpus, then *design* a new $H$ and reconstruct $WH$.
2. **Template**: fix $W$ to hand-built chord/scale templates (a grammar); solve for $H$ — the factorization *is* the arrangement.
3. **Structured**: impose the penalties above so the learned $H$ itself encodes form/articulation.

## Python implementation sketch

```python
"""Non-negative Matrix Factorization Composition (Method 085, NMF-C)."""
import numpy as np

def nmf_kl(V, K, n_iter=300, seed=0, eps=1e-9):
    """KL-divergence NMF (Lee-Seung multiplicative updates)."""
    rng = np.random.default_rng(seed)
    F, T = V.shape
    W = rng.uniform(0.1, 1.0, (F, K))
    H = rng.uniform(0.1, 1.0, (K, T))
    for _ in range(n_iter):
        WH = W @ H + eps
        # update H
        H = H * ((W.T @ (V / WH)) / (W.T @ np.ones((F, T)) + eps))
        WH = W @ H + eps
        # update W
        W = W * (((V / WH) @ H.T) / (np.ones((F, T)) @ H.T + eps))
        # normalize basis columns, fold scale into H
        norms = np.linalg.norm(W, axis=0, keepdims=True) + eps
        W = W / norms
        H = H * norms.T
    return W, H

def nmf_euclid(V, K, n_iter=300, seed=0, eps=1e-9):
    """Squared-Euclidean NMF (for pre-normalized inputs)."""
    rng = np.random.default_rng(seed)
    F, T = V.shape
    W = rng.uniform(0.1, 1.0, (F, K))
    H = rng.uniform(0.1, 1.0, (K, T))
    for _ in range(n_iter):
        H = H * ((W.T @ V) / (W.T @ W @ H + eps))
        W = W * ((V @ H.T) / (W @ H @ H.T + eps))
        norms = np.linalg.norm(W, axis=0, keepdims=True) + eps
        W = W / norms
        H = H * norms.T
    return W, H

def sparse_activation(H, lam):
    """L1-sparsity proximal step on H (soft-threshold)."""
    return np.maximum(H - lam, 0.0)

def decode_events(W, H, pitch_map, threshold=0.3):
    """Argmax-decode active atoms to (pitch, onset, velocity) events."""
    events = []
    F, K = W.shape
    K_, T = H.shape
    for t in range(T):
        for k in range(K_):
            if H[k, t] >= threshold:
                atom = W[:, k]
                pc = int(np.argmax(atom))          # pitch class
                vel = min(127, int(64 + 64 * H[k, t] / H.max()))
                events.append((pitch_map[pc], t, vel))
    return events

# --- Musicom integration (engine authors the MIDI) ---
# from workflows.unitmatrix_composer import UnitMatrixComposer, create_note_unit, create_chord_unit
# composer = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
# composer.create_matrix(num_voices=V, num_sections=S)
# W, H = nmf_kl(corpus_pianoroll, K=16, seed=7)
# for pc, t, vel in decode_events(W, H, pitch_map):
#     composer.fill_voice_section("lead", section_of(t), create_note_unit(pc, 480))
# ok, msg = composer.validate()   # MUST be True before to_midi (per AGENTS.md)
```

## References

- Lee, D. D., & Seung, H. S. (1999). "Learning the parts of objects by non-negative matrix factorization." *Nature* 401, 788–791.
- Lee, D. D., & Seung, H. S. (2001). "Algorithms for non-negative matrix factorization." *NeurIPS 13*, 556–562.
- Smaragdis, P., & Brown, J. C. (2003). "Non-negative matrix factorization for polyphonic music transcription." *IEEE WASPAA*, 177–180.
- Virtanen, T. (2007). "Monaural sound source separation by nonnegative matrix factorization with temporal continuity and sparseness criteria." *IEEE Trans. Audio, Speech, and Language Processing* 15(3), 1066–1074.
- Abdallah, S. A., & Plumbley, M. D. (2004). "Polyphonic music transcription by non-negative sparse coding of power spectra." *Proc. ISMIR*.
- Hoyer, P. O. (2004). "Non-negative matrix factorization with sparseness constraints." *JMLR* 5, 1457–1469.
- Helen, M., & Virtanen, T. (2005). "Separation of drums from polyphonic music using non-negative matrix factorization and support vector machine." *Proc. EUSIPCO*.
- Cemgil, A. T. (2009). "Bayesian inference for nonnegative matrix factorisation models." *Computational Intelligence and Neuroscience*.
