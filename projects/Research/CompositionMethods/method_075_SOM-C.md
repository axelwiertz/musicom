# Method 075 — Self-Organizing Map Composition (SOM-C)

**Paradigm**: Stochastic (corpus-learned discrete topology; walk = probabilistic)
**One-line**: Train a Kohonen self-organizing map on corpus atoms, then compose by walking trajectories across it — adjacent nodes = smooth voice leading, U-matrix ridges = section seams, concurrent walkers = voices.

---

## Extended Mathematics

### 1. Competitive learning (topology-preserving projection)
Given corpus atoms $\{x^{(i)}\} \subset \mathbb{R}^d$ and a toroidal grid of $M = m \times n$ prototypes $w_j \in \mathbb{R}^d$, for each input find the best-matching unit

$$c^{(i)} = \arg\min_j \|x^{(i)} - w_j\|_2^2$$

then update all prototypes with a Gaussian neighborhood centered on the BMU:

$$w_j \leftarrow w_j + \alpha(t)\, h_{c^{(i)} j}(t)\, \big(x^{(i)} - w_j\big), \qquad
h_{cj}(t) = \exp\!\left(-\frac{d_T^2(c,j)}{2\sigma^2(t)}\right)$$

where $d_T$ is the **toroidal grid distance** (shortest path with wrap-around):

$$d_T(c,j) = \sqrt{\,\Delta i^2 + \Delta j^2\,}, \qquad
\Delta i = \min(|i_c - i_j|,\ m - |i_c - i_j|), \quad
\Delta j = \min(|j_c - j_j|,\ n - |j_c - j_j|).$$

Learning-rate and radius schedules (common defaults):

$$\alpha(t) = \alpha_0\left(1 - \tfrac{t}{T}\right), \qquad \sigma(t) = \sigma_0\left(1 - \tfrac{t}{T}\right) + \epsilon, \qquad \sigma_0 = \max(m,n)/2.$$

The map converges to a **discretized, topology-preserving estimate of the corpus manifold**: $w_j \approx w_{j'}$ iff $j, j'$ are grid-adjacent iff their corpus Voronoi cells are similar.

### 2. U-matrix (structure cue)
The unified-distance matrix assigns each node the mean prototype distance to its $k$ toroidal neighbors:

$$U_j = \frac{1}{|N_k(j)|}\sum_{j' \in N_k(j)} \|w_j - w_{j'}\|_2.$$

Low $U_j$ ⇒ interior of a homogeneous "region" (one harmonic/registral home). High $U_j$ ⇒ a **ridge** (a boundary between regions). Section boundaries are chosen at U-matrix ridges; the macro-form is the sequence of regions the trajectory crosses.

### 3. Trajectory generation (Markov walk over the grid)
The composition walker is a Markov chain on the $M$ nodes with a similarity kernel:

$$P(j \to j') \;\propto\; \mathbf{1}[j' \in N_k(j)]\, e^{-\beta \|w_j - w_{j'}\|_2^2} \;\cdot\; e^{-\gamma \, d_T(j', R_s)}$$

- $\beta$ = exploration temperature (small ⇒ diffuse, large ⇒ stuck in one region; anneal it for a coherent-to-committed arc, mirroring 055 SAMC).
- $\gamma$ = **region potential** strength: soft-attracts the walker toward waypoint region $R_s$ (its centroid node), so a section keeps its identity while still breathing.
- $N_k(j)$ = toroidal $k$-neighborhood (grid adjacency, usually 8-neighborhood).

At each step, emit $w_{j}$ decoded to a note/chord/rhythm atom. A **deterministic gradient** variant steps to $\arg\max_{j'} P(j\to j')$ (directed harmonic motion); add noise to avoid two-node dead-oscillation.

### 4. Multi-voice coupling
For $V$ concurrent walkers, define a vertical coherence term. Walker $v$'s transition gains an attraction to the centroid of the other walkers' prototypes:

$$P^{(v)}(j \to j') \propto e^{-\beta\, \|w_j - w_{j'}\|^2} \;\cdot\; e^{-\eta\, \big\|w_{j'} - \bar{w}^{(-v)}\big\|^2}, \qquad
\bar{w}^{(-v)} = \tfrac{1}{V-1}\sum_{u \neq v} w_{j^{(u)}}.$$

- $\eta = 0$ ⇒ independent counterpoint.
- $\eta \gg 0$ ⇒ lock-step homophony (all voices drawn to a common region = a chord).
- Intermediate $\eta$ ⇒ loose parallel motion (the idiom of 056 SCCC species-1, learned instead of rule-checked).

**Continuous dissonance/density scalar** between two voices: $\delta_{uv} = \|w_{j^{(u)}} - w_{j^{(v)}}\|_2$ (map-space distance). Near 0 ⇒ unison/cluster; large ⇒ register spread.

### 5. Complexity
- Training: $\mathcal{O}(E \cdot I \cdot N \cdot M)$ for $E$ epochs, $I$ corpus atoms, dimension $N = d$, $M$ nodes.
- Generation: $\mathcal{O}(T \cdot M)$ for a $T$-step walk with full BMU/neighbor scan; $\mathcal{O}(T \log M)$ with a KD/faiss index; $\mathcal{O}(T)$ for grid-adjacent steps (neighbor list only).

---

## Python Implementation Sketch

```python
from __future__ import annotations
import numpy as np
from numpy.random import default_rng

class SOM:
    """Kohonen self-organizing map (toroidal, Gaussian neighborhood)."""
    def __init__(self, m, n, dim, seed=0):
        self.rng = default_rng(seed)
        self.m, self.n, self.dim = m, n, dim
        self.w = self.rng.normal(0, 0.1, (m, n, dim))
        self.r = np.array([(i, j) for i in range(m) for j in range(n)])

    def _tord(self, ci, rj):
        d = np.abs(self.r[ci] - rj)
        d = np.minimum(d, np.array([self.m, self.n]) - d)
        return np.sum(d * d)

    def train(self, data, epochs=100, a0=0.1, s0=None):
        s0 = s0 or max(self.m, self.n) / 2
        W = self.w.reshape(-1, self.dim)
        for e in range(epochs):
            a = a0 * (1 - e / epochs)
            s = s0 * (1 - e / epochs) + 1e-6
            for x in data:
                ci = int(np.argmin(np.sum((W - x) ** 2, axis=1)))
                for j in range(self.m * self.n):
                    h = np.exp(-self._tord(ci, self.r[j]) / (2 * s * s))
                    W[j] += a * h * (x - W[j])

    def bmu(self, x):
        return int(np.argmin(np.sum((self.w.reshape(-1, self.dim) - x) ** 2, axis=1)))

    def u_matrix(self):
        U = np.zeros((self.m, self.n))
        for i in range(self.m):
            for j in range(self.n):
                nb = []
                for di in (-1, 0, 1):
                    for dj in (-1, 0, 1):
                        if di == 0 and dj == 0:
                            continue
                        nb.append(self.w[(i + di) % self.m, (j + dj) % self.n])
                U[i, j] = np.mean([np.linalg.norm(self.w[i, j] - w) for w in nb])
        return U

    def walk(self, start, steps, beta=2.0, waypoint=None, gamma=0.0, seed=None):
        """Stochastic diffusion; waypoint = soft region anchor (centroid index)."""
        rng = default_rng(seed) if seed is not None else self.rng
        W = self.w.reshape(-1, self.dim)
        pos, path = start, [start]
        for _ in range(steps):
            d = np.sum((W - W[pos]) ** 2, axis=1)
            p = np.exp(-beta * d)
            if waypoint is not None:
                p *= np.exp(-gamma * np.sum((W - W[waypoint]) ** 2, axis=1))
            p[pos] = 0.0
            p /= p.sum()
            pos = int(rng.choice(len(W), p=p))
            path.append(pos)
        return path


def demo_tonal_som():
    """Toy: 24 key-profile atoms (Krumhansl–Kessler, major+minor) on a 12x8 torus."""
    # 12 major + 12 minor key profiles, 12 pitch-class dims (abbreviated generator)
    profiles = []
    for tonic in range(12):
        major = np.zeros(12); minor = np.zeros(12)
        # K-K major/minor profile weights over pitch classes relative to tonic
        major_w = [6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88]
        minor_w = [6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17]
        for k in range(12):
            major[(tonic + k) % 12] = major_w[k]
            minor[(tonic + k) % 12] = minor_w[k]
        profiles.append(major); profiles.append(minor)
    som = SOM(12, 8, 12, seed=0)
    som.train(np.array(profiles), epochs=500, a0=0.3)
    # Walk: 8 steps anchored near the C-major region (index 0)
    path = som.walk(som.bmu(profiles[0]), steps=8, beta=1.5,
                    waypoint=som.bmu(profiles[0]), gamma=0.2)
    return som, path
```

**Musicom integration note (per AGENTS.md)**: SOM-C only *emits decoded prototype atoms* — the actual MIDI authoring goes through `UnitMatrixComposer` (`fill_voice_section` → `create_note_unit`/`create_chord_unit` → `composer.validate()` → `to_midi()`). Never hand-roll `mido`.

---

## References

- Kohonen, T. (1982). "Self-organized formation of topologically correct feature maps." *Biological Cybernetics* 43(1), 59–69.
- Kohonen, T. (2001). *Self-Organizing Maps* (3rd ed.). Springer Series in Information Sciences, vol. 30.
- Toiviainen, P. (2005). "Visualization of tonal content with self-organizing maps and self-similarity matrices." *Computers in Entertainment* 3(4), 1–10. (ACM doi:10.1145/1095534.1095543.)
- Toiviainen, P., & Krumhansl, C. L. (2003). "Measuring and modeling real-time responses to music: the dynamics of tonality induction." *Perception* 32(6), 741–766.
- Krumhansl, C. L. (1990). *Cognitive Foundations of Musical Pitch.* Oxford University Press.
- Morchen, F., Ultsch, A., Thies, M., & Lohken, I. (2006). "Modeling timbre distance with temporal statistics from polyphonic music." *IEEE Trans. Audio, Speech & Language Processing* 14(1).

---

## Classification

| Field | Value |
|---|---|
| Method ID | 075 |
| Acronym | SOM-C |
| Name | Self-Organizing Map Composition |
| Paradigm | Stochastic |
| Primary Elements | Pitch, Rhythm, Harmony, Structure, Texture |
| Tonal Gravity | Moderate (Region-guided) |
| Metric Binding | Grid-Locked / Continuous |
| Memory Depth | Macro / Map Trajectory |
| Time Complexity | $\mathcal{O}(E \cdot I \cdot N \cdot M)$ training, $\mathcal{O}(T \cdot M)$ generation |
