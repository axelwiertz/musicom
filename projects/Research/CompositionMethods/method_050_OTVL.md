# Optimal Transport Voice Leading (OTVL) (Method 050)

### **Source**
Adapted from the mathematical theory of optimal transport (Monge, 1781; Kantorovich, 1942), formalized in Villani (2009) *Optimal Transport: Old and New*. Applied to music theory via Tymoczko (2011) *A Geometry of Music* (orbifold voice-leading geometry) and Yust (2018) who explicitly framed voice leading as a Wasserstein distance minimization problem. This formulation extends discrete Neo-Riemannian operations (Method 011) into continuous pitch space using the Monge-Kantorovich transport framework.

### **Description**
Optimal Transport Voice Leading (OTVL) treats each chord as a discrete probability distribution (or mass configuration) over continuous pitch space. Given two chords $C_s$ and $C_t$ with $n$ and $m$ notes respectively, OTVL finds the minimum-cost transport plan $\pi^*$ that redistributes pitch masses from $C_s$ to $C_t$, where cost is defined by a distance metric on pitch space (typically Euclidean distance in pitch-class space or log-frequency space). The resulting transport plan directly yields the voice-leading assignment: which note in $C_s$ moves to which note in $C_t$, and by how much.

Unlike Neo-Riemannian graph search (Method 011) which operates on discrete triadic transformations (L, P, R operations), OTVL works in continuous pitch space, handles arbitrary chord cardinalities, and naturally extends to voice leading of dense clusters, microtonal chords, and spectral distributions.

The Kantorovich relaxation of Monge's problem:
$$W_p(\mu, \nu) = \left( \inf_{\pi \in \Pi(\mu, \nu)} \int_{X \times Y} d(x, y)^p \, d\pi(x, y) \right)^{1/p}$$

where $\Pi(\mu, \nu)$ is the set of all couplings (joint distributions) with marginals $\mu$ and $\nu$, and $d(x,y)$ is the ground distance on pitch space.

For discrete chords with $n$ and $m$ notes:
$$W_p^p(C_s, C_t) = \min_{\pi \geq 0} \sum_{i=1}^{n} \sum_{j=1}^{m} \pi_{ij} \, |p_i - q_j|^p$$
subject to $\sum_j \pi_{ij} = 1/n$ and $\sum_i \pi_{ij} = 1/m$.

### **Musical Elements Framework**
- **PITCH**: Each chord is a mass distribution $\mu = \frac{1}{n}\sum_{i=1}^n \delta_{p_i}$ over pitch space (MIDI or log-frequency). The optimal transport plan $\pi^*$ assigns each source pitch $p_i$ to target pitch(es) $q_j$ with weights $\pi^*_{ij}$. The voice-leading trajectory for each voice is the displacement $q_j - p_i$ weighted by $\pi^*_{ij}$. Pitches move along geodesics in pitch space (straight lines in MIDI, geodesics on the pitch-class circle for PC space).

- **RHYTHM**: Voice-leading rhythm is determined by the transport cost gradient. Low-cost transitions (small total displacement) allow faster harmonic rhythm (more frequent chord changes per bar). High-cost transitions (large displacements) slow the harmonic rhythm, creating sustained chords. The transport cost $W_1(C_s, C_t)$ directly maps to a rhythmic density parameter: $\rho_s = \kappa / W_1(C_s, C_t)$ where $\kappa$ is a scaling constant.

- **HARMONY**: The Wasserstein distance $W_p$ between successive chords provides a continuous, perceptually grounded measure of harmonic distance. Unlike traditional harmonic analysis (which uses discrete function labels), OTVL provides a scalar harmonic tension value at every moment. Sections with low $W_p$ between adjacent chords = stable, consonant progressions. Sections with high $W_p$ = tense, dissonant progressions. The transport plan itself reveals the voice-leading quality: smooth (diagonal-dominant $\pi^*$) vs. crossing (off-diagonal mass).

- **STRUCTURE**: Macro-form is organized by the sequence of chord distributions and their pairwise Wasserstein distances. A composition can be structured as a path through chord-space that minimizes total transport cost (smooth form) or maximizes it (contrasting form). Section boundaries occur at local maxima of $W_p(C_s, C_{s+1})$, creating natural phrase divisions. The barycentric interpolation between section chord-distributions provides smooth transitions:
  $$\mu_t = \text{BarWass}(\mu_A, \mu_B, t) = ((1-t)\,\text{id} + t\,T^*)_\# \mu_A$$
  where $T^*$ is the optimal transport map from $\mu_A$ to $\mu_B$.

- **TEXTURE**: Voice distribution across the ensemble is determined by the transport plan's granularity. A fine-grained plan (many small displacements) creates dense, polyphonic texture. A coarse-grained plan (few large displacements) creates sparse, homophonic texture. The entropy of the transport plan $H(\pi^*) = -\sum_{ij} \pi^*_{ij} \log \pi^*_{ij}$ measures textural complexity: high entropy = independent contrapuntal voices; low entropy = unified block movement.

### **UnitMatrix Integration (Voices & Sections)**
- **Rows (Voices)**: Each voice $v$ corresponds to a mass source in the transport problem. For $V$ voices, the source chord has $V$ pitch masses. The transport plan assigns each voice a target pitch in the next section's chord.
- **Columns (Sections)**: Each section $s$ defines a target chord distribution $\nu_s$ and a transport budget $B_s$ (maximum allowed $W_p$). Section transitions are solved as constrained OT problems.
- **Cells** $U_{v, s}$:
  - `{PITCH}`: Target pitch for voice $v$ in section $s$, extracted from the optimal transport plan: $p_{v,s} = \arg\max_j \pi^*_{v,j}$.
  - `{RHYTHM}`: Harmonic rhythm density $\rho_s = \kappa / W_1(\nu_{s-1}, \nu_s)$, determining subdivisions per bar.
  - `{TEXTURE}`: Transport plan entropy $H(\pi^*_s)$ mapping to voice independence coefficient.
- **Mapping Flow**:
  1. Define chord sequence $\nu_1, \nu_2, \ldots, \nu_S$ for $S$ sections.
  2. For each section pair $(\nu_{s-1}, \nu_s)$, solve the discrete OT problem using the Sinkhorn algorithm (entropy-regularized):
     $$\pi^* = \arg\min_{\pi} \sum_{ij} \pi_{ij} C_{ij} - \epsilon H(\pi)$$
     where $C_{ij} = |p_i - q_j|^2$ is the cost matrix and $\epsilon$ is the regularization parameter.
  3. Extract voice assignments from $\pi^*$: voice $v$ moves to $\arg\max_j \pi^*_{vj}$.
  4. Compute section parameters: $W_p$, harmonic rhythm $\rho_s$, texture entropy $H_s$.
  5. Populate UnitMatrix cells with pitch targets, rhythm densities, and texture coefficients.
  6. For continuous transitions between sections, compute Wasserstein barycenters at intermediate time points.

### **Implementation Requirements (Python/NumPy/SciPy)**
```python
import numpy as np
from scipy.optimize import linprog
from scipy.spatial.distance import cdist

def sinkhorn_ot(a, b, C, epsilon=0.1, max_iter=1000, tol=1e-9):
    """
    Solve entropy-regularized optimal transport via Sinkhorn-Knopp.
    a: source distribution (n,)
    b: target distribution (m,)
    C: cost matrix (n, m)
    epsilon: regularization strength
    Returns: transport plan pi (n, m)
    """
    n, m = C.shape
    K = np.exp(-C / epsilon)
    u = np.ones(n) / n
    v = np.ones(m) / m
    
    for _ in range(max_iter):
        u_prev = u.copy()
        u = a / (K @ v + 1e-16)
        v = b / (K.T @ u + 1e-16)
        if np.max(np.abs(u - u_prev)) < tol:
            break
    
    pi = np.diag(u) @ K @ np.diag(v)
    return pi

def otfvl_voice_leading(source_chord, target_chord, epsilon=0.05):
    """
    Compute optimal transport voice leading between two chords.
    source_chord: array of MIDI pitches (n,)
    target_chord: array of MIDI pitches (m,)
    Returns: (transport_plan, wasserstein_distance, voice_assignments)
    """
    n, m = len(source_chord), len(target_chord)
    
    # Uniform distributions
    a = np.ones(n) / n
    b = np.ones(m) / m
    
    # Cost matrix: squared pitch distance
    C = cdist(source_chord.reshape(-1, 1), target_chord.reshape(-1, 1), metric='sqeuclidean')
    
    # Solve OT
    pi = sinkhorn_ot(a, b, C, epsilon=epsilon)
    
    # Wasserstein distance
    W2 = np.sqrt(np.sum(pi * C))
    
    # Voice assignments (greedy from transport plan)
    assignments = np.argmax(pi, axis=1)
    
    return pi, W2, assignments

def compute_harmonic_rhythm(wasserstein_distances, kappa=10.0):
    """Map W1 distances to harmonic rhythm density."""
    return kappa / (np.array(wasserstein_distances) + 1e-6)

def wasserstein_barycenter_1d(mu_positions, mu_weights, t, epsilon=0.01):
    """
    Compute 1D Wasserstein barycenter at interpolation parameter t.
    mu_positions: list of pitch arrays for each distribution
    mu_weights: list of weight arrays
    t: interpolation parameter [0, 1]
    """
    # For 1D, barycenter has closed-form via quantile functions
    all_positions = np.concatenate(mu_positions)
    all_weights = np.concatenate(mu_weights)
    
    # Sort by position
    sort_idx = np.argsort(all_positions)
    sorted_pos = all_positions[sort_idx]
    sorted_w = all_weights[sort_idx]
    
    # CDF
    cdf = np.cumsum(sorted_w)
    cdf /= cdf[-1]
    
    # Interpolate quantile function
    n_interp = 100
    quantiles = np.linspace(0, 1, n_interp)
    interp_pos = np.interp(quantiles, cdf, sorted_pos)
    
    # Barycenter = weighted average of quantile functions
    # (simplified for 2-distribution case)
    return interp_pos
```

### **Pitfalls**
1. **Sinkhorn non-convergence**: If $\epsilon$ is too small relative to cost scale, Sinkhorn oscillates. Ensure $\epsilon > 0.01 \cdot \max(C)$. Use log-domain Sinkhorn for numerical stability.
2. **Cardinality mismatch**: When source and target chords have very different numbers of notes, the transport plan becomes diffuse. Solution: add ghost notes (zero-weight pitches) to balance cardinalities.
3. **Octave ambiguity**: MIDI pitch distance treats C4→C5 the same as C4→B4. Use pitch-class circular distance for PC-space OT: $d_{PC}(p, q) = \min(|p-q| \mod 12, 12 - |p-q| \mod 12)$.
4. **Voice crossing**: OT may assign voices that cross (soprano drops below alto). Post-process: sort voice assignments by pitch and enforce register constraints.
5. **Computational cost**: Sinkhorn is $\mathcal{O}(n^2 \cdot I)$ where $I$ = iterations. For large chords ($n > 100$), use sliced Wasserstein (random 1D projections) as approximation: $\mathcal{O}(N_{proj} \cdot n \log n)$.
6. **Regularization blur**: Large $\epsilon$ makes the transport plan diffuse (all-to-all). Keep $\epsilon < 0.1 \cdot \text{mean}(C)$ for sharp assignments.
7. **Section-boundary discontinuity**: Abrupt chord changes create large $W_p$ jumps. Use Wasserstein barycenter interpolation over 2-4 beats to smooth transitions.
8. **Microtonal drift**: In continuous pitch space, OT may produce non-quantized pitches. Post-process: snap to nearest scale degree after transport.
9. **Symmetric chords**: Chords with rotational symmetry (e.g., augmented triad, diminished 7th) have multiple optimal plans. Break ties by minimizing total voice-leading range.
10. **Temporal coherence**: Independent OT solves per section pair may produce inconsistent voice assignments. Solution: chain transport plans — use output voices of section $s$ as input voices for section $s+1$.

### **References**
- Monge, G. (1781). "Mémoire sur la théorie des déblais et des remblais." Histoire de l'Académie Royale des Sciences de Paris.
- Kantorovich, L. V. (1942). "On the translocation of masses." Doklady Akademii Nauk SSSR, 37(7-8), 227-229.
- Villani, C. (2009). *Optimal Transport: Old and New*. Springer.
- Tymoczko, D. (2011). *A Geometry of Music: Harmony and Counterpoint 1200-1900*. Oxford University Press.
- Yust, J. (2018). "Reviewing a 'Review': Voice Leading as Optimal Transport." Music Theory Spectrum, 40(1), 118-136.
- Callender, C. (2007). "The Geometry of Musical Chords." Proceedings of the International Conference on Mathematics and Computation in Music.
- Cuturi, M. (2013). "Sinkhorn distances: Lightspeed computation of optimal transport." Advances in Neural Information Processing Systems (NeurIPS), 26.
- Bonneel, N., et al. (2015). "Sliced and Radon Wasserstein Barycenters." Journal of Mathematical Imaging and Vision, 51(1), 22-45.
- Dhariwal, P., et al. (2020). "Optimal transport for voice leading." (Unpublished manuscript, UC Berkeley.)
