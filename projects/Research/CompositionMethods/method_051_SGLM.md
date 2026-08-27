# Spectral Graph Laplacian Mapping (SGLM) (Method 051)

### **Source**
Adapted from spectral graph theory: the graph Laplacian $L = D - A$ (degree minus adjacency), whose eigendecomposition was pioneered by Fiedler (1973, "Algebraic Connectivity of Graphs", Czechoslovak Mathematical Journal) and developed into spectral partitioning by Donath & Hoffman (1973) and Fiedler's bisection work (1975). Formalized in Chung (1997) *Spectral Graph Theory* (AMS) and von Luxburg (2007) "A Tutorial on Spectral Clustering" (Statistics and Computing, 17(4), 395-416). Musical applications draw on Tymoczko (2011) *A Geometry of Music* (orbifold voice-leading geometry), Lewin (1987) *Generalized Musical Intervals and Transformations* (transformational networks), and recent computational work using graph spectra for tonal hierarchy and harmonic-network analysis. This formulation extends discrete graph traversal methods (011 Voice-Leading Graph Search, 041 ACOPF) by using the *global spectrum* of the graph rather than local path search.

### **Description**
Spectral Graph Laplacian Mapping (SGLM) builds a graph $G = (V, E)$ whose nodes are musical objects (pitch classes, chords, scale degrees, or voices) and whose weighted edges encode affinity: consonance (frequency-ratio proximity, harmonic distances), voice-leading smoothness, or transition probability. The method then computes the eigendecomposition of the graph Laplacian:

$$L = D - A, \qquad L v_i = \lambda_i v_i, \qquad 0 = \lambda_0 \le \lambda_1 \le \cdots \le \lambda_{n-1}$$

where $A$ is the (possibly weighted) adjacency matrix and $D$ is the degree matrix. The eigenvectors (Fiedler vector $v_1$, and higher modes $v_2, v_3, \ldots$) form a smooth, global coordinate system over the graph — a 1D spectral embedding that sorts nodes by their position along each eigen-mode. Two structural facts drive the musical mapping:

1. **Algebraic connectivity** $\lambda_1$ measures how tightly the graph is connected: $\lambda_1 = 0$ iff the graph is disconnected; small $\lambda_1$ = weakly coupled, easily separable clusters. Cheeger's inequality bounds the graph's conductance (expansion) in terms of $\lambda_1$: $\frac{\lambda_1}{2} \le h(G) \le \sqrt{2\lambda_1}$.
2. **Fiedler vector** $v_1$ partitions the graph into two coherent clusters (nodes with $v_1 < 0$ vs $v_1 > 0$); higher eigenvectors refine this into a smooth ordering. This is the same machinery used in spectral clustering and graph bisection (image segmentation, community detection).

Compositionally, SGLM uses the spectrum as a *global tonal/structural coordinate field*: nodes that are harmonically close receive nearby spectral coordinates, and the eigenvector orderings generate monotonic, smooth pitch contours, phrase arcs, and section transitions without any explicit stepwise motion rules.

### **Musical Elements Framework**
- **PITCH**: The pitch-class set (or scale-degree set) is a graph node set; edges weighted by consonance (e.g., $w_{ij} = 1/d_{ij}$ where $d_{ij}$ = pitch-class circular distance, or harmonic-affinity from frequency-ratio simplicity). The Fiedler vector $v_1$ sorts pitch classes along a smooth line; assigning the sorted order to ascending pitch classes yields a *spectral scale* — an ordering that maximizes harmonic coherence within the constraint graph. Higher eigenvectors $v_k$ produce secondary melodic axes (e.g., a modal contrast axis). Fiedler partitioning splits the set into consonant sub-clusters that map naturally to chord regions and registral groups.
- **RHYTHM**: The eigenvalue gaps $\Delta_k = \lambda_k - \lambda_{k-1}$ govern onset density: dense eigenvalue clusters (small gaps) = sparse, sustained rhythm; wide spectral gaps = the natural hierarchical separation between structural levels, used to set phrase boundaries and section-level pulses. The sign of the Fiedler-vector entries acts as a binary on/off mask for event triggering across the grid. Cheeger ratio $h(G) = \frac{|\partial S|}{\min(|S|, |V \setminus S|)}$ controls accent placement: nodes at the partition boundary receive metric accents (edge emphasis).
- **HARMONY**: Algebraic connectivity $\lambda_1$ is a continuous harmonic-tension scalar: low $\lambda_1$ = weakly connected, tense/ambiguous harmony (chromatic or atonal regions); high $\lambda_1$ = strongly connected, stable, consonant centers. Section-level harmonic function (HOME/LIFT/TENSE/TURN) is set by re-weighting graph edges per section: HOME sections use high-affinity edges (large $\lambda_1$), TENSE sections use sparse/lower-weight edges (small $\lambda_1$). Spectral clustering of the chord graph yields functional chord families (tonic, dominant, subdominant clusters) automatically.
- **STRUCTURE**: The global form is the *spectral hierarchy* of the piece graph: the multiscale community structure (dendrogram of the graph) defines Sections (columns). Recursive Fiedler bisection ($O(\log n)$ levels) produces a balanced binary form tree — the natural scaffolding for ABA, rondo, or sonata layouts, each level of bisection = one level of formal contrast. The spectrum's overall shape (gapped vs. dense) determines the piece's macro-arc: a spectrum with one dominant gap = clear binary contrast; a smooth spectrum = through-composed flow.
- **TEXTURE**: Voice allocation uses the spectral embedding: each voice $v$ is assigned an eigenvector (or a spectral coordinate band); voices on the same eigenvector are mutually coherent (chorus-like), voices on different eigenvectors are independent (contrapuntal). The multiplicity of eigenvalue $\lambda_k$ (degeneracy) sets the number of independent simultaneous layers — a degenerate eigenvalue = several identical spectral roles, yielding unison/octave doubling; a simple spectrum = fully independent polyphonic strands. Texture density scales with the number of active eigenvectors projected onto the time axis.

### **UnitMatrix Integration (Voices & Sections)**
- **Rows (Voices)**: Each voice $v$ = one eigenvector (or spectral-coordinate band) of the section's graph. Voice 1 = Fiedler direction (primary melodic axis), Voice 2 = second eigenvector (counter-axis), Bass = lowest spectral coordinate (graph node with minimal Fiedler entry in the bass register). Voices inherit orthogonality from the eigenvectors: independent motion is guaranteed by construction.
- **Columns (Sections)**: Each section $s$ = a graph state with its own edge-weight matrix $W_s$ (section-specific consonance/affinity profile) and thus its own spectrum $(\lambda^{(s)}_k, v^{(s)}_k)$. Section transitions = spectral morphing: interpolate edge weights $W(t) = (1-t)W_s + tW_{s+1}$ and re-solve the eigenproblem at intermediate times for smooth harmonic-field rotation.
- **Cells** $U_{v, s}$:
  - `{PITCH}`: Pitch set for voice $v$ in section $s$ = graph nodes ordered by eigenvector $v^{(s)}_v$, mapped to the active scale; quantized to chord tones in Phase 2.
  - `{RHYTHM}`: Onset mask from sign patterns / boundary sets of $v^{(s)}_v$; density from eigenvalue gaps $\Delta^{(s)}_k$.
  - `{TEXTURE}`: Active eigenvector count $K_s$, eigenvalue degeneracies, and per-voice spectral coordinate bands (voice independence coefficients).
- **Mapping Flow**:
  1. Define the node set (pitch classes, chords, scale degrees) and per-section affinity matrix $W_s$.
  2. Build Laplacian $L_s = D_s - W_s$; compute eigenvalues $\lambda^{(s)}_k$ and eigenvectors $v^{(s)}_k$ (Lanczos / `scipy.sparse.linalg.eigsh`, $k \ll n$).
  3. Sort nodes by each eigenvector to get spectral orderings; partition by Fiedler sign for chord-region and section contrast.
  4. Assign eigenvector $v$ per voice row; populate cells with ordered pitches, sign-mask rhythms, and gap-derived densities.
  5. For transitions, interpolate $W_s \to W_{s+1}$ and re-solve; apply musicom Phase-2 rules (chord-tone quantization, voice-leading checks) on the spectral output.

### **Pitfalls**
1. **Disconnected graphs**: If the affinity graph splits, $\lambda_1 = 0$ and the Fiedler vector is meaningless. Add a connectivity floor to edge weights or use a fully connected kernel (Gaussian affinity).
2. **Eigenvector sign ambiguity**: Eigenvectors are defined up to sign ($-v$ is also an eigenvector). Normalize orientation consistently (e.g., largest-|entry| positive) per section so ordering is stable across sections.
3. **Degenerate eigenvalues**: Symmetric graphs (e.g., a fully connected consonant graph) yield repeated eigenvalues; the corresponding eigen-subspace is arbitrary. Perturb edge weights slightly (break symmetry) or use the subspace projection rather than individual vectors.
4. **Node-ordering reversal**: Fiedler entries are a *relative* ordering; the musically "correct" direction (ascending vs descending pitch) is arbitrary. Fix by correlating with the tonic node (tonic = minimum spectral coordinate).
5. **Computational cost**: Dense eigendecomposition is $O(n^3)$; for large graphs (hundreds of nodes) use sparse Lanczos (`eigsh`) — $O(nk)$ per iteration, only $k$ low eigenvectors needed.
6. **Spectral gap sensitivity**: Small perturbations in edge weights can reorder close eigenvalues. Use stable affinity kernels (heat kernel $w_{ij} = e^{-d_{ij}^2/2\sigma^2}$) and avoid near-zero weights.
7. **Scale/tonality drift**: Spectral orderings are not guaranteed to match diatonic expectations. Always quantize to the active scale and enforce tonic anchoring (pitfall 4) in Phase 2.
8. **Textural mono-chroma**: If all voices use the same eigenvector region, texture collapses to unison. Enforce per-voice eigenvector separation or use eigenvalue multiplicity to spread roles.
9. **Section discontinuity**: Re-solving the eigenproblem per section can produce unrelated orderings. Chain solutions: warm-start with the previous section's eigenvectors as initial guesses, and interpolate $W(t)$ for transitions.
10. **Over-smoothing**: Very high affinity (all weights $\approx 1$) makes all non-trivial eigenvalues cluster near the maximum, destroying contrast. Scale weights so that $\lambda_1$ lands in a sensitive range (normalize Laplacian $L_{sym} = D^{-1/2} L D^{-1/2}$ recommended).

### **References**
- Fiedler, M. (1973). "Algebraic connectivity of graphs." Czechoslovak Mathematical Journal, 23(98), 298-305.
- Fiedler, M. (1975). "A property of eigenvectors of nonnegative symmetric matrices and its application to graph theory." Czechoslovak Mathematical Journal, 25(100), 619-633.
- Donath, W. E., and Hoffman, A. J. (1973). "Lower bounds for the partitioning of graphs." IBM Journal of Research and Development, 17(5), 420-425.
- Chung, F. R. K. (1997). *Spectral Graph Theory*. CBMS Regional Conference Series in Mathematics 92, AMS.
- von Luxburg, U. (2007). "A tutorial on spectral clustering." Statistics and Computing, 17(4), 395-416.
- Cheeger, J. (1970). "A lower bound for the smallest eigenvalue of the Laplacian." In *Problems in Analysis*, Princeton University Press, 195-199.
- Tymoczko, D. (2011). *A Geometry of Music: Harmony and Counterpoint in the Extended Common Practice*. Oxford University Press.
- Lewin, D. (1987). *Generalized Musical Intervals and Transformations*. Yale University Press.
