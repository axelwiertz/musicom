# Method 119: Tensor Decomposition Composition (TDC)

## Overview

- **ID**: 119
- **Name**: Tensor Decomposition Composition
- **Acronym**: TDC
- **Paradigm**: Rules-Based
- **Layer**: concrete
- **Line**: Generates polyphonic music from CP/Tucker low-rank decomposition of a 3-way music tensor (voices × time × pitch).

## Mathematical Foundation

### The Music Tensor

$$\mathcal{X} \in \mathbb{R}^{V \times T \times P}$$

where:
- $V$ = number of voices (UnitMatrix rows)
- $T$ = number of time slots (ticks, 16th-notes, or event slots)
- $P$ = number of pitch classes (12 for chroma) or MIDI notes (128)

Entry $\mathcal{X}_{v,t,p}$ is the activation strength of pitch $p$ at time $t$ in voice $v$.

### CP Decomposition (CANDECOMP/PARAFAC)

$$\mathcal{X} \approx \sum_{r=1}^{R} \mathbf{a}_r \circ \mathbf{b}_r \circ \mathbf{c}_r$$

Element-wise:
$$\mathcal{X}_{v,t,p} \approx \sum_{r=1}^{R} a_{v,r} \, b_{t,r} \, c_{p,r}$$

- $\mathbf{A} \in \mathbb{R}^{V \times R}$: voice factor matrix — rows weight voice participation in each component
- $\mathbf{B} \in \mathbb{R}^{T \times R}$: time factor matrix — columns encode rhythmic/time envelopes
- $\mathbf{C} \in \mathbb{R}^{P \times R}$: pitch factor matrix — columns encode pitch-class content
- $R$: rank = compositional complexity dial

CP-ALS (Alternating Least Squares) solves:
$$\hat{\mathbf{A}} = \arg\min_{\mathbf{A}} \|\mathcal{X}_{(1)} - \mathbf{A}(\mathbf{C} \odot \mathbf{B})^\top\|_F^2$$

with analogous updates for $\mathbf{B}$ and $\mathbf{C}$, where $\mathcal{X}_{(1)}$ is the mode-1 unfolding and $\odot$ is the Khatri-Rao product.

### Tucker Decomposition

$$\mathcal{X} \approx \mathcal{G} \times_1 \mathbf{A} \times_2 \mathbf{B} \times_3 \mathbf{C}$$

Element-wise:
$$\mathcal{X}_{v,t,p} \approx \sum_{r_1=1}^{R_1} \sum_{r_2=1}^{R_2} \sum_{r_3=1}^{R_3} g_{r_1 r_2 r_3} \, a_{v,r_1} \, b_{t,r_2} \, c_{p,r_3}$$

- $\mathcal{G} \in \mathbb{R}^{R_1 \times R_2 \times R_3}$: core tensor — cross-mode interactions
- $(R_1, R_2, R_3)$: per-mode ranks (can differ)
- CP is the special case $R_1 = R_2 = R_3 = R$ with super-diagonal $\mathcal{G}$

HOSVD (Higher-Order SVD) computes Tucker via:
$$\mathbf{A} = \text{leading } R_1 \text{ left singular vectors of } \mathcal{X}_{(1)}$$
$$\mathbf{B} = \text{leading } R_2 \text{ left singular vectors of } \mathcal{X}_{(2)}$$
$$\mathbf{C} = \text{leading } R_3 \text{ left singular vectors of } \mathcal{X}_{(3)}$$
$$\mathcal{G} = \mathcal{X} \times_1 \mathbf{A}^\top \times_2 \mathbf{B}^\top \times_3 \mathbf{C}^\top$$

### Section Structure (Block-Diagonal Form)

$$\mathcal{X} = \mathrm{diag}(\mathcal{X}_1, \mathcal{X}_2, \ldots, \mathcal{X}_S)$$

Each section block $\mathcal{X}_s$ has independent factor triplets $(\mathbf{A}_s, \mathbf{B}_s, \mathbf{C}_s, \mathcal{G}_s)$.

### Factor Design DSL (Proposed)

Composers specify factors via declarative templates:

```python
# Voice factor: one-hot independent voices
A = eye(V, R)  # each voice = one component

# Time factor: periodic rhythm with Gaussian-motif clusters
B = zeros(T, R)
B[0:T:4, 0] = 1.0         # quarter-note pulse for component 0
B[16:24, 1] = gaussian(8) # motif at bars 2-3 for component 1

# Pitch factor: C major scale for component 0
C[:, 0] = [1,0,1,0,1,1,0,1,0,1,0,1]  # C D E F G A B

# Core: diagonal CP (independent components)
G = eye(R, R, R)  # super-diagonal
```

### Thresholding Pipeline

$$\text{note\_on}_{v,t,p} = \begin{cases} 1 & \text{if } \hat{\mathcal{X}}_{v,t,p} > \theta_v \\ 0 & \text{otherwise} \end{cases}$$

where $\theta_v = \mu_v + k \cdot \sigma_v$ (adaptive per-voice), or $\theta = \text{global percentile}$.

## Musical Element Mapping

| Element | Tensor Mapping | Design Control |
|---------|---------------|----------------|
| PITCH | $\mathbf{C}$ columns | Scale/chord vocabulary per component |
| RHYTHM | $\mathbf{B}$ columns | Onset patterns, meter, motifs |
| HARMONY | Multi-component $\mathbf{C}$ overlap + $\mathcal{G}$ | Chord voicing, voice-leading |
| STRUCTURE | Block-diagonal $\mathcal{X}_s$ | Section form, factor sharing |
| TEXTURE | Density of $\mathcal{X}$, rank $R$ | Homophony → polyphony continuum |

## Complexity

- **CP-ALS**: $\mathcal{O}(R \cdot V \cdot T \cdot P)$ per iteration ($\sim 10^6$–$10^8$ for typical compositions)
- **Tucker HOSVD**: $\mathcal{O}(V \cdot T \cdot P \cdot \min(V,T,P))$ ($\sim 10^8$–$10^9$)
- **Thresholding**: $\mathcal{O}(V \cdot T \cdot P)$ (amortized)

## References

1. Hitchcock, F. L. (1927). "The expression of a tensor or a polyadic as a sum of products." *Journal of Mathematics and Physics* 6(1-4), 164–189.
2. Tucker, L. R. (1966). "Some mathematical notes on three-mode factor analysis." *Psychometrika* 31(3), 279–311.
3. Carroll, J. D. & Chang, J. J. (1970). "Analysis of individual differences in multidimensional scaling via an N-way generalization of 'Eckart–Young' decomposition." *Psychometrika* 35(3), 283–319.
4. Kolda, T. G. & Bader, B. W. (2009). "Tensor decompositions and applications." *SIAM Review* 51(3), 455–500.
5. Bro, R. & Kiers, H. A. L. (2003). "A new efficient method for determining the number of components in PARAFAC models." *Journal of Chemometrics* 17(5), 274–286.

## Python Implementation Sketch

```python
import numpy as np
from scipy import linalg
from structures import UnitMatrix, MusicUnit, MusicEvent

def cp_als(X, R, max_iter=100, tol=1e-6):
    """CP decomposition via alternating least squares."""
    V, T, P = X.shape
    
    # Random initialization
    A = np.random.randn(V, R)
    B = np.random.randn(T, R)
    C = np.random.randn(P, R)
    
    for it in range(max_iter):
        # Fix B, C → solve for A
        Z = np.einsum('tr,pr->trp', B, C).reshape(T*P, R)
        X1 = X.transpose(1, 2, 0).reshape(T*P, V)
        A_new = np.linalg.lstsq(Z, X1, rcond=None)[0].T
        
        # Fix A, C → solve for B
        # ... (cyclically permute and solve)
        
        # Check convergence
        rec = reconstruct_cp(A, B, C)
        err = np.linalg.norm(X - rec) / np.linalg.norm(X)
        if err < tol:
            break
    
    return A, B, C

def reconstruct_cp(A, B, C):
    """Reconstruct tensor from CP factors."""
    return np.einsum('vr,tr,pr->vtp', A, B, C)

def tucker_hosvd(X, ranks):
    """Tucker decomposition via HOSVD."""
    V, T, P = X.shape
    R1, R2, R3 = ranks
    
    U1, _, _ = linalg.svd(X.reshape(V, T*P), full_matrices=False)
    U2, _, _ = linalg.svd(X.transpose(1,0,2).reshape(T, V*P), full_matrices=False)
    U3, _, _ = linalg.svd(X.transpose(2,0,1).reshape(P, V*T), full_matrices=False)
    
    A = U1[:, :R1]
    B = U2[:, :R2]
    C = U3[:, :R3]
    
    # Core tensor
    G = np.einsum('iv,jt,kp,vtp->ijk', A.T, B.T, C.T, X)
    
    return G, A, B, C

def design_voice_factor(V, R, pattern='one-hot'):
    """Design the voice factor matrix A."""
    if pattern == 'one-hot':
        assert V <= R, "Need at least R >= V for one-hot voices"
        A = np.zeros((V, R))
        for v in range(V):
            A[v, v % R] = 1.0
    elif pattern == 'shared':
        # Voices share components with mixing weights
        A = np.random.dirichlet(np.ones(R), size=V)
    return A

def design_time_factor(T, R, section_boundaries=None):
    """Design the time factor matrix B."""
    B = np.zeros((T, R))
    if section_boundaries:
        # Block-diagonal: each section uses one component
        for s_idx, (start, end) in enumerate(section_boundaries):
            r = s_idx % R
            B[start:end, r] = 1.0
    else:
        # Periodic: component rotates through time
        for t in range(T):
            B[t, t % R] = 1.0
    return B

def design_pitch_factor(P, R, mode='C_major'):
    """Design the pitch factor matrix C."""
    C = np.zeros((P, R))
    if mode == 'C_major':
        # C major: [C, D, E, F, G, A, B]
        scale_tones = [0, 2, 4, 5, 7, 9, 11]
        for r in range(min(R, 7)):
            C[scale_tones[r], r] = 1.0
    return C

def compose_tdc(V, sections, pitches=12, rank=4):
    """
    Full TDC composition pipeline.
    
    Args:
        V: number of voices
        sections: list of (name, length_in_ticks) tuples
        pitches: number of pitch classes
        rank: CP rank
        
    Returns:
        composer: UnitMatrixComposer with filled cells
    """
    from workflows.unitmatrix_composer import UnitMatrixComposer, create_note_unit
    
    T = sum(l for _, l in sections)
    
    # Design factors
    A = design_voice_factor(V, rank, 'one-hot')
    B = design_time_factor(T, rank)
    C = design_pitch_factor(pitches, rank, 'C_major')
    
    # Reconstruct
    X = reconstruct_cp(A, B, C)
    
    # Threshold
    theta = np.mean(X) + 2.0 * np.std(X)
    binary = X > theta
    
    # Build composer
    composer = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
    composer.create_matrix(num_voices=V, num_sections=len(sections))
    
    for v in range(V):
        composer.add_voice(f"Voice_{v}", program=0, channel=v)
    
    tick_offset = 0
    for s_idx, (s_name, s_len) in enumerate(sections):
        composer.add_section(s_name, bars=s_len // 1920)
        
        for v in range(V):
            # Find active pitches in this section
            events = []
            for t_offset in range(s_len):
                t = tick_offset + t_offset
                for p in range(pitches):
                    if binary[v, t, p]:
                        events.append(MusicEvent(
                            pitch=60 + p,
                            volume=80,
                            start_tick=tick_offset + t_offset,
                            end_tick=tick_offset + t_offset + 120  # 1/4 note
                        ))
            
            if events:
                composer.set_unit(v, s_idx,
                    create_note_unit(events[0].pitch, s_len))
            else:
                composer.set_unit(v, s_idx,
                    create_note_unit(60, s_len))  # silent placeholder
        
        tick_offset += s_len
    
    ok, msg = composer.validate()
    assert ok, f"Validation failed: {msg}"
    
    return composer
```

## Related Methods

- **085 NMF-C**: 2D matrix factorization → 3D tensor decomposition (direct generalization)
- **046 VAE-LSI**: learned latent spaces → designed factor matrices
- **097 MaxEnt-C**: constraint-based structure → low-rank structure
- **024 Additive Mass**: additive frequency synthesis → additive tensor-pitch synthesis
- **050 OTVL**: optimal transport for voice-leading → factor-based voice design

## UnitMatrix Integration Summary

| Component | Tensor Mode | UnitMatrix Mapping |
|-----------|------------|-------------------|
| $\mathbf{A}$ | Voice factors | Voice rows — participation weights |
| $\mathbf{B}$ | Time factors | Section + beat columns — rhythm |
| $\mathbf{C}$ | Pitch factors | Cell content — pitch material |
| $\mathcal{G}$ | Core interactions | Cross-voice/harmonic couplings |
| $\mathcal{X}$ | Full reconstruction | Complete piano-roll → note events |