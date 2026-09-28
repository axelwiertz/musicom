# Method 099 — Self-Similarity Matrix Composition (SSMC)

## Method Identity
- **ID**: 099
- **Name**: Self-Similarity Matrix Composition (SSMC)
- **Paradigm**: Rules-Based
- **Layer**: abstract
- **Acronym**: SSMC

## Source
Foote, J. (1999). "Visualizing music and audio using self-similarity." *Proc. of ACM Multimedia* 1999, pp. 77–80.

Jhamtani, H. & Berg-Kirkpatrick, T. (2019). "Modeling Self-Repetition in Music Generation using Generative Adversarial Networks." *Proc. 36th ICML*, PMLR 97.

Hager, S., Hablutzel, K. & Kinnaird, K. (2024). "Generating Music with Structure Using Self-Similarity as Attention." arXiv:2406.15647.

Lattner, S., Grachten, M. & Widmer, G. (2016). "Imposing higher-level structure in polyphonic music generation using convolutional restricted Boltzmann machines and constraints." CoRR abs/1612.04742.

Müller, M. (2015). *Fundamentals of Music Processing*. Springer, Ch. 4: Music Structure Analysis.

Pareyon, G. (2011). *On Musical Self-Similarity: Intersemiosis as Synecdoche and Analogy*.

## Layer
**abstract** — designs the macro-form repetition structure (which sections/measures repeat, contrast, or vary) encoded as a self-similarity matrix (SSM). The SSM is a transposition- and register-invariant structural blueprint. Feeds concrete generators (any concrete-layer method) that fill UnitMatrix cells with events realizing the desired similarity pattern.

## Paradigm
**Rules-Based** — the SSM is a deterministic structural template. Solving the inverse problem (generate events whose SSM matches a target) is a constrained optimization with deterministic matching criteria. No learned neural parameters.

## Description
**Self-Similarity Matrix Composition (SSMC)** uses the self-similarity matrix (SSM, Foote 1999) — a standard MIR tool — as a generative structural blueprint. The SSM $S$ of $N$ time positions is an $N \times N$ matrix where $S_{ij}$ encodes the similarity between position $i$ and $j$:

$$S_{ij} = \frac{\mathbf{f}_i \cdot \mathbf{f}_j}{\|\mathbf{f}_i\|\|\mathbf{f}_j\|}$$

where $\mathbf{f}_i \in \mathbb{R}^d$ is a feature vector (chroma, onset-density, texture, etc.) at position $i$.

**Structural encoding via SSM**:
1. **Diagonal blocks** (high $S_{[a:b],[a:b]}$) = repeated sections
2. **Off-diagonal stripes** ($S_{[a:b],[c:d]} \gg 0$) = structural repetition across different sections
3. **Checkerboard patterns** on diagonal = periodic phrase structure
4. **Novelty boundaries** from Foote's checkerboard kernel correlation = section boundaries

**Generative workflow (inverse SSM problem)**:
1. Design target SSM $S^*$ — specify desired pairwise similarity structure
2. Initialize feature sequence $\mathbf{f}_1 \ldots \mathbf{f}_N$
3. Optimize to minimize Frobenius-norm mismatch:
   $$\mathcal{L} = \sum_{i,j} (S_{ij}(\mathbf{f}) - S^*_{ij})^2 + \lambda \sum_i \|\mathbf{f}_i - \mathbf{f}_{i-1}\|^2$$
4. Optimization strategies: gradient descent (differentiable cosine-similarity), alternating projections (block-diagonal/rank-constrained Toeplitz), dynamic programming (binary similarity targets)
5. Decode optimized features to concrete events per bar/voice

## Mathematical Formalization

### Self-Similarity Matrix
Given feature matrix $F \in \mathbb{R}^{N \times d}$ where row $i$ is $\mathbf{f}_i^T$:

$$S = \frac{F F^T}{\text{diag}(F F^T)^{1/2} \text{diag}(F F^T)^{1/2 T}}$$

Equivalently, $S_{ij} = \cos(\mathbf{f}_i, \mathbf{f}_j)$.

### Novelty Curve (Foote Kernel)
The novelty curve $n(t)$ detects section boundaries by correlating the SSM along the diagonal with a $2L \times 2L$ checkerboard kernel $K$:

$$n(t) = \sum_{i,j} S_{ij} \cdot K_{ij}^{(t)}$$

where $K^{(t)}$ is the kernel $K$ centered at diagonal position $t$:

$$K = \begin{pmatrix} -1 & +1 \\ +1 & -1 \end{pmatrix} \otimes \mathbf{1}_{L \times L}$$

convolved with a Gaussian taper of width $\sigma = L/2$.

### Optimization Algorithm (Gradient Descent)

```
Algorithm: SSMC-GD
Input: Target SSM S* ∈ ℝ^{N×N}, feature dimension d, λ > 0
Output: Feature sequence F ∈ ℝ^{N×d}

1. Initialize F ~ N(0, I)  or from reference piece
2. For step = 1 to M:
   a. Compute S = normalize(F F^T)
   b. Loss = ||S - S*||_F^2 + λ·Σ_i||f_i - f_{i-1}||^2
   c. Gradient: ∂L/∂F via chain rule through cosine similarity
   d. F ← F - η · ∂L/∂F  (Adam optimizer)
3. Return F
```

### Complexity
- SSM construction: $O(N^2 d)$
- Gradient descent per iteration: $O(N^2 d)$
- Total: $O(N^2 \cdot M)$ where $M$ = optimizer iterations
- Novelty curve: $O(N L^2)$

## Musical Elements Framework

### PITCH
Feature vector includes 12-dim chroma distribution. SSM similarity in chroma space captures harmonic/textural similarity. Optimization drives chroma vectors to produce desired per-section harmonic palette.

### RHYTHM
Feature vector includes onset-density, syncopation index, IOI entropy. SSM similarity encodes groove repetition and rhythmic contrast. Target SSM prescribes rhythmic form.

### HARMONY
Feature vector includes chord-quality profiles (major/minor/dim). SSM captures functional harmonic similarity. Block-diagonal SSM directly encodes harmonic form (strophic, binary, ternary).

### STRUCTURE
Primary domain. SSM block structure = macro-form sections. Within-block sub-structure = phrase-level patterns. Off-diagonal similarity = motivic recall/development.

### TEXTURE
Feature vector includes voice-count, registration spread, polyphony index. SSM captures textural contrast (tutti vs. solo, dense vs. sparse).

## UnitMatrix Integration

### Voices (Rows)
Multi-voice feature vector $F_i = [F_i^{(1)}, \ldots, F_i^{(V)}]$ where each $F_i^{(v)}$ is voice $v$'s features at position $i$. SSM of multi-voice sequence encodes per-voice similarity (melodic repetition), cross-voice similarity (imitation/canon), and vertical texture similarity (voicing recurrence).

### Sections (Columns)
Section boundaries from novelty curve peaks. Each section $s$ = diagonal block $[b_s, e_s] \times [b_s, e_s]$ in SSM. Off-diagonal target entries define section-level contrast/repetition.

### Cells (MusicUnit)
Each bar $i$, voice $v$ decoded from $F_i^{(v)}$ via:
- Concrete matching method conditioned on feature profile
- Direct mapping: chroma → pitch-class distribution, density → onsets
- Corpus lookup: nearest-neighbor over reference bars

## Python Implementation Sketch

```python
"""
Method 099: Self-Similarity Matrix Composition (SSMC)
Generates music structure by solving the inverse SSM problem.
Candidate code path: rules/ssm_composition.py
"""
import numpy as np
from typing import Optional, Callable


def build_ssm(features: np.ndarray) -> np.ndarray:
    \"\"\"Compute cosine-similarity self-similarity matrix.
    
    Args:
        features: (N, d) feature matrix, rows = time positions
        
    Returns:
        S: (N, N) self-similarity matrix, S_ij = cos(f_i, f_j)
    \"\"\"
    norms = np.linalg.norm(features, axis=1, keepdims=True)
    norms[norms == 0] = 1.0  # avoid div-by-zero
    normed = features / norms
    return normed @ normed.T


def novelty_curve(S: np.ndarray, L: int = 8) -> np.ndarray:
    \"\"\"Compute Foote novelty curve from SSM.
    
    Args:
        S: (N, N) self-similarity matrix
        L: half-width of checkerboard kernel
        
    Returns:
        n: (N,) novelty values, peaks = structural boundaries
    \"\"\"
    N = S.shape[0]
    # Checkerboard kernel: [[-1, +1], [+1, -1]] ⊗ 1_{L×L}
    K = np.ones((2*L, 2*L))
    K[:L, :L] = -1.0
    K[L:, L:] = -1.0
    # Gaussian taper
    x = np.linspace(-1.5, 1.5, 2*L)
    gaussian = np.exp(-x**2 / (2 * 0.5**2))
    taper = gaussian[:, None] * gaussian[None, :]
    K = K * taper
    
    n = np.zeros(N)
    # Correlate kernel along diagonal
    for t in range(L, N - L):
        window = S[t-L:t+L, t-L:t+L]
        n[t] = np.sum(window * K)
    
    # Normalize
    if np.max(np.abs(n)) > 0:
        n = n / np.max(np.abs(n))
    return n


def optimize_features(
    target_ssm: np.ndarray,
    d: int,
    lambda_reg: float = 0.1,
    lr: float = 0.01,
    n_steps: int = 500,
    seed_features: Optional[np.ndarray] = None,
) -> np.ndarray:
    \"\"\"Solve inverse SSM: find features whose SSM matches target.
    
    Args:
        target_ssm: (N, N) target self-similarity matrix
        d: feature dimension
        lambda_reg: smoothness regularization weight
        lr: learning rate for gradient descent
        n_steps: number of optimization steps
        seed_features: optional (N, d) initialization
        
    Returns:
        features: (N, d) optimized feature matrix
    \"\"\"
    N = target_ssm.shape[0]
    
    if seed_features is not None:
        F = seed_features.copy().astype(np.float64)
    else:
        F = np.random.randn(N, d).astype(np.float64) * 0.1
    
    for step in range(n_steps):
        # Current SSM
        S = build_ssm(F)
        
        # Loss: Frobenius mismatch + smoothness
        loss_ssm = np.sum((S - target_ssm)**2)
        loss_smooth = lambda_reg * np.sum(np.diff(F, axis=0)**2)
        
        # Gradient via autograd-style manual computation
        # For each pair (i,j): dS_ij/dF = ...
        # Simplified: finite-difference gradient for demo
        grad = np.zeros_like(F)
        eps = 1e-6
        
        for i in range(N):
            for k in range(d):
                F_plus = F.copy()
                F_plus[i, k] += eps
                S_plus = build_ssm(F_plus)
                loss_plus = np.sum((S_plus - target_ssm)**2)
                grad[i, k] = (loss_plus - loss_ssm) / eps
        
        # Add smoothness gradient
        for i in range(1, N-1):
            grad[i] += 2 * lambda_reg * (2*F[i] - F[i-1] - F[i+1])
        grad[0] += 2 * lambda_reg * (F[0] - F[1])
        grad[-1] += 2 * lambda_reg * (F[-1] - F[-2])
        
        # Adam-like simple update
        F -= lr * grad / (np.linalg.norm(grad, axis=1, keepdims=True) + 1e-8)
        
        if step % 100 == 0:
            print(f"Step {step}: SSM loss = {loss_ssm:.4f}, smooth = {loss_smooth:.4f}")
    
    return F


def design_verse_chorus_ssm(
    N_bars: int,
    intro_len: int = 4,
    verse_len: int = 8,
    chorus_len: int = 8,
    bridge_len: int = 0,
    outro_len: int = 4,
    sim_repeat: float = 1.0,
    sim_verse_chorus: float = 0.3,
    sim_bridge: float = 0.5,
) -> np.ndarray:
    \"\"\"Design a target SSM for verse-chorus form.
    
    Returns (N_bars, N_bars) idealised SSM where:
    - Self-similar blocks have sim_repeat similarity
    - Different sections have adjusted similarity levels
    - Contrast = 0.0 similarity
    \"\"\"
    N = N_bars
    S = np.zeros((N, N))
    
    # Define section boundaries
    sections = []
    pos = 0
    if intro_len > 0:
        sections.append(("intro", pos, pos + intro_len))
        pos += intro_len
    if verse_len > 0:
        sections.append(("verse", pos, pos + verse_len))
        pos += verse_len
    if chorus_len > 0:
        sections.append(("chorus", pos, pos + chorus_len))
        pos += chorus_len
    if bridge_len > 0:
        sections.append(("bridge", pos, pos + bridge_len))
        pos += bridge_len
    if outro_len > 0:
        sections.append(("outro", pos, pos + outro_len))
        pos += outro_len
    
    # Fill blocks
    for i, (name_i, start_i, end_i) in enumerate(sections):
        # Self-similarity (diagonal block)
        S[start_i:end_i, start_i:end_i] = sim_repeat
        
        # Cross-section similarity
        for j, (name_j, start_j, end_j) in enumerate(sections):
            if i >= j:
                continue
            if name_i == name_j:  # same section type (e.g., two verses)
                S[start_i:end_i, start_j:end_j] = sim_repeat
                S[start_j:end_j, start_i:end_i] = sim_repeat
            elif name_i == "verse" and name_j == "chorus":
                S[start_i:end_i, start_j:end_j] = sim_verse_chorus
                S[start_j:end_j, start_i:end_i] = sim_verse_chorus
            elif "bridge" in (name_i, name_j):
                S[start_i:end_i, start_j:end_j] = sim_bridge
                S[start_j:end_j, start_i:end_i] = sim_bridge
            # else: zero (max contrast)
    
    return S


# ---- Usage Example ----

if __name__ == "__main__":
    # Design a 24-bar verse-chorus form
    N = 24  # 4 intro + 8 verse + 8 chorus + 4 outro
    target = design_verse_chorus_ssm(
        N_bars=N, intro_len=4, verse_len=8, chorus_len=8, outro_len=4
    )
    
    # Solve inverse SSM
    features = optimize_features(
        target_ssm=target, d=6, lambda_reg=0.5, n_steps=500
    )
    
    # Extract novelty curve
    novelty = novelty_curve(build_ssm(features), L=4)
    
    # Find section boundaries (peaks in novelty curve)
    threshold = 0.5
    boundaries = np.where(novelty > threshold)[0]
    print(f"Detected boundaries at bars: {boundaries}")
    print(f"Feature matrix shape: {features.shape}")
```

## References
- Foote, J. (1999). "Visualizing music and audio using self-similarity." *Proc. of ACM Multimedia*, 77–80.
- Müller, M. (2015). *Fundamentals of Music Processing*. Springer, Ch. 4: Music Structure Analysis.
- Jhamtani, H. & Berg-Kirkpatrick, T. (2019). "Modeling Self-Repetition in Music Generation using GANs." *ICML 2019*.
- Hager, S., Hablutzel, K. & Kinnaird, K. (2024). "Generating Music with Structure Using Self-Similarity as Attention." arXiv:2406.15647.
- Lattner, S., Grachten, M. & Widmer, G. (2016). "Imposing higher-level structure in polyphonic music generation using convolutional RBMs and constraints." CoRR abs/1612.04742.