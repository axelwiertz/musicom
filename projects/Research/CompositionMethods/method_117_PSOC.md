# Particle Swarm Optimization Composition (PSOC) — Method 117

**Paradigm:** Stochastic  
**Layer:** concrete  
**Acronym:** PSOC  
**Next free ID:** 118

---

## Overview

Particle Swarm Optimization Composition (PSOC) frames music composition as a continuous-valued optimization problem solved by the particle swarm metaheuristic (Kennedy & Eberhart 1995). A population of P particles (candidate compositions) moves through a D-dimensional search space; each dimension encodes one musical parameter (pitch, onset, duration, velocity). The swarm's velocity-attraction dynamics — inertia, personal-best attraction, and global-best emulation — guide the population toward high-fitness solutions according to a weighted musical fitness function.

---

## Mathematical Foundation

### Particle Encoding

Each particle $\vec{x}_i \in \mathbb{R}^D$ concatenates per-note parameter vectors across all voices and sections:

$$\vec{x}_i = [\underbrace{p_{1,1}, o_{1,1}, d_{1,1}, v_{1,1}}_{\text{note 1}}, \ldots, \underbrace{p_{V,N}, o_{V,N}, d_{V,N}, v_{V,N}}_{\text{note }V\cdot N}]$$

where $p \in [0,127]$ = MIDI pitch, $o \in [0,1]$ = fractional onset within the bar, $d \in [0,1]$ = fractional duration, $v \in [0,127]$ = MIDI velocity. Total dimensionality $D = 4 V N$ for $V$ voices with $N$ notes each.

### Swarm Dynamics

The canonical PSO velocity-position update (Shi & Eberhart 1998):

$$\vec{v}_i(t+1) = w(t)\,\vec{v}_i(t) + c_1 r_1 \odot (\vec{p}_i - \vec{x}_i(t)) + c_2 r_2 \odot (\vec{g} - \vec{x}_i(t))$$

$$\vec{x}_i(t+1) = \vec{x}_i(t) + \vec{v}_i(t+1)$$

where:
- $\vec{v}_i$ = particle velocity
- $\vec{p}_i$ = personal best position
- $\vec{g}$ = global best position
- $r_1, r_2 \sim U(0,1)$ element-wise
- $c_1 = c_2 = 2.0$ (cognitive/social coefficients)
- $w(t) = 0.9 - 0.5(t/T_{\max})$ (inertia, linearly decreasing)

### Fitness Function

Six normalized sub-scores ($[0,1]$ each) weighted into a convex combination:

$$f(\vec{x}) = \sum_k w_k f_k(\vec{x}), \quad \sum_k w_k = 1$$

| Sub-score | Weight (default) | Purpose |
|---|---|---|
| $f_{\text{tonal}}$ | 0.25 | Scale deviation penalty $\propto \min_{s \in \text{scale}}(p-s)^2$ |
| $f_{\text{melodic}}$ | 0.15 | Stepwise preference, contour shape, repetition aversion |
| $f_{\text{rhythmic}}$ | 0.15 | Metric alignment, syncopation tolerance, overlap penalty |
| $f_{\text{harmonic}}$ | 0.25 | Chord-tone alignment, parallel-motion penalty, voice-leading parsimony |
| $f_{\text{texture}}$ | 0.10 | Per-voice event density, registral span |
| $f_{\text{structure}}$ | 0.10 | Within-section autocorrelation, between-section contrast |

---

## Classification

| Attribute | Value |
|---|---|
| **Paradigm** | Stochastic |
| **Layer** | concrete |
| **Tonal Gravity** | Strong (Fitness-guided, Key-bound) |
| **Metric Binding** | Grid-Locked / Continuous (style-dependent weight) |
| **Memory Depth** | Macro / Global Optimum |
| **Time Complexity** | $\mathcal{O}(I \cdot P \cdot D \cdot N)$ |
| **Primary Elements** | Pitch, Rhythm, Harmony, Structure, Texture |

---

## UnitMatrix Integration

**Voices**: Each voice $v$ occupies $4N$ contiguous dimensions. Voices evolve independently per-dimension but coupled through $f_{\text{harmonic}}$ (vertical pitch sets) and $f_{\text{texture}}$ (cross-voice density/registral separation). Percussion: pitch restricted to MIDI keys 35--81, $f_{\text{rhythmic}}$ dominates, $f_{\text{tonal}} \equiv 0$.

**Sections**: Each section $m$ has its own fitness landscape $f^{(m)}$ with per-section parameters. Section $m$ receives section $m-1$'s global best ending frame as a seed, padding/truncating to match dimensionality. The form schedule (order/repetition) is either designed or optimized by a higher-level discrete PSO.

**Cell filling**: Decoded $(p,o,d,v)$ 4-tuples from $\vec{g}$ are post-processed: pitch rounded to nearest integer MIDI, onset multiplied by bar_ticks and grid-aligned, duration multiplied by bar_ticks, velocity rounded and clamped. Zero-drift guarantee: $N$ per voice set so $\sum d_j \cdot \text{bar\_ticks} = \text{section\_ticks}$.

---

## Python Implementation Sketch

```python
import numpy as np

class Particle:
    __slots__ = ('pos', 'vel', 'pbest', 'pbest_fitness')
    def __init__(self, dim, bounds):
        self.pos = np.random.uniform(bounds[0], bounds[1], dim)
        self.vel = np.zeros(dim)
        self.pbest = self.pos.copy()
        self.pbest_fitness = -np.inf

class PSOC:
    def __init__(self, fitness_fn, bounds=(0, 1), P=50, T=500,
                 c1=2.0, c2=2.0, w_max=0.9, w_min=0.4, V_max=0.2):
        self.fitness = fitness_fn
        self.bounds = np.array(bounds)
        self.P = P                # swarm size
        self.T = T                # max iterations
        self.c1, self.c2 = c1, c2
        self.w_max, self.w_min = w_max, w_min
        self.V_max = V_max
        self.dim = None           # set by first call
        self.swarm = []
        self.gbest = None
        self.gbest_fitness = -np.inf

    def _init_swarm(self, dim):
        self.dim = dim
        self.swarm = [Particle(dim, self.bounds) for _ in range(self.P)]
        self._evaluate_all()

    def _evaluate_all(self):
        for p in self.swarm:
            f = self.fitness(p.pos)
            if f > p.pbest_fitness:
                p.pbest = p.pos.copy()
                p.pbest_fitness = f
            if f > self.gbest_fitness:
                self.gbest = p.pos.copy()
                self.gbest_fitness = f

    def optimize(self, dim, seed=None):
        if seed is not None:
            np.random.seed(seed)
        self._init_swarm(dim)
        for t in range(self.T):
            w = self.w_max - (self.w_max - self.w_min) * t / self.T
            for p in self.swarm:
                r1 = np.random.uniform(0, 1, dim)
                r2 = np.random.uniform(0, 1, dim)
                p.vel = (w * p.vel
                         + self.c1 * r1 * (p.pbest - p.pos)
                         + self.c2 * r2 * (self.gbest - p.pos))
                p.vel = np.clip(p.vel, -self.V_max, self.V_max)
                p.pos = np.clip(p.pos + p.vel, self.bounds[0], self.bounds[1])
            self._evaluate_all()
        return self.decode(self.gbest)

    @staticmethod
    def decode(x, V, N):
        """Decode particle vector to list of (pitch, onset, duration, velocity) per voice."""
        notes = []
        for v in range(V):
            start = v * N * 4
            chunk = x[start:start + N * 4].reshape(N, 4)
            notes.append(chunk)
        return notes
```

---

## Candidate Code Path

`generators/metaheuristic_psoc.py` — extends the `generators/` module. The swarm optimizer lives in a `generators/` submodule; the fitness functions ($f_{\text{tonal}}$, $f_{\text{melodic}}$, ...) live in `rules/musical_fitness.py` and are composed by the PSOC driver. Section seeding and cross-section continuity are handled at the `generators/` level.

---

## Relationship to Existing Methods

| Method | Key Difference |
|---|---|
| GA (003) | Discrete crossover/mutation vs. continuous velocity-attraction |
| SA (055) | Single-trajectory temperature-cooling vs. population-based vector-field |
| ACO (041) | Discrete pheromone-driven graph walk vs. continuous velocity in $\mathbb{R}^D$ |
| Boids (031) | Flocking kinematics without objective vs. fitness-driven optimization |
| HSIC (073) | Music-inspired operators per slot vs. generic velocity-acceleration dynamics |
| MOEPC (098) | Pareto-front multi-objective vs. scalarized single-objective PSO |

---

## References

1. Kennedy, J. & Eberhart, R. (1995). "Particle swarm optimization." *Proc. IEEE ICNN*, vol. 4, pp. 1942–1948.
2. Shi, Y. & Eberhart, R. (1998). "A modified particle swarm optimizer." *Proc. IEEE ICEC*, pp. 69–73.
3. Clerc, M. & Kennedy, J. (2002). "The particle swarm: explosion, stability, and convergence." *IEEE Trans. Evol. Comp.* 6(1), 58–73.
4. Bratton, D. & Kennedy, J. (2007). "Defining a standard for PSO." *Proc. IEEE SIS*, pp. 1–6.
5. He, Y. (2023). "Application of Particle Swarm Optimization Algorithm in the Production of Original Songs." *ICIEAI 2023*, ACM. doi:10.1145/3660043.3660094.
6. modbrin (2019). "music-pso: Composing music using Particle Swarm Optimization." GitHub. https://github.com/modbrin/music-pso

---

## Append Info

*Appended 2026-10-16 by the methods-research cron job. Layer tag: concrete. Paradigm: Stochastic. ID 117 assigned (max numeric ID before run was 116; `method_117*` and `report_117*` files did not exist at append time). Next free ID: 118.*