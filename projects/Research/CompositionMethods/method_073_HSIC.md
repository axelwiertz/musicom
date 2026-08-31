# Method 073 — Harmony Search Improvisational Composition (HSIC)

**Paradigm**: Stochastic (Probabilistic / Metaheuristic)
**Primary Elements**: Pitch, Rhythm, Harmony, Structure, Texture
**Classification**: Tonal Gravity = Strong (Fitness-guided + Key-bound) · Metric Binding = Grid-Locked / Continuous · Memory Depth = Macro / Harmony Memory · Time Complexity = $\mathcal{O}(I \cdot N \cdot HMS)$

---

## One-line description

Maintains a **Harmony Memory** of candidate musical phrases and improvises new ones slot-by-slot using the three Geem–Kim–Loganathan operators — **memory consideration** (reuse motifs), **pitch adjustment** (neighbor-tone/voice-leading micro-moves), and **random selection** (fresh leaps) — gated by a weighted musical-fitness function that converges the population toward idiomatic, in-key phrases.

## Why this is novel (not a duplicate)

003 Genetic uses mutation/crossover; 041 ACOPF uses pheromone trails; 055 SAMC uses a Metropolis temperature schedule. None of 001–072 uses the **improvisation-operator** search mechanism whose three operators are *literally named after musical actions* (memory consideration, pitch adjustment, random selection) and whose origin story is musicians improvising. HSIC closes the loop: it takes the music-inspired metaheuristic of Geem–Kim–Loganathan (2001) and turns it back onto music generation, with the Harmony Memory acting as the "band" whose shared vocabulary of licks/grooves/progressions is recombined and refined each iteration. Verified absent from the DB (grep for "harmony search" = 0 hits).

---

## Extended mathematics

### 1. Harmony vector and feasible sets

A candidate phrase ("harmony") is a vector over $N$ musical slots (one note pitch per melodic slot, one onset/duration per rhythmic slot, one chord function per bar, one density/velocity per section):

$$X = (x_1, x_2, \dots, x_N), \qquad x_i \in \mathcal{F}_i$$

where $\mathcal{F}_i$ is the feasible set for slot $i$: the key/scale pitch classes (so tonal gravity is a **hard constraint**), the grid positions (for metric binding), or the functional chord labels. The Harmony Memory is a population of $HMS$ such vectors:

$$HM = \{X^{(1)}, X^{(2)}, \dots, X^{(HMS)}\}.$$

### 2. The three improvisation operators

A new harmony is improvised slot-by-slot:

$$x_i' = \begin{cases}
x_i^{(j)} \in HM & \text{with probability } HMCR \quad (\text{memory consideration}) \\
x_i^{(j)} \pm bw \pmod{\mathcal{F}_i} & \text{with probability } HMCR \cdot PAR \quad (\text{pitch adjustment}) \\
\operatorname{uniform}(\mathcal{F}_i) & \text{with probability } 1 - HMCR \quad (\text{random selection})
\end{cases}$$

- **$HMCR$** (harmony memory considering rate, default 0.90–0.95): probability of *exploitation* — copying a slot value from a remembered phrase (persistence of motifs, grooves, progressions).
- **$PAR$** (pitch adjusting rate, default 0.3): conditional probability of *local refinement* — nudging a memory-considered value by a small step $\pm bw$ (neighbor tones, syncopation shifts, voice-leading micro-moves). For $bw = 1$ on a scale set, this enforces **conjunct motion**.
- **$1 - HMCR$**: probability of *exploration* — drawing a fresh feasible value (leaps, register jumps, novel chords).

### 3. Fitness and memory update

Each harmony is scored by a weighted energy over the five musical-element terms (the same explicit reward-vector idea as 055/062):

$$F(X) = w_1 \phi_{\text{tonal}} + w_2 \phi_{\text{groove}} + w_3 \phi_{\text{counterpoint}} + w_4 \phi_{\text{texture}} + w_5 \phi_{\text{structure}} + G(X)$$

where $G(X) = -\infty$ if the musicom `validate()` gate fails (zero-drift padding violation), otherwise $0$ — making export-safety a hard constraint. Memory update is elitist on the worst element:

$$\text{if } F(X') > \min_{X \in HM} F(X), \quad \text{then replace } \arg\min_{X \in HM} F(X) \leftarrow X'.$$

The population therefore **monotonically improves** while *retaining a diverse set of near-optimal phrases* (it is a population, not a single point), so different decodes sample different idiomatic material.

### 4. Adaptive operator schedules (explore → commit)

The analogue of 055 SA's cooling schedule is to ramp $PAR$ up and decay $bw$ down:

$$PAR(t) = PAR_0 + (PAR_{\max} - PAR_0)\frac{t}{I}, \qquad bw(t) = \max\!\Big(bw_{\min},\, \lfloor bw_0 (1 - t/I) \rfloor\Big).$$

Early improvisations explore coarsely (wide $bw$, low $PAR$); late ones polish (narrow $bw$, high $PAR$) — "improvise freely, then commit to the line."

### 5. Hierarchical / multi-stage search

For multi-section pieces the vector is decomposed top-down (the same cascade as 010/017):

$$X^{\text{form}} = (s_1, \dots, s_S) \;\rightarrow\; \text{seeds } HM^{\text{section}_s} \;\rightarrow\; X^{\text{cell}} = (\text{notes}, \text{rhythms}, \text{chords}, \text{density}).$$

A form-level HM improvises the section-label sequence; its best harmonies seed per-section HMs that improvise the note/rhythm/chord content, keeping each search small and convergent.

### 6. Complexity

- One improvisation: $\mathcal{O}(N)$.
- Fitness evaluation: $\mathcal{O}(N)$ (plus $\mathcal{O}(V \cdot S)$ for the validation gate).
- Total for $I$ improvisations: $\mathcal{O}(I \cdot N \cdot HMS)$ (each iteration scores $1$ new harmony; the $HMS$ factor comes from memory maintenance/replacement).
- Memory: $\mathcal{O}(HMS \cdot N)$ — the Harmony Memory is the only state.

---

## Python implementation sketch (NumPy)

```python
from __future__ import annotations
import numpy as np
from numpy.random import default_rng

class HarmonySearch:
    """Canonical Harmony Search (Geem-Kim-Loganathan 2001) over discrete musical slots."""
    def __init__(self, feasible_sets, fitness, hms=20, hmcr=0.90, par=0.30,
                 bw=1, par_max=0.70, bw_min=0.0, seed=0):
        self.feasible = feasible_sets          # list of np arrays: feasible values per slot
        self.fitness = fitness                 # callable X -> float (higher = better)
        self.hms, self.hmcr, self.par = hms, hmcr, par
        self.bw, self.par_max, self.bw_min = bw, par_max, bw_min
        self.rng = default_rng(seed)
        self.N = len(feasible_sets)
        self.HM = np.vstack([self._random_harmony() for _ in range(hms)])
        self.fits = np.array([self.fitness(x) for x in self.HM])

    def _random_harmony(self):
        return np.array([self.rng.choice(f) for f in self.feasible])

    def _improvise(self, par, bw):
        x = np.empty(self.N, dtype=object)
        for i, f in enumerate(self.feasible):
            if self.rng.random() < self.hmcr:              # memory consideration
                val = self.HM[self.rng.integers(self.hms), i]
                if self.rng.random() < par:                # pitch adjustment
                    idx = np.searchsorted(f, val)
                    j = int(np.clip(idx + self.rng.integers(-bw, bw + 1), 0, len(f) - 1))
                    val = f[j]
            else:                                          # random selection
                val = self.rng.choice(f)
            x[i] = val
        return x

    def run(self, iterations=2000):
        for it in range(iterations):
            par = self.par + (self.par_max - self.par) * (it / iterations)
            bw = max(self.bw_min, int(round(self.bw * (1 - it / iterations))))
            x = self._improvise(par, bw)
            fx = self.fitness(x)
            worst = int(np.argmin(self.fits))
            if fx > self.fits[worst]:
                self.HM[worst], self.fits[worst] = x, fx
        best = int(np.argmax(self.fits))
        return self.HM[best], self.fits[best]
```

### musicom integration (conceptual — engine does the MIDI authoring)

```python
# One harmony vector = one UnitMatrix filling: per-voice pitch blocks + rhythm slots
# + chord/density variables. fitness() wraps the aesthetic terms + the zero-drift
# validate() gate as a hard constraint (return -inf on violation).
#   feasible_pitch = scale_degrees_in_key(key)          # tonal gravity = hard bound
#   hs = HarmonySearch(feasible_sets, fitness, hms=20)
#   best_X, score = hs.run(iterations=2000)
#   for v in range(num_voices):
#       composer.fill_voice_section(voice=v, section=s,
#           create_note_unit(best_X[pitch_idx], dur, tick))
#   ok, msg = composer.validate()   # MUST be True before to_midi (per AGENTS.md)
```

---

## Pitfalls

1. **Premature convergence → stale single loop**: high $HMCR$ / low $PAR$ collapses HM to one loop. Fix: adaptive schedule; cap $HMCR \le 0.95$; occasional memory restart.
2. **Fixed $bw$ → too coarse or too fine**: large $bw$ never converges, tiny $bw$ traps in local optima. Fix: decay $bw$ (mirrors SA cooling); late-run $bw = 1$ enforces conjunct, vocal lines.
3. **Flat/tied fitness → no gradient**: binary pass/fail gives coin-flip updates. Fix: continuous weighted energy + jitter.
4. **HM too small → lost diversity**: $HMS < 10$ is myopic. Fix: $HMS \in [10, 50]$; reject near-duplicates (min Hamming distance).
5. **Random selection violates key**: full-chromatic feasible set destroys tonal gravity. Fix: feasible sets = key/scale pitches, grid positions, functional chords.
6. **Sparse/staccato output**: few onsets decode to staccato (011/032 failure). Fix: hybridization rule — layer a continuous fill voice (026 DPSM, pad, walking bass) from a separate low-$PAR$/low-$bw$ run.
7. **Single flat search for long pieces**: huge variable vector converges poorly. Fix: hierarchical HSIC (form-level HM seeds per-section HMs).
8. **Ignoring the validation gate**: high-fitness harmony can still violate zero-drift. Fix: wrap `validate()` as hard constraint ($-\infty$).

---

## References

- Geem, Z. W., Kim, J. H., & Loganathan, G. V. (2001). "A new heuristic optimization algorithm: Harmony Search." *Simulation* 76(2), 60–68.
- Lee, K. S., & Geem, Z. W. (2005). "A new meta-heuristic algorithm for continuous engineering optimization: harmony search theory and practice." *Computer Methods in Applied Mechanics and Engineering* 194, 3902–3933.
- Geem, Z. W., & Choi, J.-Y. (2007). "Music composition using the harmony search algorithm." *Proceedings of the 2007 International Conference on Applications of Evolutionary Computing (EvoWorkshops)*.
- Geem, Z. W. (2010). "Recent advances in harmony search algorithm." *Studies in Computational Intelligence* 270, Springer.
