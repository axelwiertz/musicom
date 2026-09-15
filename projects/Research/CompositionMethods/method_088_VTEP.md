# Method 088 — Voronoi Tessellation Event Partitioning (VTEP)

- **Layer**: concrete (emits resolved MusicEvents into UnitMatrix cells; feeds `generators/`)
- **Paradigm**: Rules-Based (deterministic computational geometry; no RNG required)
- **Primary Elements**: Pitch, Rhythm, Harmony, Structure, Texture
- **One-line**: Scatter seeds in a normalized pitch×time domain, tessellate into nearest-seed Voronoi cells, and read composition directly off the geometry — cell area = density, Delaunay simplices = voicings, seed drift = form, seams = hockets.

---

## Extended math

### 1. Domain and seeds

Normalized bounded domain $\Omega = [0,1]_\text{pitch} \times [0,1]_\text{time}$, where the pitch axis maps linearly to the MIDI range $[p_{\min}, p_{\max}]$ and the time axis to the piece's tick span. An **aspect weight** $\lambda > 0$ rescales the pitch axis:

$$\tilde\Omega = \Omega_\text{time} \times \lambda \cdot \Omega_\text{pitch}$$

- $\lambda \gg 1$: pitch distances dominate → cells are time-wise strips → sustained horizontal lines.
- $\lambda \ll 1$: time distances dominate → cells are pitch-wise columns → arpeggio/hocket textures.

Seeds: $S = \{s_i\}_{i=1}^{S}$, $s_i = (x_i, y_i, \alpha_i, \kappa_i)$ with position, weight $\alpha_i > 0$ (voice prominence) and pitch-class attribute $\kappa_i$.

### 2. Power (weighted) Voronoi cells

$$V_i = \left\{\, x \in \tilde\Omega \;:\; \frac{\|x - s_i\|}{\alpha_i} \le \frac{\|x - s_j\|}{\alpha_j}\ \forall j \ne i \,\right\}$$

$\alpha_i > 1$ grows seed $i$'s territory (louder / more prominent voice); $\alpha_i < 1$ shrinks it. $\alpha_i \equiv 1$ recovers the ordinary Voronoi diagram.

### 3. Lattice classification (the composition step)

Candidate lattice $\Lambda = \{(p_k, t_k)\}$ — all (scale-pitch, 16th-grid onset) pairs in the section window. Classify:

$$c(k) = \arg\min_i \frac{\|(p_k, t_k) - s_i\|}{\alpha_i}$$

via a `scipy.spatial.cKDTree` over weighted seed coordinates (fold $\alpha$ into the metric by scaling axes, or query $k=4$ neighbors and re-rank by weighted distance). Complexity $O(L \log S)$ for $L$ lattice points.

### 4. Density from cell areas

Cell area $A_i$ (clip cells to $\Omega$ before measuring). Event budget per seed:

$$n_i = \left\lfloor n_\text{total} \cdot \frac{1/A_i}{\sum_j 1/A_j} \right\rceil$$

Small cell → large budget → crowded burst figure; large cell → few events → sustained/sparse. Inside a cell, distribute the $n_i$ onsets either uniformly or via `euclidean_rhythm(n_i, steps_in_cell)` (pairs with 011).

### 5. Harmony from the Delaunay dual

The Delaunay triangulation $\mathcal{D}$ of $S$ groups seeds into simplices. For each triangle $\{s_a, s_b, s_c\}$, form the pitch-class set $\{\kappa_a, \kappa_b, \kappa_c\}$, take normal form, and check its interval-class vector (ICV) against the section's target subset (from the abstract layer, e.g. an ABS-002 progression id). Accept iff consonant under the section's ICV tolerance; otherwise re-voice by rotating one vertex's $\kappa$ into the section subset, or drop. The accepted simplices scheduled inside a section's time span = the section's voicing blocks.

### 6. Structure from seed motion

Seed trajectories $s_i(t)$ across section boundaries:

- **Convergence** ($\|s_i - s_j\| \to 0$): cells shrink → $1/A_i$ rises → density climbs = build/tension.
- **Lloyd relaxation** (iterate seeds to cell centroids, 2–5 iterations): evenly sized cells = cadential evenness/resolution.
- **Insertion** ($S \to S+1$): new motif entrance (chorus hook).
- **Removal**: texture decay (outro).

Form = the script of seed configurations sampled at section starts; identical seed sets under different positions = variation of the same identity.

### 7. Seams = shared material

Lattice points whose two nearest seeds are within margin $\delta$ of equidistance lie on cell seams: emit the same onset in both cells' voices (hocket/echo). Hysteresis: a point keeps its previous owner unless the weighted-distance margin exceeds $\delta$ (≈2% of the domain diagonal) to prevent one-section flicker when seeds drift.

---

## Python implementation sketch

```python
# generators/voronoi_partition.py (candidate path — prose-only registration,
# promoted by weekly-method-code-registration)
import numpy as np
from scipy.spatial import cKDTree, Voronoi  # Voronoi/Delaunay dual via Qhull

def tessellate(seeds, lattice, weights=None, lam=1.0, jitter=1e-6):
    """seeds: (S,2) xy in normalized domain; lattice: (L,2); lam: pitch-axis weight."""
    rng = np.random.default_rng(0)                      # deterministic jitter
    s = seeds + rng.uniform(-jitter, jitter, seeds.shape)  # degeneracy guard
    s = s.copy(); s[:, 0] *= lam                        # aspect weight
    lat = lattice.copy(); lat[:, 0] *= lam
    w = np.ones(len(s)) if weights is None else np.asarray(weights)
    tree = cKDTree(s / w[:, None])                      # power diagram metric
    dist, idx = tree.query(lat, k=2)
    owner = idx[:, 0]
    seam = dist[:, 1] - dist[:, 0] < 0.02               # bisector margin -> hocket
    return owner, seam

def cell_densities(seeds, lam=1.0, clip=(0.0, 1.0)):
    """Clip Voronoi cells to the domain and return inverse-area weights."""
    from scipy.spatial import Voronoi
    s = seeds.copy(); s[:, 0] *= lam
    vor = Voronoi(s)                                    # unbounded regions included
    areas = np.zeros(len(s))
    # ... clip each vor.regions[region] polygon to the unit square
    #     (Sutherland-Hodgman) and shoelace the remainder ...
    inv = 1.0 / np.maximum(areas, 1e-9)
    return inv / inv.sum()                              # density budget per seed

def compose_vtep(section_plan, scale_filter, n_total=64):
    """section_plan: {section: (seeds, weights, lam)}; scale_filter: pc-set mask."""
    events = []
    for name, (seeds, w, lam) in section_plan.items():
        lattice = build_lattice(scale_filter)           # scale-masked (pitch,time) grid
        owner, seam = tessellate(seeds, lattice, w, lam)
        budget = cell_densities(seeds, lam)
        for i in range(len(seeds)):
            pts = lattice[owner == i]
            k = int(round(n_total * budget[i]))
            onsets = pick_onsets(pts, k)                # uniform or euclidean_rhythm
            events += realize(points=pts[onsets], pc=pcs_of(seeds[i]),
                              hocket_with=neighbors_via(seam, i))
    return events  # -> UnitMatrix cells via create_note_unit; validate(); to_midi()
```

Deterministic per seed plan (the only "randomness" is the fixed-seed degeneracy jitter), so the zero-drift golden gate is trivially stable.

---

## References
- Voronoy, G. (1908). *J. reine angew. Math.* 133, 97–178 / 134, 198–287.
- Dirichlet, P. G. L. (1850). *J. reine angew. Math.* 40, 209–227.
- Thiessen, A. H. (1911). *Monthly Weather Review* 39(7), 1082–1084.
- Delaunay, B. (1934). "Sur la sphère vide." *Bull. Acad. Sci. URSS* 6, 793–800.
- Lloyd, S. P. (1982). "Least Squares Quantization in PCM." *IEEE Trans. Inf. Theory* 28(2), 129–137.
- Aurenhammer, F. (1991). "Voronoi diagrams — a survey." *ACM Comput. Surv.* 23(3), 345–405.
- Okabe, A., Boots, B., Sugihara, K., & Chiu, S. N. (2000). *Spatial Tessellations*, 2nd ed. Wiley.
- Du, Q., Faber, V., & Gunzburger, M. (1999). "Centroidal Voronoi Tessellations." *SIAM Rev.* 41(4), 637–676.
- Barber, C. B., Dobkin, D. P., & Huhdanpaa, H. (1996). "The Quickhull Algorithm." *ACM TOMS* 22(4), 469–483.

Full DB entry: `methods_db.md` → `# Voronoi Tessellation Event Partitioning (VTEP) (Method 088)`.
