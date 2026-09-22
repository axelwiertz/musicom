# Method 093: Percolation Process Network Criticality (PPNC)

**Paradigm:** Nature-Led  
**Layer:** `concrete` (feeds `generators/`; L3 meso section coordination and L2 voice contours)  
**Tonal Gravity:** Moderate (Critical-connectivity guided)  
**Metric Binding:** Grid-Locked / Continuous  
**Memory Depth:** Meso / Cluster Lattice  
**Time Complexity:** $\mathcal{O}(V \cdot T)$ direct simulation, $\mathcal{O}(N \alpha(N))$ Disjoint-Set Union (DSU) labeling  

---

## 1. Mathematical Formulation

Percolation theory examines the behavior of connected clusters on random graphs and regular lattices $\mathcal{L} = (S, B)$, where $S$ denotes vertices (sites) and $B$ denotes edges (bonds).

### 1.1 Site and Bond Percolation

Let $\mathcal{L}$ be a $d$-dimensional hypercubic lattice.
1. **Site Percolation:** Each site $s \in S$ is independently declared *occupied* with probability $p \in [0, 1]$ and *vacant* with probability $1 - p$:
   $$\mathbb{P}(X_s = 1) = p, \quad \mathbb{P}(X_s = 0) = 1 - p$$
2. **Bond Percolation:** Each bond $b = (s, s') \in B$ is independently *open* with probability $p_b$ and *closed* with probability $1 - p_b$.
3. **Directed Percolation (DP):** On a directed lattice (such as $\mathbb{Z}^{d-1} \times \mathbb{Z}^+$ where time flows forward), connectivity is strictly forward-directed: bonds exist only from $(x, t)$ to $(x \pm 1, t+1)$ with transmission probability $p_t$.

### 1.2 Phase Transitions and Critical Exponents

For an infinite lattice, there exists a sharp non-thermal critical threshold $p_c \in (0, 1)$ such that:
$$\theta(p) = \begin{cases} 0 & p < p_c \quad \text{(subcritical: only finite clusters)} \\ >0 & p > p_c \quad \text{(supercritical: unique infinite spanning cluster exists)} \end{cases}$$
where $\theta(p)$ is the percolation probability (fraction of sites belonging to the infinite cluster).

Near the critical threshold $p \to p_c$, macroscopic physical quantities obey universal scale-invariant power laws governed by critical exponents:
- **Correlation length:** $\xi(p) \propto |p - p_c|^{-\nu}$
- **Percolation strength:** $\theta(p) \propto (p - p_c)^\beta$ for $p > p_c$
- **Average cluster size:** $\chi(p) = \sum_s s^2 n_s(p) \propto |p - p_c|^{-\gamma}$
- **Cluster size distribution at criticality:**
  $$n_s(p_c) \propto s^{-\tau}$$
  For 2D square lattices ($d=2$):
  - $p_c^{\text{site}} \approx 0.592746$
  - $p_c^{\text{bond}} = 1/2 = 0.500000$
  - $\nu = 4/3 \approx 1.333$
  - $\beta = 5/36 \approx 0.139$
  - $\gamma = 43/18 \approx 2.389$
  - $\tau = 187/91 \approx 2.055$
  - Fractal dimension of the critical cluster: $D_f = d - \beta/\nu = 91/48 \approx 1.896$

For $1+1$ directed percolation:
- $p_c^{\text{bond}} \approx 0.6447$
- $p_c^{\text{site}} \approx 0.7055$
- Longitudinal correlation length exponent: $\nu_\parallel \approx 1.733$
- Transverse correlation length exponent: $\nu_\perp \approx 1.097$

---

## 2. Musical Mapping & UnitMatrix Architecture

Method 093 maps the **UnitMatrix** as a spatio-temporal lattice $\mathcal{L} = \mathcal{V} \times \mathcal{T}$:
- **Rows ($\mathcal{V}$):** Represent voice strata ($v \in \{0, \dots, V-1\}$) or discrete register/pitch classes.
- **Columns ($\mathcal{T}$):** Represent discrete metric subdivision time slots ($t \in \{0, \dots, T-1\}$).
- **Cells (Sites $(v, t)$):** Represent candidate musical events.

### 2.1 The Three Musical Percolation Regimes

1. **Subcritical Regime ($p \ll p_c$):**
   - Cluster size is exponentially truncated: $n_s \sim s^{-\tau} e^{-s/s^*}$ with cutoff $s^* \propto |p - p_c|^{-1/\sigma}$.
   - *Musical result:* Pointillistic, sparse, isolated staccato events; micro-motifs of 1–3 notes separated by long rests. High rhythmic entropy, light textural density.
2. **Critical Regime ($p \approx p_c$):**
   - Scale-free cluster distribution $n_s \propto s^{-\tau}$. Spanning clusters bridge across sections.
   - *Musical result:* Power-law distribution of note durations and phrase lengths (Zipfian musical rhythm). Organic balance between conjunct melodic coherence (within-cluster bonds) and unexpected rhythmic syncopation (inter-cluster gaps). Maximum structural complexity.
3. **Supercritical Regime ($p \gg p_c$):**
   - Giant cluster engulfs the majority of the lattice sites: $\theta(p) \to 1$.
   - *Musical result:* Dense polyphonic wall of sound, sustained organum/choral drone, saturated harmonies.

### 2.2 Musical Elements Framework

- **PITCH:**
  - Sites within the same connected cluster $\mathcal{C}_k$ are assigned pitches with constrained melodic intervals ($|\Delta p| \le 2$ scale steps), preserving melodic contour smoothness.
  - Cluster index $k$ maps to root tonal pivots or scale degree transpositions via modulo arithmetic over an active pitch-class set $\mathcal{S}$ provided by the abstract layer (e.g., ABS-002 mode or chord pool).
- **RHYTHM:**
  - Horizontal runs of occupied sites $(v, t), (v, t+1), \dots, (v, t+\ell-1)$ belonging to the same cluster merge into a single sustained note of duration $\ell \times \Delta t_{\text{tick}}$.
  - The power-law distribution $P(\ell) \propto \ell^{-\tau}$ at $p_c$ naturally yields natural musical durations: many 16th/8th notes, occasional dotted halves, and rare whole-measure holds.
- **HARMONY:**
  - Vertical bonds between $(v, t)$ and $(v+1, t)$ enforce harmonic consonance. Vertically bonded voices are assigned pitch intervals corresponding to consonant sonorities (unisons, 3rds, 4ths, 5ths, 6ths, octaves).
  - Unbonded vertical overlaps introduce tension/passing dissonances (2nds, tritones, 7ths).
- **STRUCTURE (Macro-Form Tension Trajectory):**
  - Section columns in the UnitMatrix are driven by an engineered occupation parameter trajectory $p(s)$:
    - Section 1 (Intro): $p = 0.32$ (Subcritical: sparse, fragmentary).
    - Section 2 (Verse): $p = 0.50$ (Subcritical approaching critical: rhythmic motifs solidify).
    - Section 3 (Chorus): $p = 0.593 \approx p_c$ (Critical: spanning cluster, full polyphonic breadth).
    - Section 4 (Bridge): $p = 0.28$ (Subcritical breakdown: pointillistic decay).
    - Section 5 (Outro): $p = 0.80 \to 0.20$ (Supercritical burst transitioning to fade).
- **TEXTURE:**
  - Directly governed by the number of active clusters and the giant cluster fraction $\theta(p)$. Seamless morphing between monophony, polyphonic counterpoint, and dense homophonic mass.

---

## 3. Disjoint-Set Union (DSU) & Clustering Algorithm

To identify connected clusters in $\mathcal{O}(V \cdot T \cdot \alpha(V \cdot T))$ almost-linear time, we employ the Disjoint-Set Union (Union-Find) data structure with path compression and union by rank:

```python
class DisjointSet:
    def __init__(self, size: int):
        self.parent = list(range(size))
        self.rank = [0] * size

    def find(self, i: int) -> int:
        if self.parent[i] != i:
            self.parent[i] = self.find(self.parent[i])
        return self.parent[i]

    def union(self, i: int, j: int):
        root_i = self.find(i)
        root_j = self.find(j)
        if root_i != root_j:
            if self.rank[root_i] < self.rank[root_j]:
                self.parent[root_i] = root_j
            elif self.rank[root_i] > self.rank[root_j]:
                self.parent[root_j] = root_i
            else:
                self.parent[root_j] = root_i
                self.rank[root_i] += 1
```

---

## 4. Complete Python Implementation Sketch

```python
"""
Method 093: Percolation Process Network Criticality (PPNC)
Generates polyphonic music via 2D lattice percolation near critical thresholds.
"""
from typing import List, Tuple, Dict, Set, Optional
import numpy as np
from structures import MusicUnit, MusicEvent, UnitMatrix, MidiInstrument
from workflows.unitmatrix_composer import UnitMatrixComposer

def simulate_percolation_grid(
    num_voices: int,
    num_steps: int,
    p_occ: float = 0.5927,
    seed: int = 42
) -> np.ndarray:
    """
    Simulate 2D site percolation on a voice x time lattice.
    """
    rng = np.random.default_rng(seed)
    return rng.random((num_voices, num_steps)) < p_occ

def label_clusters_4conn(grid: np.ndarray) -> Tuple[np.ndarray, Dict[int, int]]:
    """
    Label connected components using 4-connectivity (von Neumann neighborhood).
    Returns label matrix and cluster size dictionary.
    """
    rows, cols = grid.shape
    labels = np.zeros((rows, cols), dtype=int)
    cluster_sizes: Dict[int, int] = {}
    current_label = 0
    
    for r in range(rows):
        for c in range(cols):
            if grid[r, c] and labels[r, c] == 0:
                current_label += 1
                queue = [(r, c)]
                labels[r, c] = current_label
                size = 0
                while queue:
                    curr_r, curr_c = queue.pop(0)
                    size += 1
                    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nr, nc = curr_r + dr, curr_c + dc
                        if 0 <= nr < rows and 0 <= nc < cols:
                            if grid[nr, nc] and labels[nr, nc] == 0:
                                labels[nr, nc] = current_label
                                queue.append((nr, nc))
                cluster_sizes[current_label] = size
                
    return labels, cluster_sizes

def check_horizontal_spanning(labels: np.ndarray) -> List[int]:
    """
    Find clusters that horizontally span from time t=0 to time t=cols-1.
    """
    cols = labels.shape[1]
    left_labels = set(labels[:, 0]) - {0}
    right_labels = set(labels[:, cols - 1]) - {0}
    return list(left_labels.intersection(right_labels))

def compose_percolation_section(
    p_occ: float,
    bars: int = 4,
    num_voices: int = 4,
    bpm: int = 120,
    seed: int = 42,
    base_pitches: Optional[List[int]] = None,
    scale_steps: Optional[List[int]] = None
) -> UnitMatrixComposer:
    """
    Compose a zero-drift validated UnitMatrix section using percolation criticality.
    """
    if base_pitches is None:
        base_pitches = [72, 60, 48, 36]  # Soprano, Alto, Tenor, Bass
    if scale_steps is None:
        scale_steps = [0, 2, 4, 5, 7, 9, 11, 12, 14, 16] # Diatonic major extensions
        
    ticks_per_step = 120  # 16th note at 480 TPB
    steps_per_bar = 16
    total_steps = bars * steps_per_bar
    total_ticks = bars * 1920
    
    grid = simulate_percolation_grid(num_voices, total_steps, p_occ=p_occ, seed=seed)
    labels, cluster_sizes = label_clusters_4conn(grid)
    spanning = check_horizontal_spanning(labels)
    
    composer = UnitMatrixComposer(bpm=bpm, ticks_per_beat=480, beats_per_bar=4)
    composer.create_matrix(num_voices=num_voices, num_sections=1)
    
    voice_names = ["Soprano", "Alto", "Tenor", "Bass"]
    instruments = [
        MidiInstrument.FLUTE,
        MidiInstrument.VIOLIN,
        MidiInstrument.STRING_ENSEMBLE,
        MidiInstrument.BASS
    ]
    
    for v in range(num_voices):
        composer.add_voice(voice_names[v], program=instruments[v], channel=v)
    composer.add_section("A", bars=bars)
    
    for v in range(num_voices):
        events: List[MusicEvent] = []
        step = 0
        while step < total_steps:
            if grid[v, step]:
                cid = labels[v, step]
                # Measure run length of contiguous active pulses in this voice
                run_len = 1
                while (step + run_len < total_steps and 
                       grid[v, step + run_len] and 
                       labels[v, step + run_len] == cid):
                    run_len += 1
                    
                start_tick = step * ticks_per_step
                end_tick = min((step + run_len) * ticks_per_step, total_ticks)
                
                # Pitch selection based on cluster ID and spanning bonus
                scale_deg = (cid * 2 + (1 if cid in spanning else 0)) % len(scale_steps)
                pitch = base_pitches[v] + scale_steps[scale_deg]
                
                # Velocity: larger clusters get accented, spanning clusters louder
                base_vel = 75 if cid not in spanning else 95
                vel = int(np.clip(base_vel + min(30, cluster_sizes.get(cid, 1) * 2), 40, 127))
                
                events.append(MusicEvent(
                    pitch=pitch,
                    volume=vel,
                    start_tick=start_tick,
                    end_tick=end_tick
                ))
                step += run_len
            else:
                step += 1
                
        # Zero-drift padding event terminating at total_ticks
        pad = MusicEvent(pitch=0, volume=0, start_tick=max(0, total_ticks - 1), end_tick=total_ticks)
        composer.fill_voice_section(voice_names[v], "A", MusicUnit(events=events + [pad]))
        
    ok, msg = composer.validate()
    assert ok, f"Zero-drift gate failed: {msg}"
    return composer
```

---

## 5. Architectural Alignment & Comparison

| Feature | Method 093 PPNC | Method 092 DLACG | Method 078 IMEC | Method 082 RBNCC | Method 021 CA |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Physical Mechanism** | Lattice connectivity phase transition | Kinetic Brownian cluster growth | Thermal spin-flip equilibrium | Gene regulatory Boolean criticality | Deterministic neighborhood update |
| **Critical Parameter** | Occupation prob $p \approx p_c$ | Sticking prob $p_{\text{stick}}$, seed count | Temperature $T \approx T_c$ | Average in-degree $K \approx K_c$ | Wolfram rule / totalistic sum |
| **Cluster Topology** | Scale-free fractal ($D_f \approx 1.90$) | Dendritic branching ($D_f \approx 1.71$) | Fractal domain walls at $T_c$ | State-space attractor cycles | Periodic / chaotic / glider lines |
| **Time Dynamics** | Instantaneous equilibrium or DP | Iterative particle accumulation | Metropolis MCMC sampling | Synchronous state recurrence | Synchronous lockstep grid |
| **Musical Output** | Pointillism $\to$ Counterpoint $\to$ Mass | Branching melodic arborescences | Chord magnetization / harmonic shift | Repeating rhythmic/harmonic loops | Micro-polyphonic rhythm grids |

---

## 6. References

- Broadbent, S. R., & Hammersley, J. M. (1957). "Percolation processes: I. Crystals and mazes." *Proceedings of the Cambridge Philosophical Society*, 53(3), 629–641.
- Stauffer, D., & Aharony, A. (1994). *Introduction to Percolation Theory* (2nd ed.). Taylor & Francis, London.
- Grimmett, G. (1999). *Percolation* (2nd ed.). Springer-Verlag, Berlin.
- Hinrichsen, H. (2000). "Non-equilibrium critical phenomena and directed percolation." *Advances in Physics*, 49(7), 815–958.
- Newman, M. E. J., & Ziff, R. M. (2000). "Efficient Monte Carlo algorithm and high-precision results for percolation." *Physical Review Letters*, 85(19), 4104–4107.
- Buehler, M. J. (2026). "Selective Imperfection as a Generative Framework for Analysis, Creativity and Discovery." *arXiv:2601.00863v1 [cs.LG]*, MIT.
